# Datasheet — SweepFood Vietnamese Recipe–Nutrition Dataset

A data descriptor for a Vietnamese recipe/ingredient/nutrition dataset built to
support the **pantry-optimization** task: given a household's current
ingredient inventory, select or rank recipes that maximise feasibility and
minimise food waste. Structured following *Datasheets for Datasets*
(Gebru et al., 2021).

All figures below are produced by `scripts/audit_final_dataset.py` and
`scripts/add_weight_source.py`; re-run them to reproduce.

---

## 1. Motivation

- **Purpose.** Provide a clean, provenance-tracked knowledge base of Vietnamese
  home-cooking recipes with per-ingredient and per-recipe nutrition, enabling
  research on pantry-driven meal recommendation / food-waste reduction.
- **Gap.** Public Vietnamese recipe datasets with normalised ingredient→nutrition
  linkage and explicit ingredient-weight provenance are scarce.
- **Note.** This is a **dataset** contribution. A learning-to-rank recommender is
  included only as a *simulated reference baseline* (Section 6); its relevance
  labels are synthetic and it is **not** a modelling contribution.

## 2. Composition

- **Recipes:** 5,478 canonical dishes (100% deduplicated, exactly 1
  representative version per dish; 162 duplicate recipes and 1 40-serving
  outlier eliminated). Provenance mapping to all 5,641 original crawl recipes is
  preserved via `data/processed/recipes/recipe_canonical_mapping.csv`.
- **Ingredient lines:** 63,662 (median 10 per recipe, range 1–52).
- **Master ingredients (nutrition reference):** 750, derived from the Vietnamese
  National Institute of Nutrition food-composition data.
- **Per recipe fields:** `id, name, source_platform, source_url,
  default_servings, estimated_cooking_minutes, cooking_method, dish_type,
  diet_tags, total_calories, total_protein_g, total_fat_g, total_carbs_g,
  calories_per_serving, protein_per_serving, fat_per_serving, carbs_per_serving,
  nutrition_anomaly_flag, ingredients_count, core_ingredients_count, dish_cluster_id`.
- **Per ingredient fields:** `id, recipe_id, master_ingredient_code,
  master_ingredient_name, raw_text, cleaned_name, required_quantity, unit_vi,
  unit, preparation_note, match_confidence, match_method, estimated_weight_g,
  calories, protein_g, fat_g, carbs_g, weight_source, ingredient_role`.
- **Not included:** original step-by-step instruction prose, editorial
  descriptions, photographs, and original creative titles from the source sites
  (copyright-protected expression is deliberately excluded; see `DATA_LICENSE`).

### 2.1 Source distribution

| source_platform | domain | recipes |
|---|---|---:|
| monngonmoingay | monngonmoingay.com | 1,926 |
| dienmayxanh | dienmayxanh.com | 1,789 |
| cookpad | cookpad.com | 1,763 |

### 2.2 Ingredient→nutrition matching

98.7% of ingredient lines (62,864) are linked to a master nutrition record;
only 1.3% (798) are `UNMATCHED` and deliberately carry no nutrition (blank,
not zero). Match methods:

| match_method | rows |
|---|---:|
| PRESET_ALIAS_MATCH | 39,340 |
| EXACT_CATALOG_MATCH | 12,739 |
| LLM_COMPOUND_SPLIT | 9,061 |
| UNMATCHED | 798 |
| CLEANED_NAME_MATCH | 756 |
| QWEN_LLM_MATCH | 617 |
| STANDARDIZED_CURE | 344 |
| BERT_SEMANTIC_MATCH | 5 |
| SUBPHRASE_CATALOG_MATCH | 2 |
### 2.3 Ingredient-weight provenance (`weight_source`)

Weights drive nutrition, so each row is labelled by how its weight was obtained:

| weight_source | rows | % | confidence |
|---|---:|---:|---|
| vague_portion_fallback | 22,533 | 35.4% | **low (source gave no quantity)** |
| measured_mass_volume | 15,937 | 25.0% | high (quantity in g/kg/ml/lít) |
| count_portion_estimate | 13,037 | 20.5% | medium (count × per-piece portion) |
| unit_conversion_std | 11,304 | 17.8% | high (spoon/cup × standard grams) |
| unmatched_no_nutrition | 798 | 1.3% | n/a (unmatched, no nutrition) |
| role_category_estimate | 53 | 0.1% | low |
Standard conversion factors: `muỗng canh`=15 g, `muỗng cà phê`=5 g,
`chén/cốc`=200 g, `kg`=1000 g, `g`/`ml`=1 g/ml.

### 2.4 Ingredient functional roles (`ingredient_role`)

To prevent pantry recommender systems from suffering from "seasoning inflation"
(where having salt, oil, and garlic superficially satisfies 60% of a complex dish),
each ingredient line is categorized into its culinary functional role directly via
the cloud-hosted open-source reasoning model `gpt-oss:120b` (with zero heuristic fallback):

| ingredient_role | rows | % | description |
|---|---:|---:|---|
| seasoning | 30,875 | 48.5% | Salt, fish sauce, sugar, oils, bouillon, soy sauce, broths |
| core | 12,001 | 18.9% | Primary proteins (meat, seafood, eggs, tofu), primary starches, and dish-defining cores |
| secondary | 12,067 | 19.0% | Substantial vegetables, mushrooms, tubers, fruits |
| garnish | 8,719 | 13.7% | Fresh herbs, scallions, cilantro, chili garnish, small aromatics |

Every recipe has $\ge 1$ core ingredient (median 2.0 per recipe), tracked via
`core_ingredients_count`. For pure-vegetable/dessert dishes, `gpt-oss:120b` semantically
identified the primary dish-defining ingredient (e.g. mushrooms in mushroom stew) in dish context.

### 2.5 Dialect dish clustering (`dish_cluster_id`)

Candidate dialect pairs across Northern and Southern Vietnamese naming conventions
(`thịt lợn <-> thịt heo`, `ba chỉ <-> ba rọi`, `cuộn <-> cuốn`, `móng giò <-> chân giò`,
`đậu phụ <-> đậu hũ`...) were semantically evaluated by `gpt-oss:120b`, confirming 20
dialect-equivalent pairs (40 dishes) and mapping all 5,478 dishes into 5,458 distinct
`dish_cluster_id`s. Downstream cross-validation splits should group by `dish_cluster_id`
to prevent data leakage across train and test folds.

## 3. Collection

- Recipes were crawled from three public Vietnamese cooking websites (Section
  2.1). Only factual elements are retained; see `ATTRIBUTION.md`.
- The verbatim crawl snapshot (`data/raw/recipes_raw_scraped.json`) is kept
  locally for reproducibility only and is excluded from version control.

## 4. Preprocessing / cleaning / labelling

- Ingredient parsing → quantity/unit extraction → master matching (alias, exact,
  cleaned-name, sub-phrase, neural, and LLM-assisted stages) → weight estimation
  → per-ingredient and per-recipe nutrition roll-up.
- Deterministic canonicalisation groups same-dish variants and selects one
  representative by an explainable quality score (ingredient coverage, match
  coverage, fewer UNMATCHED, fewer fallback weights, explicit quantities, fewer
  nutrition anomalies, valid source URL), with recipe-id tie-break. Provenance is
  preserved via `recipe_canonical_mapping.csv`.
- Missing master nutrition is propagated as **missing** (blank/null), never
  silently zero-filled.
- **Nutrition completion (documented, not silent).**
  - Stage 1 (energy balance): where recorded energy was fully explained by the
    present macro(s) (kcal energy balance, anchored by ≥1 known macro), missing
    macro(s) were completed as 0.0 with citations in
    `master_nutrition_overrides.json`
    (`scripts/complete_macros_by_energy_balance.py`).
  - Stage 2 (curated FCT/USDA overrides): the remaining 24 non-derivable master
    items (alcohol, vinegar, MSG, salt, five-spice powder, broths) were
    manually completed with explicit citations to the Vietnam Food Composition
    Table (FCT 2007) and USDA FoodData Central
    (`scripts/apply_fct_usda_24_overrides.py`; see
    `reports/eda/fct_usda_24_overrides_report.json`).
  - Result: **750 / 750 (100.0%) master ingredients now have complete macros**
    (0 missing calories, protein, fat, or carbs), and **0 matched ingredient lines
    have missing macros**.
- **Count-weight corrections.** A small set of unambiguous standard portions
  (garlic clove 5 g, scallion stalk 15 g, lemongrass stalk 20 g) was corrected
  from earlier flat defaults, with affected nutrition and recipe totals
  recomputed (`scripts/improve_count_weights.py`; 1,633 rows / 1,331 recipes;
  `reports/eda/count_weight_corrections.json`).

## 5. Recommended uses & task definition

**Pantry-optimization task.** Input: a pantry (set of ingredients with
quantities and, optionally, expiry). Output: a ranking/selection of recipes.
Suggested objective terms, all computable from the released fields:

- *feasibility coverage* — fraction of a recipe's required ingredient weight
  satisfied by the pantry (respecting `weight_source` confidence);
- *zero-waste rescue* — preference for recipes consuming soon-to-expire items;
- *nutrition balance* — e.g. protein-energy ratio from recipe macros.

Users bring their own objective/labels. The dataset ships **no** human relevance
labels.

## 6. Simulated reference baseline (NOT a contribution)

`data/training/` and `src/recommendation/` contain a learning-to-rank pipeline
whose pantries and relevance grades are produced by a **simulated utility
function** (`ground_truth_utility.py`). Reported NDCG values reflect recovery of
that synthetic function and MUST NOT be read as real recommendation quality.
Provided only as a runnable reference; real evaluation requires human or
behavioural labels (future work).

## 7. Distribution & licensing

- Data: **CC BY 4.0** (`DATA_LICENSE`). Code: MIT (`LICENSE`).
- Each recipe retains `source_url`/`source_platform` for provenance. Original
  instructions/photos remain with the source sites and are not redistributed.
## 8. Limitations (read before use)

- **1.3% of ingredient lines are UNMATCHED (798 rows)** and lack nutrition
  (plunged from 13.3% after two-turn LLM compound ingredient splitting and
  audit via `scripts/generate_unmatched_split_map.py` and
  `scripts/audit_unmatched_split_map.py`).
- **35.4% of ingredient weights are low-confidence** (`vague_portion_fallback`, 22,533 rows):
  the source specified no quantity, so the weight is a portion estimate. These
  are labelled, not hidden; filter via `weight_source` for weight-sensitive work.
- **106 recipes (1.94%) carry a `nutrition_anomaly_flag = 1`**: recipes with
  extreme nutrition distortions (>15,000 total kcal, >1,000g fat, >1,500g carbs,
  >4,000 kcal/serving, or <50 kcal/serving; mostly herbal soaks, party platters,
  or commercial broths). Downstream rankers should filter or downweight them.
- **`estimated_cooking_minutes` is a platform-level default**: monngonmoingay=35 min,
  dienmayxanh=40 min, cookpad=30 min. It reflects website scrape defaults rather
  than recipe-specific cooking time.
- **`dish_type` and `diet_tags` are heuristic rule classifications**: derived via
  keyword patterns (`nlp/recipe_classifier.py`). `dish_type` skews heavily towards
  "Món chính" (71.6%) and "Canh" (21.9%); `diet_tags` defaults to "Món cơm gia đình"
  for ~81% of recipes. Downstream models should treat them as coarse rule-based hints.
- **0 / 750 master ingredients lack macronutrients (100% complete).** All 62,864
  matched ingredient lines have complete calories, protein, fat, and carbs
  (down from 11,695 missing fat at baseline), achieved via two-stage documented
  derivation and authoritative FCT/USDA citation.
- Ingredient→master matching precision is not yet human-validated; a stratified
  gold-labelling protocol is provided (`scripts/eda/sample_matching_eval.py`)
  and results are pending.
- Only 3 sources → coverage skews toward popular home dishes.
- Nutrition/weights are estimates and are not medical/dietary advice.
- **Ambiguous large countable items are left unchanged**: e.g. `1 con gà`,
  `1 trái dứa`, `1 cái chân giò` — whether the source means a whole item or a
  portion is undecidable from the text, so per-piece weight is not guessed
  (flagged via `weight_source = count_portion_estimate`).
- **UNMATCHED lines are mostly compound/branded strings** (e.g. `muối đường`,
  `hành tím tỏi`) that do not map to a single master; forced matching is
  deliberately avoided. Expanding matching is future work.
## 9. Maintenance

- Regenerate provenance: `python scripts/add_weight_source.py`
- Validate: `python scripts/audit_final_dataset.py` (exits non-zero on any
  broken invariant).
- Apply FCT/USDA overrides: `python scripts/apply_fct_usda_24_overrides.py`
- Complete macros: `python scripts/complete_macros_by_energy_balance.py`
- Standardize per-serving and anomaly flags: `python scripts/add_per_serving_and_anomaly_flags.py`
- Resolve roles and clusters via GPT OSS: `python scripts/resolve_issues_with_gpt_oss.py`
- Correct measure over-estimates: `python scripts/fix_measure_overestimate_weights.py`
- Correct count weights: `python scripts/improve_count_weights.py`
