"""Vision OCR pipeline for supermarket labels and receipts.

Completely replaces PaddleOCR + VietOCR local pipeline.
Performs basic image preprocessing (resize, WebP compression, base64), sends the
image with OCR_PROMPT to a vision model and parses the JSON it returns.

This module holds the shared pipeline and the Groq backend (qwen/qwen3.8-27b),
which is kept as the fallback provider. The default provider lives in
openai_vision_ocr.py; smart_input.service picks one with OCR_PROVIDER.

hours_to_expire is computed here from expiry_date, never taken from the model:
the model does not know today's date.
"""

from __future__ import annotations

import base64
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
import cv2
import numpy as np

try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

DEFAULT_HOURS_TO_EXPIRE = 72.0

# Prompt v2 (16/10/2026): no examples taken from the OCR test images, explicit
# "leave null when unsure", DD-MM-YYYY date order, separate production_date,
# expiry_date only from HSD lines, "N ngày kể từ NSX" resolved to a date.
OCR_PROMPT = """Bạn là bộ đọc tem nhãn thực phẩm và hóa đơn siêu thị Việt Nam. Hãy chép lại chính xác những gì IN TRÊN ẢNH và trả về JSON.

NGUYÊN TẮC CHUNG
- Chỉ ghi thông tin nhìn thấy trên ảnh. Không đoán, không suy từ kiến thức chung, không thêm địa chỉ, số điện thoại hay cách bảo quản không có trên ảnh.
- Chữ nào mờ, bị che, hoặc không chắc thì để null và ghi lý do vào "note" (ví dụ: "NSX mờ, không đọc được"). Thà để trống còn hơn ghi sai.

TÊN (name)
- Chép đúng nguyên văn tên sản phẩm. Chữ in không dấu thì giữ không dấu; chữ in có dấu thì giữ đúng dấu. Không tự thêm dấu.
- Bỏ logo/thương hiệu đứng riêng (ví dụ chữ "CP" trong vòng tròn) nếu nó không thuộc tên. Nếu chữ đầu tên bị logo che mất, ghi phần đọc được và nói rõ trong note.

KHỐI LƯỢNG (quantity_g)
- Lấy số cạnh "KL", "KLT", "Khối lượng tịnh", "Trọng lượng", hoặc trong tên (ví dụ "200G"). Quy ra gram: kg × 1000.
- Dấu phẩy và dấu chấm trong khối lượng là dấu thập phân của kg (ví dụ 0,5 kg = 500 g).
- Không có khối lượng trên ảnh thì để null.

NGÀY
- Tem Việt Nam ghi ngày theo thứ tự NGÀY-THÁNG-NĂM (vd "2.10.2026" là ngày 2 tháng 10). Riêng dạng "2026.10.01" là NĂM.THÁNG.NGÀY. Đọc từng chữ số cẩn thận; không gộp hai số riêng thành một.
- production_date: ngày ghi cạnh NSX, NĐG, "Ngày SX", "Ngày đóng gói", "Ngày sản xuất". Định dạng DD/MM/YYYY.
- expiry_date: CHỈ lấy ngày ghi cạnh HSD, "Hạn sử dụng", "Ngày hết hạn". Không lấy "Ngày về hàng", "Ngày in" hay ngày khác.
  - Nếu tem ghi quy tắc "N ngày/tháng kể từ NSX/NĐG" và đọc được NSX/NĐG thì tính ra ngày: lấy NSX/NĐG cộng N ngày (hoặc N tháng). Ghi cả quy tắc gốc vào note.
  - Nếu tem chỉ ghi "sử dụng khi còn tươi", "xem trên bao bì" hoặc không có HSD thì để null.
- hours_to_expire: luôn để null (hệ thống tự tính từ expiry_date).

NOTE
- Ghi lại nguyên văn các dòng ngày đọc được, theo mẫu: "NSX: <như trên tem> | HSD: <như trên tem>", kèm lý do nếu có trường để null.

Mỗi sản phẩm là một phần tử trong "items" (tem cân thường chỉ có 1 sản phẩm; hóa đơn có thể nhiều).

Trả về DUY NHẤT một khối JSON hợp lệ trong cặp thẻ ```json và ```, theo cấu trúc:
```json
{
  "raw_text": "toàn bộ dòng chữ đọc được, mỗi dòng một dòng",
  "items": [
    {
      "name": "tên nguyên văn",
      "quantity_g": 0.0,
      "production_date": "DD/MM/YYYY hoặc null",
      "expiry_date": "DD/MM/YYYY hoặc null",
      "hours_to_expire": null,
      "note": "NSX: ... | HSD: ..."
    }
  ]
}
```"""


def _get_api_key(name: str) -> str:
    """Retrieve an API key from the environment or the project .env file."""
    key = os.environ.get(name, "")
    if key:
        return key

    # Check project .env
    for parent in [Path.cwd(), Path(__file__).resolve().parents[2]]:
        env_file = parent / ".env"
        if env_file.exists():
            try:
                with open(env_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip().startswith(f"{name}="):
                            k = line.strip().split("=", 1)[1].strip("\"'")
                            if k:
                                os.environ[name] = k
                                return k
            except Exception:
                pass
    return ""


def _get_groq_api_key() -> str:
    """Retrieve GROQ_API_KEY from environment or .env file."""
    return _get_api_key("GROQ_API_KEY")


def _normalize_date(value: Any) -> Optional[str]:
    """Return a DD/MM/YYYY date string, or None when value is not a valid date."""
    m = re.fullmatch(r"\s*(\d{1,2})[/.\-](\d{1,2})[/.\-](\d{4})\s*", str(value or ""))
    if not m:
        return None
    day, month, year = (int(g) for g in m.groups())
    try:
        datetime(year, month, day)
    except ValueError:
        return None
    return f"{day:02d}/{month:02d}/{year}"


def hours_until_expiry(expiry_date: Optional[str], now: Optional[datetime] = None) -> Optional[float]:
    """Hours from now until the end of the printed expiry day (0 when already expired)."""
    normalized = _normalize_date(expiry_date)
    if normalized is None:
        return None
    day, month, year = (int(p) for p in normalized.split("/"))
    end_of_day = datetime(year, month, day, 23, 59, 59)
    now = now or datetime.now()
    return round(max(0.0, (end_of_day - now).total_seconds() / 3600.0), 1)


class GroqVisionOCR:
    """Groq Cloud Vision OCR using Qwen (qwen/qwen3.8-27b); fallback provider."""

    provider_name = "Groq"
    source_name = "groq_qwen_vision"
    api_key_name = "GROQ_API_KEY"

    def __init__(self, api_key: Optional[str] = None, model: str = "qwen/qwen3.8-27b"):
        self.api_key = api_key or _get_groq_api_key()
        self.model = model
        self.client: Any = None
        if HAS_GROQ and self.api_key:
            self.client = Groq(api_key=self.api_key)

    @property
    def engine_label(self) -> str:
        return f"{self.provider_name} API ({self.model})"

    def is_available(self) -> bool:
        return self.client is not None

    def _connect(self) -> None:
        """Retry creating the client when the key was added after startup."""
        self.api_key = _get_groq_api_key()
        if HAS_GROQ and self.api_key:
            self.client = Groq(api_key=self.api_key)

    def _call_model(self, prompt: str, b64_str: str) -> str:
        """Send prompt + image to the model and return the raw completion text."""
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
            temperature=0.0,
            max_completion_tokens=2048,
            top_p=0.95,
            reasoning_effort="default",
            stream=True,
            stop=None
        )
        text = ""
        for chunk in completion:
            if chunk.choices and chunk.choices[0].delta.content:
                text += chunk.choices[0].delta.content
        return text

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
        now: Optional[datetime] = None,
    ) -> dict[str, Any]:
        """Perform basic preprocessing and query the vision model."""
        if not self.is_available():
            self._connect()
            if not self.is_available():
                return {
                    "status": "error",
                    "message": f"{self.provider_name} client chưa được khởi tạo hoặc thiếu {self.api_key_name} trong .env",
                    "items": [],
                    "raw_text": "",
                }

        b64_str, stats = self.preprocess_image(image_bytes, max_dim=max_dim)

        last_err = None
        full_text = ""
        for attempt in range(3):
            try:
                full_text = self._call_model(OCR_PROMPT, b64_str)
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
                "message": f"Lỗi gọi {self.engine_label}: {str(last_err)}",
                "engine": self.engine_label,
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

                exp_date = _normalize_date(it.get("expiry_date"))
                prod_date = _normalize_date(it.get("production_date"))
                hrs = hours_until_expiry(exp_date, now=now)
                if hrs is None:
                    hrs = DEFAULT_HOURS_TO_EXPIRE

                note = str(it.get("note") or "").strip()
                if not note:
                    note = f"HSD: {exp_date or 'Theo bao bì'}"

                clean_items.append({
                    "name": name,
                    "quantity_g": q_g,
                    "quantity_source": quantity_source,
                    "expiry_date": exp_date,
                    "production_date": prod_date,
                    "hours_to_expire": hrs,
                    "note": note,
                })

            return {
                "status": "success",
                "source": self.source_name,
                "engine": self.engine_label,
                "raw_text": raw_text,
                "items_count": len(clean_items),
                "items": clean_items,
                "preprocess_stats": stats,
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Lỗi đọc kết quả {self.engine_label}: {str(e)}",
                "engine": self.engine_label,
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
