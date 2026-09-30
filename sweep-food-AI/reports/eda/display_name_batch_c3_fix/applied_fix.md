# Batch C3 applied stored-data repair



68 rows 4013 -> 4010; 19 rows 4021 -> 4010; 4 UNMATCHED recoveries. Exactly 91 reviewed rows across 86 recipes.

78 cleaned-name repairs: 62 `cải` -> `bắp cải`, 16 `cải trắng` -> `bắp cải trắng`. The other 13 names are preserved.

Four alias repoints and four additions; 4680 -> 4684 keys. All eight aliases are audited by exact corpus use.



## Deliberately unresolved parser damage



`nlp.llm_cleaner.VietnameseLLMIngredientCleaner._parse_single_item` treats `bắp` as unit BAP and may strip it. `bắp cải` is not protected as a multiword noun.

`Bắp cải` -> `cải`; `Bắp cải trắng` -> `cải trắng`; `Bắp cải tím` -> `cải tím`.

**PARSER_BAP_CAI_FIX_NEEDED = true. PARSER_DURABILITY_GAP = 82.**

Stored-cleaned replay: 91/91 -> 4010, PRESET_ALIAS_MATCH / 0.98 on both routes. Raw -> parser -> matcher: only 9/91 return to 4010. 82 repairs are not durable against fresh raw parsing. No parser-level reproducibility is claimed.

No parser files, CANONICAL_UNIT_MAP, protected_multiword_nouns, or parser architecture changed.



## Deferred boundaries



DEFERRED_ALIAS_POLICY: `cải` remains -> 4013 for 17 damaged radish rows. Removing it gives match() -> 4013 and match_batch() -> 4094; corrupted 4094 remains out of scope.

`cải trắng` remains -> 4021 for 119 genuine white-radish rows. Red, dried, pickled, kimchi, napa and crown-daisy probes remain unchanged.

KEEP_UNMATCHED: db378d63, eee05df7, 24f47b37, fe596f36, e8da7381, dc56ccf1, 90acbdb8, 020f668d, eb72aab4, a7875aed, 05067998, 58276236, 8a71fe23.

Brussels sprouts; sprouts; Savoy/crinkled; red/self-substituting; multi-option; dish title; compound/either-or. No broad abstention guard.

a7875aed and 58276236 remain curated divergences: existing `bắp cải` alias may claim them at 0.98.



## Measured outcomes



Nutrition delta: +1439.60 kcal; +26.12 g protein; +8.19 g fat; +305.89 g carbs. 68 fat null -> measured transitions plus four recoveries in all macros; no value -> null transitions or zero-fill.

Final populations: {"4010": 105, "4011": 0, "4012": 5, "4013": 54, "4021": 128, "20035": 33, "4109": 73, "4115": 1, "UNMATCHED": 8495}.

Final nulls: {"calories": 8495, "protein_g": 16953, "fat_g": 20190, "carbs_g": 17454}.

86 recipe totals change, four missing counts change, zero nutrition-status labels change.

Canonical: 88 ingredient rows, 84 recipe rows/groups, 67 mapping rows; zero ID, representative, group-ID or dish-name drift; row counts unchanged.

Prior A/B/bamboo/C2/C1 live population/null/alias constants are updated for C3 without changing their own reviewed row sets.



Full exact IDs, raw text, complete before/after records, alias uses, cohort nutrition and replay results: [applied_fix.json](applied_fix.json).

Validation: {"complete": true, "processed_parity": true, "canonical_parity": true, "canonical_check": true, "interim_unchanged": true, "parser_files_unchanged": true}.

Tests: {}.

No commit or push.
