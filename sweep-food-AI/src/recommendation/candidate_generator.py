"""High-Performance Inverted Index Candidate Generator for Recipe Retrieval.

Retrieves a high-quality subset of 25 to 35 candidate recipes for any given
pantry state in sub-millisecond time by indexing non-staple core ingredients.
"""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

from src.recommendation.pantry_resolver import get_effective_codes


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

    # 3. Common Vietnamese culinary synonyms & staple seasoning variants
    synonym_groups = [
        {"thịt ba chỉ", "thịt ba rọi", "ba rọi", "ba chỉ", "thịt lợn ba chỉ", "thịt heo ba chỉ"},
        {"thịt heo", "thịt lợn", "thịt thăn", "thịt nạc", "thịt heo nạc", "thịt lợn nạc", "thịt băm", "thịt xay", "thịt bầm"},
        {"thịt bò", "thịt bò thăn", "bò phi lê", "thăn bò", "ba chỉ bò", "ba rọi bò", "bắp bò", "bò tơ", "bò"},
        {"thịt gà", "thịt gà ta", "ức gà", "đùi gà", "cánh gà", "gà", "gà ta", "gà phi lê", "gà ác"},
        {"tôm", "tôm sú", "tôm thẻ", "tôm càng", "tôm đồng", "tép", "tôm tươi", "tôm bạc"},
        {"mực", "mực ống", "mực lá", "bạch tuộc", "bạch tuột"},
        {"cá", "cá lóc", "cá basa", "cá chép", "cá nục", "cá thu", "cá rô", "cá trắm"},
        {"coca", "coca cola", "cô ca", "cocacola"},
        {"giá", "giá đỗ", "giá đậu xanh"},
        {"hoa chuối", "bắp chuối"},
        {"dứa", "thơm", "khóm"},
        {"đậu phụ", "đậu hũ", "tàu hũ"},
        {"bắp", "ngô", "bắp non"},
        {"chả lụa", "giò lụa", "giò"},
        {"mộc nhĩ", "nấm mèo"},
        # Staple seasonings & aromatics
        {"đường", "đường cát", "đường trắng", "đường nâu", "đường vàng", "đường kính", "đường phèn", "đg"},
        {"tiêu", "tiêu hạt", "tiêu xay", "tiêu sọ", "tiêu đen", "tiêu trắng", "hạt tiêu", "tiêu bắc"},
        {"ớt", "trái ớt", "quả ớt", "ớt tươi", "ớt sừng", "ớt hiểm", "ớt hiểm xanh", "ớt chỉ thiên", "ớt đỏ", "ớt băm"},
        {"dầu ăn", "dầu thực vật", "dầu đậu nành", "dầu mè", "mỡ heo", "mỡ nước"},
        {"nước mắm", "nước mắm ngon", "nước mắm truyền thống", "nước mắm cốt", "nước mắm cá", "nc mắm"},
        {"muối", "muối ăn", "muối hạt", "muối hột", "muối tinh", "muối bọt", "muối i-ốt", "muối iot", "muối trắng"},
        {"hạt nêm", "bột nêm", "hạt nêm heo", "hạt nêm gà", "hạt nêm knorr", "bột canh", "mì chính", "bột ngọt"},
        {"hành tím", "hành khô", "hành củ khô", "hành củ", "hành tím nhỏ"},
        {"tỏi", "tỏi củ", "tỏi tép", "tép tỏi", "tỏi băm", "tỏi cô đơn"},
        {"hành lá", "hành hoa", "hành tươi", "đầu hành lá", "đầu hành"},
        {"nước tương", "xì dầu", "nước tương phú sĩ", "nước tương maggi"},
    ]
    found_synonyms = set()
    for a in list(aliases):
        for group in synonym_groups:
            if a in group:
                found_synonyms.update(group)

    aliases.update(found_synonyms)
    return aliases


def is_pantry_match(ing_code: str, ing_name: str, pantry_codes: set[str], pantry_names: set[str]) -> tuple[bool, str]:
    """Three-tier / dictionary-first matching:
    1. Exact dictionary code match.
    2. Surface text alias match.
    """
    c = str(ing_code or "").strip().replace(".0", "")
    n = (ing_name or "").strip().lower()

    # 1. Exact dictionary code match (highest confidence)
    if c and c in pantry_codes:
        return True, "exact_code"

    # 2. Surface text alias match
    if n:
        name_aliases = extract_pantry_name_aliases(n) | {n}
        if name_aliases & pantry_names:
            return True, "text_alias"

    return False, "missing"


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
                role = (ing.get("ingredient_role") or "core").strip().lower()

                # Non-staples are ingredients where role not in ("seasoning", "garnish", "accompaniment")
                if role not in ("seasoning", "garnish", "accompaniment"):
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
    ) -> list[dict[str, Any]]:
        """Fast inverted index retrieval using substantive ingredient matching and top_n bounds."""
        pantry_codes = set()
        pantry_names = set()
        expiring_codes = set()
        expiring_names = set()

        non_staple_items = [it for it in pantry_items if not it.get("is_staple", False)]
        if not non_staple_items:
            # Fallback if pantry only has staples (e.g. eggs/staples only)
            non_staple_items = pantry_items[:3]

        for item in non_staple_items:
            item_codes = get_effective_codes(item)
            raw_name = (item.get("name") or "").strip().lower()
            hours = item.get("hours_to_expire", 999.0)

            item_aliases = extract_pantry_name_aliases(raw_name)

            if item_codes:
                pantry_codes.update(item_codes)
                if hours <= 48.0:
                    expiring_codes.update(item_codes)

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

        # Fast rough score with substantive ingredient matching
        scored = []
        score_map: dict[str, float] = {}
        for r_id in candidate_ids:
            r = self.recipes.get(r_id)
            if not r:
                continue

            ings = self.recipe_ingredients.get(r_id, [])
            total_req = self.recipe_non_staples_count.get(r_id, 1)

            overlap = 0
            core_overlap = 0
            rescues = False
            for ing in ings:
                c = str(ing.get("master_ingredient_code") or "").strip().replace(".0", "")
                n = (ing.get("cleaned_name") or "").strip().lower()
                role = (ing.get("ingredient_role") or "core").strip().lower()
                if role in ("seasoning", "garnish", "accompaniment"):
                    continue

                ing_aliases = extract_pantry_name_aliases(n)
                matched = (c and c in pantry_codes) or bool(ing_aliases & pantry_names)
                if matched:
                    overlap += 1
                    if role == "core":
                        core_overlap += 1
                if (c and c in expiring_codes) or bool(ing_aliases & expiring_names):
                    rescues = True

            # Must match at least one substantive ingredient (core, secondary, liquid_base)
            if overlap < 1:
                continue

            rough_score = (overlap / total_req) + 0.25 * min(core_overlap, 1) + (0.5 if rescues else 0.0)
            scored.append((rough_score, r_id))
            score_map[r_id] = rough_score

        # Deterministic sort: higher rough first, then recipe_id asc
        scored.sort(key=lambda x: (-x[0], x[1]))

        selected_ids = set()
        # Guarantee quota for EACH non-staple pantry item to avoid single-ingredient starvation
        for item in non_staple_items:
            item_codes = get_effective_codes(item)
            n = (item.get("name") or "").strip().lower()
            item_cands = set()
            for c in item_codes:
                item_cands.update(self.code_to_recipes.get(c, set()))
            for alias in extract_pantry_name_aliases(n):
                item_cands.update(self.name_to_recipes.get(alias, set()))
            scored_item = [
                (sc, rid) for sc, rid in scored if rid in item_cands
            ]
            scored_item.sort(key=lambda x: (-x[0], x[1]))
            for _, rid in scored_item[:12]:
                selected_ids.add(rid)

        # Merge with overall top scored
        for _, r_id in scored[:top_n]:
            selected_ids.add(r_id)

        # Iterate urgent_candidate_ids in sorted order (by rough score desc then id,
        # falling back to id for urgent ids that were not scored)
        sorted_urgent_ids = sorted(
            urgent_candidate_ids,
            key=lambda rid: (0, -score_map[rid], rid) if rid in score_map else (1, 0.0, rid)
        )
        for r_id in sorted_urgent_ids:
            if len(selected_ids) >= top_n + 25:
                break
            if r_id in self.recipes:
                selected_ids.add(r_id)

        final_ids = sorted(
            [r_id for r_id in selected_ids if r_id in self.recipes],
            key=lambda rid: (0, -score_map[rid], rid) if rid in score_map else (1, 0.0, rid)
        )
        return [self.recipes[r_id] for r_id in final_ids]
