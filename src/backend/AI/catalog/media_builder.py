"""Recipe media and instruction step builder for the SweepFood catalog.

Constructs the recipe_media.json catalog artifact by combining structured
instructions and chef tips from detailed AI processing with scraped media URLs,
article page extraction for missing images, and rigorous HTTP image validation.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import logging
import re
import sys
from collections.abc import Sequence
from html import unescape
from pathlib import Path
from typing import cast
from urllib.parse import urljoin, urlparse, urlunparse

import httpx

logger = logging.getLogger(__name__)

DEFAULT_BUNDLE_DIR = Path(__file__).resolve().parent.parent / "data"
DEFAULT_OUTPUT_PATH = DEFAULT_BUNDLE_DIR / "catalog" / "recipe_media.json"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 "
    "(compatible; SweepFoodCatalog/1.0; +https://sweepfood.app)"
)


def clean_url(url: str | None, base_url: str) -> str | None:
    """Sanitize and resolve a candidate URL into an absolute HTTPS URL.

    Strips tracking whitespace, unescapes HTML entities, resolves relative
    paths against the base URL, and upgrades/requires HTTPS scheme.
    """
    if not url or not isinstance(url, str):
        return None
    trimmed = unescape(url).strip()
    if not trimmed:
        return None
    resolved = urljoin(base_url, trimmed)
    parsed = urlparse(resolved)
    if parsed.scheme.lower() == "http":
        resolved = urlunparse(parsed._replace(scheme="https"))
        parsed = urlparse(resolved)
    if parsed.scheme.lower() != "https" or not parsed.netloc:
        return None
    return resolved


def extract_image_from_html(html: str, page_url: str) -> str | None:
    """Extract a representative recipe image URL from HTML content.

    Extraction order:
    1. JSON-LD Recipe 'image' (string, list of strings/objects, or ImageObject)
    2. OpenGraph meta tag: og:image
    3. Twitter meta tag: twitter:image
    """
    # 1. JSON-LD Recipe image
    json_ld_blocks = re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        re.DOTALL | re.IGNORECASE,
    )
    for block in json_ld_blocks:
        try:
            data = json.loads(block.strip())
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue

        nodes: list[dict[str, object]] = []
        if isinstance(data, dict):
            graph = data.get("@graph")
            if isinstance(graph, list):
                for item in graph:
                    if isinstance(item, dict):
                        nodes.append(cast(dict[str, object], item))
            nodes.append(cast(dict[str, object], data))
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    nodes.append(cast(dict[str, object], item))

        for node in nodes:
            raw_type = node.get("@type")
            is_recipe = (
                (isinstance(raw_type, str) and "Recipe" in raw_type)
                or (
                    isinstance(raw_type, list)
                    and any(isinstance(t, str) and "Recipe" in t for t in raw_type)
                )
            )

            if not is_recipe or "image" not in node:
                continue

            img_val = node["image"]
            candidate: str | None = None
            if isinstance(img_val, str):
                candidate = img_val
            elif isinstance(img_val, list) and img_val:
                # Prefer the highest resolution or last entry in the list
                for item in reversed(img_val):
                    if isinstance(item, str) and item.strip():
                        candidate = item
                        break
                    if isinstance(item, dict) and "url" in item:
                        candidate = str(item["url"])
                        break
            elif isinstance(img_val, dict) and "url" in img_val:
                candidate = str(img_val["url"])

            cleaned = clean_url(candidate, page_url)
            if cleaned is not None:
                return cleaned

    # 2. og:image
    og_patterns = (
        r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
    )
    for pat in og_patterns:
        match = re.search(pat, html, re.IGNORECASE)
        if match:
            cleaned = clean_url(match.group(1), page_url)
            if cleaned is not None:
                return cleaned

    # 3. twitter:image
    tw_patterns = (
        r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)["\']',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']twitter:image["\']',
    )
    for pat in tw_patterns:
        match = re.search(pat, html, re.IGNORECASE)
        if match:
            cleaned = clean_url(match.group(1), page_url)
            if cleaned is not None:
                return cleaned

    return None


def normalize_step(
    step_dict: dict[str, object], fallback_number: int
) -> dict[str, object]:
    """Normalize a raw or detailed step object into the standard step contract."""
    raw_step = step_dict.get("step")
    if raw_step is None:
        raw_step = step_dict.get("step_number")

    step_number: int = fallback_number
    if isinstance(raw_step, int):
        step_number = raw_step
    elif isinstance(raw_step, str):
        try:
            step_number = int(raw_step.strip())
        except ValueError:
            step_number = fallback_number

    raw_title = step_dict.get("title")
    title = str(raw_title).strip() if raw_title is not None else ""

    raw_content = step_dict.get("content")
    content = str(raw_content).strip() if raw_content is not None else ""

    return {
        "step": step_number,
        "title": title,
        "content": content,
    }


def normalize_steps(
    detailed_steps: list[dict[str, object]] | None,
    raw_instructions: list[dict[str, object]] | None,
) -> list[dict[str, object]]:
    """Select and normalize steps, preferring detailed rephrasing over raw."""
    if detailed_steps:
        return [
            normalize_step(s, idx)
            for idx, s in enumerate(detailed_steps, start=1)
            if isinstance(s, dict)
        ]
    if raw_instructions:
        return [
            normalize_step(s, idx)
            for idx, s in enumerate(raw_instructions, start=1)
            if isinstance(s, dict)
        ]
    return []


async def validate_image_url(
    client: httpx.AsyncClient, url: str
) -> tuple[bool, str]:
    """Validate that an image URL returns status 200/206 with an image/* content type."""
    headers = {
        "Accept": "image/*",
        "Range": "bytes=0-1023",
    }
    try:
        async with client.stream("GET", url, headers=headers) as response:
            status = response.status_code
            content_type = response.headers.get("content-type", "").lower()
            if status in (403, 405, 416):
                # Fallback to GET without Range header if host rejects byte-range requests
                async with client.stream("GET", url, headers={"Accept": "image/*"}) as retry_resp:
                    retry_status = retry_resp.status_code
                    retry_ct = retry_resp.headers.get("content-type", "").lower()
                    if retry_status not in (200, 206):
                        return False, f"status_{retry_status}"
                    if not retry_ct.startswith("image/"):
                        return False, f"invalid_content_type_{retry_ct.split(';')[0]}"
                    return True, "valid"
            if status not in (200, 206):
                return False, f"status_{status}"
            if not content_type.startswith("image/"):
                return False, f"invalid_content_type_{content_type.split(';')[0]}"
            return True, "valid"
    except httpx.ConnectTimeout:
        return False, "connect_timeout"
    except httpx.ReadTimeout:
        return False, "read_timeout"
    except httpx.ConnectError:
        return False, "connect_error"
    except (httpx.HTTPError, OSError) as exc:
        return False, f"http_error_{type(exc).__name__}"

async def scrape_article_image(
    client: httpx.AsyncClient,
    source_url: str,
    semaphore: asyncio.Semaphore,
) -> str | None:
    """Fetch an article page and extract a candidate image URL."""
    async with semaphore:
        await asyncio.sleep(0.05)
        try:
            resp = await client.get(source_url)
            if resp.status_code == 200:
                return extract_image_from_html(resp.text, str(resp.url))
            logger.debug(
                "Article fetch for %s returned non-200 status %d",
                source_url,
                resp.status_code,
            )
            return None
        except (httpx.HTTPError, OSError) as exc:
            logger.debug("Article fetch for %s failed: %s", source_url, exc)
            return None


def load_json_records(path: Path) -> list[dict[str, object]]:
    """Read a JSON array of object records from a UTF-8 file."""
    if not path.is_file():
        raise FileNotFoundError(f"Input file not found: {path}")
    with path.open(mode="r", encoding="utf-8") as file_handle:
        data = json.load(file_handle)
    if not isinstance(data, list):
        raise TypeError(f"Expected JSON array in {path}")
    return [cast(dict[str, object], item) for item in data if isinstance(item, dict)]


def load_catalog_recipes(bundle_dir: Path) -> list[dict[str, str]]:
    """Load recipes.csv from the bundle directory."""
    recipes_csv = bundle_dir / "catalog" / "recipes.csv"
    if not recipes_csv.is_file():
        raise FileNotFoundError(f"Catalog recipes file not found: {recipes_csv}")
    with recipes_csv.open(mode="r", encoding="utf-8-sig") as file_handle:
        reader = csv.DictReader(file_handle)
        return list(reader)


async def run_builder(
    raw_path: Path,
    detailed_path: Path,
    bundle_dir: Path,
    output_path: Path,
    *,
    no_network: bool = False,
) -> list[dict[str, object]]:
    """Execute the full recipe media build and validation pipeline."""
    catalog_recipes = load_catalog_recipes(bundle_dir)
    raw_records = load_json_records(raw_path)
    detailed_records = load_json_records(detailed_path)

    detailed_by_id: dict[str, dict[str, object]] = {}
    for item in detailed_records:
        cid = item.get("canonical_recipe_id")
        if isinstance(cid, str) and cid.strip():
            detailed_by_id[cid.strip()] = item

    raw_by_url: dict[str, dict[str, object]] = {}
    for item in raw_records:
        surl = item.get("source_url")
        if isinstance(surl, str) and surl.strip():
            raw_by_url[surl.strip()] = item

    # Step 1: Gather steps, chef tips, and raw media URLs
    intermediate: list[dict[str, object]] = []
    recipes_needing_scrape: list[dict[str, str]] = []

    steps_detailed_count = 0
    steps_raw_count = 0

    for recipe_row in catalog_recipes:
        recipe_id = recipe_row["id"].strip()
        source_url = recipe_row["source_url"].strip()
        platform = recipe_row.get("source_platform", "unknown").strip()

        det = detailed_by_id.get(recipe_id)
        raw = raw_by_url.get(source_url)

        det_steps = cast(list[dict[str, object]] | None, det.get("steps") if det else None)
        raw_instructions = cast(
            list[dict[str, object]] | None, raw.get("instructions") if raw else None
        )

        if det_steps:
            steps_detailed_count += 1
        elif raw_instructions:
            steps_raw_count += 1

        steps = normalize_steps(det_steps, raw_instructions)

        chef_tips: str | None = None
        if det and det.get("chef_tips"):
            raw_tips = str(det["chef_tips"]).strip()
            if raw_tips:
                chef_tips = raw_tips

        raw_media = clean_url(
            cast(str | None, raw.get("media_url") if raw else None),
            source_url,
        )

        media_url: str | None = raw_media
        media_source: str | None = "scraped" if raw_media else None

        if not raw_media and not no_network:
            recipes_needing_scrape.append(recipe_row)

        intermediate.append({
            "id": recipe_id,
            "platform": platform,
            "source_url": source_url,
            "media_url": media_url,
            "media_source": media_source,
            "steps": steps,
            "chef_tips": chef_tips,
        })

    # Step 2: Article page scraping for missing images
    if recipes_needing_scrape and not no_network:
        logger.info(
            "Scraping %d recipes without raw media from article pages...",
            len(recipes_needing_scrape),
        )
        semaphore = asyncio.Semaphore(4)
        async with httpx.AsyncClient(
            headers={"User-Agent": DEFAULT_USER_AGENT},
            follow_redirects=True,
            timeout=15.0,
        ) as client:
            scrape_tasks = [
                scrape_article_image(client, r["source_url"].strip(), semaphore)
                for r in recipes_needing_scrape
            ]
            scraped_images = await asyncio.gather(*scrape_tasks)

        scraped_by_id = {
            r["id"].strip(): img
            for r, img in zip(recipes_needing_scrape, scraped_images)
            if img is not None
        }

        for item in intermediate:
            rid = str(item["id"])
            if not item["media_url"] and rid in scraped_by_id:
                item["media_url"] = scraped_by_id[rid]
                item["media_source"] = "article"

    # Step 3: Validate every candidate image URL
    validation_failures: dict[str, int] = {}
    if not no_network:
        candidates_to_validate = [
            (idx, str(item["media_url"]))
            for idx, item in enumerate(intermediate)
            if item["media_url"] is not None
        ]
        logger.info(
            "Validating %d candidate image URLs with concurrency 8...",
            len(candidates_to_validate),
        )
        val_sem = asyncio.Semaphore(8)

        async with httpx.AsyncClient(
            headers={"User-Agent": DEFAULT_USER_AGENT},
            follow_redirects=True,
            timeout=httpx.Timeout(10.0, connect=5.0),
        ) as client:
            async def validate_one(
                idx: int, url: str
            ) -> tuple[int, bool, str]:
                async with val_sem:
                    await asyncio.sleep(0.01)
                    valid, reason = await validate_image_url(client, url)
                    return idx, valid, reason

            val_tasks = [
                validate_one(idx, url) for idx, url in candidates_to_validate
            ]
            val_results = await asyncio.gather(*val_tasks)

        for idx, valid, reason in val_results:
            if not valid:
                intermediate[idx]["had_candidate"] = True
                intermediate[idx]["media_url"] = None
                intermediate[idx]["media_source"] = None
                validation_failures[reason] = validation_failures.get(reason, 0) + 1

    # Format final output ordered deterministically by recipe id
    intermediate.sort(key=lambda x: str(x["id"]))

    final_records: list[dict[str, object]] = []
    platform_stats: dict[str, dict[str, int]] = {}

    for item in intermediate:
        plat = str(item["platform"])
        if plat not in platform_stats:
            platform_stats[plat] = {
                "total": 0,
                "with_image": 0,
                "validated": 0,
                "failed": 0,
            }
        stats = platform_stats[plat]
        stats["total"] += 1

        has_img = item["media_url"] is not None
        if has_img:
            stats["with_image"] += 1
            stats["validated"] += 1
        elif item.get("had_candidate"):
            # Had candidate but validation failed
            stats["failed"] += 1

        final_records.append({
            "id": item["id"],
            "media_url": item["media_url"],
            "media_source": item["media_source"],
            "steps": item["steps"],
            "chef_tips": item["chef_tips"],
        })

    # Summary reporting
    total_recipes = len(final_records)
    with_image_count = sum(1 for r in final_records if r["media_url"] is not None)
    with_steps_count = sum(1 for r in final_records if bool(r["steps"]))
    neither_count = sum(
        1 for r in final_records if not r["media_url"] and not bool(r["steps"])
    )

    print("\n" + "=" * 60)
    print("RECIPE MEDIA BUILD SUMMARY")
    print("=" * 60)
    print(f"Total catalog recipes: {total_recipes}")
    print(
        f"Steps coverage: {with_steps_count}/{total_recipes} "
        f"(from detailed: {steps_detailed_count}, from raw: {steps_raw_count}, "
        f"missing steps: {total_recipes - with_steps_count})"
    )
    print(f"Validated media URLs: {with_image_count}/{total_recipes}")
    if validation_failures:
        print(f"Validation failure reasons: {validation_failures}")
    print(f"Recipes with neither image nor steps: {neither_count}")

    print("\nPlatform breakdown:")
    print(f"{'Platform':<20} {'Total':<8} {'With Image':<12} {'Validated':<10}")
    print("-" * 52)
    for plat, stats in sorted(platform_stats.items()):
        print(
            f"{plat:<20} {stats['total']:<8} {stats['with_image']:<12} "
            f"{stats['validated']:<10}"
        )

    # Write output artifact atomically
    output_path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(final_records, ensure_ascii=False, indent=2)
    output_path.write_text(serialized + "\n", encoding="utf-8")

    file_size_mb = len(serialized.encode("utf-8")) / (1024 * 1024)
    print(f"\nArtifact written: {output_path} ({file_size_mb:.2f} MB)")
    print("=" * 60 + "\n")

    return final_records


def parse_args(args: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse media builder command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Build recipe_media.json for the SweepFood catalog."
    )
    parser.add_argument(
        "--raw",
        type=Path,
        required=True,
        help="Path to ai_raw_scraped.json",
    )
    parser.add_argument(
        "--detailed",
        type=Path,
        required=True,
        help="Path to ai_detailed.json",
    )
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        default=DEFAULT_BUNDLE_DIR,
        help="Path to AI bundle data directory (default: AI/data)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Path to destination recipe_media.json",
    )
    parser.add_argument(
        "--no-network",
        action="store_true",
        help="Skip network scraping and image validation",
    )
    return parser.parse_args(args)


def main(args: Sequence[str] | None = None) -> int:
    """CLI entrypoint."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parsed = parse_args(args)
    asyncio.run(
        run_builder(
            raw_path=parsed.raw,
            detailed_path=parsed.detailed,
            bundle_dir=parsed.bundle_dir,
            output_path=parsed.output,
            no_network=parsed.no_network,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
