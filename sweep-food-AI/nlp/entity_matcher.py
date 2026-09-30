"""Vietnamese Ingredient Entity Matcher & Semantic Resolver.

Leverages Vietnamese BERT / Bi-Encoder models (e.g. bkai-foundation-models/vietnamese-bi-encoder
or vinai/phobert-base-v2) on NVIDIA CUDA (RTX 4060) to semantically map extracted
ingredient names into the 853 canonical master_ingredients from Viện Dinh Dưỡng.
"""

from __future__ import annotations

import csv
import json
import logging
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

try:
    import torch
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    torch = None
    F = None
    TORCH_AVAILABLE = False


def no_grad_if_available(fn: Any) -> Any:
    """Decorator applying torch.no_grad() if PyTorch is installed."""
    if TORCH_AVAILABLE and torch is not None:
        return torch.no_grad()(fn)
    return fn

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("entity_matcher")


def normalize_vietnamese_text(text: str) -> str:
    """Normalize text: lowercased, stripped, Unicode NFC, with common dialect replacement."""
    text = unicodedata.normalize("NFC", text or "")
    text = text.lower().strip()
    # Remove punctuation except commas
    text = re.sub(r"[^\w\s,]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# USE_7038_CANONICAL: retain the historical row but remove every retrieval route.
DEPRECATED_CATALOG_IDENTITIES = {"20079": "ZZ deprecated 20079 -> 7038"}
CHICKEN_FAT_GUARD_REASON = "CHICKEN_FAT_NO_CATALOG_TARGET"


def is_chicken_fat_text(*texts: str | None) -> bool:
    """Only the reviewed adjacent phrase; do not block pork fat or chicken liver."""
    return any(re.search(r"\bmỡ gà\b", normalize_vietnamese_text(t)) for t in texts if t)


# Coriander SEED/POWDER is a dried spice; the catalog carries no such identity.
# Its only coriander row is 4081 "Rau mùi" (Coriander, raw) -- a fresh leaf at
# 22 kcal / 93.3 g water per 100 g -- and the whole "Gia vị, nước chấm" band has
# cinnamon, curry, paprika, annatto and peppercorn powders but no coriander.
# Removing the two seed/powder aliases does NOT reach UNMATCHED on its own:
# "rau mùi" is a catalog subphrase head, so "bột rau mùi" and "hạt rau mùi" both
# fall straight through to SUBPHRASE_CATALOG_MATCH 4081 at 0.95, and the neural
# stage offers 20011 (curry powder) or 13072 -- different foods. Nothing else in
# the pipeline can decline a match: crawler/post_processing.py accepts whatever
# match_batch returns and only triages low confidence, so a guard is the sole
# durable route to UNMATCHED. Matched on the SEED word directly qualifying a
# coriander word, never on a bare "rau mùi" substring: leaf, root, stem and
# garnish uses must keep resolving, and "bột mùi tây" (parsley powder) is a
# different identity that this guard deliberately leaves alone.
CORIANDER_SEED_POWDER_GUARD_REASON = "CORIANDER_SEED_POWDER_NO_CATALOG_TARGET"
_CORIANDER_SEED_WORD = r"(?:hạt|hột|bột)"
_CORIANDER_HEAD = r"(?:rau mùi|ngò rí|ngò ri|ngò ta|ngò|mùi)"
_CORIANDER_SEED_POWDER_RE = re.compile(
    rf"\b{_CORIANDER_SEED_WORD}(?:\s+và\s+{_CORIANDER_SEED_WORD})?"
    rf"(?:\s+{_CORIANDER_SEED_WORD})?\s+{_CORIANDER_HEAD}\b(?!\s+tây)"
    rf"|\bcorr?iander\s+(?:seeds?|powder)\b"
)


def is_coriander_seed_powder_text(*texts: str | None) -> bool:
    """Explicit coriander seed/powder only; leaf, root, stem and parsley pass."""
    return any(_CORIANDER_SEED_POWDER_RE.search(normalize_vietnamese_text(t)) for t in texts if t)


def clean_culinary_query(query: str) -> str:
    """Strip cosmetic recipe adjectives, crawling typos, and preparation cutting verbs to expose core culinary ingredient."""
    q = normalize_vietnamese_text(query)
    
    # 1. Fix common crawling typos and broken syllables
    typo_map = [
        (r"\bha t nêm\b", "hạt nêm"),
        (r"\bto i\b", "tỏi"),
        (r"\bnươ c mă m\b", "nước mắm"),
        (r"\bbô t ngo t\b", "bột ngọt"),
        (r"\bha nh ti m\b", "hành tím"),
        (r"\bha nh la\b", "hành lá"),
        (r"\bsươ n non\b", "sườn non"),
        (r"\bbô t mi\b", "bột mì"),
        (r"\bdâ u ăn\b", "dầu ăn"),
        (r"\bđươ ng\b", "đường"),
        (r"\bha t tiêu\b", "hạt tiêu"),
        (r"\bnươ c lo c\b", "nước lọc"),
    ]
    for pattern, rep in typo_map:
        q = re.sub(pattern, rep, q, flags=re.IGNORECASE)

    # 2. Strip unit & quantity prefixes
    q = re.sub(r"^(cafe|cf|mcf|ms|muỗng|thìa|xíu|chút|nhúm|vài nhánh|vài cọng|vài tép|ít|nửa)\s+", "", q, flags=re.IGNORECASE).strip()

    # 3. Strip serving prefixes
    q = re.sub(r"^(ăn|dùng)\s+kèm\s+", "", q, flags=re.IGNORECASE).strip()
    q = re.sub(r"^(kèm\s+theo|kèm)\s+", "", q, flags=re.IGNORECASE).strip()

    # 4. Common preparation & cutting noise in Vietnamese recipes
    prep_patterns = [
        r"\bcắt sợi\b",
        r"\bcắt nhỏ\b",
        r"\bcắt khúc\b",
        r"\bcắt lát\b",
        r"\bcắt hạt lựu\b",
        r"\bxắt sợi\b",
        r"\bxắt lát\b",
        r"\bxắt nhỏ\b",
        r"\bbào sợi\b",
        r"\bbào mỏng\b",
        r"\bbào\b",
        r"\bthái lát\b",
        r"\bthái mỏng\b",
        r"\bthái chỉ\b",
        r"\bbăm nhỏ\b",
        r"\bbăm nhuyễn\b",
        r"\bbăm\b",
        r"\bđập dập\b",
        r"\bđập giập\b",
        r"\brửa sạch\b",
        r"\blàm sạch\b",
        r"\bđể ráo\b",
        r"\blàm sẵn\b",
        r"\brút xương\b",
        r"\blóc xương\b",
        r"\bxay nhuyễn\b",
        r"\bxay\b",
        r"\bgiã bể\b",
        r"\bgiã nát\b",
        r"\bxanh non\b",
        r"\btươi sống\b",
        r"\btươi ngon\b",
        r"\btươi\b",
        r"\bngon\b",
        r"\bđặc sản\b",
        r"\bnguyên chất\b",
        r"\bthông dụng\b",
        r"\bthông thường\b",
        r"\btùy chọn\b",
        r"\btùy thích\b",
        r"\bkhoảng\b",
        r"\brau nêm\b",
        r"\brau ăn kèm\b",
        r"\bcác loại\b",
        r"\blột vỏ\b",
        r"\brút sườn\b",
        r"\bđông lạnh\b",
    ]
    for w in prep_patterns:
        q = re.sub(w, "", q, flags=re.IGNORECASE)

    # 5. Strip trailing standalone numbers and specific noise words
    q = re.sub(r"\s+\d+$", "", q)
    q = re.sub(r"(ngò gai|lá chúc|xà lách|nguyệt quế)\s+lá$", r"\1", q, flags=re.IGNORECASE)
    q = re.sub(r"\s+(tai|nhánh|tép)$", "", q, flags=re.IGNORECASE)

    q = re.sub(r"\s+", " ", q).strip()
    return q


# ---------------------------------------------------------------------------
# Mango ripeness guard
# ---------------------------------------------------------------------------
# The catalog carries exactly one mango identity, 5055 "Xoài chín" -- RIPE
# mango. There is no green/unripe mango master (5033 "Muỗm, quéo" is
# Mangifera foetida, a different species and not a substitute). Green mango
# therefore has no valid target in this catalog, so it must stay UNMATCHED
# rather than borrow ripe mango's nutrition.
#
# Removing the "xoài" -> 5055 alias does NOT achieve that: clean_culinary_query()
# strips the green evidence ("xanh non", "tươi sống", "bào sợi", ...) and the
# bare "xoài" that survives still reaches 5055 through SUBPHRASE_CATALOG_MATCH.
# The guard therefore lives at the resolution layer and reads the ORIGINAL raw
# ingredient text, which is the only place the green evidence is still intact.
RIPE_MANGO_CODE = "5055"

MANGO_TOKEN_RE = re.compile(r"\bxoài\b")

# Reviewed green/unripe markers only. Each is either an explicit unripe word
# ("xanh", "sống", "non") or a cultivar this corpus only ever uses green
# ("keo", "tượng", "tứ quý"). "thái" is handled separately below -- it is the
# one marker with a second, unrelated meaning.
#
# "chua" is deliberately NOT a marker here: no mango row in the corpus carries
# it, while ~1560 non-mango rows do -- almost all as part of an unrelated
# ingredient name (cà chua, sữa chua, cải chua, kim chi chua) or as
# recipe-taste description ("tuỳ độ chua của kim chi"). It is recipe context,
# not ingredient-level ripeness evidence, so there is nothing to support it.
GREEN_MANGO_MARKER_RE = re.compile(
    r"\b(?:xanh|sống|non|keo|tượng|tứ quý)\b"
)

# The complements that turn "thái" into the verb "to slice". Drawn from the
# corpus's own usage: of 221 "thái" occurrences in raw_text, the recurring
# cutting forms are thái lát (27), thái mỏng (18), thái chỉ (17), thái nhỏ
# (16), thái sợi (10), thái miếng (4), thái hạt lựu (4), thái múi (3),
# thái rối (3), plus single khúc/vuông/nhuyễn uses.
THAI_SLICING_COMPLEMENTS = (
    "lát", "mỏng", "chỉ", "nhỏ", "sợi", "miếng", "hạt", "múi", "rối",
    "khúc", "vuông", "nhuyễn", "que", "con", "đôi", "làm",
)

# "thái" is the only marker with two meanings: the Thai cultivar (Xoài Thái,
# eaten green) and the verb "to slice". Bare \bthái\b cannot tell them apart
# and would read "xoài thái lát" -- ripe mango, sliced -- as green mango.
#
# The narrowest rule the corpus supports: cultivar evidence requires the
# adjacent phrase "xoài thái" AND no cutting complement after it. All 4
# xoài+thái rows in the corpus are cultivar and are written exactly that way
# ("1 trái xoài Thái", "Xoài Thái: 1 quả", "xoài Thái hoặc xoài tứ quý"); the
# corpus contains no mango slicing instruction today, so this closes a latent
# false positive rather than a live one. Adjacency also keeps an unrelated
# Thai ingredient in the same line ("xoài, ớt sừng thái") from counting.
CULTIVAR_THAI_RE = re.compile(
    r"\bxoài thái\b(?!\s+(?:" + "|".join(THAI_SLICING_COMPLEMENTS) + r")\b)"
)

# Explicit ripeness evidence overrides every marker above, so a ripe row still
# resolves to 5055 even where the cultivar rule would not have saved it.
RIPE_MANGO_MARKER_RE = re.compile(r"\bchín\b")

GREEN_MANGO_GUARD_REASON = "GREEN_MANGO_NO_CATALOG_TARGET"


def is_green_mango_text(*texts: str | None) -> bool:
    """True when the evidence names mango AND carries a reviewed green/unripe
    marker that no explicit ripeness marker overrides.

    Pass the ORIGINAL raw ingredient text: both clean_culinary_query() and the
    grammar parser destroy the green evidence this reads.
    """
    joined = " ".join(normalize_vietnamese_text(t) for t in texts if t)
    if not MANGO_TOKEN_RE.search(joined):
        return False
    if RIPE_MANGO_MARKER_RE.search(joined):
        return False
    if GREEN_MANGO_MARKER_RE.search(joined):
        return True
    return bool(CULTIVAR_THAI_RE.search(joined))


# ---------------------------------------------------------------------------
# Vegetarian ("chay") animal-identity guard
# ---------------------------------------------------------------------------
# "chay" is the explicit Vietnamese vegetarian marker: "đùi gà chay" is a seitan
# drumstick analogue, not poultry. The catalog carries only two imitation-meat
# identities (20039 Thịt chay, 20040 Chả lụa chay), so most analogue phrases have
# no valid target and must stay UNMATCHED rather than borrow an animal's
# nutrition -- "Xúc xích chay 100g" was being scored as 535 kcal of pork sausage.
#
# Removing the offending alias-map keys does NOT achieve that: every one of the
# four reviewed hazards is re-derived by SUBPHRASE_CATALOG_MATCH from the catalog
# head ("đùi gà chay" -> 7088 at 0.55, "thịt cua chay" -> 8069 at 0.62, both well
# over the 0.35 threshold), and the neural stage reaches animal identities on its
# own ("tôm chay" -> 8056, "thịt heo chay" -> 7065, "bò chay khô" -> 7076). The
# guard therefore lives at the resolution layer and is keyed on the RESOLVED
# catalog entry, so it covers every route into an animal identity.
#
# Unlike the green-mango guard above, this one is NOT a blanket pre-neural
# return. Green mango has no valid catalog target at all; "chay" does, and the
# bi-encoder finds it ("gà chay" -> 20040, "sườn ống chay" -> 20039, "giò sống
# chay" -> 20040). Short-circuiting ahead of the neural stage would destroy those
# correct resolutions, so the neural RESULT is filtered instead.
CHAY_TOKEN_RE = re.compile(r"\bchay\b")

# Reviewed animal-identity policy. Category metadata is the primary test: the
# live catalog carries 14 canonical categories and contains ZERO vegan or
# imitation entries filed under these two, so the test is exact.
#
# Deliberately NOT a substring heuristic on animal words. 20007 "Nấm đùi gà" is
# king oyster mushroom -- a vegetable -- and "nấm đùi gà chay" resolves to it at
# 0.67; a rule keyed on "gà" would wrongly block it. Category keeps it safe
# without a special case.
ANIMAL_CATEGORIES_VI = frozenset({
    "Thịt và sản phẩm chế biến",
    "Thủy sản và sản phẩm chế biến",
})

# Reviewed supplement: animal identities filed under NON-animal categories, which
# the category test alone would miss. Each was verified individually by name_en,
# not inferred from code proximity (AGENTS.md §2):
#   11015 Cá thu hộp ......... Mackerel, canned      | Đồ hộp
#   11016 Cá trích hộp ....... Herring, canned       | Đồ hộp
#   11017 Thịt bò hộp ........ Beef, canned          | Đồ hộp
#   11018 Thịt gà hộp ........ Chicken, canned       | Đồ hộp
#   11019 Thịt lợn hộp ....... Pork, canned          | Đồ hộp
#   11020 Thịt lợn, bò xay hộp Pork beef mince canned| Đồ hộp
#   11021 Thịt vịt hầm ....... Duck, stewed meat     | Đồ hộp
#   11022 Cá ngừ hộp ......... canned tuna           | Đồ hộp
#   11023 Cá nục hộp ......... canned scad           | Đồ hộp
#   6003  Mỡ lợn, muối ....... salted pork lard      | Dầu, mỡ, bơ
#   6004  Mỡ lợn, nước ....... rendered pork lard    | Dầu, mỡ, bơ
# These add 0 rows to the current corpus; they are forward protection for routes
# the neural stage demonstrably reaches ("vịt chay" -> 11021, "mỡ heo chay").
ANIMAL_SUPPLEMENTARY_CODES = frozenset({
    "11015", "11016", "11017", "11018", "11019",
    "11020", "11021", "11022", "11023",
    "6003", "6004",
})

# Egg and dairy are deliberately OUT of scope. Vietnamese Buddhist chay is
# normally vegan, but no "chay" row in this corpus reaches those categories and
# no "trứng chay"/"sữa chay" phrase exists, so widening would be unevidenced.
#
# Animal-derived CONDIMENTS (13017 Nước mắm, 13027 Dầu hào, 13011 Mắm tôm ...)
# are also out of scope: they live in "Gia vị, nước chấm" and are therefore
# exempt structurally rather than by special case. This is a reviewed scope
# decision, not a claim that "nước mắm chay" -> 13017 is semantically perfect.

VEGETARIAN_GUARD_REASON = "VEGETARIAN_PHRASE_ANIMAL_TARGET"


def is_chay_text(*texts: str | None) -> bool:
    """True when the evidence carries the standalone vegetarian token "chay".

    Pass BOTH the original raw ingredient line and the parsed/cleaned name: the
    reviewed policy is the UNION of the two, because the marker can survive in
    either one ("Chân nấm tẩm ướp (Chân dê chay)" keeps it only in raw text).

    Whole-token only. The corpus contains "cháy" (rang cháy cạnh, cơm cháy) and
    "chảy" (bơ lạt đun chảy), which are unrelated; diacritics are preserved
    through normalize_vietnamese_text(), so neither can match.
    """
    joined = " ".join(normalize_vietnamese_text(t) for t in texts if t)
    return bool(CHAY_TOKEN_RE.search(joined))


# ---------------------------------------------------------------------------
# Vegetable-stock animal-identity guard
# ---------------------------------------------------------------------------
# "nước dùng rau củ" is vegetable stock. The catalog's only broth identity is
# 7141 "Nước dùng" (Broth), filed under "Thịt và sản phẩm chế biến", so every
# route hands these rows a meat identity. 8 live rows were scored that way.
#
# Removing the two alias-map keys does NOT fix it, exactly as with the "chay"
# guard above: SUBPHRASE_CATALOG_MATCH re-derives 7141 from the catalog head
# "nước dùng" ("nước dùng rau" -> 0.692, "nước dùng rau củ" -> 0.562, both far
# over the 0.35 threshold), and "nước dùng rau củ quả" already reaches 7141 at
# 0.45 with no alias at all. The neural stage is no safer -- its top-1 for every
# variant is an animal identity (7141 at 0.54-0.58, else 7140 "Nước canh", also
# "Thịt và sản phẩm chế biến"), and the best non-animal candidate it offers is
# 4100 "Súp lơ xanh" (broccoli). There is no valid catalog target at all, so the
# guard is keyed on the RESOLVED catalog entry and applied at every stage.
#
# It is NOT a blanket pre-neural short-circuit, however. A future vegetable-stock
# catalog entry (recorded as a deferred catalog gap) would be non-animal, and
# _blocks_vegetable_stock() would pass it through untouched -- the guard blocks
# animal identities, not the phrase.

# Reviewed stock heads. Adjacency to "rau" is the whole point: the vegetable word
# must IMMEDIATELY follow the stock head, so an animal qualifier in between
# ("nước dùng gà rau củ") breaks the pattern structurally rather than by
# exception list. Bare "rau" is never a trigger -- on its own it resolves to
# 4066 "Rau bí", and "Rau củ nấu nước dùng chay : su su" is "rau" as a separate
# ingredient, which this deliberately does not fire on ("nước dùng" is followed
# by "chay", not "rau").
VEG_STOCK_RE = re.compile(r"\bnước\s+(?:dùng|hầm|luộc)\s+rau\b")

# Reviewed animal-token veto: explicit animal material anywhere in the evidence
# means the line describes an animal broth cooked with vegetables, which 7141
# legitimately covers. The live corpus row "600 ml Nước hầm xương/rau củ/dashi"
# is vetoed by "xương" and "dashi" (normalize_vietnamese_text() turns the slashes
# into spaces, so the tokens stand alone). Scoped to the tokens the audit
# reviewed; not broadened past that evidence.
VEG_STOCK_ANIMAL_VETO_RE = re.compile(
    r"\b(gà|bò|heo|lợn|vịt|ngan|ngỗng|xương|thịt|sườn|giò|gân|cá|tôm|cua|mực|"
    r"nghêu|ngao|hến|sò|ốc|dashi|bào ngư|sá sùng|tủy|đuôi|chân giò)\b"
)

VEGETABLE_STOCK_GUARD_REASON = "VEGETABLE_STOCK_PHRASE_ANIMAL_TARGET"


def is_vegetable_stock_text(*texts: str | None) -> bool:
    """True when the evidence explicitly describes a vegetable stock/broth.

    Pass BOTH the original raw ingredient line and the parsed/cleaned name: the
    policy is the UNION of the two, and here that is load-bearing rather than
    merely defensive. Four live rows store cleaned_name "nước dùng rau" while
    their raw text reads "Nước dùng rau củ ..." -- historical parser drift that
    today's parser no longer reproduces. Reading both keeps the guard correct
    whichever side carries the phrase (the stale-cleaned_name cleanup itself is
    deferred and deliberately not done here).
    """
    joined = " ".join(normalize_vietnamese_text(t) for t in texts if t)
    if not VEG_STOCK_RE.search(joined):
        return False
    return not VEG_STOCK_ANIMAL_VETO_RE.search(joined)


class VietnameseIngredientMatcher:
    """Matches raw ingredient names against canonical Viện Dinh Dưỡng catalog."""

    DEFAULT_MODEL = "bkai-foundation-models/vietnamese-bi-encoder"

    def __init__(
        self,
        catalog_csv_path: str | Path | None = None,
        model_name: str | None = None,
        device: str | None = None,
    ) -> None:
        workspace_root = Path(__file__).resolve().parent.parent
        if catalog_csv_path is None:
            catalog_csv_path = (
                workspace_root
                / "data"
                / "processed"
                / "viendinhduong"
                / "master_ingredients_nutrition.csv"
            )
        self.catalog_path = Path(catalog_csv_path)

        # 1. Device Selection (RTX 4060 GPU with CUDA 12.4 prioritization)
        if device is None:
            self.device = "cuda" if (TORCH_AVAILABLE and torch.cuda.is_available()) else "cpu"
        else:
            self.device = device

        logger.info("Initializing Vietnamese Ingredient Matcher on device: %s", self.device)
        if self.device == "cuda" and TORCH_AVAILABLE:
            gpu_name = torch.cuda.get_device_name(0)
            logger.info("Target GPU: %s", gpu_name)

        # 2. Load Master Ingredients Catalog
        self.catalog: list[dict[str, Any]] = []
        self.catalog_names: list[str] = []
        self.normalized_to_index: dict[str, int] = {}
        self._load_catalog()

        # 3. Known Synonyms / Aliases Dictionary (Rules & Presets)
        self.alias_dict: dict[str, int] = self._build_preset_aliases()

        # 4. Lazy-loaded Transformer Model & Embeddings Cache
        self.model_name = model_name or self.DEFAULT_MODEL
        self.tokenizer = None
        self.model = None
        self.catalog_embeddings: torch.Tensor | None = None

    def _load_catalog(self) -> None:
        """Load 853 master ingredients from processed CSV."""
        if not self.catalog_path.exists():
            raise FileNotFoundError(f"Catalog CSV not found at: {self.catalog_path}")

        with open(self.catalog_path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):
                self.catalog.append(row)
                name_vi = row.get("name_vi", "").strip()
                name_en = row.get("name_en", "").strip()
                norm_vi = normalize_vietnamese_text(name_vi)
                self.catalog_names.append(name_vi)
                if row.get("code") in DEPRECATED_CATALOG_IDENTITIES:
                    continue
                self.normalized_to_index[norm_vi] = idx

                if name_en:
                    norm_en = normalize_vietnamese_text(name_en)
                    if norm_en not in self.normalized_to_index:
                        self.normalized_to_index[norm_en] = idx

        self.catalog_subphrase_items: list[tuple[str, str, int, int]] = []
        for idx, row in enumerate(self.catalog):
            if row.get("code") in DEPRECATED_CATALOG_IDENTITIES:
                continue
            name_vi = row.get("name_vi", "").strip()
            norm_head = normalize_vietnamese_text(name_vi.split(",")[0])
            if norm_head:
                self.catalog_subphrase_items.append((norm_head, f" {norm_head} ", len(norm_head), idx))

        logger.info("Loaded %d master ingredients into catalog index.", len(self.catalog))

    def _build_preset_aliases(self) -> dict[str, int]:
        """Pre-populate common Vietnamese dialectal and regional synonyms from file and presets."""
        code_to_idx = {item["code"]: idx for idx, item in enumerate(self.catalog)
                       if item["code"] not in DEPRECATED_CATALOG_IDENTITIES}
        alias_map: dict[str, int] = {}

        # 1. Load generated alias map if available
        alias_file = self.catalog_path.parent / "ingredient_alias_map.json"
        if alias_file.exists():
            try:
                with open(alias_file, encoding="utf-8") as f:
                    generated_aliases = json.load(f)
                for alias_k, target_code in generated_aliases.items():
                    if target_code in code_to_idx:
                        alias_map[normalize_vietnamese_text(alias_k)] = code_to_idx[target_code]
                logger.info("Loaded %d aliases from ingredient_alias_map.json", len(alias_map))
            except Exception as err:
                logger.warning("Failed to load alias map from %s: %s", alias_file, err)

        # 2. Preset fallback synonyms
        presets = {
            "thịt ba chỉ heo": "thịt ba chỉ",
            "thịt ba chỉ": "thịt ba chỉ",
            "thịt ba rọi": "thịt ba chỉ",
            "ba chỉ heo": "thịt ba chỉ",
            "ba rọi": "thịt ba chỉ",
            "thịt nạc heo": "thịt nạc heo",
            "thịt nạc vai": "thịt nạc vai",
            "nạc vai": "thịt nạc vai",
            "nạc thăn": "thịt nạc thăn",
            "thịt heo": "thịt nạc heo",
            "thịt lợn": "thịt nạc heo",
            "cá lóc đồng": "cá quả",
            "cá lóc": "cá quả",
            "cá chuối": "cá quả",
            "cá quả": "cá quả",
            "tỏi khô": "tỏi",
            "tỏi": "tỏi",
            "ớt sừng": "ớt",
            "ớt hiểm": "ớt",
            "ớt chỉ thiên": "ớt",
            "rau muống": "rau muống",
            "ngò gai": "mùi tàu",
            "ngò rí": "rau mùi",
            "đậu bắp": "đậu bắp",
            "cải thìa": "cải chíp",
            "trứng gà ta": "trứng gà",
            "trứng vịt": "trứng vịt",
            "cà chua bi": "cà chua",
            "hành hoa": "hành lá",
            "nước mắm": "nước mắm",
            "sữa tươi": "sữa tươi không đường",
            "đậu nành": "đậu nành",
            "đậu tương": "đậu nành",
        }

        for alias, target_str in presets.items():
            norm_alias = normalize_vietnamese_text(alias)
            if norm_alias not in alias_map:
                for idx, c_name in enumerate(self.catalog_names):
                    if self.catalog[idx]["code"] in DEPRECATED_CATALOG_IDENTITIES:
                        continue
                    norm_c = normalize_vietnamese_text(c_name)
                    if target_str in norm_c:
                        alias_map[norm_alias] = idx
                        break
        return alias_map

    def _resolve_alias(self, query_norm: str, cleaned_q: str) -> int | None:
        """Look up the preset alias dict, preferring the exact query over the
        prep-stripped cleaned query. Catalog index 0 is a valid match and must
        not be treated as falsy: `a or b` here would silently fall through to
        `cleaned_q` whenever `query_norm` resolved to index 0, letting a
        cleaning-stage side effect (e.g. clean_culinary_query() stripping the
        bare word "tươi" from "sữa tươi" down to "sữa") override a correct
        exact-alias resolution with a different, unrelated one."""
        if query_norm in self.alias_dict:
            return self.alias_dict[query_norm]
        return self.alias_dict.get(cleaned_q)

    def _blocks_ripe_mango(self, catalog_idx: int, green_mango: bool) -> bool:
        """True when a resolution would hand green-mango evidence to ripe 5055.

        Deliberately keyed on the RESOLVED catalog code, not on the alias key or
        the subphrase text, so it covers every route into 5055 -- the bare
        "xoài" alias, any future mango alias, and SUBPHRASE_CATALOG_MATCH
        falling back to the catalog head "xoài chín" -- without removing the
        bare alias, which 6 ambiguous, plausibly-ripe rows still depend on."""
        if not green_mango:
            return False
        return str(self.catalog[catalog_idx].get("code", "")).strip() == RIPE_MANGO_CODE

    def _blocks_vegetarian(self, catalog_idx: int, chay: bool) -> bool:
        """True when a resolution would hand explicit "chay" evidence to an
        animal identity.

        Keyed on the RESOLVED catalog entry, not on the alias key or the
        subphrase text, so it covers every route -- the four reviewed hazardous
        alias-map keys, SUBPHRASE_CATALOG_MATCH re-deriving the same code from
        the catalog head, and the neural stage picking an animal on its own --
        without removing any alias, which would only relabel match_method.

        Non-animal targets pass untouched: 20039/20040 (imitation meat) and 3025
        (tofu) sit in "Hạt, quả giàu đạm...", 20007/4129 in "Rau, quả, củ...",
        and the seasoning analogues in "Gia vị, nước chấm".
        """
        if not chay:
            return False
        item = self.catalog[catalog_idx]
        if str(item.get("category_vi", "")).strip() in ANIMAL_CATEGORIES_VI:
            return True
        return str(item.get("code", "")).strip() in ANIMAL_SUPPLEMENTARY_CODES

    def _blocks_vegetable_stock(self, catalog_idx: int, veg_stock: bool) -> bool:
        """True when a resolution would hand explicit vegetable-stock evidence
        to an animal identity.

        Reuses the vegetarian guard's reviewed animal-target policy verbatim
        (both animal categories plus the reviewed supplementary codes) so the
        two guards cannot drift apart, and is keyed on the RESOLVED catalog
        entry for the same reason: alias, subphrase and neural all reach 7141
        or 7140 independently, so a phrase- or alias-keyed block would leak.

        A non-animal target passes through untouched. That is deliberate and is
        what keeps the deferred vegetable-stock catalog entry viable: once such
        an identity exists, these phrases resolve to it and this guard never
        fires on them.
        """
        if not veg_stock:
            return False
        item = self.catalog[catalog_idx]
        if str(item.get("category_vi", "")).strip() in ANIMAL_CATEGORIES_VI:
            return True
        return str(item.get("code", "")).strip() in ANIMAL_SUPPLEMENTARY_CODES

    @staticmethod
    def _unmatched_result(query: str, reason: str) -> dict[str, Any]:
        """An explicit no-identity verdict.

        confidence is None, not 0.0: an UNMATCHED row asserts "no master link",
        and a numeric confidence would read as a scored rejection this codebase
        no longer has (see tests/test_unmatched_confidence_semantics.py)."""
        return {
            "query": query,
            "matched_item": {},
            "confidence": None,
            "method": "UNMATCHED",
            "guard": reason,
            "top_candidates": [],
        }

    def _init_model(self) -> None:
        """Initialize HuggingFace BERT / Bi-Encoder model and compute embeddings."""
        if self.model is not None:
            return

        from transformers import AutoModel, AutoTokenizer

        logger.info("Loading Transformer model '%s' (fast local cache) ...", self.model_name)
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, local_files_only=True)
            self.model = AutoModel.from_pretrained(self.model_name, local_files_only=True).to(self.device)
        except Exception:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name).to(self.device)

        self.model.eval()

        if self.device == "cuda":
            self.model = self.model.half()  # FP16 precision for RTX 4060 Tensor Cores

        logger.info("Computing dense embeddings for %d master ingredients on %s ...", len(self.catalog), self.device)
        self._compute_catalog_embeddings()

    def _mean_pooling(self, model_output: Any, attention_mask: torch.Tensor) -> torch.Tensor:
        """Mean pooling to extract sentence vector from token embeddings."""
        token_embeddings = model_output[0]
        input_mask_expanded = (
            attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        )
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
            input_mask_expanded.sum(1), min=1e-9
        )

    @no_grad_if_available
    def _compute_catalog_embeddings(self) -> None:
        """Encode all catalog names into normalized embedding matrix on GPU or load from disk cache."""
        cache_dir = self.catalog_path.parent
        cache_file = cache_dir / "catalog_embeddings_bkai.pt"

        if cache_file.exists():
            logger.info("Loading precomputed embeddings from cache: %s", cache_file)
            cached_t = torch.load(cache_file, map_location=self.device)
            if cached_t.shape[0] == len(self.catalog):
                self.catalog_embeddings = cached_t
                logger.info("Loaded embeddings cache. Tensor shape: %s", self.catalog_embeddings.shape)
                return
            logger.info("Cache size mismatch (%s != %s). Recomputing on GPU...", cached_t.shape[0], len(self.catalog))

        texts = [f"{item['name_vi']} ({item['category_vi']})" for item in self.catalog]
        encoded = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=64,
            return_tensors="pt",
        ).to(self.device)

        outputs = self.model(**encoded)
        embeddings = self._mean_pooling(outputs, encoded["attention_mask"])
        self.catalog_embeddings = F.normalize(embeddings, p=2, dim=1)
        logger.info("Catalog embeddings computed on GPU. Tensor shape: %s", self.catalog_embeddings.shape)

        try:
            torch.save(self.catalog_embeddings, cache_file)
            logger.info("Saved catalog embeddings cache to: %s", cache_file)
        except Exception as err:
            logger.warning("Failed to save embeddings cache: %s", err)

    @no_grad_if_available
    def encode_text(self, text: str) -> torch.Tensor:
        """Encode single query text into normalized 768-dim vector."""
        encoded = self.tokenizer(
            [text],
            padding=True,
            truncation=True,
            max_length=64,
            return_tensors="pt",
        ).to(self.device)
        outputs = self.model(**encoded)
        emb = self._mean_pooling(outputs, encoded["attention_mask"])
        return F.normalize(emb, p=2, dim=1)

    def match(
        self,
        raw_ingredient_name: str,
        top_k: int = 3,
        raw_context: str | None = None,
    ) -> dict[str, Any]:
        """Resolve a raw ingredient name to the best master_ingredient.

        1. Stage 1: Exact / Normalized Dictionary Match (Confidence: 1.0)
        2. Stage 2: Preset Synonyms / Aliases Lookup (Confidence: 0.98)
        3. Stage 3: Vietnamese BERT Dense Semantic Retrieval (Confidence: Cosine Sim)

        raw_context is the ORIGINAL recipe line this name was extracted from.
        It is evidence only -- it never becomes a query -- and exists because
        the grammar parser and clean_culinary_query() both strip the ripeness
        evidence the mango guard needs ("Xoài keo 160g" -> "xoài").
        """
        # Stage 1: Exact / Cleaned Name Match
        if is_chicken_fat_text(raw_ingredient_name, raw_context):
            return self._unmatched_result(raw_ingredient_name, CHICKEN_FAT_GUARD_REASON)
        if is_coriander_seed_powder_text(raw_ingredient_name, raw_context):
            return self._unmatched_result(
                raw_ingredient_name, CORIANDER_SEED_POWDER_GUARD_REASON
            )
        query_norm = normalize_vietnamese_text(raw_ingredient_name)
        cleaned_q = clean_culinary_query(raw_ingredient_name)
        green_mango = is_green_mango_text(raw_context or raw_ingredient_name)
        # Union of both evidence sources, per the reviewed "chay" policy.
        chay = is_chay_text(raw_context, raw_ingredient_name)
        # Same union, same reason -- and load-bearing here, because 5 live rows
        # carry the phrase only in raw text (stale cleaned_name drift).
        veg_stock = is_vegetable_stock_text(raw_context, raw_ingredient_name)

        # The exact stages are guarded too. A query that itself contains "chay"
        # can never match an animal by name (only 1038, 12007, 20039 and 20040
        # carry the word, none of them animal) -- but the evidence is the UNION
        # of raw text and parsed name, so a line whose marker survives only in
        # the raw text can arrive here as a bare animal name ("Đùi gà chay 250
        # gr" -> "đùi gà" -> EXACT_CATALOG_MATCH 7088). No live row takes that
        # route today; guarding it costs nothing and closes the hole.
        if query_norm in self.normalized_to_index:
            idx = self.normalized_to_index[query_norm]
            if self._blocks_vegetarian(idx, chay):
                return self._unmatched_result(raw_ingredient_name, VEGETARIAN_GUARD_REASON)
            if self._blocks_vegetable_stock(idx, veg_stock):
                return self._unmatched_result(
                    raw_ingredient_name, VEGETABLE_STOCK_GUARD_REASON
                )
            item = self.catalog[idx]
            return {
                "query": raw_ingredient_name,
                "matched_item": item,
                "confidence": 1.00,
                "method": "EXACT_CATALOG_MATCH",
                "top_candidates": [
                    {"name_vi": item["name_vi"], "category": item["category_vi"], "confidence": 1.00}
                ],
            }

        if cleaned_q in self.normalized_to_index:
            idx = self.normalized_to_index[cleaned_q]
            if self._blocks_vegetarian(idx, chay):
                return self._unmatched_result(raw_ingredient_name, VEGETARIAN_GUARD_REASON)
            if self._blocks_vegetable_stock(idx, veg_stock):
                return self._unmatched_result(
                    raw_ingredient_name, VEGETABLE_STOCK_GUARD_REASON
                )
            item = self.catalog[idx]
            return {
                "query": raw_ingredient_name,
                "matched_item": item,
                "confidence": 0.99,
                "method": "CLEANED_NAME_MATCH",
                "top_candidates": [
                    {"name_vi": item["name_vi"], "category": item["category_vi"], "confidence": 0.99}
                ],
            }

        # Stage 2: Preset Alias Match
        alias_candidate = self._resolve_alias(query_norm, cleaned_q)
        if alias_candidate is not None:
            if self._blocks_ripe_mango(alias_candidate, green_mango):
                return self._unmatched_result(raw_ingredient_name, GREEN_MANGO_GUARD_REASON)
            if self._blocks_vegetarian(alias_candidate, chay):
                return self._unmatched_result(raw_ingredient_name, VEGETARIAN_GUARD_REASON)
            if self._blocks_vegetable_stock(alias_candidate, veg_stock):
                return self._unmatched_result(
                    raw_ingredient_name, VEGETABLE_STOCK_GUARD_REASON
                )
            item = self.catalog[alias_candidate]
            return {
                "query": raw_ingredient_name,
                "matched_item": item,
                "confidence": 0.98,
                "method": "PRESET_ALIAS_MATCH",
                "top_candidates": [
                    {"name_vi": item["name_vi"], "category": item["category_vi"], "confidence": 0.98}
                ],
            }

        # Stage 2.5: Subphrase Catalog Match (e.g. 'rau muống' in 'Rau muống, tươi')
        best_subphrase_idx = None
        best_subphrase_score = 0.0

        if len(cleaned_q) >= 3:
            padded_q = f" {cleaned_q} "
            for norm_c, padded_c, c_len, idx in self.catalog_subphrase_items:
                # Negative filter: don't match if catalog has "không <query>" or "tách <query>"
                if f"không {cleaned_q}" in norm_c or f"tách {cleaned_q}" in norm_c:
                    continue

                # Case A: catalog item is contained inside query (e.g. 'cà chua' in 'cà chua bi đà lạt')
                if c_len >= 3 and padded_c in padded_q:
                    score = c_len / len(cleaned_q)
                    if score > best_subphrase_score:
                        best_subphrase_score = score
                        best_subphrase_idx = idx

                # Case B: query is contained inside catalog item (e.g. 'ba chỉ' in 'thịt ba chỉ (ba rọi) heo')
                elif len(cleaned_q) >= 3 and padded_q in padded_c:
                    score = len(cleaned_q) / c_len
                    if score > best_subphrase_score and score >= 0.35:
                        best_subphrase_score = score
                        best_subphrase_idx = idx

        if best_subphrase_idx is not None and best_subphrase_score >= 0.35:
            if self._blocks_ripe_mango(best_subphrase_idx, green_mango):
                return self._unmatched_result(raw_ingredient_name, GREEN_MANGO_GUARD_REASON)
            if self._blocks_vegetarian(best_subphrase_idx, chay):
                return self._unmatched_result(raw_ingredient_name, VEGETARIAN_GUARD_REASON)
            if self._blocks_vegetable_stock(best_subphrase_idx, veg_stock):
                return self._unmatched_result(
                    raw_ingredient_name, VEGETABLE_STOCK_GUARD_REASON
                )
            item = self.catalog[best_subphrase_idx]
            return {
                "query": raw_ingredient_name,
                "matched_item": item,
                "confidence": 0.95,
                "method": "SUBPHRASE_CATALOG_MATCH",
                "top_candidates": [
                    {"name_vi": item["name_vi"], "category": item["category_vi"], "confidence": 0.95}
                ],
            }

        # Green mango that reached this point has no dictionary identity left to
        # find. Letting it fall through to the neural stage would only produce a
        # different wrong fruit (the bi-encoder returns 5055 or "Quả sấu xanh"),
        # so the guard is terminal rather than merely stage-local.
        if green_mango:
            return self._unmatched_result(raw_ingredient_name, GREEN_MANGO_GUARD_REASON)

        # Stage 3: Neural Semantic Matching (BERT on RTX 4060)
        if not TORCH_AVAILABLE:
            # Fallback: Token overlap score
            best_idx = 0
            best_score = 0.0
            q_words = set(query_norm.split())

            for idx, c_name in enumerate(self.catalog_names):
                if self.catalog[idx]["code"] in DEPRECATED_CATALOG_IDENTITIES:
                    continue
                c_words = set(normalize_vietnamese_text(c_name).split())
                overlap = len(q_words & c_words) / max(1, len(q_words | c_words))
                if overlap > best_score:
                    best_score = overlap
                    best_idx = idx

            if self._blocks_vegetarian(best_idx, chay):
                return self._unmatched_result(raw_ingredient_name, VEGETARIAN_GUARD_REASON)
            if self._blocks_vegetable_stock(best_idx, veg_stock):
                return self._unmatched_result(
                    raw_ingredient_name, VEGETABLE_STOCK_GUARD_REASON
                )
            item = self.catalog[best_idx]
            return {
                "query": raw_ingredient_name,
                "matched_item": item,
                "confidence": round(best_score, 4),
                "method": "TOKEN_OVERLAP_FALLBACK (Run with CUDA environment for Full BERT)",
                "top_candidates": [
                    {"name_vi": item["name_vi"], "category": item["category_vi"], "confidence": round(best_score, 4)}
                ],
            }

        self._init_model()
        query_emb = self.encode_text(query_norm)

        # Compute cosine similarity with all catalog embeddings: shape (1, 853)
        scores = torch.mm(query_emb, self.catalog_embeddings.T).squeeze(0)
        active_indices = [i for i, row in enumerate(self.catalog)
                          if row["code"] not in DEPRECATED_CATALOG_IDENTITIES]
        top_scores, active_top = torch.topk(scores[active_indices], k=min(top_k, len(active_indices)))
        top_indices = torch.tensor(active_indices, device=scores.device)[active_top]

        top_candidates = []
        for score_val, idx_val in zip(top_scores.tolist(), top_indices.tolist()):
            c_item = self.catalog[idx_val]
            top_candidates.append({
                "code": c_item["code"],
                "name_vi": c_item["name_vi"],
                "name_en": c_item["name_en"],
                "category": c_item["category_vi"],
                "energy_kcal": c_item["energy_kcal"],
                "protein_g": c_item["protein_g"],
                "fat_g": c_item["fat_g"],
                "carbs_g": c_item["carbs_g"],
                "confidence": round(score_val, 4),
            })

        best_idx = top_indices[0].item()
        best_score = float(top_scores[0].item())
        best_item = self.catalog[best_idx]

        # Filter the neural RESULT rather than short-circuiting ahead of it, so
        # a genuinely vegan neural pick (20039/20040) still resolves.
        if self._blocks_vegetarian(best_idx, chay):
            return self._unmatched_result(raw_ingredient_name, VEGETARIAN_GUARD_REASON)
        if self._blocks_vegetable_stock(best_idx, veg_stock):
            return self._unmatched_result(
                raw_ingredient_name, VEGETABLE_STOCK_GUARD_REASON
            )

        return {
            "query": raw_ingredient_name,
            "matched_item": best_item,
            "confidence": round(best_score, 4),
            "method": "BERT_SEMANTIC_MATCH",
            "top_candidates": top_candidates,
        }

    @no_grad_if_available
    def encode_batch(self, texts: list[str], batch_size: int = 128) -> torch.Tensor:
        """Encode a batch of query texts into normalized (N, 768) embeddings on GPU."""
        self._init_model()
        if not texts:
            return torch.empty((0, 768), device=self.device)

        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            chunk = texts[i : i + batch_size]
            encoded = self.tokenizer(
                chunk,
                padding=True,
                truncation=True,
                max_length=64,
                return_tensors="pt",
            ).to(self.device)
            outputs = self.model(**encoded)
            emb = self._mean_pooling(outputs, encoded["attention_mask"])
            emb = F.normalize(emb, p=2, dim=1)
            all_embeddings.append(emb)

        return torch.cat(all_embeddings, dim=0)

    def match_batch(
        self,
        raw_ingredient_names: list[str],
        batch_size: int = 128,
        top_k: int = 3,
        raw_contexts: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Resolve a batch of raw ingredient names leveraging GPU batch matrix multiplication.

        raw_contexts, when given, are the ORIGINAL recipe lines positionally
        aligned with raw_ingredient_names; see match() for why the guard needs
        them. A shorter or absent list simply falls back to the name itself.
        """
        if not raw_ingredient_names:
            return []

        contexts = list(raw_contexts or [])
        contexts += [None] * (len(raw_ingredient_names) - len(contexts))

        results: list[dict[str, Any] | None] = [None] * len(raw_ingredient_names)
        unresolved_indices: list[int] = []
        unresolved_queries: list[str] = []
        # Positional "chay" evidence, needed again at the batched neural step.
        chay_flags: list[bool] = [False] * len(raw_ingredient_names)
        # Same, for the vegetable-stock guard.
        veg_stock_flags: list[bool] = [False] * len(raw_ingredient_names)

        # Step 1: Fast in-memory resolution (Exact, Cleaned, Alias, Subphrase)
        for idx, raw_name in enumerate(raw_ingredient_names):
            if is_chicken_fat_text(raw_name, contexts[idx]):
                results[idx] = self._unmatched_result(raw_name, CHICKEN_FAT_GUARD_REASON)
                continue
            if is_coriander_seed_powder_text(raw_name, contexts[idx]):
                results[idx] = self._unmatched_result(
                    raw_name, CORIANDER_SEED_POWDER_GUARD_REASON
                )
                continue
            query_norm = normalize_vietnamese_text(raw_name)
            cleaned_q = clean_culinary_query(raw_name)
            green_mango = is_green_mango_text(contexts[idx] or raw_name)
            chay = is_chay_text(contexts[idx], raw_name)
            chay_flags[idx] = chay
            veg_stock = is_vegetable_stock_text(contexts[idx], raw_name)
            veg_stock_flags[idx] = veg_stock

            # Stage 1: Exact Name Match
            if query_norm in self.normalized_to_index:
                c_idx = self.normalized_to_index[query_norm]
                if self._blocks_vegetarian(c_idx, chay):
                    results[idx] = self._unmatched_result(raw_name, VEGETARIAN_GUARD_REASON)
                    continue
                if self._blocks_vegetable_stock(c_idx, veg_stock):
                    results[idx] = self._unmatched_result(
                        raw_name, VEGETABLE_STOCK_GUARD_REASON
                    )
                    continue
                item = self.catalog[c_idx]
                results[idx] = {
                    "query": raw_name,
                    "matched_item": item,
                    "confidence": 1.00,
                    "method": "EXACT_CATALOG_MATCH",
                    "top_candidates": [{"name_vi": item["name_vi"], "category": item["category_vi"], "confidence": 1.00}],
                }
                continue

            if cleaned_q in self.normalized_to_index:
                c_idx = self.normalized_to_index[cleaned_q]
                if self._blocks_vegetarian(c_idx, chay):
                    results[idx] = self._unmatched_result(raw_name, VEGETARIAN_GUARD_REASON)
                    continue
                if self._blocks_vegetable_stock(c_idx, veg_stock):
                    results[idx] = self._unmatched_result(
                        raw_name, VEGETABLE_STOCK_GUARD_REASON
                    )
                    continue
                item = self.catalog[c_idx]
                results[idx] = {
                    "query": raw_name,
                    "matched_item": item,
                    "confidence": 0.99,
                    "method": "CLEANED_NAME_MATCH",
                    "top_candidates": [{"name_vi": item["name_vi"], "category": item["category_vi"], "confidence": 0.99}],
                }
                continue

            # Stage 2: Preset Alias Match
            alias_candidate = self._resolve_alias(query_norm, cleaned_q)
            if alias_candidate is not None:
                if self._blocks_ripe_mango(alias_candidate, green_mango):
                    results[idx] = self._unmatched_result(raw_name, GREEN_MANGO_GUARD_REASON)
                    continue
                if self._blocks_vegetarian(alias_candidate, chay):
                    results[idx] = self._unmatched_result(raw_name, VEGETARIAN_GUARD_REASON)
                    continue
                if self._blocks_vegetable_stock(alias_candidate, veg_stock):
                    results[idx] = self._unmatched_result(
                        raw_name, VEGETABLE_STOCK_GUARD_REASON
                    )
                    continue
                item = self.catalog[alias_candidate]
                results[idx] = {
                    "query": raw_name,
                    "matched_item": item,
                    "confidence": 0.98,
                    "method": "PRESET_ALIAS_MATCH",
                    "top_candidates": [{"name_vi": item["name_vi"], "category": item["category_vi"], "confidence": 0.98}],
                }
                continue

            # Stage 2.5: Subphrase Match (lightning fast space-padded whole-word match)
            best_sub_idx = None
            best_sub_len = 0
            padded_q = f" {cleaned_q} "
            for norm_c, padded_c, c_len, c_i in self.catalog_subphrase_items:
                if (c_len >= 3 and padded_c in padded_q) or (len(cleaned_q) >= 3 and padded_q in padded_c):
                    if c_len > best_sub_len:
                        best_sub_len = c_len
                        best_sub_idx = c_i

            if best_sub_idx is not None and best_sub_len >= 3:
                if self._blocks_ripe_mango(best_sub_idx, green_mango):
                    results[idx] = self._unmatched_result(raw_name, GREEN_MANGO_GUARD_REASON)
                    continue
                if self._blocks_vegetarian(best_sub_idx, chay):
                    results[idx] = self._unmatched_result(raw_name, VEGETARIAN_GUARD_REASON)
                    continue
                if self._blocks_vegetable_stock(best_sub_idx, veg_stock):
                    results[idx] = self._unmatched_result(
                        raw_name, VEGETABLE_STOCK_GUARD_REASON
                    )
                    continue
                item = self.catalog[best_sub_idx]
                results[idx] = {
                    "query": raw_name,
                    "matched_item": item,
                    "confidence": 0.95,
                    "method": "SUBPHRASE_CATALOG_MATCH",
                    "top_candidates": [{"name_vi": item["name_vi"], "category": item["category_vi"], "confidence": 0.95}],
                }
                continue

            # Terminal guard, mirroring match(): green mango never reaches the
            # neural stage, so it can neither be batched nor scored.
            if green_mango:
                results[idx] = self._unmatched_result(raw_name, GREEN_MANGO_GUARD_REASON)
                continue

            # Requires BERT Neural Retrieval
            unresolved_indices.append(idx)
            unresolved_queries.append(query_norm or raw_name)

        # Step 2: Batched Neural Inference on GPU
        if unresolved_indices:
            if not TORCH_AVAILABLE:
                # Fallback if torch is not installed
                for orig_idx, q_str in zip(unresolved_indices, unresolved_queries):
                    results[orig_idx] = self.match(
                        raw_ingredient_names[orig_idx],
                        top_k=top_k,
                        raw_context=contexts[orig_idx],
                    )
            else:
                self._init_model()
                # Batched encoding of all unresolved queries on GPU
                query_embeddings = self.encode_batch(unresolved_queries, batch_size=batch_size)

                # Batched matrix multiplication: (M, 768) x (768, 853) -> (M, 853)
                batch_scores = torch.mm(query_embeddings, self.catalog_embeddings.T)
                active_indices = [i for i, row in enumerate(self.catalog)
                                  if row["code"] not in DEPRECATED_CATALOG_IDENTITIES]
                top_scores_batch, active_top = torch.topk(
                    batch_scores[:, active_indices], k=min(top_k, len(active_indices)), dim=1
                )
                top_indices_batch = torch.tensor(active_indices, device=batch_scores.device)[active_top]

                top_scores_list = top_scores_batch.tolist()
                top_indices_list = top_indices_batch.tolist()

                for row_idx, orig_idx in enumerate(unresolved_indices):
                    q_raw = raw_ingredient_names[orig_idx]
                    q_raw_lower = q_raw.lower()
                    best_c_idx = top_indices_list[row_idx][0]
                    best_conf = float(top_scores_list[row_idx][0])
                    best_item = self.catalog[best_c_idx]

                    # Anti-mismatch heuristic: If query does NOT mention 'khô', but candidate has 'khô',
                    # prefer a fresh candidate in the top_k if its score is close
                    if not re.search(r"\b(khô|sấy|phơi)\b", q_raw_lower):
                        if re.search(r"\b(khô|sấy|phơi)\b", best_item.get("name_vi", "").lower()):
                            for s_val, c_i in zip(top_scores_list[row_idx][1:], top_indices_list[row_idx][1:]):
                                alt_item = self.catalog[c_i]
                                if not re.search(r"\b(khô|sấy|phơi)\b", alt_item.get("name_vi", "").lower()):
                                    if float(s_val) >= best_conf - 0.15:
                                        best_c_idx = c_i
                                        best_conf = float(s_val)
                                        best_item = alt_item
                                        break

                    # Mirrors match(): filter the neural RESULT (after the khô
                    # preference has settled on a final candidate) rather than
                    # short-circuiting ahead of the neural stage, so a genuinely
                    # vegan pick such as 20039/20040 still resolves.
                    if self._blocks_vegetarian(best_c_idx, chay_flags[orig_idx]):
                        results[orig_idx] = self._unmatched_result(
                            q_raw, VEGETARIAN_GUARD_REASON
                        )
                        continue
                    if self._blocks_vegetable_stock(
                        best_c_idx, veg_stock_flags[orig_idx]
                    ):
                        results[orig_idx] = self._unmatched_result(
                            q_raw, VEGETABLE_STOCK_GUARD_REASON
                        )
                        continue

                    candidates = []
                    for s_val, c_i in zip(top_scores_list[row_idx], top_indices_list[row_idx]):
                        ci_item = self.catalog[c_i]
                        candidates.append({
                            "code": ci_item["code"],
                            "name_vi": ci_item["name_vi"],
                            "name_en": ci_item["name_en"],
                            "category": ci_item["category_vi"],
                            "energy_kcal": ci_item["energy_kcal"],
                            "protein_g": ci_item["protein_g"],
                            "fat_g": ci_item["fat_g"],
                            "carbs_g": ci_item["carbs_g"],
                            "confidence": round(s_val, 4),
                        })

                    results[orig_idx] = {
                        "query": q_raw,
                        "matched_item": best_item,
                        "confidence": round(best_conf, 4),
                        "method": "BERT_BATCH_GPU_MATCH",
                        "top_candidates": candidates,
                    }
        return results  # type: ignore[return-value]
