"""Mon Ngon Moi Ngay Recipe Spider."""

from __future__ import annotations

import html
import logging
import re
import time
from typing import Any
import requests
from bs4 import BeautifulSoup

from crawler.spiders.base_spider import BaseRecipeSpider, RawRecipe

logger = logging.getLogger("monngonmoingay_spider")


class MonNgonMoiNgaySpider(BaseRecipeSpider):
    """Crawler for Mon Ngon Moi Ngay (monngonmoingay.com)."""

    def __init__(self, request_delay: float = 1.0) -> None:
        super().__init__(request_delay=request_delay)
        self.base_url = "https://monngonmoingay.com"

    def discover_recipe_urls(self, limit: int = 2000) -> list[str]:
        """Discover recipe URLs from search and category pages with deep pagination."""
        seed_urls = []
        # Main comprehensive search index (180+ pages with 12 dishes each = 2,160+ recipes)
        for page in range(1, 185):
            seed_urls.append(f"{self.base_url}/tim-kiem-mon-ngon/page/{page}/")

        # Category indexes for additional coverage
        categories = [
            "mon-kho", "mon-canh", "mon-xao", "mon-chien", "mon-hap", "mon-nuong",
            "mon-lau", "mon-goi", "mon-chay", "mon-an-sang", "mon-trang-mieng",
            "mon-sup", "mon-cuon", "mon-an-vat"
        ]
        for cat in categories:
            for page in range(1, 35):
                seed_urls.append(f"{self.base_url}/{cat}/page/{page}/")
        seed_urls.append(f"{self.base_url}/")
        discovered: list[str] = []

        for seed in seed_urls:
            if len(discovered) >= limit:
                break
            for retry in range(2):
                try:
                    time.sleep(self.request_delay * 0.1)
                    resp = self.session.get(seed, timeout=15)
                    if resp.status_code != 200:
                        break

                    soup = BeautifulSoup(resp.text, "html.parser")
                    page_items = 0
                    for a in soup.find_all("a", href=True):
                        href = a["href"]
                        # Target 'Xem chi tiết' links pointing to dish pages
                        if a.text.strip().lower() == "xem chi tiết" and href.startswith(self.base_url):
                            clean_url = href.split("?")[0].rstrip("/") + "/"
                            if clean_url not in discovered:
                                discovered.append(clean_url)
                                page_items += 1
                            if len(discovered) >= limit:
                                break
                    if page_items == 0 and "/page/" in seed:
                        break
                    break
                except Exception as e:
                    if retry == 1:
                        logger.warning(f"Error discovering Mon Ngon Moi Ngay URLs from {seed}: {e}")
                    time.sleep(1.0)

        return discovered[:limit]

    def crawl_recipe(self, url: str) -> RawRecipe | None:
        """Parse Mon Ngon Moi Ngay recipe detail page."""
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

            h1 = soup.find("h1")
            if not h1:
                return None
            title = html.unescape(h1.text.strip())

            # Ingredients
            raw_ingredients: list[str] = []
            for row in soup.select(".block-nguyenlieu .row, .block-nguyenlieu li, .nguyen-lieu li"):
                text = " ".join(row.stripped_strings)
                # Filter out headers like "Nguyên Liệu" or "Gia vị:"
                if text and text not in raw_ingredients and not text.lower().startswith("nguyên liệu"):
                    # Normalize tabs and consecutive whitespace
                    cleaned = re.sub(r"\s+", " ", text).strip()
                    if cleaned:
                        raw_ingredients.append(html.unescape(cleaned))

            if not raw_ingredients:
                return None

            # Instructions
            instructions: list[dict[str, Any]] = []
            step_no = 1
            for h4 in soup.find_all("h4"):
                h4_title = h4.text.strip()
                if any(k in h4_title for k in ["Sơ Chế", "Thực Hiện", "Cách Dùng"]):
                    # Gather text until next h4
                    cur = h4.find_next_sibling()
                    section_texts = []
                    while cur and cur.name != "h4":
                        t = cur.text.strip()
                        if t:
                            section_texts.append(t)
                        cur = cur.find_next_sibling()

                    if section_texts:
                        content = " ".join(section_texts)
                        instructions.append({
                            "step_number": step_no,
                            "title": h4_title.rstrip(":"),
                            "content": html.unescape(content)
                        })
                        step_no += 1

            # Description & Media URL
            description = ""
            desc_meta = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", property="og:description")
            if desc_meta and desc_meta.get("content"):
                description = html.unescape(desc_meta["content"].strip())

            media_url = None
            img_meta = soup.find("meta", property="og:image")
            if img_meta and img_meta.get("content"):
                media_url = img_meta["content"].strip()

            return RawRecipe(
                source_url=url,
                source_platform="monngonmoingay",
                title=title,
                description=description,
                default_servings=4.0,
                estimated_cooking_minutes=35,
                media_url=media_url,
                raw_ingredients=raw_ingredients,
                instructions=instructions,
                tags=["mon_ngon_moi_ngay", "vietnamese_cuisine"],
            )
        except Exception as e:
            logger.error(f"Error crawling Mon Ngon Moi Ngay recipe {url}: {e}")
            return None
