"""High-Performance Inverted Index Candidate Generator for Recipe Retrieval.

Retrieves a high-quality subset of 25 to 35 candidate recipes for any given
pantry state in sub-millisecond time by indexing non-staple core ingredients.
"""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any
from src.recommendation.ingredient_roles import IngredientRole, classify_ingredient_role


def extract_pantry_name_aliases(raw_name: str) -> set[str]:
    """Expands ingredient name by extracting parentheses sub-phrases and common Vietnamese aliases."""
    aliases = set()
    name = (raw_name or "").strip().lower()
    if not name:
        return aliases

    aliases.add(name)

    # 1. Extract content inside parentheses: e.g. "thịt ba chỉ (ba rọi) heo" -> "ba rọi"
    paren_contents = re.findall(r"\((.*?)\)", name)
    for p in paren_contents:
        clean_p = p.strip().lower()
        if clean_p:
            aliases.add(clean_p)

    # 2. Name without parentheses: e.g. "thịt ba chỉ heo"
    without_parens = re.sub(r"\(.*?\)", "", name).strip()
    if without_parens:
        aliases.add(re.sub(r"\s+", " ", without_parens))

    # 3. Common Vietnamese culinary synonyms
    synonym_groups = [
        {"thịt ba chỉ", "thịt ba rọi", "ba rọi", "ba chỉ", "thịt lợn ba chỉ", "thịt heo ba chỉ"},
        {"coca", "coca cola", "cô ca", "cocacola"},
        {"giá", "giá đỗ", "giá đậu xanh"},
        {"hoa chuối", "bắp chuối"},
        {"dứa", "thơm", "khóm"},
        {"đậu phụ", "đậu hũ", "tàu hũ"},
        {"bắp", "ngô"},
        {"hành lá", "hành hoa"},
        {"chả lụa", "giò lụa"},
        {"mộc nhĩ", "nấm mèo"},
    ]

    found_synonyms = set()
    for a in list(aliases):
        for group in synonym_groups:
            if a in group or any(g in a for g in group):
                found_synonyms.update(group)

    aliases.update(found_synonyms)
    return aliases


class CandidateGenerator:
    def __init__(self, recipes: list[dict[str, Any]], ingredients: list[dict[str, Any]]):
        self.recipes = {r["id"]: r for r in recipes}
        self.recipe_ingredients: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for ing in ingredients:
            self.recipe_ingredients[ing["recipe_id"]].append(ing)

        # Pre-indexed mappings for speed
        self.code_to_recipes: dict[str, set[str]] = defaultdict(set)
        self.name_to_recipes: dict[str, set[str]] = defaultdict(set)
        self.recipe_non_staples_count: dict[str, int] = defaultdict(int)

        self._build_index()

    def _build_index(self):
        for r_id, ing_list in self.recipe_ingredients.items():
            non_staple_count = 0
            for ing in ing_list:
                code = str(ing.get("master_ingredient_code") or "").strip().replace(".0", "")
                name = (ing.get("cleaned_name") or "").strip().lower()
                role = (ing.get("ingredient_role") or "").strip().lower()
                if not role:
                    role = classify_ingredient_role(name, code).lower()

                # Core and secondary are non-staple substantive ingredients
                if role not in ("seasoning", "garnish", "staple_spice", "optional_garnish"):
                    non_staple_count += 1
                    if code:
                        self.code_to_recipes[code].add(r_id)
                    if name:
                        self.name_to_recipes[name].add(r_id)

            self.recipe_non_staples_count[r_id] = max(1, non_staple_count)

    def retrieve_candidates(
        self,
        pantry_items: list[dict[str, Any]],
        top_n: int = 35,
        min_threshold: float = 0.15
    ) -> list[dict[str, Any]]:
        """Fast inverted index retrieval using dynamic threshold filtering and top_n bounds."""
        pantry_codes = set()
        pantry_names = set()
        expiring_codes = set()
        expiring_names = set()

        non_staple_items = [it for it in pantry_items if not it.get("is_staple", False)]
        if not non_staple_items:
            # Fallback if pantry only has staples (e.g. eggs/staples only)
            non_staple_items = pantry_items[:3]

        for item in non_staple_items:
            code = item.get("code")
            raw_name = (item.get("name") or "").strip().lower()
            hours = item.get("hours_to_expire", 999.0)

            item_aliases = extract_pantry_name_aliases(raw_name)

            if code:
                pantry_codes.add(code)
                if hours <= 48.0:
                    expiring_codes.add(code)

            pantry_names.update(item_aliases)
            if hours <= 48.0:
                expiring_names.update(item_aliases)

        candidate_ids = set()
        urgent_candidate_ids = set()

        for c in pantry_codes:
            matched = self.code_to_recipes.get(c, set())
            candidate_ids.update(matched)
            if c in expiring_codes:
                urgent_candidate_ids.update(matched)

        for n in pantry_names:
            matched = self.name_to_recipes.get(n, set())
            candidate_ids.update(matched)
            if n in expiring_names:
                urgent_candidate_ids.update(matched)

        if not candidate_ids:
            return []

        # Fast rough score with threshold-based filtering
        scored = []
        for r_id in candidate_ids:
            r = self.recipes.get(r_id)
            if not r:
                continue

            ings = self.recipe_ingredients.get(r_id, [])
            total_req = self.recipe_non_staples_count.get(r_id, 1)

            overlap = 0
            core_overlap = 0
            total_core = 0
            rescues = False
            for ing in ings:
                c = str(ing.get("master_ingredient_code") or "").strip().replace(".0", "")
                n = (ing.get("cleaned_name") or "").strip().lower()
                role = (ing.get("ingredient_role") or "").strip().lower()
                is_core = role == "core" or classify_ingredient_role(n, c) == IngredientRole.CORE_PROTEIN
                if is_core:
                    total_core += 1

                ing_aliases = extract_pantry_name_aliases(n)
                matched = (c and c in pantry_codes) or (n and n in pantry_names) or bool(ing_aliases & pantry_names)
                if matched:
                    overlap += 1
                    if is_core:
                        core_overlap += 1
                if (c and c in expiring_codes) or (n and n in expiring_names) or bool(ing_aliases & expiring_names):
                    rescues = True

            # Hard filter against seasoning inflation:
            # If recipe has core ingredients and user pantry has non-staples,
            # must match >= 1 core ingredient or >= 50% of core ingredients (unless rescuing urgent food).
            if total_core > 0 and len(non_staple_items) > 0:
                if core_overlap < 1 and (core_overlap / total_core) < 0.5 and not rescues:
                    continue

            rough_score = (overlap / total_req) + (0.5 if rescues else 0.0)
            if rough_score >= min_threshold or rescues:
                scored.append((rough_score, r_id))

        scored.sort(key=lambda x: x[0], reverse=True)

        selected_ids = set(r_id for _, r_id in scored[:top_n])
        for r_id in urgent_candidate_ids:
            if len(selected_ids) >= top_n + 10:
                break
            selected_ids.add(r_id)

        return [self.recipes[r_id] for r_id in selected_ids if r_id in self.recipes]
