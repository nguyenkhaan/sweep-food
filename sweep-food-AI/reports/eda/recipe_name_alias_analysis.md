# Recipe-name alias candidate analysis

## Scope and reproduction

This is the lexical discovery snapshot, not the reviewed decision layer. Candidate rows retain their original unreviewed status; subsequent business decisions are in recipe_name_alias_decisions.json and their application is in recipe_name_alias_application_audit.csv.
Discovery reconstructs Phase 1 in memory so reviewed alias application does not change its 5,510-name input. Discovery does not modify canonical outputs or protected source data.

```powershell
python scripts/eda/recipe_name_alias_analysis.py
python scripts/eda/recipe_name_alias_analysis.py --check
python -m unittest discover -s tests -p test_recipe_name_alias_analysis.py -v
```

## Rules and safeguards

Names retain Phase 1 NFC/lowercase/whitespace normalization. Unicode punctuation becomes spaces only in analysis keys; accents remain.
Pairs must have different Phase 1 normalized names. Deterministic blocking uses equal normalized keys or equal token multisets after deleting one token.

- punctuation_equal: identical punctuation-normalized strings.
- token_reorder: identical token multisets, different order; no token is discarded.
- parenthetical_base_equal: exact base equality after removing balanced nonnested parentheses, at least two base tokens. Removed wording is exposed.
- descriptive_suffix_equal: exact base equality after removing one explicitly listed trailing phrase, at least two base tokens.
- single_token_edit: equal token counts of at least four, exactly one differing token per side; both differing tokens have at least four characters, Levenshtein distance exactly one, token Jaccard >=0.60 and whole-name edit similarity >=0.90. Accent-only differences are excluded.

Suffix list: nhanh gọn, đơn giản, ngon, dễ làm, phiên bản nhà làm, phiên bản nhà tôi, món ăn sáng cho bé.

All rules reject pairs whose protected ingredient/method/diet token sets differ. Protected tokens: basa, bê, bò, chanh, chay, chiên, chua, chép, chín, cua, cà, cá, cừu, diêu, dê, dứa, ghẹ, gà, gừng, heo, hấp, hầm, hến, hồi, hồng, keto, kho, luộc, lóc, lươn, lợn, mai, muối, mật, mắm, mặn, mực, ngan, nghêu, ngọt, ngỗng, ngừ, nướng, nấm, nấu, om, ong, phô, quay, ram, rang, ri, rim, sò, sả, sống, sữa, thơm, tiêu, trộn, trứng, tái, tép, tôm, tương, tỏi, vịt, xào, đậu, ếch, ốc, ớt.

This finite vocabulary is a conservative screen, not complete semantic detection. Broad containment alone is never a rule. Thus 'canh chua cá' / 'canh chua cá hồi' and 'gà nướng' / 'gà nướng mật ong' are excluded. No abbreviation expansion, ingredient aliases, LLM identity decisions, accent stripping or transitive grouping is used.

## Counts and distributions

Canonical names analyzed: **5,510**.
Unique candidate pairs: **32**. Output contains pairs only, not inferred equivalence groups.
Distinct recipe IDs involved: **64**.

Rule counts overlap when one pair satisfies several rules:

| Rule | Pairs |
| --- | ---: |
| punctuation_equal | 1 |
| token_reorder | 25 |
| parenthetical_base_equal | 5 |
| descriptive_suffix_equal | 2 |
| single_token_edit | 0 |

Scores are descriptive lexical evidence, not confidence probabilities. Jaccard uses sets; edit similarity is 1 - Levenshtein/max character length, on punctuation-normalized strings. Containment is shared token count divided by smaller set size. Ingredient overlap uses safely normalized cleaned names; blank evidence stays missing.

| Metric | Min | Median | Max | <0.5 | 0.5–<0.8 | 0.8–<0.9 | 0.9–1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| token_jaccard | 0.333 | 1.000 | 1.000 | 1 | 3 | 2 | 26 |
| edit_similarity | 0.067 | 0.286 | 1.000 | 25 | 5 | 1 | 1 |
| ingredient_jaccard | 0.000 | 0.088 | 0.444 | 32 | 0 | 0 | 0 |

## Strongest-looking lexical candidates (not confirmed)

- **Salad BÒ-ĐẬU RỒNG** / **Salad bò đậu rồng** — punctuation_equal; token=1.000000, edit=1.000000, ingredient=0.100000. IDs: `0b96afae-1449-4b59-9c36-f5c05a44f684` / `f605dcc1-ff3b-4cf5-97e2-82d21fe4849e`. low ingredient-name overlap (<0.25); inspect source recipes
- **Mì trứng tôm thịt heo** / **Mì tôm Trứng Thịt heo** — token_reorder; token=1.000000, edit=0.619048, ingredient=0.055556. IDs: `9284fb5b-d3fa-42bc-91f9-817fcd4cfb3f` / `cf066500-9078-4666-9689-815d968ffb46`. word order can change ingredient roles; low ingredient-name overlap (<0.25); inspect source recipes
- **Bánh ram ít Huế** / **Bánh Ít Ram Huế** — token_reorder; token=1.000000, edit=0.600000, ingredient=0.000000. IDs: `30f3b3ef-c37a-46dd-a80b-e42d2125e4f4` / `b91ed423-2ed7-4c65-b976-cf1ffa4c88fd`. word order can change ingredient roles; low ingredient-name overlap (<0.25); inspect source recipes
- **Canh đu đủ hầm giò heo** / **Canh giò heo hầm đu đủ** — token_reorder; token=1.000000, edit=0.454545, ingredient=0.000000. IDs: `b36c1f0d-c86a-45b0-91dc-d2083a064662` / `b674691a-974f-47cf-abb8-0d6fa96ba5e4`. word order can change ingredient roles; low ingredient-name overlap (<0.25); inspect source recipes
- **Canh sườn non nấu khoai mỡ** / **Canh Khoai Mỡ Nấu Sườn Non** — token_reorder; token=1.000000, edit=0.384615, ingredient=0.066667. IDs: `09eb35ab-bf18-4158-bdcb-61629ad5acb2` / `7c716f33-c267-4721-9042-676b0695c314`. word order can change ingredient roles; low ingredient-name overlap (<0.25); inspect source recipes
- **Củ sen hầm chân giò** / **Chân giò hầm củ sen** — token_reorder; token=1.000000, edit=0.368421, ingredient=0.000000. IDs: `3aaae5d6-b601-4bce-be3c-752762f89640` / `3e29ddff-c4e4-41c9-b585-b7c181eeb92a`. word order can change ingredient roles; low ingredient-name overlap (<0.25); inspect source recipes

## False-positive-looking / caution examples (not rejected)

A specific role-ambiguity example is 'Mì trứng tôm thịt heo' / 'Mì tôm Trứng Thịt heo': 'mì trứng' and 'mì tôm' can describe different noodle types, despite identical token multisets. This pair needs source review; it is not classified as equivalent or different.

- **Bánh ram ít Huế** / **Bánh Ít Ram Huế** — token_reorder; token=1.000000, edit=0.600000, ingredient=0.000000. IDs: `30f3b3ef-c37a-46dd-a80b-e42d2125e4f4` / `b91ed423-2ed7-4c65-b976-cf1ffa4c88fd`. word order can change ingredient roles; low ingredient-name overlap (<0.25); inspect source recipes
- **Măng kho ba rọi** / **Ba rọi kho măng** — token_reorder; token=1.000000, edit=0.200000, ingredient=0.000000. IDs: `3aa44973-0694-49eb-9884-aafcd1277ed2` / `596a27d9-f9da-432d-8df6-585863060022`. word order can change ingredient roles; low ingredient-name overlap (<0.25); inspect source recipes
- **Củ sen hầm chân giò** / **Chân giò hầm củ sen** — token_reorder; token=1.000000, edit=0.368421, ingredient=0.000000. IDs: `3aaae5d6-b601-4bce-be3c-752762f89640` / `3e29ddff-c4e4-41c9-b585-b7c181eeb92a`. word order can change ingredient roles; low ingredient-name overlap (<0.25); inspect source recipes
- **Canh cải cúc nấu thịt băm** / **Canh cải cúc (tần ô) nấu thịt băm** — parenthetical_base_equal; token=0.750000, edit=0.806452, ingredient=0.000000. IDs: `3f8ae57b-68e4-4c14-975e-91e28a6302e9` / `ccac0135-8bd4-4b49-b5f2-22d8e1228a9a`. parenthetical wording may specify a meaningful variant; low ingredient-name overlap (<0.25); inspect source recipes
- **Canh cải chua sườn non** / **Canh sườn non cải chua** — token_reorder; token=1.000000, edit=0.272727, ingredient=0.000000. IDs: `47d8d0d4-e9ec-4472-93fa-bf86fbe12861` / `77260cee-2908-4850-960e-b684624f9d47`. word order can change ingredient roles; low ingredient-name overlap (<0.25); inspect source recipes
- **Cháo Khoai Lang Tím Thịt Heo** / **Cháo thịt heo khoai lang tím** — token_reorder; token=1.000000, edit=0.357143, ingredient=0.000000. IDs: `9895807c-57d4-454c-a4cb-8f72ad5c23f2` / `c7817bd6-6507-465d-bdf4-6c02d3df8c47`. word order can change ingredient roles; low ingredient-name overlap (<0.25); inspect source recipes

## Limitations and validation

High token similarity can hide meaningful differences; even punctuation or word order can affect interpretation. Parentheticals may specify regional, dietary or preparation variants. Low ingredient overlap is a review cue, not proof of distinct identity: source recipes and cleaned names vary. Vocabulary guards miss unknown ingredients and methods and can suppress real synonyms. Short typos, abbreviations, regional synonyms, larger reorderings with changed words, and unlisted suffixes are intentionally missed. No precision/recall claim is made without labeled review.

Generation checks unique canonical IDs/names and ingredient references, compares full CSV bytes after reversing both inputs, reads back outputs, and checks SHA-256 for all other data files before and after writing. --check compares the report and CSV against disk. No canonical pipeline or consumer is changed.

Validation on this dataset: seven focused Phase 2 unittest tests and eleven Phase 1 tests passed. The discovery --check and Phase 1 canonicalization --check passed. Tests cover unsafe containment, cooking/ingredient changes, accent preservation, malformed parentheses, tight edits, evidence, input permutation and input immutability.

Protected dataset files checked: 28. SHA-256 of the sorted path/hash manifest (excludes only the candidate CSV): `6eba47e5a522346b328034a529759c8e830fdcb063b4f3f86ff8aa0958ec3fd5`.
