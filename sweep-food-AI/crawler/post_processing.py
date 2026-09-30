"""SweepFood Global Post-Processing & Master Ingredient Ingestion Engine.

Giai đoạn 2: Đọc toàn bộ dữ liệu cào đã được Small LLM làm sạch từ data/interim/,
gom từ điển nguyên liệu độc nhất, làm giàu danh mục Master Ingredients ẩm thực,
chạy Batch Semantic Resolution trên GPU RTX 4060 và tính toán dinh dưỡng chuẩn xác.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
import uuid
from pathlib import Path
from typing import Any
from tqdm import tqdm

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from nlp.nutrition import nutrition_value, scale_nutrition
from nlp.entity_matcher import VietnameseIngredientMatcher, is_green_mango_text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("post_processing")


# Vocabulary key
# --------------
# Resolution is batched over unique vocabulary rather than per row, so each
# batch entry needs ONE raw_context -- but a cleaned name is shared by many raw
# ingredient lines. In the current corpus 2536 of 9358 cleaned names carry more
# than one distinct raw_text, and for "xoài" those 18 variants DISAGREE about
# green evidence (10 green: "Xoài keo 1 quả", "Xoài cát xanh: 1/2 trái", ...;
# 8 not: "45 g xoài", "ĂN KÈM: xoài cát chín", ...). Handing the batch any one
# of them would let whichever recipe was visited first decide all 18 rows.
#
# So the vocabulary is keyed on (cleaned_name, green_flag) instead. This is
# lossless, not a heuristic: raw_context reaches the matching decision through
# exactly one function -- is_green_mango_text(), returning a bool -- and every
# other input to resolution is a function of the cleaned name alone. Resolution
# is therefore f(cleaned_name, green_flag), and within one partition the choice
# of representative raw_context is immaterial because every member of the
# partition yields the same boolean by construction. Keying on the raw_text
# itself would be equally safe but would grow the neural batch from 9358 to
# 27196 entries; this split costs exactly one extra entry ("xoài").


def vocab_key(cleaned_name: str, raw_text: str | None) -> tuple[str, bool]:
    """The (cleaned_name, green_flag) identity a resolution is cached under.

    The fallback to cleaned_name mirrors match_batch(), which reads
    `contexts[idx] or raw_name`, so a row with no raw_text keeps today's
    behaviour and the two sides cannot drift apart.
    """
    return cleaned_name, is_green_mango_text(raw_text or cleaned_name)


# Rich Culinary Taxonomy Augmentation: Maps common everyday culinary terms to standard nutrition
CULINARY_ENRICHMENT_MAP = {
    # Spices, Sauces, Condiments
    "nước tương": {"code": "13010", "name": "Nước tương (xì dầu)", "kcal_100g": 60.0, "p": 5.0, "f": 0.1, "c": 8.0},
    "xì dầu": {"code": "13010", "name": "Nước tương (xì dầu)", "kcal_100g": 60.0, "p": 5.0, "f": 0.1, "c": 8.0},
    "dầu hào": {"code": "13027", "name": "Dầu hào", "kcal_100g": 51.0, "p": 1.4, "f": 0.2, "c": 11.0},
    "ngũ vị hương": {"code": "13030", "name": "Ngũ vị hương", "kcal_100g": 310.0, "p": 10.0, "f": 12.0, "c": 40.0},
    "hạt nêm": {"code": "13026", "name": "Bột nêm (hạt nêm)", "kcal_100g": 180.0, "p": 8.0, "f": 1.0, "c": 35.0},
    "bột nêm": {"code": "13026", "name": "Bột nêm (hạt nêm)", "kcal_100g": 180.0, "p": 8.0, "f": 1.0, "c": 35.0},
    "mì chính": {"code": "13025", "name": "Bột ngọt (mì chính)", "kcal_100g": 0.0, "p": 0.0, "f": 0.0, "c": 0.0},
    "nước mắm": {"code": "13017", "name": "Nước mắm", "kcal_100g": 35.0, "p": 5.1, "f": 0.0, "c": 3.7},
    "nước mắm chua ngọt": {"code": "13017", "name": "Nước mắm", "kcal_100g": 35.0, "p": 5.1, "f": 0.0, "c": 3.7},
    "mắm ruốc": {"code": "13011", "name": "Mắm tôm (ruốc)", "kcal_100g": 73.0, "p": 14.8, "f": 1.5, "c": 0.0},
    "mắm ruốc huế": {"code": "13011", "name": "Mắm tôm (ruốc)", "kcal_100g": 73.0, "p": 14.8, "f": 1.5, "c": 0.0},
    "mắm nêm": {"code": "13011", "name": "Mắm nêm (mắm cá)", "kcal_100g": 73.0, "p": 14.8, "f": 1.5, "c": 0.0},
    "muối": {"code": "13015", "name": "Muối ăn", "kcal_100g": 0.0, "p": 0.0, "f": 0.0, "c": 0.0},
    "đường": {"code": "12001", "name": "Đường kính trắng", "kcal_100g": 397.0, "p": 0.0, "f": 0.0, "c": 99.3},
    "đường trắng": {"code": "12001", "name": "Đường kính trắng", "kcal_100g": 397.0, "p": 0.0, "f": 0.0, "c": 99.3},
    "đường phèn": {"code": "12002", "name": "Đường phèn", "kcal_100g": 390.0, "p": 0.0, "f": 0.0, "c": 97.5},
    "dầu ăn": {"code": "6023", "name": "Dầu thực vật hỗn hợp", "kcal_100g": 897.0, "p": 0.0, "f": 99.7, "c": 0.0},
    "dầu mè": {"code": "6012", "name": "Dầu mè", "kcal_100g": 900.0, "p": 0.0, "f": 100.0, "c": 0.0},
    "dầu mè đen": {"code": "6012", "name": "Dầu mè", "kcal_100g": 900.0, "p": 0.0, "f": 100.0, "c": 0.0},
    "tiêu": {"code": "13018", "name": "Hạt tiêu", "kcal_100g": 255.0, "p": 10.9, "f": 3.3, "c": 64.8},
    "dấm": {"code": "13007", "name": "Giấm ăn", "kcal_100g": 18.0, "p": 0.1, "f": 0.0, "c": 0.9},
    "giấm": {"code": "13007", "name": "Giấm ăn", "kcal_100g": 18.0, "p": 0.1, "f": 0.0, "c": 0.9},
    # Allium & Aromatics
    "tỏi": {"code": "4080", "name": "Tỏi ta, tươi", "kcal_100g": 121.0, "p": 6.3, "f": 0.5, "c": 22.8},
    "tỏi bằm": {"code": "4080", "name": "Tỏi ta, tươi", "kcal_100g": 121.0, "p": 6.3, "f": 0.5, "c": 22.8},
    "tỏi băm": {"code": "4080", "name": "Tỏi ta, tươi", "kcal_100g": 121.0, "p": 6.3, "f": 0.5, "c": 22.8},
    "hành tím": {"code": "4081", "name": "Hành củ tươi", "kcal_100g": 38.0, "p": 1.4, "f": 0.2, "c": 7.6},
    "hành khô": {"code": "4081", "name": "Hành củ tươi", "kcal_100g": 38.0, "p": 1.4, "f": 0.2, "c": 7.6},
    "hành lá": {"code": "4019", "name": "Hành hoa, tươi", "kcal_100g": 22.0, "p": 1.3, "f": 0.3, "c": 3.6},
    "ngò rí": {"code": "4041", "name": "Rau mùi (ngò rí)", "kcal_100g": 23.0, "p": 2.1, "f": 0.5, "c": 3.7},
    "rau thơm": {"code": "4041", "name": "Rau thơm (rau mùi)", "kcal_100g": 23.0, "p": 2.1, "f": 0.5, "c": 3.7},
    "rau dền": {"code": "4025", "name": "Rau dền đỏ/trắng, tươi", "kcal_100g": 42.0, "p": 3.1, "f": 0.3, "c": 6.8},
    "dền": {"code": "4025", "name": "Rau dền đỏ/trắng, tươi", "kcal_100g": 42.0, "p": 3.1, "f": 0.3, "c": 6.8},
    "cải muối": {"code": "4014", "name": "Củ cải / cà rốt muối", "kcal_100g": 25.0, "p": 1.0, "f": 0.1, "c": 5.0},
    # Meats & Seafood
    "thịt ba chỉ": {"code": "7018", "name": "Thịt lợn, nửa nạc, nửa mỡ, tươi", "kcal_100g": 260.0, "p": 16.5, "f": 21.5, "c": 0.0},
    "thịt ba chỉ heo": {"code": "7018", "name": "Thịt lợn, nửa nạc, nửa mỡ, tươi", "kcal_100g": 260.0, "p": 16.5, "f": 21.5, "c": 0.0},
    "thịt nạc thăn": {"code": "7017", "name": "Thịt lợn, nạc, tươi", "kcal_100g": 139.0, "p": 19.0, "f": 7.0, "c": 0.0},
    "thịt đùi heo": {"code": "7017", "name": "Thịt lợn, nạc, tươi", "kcal_100g": 139.0, "p": 19.0, "f": 7.0, "c": 0.0},
    "thịt đùi": {"code": "7017", "name": "Thịt lợn, nạc, tươi", "kcal_100g": 139.0, "p": 19.0, "f": 7.0, "c": 0.0},
    "thịt đùi lợn": {"code": "7017", "name": "Thịt lợn, nạc, tươi", "kcal_100g": 139.0, "p": 19.0, "f": 7.0, "c": 0.0},
    "sườn non": {"code": "7053", "name": "Sườn heo (xương heo)", "kcal_100g": 187.0, "p": 17.9, "f": 12.8, "c": 0.0},
    "sườn cốt lết": {"code": "7053", "name": "Sườn heo (xương heo)", "kcal_100g": 187.0, "p": 17.9, "f": 12.8, "c": 0.0},
    "thịt cốt lết": {"code": "7017", "name": "Thịt lợn, nạc, tươi", "kcal_100g": 139.0, "p": 19.0, "f": 7.0, "c": 0.0},
    "cốt lết": {"code": "7017", "name": "Thịt lợn, nạc, tươi", "kcal_100g": 139.0, "p": 19.0, "f": 7.0, "c": 0.0},
    "thịt bò": {"code": "7003", "name": "Thịt bò, loại I, tươi", "kcal_100g": 118.0, "p": 21.0, "f": 3.8, "c": 0.0},
    "thịt bò phi lê": {"code": "7005", "name": "Thịt bò, thăn nạc, tươi", "kcal_100g": 121.0, "p": 23.0, "f": 3.1, "c": 0.0},
    "thịt nguội": {"code": "7066", "name": "Dăm bông lợn (thịt nguội)", "kcal_100g": 318.0, "p": 23.0, "f": 25.0, "c": 0.3},
    "xương gà": {"code": "7013", "name": "Thịt gà ta, tươi", "kcal_100g": 199.0, "p": 20.3, "f": 13.1, "c": 0.0},
    "tôm": {"code": "8032", "name": "Tôm đồng/biển tươi", "kcal_100g": 85.0, "p": 18.4, "f": 0.8, "c": 1.2},
    "ốc": {"code": "8041", "name": "Ốc bươu", "kcal_100g": 84.0, "p": 11.1, "f": 0.7, "c": 8.3},
    "ốc bươu": {"code": "8041", "name": "Ốc bươu", "kcal_100g": 84.0, "p": 11.1, "f": 0.7, "c": 8.3},
    "lá sách bò": {"code": "7003", "name": "Thịt bò, loại I, tươi", "kcal_100g": 118.0, "p": 21.0, "f": 3.8, "c": 0.0},
    "sách bò": {"code": "7003", "name": "Thịt bò, loại I, tươi", "kcal_100g": 118.0, "p": 21.0, "f": 3.8, "c": 0.0},
    # Fruits & Produce
    "dứa": {"code": "5008", "name": "Dứa (thơm/khóm), quả tươi", "kcal_100g": 50.0, "p": 0.5, "f": 0.1, "c": 13.1},
    "thơm": {"code": "5008", "name": "Dứa (thơm/khóm), quả tươi", "kcal_100g": 50.0, "p": 0.5, "f": 0.1, "c": 13.1},
    "khóm": {"code": "5008", "name": "Dứa (thơm/khóm), quả tươi", "kcal_100g": 50.0, "p": 0.5, "f": 0.1, "c": 13.1},
    "dứa chín": {"code": "5015", "name": "Dứa tây", "kcal_100g": 40.0, "p": 0.5, "f": 0.1, "c": 9.2},
    "tắc": {"code": "5037", "name": "Quất (tắc), tươi", "kcal_100g": 71.0, "p": 1.9, "f": 0.9, "c": 15.9},
    "nước cốt tắc": {"code": "5037", "name": "Nước cốt quất (tắc)", "kcal_100g": 35.0, "p": 0.8, "f": 0.1, "c": 8.0},
    "dừa xiêm": {"code": "5010", "name": "Nước dừa tươi", "kcal_100g": 19.0, "p": 0.7, "f": 0.2, "c": 3.7},
    "nước dừa tươi": {"code": "5010", "name": "Nước dừa tươi", "kcal_100g": 19.0, "p": 0.7, "f": 0.2, "c": 3.7},
    "nước dừa": {"code": "5010", "name": "Nước dừa tươi", "kcal_100g": 19.0, "p": 0.7, "f": 0.2, "c": 3.7},
    "cơm dừa": {"code": "5011", "name": "Cơm dừa nạo", "kcal_100g": 354.0, "p": 3.3, "f": 33.5, "c": 15.2},
    "bột rau câu": {"code": "4067", "name": "Rau câu, khô", "kcal_100g": 281.0, "p": 11.2, "f": 0.0, "c": 56.6},
    "bắp mỹ": {"code": "1007", "name": "Ngô ngọt (bắp Mỹ), tươi", "kcal_100g": 86.0, "p": 3.2, "f": 1.2, "c": 19.0},
    "ngô hạt bắp": {"code": "1007", "name": "Ngô ngọt (bắp Mỹ) tách hạt", "kcal_100g": 86.0, "p": 3.2, "f": 1.2, "c": 19.0},
    "bắp hạt": {"code": "1007", "name": "Ngô ngọt (bắp Mỹ) tách hạt", "kcal_100g": 86.0, "p": 3.2, "f": 1.2, "c": 19.0},
    "đậu bắp": {"code": "4013", "name": "Đậu bắp, tươi", "kcal_100g": 33.0, "p": 1.9, "f": 0.2, "c": 7.5},
    "bánh hỏi": {"code": "1013", "name": "Bánh hỏi (từ bột gạo)", "kcal_100g": 146.0, "p": 3.2, "f": 0.2, "c": 31.2},
    "bánh hỏi khô": {"code": "1013", "name": "Bánh hỏi khô (từ bột gạo)", "kcal_100g": 340.0, "p": 7.0, "f": 0.5, "c": 77.0},
    "bột char siu": {"code": "13030", "name": "Gia vị xá xíu (ngũ vị hương)", "kcal_100g": 310.0, "p": 10.0, "f": 12.0, "c": 40.0},
    "bột xá xíu": {"code": "13030", "name": "Gia vị xá xíu (ngũ vị hương)", "kcal_100g": 310.0, "p": 10.0, "f": 12.0, "c": 40.0},
    "bánh xếp kiểu nhật gyoza": {"code": "12089", "name": "Bánh gối (bánh xếp)", "kcal_100g": 210.0, "p": 8.0, "f": 6.0, "c": 30.0},
    "bánh xếp gyoza": {"code": "12089", "name": "Bánh gối (bánh xếp)", "kcal_100g": 210.0, "p": 8.0, "f": 6.0, "c": 30.0},
    "lá dứa": {"code": "4090", "name": "Lá nếp (lá dứa), tươi", "kcal_100g": 20.0, "p": 1.0, "f": 0.2, "c": 3.5},
    "đá viên": {"code": "14057", "name": "Nước đá", "kcal_100g": 0.0, "p": 0.0, "f": 0.0, "c": 0.0},
    "mít thái sợi": {"code": "5028", "name": "Mít chín tươi thái sợi", "kcal_100g": 95.0, "p": 1.7, "f": 0.6, "c": 23.2},
    "tàu hũ ky": {"code": "3026", "name": "Đậu phụ chúc", "kcal_100g": 465.0, "p": 44.6, "f": 28.0, "c": 8.7},
    "tàu hủ ky": {"code": "3026", "name": "Đậu phụ chúc", "kcal_100g": 465.0, "p": 44.6, "f": 28.0, "c": 8.7},
    "váng đậu": {"code": "3026", "name": "Đậu phụ chúc", "kcal_100g": 465.0, "p": 44.6, "f": 28.0, "c": 8.7},
    "phù trúc": {"code": "3026", "name": "Đậu phụ chúc", "kcal_100g": 465.0, "p": 44.6, "f": 28.0, "c": 8.7},
    "rau nêm": {"code": "4019", "name": "Hành hoa, tươi", "kcal_100g": 22.0, "p": 1.3, "f": 0.3, "c": 3.6},
    "thảo quả": {"code": "13030", "name": "Ngũ vị hương", "kcal_100g": 310.0, "p": 10.0, "f": 12.0, "c": 40.0},
    "thuốc bắc": {"code": "13030", "name": "Ngũ vị hương", "kcal_100g": 310.0, "p": 10.0, "f": 12.0, "c": 40.0},
    "đồ chua": {"code": "4014", "name": "Củ cải / cà rốt muối", "kcal_100g": 25.0, "p": 1.0, "f": 0.1, "c": 5.0},
    "lá chúc": {"code": "13059", "name": "Lá chanh", "kcal_100g": 85.0, "p": 3.5, "f": 0.5, "c": 16.0},
    "chanh thái": {"code": "13059", "name": "Lá chanh", "kcal_100g": 85.0, "p": 3.5, "f": 0.5, "c": 16.0},
    "măng luộc": {"code": "4053", "name": "Măng tre, tươi", "kcal_100g": 31.0, "p": 1.7, "f": 0.1, "c": 5.8},
    "măng": {"code": "4053", "name": "Măng tre, tươi", "kcal_100g": 31.0, "p": 1.7, "f": 0.1, "c": 5.8},
    "măng tươi": {"code": "4053", "name": "Măng tre, tươi", "kcal_100g": 31.0, "p": 1.7, "f": 0.1, "c": 5.8},
}


class GlobalRecipePostProcessor:
    """Master Post-Processing Engine for the entire crawled recipe collection."""

    def __init__(
        self,
        interim_dir: str | Path = "data/interim",
        output_dir: str | Path = "data/processed/recipes",
        catalog_csv_path: str | Path | None = None,
    ) -> None:
        self.interim_dir = Path(interim_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Initializing Post-Processing Semantic Matcher on GPU (RTX 4060)...")
        self.matcher = VietnameseIngredientMatcher(
            catalog_csv_path=catalog_csv_path,
        )

    def run(self) -> dict[str, Any]:
        """Execute post-processing: vocabulary aggregation, batch resolution, and final exports."""
        interim_json = self.interim_dir / "recipes_crawled_cleaned.json"
        if not interim_json.exists():
            raise FileNotFoundError(f"Interim cleaned recipes not found at {interim_json}. Run crawler first.")

        with open(interim_json, "r", encoding="utf-8") as f:
            cleaned_recipes = json.load(f)

        logger.info(f"Loaded {len(cleaned_recipes)} cleaned recipes from interim storage.")

        # 1. Gather all unique ingredient names across recipes, each with the
        # original raw ingredient line the green-mango guard has to read. A
        # dict keyed in first-seen order, not a set: set iteration order varies
        # between processes (string hash randomisation), which would make both
        # the batch order and the representative raw_context unreproducible.
        vocab_contexts: dict[tuple[str, bool], str | None] = {}
        for r in cleaned_recipes:
            for ing in r.get("ingredients", []):
                name = ing.get("name", "").strip().lower()
                if not name:
                    continue
                raw_text = ing.get("raw_text")
                vocab_contexts.setdefault(vocab_key(name, raw_text), raw_text)

        unique_names = {key[0] for key in vocab_contexts}
        logger.info(
            f"Aggregated {len(unique_names)} unique cleaned ingredients "
            f"({len(vocab_contexts)} resolution keys) across all recipes."
        )

        # 2. Batch Resolve Unique Vocabulary
        # First check Culinary Enrichment Map, then BERT Semantic Match
        resolved_vocab: dict[tuple[str, bool], dict[str, Any]] = {}
        unresolved_for_bert: list[str] = []
        unresolved_keys: list[tuple[str, bool]] = []
        unresolved_contexts: list[str | None] = []

        for key, raw_context in vocab_contexts.items():
            name = key[0]
            # Check direct culinary map
            if name in CULINARY_ENRICHMENT_MAP:
                info = CULINARY_ENRICHMENT_MAP[name]
                resolved_vocab[key] = {
                    "code": info["code"],
                    "name": info["name"],
                    "confidence": 1.0,
                    "method": "CULINARY_TAXONOMY_MATCH",
                    "nutrition_100g": {
                        "calories": info["kcal_100g"],
                        "protein": info["p"],
                        "fat": info["f"],
                        "carbs": info["c"],
                    },
                }
            else:
                # The three lists stay positionally aligned: one append per
                # list, per key, in the same iteration. match_batch() pairs
                # unresolved_for_bert[i] with unresolved_contexts[i].
                unresolved_for_bert.append(name)
                unresolved_keys.append(key)
                unresolved_contexts.append(raw_context)

        logger.info(f"Instantly resolved {len(resolved_vocab)} items via Culinary Taxonomy.")
        logger.info(f"Submitting {len(unresolved_for_bert)} items to Vietnamese BERT Bi-Encoder on RTX 4060...")

        # Run BERT batch matching on remaining items
        if unresolved_for_bert:
            bert_matches = self.matcher.match_batch(
                unresolved_for_bert,
                batch_size=128,
                raw_contexts=unresolved_contexts,
            )
            for key, m_res in zip(unresolved_keys, bert_matches):
                matched_item = m_res["matched_item"]
                confidence = m_res["confidence"]
                method = m_res["method"]

                try:
                    c_kcal = nutrition_value(matched_item.get("energy_kcal"))
                    c_p = nutrition_value(matched_item.get("protein_g"))
                    c_f = nutrition_value(matched_item.get("fat_g"))
                    c_c = nutrition_value(matched_item.get("carbs_g"))
                except Exception:
                    c_kcal, c_p, c_f, c_c = None, None, None, None

                resolved_vocab[key] = {
                    "code": matched_item.get("code"),
                    "name": matched_item.get("name_vi"),
                    "confidence": confidence,
                    "method": method,
                    "nutrition_100g": {
                        "calories": c_kcal,
                        "protein": c_p,
                        "fat": c_f,
                        "carbs": c_c,
                    },
                }

        # 3. Apply resolved data to recipes and calculate accurate portion nutrition
        final_recipes = []
        final_ingredients = []
        triage_review_needed = []
        learned_aliases = []

        for r in tqdm(cleaned_recipes, desc="Building DB & Portions", unit="recipe", dynamic_ncols=True):
            recipe_id = r["id"]
            tot_cal, tot_prot, tot_fat, tot_carbs = 0.0, 0.0, 0.0, 0.0
            recipe_ing_list = []

            for ing in r.get("ingredients", []):
                name = ing.get("name", "").strip().lower()
                # Each row is resolved under its OWN green evidence, so
                # "45 g xoài" and "Xoài keo 1 quả" reach different verdicts in
                # the same run despite sharing the cleaned name "xoài".
                resolved = resolved_vocab.get(vocab_key(name, ing.get("raw_text")), {})
                conf = resolved.get("confidence", 0.0)
                m_code = resolved.get("code")
                m_name = resolved.get("name")
                nut = resolved.get("nutrition_100g", {})

                # Calculate portion nutrition
                qty = ing.get("quantity")
                unit = ing.get("unit")
                portion_cal = None
                portion_prot = None
                portion_fat = None
                portion_carbs = None

                factor = None
                if unit == "KG" and qty is not None:
                    factor = (qty * 1000.0) / 100.0
                elif unit in ("GRAM", "ML") and qty is not None:
                    factor = qty / 100.0
                elif unit == "LB" and qty is not None:
                    factor = (qty * 453.6) / 100.0
                elif unit == "LITER" and qty is not None:
                    factor = (qty * 1000.0) / 100.0
                elif unit == "MUONG_CANH" and qty is not None:
                    factor = (qty * 15.0) / 100.0
                elif unit == "MUONG_CA_PHE" and qty is not None:
                    factor = (qty * 5.0) / 100.0
                elif unit == "CHEN_COC" and qty is not None:
                    factor = (qty * 200.0) / 100.0
                elif unit == "BO" and qty is not None:
                    factor = (qty * 100.0) / 100.0
                elif unit in ("PIECE", "TRAI_QUA") and qty is not None:
                    factor = (qty * 100.0) / 100.0

                if factor is not None and nut:
                    portion_cal = scale_nutrition(nut.get("calories"), factor)
                    portion_prot = scale_nutrition(nut.get("protein"), factor)
                    portion_fat = scale_nutrition(nut.get("fat"), factor)
                    portion_carbs = scale_nutrition(nut.get("carbs"), factor)

                    # Preserve legacy sums of known contributions; totals may be incomplete.
                    tot_cal += portion_cal or 0.0
                    tot_prot += portion_prot or 0.0
                    tot_fat += portion_fat or 0.0
                    tot_carbs += portion_carbs or 0.0

                unit_vi = ing.get("unit_vi") or "phần ăn"

                # Flag for triage if confidence is low. conf is None for an
                # UNMATCHED verdict -- the guard asserts "no master link", not
                # a scored rejection (see nlp/entity_matcher._unmatched_result
                # and tests/test_unmatched_confidence_semantics.py) -- so it is
                # triaged rather than compared, which would raise TypeError.
                if conf is None or conf < 0.70:
                    triage_review_needed.append({
                        "raw_text": ing.get("raw_text"),
                        "cleaned_name": name,
                        "suggested_master_code": m_code,
                        "suggested_master_name": m_name,
                        "confidence": conf,
                    })
                elif conf >= 0.88 and m_code:
                    learned_aliases.append({
                        "alias": name,
                        "normalized_alias": name,
                        "master_ingredient_code": m_code,
                        "master_ingredient_name": m_name,
                        "confidence": conf,
                    })

                ing_record = {
                    "id": ing["id"],
                    "recipe_id": recipe_id,
                    "master_ingredient_code": m_code,
                    "master_ingredient_name": m_name,
                    "raw_text": ing.get("raw_text"),
                    "cleaned_name": name,
                    "required_quantity": qty if qty is not None else 1.0,
                    "unit_vi": unit_vi,
                    "unit": unit or "OTHER",
                    "preparation_note": ing.get("preparation_note"),
                    "match_confidence": conf,
                    "match_method": resolved.get("method"),
                    "portion_nutrition": {
                        "calories_kcal": portion_cal,
                        "protein_g": portion_prot,
                        "fat_g": portion_fat,
                        "carbs_g": portion_carbs,
                    },
                }
                recipe_ing_list.append(ing_record)
                final_ingredients.append(ing_record)

            final_recipe_record = {
                "id": recipe_id,
                "name": r["name"],
                "source_platform": r["source_platform"],
                "source_url": r["source_url"],
                "description": r["description"],
                "instructions": r["instructions"],
                "media_url": r["media_url"],
                "default_servings": r["default_servings"],
                "estimated_cooking_minutes": r["estimated_cooking_minutes"],
                "total_calories": round(tot_cal, 2) if tot_cal > 0 else None,
                "total_protein_g": round(tot_prot, 2) if tot_prot > 0 else None,
                "total_fat_g": round(tot_fat, 2) if tot_fat > 0 else None,
                "total_carbs_g": round(tot_carbs, 2) if tot_carbs > 0 else None,
                "tags": r["tags"],
                "ingredients_count": len(recipe_ing_list),
            }
            final_recipes.append(final_recipe_record)

        # 4. Save Final Relational Database Seed Files
        recipes_json = self.output_dir / "recipes.json"
        recipes_csv = self.output_dir / "recipes.csv"
        ingredients_json = self.output_dir / "recipe_ingredients.json"
        ingredients_csv = self.output_dir / "recipe_ingredients.csv"
        aliases_csv = self.output_dir / "ingredient_aliases_learned.csv"
        triage_csv = self.output_dir / "triage_review_needed.csv"

        with open(recipes_json, "w", encoding="utf-8") as f:
            json.dump(final_recipes, f, ensure_ascii=False, indent=2)

        with open(ingredients_json, "w", encoding="utf-8") as f:
            json.dump(final_ingredients, f, ensure_ascii=False, indent=2)

        if final_recipes:
            r_keys = [
                "id", "name", "source_platform", "source_url", "default_servings",
                "estimated_cooking_minutes", "total_calories", "total_protein_g",
                "total_fat_g", "total_carbs_g", "ingredients_count"
            ]
            with open(recipes_csv, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=r_keys, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(final_recipes)

        if final_ingredients:
            i_keys = [
                "id", "recipe_id", "master_ingredient_code", "master_ingredient_name",
                "raw_text", "cleaned_name", "required_quantity", "unit_vi", "unit",
                "preparation_note", "match_confidence", "match_method"
            ]
            with open(ingredients_csv, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=i_keys, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(final_ingredients)

        if learned_aliases:
            a_keys = ["alias", "normalized_alias", "master_ingredient_code", "master_ingredient_name", "confidence"]
            with open(aliases_csv, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=a_keys, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(learned_aliases)

        if triage_review_needed:
            t_keys = ["raw_text", "cleaned_name", "suggested_master_code", "suggested_master_name", "confidence"]
            with open(triage_csv, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=t_keys, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(triage_review_needed)

        logger.info(f"Exported {len(final_recipes)} final recipes to {recipes_json} and {recipes_csv}")
        logger.info(f"Exported {len(final_ingredients)} final recipe_ingredients to {ingredients_json} and {ingredients_csv}")
        logger.info(f"Recorded {len(learned_aliases)} high-confidence aliases to {aliases_csv}")
        logger.info(f"Isolated {len(triage_review_needed)} low-confidence items to {triage_csv}")

        return {
            "recipes_count": len(final_recipes),
            "ingredients_count": len(final_ingredients),
            "unique_vocab_count": len(unique_names),
            "aliases_learned": len(learned_aliases),
            "triage_count": len(triage_review_needed),
            "recipes": final_recipes,
            "ingredients": final_ingredients,
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="SweepFood Global Recipe Post-Processing Engine")
    parser.add_argument("--interim", type=str, default="data/interim", help="Directory of cleaned interim recipes")
    parser.add_argument("--output", type=str, default="data/processed/recipes", help="Final processed database directory")
    args = parser.parse_args()

    processor = GlobalRecipePostProcessor(interim_dir=args.interim, output_dir=args.output)
    result = processor.run()

    print("\n" + "=" * 80)
    print("STAGE 2: POST-PROCESSING & MASTER RESOLUTION COMPLETE")
    print("=" * 80)
    print(f"Total Processed Recipes:    {result['recipes_count']}")
    print(f"Total Ingredients Resolved: {result['ingredients_count']}")
    print(f"Unique Vocabularies Mapped: {result['unique_vocab_count']}")
    print(f"High-Confidence Aliases:    {result['aliases_learned']}")
    print(f"Triage Items for Review:    {result['triage_count']}")

    print("\nResolved Ingredient Samples:")
    for ing in result["ingredients"][:10]:
        print(f"  * Cleaned: '{ing['cleaned_name']}' (from '{ing['raw_text']}')")
        print(f"    -> Mapped to: [{ing['master_ingredient_code']}] {ing['master_ingredient_name']}")
        print(f"    -> Method: {ing['match_method']} | Confidence: {ing['match_confidence']:.4f}")
        cal = ing['portion_nutrition']['calories_kcal']
        if cal:
            print(f"    -> Portion Nutrition: {cal} kcal, {ing['portion_nutrition']['protein_g']}g P")


if __name__ == "__main__":
    main()
