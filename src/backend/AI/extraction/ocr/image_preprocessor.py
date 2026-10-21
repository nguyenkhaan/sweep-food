"""Image preprocessing for AI OCR extraction using Pillow."""

from __future__ import annotations

import base64
import io
import logging
from typing import Any

from PIL import Image, ImageOps, UnidentifiedImageError

logger = logging.getLogger(__name__)


def preprocess_image_bytes(
    image_bytes: bytes,
    max_dim: int = 1600,
    quality: int = 85,
    enhance_contrast: bool = True,
) -> tuple[bytes, dict[str, Any]]:
    """Decode, downscale to max_dim, enhance contrast, and re-encode image bytes.

    Args:
        image_bytes: Raw input image bytes (JPEG, PNG, WebP, etc.).
        max_dim: Maximum width or height constraint.
        quality: WebP/JPEG encoding quality (1-100).
        enhance_contrast: Whether to apply autocontrast for faint text.

    Returns:
        Tuple of (compressed_image_bytes, stats_dict).
    """
    if not image_bytes:
        raise ValueError("Image bytes must not be empty.")

    try:
        img = Image.open(io.BytesIO(image_bytes))
    except (UnidentifiedImageError, OSError, ValueError):
        # Fallback for raw/mock bytes: pass through directly
        return image_bytes, {
            "original_width": 0,
            "original_height": 0,
            "processed_width": 0,
            "processed_height": 0,
            "downscaled": False,
        }

    # Ensure RGB orientation/channels
    if img.mode != "RGB":
        img = img.convert("RGB")

    orig_w, orig_h = img.size
    downscaled = False

    if max(orig_w, orig_h) > max_dim:
        scale = max_dim / float(max(orig_w, orig_h))
        new_w = max(1, round(orig_w * scale))
        new_h = max(1, round(orig_h * scale))
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        downscaled = True

    cur_w, cur_h = img.size

    if enhance_contrast:
        try:
            img = ImageOps.autocontrast(img)
        except (OSError, ValueError) as exc:
            logger.debug("Image autocontrast skipped: %s", exc)

    out_buf = io.BytesIO()
    try:
        img.save(out_buf, format="WEBP", quality=quality)
    except (OSError, ValueError):
        # Fallback to JPEG if WEBP writer is unavailable
        out_buf = io.BytesIO()
        img.save(out_buf, format="JPEG", quality=quality)

    compressed_bytes = out_buf.getvalue()
    stats: dict[str, Any] = {
        "original_width": orig_w,
        "original_height": orig_h,
        "processed_width": cur_w,
        "processed_height": cur_h,
        "downscaled": downscaled,
    }
    return compressed_bytes, stats


def encode_image_to_base64(
    image_bytes: bytes,
    max_dim: int = 1600,
    quality: int = 85,
) -> tuple[str, dict[str, Any]]:
    """Preprocess image and return base64 encoded string with stats."""
    comp_bytes, stats = preprocess_image_bytes(
        image_bytes, max_dim=max_dim, quality=quality
    )
    b64_str = base64.b64encode(comp_bytes).decode("utf-8")
    return b64_str, stats
