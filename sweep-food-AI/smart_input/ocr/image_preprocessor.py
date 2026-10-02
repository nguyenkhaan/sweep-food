"""Image Preprocessor for Smart Input OCR.

Optimizes images from image upload and camera snapshots:
1. Downsampling high-resolution smartphone photos (up to 4000x3000) to max 1600px via cv2.INTER_AREA.
2. Contrast-Limited Adaptive Histogram Equalization (CLAHE) on the L-channel to enhance faint receipts and food packaging labels.
3. High-efficiency JPEG compression (quality 85) to reduce payload size by >90% while preserving text legibility.
"""

from __future__ import annotations

import io
from typing import Any, Tuple
import cv2
import numpy as np
from PIL import Image


def preprocess_ocr_image(
    image: np.ndarray,
    max_dim: int = 1600,
    enhance_contrast: bool = True,
) -> Tuple[np.ndarray, dict[str, Any]]:
    """Preprocess an OpenCV image (BGR or RGB) for optimal OCR accuracy and throughput.

    Args:
        image: Input image array (H, W, C) in BGR or RGB.
        max_dim: Maximum width or height allowed before downsampling.
        enhance_contrast: Whether to apply CLAHE contrast enhancement.

    Returns:
        (processed_image_rgb, stats_dict)
    """
    if image is None or image.size == 0:
        raise ValueError("Empty image passed to preprocess_ocr_image")

    h, w = image.shape[:2]
    orig_shape = (h, w)
    scale_factor = 1.0

    # 1. Downsample if larger than max_dim
    if max(h, w) > max_dim:
        scale_factor = max_dim / float(max(h, w))
        new_w = max(1, int(round(w * scale_factor)))
        new_h = max(1, int(round(h * scale_factor)))
        # cv2.INTER_AREA is the golden standard for downsampling without moiré/aliasing
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    else:
        resized = image.copy()

    cur_h, cur_w = resized.shape[:2]

    # Convert to RGB if 3 channels
    if len(resized.shape) == 2:
        img_rgb = cv2.cvtColor(resized, cv2.COLOR_GRAY2RGB)
    elif resized.shape[2] == 4:
        img_rgb = cv2.cvtColor(resized, cv2.COLOR_BGRA2RGB)
    else:
        # Assuming input is BGR from cv2.imdecode
        img_rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)

    # VietOCR and the fallback detector expect dark text on a light background.
    # Normalize dark-mode screenshots before contrast enhancement.
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    polarity_inverted = float(np.median(gray)) < 127
    if polarity_inverted:
        img_rgb = cv2.bitwise_not(img_rgb)

    # 2. CLAHE Contrast Enhancement for faint receipts and glossy food packaging
    if enhance_contrast:
        try:
            lab = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2LAB)
            l_channel, a_channel, b_channel = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            cl = clahe.apply(l_channel)
            merged_lab = cv2.merge((cl, a_channel, b_channel))
            img_rgb = cv2.cvtColor(merged_lab, cv2.COLOR_LAB2RGB)
        except Exception:
            pass  # Fallback to unenhanced RGB

    stats = {
        "original_width": w,
        "original_height": h,
        "processed_width": cur_w,
        "processed_height": cur_h,
        "scale_factor": round(scale_factor, 3),
        "downscaled": scale_factor < 1.0,
        "polarity_inverted": polarity_inverted,
        "contrast_enhanced": enhance_contrast,
    }

    return img_rgb, stats


def preprocess_image_bytes(
    image_bytes: bytes,
    max_dim: int = 1600,
    quality: int = 85,
    enhance_contrast: bool = True,
) -> Tuple[bytes, np.ndarray, dict[str, Any]]:
    """Decode, downscale, enhance contrast, and re-compress image bytes.

    Args:
        image_bytes: Raw input image bytes (JPEG, PNG, WebP, etc.)
        max_dim: Maximum dimension limit.
        quality: JPEG output quality (0-100).
        enhance_contrast: Whether to apply CLAHE.

    Returns:
        (compressed_jpeg_bytes, processed_image_rgb, stats_dict)
    """
    orig_bytes_len = len(image_bytes)
    nparr = np.frombuffer(image_bytes, np.uint8)
    img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img_bgr is None:
        raise ValueError("Failed to decode image from provided bytes")

    img_rgb, stats = preprocess_ocr_image(
        img_bgr,
        max_dim=max_dim,
        enhance_contrast=enhance_contrast,
    )

    # Re-encode to optimized JPEG for fast network & downstream transmission
    img_bgr_out = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
    encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), quality, int(cv2.IMWRITE_JPEG_OPTIMIZE), 1]
    success, encoded_buf = cv2.imencode(".jpg", img_bgr_out, encode_params)

    if not success:
        # Fallback to original bytes
        compressed_bytes = image_bytes
    else:
        compressed_bytes = encoded_buf.tobytes()

    new_bytes_len = len(compressed_bytes)
    savings_pct = round((1.0 - (new_bytes_len / max(1, orig_bytes_len))) * 100, 1) if orig_bytes_len > 0 else 0.0

    stats.update({
        "original_size_kb": round(orig_bytes_len / 1024, 1),
        "compressed_size_kb": round(new_bytes_len / 1024, 1),
        "savings_percent": max(0.0, savings_pct),
        "format": "JPEG",
        "quality": quality,
    })

    return compressed_bytes, img_rgb, stats
