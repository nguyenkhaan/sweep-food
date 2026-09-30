# Applied fix: rib/bone (sườn) PRESET_ALIAS contamination on 7069 / Giò lụa

Branch `fix/matching-data-followups`. Applied by `scripts/eda/apply_suon_rib_alias_safe_fix.py --apply`, tests in `tests/test_suon_rib_alias_safe_fix.py`. Machine-readable companion: `applied_fix.json`.

## Problem

Five rib/bone preset aliases all resolved to **7069 / Giò lụa** (a steamed minced-pork sausage), an identity unrelated to pork rib. The catalog already holds the correct rib identity as **7053 / Sườn heo (xương heo)** (`Pork, ribs, raw`), and eight other rib/bone aliases already pointed there correctly. 12 processed ingredient rows sat on the wrong identity as a result.

A latent regression made ordering critical: the alias `sườn non heo` pointed at 7069, yet the 15 processed rows whose `cleaned_name` is `sườn non heo` were already correctly on 7053. Regenerating processed data **before** repairing the alias map would have regressed all 15 onto 7069. The alias map was therefore fixed first.

## 1. Alias decisions (5)

| Alias | Before | After | Rationale |
|---|---|---|---|
| `xương sườn heo` | 7069 | **7053** | Explicitly qualified as pork rib; globally safe. |
| `sườn non heo` | 7069 | **7053** | Explicitly qualified as pork rib; globally safe. |
| `sươ n non heo` | 7069 | **7053** | Explicitly qualified as pork rib; globally safe. |
| `sườn` | 7069 | *(removed)* | Bare term spans pork rib, pork chop, beef rib and ambiguous uses. No safe global target. |
| `dẻ sườn` | 7069 | *(removed)* | Not species-safe on its own. |

No new broad `sườn` alias was added. Rows using the removed aliases were resolved individually on recipe evidence (below), never by a global rule.

Unchanged and verified still on 7053: `sườn heo`, `sườn non`, `xương heo`, `xương lợn`, `xương ống`, `sườn thăn`, `sườn cọng`, `sươ n non`.

> **Note on `sươ n non heo`.** This odd alias key is real, not a typo. The source row's `raw_text` is NFD-decomposed (`sươ` + combining U+0300 + `n`), so the name cleaner dropped the combining mark and left a gap. The remediation script pins that row's `raw_text` as explicit `\u` escapes so the literal cannot be silently re-normalized by an editor.

## 2. Row decisions (12)

**10 → 7053**, **2 → UNMATCHED**.

### A. Remapped to 7053 via the three alias re-points (6)

| Row | raw_text | Recipe | kcal before → after |
|---|---|---|---|
| `a56ffa1e` | 400 gr xương / sườn heo | Canh súp lơ sườn heo nấu miến | 820.0 → 748.0 |
| `25f14bf1` | 500g xương sườn heo | Nui - Mì Nấu Gà Sườn Heo | 1025.0 → 935.0 |
| `0f84cccc` | Xương sườn heo 1 kg | Canh khoai tây xương hầm | 2050.0 → 1870.0 |
| `d1400f26` | Xương sườn heo 400 gr | Canh xương khoai sọ nấu sấu | 820.0 → 748.0 |
| `5fbe1cf4` | Xương sườn heo 8 miếng | Canh rau má | 820.0 → 748.0 |
| `dfd609c0` | 500 gr sườn non heo | Sườn heo nấu đậu | 1025.0 → 935.0 |

### B. Remapped to 7053 on row-level recipe evidence (4)

These used the two removed aliases; each was resolved individually.

| Row | raw_text | Recipe | Evidence | kcal before → after |
|---|---|---|---|---|
| `36db3701` | 300 g sườn | Canh cải thìa nấu sườn non | Recipe is a pork-rib soup. | 615.0 → 561.0 |
| `1da91cd2` | 15 g sườn | Cháo sườn heo cà rốt | Recipe names pork rib explicitly. | 30.8 → 28.1 |
| `19504d22` | 2 miếng Sườn | Cốt lết chiên nước mắm | Pork chop/rib-cut context; 7053 is the appropriate pork-rib identity available in this dataset. | 205.0 → 187.0 |
| `ac206911` | 4 dẻ sườn | Dẻ Sườn Nướng Sốt Thái - BBQ Pork Rib with Thai Sauce | Recipe title states **BBQ Pork Rib**. | 1230.0 → 1122.0 |

### C. Cleared to UNMATCHED (2)

| Row | raw_text | Recipe | Reason |
|---|---|---|---|
| `c9c53624` | 3 lát sườn | Thịt chân giò chiên nước mắm | Ingredient identity is ambiguous relative to a pork-hock recipe; not force-resolved. |
| `78e45baf` | Sườn 1 kg | Sườn bò hầm mềm | **Beef rib.** No valid beef-rib catalog entry exists. Not mapped to pork 7053, nor to a beef shank/brisket code naming a different cut. |

UNMATCHED contract applied and asserted: `master_ingredient_code`, `master_ingredient_name`, `match_confidence` and all four nutrition fields are null/blank; `match_method` = `UNMATCHED`; `raw_text`, `cleaned_name` and `estimated_weight_g` preserved. `0.0` is never used as a missing-confidence sentinel.

All 10 remapped rows carry `7053` / `Sườn heo (xương heo)` / `PRESET_ALIAS_MATCH` / `0.98`, with nutrition recomputed by `nlp.matching_integrity.stage_qwen_update` from the live 7053 profile and each row's own weight. 7053 declares no `carbs_g`, so every remapped row's `carbs_g` is **null (unknown), not 0.0**.

## 3. Nutrition impact

Sums over the affected rows. Null is treated as absent, not zero.

| Group | Metric | Before | After | Delta |
|---|---|---:|---:|---:|
| All 12 rows | calories | 10998.3 | 7882.1 | -3116.2 |
| All 12 rows | protein_g | 906.6 | 754.5 | -152.1 |
| All 12 rows | fat_g | 804.7 | 539.5 | -265.2 |
| All 12 rows | carbs_g | 96.6 | 0.0 | -96.6 |
| 10 remapped → 7053 | calories | 8640.8 | 7882.1 | -758.7 |
| 10 remapped → 7053 | protein_g | 712.3 | 754.5 | +42.2 |
| 10 remapped → 7053 | fat_g | 632.2 | 539.5 | -92.7 |
| 10 remapped → 7053 | carbs_g | 75.9 | 0.0 | -75.9 |
| 2 cleared → UNMATCHED | calories | 2357.5 | 0.0 | -2357.5 |
| 2 cleared → UNMATCHED | protein_g | 194.3 | 0.0 | -194.3 |
| 2 cleared → UNMATCHED | fat_g | 172.5 | 0.0 | -172.5 |
| 2 cleared → UNMATCHED | carbs_g | 20.7 | 0.0 | -20.7 |

The 10 remapped rows *gain* protein (+42.2 g) while losing calories and fat: 7053 is leaner and more protein-dense per 100 g than 7069. Their carbs drop to zero in the sum only because 7053 has no carbs value — those rows are now null, not measured zero.

## 4. Affected recipe rollups (12)

| Recipe | kcal | protein | fat | carbs | missing | status |
|---|---|---|---|---|---|---|
| Canh cải thìa nấu sườn non | 623.5 → 569.5 | 51.5 → 54.5 | 45.1 → 38.5 | 6.5 → 1.1 | 0 → 0 | COMPLETE |
| Canh khoai tây xương hầm | 2964.1 → 2784.1 | 205.7 → 215.7 | 173.9 → 151.9 | 189.5 → 171.5 | 2 → 2 | PARTIAL |
| Canh rau má | 1834.8 → 1762.8 | 184.7 → 188.7 | 92.9 → 84.1 | 70.2 → 63.0 | 2 → 2 | PARTIAL |
| Canh súp lơ sườn heo nấu miến | 1063.9 → 991.9 | 72.0 → 76.0 | 60.5 → 51.7 | 60.5 → 53.3 | 0 → 0 | COMPLETE |
| Canh xương khoai sọ nấu sấu | 2116.1 → 2044.1 | 88.4 → 92.4 | 61.1 → 52.3 | 307.7 → 300.5 | 2 → 2 | PARTIAL |
| Cháo sườn heo cà rốt | 123.9 → 121.2 | 4.7 → 4.9 | 2.4 → 2.1 | 20.8 → 20.5 | 0 → 0 | COMPLETE |
| Cốt lết chiên nước mắm | 740.7 → 722.7 | 45.8 → 46.8 | 18.2 → 16.0 | 99.5 → 97.7 | 1 → 1 | PARTIAL |
| Dẻ Sườn Nướng Sốt Thái - BBQ Pork Rib with Thai Sauce | 1296.0 → 1188.0 | 103.6 → 109.6 | 90.3 → 77.1 | 24.3 → 13.5 | 1 → 1 | INCOMPLETE |
| Nui - Mì Nấu Gà Sườn Heo | 1253.9 → 1163.9 | 95.2 → 100.2 | 81.5 → 70.5 | 39.4 → 30.4 | 3 → 3 | PARTIAL |
| Sườn bò hầm mềm | 4309.1 → 2259.1 | 413.1 → 244.1 | 221.8 → 71.8 | 176.2 → 158.2 | 0 → 1 | COMPLETE → PARTIAL |
| Sườn heo nấu đậu | 3045.1 → 2955.1 | 147.7 → 152.7 | 81.6 → 70.6 | 428.7 → 419.7 | 8 → 8 | INCOMPLETE |
| Thịt chân giò chiên nước mắm | 320.9 → 13.4 | 26.2 → 0.9 | 22.5 → 0.0 | 5.1 → 2.4 | 2 → 3 | INCOMPLETE |

One `nutrition_status` label transition: **Sườn bò hầm mềm** COMPLETE → PARTIAL, the correct consequence of clearing its beef-rib row. *Thịt chân giò chiên nước mắm* gains a missing-nutrition row but was already INCOMPLETE.

## 5. Canonical propagation

Regenerated after processed data was correct, in the required order.

- Canonical ingredient rows: 62,023 → 62,023 (id set identical).
- **11 of 12** rows propagate to canonical; **11** canonical ingredient rows changed — exactly those 11.
- 11 canonical recipes changed; 12 mapping rows changed (all 12 target recipes; the 12th changed only its quality metrics).
- Canonical recipe ID drift: **0**. Representative / `candidate_rank` flips: **0**. Canonical recipe set identical (5,479).

### The one row that does not propagate

`0f84cccc` (`Xương sườn heo 1 kg`, recipe *Canh khoai tây xương hầm*) is **absent from canonical output — and was already absent at HEAD**. Its recipe is a non-representative duplicate (rank 2) of canonical group *canh xương hầm khoai tây*; canonicalization keeps only the representative's ingredient rows. This is pre-existing de-duplication behaviour, not an effect of this fix. The group's representative (`86f66ac8`, *Canh xương hầm khoai tây*) already resolves its `Xương heo 300 gr` row to 7053 via the correct `xương heo` alias, so the canonical output for that dish is semantically correct.

## 6. Validation

| Check | Result |
|---|---|
| Processed CSV/JSON parity (ingredients, recipes) | pass — 0 differing |
| Canonical CSV/JSON parity (ingredients, recipes, mapping) | pass — 0 differing |
| Ingredient → recipe referential integrity (processed + canonical) | pass — 0 orphans |
| Processed recipe rollups match ingredient rows | pass — 0 mismatched |
| `canonicalize_recipes.py --check` | pass |
| Canonical regeneration determinism (re-run byte-identical) | pass |
| Isolated replay from HEAD reproduces live data byte-for-byte | pass |
| Unrelated processed rows changed | 0 (12 of 63,943 ingredient rows; 12 of 5,641 recipes) |
| UNMATCHED contract across whole dataset | pass — no populated code/name/confidence, no 0.0 sentinel |
| Script idempotence (second `--apply`) | pass — no-op, byte-identical |
| Drift guards (raw_text, alias value, catalog identity) | pass — abort before any write |
| `git diff --check` | clean |

Tests: **47 passed** in `tests/test_suon_rib_alias_safe_fix.py` (27 fixture + 20 real-data); full suite **1032 passed**. `tests/test_api_endpoints.py` and `tests/test_smart_input.py` still fail to collect because `fastapi` is absent — a pre-existing environment issue this task does not touch.

## 7. Explicitly out of scope

Left exactly as-is for a later audit; this was not broadened into a 70xx cleanup:

- `sườn cốt lết` → 7070 / Giò thủ lợn
- `sườn cốt lết xắt lát` → 7070
- `thịt ba chỉ rút sườn` → 7082 / Lòng gà
- `sườn bò` → 7094 / Thịt bắp bò
- `dẻ sườn bò` → 7094
- `canh sườn khoai sọ` → 2013

A regression test asserts each of these still holds its current value.

## 8. Regeneration caveat

The 6 alias-driven remaps are reproducible by re-running the matcher. The **4 row-level remaps and 2 clears are not** — they are reviewed, row-specific overrides that exist because no safe global alias covers bare `sườn` / `dẻ sườn`. A future full re-match from raw text will leave those 6 rows UNMATCHED unless these decisions are re-applied.

