from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import smart_input.ocr.expiry_check as expiry_check
import smart_input.service as smart_input_service
from smart_input.ocr.expiry_check import check_label_expiry
from smart_input.ocr.groq_vision_ocr import OCR_PROMPT, GroqVisionOCR, hours_until_expiry
from smart_input.ocr.openai_vision_ocr import OpenAIVisionOCR
from smart_parser.pantry_parser import PantryEntityParser

NOW = datetime(2026, 10, 2, 9, 0, 0)


def _openai_reply(content: str) -> SimpleNamespace:
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])


def test_hours_until_expiry_counts_to_end_of_printed_day() -> None:
    assert hours_until_expiry("02/10/2026", now=NOW) == 15.0
    assert hours_until_expiry("4.10.2026", now=NOW) == 63.0
    assert hours_until_expiry("01/10/2026", now=NOW) == 0.0
    assert hours_until_expiry(None, now=NOW) is None
    assert hours_until_expiry("31/02/2026", now=NOW) is None


def test_prompt_has_no_examples_from_ocr_test_images() -> None:
    for leaked in ("TOM THE NC", "THIT OC MONG TAY", "CA BASA MINI", "0,298", "Má đùi gà"):
        assert leaked not in OCR_PROMPT


def test_openai_ocr_computes_hours_and_keeps_production_date() -> None:
    ocr = OpenAIVisionOCR(api_key="test-key", model="gpt-6.1-sol", reasoning_effort="medium")
    ocr.client = MagicMock()
    ocr.client.chat.completions.create.return_value = _openai_reply(
        '```json\n{"raw_text": "THIT DUI HEO", "items": [{"name": "THIT DUI HEO", "quantity_g": 294,'
        ' "production_date": "1.10.2026", "expiry_date": "2/10/2026", "hours_to_expire": 999,'
        ' "note": "NSX: 1.10.2026 | HSD: 2.10.2026"}]}\n```'
    )

    result = ocr.recognize_image_bytes(b"not-an-image", now=NOW)

    item = result["items"][0]
    assert result["status"] == "success"
    assert result["source"] == "openai_vision"
    assert result["engine"] == "OpenAI API (gpt-6.1-sol)"
    assert item["expiry_date"] == "02/10/2026"
    assert item["production_date"] == "01/10/2026"
    assert item["hours_to_expire"] == 15.0  # from expiry_date, not the model's 999
    kwargs = ocr.client.chat.completions.create.call_args.kwargs
    assert kwargs["model"] == "gpt-6.1-sol"
    assert kwargs["reasoning_effort"] == "medium"
    assert kwargs["messages"][0]["content"][0]["text"] == OCR_PROMPT


def test_missing_expiry_falls_back_to_default_hours() -> None:
    ocr = OpenAIVisionOCR(api_key="test-key")
    ocr.client = MagicMock()
    ocr.client.chat.completions.create.return_value = _openai_reply(
        '{"raw_text": "CAI NGOT", "items": [{"name": "CAI NGOT", "quantity_g": null, "expiry_date": null}]}'
    )

    item = ocr.recognize_image_bytes(b"not-an-image", now=NOW)["items"][0]

    assert item["expiry_date"] is None
    assert item["hours_to_expire"] == 72.0
    assert item["quantity_source"] == "estimated"


def test_openai_ocr_reports_missing_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    ocr = OpenAIVisionOCR(api_key="")
    ocr.client = None
    monkeypatch.setattr(ocr, "_connect", lambda: None)

    result = ocr.recognize_image_bytes(b"not-an-image")

    assert result["status"] == "error"
    assert "OPENAI_API_KEY" in result["message"]


def test_provider_selection(monkeypatch) -> None:
    monkeypatch.setattr(smart_input_service, "_ocr_pipeline", None)
    monkeypatch.setenv("OCR_PROVIDER", "groq")
    assert type(smart_input_service.get_ocr_pipeline()) is GroqVisionOCR

    monkeypatch.setattr(smart_input_service, "_ocr_pipeline", None)
    monkeypatch.setenv("OCR_PROVIDER", "openai")
    monkeypatch.setattr(OpenAIVisionOCR, "is_available", lambda self: True)
    assert isinstance(smart_input_service.get_ocr_pipeline(), OpenAIVisionOCR)

    monkeypatch.setattr(smart_input_service, "_ocr_pipeline", None)
    monkeypatch.setattr(OpenAIVisionOCR, "is_available", lambda self: False)
    assert type(smart_input_service.get_ocr_pipeline()) is GroqVisionOCR  # no OpenAI key -> Groq
    monkeypatch.setattr(smart_input_service, "_ocr_pipeline", None)


def _parser_with_kb() -> PantryEntityParser:
    parser = PantryEntityParser.__new__(PantryEntityParser)
    ingredient = {"code": "7001", "name": "Thịt heo nạc", "category": "Thịt", "nutrition": {}}
    parser.alias_to_master = {"thit dui heo": ingredient}
    parser.unaccented_to_master = {"thit dui heo": ingredient}
    parser.master_by_code = {"7001": ingredient}
    parser.fresh_kb = {
        "ingredients": {
            "thit_nac_heo": {
                "code": "7001",
                "names_vi": ["thịt heo nạc"],
                "archetype": "FRESH_MEAT",
                "base_shelf_life_hours": {"fridge_2_4c": {"value": 72.0}},
            }
        },
        "archetypes": {"FRESH_MEAT": {"name_vi": "Thịt tươi", "preservation_protocols": {}}},
    }
    return parser


def test_enrich_item_keeps_hours_from_printed_expiry() -> None:
    parser = _parser_with_kb()

    printed = parser.enrich_item(
        {"name": "THIT DUI HEO", "code": "7001", "expiry_date": "02/10/2026", "hours_to_expire": 15.0}
    )
    expired = parser.enrich_item(
        {"name": "THIT DUI HEO", "code": "7001", "expiry_date": "01/10/2026", "hours_to_expire": 0.0}
    )
    no_label = parser.enrich_item({"name": "THIT DUI HEO", "code": "7001", "hours_to_expire": 72.0})

    assert printed["hours_to_expire"] == 15.0
    assert expired["hours_to_expire"] == 0.0
    assert no_label["hours_to_expire"] == 72.0  # from FreshCheck KB


CANH_GA_KB = {
    "canh_ga": {
        "code": "7087",
        "names_vi": ["cánh gà", "cánh gà khúc giữa"],
        "base_shelf_life_hours": {"fridge_2_4c": {"value": 48.0}, "freezer_-18c": {"value": 2880.0}},
    }
}


def _label(expiry_date: str, production_date: str | None = "01/10/2026", **extra) -> dict:
    return {
        "name": "Cánh gà",
        "raw_name": "CANH GIUA GA NHAP KHAU",
        "code": "7087",
        "storage_mode": "fridge_2_4c",
        "production_date": production_date,
        "expiry_date": expiry_date,
        "note": "NĐG: 1.10.2026 | HSD: 2.10.2026",
        **extra,
    }


def test_expiry_check_flags_hsd_longer_than_freshcheck() -> None:
    # Ảnh #10: NĐG 1.10, HSD in 2.10, model đọc thành 4.10 -> 3 ngày > 48h cánh gà ngăn mát.
    flagged = check_label_expiry(_label("04/10/2026"), ingredients=CANH_GA_KB)

    assert flagged["expiry_check"] == "suspicious"
    assert flagged["expiry_date"] == "04/10/2026"  # never rewritten
    assert "Kiểm tra lại HSD" in flagged["expiry_check_reason"]
    assert flagged["note"].startswith("NĐG: 1.10.2026 | HSD: 2.10.2026 | ")
    assert flagged["expiry_check_reason"] in flagged["note"]


def test_expiry_check_trusts_printed_rule_matching_the_span() -> None:
    # Ảnh #17–19: JAPFA in "HSD: 4 ngày kể từ NSX", NSX 29/09 -> 03/10 là hạn nhà sản xuất in, không báo nhầm.
    japfa = check_label_expiry(
        _label("03/10/2026", production_date="29/09/2026",
               note="NSX: 29/09/2026 | HSD: 4 ngày kể từ NSX. Hạn sử dụng được tính bằng NSX cộng 4 ngày."),
        ingredients=CANH_GA_KB,
    )
    unaccented = check_label_expiry(
        _label("04/10/2026", note="NSX: Ngay san xuat 01/10/26 | HSD: 3 ngay ke tu ngay san xuat"),
        ingredients=CANH_GA_KB,
    )
    months = check_label_expiry(
        _label("15/03/2027", production_date="15/09/2026", note="NĐG: 15-09-2026 | HSD: 6 THÁNG KỂ TỪ NGÀY ĐÓNG GÓI"),
        ingredients=CANH_GA_KB,
    )

    assert japfa["expiry_check"] == "ok"
    assert unaccented["expiry_check"] == "ok"
    assert months["expiry_check"] == "ok"


def test_expiry_check_still_flags_when_span_disagrees_with_printed_rule() -> None:
    # Tem in "2 ngày kể từ NĐG" nhưng ngày đọc được cách 5 ngày -> vẫn nghi đọc nhầm.
    flagged = check_label_expiry(
        _label("06/10/2026", note="NĐG: 1.10.2026 | HSD: 2 ngày kể từ NĐG"), ingredients=CANH_GA_KB
    )

    assert flagged["expiry_check"] == "suspicious"


def test_expiry_check_accepts_printed_hsd_within_reference() -> None:
    printed = check_label_expiry(_label("02/10/2026"), ingredients=CANH_GA_KB)
    two_days = check_label_expiry(_label("03/10/2026"), ingredients=CANH_GA_KB)

    assert printed["expiry_check"] == "ok"
    assert printed["expiry_check_reason"] is None
    assert printed["note"] == "NĐG: 1.10.2026 | HSD: 2.10.2026"
    assert two_days["expiry_check"] == "ok"  # 48h == reference


def test_expiry_check_uses_storage_mode_and_name_lookup() -> None:
    frozen = check_label_expiry(_label("04/10/2026", storage_mode="freezer_-18c"), ingredients=CANH_GA_KB)
    by_name = check_label_expiry(_label("04/10/2026", code=None, name="Cánh gà khúc giữa BHX"), ingredients=CANH_GA_KB)

    assert frozen["expiry_check"] == "ok"
    assert by_name["expiry_check"] == "suspicious"


def test_expiry_check_flags_expiry_before_production() -> None:
    swapped = check_label_expiry(_label("30/09/2026"), ingredients=CANH_GA_KB)

    assert swapped["expiry_check"] == "suspicious"
    assert "sớm hơn" in swapped["expiry_check_reason"]


def test_expiry_check_skips_when_it_cannot_compare() -> None:
    no_production = check_label_expiry(_label("04/10/2026", production_date=None), ingredients=CANH_GA_KB)
    unknown = check_label_expiry(_label("04/10/2026", code="9999", name="Bánh lạ", raw_name="BANH LA"), ingredients=CANH_GA_KB)

    assert no_production["expiry_check"] is None
    assert unknown["expiry_check"] is None
    assert unknown["note"] == "NĐG: 1.10.2026 | HSD: 2.10.2026"


def test_expiry_check_runs_on_ocr_upload(monkeypatch) -> None:
    ocr = OpenAIVisionOCR(api_key="test-key")
    ocr.client = MagicMock()
    ocr.client.chat.completions.create.return_value = _openai_reply(
        '{"raw_text": "CANH GIUA GA NHAP KHAU", "items": [{"name": "CANH GIUA GA NHAP KHAU", "quantity_g": 296,'
        ' "production_date": "1.10.2026", "expiry_date": "4.10.2026"}]}'
    )
    monkeypatch.setattr(smart_input_service, "_ocr_pipeline", ocr)
    monkeypatch.setattr(
        smart_input_service, "_enrich_contract_items", lambda items: [{**it, "code": "7087"} for it in items]
    )
    monkeypatch.setattr(expiry_check, "_kb_ingredients", CANH_GA_KB)

    item = smart_input_service.process_receipt_input(image_bytes=b"not-an-image")["items"][0]
    monkeypatch.setattr(smart_input_service, "_ocr_pipeline", None)

    assert item["expiry_check"] == "suspicious"
    assert item["expiry_date"] == "04/10/2026"


def test_freshcheck_source_has_canh_ga_reference() -> None:
    kb_canh_ga = expiry_check.find_freshcheck_ingredient(expiry_check.load_freshcheck_ingredients(), "7087", [])

    assert kb_canh_ga is not None
    assert kb_canh_ga["base_shelf_life_hours"]["fridge_2_4c"]["value"] == 48.0
