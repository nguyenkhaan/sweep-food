"""Groq Vision OCR Pipeline using Qwen (qwen/qwen3.8-27b).

Completely replaces PaddleOCR + VietOCR local pipeline.
Performs basic image preprocessing (resize, JPEG compression, base64)
and calls the Groq Cloud API:
    client = Groq()
    completion = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[...],
        temperature=0.6,
        max_completion_tokens=2048,
        top_p=0.95,
        reasoning_effort="default",
        stream=True,
        stop=None
    )
"""

from __future__ import annotations

import base64
import json
import os
import re
from pathlib import Path
from typing import Any, Optional
import cv2
import numpy as np

try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False


def _get_groq_api_key() -> str:
    """Retrieve GROQ_API_KEY from environment or .env file."""
    key = os.environ.get("GROQ_API_KEY", "")
    if key:
        return key

    # Check project .env
    for parent in [Path.cwd(), Path(__file__).resolve().parents[2]]:
        env_file = parent / ".env"
        if env_file.exists():
            try:
                with open(env_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip().startswith("GROQ_API_KEY="):
                            k = line.strip().split("=", 1)[1].strip("\"'")
                            if k:
                                os.environ["GROQ_API_KEY"] = k
                                return k
            except Exception:
                pass
    return ""


class GroqVisionOCR:
    """High-accuracy Groq Cloud Vision OCR using Qwen (qwen/qwen3.8-27b)."""

    def __init__(self, api_key: Optional[str] = None, model: str = "qwen/qwen3.8-27b"):
        self.api_key = api_key or _get_groq_api_key()
        self.model = model
        self.client: Optional[Groq] = None
        if HAS_GROQ and self.api_key:
            self.client = Groq(api_key=self.api_key)

    def is_available(self) -> bool:
        return self.client is not None

    def preprocess_image(
        self,
        image_bytes: bytes,
        max_dim: int = 1600,
        quality: int = 85,
    ) -> tuple[str, dict[str, Any]]:
        """Basic image preprocessing: downsample to max_dim, WebP 85 compression, base64."""
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            b64 = base64.b64encode(image_bytes).decode("utf-8")
            return b64, {"width": 0, "height": 0, "downscaled": False}

        h, w = img.shape[:2]
        downscaled = False
        if max(h, w) > max_dim:
            scale = max_dim / float(max(h, w))
            new_w = max(1, int(round(w * scale)))
            new_h = max(1, int(round(h * scale)))
            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
            downscaled = True

        cur_h, cur_w = img.shape[:2]

        # WebP compression (>50% smaller than JPEG at identical quality, sharp text edges)
        encode_params = [int(cv2.IMWRITE_WEBP_QUALITY), quality]
        success, buf = cv2.imencode(".webp", img, encode_params)
        if success:
            b64 = base64.b64encode(buf.tobytes()).decode("utf-8")
        else:
            b64 = base64.b64encode(image_bytes).decode("utf-8")
        stats = {
            "original_width": w,
            "original_height": h,
            "processed_width": cur_w,
            "processed_height": cur_h,
            "downscaled": downscaled,
        }
        return b64, stats

    def recognize_image_bytes(
        self,
        image_bytes: bytes,
        max_dim: int = 1600,
    ) -> dict[str, Any]:
        """Perform basic preprocessing and query Groq Vision API."""
        if not self.is_available():
            self.api_key = _get_groq_api_key()
            if HAS_GROQ and self.api_key:
                self.client = Groq(api_key=self.api_key)
            else:
                return {
                    "status": "error",
                    "message": "Groq client chưa được khởi tạo hoặc thiếu GROQ_API_KEY trong .env",
                    "items": [],
                    "raw_text": "",
                }

        b64_str, stats = self.preprocess_image(image_bytes, max_dim=max_dim)

        prompt = (
            "Bạn là hệ thống OCR bóc tách thông tin thực phẩm siêu thị Việt Nam.\n"
            "Hãy đọc toàn bộ văn bản trong ảnh (tem nhãn bao bì hoặc hóa đơn mua sắm) và trích xuất thành định dạng JSON chuẩn.\n\n"
            "YÊU CẦU QUAN TRỌNG VỀ ĐỘ CHÍNH XÁC:\n"
            "1. TÊN THỰC PHẨM (name): Cố gắng nhận diện RAW đúng nguyên văn từng chữ như in trên ảnh. "
            "Nếu chữ in KHÔNG CÓ DẤU (ví dụ: TOM THE NC, THIT OC MONG TAY, CA BASA MINI, DUI GA GOC TU, CHAN GIO HEO, XUONG HEO CO THIT) "
            "thì BẮT BUỘC GIỮ NGUYÊN RAW KHÔNG DẤU, tuyệt đối KHÔNG tự thêm dấu hay đoán từ. "
            "Nếu chữ in CÓ DẤU (ví dụ: Đậu rồng vỉ 200g, Chả cá Nha Trang, Má đùi gà) thì giữ đúng chữ có dấu đó.\n"
            "2. KHỐI LƯỢNG (quantity_g): Phải cố gắng nhận diện và tính toán thật ĐÚNG, quy đổi chính xác ra số gram thực (float). "
            "Đọc kỹ chỉ số in cạnh 'KL:', 'KLT:', 'Khối lượng', 'Trọng lượng' hoặc khối lượng tịnh. "
            "Ví dụ: '0,298 Kg' -> 298.0; '0,384 Kg' -> 384.0; '0.268 kg' -> 268.0; '500g' -> 500.0; '0,748 Kg' -> 748.0; '0.356 kg' -> 356.0. "
            "Đảm bảo không bị sai đơn vị (lưu ý số thập phân kg nhân 1000 để ra gram).\n"
            "3. HẠN DÙNG VÀ GHI CHÚ (expiry_date, hours_to_expire, note): Cố gắng nhận diện thật ĐÚNG ngày hết hạn (HSD), "
            "ngày đóng gói/sản xuất (NĐG/NSX), hoặc hạn bảo quản (ví dụ '3 ngày kể từ NĐG'). "
            "Định dạng expiry_date chuẩn DD/MM/YYYY nếu có. "
            "Ghi chú (note) ghi rõ đầy đủ thông tin HSD và NĐG/NSX đọc được trên ảnh (ví dụ: 'HSD: 02/10/2026 | NĐG: 02/10/2026').\n\n"
            "Trả về DUY NHẤT một khối JSON hợp lệ theo cấu trúc:\n"
            "```json\n"
            "{\n"
            '  "raw_text": "toàn bộ các dòng chữ đọc được trên ảnh theo đúng nguyên bản, phân cách bằng dấu xuống dòng",\n'
            '  "items": [\n'
            "    {\n"
            '      "name": "tên thực phẩm raw nguyên bản (vd: TOM THE NC, THIT OC MONG TAY, hoặc Má đùi gà)",\n'
            '      "quantity_g": khối_lượng_chính_xác_theo_gram (số thực, vd: 298.0, 384.0, 500.0),\n'
            '      "expiry_date": "DD/MM/YYYY hoặc null",\n'
            '      "hours_to_expire": số_giờ_còn_hạn (số thực, vd: 48.0, 72.0),\n'
            '      "note": "ghi chú chi tiết HSD, NĐG/NSX (vd: HSD: 02/10/2026 | NĐG: 02/10/2026)"\n'
            "    }\n"
            "  ]\n"
            "}\n"
            "```\n"
            "Chỉ trả về DUY NHẤT một khối JSON hợp lệ trong cặp thẻ ```json và ```."
        )

        last_err = None
        full_text = ""
        for attempt in range(3):
            try:
                assert self.client is not None
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": f"data:image/webp;base64,{b64_str}"}}
                            ]
                        }
                    ],
                    temperature=0.6,
                    max_completion_tokens=2048,
                    top_p=0.95,
                    reasoning_effort="default",
                    stream=True,
                    stop=None
                )

                for chunk in completion:
                    if chunk.choices and chunk.choices[0].delta.content:
                        full_text += chunk.choices[0].delta.content
                last_err = None
                break
            except Exception as e:
                last_err = e
                err_str = str(e).lower()
                if "rate" in err_str or "429" in err_str or "limit" in err_str:
                    import time
                    time.sleep(2.0 * (attempt + 1))
                    continue
                break

        if last_err is not None:
            return {
                "status": "error",
                "message": f"Lỗi gọi Groq Vision API ({self.model}): {str(last_err)}",
                "engine": f"Groq API ({self.model})",
                "raw_text": "",
                "items_count": 0,
                "items": [],
                "preprocess_stats": stats,
            }

        try:
            parsed_data = self._parse_llm_json(full_text)
            raw_text = parsed_data.get("raw_text", "") or full_text
            items = parsed_data.get("items", [])

            clean_items = []
            for it in items:
                name = str(it.get("name", "")).strip()
                if not name or len(name) < 2:
                    continue
                raw_q = it.get("quantity_g")
                quantity_source = "estimated"
                try:
                    if isinstance(raw_q, str):
                        quantity_is_kg = "kg" in raw_q.lower()
                        raw_q = re.sub(r"[^0-9.,-]", "", raw_q).replace(",", ".")
                    else:
                        quantity_is_kg = False
                    q_g = float(raw_q)
                    if q_g <= 0.0:
                        raise ValueError("quantity must be positive")
                    if quantity_is_kg or q_g < 5.0:
                        q_g = round(q_g * 1000.0, 1)
                    quantity_source = "extracted"
                except Exception:
                    q_g = 500.0

                hrs = 72.0
                try:
                    hrs = float(it.get("hours_to_expire", 72.0))
                except Exception:
                    pass

                exp_date = it.get("expiry_date")
                note = str(it.get("note") or "").strip()
                if not note:
                    note = f"HSD: {exp_date or 'Theo bao bì'}"

                clean_items.append({
                    "name": name,
                    "quantity_g": q_g,
                    "quantity_source": quantity_source,
                    "expiry_date": exp_date,
                    "hours_to_expire": hrs,
                    "note": note,
                })

            return {
                "status": "success",
                "source": "groq_qwen_vision",
                "engine": f"Groq API ({self.model})",
                "raw_text": raw_text,
                "items_count": len(clean_items),
                "items": clean_items,
                "preprocess_stats": stats,
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Lỗi gọi Groq Vision API ({self.model}): {str(e)}",
                "engine": f"Groq API ({self.model})",
                "raw_text": "",
                "items_count": 0,
                "items": [],
                "preprocess_stats": stats,
            }

    def _parse_llm_json(self, response_text: str) -> dict[str, Any]:
        """Extract and parse JSON block from LLM completion text."""
        m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response_text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                pass

        m2 = re.search(r"(\{.*\})", response_text, re.DOTALL)
        if m2:
            try:
                return json.loads(m2.group(1))
            except Exception:
                pass

        return {"raw_text": response_text, "items": []}
