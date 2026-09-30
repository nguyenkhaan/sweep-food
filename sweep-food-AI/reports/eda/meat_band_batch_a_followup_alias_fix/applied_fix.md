# Applied fix: Batch-A follow-up — six deferred PRESET_ALIAS repoints (70xx meat band)

Branch `fix/matching-data-followups`. Applied by `scripts/eda/apply_meat_band_batch_a_followup_safe_fix.py --apply`, tests in `tests/test_meat_band_batch_a_followup_safe_fix.py`. Machine-readable companion: `applied_fix.json`.

## Problem

`scripts/eda/apply_meat_band_batch_a_alias_safe_fix.py` (Batch A) repaired fifteen preset aliases whose correct catalog identity was exact and undisputed, and deliberately **deferred** a second set whose correct identity needed a documented *approximation* policy rather than an exact match. It pinned those deferred keys on their wrong codes so it could prove it had not dragged them along.

That policy has now been reviewed and approved. This fix applies the approved subset — six aliases, no more.

| Alias | Before | After | Rows |
|---|---|---|---:|
| `sườn cốt lết` | 7070 Giò thủ lợn | **7053 Sườn heo (xương heo)** | 24 |
| `thịt cốt lết` | 7070 Giò thủ lợn | **7053** | 11 |
| `cốt lết` | 7070 Giò thủ lợn | **7053** | 5 |
| `sườn cốt lết xắt lát` | 7070 Giò thủ lợn | **7053** | 1 |
| `bóng bì` | 7064 Chả lợn | **7031 Bì lợn** | 4 |
| `thịt bò chay lát` | 7006 Thịt bò, lưng, nạc và mỡ | **20039 Thịt chay (sườn non chay)** | 1 |

**ALIAS DECISION: `SAFE_REPOINT` for all six** (AGENTS.md §6). No alias added, no alias removed, alias-map size unchanged at 4,676.

## 1. Alias rationale

### 1.1 The cốt lết family → 7053 — approved approximation

`cốt lết` (< Fr. *côtelette*) is the Vietnamese bone-in pork loin/rib chop. The corpus glosses it itself: row `ed46d4bd` reads `2 lbs sườn cốt lết (rib cutlet)` and one recipe is titled *Sườn nướng (rib cutlet)*. 7070 `Giò thủ lợn` is pressed pork **head cheese** (553 kcal / 54.3 g fat per 100 g) — a different part, a different preparation, and a 3× energy error.

**7053 is an approved approximation, not an exact identity.** A full catalog scan for `chop|cutlet|loin` returns only 7085 (boneless tenderloin) and the beef/buffalo loins; there is no pork-chop entry. 7053 `Sườn heo (xương heo)` / *Pork, ribs, raw* (187 / 17.9 / 12.8) is the only identity carrying the bone-in pork rib semantics the raw text asserts.

It is also the identity a **prior review already chose for this exact context**. `reports/eda/suon_rib_alias_fix/applied_fix.md` §2.B resolved row `19504d22` (`2 miếng Sườn`, recipe *Cốt lết chiên nước mắm*) onto 7053 as *"Pork chop/rib-cut context; 7053 is the appropriate pork-rib identity available in this dataset."* Leaving the alias on 7070 kept the live data self-contradictory:

- *Cốt lết chiên nước mắm* → `Sườn` → **7053**
- *Sườn cốt lết chiên nước mắm* → `thịt cốt lết` → **7070**

Rejected alternatives: 7085 `Thịt nạc thăn heo` (boneless, 2.9 g fat — understates a bone-in chop), 7017 `Thịt nạc heo` (drops the rib/bone identity the raw text states), 7018 pork belly and 7083/7084 shoulder/rump (cuts the raw text contradicts).

> **`sườn cốt lết xắt lát` is redundant and repointed anyway.** `clean_culinary_query` strips the `xắt lát` slicing verb, so a row missing this exact key falls through to `sườn cốt lết` and reaches 7053 either way (verified in simulation). It is repointed rather than removed so the map never states a rejected identity — the Batch-A convention of never deleting a real Vietnamese term.

### 1.2 `bóng bì` → 7031 — approved approximation, with a recorded hydration caveat

`bóng bì` is dried/puffed pork skin, soaked before use; three of its four rows sit in the northern *canh bóng* Tết soup whose defining ingredient it is. 7064 `Chả lợn` is fried minced pork paste — not pork skin at all, and 4× off on energy.

Every other pork-skin alias in the map already pointed at 7031: `bì lợn`, `bì lợn tươi`, `da heo`, `da heo tươi` (the last two repointed off 7064 by Batch A), and decisively **`bóng bì lợn`** — the *same ingredient with an explicit pork qualifier*, whose one live row sits in *Canh bóng nấu thả*, the same dish family. `bóng bì` was simply the unrepaired duplicate of a decision this repo had already made.

> #### Hydration / density caveat — recorded, reviewed, **not a blocker**
>
> 7031 is **raw** pork skin at `water 73.3 g/100 g`. `bóng bì` as sold is a **dried** sheet at roughly 10 % water and ~3× the energy density per dry gram. 7031 therefore understates energy per dry gram.
>
> The approximation was accepted because:
>
> 1. The alternative on the table, 7064, is wrong on part **and** preparation **and** magnitude — 7031 is wrong on strictly fewer axes.
> 2. *Canh bóng* rehydrates the skin before it enters the pot, so the in-dish state is nearer 7031's hydrated profile than the dry sheet's, and the recorded weights (`2 miếng` → 100 g) are already hydrated-scale rather than dry-sheet scale.
> 3. **No dried/puffed pork-skin identity exists in the catalog.** A scan for `bì|bóng|phồng|tóp` returns only 7031, the fruit 5019 `Hồng bì`, and two shrimp-cracker entries. Creating one is catalog repair — a separate concern under AGENTS.md §18.

### 1.3 `thịt bò chay lát` → 20039 — sibling consistency, no new policy

Vegan sliced "beef". 7006 is real beef short loin — a kingdom error in a recipe (*Mì cay chay*) tagged `Ăn chay`. 20039 already declares **both** `thịt bò chay` and `bò lát chay` as aliases; `thịt bò chay lát` is the same product with the last two words transposed. 20039's dry-TVP profile is the reviewed identity for that whole dry-slice family, which carries 32 other live rows.

## 2. Repoint, not removal — fallthrough simulated

Removal was simulated for every one of the six and is **not** safe (AGENTS.md §6):

| Alias removed | Falls through to | Method | Conf |
|---|---|---|---|
| `thịt bò chay lát` | 7006 Thịt bò, lưng (**the same wrong code**) | `SUBPHRASE_CATALOG_MATCH` | 0.95 |
| `sườn cốt lết` / `thịt cốt lết` | 7074 Ruốc thịt lợn | `BERT_SEMANTIC_MATCH` | 0.44 / 0.48 |
| `cốt lết` | 12001 Bánh bích cốt | `BERT_SEMANTIC_MATCH` | 0.42 |
| `bóng bì` | 5019 Hồng bì (**a fruit**) | `BERT_SEMANTIC_MATCH` | 0.42 |

Repointing keeps `PRESET_ALIAS_MATCH` / `0.98` — the method and confidence every one of these rows already carried — so match-method semantics are unchanged by this fix; only the identity behind them moves.

## 3. Row outcomes — 46 rows, all repaired

**41 → 7053**, **4 → 7031**, **1 → 20039.** Every row was `7070`/`7064`/`7006` + `PRESET_ALIAS_MATCH` + `0.98` before, and carries its new code + `PRESET_ALIAS_MATCH` + `0.98` after. `match_method` and `match_confidence` are byte-identical across the fix; so are `raw_text`, `cleaned_name`, `required_quantity`, `unit_vi`, `unit` and `estimated_weight_g`.

There are **no cure-held rows and no row-level overrides** in this batch: no raw_text here trips any unconditional systemic-mismatch cure in `scripts/run_qwen_line_pipeline.py`, and the Qwen recovery branch is reachable only by rows carrying neither a code nor a name. All 46 are reproducible by re-running the matcher against the repaired alias map — unlike the rib fix, this one leaves no un-reproducible state.

| Row | raw_text | Recipe | w (g) | kcal | protein g | fat g | carbs g |
|---|---|---|---:|---|---|---|---|
| **`sườn cốt lết`** → 7053 (24 rows) | | | | | | | |
| `15d38df7` | 4 miếng sườn cốt lết | Sườn cốt lết sốt Teriyaki | 200.0 | 1106.0 → 374.0 | 32.0 → 35.8 | 108.6 → 25.6 | — → **null** |
| `194b844b` | 4 miếng sườn cốt lết | Sườn cốt lết rang | 200.0 | 1106.0 → 374.0 | 32.0 → 35.8 | 108.6 → 25.6 | — → **null** |
| `283747ca` | Sườn cốt lết 500 gr | Sườn cốt lết rim sả ớt | 500.0 | 2765.0 → 935.0 | 80.0 → 89.5 | 271.5 → 64.0 | — → **null** |
| `5043b577` | 800 gram sườn cốt lết | Sườn cốt lết rim nước dừa | 800.0 | 4424.0 → 1496.0 | 128.0 → 143.2 | 434.4 → 102.4 | — → **null** |
| `50b63f20` | 1 kí sườn cốt lết (đã cắt miếng mỏng) | Sườn Cốt Lết Rim | 1000.0 | 5530.0 → 1870.0 | 160.0 → 179.0 | 543.0 → 128.0 | — → **null** |
| `54da621d` | 3 miếng sườn cốt lết | Sườn cốt lết nướng mật ong | 150.0 | 829.5 → 280.5 | 24.0 → 26.8 | 81.4 → 19.2 | — → **null** |
| `57f44a9c` | Sườn cốt lết 600 gr | Sườn cốt lết rim sả ớt | 600.0 | 3318.0 → 1122.0 | 96.0 → 107.4 | 325.8 → 76.8 | — → **null** |
| `766dab66` | 4 miếng sườn cốt lết (khoảng 250gr-300gr) | Sườn cốt lết nướng sả | 200.0 | 1106.0 → 374.0 | 32.0 → 35.8 | 108.6 → 25.6 | — → **null** |
| `7e1ccc35` | 600 gr sườn cốt lết | Sườn cốt lết ram | 600.0 | 3318.0 → 1122.0 | 96.0 → 107.4 | 325.8 → 76.8 | — → **null** |
| `83fa0551` | Sườn cốt lết 600 gr | Sườn cốt lết rim nước tương (xì dầu) và mắm  | 600.0 | 3318.0 → 1122.0 | 96.0 → 107.4 | 325.8 → 76.8 | — → **null** |
| `85781101` | Sườn cốt lết 500 gr | Sườn cốt lết rim nước dừa | 500.0 | 2765.0 → 935.0 | 80.0 → 89.5 | 271.5 → 64.0 | — → **null** |
| `8be83165` | Sườn cốt lết 4 miếng | Sườn cốt lết rim nước tương (xì dầu) và mắm  | 200.0 | 1106.0 → 374.0 | 32.0 → 35.8 | 108.6 → 25.6 | — → **null** |
| `a01ec750` | 2 miếng sườn cốt lết | Sườn cốt lết nướng mềm | 100.0 | 553.0 → 187.0 | 16.0 → 17.9 | 54.3 → 12.8 | — → **null** |
| `a597e032` | Sườn cốt lết (rib cutlet) | Thịt Cốt Lết (Cutlet) Ram | 150.0 | 829.5 → 280.5 | 24.0 → 26.8 | 81.4 → 19.2 | — → **null** |
| `a95f94da` | Sườn cốt lết 500g | Cốt lết chiên sả ớt | 500.0 | 2765.0 → 935.0 | 80.0 → 89.5 | 271.5 → 64.0 | — → **null** |
| `b2e7d7e3` | 4 miếng sườn cốt lết | Sườn Cốt Lết Rim Me | 200.0 | 1106.0 → 374.0 | 32.0 → 35.8 | 108.6 → 25.6 | — → **null** |
| `bde5e5c2` | Sườn cốt lết 300 gr | Sườn cốt lết rim | 300.0 | 1659.0 → 561.0 | 48.0 → 53.7 | 162.9 → 38.4 | — → **null** |
| `c211f506` | 3 miếng sườn cốt lết | Bữa cơm gia đình | 150.0 | 829.5 → 280.5 | 24.0 → 26.8 | 81.4 → 19.2 | — → **null** |
| `c3f2bd9a` | 500 g sườn cốt lết (tầm 5 miếng sườn) | Sườn cốt lết ram mặn siêu ngon | 500.0 | 2765.0 → 935.0 | 80.0 → 89.5 | 271.5 → 64.0 | — → **null** |
| `c8a1b75f` | Sườn cốt lết: 500g | Sườn cốt lết xốt dầu hào | 500.0 | 2765.0 → 935.0 | 80.0 → 89.5 | 271.5 → 64.0 | — → **null** |
| `e11063c2` | 1 miếng sườn cốt lết | Sườn cốt lết baby | 50.0 | 276.5 → 93.5 | 8.0 → 8.9 | 27.1 → 6.4 | — → **null** |
| `ed46d4bd` | 2 lbs sườn cốt lết (rib cutlet) | Sườn nướng (rib cutlet) | 907.2 | 5016.8 → 1696.5 | 145.2 → 162.4 | 492.6 → 116.1 | — → **null** |
| `ed7a60e4` | Sườn cốt lết 4 miếng | Sườn cốt lết rim mật ong | 200.0 | 1106.0 → 374.0 | 32.0 → 35.8 | 108.6 → 25.6 | — → **null** |
| `ee7f48f4` | Sườn cốt lết 1/2 kg | Sườn cốt lết rim | 500.0 | 2765.0 → 935.0 | 80.0 → 89.5 | 271.5 → 64.0 | — → **null** |
| **`thịt cốt lết`** → 7053 (11 rows) | | | | | | | |
| `1bfbd300` | 500 g thịt cốt lết | Sườn cốt lết chiên nước mắm | 500.0 | 2765.0 → 935.0 | 80.0 → 89.5 | 271.5 → 64.0 | — → **null** |
| `3e1d6c8f` | 2 miếng thịt cốt lết | Bánh mì nướng muối ớt kèm thịt nướng | 100.0 | 553.0 → 187.0 | 16.0 → 17.9 | 54.3 → 12.8 | — → **null** |
| `5ccca8ea` | 1 kg thịt cốt lết | Sườn cốt lết nướng cam | 1000.0 | 5530.0 → 1870.0 | 160.0 → 179.0 | 543.0 → 128.0 | — → **null** |
| `609ca26e` | 700 g thịt cốt lết | Thịt Cốt Lết Khìa Nước Dừa | 700.0 | 3871.0 → 1309.0 | 112.0 → 125.3 | 380.1 → 89.6 | — → **null** |
| `77ebed1c` | 2 miếng thịt cốt lết | Eat clean (cốt lết nướng, rau và bắp luộc) | 100.0 | 553.0 → 187.0 | 16.0 → 17.9 | 54.3 → 12.8 | — → **null** |
| `7bca160e` | Thịt cốt lết | Cơm thịt heo chiên xù và cà ri Nhật (curry k | 150.0 | 829.5 → 280.5 | 24.0 → 26.8 | 81.4 → 19.2 | — → **null** |
| `cbe41198` | 3 miếng thịt cốt lết | Sườn nướng mỡ hành tóp mỡ | 150.0 | 829.5 → 280.5 | 24.0 → 26.8 | 81.4 → 19.2 | — → **null** |
| `ce9a0967` | 500 gr thịt cốt lết (được tầm 5-6 lát) | Cốt lết nướng mật ong | 500.0 | 2765.0 → 935.0 | 80.0 → 89.5 | 271.5 → 64.0 | — → **null** |
| `de143173` | 1 hộp thịt cốt lết | Thịt cốt lết rim sữa | 50.0 | 276.5 → 93.5 | 8.0 → 8.9 | 27.1 → 6.4 | — → **null** |
| `f489779c` | 4 miếng thịt cốt lết | Thịt Cốt Lết Ram | 200.0 | 1106.0 → 374.0 | 32.0 → 35.8 | 108.6 → 25.6 | — → **null** |
| `fadd1da3` | 1 kg thịt cốt lết | Thịt heo cốt lết nướng Nồi chiên không dầu | 1000.0 | 5530.0 → 1870.0 | 160.0 → 179.0 | 543.0 → 128.0 | — → **null** |
| **`cốt lết`** → 7053 (5 rows) | | | | | | | |
| `1a327d06` | Cốt lết | Cốt lếch ram mặn | 150.0 | 829.5 → 280.5 | 24.0 → 26.8 | 81.4 → 19.2 | — → **null** |
| `b4ec2e0e` | 300 gram cốt lết | Cốt lết xào xả ớt | 300.0 | 1659.0 → 561.0 | 48.0 → 53.7 | 162.9 → 38.4 | — → **null** |
| `c632242c` | Cốt lết | Cốt lết chiên | 150.0 | 829.5 → 280.5 | 24.0 → 26.8 | 81.4 → 19.2 | — → **null** |
| `cc58687b` | 4 miếng cốt lết | Cốt lết ram thơm mềm | 200.0 | 1106.0 → 374.0 | 32.0 → 35.8 | 108.6 → 25.6 | — → **null** |
| `fe922dbe` | 3 miếng cốt lết | Pork chops rim (sườn cốt lết) | 150.0 | 829.5 → 280.5 | 24.0 → 26.8 | 81.4 → 19.2 | — → **null** |
| **`sườn cốt lết xắt lát`** → 7053 (1 rows) | | | | | | | |
| `18485b70` | 750 gam sườn cốt lết xắt lát (khoảng 6 lát) | Sườn Cốt Lết Nướng | 750.0 | 4147.5 → 1402.5 | 120.0 → 134.2 | 407.2 → 96.0 | — → **null** |
| **`bóng bì`** → 7031 (4 rows) | | | | | | | |
| `4e57445f` | Bóng bì: 10g | Bánh bèo | 10.0 | 51.7 → 11.8 | 1.1 → 2.3 | 5.0 → 0.3 | 0.5 → **null** |
| `876b2f44` | Bóng bì 50 gr | Canh bóng thập cẩm | 50.0 | 258.5 → 59.0 | 5.4 → 11.7 | 25.2 → 1.4 | 2.5 → **null** |
| `978ac64d` | Bóng bì (loại mỏng dai): 2 miếng | Canh bóng cuộn bí ngòi | 100.0 | 517.0 → 118.0 | 10.8 → 23.3 | 50.4 → 2.7 | 5.1 → **null** |
| `b86566d6` | Bóng bì: 50g | Canh bóng thập cẩm | 50.0 | 258.5 → 59.0 | 5.4 → 11.7 | 25.2 → 1.4 | 2.5 → **null** |
| **`thịt bò chay lát`** → 20039 (1 rows) | | | | | | | |
| `eb46216a` | Thịt bò chay lát 100g | Mì cay chay | 100.0 | 174.0 → 310.0 | 21.5 → 50.0 | 9.5 → 1.2 | 0.7 → 25.0 |

## 4. Nutrition impact

Sums over the 46 repaired rows. Null is treated as absent, not zero.

| Group | Metric | Before | After | Delta |
|---|---|---:|---:|---:|
| **All 46 rows** | calories | 88,397.0 | 30,023.8 | **−58,373.2** |
| | protein_g | 2,565.4 | 2,919.0 | **+353.6** |
| | fat_g | 8,670.9 | 2,023.9 | **−6,647.0** |
| | carbs_g | 11.3 | 25.0 | **+13.7** |
| 41 rows → 7053 | calories | 87,137.3 | 29,466.0 | −57,671.3 |
| | protein_g | 2,521.2 | 2,820.0 | +298.8 |
| | fat_g | 8,555.6 | 2,016.9 | −6,538.7 |
| | carbs_g | 0.0 (null) | 0.0 (null) | 0.0 |
| 4 rows → 7031 | calories | 1,085.7 | 247.8 | −837.9 |
| | protein_g | 22.7 | 49.0 | +26.3 |
| | fat_g | 105.8 | 5.8 | −100.0 |
| | carbs_g | 10.6 | 0.0 (**null**) | −10.6 |
| 1 row → 20039 | calories | 174.0 | 310.0 | +136.0 |
| | protein_g | 21.5 | 50.0 | +28.5 |
| | fat_g | 9.5 | 1.2 | −8.3 |
| | carbs_g | 0.7 | 25.0 | +24.3 |

The large calorie and fat reductions are the correction, not a loss: 553 kcal per 100 g of pork chop and 517 kcal per 100 g of pork skin were both physically impossible. Protein rises in every group because each target is leaner and more protein-dense per 100 g than the code it replaced.

Per-alias breakdown: `sườn cốt lết` −35,162.3 kcal / +182.3 P · `thịt cốt lết` −16,287.0 / +84.4 · `cốt lết` −3,477.0 / +17.9 · `sườn cốt lết xắt lát` −2,745.0 / +14.2 · `bóng bì` −837.9 / +26.3 · `thịt bò chay lát` +136.0 / +28.5.

### 4.1 Null nutrition transitions

Nutrition was recomputed by `nlp.matching_integrity.stage_qwen_update` from the live target catalog row and each row's **own existing weight** — never typed by hand, never weight-edited.

| Repoint | carbs_g availability | Transition |
|---|---|---|
| 7070 → 7053 | neither code declares carbs | **none** — 41 rows null before and after |
| 7064 → 7031 | 7064 declares 5.1, 7031 declares none | **4 rows: measured → null (unknown)** |
| 7006 → 20039 | both declare all four macros | none — row stays fully populated |

The 4 `bóng bì` rows (`4e57445f`, `876b2f44`, `978ac64d`, `b86566d6`) moved from a measured carbs value to **null, not 0.0**. `calories`, `protein_g` and `fat_g` had zero transitions in either direction across all 46 rows. `0.0` is never written as a confidence sentinel, and the dataset-wide UNMATCHED contract is untouched (this fix writes no UNMATCHED row).

The script pins the reviewed null-carbs set against the live catalog and aborts if a target code gains or loses a carbs value, so this table cannot silently go stale.

## 5. Affected recipe rollups — 43 recipes

All 43 had their four `total_*` fields recomputed from their ingredient rows. **`nutrition_status` label changes: 0. `missing_nutrition_count` changes: 0** — every affected row had known nutrition before and has known nutrition after, so no recipe crossed a COMPLETE/PARTIAL/INCOMPLETE threshold.

> **Recipe-count correction.** The audit that approved this fix stated *42* recipes. The live measurement is **43**: the audit counted the four `bóng bì` rows as 3 recipes because two distinct recipes share the name *Canh bóng thập cẩm*. The script pins 43 and fails closed on any other value.

Three recipes carry two repaired rows each: *Sườn cốt lết rim*, *Sườn cốt lết rim nước tương (xì dầu) và mắm sả*, *Sườn cốt lết rim sả ớt*.

| Recipe | rows | kcal | protein g | fat g | carbs g |
|---|---:|---|---|---|---|
| Bánh bèo | 1 | 487.7 → 447.8 | 8.0 → 9.2 | 15.2 → 10.5 | 77.5 → 77.0 |
| Bánh mì nướng muối ớt kèm thịt nướng | 1 | 1957.0 → 1591.0 | 41.2 → 43.1 | 125.3 → 83.8 | 165.8 → 165.8 |
| Bữa cơm gia đình | 1 | 2726.5 → 2177.5 | 149.0 → 151.8 | 225.1 → 162.9 | 24.5 → 24.5 |
| Canh bóng cuộn bí ngòi | 1 | 1311.9 → 912.9 | 76.5 → 89.0 | 81.0 → 33.3 | 64.4 → 59.3 |
| Canh bóng thập cẩm | 1 | 1282.5 → 1083.0 | 119.2 → 125.5 | 49.4 → 25.6 | 90.2 → 87.7 |
| Canh bóng thập cẩm | 1 | 1329.0 → 1129.5 | 119.6 → 125.9 | 43.7 → 19.9 | 105.4 → 102.9 |
| Cơm thịt heo chiên xù và cà ri Nhật (curry katsu) | 1 | 1368.1 → 819.1 | 50.1 → 52.9 | 105.9 → 43.7 | 53.5 → 53.5 |
| Cốt lếch ram mặn | 1 | 1209.3 → 660.3 | 44.0 → 46.8 | 94.1 → 31.9 | 46.3 → 46.3 |
| Cốt lết chiên | 1 | 829.5 → 280.5 | 24.0 → 26.8 | 81.4 → 19.2 | 0.0 → 0.0 |
| Cốt lết chiên sả ớt | 1 | 3470.9 → 1640.9 | 95.0 → 104.5 | 292.4 → 84.9 | 112.3 → 112.3 |
| Cốt lết nướng mật ong | 1 | 3888.6 → 2058.6 | 86.4 → 95.9 | 276.3 → 68.8 | 263.5 → 263.5 |
| Cốt lết ram thơm mềm | 1 | 1308.5 → 576.5 | 36.7 → 40.5 | 112.1 → 29.1 | 37.8 → 37.8 |
| Cốt lết xào xả ớt | 1 | 1734.9 → 636.9 | 49.9 → 55.6 | 163.1 → 38.6 | 16.5 → 16.5 |
| Eat clean (cốt lết nướng, rau và bắp luộc) | 1 | 768.9 → 402.9 | 21.3 → 23.2 | 69.2 → 27.7 | 15.1 → 15.1 |
| Mì cay chay | 1 | 621.0 → 757.0 | 33.1 → 61.6 | 21.1 → 12.8 | 75.7 → 100.0 |
| Pork chops rim (sườn cốt lết) | 1 | 983.5 → 434.5 | 25.7 → 28.5 | 91.7 → 29.5 | 13.6 → 13.6 |
| Sườn cốt lết baby | 1 | 365.8 → 182.8 | 8.9 → 9.8 | 35.4 → 14.7 | 2.7 → 2.7 |
| Sườn cốt lết chiên nước mắm | 1 | 2866.0 → 1036.0 | 82.3 → 91.8 | 277.0 → 69.5 | 10.5 → 10.5 |
| Sườn Cốt Lết Nướng | 1 | 5202.6 → 2457.6 | 126.7 → 140.9 | 492.3 → 181.1 | 53.4 → 53.4 |
| Sườn cốt lết nướng cam | 1 | 5637.5 → 1977.5 | 162.2 → 181.2 | 543.1 → 128.1 | 24.4 → 24.4 |
| Sườn cốt lết nướng mật ong | 1 | 1027.2 → 478.2 | 28.2 → 31.0 | 88.1 → 25.9 | 30.3 → 30.3 |
| Sườn cốt lết nướng mềm | 1 | 553.0 → 187.0 | 16.0 → 17.9 | 54.3 → 12.8 | 0.0 → 0.0 |
| Sườn cốt lết nướng sả | 1 | 1398.0 → 666.0 | 37.9 → 41.7 | 111.1 → 28.1 | 58.7 → 58.7 |
| Sườn cốt lết ram | 1 | 3442.6 → 1246.6 | 99.1 → 110.5 | 327.9 → 78.9 | 23.9 → 23.9 |
| Sườn cốt lết ram mặn siêu ngon | 1 | 3029.7 → 1199.7 | 83.2 → 92.7 | 290.0 → 82.5 | 21.3 → 21.3 |
| Sườn cốt lết rang | 1 | 1111.7 → 379.7 | 32.3 → 36.1 | 108.6 → 25.6 | 1.1 → 1.1 |
| Sườn Cốt Lết Rim | 1 | 5629.9 → 1969.9 | 164.7 → 183.7 | 544.4 → 129.4 | 16.8 → 16.8 |
| Sườn cốt lết rim | 2 | 5013.2 → 2085.2 | 140.1 → 155.3 | 475.0 → 143.0 | 41.0 → 41.0 |
| Sườn Cốt Lết Rim Me | 1 | 1198.9 → 466.9 | 36.8 → 40.6 | 113.1 → 30.1 | 8.5 → 8.5 |
| Sườn cốt lết rim mật ong | 1 | 1632.3 → 900.3 | 34.8 → 38.6 | 153.6 → 70.6 | 27.6 → 27.6 |
| Sườn cốt lết rim nước dừa | 1 | 4714.6 → 1786.6 | 134.1 → 149.3 | 445.5 → 113.5 | 42.1 → 42.1 |
| Sườn cốt lết rim nước dừa | 1 | 3116.3 → 1286.3 | 82.6 → 92.1 | 301.8 → 94.3 | 17.3 → 17.3 |
| Sườn cốt lết rim nước tương (xì dầu) và mắm sả | 2 | 5765.6 → 2837.6 | 141.0 → 156.2 | 554.9 → 222.9 | 51.3 → 51.3 |
| Sườn cốt lết rim sả ớt | 2 | 7550.8 → 3524.8 | 204.2 → 225.1 | 674.6 → 218.1 | 164.8 → 164.8 |
| Sườn cốt lết sốt Teriyaki | 1 | 1118.6 → 386.6 | 32.6 → 36.4 | 108.6 → 25.6 | 2.5 → 2.5 |
| Sườn cốt lết xốt dầu hào | 1 | 3347.5 → 1517.5 | 91.5 → 101.0 | 282.9 → 75.4 | 108.5 → 108.5 |
| Sườn nướng (rib cutlet) | 1 | 5016.8 → 1696.5 | 145.2 → 162.4 | 492.6 → 116.1 | 0.0 → 0.0 |
| Sườn nướng mỡ hành tóp mỡ | 1 | 1134.2 → 585.2 | 36.3 → 39.1 | 101.4 → 39.2 | 18.4 → 18.4 |
| Thịt Cốt Lết (Cutlet) Ram | 1 | 976.8 → 427.8 | 25.2 → 28.0 | 91.4 → 29.2 | 13.1 → 13.1 |
| Thịt Cốt Lết Khìa Nước Dừa | 1 | 4515.0 → 1953.0 | 118.8 → 132.1 | 426.1 → 135.6 | 50.6 → 50.6 |
| Thịt Cốt Lết Ram | 1 | 1719.0 → 987.0 | 35.8 → 39.6 | 153.7 → 70.7 | 47.3 → 47.3 |
| Thịt cốt lết rim sữa | 1 | 400.7 → 217.7 | 10.4 → 11.3 | 37.2 → 16.5 | 6.0 → 6.0 |
| Thịt heo cốt lết nướng Nồi chiên không dầu | 1 | 5799.9 → 2139.9 | 166.3 → 185.3 | 559.6 → 144.6 | 18.5 → 18.5 |

## 6. Canonical propagation

Regenerated **after** processed data was correct, in the AGENTS.md §11 order: alias map → processed rows → recipe rollups → validation → `canonicalize_recipes.py` → `export_canonical_json.py` → `--check`.

| Check | Result |
|---|---|
| Canonical ingredient rows | 62,023 → 62,023 (id set identical) |
| Repaired rows reaching canonical | **42 of 46**; 42 canonical ingredient rows changed — exactly those 42 |
| Canonical recipes | 5,479 → 5,479 (**id set identical**) |
| Canonical recipes changed | 39 |
| **Canonical recipe ID drift** | **0** |
| **Representative / `candidate_rank` flips** | **0** |
| Canonical dish-name drift | 0 |
| `selected_source_url` drift | 0 |
| Mapping rows changed | 4 — quality metrics only (`nutrition_anomaly_count`, `candidate_score`, `selection_score`), all on affected recipes |

### The four rows that do not propagate

`5043b577`, `50b63f20`, `b86566d6` and `f489779c` are **absent from canonical output — and were already absent at HEAD**. Each is a `candidate_rank = 2` duplicate in a two-member canonicalization group; canonicalization keeps only the representative's ingredient rows. In all four cases **the group representative is itself repaired by this fix**, so every canonical dish is semantically correct:

| Absent row | Its recipe (rank 2) | Representative (rank 1) | Representative's repaired rows |
|---|---|---|---|
| `5043b577` | Sườn cốt lết rim nước dừa | Sườn cốt lết rim nước dừa | 1 → 7053 |
| `50b63f20` | Sườn Cốt Lết Rim | Sườn cốt lết rim | 2 → 7053 |
| `b86566d6` | Canh bóng thập cẩm | Canh bóng thập cẩm | 1 → 7031 |
| `f489779c` | Thịt Cốt Lết Ram | Thịt Cốt Lết (Cutlet) Ram | 1 → 7053 |

This is pre-existing de-duplication behaviour, not an effect of this fix — the same pattern documented in `reports/eda/suon_rib_alias_fix/applied_fix.md` §5.

## 7. Prior pin tables and tests updated

Batch A and the two earlier rib/belly fixes pinned these keys on their old codes as evidence they had not been dragged along. Those pins now assert **superseded policy** and would abort against correct data, so they were updated in this task — replaced with the new reviewed invariants, not deleted or weakened.

| File | Change |
|---|---|
| `scripts/eda/apply_meat_band_batch_a_alias_safe_fix.py` | Removed the four cốt lết keys from `ALIAS_MUST_REMAIN["7070"]` and `bóng bì` from `ALIAS_MUST_REMAIN["7064"]`; both codes keep their genuine survivors (`giò thủ`*, `chả lợn`/`chả`). Docstring gains a **SUPERSEDED DEFERRALS** section; `out_of_scope_note` rewritten to name what is *still* deferred. Re-validates as a clean no-op: 111/111 already applied. |
| `tests/test_meat_band_batch_a_alias_safe_fix.py` | `EXPECTED_CODE_ROWS` re-counted: `7070` 43→2, `7064` 5→1, `7031` 14→18. Fixture rows `cot-let-legit`/`bong-bi-legit` replaced by `gio-thu-legit`/`cha-legit` (what actually stays on those codes). The six keys moved into `OUT_OF_SCOPE_ALIASES` at their **new** values, with a new test asserting Batch A leaves them there. `test_fixture_drifted_sibling_alias_aborts` re-based onto `giò thủ` — the guard is unchanged; only its example moved, because `bóng bì → 7031` is now the *correct* value. `test_real_deferred_findings_are_still_deferred` keeps only genuinely-deferred keys and gains the still-deferred vegan analogues; new `test_real_followup_resolved_findings_hold_their_new_codes` asserts the new values **and** that Batch A neither repoints nor pins them. |
| `tests/test_suon_rib_alias_safe_fix.py` | Obsolete `sườn cốt lết`/`sườn cốt lết xắt lát` → 7070 pins replaced by `test_real_deferred_cot_let_keys_joined_7053_by_review`, which asserts the four keys now sit on `RIB_CODE` **and** that they displaced none of the aliases this fix put on 7053. Fixture value updated to the current code. |
| `tests/test_thit_ba_chi_rut_suon_alias_safe_fix.py` | Same two pins updated to 7053 in both the fixture and the real-data test; the assertion's point (Batch B did not touch them) is preserved and documented. |

No test was broadened or deleted; every replacement asserts at least as much as the pin it replaces.

## 8. Validation

| Check | Result |
|---|---|
| Processed CSV/JSON parity (ingredients, recipes) | pass — 0 differing values across 63,943 / 5,641 records |
| Canonical CSV/JSON parity (ingredients, recipes, mapping) | pass — 0 differing |
| Ingredient → recipe referential integrity (processed + canonical) | pass — 0 orphans |
| Processed recipe rollups match ingredient rows | pass — 0 mismatched |
| `canonicalize_recipes.py --check` | pass |
| Canonical regeneration determinism (re-run byte-identical) | pass |
| **Isolated replay from HEAD reproduces live data byte-for-byte** | pass |
| Alias keys added / removed | 0 / 0 (4,676 before and after) |
| Aliases changed | exactly 6 |
| Ingredient rows changed | exactly 46 of 63,943 |
| Recipe rows changed | exactly 43 of 5,641 (four `total_*` fields only) |
| Legitimate rows left on vacated codes | 7070: 2 · 7064: 1 · 7006: 203 — all byte-identical |
| UNMATCHED contract across whole dataset | pass — no populated code/name/confidence, no `0.0` sentinel |
| Script idempotence (second `--apply`) | pass — no-op, byte-identical, 46/46 already applied |
| Drift guards (alias value, sibling family, catalog name, catalog carbs, raw_text, blast radius, recipe count) | pass — abort before any write |
| `git diff --check` | clean |

**Tests: 1,243 passed** (full suite, 11 subtests). Focused: 53 in `tests/test_meat_band_batch_a_followup_safe_fix.py`. Regression group (this fix + Batch A + rib + belly + matcher alias resolution + matching integrity): 290 passed.

`tests/test_api_endpoints.py` and `tests/test_smart_input.py` still fail to **collect** because `fastapi` is absent — a pre-existing environment limitation this task does not touch (AGENTS.md §15). They are excluded from the run above and from the 1,243 count.

## 9. Explicitly out of scope

Left exactly as-is; this was not broadened into a 70xx cleanup. A regression test asserts each still holds its current value.

- **The remaining vegan analogues**: `đùi gà chay` → 7088, `xúc xích chay` → 7077, `nem chua chay` → 7073. All three are kingdom errors in `Ăn chay`-tagged recipes, but each is a **wet, ready-formed** analogue while 20039 is **dry TVP** (`water 8.0`, `protein 50.0`). Mapping them at as-purchased weight would overstate protein 3–5× (e.g. `Đùi gà chay 250 gr` → 125 g protein). The review did not settle the wet-vs-dry form policy, so they stay deferred. Note that **removal is not an escape hatch** — all three fall back onto the identical wrong code via `SUBPHRASE_CATALOG_MATCH` at 0.95.
- `thịt cua chay` → 8069 `Thịt cua` — same defect class, same blast mechanism, 1 row.
- Vegan seasoning analogues: `nước mắm chay` → 13017, `dầu hào chay` → 13027.
- Catalog repair (including creating a dried-pork-skin or wet-vegan-analogue identity).
- Any matcher-level `chay` guard.
- **Cốt-lết coverage expansion.** 13 further pork cốt-lết rows remain `UNMATCHED` because their `cleaned_name` carries a qualifier no alias covers. Three of them are `cốt lết bỏ xương` — **boneless**, and therefore explicitly *not* 7053 material; they belong on a boneless-loin identity a later review must choose. The others are `sườn cốt lết heo`, `thịt cốt lết iberico`, `cốt lết dày 1 5 cm`, `400 sườn cốt lết`, and similar. A further row, `sườn cốt lết chay`, is vegan and also stays UNMATCHED. Regression tests assert the boneless and vegan rows did **not** join 7053.
- Every other 70xx finding: `sườn bò`/`dẻ sườn bò` → 7094, `mỡ gà`, `thịt heo quay`, `nạm bò`, `ba chỉ bò`, `chả chiên`, `mỡ nước`, `tóp mỡ`, `gà tre`, catalog `name_vi` corruption, `xương bò`, the 7096 corruption, cleaner/matcher policy, stale-code remediation.

## 10. Regeneration note

Unlike the rib fix, **every one of the 46 rows here is reproducible**. All are resolved by the alias repoint alone — no row-level override, no cure-held row — so a future full re-match from raw text reproduces this outcome without any decision needing to be re-applied by hand.
