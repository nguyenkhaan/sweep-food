"""Gipformer ASR Engine for Local Vietnamese Speech Recognition.

References: G:\\github\\FAINANCE-smart-input\\gipformer
Compresses audio via ffmpeg to 16kHz mono FLAC first, then runs inference.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from smart_input.asr.audio_preprocessor import convert_to_16k_mono_flac


class GipformerEngine:
    """Inference engine for local Gipformer Vietnamese speech recognition."""

    def __init__(
        self,
        model_dir: Optional[str | Path] = None,
        quantize: str = "int8",
    ):
        self.quantize = quantize
        self.model_dir = Path(model_dir) if model_dir else Path("G:/github/FAINANCE-smart-input/gipformer")
        self._recognizer = None
        self._initialized = False

    def is_available(self) -> bool:
        """Check if local sherpa-onnx and model files are ready."""
        try:
            import sherpa_onnx  # noqa: F401
            return True
        except ImportError:
            return False

    def _init_model(self):
        if self._initialized:
            return
        try:
            import sherpa_onnx
            from huggingface_hub import hf_hub_download

            repo_id = "g-group-ai-lab/gipformer-65M-rnnt"
            encoder = hf_hub_download(repo_id=repo_id, filename="encoder-epoch-35-avg-6.int8.onnx")
            decoder = hf_hub_download(repo_id=repo_id, filename="decoder-epoch-35-avg-6.int8.onnx")
            joiner = hf_hub_download(repo_id=repo_id, filename="joiner-epoch-35-avg-6.int8.onnx")
            tokens = hf_hub_download(repo_id=repo_id, filename="tokens.txt")

            self._recognizer = sherpa_onnx.OfflineRecognizer.from_transducer(
                encoder=encoder,
                decoder=decoder,
                joiner=joiner,
                tokens=tokens,
                num_threads=4,
                sample_rate=16000,
                feature_dim=80,
                decoding_method="greedy_search",
            )
            self._initialized = True
        except Exception as exc:
            self._recognizer = None
            self._initialized = False
            raise RuntimeError(f"Failed to initialize local Gipformer engine: {exc}") from exc

    def transcribe_file(self, audio_path: str | Path) -> dict:
        """Preprocess audio to 16kHz mono FLAC and transcribe."""
        # 1. Always downsample and convert to 16kHz mono FLAC first (User requirement)
        flac_path = convert_to_16k_mono_flac(audio_path)

        if not self.is_available():
            return {
                "text": "",
                "engine": "gipformer_local",
                "flac_path": str(flac_path),
                "success": False,
                "note": "sherpa-onnx not installed in current environment. Switch to Groq Whisper Turbo for instant cloud transcription.",
            }

        try:
            self._init_model()
            import soundfile as sf
            samples, sample_rate = sf.read(str(flac_path), dtype="float32")
            if samples.ndim > 1:
                samples = samples.mean(axis=1)

            stream = self._recognizer.create_stream()
            stream.accept_waveform(sample_rate, samples)
            self._recognizer.decode_streams([stream])
            recognized_text = stream.result.text.strip()

            return {
                "text": recognized_text,
                "engine": "gipformer_local",
                "flac_path": str(flac_path),
                "success": True,
            }
        except Exception as err:
            return {
                "text": "",
                "engine": "gipformer_local",
                "flac_path": str(flac_path),
                "success": False,
                "error": str(err),
            }
