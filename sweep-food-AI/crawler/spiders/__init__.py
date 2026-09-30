"""SweepFood Spiders Package."""

from crawler.spiders.base_spider import BaseRecipeSpider, RawRecipe
from crawler.spiders.cookpad_spider import CookpadSpider
from crawler.spiders.monngonmoingay_spider import MonNgonMoiNgaySpider
from crawler.spiders.dienmayxanh_spider import DienMayXanhSpider

__all__ = [
    "BaseRecipeSpider",
    "RawRecipe",
    "CookpadSpider",
    "MonNgonMoiNgaySpider",
    "DienMayXanhSpider",
]
