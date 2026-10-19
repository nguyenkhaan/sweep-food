"""Shared typed async OpenAI API client for SweepFood AI."""

from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any, Self

import httpx

from AI.errors import (
    ExtractionBadResponseError,
    ExtractionTimeoutError,
    ExtractionUnavailableError,
)
from src.core.setting import (
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    OPENAI_LLM_MODEL,
    OPENAI_TIMEOUT_SECONDS,
)

logger = logging.getLogger(__name__)

_RETRY_STATUS_CODES = frozenset({429, 500, 502, 503, 504})
_MARKDOWN_JSON_REGEX = re.compile(
    r"```(?:json)?\s*([\{\[].*?[\}\]])\s*```", re.DOTALL
)


class OpenAIClient:
    """Shared typed async OpenAI API client using httpx.

    Provides bounded retries on 429 and 5xx errors with exponential backoff,
    support for structured JSON output and multimodal (image) inputs,
    and typed domain exceptions without leaking user text or credentials.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
        max_retries: int = 2,
        backoff_factor: float = 0.05,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else OPENAI_API_KEY
        self.base_url = (base_url or OPENAI_BASE_URL).rstrip("/")
        self.model = model or OPENAI_LLM_MODEL
        self.timeout = (
            timeout if timeout is not None else float(OPENAI_TIMEOUT_SECONDS)
        )
        self.max_retries = max(0, max_retries)
        self.backoff_factor = max(0.05, backoff_factor)
        self._external_client = http_client
        self._owned_client: httpx.AsyncClient | None = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._external_client is not None:
            return self._external_client
        if self._owned_client is None or self._owned_client.is_closed:
            self._owned_client = httpx.AsyncClient(timeout=self.timeout)
        return self._owned_client

    async def aclose(self) -> None:
        """Close any owned HTTP client session."""
        if self._owned_client is not None and not self._owned_client.is_closed:
            await self._owned_client.aclose()
            self._owned_client = None

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        await self.aclose()

    def _calculate_backoff(
        self, attempt: int, resp: httpx.Response | None = None
    ) -> float:
        if resp is not None:
            retry_after = resp.headers.get("retry-after")
            if retry_after:
                try:
                    val = float(retry_after)
                    if 0 < val <= 30.0:
                        return val
                except ValueError:
                    pass
        delay = self.backoff_factor * (2**attempt)
        return min(delay, 10.0)

    async def create_raw_chat_completion(
        self,
        payload: dict[str, Any],
        *,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        """Send chat completion payload to OpenAI API with bounded retry on 429/5xx."""
        if not self.api_key or not self.api_key.strip():
            raise ExtractionUnavailableError(
                "OpenAI API key is missing or not configured."
            )

        req_timeout = timeout if timeout is not None else self.timeout
        client = self._get_client()
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        last_resp: httpx.Response | None = None
        for attempt in range(self.max_retries + 1):
            try:
                resp = await client.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=req_timeout,
                )
                last_resp = resp
            except httpx.TimeoutException as exc:
                if attempt < self.max_retries:
                    delay = self._calculate_backoff(attempt)
                    logger.warning(
                        "OpenAI request timed out, retrying (attempt %d/%d) after %.2fs delay",
                        attempt + 1,
                        self.max_retries,
                        delay,
                    )
                    await asyncio.sleep(delay)
                    continue
                raise ExtractionTimeoutError(
                    f"OpenAI chat completion timed out: {exc}"
                ) from exc
            except httpx.NetworkError as exc:
                if attempt < self.max_retries:
                    delay = self._calculate_backoff(attempt)
                    logger.warning(
                        "OpenAI network error, retrying (attempt %d/%d) after %.2fs delay",
                        attempt + 1,
                        self.max_retries,
                        delay,
                    )
                    await asyncio.sleep(delay)
                    continue
                raise ExtractionUnavailableError(
                    f"Network error contacting OpenAI: {exc}"
                ) from exc

            if resp.status_code in _RETRY_STATUS_CODES and attempt < self.max_retries:
                delay = self._calculate_backoff(attempt, resp)
                logger.warning(
                    "OpenAI request returned HTTP %s, retrying (attempt %d/%d) after %.2fs delay",
                    resp.status_code,
                    attempt + 1,
                    self.max_retries,
                    delay,
                )
                await asyncio.sleep(delay)
                continue

            break

        assert last_resp is not None
        if last_resp.status_code in (401, 403, 429, 503):
            raise ExtractionUnavailableError(
                f"OpenAI service unavailable (HTTP {last_resp.status_code})"
            )
        if last_resp.status_code != 200:
            raise ExtractionBadResponseError(
                f"OpenAI request failed (HTTP {last_resp.status_code})"
            )

        try:
            data = last_resp.json()
        except (json.JSONDecodeError, ValueError) as exc:
            raise ExtractionBadResponseError(
                f"OpenAI returned invalid HTTP JSON: {exc}"
            ) from exc

        if not isinstance(data, dict):
            raise ExtractionBadResponseError("OpenAI JSON response must be a dict.")

        return data

    async def create_chat_completion(
        self,
        messages: list[dict[str, Any]],
        *,
        model: str | None = None,
        max_completion_tokens: int | None = 4096,
        response_format: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> str:
        """Call OpenAI chat completion and return the assistant message content string."""
        payload: dict[str, Any] = {
            "model": model or self.model,
            "messages": messages,
        }
        if max_completion_tokens is not None:
            payload["max_completion_tokens"] = max_completion_tokens
        if response_format is not None:
            payload["response_format"] = response_format

        data = await self.create_raw_chat_completion(payload, timeout=timeout)
        choices = data.get("choices")
        if not choices or not isinstance(choices, list):
            raise ExtractionBadResponseError("OpenAI response missing 'choices'.")

        first_choice = choices[0]
        if not isinstance(first_choice, dict):
            raise ExtractionBadResponseError("Invalid choice structure in OpenAI response.")

        message = first_choice.get("message")
        if not isinstance(message, dict):
            raise ExtractionBadResponseError("Missing message in OpenAI response choice.")

        if message.get("refusal"):
            refusal_text = str(message.get("refusal"))
            raise ExtractionBadResponseError(f"OpenAI model refused request: {refusal_text}")

        content = message.get("content")
        if content is None:
            raise ExtractionBadResponseError("OpenAI returned null message content.")

        return str(content)

    async def create_chat_completion_json(
        self,
        messages: list[dict[str, Any]],
        *,
        model: str | None = None,
        max_completion_tokens: int | None = 4096,
        timeout: float | None = None,
    ) -> Any:
        """Call OpenAI chat completion in JSON mode and parse the resulting JSON object."""
        content = await self.create_chat_completion(
            messages=messages,
            model=model,
            max_completion_tokens=max_completion_tokens,
            response_format={"type": "json_object"},
            timeout=timeout,
        )

        stripped = content.strip()
        # Strip markdown ```json codeblock if present
        m = _MARKDOWN_JSON_REGEX.search(stripped)
        if m:
            stripped = m.group(1).strip()

        try:
            return json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ExtractionBadResponseError(
                f"OpenAI response was not valid JSON: {exc}"
            ) from exc
