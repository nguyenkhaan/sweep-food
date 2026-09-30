# Vegetable-stock animal-identity guard — applied fix

**Branch:** `fix/matching-data-followups`
**Guard reason:** `VEGETABLE_STOCK_PHRASE_ANIMAL_TARGET`
**Remediation script:** `scripts/eda/apply_vegetable_stock_animal_guard_safe_fix.py`
**Tests:** `tests/test_vegetable_stock_animal_guard.py` (76 tests)

---

## Root cause

`Nước dùng rau củ 1,6 lít` is vegetable stock. The live catalog's only broth
identity is **7141 `Nước dùng`** (Broth), filed under **`Thịt và sản phẩm chế
biến`** — meat. Eight live rows were resolving there at
`PRESET_ALIAS_MATCH` / `0.98` and being scored as meat broth.

This is the residual case the vegetarian (`chay`) guard explicitly deferred:
these rows carry no ingredient-level `chay` marker, so `is_chay_text()` is
inert on them and they survived that fix.

**Removing the two alias-map keys would not have fixed it.** Measured against
the live catalog:

| route | result |
|---|---|
| `SUBPHRASE_CATALOG_MATCH` re-derives 7141 from catalog head `nước dùng` | `nước dùng rau` → **0.692**, `nước dùng rau củ` → **0.562** (threshold 0.35) |
| `nước dùng rau củ quả` — no alias exists at all | already reaches 7141 at **0.45** |
| neural top-1, every variant | **7141** (0.54–0.58) or **7140 `Nước canh`** — also meat |
| best non-animal neural candidate | 4100 `Súp lơ xanh` — broccoli |

There is no valid catalog target, so `UNMATCHED` is the correct verdict
(AGENTS.md §2, §5). The guard is therefore keyed on the **resolved catalog
identity** and applied at **every** stage that can emit one.

---

## Policy decision

> If ingredient evidence — the NFC-normalized union of `raw_text` and
> `cleaned_name` — explicitly describes a vegetable stock/broth, **and** the
> resolved catalog target is an animal identity, block terminally to
> `UNMATCHED`.

Rejected alternatives:

| option | why rejected |
|---|---|
| alias removal | ineffective — subphrase and neural re-derive 7141 (above) |
| row-level clear only | not reproducible; a re-match would rewrite the rows |
| repoint to **20002** `Nước lọc` | vegetable stock is not drinking water, and 20002 carries explicit `0.0` macros — repointing converts *missing* nutrition into asserted *real* zeros (AGENTS.md §4) |
| new vegetable-stock catalog entry | correct long-term fix; **recorded as a deferred catalog gap**, needs real Viện Dinh Dưỡng nutrition plus catalog + embeddings regeneration |

---

## Code changes — `nlp/entity_matcher.py`

**Detector** (module level):

```python
VEG_STOCK_RE = re.compile(r"\bnước\s+(?:dùng|hầm|luộc)\s+rau\b")

VEG_STOCK_ANIMAL_VETO_RE = re.compile(
    r"\b(gà|bò|heo|lợn|vịt|ngan|ngỗng|xương|thịt|sườn|giò|gân|cá|tôm|cua|mực|"
    r"nghêu|ngao|hến|sò|ốc|dashi|bào ngư|sá sùng|tủy|đuôi|chân giò)\b"
)

VEGETABLE_STOCK_GUARD_REASON = "VEGETABLE_STOCK_PHRASE_ANIMAL_TARGET"


def is_vegetable_stock_text(*texts: str | None) -> bool:
    joined = " ".join(normalize_vietnamese_text(t) for t in texts if t)
    if not VEG_STOCK_RE.search(joined):
        return False
    return not VEG_STOCK_ANIMAL_VETO_RE.search(joined)
```

**Predicate** (`VietnameseIngredientMatcher._blocks_vegetable_stock`) — reuses
the vegetarian guard's reviewed animal policy verbatim so the two cannot drift
apart:

```python
if not veg_stock:
    return False
item = self.catalog[catalog_idx]
if str(item.get("category_vi", "")).strip() in ANIMAL_CATEGORIES_VI:
    return True
return str(item.get("code", "")).strip() in ANIMAL_SUPPLEMENTARY_CODES
```

### Why this is narrow

Two independent mechanisms, neither a broad substring rule:

1. **Adjacency.** `rau` must *immediately* follow the stock head, so an animal
   qualifier in between breaks the pattern **structurally**, not by exception
   list: `nước dùng gà rau củ` and `nước dùng bò với rau` never match.
   Bare `rau` is never a trigger — alone it resolves to 4066 `Rau bí`.
2. **Animal veto.** Explicit animal material anywhere means the line describes
   an animal broth cooked with vegetables, which 7141 legitimately covers.

### Stage coverage — 11 call sites

| method | sites |
|---|---|
| `match()` | EXACT, CLEANED, `PRESET_ALIAS_MATCH`, `SUBPHRASE_CATALOG_MATCH`, `TOKEN_OVERLAP_FALLBACK`, `BERT_SEMANTIC_MATCH` — **6** |
| `match_batch()` | EXACT, CLEANED, `PRESET_ALIAS_MATCH`, `SUBPHRASE_CATALOG_MATCH`, `BERT_BATCH_GPU_MATCH` — **5** |

Because each site returns `UNMATCHED` immediately, no later stage can
re-derive another animal broth — the guard is terminal in effect.

**The guard is not a blanket pre-neural short-circuit.** A non-animal target
passes through untouched, which is what keeps the deferred catalog entry
viable. Demonstrated live: `nước luộc rau` fires the detector yet resolves to
**4135002 `Rau cải chíp luộc`**, a vegetable.

---

## Rows changed — exactly 8

All were `7141 / Nước dùng` via `PRESET_ALIAS_MATCH` / `0.98` → now
`UNMATCHED`, null confidence, null nutrition.

| row | recipe | raw_text | cleaned_name | weight | kcal removed |
|---|---|---|---|---|---|
| `f9e2f60c` | Mì Nấm Củ Hủ Dừa Táo Đỏ | `Nước dùng rau củ 1,6 lít` | `nước dùng rau` | 1600 g | 16.0 |
| `e07fe326` | Súp Rau Chùm Ngây Đậu Hủ Non | `Nước dùng rau củ 1,2 lít` | `nước dùng rau` | 1200 g | 12.0 |
| `e3b10cc6` | Sườn chay om nấm đùi gà | `Nước dùng rau củ 1 lít` | `nước dùng rau` | 1000 g | 10.0 |
| `16c22e9a` | Súp nấm ngưu bàng | `Nước dùng rau củ 1,5 lít` | `nước dùng rau` | 1500 g | 15.0 |
| `81739420` | Súp tỏi Ý và Tây Ban Nha | `Nước dùng rau 950 ml` | `nước dùng rau` | 950 g | 9.5 |
| `22b6999f` | Súp gấc nấm mỡ | `Nước dùng rau củ: 1,2 L` | `nước dùng rau củ` | 1200 g | 12.0 |
| `ba987c1c` | Súp đậu non trứng rong biển | `Nước dùng rau củ: 1 lít` | `nước dùng rau củ` | 1000 g | 10.0 |
| `c9f4c65d` | Súp bát trân chay | `Nước dùng rau củ: 1,5L` | `nước dùng rau củ` | 1500 g | 15.0 |

Preserved on every row (AGENTS.md §4): `raw_text`, `cleaned_name`,
`required_quantity`, `unit_vi`, `unit`, `preparation_note`,
`estimated_weight_g`.

### Nutrition

**−99.5 kcal total. Protein / fat / carbs impact exactly 0.0** — 7141 is
nutritionally near-empty (1 kcal/100 g) and its macros are already blank in the
live catalog, so these rows never carried any. Cleared values are **null**,
never `0.0`.

### Recipe rollups — 8 recipes

| recipe | before | after |
|---|---|---|
| Mì Nấm Củ Hủ Dừa Táo Đỏ | 2187.4 | 2171.4 |
| Súp gấc nấm mỡ | 833.2 | 821.2 |
| Súp Rau Chùm Ngây Đậu Hủ Non | 794.6 | 782.6 |
| Súp nấm ngưu bàng | 892.6 | 877.6 |
| Sườn chay om nấm đùi gà | 1631.3 | 1621.3 |
| Súp bát trân chay | 1687.6 | 1672.6 |
| Súp tỏi Ý và Tây Ban Nha | 3854.4 | 3844.9 |
| Súp đậu non trứng rong biển | 514.2 | 504.2 |

---

## Blast radius — verified against all 63,943 rows

| set | count | status |
|---|---|---|
| ingredient rows changed | **8** | exactly the reviewed set |
| recipe rows changed | **8** | only `total_calories` |
| rows on 7141 | 149 → **141** | 141 animal broths keep their identity |
| forward-protection row `470f6222` | 1 | already UNMATCHED, **byte-identical** |
| `nước dùng chay` rows | 6 | unchanged, still owned by the chay guard |
| rows on 20002 | 358 | unchanged |
| dashi rows | 14 | unchanged |
| chay rows corpus-wide | 376 | unchanged |

CSV/JSON parity verified on all 8 rows in both
`recipe_ingredients.{csv,json}` and `recipes.{csv,json}`.

### False-positive safeguards

Two of the reviewed probes occur **live** in the corpus and are correctly
declined:

| live row | why safe |
|---|---|
| `600 ml Nước hầm xương/rau củ/dashi` | animal veto (`xương`, `dashi`) — `normalize_vietnamese_text()` turns the slashes into spaces so the tokens stand alone |
| `Rau củ nấu nước dùng chay : su su` | adjacency — `nước dùng` is followed by `chay`, not `rau`; this is `rau` as a *separate ingredient* |

Synthetic probes `nước dùng gà rau củ`, `nước dùng bò với rau`,
`nước dùng rau củ và gà`, `nước hầm xương rau củ` all keep their identity.

---

## Canonical propagation

Regenerated via `scripts/canonicalize_recipes.py` →
`scripts/export_canonical_json.py` → `canonicalize_recipes.py --check`
(AGENTS.md §11). Check result:

> `validation: passed: unique selections, mapping coverage, references,
> singleton retention, unchanged source values, input-order-independent bytes,
> protected hashes`

| metric | result |
|---|---|
| canonical ingredient rows | 62,023 (unchanged) |
| canonical recipes | 5,479 (unchanged) |
| **canonical ID drift** | **0** |
| **representative drift** (`canonical_recipe_id`) | **0** |
| `canonical_group_id` drift | 0 |
| `canonical_dish_name` drift | 0 |
| canonical ingredient rows changed | 8 |
| canonical recipe rows changed | 8 (`total_calories`, `selection_score`) |
| mapping rows changed | 8 |
| deterministic regeneration | **byte-identical** on re-run |

Mapping columns that moved, on those 8 rows only: `unmatched_count` (+1),
`valid_master_match_count` (−1), `valid_match_rate`,
`negative_unmatched_rate`, `selection_score`, `candidate_score`, and for
`b049b052` `negative_recipe_nutrition_anomalies` (−3 → −4). All are the
expected arithmetic consequence of one row becoming UNMATCHED:
`recipe_anomalies` counts macros where any ingredient is null, and
`b049b052`'s row already had null protein/fat/carbs (3) before its calories
also became null (4). The other seven were already at 4.

`recipe_canonicalization_summary.json` changed only its `protected_sha256` /
`output_sha256` entries; every count is unchanged.

---

## Validation

| check | result |
|---|---|
| new tests `tests/test_vegetable_stock_animal_guard.py` | **76 passed** |
| related guard/integrity suites | 286 passed |
| full practical suite | **1408 passed, 0 failed** |
| `tests/test_api_endpoints.py`, `tests/test_smart_input.py` | pre-existing `ModuleNotFoundError: fastapi` (AGENTS.md §15) |
| `git diff --check` | clean |
| script idempotency | re-run reports 0 pending, writes nothing |

No prior test or script needed updating: nothing pinned these rows or the 7141
population as matched.

---

## Out of scope — recorded, deliberately unchanged (AGENTS.md §18)

* **The two alias-map keys** `nước dùng rau` / `nước dùng rau củ` → 7141. Left
  in the map and made inert by the guard, exactly as the chay fix left its four
  hazardous keys. Removal would not help and would only relabel `match_method`.
* **Vegetable-stock catalog gap (deferred task).** Adding a real vegetable-stock
  identity under a non-animal category is the correct long-term fix; it would
  let these 8 rows, the 6 `nước dùng chay` rows and `Nước hầm rau` resolve
  instead of being guarded. Needs real Viện Dinh Dưỡng nutrition plus catalog
  and embeddings-cache regeneration.
  `test_catalog_still_has_no_vegetable_stock_identity` fails when it is added.
* **Stale `cleaned_name` (deferred task).** Four rows store `nước dùng rau`
  while their raw text reads `Nước dùng rau củ`; today's parser preserves the
  `củ`. Not rewritten here — the guard reads raw_text too, so it is correct
  regardless. A global stale-`cleaned_name` audit is separate.
* 20002 as a repoint target; the 7141 catalog definition; dashi mappings;
  seasoning analogues; the `nước dùng chay` policy and the chay guard itself.
* `rau trai` → 8054 `Trai, nước ngọt` (freshwater mussel) — likely mis-match,
  unrelated.
* Garnish-list collapse (`ăn kèm bánh phồng tôm rau xà lách trang trí` → 8055).

## Not done

Nothing was committed or pushed.
