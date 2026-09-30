# Conservative Qwen recovery eligibility guard

This is a first guard before Batch 2, not complete compound detection. No
101-head vocabulary or general-purpose ingredient classifier is introduced.
The earlier 46/47 result is not used as evidence of generalization; its labeled
audit artifact was not found in this checkout, so this report does not claim
to reproduce that denominator.

## Production logic

`qwen_candidate_eligibility(raw_text, qwen_cleaned_name, winning_code)` is pure
and returns `(eligible, rejection_reason)`. Normalization uses NFC, casefold,
and collapsed whitespace. Rejections are evaluated in this order:

1. `qwen_explicit_ingredient_list`: Qwen output has `/`, `+`, `;`, a spaced
   hyphen, or whole-word `và`, `hoặc`, `hay`, with distinct textual items.
   Fractions/numeric ranges, repeated identical items, quantity-only sides,
   purpose/comparison/unit markers, and sides beginning with the preparation
   verbs rửa/cắt/thái/băm/chẻ abstain. Commas are not output separators.
   The hardened distinct-item comparison normalizes each fragment with NFC,
   casefold, NFC and collapsed/trimmed whitespace, then strips only terminal
   spaces and `. , ! ? : ; …`. Internal punctuation is preserved. Exact
   normalized repeats are one identity. The only reviewed synonym identities
   are `hành lá` ↔ `hành hoa` (4038 / Hành lá (hành hoa)) and
   `nấm bào ngư` ↔ `nấm sò` (20004 / Nấm bào ngư (nấm sò)). Every fragment
   must resolve to the same identity to bypass this structural rejection;
   shared mapper targets, aliases, substrings and fuzzy similarity provide no
   equivalence evidence. The other two guards still run after a bypass.
2. `qwen_collapsed_reviewed_raw_list`: raw text matches one of the seven
   user-reviewed list shapes, and exactly one of that shape's members remains
   in the Qwen output. Whitespace around punctuation is immaterial. Only the
   finite trailing forms `1 ít`, `10/20/50 gr`, `1 muỗng canh`, `bào`, `băm`,
   `cắt sợi` (with optional colon) are accepted; these occur in the inspected
   fixture families. Arbitrary preparation/purpose clauses do not match.
3. `generic_ngo_conflicts_with_raw_ngo_gai`: the validated winning mapper
   code is `4073`, and raw text contains whole-word `ngò gai`. That code belongs
   to the current generic-ngò rule. No alternative ngò-gai code is selected.

The pipeline calls this gate only in recovery block B, after mapping and before
staging a candidate or cleaned-name rewrite. Each rejected candidate logs raw
text, Qwen output and reason; a summary counts each reason. Rejected rows retain
their unresolved matching fields. Independent weight corrections continue under
the existing pipeline rules. Allowed candidates use the original match, code,
confidence, cleaned-name preservation and weight/nutrition staging behavior.
`STANDARDIZED_CURE` and existing links are outside this guard.

## Measured impact

Run `python -X utf8 -m scripts.eda.audit_qwen_eligibility_guard --write-report`.
The JSON sibling contains input hashes, row IDs, exact candidate evidence and
reasons. Two independently built reports must be equal, and all files under
`data/` are hashed before/after the audit to verify no data changes.

| Surface | Before | After | Newly rejected |
| --- | ---: | ---: | ---: |
| Unlinked processed rows with cache + active mapper candidate | 15 | 8 | 7 |
| Validated Batch-1 rows | 8 | 8 | 0 |
| Cache keys with active mapper candidate, regardless of row links | 362 | 291 | 71 |

All seven live rejections are the specified ngò-gai collisions. The five hành-lá
and three cải-thảo rows remain eligible. Cache rejection reasons: 18 explicit
lists, 15 reviewed raw-list collapses, 38 ngò-gai identity collisions. These
counts are exclusive according to the precedence above, not additive detectors.
Eligibility here measures the recovery gate; it is not an end-to-end replay of
earlier cure precedence and does not imply that linked cache rows will change.

Hardening leaves all 71 cache rejection records and all seven eligible-row
rejection records identical to the pre-hardening comparison (verified by
replaying that comparison in memory). Thus the supplied 71/71 CORRECT_REJECT
review remains applicable, with zero current eligible false positives. All
eight Batch-1 recoveries remain allowed; all seven eligible ngò-gai rows remain
rejected. Audit input hashes are unchanged and repeated builds are equal.

The nine reported synthetic false positives now pass: `hành lá/hành hoa`,
`hành lá + hành hoa`, `hành lá - hành hoa`, `hành lá; hành hoa`,
`hành lá và hành hoa`, `hành lá hoặc hành hoa`, `hành lá hay hành hoa`,
`nấm bào ngư/nấm sò`, and `hành lá/hành lá.`. All nine were rejected by
the previous comparison. `hành lá/hành lá` remains allowed before and after.
The JSON records these ten probes individually; their baseline results were
verified against the previous comparison. Mixed identities still reject,
including third fragments before, between or after reviewed synonyms.

## Known misses

The report enumerates seven still-mappable cache examples that remain allowed:

- `Dầu mè, ngò rí` → `dầu mè ngò rí`
- `Dầu ăn, dầu điều` → `dầu ăn dầu điều`
- `Tỏi băm nhỏ, hành lá thái nhỏ` → `tỏi hành lá`
- `Tỏi băm, ngò rí` → `tỏi ngò rí` (both members retained without separators)
- `Hành lá và tỏi băm 1 ít` → `hành lá`
- `Hành lá, ngò gai` → `hành lá`
- `Hành lá, ớt sừng` → `hành lá`

None has an eligible unlinked processed row today. This is an explicit sample,
not an exhaustive miss count. Separator-free outputs, unreviewed raw-list
shapes, and structures containing abstention markers remain future work.
Processed derivatives, cure defects, stale links, Batch-2 rules, catalog gaps,
and data remediation are unchanged.

## Validation

The final hardened guard suite passed: **92 tests**, using
`python -X utf8 -m pytest tests/test_qwen_eligibility_guard.py -q`.
Tests execute the actual pipeline recovery AST block without GPU models,
preserve all eight Batch-1 patches, cover both synonym directions across all
seven separators, repeated fragments, Unicode/case/whitespace, mixed third
fragments, unreviewed shared mapper targets and meaningful internal punctuation.
They also verify that structural bypass still runs both downstream guards.
Existing parser deprecation warnings remain. The initial focused run reported
a pytest cache permission warning; the rerun with `-p no:cacheprovider` passed.

Full-suite collection remains blocked by missing `fastapi` in the current
Python environment (`test_api_endpoints.py`, `test_smart_input.py`).
The broader suite, including all Qwen/mapping regressions, passed:
**851 tests and 11 subtests**, using `python -X utf8 -m pytest -q
-p no:cacheprovider --ignore=tests/test_api_endpoints.py
--ignore=tests/test_smart_input.py --tb=short`. The sandboxed run had 169
temporary-directory fixture permission errors; the authorized rerun outside
the sandbox passed. `git diff --check` passed.
No data files, catalog, alias map, matching thresholds, or canonical outputs
were modified. No commit or push was made.
