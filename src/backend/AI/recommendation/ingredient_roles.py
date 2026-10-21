"""Ingredient roles and taxonomy classifier for recipe recommendation.

Distinguishes between:
1. STAPLE_SPICE: Salt, sugar, fish sauce, pepper, garlic, chili, oil, etc.
   Missing these in household cooking is non-critical (no harsh penalty).
2. CORE_PROTEIN: Pork, beef, chicken, fish, shrimp, tofu, eggs, etc.
   Missing these prevents the core dish from being cooked.
3. CORE_PRODUCE: Morning glory, cabbage, tomato, potato, squash, mushrooms, etc.
   Subject to quantity elasticity (half a bunch is still very acceptable).
4. OPTIONAL_GARNISH: Cilantro, culantro, toasted sesame, decorative herbs, etc.
"""

from __future__ import annotations

# Common Vietnamese pantry staples, basic seasonings, and aromatics
STAPLE_SPICE_KEYWORDS: frozenset[str] = frozenset({
    # Basic Seasonings
    "muối", "đường", "tiêu", "nước mắm", "mắm", "nước tương", "xì dầu",
    "dầu ăn", "mỡ", "hạt nêm", "bột ngọt", "mì chính", "giấm", "dầu hào",
    "sa tế", "bột canh", "ngũ vị hương", "tiêu xay", "tiêu sọ", "bột nghệ",
    "dầu mè", "mật ong", "rượu trắng", "rượu mai quế lộ", "bột ớt",
    # Aromatics & Alliums
    "tỏi", "hành tím", "hành khô", "hành lá", "gừng", "sả", "ớt",
    "hành boa rô", "tỏi băm", "hành băm", "hành phi", "ớt hiểm", "ớt sừng",
    # Thickeners & Frying aids
    "bột năng", "bột bắp", "bột chiên giòn", "bột mì",
})

# Core Animal and Plant Proteins
CORE_PROTEIN_KEYWORDS: frozenset[str] = frozenset({
    "thịt heo", "thịt lợn", "sườn heo", "sườn non", "ba chỉ", "ba rọi",
    "nạc vai", "thịt xay", "thịt băm", "giò sống", "chả lụa", "tai heo",
    "thịt bò", "bắp bò", "thăn bò", "gầu bò", "xương bò",
    "thịt gà", "ức gà", "đùi gà", "cánh gà", "gà ta", "chân gà", "mề gà",
    "thịt vịt", "thịt ngan", "thịt chim",
    "cá", "cá hồi", "cá thu", "cá lóc", "cá chép", "cá rô", "cá diêu hồng",
    "cá bống", "cá ngừ", "cá basa", "phi lê cá", "chả cá",
    "tôm", "tôm sú", "tôm thẻ", "tôm đất", "tép",
    "mực", "mực ống", "mực nang", "bạch tuộc",
    "cua", "ghẹ", "ốc", "ngao", "sò", "nghêu", "hến",
    "ếch", "lươn",
    "trứng", "trứng gà", "trứng vịt", "trứng cút", "lòng đỏ",
    # Plant proteins
    "đậu phụ", "đậu hũ", "tàu hũ", "sườn non chay", "chả chay", "thịt chay",
})

# Core Vegetables, Tubers & Starches
CORE_PRODUCE_KEYWORDS: frozenset[str] = frozenset({
    "rau muống", "bắp cải", "cải ngọt", "cải thảo", "cải thìa", "cải cúc",
    "mồng tơi", "rau đay", "rau ngót", "rau dền", "xà lách", "rau diếp",
    "cà chua", "cà rốt", "củ cải", "khoai tây", "khoai lang", "khoai môn",
    "khoai sọ", "bí đỏ", "bí xanh", "bí đao", "bầu", "mướp", "khổ qua",
    "mướp đắng", "su su", "su hào", "súp lơ", "bông cải", "đậu cô ve",
    "đậu bắp", "đậu đũa", "đậu hà lan", "giá đỗ", "giá", "ngô", "bắp",
    "măng", "măng tây", "nấm rơm", "nấm hương", "nấm đùi gà", "nấm kim châm",
    "nấm linh chi", "nấm bào ngư", "nấm tuyết", "mộc nhĩ",
    # Starches & Wrappers
    "gạo", "cơm", "bún", "phở", "mì", "miến", "hủ tiếu", "bánh đa",
    "hoành thánh", "vỏ hoành thánh", "lá hoành thánh", "sủi cảo", "há cảo",
    "bánh tráng", "vỏ ram", "bánh phở", "bánh canh", "bánh mì", "bánh hỏi", "bánh cuốn",
})

# Optional Garnishes & Decorative Herbs
OPTIONAL_GARNISH_KEYWORDS: frozenset[str] = frozenset({
    "ngò gai", "mùi tàu", "rau om", "rau ngổ", "ngò rí", "rau mùi",
    "húng quế", "húng lủi", "lá chanh", "rau răm", "tía tô", "kinh giới",
    "mè rang", "vừng rang", "đậu phộng", "lạc rang", "ớt tỉa hoa",
})


class IngredientRole:
    STAPLE_SPICE: str = "STAPLE_SPICE"
    CORE_PROTEIN: str = "CORE_PROTEIN"
    CORE_PRODUCE: str = "CORE_PRODUCE"
    OPTIONAL_GARNISH: str = "OPTIONAL_GARNISH"


_MEAT_OR_WRAPPER_EXCLUSIONS: tuple[str, ...] = (
    "thịt", "cá", "tôm", "gà", "bò", "hoành thánh", "sủi cảo", "há cảo", "bánh tráng", "bánh mì"
)


def classify_ingredient_role(cleaned_name: str, master_code: str | None = None) -> str:
    """Classify an ingredient into one of the four roles."""
    n = cleaned_name.strip().lower()

    # 1. Check Staple & Basic Seasoning
    for kw in STAPLE_SPICE_KEYWORDS:
        if kw in n or n.startswith(kw) or n.endswith(kw):
            if any(p in n for p in _MEAT_OR_WRAPPER_EXCLUSIONS):
                continue
            return IngredientRole.STAPLE_SPICE

    # 2. Check Core Protein
    for kw in CORE_PROTEIN_KEYWORDS:
        if kw in n:
            return IngredientRole.CORE_PROTEIN

    # 3. Check Optional Garnish
    for kw in OPTIONAL_GARNISH_KEYWORDS:
        if kw in n:
            return IngredientRole.OPTIONAL_GARNISH

    # 4. Check Core Produce / Vegetable
    for kw in CORE_PRODUCE_KEYWORDS:
        if kw in n:
            return IngredientRole.CORE_PRODUCE

    # Fallback heuristics based on Viện Dinh Dưỡng code prefix
    if master_code:
        clean_c = master_code.strip()
        if clean_c.startswith(("7", "8", "9")):
            return IngredientRole.CORE_PROTEIN
        if clean_c.startswith(("4", "5", "1", "2")):
            return IngredientRole.CORE_PRODUCE
        if clean_c.startswith(("6", "13", "14")):
            return IngredientRole.STAPLE_SPICE

    return IngredientRole.CORE_PRODUCE
