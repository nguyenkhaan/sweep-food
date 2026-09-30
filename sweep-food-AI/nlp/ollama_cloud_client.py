"""Ollama Cloud Client (hosted on ollama.com, not localhost).

Connects directly to Ollama Cloud API (https://ollama.com/v1) using the keys
specified in desktop key.txt or environment variable OLLAMA_API_KEY.
Default model: gpt-oss:120b (cloud hosted OSS 120B reasoning model).
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

OLLAMA_CLOUD_BASE_URL = "https://ollama.com/v1"
DEFAULT_MODEL = "gpt-oss:120b"
KEY_FILE_PATH = Path("C:/Users/HUYPNG/Desktop/key.txt")


def load_keys() -> list[str]:
    """Load all valid Ollama Cloud API keys from key.txt and environment."""
    keys = []
    env_key = os.environ.get("OLLAMA_API_KEY")
    if env_key and "." in env_key:
        keys.append(env_key.strip())

    if KEY_FILE_PATH.exists():
        text = KEY_FILE_PATH.read_text(encoding="utf-8", errors="ignore")
        for line in text.splitlines():
            line = line.strip()
            # Look for 32hex.token pattern
            parts = line.split()
            for p in parts:
                p = p.strip(" -:,")
                if "." in p and len(p.split(".")[0]) == 32:
                    if p not in keys:
                        keys.append(p)

    return keys


class OllamaCloudClient:
    def __init__(self, api_key: str | None = None, base_url: str = OLLAMA_CLOUD_BASE_URL, default_model: str = DEFAULT_MODEL):
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        if api_key:
            self.keys = [api_key]
        else:
            self.keys = load_keys()
        if not self.keys:
            raise ValueError("No Ollama Cloud API key found in Desktop/key.txt or OLLAMA_API_KEY env var.")
        self._key_index = 0
    def get_current_key(self) -> str:
        return self.keys[self._key_index % len(self.keys)]

    def rotate_key(self) -> str:
        self._key_index = (self._key_index + 1) % len(self.keys)
        return self.get_current_key()

    def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int | None = 4096,
        retries: int | None = None,
        timeout: float = 90.0,
    ) -> dict[str, Any]:
        """Send chat completion request to Ollama Cloud (OpenAI compatible endpoint)."""
        target_model = model or self.default_model
        payload = {
            "model": target_model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        data = json.dumps(payload).encode("utf-8")

        if retries is None:
            retries = max(len(self.keys) * 2, 15)
        for attempt in range(retries):
            current_key = self.get_current_key()
            req = urllib.request.Request(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {current_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "SweepFood-OllamaCloud/1.0",
                },
                data=data,
            )

            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    result = json.loads(resp.read().decode("utf-8"))
                    choice = result["choices"][0]["message"]
                    return {
                        "content": choice.get("content", ""),
                        "reasoning": choice.get("reasoning", ""),
                        "model": result.get("model", target_model),
                        "usage": result.get("usage", {}),
                    }
            except urllib.error.HTTPError as e:
                # 429 = rate limit, 401 = unauthorized -> rotate key
                if e.code in (401, 429) and len(self.keys) > 1:
                    print(f"[OllamaCloud] Key rate limited or unauthorized (HTTP {e.code}), rotating key...")
                    self.rotate_key()
                    time.sleep(1.0)
                    continue
                err_body = e.read().decode("utf-8", errors="ignore")
                if attempt == retries - 1:
                    raise RuntimeError(f"Ollama Cloud HTTP {e.code}: {err_body}") from e
                time.sleep(2.0 ** attempt)
            except Exception as e:
                if attempt == retries - 1:
                    raise
                time.sleep(2.0 ** attempt)

        raise RuntimeError("Failed to obtain response from Ollama Cloud after retries.")


if __name__ == "__main__":
    client = OllamaCloudClient()
    print(f"Loaded {len(client.keys)} Ollama Cloud keys.")
    print("Testing chat with gpt-oss:120b on https://ollama.com/v1...")
    res = client.chat([
        {"role": "user", "content": "Tóm tắt 3 quy tắc nấu phở bò ngon trong đúng 3 gạch đầu dòng."}
    ])
    print("\n--- Response ---")
    print(res["content"])
    if res.get("reasoning"):
        print("\n--- Model CoT Reasoning (Preview) ---")
        print(res["reasoning"][:250] + "...")
    print("\n--- Usage ---")
    print(res["usage"])
