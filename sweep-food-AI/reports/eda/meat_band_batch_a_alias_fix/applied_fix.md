# Applied fix: Batch A of the 70xx meat-band audit — fifteen PRESET_ALIAS repoints

Branch `fix/matching-data-followups`. Applied by `scripts/eda/apply_meat_band_batch_a_alias_safe_fix.py --apply`, tests in `tests/test_meat_band_batch_a_alias_safe_fix.py`. Machine-readable companion: `applied_fix.json`.

This is the **high-confidence exact-target subset** of Batch A only. Everything else the audit recorded is listed in §9 and is deliberately untouched.

## Problem

Fifteen preset aliases in `data/processed/viendinhduong/ingredient_alias_map.json` resolved to a catalog identity of the wrong species, the wrong animal part, or — twice — the wrong biological kingdom. Each has a single unambiguous correct identity already present in the live catalog, so every decision here is `SAFE_REPOINT`.

126 processed ingredient rows reach these keys. 111 of them carried a wrong master identity; the other 15 were already held on the correct code by an unrelated reviewed cure (§4).

Recipe context corroborates every repoint independently of the alias text — e.g. the `gân bò` rows sit in *Gân bò hầm hạt sen* (braised beef **tendon**), the `vịt` rows in *Vịt nướng me cay* and *Vịt nấu măng tươi* (duck **meat** dishes, not liver), the `chim bồ câu` rows in *Bồ câu rôti* and *Bồ câu hầm ngải cứu*, the single `nấm hủ đùi gà` row in *Sườn chay om nấm đùi gà* (a **vegan** dish), and the single `phô mai đầu bò` row in *Trà sữa hạt é sương sâm* (a milk tea).

## 1. Alias decision (15): `SAFE_REPOINT`

| Alias | From | To | Why the old target is wrong |
|---|---|---|---|
| `thịt thịt nạc thăn` | 7070 `Giò thủ lợn` | **7085** `Thịt nạc thăn heo (lợn)` | Doubled-`thịt` spelling of the pork tenderloin term the sibling `thịt nạc thăn` already maps to 7085. 7070 is pressed pork head cheese — a different product. |
| `chả lụa` | 7068 `Giò bò` | **7069** `Giò lụa` | `chả lụa` is the southern name for `giò lụa` — the same steamed **pork** sausage. 7068 is the **beef** version. |
| `chả lụa cắt hạt lựu` | 7068 `Giò bò` | **7069** `Giò lụa` | Same identity, diced. |
| `da heo` | 7064 `Chả lợn` | **7031** `Bì lợn` | `da heo` is pork **skin**. 7064 is fried pork paste: same animal, different part and preparation. |
| `da heo tươi` | 7064 `Chả lợn` | **7031** `Bì lợn` | Same, with a `tươi` qualifier. |
| `phile bò` | 7001 `Thịt bê mỡ` | **7005** `Thịt thăn bò` | Beef fillet. 7001 is **veal**, fatty — different animal maturity and a fat-bearing cut. |
| `bò phile` | 7001 `Thịt bê mỡ` | **7005** `Thịt thăn bò` | Word-order variant of the same term. |
| `bò thăn` | 7001 `Thịt bê mỡ` | **7005** `Thịt thăn bò` | Beef loin; 7005 is exactly that, and the sibling `thăn bò` already points there. |
| `gân bò` | 7001 `Thịt bê mỡ` | **7043** `Gân chân bò` | Beef **tendon**. 7043 is the catalog's only tendon identity; 7001 is muscle meat. |
| `bò hoa` | 7001 `Thịt bê mỡ` | **7094** `Thịt bắp bò` | The `bắp bò hoa` flower-shank cut. **Latent** — see §4. |
| `chim bồ câu` | 7012 `Thịt gà rừng` | **7007** `Thịt bồ câu, cả con non (ra ràng)` | Pigeon. 7012 is wild **chicken**: different species. |
| `vịt` | 7042 `Gan vịt` | **7028** `Thịt vịt` | Duck **meat**. 7042 is duck **liver** — an organ whose nutrition is nothing like carcass meat. |
| `phô mai đầu bò` | 7035 `Đầu bò` | **10009** `Phô mai (phó mát)` | A colloquial name for a processed cheese wedge, resolved on its `đầu bò` substring to literal **beef head**. |
| `đùi gà tây` | 7088 `Đùi gà` | **7014** `Thịt gà tây` | **Turkey** leg. 7088 is chicken thigh; the catalog has no turkey-leg cut, so 7014 (turkey, average meat) is the correct species identity. |
| `nấm hủ đùi gà` | 7088 `Đùi gà` | **20007** `Nấm đùi gà` | King oyster **mushroom** with a `hủ`/jar typo. 7088 put a vegetable on poultry meat — a kingdom error. |

**Why repoint rather than remove.** Every one of these keys is a real Vietnamese ingredient term users write, and every one needs an identity. Removal would drop the rows into SUBPHRASE/neural matching — which is exactly how `phô mai đầu bò` reached a beef-head entry in the first place. Repointing keeps `PRESET_ALIAS_MATCH` / `0.98`, the same method and confidence the rows already carried, so **no row's match method or confidence changes in this fix** (§3).

**`đùi gà tây` — species over cut.** The catalog carries no turkey-leg entry. The choice is turkey meat or chicken thigh; the only semantically defensible one is turkey. Recorded explicitly because it is the one repoint in this batch that trades cut granularity for species correctness (AGENTS.md §5).

### Exact alias diff

15 values changed, **0 keys added, 0 keys removed**, map size 4676 before and after:

```
-  "thịt thịt nạc thăn": "7070"    +  "thịt thịt nạc thăn": "7085"
-  "chả lụa": "7068"               +  "chả lụa": "7069"
-  "chả lụa cắt hạt lựu": "7068"   +  "chả lụa cắt hạt lựu": "7069"
-  "da heo": "7064"                +  "da heo": "7031"
-  "da heo tươi": "7064"           +  "da heo tươi": "7031"
-  "phile bò": "7001"              +  "phile bò": "7005"
-  "bò phile": "7001"              +  "bò phile": "7005"
-  "bò thăn": "7001"               +  "bò thăn": "7005"
-  "gân bò": "7001"                +  "gân bò": "7043"
-  "bò hoa": "7001"                +  "bò hoa": "7094"
-  "chim bồ câu": "7012"           +  "chim bồ câu": "7007"
-  "vịt": "7042"                   +  "vịt": "7028"
-  "phô mai đầu bò": "7035"        +  "phô mai đầu bò": "10009"
-  "đùi gà tây": "7088"            +  "đùi gà tây": "7014"
-  "nấm hủ đùi gà": "7088"         +  "nấm hủ đùi gà": "20007"
```

### Sibling aliases verified unchanged (no regression)

All 99 pinned sibling keys across the 19 codes hold their pre-fix targets before **and** after the write. In particular the deferred findings this fix must not drag along:

| Must remain | On |
|---|---|
| `sườn cốt lết`, `thịt cốt lết`, `cốt lết`, `sườn cốt lết xắt lát`, `giò thủ`, `giò thủ lợn`, `giò thủ lợn chín` | 7070 |
| `chả`, `chả lợn`, `bóng bì` | 7064 |
| `chả chiên`, `giò bò`, `giò bò chín`, `khoanh giò bò` | 7068 |
| `thịt bê`, `thịt bê mỡ`, `thịt bê mỡ tươi`, `nạm bò`, `thịt nạm bò`, `ba chỉ bò`, `ba chỉ bò đông lạnh` | 7001 |
| `gà tre`, `thịt gà rừng`, `thịt gà rừng tươi` | 7012 |
| `gan vịt`, `gan vịt tươi` | 7042 |
| `đầu bò`, `đầu bò tươi` | 7035 |
| `đùi gà chay` + 18 other chicken-thigh keys | 7088 |
| `sườn bò`, `dẻ sườn bò`, `bắp bò`, `thịt bắp bò`, … | 7094 |

`bóng bì` stays on 7064 even though `da heo` leaves it, and `đùi gà chay` stays on 7088 even though `đùi gà tây` leaves it — both are separately-listed audit findings, not this batch's.

## 2. Row outcomes

**111 rows repaired**, all to `PRESET_ALIAS_MATCH` / `0.98`, **0 row-level overrides**. Every one is resolved by the repoint alone, so a full re-match from raw text reproduces all 111.

| Alias | Reachable | Repaired | Cure-held | Recipes | kcal Δ |
|---|---:|---:|---:|---:|---:|
| `thịt thịt nạc thăn` | 5 | 5 | 0 | 5 | −8482.5 |
| `chả lụa` | 9 | 9 | 0 | 9 | −1404.0 |
| `chả lụa cắt hạt lựu` | 1 | 1 | 0 | 1 | −65.0 |
| `da heo` | 12 | 12 | 0 | 12 | −9177.0 |
| `da heo tươi` | 1 | 1 | 0 | 1 | −798.0 |
| `phile bò` | 18 | 18 | 0 | 18 | −598.0 |
| `bò phile` | 7 | **4** | **3** | 4 | −126.5 |
| `bò thăn` | 7 | 7 | 0 | 7 | −345.0 |
| `gân bò` | 17 | 17 | 0 | 13 | −1390.0 |
| `bò hoa` | 12 | **0** | **12** | 0 | ±0.0 |
| `chim bồ câu` | 5 | 5 | 0 | 4 | +3980.0 |
| `vịt` | 29 | 29 | 0 | 28 | +5184.5 |
| `phô mai đầu bò` | 1 | 1 | 0 | 1 | +97.5 |
| `đùi gà tây` | 1 | 1 | 0 | 1 | +194.4 |
| `nấm hủ đùi gà` | 1 | 1 | 0 | 1 | −204.0 |
| **Total** | **126** | **111** | **15** | **105** | **−13133.6** |

Per-row before/after identity and nutrition for all 111 rows is in `applied_fix.json` under `row_outcomes`.

Master-code population shift across the whole 63,943-row processed dataset — every delta accounted for, summing to exactly 111:

| Code | Before | After | Δ | | Code | Before | After | Δ |
|---|---:|---:|---:|---|---|---:|---:|---:|
| 7070 | 48 | 43 | −5 | | 7085 | 28 | 33 | +5 |
| 7068 | 16 | 6 | −10 | | 7069 | 7 | 17 | +10 |
| 7064 | 18 | 5 | −13 | | 7031 | 1 | 14 | +13 |
| 7001 | 75 | 29 | −46 | | 7005 | 24 | 53 | +29 |
| | | | | | 7043 | 0 | 17 | +17 |
| 7012 | 8 | 3 | −5 | | 7007 | 5 | 10 | +5 |
| 7042 | 30 | 1 | −29 | | 7028 | 33 | 62 | +29 |
| 7035 | 1 | 0 | −1 | | 10009 | 21 | 22 | +1 |
| 7088 | 87 | 85 | −2 | | 7014 | 1 | 2 | +1 |
| | | | | | 20007 | 94 | 95 | +1 |
| **7094** | **110** | **110** | **±0** | | | | | |

7094 is unchanged: `bò hoa` is latent (§4).

### Populations that did not move

- **Legitimate rows on every vacated code are byte-identical**: 7001 ×29 (`thịt bê`, `nạm bò`, `ba chỉ bò` routes), 7070 ×43, 7088 ×85, 7068 ×6, 7064 ×5, 7012 ×3, 7042 ×1 (`gan vịt` — the real duck-liver row), 7035 ×0.
- **15 cure-held rows** byte-identical on 7094 / `STANDARDIZED_CURE` / `0.98`.
- Verified programmatically against `HEAD`: exactly **111 of 63,943** ingredient rows differ, and the changed id set **equals** the reviewed repair set. Fields changed on those rows: `master_ingredient_code`, `master_ingredient_name`, `calories`, `protein_g`, `fat_g`, `carbs_g` — and nothing else. `raw_text`, `cleaned_name`, parsed quantity/unit, `estimated_weight_g`, `match_method` and `match_confidence` are preserved on every row.

## 3. Match method and confidence semantics

| Population | Method / confidence | Change |
|---|---|---|
| 111 repaired rows | `PRESET_ALIAS_MATCH` / `0.98` | **none** — alias-resolved before, alias-resolved after |
| 15 cure-held rows | `STANDARDIZED_CURE` / `0.98` | **none** |

No `0.0` confidence is written anywhere, no row becomes `UNMATCHED`, and no row-level override is created (AGENTS.md §4). The identity behind the match moves; the match semantics do not.

## 4. Cure-held rows — `bò hoa` is latent, `bò phile` splits

`scripts/run_qwen_line_pipeline.py` section A carries a reviewed systemic-mismatch cure:

```python
elif re.search(r"\bbắp bò\b", raw_l):
    candidate = ("7094", "Thịt bắp bò", "STANDARDIZED_CURE")
```

It runs **after** matching and overrides the alias result, so any row whose `raw_text` contains `bắp bò` is held on 7094 regardless of what its alias says.

- **`bò hoa` (12 rows)** — every reachable row reads `Bắp bò hoa …`, so all 12 are already on 7094 / `STANDARDIZED_CURE`. The repoint changes **zero rows today**. It is still applied: it removes a wrong identity (veal) that would be published the moment a `bò hoa` row appears without the `bắp bò` spelling, and 7094 is precisely what the reviewed cure already concluded for this text. The script asserts all 12 come through byte-identical, in both directions.
- **`bò phile` (7 rows)** — 3 read `… bắp bò phile` and stay cure-held on 7094 (correct: that *is* beef shank); the other 4 read `… bò phile` and repair to 7005.

The script fails closed if any repaired row's `raw_text` matches the cure pattern, so a repaired identity can never be silently overwritten by a later pipeline run.

## 5. Nutrition impact

Sums over the 111 repaired rows. Null is treated as absent, not zero.

| Metric | Before | After | Delta |
|---|---:|---:|---:|
| calories | 52,074.8 | 38,941.2 | **−13,133.6** |
| protein_g | 4,180.3 | 5,447.7 | **+1,267.4** |
| fat_g | 3,817.5 | 1,895.1 | **−1,922.4** |
| carbs_g | 231.3 | 39.0 | −192.3 |

The direction is expected and is the point of the fix: the large negative calorie/fat swing is dominated by rows leaving fatty veal (7001), fried pork paste (7064) and pork head cheese (7070) for lean tenderloin, pork skin and beef tendon; the positive swings are duck liver → duck meat (`vịt`, +5,184.5 kcal) and wild chicken → pigeon (`chim bồ câu`, +3,980.0 kcal at 340 kcal/100 g). Protein rises overall because several rows move from fat-bearing cuts to lean ones (`gân bò` alone: 1,320.5 → 2,098.9 g).

Nutrition was recomputed by `nlp.matching_integrity.stage_qwen_update` from the live target catalog profile and each row's own existing weight — never typed by hand. **Five target codes declare no `carbs_g`** (7031, 7043, 7007, 7028, 10009), so rows landing on them carry a **null** `carbs_g`, not `0.0`, per the nullable-nutrition contract in `nlp.nutrition`. Verified: 0 null-semantics violations across all 111 rows in both directions (no null written where the catalog has a value, no value written where the catalog has none).

**105 recipes** had totals recomputed. Recipe rollups were verified to agree with the ingredient sums for all 5,641 recipes: **0 mismatches**. `nutrition_status` / `missing_nutrition_count` are keyed on `calories`, which stayed non-null on every repaired row, so **0 recipes changed status label and 0 changed missing-nutrition count** (5,641 recipes, all `unchanged`).

## 6. CSV/JSON parity

`recipe_ingredients.csv` / `.json` and `recipes.csv` / `.json` are read, transformed and written independently so neither format's field set is narrowed to the other's. Verified after applying:

- **0** field mismatches across all 63,943 ingredient rows (identity, match, nutrition, weight, raw/cleaned text, recipe link).
- **0** total mismatches across all 5,641 recipes.
- Row counts and id order identical in both formats.

## 7. Canonical propagation

Regenerated **after** the processed data was correct, in the AGENTS.md §11 order: `scripts/canonicalize_recipes.py` → `scripts/export_canonical_json.py` → `scripts/canonicalize_recipes.py --check`.

| Check | Result |
|---|---|
| `--check` (determinism + protected-input hashes) | **passed**: unique selections, mapping coverage, references, singleton retention, unchanged source values, input-order-independent bytes, protected hashes |
| **Canonical ID drift** | **0** of 5,641 mappings changed |
| **Representative drift** | **0** — canonical recipe set identical (5,479 before and after) |
| Canonical recipes changed | 102 (totals + `selection_score` only) |
| Canonical ingredient rows changed | 108, all in the reviewed repair set; 0 cure-held rows |
| Canonical row/recipe counts | unchanged (62,023 rows / 5,479 recipes) |
| `recipe_canonical_mapping.json` (the id-only projection) | **byte-identical** — independent proof that no canonical id moved |
| Protected input hashes changed | exactly the 5 files this fix wrote; all `data/interim/*`, the catalog and the raw inputs unchanged |
| `recipe_canonicalization_summary.json` phase1/phase2 | identical apart from output hashes |

108 of 111 repaired rows appear in canonical output; the other 3 belong to recipes that were deduplicated into a different representative (`65bf873c`, `12dcee6e`, `48e65763`) — expected, and not drift.

**Quality-score churn, explained.** 86 rows in `recipe_canonical_mapping.csv` show a changed `nutrition_anomaly_count` and its derived scores (41 higher, 44 lower). `nutrition_bad()` in `scripts/canonicalize_recipes.py` counts a master row with any null macro as an anomaly, so this is entirely the **pre-existing catalog carb-null pattern moving with the identities**: rows leaving 7068/7070 (carbs null) for 7069/7085 (complete) lower the count, rows leaving 7042/7064 (complete) for 7028/7031 (carbs null) raise it. It reflects the catalog's carb coverage, not a defect introduced here, and the nulls are preserved as nulls per AGENTS.md §4/§9. Critically, it **selected nothing**: canonical id and representative drift are both 0.

## 8. Fail-closed safety model

Dry-run by default, deterministic, idempotent. Every write is gated on:

- each of the 15 alias keys holding exactly its reviewed old code, or already holding the reviewed new code (any third value aborts);
- every alias key outside the 15 byte-identical before and after, and the key set unchanged (this fix may only repoint — never add or remove);
- all 99 pinned sibling aliases across 19 codes holding their expected targets, before **and** after;
- all 19 codes existing in the live catalog under their exact current `name_vi`, via the identity guard in `stage_qwen_update` (which rejects a stale name even when the code exists);
- each of the 111 repair rows pinned by id **and** exact `raw_text` **and** its exact pre-fix match fields, in either `pending` or `already_applied` state;
- each of the 15 cure-held rows pinned by id, `raw_text`, and its exact 7094 / `STANDARDIZED_CURE` state;
- no repair row's `raw_text` matching the `bắp bò` cure pattern;
- the pinned id sets equalling, per alias, the set of rows each alias can actually reach — recomputed from live data through the real `normalize_vietnamese_text` / `clean_culinary_query` functions and the real Stage-1 catalog index, with Stage-1 precedence honoured (drift in either direction aborts);
- post-transform: every repair row in its target fixed state, every cure-held row byte-identical, every legitimate row on all 8 vacated codes byte-identical, and no unrelated row changed at all.

Any violation raises `DriftError` before anything is written. Re-running after `--apply` reports `rows_already_applied: 111`, all alias states `already_applied`, and produces a byte-identical no-op.

## 9. Known exclusions and deferred issues

Batch A repoints exactly fifteen aliases. Every other 70xx audit finding is deliberately left unchanged and is **not** addressed here:

the `cốt lết` family → 7070 · `bóng bì` → 7031 · the vegan analogues (`đùi gà chay`) → 20039 · `thịt ba chỉ rút sườn` (already fixed in Batch B) · `sườn bò` / `dẻ sườn bò` · `mỡ gà` · `thịt heo quay` · `nạm bò` · `ba chỉ bò` · `chả chiên` · `mỡ nước` · `tóp mỡ` · `gà tre` · catalog `name_vi` corruption · `xương bò` · the 7096 corruption · cleaner/matcher policy · stale-code remediation.

Two observations recorded for later, changed by nobody here:

1. **Audit target names were abbreviated** for three codes relative to the live catalog, which is authoritative (AGENTS.md §3): 7085 is `Thịt nạc thăn heo (lợn)` (audit said `Thịt nạc thăn heo`), 7007 is `Thịt bồ câu, cả con non (ra ràng)` (audit said `Thịt bồ câu`), 10009 is `Phô mai (phó mát)` (audit said `Phô mai`). The **codes and identities are exact**; only the display names differ, and the live names are what was written.
2. **Catalog carb nulls** on 7031, 7043, 7007, 7028 and 10009 drive the canonical anomaly-score churn in §7. This is a catalog-completeness question, not an alias question.

Nothing was committed or pushed.
