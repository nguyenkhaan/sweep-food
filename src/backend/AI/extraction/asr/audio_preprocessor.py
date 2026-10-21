"""Audio preprocessor for Smart Input ASR using ffmpeg."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from AI.errors import AudioPreprocessingError


def get_ffmpeg_binary() -> str | None:
    """Find available ffmpeg binary from system PATH or imageio_ffmpeg."""
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return ffmpeg_path

    try:
        import imageio_ffmpeg

        return str(imageio_ffmpeg.get_ffmpeg_exe())
    except (ImportError, AttributeError, OSError):
        return None


def convert_to_16k_mono_flac(
    input_path: Path,
    output_path: Path | None = None,
    strip_silence: bool = True,
) -> Path:
    """Convert any audio file to 16000Hz, single channel (mono) FLAC."""
    ffmpeg = get_ffmpeg_binary()
    if not ffmpeg:
        raise AudioPreprocessingError(
            "ffmpeg binary not found in PATH or environment."
        )

    in_p = Path(input_path).resolve()
    if not in_p.exists():
        raise AudioPreprocessingError(f"Audio file does not exist: {in_p}")

    if output_path is None:
        with tempfile.NamedTemporaryFile(suffix=".flac", delete=False) as out_f:
            out_p = Path(out_f.name)
    else:
        out_p = Path(output_path).resolve()

    filter_args: list[str] = []
    if strip_silence:
        filter_args = [
            "-af",
            (
                "silenceremove=start_periods=1:start_duration=0.1:start_threshold=-45dB:"
                "stop_periods=1:stop_duration=0.5:stop_threshold=-45dB"
            ),
        ]

    cmd = [
        ffmpeg,
        "-y",
        "-i",
        str(in_p),
        *filter_args,
        "-ar",
        "16000",
        "-ac",
        "1",
        "-c:a",
        "flac",
        str(out_p),
    ]

    try:
        res = subprocess.run(
            cmd,
            capture_output=True,
            check=False,
            timeout=15.0,
        )
        if res.returncode != 0:
            err = res.stderr.decode("utf-8", errors="ignore")
            raise AudioPreprocessingError(
                f"ffmpeg conversion failed (code {res.returncode}): {err}"
            )
    except subprocess.TimeoutExpired as exc:
        raise AudioPreprocessingError("ffmpeg execution timed out") from exc
    except Exception as exc:
        if isinstance(exc, AudioPreprocessingError):
            raise
        raise AudioPreprocessingError(f"ffmpeg conversion failed: {exc}") from exc

    return out_p


def preprocess_audio_bytes(
    audio_bytes: bytes,
    input_format: str = "wav",
    strip_silence: bool = True,
) -> tuple[bytes, dict[str, Any]]:
    """Convert raw audio bytes to 16kHz mono FLAC bytes if ffmpeg is available.

    Falls back cleanly to input bytes if ffmpeg is not present on the host.
    """
    if not audio_bytes:
        raise ValueError("Audio bytes must not be empty.")

    ffmpeg = get_ffmpeg_binary()
    if not ffmpeg:
        return audio_bytes, {
            "ffmpeg_available": False,
            "original_size": len(audio_bytes),
            "processed_size": len(audio_bytes),
            "ratio": 1.0,
        }

    fmt = input_format.lstrip(".").lower()
    in_suffix = f".{fmt}" if fmt else ".wav"

    with tempfile.NamedTemporaryFile(
        suffix=in_suffix, delete=False
    ) as tmp_input:
        tmp_input.write(audio_bytes)
        in_path = tmp_input.name

    out_path = None
    try:
        out_p = convert_to_16k_mono_flac(
            Path(in_path), strip_silence=strip_silence
        )
        out_path = str(out_p)
        flac_bytes = out_p.read_bytes()
        stats: dict[str, Any] = {
            "ffmpeg_available": True,
            "original_size": len(audio_bytes),
            "processed_size": len(flac_bytes),
            "ratio": (
                round(len(flac_bytes) / len(audio_bytes), 3)
                if audio_bytes
                else 1.0
            ),
        }
        return flac_bytes, stats
    except (AudioPreprocessingError, OSError, subprocess.SubprocessError):
        # Fall back to raw audio bytes if conversion fails
        return audio_bytes, {
            "ffmpeg_available": True,
            "conversion_failed": True,
            "original_size": len(audio_bytes),
            "processed_size": len(audio_bytes),
            "ratio": 1.0,
        }
    finally:
        if os.path.exists(in_path):
            os.unlink(in_path)
        if out_path and os.path.exists(out_path):
            os.unlink(out_path)
