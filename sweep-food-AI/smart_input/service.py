"""Unified Service Facade for Smart Input (OCR & ASR Dual Stream).

Decoupled from the recommendation engine.
Features:
- OCR: Supermarket receipts & Bách Hóa Xanh food packaging stickers (PaddleOCR + VietOCR)
  with image downsampling (max 1600px), CLAHE contrast enhancement, and JPEG compression.
- ASR Dual Stream:
    1. Local Gipformer + 16kHz mono FLAC compression & silence stripping via ffmpeg
    2. Cloud Groq Whisper-large-v3-turbo API (<500ms) with 16kHz mono FLAC
- Culinary Speech NLP for Vietnamese pantry normalization
- GPU Warm-up on startup to eliminate cold-start inference latency
"""

from __future__ import annotations

import base64
import os
import tempfile
import time
from pathlib import Path
from typing import Any, Optional

from smart_input.ocr.receipt_parser import parse_receipt_text
from smart_input.ocr.label_parser import FoodLabelParser
from smart_input.ocr.paddle_vietocr_pipeline import PaddleVietOCRPipeline
from smart_input.ocr.sample_receipts import SAMPLE_RECEIPTS
from smart_input.asr.speech_parser import parse_vietnamese_speech
from smart_input.asr.sample_transcripts import SAMPLE_VOICE_QUERIES
from smart_input.asr.groq_whisper import GroqWhisperClient
from smart_input.asr.gipformer_engine import GipformerEngine
from smart_input.asr.audio_preprocessor import convert_to_16k_mono_flac, preprocess_audio_bytes
from smart_input.ocr.image_preprocessor import preprocess_image_bytes
from smart_input.correction.protonx_corrector import get_corrector

# Global singleton instances for speed
_ocr_pipeline: Optional[PaddleVietOCRPipeline] = None
_label_parser: Optional[FoodLabelParser] = None
_groq_client: Optional[GroqWhisperClient] = None
_gipformer_engine: Optional[GipformerEngine] = None

def _serialize_label_item(label_item: dict[str, Any]) -> dict[str, Any]:
    """Expose label facts and provenance already produced by the parser."""
    return {
        "name": label_item["name"],
        "quantity_g": label_item["quantity_g"],
        "quantity_source": label_item["quantity_source"],
        "hours_to_expire": label_item["hours_to_expire"],
        "expiry_date": label_item.get("expiry_date"),
        "production_date": label_item.get("production_date"),
        "note": f"HSD: {label_item.get('expiry_date') or 'Theo bao bì'}",
    }



def get_ocr_pipeline(use_gpu: Optional[bool] = None) -> PaddleVietOCRPipeline:
    global _ocr_pipeline
    if _ocr_pipeline is None:
        if use_gpu is None:
            try:
                import torch
                use_gpu = torch.cuda.is_available()
            except Exception:
                use_gpu = False
        _ocr_pipeline = PaddleVietOCRPipeline(use_gpu=use_gpu)
    return _ocr_pipeline


def get_label_parser() -> FoodLabelParser:
    global _label_parser
    if _label_parser is None:
        _label_parser = FoodLabelParser()
    return _label_parser


def get_groq_client() -> GroqWhisperClient:
    global _groq_client
    if _groq_client is None:
        _groq_client = GroqWhisperClient()
    return _groq_client


def get_gipformer_engine() -> GipformerEngine:
    global _gipformer_engine
    if _gipformer_engine is None:
        _gipformer_engine = GipformerEngine()
    return _gipformer_engine


def warmup_smart_input_gpu() -> dict[str, Any]:
    """Preloads OCR and ASR models into GPU VRAM to eliminate cold-start latency."""
    global _ocr_pipeline
    import numpy as np

    try:
        import torch
        cuda_avail = torch.cuda.is_available()
        device_name = torch.cuda.get_device_name(0) if cuda_avail else "CPU"
    except Exception:
        cuda_avail = False
        device_name = "CPU"

    ocr = get_ocr_pipeline(use_gpu=cuda_avail)
    # Warm up OCR pipeline with synthetic 64x200 RGB canvas
    dummy_img = np.ones((64, 200, 3), dtype=np.uint8) * 255
    ocr.recognize_image(dummy_img)

    # Warm up Vietnamese text corrector (ProtonX CT2)
    corrector = get_corrector(use_gpu=cuda_avail)
    corrector.correct_text("Xin chao")

    vram_mb = 0.0
    if cuda_avail:
        try:
            import torch
            vram_mb = round(torch.cuda.memory_allocated() / (1024 ** 2), 2)
        except Exception:
            pass

    return {
        "cuda_available": cuda_avail,
        "device_name": device_name,
        "vram_allocated_mb": vram_mb,
        "ocr_engine": "PaddleOCR+VietOCR (CUDA)" if cuda_avail else "PaddleOCR+VietOCR (CPU)",
        "corrector_engine": f"welcomyou/distilled-protonx-vn-correction-ct2 ({corrector.device.upper()})",
        "status": "ready",
    }


def process_receipt_input(
    image_bytes: bytes | None = None,
    image_base64: str | None = None,
    receipt_text: str | None = None,
    sample_id: str | None = None,
    filename: str = "receipt.jpg",
) -> dict[str, Any]:
    """Processes receipt or food label from image upload, base64, raw text, or sample ID.

    Applies high-throughput preprocessing:
    - Downsamples high-res images to max 1600px
    - CLAHE contrast enhancement for faint receipts & reflective labels
    - Re-compresses to clean JPEG (quality 85)
    """
    if image_base64:
        try:
            clean_b64 = image_base64
            if "," in clean_b64:
                clean_b64 = clean_b64.split(",", 1)[1]
            image_bytes = base64.b64decode(clean_b64)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Lỗi giải mã ảnh Base64: {str(e)}",
                "items": [],
            }

    # 1. Handle Sample ID
    if sample_id:
        sample = next((s for s in SAMPLE_RECEIPTS if s["id"] == sample_id), None)
        if sample:
            raw = sample["raw_text"]
            is_label = sample.get("type") == "label" or "KLT:" in raw or "HSD:" in raw
            if is_label:
                label_item = get_label_parser().parse_label_text(raw)
                items = [_serialize_label_item(label_item)]
            else:
                items = parse_receipt_text(raw)

            return {
                "status": "success",
                "source": "sample_receipt",
                "store_name": sample.get("store_name", "Bách Hóa Xanh / Siêu Thị"),
                "title": sample["title"],
                "raw_text": raw,
                "items_count": len(items),
                "items": items,
            }

    # 2. Handle Image Bytes (LiveKit camera snapshot or uploaded file)
    if image_bytes:
        _, img_rgb, preprocess_stats = preprocess_image_bytes(
            image_bytes,
            max_dim=1600,
            quality=85,
            enhance_contrast=True,
        )
        ocr_res = get_ocr_pipeline().recognize_image(img_rgb)
        extracted_text = ocr_res.get("full_text", "")

        if "klt" in extracted_text.lower() or "hsd" in extracted_text.lower() or "nsx" in extracted_text.lower():
            label_item = get_label_parser().parse_label_text(extracted_text)
            items = [_serialize_label_item(label_item)]
        else:
            items = parse_receipt_text(extracted_text)

        return {
            "status": "success",
            "source": "live_camera_or_upload",
            "engine": ocr_res.get("engine", "PaddleOCR+VietOCR"),
            "raw_text": extracted_text,
            "items_count": len(items),
            "items": items,
            "preprocess_stats": preprocess_stats,
        }

    # 3. Handle Raw Text directly
    if receipt_text:
        raw = receipt_text.strip()
        if "klt" in raw.lower() or "hsd" in raw.lower() or "nsx" in raw.lower():
            label_item = get_label_parser().parse_label_text(raw)
            items = [_serialize_label_item(label_item)]
        else:
            items = parse_receipt_text(raw)

        return {
            "status": "success",
            "source": "text_input",
            "raw_text": raw,
            "items_count": len(items),
            "items": items,
        }

    return {
        "status": "error",
        "message": "Vui lòng cung cấp ảnh hóa đơn, ảnh nhãn mác Bách Hóa Xanh, hoặc chọn mẫu có sẵn.",
        "items": [],
    }


def process_voice_input(
    transcript: str | None = None,
    audio_bytes: bytes | None = None,
    audio_format: str = "wav",
    sample_id: str | None = None,
    engine: str = "groq_whisper",  # "groq_whisper" or "gipformer"
) -> dict[str, Any]:
    """Processes spoken Vietnamese voice input from audio, transcript or sample ID.

    Applies high-throughput preprocessing:
    - Downsamples to 16kHz mono FLAC via ffmpeg
    - Trims dead silence leading/trailing
    - Dispatches to Groq Whisper-large-v3-turbo or local Gipformer
    """
    start_time = time.time()
    text_to_process = ""
    title = "Giọng nói người dùng"
    engine_used = engine
    preprocess_stats = None

    # 1. Handle Sample ID
    if sample_id:
        sample = next((s for s in SAMPLE_VOICE_QUERIES if s["id"] == sample_id), None)
        if sample:
            text_to_process = sample["transcript"]
            title = sample["title"]
            engine_used = "sample_preset"

    # 2. Handle Audio Bytes upload or live recorded audio
    elif audio_bytes:
        try:
            flac_bytes, preprocess_stats = preprocess_audio_bytes(
                audio_bytes, input_format=audio_format, strip_silence=True
            )
        except Exception:
            flac_bytes = audio_bytes

        with tempfile.NamedTemporaryFile(suffix=".flac", delete=False) as tmp_audio:
            tmp_audio.write(flac_bytes)
            tmp_path = tmp_audio.name

        try:
            if engine == "gipformer":
                gip_res = get_gipformer_engine().transcribe_file(tmp_path)
                if gip_res.get("success"):
                    text_to_process = gip_res.get("text", "")
                else:
                    # Fallback to groq whisper if local gipformer not installed
                    groq_res = get_groq_client().transcribe_file(tmp_path)
                    text_to_process = groq_res.get("text", "")
                    engine_used = f"groq_whisper (fallback from gipformer: {gip_res.get('note', '')})"
            else:
                # Default: Groq Whisper Large V3 Turbo
                groq_res = get_groq_client().transcribe_file(tmp_path)
                text_to_process = groq_res.get("text", "")
                engine_used = "groq_whisper_turbo"
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    # 3. Handle Direct Text Transcript (from Web Speech API)
    elif transcript:
        text_to_process = transcript.strip()
        engine_used = "web_speech_api"

    if not text_to_process:
        return {
            "status": "error",
            "message": "Không nhận được nội dung giọng nói. Vui lòng thử nói lại, upload file âm thanh hoặc chọn mẫu.",
            "items": [],
        }

    # Vietnamese Text Correction (ProtonX CT2)
    corrector = get_corrector()
    corrected_transcript = corrector.correct_asr_transcript(text_to_process)
    effective_text = corrected_transcript or text_to_process

    # NLP culinary entity parsing
    items = parse_vietnamese_speech(effective_text)
    if not items and effective_text != text_to_process:
        items = parse_vietnamese_speech(text_to_process)

    latency_ms = round((time.time() - start_time) * 1000, 1)

    result = {
        "status": "success",
        "title": title,
        "engine": engine_used,
        "transcript": effective_text,
        "raw_transcript": text_to_process,
        "corrected_transcript": corrected_transcript,
        "correction_applied": bool(corrected_transcript and corrected_transcript != text_to_process),
        "correction_engine": f"welcomyou/distilled-protonx-vn-correction-ct2 ({corrector.device.upper()})",
        "latency_ms": latency_ms,
        "items_count": len(items),
        "items": items,
    }
    if preprocess_stats:
        result["preprocess_stats"] = preprocess_stats

    return result


def get_smart_input_samples() -> dict[str, Any]:
    """Returns sample receipts, Bách Hóa Xanh labels and voice phrases for UI 1-click demos."""
    return {
        "receipt_samples": SAMPLE_RECEIPTS,
        "voice_samples": SAMPLE_VOICE_QUERIES,
    }
