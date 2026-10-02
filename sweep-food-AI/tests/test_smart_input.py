import os
import struct
import tempfile
import wave
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from web.app import app
from smart_input.ocr.receipt_parser import parse_receipt_text
from smart_input.ocr.label_parser import FoodLabelParser
from smart_input.ocr.sample_receipts import SAMPLE_RECEIPTS
from smart_input.asr.speech_parser import parse_vietnamese_speech
from smart_input.asr.audio_preprocessor import convert_to_16k_mono_flac
from smart_input.asr.groq_whisper import GroqWhisperClient
from smart_input.asr.gipformer_engine import GipformerEngine


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_ocr_winmart_receipt_parsing():
    """Verify WinMart receipt parsing extracts food accurately and filters non-food."""
    winmart_sample = next(s for s in SAMPLE_RECEIPTS if s["id"] == "winmart_family")
    items = parse_receipt_text(winmart_sample["raw_text"])

    assert len(items) >= 4
    names = [it["name"] for it in items]

    # Verify key food items were extracted
    assert any("Thịt bò" in n for n in names)
    assert any("Cá điêu hồng" in n for n in names)
    assert any("Rau muống" in n for n in names)
    assert any("Cà chua" in n for n in names)

    # Verify non-food items (Sunlight, Túi nilon) were filtered out
    assert not any("sunlight" in n.lower() for n in names)
    assert not any("túi" in n.lower() for n in names)

    # Verify weights in grams
    beef = next(it for it in items if "Thịt bò" in it["name"])
    assert beef["quantity_g"] == 450.0  # 0.45 kg -> 450g

    fish = next(it for it in items if "Cá điêu hồng" in it["name"])
    assert fish["quantity_g"] == 700.0  # 0.70 kg -> 700g


def test_ocr_bachhoaxanh_receipt_parsing():
    """Verify Bách Hóa Xanh receipt parsing with eggs, tofu, and pork."""
    bhx_sample = next(s for s in SAMPLE_RECEIPTS if s["id"] == "bachhoaxanh_student")
    items = parse_receipt_text(bhx_sample["raw_text"])

    names = [it["name"] for it in items]
    assert any("Trứng gà" in n for n in names)
    assert any("Đậu hũ" in n for n in names)
    assert any("Thịt heo" in n for n in names)

    # Verify wipes filtered out
    assert not any("khăn" in n.lower() for n in names)


def test_receipt_parser_does_not_match_words_that_only_share_unaccented_text():
    raw_text = """Tái sử dụng mã nguồn tối đa
    DB có cột Store_ID và cho phép cửa hàng tự tạo kho
    Mặt hàng phi sách khác"""

    assert parse_receipt_text(raw_text) == []


def test_bachhoaxanh_food_packaging_label_parser():
    """Verify Bách Hóa Xanh food packaging stickers (Cải thìa VietGAP, Thịt ba rọi heo)."""
    parser = FoodLabelParser()

    # 1. Vegetable package sticker
    caithia_sample = """
    SIEU THI BACH HOA XANH
    CAI THIA SACH DA LAT VIETGAP
    KLT: 500g
    NSX: 05/09/2026
    HSD: 09/09/2026
    XUAT XU: LAM DONG
    """
    res1 = parser.parse_label_text(caithia_sample)
    assert "CAI THIA" in res1["name"].upper()
    assert res1["quantity_g"] == 500.0
    assert res1["expiry_date"] == "09/09/2026"
    assert res1["store"] == "Bách Hóa Xanh"

    # 2. Fresh Meat package sticker
    thitheo_sample = """
    BACH HOA XANH - THIT TUOI MOI NGAY
    THIT BA ROI HEO CP CHILLED
    TRONG LUONG: 0.420 kg
    HAN SU DUNG: 08/09/2026
    """
    res2 = parser.parse_label_text(thitheo_sample)
    assert "THIT BA ROI" in res2["name"].upper()
    assert res2["quantity_g"] == 420.0
    assert res2["expiry_date"] == "08/09/2026"


def test_audio_preprocessor_ffmpeg_flac():
    """Verify ffmpeg converts input audio to 16kHz mono FLAC."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav_path = f.name

    try:
        with wave.open(wav_path, "w") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(44100)
            data = struct.pack("<h", 500) * 44100 * 2
            wf.writeframes(data)

        flac_path = convert_to_16k_mono_flac(wav_path)
        assert flac_path.exists()
        assert flac_path.stat().st_size > 0
        assert flac_path.suffix.lower() == ".flac"
        if flac_path.exists():
            os.unlink(flac_path)
    finally:
        if os.path.exists(wav_path):
            os.unlink(wav_path)


def test_groq_whisper_client_mock():
    """Verify GroqWhisperClient sends proper payload and headers."""
    client = GroqWhisperClient(api_key="test_mock_key")

    with patch.object(client.session, "post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "text": "tôi có nửa cân thịt bò và một bó rau muống"
        }
        mock_post.return_value = mock_resp

        # Create dummy file to pass path validation
        with tempfile.NamedTemporaryFile(suffix=".flac", delete=False) as tf:
            tf.write(b"RIFFdummyflacdata")
            dummy_path = tf.name

        try:
            res = client.transcribe_file(dummy_path)
            assert res["success"] is True
            assert "thịt bò" in res["text"]
            assert res["model"] == "whisper-large-v3-turbo"
            assert res["language"] == "vi"

            # Check that requests.post was called with right URL and auth header
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            assert "api.groq.com" in args[0]
            assert kwargs["headers"]["Authorization"] == "Bearer test_mock_key"
            assert kwargs["data"]["model"] == "whisper-large-v3-turbo"
            assert kwargs["data"]["language"] == "vi"
        finally:
            if os.path.exists(dummy_path):
                os.unlink(dummy_path)


def test_gipformer_engine_availability():
    """Verify GipformerEngine pre-checks model dependencies gracefully."""
    engine = GipformerEngine()
    # It should not throw on initialization
    assert isinstance(engine.is_available(), bool)


def test_asr_culinary_speech_parser():
    """Verify Vietnamese natural spoken speech entity and unit parsing."""
    transcript = "Hôm nay tôi mua nửa cân thịt bò và hai lạng tỏi với một bó rau muống"
    items = parse_vietnamese_speech(transcript)

    assert len(items) == 3
    item_map = {it["name"]: it["quantity_g"] for it in items}

    # "nửa cân" -> 500g
    assert item_map.get("Thịt bò") == 500.0
    # "hai lạng" -> 200g
    assert item_map.get("Tỏi") == 200.0
    # "một bó" -> 300g
    assert item_map.get("Rau muống") == 300.0


def test_asr_chicken_and_eggs_speech():
    """Verify speech with ký rưỡi (1.5kg) and quả (count)."""
    transcript = "Trong tủ lạnh đang có một con gà một ký rưỡi và ba quả trứng gà"
    items = parse_vietnamese_speech(transcript)

    assert len(items) == 2
    item_map = {it["name"]: it["quantity_g"] for it in items}

    # "một ký rưỡi" -> 1500g
    assert item_map.get("Thịt gà") == 1500.0
    # "ba quả trứng gà" -> 3 * 50g = 150g
    assert item_map.get("Trứng gà") == 150.0


def test_smart_input_api_endpoints(client):
    """Test API endpoints for Smart Input."""
    # 1. Samples
    resp_samples = client.get("/api/smart-input/samples")
    assert resp_samples.status_code == 200
    s_data = resp_samples.json()
    assert "receipt_samples" in s_data
    assert "voice_samples" in s_data
    assert len(s_data["receipt_samples"]) >= 5

    # 2. OCR JSON sample receipt
    resp_ocr = client.post("/api/smart-input/ocr", json={"sample_id": "winmart_family"})
    assert resp_ocr.status_code == 200
    ocr_data = resp_ocr.json()
    assert ocr_data.get("status") == "success"
    assert len(ocr_data.get("items", [])) >= 4

    # 3. OCR Bách Hóa Xanh food label sample
    resp_bhx = client.post("/api/smart-input/ocr", json={"sample_id": "bhx_label_caithia"})
    assert resp_bhx.status_code == 200
    bhx_data = resp_bhx.json()
    assert bhx_data.get("status") == "success"
    assert len(bhx_data.get("items", [])) >= 1
    assert "CAI THIA" in bhx_data["items"][0]["name"].upper()

    # 4. ASR
    resp_asr = client.post("/api/smart-input/asr", json={
        "transcript": "Tôi có bốn trăm gram tôm thẻ và nửa bắp cải",
        "engine": "groq_whisper"
    })
    assert resp_asr.status_code == 200
    asr_data = resp_asr.json()
    assert asr_data.get("status") == "success"
    assert len(asr_data.get("items", [])) == 2


def test_smart_input_to_recommendation_pipeline(client):
    """End-to-end integration: Smart Input feeds parsed items directly into the recommendation engine."""
    # 1. Voice input
    resp_asr = client.post("/api/smart-input/asr", json={"sample_id": "voice_beef_garlic"})
    assert resp_asr.status_code == 200
    items = resp_asr.json()["items"]
    assert len(items) > 0

    # 2. Convert to recommendation request
    pantry_items = [
        {"name": it["name"], "quantity_g": it["quantity_g"], "hours_to_expire": it["hours_to_expire"]}
        for it in items
    ]

    resp_rec = client.post("/api/recommend", json={
        "items": pantry_items,
        "household_size": 2,
        "max_cooking_time_min": 45,
        "scenario_type": "custom"
    })
    assert resp_rec.status_code == 200
    rec_data = resp_rec.json()
    assert rec_data.get("status") == "success"
    assert len(rec_data.get("recommendations", [])) > 0


def test_image_preprocessor_downsampling_and_clahe():
    """Verify image preprocessor downscales high-res photos and computes compression ratio."""
    import cv2
    import numpy as np
    from smart_input.ocr.image_preprocessor import preprocess_ocr_image, preprocess_image_bytes

    # Create synthetic high-res image (2400 x 1800)
    high_res = np.ones((2400, 1800, 3), dtype=np.uint8) * 240
    cv2.putText(high_res, "BACH HOA XANH", (100, 500), cv2.FONT_HERSHEY_SIMPLEX, 3, (10, 10, 10), 4)

    # Test array preprocessor
    processed_rgb, stats = preprocess_ocr_image(high_res, max_dim=1600, enhance_contrast=True)
    assert stats["downscaled"] is True
    assert max(stats["processed_width"], stats["processed_height"]) == 1600
    assert processed_rgb.shape[0] == 1600
    assert processed_rgb.shape[1] == 1200

    # Test bytes preprocessor
    _, encoded = cv2.imencode(".png", high_res)
    comp_bytes, _, b_stats = preprocess_image_bytes(encoded.tobytes(), max_dim=1600, quality=85)
    assert len(comp_bytes) > 0
    assert b_stats["format"] == "JPEG"
    assert b_stats["savings_percent"] >= 0.0


def test_image_preprocessor_normalizes_dark_background():
    """Dark-mode screenshots become dark text on a light background for OCR."""
    import cv2
    import numpy as np
    from smart_input.ocr.image_preprocessor import preprocess_ocr_image

    image = np.full((80, 240, 3), 30, dtype=np.uint8)
    cv2.putText(image, "Yeu cau", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (240, 240, 240), 2)

    processed, stats = preprocess_ocr_image(image, enhance_contrast=False)

    assert stats["polarity_inverted"] is True
    assert np.median(processed) > 127


def test_audio_preprocessor_silence_stripping():
    """Verify audio preprocessor downsamples to 16kHz mono FLAC with silence stripping."""
    from smart_input.asr.audio_preprocessor import preprocess_audio_bytes

    # Generate 1 sec tone with leading and trailing silence
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav_path = f.name

    try:
        with wave.open(wav_path, "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(44100)
            silence = struct.pack("<h", 0) * 44100 * 2
            signal = struct.pack("<h", 800) * 44100 * 2
            wf.writeframes(silence + signal + silence)

        with open(wav_path, "rb") as f:
            raw_bytes = f.read()

        flac_bytes, stats = preprocess_audio_bytes(raw_bytes, input_format="wav", strip_silence=True)
        assert len(flac_bytes) > 0
        assert stats["format"] == "FLAC"
        assert stats["sample_rate"] == 16000
        assert stats["channels"] == 1
        assert stats["savings_percent"] > 50.0
    finally:
        if os.path.exists(wav_path):
            os.unlink(wav_path)


def test_system_status_and_gpu_warmup(client):
    """Verify /api/system/status returns GPU status and warm-up state."""
    from smart_input.service import warmup_smart_input_gpu

    warmup_res = warmup_smart_input_gpu()
    assert "cuda_available" in warmup_res
    assert "status" in warmup_res
    assert warmup_res["status"] == "ready"

    resp = client.get("/api/system/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "cuda_available" in data
    assert "device_name" in data
    assert "xgb_device" in data
    assert "ocr_device" in data
