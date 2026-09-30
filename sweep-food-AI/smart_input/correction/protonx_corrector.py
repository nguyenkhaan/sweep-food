"""Vietnamese Text Correction using welcomyou/distilled-protonx-vn-correction-ct2.

Post-processing engine for both OCR and ASR.
Applies fast, sequence-to-sequence neural spelling and diacritics correction
using CTranslate2 quantized model (int8 / float16) on CUDA/CPU.

Includes domain safeguards against legal-text hallucinations (since the base model
was distilled from ProtonX legal documents) and preserves culinary terminology.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional, Sequence
import ctranslate2
from tokenizers import Tokenizer

DEFAULT_MODEL_DIR = Path(__file__).resolve().parent / "weights"

# Common culinary replacements & protections
# (Prevents legal domain words like 'theo luật' from overriding 'thịt heo')
CULINARY_PROTECTIONS = [
    (re.compile(r"\btheo\b", re.IGNORECASE), "heo", ["heo", "thit heo", "suon heo", "ba roi heo", "thịt heo", "sườn heo", "ba rọi heo", "nạc heo"]),
    (re.compile(r"\bcác hồi\b", re.IGNORECASE), "cá hồi", ["cá hồi", "ca hoi"]),
    (re.compile(r"\bcán nước\b", re.IGNORECASE), "cá nục", ["cá nục", "ca nuc"]),
    (re.compile(r"\bdầu phụ\b", re.IGNORECASE), "đậu phụ", ["đậu phụ", "dau phu", "đậu hũ", "dau hu"]),
    (re.compile(r"\bcăn cá\b", re.IGNORECASE), "cân cà", ["cà chua", "ca chua"]),
    (re.compile(r"\bbộ rau cái\b", re.IGNORECASE), "bó rau cải", ["rau cải", "rau cai"]),
    (re.compile(r"\bbò xanh\b", re.IGNORECASE), "bẹ xanh", ["cải bẹ", "cải bẹ xanh", "cải bọ"]),
]

LEGAL_HALLUCINATION_TRIGGERS = [
    "cộng hòa xã hội",
    "chủ nghĩa việt nam",
    "độc lập - tự do",
    "độc lập tự do",
    "hạnh phúc",
    "nghị định số",
    "thông tư số",
    "bộ luật",
    "chính phủ ban hành",
    "quy định tại",
]


class VietnameseTextCorrector:
    """Fast Vietnamese spelling and diacritics corrector powered by CTranslate2."""

    def __init__(
        self,
        model_dir: Optional[str | Path] = None,
        use_gpu: bool = True,
        compute_type: str = "default",
    ):
        self.model_dir = Path(model_dir) if model_dir else DEFAULT_MODEL_DIR
        self.use_gpu = use_gpu
        self.compute_type = compute_type
        self._translator: Optional[ctranslate2.Translator] = None
        self._tokenizer: Optional[Tokenizer] = None
        self._init_done = False
        self._device = "cpu"

    def _init_model(self):
        if self._init_done:
            return

        tokenizer_path = self.model_dir / "tokenizer.json"
        model_bin = self.model_dir / "model.bin"
        if not tokenizer_path.exists() or not model_bin.exists():
            self._init_done = True
            return

        # Setup Tokenizer
        self._tokenizer = Tokenizer.from_file(str(tokenizer_path))

        # Setup CTranslate2 Translator
        device = "cpu"
        if self.use_gpu:
            try:
                import torch
                if torch.cuda.is_available():
                    device = "cuda"
            except Exception:
                device = "cpu"

        try:
            self._translator = ctranslate2.Translator(
                str(self.model_dir),
                device=device,
                compute_type=self.compute_type,
                intra_threads=2,
            )
            self._device = device
        except Exception:
            # Fallback to CPU if CUDA provider encounters an issue
            self._translator = ctranslate2.Translator(
                str(self.model_dir),
                device="cpu",
                intra_threads=4,
            )
            self._device = "cpu"

        self._init_done = True

    @property
    def device(self) -> str:
        self._init_model()
        return self._device

    def correct_text(self, text: str) -> str:
        """General text correction for a single phrase or sentence."""
        return self.correct_asr_transcript(text)

    def correct_batch(self, texts: Sequence[str], beam_size: int = 1) -> list[str]:
        """Raw sequence-to-sequence translation for a batch of strings."""
        self._init_model()
        if not texts or self._translator is None or self._tokenizer is None:
            return list(texts)

        processed_indices = []
        batch_tokens = []

        for idx, text in enumerate(texts):
            clean = text.strip()
            # Skip empty, pure digits, or tiny tokens
            if not clean or clean.isdigit() or len(clean) <= 2:
                continue
            processed_indices.append(idx)
            tokens = self._tokenizer.encode(clean).tokens + ["</s>"]
            batch_tokens.append(tokens)

        if not batch_tokens:
            return list(texts)

        try:
            results = self._translator.translate_batch(
                batch_tokens,
                beam_size=beam_size,
                max_decoding_length=128,
            )

            outputs = list(texts)
            for orig_idx, res in zip(processed_indices, results):
                if not res.hypotheses:
                    continue
                hyp = res.hypotheses[0]
                out_tokens = [t for t in hyp if t != "</s>"]
                ids = [self._tokenizer.token_to_id(t) for t in out_tokens if self._tokenizer.token_to_id(t) is not None]
                corrected = self._tokenizer.decode(ids).strip()
                if corrected:
                    outputs[orig_idx] = corrected

            return outputs
        except Exception:
            return list(texts)

    def _apply_safeguards(self, original: str, candidate: str, was_upper: bool = False) -> str:
        """Protects against hallucinations and restores culinary vocabulary."""
        orig_clean = original.strip()
        cand_clean = candidate.strip()
        if not cand_clean or cand_clean == orig_clean:
            return original

        # 1. Hallucination check: length explosion
        orig_words = orig_clean.split()
        cand_words = cand_clean.split()
        if len(cand_words) > len(orig_words) * 2 + 2:
            return original

        # 2. Check for legal document hallucination
        cand_low = cand_clean.lower()
        if any(trig in cand_low for trig in LEGAL_HALLUCINATION_TRIGGERS):
            return original

        # 3. Culinary protections
        orig_low = orig_clean.lower()
        result = cand_clean
        for pat, rep, triggers in CULINARY_PROTECTIONS:
            if any(trig in orig_low for trig in triggers):
                result = pat.sub(rep, result)

        # 4. If original was all uppercase, restore uppercase or titlecase
        if was_upper:
            # If original line was uppercase, keep uppercase format
            result = result.upper()

        return result

    def correct_asr_transcript(self, transcript: str) -> str:
        """Post-processes Vietnamese ASR voice transcript.

        Fixes missing tone marks, colloquial diacritics, and light spelling errors.
        """
        clean = (transcript or "").strip()
        if not clean:
            return ""

        # Normalize double spaces
        clean = re.sub(r"\s+", " ", clean)

        # Translate single sentence
        raw_corr = self.correct_batch([clean])
        candidate = raw_corr[0] if raw_corr else clean

        # Apply culinary safeguards
        return self._apply_safeguards(clean, candidate, was_upper=False)

    def correct_ocr_lines(self, lines: Sequence[str]) -> list[str]:
        """Post-processes OCR lines (receipts, food labels) in an efficient single batch."""
        if not lines:
            return []

        # Prepare normalized inputs for model
        need_correction_indices = []
        model_inputs = []
        is_upper_flags = []

        for idx, line in enumerate(lines):
            l = line.strip()
            # Skip lines that are numbers, dates, times, bar codes, or short table headers
            if (
                not l
                or len(l) <= 2
                or l.isdigit()
                or re.match(r"^[\d\.,\s\:\/\-\%]+$", l)
                or l.lower() in ("sl", "kg", "g", "vat", "vnd", "đ", "đvt")
            ):
                continue

            need_correction_indices.append(idx)
            is_upper = l.isupper()
            is_upper_flags.append(is_upper)
            # Normalize all-caps to lowercase before model ingestion to prevent legal header hallucination
            model_inputs.append(l.lower() if is_upper else l)

        if not model_inputs:
            return list(lines)

        # Run translation in one parallel batch
        corrected_batch = self.correct_batch(model_inputs)

        final_lines = list(lines)
        for orig_idx, is_up, model_in, corr in zip(
            need_correction_indices, is_upper_flags, model_inputs, corrected_batch
        ):
            orig_text = lines[orig_idx]
            safe_text = self._apply_safeguards(orig_text, corr, was_upper=is_up)
            final_lines[orig_idx] = safe_text

        return final_lines

    def correct_ocr_text(self, multiline_text: str) -> str:
        """Processes multiline OCR text block, returning corrected multiline string."""
        if not multiline_text:
            return ""
        lines = multiline_text.splitlines()
        corrected_lines = self.correct_ocr_lines(lines)
        return "\n".join(corrected_lines)


# Global singleton instance
_corrector_instance: Optional[VietnameseTextCorrector] = None


def get_corrector(use_gpu: Optional[bool] = None) -> VietnameseTextCorrector:
    """Returns the global singleton VietnameseTextCorrector instance."""
    global _corrector_instance
    if _corrector_instance is None:
        if use_gpu is None:
            try:
                import torch
                use_gpu = torch.cuda.is_available()
            except Exception:
                use_gpu = False
        _corrector_instance = VietnameseTextCorrector(use_gpu=use_gpu)
    return _corrector_instance
