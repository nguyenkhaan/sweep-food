"""Groq Whisper-large-v3-turbo Client for Vietnamese ASR.

Sends audio to https://api.groq.com/openai/v1/audio/transcriptions
using the whisper-large-v3-turbo model for ultra-fast, high-precision
transcription in Vietnamese.
"""

from __future__ import annotations

import os
import socket
from pathlib import Path
from typing import Optional
import requests
import urllib3.util.connection as urllib3_cn

# Force IPv4 on Windows to prevent 40s IPv6 route hang
urllib3_cn.allowed_gai_family = lambda: socket.AF_INET
def _load_env_fallback():
    if "GROQ_API_KEY" in os.environ and os.environ["GROQ_API_KEY"]:
        return
    env_file = Path(__file__).resolve().parents[2] / ".env"
    if env_file.exists():
        try:
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("GROQ_API_KEY="):
                    val = line.split("=", 1)[1].strip().strip('"\'')
                    if val:
                        os.environ["GROQ_API_KEY"] = val
        except Exception:
            pass

_load_env_fallback()

GROQ_API_KEY_DEFAULT = ""
GROQ_TRANSCRIPTION_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
DEFAULT_MODEL = "whisper-large-v3-turbo"

class GroqWhisperClient:
    """Client for Groq Audio Transcriptions API using whisper-large-v3-turbo."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY", GROQ_API_KEY_DEFAULT)
        self.session = requests.Session()
        self.session.trust_env = False  # Avoid Windows PAC proxy resolution delays

    def transcribe_file(
        self,
        audio_path: str | Path,
        language: str = "vi",
        prompt: Optional[str] = None,
        timeout: float = 30.0,
    ) -> dict:
        """Transcribe an audio file using Groq Whisper API.

        Args:
            audio_path: Path to audio file (.flac, .wav, .mp3, .m4a, .ogg, .webm).
            language: ISO-639-1 language code (default 'vi' for Vietnamese).
            prompt: Optional context prompt to guide spelling/domain (e.g. food items).
            timeout: Request timeout in seconds.

        Returns:
            Dict containing 'text', 'model', 'language', and status information.
        """
        path = Path(audio_path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Audio file does not exist: {audio_path}")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        # Context prompt tailored for Vietnamese groceries & ingredients
        default_prompt = "Danh sách thực phẩm, nguyên liệu nấu ăn: thịt bò, tôm sú, cải thìa, rau muống, nấm, gia vị."
        effective_prompt = prompt or default_prompt

        filename = path.name
        # Determine content type based on extension
        ext = path.suffix.lower()
        content_type_map = {
            ".flac": "audio/flac",
            ".wav": "audio/wav",
            ".mp3": "audio/mpeg",
            ".m4a": "audio/m4a",
            ".ogg": "audio/ogg",
            ".webm": "audio/webm",
        }
        mime = content_type_map.get(ext, "application/octet-stream")

        try:
            with open(path, "rb") as f:
                files = {
                    "file": (filename, f, mime),
                }
                data = {
                    "model": DEFAULT_MODEL,
                    "language": language,
                    "response_format": "json",
                    "prompt": effective_prompt,
                    "temperature": 0.0,
                }

                resp = self.session.post(
                    GROQ_TRANSCRIPTION_URL,
                    headers=headers,
                    data=data,
                    files=files,
                    timeout=timeout,
                )

            if resp.status_code != 200:
                err_details = resp.text
                return {
                    "text": "",
                    "engine": "groq_whisper_turbo",
                    "model": DEFAULT_MODEL,
                    "language": language,
                    "success": False,
                    "error": f"Groq API trả về mã lỗi HTTP {resp.status_code}: {err_details}",
                }

            resp_json = resp.json()
            transcribed_text = resp_json.get("text", "").strip()

            return {
                "text": transcribed_text,
                "engine": "groq_whisper_turbo",
                "model": DEFAULT_MODEL,
                "language": language,
                "success": True,
            }
        except requests.RequestException as exc:
            return {
                "text": "",
                "engine": "groq_whisper_turbo",
                "model": DEFAULT_MODEL,
                "language": language,
                "success": False,
                "error": f"Lỗi kết nối mạng tới Groq API ({GROQ_TRANSCRIPTION_URL}): {str(exc)}",
            }
