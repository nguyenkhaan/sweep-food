# SweepFood AI - Codex Instructions

## Project Context

This repository contains the data and AI pipeline for SweepFood.

The current task focuses on recipe canonicalization and data quality.

The source recipe dataset may contain multiple recipes that represent the same dish.
These recipes can have the same or equivalent names but differ in:

- source URL
- source platform
- servings
- ingredient list
- ingredient matching quality
- estimated ingredient weights
- nutrition values

For downstream recommendation, we want one representative canonical recipe per dish.

---

## Core Principles

### 1. Never destroy source data

Do not delete, overwrite, or directly deduplicate:

- `data/raw/`
- `data/interim/`

Existing source and interim datasets must remain reproducible.

Canonicalization must produce new derived files under `data/processed/`.

---

### 2. Do not deduplicate recipes using exact name alone

Recipes with the same normalized name are not necessarily exact duplicates.

The original recipe IDs must remain preserved.

When multiple recipes belong to the same canonical dish, select one representative recipe using explicit and reproducible quality criteria.

Do not simply keep the first row.

---

### 3. Selection must be deterministic and explainable

The selected canonical recipe must be chosen using a deterministic quality score or deterministic ranking rules.

Prefer recipes with:

1. better ingredient coverage;
2. higher master ingredient match coverage;
3. fewer `UNMATCHED` ingredients;
4. fewer ingredients using fallback `estimated_weight_g = 10`;
5. more explicit ingredient quantities;
6. fewer nutrition anomalies;
7. reasonable recipe completeness;
8. a valid source URL.

Do not use subjective criteria such as "this recipe looks better" unless no measurable criterion can distinguish the candidates.

If a tie remains after all quality criteria, use a deterministic tie-breaker such as recipe ID.

---

### 4. Preserve provenance

Every canonical recipe must retain enough information to trace it back to the original recipe.

At minimum preserve:

- original recipe ID;
- canonical dish name;
- selected source URL;
- selection score;
- selection reason.

Also create a mapping from every original recipe in a duplicate group to the selected canonical recipe.

Example:

`original_recipe_id -> canonical_recipe_id`

---

### 5. Do not modify ingredient aliases as part of recipe deduplication

Ingredient aliases and recipe aliases are different concepts.

Do not merge master ingredients merely because their Vietnamese names or aliases are similar.

Do not modify:

- `ingredient_alias_map.json`
- `master_ingredients_nutrition.csv`

unless the task explicitly requests it.

---

### 6. Canonical name normalization must be conservative

Normalization may include safe operations such as:

- Unicode normalization;
- trimming whitespace;
- collapsing repeated whitespace;
- lowercase comparison;
- safe punctuation normalization.

Do not aggressively remove words that may change dish identity.

Do not assume two semantically different dish names are the same without evidence.

---

### 7. Do not hide data quality problems

Known EDA problems must not be silently repaired during canonicalization.

Examples include:

- fallback `estimated_weight_g = 10`;
- missing master nutrition;
- `NaN` converted to zero;
- inconsistent nutrition values;
- `UNMATCHED` rows with master codes;
- Qwen false-positive matches.

These signals may be used when calculating recipe quality, but they must not be silently rewritten by this task.

---

### 8. Separate analysis from production output

Put analysis scripts under:

`scripts/eda/` or an appropriate data-processing script directory.

Canonicalized datasets must be written under:

`data/processed/recipes/`

Do not overwrite the existing processed recipe files unless explicitly requested.

Prefer new outputs such as:

- `canonical_recipes.csv`
- `canonical_recipe_ingredients.csv`
- `recipe_canonical_mapping.csv`

Exact filenames may be adjusted if the existing project conventions suggest better names.

---

### 9. Validate before writing final output

Before considering the task complete, validate:

- canonical recipe IDs are unique;
- every canonical dish has exactly one selected recipe;
- every selected recipe exists in the original dataset;
- mapping references valid recipe IDs;
- ingredient rows for canonical recipes reference valid selected recipe IDs;
- no source/interim files were modified;
- output generation is deterministic across repeated runs.

Run the relevant existing tests or data validation scripts.

---

### 10. Report findings before making ambiguous business decisions

If recipe grouping requires semantic decisions that cannot be safely inferred from the data, do not guess.

Produce an ambiguity report containing:

- candidate recipe names;
- recipe IDs;
- relevant evidence;
- reason the group is ambiguous.

Leave those groups unresolved or use a clearly documented fallback rule.

---

## Git Rules

Work only on the current branch.

Do not create a new branch unless explicitly requested.

Do not commit or push unless explicitly requested.

Before finishing, show:

- files created;
- files modified;
- validation results;
- remaining ambiguities;
- `git status`.

Avoid unrelated refactoring.