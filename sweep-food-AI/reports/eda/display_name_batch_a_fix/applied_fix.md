# Display-name corruption repair, Batch A

Policy: DISPLAY_NAME_BATCH_A. 1188 ingredient rows / 1104 source recipes.

Only `name_vi` changes in the catalog. Codes, `name_en`, categories and all nutrition columns are untouched; each replacement is the identity the row's own `name_en` already asserts.

## Exact catalog changes

| Code | Field | Before | After | name_en (unchanged) |
|---|---|---|---|---|
| 4073 | name_vi | Rau mùi (ngò rí) | Rau giền đỏ | Amaranth, sp. Red, raw |
| 4055 | name_vi | Mùi tàu (ngò gai) | Mướp đắng | Balsam-pear,  Bitter gourd, raw |
| 5047 | name_vi | Quả quất (tắc) | Quít | Tangerine; Orange; Mandarin, raw |
| 8050 | name_vi | Tôm đồng | Tép khô | Shrimp, fresh water, tiny, dried |

## Exact alias changes

Alias map size 4672.

| Alias | Before | After |
|---|---|---|
| bột rau mùi | 4081 | removed |
| gốc ngò rí | 4055 | 4081 |
| hạt rau mùi | 4081 | removed |
| lá ngò gai | 4055 | 4082 |
| lá ngò gai lá | 4055 | 4082 |
| mùi tàu | 4055 | 4082 |
| ngò | 4073 | 4081 |
| ngò gai | 4055 | 4082 |
| ngò gai cắt nhỏ | 4055 | 4082 |
| ngò gai cắt nhỏ lá | 4055 | 4082 |
| ngò gai lá | 4055 | 4082 |
| ngò ri | 4073 | 4081 |
| ngò rí | 4073 | 4081 |
| ngò rí cắt nhuyễn | 4055 | 4081 |
| ngò rí cắt nhỏ | 4073 | 4081 |
| ngò rí rau nêm | 4073 | 4081 |
| ngò rí rau nêm cắt nhỏ | 4073 | 4081 |
| nước cốt tắc | 5047 | 5046 |
| quả quất | 5047 | 5046 |
| quả tắc | 5047 | 5046 |
| quất | 5047 | 5046 |
| rau nêm ngò | 4073 | 4081 |
| rau nêm ngò gai | 4055 | 4082 |
| rau nêm ngò gai cắt nhỏ | 4055 | 4082 |
| rau nêm ngò rí | 4073 | 4081 |
| rau nêm ngò rí cắt nhỏ | 4073 | 4081 |
| rễ ngò | 4055 | 4081 |
| trái tắc | 5047 | 5046 |
| tép đồng | 8050 | 8049 |
| tôm sông | 8050 | 8052 |
| tôm đất | 8050 | 8052 |
| tôm đất tươi | 8050 | 8052 |
| tôm đất xay | 8050 | 8052 |
| tắc | 5047 | 5046 |
| tắc 1 | 5047 | 5046 |
| tắc cắt lát | 5047 | 5046 |
| tắc tươi | 5047 | 5046 |
| vài cọng ngò rí | 4073 | 4081 |
| vài nhánh ngò gai | 4055 | 4082 |
| vài nhánh ngò rí | 4073 | 4081 |
| ăn kèm ngò gai | 4055 | 4082 |
| ăn kèm ngò rí | 4073 | 4081 |

Reviewed aliases that were always correct against `name_en` and stay put: `rau giền đỏ tươi` → 4073, `mướp đắng tươi` → 4055, `quít tươi` → 5047, `tép khô sống` → 8050.

Deliberately unchanged: the broad `khô` → 5029 and `đồng` aliases, and `mướp đắng`/`khổ qua` → 4050 (Batch B).

## Coriander seed/powder guard

Guard reason `CORIANDER_SEED_POWDER_NO_CATALOG_TARGET`, applied on both `match` and `match_batch`. The catalog has no coriander seed or powder identity, and removing the two aliases alone does not reach UNMATCHED: `rau mùi` is a catalog subphrase head, so both phrases fall through to SUBPHRASE_CATALOG_MATCH 4081 at 0.95. The guard blocks 20 reviewed rows; only the 4 that carried a code change state.

## Processed rows and nutrition

Nutrition sums include known values only; missing values remain null. Exact before/after records for all 1188 ingredient rows and 1104 recipes are in [applied_fix.json](applied_fix.json).

| Cohort | Source | Target | Rows | Recipes | kcal delta | Protein delta | Fat delta | Carbs delta |
|---|---|---|---:|---:|---:|---:|---:|---:|
| coriander_leaf_4073_to_4081 | 4073 | 4081 | 785 | 766 | -7734.5 | -178.4 | 4.7 | -1754.8 |
| culantro_4073_to_4082 | 4073 | 4082 | 43 | 43 | -759.9 | -51.6 | 11.5 | -157.8 |
| parsley_4073_to_20036 | 4073 | 20036 | 2 | 2 | -17.6 | -0.4 | 0.8 | -2.4 |
| coriander_leaf_4055_to_4081 | 4055 | 4081 | 21 | 21 | 42.2 | 36.5 | 6.8 | -40.9 |
| culantro_4055_to_4082 | 4055 | 4082 | 215 | 211 | 2449.0 | 298.1 | 132.7 | 35.8 |
| quat_tac_5047_to_5046 | 5047 | 5046 | 76 | 72 | 232.3 | 11.5 | 0 | 47.5 |
| tom_dat_8050_to_8052 | 8050 | 8052 | 33 | 33 | -10113.5 | -2339.1 | -67.8 | -39.5 |
| seed_powder_to_unmatched | - | UNMATCHED | 4 | 4 | -7.4 | -0.9 | 0.0 | -0.9 |
| bitter_gourd_4050_to_4055 | 4050 | 4055 | 1 | 1 | -4.0 | -0.2 | 0 | -0.8 |
| tep_kho_5029_to_8050 | 5029 | 8050 | 8 | 8 | -149.6 | 500.7 | 26.4 | -596.8 |

| Nutrient | Before known sum | After known sum | Delta | Nulls before → after |
|---|---:|---:|---:|---:|
| calories | 44419.8 | 28356.8 | -16063.0 | 0 → 4 |
| protein_g | 4890.6 | 3166.8 | -1723.8 | 0 → 4 |
| fat_g | 264.3 | 379.4 | 115.1 | 321 → 81 |
| carbs_g | 5585.9 | 3075.3 | -2510.6 | 0 → 37 |

Corpus-wide null counts after: {"calories": 8466, "protein_g": 16924, "fat_g": 20239, "carbs_g": 17425}.

Recipe status transitions: {"recipes_with_changed_missing_count": 4, "recipes_with_status_label_changed": 1, "status_transitions": {"unchanged": 1103, "COMPLETE -> PARTIAL": 1}}.

## Final populations

| Code | Rows |
|---|---:|
| 4073 | 0 |
| 4055 | 1 |
| 5047 | 0 |
| 8050 | 8 |
| 4081 | 904 |
| 4082 | 265 |
| 5046 | 80 |
| 8052 | 33 |
| 20036 | 48 |
| 5029 | 2 |
| 4050 | 56 |
| UNMATCHED | 8466 |

## Matcher replay

| Query | Code | Single route | Batch route |
|---|---|---|---|
| rau giền đỏ | 4073 | EXACT_CATALOG_MATCH | EXACT_CATALOG_MATCH |
| mướp đắng | 4055 | EXACT_CATALOG_MATCH | EXACT_CATALOG_MATCH |
| quít | 5047 | EXACT_CATALOG_MATCH | EXACT_CATALOG_MATCH |
| tép khô | 8050 | EXACT_CATALOG_MATCH | EXACT_CATALOG_MATCH |
| rau giền đỏ tươi | 4073 | CLEANED_NAME_MATCH | CLEANED_NAME_MATCH |
| mướp đắng tươi | 4055 | CLEANED_NAME_MATCH | CLEANED_NAME_MATCH |
| quít tươi | 5047 | CLEANED_NAME_MATCH | CLEANED_NAME_MATCH |
| tép khô sống | 8050 | PRESET_ALIAS_MATCH | PRESET_ALIAS_MATCH |
| ngò rí | 4081 | PRESET_ALIAS_MATCH | PRESET_ALIAS_MATCH |
| ngò | 4081 | PRESET_ALIAS_MATCH | PRESET_ALIAS_MATCH |
| rau nêm ngò rí | 4081 | PRESET_ALIAS_MATCH | PRESET_ALIAS_MATCH |
| rễ ngò | 4081 | PRESET_ALIAS_MATCH | PRESET_ALIAS_MATCH |
| gốc ngò rí | 4081 | PRESET_ALIAS_MATCH | PRESET_ALIAS_MATCH |
| ngò rí cắt nhuyễn | 4081 | PRESET_ALIAS_MATCH | PRESET_ALIAS_MATCH |
| rau mùi | 4081 | EXACT_CATALOG_MATCH | EXACT_CATALOG_MATCH |
| rễ và gốc rau mùi | 4081 | PRESET_ALIAS_MATCH | PRESET_ALIAS_MATCH |
| rau mùi thái nhỏ | 4081 | PRESET_ALIAS_MATCH | PRESET_ALIAS_MATCH |
| ngò gai | 4082 | PRESET_ALIAS_MATCH | PRESET_ALIAS_MATCH |
| mùi tàu | 4082 | PRESET_ALIAS_MATCH | PRESET_ALIAS_MATCH |
| lá ngò gai | 4082 | PRESET_ALIAS_MATCH | PRESET_ALIAS_MATCH |
| rau mùi tàu | 4082 | EXACT_CATALOG_MATCH | EXACT_CATALOG_MATCH |
| ngò tây | 20036 | PRESET_ALIAS_MATCH | PRESET_ALIAS_MATCH |
| mùi tây | 20036 | PRESET_ALIAS_MATCH | PRESET_ALIAS_MATCH |
| parsley | 20036 | PRESET_ALIAS_MATCH | PRESET_ALIAS_MATCH |
| tắc | 5046 | PRESET_ALIAS_MATCH | PRESET_ALIAS_MATCH |
| quất | 5046 | PRESET_ALIAS_MATCH | PRESET_ALIAS_MATCH |
| nước cốt tắc | 5046 | PRESET_ALIAS_MATCH | PRESET_ALIAS_MATCH |
| quất chín | 5046 | EXACT_CATALOG_MATCH | EXACT_CATALOG_MATCH |
| tôm đất | 8052 | PRESET_ALIAS_MATCH | PRESET_ALIAS_MATCH |
| tôm sông | 8052 | PRESET_ALIAS_MATCH | PRESET_ALIAS_MATCH |
| tôm đồng | 8052 | EXACT_CATALOG_MATCH | EXACT_CATALOG_MATCH |
| tép đồng | 8049 | PRESET_ALIAS_MATCH | PRESET_ALIAS_MATCH |
| tép gạo | 8049 | EXACT_CATALOG_MATCH | EXACT_CATALOG_MATCH |
| tôm biển | 8051 | EXACT_CATALOG_MATCH | EXACT_CATALOG_MATCH |
| tôm khô | 8053 | PRESET_ALIAS_MATCH | PRESET_ALIAS_MATCH |
| hạt rau mùi | UNMATCHED | UNMATCHED | UNMATCHED |
| bột rau mùi | UNMATCHED | UNMATCHED | UNMATCHED |
| bột và hạt rau mùi corriander | UNMATCHED | UNMATCHED | UNMATCHED |
| hạt ngò | UNMATCHED | UNMATCHED | UNMATCHED |
| bột hạt ngò | UNMATCHED | UNMATCHED | UNMATCHED |
| hạt mùi | UNMATCHED | UNMATCHED | UNMATCHED |
| bột ngò ta | UNMATCHED | UNMATCHED | UNMATCHED |
| coriander seeds | UNMATCHED | UNMATCHED | UNMATCHED |
| coriander powder | UNMATCHED | UNMATCHED | UNMATCHED |
| rau giền cơm | 4072 | EXACT_CATALOG_MATCH | EXACT_CATALOG_MATCH |
| rau giền trắng | 4074 | EXACT_CATALOG_MATCH | EXACT_CATALOG_MATCH |
| khổ qua | 4050 | PRESET_ALIAS_MATCH | PRESET_ALIAS_MATCH |
| mít khô | 5029 | EXACT_CATALOG_MATCH | EXACT_CATALOG_MATCH |
| măng tre | 4053 | EXACT_CATALOG_MATCH | EXACT_CATALOG_MATCH |

## Canonical propagation

| Artifact | Changed logical records |
|---|---:|
| canonical_recipes.csv | 1065 |
| canonical_recipe_ingredients.csv | 1146 |
| recipe_canonical_mapping.csv | 285 |

Canonical ID drift = 0; representative drift = 0.

## Embeddings and validation

Embeddings: {"rebuilt": true, "tracked": false, "shape": [750, 768], "sha256": "0211440329d5d93bdfa8b895c486cc22c811fdbc240187c9843c3a5438d60ea9", "next_load_equal": true, "input_sha256": "2088046232a91876d4bb18e3377013d2a0efa41a04e60771b0fb362467d921ef", "build_inputs": {"4055": "Mướp đắng (Rau, quả, củ dùng làm rau)", "4073": "Rau giền đỏ (Rau, quả, củ dùng làm rau)", "5047": "Quít (Quả chín)", "8050": "Tép khô (Thủy sản và sản phẩm chế biến)"}}

Validation: {"complete": true, "processed_parity": true, "canonical_parity": true, "canonical_check": true, "canonical_determinism": true, "interim_unchanged": true, "rows_changed_vs_git_head": 1188, "recipes_changed_vs_git_head": 1104, "catalog_rows_changed_vs_git_head": 4, "alias_keys_changed_vs_git_head": 42, "unexpected_rows_changed": 0, "canonical_changed_vs_git_head": {"canonical_recipe_ingredients.csv": 1146, "canonical_recipes.csv": 1065, "recipe_canonical_mapping.csv": 285}}

Tests: {"focused": "223 passed (tests/test_display_name_batch_a_safe_fix.py)", "practical_suite": "1682 passed; 11 subtests passed", "excluded": ["tests/test_api_endpoints.py", "tests/test_smart_input.py"], "warnings": "2300 pre-existing parser DeprecationWarnings", "prior_assertions_adjusted": ["alias count 4674 -> 4672 with the two removed keys pinned (both meat-band files)", "Qwen ngo rule pin 4073/Rau mui (ngo ri) -> 4081/Rau mui", "qwen_candidate_eligibility winning_code pin 4073 -> 4081", "eligibility denominator 46 -> 47 with the newly eligible cleared row"]}

Excluded: 56 khổ qua rows on 4050 (Batch B); khổ qua rừng rows; broad khô alias; broad đồng alias; parsley misroutes outside this classification; generic rau dền; beetroot / galangal false textual matches; mandarin peel rows; recipe-title rows; 4010 / 4016; 4050 / 4121 chain beyond d6f83055; duplicate extension pairs; catalog gaps; dangling 13038; global stale cleaned_name; parser fixes.

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
 M nlp/entity_matcher.py
 M nlp/qwen_matching.py
 M tests/test_meat_band_batch_a_alias_safe_fix.py
 M tests/test_meat_band_batch_a_followup_safe_fix.py
 M tests/test_qwen_eligibility_guard.py
 M tests/test_qwen_mapper_rule_repair_batch2.py
 M tests/test_qwen_matching.py
?? reports/eda/display_name_batch_a_fix/
?? scripts/eda/apply_display_name_batch_a_safe_fix.py
?? scripts/eda/display_name_batch_a_reviewed_state.json
?? tests/test_display_name_batch_a_safe_fix.py
```
