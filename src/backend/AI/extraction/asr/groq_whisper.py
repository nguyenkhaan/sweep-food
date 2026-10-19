"""Async Groq Whisper client for Vietnamese speech-to-text."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import httpx

from AI.errors import (
    ExtractionBadResponseError,
    ExtractionTimeoutError,
    ExtractionUnavailableError,
)
from AI.extraction.asr.audio_preprocessor import preprocess_audio_bytes
from src.core.setting import (
    GROQ_API_KEY,
    GROQ_ASR_MODEL,
    GROQ_TIMEOUT_SECONDS,
)

GROQ_TRANSCRIPTION_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
DEFAULT_PROMPT = (
    "Danh sách thực phẩm, nguyên liệu nấu ăn: "
    "thịt bò, tôm sú, cải thìa, rau muống, nấm, gia vị."
)

MIME_TYPE_MAP: dict[str, str] = {
    ".flac": "audio/flac",
    ".wav": "audio/wav",
    ".mp3": "audio/mpeg",
    ".m4a": "audio/m4a",
    ".ogg": "audio/ogg",
    ".webm": "audio/webm",
}


class GroqWhisperClient:
    """Async client for Groq Audio Transcriptions API using whisper-large-v3-turbo."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else GROQ_API_KEY
        self.model = model or GROQ_ASR_MODEL
        self.timeout = (
            timeout if timeout is not None else float(GROQ_TIMEOUT_SECONDS)
        )
        self._client = http_client

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is not None:
            return self._client
        return httpx.AsyncClient(timeout=self.timeout)

    async def transcribe_audio_bytes(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav",
        language: str = "vi",
        prompt: str | None = None,
    ) -> dict[str, Any]:
        """Transcribe audio bytes using Groq Whisper API.

        Applies ffmpeg preprocessing if available, then posts to Groq API.
        """
        if not self.api_key or not self.api_key.strip():
            raise ExtractionUnavailableError(
                "Groq API key is missing or not configured."
            )

        if not audio_bytes:
            raise ValueError("Audio bytes must not be empty.")

        ext = Path(filename).suffix.lower() or ".wav"
        processed_bytes, stats = await asyncio.to_thread(
            preprocess_audio_bytes, audio_bytes, input_format=ext, strip_silence=True
        )

        upload_filename = (
            "audio.flac" if stats.get("ffmpeg_available") else filename
        )
        upload_mime = (
            "audio/flac"
            if stats.get("ffmpeg_available")
            else MIME_TYPE_MAP.get(ext, "application/octet-stream")
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        files = {
            "file": (upload_filename, processed_bytes, upload_mime),
        }
        data = {
            "model": self.model,
            "language": language,
            "response_format": "json",
            "prompt": prompt or DEFAULT_PROMPT,
            "temperature": "0.0",
        }

        client = self._get_client()
        should_close = self._client is None

        try:
            try:
                resp = await client.post(
                    GROQ_TRANSCRIPTION_URL,
                    headers=headers,
                    data=data,
                    files=files,
                    timeout=self.timeout,
                )
            except httpx.TimeoutException as exc:
                raise ExtractionTimeoutError(
                    f"Groq Whisper request timed out: {exc}"
                ) from exc
            except httpx.NetworkError as exc:
                raise ExtractionUnavailableError(
                    f"Network error contacting Groq Whisper: {exc}"
                ) from exc

            if resp.status_code in (401, 403, 429, 503):
                raise ExtractionUnavailableError(
                    f"Groq Whisper service unavailable (HTTP {resp.status_code}): {resp.text}"
                )
            if resp.status_code != 200:
                raise ExtractionBadResponseError(
                    f"Groq Whisper failed (HTTP {resp.status_code}): {resp.text}"
                )

            try:
                resp_json = resp.json()
            except Exception as exc:
                raise ExtractionBadResponseError(
                    f"Groq Whisper returned invalid JSON: {exc}"
                ) from exc

            transcript = str(resp_json.get("text") or "").strip()

            return {
                "status": "success",
                "engine": "groq_whisper_turbo",
                "model": self.model,
                "language": language,
                "transcript": transcript,
                "preprocess_stats": stats,
            }
        finally:
            if should_close:
                await client.aclose()
