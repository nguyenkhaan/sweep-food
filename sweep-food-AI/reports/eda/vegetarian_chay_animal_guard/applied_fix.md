# Vegetarian (`chay`) animal-identity guard — applied fix

Branch: `fix/matching-data-followups`
Guard reason: `VEGETARIAN_PHRASE_ANIMAL_TARGET`
Machine-readable companion: [`applied_fix.json`](applied_fix.json)

## Root cause

Explicit Vietnamese vegetarian analogue phrases were resolving to real animal
identities, so imitation products were being scored with the nutrition of the
meat they imitate — `Xúc xích chay 100g` was counted as 535 kcal of pork
sausage, `Đùi gà chay 250 gr` as 250 g of chicken thigh.

Two independent mechanisms produced this, which is why an alias-only fix could
not work:

1. **Harvested alias map.** `ingredient_alias_map.json` is corpus-harvested,
   not curated, and carries `đùi gà chay→7088`, `xúc xích chay→7077`,
   `nem chua chay→7073`, `thịt cua chay→8069` as literal keys. The learned-alias
   writer at `crawler/post_processing.py:364` promotes any resolution at
   `conf >= 0.88`, which both `PRESET_ALIAS_MATCH` (0.98) and
   `SUBPHRASE_CATALOG_MATCH` (0.95) clear.
2. **Re-derivation.** With those aliases removed, `SUBPHRASE_CATALOG_MATCH`
   reaches the identical animal code from the catalog head — `đùi gà chay`→7088
   at 0.55, `thịt cua chay`→8069 at 0.62, both over the 0.35 threshold — and the
   neural stage reaches animal identities with no alias involved at all
   (`tôm chay`→8056, `thịt heo chay`→7065, `bò chay khô`→7076, `vịt chay`→11021).

`REMOVE_ALIAS` would therefore have changed the `match_method` label and nothing
else. The guard sits at the resolution layer instead, keyed on the **resolved
catalog entry**, so it covers every route.

## Policy decision

> When ingredient evidence — the union of NFC-normalized `raw_text` and
> `cleaned_name` — contains the standalone token `chay`, and the resolved
> catalog target is an animal identity, block terminally and return `UNMATCHED`.

**Animal identity** is decided by catalog metadata, never by animal-name
substrings:

| Test | Entries |
|---|---|
| `category_vi ∈ {Thịt và sản phẩm chế biến, Thủy sản và sản phẩm chế biến}` | 199 |
| `code ∈` reviewed supplementary set (11015–11023 canned meat/fish, 6003/6004 pork lard) | 11 |

The supplementary codes are animal identities filed under *non-animal*
categories, each verified individually by `name_en` rather than inferred from
code proximity (AGENTS.md §2). They add 0 live rows — they are forward
protection for routes the neural stage demonstrably reaches.

Why not substrings: **20007 `Nấm đùi gà` is king oyster mushroom**, and
`nấm đùi gà chay` resolves to it at 0.67. A rule keyed on `gà` would wrongly
block it; the category test exempts it with no special case. Symmetrically, the
live catalog contains **zero** vegan or imitation entries filed under the two
animal categories, so the test is exact rather than approximate.

**No repoint target exists.** The catalog holds only two imitation-meat
identities (20039 `Thịt chay`, 20040 `Chả lụa chay`), and neither is a
drumstick, a sausage, fermented pork, crab meat or a broth. Pointing these rows
at 20039 would assert 50 g protein/100 g for a product nobody measured
(AGENTS.md §5, §7). `UNMATCHED` is the correct verdict.

## Matcher changes — `nlp/entity_matcher.py`

Added module-level `CHAY_TOKEN_RE`, `ANIMAL_CATEGORIES_VI`,
`ANIMAL_SUPPLEMENTARY_CODES`, `VEGETARIAN_GUARD_REASON`, `is_chay_text()`, and
the method `VietnameseIngredientMatcher._blocks_vegetarian(catalog_idx, chay)`.

Applied at every resolution stage, in **both** `match()` and `match_batch()`:

| Stage | `match()` | `match_batch()` |
|---|:--:|:--:|
| `EXACT_CATALOG_MATCH` | ✅ | ✅ |
| `CLEANED_NAME_MATCH` | ✅ | ✅ |
| `PRESET_ALIAS_MATCH` | ✅ | ✅ |
| `SUBPHRASE_CATALOG_MATCH` | ✅ | ✅ |
| neural result (`BERT_SEMANTIC_MATCH` / `BERT_BATCH_GPU_MATCH`) | ✅ | ✅ |
| `TOKEN_OVERLAP_FALLBACK` | ✅ | n/a (delegates to `match()`) |

Two design points differ from the green-mango precedent and are deliberate:

- **Not a blanket pre-neural return.** Green mango has no valid catalog target;
  `chay` does, and the bi-encoder finds it (`gà chay`→20040,
  `sườn ống chay`→20039, `giò sống chay`→20040). The neural **result** is
  filtered instead, after the `khô` preference has settled, so correct vegan
  resolutions survive.
- **The exact stages are guarded too.** A query containing `chay` can never
  match an animal by name, but the evidence is the *union* of raw text and
  parsed name, so a line whose marker survives only in the raw text can arrive
  as a bare animal name (`Đùi gà chay 250 gr` → `đùi gà` →
  `EXACT_CATALOG_MATCH` 7088). No live row takes that route; guarding it closes
  the hole at no cost.

Because the guard prevents the bad resolution from ever being emitted, it also
prevents it from being re-learned as an alias — it closes the feedback loop as
well as the live errors.

## Aliases and data deliberately NOT changed

The four hazardous alias-map keys remain in place pointing at their animal
codes. The guard makes them **inert**, which keeps this fix's blast-radius
measurement clean; removing or repointing them is a separate reviewed decision
(AGENTS.md §6, §18). A regression test pins both facts.

Also unchanged, and recorded rather than fixed:

- **Seasoning analogues** — 213 `chay` rows in `Gia vị, nước chấm`
  (`nước mắm chay`→13017, `dầu hào chay`→13027, `hạt nêm chay`→13026,
  `sa tế chay`→13054). Exempt *structurally*, not by special case. This is a
  scope decision, **not** a claim the mappings are semantically perfect — 13017
  is literally fish sauce. They are teaspoon-dose condiments whose profile is
  close to their animal counterpart, the catalog has no vegetarian condiment
  identity to move them to, and blocking them would destroy real coverage for no
  semantic gain.
- 20002 `Nước lọc` as a replacement for `nước dùng chay`.
- The 61 rows already correct on 20039/20040.
- Residual rows whose vegetarian intent is stated only at recipe level with no
  ingredient-level marker: `Chà bông chay từ sườn non` (line reads
  `6 miếng sườn non` → 7053) and `Nước dùng rau củ 1,6 lít` → 7141.
- Dairy/egg policy: no `chay` row reaches those categories.
- A **pre-existing** `match()` / `match_batch()` divergence unrelated to this
  guard: `match()` gates the subphrase stage on a 0.35 length ratio while
  `match_batch()` gates only on a 3-character catalog head, so `vịt cháy tỏi`
  lands on 11021 in one and 4103 in the other. Verified against a stashed tree
  to predate this change; pinned by a test so it stays visible.

## Rows changed — 11 ingredient rows, 11 recipes

All transition to the AGENTS.md §4 contract: blank code/name, `UNMATCHED`,
null confidence, null nutrition. `raw_text`, `cleaned_name`, quantity/unit,
preparation note and `estimated_weight_g` are preserved verbatim.

| id | raw_text | before | weight |
|---|---|---|---:|
| `f2c392cf` | Đùi gà chay 250 gr | 7088 Đùi gà | 250 g |
| `dcc433c7` | Đùi gà chay 300 gr | 7088 Đùi gà | 300 g |
| `fb37da49` | Xúc xích chay 100g | 7077 Xúc xích | 100 g |
| `256d7443` | Nem chua chay 150g | 7073 Nem chua | 150 g |
| `7c4d60bc` | Thịt cua chay: 100g | 8069 Thịt cua | 100 g |
| `1d643050` | Nước dùng chay: 250ml | 7141 Nước dùng | 250 g |
| `22d71f4f` | Nước dùng chay 2 lít | 7141 Nước dùng | 2000 g |
| `318fddc7` | Nước dùng chay 1.5 lít | 7141 Nước dùng | 1500 g |
| `bb9a520c` | Nước dùng chay 2,5 lít (Nấu từ củ sắn…) | 7141 Nước dùng | 2500 g |
| `2175a41f` | Nước dùng chay: 1L | 7141 Nước dùng | 1000 g |
| `1e0d1e8b` | Nước dùng chay : 1,2 lít | 7141 Nước dùng | 1200 g |

`7141 Nước dùng` was not in the originally reported error set — it is a finding
from this work. It is a *broth* analogue rather than a seasoning: it is
categorized `Thịt và sản phẩm chế biến` and is a dish component, not a
condiment.

### Nutrition removed

| | value |
|---|---:|
| calories | 1,663.5 kcal |
| protein | 174.7 g |
| fat | 90.3 g |
| carbs | 16.7 g |

Split: 1,579.0 kcal from the five meat/seafood rows, 84.5 kcal from the six
broth rows (7141 is nutritionally near-empty at 1 kcal/100 g with blank macros).
Missing nutrition is written as null, never 0.0; `match_confidence` is null, not
the 0.0 rejection sentinel.

### Recipe rollups — 11 recipes, CSV and JSON both

| recipe | kcal before → after |
|---|---|
| Bánh khọt chay | 2322.0 → 1787.0 |
| Súp hột lựu chay | 1965.7 → 1955.7 |
| Lẩu đậu tương | 1076.3 → 1064.3 |
| Miến xào chay | 881.6 → 778.6 |
| Gà kho tàu chay | 857.7 → 446.7 |
| Mì cay chay | 757.0 → 742.0 |
| Mì vịt tiềm chay | 733.0 → 708.0 |
| Canh gà hầm sả chay | 728.7 → 386.2 |
| Lẩu khoai mỡ | 549.3 → 529.3 |
| Phở sắn xào thập cẩm | 528.9 → 526.4 |
| Nem chua mì căn | 398.3 → 210.8 |

Deltas sum to exactly 1,663.5 kcal. `nutrition_status` in `recipes.json`:
11 recipes gained one missing-nutrition row; exactly 1 crossed a label
threshold (`PARTIAL → INCOMPLETE`).

## Canonical propagation

Regenerated per AGENTS.md §11 (`canonicalize_recipes.py` →
`export_canonical_json.py` → `canonicalize_recipes.py --check`).

| Check | Result |
|---|---|
| `canonical_recipe_ingredients.csv` rows | 62,023 → 62,023, **11 changed, all targets** |
| `canonical_recipes.csv` rows | 5,479 → 5,479 |
| Canonical ID drift | **0** |
| Representative flips | **0** |
| Mapping rows changed | 11, quality metrics only |
| `--check` validation | passed — unique selections, mapping coverage, references, singleton retention, unchanged source values, input-order-independent bytes, protected hashes |

All 11 affected recipes sit in `duplicate_group_size = 1`, `candidate_rank = 1`,
so no representative could flip. Changed mapping fields are confined to
`unmatched_count`, `valid_master_match_count`, `valid_match_rate`,
`negative_unmatched_rate`, `nutrition_anomaly_count`,
`negative_nutrition_anomaly_rate`, `candidate_score`, `selection_score`.

## Validation

- `tests/test_vegetarian_chay_animal_guard.py` — 88 passed.
- Matcher/integrity regression groups (green-mango guard, alias resolution,
  alias integrity, matching integrity, UNMATCHED confidence and nutrition
  semantics, missing nutrition) — 224 passed.
- Remediation script is fail-closed (drift in `raw_text`, `cleaned_name`,
  code, name, method or confidence aborts before any write; the blocked set is
  recomputed from live data and cross-checked against the pinned ids), dry-run
  by default, and idempotent — a second `--apply` reports
  `0 pending, 11 already applied` and writes nothing.
- Blast radius verified against `HEAD`: exactly 11 ingredient rows and 11
  recipe rows differ; no unrelated row moved.
