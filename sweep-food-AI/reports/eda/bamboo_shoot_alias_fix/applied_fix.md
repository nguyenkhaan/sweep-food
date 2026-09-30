# Bamboo-shoot alias corruption repair

Policy: BAMBOO_SHOOT_ALIAS_FIX. 55 ingredient rows / 50 source recipes.

## Root cause

Three alias keys have pointed at the wrong catalog identity since the original dataset commit: `măng khô` at 4048 Lá mơ lông (skunk vine, not bamboo) and `măng tươi` / `măng tươi bào` at 4051 Măng tre, khô (dried, for explicitly fresh rows). All three resolve at PRESET_ALIAS_MATCH 0.98, the earliest scored stage, so 55 rows carried the wrong identity and the wrong nutrition with high confidence while the already-correct siblings `măng tre khô` and `măng tre tươi` sat beside them contradicting them.

The catalog is **not** modified and embeddings are **not** rebuilt. All four identities below are raw Viện Dinh Dưỡng source rows, not project extensions, and the repair uses the preparation state each row's own `name_en` already asserts.

| Code | name_vi | name_en | kcal/100 g | water g/100 g |
|---|---|---|---:|---:|
| 4048 | Lá mơ lông | Skunk vine, raw | 48 | 86.1 |
| 4050 | Măng chua, măng tre | Bamboo shoot, fermented, raw | 28 | 92.8 |
| 4051 | Măng tre, khô | Bamboo shoot, dried | 301 | 23 |
| 4053 | Măng tre | Bamboo shoots, raw | 31 | 92 |

## Exact alias changes

Alias map size 4672 (unchanged; nothing added, nothing removed).

| Alias | Before | After | Why |
|---|---|---|---|
| măng khô | 4048 `Lá mơ lông` | 4051 `Măng tre, khô` | skunk vine is not bamboo; agrees with the existing `măng tre khô` → 4051 |
| măng tươi | 4051 `Măng tre, khô` | 4053 `Măng tre` | explicit `tươi`; agrees with the existing `măng tre tươi` → 4053 |
| măng tươi bào | 4051 `Măng tre, khô` | 4053 `Măng tre` | explicit `tươi`; `bào` is a cut, not a state |

Reviewed aliases that were already correct and stay put: `măng` → 4051, `măng tre khô` → 4051, `măng tre` → 4053, `măng tre tươi` → 4053, `măng chua` → 4050, `măng muối` → 4050, `măng le chua` → 4050, `măng chua măng tre` → 4050, `lá mơ lông` → 4048, `lá mơ lông tươi` → 4048, `măng tây` → 20033, `măng cụt` → 5061.

## Processed rows and nutrition

Nutrition sums include known values only; missing values remain null. Every populated value is the live target catalog column scaled by the row's own weight. Exact before/after records for all 55 ingredient rows and 50 recipes are in [applied_fix.json](applied_fix.json).

| Cohort | Cleaned name | Source | Target | Rows | Recipes | kcal | Protein | Fat | Carbs |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| mang_kho_4048_to_4051 | `măng khô` | 4048 | 4051 | 20 | 20 | 12017.5 | 432.3 | 99.8 | 2351.2 |
| mang_tuoi_4051_to_4053 | `măng tươi` | 4051 | 4053 | 32 | 29 | -31401.0 | -1314.2 | -219.8 | -6037.0 |
| mang_tuoi_bao_4051_to_4053 | `măng tươi bào` | 4051 | 4053 | 3 | 3 | -1755.0 | -73.6 | -12.3 | -337.4 |

| Nutrient | Before known sum | After known sum | Delta | Nulls before → after |
|---|---:|---:|---:|---:|
| calories | 39242.8 | 18104.3 | -21138.5 | 0 → 0 |
| protein_g | 1781.6 | 826.1 | -955.5 | 0 → 0 |
| fat_g | 257.9 | 125.6 | -132.3 | 20 → 0 |
| carbs_g | 7441.0 | 3417.8 | -4023.2 | 0 → 0 |

The only null transition is `fat_g` null → real on the 20 `măng khô` rows: 4048 carries no fat figure and 4051 carries 2.1 g/100 g, so the value comes from the live target catalog. Nothing moves value → null and no missing nutrient is coerced to zero.

Corpus-wide null counts after: {"calories": 8465, "protein_g": 16923, "fat_g": 20219, "carbs_g": 17424}.

Recipe rollups: {"recipes_with_changed_missing_count": 0, "recipes_with_status_label_changed": 0, "status_transitions": {}} — `missing_nutrition_count` keys on null calories only, and no reviewed row has null calories before or after, so no recipe changes label.

## Final populations

| Code | Rows |
|---|---:|
| 4048 | 1 |
| 4051 | 34 |
| 4053 | 37 |
| 4050 | 62 |
| 4055 | 57 |
| 4121 | 0 |
| 20033 | 51 |
| 5061 | 6 |
| UNMATCHED | 8465 |

## Reviewed keeps, measured

Verified against the repaired data, not asserted: {"sour_bamboo_rows": 62, "fresh_bamboo_exact_rows": 2, "unmatched_bamboo_rows": 36, "rows_on_20033": 51, "rows_on_5061": 6}. The single genuine `Lá mơ lông` row is the entire 4048 population after the repair.

## Matcher replay

| Query | Code | Single route | Batch route |
|---|---|---|---|
| măng khô | 4051 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| măng tươi | 4053 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| măng tươi bào | 4053 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| măng tre khô | 4051 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| măng tre | 4053 | EXACT_CATALOG_MATCH 1.0 | EXACT_CATALOG_MATCH 1.0 |
| măng tre tươi | 4053 | CLEANED_NAME_MATCH 0.99 | CLEANED_NAME_MATCH 0.99 |
| măng | 4051 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| măng chua | 4050 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| măng chua ớt | 4050 | SUBPHRASE_CATALOG_MATCH 0.95 | SUBPHRASE_CATALOG_MATCH 0.95 |
| măng muối | 4050 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| măng le chua | 4050 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| măng chua măng tre | 4050 | PRESET_ALIAS_MATCH 0.98 | PRESET_ALIAS_MATCH 0.98 |
| lá mơ lông | 4048 | EXACT_CATALOG_MATCH 1.0 | EXACT_CATALOG_MATCH 1.0 |
| lá mơ lông tươi | 4048 | CLEANED_NAME_MATCH 0.99 | CLEANED_NAME_MATCH 0.99 |
| măng tây | 20033 | EXACT_CATALOG_MATCH 1.0 | EXACT_CATALOG_MATCH 1.0 |
| măng cụt | 5061 | EXACT_CATALOG_MATCH 1.0 | EXACT_CATALOG_MATCH 1.0 |

Cultivar and preparation phrases with no catalog identity keep their pre-existing neural verdicts and acquire no dictionary route — the repair does not widen the bamboo band: `măng le` → 5023, `măng sặt` → 5010, `măng trúc` → 4053, `măng nứa` → 5061, `măng vầu` → 4053, `măng non` → 5061, `măng vàng` → 2026, `măng luộc` → 2012002.

## Bare `măng` — DEFERRED_NEEDS_DOMAIN_REVIEW

`bare_mang_ambiguous_state_resolution = DEFERRED_NEEDS_DOMAIN_REVIEW`. Alias: măng -> 4051 (unchanged). Rows: 14, asserted byte-for-byte unchanged.

- **Corpus evidence.** 8 of the 14 raw lines read `măng luộc` (boiled) and 6 are bare. None carries khô, tươi or chua, while every dried row in the corpus says khô, every fresh row says tươi and every fermented row says chua. The corpus therefore offers no positive evidence for a single identity.
- **Why not 4053.** Fresh is only the residual after eliminating dried and fermented. AGENTS.md section 5 requires broad aliases to clear a higher evidence bar than qualified ones, and elimination is not that evidence.
- **Why not removed.** Removal does not reach UNMATCHED. `măng` is 4 characters, so SUBPHRASE_CATALOG_MATCH picks it up at 0.95 against the catalog heads `măng tre` (4051) and `măng chua` (4050): measured, the single route lands on 4051 and the batch route on 4050. Production uses match_batch, so deletion would silently move 14 rows onto fermented bamboo AND manufacture a match()/match_batch() divergence that does not exist today.
- **Why not cleared.** Clearing the rows without removing the alias is not durable: a reprocess re-applies PRESET_ALIAS_MATCH. A durable clear needs a terminal guard in the chicken-fat / coriander-seed style, which is a separate decision.
- **Nutrition left wrong.** The 14 rows keep dried-bamboo nutrition, which is known to be wrong in magnitude (`Măng luộc 500 gr` = 1505 kcal). This is recorded as a deferred defect, not as an accepted value.
- **Parser note.** clean_culinary_query strips `tươi` but preserves `khô`, so bare `măng` is structurally enriched with fresh phrases and cannot receive dried ones. Reported as evidence for the future decision; parser behaviour is not changed.

## Canonical propagation

| Artifact | Changed logical records |
|---|---:|
| canonical_recipes.csv | 46 |
| canonical_recipe_ingredients.csv | 51 |
| recipe_canonical_mapping.csv | 20 |

The 50 affected recipes span 49 canonical groups. 4 of the reviewed rows belong to non-winning duplicates and so do not appear in `canonical_recipe_ingredients.csv`, which is also why 46 representative rows change rather than 49. 20 mapping rows change content, all of them `măng khô` recipes, and only in `candidate_score`, `negative_nutrition_anomaly_rate`, `negative_recipe_nutrition_anomalies`, `nutrition_anomaly_count`, `selection_score` — clearing a null fat clears a nutrition anomaly. The 35 fresh-bamboo rows swap one fully populated identity for another and move no counter. Canonical ID drift = 0; representative drift = 0.

## Embeddings and validation

Embeddings: {"rebuilt": false, "tracked": false, "reused_existing_cache": true, "shape": [750, 768], "sha256": "f20dd5c79f8cf89155a94fba70a6f9c853ea0eb6c960fcd02f3692710bfacc36", "input_sha256": "7275367f7196ed8a9af827790ab8b45312060d863b307cd1cf41f94935c52115"}

Validation: {"complete": true, "processed_parity": true, "canonical_parity": true, "canonical_check": true, "canonical_determinism": true, "interim_unchanged": true, "catalog_unchanged": true, "embeddings_unchanged": true, "rows_changed_vs_git_head": 55, "recipes_changed_vs_git_head": 50, "catalog_rows_changed_vs_git_head": 0, "alias_keys_changed_vs_git_head": 3, "unexpected_rows_changed": 0, "canonical_changed_vs_git_head": {"canonical_recipe_ingredients.csv": 51, "canonical_recipes.csv": 46, "recipe_canonical_mapping.csv": 20}}

Tests: {"focused": "tests/test_bamboo_shoot_alias_safe_fix.py: 117 passed (torch), 109 passed / 8 skipped (no torch)", "siblings": "tests/test_display_name_batch_a_safe_fix.py + tests/test_display_name_batch_b_safe_fix.py + focused: 472 passed", "full_practical_suite": "1931 passed, 11 subtests passed, 0 failed", "excluded": "tests/test_api_endpoints.py and tests/test_smart_input.py do not collect without fastapi (AGENTS.md section 15, pre-existing)", "interpreter": ".venv-1 (torch 2.14.0+cpu) for neural probes; .venv (no torch) also green"}

Excluded: bare `măng` -> 4051 and its 14 rows; 36 UNMATCHED cultivar/typo/fragment bamboo rows; cultivar-level identities (măng le, nứa, vầu, sặt, trúc, vàng) have no catalog target; 4121 vs 20077 duplicate resolution; 4010 / 4016; 4052 / 20033; 4058 / 20037; 4044 / 20062; other catalog-gap codes; broad parser architecture; clean_culinary_query stripping `tươi` but preserving `khô`; match()/match_batch() structural divergence; stale code-space contamination generally.

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
 M scripts/eda/apply_display_name_batch_a_safe_fix.py
 M scripts/eda/apply_display_name_batch_b_safe_fix.py
 M tests/test_display_name_batch_b_safe_fix.py
?? reports/eda/bamboo_shoot_alias_fix/
?? scripts/eda/apply_bamboo_shoot_alias_safe_fix.py
?? scripts/eda/bamboo_shoot_alias_reviewed_state.json
?? tests/test_bamboo_shoot_alias_safe_fix.py
```
