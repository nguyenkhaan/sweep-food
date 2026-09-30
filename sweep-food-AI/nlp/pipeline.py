"""Unified SweepFood Ingredient Processing Pipeline.

Combines Rule-based Grammar Parsing with Vietnamese BERT Semantic Entity Resolution
to transform raw recipe ingredient lines into database-ready records with
exact nutritional estimates.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

from nlp.nutrition import scale_nutrition
from nlp.entity_matcher import VietnameseIngredientMatcher
from nlp.ingredient_parser import VietnameseIngredientParser

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("ingredient_pipeline")


class IngredientProcessingPipeline:
    """Unified parser and matcher pipeline."""

    def __init__(
        self,
        catalog_csv_path: str | Path | None = None,
        model_name: str | None = None,
        device: str | None = None,
    ) -> None:
        self.parser = VietnameseIngredientParser()
        self.matcher = VietnameseIngredientMatcher(
            catalog_csv_path=catalog_csv_path,
            model_name=model_name,
            device=device,
        )

    def process(self, raw_text: str) -> dict[str, Any]:
        """Process a single ingredient string end-to-end."""
        # 1. Parse grammar (Quantity, Unit, Cleaned Name, Notes)
        parsed = self.parser.parse(raw_text)

        # 2. Semantic Entity Resolution (BERT on RTX 4060)
        # raw_text travels alongside parsed.name as evidence: the parser strips
        # ripeness words the matcher's guards need ("Xoài keo 160g" -> "Xoài keo").
        match_result = self.matcher.match(parsed.name, top_k=3, raw_context=raw_text)
        matched_item = match_result["matched_item"]
        confidence = match_result["confidence"]

        # 3. Calculate recipe portion nutrition if quantity is in GRAM / ML
        calories_est = None
        protein_est = None
        fat_est = None
        carbs_est = None

        qty = parsed.quantity
        c_unit = parsed.canonical_unit

        # Convert to gram baseline for nutrition calculation if mass/volume
        factor = None
        if c_unit == "KG" and qty is not None:
            factor = (qty * 1000.0) / 100.0
        elif c_unit in ("GRAM", "ML") and qty is not None:
            factor = qty / 100.0
        elif c_unit == "LB" and qty is not None:
            factor = (qty * 453.6) / 100.0
        elif c_unit == "LITER" and qty is not None:
            factor = (qty * 1000.0) / 100.0

        if factor is not None:
            try:
                calories_est = scale_nutrition(matched_item.get("energy_kcal"), factor)
                protein_est = scale_nutrition(matched_item.get("protein_g"), factor)
                fat_est = scale_nutrition(matched_item.get("fat_g"), factor)
                carbs_est = scale_nutrition(matched_item.get("carbs_g"), factor)
            except (ValueError, TypeError):
                pass

        return {
            "input_text": raw_text,
            "parsed": parsed.to_dict(),
            "matched_master_ingredient": {
                "code": matched_item.get("code"),
                "name_vi": matched_item.get("name_vi"),
                "name_en": matched_item.get("name_en"),
                "category_vi": matched_item.get("category_vi"),
                "canonical_energy_100g": matched_item.get("energy_kcal"),
                "canonical_protein_100g": matched_item.get("protein_g"),
                "canonical_fat_100g": matched_item.get("fat_g"),
                "canonical_carbs_100g": matched_item.get("carbs_g"),
                "match_confidence": confidence,
                "match_method": match_result["method"],
            },
            "estimated_portion_nutrition": {
                "calories_kcal": calories_est,
                "protein_g": protein_est,
                "fat_g": fat_est,
                "carbs_g": carbs_est,
            },
            "top_candidates": match_result["top_candidates"],
        }

    def process_batch(
        self,
        raw_texts: list[str],
        batch_size: int = 128,
        top_k: int = 3,
        max_workers: int | None = None,
    ) -> list[dict[str, Any]]:
        """Process a large batch of raw ingredient strings end-to-end with GPU acceleration."""
        if not raw_texts:
            return []

        # 1. Parallel / Vectorized grammar parsing
        parsed_items = self.parser.parse_batch(raw_texts, max_workers=max_workers)
        extracted_names = [p.name for p in parsed_items]

        # 2. Batched semantic entity matching on RTX 4060 GPU
        match_results = self.matcher.match_batch(
            extracted_names,
            batch_size=batch_size,
            top_k=top_k,
            raw_contexts=raw_texts,
        )

        # 3. Vectorized portion nutrition calculations
        output_records = []
        for raw_text, parsed, match_res in zip(raw_texts, parsed_items, match_results):
            matched_item = match_res["matched_item"]
            confidence = match_res["confidence"]

            calories_est = None
            protein_est = None
            fat_est = None
            carbs_est = None

            qty = parsed.quantity
            c_unit = parsed.canonical_unit

            factor = None
            if c_unit == "KG" and qty is not None:
                factor = (qty * 1000.0) / 100.0
            elif c_unit in ("GRAM", "ML") and qty is not None:
                factor = qty / 100.0
            elif c_unit == "LB" and qty is not None:
                factor = (qty * 453.6) / 100.0
            elif c_unit == "LITER" and qty is not None:
                factor = (qty * 1000.0) / 100.0

            if factor is not None:
                try:
                    calories_est = scale_nutrition(matched_item.get("energy_kcal"), factor)
                    protein_est = scale_nutrition(matched_item.get("protein_g"), factor)
                    fat_est = scale_nutrition(matched_item.get("fat_g"), factor)
                    carbs_est = scale_nutrition(matched_item.get("carbs_g"), factor)
                except (ValueError, TypeError):
                    pass

            output_records.append({
                "input_text": raw_text,
                "parsed": parsed.to_dict(),
                "matched_master_ingredient": {
                    "code": matched_item.get("code"),
                    "name_vi": matched_item.get("name_vi"),
                    "name_en": matched_item.get("name_en"),
                    "category_vi": matched_item.get("category_vi"),
                    "canonical_energy_100g": matched_item.get("energy_kcal"),
                    "canonical_protein_100g": matched_item.get("protein_g"),
                    "canonical_fat_100g": matched_item.get("fat_g"),
                    "canonical_carbs_100g": matched_item.get("carbs_g"),
                    "match_confidence": confidence,
                    "match_method": match_res["method"],
                },
                "estimated_portion_nutrition": {
                    "calories_kcal": calories_est,
                    "protein_g": protein_est,
                    "fat_g": fat_est,
                    "carbs_g": carbs_est,
                },
                "top_candidates": match_res["top_candidates"],
            })

        return output_records
