"""Apply the reviewed Batch-A FOLLOW-UP PRESET_ALIAS repoints from the 70xx
meat-band audit. Default previews; --apply writes.

scripts/eda/apply_meat_band_batch_a_alias_safe_fix.py repaired fifteen aliases
whose correct identity was exact and undisputed, and deliberately DEFERRED a
second set for which the correct identity needed a documented approximation
policy. That policy has now been reviewed and approved, and this script applies
the approved subset of it -- six aliases, no more.

    alias                     from                      to
    ------------------------------------------------------------------------
    sườn cốt lết              7070 Giò thủ lợn          7053 Sườn heo (xương heo)
    thịt cốt lết              7070 Giò thủ lợn          7053 Sườn heo (xương heo)
    cốt lết                   7070 Giò thủ lợn          7053 Sườn heo (xương heo)
    sườn cốt lết xắt lát      7070 Giò thủ lợn          7053 Sườn heo (xương heo)
    bóng bì                   7064 Chả lợn              7031 Bì lợn
    thịt bò chay lát          7006 Thịt bò, lưng...     20039 Thịt chay (sườn non chay)

REVIEWED RATIONALE (AGENTS.md §5 -- none of these rests on code proximity,
lexical similarity or "better than unmatched"):

  * THE CỐT LẾT FAMILY. "cốt lết" (< Fr. côtelette) is the Vietnamese bone-in
    pork loin/rib chop. The corpus glosses it itself: one row reads
    "2 lbs sườn cốt lết (rib cutlet)" and one recipe is titled
    "Sườn nướng (rib cutlet)". 7070 "Giò thủ lợn" is pressed pork HEAD CHEESE
    (553 kcal / 54.3 g fat per 100 g) -- a different part, a different
    preparation and a 3x energy error.

    7053 "Sườn heo (xương heo)" / "Pork, ribs, raw" (187 / 17.9 / 12.8) is the
    APPROVED APPROXIMATION, not an exact identity: the catalog carries no
    pork-chop or cutlet entry at all (a full scan for chop/cutlet/loin returns
    only 7085 boneless tenderloin and the beef/buffalo loins). 7053 is the only
    catalog identity that carries the bone-in pork rib semantics the raw text
    asserts, and it is the identity a prior review already chose for this exact
    context: row 19504d22 ("2 miếng Sườn" in recipe *Cốt lết chiên nước mắm*)
    was approved onto 7053 in reports/eda/suon_rib_alias_fix/applied_fix.md §2.B
    as "Pork chop/rib-cut context; 7053 is the appropriate pork-rib identity
    available in this dataset." Leaving the alias on 7070 kept the live data
    self-contradictory: *Cốt lết chiên nước mắm* resolved to 7053 while
    *Sườn cốt lết chiên nước mắm* resolved to 7070.

    Rejected alternatives: 7085 "Thịt nạc thăn heo" (boneless trimmed
    tenderloin, 2.9 g fat -- understates a bone-in chop), 7017 "Thịt nạc heo"
    (drops the rib/bone identity the raw text states), 7018 pork belly and
    7083/7084 shoulder/rump (cuts the raw text contradicts).

  * BÓNG BÌ. "bóng bì" is dried/puffed pork skin, soaked before use; three of
    its four rows are in the northern *canh bóng* Tết soup whose defining
    ingredient it is. 7064 "Chả lợn" is fried minced pork paste -- not pork
    skin at all, and 4x off on energy. 7031 "Bì lợn" / "Pork, skin, raw" is the
    APPROVED APPROXIMATION: right animal, right part, wrong hydration state
    (see the caveat below). Every other pork-skin alias in the map already
    points there -- "bì lợn", "bì lợn tươi", "da heo", "da heo tươi" (the last
    two repointed off 7064 by Batch A), and decisively "bóng bì lợn", the SAME
    ingredient with an explicit pork qualifier, whose one live row sits in
    *Canh bóng nấu thả*, the same dish family. "bóng bì" was simply the
    unrepaired duplicate of a decision this repo had already made.

    HYDRATION/DENSITY CAVEAT, recorded and reviewed as NOT a blocker: 7031 is
    raw skin at water 73.3 g/100 g, while bóng bì as sold is a dried sheet at
    roughly 10 % water and ~3x the energy density per gram. The approximation
    was accepted because (a) the alternative on the table, 7064, is wrong on
    part AND preparation AND magnitude, so 7031 is wrong on strictly fewer
    axes; (b) canh bóng rehydrates the skin before it enters the pot, so the
    in-dish state is nearer 7031's hydrated profile than the dry sheet's, and
    the recorded weights ("2 miếng" -> 100 g) are already hydrated-scale; and
    (c) no dried- or puffed-pork-skin identity exists anywhere in the catalog
    (a scan for bì/bóng/phồng/tóp returns only 7031, the fruit 5019 "Hồng bì"
    and two shrimp-cracker entries). Creating one is catalog repair, a separate
    concern under AGENTS.md §18.

  * THỊT BÒ CHAY LÁT. Vegan sliced "beef". 7006 is real beef short loin -- a
    kingdom error in a recipe tagged "Ăn chay". This is pure sibling-consistency
    repair with no new policy: 20039 "Thịt chay (sườn non chay)" /
    "Textured vegetable protein (Soy meat)" already declares BOTH
    "thịt bò chay" and "bò lát chay" as aliases, and "thịt bò chay lát" is the
    same product with the last two words transposed. 20039's dry-TVP profile
    (water 8.0, protein 50.0) is the reviewed identity for that whole
    dry-slice family, which carries 32 live rows today.

ALIAS DECISION: SAFE_REPOINT for all six (AGENTS.md §6).

Repoint, not removal. Removal was simulated for every one of the six and is
NOT safe: with the alias gone, "thịt bò chay lát" falls straight back onto
7006 via SUBPHRASE_CATALOG_MATCH at 0.95, and the cốt lết keys fall onto
BERT_SEMANTIC_MATCH junk (7074 "Ruốc thịt lợn", 12001 "Bánh bích cốt") while
"bóng bì" lands on the fruit 5019 "Hồng bì". Repointing keeps
PRESET_ALIAS_MATCH / 0.98 -- the same method and confidence every one of these
rows already carries -- so match-method semantics are unchanged by this fix;
only the identity behind them moves.

BLAST RADIUS (measured against the live 63,943-row processed dataset, not
inferred from the audit): exactly 46 ingredient rows across 43 recipes resolve
through these six alias keys, and all 46 are repaired here.

  41 cốt lết rows -> 7053   (24 + 11 + 5 + 1 across the four keys, 38 recipes)
   4 bóng bì rows -> 7031   (4 recipes)
   1 thịt bò chay lát row -> 20039 (1 recipe)

There are NO cure-held rows in this batch and NO row-level overrides: no
raw_text here trips any systemic-mismatch cure in
scripts/run_qwen_line_pipeline.py, and the Qwen recovery branch is reachable
only by rows that carry neither a code nor a name, which none of these do. All
46 are therefore reproducible by re-running the matcher against the repaired
alias map -- unlike the rib fix, this one leaves no un-reproducible state.

NULL NUTRITION TRANSITIONS (AGENTS.md §4, §9). Nutrition is recomputed by
nlp.matching_integrity.stage_qwen_update from the live target catalog row and
each row's own existing weight -- never typed by hand, and never weight-edited.
Two of the three repoints change which nutrients are KNOWN:

  * 7070 -> 7053: neither code declares carbs_g, so all 41 cốt lết rows keep
    carbs_g null before and after. No transition.
  * 7064 -> 7031: 7064 declares carbs_g 5.1, 7031 declares none. All 4 bóng bì
    rows move from a measured carbs value to NULL (unknown) -- not to 0.0.
  * 7006 -> 20039: both declare all four macros; the single row stays fully
    populated.

Missing nutrition is never converted to zero, and 0.0 is never written as a
confidence sentinel.

SIBLING SAFETY. Every vacated code keeps its legitimate rows and aliases:
7070 keeps "giò thủ"/"giò thủ lợn"/"giò thủ lợn chín" and its 2 giò-thủ rows,
7064 keeps "chả lợn"/"chả" and its 1 chả row, 7006 keeps its beef-loin family
and 203 other rows. Those aliases are pinned before and after the write, and
every processed row on a vacated code that is not in the reviewed repair set is
asserted byte-identical.

EXPLICITLY OUT OF SCOPE (recorded by the audit, deliberately unchanged here):
the remaining vegan analogues "đùi gà chay" -> 7088, "xúc xích chay" -> 7077
and "nem chua chay" -> 7073, which need a wet-vs-dry analogue FORM policy this
review did not settle; "thịt cua chay" -> 8069; the vegan seasoning analogues
("nước mắm chay" -> 13017, "dầu hào chay" -> 13027); any catalog repair; any
matcher-level "chay" guard; and cốt-lết coverage expansion. That last one is
specific and measured: 13 further pork cốt-lết rows are currently UNMATCHED
because their cleaned_name carries a qualifier no alias covers
("cốt lết bỏ xương" x3 -- which are BONELESS and do NOT belong on 7053,
"sườn cốt lết heo", "thịt cốt lết iberico", "cốt lết dày 1 5 cm", ...), plus
1 vegan row "sườn cốt lết chay". None of them is inside this fix's blast
radius and none of them moves. No other 70xx finding is touched.

Safety model (fail closed, idempotent, dry-run by default):
  - Every alias edit is pinned in BOTH directions: the key must currently hold
    its reviewed old code, or already hold the reviewed new code (post-fix).
    Any third value aborts before anything is written. Every alias key outside
    the six is verified byte-identical, and the map size may not change.
  - Sibling aliases on all three vacated codes and on the three target codes
    are asserted intact before and after, so this fix cannot quietly widen.
  - Every target row is pinned by id AND exact raw_text AND its exact pre-fix
    match fields. Each must be either "pending" or "already_applied"; anything
    else aborts the ENTIRE run before any write.
  - The pinned id sets are cross-checked against the rows the aliases can
    actually reach, recomputed from live data through the real
    normalize_vietnamese_text/clean_culinary_query functions and the real
    Stage-1 catalog index. Drift in either direction aborts.
  - Every code this fix reads or writes must exist in the live catalog under
    its exact current name_vi, checked through the same identity guard
    nlp.matching_integrity.stage_qwen_update enforces for the Qwen pipeline.
  - No repaired row's raw_text may match any unconditional systemic-mismatch
    cure pattern, so a repaired identity cannot be silently overridden by a
    later pipeline run.
  - Rows/aliases already in "already_applied" state are left byte-identical
    (idempotent reruns produce no diff and no error).

Scope: data/processed/viendinhduong/ingredient_alias_map.json and
data/processed/recipes/recipe_ingredients.{csv,json} plus the recipe-level
rollup totals and nutrition_status/missing_nutrition_count in
data/processed/recipes/recipes.{csv,json}. Canonical outputs are intentionally
NOT regenerated here -- regenerate them via scripts/canonicalize_recipes.py
(then scripts/export_canonical_json.py) after this fix is applied, per
AGENTS.md §11.
"""

import argparse
import json
import re
from pathlib import Path

from nlp.entity_matcher import (
    VietnameseIngredientMatcher,
    clean_culinary_query,
    normalize_vietnamese_text,
)
from nlp.matching_integrity import stage_qwen_update
from nlp.nutrition import nutrition_value
from scripts.eda.apply_qwen_class_d_safe_fix import _recompute_status, write_csv
from scripts.eda.apply_qwen_safe_fix import (
    ING,
    ING_JSON,
    RECIPES_CSV,
    RECIPES_JSON,
    _apply_rollups,
    read_csv,
    read_json,
    recompute_recipe_rollups,
    write_json,
)

ROOT = Path(__file__).resolve().parents[2]
ALIAS_PATH = ROOT / "data/processed/viendinhduong/ingredient_alias_map.json"
MASTER = ROOT / "data/processed/viendinhduong/master_ingredients_nutrition.csv"
OUT = ROOT / "reports/eda/meat_band_batch_a_followup_alias_fix"

PRESET_ALIAS_METHOD = "PRESET_ALIAS_MATCH"
PRESET_ALIAS_CONFIDENCE = "0.98"

# --- Catalog identities ----------------------------------------------------

# Every code this fix reads or writes, with its exact current live name_vi.
# Verified before anything is written: a code that has been silently repointed
# to a different ingredient must not be published under a stale name
# (AGENTS.md §3 -- the live catalog is authoritative for identity).
CODE_NAMES = {
    "7006": "Thịt bò, lưng, nạc và mỡ",
    "7031": "Bì lợn",
    "7053": "Sườn heo (xương heo)",
    "7064": "Chả lợn",
    "7070": "Giò thủ lợn",
    "20039": "Thịt chay (sườn non chay)",
}

# Codes that declare no carbs_g in the live catalog, so a row repaired onto one
# of them must report carbs_g as NULL (unknown), never 0.0. Asserted against the
# live catalog in build_plan() rather than trusted from this literal.
NULL_CARBS_CODES = frozenset({"7031", "7053", "7070"})

# --- Alias-map edits -------------------------------------------------------

# alias key -> (reviewed current code, reviewed correct code). Repoints only;
# no key is added and no key is removed.
ALIAS_REPOINTS = {
    "sườn cốt lết": ("7070", "7053"),
    "thịt cốt lết": ("7070", "7053"),
    "cốt lết": ("7070", "7053"),
    "sườn cốt lết xắt lát": ("7070", "7053"),
    "bóng bì": ("7064", "7031"),
    "thịt bò chay lát": ("7006", "20039"),
}
assert len(ALIAS_REPOINTS) == 6
assert not {old for old, _ in ALIAS_REPOINTS.values()} - set(CODE_NAMES)
assert not {new for _, new in ALIAS_REPOINTS.values()} - set(CODE_NAMES)

# "sườn cốt lết xắt lát" is REDUNDANT, and repointed anyway. clean_culinary_query
# strips the "xắt lát" slicing verb, so the key is reached only when the exact
# raw spelling survives normalization; a row that misses it falls through to
# "sườn cốt lết" and lands on the same code either way (verified in simulation).
# It is repointed rather than removed so the map never states an identity this
# review has rejected, matching the Batch-A convention of never deleting a real
# Vietnamese term.
REDUNDANT_ALIASES = ("sườn cốt lết xắt lát",)

# Sibling aliases that must survive this fix on their current code. These are
# the evidence that each vacated code remains a legitimate identity with a
# legitimate alias family, and that only the six listed keys were wrong.
#
# The three TARGET families are pinned too, because each repoint's justification
# is that the target already owns this ingredient's sibling terms: "bóng bì lợn"
# on 7031 and "thịt bò chay"/"bò lát chay" on 20039 are the precedent this fix
# rests on, and "sườn heo"/"xương heo" on 7053 are the rib family the cốt lết
# keys are joining.
#
# 7006 is pinned to a REVIEWED SUBSET rather than its full 46-key alias family:
# most of that family is crawl noise ("300 thịt bò", "k thịt bò", "vuông thịt
# bò") this review has not audited, and pinning it would assert a correctness
# this task did not establish. The keys listed are the beef-loin identity heads
# plus "thịt bò lát", the word-order neighbour of the repointed key -- the ones
# that actually carry this fix's reasoning. Widening is prevented independently:
# apply_alias_changes() requires every key outside the six to be byte-identical.
ALIAS_MUST_REMAIN = {
    "7006": ("thịt bò lưng nạc và mỡ", "thịt bò lưng nạc và mỡ tươi",
             "thịt bò lát", "thịt bò thăn", "thịt bò phi lê", "thịt bò xay"),
    "7031": ("bì lợn tươi", "bì lợn", "bóng bì lợn", "da heo", "da heo tươi"),
    "7053": ("sườn heo", "sườn non", "xương heo", "xương lợn", "xương ống",
             "sườn thăn", "sườn cọng", "xương sườn heo", "sườn non heo"),
    "7064": ("chả lợn", "chả"),
    "7070": ("giò thủ lợn chín", "giò thủ lợn", "giò thủ"),
    "20039": ("thịt chay", "thịt bò chay", "sườn non chay", "bò lát chay",
              "sườn chay", "thịt lát chay", "heo lát chay", "thịt vụn chay",
              "đạm đậu nành"),
}
assert set(ALIAS_MUST_REMAIN) == set(CODE_NAMES)
assert not set(ALIAS_REPOINTS) & {k for v in ALIAS_MUST_REMAIN.values() for k in v}

# The unconditional systemic-mismatch cures in scripts/run_qwen_line_pipeline.py
# section A -- the ones that fire on raw_text alone, with no dependence on the
# row's current code. A repaired row whose raw_text tripped one of these would
# have its new identity silently overwritten on the next pipeline run, so none
# may. (The remaining cures in that section are gated on a specific current
# m_code -- 8041, 8011, 3015, 10001 -- none of which this fix writes.)
# Re-declared here rather than imported because that module is a top-level
# script that executes the whole pipeline on import.
CURE_RAW_PATTERNS = (
    re.compile(r"\bđậu bắp\b"),
    re.compile(r"\bcá cam\b"),
    re.compile(r"\bcá nục chuối\b"),
    re.compile(r"\bcủ sen\b"),
    re.compile(r"\bngó sen\b"),
    re.compile(r"\bbắp bò\b"),
    re.compile(r"\bnấm chân gà\b"),
)

# --- Row-level scope -------------------------------------------------------

# The 46 rows repaired by this fix, grouped by the alias that reaches them and
# pinned by id and exact raw_text. Every one is resolved by the repoint alone:
# there are no row-level overrides here, so re-running the matcher reproduces
# all 46.
REPAIR_ROWS = {
    "sườn cốt lết": (
        ("15d38df7-bb77-4078-a3ef-1704417ab570", "4 miếng sườn cốt lết"),
        ("194b844b-442d-4f3f-b1c9-347e6921cba4", "4 miếng sườn cốt lết"),
        ("283747ca-acad-4065-9f98-041a10191782", "Sườn cốt lết 500 gr"),
        ("5043b577-83df-41a6-89a7-1925d96fa195", "800 gram sườn cốt lết"),
        ("50b63f20-43b1-47e4-897b-a86f816b5e87", "1 kí sườn cốt lết (đã cắt miếng mỏng)"),
        ("54da621d-1512-4ebb-98d2-0cdeb1adf4c1", "3 miếng sườn cốt lết"),
        ("57f44a9c-67a9-4ed6-8d36-307c78a2aacd", "Sườn cốt lết 600 gr"),
        ("766dab66-9421-4786-9f4e-7b1fd9fef5cd", "4 miếng sườn cốt lết (khoảng 250gr-300gr)"),
        ("7e1ccc35-9c18-4f76-8c44-bc1b33b593e7", "600 gr sườn cốt lết"),
        ("83fa0551-a397-4a29-8647-4163f1dd99dd", "Sườn cốt lết 600 gr"),
        ("85781101-d3da-4067-bc95-7f22ace36c6c", "Sườn cốt lết 500 gr"),
        ("8be83165-193a-4553-8f17-fc5bec791754", "Sườn cốt lết 4 miếng"),
        ("a01ec750-533b-476a-9bbb-f767f23e1cc5", "2 miếng sườn cốt lết"),
        ("a597e032-a0e5-4f76-ae55-5592b2bfa9fa", "Sườn cốt lết (rib cutlet)"),
        ("a95f94da-cc1b-4a2f-882a-047c703ca266", "Sườn cốt lết 500g"),
        ("b2e7d7e3-0a5d-460f-af32-b3078e88687c", "4 miếng sườn cốt lết"),
        ("bde5e5c2-f6f3-424e-a4b3-5d1fe5cb8e65", "Sườn cốt lết 300 gr"),
        ("c211f506-8347-464f-9815-7077d92cde0f", "3 miếng sườn cốt lết"),
        ("c3f2bd9a-b4da-4def-9be2-db1111c7f4d6", "500 g sườn cốt lết (tầm 5 miếng sườn)"),
        ("c8a1b75f-a55f-43be-8b79-e5acc24077c2", "Sườn cốt lết: 500g"),
        ("e11063c2-2f4f-4655-aad4-dc30a8ee8a74", "1 miếng sườn cốt lết"),
        ("ed46d4bd-ddd2-4a43-ab27-4bc95b81cdc3", "2 lbs sườn cốt lết (rib cutlet)"),
        ("ed7a60e4-1231-43fc-ad71-6fb483249ccf", "Sườn cốt lết 4 miếng"),
        ("ee7f48f4-1e87-431f-95f3-e2492c2008bc", "Sườn cốt lết 1/2 kg"),
    ),
    "thịt cốt lết": (
        ("1bfbd300-dff6-4fee-9d0f-a1f561d60d13", "500 g thịt cốt lết"),
        ("3e1d6c8f-2475-4b4e-b444-d155bc9c2d7d", "2 miếng thịt cốt lết"),
        ("5ccca8ea-8898-4892-8391-c238ba9e5d56", "1 kg thịt cốt lết"),
        ("609ca26e-6a12-4c9a-9165-7adf0571caab", "700 g thịt cốt lết"),
        ("77ebed1c-5a1b-4a9f-803a-380155826f94", "2 miếng thịt cốt lết"),
        ("7bca160e-caa0-477f-9f0d-57d65af49b3b", "Thịt cốt lết"),
        ("cbe41198-769d-4c3b-a4c9-9fd64a5413c1", "3 miếng thịt cốt lết"),
        ("ce9a0967-77d9-4d74-9e6f-df477dc2b3c6", "500 gr thịt cốt lết (được tầm 5-6 lát)"),
        ("de143173-3748-4f19-9b6c-c70bddd43c8f", "1 hộp thịt cốt lết"),
        ("f489779c-b955-4ff3-8b84-f6b7c92ca01c", "4 miếng thịt cốt lết"),
        ("fadd1da3-d780-40db-b5c7-34aeddf5f090", "1 kg thịt cốt lết"),
    ),
    "cốt lết": (
        ("1a327d06-cce5-4bd6-b5c3-a37e5577c646", "Cốt lết"),
        ("b4ec2e0e-0efc-45d3-b15b-d47abdacf84d", "300 gram cốt lết"),
        ("c632242c-6487-42fd-b704-cb93746a83fc", "Cốt lết"),
        ("cc58687b-ff35-4270-bba4-f3ee4d12b8fb", "4 miếng cốt lết"),
        ("fe922dbe-d84f-4370-a274-7cae779d9c98", "3 miếng cốt lết"),
    ),
    "sườn cốt lết xắt lát": (
        ("18485b70-cd68-44e7-91df-d1f9b8fe5902", "750 gam sườn cốt lết xắt lát (khoảng 6 lát)"),
    ),
    "bóng bì": (
        ("4e57445f-d843-49ec-842c-903f4cbcb164", "Bóng bì: 10g"),
        ("876b2f44-b5b5-420b-adb6-3e40783c8da8", "Bóng bì 50 gr"),
        ("978ac64d-c8b2-4f37-93d1-e4d444714ddd", "Bóng bì (loại mỏng dai): 2 miếng"),
        ("b86566d6-7a31-45ac-8f1c-fc07d51c50d0", "Bóng bì: 50g"),
    ),
    "thịt bò chay lát": (
        ("eb46216a-f920-42f9-95f1-27c87a119463", "Thịt bò chay lát 100g"),
    ),
}

REPAIR_IDS_BY_ALIAS = {k: frozenset(i for i, _ in v) for k, v in REPAIR_ROWS.items()}
REPAIR_RAW_BY_ID = {i: raw for rows in REPAIR_ROWS.values() for i, raw in rows}
ALIAS_BY_REPAIR_ID = {i: key for key, rows in REPAIR_ROWS.items() for i, _ in rows}
REPAIR_IDS = frozenset(REPAIR_RAW_BY_ID)

assert set(REPAIR_ROWS) == set(ALIAS_REPOINTS)
assert len(REPAIR_IDS) == 46 == sum(len(v) for v in REPAIR_ROWS.values())
# The reviewed per-target split, asserted so a mis-edit of the table above
# cannot quietly change what this fix claims to do.
assert sum(len(REPAIR_ROWS[k]) for k, (_, new) in ALIAS_REPOINTS.items() if new == "7053") == 41
assert len(REPAIR_ROWS["bóng bì"]) == 4
assert len(REPAIR_ROWS["thịt bò chay lát"]) == 1
# No repaired row may carry a cure trigger.
assert not any(
    p.search(raw.lower()) for raw in REPAIR_RAW_BY_ID.values() for p in CURE_RAW_PATTERNS
)

EXPECTED_RECIPE_COUNT = 43

REPORT_ROW_FIELDS = (
    "master_ingredient_code", "master_ingredient_name", "match_method",
    "match_confidence", "calories", "protein_g", "fat_g", "carbs_g",
)
NUTRITION_FIELDS = ("calories", "protein_g", "fat_g", "carbs_g")


class DriftError(ValueError):
    """A reviewed target (alias or row) no longer matches its expected pre/post state."""


def read_alias_map():
    return json.loads(ALIAS_PATH.read_text(encoding="utf-8"))


def write_alias_map(alias_map):
    ALIAS_PATH.write_text(
        json.dumps(alias_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _alias_repoint_state(alias_map, key):
    """pending (still on the reviewed old code) / already_applied (on the new
    one). Any third value means the reviewed evidence has drifted."""
    old, new = ALIAS_REPOINTS[key]
    if key not in alias_map:
        raise DriftError(f"alias {key!r} is absent -- this fix repoints, it does not add")
    value = alias_map[key]
    if value == old:
        return "pending"
    if value == new:
        return "already_applied"
    raise DriftError(
        f"alias {key!r} has unexpected value {value!r} (expected {old!r} or {new!r})"
    )


def _assert_siblings_intact(alias_map):
    """The sibling families on every code this fix touches are the evidence it
    rests on. If one has drifted, the reviewed conclusion no longer holds."""
    for code, keys in ALIAS_MUST_REMAIN.items():
        for key in keys:
            if alias_map.get(key) != code:
                raise DriftError(
                    f"sibling alias {key!r} is {alias_map.get(key)!r}, expected {code!r}"
                )


def apply_alias_changes(alias_map, states):
    """Build the new alias map, touching only the six reviewed keys."""
    new_map = dict(alias_map)
    for key, (_, new) in ALIAS_REPOINTS.items():
        new_map[key] = new

    # Belt-and-suspenders: every key outside the six must be byte-identical
    # between old and new maps, and the map may not grow or shrink.
    for key, value in alias_map.items():
        if key in ALIAS_REPOINTS:
            continue
        if new_map.get(key) != value:
            raise DriftError(f"unrelated alias {key!r} would be changed -- refusing to write")
    if set(new_map) != set(alias_map):
        raise DriftError("alias key set changed -- this fix may only repoint existing keys")

    for key, (_, new) in ALIAS_REPOINTS.items():
        if new_map[key] != new:
            raise DriftError(f"alias {key!r} did not reach {new!r} -- refusing to write")
    _assert_siblings_intact(new_map)
    # States are informational for the report; a fully-applied map is a no-op.
    if all(state == "already_applied" for state in states.values()) and new_map != alias_map:
        raise DriftError("alias map would change even though every repoint is already applied")
    return new_map


def _match_state_probe(row, code):
    name = (row.get("master_ingredient_name") or "").strip()
    return (
        (row.get("master_ingredient_code") or "").strip() == code
        and name == CODE_NAMES[code]
        and row.get("match_method") == PRESET_ALIAS_METHOD
        and (row.get("match_confidence") or "").strip() == PRESET_ALIAS_CONFIDENCE
    )


def _row_state(row, raw_text, alias_key):
    rid = row.get("id")
    if row.get("raw_text") != raw_text:
        raise DriftError(
            f"row {rid}: raw_text drifted (expected {raw_text!r}, found {row.get('raw_text')!r})"
        )
    old, new = ALIAS_REPOINTS[alias_key]
    if _match_state_probe(row, old):
        return "pending"
    if _match_state_probe(row, new):
        return "already_applied"
    raise DriftError(
        f"row {rid}: neither pending ({old}/{CODE_NAMES[old]!r}) nor already-repaired "
        f"({new}/{CODE_NAMES[new]!r}) state matched (found "
        f"code={row.get('master_ingredient_code')!r} name={row.get('master_ingredient_name')!r} "
        f"method={row.get('match_method')!r} confidence={row.get('match_confidence')!r})"
    )


def rows_reachable_by_alias(ing_rows, matcher):
    """Recompute, from live data, which rows each repointed alias can actually
    reach -- through the real Stage-1 catalog index and both Stage-2 lookup
    routes (normalized query, then prep-stripped cleaned query), in the same
    precedence VietnameseIngredientMatcher.match() uses.

    Repointing does not add or remove keys, so this mapping is identical before
    and after the fix; it is computed once and used to prove the pinned id sets
    are neither stale nor short.
    """
    norm_to_key = {normalize_vietnamese_text(key): key for key in ALIAS_REPOINTS}
    if len(norm_to_key) != len(ALIAS_REPOINTS):
        raise DriftError("two reviewed alias keys normalize to the same string")
    reachable = {key: set() for key in ALIAS_REPOINTS}
    for row in ing_rows:
        cleaned = (row.get("cleaned_name") or "").strip()
        if not cleaned:
            continue
        query_norm = normalize_vietnamese_text(cleaned)
        cleaned_q = clean_culinary_query(cleaned)
        # Stage 1 wins outright; the alias dict is never consulted for these.
        if query_norm in matcher.normalized_to_index or cleaned_q in matcher.normalized_to_index:
            continue
        if query_norm in matcher.alias_dict:
            hit = query_norm
        elif cleaned_q in matcher.alias_dict:
            hit = cleaned_q
        else:
            continue
        key = norm_to_key.get(hit)
        if key is not None:
            reachable[key].add(row["id"])
    return reachable


def build_plan():
    """Read-only: locate the alias edits and the 46 in-scope rows, classify each."""
    alias_map = read_alias_map()
    _assert_siblings_intact(alias_map)
    alias_states = {key: _alias_repoint_state(alias_map, key) for key in ALIAS_REPOINTS}

    masters = {r["code"]: r for r in read_csv(MASTER)}
    for code, name in CODE_NAMES.items():
        if code not in masters:
            raise DriftError(f"code {code!r} is absent from the current catalog")
        if masters[code].get("name_vi", "").strip() != name:
            raise DriftError(
                f"code {code!r} now names {masters[code].get('name_vi')!r}, not {name!r} -- "
                "the reviewed identity evidence for this fix has drifted"
            )
    # The reviewed null-carbs set must still describe the live catalog: a code
    # that gained or lost a carbs value would change which rows report carbs as
    # unknown, and that transition is part of the reviewed policy.
    for code in CODE_NAMES:
        declares_carbs = nutrition_value(masters[code].get("carbs_g")) is not None
        if declares_carbs == (code in NULL_CARBS_CODES):
            raise DriftError(
                f"code {code!r} carbs_g availability drifted "
                f"(declares_carbs={declares_carbs}, reviewed null-carbs={code in NULL_CARBS_CODES})"
            )

    ing_rows = read_csv(ING)
    by_id = {r["id"]: r for r in ing_rows}

    row_states = {}
    for rid, raw_text in REPAIR_RAW_BY_ID.items():
        row = by_id.get(rid)
        if row is None:
            raise DriftError(f"repair row {rid} not found in {ING}")
        row_states[rid] = _row_state(row, raw_text, ALIAS_BY_REPAIR_ID[rid])

    # No repaired row's raw_text may trigger a systemic-mismatch cure: if one
    # did, a later pipeline run would silently overwrite the identity written
    # here. Checked against live raw_text, not only against the pinned literal.
    for rid in REPAIR_IDS:
        raw_l = (by_id[rid].get("raw_text") or "").lower()
        for pattern in CURE_RAW_PATTERNS:
            if pattern.search(raw_l):
                raise DriftError(
                    f"repair row {rid} raw_text {by_id[rid].get('raw_text')!r} matches cure "
                    f"pattern {pattern.pattern!r} -- its identity is the cure's to set, "
                    "not this alias fix's"
                )

    # The pinned sets must equal the sets the aliases can actually reach. A row
    # appearing or disappearing means the blast radius is no longer the
    # reviewed one, so nothing may be written.
    matcher = VietnameseIngredientMatcher(catalog_csv_path=MASTER)
    reachable = rows_reachable_by_alias(ing_rows, matcher)
    for key in ALIAS_REPOINTS:
        expected = REPAIR_IDS_BY_ALIAS[key]
        if reachable[key] != set(expected):
            raise DriftError(
                f"blast radius drifted for alias {key!r}: reachable "
                f"{sorted(reachable[key] - set(expected))[:5]} extra / "
                f"{sorted(set(expected) - reachable[key])[:5]} missing"
            )

    affected_recipe_ids = {by_id[rid]["recipe_id"] for rid in REPAIR_IDS}
    if len(affected_recipe_ids) != EXPECTED_RECIPE_COUNT:
        raise DriftError(
            f"reviewed recipe count drifted: {len(affected_recipe_ids)} affected recipes, "
            f"expected {EXPECTED_RECIPE_COUNT}"
        )

    # Rows sitting on an old code by some route other than the reviewed aliases
    # are legitimate (or stale, which is a separate task) and must not move.
    legit_by_old_code = {}
    for old in sorted({old for old, _ in ALIAS_REPOINTS.values()}):
        legit_by_old_code[old] = {
            r["id"] for r in ing_rows
            if (r.get("master_ingredient_code") or "").strip() == old
            and r["id"] not in REPAIR_IDS
        }
    return alias_map, alias_states, masters, row_states, legit_by_old_code


def _apply_repair(row, masters):
    _, new = ALIAS_REPOINTS[ALIAS_BY_REPAIR_ID[row["id"]]]
    match_fields = {
        "master_ingredient_code": new,
        "master_ingredient_name": CODE_NAMES[new],
        "match_method": PRESET_ALIAS_METHOD,
        "match_confidence": PRESET_ALIAS_CONFIDENCE,
    }
    weight = nutrition_value(row.get("estimated_weight_g")) or 0.0
    updates = stage_qwen_update(row, masters, weight, match_fields=match_fields)
    new_row = dict(row)
    new_row.update(updates)
    return new_row


def _nutrition_totals(rows):
    """Sum the four nutrition fields, treating null (unknown) as absent, not zero."""
    totals = {field: 0.0 for field in NUTRITION_FIELDS}
    for row in rows:
        for field in totals:
            value = nutrition_value(row.get(field))
            if value is not None:
                totals[field] += value
    return {k: round(v, 1) for k, v in totals.items()}


def _delta(before, after):
    return {k: round(after[k] - before[k], 1) for k in before}


def _null_transitions(before_by_id, after_by_id, ids):
    """Count, per nutrition field, rows whose value moved between known and
    unknown. Recorded explicitly because a measured -> null move is a real
    semantic change that must never be papered over with a 0.0."""
    out = {}
    for field in NUTRITION_FIELDS:
        known_to_null, null_to_known = [], []
        for rid in sorted(ids):
            b = nutrition_value(before_by_id[rid].get(field))
            a = nutrition_value(after_by_id[rid].get(field))
            if b is not None and a is None:
                known_to_null.append(rid)
            elif b is None and a is not None:
                null_to_known.append(rid)
        out[field] = {
            "known_to_null": len(known_to_null),
            "null_to_known": len(null_to_known),
            "known_to_null_ids": known_to_null,
            "null_to_known_ids": null_to_known,
        }
    return out


def run(apply=False):
    alias_map, alias_states, masters, row_states, legit_by_old_code = build_plan()
    repair_now = {rid for rid in REPAIR_IDS if row_states[rid] == "pending"}

    ing_csv_rows = read_csv(ING)
    ing_json_rows = read_json(ING_JSON)

    def transform(row):
        rid = row["id"]
        if rid in REPAIR_IDS and row_states.get(rid) == "pending":
            return _apply_repair(row, masters)
        return row

    new_ing_csv_rows = [transform(r) for r in ing_csv_rows]
    ing_csv_fields = list(ing_csv_rows[0].keys())
    new_ing_json_rows = [transform(r) for r in ing_json_rows]

    rollups = recompute_recipe_rollups(new_ing_csv_rows)
    recipes_csv_rows = read_csv(RECIPES_CSV)
    recipes_csv_fields = list(recipes_csv_rows[0].keys())
    changed_totals = _apply_rollups(recipes_csv_rows, rollups)

    recipes_json_rows = read_json(RECIPES_JSON)
    _apply_rollups(recipes_json_rows, rollups)
    status_report = _recompute_status(recipes_json_rows, new_ing_json_rows)

    new_alias_map = apply_alias_changes(alias_map, alias_states)

    before_by_id = {r["id"]: r for r in ing_csv_rows if r["id"] in REPAIR_IDS}
    after_by_id = {r["id"]: r for r in new_ing_csv_rows if r["id"] in REPAIR_IDS}

    # Post-transform guards.
    for rid in REPAIR_IDS:
        _, new = ALIAS_REPOINTS[ALIAS_BY_REPAIR_ID[rid]]
        if not _match_state_probe(after_by_id[rid], new):
            raise DriftError(f"row {rid} did not reach the {new} fixed state -- refusing to write")
        # Weight is evidence, not this fix's to set: the repair scales nutrition
        # from the row's own existing weight and must leave it untouched.
        if after_by_id[rid].get("estimated_weight_g") != before_by_id[rid].get("estimated_weight_g"):
            raise DriftError(f"row {rid}: estimated_weight_g changed -- refusing to write")
        if after_by_id[rid].get("raw_text") != before_by_id[rid].get("raw_text"):
            raise DriftError(f"row {rid}: raw_text changed -- refusing to write")
        if after_by_id[rid].get("cleaned_name") != before_by_id[rid].get("cleaned_name"):
            raise DriftError(f"row {rid}: cleaned_name changed -- refusing to write")
        # A code that declares no carbs must produce a NULL carbs_g, never 0.0.
        if new in NULL_CARBS_CODES and nutrition_value(after_by_id[rid].get("carbs_g")) is not None:
            raise DriftError(
                f"row {rid}: carbs_g is {after_by_id[rid].get('carbs_g')!r} but {new} declares "
                "no carbs -- missing nutrition must stay null, not become a number"
            )
    # Legitimate rows on every vacated code must come through byte-identical.
    after_all = {r["id"]: r for r in new_ing_csv_rows}
    before_all = {r["id"]: r for r in ing_csv_rows}
    for old, ids in legit_by_old_code.items():
        for rid in ids:
            if after_all[rid] != before_all[rid]:
                raise DriftError(f"legitimate {old} row {rid} was modified -- refusing to write")
    # No unrelated row may change at all.
    changed_ids = {r["id"] for r, o in zip(new_ing_csv_rows, ing_csv_rows) if r != o}
    if not changed_ids <= REPAIR_IDS:
        raise DriftError(f"unrelated rows would change: {sorted(changed_ids - REPAIR_IDS)[:10]}")

    affected_recipe_ids = {r["recipe_id"] for r in ing_csv_rows if r["id"] in REPAIR_IDS}
    nutrition_before = _nutrition_totals(before_by_id[r] for r in REPAIR_IDS)
    nutrition_after = _nutrition_totals(after_by_id[r] for r in REPAIR_IDS)

    by_alias = {}
    for key in ALIAS_REPOINTS:
        old, new = ALIAS_REPOINTS[key]
        repair_ids = REPAIR_IDS_BY_ALIAS[key]
        before = _nutrition_totals(before_by_id[r] for r in repair_ids)
        after = _nutrition_totals(after_by_id[r] for r in repair_ids)
        by_alias[key] = {
            "from": {"code": old, "name": CODE_NAMES[old]},
            "to": {"code": new, "name": CODE_NAMES[new]},
            "alias_state": alias_states[key],
            "redundant_key": key in REDUNDANT_ALIASES,
            "rows_repaired": len(repair_ids),
            "recipes_affected": len({before_by_id[r]["recipe_id"] for r in repair_ids}),
            "nutrition": {"before": before, "after": after, "delta": _delta(before, after)},
        }

    by_target = {}
    for new in sorted({n for _, n in ALIAS_REPOINTS.values()}):
        ids = {rid for rid in REPAIR_IDS if ALIAS_REPOINTS[ALIAS_BY_REPAIR_ID[rid]][1] == new}
        before = _nutrition_totals(before_by_id[r] for r in ids)
        after = _nutrition_totals(after_by_id[r] for r in ids)
        by_target[new] = {
            "name": CODE_NAMES[new],
            "aliases": sorted(k for k, v in ALIAS_REPOINTS.items() if v[1] == new),
            "rows": len(ids),
            "recipes": len({before_by_id[r]["recipe_id"] for r in ids}),
            "declares_carbs": new not in NULL_CARBS_CODES,
            "nutrition": {"before": before, "after": after, "delta": _delta(before, after)},
        }

    report = {
        "status": "applied" if apply else "preview",
        "alias_decision": "SAFE_REPOINT",
        "alias_repoint_count": len(ALIAS_REPOINTS),
        "alias_states": alias_states,
        "alias_repoints": {k: {"from": v[0], "to": v[1]} for k, v in ALIAS_REPOINTS.items()},
        "redundant_aliases": list(REDUNDANT_ALIASES),
        "aliases_removed": 0,
        "aliases_added": 0,
        "alias_map_size": len(new_alias_map),
        "match_method_semantics": {
            "repaired_rows": f"{PRESET_ALIAS_METHOD} / {PRESET_ALIAS_CONFIDENCE} (unchanged)",
            "row_level_overrides": 0,
            "cure_held_rows": 0,
        },
        "rows_in_scope": len(REPAIR_IDS),
        "rows_repaired_total": len(REPAIR_IDS),
        "rows_repaired_now": len(repair_now),
        "rows_already_applied": len(REPAIR_IDS) - len(repair_now),
        "legitimate_old_code_rows_untouched": {
            code: len(ids) for code, ids in sorted(legit_by_old_code.items())
        },
        "affected_recipe_count": len(affected_recipe_ids),
        "affected_recipe_ids": sorted(affected_recipe_ids),
        "recipes_with_changed_totals": changed_totals,
        "recipes_with_changed_missing_count": status_report["recipes_with_changed_missing_count"],
        "recipes_with_status_label_changed": status_report["recipes_with_status_label_changed"],
        "status_transitions": status_report["status_transitions"],
        "nutrition_all_repaired_rows": {
            "before": nutrition_before,
            "after": nutrition_after,
            "delta": _delta(nutrition_before, nutrition_after),
        },
        "null_nutrition_transitions": _null_transitions(before_by_id, after_by_id, REPAIR_IDS),
        "by_target_code": by_target,
        "by_alias": by_alias,
        "repair_row_ids": sorted(REPAIR_IDS),
        "row_outcomes": {
            rid: {
                "alias": ALIAS_BY_REPAIR_ID[rid],
                "raw_text": before_by_id[rid].get("raw_text"),
                "cleaned_name": before_by_id[rid].get("cleaned_name"),
                "recipe_id": before_by_id[rid].get("recipe_id"),
                "estimated_weight_g": after_by_id[rid].get("estimated_weight_g"),
                "decision": "REPOINT_ALIAS_AND_REPAIR_ROW",
                "before": {f: before_by_id[rid].get(f) for f in REPORT_ROW_FIELDS},
                "after": {f: after_by_id[rid].get(f) for f in REPORT_ROW_FIELDS},
            }
            for rid in sorted(REPAIR_IDS)
        },
        "approximation_caveats": {
            "7053": (
                "APPROVED APPROXIMATION, not an exact identity. The catalog carries no pork "
                "chop/cutlet entry; 7053 'Sườn heo (xương heo)' (Pork, ribs, raw) is the only "
                "bone-in pork rib identity available, and is the identity a prior review already "
                "chose for this exact context (row 19504d22, reports/eda/suon_rib_alias_fix)."
            ),
            "7031": (
                "APPROVED APPROXIMATION with a reviewed hydration/density caveat, explicitly NOT "
                "a blocker. 'bóng bì' is DRIED/puffed pork skin (~10% water); 7031 'Bì lợn' is RAW "
                "pork skin (water 73.3 g/100 g), so 7031 understates energy density per dry gram "
                "by roughly 3x. Accepted because the alternative on the table (7064 'Chả lợn') is "
                "wrong on part AND preparation AND magnitude; because canh bóng rehydrates the "
                "skin before use and the recorded weights are already hydrated-scale; and because "
                "no dried/puffed pork-skin identity exists in the catalog. Creating one is catalog "
                "repair, out of scope under AGENTS.md §18."
            ),
            "20039": (
                "Sibling-consistency repair, no new policy: 20039 already declares 'thịt bò chay' "
                "and 'bò lát chay' as aliases, and 'thịt bò chay lát' is the same product with the "
                "last two words transposed."
            ),
        },
        "out_of_scope_note": (
            "This follow-up repoints exactly six aliases. Deliberately unchanged: the remaining "
            "vegan analogues 'đùi gà chay' -> 7088, 'xúc xích chay' -> 7077 and 'nem chua chay' -> "
            "7073 (they need a wet-vs-dry analogue FORM policy this review did not settle); "
            "'thịt cua chay' -> 8069; the vegan seasoning analogues ('nước mắm chay' -> 13017, "
            "'dầu hào chay' -> 13027); catalog repair; any matcher-level 'chay' guard; cốt-lết "
            "coverage expansion beyond these six aliases (13 further pork cốt-lết rows stay "
            "UNMATCHED, three of which are BONELESS 'cốt lết bỏ xương' and do not belong on 7053, "
            "plus 1 vegan 'sườn cốt lết chay' row); and every other 70xx finding."
        ),
        "canonical_note": (
            "Canonical outputs (canonical_recipes.csv/json, canonical_recipe_ingredients.csv/json, "
            "recipe_canonical_mapping.csv/json, recipe_canonicalization_summary.json) are NOT "
            "regenerated by this script and are stale for these rows/recipes until "
            "scripts/canonicalize_recipes.py and scripts/export_canonical_json.py are re-run."
        ),
    }

    if apply:
        write_alias_map(new_alias_map)
        write_csv(ING, new_ing_csv_rows, ing_csv_fields)
        write_json(ING_JSON, new_ing_json_rows)
        write_csv(RECIPES_CSV, recipes_csv_rows, recipes_csv_fields)
        write_json(RECIPES_JSON, recipes_json_rows)
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "applied_fix.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    report = run(apply=args.apply)
    skip = ("repair_row_ids", "row_outcomes", "affected_recipe_ids",
            "approximation_caveats", "out_of_scope_note", "canonical_note")
    print(json.dumps(
        {k: v for k, v in report.items() if k not in skip},
        ensure_ascii=False, indent=2,
    ))


if __name__ == "__main__":
    main()
