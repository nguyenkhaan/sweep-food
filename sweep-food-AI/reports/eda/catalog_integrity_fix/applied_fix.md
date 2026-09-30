# Catalog integrity repair

Policy: USE_7038_CANONICAL. 72 ingredient rows / 61 source recipes.

Catalog nutrition, categories and codes are unchanged. 20079 remains available for historical code resolution but is excluded from all active retrieval surfaces.

## Exact catalog changes

| Code | Field | Before | After |
|---|---|---|---|
| 7038 | name_vi | Gan heo (lợn) | Đuôi lợn |
| 7041 | name_vi | Lưỡi heo (lợn) | Gan lợn |
| 7056 | name_vi | Tim heo (lợn) | Tim gà |
| 7056 | name_en | Chicken, heart, tươi | Chicken, heart, raw |
| 20079 | name_vi | Đuôi heo (Đuôi lợn) | ZZ deprecated 20079 -> 7038 |
| 20079 | name_en | Pig tail | (blank) |

## Exact alias changes

| Alias | Before | After |
|---|---|---|
| gan heo | 7038 | 7041 |
| gan lợn | 7038 | 7041 |
| lưỡi heo | 7041 | 7045 |
| tim heo | 7056 | 7057 |
| mỡ gà | 7041 | removed |
| đuôi heo | 20079 | 7038 |
| đuôi lợn | 20079 | 7038 |
| đuôi heo tươi | 20079 | 7038 |
| đuôi heo đuôi lợn | 20079 | removed |

The existing đuôi lợn tươi → 7038 alias and all beef-tail aliases are unchanged. No tim gà alias was added.

## Processed rows and nutrition

Nutrition sums below include known values only; missing values remain null. Exact before/after records for all ingredient rows and 61 named recipes are in [applied_fix.json](applied_fix.json).

| Cohort | Rows | Recipes | kcal delta | Protein delta | Fat delta | Carbs known-sum delta |
|---|---:|---:|---:|---:|---:|---:|
| pork_tail | 17 | 16 | 11954.0 | -361.4 | 1501.2 | 0.0 |
| pork_liver | 18 | 17 | -12987.0 | 296.0 | -1609.8 | 74.0 |
| pork_tongue | 7 | 7 | 651.0 | -48.3 | 96.6 | -6.3 |
| chicken_fat | 9 | 9 | -1113.6 | -180.4 | -34.6 | -19.2 |
| pork_heart | 19 | 19 | -670.0 | -30.3 | -77.2 | 40.2 |
| chicken_heart | 2 | 1 | 1254.0 | 176.0 | 60.5 | 0 |

| Cohort | Nutrient | Before known sum | After known sum | Delta | Nulls before → after |
|---|---|---:|---:|---:|---:|
| pork_tail | calories | 20502.5 | 32456.5 | 11954.0 | 0 → 0 |
| pork_tail | protein_g | 1112.0 | 750.6 | -361.4 | 0 → 0 |
| pork_tail | fat_g | 1772.4 | 3273.6 | 1501.2 | 0 → 0 |
| pork_tail | carbs_g | 0.0 | 0 | 0.0 | 0 → 17 |
| pork_liver | calories | 17279.0 | 4292.0 | -12987.0 | 0 → 0 |
| pork_liver | protein_g | 399.6 | 695.6 | 296.0 | 0 → 0 |
| pork_liver | fat_g | 1743.0 | 133.2 | -1609.8 | 0 → 0 |
| pork_liver | carbs_g | 0 | 74.0 | 74.0 | 18 → 0 |
| pork_tongue | calories | 1218.0 | 1869.0 | 651.0 | 0 → 0 |
| pork_tongue | protein_g | 197.4 | 149.1 | -48.3 | 0 → 0 |
| pork_tongue | fat_g | 37.8 | 134.4 | 96.6 | 0 → 0 |
| pork_tongue | carbs_g | 21.0 | 14.7 | -6.3 | 0 → 0 |
| chicken_fat | calories | 1113.6 | 0 | -1113.6 | 0 → 9 |
| chicken_fat | protein_g | 180.4 | 0 | -180.4 | 0 → 9 |
| chicken_fat | fat_g | 34.6 | 0 | -34.6 | 0 → 9 |
| chicken_fat | carbs_g | 19.2 | 0 | -19.2 | 0 → 9 |
| pork_heart | calories | 3819.0 | 3149.0 | -670.0 | 0 → 0 |
| pork_heart | protein_g | 536.0 | 505.7 | -30.3 | 0 → 0 |
| pork_heart | fat_g | 184.4 | 107.2 | -77.2 | 0 → 0 |
| pork_heart | carbs_g | 0 | 40.2 | 40.2 | 19 → 0 |
| chicken_heart | calories | 0 | 1254.0 | 1254.0 | 2 → 0 |
| chicken_heart | protein_g | 0 | 176.0 | 176.0 | 2 → 0 |
| chicken_heart | fat_g | 0 | 60.5 | 60.5 | 2 → 0 |
| chicken_heart | carbs_g | 0 | 0 | 0 | 2 → 2 |
| combined | calories | 43932.1 | 43020.5 | -911.6 | 2 → 9 |
| combined | protein_g | 2425.4 | 2277.0 | -148.4 | 2 → 9 |
| combined | fat_g | 3772.2 | 3708.9 | -63.3 | 2 → 9 |
| combined | carbs_g | 40.2 | 128.9 | 88.7 | 39 → 28 |

All 17 tail carbohydrate values changed from real 0.0 to null. Nine chicken-fat rows have null code/name/confidence/nutrition and method UNMATCHED. Source text, parsed fields and weights are unchanged.

Recipe status transitions: {"recipes_with_changed_missing_count": 10, "recipes_with_status_label_changed": 6, "status_transitions": {"COMPLETE -> PARTIAL": 4, "unchanged": 55, "PARTIAL -> INCOMPLETE": 1, "PARTIAL -> COMPLETE": 1}}.

## Matcher and deprecation

The narrow mỡ gà phrase guard prevents unsafe neural fallthrough. Deprecated 20079 is excluded from exact, cleaned-name, alias, subphrase, token-overlap and both neural ranking paths, including candidate lists. The retained display marker does not collide with current normalized raw/cleaned queries or aliases.

| Query | Code | Single route | Batch route |
|---|---|---|---|
| gan heo | 7041 | PRESET_ALIAS_MATCH | PRESET_ALIAS_MATCH |
| gan lợn | 7041 | EXACT_CATALOG_MATCH | EXACT_CATALOG_MATCH |
| lưỡi heo | 7045 | PRESET_ALIAS_MATCH | PRESET_ALIAS_MATCH |
| tim heo | 7057 | PRESET_ALIAS_MATCH | PRESET_ALIAS_MATCH |
| tim gà | 7056 | EXACT_CATALOG_MATCH | EXACT_CATALOG_MATCH |
| tim gà tươi | 7056 | CLEANED_NAME_MATCH | CLEANED_NAME_MATCH |
| mỡ gà | UNMATCHED | UNMATCHED | UNMATCHED |
| đuôi heo | 7038 | PRESET_ALIAS_MATCH | PRESET_ALIAS_MATCH |
| đuôi lợn | 7038 | EXACT_CATALOG_MATCH | EXACT_CATALOG_MATCH |
| đuôi heo tươi | 7038 | PRESET_ALIAS_MATCH | PRESET_ALIAS_MATCH |
| đuôi lợn tươi | 7038 | CLEANED_NAME_MATCH | CLEANED_NAME_MATCH |
| đuôi heo đuôi lợn | 7038 | SUBPHRASE_CATALOG_MATCH | SUBPHRASE_CATALOG_MATCH |
| gan bò | 7039 | EXACT_CATALOG_MATCH | EXACT_CATALOG_MATCH |
| gan gà | 7040 | EXACT_CATALOG_MATCH | EXACT_CATALOG_MATCH |
| gan vịt | 7042 | EXACT_CATALOG_MATCH | EXACT_CATALOG_MATCH |
| lưỡi bò | 7044 | EXACT_CATALOG_MATCH | EXACT_CATALOG_MATCH |
| lưỡi lợn | 7045 | EXACT_CATALOG_MATCH | EXACT_CATALOG_MATCH |
| tim bò | 7055 | EXACT_CATALOG_MATCH | EXACT_CATALOG_MATCH |
| tim lợn | 7057 | EXACT_CATALOG_MATCH | EXACT_CATALOG_MATCH |
| đuôi bò | 7037 | EXACT_CATALOG_MATCH | EXACT_CATALOG_MATCH |
| đuôi | 7037 | PRESET_ALIAS_MATCH | PRESET_ALIAS_MATCH |
| mỡ heo | 7016 | PRESET_ALIAS_MATCH | PRESET_ALIAS_MATCH |
| mỡ lợn | 7016 | PRESET_ALIAS_MATCH | PRESET_ALIAS_MATCH |
| pig tail | 11005 | BERT_BATCH_GPU_MATCH | BERT_BATCH_GPU_MATCH |
| ZZ deprecated 20079 -> 7038 | 14011 | BERT_BATCH_GPU_MATCH | BERT_BATCH_GPU_MATCH |

English pig tail and the marker are neural diagnostic probes: their candidates exclude 20079; no new English tail alias or broader neural correction is part of this repair.

## Canonical propagation

| Artifact | Changed logical records |
|---|---:|
| canonical_recipes.csv | 60 |
| canonical_recipe_ingredients.csv | 71 |
| recipe_canonical_mapping.csv | 56 |

Canonical ID drift = 0; representative drift = 0. Changes remain within the reviewed groups. The 71 canonical ingredients comprise 17 tails + 52 previously matched corruption-scope rows + 2 newly matched chicken hearts. Mapping changes are selection/quality metrics, not membership or representative changes.

## Embeddings and validation

Embeddings: {"rebuilt": true, "tracked": false, "shape": [750, 768], "sha256": "9660451dafa865b8918f5a09f80a8a5cc9b2c231e1df1828093ae10bfde23ad2", "next_load_equal": true, "build_inputs": {"7038": "Đuôi lợn (Thịt và sản phẩm chế biến)", "7041": "Gan lợn (Thịt và sản phẩm chế biến)", "7056": "Tim gà (Thịt và sản phẩm chế biến)", "20079": "ZZ deprecated 20079 -> 7038 (Thịt và sản phẩm chế biến)"}, "input_sha256": "58fef92b7fbae2577fa88762e1947ecbe0fbf49f5f9107b581b707be20574287"}

Validation: {"complete": true, "processed_parity": true, "canonical_parity": true, "canonical_check": true, "canonical_determinism": true, "interim_unchanged": true, "exact_git_baseline_scope": true, "all_72_rows_replayed_single_and_batch": true, "unrelated_ingredient_changes": 0, "unrelated_recipe_changes": 0, "source_context_and_weights_unchanged": true, "interim_git_diff_empty": true, "dry_run_zero_byte_changes": true, "idempotent_apply_zero_byte_changes": true, "cache_unchanged_on_idempotent_rerun": true}

Tests: {"focused": "51 passed (final script revision)", "practical_suite": "1459 passed; 11 subtests passed", "excluded": ["tests/test_api_endpoints.py", "tests/test_smart_input.py"], "warnings": "2300 existing parser DeprecationWarnings", "prior_assertions_adjusted": ["Batch A synthetic m? g? fixture", "Batch A alias count 4676 -> 4674 with explicit removed-key checks", "Batch A followup alias count 4676 -> 4674 with explicit removed-key checks"]}

Prior-test adjustments: removed the synthetic mỡ gà preservation fixture; updated both historical alias-count checks from 4676 to 4674 and pinned the two removals. Unrelated drift guards remain intact.

Excluded: Other 9 extension duplicate pairs; Other corrupted display-name codes; Tail weight estimation; Tim Heo Xào Măng Tây; Global stale cleaned_name; New catalog identities; Historical/interim data.

No commit or push.

## Git validation and changed files

git diff --check: passed.

Branch: fix/matching-data-followups. All changes remain unstaged.

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
 M nlp/entity_matcher.py
 M tests/test_meat_band_batch_a_alias_safe_fix.py
 M tests/test_meat_band_batch_a_followup_safe_fix.py
?? reports/eda/catalog_integrity_fix/applied_fix.json
?? reports/eda/catalog_integrity_fix/applied_fix.md
?? scripts/eda/apply_catalog_integrity_safe_fix.py
?? scripts/eda/catalog_integrity_reviewed_state.json
?? tests/test_catalog_integrity_safe_fix.py
```
