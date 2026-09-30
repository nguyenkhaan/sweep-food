# Applied fix: `thịt ba chỉ rút sườn` PRESET_ALIAS contamination on 7082 / Lòng gà (cả bộ)

Batch B of the 70xx meat-band audit. Branch `fix/matching-data-followups`. Applied by `scripts/eda/apply_thit_ba_chi_rut_suon_alias_safe_fix.py --apply`, tests in `tests/test_thit_ba_chi_rut_suon_alias_safe_fix.py`. Machine-readable companion: `applied_fix.json`.

## Problem

One preset alias in `data/processed/viendinhduong/ingredient_alias_map.json` mapped pork belly onto chicken giblets:

```
"thịt ba chỉ rút sườn" -> 7082   ("Lòng gà (cả bộ)" / Chicken, whole giblets, raw)
```

*Thịt ba chỉ rút sườn* is **pork belly with the rib bones removed**. 7082 is whole chicken giblets — a different species and a different organ/cut entirely. The correct identity was already in the catalog as **7018 / `Thịt ba chỉ (ba rọi) heo`** (`Pork, lean and fat meat, raw`), and every sibling pork-belly alias already pointed there, *including the two carrying the identical `rút sườn` qualifier*:

| Sibling alias | Target |
|---|---|
| `ba chỉ rút sườn` | 7018 |
| `thịt ba chỉ heo rút sườn` | 7018 |
| `ba rọi rút sườn` | 7018 |
| `thịt ba chỉ rút xương` | 7018 |

The 7082 value was therefore an isolated corruption, not a reviewed decision. 10 processed ingredient rows sat on the wrong identity as a result — every one of them in an unambiguously pork dish (`Thịt ba chỉ kho cam`, `Ba Chỉ Nướng Riềng Mẻ Mắm Tôm`, `Thịt một nắng`, …).

## 1. Alias decision (1): `REMOVE_ALIAS`

| Alias | Before | After | Rationale |
|---|---|---|---|
| `thịt ba chỉ rút sườn` | 7082 | *(removed)* | Pork belly resolved to chicken giblets. Removed rather than repointed — see below. |

**Why removal, not `SAFE_REPOINT` to 7018.** `clean_culinary_query()` in `nlp/entity_matcher.py` already strips `rút sườn` as preparation noise (it is in that function's `prep_patterns` list). With the corrupt key gone, Stage 2 of the matcher resolves the phrase through its own cleaned form:

```
"thịt ba chỉ rút sườn"
  → clean_culinary_query → "thịt ba chỉ"
  → existing sibling alias → 7018 / Thịt ba chỉ (ba rọi) heo
  → PRESET_ALIAS_MATCH / 0.98
```

Adding a redundant `thịt ba chỉ rút sườn -> 7018` entry would duplicate a resolution the cleaner already provides and grow the alias map for no behavioural gain. No replacement alias was added; asserted by `test_real_no_replacement_alias_was_added`.

**Fallthrough simulation (AGENTS.md §6).** Removing an unsafe alias is not automatically safe, so the post-removal path was simulated against the real matcher stages before writing, and is re-asserted at run time by `_assert_fallthrough_resolves_to_7018()`:

| Stage | Outcome |
|---|---|
| Stage 1 EXACT / CLEANED | Does not fire — neither `thịt ba chỉ rút sườn` nor `thịt ba chỉ` is a catalog name (7018 normalizes to `thịt ba chỉ ba rọi heo`). |
| **Stage 2 PRESET_ALIAS** | `query_norm` misses (key removed); `cleaned_q` = `thịt ba chỉ` **hits → 7018 @ 0.98**. Resolves here. |
| Stage 2.5 SUBPHRASE | Never reached. |
| Stage 3 NEURAL | Never reached. |

All ten rows therefore land on 7018 by alias resolution alone. **No row-level override was created**, and a future full re-match from raw text reproduces this state exactly — unlike the row-level decisions in `apply_suon_rib_alias_safe_fix.py`. One row (`500 gr thịt ba rọi rút sườn`) reaches 7018 via the sibling alias `thịt ba rọi` instead, because its parsed name keeps the `ba rọi` spelling; same code, same method, same confidence.

Unchanged and verified still on 7018: `thịt ba chỉ`, `thịt ba rọi`, `ba chỉ`, `ba chỉ heo`, `ba rọi`, `thịt ba chỉ heo`, `ba chỉ rút sườn`, `thịt ba chỉ heo rút sườn`, `ba rọi rút sườn`, `thịt ba chỉ rút xương`, `thịt ba chỉ cắt lát`, `thịt ba chỉ xay`, `thịt ba chỉ heo xay`, `thịt ba chỉ heo cắt nhỏ`, `thịt ba chỉ ngon`, `ba rọi ngon`, `thi t ba chi`, `thịt lợn nửa nạc nửa mỡ tươi`.

Unchanged and verified still on 7082: `lòng gà`, `lòng gà cả bộ`, `lòng gà cả bộ tươi`. **7082 is a legitimate identity; only the one pork-belly key was wrong.**

Nearby identities that share the `ba chỉ` token and must not drift, verified unchanged: `thịt ba chỉ xông khói` → 20051 (bacon), `ba chỉ bò` → 7001, `thịt bò ba chỉ cắt lát mỏng` → 7006, `thịt lợn ba chỉ` → 11020.

## 2. Row outcomes (10)

All 10 → **7018 / `Thịt ba chỉ (ba rọi) heo` / `PRESET_ALIAS_MATCH` / `0.98`**, all by alias fallthrough, 0 row-level overrides.

| Row | raw_text | Recipe | Weight (g) | kcal before → after |
|---|---|---|---:|---|
| `649979f6` | 400 g Thịt ba chỉ rút sườn | Ba Chỉ Nướng Riềng Mẻ Mắm Tôm | 400.0 | 476.0 → 1040.0 |
| `d74a55d5` | 500 gr thịt ba rọi rút sườn | Thịt Xíu Mè | 500.0 | 595.0 → 1300.0 |
| `49e65216` | Thịt ba chỉ rút sườn 600g | Heo xiên que nướng mắc khén | 600.0 | 714.0 → 1560.0 |
| `42cf8d71` | Thịt ba chỉ rút sườn 300g | Thịt ba chỉ rim chanh sả | 300.0 | 357.0 → 780.0 |
| `e2278878` | Thịt ba chỉ rút sườn: 300g | Heo nướng mỡ hẹ | 300.0 | 357.0 → 780.0 |
| `dfce19a5` | Thịt ba chỉ rút sườn 500g | Thịt ba chỉ kho cam | 500.0 | 595.0 → 1300.0 |
| `d321c9bf` | Thịt ba chỉ rút sườn 400g | Thịt rang gừng lá chanh | 400.0 | 476.0 → 1040.0 |
| `6f9cfee5` | Thịt ba chỉ rút sườn 300g | Thịt ba chỉ kho mơ | 300.0 | 357.0 → 780.0 |
| `9dd7353b` | Thịt ba chỉ rút sườn 2.5 kg | Thịt một nắng | 2500.0 | 2975.0 → 6500.0 |
| `7d78336c` | Thịt ba chỉ rút sườn 500 gr | Thịt kho nước tương | 500.0 | 595.0 → 1300.0 |

Nutrition was recomputed by `nlp.matching_integrity.stage_qwen_update` from the live 7018 profile and each row's own existing weight — never typed by hand. **7018 declares no `carbs_g`, so every repaired row's `carbs_g` is now null (unknown), not `0.0`**, per the nullable-nutrition contract in `nlp.nutrition`. `raw_text`, `cleaned_name`, parsed quantity/unit and `estimated_weight_g` are preserved on every row.

### Populations that did not move

- **5 legitimate 7082 rows** (`Lòng gà: 300g` ×2, `Lòng gà 300 gr`, `Lòng gà 100 g`, `Lòng gà 600 gr`) remain byte-identical on 7082, `cleaned_name` = `lòng gà`.
- **525 pre-existing 7018 rows** are untouched; the population is now 535 (525 + 10), all `PRESET_ALIAS_MATCH`.
- Verified programmatically: exactly 10 of 63,943 ingredient rows differ from the pre-fix dataset, and all 10 are the reviewed ids.

## 3. Nutrition impact

Sums over the 10 repaired rows. Null is treated as absent, not zero.

| Metric | Before (7082) | After (7018) | Delta |
|---|---:|---:|---:|
| calories | 7497.0 | 16380.0 | **+8883.0** |
| protein_g | 1126.3 | 1039.5 | −86.8 |
| fat_g | 281.5 | 1354.5 | **+1073.0** |
| carbs_g | 112.8 | *(all null)* | −112.8 |

The direction is expected: chicken giblets are a lean 119 kcal/100 g organ meat, pork belly is 260 kcal/100 g at 21.5 g fat. The `carbs_g` "after" figure of 0.0 in `applied_fix.json` is the sum of ten **null** values, not ten zeros.

10 recipes had totals recomputed:

| Recipe | kcal before → after | carbs before → after |
|---|---|---|
| Ba Chỉ Nướng Riềng Mẻ Mắm Tôm | 853.3 → 1417.3 | 85.7 → 78.5 |
| Thịt ba chỉ kho cam | 1165.4 → 1870.4 | 132.5 → 123.6 |
| Thịt ba chỉ rim chanh sả | 926.4 → 1349.4 | 104.6 → 99.2 |
| Thịt rang gừng lá chanh | 554.6 → 1118.6 | 24.1 → 16.9 |
| Heo xiên que nướng mắc khén | 962.5 → 1808.5 | 43.8 → 33.1 |
| Thịt một nắng | 3351.6 → 6876.6 | 66.2 → 21.4 |
| Thịt kho nước tương | 897.1 → 1602.1 | 41.1 → 32.2 |
| Heo nướng mỡ hẹ | 1088.5 → 1511.5 | 52.2 → 46.8 |
| Thịt Xíu Mè | 971.3 → 1676.3 | 35.7 → 26.8 |
| Thịt ba chỉ kho mơ | 598.0 → 1021.0 | 35.1 → 29.7 |

`nutrition_status` / `missing_nutrition_count` are recomputed by the same rule `scripts/reprocess_recipe_weights_and_nutrition.py` uses. Both are keyed on `calories`, which stayed non-null on every repaired row, so **0 recipes changed status label and 0 changed missing-nutrition count** (5641 recipes, all `unchanged`).

## 4. CSV/JSON parity

`recipe_ingredients.csv` / `.json` and `recipes.csv` / `.json` are read, transformed and written independently so neither format's field set is narrowed to the other's. Verified after applying: 0 field mismatches across all 63,943 ingredient rows and 0 total mismatches across all 5,641 recipes.

## 5. Canonical propagation

Regenerated **after** the processed data was correct, in the AGENTS.md §11 order: `scripts/canonicalize_recipes.py` → `scripts/export_canonical_json.py` → `scripts/canonicalize_recipes.py --check`.

| Check | Result |
|---|---|
| `--check` (determinism + protected-input hashes) | **passed** |
| Canonical ID drift | **0** of 5641 mappings changed |
| Representative drift | **0** — canonical recipe set identical (5479 before and after) |
| Canonical recipes changed | 10, all in the reviewed set |
| Canonical ingredient rows changed | 10, all in the reviewed set |
| Canonical row/recipe counts | unchanged (62,023 rows / 5,479 recipes) |
| CSV/JSON parity (recipes, ingredients, mapping) | identical |
| Referential integrity | every canonical ingredient's `recipe_id` present in canonical recipes |
| `recipe_canonicalization_summary.json` phase1/phase2 | byte-identical apart from output hashes |

All 10 affected recipes are **`singleton retained`** in `recipe_canonical_mapping.csv`, so no duplicate group's representative selection could be influenced. The mapping rows for those 10 do show a quality-score change: each recipe's missing-nutrient counter increments by one, because the repaired row's `carbs_g` is now correctly null. That is a score-column change on singletons only — it selects nothing and moved no canonical id.

## 6. Validation results

- `scripts/eda/apply_thit_ba_chi_rut_suon_alias_safe_fix.py` (dry-run) → preview matched the reviewed plan exactly; `--apply` → 10/10 remapped, 5 legitimate 7082 rows untouched; second run → `remap_already_applied: 10`, byte-identical no-op (idempotent).
- `tests/test_thit_ba_chi_rut_suon_alias_safe_fix.py` — **56 passed**.
- `tests/test_suon_rib_alias_safe_fix.py`, `tests/test_alias_integrity.py`, `tests/test_entity_matcher_alias_resolution.py` — passed.

One assertion in `tests/test_suon_rib_alias_safe_fix.py::test_real_out_of_scope_rib_aliases_left_alone` pinned `thịt ba chỉ rút sườn -> 7082` as a then-deferred finding. Batch B is that deferral being resolved, so the assertion now pins `lòng gà -> 7082` instead — still proving the rib remediation never touched 7082 — and the removed key is owned by this fix's own test module.

## 7. Fail-closed safety model

Dry-run by default, deterministic, idempotent. Every write is gated on:

- the alias key holding exactly `7082`, or already being absent;
- every other alias entry byte-identical before and after, and the map shrinking by at most the one expected key;
- the 18 sibling 7018 aliases and 3 giblet 7082 aliases holding their expected values, before **and** after;
- the post-removal fallthrough resolving to 7018 through the real `clean_culinary_query`/`normalize_vietnamese_text` functions;
- each of the 10 rows pinned by id **and** exact `raw_text` **and** exact `cleaned_name` **and** its exact pre-fix match fields, in either `pending` or `already_applied` state;
- the pinned id set equalling the set of rows the removal can actually reach, recomputed from live data (drift in either direction aborts);
- 7018 existing in the live catalog under its exact expected name, via the identity guard in `stage_qwen_update`;
- post-transform: every target row in the 7018 fixed state, every legitimate 7082 row byte-identical, and no unrelated row changed at all.

Any violation raises `DriftError` before anything is written.

## 8. Known exclusions and deferred issues

Batch B removes exactly one alias. Every other 70xx audit finding is deliberately left unchanged and is **not** addressed here:

`cốt lết` (`sườn cốt lết` / `sườn cốt lết xắt lát` → 7070) · `chả lụa` · `da heo` · the beef aliases · `vịt` · `chim bồ câu` · `sườn bò` / `dẻ sườn bò` → 7094 · `mỡ gà` · `thịt heo quay` · catalog corruption · stale-code rows · cleaner/matcher policy issues.

Nothing was committed or pushed.
