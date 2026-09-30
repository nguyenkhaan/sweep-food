# Display-name corruption repair, Batch B

Policy: DISPLAY_NAME_BATCH_B. 118 ingredient rows / 110 source recipes.

The 4121 → 4050 → 4055 chain. Only `name_vi` changes in the catalog: codes, `name_en`, categories and all nutrition columns are untouched, and each replacement is the identity the row's own `name_en` already asserts. 4055 is Batch A's repair and is not modified here.

## Exact catalog changes

| Code | Field | Before | After | name_en (unchanged) | Subphrase head |
|---|---|---|---|---|---|
| 4050 | name_vi | Mướp đắng (khổ qua) | Măng chua, măng tre | Bamboo shoot, fermented, raw | `măng chua` |
| 4121 | name_vi | Măng muối (măng chua) | Kiệu muối | Onion shallot, scallion, pickled with salt | `kiệu muối` |

The punctuation is reviewed. The matcher indexes `normalize_vietnamese_text(name_vi.split(",")[0])` as a subphrase retrieval head, so the comma in 4050 publishes `măng chua` — which is exactly what recovers `Măng chua ớt 500 gr` at SUBPHRASE_CATALOG_MATCH 0.95. 4121 is deliberately comma-less: a raw `Kiệu, muối` would publish a bare `kiệu` head and hand every ambiguous kiệu row a 0.95 match onto a pickle identity nobody reviewed.

## Exact alias changes

Alias map size 4672 (unchanged; nothing added, nothing removed).

| Alias | Before | After |
|---|---|---|
| khổ qua | 4050 | 4055 |
| khổ qua bào | 4050 | 4055 |
| măng chua | 4121 | 4050 |
| măng le chua | 4121 | 4050 |
| măng muối | 4121 | 4050 |
| mướp đắng | 4050 | 4055 |
| quả mướp đắng | 4050 | 4055 |
| trái khổ qua | 4050 | 4055 |
| ăn kèm khổ qua | 4050 | 4055 |

Reviewed aliases that were always correct against `name_en` and stay put: `kiệu muối` → 4121, `măng chua măng tre` → 4050, `mướp đắng tươi` → 4055.

All 11 aliases targeting 20077 are unchanged.

## Processed rows and nutrition

Nutrition sums include known values only; missing values remain null. Exact before/after records for all 118 ingredient rows and 110 recipes are in [applied_fix.json](applied_fix.json).

| Cohort | Source | Target | Rows | Recipes | kcal delta | Protein delta | Fat delta | Carbs delta |
|---|---|---|---:|---:|---:|---:|---:|---:|
| sour_bamboo_4121_to_4050 | 4121 | 4050 | 61 | 58 | -146.5 | 14.7 | 0 | -58.9 |
| bitter_gourd_4050_to_4055 | 4050 | 4055 | 56 | 51 | -945.6 | -58.5 | 0 | -166.4 |
| sour_bamboo_chilli_recovery | UNMATCHED | 4050 | 1 | 1 | 140.0 | 7.0 | 0 | 27.5 |

| Nutrient | Before known sum | After known sum | Delta | Nulls before → after |
|---|---:|---:|---:|---:|
| calories | 7558.1 | 6606.0 | -952.1 | 1 → 0 |
| protein_g | 355.8 | 319.0 | -36.8 | 1 → 0 |
| fat_g | 0 | 0 | 0 | 118 → 118 |
| carbs_g | 1515.3 | 1317.5 | -197.8 | 1 → 0 |

The 117 identity remaps alone: calories -1092.1, protein_g -43.8, fat_g 0, carbs_g -225.3, with no null transition in either direction. The recovery of 545ef564 supplies the whole null → value movement (calories, protein and carbs each 1 → 0); `fat_g` stays null on all 118 rows because neither 4050 nor 4055 carries a fat value, and missing fat is never coerced to zero.

### Divergence from the pre-implementation review estimate

The review estimated `carbs_g` -224.9 for the base 117 and -197.4 in total. The measured figures are -225.3 and -197.8. 4 khổ qua rows at 150 g: 4.1 * 1.5 = 6.15 rounds to 6.1 under the project's float scaler and to 6.2 under exact decimal rounding. calories, protein and fat match the estimate exactly. The measured values are pinned because they are what `nlp.nutrition.scale_nutrition` — and therefore the live corpus — actually produces.

Corpus-wide null counts after: {"calories": 8465, "protein_g": 16923, "fat_g": 20239, "carbs_g": 17424}.

Recipe rollups: {"recipes_with_changed_missing_count": 1, "recipes_with_status_label_changed": 0, "missing_count_transitions": {"32a39c4a-c638-49c0-b90a-9d010017146e": {"before": 2, "after": 1}}, "status_transitions": {}}.

## Final populations

| Code | Rows |
|---|---:|
| 4121 | 0 |
| 4050 | 62 |
| 4055 | 57 |
| 20077 | 29 |
| 4048 | 21 |
| 4051 | 49 |
| 4053 | 2 |
| 4054 | 70 |
| UNMATCHED | 8465 |

## Matcher replay

| Query | Code | Single route | Batch route |
|---|---|---|---|
| măng chua | 4050 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| măng muối | 4050 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| măng le chua | 4050 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| măng chua tươi | 4050 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| măng chua ớt | 4050 | SUBPHRASE_CATALOG_MATCH 0.95 | SUBPHRASE_CATALOG_MATCH 0.95 |
| khổ qua | 4055 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| khổ qua bào | 4055 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| trái khổ qua | 4055 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| quả mướp đắng | 4055 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| ăn kèm khổ qua | 4055 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| mướp đắng | 4055 | EXACT_CATALOG_MATCH 1.0 | EXACT_CATALOG_MATCH 1.0 |
| kiệu muối | 4121 | EXACT_CATALOG_MATCH 1.0 | EXACT_CATALOG_MATCH 1.0 |
| măng chua măng tre | 4050 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| mướp đắng tươi | 4055 | CLEANED_NAME_MATCH 0.99 | CLEANED_NAME_MATCH 0.99 |
| măng tre | 4053 | EXACT_CATALOG_MATCH 1.0 | EXACT_CATALOG_MATCH 1.0 |
| măng tre tươi | 4053 | CLEANED_NAME_MATCH 0.99 | CLEANED_NAME_MATCH 0.99 |
| măng khô | 4048 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| măng | 4051 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| măng tươi | 4051 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| măng tây | 20033 | EXACT_CATALOG_MATCH 1.0 | EXACT_CATALOG_MATCH 1.0 |
| khổ qua rừng | 4054 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| mướp | 4054 | EXACT_CATALOG_MATCH 1.0 | EXACT_CATALOG_MATCH 1.0 |
| mướp hương | 4054 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| mướp nhật bản | 4056 | EXACT_CATALOG_MATCH 1.0 | EXACT_CATALOG_MATCH 1.0 |
| kiệu chua | 20077 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| dưa kiệu | 20077 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| củ kiệu chua ngọt | 20077 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| dưa kiệu chua | 20077 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| củ kiệu muối | 20077 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| hành củ muối | 4120 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| dưa giá đậu xanh | 4119 | EXACT_CATALOG_MATCH 1.0 | EXACT_CATALOG_MATCH 1.0 |

Pre-existing `match()` / `match_batch()` divergence, deliberately not fixed:

| Query | Single before | Single after | Batch | Still divergent |
|---|---|---|---|---|
| kiệu | 4101 | 4121 | 20077 | yes |
| củ kiệu | 4101 | 4101 | 20077 | yes |

Bare `kiệu` changes which code its single route reaches (4101 → 4121) because `Kiệu muối` is now a subphrase head, but it stays divergent from the batch route and no stored row moves for it. Both queries remain reviewed deferrals.

## 4121 vs 20077 — DEFERRED_NEEDS_DOMAIN_REVIEW

`4121_vs_20077_duplicate_resolution = DEFERRED_NEEDS_DOMAIN_REVIEW`

- **4121 raw authority.** 4121 is a raw Vien Dinh Duong catalog row: code, name_en "Onion shallot, scallion, pickled with salt", category and all nutrition columns come from the source table. Only its Vietnamese display name was corrupted, and only that is repaired here.
- **20077 authored provenance.** 20077 "Củ kiệu muối (Dưa kiệu chua ngọt)" is a project-authored master extension, not a source-table row. It was added to carry the sweet-sour Tet pickle and owns 11 aliases and 29 processed rows.
- **Preparation ambiguity.** The two are not obviously the same food: 4121 is salt-pickled scallion/shallot bulb, 20077 is the sweetened chua ngọt preparation. Vietnamese usage collapses both under "củ kiệu"/"kiệu", and the corpus contains fresh kiệu, bare kiệu, nước củ kiệu and compound rows that belong to neither without a human reading of each recipe.
- **Nutrition difference.** Per 100 g: 4121 is 29 kcal / 1.3 g protein / null fat / 5.9 g carbs; 20077 is 55 kcal / 1.2 g protein / 0.1 g fat / 12.0 g carbs. Roughly double the energy and carbohydrate, consistent with added sugar. Merging either way would silently restate 29 or 61 rows of nutrition.
- **Why no automatic merge.** No mechanical signal separates them: same category, adjacent semantics, and lexical similarity alone is exactly the evidence AGENTS.md section 5 rejects. Choosing a survivor also decides which nutrition profile 29 reviewed rows inherit and whether 11 aliases move, so it needs a domain decision, not a code change.

Verified preserved: {"rows_on_20077": 29, "aliases_on_20077": ["củ kiệu chua ngọt", "củ kiệu muối", "củ kiệu muối dưa kiệu chua ngọt", "dưa kiệu", "dưa kiệu chua", "dưa kiệu cắt sợi", "kiệu chua", "kiệu chua cắt lát", "kiệu chua cắt sợi", "ăn kèm dưa kiệu", "ăn kèm kiệu chua cắt sợi"], "unmatched_kieu_rows": 18}.

## Canonical propagation

| Artifact | Changed logical records |
|---|---:|
| canonical_recipes.csv | 104 |
| canonical_recipe_ingredients.csv | 112 |
| recipe_canonical_mapping.csv | 1 |

Mapping rows belonging to the 110 affected recipes: 110, spanning 107 canonical groups; only 1 changes content, because the 117 identity remaps swap one valid code for another and move no quality counter. Canonical ID drift = 0; representative drift = 0.

## Embeddings and validation

Embeddings: {"rebuilt": true, "tracked": false, "shape": [750, 768], "sha256": "f20dd5c79f8cf89155a94fba70a6f9c853ea0eb6c960fcd02f3692710bfacc36", "next_load_equal": true, "input_sha256": "7275367f7196ed8a9af827790ab8b45312060d863b307cd1cf41f94935c52115", "build_inputs": {"4050": "Măng chua, măng tre (Rau, quả, củ dùng làm rau)", "4121": "Kiệu muối (Rau, quả, củ dùng làm rau)"}}

Validation: {"complete": true, "processed_parity": true, "canonical_parity": true, "canonical_check": true, "canonical_determinism": true, "interim_unchanged": true, "rows_changed_vs_git_head": 118, "recipes_changed_vs_git_head": 110, "catalog_rows_changed_vs_git_head": 2, "alias_keys_changed_vs_git_head": 9, "unexpected_rows_changed": 0, "canonical_changed_vs_git_head": {"canonical_recipe_ingredients.csv": 112, "canonical_recipes.csv": 104, "recipe_canonical_mapping.csv": 1}}

Tests: {"focused": "128 passed (tests/test_display_name_batch_b_safe_fix.py)", "batch_a_regression": "227 passed (tests/test_display_name_batch_a_safe_fix.py)", "regression_groups": "518 passed, 4 subtests (alias/entity-matcher/data/matching/nutrition/unmatched/canonical/catalog-integrity)", "full_practical_suite": "1814 passed, 11 subtests", "excluded": "tests/test_api_endpoints.py and tests/test_smart_input.py do not collect: fastapi is not installed (pre-existing, AGENTS.md section 15)"}

Excluded: 4121 vs 20077 duplicate resolution; 11 UNMATCHED sweet-sour kiệu rows; fresh kiệu and bare/ambiguous kiệu rows; nước củ kiệu row; compound kiệu row; măng khô -> 4048; măng / măng tươi -> 4051; khổ qua rừng -> 4054; match()/match_batch() structural divergence for kiệu and củ kiệu; d6f83055 stale match_method/confidence; 4010 / 4016; other duplicate-extension pairs; parser behaviour; stale code-space contamination.

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
 M scripts/eda/apply_display_name_batch_a_safe_fix.py
 M tests/test_display_name_batch_a_safe_fix.py
?? reports/eda/display_name_batch_b_fix/
?? scripts/eda/apply_display_name_batch_b_safe_fix.py
?? scripts/eda/display_name_batch_b_reviewed_state.json
?? tests/test_display_name_batch_b_safe_fix.py
```
