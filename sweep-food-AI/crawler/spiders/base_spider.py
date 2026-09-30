"""Base Spider definitions and data structures for SweepFood recipe crawlers."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from typing import Any

logger = logging.getLogger("sweepfood_crawler")


@dataclass
class RawRecipe:
    """Raw crawled recipe before NLP parsing and semantic resolution."""

    source_url: str
    source_platform: str
    title: str
    description: str = ""
    default_servings: float = 2.0
    estimated_cooking_minutes: int = 30
    media_url: str | None = None
    raw_ingredients: list[str] = field(default_factory=list)
    instructions: list[dict[str, Any]] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class BaseRecipeSpider(ABC):
    """Abstract Base Class for recipe crawlers with connection pooling."""

    def __init__(self, request_delay: float = 0.5) -> None:
        self.request_delay = request_delay
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        }

        # High-performance Session with connection pooling
        self.session = requests.Session()
        retries = Retry(
            total=2,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = HTTPAdapter(
            pool_connections=50,
            pool_maxsize=50,
            max_retries=retries,
        )
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        self.session.headers.update(self.headers)

    @abstractmethod
    def crawl_recipe(self, url: str) -> RawRecipe | None:
        """Crawl a single recipe detail page."""
        pass

    @abstractmethod
    def discover_recipe_urls(self, limit: int = 10) -> list[str]:
        """Discover recipe URLs from search or category pages."""
        pass
