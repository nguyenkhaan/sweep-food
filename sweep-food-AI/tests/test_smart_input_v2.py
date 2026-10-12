from types import SimpleNamespace
from unittest.mock import MagicMock

from smart_input.ocr.groq_vision_ocr import GroqVisionOCR
import smart_input.service as smart_input_service
from smart_input.service import process_receipt_input
from smart_parser.pantry_parser import PantryEntityParser


def test_groq_vision_parser_extracts_json_code_block() -> None:
    parser = GroqVisionOCR(api_key="")

    result = parser._parse_llm_json(
        '```json\n{"raw_text": "CA CHUA", "items": [{"name": "CA CHUA"}]}\n```'
    )

    assert result["raw_text"] == "CA CHUA"
    assert result["items"] == [{"name": "CA CHUA"}]


def test_groq_vision_marks_extracted_and_default_quantities() -> None:
    parser = GroqVisionOCR(api_key="")
    parser.client = MagicMock()
    parser.client.chat.completions.create.return_value = [
        SimpleNamespace(
            choices=[
                SimpleNamespace(
                    delta=SimpleNamespace(
                        content='{"raw_text":"label","items":['
                        '{"name":"Cà chua","quantity_g":"0.5kg"},'
                        '{"name":"Tỏi"}]}'
                    )
                )
            ]
        )
    ]

    result = parser.recognize_image_bytes(b"not-an-image")

    assert result["items"][0]["quantity_g"] == 500.0
    assert result["items"][0]["quantity_source"] == "extracted"
    assert result["items"][1]["quantity_g"] == 500.0
    assert result["items"][1]["quantity_source"] == "estimated"


def test_pantry_parser_resolves_unaccented_ocr_name() -> None:
    parser = PantryEntityParser.__new__(PantryEntityParser)
    ingredient = {
        "code": "4005",
        "name": "Cà chua",
        "category": "Rau, củ, quả",
        "nutrition": {"energy_kcal": 19.0},
    }
    parser.alias_to_master = {"cà chua": ingredient}
    parser.unaccented_to_master = {"ca chua": ingredient}
    parser.master_by_code = {"4005": ingredient}
    parser.fresh_kb = {}

    assert parser.resolve_master_ingredient("CA CHUA") == ingredient


def test_pantry_enrichment_preserves_contract_fields() -> None:
    parser = PantryEntityParser.__new__(PantryEntityParser)
    ingredient = {
        "code": "4005",
        "name": "Cà chua",
        "category": "Rau, củ, quả",
        "nutrition": {"energy_kcal": 19.0},
    }
    parser.alias_to_master = {"cà chua": ingredient}
    parser.unaccented_to_master = {"ca chua": ingredient}
    parser.master_by_code = {"4005": ingredient}
    parser.fresh_kb = {}

    enriched = parser.enrich_item(
        {
            "name": "CA CHUA",
            "quantity_g": 300.0,
            "quantity_source": "extracted",
            "expiry_date": "14/10/2026",
            "note": "HSD: 14/10/2026",
        }
    )

    assert enriched["category"] == "Rau, củ, quả"
    assert enriched["quantity_source"] == "extracted"
    assert enriched["expiry_date"] == "14/10/2026"
    assert enriched["note"] == "HSD: 14/10/2026"


def test_receipt_text_flow_assigns_raw_before_parsing() -> None:
    result = process_receipt_input(receipt_text="Cà chua 300g")

    assert result["status"] == "success"
    assert result["raw_text"] == "Cà chua 300g"
    assert result["items"][0]["quantity_source"] == "extracted"


def test_image_flow_preserves_quantity_provenance(monkeypatch) -> None:
    ocr = MagicMock()
    ocr.recognize_image_bytes.return_value = {
        "status": "success",
        "items": [
            {
                "name": "Cà chua",
                "quantity_g": 300.0,
                "quantity_source": "extracted",
                "hours_to_expire": 48.0,
            }
        ],
    }
    monkeypatch.setattr(smart_input_service, "_ocr_pipeline", ocr)

    result = process_receipt_input(image_bytes=b"mock-image")

    assert result["items"][0]["quantity_source"] == "extracted"
    assert result["items"][0]["category"]
