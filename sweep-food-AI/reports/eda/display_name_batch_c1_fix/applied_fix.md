# Display-name corruption repair, Batch C1 — mustard greens 4016

Policy: DISPLAY_NAME_BATCH_C1. 345 ingredient rows change identity across 333 source recipes; 10 more rows only refresh a stale display name (355 rows written in total).

## Root cause

Catalog 4016 is the raw Viện Dinh Dưỡng row `Mustard greens, raw`, but its Vietnamese display name read `Dưa chuột (dưa leo)` -- cucumber -- which is 4027's identity, and 4027 already carries `Dưa chuột`. The alias map organised three cucumber keys and 248 processed rows around 4016 as though it were a cucumber, while the genuine mustard greens sat on red cabbage 4011 and bok choy 4015, five more sat stored-UNMATCHED, and spinach, kale, napa and kimchi rows were parked on 4016 because nothing else claimed them.

## Reviewer decision that supersedes the audit

Row `2c660d89` — `1 muỗng cải thảo muối khô` — was **DEFER on repaired 4016** in the audit and is **CLEAR_TO_UNMATCHED** here.

Semantic identity is dried salted napa. No exact catalog identity exists, and the repaired 4016 is fresh mustard greens, so keeping the row on 4016 would knowingly preserve a wrong identity. AGENTS.md section 2 prefers UNMATCHED to a known-wrong target, so the audit deferral is superseded by an explicit clear.

Changed rows 344 -> 345, clears 34 -> 35, final 4016 population 61 -> 60, UNMATCHED 8498 -> 8499, one more corpus null per nutrient, one fewer QWEN_LLM_MATCH row, and a macro delta that is no longer the audit figure.

Every figure below is therefore re-measured from the approved 345-row state rather than carried forward from the audit. The audit macro delta -6697.3 / -377.8 / -26.2 / -1218.5 is recorded as superseded, not reused.

## Catalog

| Code | Field | Before | After | name_en (unchanged) |
|---|---|---|---|---|
| 4016 | name_vi | Dưa chuột (dưa leo) | Cải xanh | `Mustard greens,   raw` |

Every other column is asserted byte-for-byte unchanged: `ash_g`, `calcium_mg`, `carbs_g`, `category_en`, `category_vi`, `code`, `copper_mg`, `energy_kcal`, `fat_g`, `fiber_g`, `folate_food_mcg`, `folate_total_mcg`, `iron_mg`, `magnesium_mg`, `manganese_mg`, `name_en`, `phosphorus_mg`, `potassium_mg`, `protein_g`, `retinol_mcg`, `selenium_mcg`, `sodium_mg`, `sugar_g`, `vitamin_a_rae_mcg`, `vitamin_b1_mg`, `vitamin_b2_mg`, `vitamin_b3_mg`, `vitamin_b5_mg`, `vitamin_b6_mg`, `vitamin_c_mg`, `water_g`, `zinc_mg`. Catalog row count stays 750.

`Cải bẹ trắng (cải thìa/thảo)` was **not** used: it would reactivate the disabled Qwen rule ("cải con", "cải mầm", "cải thìa") -> 4016 "Cải bẹ trắng (cải thìa/thảo)" through the A1 identity check, republishing the bok-choy/napa identity this batch removes from 4016. Qwen mapper rules after the repair: 29 active / 20 disabled, unchanged, with that rule still disabled and `map_clean_to_master` still unresolved for all three of its terms.

Colliding display names before: `nấm kim châm`, `thịt trâu, đùi`. After: `nấm kim châm`, `thịt trâu, đùi` — unchanged; `Cải xanh` is unique in the catalog and `Dưa chuột (dưa leo)` was never a duplicate of 4027 `Dưa chuột`, which is why the corruption survived a duplicate-name sweep.

## Exact alias changes

20 actions. Map size 4674 − 2 removed + 8 added = 4680.

| Action | Alias | Before | After |
|---|---|---|---|
| repointed | cải bẹ | 4011 | 4016 |
| repointed | cải bẹ xanh | 4011 | 4016 |
| repointed | cải canh | 4011 | 4016 |
| repointed | cải xanh | 4011 | 4016 |
| repointed | dưa leo | 4016 | 4027 |
| repointed | dưa leo cắt sợi | 4016 | 4027 |
| repointed | rau cải bẹ xanh | 4011 | 4016 |
| repointed | rau cải xanh | 4011 | 4016 |
| repointed | ăn kèm cải bẹ xanh | 4011 | 4016 |
| repointed | ăn kèm dưa leo | 4016 | 4027 |
| removed | cải cải bó xôi | 4016 | — |
| removed | cải xoăn | 4016 | — |
| added | cải bẹ xanh 1 2cm để riêng phần cọng và lá | — | 4016 |
| added | cải bẹ xanh con | — | 4016 |
| added | cải bẹ xanh nhỏ | — | 4016 |
| added | cải bẹ xanh to | — | 4016 |
| added | kimchi cải thảo | — | 20034 |
| added | lá cải thảo | — | 4109 |
| added | lá cải xanh | — | 4016 |
| added | rau cải canh | — | 4016 |

Reviewed aliases that were already correct and stay put: `cải xanh tươi` → 4016, `cải thảo` → 4109, `rau cải thảo` → 4109, `kim chi cải thảo` → 20034, `cải thảo kim chi` → 20034, `cải thìa` → 4135, `dưa chuột` → 4027, `dưa chuột tươi` → 4027, `dưa chuột muối` → 4118, `dưa leo baby` → 4034, `dưa cải bẹ` → 4116, `cải` → 4013, `cải trắng` → 4021, `cải mầm` → 20050, `mầm cải` → 20050, `bông cải xanh` → 4094, `bông cải xanh cắt nhỏ` → 4094, `ăn kèm bông cải xanh` → 4094, `súp lơ` → 4094.

**NO NEW ALIAS TO 4094.** 4094 publishes `Súp lơ (bông cải xanh)` over name_en `Mint leaves, raw` and is itself display-name corrupted. Its keys (`bông cải`, `bông cải trắng`, `bông cải xanh`, `bông cải xanh cắt nhỏ`, `rau thơm tươi`, `súp lơ`, `ăn kèm bông cải xanh`) are asserted unchanged, and so is its 106-row population.

Removing the spinach and kale keys does **not** make those phrases unmatched: `cải cải bó xôi` was 4016 and now reaches 4010 at the neural stage; `cải xoăn` was 4016 and now reaches 4016 at the neural stage. That is exactly why the 31 rows are ID-pinned curated clears and the removal is not left to define behaviour.

The added key `cải bẹ xanh 1 2cm để riêng phần cọng và lá` is deliberately long: it is the parser-damaged cleaned text of exactly one reviewed row. A broad generic key in its place would claim rows nobody reviewed. Generic `cải` → 4013 is untouched.

## Processed rows and nutrition

Nutrition sums include known values only; missing values remain null. Every populated value is the live target catalog column scaled by the row's own weight through `nlp.nutrition.scale_nutrition` — no second rounding convention is implemented, and the extra row's delta is measured, never inferred from its textual quantity. Exact before/after records for all 355 ingredient rows and 340 recipes are in [applied_fix.json](applied_fix.json).

| Cohort | Source | Target | Provenance | Rows | Recipes | kcal | Protein | Fat | Carbs |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| cucumber_4016_to_4027 | 4016 | 4027 | preserved | 248 | 244 | -1282.5 | -237.9 | -5.0 | -41.9 |
| mustard_alias_4011_to_4016 | 4011 | 4016 | preserved | 35 | 34 | -3275.6 | -16.8 | -5.6 | -796.3 |
| mustard_exact_4011_to_4016 | 4011 | 4016 | measured | 5 | 5 | -421.8 | -2.1 | -0.8 | -102.6 |
| mustard_leaf_4015_to_4016 | 4015 | 4016 | measured | 5 | 5 | -33.2 | 9.9 | 0.0 | -16.6 |
| mustard_unmatched_recovery_to_4016 | UNMATCHED | 4016 | measured | 5 | 5 | 108.1 | 8.0 | 0.6 | 17.8 |
| green_cabbage_4011_to_4010 | 4011 | 4010 | preserved | 1 | 1 | -6.2 | 0.0 | -0.1 | -1.5 |
| fresh_napa_4016_to_4109 | 4016 | 4109 | measured | 8 | 8 | -490.0 | -43.6 | -7.6 | -64.8 |
| salted_napa_4016_to_4115 | 4016 | 4115 | preserved | 1 | 1 | 1.0 | -0.5 | -0.1 | 1.1 |
| kimchi_4016_to_20034 | 4016 | 20034 | measured | 2 | 2 | -5.0 | -0.4 | 0.2 | -1.4 |
| spinach_clear_to_unmatched | 4016 | UNMATCHED | cleared | 27 | 24 | -1030.4 | -75.8 | -6.2 | -168.9 |
| kale_clear_to_unmatched | 4016 | UNMATCHED | cleared | 4 | 4 | -218.5 | -16.1 | -1.3 | -35.8 |
| collision_clear_to_unmatched | 4015 | UNMATCHED | cleared | 3 | 3 | -43.2 | -2.5 | -0.3 | -7.6 |
| dried_salted_napa_clear_to_unmatched | 4016 | UNMATCHED | cleared | 1 | 1 | -3.4 | -0.3 | 0.0 | -0.6 |
| residual_qwen_keep_4016 | 4016 | 4016 | name_refresh | 10 | 10 | 0.0 | 0.0 | 0.0 | 0.0 |

| Nutrient | Before known sum | After known sum | Delta | Nulls before → after |
|---|---:|---:|---:|---:|
| calories | 15537.0 | 8836.3 | -6700.7 | 5 → 35 |
| protein_g | 883.1 | 505.0 | -378.1 | 5 → 35 |
| fat_g | 73.6 | 47.4 | -26.2 | 5 → 44 |
| carbs_g | 2850.8 | 1631.7 | -1219.1 | 5 → 35 |

Null movement is the 35 clears (value → null on all four nutrients) and the five UNMATCHED recoveries (null → value on all four). `fat_g` moves nine further values to null: 4109 `Rau cải thảo` and 4115 `Dưa cải bắp` publish no `fat_g` column at all, so the eight fresh-napa rows and the one salted-napa row correctly store a null rather than a zero — AGENTS.md section 9. No zero-fill anywhere.

Corpus-wide null counts after: {"calories": 8499, "protein_g": 16957, "fat_g": 20262, "carbs_g": 17458}.

## The 35 curated clears

27 spinach rows, four kale rows, three collision rows and one dried salted napa row. Neither spinach nor kale exists anywhere in the 750-row catalog, and the three collision rows (two broccoli, one mizuna) have no trustworthy target because 4094 is itself display-name corrupted. Picking a component or a neighbour would be exactly the forced coverage AGENTS.md section 5 rejects. Each is pinned by exact id, exact raw text and a complete before record, and each carries the full UNMATCHED contract afterwards: blank code, blank name, `UNMATCHED`, blank confidence (never `0.0`) and four null nutrients, with raw text, cleaned name, quantity/unit, preparation note and estimated weight preserved.

**All 35 are intentionally NOT matcher-reproducible**, and no broad guard is added to reproduce them: 2c660d89 would reach 4109; spinach would reach 4010; kale would reach 4016; collision would reach 4016. A guard wide enough to catch these lines would reach rows nobody reviewed.

## The two reviewed non-reproducible repairs

- **633ea6e1** → stored `4010`, matcher would reach `4016`. `Bắp cải xanh 1/2 cái` is green HEAD CABBAGE, not mustard greens. Its cleaned_name is parser-damaged to `cải xanh`, which the repaired catalog now matches exactly, so the matcher reaches 4016 at EXACT_CATALOG_MATCH / 1.00. The reviewed target 4010 is stored anyway.
- **89749d54** → stored `4115`, matcher would reach `4109`. `Cải thảo muối 100 gr` is salt-pickled napa. 4115 `Dưa cải bắp` (Cabbage Chinese pickled with salt) is the reviewed preparation-correct identity; the matcher still prefers fresh napa 4109 through the `cải thảo` alias.

## Final populations

| Code | Rows |
|---|---:|
| 4010 | 14 |
| 4011 | 0 |
| 4015 | 11 |
| 4016 | 60 |
| 4027 | 270 |
| 4109 | 73 |
| 4115 | 1 |
| 20034 | 75 |
| 4094 | 106 |
| 4135 | 59 |
| 4018 | 177 |
| 20035 | 33 |
| 4013 | 122 |
| 4021 | 147 |
| 20086 | 101 |
| UNMATCHED | 8499 |

The repaired 4016 carries 60 rows: 40 recovered from 4011, five from 4015, five recovered from stored-UNMATCHED, and the 10 deferred residual rows below.

Recipe rollups: 37 recipes change `missing_nutrition_count` and 16 cross a COMPLETE/PARTIAL/INCOMPLETE threshold. Every transition is measured from the ingredient rows and pinned; none is forced.

## The 10 deferred residual 4016 rows

Five `cải con` and five `cải thìa`-family rows stay on the repaired 4016 and only refresh their stale stored display name to `Cải xanh` — code, provenance and all four nutrients are byte-identical. They stay deferred because the bok-choy duplicate 4015 vs 4135 is unresolved and `cải con` remains domain-ambiguous.

## Downstream hard-coded cucumber code

| File | Occurrences | on 4016 | on 4027 |
|---|---:|---:|---:|
| src/recommendation/pantry_simulator.py | 1 | 0 | 1 |

One live pantry entry bought `dưa chuột` at 4016, which publishes `Mustard greens, raw`. It now points at 4027. `src/` is re-scanned on every run for any `("dưa chuột"|"dưa leo", "<code>")` pair, and any other live occurrence fails the batch closed.

## Protecting the reviewed clear from a future Qwen pass

Clearing `2c660d89` made it Qwen-eligible for the first time: it now has no master link, and the Qwen extraction cache carries an output for its line. Measured against the live pipeline, the mapper resolves that output to 4109 `Rau cải thảo` -- FRESH napa -- and before this was added the recovery block produced a candidate for it. A Qwen pass would have silently restated the reviewed clear as a wrong match.

The protection is production logic, not a test assertion: the exact reviewed line `1 muỗng cải thảo muối khô` is pinned in `nlp.qwen_matching._REVIEWED_NO_CATALOG_TARGET_RAW` and refused by `qwen_candidate_eligibility (scripts/run_qwen_line_pipeline.py block B)` with the reason `DRIED_SALTED_NAPA_NO_EXACT_CATALOG_TARGET`. It refuses the line whatever the mapper resolves it to, because the reviewed claim is that no exact catalog identity exists for it at all -- not that one particular code is wrong.

The table holds 1 line. It is keyed on the whole raw line and nothing else: a rule on the cleaned output `cải thảo` would block every fresh napa row, and a rule on `muối` or `khô` would block salt-pickled napa and kimchi, which do have catalog identities (4115, 20034). Asserted still eligible: `Cải thảo 2 lá` → 4109, `Vài lá cải thảo` → 4109, `3 lá cải thảo` → 4109, `1 chén kimchi cải thảo` → 4109.

## Audit evidence hygiene

`WRONG["4016"]` in `scripts/eda/audit_qwen_matching.py` is **not** retired: 4016 is still the wrong home for the rows that remain on it. Its display name becomes `Cải xanh` and its synonym list narrows to `cải con|cải thìa|cải thìa con` — the cleaned names the 10 surviving reviewed rows actually carry. `cải thảo` and `lá cải thảo` are dropped because those rows are gone, and the one row that would have justified keeping `cải thảo` is now cleared. `cải thìa chua` is deliberately absent: the existing compound/preparation logic already holds it in class B, and widening this regex would relabel other rows.

Re-measured against the repaired corpus: {"qwen_rows": 643, "class_counts": {"A": 0, "B": 549, "C": 55, "D": 39}, "class_recipes": {"A": 0, "B": 513, "C": 55, "D": 38}}. Pre-C1: {"qwen_rows": 662, "class_counts": {"A": 0, "B": 568, "C": 55, "D": 39}} — 19 rows leave `QWEN_LLM_MATCH` (five `lá cải xanh`, eight napa and two kimchi rows are re-measured onto `PRESET_ALIAS_MATCH`; three collision rows and the dried salted napa row are cleared).

## Matcher replay

Production shape: `match_batch(cleaned_name, raw_contexts=raw_text)`.

| Class | Rows |
|---|---:|
| A_reproducible | 308 |
| B_curated_divergence | 2 |
| C_curated_unmatched | 35 |
| D_deferred_name_refresh | 10 |

Class B is exactly the two reviewed non-reproducible repairs; class C is the 35 curated clears; class D is the 10 deferred residual rows, which the matcher would scatter across 4010, 4135, 4015 and 13013 and which this batch therefore does not move. Every divergence records the code the matcher would have reached instead; the full table is in [applied_fix.json](applied_fix.json). No global matcher or parser fix is made.

| Probe | Code | Method | Confidence |
|---|---|---|---:|
| dưa leo | 4027 | PRESET_ALIAS_MATCH | 0.98 |
| ăn kèm dưa leo | 4027 | PRESET_ALIAS_MATCH | 0.98 |
| dưa leo cắt sợi | 4027 | PRESET_ALIAS_MATCH | 0.98 |
| dưa chuột | 4027 | EXACT_CATALOG_MATCH | 1.0 |
| dưa chuột tươi | 4027 | CLEANED_NAME_MATCH | 0.99 |
| cải xanh | 4016 | EXACT_CATALOG_MATCH | 1.0 |
| cải bẹ xanh | 4016 | PRESET_ALIAS_MATCH | 0.98 |
| rau cải xanh | 4016 | PRESET_ALIAS_MATCH | 0.98 |
| rau cải bẹ xanh | 4016 | PRESET_ALIAS_MATCH | 0.98 |
| ăn kèm cải bẹ xanh | 4016 | PRESET_ALIAS_MATCH | 0.98 |
| cải canh | 4016 | PRESET_ALIAS_MATCH | 0.98 |
| cải bẹ | 4016 | PRESET_ALIAS_MATCH | 0.98 |
| lá cải xanh | 4016 | PRESET_ALIAS_MATCH | 0.98 |
| rau cải canh | 4016 | PRESET_ALIAS_MATCH | 0.98 |
| cải bẹ xanh con | 4016 | PRESET_ALIAS_MATCH | 0.98 |
| cải bẹ xanh nhỏ | 4016 | PRESET_ALIAS_MATCH | 0.98 |
| cải bẹ xanh to | 4016 | PRESET_ALIAS_MATCH | 0.98 |
| cải bẹ xanh 1 2cm để riêng phần cọng và lá | 4016 | PRESET_ALIAS_MATCH | 0.98 |
| cải xanh tươi | 4016 | CLEANED_NAME_MATCH | 0.99 |
| cải thảo | 4109 | PRESET_ALIAS_MATCH | 0.98 |
| lá cải thảo | 4109 | PRESET_ALIAS_MATCH | 0.98 |
| rau cải thảo | 4109 | EXACT_CATALOG_MATCH | 1.0 |
| kim chi cải thảo | 20034 | PRESET_ALIAS_MATCH | 0.98 |
| kimchi cải thảo | 20034 | PRESET_ALIAS_MATCH | 0.98 |
| cải thảo kim chi | 20034 | PRESET_ALIAS_MATCH | 0.98 |
| cải thìa | 4135 | PRESET_ALIAS_MATCH | 0.98 |
| cải | 4013 | PRESET_ALIAS_MATCH | 0.98 |
| cải trắng | 4021 | PRESET_ALIAS_MATCH | 0.98 |
| cải mầm | 20050 | PRESET_ALIAS_MATCH | 0.98 |
| mầm cải | 20050 | PRESET_ALIAS_MATCH | 0.98 |
| bông cải xanh | 4094 | PRESET_ALIAS_MATCH | 0.98 |
| bông cải xanh cắt nhỏ | 4094 | PRESET_ALIAS_MATCH | 0.98 |
| ăn kèm bông cải xanh | 4094 | PRESET_ALIAS_MATCH | 0.98 |
| súp lơ | 4094 | PRESET_ALIAS_MATCH | 0.98 |
| dưa chuột muối | 4118 | PRESET_ALIAS_MATCH | 0.98 |
| dưa leo baby | 4034 | PRESET_ALIAS_MATCH | 0.98 |
| dưa cải bẹ | 4116 | PRESET_ALIAS_MATCH | 0.98 |
| bắp cải | 4010 | PRESET_ALIAS_MATCH | 0.98 |
| cần tây | 4018 | EXACT_CATALOG_MATCH | 1.0 |
| bắp cải tím | 20035 | PRESET_ALIAS_MATCH | 0.98 |

## Deferred, recorded and unchanged

- **residual_4016_qwen_rows.** Ten rows stay on the repaired 4016 -- five `cải con` and five `cải thìa`-family -- and only refresh their stale stored display name. The bok-choy duplicate 4015 `Cải thìa (cải trắng)` vs 4135 `Rau cải chíp` is unresolved and `cải con` remains domain-ambiguous, so choosing a target for them is a separate reviewed decision.
- **keep_current_broccoli_compound.** e9b2ce8d `Rau luộc ăn kèm (Cà rốt/bông cải xanh/bí chanh/đậu bắp 200 gram` stays on 20086. After C1 the matcher would move it from 4007 to the new `cải xanh` head at SUBPHRASE_CATALOG_MATCH. KEEP_CURRENT / NEEDS_REVIEW, and a blast-radius exclusion.
- **curated_unmatched_compound.** 6ce0333f `Rau dền/rau má/cải xanh/giá…(rau tuỳ sở thích)` remains stored UNMATCHED. After C1 the matcher resolves it to 4016 by subphrase; that divergence is intentional and pinned. It is NOT counted as a changed processed row.
- **lá_cải_thảo_unreviewed_rows.** Adding `lá cải thảo` -> 4109 for the one reviewed row also makes three stored-UNMATCHED rows carrying the same cleaned name matcher-claimable at 4109 (a176477b `1 chén lá cải thảo`, 47346974 `2-3 lá cải thảo`, d7f6dbcf `3 lá cải thảo`). Their IDENTITY audits clean -- plain fresh napa leaves, no preservation or preparation qualifier and no second ingredient -- but their parsed WEIGHT does not: the parser read the bare leaf counts as `phần ăn` servings at 150 g each, giving 300 g for `2-3 lá` and 450 g for `3 lá`. Linking them would write nutrition scaled by those weights, so KEEP_UNMATCHED / DEFERRED_REVIEW: they are recorded, pinned unchanged, and left for a batch that owns the weight question. Parser behaviour is not changed here.
- **4094_display_name_corruption.** 4094 publishes `Súp lơ (bông cải xanh)` over name_en `Mint leaves, raw`. That repair is a later batch. No alias action here targets 4094 and its 106 rows are asserted stable.
- **spinach_and_kale_catalog_gaps.** Neither spinach nor kale exists in the catalog. Adding either identity is a catalog change, not an alias change, and is out of scope.
- **4015_vs_4135_bok_choy_duplicate.** 4015 `Cải thìa (cải trắng)` and 4135 `Rau cải chíp` are both bok choy. Their 11 and 59 rows are asserted stable; choosing a survivor is a separate domain decision.

## Canonical propagation

| Artifact | Changed logical records |
|---|---:|
| canonical_recipes.csv | 330 |
| canonical_recipe_ingredients.csv | 351 |
| recipe_canonical_mapping.csv | 52 |

The 355 pinned rows span 340 canonical groups (333 for the changed rows alone), and all but 4 appear in `canonical_recipe_ingredients.csv` — the others live in recipes canonicalisation deduplicated away. Canonical ID drift = 0; representative drift = 0.

The audit quoted {"processed_recipes_touched": 332, "canonical_ingredient_rows": 340, "canonical_groups": 329, "canonical_recipes_rows": 332, "nutrition_status_transitions": 16} for its 344-row plan. Measured for the approved state: {"processed_ingredient_rows_changed": 345, "processed_rows_written": 355, "processed_recipes_touched": 333, "processed_recipes_touched_including_name_refresh": 340, "canonical_ingredient_rows": 351, "canonical_groups": 340, "canonical_recipes_rows": 330, "recipe_canonical_mapping_rows": 52, "recipes_with_changed_missing_count": 37, "nutrition_status_transitions": 16}.

## Embeddings and validation

Embeddings: {"rebuilt": true, "tracked": false, "shape": [750, 768], "sha256": "849540ae171fa8fb92a6508806cf68dbef998cbcc27e52836a5503e8e9810505", "next_load_equal": true, "input_sha256": "f042641089b74ba2ff33bb9a32adcf35dd3521b3ad381a82f454703a7fff3202", "build_inputs": {"4016": "Cải xanh (Rau, quả, củ dùng làm rau)"}}

Validation: {"complete": true, "processed_parity": true, "canonical_parity": true, "canonical_check": true, "canonical_determinism": true, "interim_unchanged": true, "catalog_name_vi_only": true, "embeddings_rebuilt": true, "downstream_hard_codes_repaired": 1, "blast_radius_measured_against": "reviewed manifest, not git HEAD"}

Tests: {"focused_c1": "184 passed", "dried_salted_napa_qwen_exclusion": "30 passed", "qwen_eligibility_guard": "92 passed", "qwen_mapper_rule_repair_batch1": "88 passed", "c2_regression": "152 passed", "full_suite": "2306 passed, 11 subtests passed, 0 failed", "excluded": "tests/test_api_endpoints.py and tests/test_smart_input.py (fastapi not installed; pre-existing collection limitation)"}

Excluded: 4094 / 4096 display-name corruption; 4015 / 4135 bok-choy duplicate; `cải con` target ambiguity; spinach and kale catalog gaps; e9b2ce8d broccoli compound (KEEP_CURRENT / NEEDS_REVIEW); 6ce0333f multi-option compound (curated UNMATCHED); three unreviewed `lá cải thảo` stored-UNMATCHED rows; parser damage producing `cải xanh` from `Bắp cải xanh`; match()/match_batch() architecture; general stale code-space contamination.

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
 M nlp/qwen_matching.py
 M scripts/eda/apply_bamboo_shoot_alias_safe_fix.py
 M scripts/eda/apply_display_name_batch_a_safe_fix.py
 M scripts/eda/apply_display_name_batch_b_safe_fix.py
 M scripts/eda/apply_display_name_batch_c2_safe_fix.py
 M scripts/eda/audit_qwen_matching.py
 M src/recommendation/pantry_simulator.py
 M tests/test_bamboo_shoot_alias_safe_fix.py
 M tests/test_display_name_batch_a_safe_fix.py
 M tests/test_display_name_batch_b_safe_fix.py
 M tests/test_display_name_batch_c2_safe_fix.py
 M tests/test_meat_band_batch_a_alias_safe_fix.py
 M tests/test_meat_band_batch_a_followup_safe_fix.py
 M tests/test_qwen_eligibility_guard.py
 M tests/test_qwen_mapper_rule_repair_batch1.py
?? reports/eda/display_name_batch_c1_fix/
?? scripts/eda/apply_display_name_batch_c1_safe_fix.py
?? scripts/eda/display_name_batch_c1_reviewed_state.json
?? tests/test_display_name_batch_c1_safe_fix.py
?? tests/test_dried_salted_napa_qwen_exclusion.py
```
