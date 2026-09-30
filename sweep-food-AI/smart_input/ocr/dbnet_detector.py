"""DBNet ONNX Text Detector for Receipts and Food Packaging.

Self-contained ONNX runtime detector using DBNet (Differentiable Binarization).
Provides high-accuracy text bounding boxes even for crumpled, folded, or low-contrast receipts.
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any, Optional
import cv2
import numpy as np
import onnxruntime as ort

from smart_input.ocr.dbnet import operators
from smart_input.ocr.dbnet.postprocess import build_post_process


def transform(data, ops=None):
    if ops is None:
        ops = []
    for op in ops:
        data = op(data)
        if data is None:
            return None
    return data


def create_operators(op_param_list):
    ops = []
    for operator in op_param_list:
        op_name = list(operator)[0]
        param = {} if operator[op_name] is None else operator[op_name]
        op = getattr(operators, op_name)(**param)
        ops.append(op)
    return ops


class DBNetTextDetector:
    """High-accuracy DBNet text bounding box detector using ONNX Runtime."""

    def __init__(self, model_path: Optional[str | Path] = None, use_gpu: bool = True):
        if model_path is None:
            model_path = Path(__file__).resolve().parent / "weights" / "det.onnx"
        self.model_path = Path(model_path).resolve()
        if not self.model_path.exists():
            raise FileNotFoundError(f"DBNet ONNX model not found: {self.model_path}")

        # Setup ONNX Runtime Session
        options = ort.SessionOptions()
        options.enable_cpu_mem_arena = False
        options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        options.intra_op_num_threads = 4

        providers = ['CPUExecutionProvider']
        if use_gpu:
            try:
                import torch
                if torch.cuda.is_available():
                    providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
            except Exception:
                pass

        try:
            self.session = ort.InferenceSession(str(self.model_path), options=options, providers=providers)
        except Exception:
            # Fallback to CPU execution provider
            self.session = ort.InferenceSession(str(self.model_path), options=options, providers=['CPUExecutionProvider'])

        self.input_tensor = self.session.get_inputs()[0]

        # Setup preprocessing
        pre_process_list = [
            {
                'DetResizeForTest': {
                    'limit_side_len': 960,
                    'limit_type': "max",
                }
            },
            {
                'NormalizeImage': {
                    'std': [0.229, 0.224, 0.225],
                    'mean': [0.485, 0.456, 0.406],
                    'scale': '1./255.',
                    'order': 'hwc'
                }
            },
            {'ToCHWImage': None},
            {'KeepKeys': {'keep_keys': ['image', 'shape']}}
        ]

        # Setup postprocessing
        postprocess_params = {
            "name": "DBPostProcess",
            "thresh": 0.3,
            "box_thresh": 0.5,
            "max_candidates": 1000,
            "unclip_ratio": 1.5,
            "use_dilation": False,
            "score_mode": "fast",
            "box_type": "quad"
        }
        self.postprocess_op = build_post_process(postprocess_params)
        self.preprocess_op = create_operators(pre_process_list)

    def order_points_clockwise(self, pts):
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        tmp = np.delete(pts, (np.argmin(s), np.argmax(s)), axis=0)
        diff = np.diff(np.array(tmp), axis=1)
        rect[1] = tmp[np.argmin(diff)]
        rect[3] = tmp[np.argmax(diff)]
        return rect

    def clip_det_res(self, points, img_height, img_width):
        for pno in range(points.shape[0]):
            points[pno, 0] = int(min(max(points[pno, 0], 0), img_width - 1))
            points[pno, 1] = int(min(max(points[pno, 1], 0), img_height - 1))
        return points

    def filter_boxes(self, dt_boxes, image_shape):
        img_height, img_width = image_shape[0:2]
        dt_boxes_new = []
        for box in dt_boxes:
            if isinstance(box, list):
                box = np.array(box)
            box = self.order_points_clockwise(box)
            box = self.clip_det_res(box, img_height, img_width)
            rect_width = int(np.linalg.norm(box[0] - box[1]))
            rect_height = int(np.linalg.norm(box[0] - box[3]))
            if rect_width <= 4 or rect_height <= 4:
                continue
            dt_boxes_new.append(box)
        return dt_boxes_new

    def detect(self, img_bgr: np.ndarray) -> list[dict[str, Any]]:
        """Detect text boxes from a BGR image."""
        ori_im = img_bgr.copy()
        data = {'image': img_bgr}

        data = transform(data, self.preprocess_op)
        img, shape_list = data
        if img is None:
            return []

        img = np.expand_dims(img, axis=0)
        shape_list = np.expand_dims(shape_list, axis=0)
        img = img.copy()

        input_dict = {self.input_tensor.name: img}
        outputs = self.session.run(None, input_dict)

        post_result = self.postprocess_op({"maps": outputs[0]}, shape_list)
        raw_points = post_result[0]['points']
        boxes = self.filter_boxes(raw_points, ori_im.shape)

        return [{"box": np.array(b, dtype=np.float32), "confidence": 0.95} for b in boxes]
