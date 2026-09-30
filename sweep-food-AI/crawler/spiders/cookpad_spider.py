"""Cookpad Vietnam Recipe Spider."""

from __future__ import annotations

import html
import json
import logging
import re
import time
from typing import Any
import requests
from bs4 import BeautifulSoup

from crawler.spiders.base_spider import BaseRecipeSpider, RawRecipe

logger = logging.getLogger("cookpad_spider")


class CookpadSpider(BaseRecipeSpider):
    """Crawler for Cookpad Vietnam (cookpad.com/vn)."""

    def __init__(self, request_delay: float = 1.0) -> None:
        super().__init__(request_delay=request_delay)
        self.base_url = "https://cookpad.com"

    def discover_recipe_urls(self, limit: int = 2000) -> list[str]:
        """Discover recipe URLs across popular Vietnamese culinary keywords and pages."""
        keywords = [
            "thịt heo", "thịt bò", "gà", "vịt", "cá", "tôm", "mực", "hải sản",
            "canh", "món kho", "món xào", "món nướng", "món chiên", "món hấp",
            "lẩu", "gỏi", "súp", "cháo", "bún", "phở", "mì", "cơm", "món chay",
            "rau", "nấm", "đậu phụ", "trứng", "chè", "bánh", "sinh tố", "nước ép",
            "sườn", "ếch", "bò kho", "thịt kho", "canh chua", "món nhậu", "món cuốn",
            "kho quẹt", "chả giò", "nem rán", "chả cá", "món ăn vặt", "món rim"
        ]
        discovered: list[str] = []

        for kw in keywords:
            if len(discovered) >= limit:
                break
            for page in range(1, 50):
                if len(discovered) >= limit:
                    break
                search_url = f"{self.base_url}/vn/tim-kiem/{requests.utils.quote(kw)}?page={page}"
                try:
                    time.sleep(self.request_delay * 0.1)
                    resp = self.session.get(search_url, timeout=15)
                    if resp.status_code != 200:
                        break

                    soup = BeautifulSoup(resp.text, "html.parser")
                    page_links_found = 0
                    for a in soup.find_all("a", href=True):
                        href = a["href"]
                        if re.search(r"/vn/cong-thuc/\d+", href):
                            clean_url = href.split("?")[0]
                            if not clean_url.startswith("http"):
                                clean_url = f"{self.base_url}{clean_url}"
                            if clean_url not in discovered:
                                discovered.append(clean_url)
                                page_links_found += 1
                            if len(discovered) >= limit:
                                break

                    # If no recipes found on this page, stop paginating this keyword
                    if page_links_found == 0:
                        break
                except Exception as e:
                    logger.warning(f"Error discovering Cookpad for '{kw}' p.{page}: {e}")
                    break

        return discovered[:limit]

    def crawl_recipe(self, url: str) -> RawRecipe | None:
        """Parse Cookpad recipe detail page via Schema.org Recipe JSON-LD and HTML fallback."""
        try:
            resp = None
            for retry in range(2):
                try:
                    time.sleep(self.request_delay * 0.2)
                    resp = self.session.get(url, timeout=15)
                    if resp.status_code != 200:
                        logger.warning(f"Failed to fetch {url}: status {resp.status_code}")
                        return None
                    break
                except Exception as e:
                    if retry == 1:
                        logger.error(f"Failed to fetch {url} after retries: {e}")
                        return None
                    time.sleep(2.0)

            if not resp:
                return None

            soup = BeautifulSoup(resp.text, "html.parser")

            # Try parsing Schema.org Recipe LD+JSON
            recipe_data = None
            for script in soup.find_all("script", type="application/ld+json"):
                if not script.string:
                    continue
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and data.get("@type") == "Recipe":
                        recipe_data = data
                        break
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and item.get("@type") == "Recipe":
                                recipe_data = item
                                break
                except Exception:
                    continue

            title = ""
            description = ""
            raw_ingredients: list[str] = []
            instructions: list[dict[str, Any]] = []
            servings = 2.0
            cooking_time = 30
            media_url = None

            if recipe_data:
                title = html.unescape(recipe_data.get("name", "").strip())
                description = html.unescape(recipe_data.get("description", "").strip())
                raw_ingredients = [html.unescape(str(x).strip()) for x in recipe_data.get("recipeIngredient", []) if str(x).strip()]

                # Instructions
                raw_instructions = recipe_data.get("recipeInstructions", [])
                step_no = 1
                for item in raw_instructions:
                    content = ""
                    if isinstance(item, dict):
                        content = item.get("text", "") or item.get("name", "")
                    elif isinstance(item, str):
                        content = item
                    if content.strip():
                        instructions.append({
                            "step_number": step_no,
                            "title": f"Bước {step_no}",
                            "content": html.unescape(content.strip())
                        })
                        step_no += 1

                # Yield / Servings
                yield_val = recipe_data.get("recipeYield")
                if yield_val:
                    m = re.search(r"(\d+(?:\.\d+)?)", str(yield_val))
                    if m:
                        servings = float(m.group(1))

                # Image
                img = recipe_data.get("image")
                if isinstance(img, list) and img:
                    media_url = img[0]
                elif isinstance(img, str):
                    media_url = img

                # Cook / Total Time
                total_time = recipe_data.get("totalTime") or recipe_data.get("cookTime")
                if total_time and isinstance(total_time, str):
                    m_time = re.search(r"PT(?:(\d+)H)?(?:(\d+)M)?", total_time)
                    if m_time:
                        hours = int(m_time.group(1) or 0)
                        minutes = int(m_time.group(2) or 0)
                        calc_time = hours * 60 + minutes
                        if calc_time > 0:
                            cooking_time = calc_time

            # Fallback to DOM elements if missing
            if not title:
                h1 = soup.find("h1")
                if h1:
                    title = h1.text.strip()

            if not raw_ingredients:
                for li in soup.select("ul#ingredients-list li, .ingredient-item"):
                    t = li.text.strip()
                    if t:
                        raw_ingredients.append(t)

            if not instructions:
                step_no = 1
                for li in soup.select("ol#steps li, .step-item"):
                    t = li.text.strip()
                    if t:
                        instructions.append({
                            "step_number": step_no,
                            "title": f"Bước {step_no}",
                            "content": t
                        })
                        step_no += 1

            if not title or not raw_ingredients:
                logger.warning(f"Incomplete recipe data from {url}")
                return None

            return RawRecipe(
                source_url=url,
                source_platform="cookpad",
                title=title,
                description=description,
                default_servings=servings,
                estimated_cooking_minutes=cooking_time,
                media_url=media_url,
                raw_ingredients=raw_ingredients,
                instructions=instructions,
                tags=["vietnamese_homecooked", "cookpad"],
            )
        except Exception as e:
            logger.error(f"Error crawling Cookpad recipe {url}: {e}")
            return None
