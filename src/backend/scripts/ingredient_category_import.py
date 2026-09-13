"""Transform nutrition categories into ingredient_categories.json."""

from __future__ import annotations

import argparse
import json
import unicodedata
from collections.abc import Iterable
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid5

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT = PROJECT_ROOT / "data/raw/food_nutrition_raw.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "data/normalized/ingredient_categories.json"
UNCLASSIFIED_CATEGORY = "Chưa phân loại"
CATEGORY_DESCRIPTIONS = {
    "Chưa phân loại": "Nguyên liệu chưa đủ thông tin để xếp vào một nhóm cụ thể.",
    "Dầu, mỡ, bơ": "Dầu ăn, mỡ động vật, bơ và các chất béo dùng trong chế biến.",
    "Gia vị, nước chấm": "Gia vị, thảo mộc, nước chấm và sản phẩm tạo hương vị cho món ăn.",
    "Hạt, quả giàu đạm, béo và sản phẩm chế biến": "Các loại hạt, đậu, quả giàu đạm hoặc chất béo và sản phẩm chế biến.",
    "Khoai củ và sản phẩm chế biến": "Khoai, củ, rễ ăn được và các sản phẩm chế biến từ chúng.",
    "Ngũ cốc và sản phẩm chế biến": "Gạo, ngũ cốc, bột, mì và các sản phẩm chế biến từ ngũ cốc.",
    "Nước giải khát": "Đồ uống không cồn, bao gồm nước giải khát và thức uống pha chế.",
    "Quả chín": "Các loại trái cây chín dùng để ăn tươi hoặc chế biến.",
    "Rau, quả, củ dùng làm rau": "Rau xanh, củ và quả được sử dụng như rau trong bữa ăn.",
    "Sữa và sản phẩm chế biến": "Sữa và các sản phẩm chế biến từ sữa.",
    "Thịt và sản phẩm chế biến": "Thịt gia súc, gia cầm và các sản phẩm chế biến từ thịt.",
    "Thủy sản và sản phẩm chế biến": "Cá, tôm, cua, nhuyễn thể và các sản phẩm chế biến từ thủy sản.",
    "Thức ăn truyền thống": "Món ăn, thực phẩm và sản phẩm mang đặc trưng ẩm thực truyền thống.",
    "Trứng và sản phẩm chế biến": "Trứng gia cầm và các sản phẩm chế biến từ trứng.",
    "Đồ hộp": "Thực phẩm đóng hộp hoặc chế biến sẵn để bảo quản lâu hơn.",
    "Đồ ngọt (đường, bánh, mứt, kẹo)": "Đường, bánh, mứt, kẹo và các sản phẩm có vị ngọt.",
}


def normalize_text(value: str) -> str:
    """Return NFC text with zero-width characters and excess whitespace removed."""
    normalized = unicodedata.normalize("NFC", value).replace("\u200b", "")
    return " ".join(normalized.split())


def category_id(name: str) -> str:
    """Return the stable UUID for one category natural key."""
    return str(uuid5(NAMESPACE_URL, f"sweep-food:ingredient-category:{name.casefold()}"))


def category_description(name: str) -> str:
    """Return the short curated description for one stable category name."""
    return CATEGORY_DESCRIPTIONS.get(name, f"Nhóm nguyên liệu thuộc danh mục {name}.")


def load_food_rows(input_path: Path) -> list[dict[str, Any]]:
    """Load the paginated nutrition payload and return its data rows."""
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    rows = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise ValueError("Expected food_nutrition_raw.json to contain a data array of objects.")
    return rows


def transform_categories(food_rows: Iterable[dict[str, Any]]) -> list[dict[str, str]]:
    """Normalize source categories into rows for ingredient_categories."""
    names: set[str] = {UNCLASSIFIED_CATEGORY}
    for row in food_rows:
        category = row.get("category")
        if not isinstance(category, str):
            raise TypeError(f"Food {row.get('code', '<unknown>')} has no category.")
        name = normalize_text(category)
        if not name:
            raise ValueError(f"Food {row.get('code', '<unknown>')} has a blank category.")
        names.add(name)

    rows = [
        {"id": category_id(name), "name": name, "description": category_description(name)}
        for name in sorted(names, key=str.casefold)
    ]
    if len({name.casefold() for name in names}) != len(rows):
        raise ValueError("Normalized ingredient category names are not unique.")
    if len({row["id"] for row in rows}) != len(rows):
        raise ValueError("Normalized ingredient category IDs are not unique.")
    return rows


def write_json(output_path: Path, rows: list[dict[str, str]]) -> None:
    """Write a complete JSON array atomically."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(f"{output_path.suffix}.tmp")
    temporary_path.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary_path.replace(output_path)


def parse_args() -> argparse.Namespace:
    """Parse category-transform options."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    """Run the ingredient-category transformation."""
    args = parse_args()
    rows = transform_categories(load_food_rows(args.input))
    write_json(args.output, rows)
    print(f"Wrote {len(rows)} ingredient categories to {args.output}")


if __name__ == "__main__":
    main()
