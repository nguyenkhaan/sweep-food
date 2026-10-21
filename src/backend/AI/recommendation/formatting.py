"""Ingredient grouping, scaling, and feasibility formatting for recipe recommendations."""

from __future__ import annotations

import re
from typing import Any

from AI.catalog.master_index import get_effective_codes
from AI.recommendation.candidate_generator import extract_pantry_name_aliases


def _clean_code(code_val: object) -> str:
    if code_val is None:
        return ""
    c = str(code_val).strip().removesuffix(".0")
    return "" if c.lower() == "nan" else c


def pantry_item_matches(
    p_item: dict[str, Any],
    groups: list[tuple[str, set[str]]],
) -> bool:
    """Return True if pantry item matches any group's code or aliases."""
    p_eff_codes = get_effective_codes(p_item)
    p_name = (p_item.get("name") or "").strip().lower()
    p_aliases = extract_pantry_name_aliases(p_name) | {p_name}
    return any(
        bool(g_code and g_code in p_eff_codes) or bool(p_aliases & g_aliases)
        for g_code, g_aliases in groups
    )


def format_candidate_recommendation(
    cand: dict[str, Any],
    full_rec: dict[str, Any],
    score: float,
    feats: dict[str, float],
    r_ings: list[dict[str, Any]],
    pantry_dict: dict[str, Any],
    household_size: float,
) -> dict[str, Any]:
    """Group ingredients, scale quantities, evaluate feasibility badges, and format recommendation."""
    r_id = str(cand["id"])

    try:
        raw_servings = float(full_rec.get("default_servings") or 4.0)
        default_servings = raw_servings if raw_servings > 0 else 4.0
    except (ValueError, TypeError):
        default_servings = 4.0

    target_servings = float(household_size if household_size > 0 else 4.0)
    scale_factor = target_servings / default_servings
    is_scaled = abs(scale_factor - 1.0) >= 0.01

    pantry_names: set[str] = set()
    pantry_codes: set[str] = set()
    for it in pantry_dict.get("items", []):
        pantry_codes.update(get_effective_codes(it))
        it_name = (it.get("name") or "").strip().lower()
        pantry_names.update(extract_pantry_name_aliases(it_name))
        pantry_names.add(it_name)

    grouped_ings: dict[str, dict[str, Any]] = {}
    for ing in r_ings:
        clean_n = (ing.get("master_ingredient_name") or ing.get("cleaned_name") or "").strip()
        c = ing.get("master_ingredient_code")
        raw_t = (ing.get("raw_text") or "").strip()
        req_g = float(ing.get("estimated_weight_g") or 0.0)
        role = (ing.get("ingredient_role") or "").strip().lower()

        key = str(c) if c else clean_n
        if key not in grouped_ings:
            grouped_ings[key] = {
                "name": clean_n,
                "code": c,
                "total_g": 0.0,
                "raw_texts": [],
                "roles": [],
                "cleaned_names": set(),
            }
        grouped_ings[key]["total_g"] += req_g
        if raw_t:
            grouped_ings[key]["raw_texts"].append(raw_t)
        if role:
            grouped_ings[key]["roles"].append(role)
        cleaned = (ing.get("cleaned_name") or "").strip().lower()
        if cleaned:
            grouped_ings[key]["cleaned_names"].add(cleaned)

    matched_ings: list[dict[str, Any]] = []
    staple_ings: list[dict[str, Any]] = []
    missing_ings: list[dict[str, Any]] = []
    optional_ings: list[dict[str, Any]] = []
    matched_groups: list[tuple[str, set[str]]] = []
    matched_weights_g: list[float] = []

    for g in grouped_ings.values():
        n = str(g["name"])
        c = _clean_code(g.get("code"))
        tot_g = round(float(g["total_g"]) * scale_factor, 1)

        n_aliases = extract_pantry_name_aliases(n) | {n.strip().lower()}
        for cleaned in sorted(g["cleaned_names"]):
            n_aliases |= extract_pantry_name_aliases(cleaned)

        is_present = bool(
            (c and c in pantry_codes)
            or (n and n.strip().lower() in pantry_names)
            or bool(n_aliases & pantry_names)
        )

        roles = g.get("roles", [])
        is_staple = any(r == "seasoning" for r in roles)
        is_accompaniment = bool(roles) and all(r == "accompaniment" for r in roles)
        first_raw = g["raw_texts"][0] if g["raw_texts"] else ""

        if not is_scaled and len(g["raw_texts"]) == 1:
            if re.search(r"\b\d+([.,]\d+)?\s*(g|gr|gam|gram|kg|ml|l|lít)\b", first_raw, re.IGNORECASE):
                display_str = first_raw
            else:
                display_str = f"{first_raw} (~{int(tot_g)}g)" if tot_g > 0 else first_raw
        else:
            clean_label = ""
            if first_raw and len(g["raw_texts"]) == 1:
                clean_label = re.sub(
                    r"\b\d+([.,]\d+)?\s*(g|gr|gam|gram|kg|ml|l|lít|muỗng|thìa|quả|trái|tép|củ|gói|nhánh|hộp|lon|bát|chén|lát|miếng|bó)\b.*",
                    "",
                    first_raw,
                    flags=re.IGNORECASE,
                ).strip()
                clean_label = re.sub(r"[\s\d:,-]+$", "", clean_label).strip()

            if not clean_label or len(clean_label) < 3:
                clean_label = n.capitalize()
            display_str = (
                f"{clean_label} (~{int(tot_g) if tot_g.is_integer() else tot_g}g)"
                if tot_g > 0
                else clean_label
            )

        item_info: dict[str, Any] = {
            "name": n.capitalize(),
            "code": c if c else None,
            "display": display_str,
            "required_g": tot_g,
            "weight_g": tot_g,
            "unit": "g",
            "is_staple": is_staple,
            "is_present": is_present,
        }

        if is_present:
            matched_ings.append(item_info)
            matched_groups.append((c, n_aliases))
            matched_weights_g.append(tot_g)
        elif is_accompaniment:
            opt_info = dict(item_info)
            opt_info["is_optional"] = True
            optional_ings.append(opt_info)
        elif is_staple:
            staple_ings.append(item_info)
        else:
            missing_ings.append(item_info)

    # Feasibility Badge: staples do not count against grocery gaps
    if len(missing_ings) == 0:
        if len(staple_ings) > 0:
            status_text = "Sẵn sàng nấu ngay 100% (Gia vị bếp có sẵn)"
        else:
            status_text = "Sẵn sàng nấu ngay 100%"
        status_badge = "ready"
    elif len(missing_ings) == 1 and (
        feats.get("raw_weight_ratio", 0.0) >= 0.75 or feats.get("core_coverage", 0.0) >= 0.75
    ):
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

    used_items = [
        it for it in pantry_dict.get("items", [])
        if pantry_item_matches(it, matched_groups)
    ]
    pantry_used = len(used_items)
    rescued_requirements: dict[str, dict[str, Any]] = {}
    for it in used_items:
        if it.get("is_staple") or float(it.get("hours_to_expire") or 999.0) > 24.0:
            continue
        name = str(it["name"])
        key = name.strip().lower()
        if key in rescued_requirements:
            continue
        required_g = sum(
            weight_g
            for group, weight_g in zip(matched_groups, matched_weights_g)
            if pantry_item_matches(it, [group])
        )
        rescued_requirements[key] = {"name": name, "required_g": round(required_g, 1)}
    rescued_items = [str(item["name"]) for item in rescued_requirements.values()]
    is_zero_waste_hero = len(rescued_items) > 0

    return {
        "id": r_id,
        "name": full_rec["name"],
        "score": float(score),
        "rank_score": float(score),
        "cooking_time_min": int(float(full_rec.get("estimated_cooking_minutes") or 30)),
        "cooking_method": full_rec.get("cooking_method", "Khác"),
        "dish_type": full_rec.get("dish_type", "Món chính"),
        "source_url": full_rec.get("source_url") or "",
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
        "rescued_requirements": list(rescued_requirements.values()),
        "status_text": status_text,
        "status_badge": status_badge,
        "matched_ingredients": matched_ings,
        "pantry_used_count": pantry_used,
        "staple_ingredients": staple_ings,
        "missing_ingredients": missing_ings,
        "optional_ingredients": optional_ings,
        "ranking_features": feats,
    }
