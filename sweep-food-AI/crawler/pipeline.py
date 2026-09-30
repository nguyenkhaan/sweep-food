"""SweepFood Recipe Crawling & Real-time Sanitization Pipeline.

Giai đoạn 1 (Scale-out): Thu thập công thức quy mô lớn từ các website ẩm thực
(Cookpad, Món Ngon Mỗi Ngày, Điện Máy Xanh) với khoảng 2.000 món mỗi trang.
Tự động làm sạch và chuẩn hóa danh mục nguyên liệu theo thời gian thực,
tự động lưu checkpoint định kỳ và đồng bộ trực tiếp ra data/processed/recipes/
(bỏ qua bước so sánh với Master Ingredients / BERT theo yêu cầu).
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
import threading
import uuid
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from tqdm import tqdm

# Ensure UTF-8 output across Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from crawler.spiders import CookpadSpider, DienMayXanhSpider, MonNgonMoiNgaySpider, RawRecipe
from nlp.llm_cleaner import VietnameseLLMIngredientCleaner

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("crawler_pipeline")


class RecipeCrawlerPipeline:
    """High-throughput concurrent recipe crawler with streaming checkpoints and direct processed export."""

    def __init__(
        self,
        output_dir: str | Path = "data/interim",
        processed_dir: str | Path = "data/processed/recipes",
        raw_dir: str | Path = "data/raw",
        model_name: str | None = None,
        device: str | None = None,
        max_workers: int = 16,
        checkpoint_interval: int = 50,
    ) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir = Path(processed_dir)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir = Path(raw_dir)
        self.raw_dir.mkdir(parents=True, exist_ok=True)

        self.max_workers = max_workers
        self.checkpoint_interval = checkpoint_interval
        self._save_lock = threading.Lock()

        logger.info(f"Initializing Crawler Pipeline (Workers: {max_workers}, Checkpoint: {checkpoint_interval})")
        self.cleaner = VietnameseLLMIngredientCleaner(
            model_name=model_name,
            device=device,
            lazy_load=True,
        )

        self.spiders = {
            "cookpad": CookpadSpider(request_delay=0.15),
            "monngonmoingay": MonNgonMoiNgaySpider(request_delay=0.15),
            "dienmayxanh": DienMayXanhSpider(request_delay=0.15),
        }

    def _clean_and_structure_recipe(self, raw: RawRecipe) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        """Convert RawRecipe into structured recipe record and ingredient records."""
        recipe_id = str(uuid.uuid4())
        cleaned_ings = self.cleaner.clean_recipe_ingredients(raw.raw_ingredients)

        recipe_ing_records = []
        for item in cleaned_ings:
            ing_record = {
                "id": str(uuid.uuid4()),
                "recipe_id": recipe_id,
                "recipe_name": raw.title,
                "name": item.get("name"),
                "quantity": item.get("quantity"),
                "unit": item.get("unit") or "OTHER",
                "unit_vi": item.get("unit_vi") or "phần ăn",
                "preparation_note": item.get("preparation_note"),
                "raw_text": item.get("raw_text"),
            }
            recipe_ing_records.append(ing_record)

        recipe_record = {
            "id": recipe_id,
            "name": raw.title,
            "source_platform": raw.source_platform,
            "source_url": raw.source_url,
            "description": raw.description,
            "instructions": raw.instructions,
            "media_url": raw.media_url,
            "default_servings": raw.default_servings,
            "estimated_cooking_minutes": raw.estimated_cooking_minutes,
            "tags": raw.tags,
            "raw_ingredients_count": len(raw.raw_ingredients),
            "cleaned_ingredients_count": len(recipe_ing_records),
            "ingredients": recipe_ing_records,
        }
        return recipe_record, recipe_ing_records

    def save_checkpoints(self, all_recipes: list[dict[str, Any]]) -> None:
        """Persist all cumulative recipes to data/interim and data/processed/recipes."""
        with self._save_lock:
            # 1. Gather all ingredients
            all_ingredients = []
            for r in all_recipes:
                for ing in r.get("ingredients", []):
                    all_ingredients.append(ing)

            # 2. Interim storage
            interim_json = self.output_dir / "recipes_crawled_cleaned.json"
            interim_csv = self.output_dir / "recipes_crawled_cleaned.csv"
            interim_ing_csv = self.output_dir / "ingredients_crawled_cleaned.csv"

            with open(interim_json, "w", encoding="utf-8") as f:
                json.dump(all_recipes, f, ensure_ascii=False, indent=2)

            recipe_keys = [
                "id", "name", "source_platform", "source_url", "default_servings",
                "estimated_cooking_minutes", "cleaned_ingredients_count"
            ]
            with open(interim_csv, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=recipe_keys, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(all_recipes)

            if all_ingredients:
                ing_keys = ["id", "recipe_id", "recipe_name", "name", "quantity", "unit_vi", "unit", "preparation_note", "raw_text"]
                with open(interim_ing_csv, "w", encoding="utf-8-sig", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=ing_keys, extrasaction="ignore")
                    writer.writeheader()
                    writer.writerows(all_ingredients)

            # 3. Direct Processed Database Seed Exports (Skipping Master Ingredients)
            proc_recipes_json = self.processed_dir / "recipes.json"
            proc_recipes_csv = self.processed_dir / "recipes.csv"
            proc_ings_json = self.processed_dir / "recipe_ingredients.json"
            proc_ings_csv = self.processed_dir / "recipe_ingredients.csv"

            processed_recipe_rows = []
            processed_ing_rows = []

            for r in all_recipes:
                proc_r = {
                    "id": r["id"],
                    "name": r["name"],
                    "source_platform": r["source_platform"],
                    "source_url": r["source_url"],
                    "description": r.get("description") or "",
                    "instructions": r.get("instructions") or [],
                    "media_url": r.get("media_url"),
                    "default_servings": r.get("default_servings") or 2.0,
                    "estimated_cooking_minutes": r.get("estimated_cooking_minutes") or 30,
                    "total_calories": r.get("total_calories"),
                    "total_protein_g": r.get("total_protein_g"),
                    "total_fat_g": r.get("total_fat_g"),
                    "total_carbs_g": r.get("total_carbs_g"),
                    "tags": r.get("tags") or [],
                    "ingredients_count": len(r.get("ingredients", [])),
                }
                processed_recipe_rows.append(proc_r)

                for ing in r.get("ingredients", []):
                    proc_ing = {
                        "id": ing["id"],
                        "recipe_id": r["id"],
                        "master_ingredient_code": ing.get("master_ingredient_code"),
                        "master_ingredient_name": ing.get("master_ingredient_name"),
                        "raw_text": ing.get("raw_text") or "",
                        "cleaned_name": ing.get("name") or "",
                        "required_quantity": ing.get("quantity"),
                        "unit_vi": ing.get("unit_vi") or "khác",
                        "unit": ing.get("unit") or "OTHER",
                        "preparation_note": ing.get("preparation_note"),
                        "match_confidence": ing.get("match_confidence"),
                        "match_method": ing.get("match_method") or "SKIPPED_PER_USER_REQUEST",
                        "portion_nutrition": ing.get("portion_nutrition"),
                    }
                    processed_ing_rows.append(proc_ing)

            with open(proc_recipes_json, "w", encoding="utf-8") as f:
                json.dump(processed_recipe_rows, f, ensure_ascii=False, indent=2)

            with open(proc_recipes_csv, "w", encoding="utf-8-sig", newline="") as f:
                p_keys = [
                    "id", "name", "source_platform", "source_url", "default_servings",
                    "estimated_cooking_minutes", "ingredients_count"
                ]
                writer = csv.DictWriter(f, fieldnames=p_keys, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(processed_recipe_rows)

            with open(proc_ings_json, "w", encoding="utf-8") as f:
                json.dump(processed_ing_rows, f, ensure_ascii=False, indent=2)

            if processed_ing_rows:
                with open(proc_ings_csv, "w", encoding="utf-8-sig", newline="") as f:
                    pi_keys = [
                        "id", "recipe_id", "master_ingredient_code", "master_ingredient_name",
                        "raw_text", "cleaned_name", "required_quantity", "unit_vi", "unit",
                        "preparation_note", "match_confidence", "match_method"
                    ]
                    writer = csv.DictWriter(f, fieldnames=pi_keys, extrasaction="ignore")
                    writer.writeheader()
                    writer.writerows(processed_ing_rows)

            logger.info(
                f"[CHECKPOINT] Saved {len(all_recipes)} recipes & {len(all_ingredients)} ingredients to interim and processed dirs."
            )

    def run(
        self,
        platforms: list[str] | None = None,
        limit_per_platform: int = 2000,
    ) -> dict[str, Any]:
        """Harvest recipes up to limit_per_platform per source, skipping master ingredients matching."""
        if not platforms or "all" in platforms:
            target_platforms = list(self.spiders.keys())
        else:
            target_platforms = [p for p in platforms if p in self.spiders]

        # 0. Load Existing Recipes for Deduplication & Incremental Growth
        interim_recipes_json = self.output_dir / "recipes_crawled_cleaned.json"
        all_recipes: list[dict[str, Any]] = []
        existing_urls = set()

        if interim_recipes_json.exists():
            try:
                with open(interim_recipes_json, "r", encoding="utf-8") as f:
                    all_recipes = json.load(f)
                    existing_urls = {r.get("source_url") for r in all_recipes if r.get("source_url")}
                logger.info(f"Loaded {len(all_recipes)} existing recipes for deduplication.")
            except Exception as e:
                logger.warning(f"Could not load existing recipes: {e}")

        counts_by_platform = Counter(r.get("source_platform") for r in all_recipes)
        logger.info(f"Current platform distribution: {dict(counts_by_platform)}")

        # 1. URL Discovery for Platforms that need more recipes
        platform_urls: dict[str, list[str]] = {}
        platforms_to_crawl = []
        for p in target_platforms:
            current_count = counts_by_platform.get(p, 0)
            needed = limit_per_platform - current_count
            if needed <= 0:
                logger.info(f"[{p}] already has {current_count} recipes >= target {limit_per_platform}. Skipping discovery.")
            else:
                platforms_to_crawl.append(p)
                logger.info(f"[{p}] currently has {current_count} recipes. Target: {limit_per_platform} (Needs +{needed})")

        if platforms_to_crawl:
            logger.info(f"Starting parallel URL discovery for: {platforms_to_crawl}...")
            with ThreadPoolExecutor(max_workers=min(len(platforms_to_crawl), 3)) as executor:
                future_to_plat = {
                    executor.submit(self.spiders[p].discover_recipe_urls, limit=limit_per_platform): p
                    for p in platforms_to_crawl
                }
                for future in as_completed(future_to_plat):
                    p = future_to_plat[future]
                    try:
                        urls = future.result()
                        # Deduplicate against already crawled URLs
                        new_urls = [u for u in urls if u not in existing_urls]
                        needed = limit_per_platform - counts_by_platform.get(p, 0)
                        platform_urls[p] = new_urls[:needed]
                        logger.info(f"Discovered {len(urls)} URLs for [{p}] ({len(new_urls)} new, selected {len(platform_urls[p])})")
                    except Exception as e:
                        logger.error(f"Error discovering URLs for {p}: {e}")
                        platform_urls[p] = []

        total_new_urls = sum(len(u) for u in platform_urls.values())
        logger.info(f"Total new URLs queued across all platforms: {total_new_urls}")

        # 2. Parallel Crawling with Streaming Sanitization & Checkpoints
        new_recipes_scraped = 0
        raw_recipes_backup: list[dict[str, Any]] = []

        for platform_name in platforms_to_crawl:
            urls = platform_urls.get(platform_name, [])
            if not urls:
                continue

            spider = self.spiders[platform_name]
            crawl_pbar = tqdm(
                total=len(urls),
                desc=f"[{platform_name}] Crawling ({self.max_workers} threads)",
                unit="recipe",
                dynamic_ncols=True,
            )

            def _crawl_and_clean_worker(url: str) -> tuple[RawRecipe | None, dict[str, Any] | None]:
                try:
                    raw = spider.crawl_recipe(url)
                    if not raw:
                        return None, None
                    rec_dict, _ = self._clean_and_structure_recipe(raw)
                    return raw, rec_dict
                except Exception as ex:
                    logger.debug(f"Worker error on {url}: {ex}")
                    return None, None

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_url = {executor.submit(_crawl_and_clean_worker, u): u for u in urls}
                for future in as_completed(future_to_url):
                    try:
                        raw, rec_dict = future.result()
                        if raw and rec_dict:
                            all_recipes.append(rec_dict)
                            raw_recipes_backup.append(raw.to_dict())
                            existing_urls.add(raw.source_url)
                            new_recipes_scraped += 1

                            crawl_pbar.set_postfix({
                                "total_platform": counts_by_platform[platform_name] + new_recipes_scraped,
                                "last": rec_dict["name"][:18]
                            })

                            # Checkpoint auto-save
                            if new_recipes_scraped % self.checkpoint_interval == 0:
                                self.save_checkpoints(all_recipes)
                    except Exception as err:
                        logger.warning(f"Error in future processing: {err}")
                    crawl_pbar.update(1)

            crawl_pbar.close()

        # 3. Final Persistence
        logger.info(f"Crawling complete! Persisting final datasets...")
        self.save_checkpoints(all_recipes)

        # Save raw backup
        if raw_recipes_backup:
            raw_backup_path = self.raw_dir / "recipes_raw_scraped.json"
            try:
                existing_raw = []
                if raw_backup_path.exists():
                    with open(raw_backup_path, "r", encoding="utf-8") as f:
                        existing_raw = json.load(f)
                combined_raw = existing_raw + raw_recipes_backup
                with open(raw_backup_path, "w", encoding="utf-8") as f:
                    json.dump(combined_raw, f, ensure_ascii=False, indent=2)
            except Exception as e:
                logger.warning(f"Could not update raw backup: {e}")

        final_counts = Counter(r.get("source_platform") for r in all_recipes)
        total_ingredients = sum(len(r.get("ingredients", [])) for r in all_recipes)

        return {
            "new_recipes_count": new_recipes_scraped,
            "total_recipes_count": len(all_recipes),
            "total_ingredients_count": total_ingredients,
            "platform_distribution": dict(final_counts),
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="SweepFood High-Scale Recipe Crawler (Skip Master Ingredients)")
    parser.add_argument("--platform", nargs="+", default=["all"], help="Target platforms: cookpad, monngonmoingay, dienmayxanh, or all")
    parser.add_argument("--limit", type=int, default=2000, help="Target number of recipes per platform")
    parser.add_argument("--workers", type=int, default=16, help="Number of concurrent worker threads")
    parser.add_argument("--checkpoint", type=int, default=50, help="Checkpoint auto-save interval")
    parser.add_argument("--output", type=str, default="data/interim", help="Output directory for interim data")
    parser.add_argument("--processed", type=str, default="data/processed/recipes", help="Output directory for processed recipes")
    args = parser.parse_args()

    pipeline = RecipeCrawlerPipeline(
        output_dir=args.output,
        processed_dir=args.processed,
        max_workers=args.workers,
        checkpoint_interval=args.checkpoint,
    )
    result = pipeline.run(platforms=args.platform, limit_per_platform=args.limit)

    print("\n" + "=" * 80)
    print("SWEEPFOOD RECIPE HARVEST COMPLETE (MASTER INGREDIENTS MATCHING SKIPPED)")
    print("=" * 80)
    print(f"New Recipes Scraped This Run: {result['new_recipes_count']}")
    print(f"Total Cumulative Recipes:     {result['total_recipes_count']}")
    print(f"Total Cumulative Ingredients: {result['total_ingredients_count']}")
    print(f"Platform Breakdown:           {result['platform_distribution']}")


if __name__ == "__main__":
    main()
