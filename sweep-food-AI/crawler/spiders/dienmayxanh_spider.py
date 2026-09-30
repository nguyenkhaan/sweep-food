"""Dien May Xanh / Bach Hoa Xanh Vao Bep Recipe Spider."""

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

logger = logging.getLogger("dienmayxanh_spider")


class DienMayXanhSpider(BaseRecipeSpider):
    """Crawler for Dien May Xanh Vao Bep (dienmayxanh.com/vao-bep)."""

    def __init__(self, request_delay: float = 1.0) -> None:
        super().__init__(request_delay=request_delay)
        self.base_url = "https://www.dienmayxanh.com"

    def discover_recipe_urls(self, limit: int = 2000) -> list[str]:
        """Discover recipe URLs from Vao Bep portal using category index and AJAX ViewMoreDish."""
        discovered: list[str] = []
        categories = [
            "mon-chinh", "mon-canh", "mon-kho", "mon-xao", "mon-nuong",
            "mon-lau", "mon-chay", "mon-hap", "mon-chien", "mon-goi-tron",
            "mon-trang-mieng", "thuc-uong", "mon-banh", "an-vat", "mon-cuon-tron",
            "meo-vao-bep", "ngay-le-tet", "tra-sua"
        ]

        ajax_url = f"{self.base_url}/vao-bep/aj/Category/ViewMoreDish"

        for cat in categories:
            if len(discovered) >= limit:
                break
            cat_url = f"{self.base_url}/vao-bep/{cat}"
            try:
                time.sleep(self.request_delay * 0.1)
                resp = self.session.get(cat_url, timeout=15)
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")
                # 1. Harvest initial page links
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if "/vao-bep/" in href and re.search(r"-\d+$", href):
                        clean_url = href.split("?")[0]
                        if not clean_url.startswith("http"):
                            clean_url = f"{self.base_url}{clean_url}"
                        if clean_url not in discovered:
                            discovered.append(clean_url)
                        if len(discovered) >= limit:
                            return discovered[:limit]

                # 2. Extract cateId for AJAX ViewMoreDish
                cate_input = soup.find("input", id="categoryId")
                if not cate_input:
                    continue
                cate_id = cate_input.get("value")
                if not cate_id:
                    continue

                # 3. Deep pagination via ViewMoreDish AJAX
                headers = {
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": cat_url,
                }
                for page_idx in range(1, 80):
                    if len(discovered) >= limit:
                        return discovered[:limit]
                    time.sleep(self.request_delay * 0.1)
                    ajax_resp = self.session.post(
                        ajax_url,
                        data={"pageIndex": page_idx, "cateId": cate_id, "isVideo": 0},
                        headers=headers,
                        timeout=15,
                    )
                    if ajax_resp.status_code != 200 or not ajax_resp.text.strip():
                        break

                    ajax_soup = BeautifulSoup(ajax_resp.text, "html.parser")
                    ajax_links = 0
                    for a in ajax_soup.find_all("a", href=True):
                        href = a["href"]
                        if "/vao-bep/" in href and re.search(r"-\d+$", href):
                            clean_url = href.split("?")[0]
                            if not clean_url.startswith("http"):
                                clean_url = f"{self.base_url}{clean_url}"
                            if clean_url not in discovered:
                                discovered.append(clean_url)
                                ajax_links += 1
                            if len(discovered) >= limit:
                                return discovered[:limit]

                    if ajax_links == 0:
                        break

            except Exception as e:
                logger.warning(f"Error discovering Dien May Xanh URLs from {cat}: {e}")

        return discovered[:limit]

    def crawl_recipe(self, url: str) -> RawRecipe | None:
        """Parse Dien May Xanh recipe detail page."""
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
            servings = 4.0
            cooking_time = 40
            media_url = None

            if recipe_data:
                title = html.unescape(recipe_data.get("name", "").strip())
                description = html.unescape(recipe_data.get("description", "").strip())
                raw_ingredients = [html.unescape(str(x).strip()) for x in recipe_data.get("recipeIngredient", []) if str(x).strip()]

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

                img = recipe_data.get("image")
                if isinstance(img, list) and img:
                    media_url = img[0]
                elif isinstance(img, str):
                    media_url = img

                yield_val = recipe_data.get("recipeYield")
                if yield_val:
                    m = re.search(r"(\d+(?:\.\d+)?)", str(yield_val))
                    if m:
                        servings = float(m.group(1))

            if not title:
                h1 = soup.find("h1")
                if h1:
                    title = h1.text.strip()

            if not raw_ingredients:
                for li in soup.select(".box-ingredient li, .ingredient-item, .content-ingredient li"):
                    t = " ".join(li.stripped_strings)
                    if t and t not in raw_ingredients:
                        raw_ingredients.append(t)

            if not instructions:
                step_no = 1
                for step_div in soup.select(".step-detail, .box-step .item-step"):
                    t = " ".join(step_div.stripped_strings)
                    if t:
                        instructions.append({
                            "step_number": step_no,
                            "title": f"Bước {step_no}",
                            "content": t
                        })
                        step_no += 1

            if not title or not raw_ingredients:
                return None

            return RawRecipe(
                source_url=url,
                source_platform="dienmayxanh",
                title=title,
                description=description,
                default_servings=servings,
                estimated_cooking_minutes=cooking_time,
                media_url=media_url,
                raw_ingredients=raw_ingredients,
                instructions=instructions,
                tags=["dien_may_xanh", "vao_bep", "vietnamese_cuisine"],
            )
        except Exception as e:
            logger.error(f"Error crawling Dien May Xanh recipe {url}: {e}")
            return None
