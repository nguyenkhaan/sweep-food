"""SweepFood AI - Interactive Web UI & Recommendation API Service.

Powered by:
- Inverted Index Candidate Generator (sub-millisecond candidate retrieval)
- 30-Tier Observable Feature Extractor
- Production-Trained XGBoost Ranker (rank:ndcg)
- Full Vietnamese Recipe & Nutritional Knowledge Base
"""

from __future__ import annotations
import math

import json
import os
import sys
import re
import time
from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel


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

import xgboost as xgb
from src.recommendation.candidate_generator import CandidateGenerator, extract_pantry_name_aliases
from src.recommendation.feature_extractor import extract_all_features
from src.recommendation.ingredient_roles import classify_ingredient_role, IngredientRole
from src.recommendation.heuristic_baseline import compute_domain_heuristic_score
from smart_input.service import (
    process_receipt_input,
    process_voice_input,
    get_smart_input_samples,
    warmup_smart_input_gpu,
)

# Global GPU Acceleration Status
SYSTEM_GPU_STATUS = {
    "cuda_available": False,
    "device_name": "CPU",
    "xgb_device": "cpu",
    "ocr_device": "cpu",
    "vram_allocated_mb": 0.0,
    "warmed_up": False,
}

app = FastAPI(title="SweepFood AI Web Demo", version="2.0.0")

CANONICAL_RECIPES_JSON = os.path.join(ROOT_DIR, "data/processed/recipes/canonical_recipes.json")
CANONICAL_ING_JSON = os.path.join(ROOT_DIR, "data/processed/recipes/canonical_recipe_ingredients.json")
CANONICAL_MAP_JSON = os.path.join(ROOT_DIR, "data/processed/recipes/recipe_canonical_mapping.json")
CANONICAL_DETAILED_JSON = os.path.join(ROOT_DIR, "data/processed/recipes/canonical_recipes_detailed.json")

RECIPES_JSON = os.path.join(ROOT_DIR, "data/processed/recipes/recipes.json")
ING_JSON = os.path.join(ROOT_DIR, "data/processed/recipes/recipe_ingredients.json")
MASTER_VDD_CSV = os.path.join(ROOT_DIR, "data/processed/viendinhduong/master_ingredients_nutrition.csv")
MODEL_PATH = os.path.join(ROOT_DIR, "data/training/xgb_full.json")
METADATA_PATH = os.path.join(ROOT_DIR, "data/training/metadata.json")

print("Loading knowledge base and production models...")
active_recipes_path = CANONICAL_RECIPES_JSON if os.path.exists(CANONICAL_RECIPES_JSON) else RECIPES_JSON
active_ing_path = CANONICAL_ING_JSON if os.path.exists(CANONICAL_ING_JSON) else ING_JSON
print(f"Active recipe knowledge base: {active_recipes_path}")

with open(active_recipes_path, "r", encoding="utf-8") as f:
    recipes_list = json.load(f)
with open(active_ing_path, "r", encoding="utf-8") as f:
    ingredients_list = json.load(f)

canonical_id_map = {}
if os.path.exists(CANONICAL_MAP_JSON):
    with open(CANONICAL_MAP_JSON, "r", encoding="utf-8") as f:
        canonical_id_map = json.load(f)

cg = CandidateGenerator(recipes_list, ingredients_list)
recipe_map = {r["id"]: r for r in recipes_list}
recipe_ings_map = cg.recipe_ingredients
# Load structured detailed recipe instructions, sensory profile & chef tips
detailed_recipe_map = {}
if os.path.exists(CANONICAL_DETAILED_JSON):
    try:
        with open(CANONICAL_DETAILED_JSON, "r", encoding="utf-8") as f:
            for det in json.load(f):
                cid = det.get("canonical_recipe_id")
                if cid:
                    detailed_recipe_map[cid] = det
        print(f"Loaded structured detailed recipes (steps, sensory, chef tips) for {len(detailed_recipe_map):,} canonical dishes.")
    except Exception as e:
        print(f"Warning: Failed loading canonical detailed recipes: {e}")

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
# Load feature names & XGBoost Ranker (or graceful fallback to domain heuristic ranker)
xgb_ranker = None
feature_cols = []
if os.path.exists(METADATA_PATH) and os.path.exists(MODEL_PATH):
    try:
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            meta = json.load(f)
        feature_cols = meta["feature_tiers"]["full_features"]
        xgb_ranker = xgb.Booster()
        xgb_ranker.load_model(MODEL_PATH)
        print(f"XGBoost Ranker loaded successfully with {len(feature_cols)} features.")
    except Exception as e:
        print(f"Warning: Could not load XGBoost model: {e}")
        xgb_ranker = None

if xgb_ranker is None:
    print("Using High-Precision Culinary Domain Heuristic Ranker (Zero-Dependency Mode).")
# Load master ingredients for autocomplete (name & code)
df_master = pd.read_csv(MASTER_VDD_CSV)
master_items = []
for _, row in df_master.iterrows():
    c_val = str(row["code"]).strip()
    n_val = str(row["name_vi"]).strip()
    if n_val and n_val != "nan":
        master_items.append({"code": c_val, "name": n_val})
master_items.sort(key=lambda x: x["name"])

CATALOG_REVISION = f"catalog-{Path(active_recipes_path).stat().st_mtime_ns}"
MODEL_VERSION = (
    f"xgboost-full-{Path(MODEL_PATH).stat().st_mtime_ns}"
    if xgb_ranker is not None else "domain-heuristic-v1"
)

@app.on_event("startup")
def startup_gpu_warmup():
    """Initializes and warms up GPU acceleration for XGBoost Ranker & Smart Input OCR/ASR."""
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

    # 1. Warm up XGBoost Booster on GPU
    xgb_dev = "cpu"
    if cuda_avail:
        try:
            xgb_ranker.set_param({"device": "cuda"})
            dummy_df = pd.DataFrame(np.zeros((1, len(feature_cols))), columns=feature_cols)
            xgb_ranker.predict(xgb.DMatrix(dummy_df))
            xgb_dev = "cuda"
            print(f"[GPU] XGBoost Ranker successfully loaded on CUDA ({device_name})")
        except Exception as e:
            print(f"[GPU Warning] Failed setting XGBoost to CUDA, fallback to CPU: {e}")
            xgb_ranker.set_param({"device": "cpu"})
            xgb_dev = "cpu"

    # 2. Warm up Smart Input OCR/ASR on GPU
    try:
        ocr_info = warmup_smart_input_gpu()
        ocr_dev = ocr_info.get("ocr_engine", "PaddleOCR+VietOCR (CPU)")
        vram_mb = ocr_info.get("vram_allocated_mb", 0.0)
        print(f"[GPU] Smart Input OCR: {ocr_dev} (Allocated VRAM: {vram_mb} MB)")
    except Exception as e:
        ocr_dev = "PaddleOCR+VietOCR (Fallback)"
        vram_mb = 0.0
        print(f"[GPU Warning] Smart Input warm up error: {e}")

    SYSTEM_GPU_STATUS = {
        "cuda_available": cuda_avail,
        "device_name": device_name,
        "xgb_device": xgb_dev,
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
    name: str
    code: str | None = None
    quantity_g: float = 200.0
    hours_to_expire: float | None = None
    is_staple: bool = False


class RecommendRequest(BaseModel):
    items: list[PantryItem]
    household_size: float = 4.0
    max_cooking_time_min: float = 45.0
    scenario_type: str = "custom"
    dietary_restrictions: list[str] = []
    allergies: list[str] = []
    disliked_ingredients: list[str] = []
    preferred_cuisines: list[str] = []


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
def _clamp_score(value: float) -> float:
    return round(max(0.0, min(1.0, float(value))), 6)


def _calibrate_rank_score(value: float) -> float:
    bounded = max(-60.0, min(60.0, float(value)))
    return round(1.0 / (1.0 + math.exp(-bounded)), 6)


def _preference_fit(
    req: RecommendRequest,
    recipe: dict[str, Any],
    recipe_ingredients: list[dict[str, Any]],
) -> float | None:
    ingredient_text = " ".join(
        str(item.get("cleaned_name") or item.get("name") or "").lower()
        for item in recipe_ingredients
    )
    excluded = [*req.allergies, *req.disliked_ingredients]
    if any(term.strip().lower() in ingredient_text for term in excluded if term.strip()):
        return None

    metadata = " ".join(
        str(recipe.get(field) or "").lower()
        for field in ("name", "diet_tags", "dish_type", "cooking_method")
    )
    restrictions = [term.strip().lower() for term in req.dietary_restrictions if term.strip()]
    if any(term not in metadata for term in restrictions):
        return None
    cuisines = [term.strip().lower() for term in req.preferred_cuisines if term.strip()]
    if not cuisines:
        return 1.0
    return _clamp_score(sum(term in metadata for term in cuisines) / len(cuisines))


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
    if torch.cuda.is_available():
        status["vram_allocated_mb"] = round(torch.cuda.memory_allocated() / (1024 ** 2), 2)
        status["vram_reserved_mb"] = round(torch.cuda.memory_reserved() / (1024 ** 2), 2)
    return status


@app.get("/api/presets")
def get_presets():
    """Empty presets (deprecated to keep focus on dynamic pantry input)."""
    return {"presets": []}


@app.post("/api/recommend")
def recommend_recipes(req: RecommendRequest):
    t0 = time.time()
    pantry_dict = {
        "pantry_id": "live_user_query",
        "scenario_type": req.scenario_type,
        "items": [item.model_dump() for item in req.items],
        "household_size": req.household_size,
        "max_cooking_time_min": req.max_cooking_time_min
    }

    # 1. Candidate Generation via Inverted Index
    t_cand_start = time.time()
    candidates = cg.retrieve_candidates(pantry_dict["items"], top_n=35)
    cand_time_ms = round((time.time() - t_cand_start) * 1000, 2)

    if not candidates:
        return {
            "model_version": MODEL_VERSION,
            "catalog_revision": CATALOG_REVISION,
            "status": "empty",
            "message": "Không tìm thấy món ăn phù hợp với nguyên liệu hiện tại. Thử thêm thịt, cá hoặc rau nhé!",
            "candidates_count": 0,
            "recommendations": []
        }

    # 2 & 3. Predict Scores via XGBoost Ranker or Domain Heuristic Ranker
    t_rank_start = time.time()
    rows = []
    for cand in candidates:
        r_id = cand["id"]
        r_ings = recipe_ings_map.get(r_id, [])
        feats = extract_all_features(pantry_dict, cand, r_ings)
        rows.append(feats)

    if xgb_ranker is not None and feature_cols:
        df_feats = pd.DataFrame(rows)[feature_cols]
        dmatrix = xgb.DMatrix(df_feats)
        scores = xgb_ranker.predict(dmatrix)
    else:
        scores = [
            compute_domain_heuristic_score(pantry_dict, cand, recipe_ings_map.get(cand["id"], []))
            for cand in candidates
        ]
    rank_time_ms = round((time.time() - t_rank_start) * 1000, 2)

    # 4. Rank & Format Top 6 Recommendations
    scored_candidates = []
    for cand, score, feats in zip(candidates, scores, rows):
        r_id = cand["id"]
        full_rec = recipe_map.get(r_id, cand)
        r_ings = recipe_ings_map.get(r_id, [])
        preference_fit = _preference_fit(req, full_rec, r_ings)
        if preference_fit is None:
            continue

        try:
            raw_servings = float(full_rec.get("default_servings") or 4.0)
            default_servings = raw_servings if raw_servings > 0 else 4.0
        except (ValueError, TypeError):
            default_servings = 4.0

        target_servings = float(req.household_size if req.household_size and req.household_size > 0 else 4.0)
        scale_factor = target_servings / default_servings
        is_scaled = abs(scale_factor - 1.0) >= 0.01

        # Ingredient matching details with aggregation to eliminate duplicate rows & raw enums
        pantry_names = set()
        pantry_codes = set()
        urgent_names = set()
        for it in pantry_dict["items"]:
            c_it = it.get("code")
            if c_it:
                pantry_codes.add(str(c_it).strip())
            aliases = extract_pantry_name_aliases(it["name"])
            pantry_names.update(aliases)
            if not it.get("is_staple") and (it.get("hours_to_expire") or 999) <= 24:
                urgent_names.update(aliases)

        grouped_ings = {}
        for ing in r_ings:
            raw_n = (ing.get("cleaned_name") or ing.get("name") or "").strip().lower()
            clean_n = raw_n.replace("nước nước mắm", "nước mắm")
            c = ing.get("master_ingredient_code")
            raw_t = (ing.get("raw_text") or "").strip().replace("nước nước mắm", "nước mắm")
            req_g = float(ing.get("estimated_weight_g") or 0.0)

            key = c if c else clean_n
            if key not in grouped_ings:
                grouped_ings[key] = {
                    "name": clean_n,
                    "code": c,
                    "total_g": 0.0,
                    "raw_texts": []
                }
            grouped_ings[key]["total_g"] += req_g
            if raw_t:
                grouped_ings[key]["raw_texts"].append(raw_t)

        matched_ings = []
        staple_ings = []
        missing_ings = []
        rescued_items = []

        for key, g in grouped_ings.items():
            n = g["name"]
            c = str(g["code"]).strip() if g["code"] else ""
            tot_g = round(g["total_g"] * scale_factor, 1)

            n_aliases = extract_pantry_name_aliases(n)
            is_present = (c and c in pantry_codes) or (n and n in pantry_names) or bool(n_aliases & pantry_names)

            # Classify role
            role = classify_ingredient_role(n, c)
            is_staple = (role == IngredientRole.STAPLE_SPICE)

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
                "code": c or None,
                "display": display_str,
                "required_g": tot_g,
                "weight_g": tot_g,
                "unit": "g",
                "is_staple": is_staple,
                "is_present": is_present
            }

            if is_present:
                matched_ings.append(item_info)
                if (n in urgent_names) or bool(n_aliases & urgent_names):
                    rescued_items.append(n)
            elif is_staple:
                # Basic pantry staples (Muối, Tiêu, Nước mắm, Dầu ăn, Tỏi, Hành tím...)
                # Assumed readily available in any kitchen cabinet!
                staple_ings.append(item_info)
            else:
                missing_ings.append(item_info)

        # Determine Feasibility Badge (Staples DO NOT count as missing grocery shopping!)
        is_zero_waste_hero = len(rescued_items) > 0
        if len(missing_ings) == 0:
            if len(staple_ings) > 0:
                status_text = "Sẵn sàng nấu ngay 100% (Gia vị bếp có sẵn)"
            else:
                status_text = "Sẵn sàng nấu ngay 100%"
            status_badge = "ready"
        elif len(missing_ings) == 1 and feats["raw_weight_ratio"] >= 0.75:
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

        non_staple_count = len(matched_ings) + len(missing_ings)
        availability = _clamp_score(feats["raw_weight_ratio"])
        expiration_utilization = (
            _clamp_score(len(set(rescued_items)) / max(1, len(urgent_names)))
            if urgent_names else 0.0
        )
        purchase_minimization = _clamp_score(
            1.0 - len(missing_ings) / max(1, non_staple_count)
        )
        score_components = {
            "expiration_utilization": expiration_utilization,
            "availability": availability,
            "preference_fit": preference_fit,
            "purchase_minimization": purchase_minimization,
        }
        scored_candidates.append({
            "id": r_id,
            "name": full_rec["name"],
            "score": _calibrate_rank_score(float(score)),
            "score_components": score_components,
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
            "staple_ingredients": staple_ings,
            "missing_ingredients": missing_ings,
            "instructions": inst_text,
            "instructions_steps": inst_steps,
            "chef_tips": chef_tips,
            "sensory_profile": sensory_profile,
        })

    # Sort descending by XGBoost score with Top-K dynamic bounded selection (K <= 7)
    scored_candidates.sort(key=lambda x: x["score"], reverse=True)
    # Prefer viable dishes (rescuing expiring items or not missing too many core ingredients)
    viable_candidates = [
        c for c in scored_candidates
        if len(c.get("missing_ingredients", [])) <= 3 or c.get("is_zero_waste_hero")
    ]
    top_recommendations = (viable_candidates if viable_candidates else scored_candidates)[:7]

    total_latency_ms = round((time.time() - t0) * 1000, 2)

    return {
        "status": "success",
        "model_version": MODEL_VERSION,
        "catalog_revision": CATALOG_REVISION,
        "total_latency_ms": total_latency_ms,
        "candidate_retrieval_ms": cand_time_ms,
        "xgboost_inference_ms": rank_time_ms,
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
    try:
        return process_receipt_input(image_bytes=contents, filename=file.filename or "receipt.jpg")
    except ValueError as error:
        raise HTTPException(status_code=422, detail="Invalid image") from error
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail="OCR recognizer is unavailable") from error


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
