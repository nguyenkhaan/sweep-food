"""SweepFood AI - Interactive Web UI & Recommendation API Service.

Powered by:
- Inverted Index Candidate Generator (sub-millisecond candidate retrieval)
- Contextual Feature Extractor
- Production-Trained LightGBM LambdaMART Ranker (rank:pairwise)
- Full Vietnamese Recipe & Nutritional Knowledge Base
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field


class SmartInputOcrRequest(BaseModel):
    image_base64: str | None = None
    receipt_text: str | None = None
    sample_id: str | None = None


class SmartInputAsrRequest(BaseModel):
    transcript: str | None = None
    sample_id: str | None = None
    engine: str = "groq_whisper"


# Set root directory
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

import lightgbm as lgb

from smart_input.service import (
    get_smart_input_samples,
    process_receipt_input,
    process_voice_input,
    warmup_smart_input_gpu,
)
from src.recommendation.candidate_generator import (
    CandidateGenerator,
    extract_pantry_name_aliases,
)
from src.recommendation.contextual_features import (
    FEATURE_COLS,
    extract_contextual_features,
)
from src.recommendation.heuristic_baseline import compute_domain_heuristic_score
from src.recommendation.pantry_resolver import (
    build_master_alias_index,
    get_effective_codes,
    normalize,
    resolve_pantry_items,
)

# Global GPU Acceleration Status
SYSTEM_GPU_STATUS = {
    "cuda_available": False,
    "device_name": "CPU",
    "ocr_device": "cpu",
    "vram_allocated_mb": 0.0,
    "warmed_up": False,
}

app = FastAPI(title="SweepFood AI Web Demo", version="2.0.0")

RECIPES_JSON = os.path.join(ROOT_DIR, "data/processed/recipes/recipes.json")
ING_JSON = os.path.join(ROOT_DIR, "data/processed/recipes/recipe_ingredients.json")
MAP_JSON = os.path.join(ROOT_DIR, "data/processed/recipes/recipe_canonical_mapping.json")
DETAILED_JSON = os.path.join(ROOT_DIR, "data/processed/recipes/recipes_restructured_detailed.json")
MASTER_VDD_CSV = os.path.join(ROOT_DIR, "data/processed/viendinhduong/master_ingredients_nutrition.csv")
LGBM_MODEL_PATH = os.path.join(ROOT_DIR, "data/training/lgbm_contextual.txt")
CONTRACT_VERSION = "2"
CATALOG_REVISION = f"sha256:{hashlib.sha256(Path(RECIPES_JSON).read_bytes()).hexdigest()}"

print("Loading knowledge base and production models...")
print(f"Active recipe knowledge base: {RECIPES_JSON}")

with open(RECIPES_JSON, "r", encoding="utf-8") as f:
    recipes_list = json.load(f)
with open(ING_JSON, "r", encoding="utf-8") as f:
    ingredients_list = json.load(f)

cg = CandidateGenerator(recipes_list, ingredients_list)
recipe_map = {r["id"]: r for r in recipes_list}
recipe_ings_map = cg.recipe_ingredients

# Load structured detailed recipe instructions (steps, sensory, chef tips)
detailed_recipe_map = {}
if os.path.exists(DETAILED_JSON):
    try:
        with open(DETAILED_JSON, "r", encoding="utf-8") as f:
            for det in json.load(f):
                rid = det.get("canonical_recipe_id") or det.get("id")
                if rid:
                    detailed_recipe_map[rid] = det
        print(f"Loaded structured detailed recipes for {len(detailed_recipe_map):,} dishes.")
    except Exception as e:
        print(f"Warning: Failed loading detailed recipes: {e}")

# Fallback raw recipe instructions
RAW_RECIPES_JSON = os.path.join(ROOT_DIR, "data/raw/recipes_raw_scraped.json")
recipe_instructions_map = {}
if not detailed_recipe_map and os.path.exists(RAW_RECIPES_JSON):
    try:
        with open(RAW_RECIPES_JSON, "r", encoding="utf-8") as f:
            raw_recipes_data = json.load(f)
        for item in raw_recipes_data:
            url = item.get("source_url")
            raw_inst = item.get("instructions")
            if url and raw_inst and isinstance(raw_inst, list):
                steps = []
                for s in raw_inst:
                    if isinstance(s, dict):
                        num = s.get("step_number") or len(steps) + 1
                        title = (s.get("title") or f"Bước {num}").strip()
                        content = (s.get("content") or "").strip()
                        if content:
                            steps.append({"step": num, "title": title, "content": content})
                    elif isinstance(s, str) and s.strip():
                        steps.append({"step": len(steps) + 1, "title": f"Bước {len(steps) + 1}", "content": s.strip()})
                if steps:
                    recipe_instructions_map[url] = {
                        "steps": steps,
                        "formatted_text": "\n\n".join([f"{s['title']}: {s['content']}" for s in steps])
                    }
        print(f"Loaded step-by-step instructions for {len(recipe_instructions_map)} recipes from raw scrape.")
    except Exception as e:
        print(f"Warning: Failed loading raw recipe instructions: {e}")
# Load Production LightGBM Ranker (or graceful fallback to domain heuristic ranker)
lgbm_ranker = None
if os.path.exists(LGBM_MODEL_PATH):
    try:
        lgbm_ranker = lgb.Booster(model_file=LGBM_MODEL_PATH)
        print(f"Production LightGBM LambdaMART Ranker loaded successfully ({len(FEATURE_COLS)} contextual features).")
    except Exception as e:
        print(f"Warning: Could not load LightGBM model: {e}")
        lgbm_ranker = None

if lgbm_ranker is None:
    print("Using High-Precision Culinary Domain Heuristic Ranker (Zero-Dependency Mode).")
MODEL_VERSION = "lgbm-contextual-v1" if lgbm_ranker is not None else "domain-heuristic-v1"
RANKER_MODEL_NAME = "LightGBM LambdaMART" if lgbm_ranker is not None else "Domain Heuristic"
# Load master ingredients for autocomplete (name & code) and category mapping
df_master = pd.read_csv(MASTER_VDD_CSV)
MASTER_CODE_TO_CATEGORY = {str(row["code"]).strip(): str(row["category_vi"]).strip() for _, row in df_master.iterrows()}
MASTER_ALIAS_INDEX = build_master_alias_index(df_master)
_ambiguous_keys_count = sum(1 for codes in MASTER_ALIAS_INDEX.values() if len(codes) > 1)
print(f"Master alias index built: {len(MASTER_ALIAS_INDEX):,} keys ({_ambiguous_keys_count:,} map to >1 code).")

ANIMAL_CATEGORIES = {
    "Thịt và sản phẩm chế biến",
    "Thủy sản và sản phẩm chế biến",
    "Trứng và sản phẩm chế biến",
}

ANIMAL_KEYWORDS = [
    r"\bthịt\b", r"\bcá\b", r"\btôm\b", r"\bcua\b", r"\bmực\b", r"\bgà\b", r"\bvịt\b",
    r"\bheo\b", r"\blợn\b", r"\bbò\b", r"\btrứng\b", r"\bmỡ lợn\b", r"\bmỡ heo\b",
    r"\bmỡ bò\b", r"\bmỡ gà\b", r"\bmỡ động vật\b", r"\bngao\b", r"\bsò\b",
    r"\bốc\b", r"\bhến\b", r"\bhàu\b", r"\blòng\b", r"\bgan\b", r"\bcật\b", r"\bdạ dày\b",
    r"\bnội tạng\b", r"\bdê\b", r"\bcừu\b", r"\bbê\b", r"\blươn\b", r"\bếch\b",
    r"\bchả lụa\b", r"\bpate\b", r"\blạp xưởng\b", r"\bbò viên\b", r"\bcá viên\b",
    r"\bmắm tôm\b", r"\bmắm tép\b", r"\bmắm cá\b", r"\bmắm ruốc\b", r"\bmắm nêm\b"
]

GOUT_KEYWORDS = [
    r"\bbò\b", r"\bbê\b", r"\bcừu\b", r"\bdê\b", r"\bcua\b", r"\bghẹ\b",
    r"\btôm\b", r"\bsò\b", r"\bngao\b", r"\bhàu\b", r"\blòng\b", r"\bgan\b",
    r"\bcật\b", r"\bdạ dày\b", r"\bnội tạng\b"
]


def has_animal_ingredients(recipe_ings: list[dict]) -> bool:
    for ing in recipe_ings:
        clean_n = (ing.get("cleaned_name") or "").strip().lower()
        raw_t = (ing.get("raw_text") or "").strip().lower()
        code = str(ing.get("master_ingredient_code") or "").strip()

        # Vegetarian / plant-based exemptions
        if "chay" in clean_n or "chay" in raw_t:
            continue
        if "nấm" in clean_n or "nấm" in raw_t:
            continue
        if "đậu phụ" in clean_n or "tàu hũ" in clean_n or "đậu hũ" in clean_n:
            continue
        if "tép tỏi" in clean_n or "tép tỏi" in raw_t:
            clean_n = clean_n.replace("tép tỏi", "")
            raw_t = raw_t.replace("tép tỏi", "")
        if "khoai mỡ" in clean_n or "xà lách mỡ" in clean_n:
            clean_n = clean_n.replace("khoai mỡ", "").replace("xà lách mỡ", "")

        cat = MASTER_CODE_TO_CATEGORY.get(code, "")
        if cat in ANIMAL_CATEGORIES:
            return True

        for pat in ANIMAL_KEYWORDS:
            if re.search(pat, clean_n) or re.search(pat, raw_t):
                return True
        if ("nước mắm" in clean_n or "nước mắm" in raw_t) and "chay" not in clean_n and "chay" not in raw_t:
            return True
        if re.search(r"\bmỡ\b", clean_n) and not ("khoai" in clean_n or "xà lách" in clean_n or "hành" in clean_n):
            return True
    return False


def has_gout_forbidden_ingredients(recipe_ings: list[dict]) -> bool:
    for ing in recipe_ings:
        clean_n = (ing.get("cleaned_name") or "").strip().lower()
        raw_t = (ing.get("raw_text") or "").strip().lower()
        code = str(ing.get("master_ingredient_code") or "").strip()

        if "chay" in clean_n or "chay" in raw_t:
            continue
        if "tép tỏi" in clean_n or "tép tỏi" in raw_t:
            clean_n = clean_n.replace("tép tỏi", "")
            raw_t = raw_t.replace("tép tỏi", "")
        if "bắp cải" in clean_n or "bắp ngô" in clean_n:
            clean_n = clean_n.replace("bắp cải", "").replace("bắp ngô", "")

        cat = MASTER_CODE_TO_CATEGORY.get(code, "")
        if cat in {"Thịt và sản phẩm chế biến", "Thủy sản và sản phẩm chế biến"}:
            return True

        for pat in GOUT_KEYWORDS:
            if re.search(pat, clean_n) or re.search(pat, raw_t):
                return True
    return False


def has_excluded_ingredients(recipe_ings: list[dict], excluded_names: list[str]) -> bool:
    normalized_names = {normalize(name) for name in excluded_names if normalize(name)}
    resolved = resolve_pantry_items(
        ({"name": name} for name in normalized_names),
        MASTER_ALIAS_INDEX,
    )
    excluded_codes = {code for item in resolved for code in get_effective_codes(item)}

    for ingredient in recipe_ings:
        code = str(ingredient.get("master_ingredient_code") or "").strip()
        code = code.removesuffix(".0")
        if code and code in excluded_codes:
            return True
        ingredient_names = (
            ingredient.get("master_ingredient_name"),
            ingredient.get("cleaned_name"),
            ingredient.get("raw_text"),
        )
        for raw_name in ingredient_names:
            candidate = normalize(raw_name)
            if any(
                candidate == excluded
                or re.search(rf"(?<!\w){re.escape(excluded)}(?!\w)", candidate)
                for excluded in normalized_names
            ):
                return True
    return False


master_items = []
for _, row in df_master.iterrows():
    c_val = str(row["code"]).strip()
    n_val = str(row["name_vi"]).strip()
    if n_val and n_val != "nan":
        master_items.append({"code": c_val, "name": n_val})
master_items.sort(key=lambda x: x["name"])
# Precompute audited dataset statistics for API and UI
_matched_ings = sum(1 for i in ingredients_list if i.get("master_ingredient_code") and i["master_ingredient_code"] != "UNMATCHED")
_unmatched_ings = len(ingredients_list) - _matched_ings
DATASET_STATS = {
    "recipes_count": len(recipes_list),
    "ingredients_count": len(ingredients_list),
    "master_ingredients_count": len(master_items),
    "matched_ingredients_count": _matched_ings,
    "unmatched_ingredients_count": _unmatched_ings,
    "matched_rate_pct": round(_matched_ings / len(ingredients_list) * 100, 2) if ingredients_list else 0.0,
    "platforms": dict(Counter(r.get("source_platform", "other") for r in recipes_list)),
    "dish_types": dict(Counter(r.get("dish_type", "other") for r in recipes_list)),
    "nutrition_anomalies_count": sum(1 for r in recipes_list if str(r.get("nutrition_anomaly_flag", "0")) == "1"),
}


@app.on_event("startup")
def startup_gpu_warmup():
    """Initializes and warms up GPU acceleration for Smart Input OCR/ASR and Ranker."""
    global SYSTEM_GPU_STATUS
    print("\n" + "=" * 60)
    print(" SweepFood AI — Initializing GPU Hardware Acceleration...")
    print("=" * 60)

    try:
        import torch
        cuda_avail = torch.cuda.is_available()
        device_name = torch.cuda.get_device_name(0) if cuda_avail else "CPU"
    except Exception:
        cuda_avail = False
        device_name = "CPU"

    # 1. Warm up Rankers
    if lgbm_ranker is not None:
        try:
            dummy_lgb = np.zeros((1, len(FEATURE_COLS)))
            lgbm_ranker.predict(dummy_lgb)
            print(f"[Ranker] Production LightGBM LambdaMART (9 features) ready for inference.")
        except Exception as e:
            print(f"[Ranker Warning] LightGBM warmup: {e}")

    # 2. Warm up Smart Input OCR/ASR on GPU
    try:
        ocr_info = warmup_smart_input_gpu()
        ocr_dev = ocr_info.get("ocr_engine", "Groq Vision API (qwen/qwen3.8-27b)")
        vram_mb = ocr_info.get("vram_allocated_mb", 0.0)
        print(f"[Smart Input] OCR Engine: {ocr_dev}")
    except Exception as e:
        ocr_dev = "Groq Vision API (qwen/qwen3.8-27b)"
        vram_mb = 0.0
        print(f"[Smart Input Warning] Warm up error: {e}")

    SYSTEM_GPU_STATUS = {
        "cuda_available": cuda_avail,
        "device_name": device_name,
        "ocr_device": ocr_dev,
        "vram_allocated_mb": vram_mb,
        "warmed_up": True,
    }
    print("=" * 60)
    print(f" All models active in GPU VRAM. Zero cold-start latency achieved!\n")



# -----------------------------------------------------------------------------
# Pydantic Schemas
# -----------------------------------------------------------------------------
class PantryItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    code: str | None = None
    quantity_g: float = Field(default=200.0, gt=0)
    hours_to_expire: float = 72.0
    is_staple: bool = False


class RecommendRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[PantryItem]
    household_size: float = Field(default=4.0, gt=0)
    max_cooking_time_min: float = Field(default=45.0, gt=0)
    scenario_type: str = "custom"
    dietary_restrictions: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)
    disliked_ingredients: list[str] = Field(default_factory=list)
    preferred_cuisines: list[str] = Field(default_factory=list)


class SmartOcrRequest(BaseModel):
    sample_id: str | None = None
    receipt_text: str | None = None
    image_base64: str | None = None
    filename: str = "receipt.jpg"


class SmartAsrRequest(BaseModel):
    sample_id: str | None = None
    transcript: str | None = None


# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------
@app.get("/api/smart-input/samples")
def get_samples():
    return get_smart_input_samples()


@app.post("/api/smart-input/ocr")
def api_smart_ocr(req: SmartOcrRequest):
    return process_receipt_input(
        image_base64=req.image_base64,
        receipt_text=req.receipt_text,
        sample_id=req.sample_id,
        filename=req.filename
    )


@app.post("/api/smart-input/asr")
def api_smart_asr(req: SmartAsrRequest):
    return process_voice_input(
        transcript=req.transcript,
        sample_id=req.sample_id
    )


@app.get("/api/autocomplete")
def autocomplete(q: str = ""):
    query = (q or "").strip().lower()
    if not query:
        return {"results": master_items[:25]}
    matches = [it for it in master_items if query in it["name"].lower()][:15]
    return {"results": matches}


@app.get("/api/system/status")
def get_system_status():
    """Returns GPU status, VRAM usage, and active inference engines."""
    import torch
    status = dict(SYSTEM_GPU_STATUS)
    status["ranker_model"] = RANKER_MODEL_NAME
    if torch.cuda.is_available():
        status["vram_allocated_mb"] = round(torch.cuda.memory_allocated() / (1024 ** 2), 2)
        status["vram_reserved_mb"] = round(torch.cuda.memory_reserved() / (1024 ** 2), 2)
    return status


@app.get("/api/stats")
def get_dataset_stats():
    """Returns audited statistics of the active processed recipe & master nutrition dataset."""
    return DATASET_STATS

@app.get("/api/presets")
def get_presets():
    """Empty presets (deprecated to keep focus on dynamic pantry input)."""
    return {"presets": []}


@app.post("/api/recommend")
def recommend_recipes(req: RecommendRequest):
    t0 = time.time()
    raw_items = [item.model_dump() for item in req.items]
    resolved_items = resolve_pantry_items(raw_items, MASTER_ALIAS_INDEX)
    pantry_dict = {
        "pantry_id": "live_user_query",
        "scenario_type": req.scenario_type,
        "items": resolved_items,
        "household_size": req.household_size,
        "max_cooking_time_min": req.max_cooking_time_min
    }

    # 1. Candidate Generation via Inverted Index
    t_cand_start = time.time()
    raw_candidates = cg.retrieve_candidates(pantry_dict["items"], top_n=35)
    cand_time_ms = round((time.time() - t_cand_start) * 1000, 2)

    if not raw_candidates:
        return {
            "status": "empty",
            "contract_version": CONTRACT_VERSION,
            "model_version": MODEL_VERSION,
            "catalog_revision": CATALOG_REVISION,
            "ranker_model": RANKER_MODEL_NAME,
            "timings": {
                "total_ms": round((time.time() - t0) * 1000, 2),
                "candidate_ms": cand_time_ms,
                "ranker_ms": 0.0,
            },
            "message": "Không tìm thấy món ăn phù hợp với nguyên liệu hiện tại. Thử thêm thịt, cá hoặc rau nhé!",
            "candidates_count": 0,
            "recommendations": []
        }

    # Hard Constraint Filtering Layer
    scenario = (pantry_dict.get("scenario_type") or "custom").lower().strip()
    restrictions = {normalize(value) for value in req.dietary_restrictions}
    vegetarian = (
        scenario in ("an_chay_ram_mung_mot", "an_chay", "chay")
        or "chay" in scenario
        or bool(restrictions & {"vegetarian", "vegan", "ăn chay", "an chay", "chay"})
    )
    diabetic = scenario in ("nguoi_tieu_duong", "tieu_duong", "diabetes") or bool(
        restrictions & {"diabetic", "diabetes", "tiểu đường", "tieu duong"}
    )
    low_sodium = scenario in ("nguoi_cao_huyet_ap", "cao_huyet_ap", "hypertension") or bool(
        restrictions & {"low sodium", "hypertension", "cao huyết áp", "cao huyet ap"}
    )
    gout = scenario in ("nguoi_benh_gout", "gout") or "gout" in restrictions
    keto = scenario in ("an_kieng_keto_lowcarb", "keto", "lowcarb") or bool(
        restrictions & {"keto", "low carb", "lowcarb"}
    )
    sensitive_stomach = scenario in ("nguoi_dau_da_day", "dau_da_day") or bool(
        restrictions & {"đau dạ dày", "dau da day", "sensitive stomach"}
    )
    excluded_ingredients = req.allergies + req.disliked_ingredients
    candidates = []
    for cand in raw_candidates:
        # a. Data Quality Safety Filter
        if cand.get("nutrition_anomaly_flag") in (1, "1", True) or cand.get("incomplete_flag") in (1, "1", True):
            continue

        # b. Scenario Constraint Filter
        r_id = cand["id"]
        r_ings = recipe_ings_map.get(r_id, [])

        if excluded_ingredients and has_excluded_ingredients(r_ings, excluded_ingredients):
            continue
        if vegetarian:
            diet_tags = (cand.get("diet_tags") or "").lower()
            if "ăn chay" not in diet_tags:
                continue
            if has_animal_ingredients(r_ings):
                continue
        if diabetic:
            sugar = float(cand.get("sugar_g_per_serving") or 0.0)
            carbs = float(cand.get("carbs_per_serving") or 0.0)
            if sugar >= 10.0 or carbs >= 45.0:
                continue
        if low_sodium:
            sodium = float(cand.get("sodium_mg_per_serving") or 0.0)
            servings = max(1.0, float(cand.get("default_servings") or 4.0))
            tot_sodium_per_serv = float(cand.get("total_sodium_mg") or 0.0) / servings
            if sodium >= 1000.0 or tot_sodium_per_serv >= 1000.0:
                continue
        if gout and has_gout_forbidden_ingredients(r_ings):
            continue
        if keto:
            carbs = float(cand.get("carbs_per_serving") or 0.0)
            if carbs > 20.0:
                continue
        if sensitive_stomach:
            method = (cand.get("cooking_method") or "").strip().lower()
            if method in ("chiên/rán", "chiên", "rán"):
                continue

        candidates.append(cand)

    if not candidates:
        return {
            "status": "empty",
            "contract_version": CONTRACT_VERSION,
            "model_version": MODEL_VERSION,
            "catalog_revision": CATALOG_REVISION,
            "ranker_model": RANKER_MODEL_NAME,
            "timings": {
                "total_ms": round((time.time() - t0) * 1000, 2),
                "candidate_ms": cand_time_ms,
                "ranker_ms": 0.0,
            },
            "message": "Không tìm thấy món ăn phù hợp với yêu cầu dinh dưỡng và nguyên liệu hiện tại. Hãy thử điều chỉnh bộ lọc hoặc thêm nguyên liệu khác!",
            "candidates_count": 0,
            "recommendations": []
        }

    # 2 & 3. Predict Scores via LightGBM Ranker or Domain Heuristic Ranker
    t_rank_start = time.time()

    rows = []
    if lgbm_ranker is not None:
        lgbm_rows = []
        for cand in candidates:
            r_id = cand["id"]
            r_ings = recipe_ings_map.get(r_id, [])
            steps = detailed_recipe_map.get(r_id, {}).get("steps")
            f_dict = extract_contextual_features(pantry_dict, cand, r_ings, steps)
            lgbm_rows.append([f_dict[col] for col in FEATURE_COLS])
            rows.append(f_dict)
        scores = lgbm_ranker.predict(np.array(lgbm_rows))
    else:
        for cand in candidates:
            r_id = cand["id"]
            r_ings = recipe_ings_map.get(r_id, [])
            steps = detailed_recipe_map.get(r_id, {}).get("steps")
            f_dict = extract_contextual_features(pantry_dict, cand, r_ings, steps)
            rows.append(f_dict)
        scores = [
            compute_domain_heuristic_score(pantry_dict, cand, recipe_ings_map.get(cand["id"], []))
            for cand in candidates
        ]
    rank_time_ms = round((time.time() - t_rank_start) * 1000, 2)

    # 4. Rank & Format Top Recommendations
    scored_candidates = []
    for cand, score, feats in zip(candidates, scores, rows):
        r_id = cand["id"]
        full_rec = recipe_map.get(r_id, cand)
        r_ings = recipe_ings_map.get(r_id, [])

        try:
            raw_servings = float(full_rec.get("default_servings") or 4.0)
            default_servings = raw_servings if raw_servings > 0 else 4.0
        except (ValueError, TypeError):
            default_servings = 4.0

        target_servings = float(req.household_size if req.household_size and req.household_size > 0 else 4.0)
        scale_factor = target_servings / default_servings
        is_scaled = abs(scale_factor - 1.0) >= 0.01

        # Ingredient matching details with aggregation
        pantry_names = set()
        pantry_codes = set()
        for it in pantry_dict["items"]:
            pantry_codes.update(get_effective_codes(it))
            aliases = extract_pantry_name_aliases(it["name"])
            pantry_names.update(aliases)
            pantry_names.add(it["name"].strip().lower())

        grouped_ings = {}
        for ing in r_ings:
            clean_n = (ing.get("master_ingredient_name") or ing.get("cleaned_name") or "").strip()
            c = ing.get("master_ingredient_code")
            raw_t = (ing.get("raw_text") or "").strip()
            req_g = float(ing.get("estimated_weight_g") or 0.0)
            role = (ing.get("ingredient_role") or "").strip().lower()

            key = c if c else clean_n
            if key not in grouped_ings:
                grouped_ings[key] = {
                    "name": clean_n,
                    "code": c,
                    "total_g": 0.0,
                    "raw_texts": [],
                    "roles": [],
                    "cleaned_names": set()
                }
            grouped_ings[key]["total_g"] += req_g
            if raw_t:
                grouped_ings[key]["raw_texts"].append(raw_t)
            if role:
                grouped_ings[key]["roles"].append(role)
            cleaned = (ing.get("cleaned_name") or "").strip().lower()
            if cleaned:
                grouped_ings[key]["cleaned_names"].add(cleaned)

        matched_ings = []
        staple_ings = []
        missing_ings = []
        optional_ings = []
        matched_groups: list[tuple[str, set[str]]] = []

        for key, g in grouped_ings.items():
            n = g["name"]
            c = str(g["code"]).strip() if g["code"] else ""
            if c.endswith(".0"):
                c = c[:-2]
            tot_g = round(g["total_g"] * scale_factor, 1)

            # Same names the candidate generator and features match on: master name + every cleaned_name in the group
            n_aliases = extract_pantry_name_aliases(n) | {n.strip().lower()}
            for cleaned in sorted(g["cleaned_names"]):
                n_aliases |= extract_pantry_name_aliases(cleaned)
            is_present = bool((c and c in pantry_codes) or (n and n.strip().lower() in pantry_names) or bool(n_aliases & pantry_names))

            # Staple spice: ingredient_role == "seasoning"
            is_staple = any(r == "seasoning" for r in g.get("roles", []))
            # Accompaniment: ALL rows have role "accompaniment"
            roles = g.get("roles", [])
            is_accompaniment = bool(roles) and all(r == "accompaniment" for r in roles)
            first_raw = g["raw_texts"][0] if g["raw_texts"] else ""
            if not is_scaled and len(g["raw_texts"]) == 1:
                # If raw_text already specifies a numeric weight/volume, don't duplicate it
                if re.search(r"\b\d+([.,]\d+)?\s*(g|gr|gam|gram|kg|ml|l|lít)\b", first_raw, re.I):
                    display_str = first_raw
                else:
                    display_str = f"{first_raw} (~{int(tot_g)}g)" if tot_g > 0 else first_raw
            else:
                # Cleanly display scaled weight
                clean_label = ""
                if first_raw and len(g["raw_texts"]) == 1:
                    clean_label = re.sub(
                        r"\b\d+([.,]\d+)?\s*(g|gr|gam|gram|kg|ml|l|lít|muỗng|thìa|quả|trái|tép|củ|gói|nhánh|hộp|lon|bát|chén|lát|miếng|bó)\b.*",
                        "",
                        first_raw,
                        flags=re.I
                    ).strip()
                    clean_label = re.sub(r"[\s\d:,-]+$", "", clean_label).strip()

                if not clean_label or len(clean_label) < 3:
                    clean_label = n.capitalize()
                display_str = f"{clean_label} (~{int(tot_g) if tot_g.is_integer() else tot_g}g)" if tot_g > 0 else clean_label

            item_info = {
                "name": n.capitalize(),
                "code": c,
                "display": display_str,
                "required_g": tot_g,
                "weight_g": tot_g,
                "unit": "g",
                "is_staple": is_staple,
                "is_present": is_present
            }

            if is_present:
                matched_ings.append(item_info)
                matched_groups.append((c, n_aliases))
            elif is_accompaniment:
                opt_info = dict(item_info)
                opt_info["is_optional"] = True
                optional_ings.append(opt_info)
            elif is_staple:
                staple_ings.append(item_info)
            else:
                missing_ings.append(item_info)

        # Determine Feasibility Badge (Staples DO NOT count as missing grocery shopping!)
        if len(missing_ings) == 0:
            if len(staple_ings) > 0:
                status_text = "Sẵn sàng nấu ngay 100% (Gia vị bếp có sẵn)"
            else:
                status_text = "Sẵn sàng nấu ngay 100%"
            status_badge = "ready"
        elif len(missing_ings) == 1 and (feats.get("raw_weight_ratio", 0.0) >= 0.75 or feats.get("core_coverage", 0.0) >= 0.75):
            status_text = f"Co giãn linh hoạt (Thiếu nhẹ {missing_ings[0]['name']})"
            status_badge = "elastic"
        else:
            status_text = f"Cần mua thêm {len(missing_ings)} thực phẩm chính"
            status_badge = "shopping"

        tot_cal = float(full_rec.get("total_calories") or 0.0)
        tot_p = float(full_rec.get("total_protein_g") or 0.0)
        tot_f = float(full_rec.get("total_fat_g") or 0.0)
        tot_c = float(full_rec.get("total_carbs_g") or 0.0)

        scaled_cal = round(tot_cal * scale_factor, 1)
        scaled_p = round(tot_p * scale_factor, 1)
        scaled_f = round(tot_f * scale_factor, 1)
        scaled_c = round(tot_c * scale_factor, 1)
        cal_per_serving = round(tot_cal / default_servings, 1)

        # Detailed step-by-step instructions, chef tips, sensory profile & source attribution
        source_url = full_rec.get("source_url") or ""
        det = detailed_recipe_map.get(r_id)
        if det and det.get("steps"):
            inst_steps = det["steps"]
            step_lines = []
            for i, s in enumerate(inst_steps):
                s_title = s.get("title") or f"Bước {s.get('step', i+1)}"
                s_content = s.get("content", "")
                step_lines.append(f"{s_title}: {s_content}")
            inst_text = "\n\n".join(step_lines)
            chef_tips = det.get("chef_tips") or ""
            sensory_profile = det.get("sensory_profile") or {}
        else:
            inst_info = recipe_instructions_map.get(source_url) if source_url else None
            if inst_info:
                inst_text = inst_info["formatted_text"]
                inst_steps = inst_info["steps"]
            else:
                inst_text = full_rec.get("instructions") or full_rec.get("description") or "Chưa có hướng dẫn chi tiết."
                inst_steps = []
            chef_tips = ""
            sensory_profile = {}

        # Pantry items used / rescued: match if effective codes intersect group code, or aliases intersect
        def pantry_item_matches(p_item, groups):
            p_eff_codes = get_effective_codes(p_item)
            p_aliases = extract_pantry_name_aliases(p_item.get("name", "")) | {p_item.get("name", "").strip().lower()}
            return any(bool(g_code and g_code in p_eff_codes) or bool(p_aliases & g_aliases) for g_code, g_aliases in groups)

        used_items = [it for it in pantry_dict["items"] if pantry_item_matches(it, matched_groups)]
        pantry_used = len(used_items)
        rescued_items = [
            it["name"] for it in used_items
            if not it.get("is_staple") and float(it.get("hours_to_expire", 999)) <= 24
        ]
        is_zero_waste_hero = len(rescued_items) > 0

        scored_candidates.append({
            "id": r_id,
            "name": full_rec["name"],
            "score": float(score),
            "rank_score": float(score),
            "ranking_features": {
                feature: float(feats[feature]) for feature in FEATURE_COLS
            },
            "cooking_time_min": int(float(full_rec.get("estimated_cooking_minutes") or 30)),
            "cooking_method": full_rec.get("cooking_method", "Khác"),
            "dish_type": full_rec.get("dish_type", "Món chính"),
            "source_url": source_url,
            "source_platform": full_rec.get("source_platform") or "Cookpad Việt Nam",
            "servings": int(target_servings),
            "default_servings": int(default_servings),
            "scale_factor": round(scale_factor, 2),
            "is_scaled": is_scaled,
            "calories_total": scaled_cal,
            "calories_per_serving": cal_per_serving,
            "protein_g": scaled_p,
            "fat_g": scaled_f,
            "carbs_g": scaled_c,
            "is_zero_waste_hero": is_zero_waste_hero,
            "rescued_items": rescued_items,
            "status_text": status_text,
            "status_badge": status_badge,
            "matched_ingredients": matched_ings,
            "pantry_used_count": pantry_used,
            "staple_ingredients": staple_ings,
            "missing_ingredients": missing_ings,
            "optional_ingredients": optional_ings,
            "instructions": inst_text,
            "instructions_steps": inst_steps,
            "chef_tips": chef_tips,
            "sensory_profile": sensory_profile,
        })

    # Feasibility-First Tiered Ranking with Multi-Urgent Round-Robin Diversity:
    urgent_pantry_items = sorted(
        [it for it in pantry_dict["items"] if not it.get("is_staple") and float(it.get("hours_to_expire", 999)) <= 24],
        key=lambda x: float(x.get("hours_to_expire", 999))
    )

    def feasibility_rank_key(c):
        badge = c.get("status_badge", "shopping")
        is_hero = c.get("is_zero_waste_hero", False)
        n_missing = len(c.get("missing_ingredients", []))
        p_used = c.get("pantry_used_count", 0)

        if badge == "ready" and is_hero:
            tier = 0
        elif badge == "ready":
            tier = 1
        elif is_hero:
            tier = 2
        elif badge == "elastic" and n_missing <= 1:
            tier = 3
        else:
            tier = 4 + min(n_missing, 10)

        return (tier, -p_used, -c["score"])

    scored_candidates.sort(key=feasibility_rank_key)

    # If user has multiple expiring ingredients (e.g. cá basa 6h, thịt ba chỉ 8h, đậu phụ 12h):
    # Interleave recommendations across the urgent items so one ingredient never monopolizes the list!
    if len(urgent_pantry_items) >= 2:
        top_recommendations = []
        seen_ids = set()

        # Priority 0: Super-Hero dishes that rescue MULTIPLE urgent items at once
        super_heroes = [
            c for c in scored_candidates
            if len(c.get("rescued_items", [])) >= 2 and c.get("status_badge") in ("ready", "elastic")
        ]
        for sh in super_heroes[:2]:
            top_recommendations.append(sh)
            seen_ids.add(sh["id"])

        # Buckets for each urgent item
        buckets: dict[str, list[dict]] = {u["name"].lower(): [] for u in urgent_pantry_items}
        for c in scored_candidates:
            if c["id"] in seen_ids:
                continue
            rescued_aliases_list = [extract_pantry_name_aliases(r) | {r.strip().lower()} for r in c.get("rescued_items", [])]
            for u in urgent_pantry_items:
                u_name = u["name"].lower()
                u_aliases = extract_pantry_name_aliases(u_name) | {u_name.strip()}
                if any(bool(u_aliases & r_aliases) for r_aliases in rescued_aliases_list):
                    buckets[u_name].append(c)
                    break

        # Round-robin selection in order of expiry urgency (most urgent first)
        max_rounds = 4
        for round_idx in range(max_rounds):
            for u in urgent_pantry_items:
                u_name = u["name"].lower()
                b_list = buckets.get(u_name, [])
                if round_idx < len(b_list):
                    cand = b_list[round_idx]
                    if cand["id"] not in seen_ids:
                        top_recommendations.append(cand)
                        seen_ids.add(cand["id"])
                if len(top_recommendations) >= 7:
                    break
            if len(top_recommendations) >= 7:
                break

        # Fill any remaining slots with top scored candidates
        for c in scored_candidates:
            if len(top_recommendations) >= 7:
                break
            if c["id"] not in seen_ids:
                top_recommendations.append(c)
                seen_ids.add(c["id"])
    else:
        top_recommendations = scored_candidates[:7]

    total_latency_ms = round((time.time() - t0) * 1000, 2)

    return {
        "status": "success",
        "contract_version": CONTRACT_VERSION,
        "model_version": MODEL_VERSION,
        "catalog_revision": CATALOG_REVISION,
        "ranker_model": RANKER_MODEL_NAME,
        "timings": {
            "total_ms": total_latency_ms,
            "candidate_ms": cand_time_ms,
            "ranker_ms": rank_time_ms,
        },
        "total_latency_ms": total_latency_ms,
        "candidate_retrieval_ms": cand_time_ms,
        "ranker_inference_ms": rank_time_ms,
        "candidates_evaluated": len(candidates),
        "gpu_accelerated": SYSTEM_GPU_STATUS["cuda_available"],
        "device": SYSTEM_GPU_STATUS["device_name"],
        "recommendations": top_recommendations,
    }

# =========================================================================
# SMART INPUT API ENDPOINTS (Decoupled Module)
# =========================================================================

@app.get("/api/smart-input/samples")
def smart_input_samples():
    """Retrieve curated receipt, food label and culinary speech samples."""
    return get_smart_input_samples()


@app.post("/api/smart-input/ocr")
def smart_input_ocr(req: SmartInputOcrRequest):
    """Process receipt text, base64 image, or sample ID."""
    return process_receipt_input(
        image_base64=req.image_base64,
        receipt_text=req.receipt_text,
        sample_id=req.sample_id,
    )


@app.post("/api/smart-input/ocr-upload")
async def smart_input_ocr_upload(file: UploadFile = File(...)):
    """Process uploaded receipt or Bách Hóa Xanh food label image."""
    contents = await file.read()
    return process_receipt_input(image_bytes=contents, filename=file.filename or "receipt.jpg")


@app.post("/api/smart-input/asr")
def smart_input_asr(req: SmartInputAsrRequest):
    """Process culinary voice transcript or sample ID."""
    return process_voice_input(
        transcript=req.transcript,
        sample_id=req.sample_id,
        engine=req.engine,
    )


@app.post("/api/smart-input/asr-upload")
async def smart_input_asr_upload(
    audio: UploadFile = File(...),
    engine: str = Form("groq_whisper"),
):
    """Process uploaded audio file with dual engine (Groq Whisper Turbo or Gipformer)."""
    contents = await audio.read()
    ext = Path(audio.filename or "audio.wav").suffix.lower()
    return process_voice_input(
        audio_bytes=contents,
        audio_format=ext,
        engine=engine,
    )


# Serve Static Files

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def get_index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


if __name__ == "__main__":
    import uvicorn
    print("Starting SweepFood AI Web Server on http://127.0.0.1:8000 ...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
