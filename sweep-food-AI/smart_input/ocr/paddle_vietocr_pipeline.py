"""PaddleOCR text detector + VietOCR text recognizer pipeline.

References:
    G:\\github\\AIC_ProcessData\\ocr_nhan\\predict_pipeline.py

Features:
- Polygon / Quad point ordering and perspective crop with padding
- Horizontal box merging for receipt and product label text lines
- Line sorting by vertical coordinate and baseline
- PaddleOCR detector with fallback OpenCV text line segmenter
- VietOCR recognition with vgg_transformer / seq2seq
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Optional, Sequence
import cv2
import numpy as np
from PIL import Image

try:
    from vietocr.tool.predictor import Predictor
    from vietocr.tool.config import Cfg
    HAS_VIETOCR = True
except ImportError:
    HAS_VIETOCR = False

try:
    from paddleocr import PaddleOCR
    HAS_PADDLEOCR = True
except ImportError:
    HAS_PADDLEOCR = False


def order_points_clockwise(points: Any) -> np.ndarray:
    """Order 4 points clockwise starting from top-left."""
    pts = np.asarray(points, dtype="float32").reshape(4, 2)
    rect = np.zeros((4, 2), dtype="float32")
    point_sum = pts.sum(axis=1)
    rect[0] = pts[np.argmin(point_sum)]
    rect[2] = pts[np.argmax(point_sum)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect


def clip_box(points: Any, width: int, height: int) -> np.ndarray:
    """Clip coordinates inside image boundary."""
    pts = np.asarray(points, dtype="float32").reshape(4, 2)
    pts[:, 0] = np.clip(pts[:, 0], 0, max(0, width - 1))
    pts[:, 1] = np.clip(pts[:, 1], 0, max(0, height - 1))
    return pts


def box_size(points: Any) -> tuple[float, float]:
    """Calculate width and height of a quad box."""
    pts = order_points_clockwise(points)
    w = max(np.linalg.norm(pts[0] - pts[1]), np.linalg.norm(pts[2] - pts[3]))
    h = max(np.linalg.norm(pts[0] - pts[3]), np.linalg.norm(pts[1] - pts[2]))
    return float(w), float(h)


def perspective_crop(
    image_rgb: np.ndarray,
    box: Any,
    padding_ratio: float = 0.08,
    upscale_min_height: int = 24,
) -> np.ndarray:
    """Rectify a quad text box and enlarge short crops with Lanczos."""
    points = order_points_clockwise(box)
    h_img, w_img = image_rgb.shape[:2]

    raw_h = max(np.linalg.norm(points[0] - points[3]), np.linalg.norm(points[1] - points[2]))
    pad_y = max(2.0, raw_h * padding_ratio)
    pad_x = max(3.0, raw_h * padding_ratio)

    center = np.mean(points, axis=0)
    expanded = np.zeros_like(points)
    for i in range(4):
        vec = points[i] - center
        norm = np.linalg.norm(vec)
        if norm > 0:
            scale_x = 1.0 + (pad_x / max(1.0, norm))
            scale_y = 1.0 + (pad_y / max(1.0, norm))
            expanded[i, 0] = center[0] + vec[0] * scale_x
            expanded[i, 1] = center[1] + vec[1] * scale_y
        else:
            expanded[i] = points[i]

    expanded[:, 0] = np.clip(expanded[:, 0], 0, w_img - 1)
    expanded[:, 1] = np.clip(expanded[:, 1], 0, h_img - 1)

    points = order_points_clockwise(expanded)
    crop_w = int(round(max(np.linalg.norm(points[0] - points[1]), np.linalg.norm(points[2] - points[3]))))
    crop_h = int(round(max(np.linalg.norm(points[0] - points[3]), np.linalg.norm(points[1] - points[2]))))
    crop_w = max(1, crop_w)
    crop_h = max(1, crop_h)

    target = np.float32([[0, 0], [crop_w, 0], [crop_w, crop_h], [0, crop_h]])
    matrix = cv2.getPerspectiveTransform(points, target)
    crop = cv2.warpPerspective(
        image_rgb,
        matrix,
        (crop_w, crop_h),
        borderMode=cv2.BORDER_REPLICATE,
        flags=cv2.INTER_CUBIC,
    )
    if crop.shape[0] < upscale_min_height:
        scale = upscale_min_height / max(1, crop.shape[0])
        crop = cv2.resize(
            crop,
            (max(1, round(crop.shape[1] * scale)), upscale_min_height),
            interpolation=cv2.INTER_LANCZOS4,
        )
    return crop


def sort_text_boxes(boxes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sort text boxes top-to-bottom, left-to-right."""
    if not boxes:
        return []
    heights = [box_size(b["box"])[1] for b in boxes]
    median_h = sorted(heights)[len(heights) // 2] if heights else 15.0
    same_line_threshold = max(10.0, median_h * 0.5)

    ordered = sorted(
        boxes,
        key=lambda item: (
            order_points_clockwise(item["box"])[0][1],
            order_points_clockwise(item["box"])[0][0],
        ),
    )
    for idx in range(len(ordered) - 1):
        for inner in range(idx, -1, -1):
            cur = order_points_clockwise(ordered[inner]["box"])
            nxt = order_points_clockwise(ordered[inner + 1]["box"])
            if abs(float(nxt[0][1] - cur[0][1])) < same_line_threshold and nxt[0][0] < cur[0][0]:
                ordered[inner], ordered[inner + 1] = ordered[inner + 1], ordered[inner]
            else:
                break
    return ordered


def detect_text_regions_fallback(image_rgb: np.ndarray) -> list[dict[str, Any]]:
    """OpenCV contour/morphology based line text detector for fallback."""
    gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    # Adaptive threshold
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 8
    )
    # Horizontal kernel to connect characters on the same line
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 3))
    dilated = cv2.dilate(thresh, kernel, iterations=2)

    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []
    h_img, w_img = image_rgb.shape[:2]

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 20 and h > 8 and (w * h) > 200:
            box = np.array([
                [x, y],
                [x + w, y],
                [x + w, y + h],
                [x, y + h]
            ], dtype=np.float32)
            boxes.append({"box": box, "confidence": 0.85})

    return sort_text_boxes(boxes)


class PaddleVietOCRPipeline:
    """Full OCR Pipeline combining DBNet ONNX text detector and VietOCR recognizer."""

    def __init__(self, use_gpu: bool = False, config_name: str = "vgg_transformer"):
        self.use_gpu = use_gpu
        self.config_name = config_name
        self._recognizer: Optional[Predictor] = None
        self._dbnet_detector = None
        self._detector = None
        self._init_done = False

    def _init_models(self):
        if self._init_done:
            return

        # 1. Initialize VietOCR Recognizer
        if HAS_VIETOCR:
            try:
                config_dir = Path(__file__).resolve().parent / "config"
                base_cfg_path = config_dir / "base.yml"
                model_cfg_path = config_dir / f"{self.config_name.replace('_', '-')}.yml"
                if not model_cfg_path.exists():
                    model_cfg_path = config_dir / "vgg-transformer.yml"

                if base_cfg_path.exists() and model_cfg_path.exists():
                    cfg = Cfg.load_config_from_file(str(base_cfg_path))
                    model_cfg = Cfg.load_config_from_file(str(model_cfg_path))
                    cfg.update(model_cfg)
                else:
                    cfg = Cfg.load_config_from_name(self.config_name)

                # Prioritize local weights to eliminate any network requests to vocr.vn
                local_weights = Path(__file__).resolve().parent / "weights" / "vgg_transformer.pth"
                if local_weights.exists():
                    cfg["weights"] = str(local_weights)

                device = "cuda:0" if self.use_gpu else "cpu"
                cfg["device"] = device
                cfg["predictor"]["beamsearch"] = False
                self._recognizer = Predictor(cfg)
            except Exception as e:
                raise RuntimeError("VietOCR recognizer could not be initialized") from e
        else:
            raise RuntimeError("VietOCR is not installed")

        # 2. Initialize DBNet ONNX Detector (Deep Learning Binarization)
        try:
            from smart_input.ocr.dbnet_detector import DBNetTextDetector
            det_weights = Path(__file__).resolve().parent / "weights" / "det.onnx"
            if det_weights.exists():
                self._dbnet_detector = DBNetTextDetector(model_path=det_weights, use_gpu=self.use_gpu)
        except Exception as e:
            print(f"[DBNet Warning] Failed to init DBNet detector: {e}")
            self._dbnet_detector = None

        self._init_done = True

    def detect_boxes(self, image_rgb: np.ndarray) -> list[dict[str, Any]]:
        """Detect text bounding boxes using DBNet ONNX or fallback."""
        self._init_models()
        if self._dbnet_detector is not None:
            try:
                img_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
                raw_boxes = self._dbnet_detector.detect(img_bgr)
                if raw_boxes:
                    return sort_text_boxes(raw_boxes)
            except Exception as e:
                print(f"[DBNet Warning] Detection error: {e}")

        return detect_text_regions_fallback(image_rgb)

    def recognize_image(self, image_rgb: np.ndarray) -> dict[str, Any]:
        """Run complete detection + recognition pipeline on an RGB image."""
        self._init_models()
        detected = self.detect_boxes(image_rgb)

        lines = []
        if self._recognizer is not None:
            for item in detected:
                crop = perspective_crop(image_rgb, item["box"])
                pil_img = Image.fromarray(crop)
                try:
                    text, prob = self._recognizer.predict(pil_img, return_prob=True)
                    text_str = str(text).strip()
                    if text_str:
                        lines.append({
                            "text": text_str,
                            "prob": float(prob) if prob is not None else 1.0,
                            "box": item["box"].tolist(),
                        })
                except Exception:
                    continue

        full_text = "\n".join([l["text"] for l in lines])
        engine_label = "DBNet+VietOCR" if self._dbnet_detector else "VietOCR_Fallback"
        if self.use_gpu:
            engine_label += " (CUDA)"
        return {
            "full_text": full_text,
            "lines": lines,
            "num_boxes": len(detected),
            "engine": engine_label,
        }
