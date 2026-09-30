# Display-name corruption repair, Batch C2 — white cabbage 4010

Policy: DISPLAY_NAME_BATCH_C2. 92 ingredient rows / 91 source recipes.

## Root cause

Catalog 4010 is the raw Viện Dinh Dưỡng row `Cabbage, common, raw`, but its Vietnamese display name read `Cần tây` -- 4018's name, which 4018 also still carries. Two codes published one display name, and the alias map organised eighteen keys and 89 processed rows around 4010 as though it were celery: 72 celery rows carried cabbage nutrition, bare `bắp cải` was handed to red cabbage, and the genuine white-cabbage rows sat on a code that denied them.

## Catalog

| Code | Field | Before | After | name_en (unchanged) |
|---|---|---|---|---|
| 4010 | name_vi | Cần tây | Cải bắp trắng | Cabbage, common, raw |

Every other column is asserted byte-for-byte unchanged: `ash_g`, `calcium_mg`, `carbs_g`, `category_en`, `category_vi`, `code`, `copper_mg`, `energy_kcal`, `fat_g`, `fiber_g`, `folate_food_mcg`, `folate_total_mcg`, `iron_mg`, `magnesium_mg`, `manganese_mg`, `name_en`, `phosphorus_mg`, `potassium_mg`, `protein_g`, `retinol_mcg`, `selenium_mcg`, `sodium_mg`, `sugar_g`, `vitamin_a_rae_mcg`, `vitamin_b1_mg`, `vitamin_b2_mg`, `vitamin_b3_mg`, `vitamin_b5_mg`, `vitamin_b6_mg`, `vitamin_c_mg`, `water_g`, `zinc_mg`.

`Cải bắp` was **not** used: it would reactivate the disabled Qwen rule ("bắp cải",) -> 4010 "Cải bắp" through the A1 identity check. `Cải bắp trắng` states the white/common cultivar the row's own `name_en` asserts and stays distinct from 4011 `Cải bắp đỏ` and 4012 `Cải bắp trắng, khô`. Qwen mapper rules after the repair: 29 active / 20 disabled, unchanged, with that rule still disabled and `map_clean_to_master("bắp cải")` still unresolved.

Colliding display names before: `cần tây`, `nấm kim châm`, `thịt trâu, đùi`. After: `nấm kim châm`, `thịt trâu, đùi` — `cần tây` leaves the set, which is what this batch is for.

## Reviewed synonym

`cần tàu` == `cần tây` → 4018.

The recipe author names both terms for one ingredient on one line: "1 ít rau cần tây (hay cần tàu)". "hay" is Vietnamese for "or", so the line asserts the equivalence itself. Recorded from that raw text, NOT inferred from the fact that both keys currently resolve to the same alias-map target -- AGENTS.md section 7 forbids that inference.

Evidence row `03f24d73-136a-41b1-8585-5ac712c143f2`: `1 ít rau cần tây (hay cần tàu)`.

## Exact alias changes

18 actions. Map size 4672 − 3 removed + 5 added = 4674.

| Action | Alias | Before | After |
|---|---|---|---|
| repointed | bắp cải | 20035 | 4010 |
| repointed | cần tàu | 4010 | 4018 |
| repointed | cần tây bào vỏ | 4010 | 4018 |
| repointed | cần tây bẹ | 4010 | 4018 |
| repointed | cần tây bẹ cắt lát xéo | 4010 | 4018 |
| repointed | cần tây tước xơ cắt lát | 4010 | 4018 |
| repointed | lá cần tây non | 4010 | 4018 |
| repointed | rau cần tây | 4010 | 4018 |
| repointed | rau cần tây to | 4010 | 4018 |
| repointed | rau nêm cần tàu | 4010 | 4018 |
| removed | mĩ 1 cây cần tây | 4010 | — |
| removed | rau ngổ hoặc cần tây | 4010 | — |
| removed | tây | 4010 | — |
| added | bắp cải nhỏ | — | 4010 |
| added | bắp cải trái tim | — | 4010 |
| added | bắp cải trắng | — | 4010 |
| added | bắp cải trộn | — | 4010 |
| added | cải bắp | — | 4010 |

Reviewed aliases that were already correct and stay put: `cải bắp trắng tươi` → 4010, `cần tây` → 4018, `cần tây tươi` → 4018, `cần tây cắt nhỏ` → 4018, `cần tây cắt hạt lựu` → 4018, `bắp cải tím` → 20035, `cải tím` → 20035, `rau cải tím` → 20035, `bắp cải tím cải tím` → 20035, `cải tím cắt sợi` → 20035, `cải tím xắt sợi` → 20035, `cải tím bào mỏng` → 20035, `cải` → 4013, `cải trắng` → 4021, `cải bắp đỏ` → 4011, `cải bắp trắng khô` → 4012, `cải khô` → 4012, `cần ta` → 4017, `cần` → 4017. `cải` → 4013 and `cải trắng` → 4021 belong to C3 and are asserted unchanged.

## Processed rows and nutrition

Nutrition sums include known values only; missing values remain null. Every populated value is the live target catalog column scaled by the row's own weight through `nlp.nutrition.scale_nutrition` — no second rounding convention is implemented. Exact before/after records for all 92 ingredient rows and 91 recipes are in [applied_fix.json](applied_fix.json).

| Cohort | Source | Target | Provenance | Rows | Recipes | kcal | Protein | Fat | Carbs |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| celery_4010_to_4018 | 4010 | 4018 | preserved | 71 | 71 | 1355.8 | 145.5 | 5.3 | 190.6 |
| celery_compound_subphrase_4010_to_4018 | 4010 | 4018 | measured | 1 | 1 | 9.0 | 1.0 | 0.1 | 1.2 |
| ambiguous_clear_to_unmatched | 4010 | UNMATCHED | cleared | 6 | 5 | -153.0 | -7.6 | -0.3 | -29.4 |
| white_cabbage_keep_4010 | 4010 | 4010 | preserved | 10 | 10 | 0.0 | 0.0 | 0.0 | 0.0 |
| red_cabbage_4010_to_20035 | 4010 | 20035 | preserved | 1 | 1 | -60.0 | -4.8 | 1.3 | 5.9 |
| white_cabbage_20035_to_4010 | 20035 | 4010 | measured | 1 | 1 | 4.0 | 0.3 | -0.1 | -0.4 |
| white_cabbage_unmatched_recovery | UNMATCHED | 4010 | measured | 2 | 2 | 28.8 | 1.4 | 0.0 | 5.6 |

| Nutrient | Before known sum | After known sum | Delta | Nulls before → after |
|---|---:|---:|---:|---:|
| calories | 3581.1 | 4765.7 | 1184.6 | 2 → 6 |
| protein_g | 178.1 | 313.9 | 135.8 | 2 → 6 |
| fat_g | 8.3 | 14.6 | 6.3 | 2 → 6 |
| carbs_g | 689.1 | 862.6 | 173.5 | 2 → 6 |

The only null movement is the six clears (value → null on all four nutrients) and the two UNMATCHED recoveries (null → value on all four). The recoveries store `fat_g = 0.0`: 4010 carries 0.09 g/100 g and 0.09 × 0.30 / 0.09 × 0.50 both round to 0.0 at the project's one decimal. That is a real scaled numeric zero, not a coerced null — AGENTS.md section 4.

Corpus-wide null counts after: {"calories": 8469, "protein_g": 16927, "fat_g": 20223, "carbs_g": 17428}.

## The six curated clears

An either-or line, two compounds, two dish titles and a multi-identity line. None of them has a single defensible catalog identity, and picking one component would be exactly the forced coverage AGENTS.md section 5 rejects. Each is pinned by exact id, exact raw text and a complete before record, and each carries the full UNMATCHED contract afterwards: blank code, blank name, `UNMATCHED`, blank confidence (never `0.0`) and four null nutrients, with raw text, cleaned name, quantity/unit, preparation note and estimated weight preserved.

**These six are intentionally NOT matcher-reproducible.** `rau ngổ hoặc cần tây` is stored UNMATCHED while the matcher would reach 4018 (either-or line naming two distinct herbs); `bắp cải` is stored UNMATCHED while the matcher would reach 4010 (two rows whose raw text names cabbage alongside another identity). No broad guard is added to reproduce them: a guard wide enough to catch these lines would reach rows nobody reviewed, and is a separate reviewed decision.

## Final populations

| Code | Rows |
|---|---:|
| 4010 | 13 |
| 4018 | 177 |
| 20035 | 33 |
| 4011 | 41 |
| 4012 | 5 |
| 4013 | 122 |
| 4017 | 8 |
| 4021 | 147 |
| 4015 | 19 |
| 4016 | 301 |
| 4109 | 65 |
| 4135 | 59 |
| UNMATCHED | 8469 |

Recipe rollups: {"recipes_with_changed_missing_count": 7, "recipes_with_status_label_changed": 0, "missing_count_transitions": {"1022eb07-c5b1-4fac-abec-6de502e4289a": {"before": 4, "after": 5}, "2b0fe656-9cd9-46d2-b5ca-90659d0a79b2": {"before": 4, "after": 3}, "2b3ed220-c1c1-44fa-838e-3844ddb1b611": {"before": 2, "after": 4}, "86aa60e9-62eb-45c9-ac47-33a73a9d7d54": {"before": 2, "after": 3}, "ae835445-9dec-4a32-b417-ad0f653904ea": {"before": 2, "after": 1}, "d5ba12dc-cccb-4621-b71c-f8ede7bceb40": {"before": 1, "after": 2}, "fd85d160-cd83-4f76-80a3-0e12b1fb2757": {"before": 1, "after": 2}}, "status_transitions": {}} — five clear-bearing recipes gain a missing row (one holds two of the six clears) and the two recovery recipes lose one. No recipe crosses a COMPLETE/PARTIAL/INCOMPLETE threshold, so there are zero `nutrition_status` label transitions, and none is forced.

## Downstream hard-coded cabbage codes

| File | Occurrences | on 4012 | on 4010 |
|---|---:|---:|---:|
| src/recommendation/pantry_simulator.py | 4 | 0 | 4 |
| src/recommendation/benchmark_generator.py | 1 | 0 | 1 |

Five live fresh-cabbage pantry entries pointed at 4012 `Cải bắp trắng, khô` — dried cabbage at 301 kcal/100 g — for a vegetable a household buys by the 200–600 g head. They now point at the repaired fresh 4010. `("dưa chuột", "4016", …)` is C1's and is untouched. `src/` is re-scanned on every run, and any other hard-coded fresh-cabbage code fails the batch closed.

## Audit evidence hygiene

The stale `4010 → `Cần tây`` WRONG signature in `scripts/eda/audit_qwen_matching.py` is retired and replaced by the narrow VALID pattern for the repaired identity: `Cải bắp trắng` / `bắp cải`, `bắp cải trắng`, `bắp cải nhỏ`, `bắp cải trái tim`, `bắp cải trộn`. Evidence hygiene only — no production matcher behaviour changes, and 4016's evidence is C1's and is not touched. Measured consequence: exactly one surviving row moves B → C.

## Matcher replay

| Query | Code | Single route | Batch route |
|---|---|---|---|
| cần tây | 4018 | EXACT_CATALOG_MATCH 1.0 | EXACT_CATALOG_MATCH 1.0 |
| rau cần tây | 4018 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| cần tàu | 4018 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| rau nêm cần tàu | 4018 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| cần tây bẹ | 4018 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| lá cần tây non | 4018 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| rau cần tây to | 4018 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| cần tây bào vỏ | 4018 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| cần tây bẹ cắt lát xéo | 4018 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| cần tây tước xơ cắt lát | 4018 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| cần tây tươi | 4018 | CLEANED_NAME_MATCH 0.99 | CLEANED_NAME_MATCH 0.99 |
| cần tây cắt nhỏ | 4018 | CLEANED_NAME_MATCH 0.99 | CLEANED_NAME_MATCH 0.99 |
| cần tây cắt hạt lựu | 4018 | CLEANED_NAME_MATCH 0.99 | CLEANED_NAME_MATCH 0.99 |
| cải bắp | 4010 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| cải bắp trắng | 4010 | EXACT_CATALOG_MATCH 1.0 | EXACT_CATALOG_MATCH 1.0 |
| bắp cải | 4010 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| bắp cải trắng | 4010 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| bắp cải nhỏ | 4010 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| bắp cải trái tim | 4010 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| bắp cải trộn | 4010 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| cải bắp trắng tươi | 4010 | CLEANED_NAME_MATCH 0.99 | CLEANED_NAME_MATCH 0.99 |
| bắp cải tím | 20035 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| cải tím | 20035 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| rau cải tím | 20035 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| cải bắp đỏ | 4011 | EXACT_CATALOG_MATCH 1.0 | EXACT_CATALOG_MATCH 1.0 |
| cải bắp trắng khô | 4012 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| cải khô | 4012 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| cần ta | 4017 | EXACT_CATALOG_MATCH 1.0 | EXACT_CATALOG_MATCH 1.0 |
| cải | 4013 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| cải trắng | 4021 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| dưa leo | 4016 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| dưa chuột | 4027 | EXACT_CATALOG_MATCH 1.0 | EXACT_CATALOG_MATCH 1.0 |
| cải xanh | 4011 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| cải bẹ xanh | 4011 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| cải thảo | 4109 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| cải thìa | 4135 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| mĩ 1 cây cần tây | 4018 | SUBPHRASE_CATALOG_MATCH 0.95 | SUBPHRASE_CATALOG_MATCH 0.95 |

Known divergence, documented and not fixed: `tây` was 4010, now reaches 4018 on the single route and 20036 on the batch route, with 0 live rows. It moves no stored row, and no phrase a live row uses diverges.

## Deferred, recorded and unchanged

- **c3_parser_damaged_white_cabbage_recovery.** Bare `cải` -> 4013 and `cải trắng` -> 4021 are asserted unchanged here. Recovering parser-damaged white-cabbage rows hiding behind them is C3.
- **c1_cucumber_and_mustard_green_identities.** 4016 `Dưa chuột (dưa leo)` publishes `Mustard greens, raw` as its name_en. C1 owns that repair and lands after C2; its aliases, rows and audit evidence are untouched.
- **4011_vs_20035_duplicate_resolution.** 4011 `Cải bắp đỏ` and 20035 `Bắp cải tím (cải tím)` are both red cabbage. Their 41 and 33 rows are asserted stable; choosing a survivor is a separate domain decision.
- **parser_canonical_unit_map_bap.** The parser treats `bắp` as a unit, which is what collapsed `1 trái bắp mĩ, 1 cây cần tây` into an alias key. Parser behaviour is not changed by this batch.

## Canonical propagation

| Artifact | Changed logical records |
|---|---:|
| canonical_recipes.csv | 81 |
| canonical_recipe_ingredients.csv | 92 |
| recipe_canonical_mapping.csv | 7 |

The 91 affected recipes span 91 canonical groups, and every reviewed row appears in `canonical_recipe_ingredients.csv`. The pre-implementation review quoted 91 canonical recipes changed; measured, 91 canonical recipes are touched and 81 rows change content. The ten reviewed KEEP rows stay on code 4010 and only refresh their display name, so their recipes carry an identical nutrition rollup before and after. canonical_recipes.csv holds totals, not ingredient names, so those ten recipes are touched without changing content. Canonical ID drift = 0; representative drift = 0.

## Embeddings and validation

Embeddings: {"rebuilt": true, "tracked": false, "shape": [750, 768], "sha256": "2d4562128619cf0b4e7173ac6a848e7813962bbf5d89045049a82e2112559978", "next_load_equal": true, "input_sha256": "5b2fa9028798523280e0a3fe0ae354331dc52b7731f9b47dc443e97039a4459b", "build_inputs": {"4010": "Cải bắp trắng (Rau, quả, củ dùng làm rau)"}}

Validation: {"complete": true, "processed_parity": true, "canonical_parity": true, "canonical_check": true, "canonical_determinism": true, "interim_unchanged": true, "catalog_name_vi_only": true, "embeddings_rebuilt": true, "downstream_hard_codes_repaired": 5, "blast_radius_measured_against": "reviewed manifest, not git HEAD"}

Tests: {}

Excluded: 4016 / C1 cucumber-vs-mustard-green repair; parser CANONICAL_UNIT_MAP["bắp"]; `cải` -> 4013 and `cải trắng` -> 4021 (C3); C3 parser-damaged white-cabbage recovery; 4011 / 20035 duplicate resolution; 4015 / 4135 bok-choy duplicate; spinach / kale catalog gaps; 4094 / 4096 corruption; bare măng; 4121 / 20077; match()/match_batch() architecture; general stale code-space contamination.

No commit or push.

## Git validation and changed files

git diff --check: passed.

Branch: fix/catalog-integrity-followups. All changes remain unstaged.

```text
 M data/processed/recipes/canonical_recipe_ingredients.csv
 M data/processed/recipes/canonical_recipe_ingredients.json
 M data/processed/recipes/canonical_recipes.csv
 M data/processed/recipes/canonical_recipes.json
 M data/processed/recipes/recipe_canonical_mapping.csv
 M data/processed/recipes/recipe_canonicalization_summary.json
 M data/processed/recipes/recipe_ingredients.csv
 M data/processed/recipes/recipe_ingredients.json
 M data/processed/recipes/recipes.csv
 M data/processed/recipes/recipes.json
 M data/processed/viendinhduong/ingredient_alias_map.json
 M data/processed/viendinhduong/master_ingredients_nutrition.csv
 M scripts/eda/apply_bamboo_shoot_alias_safe_fix.py
 M scripts/eda/apply_display_name_batch_a_safe_fix.py
 M scripts/eda/apply_display_name_batch_b_safe_fix.py
 M scripts/eda/audit_qwen_matching.py
 M src/recommendation/benchmark_generator.py
 M src/recommendation/pantry_simulator.py
 M tests/test_bamboo_shoot_alias_safe_fix.py
 M tests/test_display_name_batch_a_safe_fix.py
 M tests/test_display_name_batch_b_safe_fix.py
 M tests/test_meat_band_batch_a_alias_safe_fix.py
 M tests/test_meat_band_batch_a_followup_safe_fix.py
 M tests/test_qwen_eligibility_guard.py
?? reports/eda/display_name_batch_c2_fix/
?? scripts/eda/apply_display_name_batch_c2_safe_fix.py
?? scripts/eda/display_name_batch_c2_reviewed_state.json
?? tests/test_display_name_batch_c2_safe_fix.py
```
