"""Apply the reviewed Batch-A PRESET_ALIAS repoints from the 70xx meat-band
audit (high-confidence exact-target subset only). Default previews; --apply writes.

The audit found fifteen preset aliases in
data/processed/viendinhduong/ingredient_alias_map.json that resolve to a
catalog identity of the wrong species, the wrong animal part, or (twice) the
wrong kingdom entirely. Each one has a single unambiguous correct identity
already present in the live catalog, so every decision here is SAFE_REPOINT --
no alias is removed, no alias is split, and no row-level override is created.

    alias                     from                      to
    ------------------------------------------------------------------------
    thịt thịt nạc thăn        7070 Giò thủ lợn          7085 Thịt nạc thăn heo (lợn)
    chả lụa                   7068 Giò bò               7069 Giò lụa
    chả lụa cắt hạt lựu       7068 Giò bò               7069 Giò lụa
    da heo                    7064 Chả lợn              7031 Bì lợn
    da heo tươi               7064 Chả lợn              7031 Bì lợn
    phile bò                  7001 Thịt bê mỡ           7005 Thịt thăn bò
    bò phile                  7001 Thịt bê mỡ           7005 Thịt thăn bò
    bò thăn                   7001 Thịt bê mỡ           7005 Thịt thăn bò
    gân bò                    7001 Thịt bê mỡ           7043 Gân chân bò
    bò hoa                    7001 Thịt bê mỡ           7094 Thịt bắp bò
    chim bồ câu               7012 Thịt gà rừng         7007 Thịt bồ câu, cả con non (ra ràng)
    vịt                       7042 Gan vịt              7028 Thịt vịt
    phô mai đầu bò            7035 Đầu bò               10009 Phô mai (phó mát)
    đùi gà tây                7088 Đùi gà               7014 Thịt gà tây
    nấm hủ đùi gà             7088 Đùi gà               20007 Nấm đùi gà

Why each is an exact target rather than a "closest catalog entry"
(AGENTS.md §5 -- none of these rests on code proximity or lexical similarity):

  * "thịt thịt nạc thăn" is a doubled-"thịt" spelling of the pork tenderloin
    term the sibling alias "thịt nạc thăn" already maps to 7085. 7070 is
    "Giò thủ lợn" (pressed pork head cheese) -- a different product entirely.
  * "chả lụa" is the southern name for "giò lụa" -- the SAME steamed pork
    sausage 7069 already names. 7068 is "Giò bò", the beef version: right
    product family, wrong species.
  * "da heo" is pork SKIN (7031 "Bì lợn"). 7064 is "Chả lợn", fried pork
    paste: same animal, different part and different preparation.
  * "phile bò"/"bò phile"/"bò thăn" are beef loin/fillet (7005 "Thịt thăn
    bò"). 7001 is "Thịt bê mỡ" -- VEAL, fatty: different animal maturity and
    a fat-bearing cut, so the nutrition is materially different too.
  * "gân bò" is beef TENDON; 7043 "Gân chân bò" is the only tendon identity in
    the catalog. 7001 is muscle meat.
  * "bò hoa" is the "bắp bò hoa" flower-shank cut -- 7094 "Thịt bắp bò".
  * "chim bồ câu" is pigeon; 7007 is the catalog's only pigeon entry. 7012 is
    "Thịt gà rừng" (wild chicken): different species.
  * "vịt" is duck MEAT (7028 "Thịt vịt"). 7042 is "Gan vịt" -- duck LIVER, an
    organ whose nutrition profile is nothing like the carcass meat's.
  * "phô mai đầu bò" is a colloquial Vietnamese name for a processed cheese
    wedge. The alias had been resolved on its "đầu bò" substring to 7035
    "Đầu bò" -- literal beef head. The identity is cheese: 10009.
  * "đùi gà tây" is TURKEY leg. 7088 "Đùi gà" is chicken thigh; the catalog
    carries no turkey-leg cut, and 7014 "Thịt gà tây" (turkey, average meat)
    is the correct species identity. Species correctness outranks cut
    granularity here -- the only alternative on offer is a chicken identity,
    which is simply a different bird.
  * "nấm hủ đùi gà" is king oyster MUSHROOM ("nấm đùi gà", 20007) with a
    "hủ"/jar typo. 7088 put a vegetable on poultry meat -- a kingdom error.

ALIAS DECISION: SAFE_REPOINT for all fifteen (AGENTS.md §6).

Repoint, not removal: every one of these keys is a real Vietnamese ingredient
term that users write, and every one needs an identity. Removing them would
drop the rows into SUBPHRASE/neural matching, which is exactly how at least
one of them landed on a wrong 70xx code in the first place ("phô mai đầu bò"
-> the "đầu bò" head-meat entry). Repointing keeps PRESET_ALIAS_MATCH / 0.98
-- the same method and confidence the rows already carry -- so match-method
semantics are unchanged by this fix; only the identity behind them moves.

BLAST RADIUS (measured against the live 63,943-row processed dataset, not
inferred from the audit): 126 ingredient rows resolve through these fifteen
alias keys. 111 of them are repaired here. The other 15 are CURE-HELD and are
deliberately left byte-identical:

  * 12 "bò hoa" rows and 3 "bò phile" rows whose raw_text contains "bắp bò"
    were already standardised onto 7094 "Thịt bắp bò" by the systemic-mismatch
    cure in scripts/run_qwen_line_pipeline.py (STANDARDIZED_CURE / 0.98). That
    cure runs AFTER matching and overrides the alias result, so those rows
    would stay on 7094 through a full re-run no matter what the alias says.

"bò hoa" is therefore a LATENT repoint: all 12 of its reachable rows are
cure-held, so it changes zero rows today. It is still applied, because it
removes a wrong identity (veal) that would be published the moment a "bò hoa"
row appears without the "bắp bò" spelling, and because 7094 is precisely what
the reviewed cure already concluded for this text.

MATCH METHOD / CONFIDENCE SEMANTICS. All 111 repaired rows keep
PRESET_ALIAS_MATCH / 0.98: they were alias-resolved before and are
alias-resolved after, just to the right code. The 15 cure-held rows keep
STANDARDIZED_CURE / 0.98. No row's method or confidence changes in this fix,
and no 0.0 confidence is written anywhere (AGENTS.md §4).

LEGITIMATE ROWS ON THE OLD CODES ARE NEVER TOUCHED. The eight vacated codes
keep every alias and every row that reaches them by a correct route -- the
"giò thủ" aliases on 7070, "chả lợn"/"chả" on 7064,
"thịt bê"/"nạm bò"/"ba chỉ bò" on 7001, "gà tre" on 7012, "gan vịt" on 7042,
"đầu bò" on 7035, and the nineteen chicken-thigh aliases on 7088. Those
aliases are pinned before and after the write, and every processed row on an
old code that is not in the reviewed repair set is asserted byte-identical.

SUPERSEDED DEFERRALS. This batch originally also deferred the cốt lết family
and "bóng bì", and pinned them on 7070/7064 as evidence it had not dragged
them along. That deferral has since been reviewed and resolved: the follow-up
in scripts/eda/apply_meat_band_batch_a_followup_safe_fix.py repointed
"sườn cốt lết"/"thịt cốt lết"/"cốt lết"/"sườn cốt lết xắt lát" -> 7053
"Sườn heo (xương heo)", "bóng bì" -> 7031 "Bì lợn" and "thịt bò chay lát" ->
20039 "Thịt chay (sườn non chay)". Those keys are therefore no longer pinned
here on their old codes -- pinning them would now assert a superseded policy
and make this script abort against correct data. What IS still pinned on the
vacated codes is what genuinely stayed: "giò thủ"* on 7070 and "chả lợn"/"chả"
on 7064.

EXPLICITLY OUT OF SCOPE (recorded by the audit, deliberately unchanged):
the remaining vegan analogues "đùi gà chay" -> 7088, "xúc xích chay" -> 7077,
"nem chua chay" -> 7073 and "thịt cua chay" -> 8069, which still need a
wet-vs-dry analogue form policy; the vegan seasoning analogues;
"thịt ba chỉ rút sườn" (already fixed in Batch B);
"sườn bò"/"dẻ sườn bò" -> 7094; "mỡ gà"; "thịt heo quay"; "nạm bò";
"ba chỉ bò"; "chả chiên"; "mỡ nước"; "tóp mỡ"; "gà tre"; catalog name_vi
corruption; "xương bò"; the 7096 corruption; cleaner/matcher policy; and
stale-code remediation.

Safety model (fail closed, idempotent, dry-run by default):
  - Every alias edit is pinned in BOTH directions: the key must currently hold
    its reviewed old code, or already hold the reviewed new code (post-fix).
    Any third value aborts before anything is written. Every alias key outside
    the fifteen is verified byte-identical, and the map size may not change.
  - Sibling aliases on all eight vacated codes and on the ten target codes are
    asserted intact before and after, so this fix cannot quietly widen.
  - Every target row is pinned by id AND exact raw_text AND its exact pre-fix
    match fields. Each must be either "pending" or "already_applied"; anything
    else aborts the ENTIRE run before any write.
  - The pinned id sets are cross-checked against the rows the aliases can
    actually reach, recomputed from live data through the real
    normalize_vietnamese_text/clean_culinary_query functions and the real
    Stage-1 catalog index. Drift in either direction aborts.
  - Every target code must exist in the live catalog under its exact current
    name, checked through the same identity guard
    nlp.matching_integrity.stage_qwen_update enforces for the Qwen pipeline.
    Nutrition is computed by that function from the catalog plus each row's
    own current weight -- never typed by hand. Codes that declare no carbs
    (7031, 7043, 7007, 7028, 10009) produce a null carbs_g, not a zero, per
    the nullable-nutrition contract in nlp.nutrition.
  - No repaired row's raw_text may match the "bắp bò" cure pattern, so a
    repaired identity cannot be silently overridden by a later pipeline run.
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
OUT = ROOT / "reports/eda/meat_band_batch_a_alias_fix"

PRESET_ALIAS_METHOD = "PRESET_ALIAS_MATCH"
PRESET_ALIAS_CONFIDENCE = "0.98"
CURE_METHOD = "STANDARDIZED_CURE"
CURE_CONFIDENCE = "0.98"

# --- Catalog identities ----------------------------------------------------

# Every code this fix reads or writes, with its exact current live name_vi.
# Verified before anything is written: a code that has been silently repointed
# to a different ingredient must not be published under a stale name
# (AGENTS.md §3 -- the live catalog is authoritative for identity).
CODE_NAMES = {
    "7001": "Thịt bê mỡ",
    "7005": "Thịt thăn bò",
    "7007": "Thịt bồ câu, cả con non (ra ràng)",
    "7012": "Thịt gà rừng",
    "7014": "Thịt gà tây",
    "7028": "Thịt vịt",
    "7031": "Bì lợn",
    "7035": "Đầu bò",
    "7042": "Gan vịt",
    "7043": "Gân chân bò",
    "7064": "Chả lợn",
    "7068": "Giò bò",
    "7069": "Giò lụa",
    "7070": "Giò thủ lợn",
    "7085": "Thịt nạc thăn heo (lợn)",
    "7088": "Đùi gà",
    "7094": "Thịt bắp bò",
    "10009": "Phô mai (phó mát)",
    "20007": "Nấm đùi gà",
}

# --- Alias-map edits -------------------------------------------------------

# alias key -> (reviewed current code, reviewed correct code). Repoints only;
# no key is added and no key is removed.
ALIAS_REPOINTS = {
    "thịt thịt nạc thăn": ("7070", "7085"),
    "chả lụa": ("7068", "7069"),
    "chả lụa cắt hạt lựu": ("7068", "7069"),
    "da heo": ("7064", "7031"),
    "da heo tươi": ("7064", "7031"),
    "phile bò": ("7001", "7005"),
    "bò phile": ("7001", "7005"),
    "bò thăn": ("7001", "7005"),
    "gân bò": ("7001", "7043"),
    "bò hoa": ("7001", "7094"),
    "chim bồ câu": ("7012", "7007"),
    "vịt": ("7042", "7028"),
    "phô mai đầu bò": ("7035", "10009"),
    "đùi gà tây": ("7088", "7014"),
    "nấm hủ đùi gà": ("7088", "20007"),
}
assert len(ALIAS_REPOINTS) == 15
assert not {old for old, _ in ALIAS_REPOINTS.values()} - set(CODE_NAMES)
assert not {new for _, new in ALIAS_REPOINTS.values()} - set(CODE_NAMES)

# Sibling aliases that must survive this fix on their current code. These are
# the evidence that each vacated code is a legitimate identity with a
# legitimate alias family, and that only the fifteen listed keys are wrong.
# Several are explicitly out of scope for this batch ("nạm bò"/"ba chỉ bò" ->
# 7001, "chả chiên" -> 7068, "gà tre" -> 7012, "sườn bò"/"dẻ sườn bò" -> 7094,
# "đùi gà chay" -> 7088) and are pinned here precisely so this fix cannot drag
# them along.
#
# The cốt lết family and "bóng bì" were pinned here for the same reason and
# have since been REPOINTED by the reviewed follow-up
# (scripts/eda/apply_meat_band_batch_a_followup_safe_fix.py): cốt lết* -> 7053,
# "bóng bì" -> 7031. They are deliberately absent below -- a pin is a statement
# about current reviewed policy, and re-adding them would abort this script
# against correct data. Their new homes are pinned by the follow-up instead.
ALIAS_MUST_REMAIN = {
    "7001": ("thịt bê mỡ tươi", "thịt bê mỡ", "thịt bê", "nạm bò",
             "thịt nạm bò", "ba chỉ bò", "ba chỉ bò đông lạnh"),
    "7005": ("thịt thăn bò", "thăn bò", "thịt bò lưng nạc tươi", "thịt thăn"),
    "7007": ("thịt bồ câu cả con non ra ràng tươi",
             "thịt bồ câu cả con non ra ràng", "bồ câu"),
    "7012": ("thịt gà rừng tươi", "thịt gà rừng", "gà tre"),
    "7014": ("thịt gà tây tươi", "thịt gà tây"),
    "7028": ("thịt vịt tươi", "thịt vịt", "thịt vịt xiêm", "thịt vịt 1 5",
             "thịt vịt quay"),
    "7031": ("bì lợn tươi", "bì lợn", "bóng bì lợn"),
    "7035": ("đầu bò tươi", "đầu bò"),
    "7042": ("gan vịt tươi", "gan vịt"),
    "7043": ("gân chân bò tươi", "gân chân bò"),
    "7064": ("chả lợn", "chả"),
    "7068": ("giò bò chín", "giò bò", "khoanh giò bò", "chả chiên"),
    "7069": ("giò lụa chín", "giò lụa"),
    "7070": ("giò thủ lợn chín", "giò thủ lợn", "giò thủ"),
    "7085": ("thịt nạc thăn", "thịt thăn heo", "thịt thăn lợn", "thăn heo",
             "thịt lợn nạc thăn tươi", "thịt nạc thăn heo"),
    "7088": ("đùi gà", "má đùi gà", "thịt gà công nghiệp đùi tươi",
             "má đùi gà rút xương", "đùi gà góc tư", "thịt má đùi gà",
             "đùi gà rút xương", "đùi gà góc 4", "thịt đùi gà",
             "gà má đùi gà rút xương", "thịt má đùi gà rút xương",
             "thịt má đùi gà lóc xương", "phi lê đùi gà", "đùi gà chay",
             "đùi gà góc", "má đùi gà 400g", "đùi gà lóc xương",
             "đùi gà tỏi", "đùi tỏi gà"),
    "7094": ("bắp bò", "thịt bắp bò", "thịt bò bắp sống",
             "thịt bắp bò cắt lát", "sườn bò", "dẻ sườn bò"),
    "10009": ("phô mai", "phó mát", "cheese", "phô mai bào sợi",
              "phô mai các loại", "phô mai bào"),
    "20007": ("nấm đùi gà", "nấm đùi gà non", "nấm đùi gà mini",
              "nấm king oyster", "nấm đùi gà baby", "nấm đùi gà nhỏ",
              "nấm đùi gà chín giũ ráo nước", "nấm đùi gà cắt hạt lựu",
              "nấm rơm nấm đùi gà", "nấm đùi gà cắt dọc cắt lát dày",
              "nấm đùi gà lớn", "nấm đùi gà to", "nấm đùi gà mi ni"),
}
assert set(ALIAS_MUST_REMAIN) == set(CODE_NAMES)
assert not set(ALIAS_REPOINTS) & {k for v in ALIAS_MUST_REMAIN.values() for k in v}

# The systemic-mismatch cure in scripts/run_qwen_line_pipeline.py section A
# ("elif re.search(r'\bbắp bò\b', raw_l): candidate = ('7094', ...)"). It runs
# after matching and overrides the alias result, which is why the cure-held
# rows below sit on 7094 regardless of what their alias says. Re-declared here
# rather than imported because that module is a top-level script that executes
# the whole pipeline on import.
CURE_RAW_PATTERN = re.compile(r"\bbắp bò\b")
CURE_CODE = "7094"

# --- Row-level scope -------------------------------------------------------

# The 111 rows repaired by this fix, grouped by the alias that reaches them and
# pinned by id and exact raw_text. Every one is resolved by the repoint alone:
# there are no row-level overrides here, so re-running the matcher reproduces
# all 111.
REPAIR_ROWS = {
    "thịt thịt nạc thăn": (
        ("5e7f1ca3-cba7-45c9-8dd1-76e2c8e48ca9", "300 g thịt nạc thăn"),
        ("0a015a58-5c03-413b-ba3a-bcdc56e94ade", "Thịt nạc thăn"),
        ("d96eeb79-74f0-4091-b055-90c05a88930e", "1 kg thịt nạc thăn"),
        ("4c08e8ff-c555-4509-a94a-668dcccaf2d8", "300 gr Thịt nạc thăn"),
        ("712921e7-d15a-431c-a976-5b962c0631d4", "Thịt nạc thăn 200 gr"),
    ),
    "chả lụa": (
        ("32b99d97-a9e0-4ac8-accf-b77cc011cbdf", "50 gr chả lụa"),
        ("6f8e42ad-6dec-44ea-86db-cbeeba9cea37", "Chả lụa"),
        ("f02deed6-8333-4dd6-972e-73754d606213", "200 g chả lụa"),
        ("1267bdd0-b0d4-4c6b-bcab-52b8d67fe337", "Chả lụa 50g"),
        ("8d40fd03-500b-4d3a-bec9-805e2e15ad70", "Chả lụa 100g"),
        ("f946f1db-6517-42a4-8def-22dba9f4d4ed", "Chả lụa: 150g"),
        ("81bb95aa-7457-4b4a-a240-fbda8ca76539", "Chả lụa: 80g"),
        ("4f5b8e26-15dc-4551-ac31-ed5fe0e27dc1", "Chả lụa 250 gr"),
        ("031b4c4e-4c8c-4e7a-9e42-77b9fbf1c1db", "Chả lụa 1 cây"),
    ),
    "chả lụa cắt hạt lựu": (
        ("56c3a1a6-68b8-4fe4-9030-f9d42f008d4e", "Chả lụa 50g - cắt hạt lựu"),
    ),
    "da heo": (
        ("2a466722-ed43-4220-899e-4c694db6ea2f", "1 miếng da heo"),
        ("f5fdb0f6-a9f2-4458-92fc-5ffd048b274a", "150 gr da heo"),
        ("7e4d63e8-de9a-428a-8795-5eeea5487805", "200 gr da heo"),
        ("9592cf60-e7bf-4286-983f-730525e9542c", "300 gr da heo"),
        ("a9bef67a-b3b3-4a39-98e3-b8c375f4ed24", "50 g da heo"),
        ("174da2e3-bb18-468f-9aab-d8e57b3c2c4d", "Da heo 500g"),
        ("8ff37f84-8bf8-4893-ab48-563d749bd0af", "Da heo 100g"),
        ("f6d262e6-e2fa-47a2-91b1-68394d8b64c2", "Da heo: 100g"),
        ("6dfc3067-060d-4cf6-b17a-4620c3236f5c", "Da heo 1 ít"),
        ("aa3e3ad7-4f24-4cc2-adc1-3b034c49b037", "Da heo 100 g"),
        ("d492c791-f3b6-4dd4-b30b-17f94750f95c", "Da heo 500 gr"),
        ("91b0c9e3-d907-4089-85a2-d999d550a7d9", "Da heo 100 gr"),
    ),
    "da heo tươi": (
        ("af09ba50-0c60-41cf-be08-c00367ef82af", "Da heo tươi: 200g"),
    ),
    "phile bò": (
        ("079c6db7-0039-4e35-b36b-9e3007a0e540", "300 g phile bò"),
        ("a18851e7-10b6-4ed7-bb81-017ca4690902", "100 g phile bò"),
        ("edae7b38-99a2-40ac-9f94-a6d348c33b18", "100 g phile bò"),
        ("71e3b34b-b5d4-47ae-8060-9accde3304ef", "100 g phile bò"),
        ("c2754dd6-0c4f-4a33-acd2-352148297e61", "100 g phile bò"),
        ("4b9920e4-7a7f-43ee-9053-31030b19fa24", "100 g phile bò"),
        ("4c926ed0-cdd2-4f9a-b399-29dc9cce8213", "100 g phile bò"),
        ("d399c4e3-8a54-4057-b929-c374b7976076", "200 g phile bò"),
        ("d3ecd030-55f1-42fa-b1c1-aa3f5a432cea", "100 g phile bò"),
        ("d0c49e4d-5867-42bc-ae25-f0ba8ce57dae", "100 g phile bò"),
        ("65bf873c-538f-47f4-8c8c-c68760f1f2aa", "200 g phile bò"),
        ("57524cfe-258c-4252-9c80-dd12dd32ec59", "100 g phile bò"),
        ("e3bf7be2-f222-479d-87e1-6f83cff83127", "200 g phile bò"),
        ("8bdcab54-7b00-4a53-a3e3-49d3e071cff5", "100 g phile bò"),
        ("48e65763-9f99-42d0-8869-297d8864425b", "100 g phile bò"),
        ("86799f42-d583-43fb-91fb-e5edc9a2feb2", "300 g phile bò"),
        ("146a2be0-fa7b-412c-81c8-e42eb383eaf1", "200 g phile bò"),
        ("d6ad173a-3ba7-4caa-92a8-5b74787d0296", "100 g phile bò"),
    ),
    "bò phile": (
        ("2e40483c-e411-4254-b9d4-9dcc402794f3", "50 g bò phile"),
        ("f0791dc5-c6fa-4552-8e40-1d21070e17ab", "100 g bò phile"),
        ("b6e81aee-6b9e-4678-ab34-31e0fd53368c", "100 g bò phile"),
        ("3742d492-c22c-457d-964f-4d8300cbcf5b", "300 g bò phile"),
    ),
    "bò thăn": (
        ("16839bd0-add4-4283-886c-e16a118e46d9", "200 gr bò thăn"),
        ("ee21b5ed-292d-47c3-8af0-64319e0f1ec1", "150 gr bò thăn"),
        ("21039de6-08ec-43ae-81b9-daf8dfdf997a", "150 gr bò thăn"),
        ("2f188c40-ce67-42a0-8628-bb903b6389e8", "100 gr bò thăn"),
        ("9a71e0f0-23e2-4ae1-bfaa-886af0347204", "400 gr Bò thăn thái mỏng"),
        ("5b31613a-5ef8-447b-b4da-e647bf4d18ea", "100 gr Bò thăn"),
        ("5fc97719-ceab-4b40-a19d-0e5924ae848a", "Bò thăn (chọn khối chữ nhật): 400g"),
    ),
    "gân bò": (
        ("9d6e63c5-8aec-4cf1-9ab3-fa6a668c08e5", "Gân bò 200 gr"),
        ("1a56a54e-a25d-4699-ac41-8a72302ff673", "Gân bò 0.5 kg"),
        ("59a39b9b-eafb-402e-9c93-a4575043c064", "Gân bò 350 gr"),
        ("10eb2c4d-2ba4-4f96-a0f3-fe570f51abf0", "Gân bò 500 gr"),
        ("89e768b2-1376-437b-b73b-f5b3b68f8cd2", "Gân bò 500 gr"),
        ("cfbc5fd8-f654-42eb-94fb-82ae0017a0eb", "Gân bò 500 gr"),
        ("a70203de-5b2e-4616-9998-8c6930c55944", "Gân bò 350 gr"),
        ("38fd2474-45cf-4a1c-b006-8df442471744", "Gân bò 700 gr"),
        ("ffc9d830-a111-4a14-b45a-a8d2ad6972e0", "Gân bò 300 gr"),
        ("5ad34949-1d5a-40a8-8e22-26a61897d824", "Gân bò 400 g"),
        ("0147e439-8c8d-4ac8-a1f6-391594e86214", "Gân bò 500 gr"),
        ("e4f305bd-02a7-42ee-8d8d-6044354ca750", "Gân bò 300 gr"),
        ("fff25e63-3552-4389-a44c-c6b9e53ffa58", "Gân bò 500 gr"),
        ("db5a82cb-b817-4bf6-87ef-39fe0f05c56e", "Gân bò 400 gr"),
        ("8c336e8f-3bc0-4dde-bf1b-737fc3a2e848", "Gân bò 250 gr"),
        ("14b9c774-8421-4682-94e3-2b823b4bc3e0", "Gân bò 300 gr"),
        ("9b297680-b1f6-4151-986d-8327bbff5711", "Gân bò 400 g"),
    ),
    "chim bồ câu": (
        ("740e9aaf-72c5-4999-bc84-3d4daa235caa", "Chim bồ câu 2 con"),
        ("f912f3ab-24ab-44b0-b41c-e1fb5f50334d", "Chim bồ câu 1.6 kg"),
        ("fc89ff58-217a-4e9f-838a-e7c512b81c19", "Chim bồ câu 2 con"),
        ("8bb76f23-36d9-4871-9faf-4538582b3ed1", "Chim bồ câu 1 con"),
        ("32982570-3c1e-4454-adb2-620fde905ba4", "Chim bồ câu 3 con"),
    ),
    "vịt": (
        ("e80e7b99-1bab-417c-a4c0-bdb26f03d2e1", "Vịt 1 con"),
        ("e1075b22-e6b1-4724-a0a5-a6c8dc948034", "Vịt 1 con"),
        ("26ad156e-0e13-49bc-99b6-6a60c1ce1767", "Vịt 1 con"),
        ("dd351296-9fb5-419c-950a-5ceae9932f85", "Vịt 600g"),
        ("b0b22d0f-770e-4010-a745-234bf9b8f3de", "Vịt làm sạch: 1/2 con"),
        ("de116ee8-97a8-4669-9c61-29039c167b2f", "Vịt 1/2 con (1kg)"),
        ("ae9016ff-ab85-48be-912d-755dd9fadac1", "Vịt 1/2 con (khoảng 1,2kg)"),
        ("20bf460c-5971-4af2-98e0-7bec288dad02", "Vịt 1/2 con"),
        ("d24850b0-e559-41d9-a229-f439560fae11", "Vịt 1/2 con (khoảng 700- 800g)"),
        ("cf0f9439-77d7-4236-a3c4-97355fc41100", "Vịt làm sạch 1/2 con"),
        ("8d028b94-099f-4af3-b8ee-13f3079d072f", "Vịt: 1/2 con"),
        ("88c8649b-cb29-4646-a0c4-b53930a16cfb", "Vịt 1 con"),
        ("6ad3e04a-da31-41ed-8e7c-1a9dd22ff2b4", "Vịt 1 con"),
        ("db23a2ee-bb08-46ab-b684-d25a10a7579d", "Vịt 1/2 con"),
        ("03df52ae-205f-46f0-8389-bbdeb25274b8", "Vịt 1/2 con"),
        ("34813066-e7d4-4316-a102-8239ecc09308", "Vịt 1 con"),
        ("5bd3f359-e852-4ce7-9460-a904441e108e", "Vịt 1 con"),
        ("ea71ef40-88ea-4f3a-b439-a1a01c642b45", "Vịt 1/2 con"),
        ("3a88d9e4-43ee-4073-bb4b-9c3a0b66ee7a", "Vịt 1/2 con"),
        ("77b994a2-d001-429b-9b58-8980556515ac", "Vịt 1 con"),
        ("21477f12-adfd-4c69-a9ec-24e9bc0db22f", "Vịt 1 con"),
        ("caafbc8c-aece-4077-ba05-c097e1defbc8", "Vịt 1/2 con"),
        ("9c53c31f-4d72-4839-a542-dd66f714a958", "Vịt 1/2 con"),
        ("f044ca7f-cc1b-4710-83d4-941d102c09ed", "Vịt 1/2 con"),
        ("12dcee6e-1f01-4850-8eef-5bbf37bb5a97", "Vịt 1/2 con"),
        ("f1ac6182-dc8a-4c0e-93f1-04f3bd699a88", "Vịt 1 con"),
        ("293fb46e-f167-465a-98a7-fdc7b7f1deb3", "Vịt 1 con"),
        ("b982aa73-ebc3-45ae-a1a9-5d76212c27c1", "Vịt 2 kg"),
        ("75bffd55-3821-4bfa-8a84-795d8ab91a77", "Vịt 1 con"),
    ),
    "phô mai đầu bò": (
        ("698a32ae-ed89-477f-afc9-55d7cb2e2ffe", "Phô mai đầu bò 1 miếng"),
    ),
    "đùi gà tây": (
        ("a75cef69-256a-461d-a06b-13fc854ac93f", "Đùi gà tây: 2 cái (600-700g)"),
    ),
    "nấm hủ đùi gà": (
        ("69be6f2a-8240-4509-b0c8-64f4667d1732", "Nấm hủ đùi gà 200g"),
    ),
}

# The 15 rows the "bắp bò" cure already standardised onto 7094. They are
# reachable by a repointed alias but must come through this fix byte-identical:
# the cure runs after matching and wins, so their identity is not this fix's to
# set. Every one of them is already on the correct beef-shank identity.
CURE_HELD_ROWS = {
    "bò phile": (
        ("f8a40702-28ba-45a9-afaa-4435a77d1dbb", "100 g bắp bò phile"),
        ("20f6d3fe-2241-4fdf-b6a2-7cb855daa459", "100 g bắp bò phile"),
        ("11e9706d-f998-473e-a319-44aa0c1fbe6b", "500 g bắp bò phile"),
    ),
    "bò hoa": (
        ("5a5e421a-b4ab-46ba-a0d1-cc1263badf29", "Bắp bò hoa 350g (1 cái)"),
        ("1f80c394-b7d0-40d6-952f-7e88f69dbb6e", "Bắp bò hoa: 300g"),
        ("052845b9-25d3-43a6-b438-597bade70c38", "Bắp bò hoa: 300g"),
        ("8f9ca4c4-35bc-4682-a245-3b60de4f531b", "Bắp bò hoa: 400g"),
        ("1c88ba8c-0d58-4317-9e92-8dce35800252", "Bắp bò hoa: 300g"),
        ("d9feb556-5247-473f-8379-70b666f1e1bb", "Bắp bò hoa: 200g (thái lát mỏng)"),
        ("184aa6b7-f73f-4828-aa68-61f873920fa7", "Bắp bò hoa 200g"),
        ("883b19f1-6da9-44c1-a59d-1d4a7b4cc8ec", "Bắp bò hoa 1 cái"),
        ("2fb1f315-db07-4bf9-bc60-3bffca5c3d61", "Bắp bò hoa 200g"),
        ("75fdc30f-37de-4470-82b7-ca74a8d26a60", "Bắp bò hoa 200g"),
        ("61307b00-92fe-4d75-80de-04ab3185049e", "Bắp bò hoa 150g"),
        ("ba68e662-b8bd-4f46-abdb-d62cc620e697", "Bắp bò hoa: 300g"),
    ),
}

# "bò hoa" is latent: every row it reaches is cure-held, so the repoint fixes
# the alias without moving a single row today.
LATENT_ALIASES = tuple(
    key for key in ALIAS_REPOINTS
    if not REPAIR_ROWS.get(key) and CURE_HELD_ROWS.get(key)
)

REPAIR_IDS_BY_ALIAS = {k: frozenset(i for i, _ in v) for k, v in REPAIR_ROWS.items()}
CURE_IDS_BY_ALIAS = {k: frozenset(i for i, _ in v) for k, v in CURE_HELD_ROWS.items()}
REPAIR_RAW_BY_ID = {i: raw for rows in REPAIR_ROWS.values() for i, raw in rows}
CURE_RAW_BY_ID = {i: raw for rows in CURE_HELD_ROWS.values() for i, raw in rows}
ALIAS_BY_REPAIR_ID = {i: key for key, rows in REPAIR_ROWS.items() for i, _ in rows}
REPAIR_IDS = frozenset(REPAIR_RAW_BY_ID)
CURE_IDS = frozenset(CURE_RAW_BY_ID)

assert set(REPAIR_ROWS) <= set(ALIAS_REPOINTS)
assert set(CURE_HELD_ROWS) <= set(ALIAS_REPOINTS)
assert len(REPAIR_IDS) == 111 == sum(len(v) for v in REPAIR_ROWS.values())
assert len(CURE_IDS) == 15 == sum(len(v) for v in CURE_HELD_ROWS.values())
assert not REPAIR_IDS & CURE_IDS
assert LATENT_ALIASES == ("bò hoa",)
# Every cure-held row really does carry the cure trigger; no repaired row does.
assert all(CURE_RAW_PATTERN.search(raw.lower()) for raw in CURE_RAW_BY_ID.values())
assert not any(CURE_RAW_PATTERN.search(raw.lower()) for raw in REPAIR_RAW_BY_ID.values())

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
    """Build the new alias map, touching only the fifteen reviewed keys."""
    new_map = dict(alias_map)
    for key, (_, new) in ALIAS_REPOINTS.items():
        new_map[key] = new

    # Belt-and-suspenders: every key outside the fifteen must be byte-identical
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


def _pending_probe(row, old_code):
    code = (row.get("master_ingredient_code") or "").strip()
    name = (row.get("master_ingredient_name") or "").strip()
    return (
        code == old_code
        and name == CODE_NAMES[old_code]
        and row.get("match_method") == PRESET_ALIAS_METHOD
        and (row.get("match_confidence") or "").strip() == PRESET_ALIAS_CONFIDENCE
    )


def _repair_applied_probe(row, new_code):
    code = (row.get("master_ingredient_code") or "").strip()
    name = (row.get("master_ingredient_name") or "").strip()
    return (
        code == new_code
        and name == CODE_NAMES[new_code]
        and row.get("match_method") == PRESET_ALIAS_METHOD
        and (row.get("match_confidence") or "").strip() == PRESET_ALIAS_CONFIDENCE
    )


def _cure_held_probe(row):
    code = (row.get("master_ingredient_code") or "").strip()
    name = (row.get("master_ingredient_name") or "").strip()
    return (
        code == CURE_CODE
        and name == CODE_NAMES[CURE_CODE]
        and row.get("match_method") == CURE_METHOD
        and (row.get("match_confidence") or "").strip() == CURE_CONFIDENCE
    )


def _row_state(row, raw_text, alias_key):
    rid = row.get("id")
    if row.get("raw_text") != raw_text:
        raise DriftError(
            f"row {rid}: raw_text drifted (expected {raw_text!r}, found {row.get('raw_text')!r})"
        )
    old, new = ALIAS_REPOINTS[alias_key]
    if _pending_probe(row, old):
        return "pending"
    if _repair_applied_probe(row, new):
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
    """Read-only: locate the alias edits and the 126 in-scope rows, classify each."""
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

    ing_rows = read_csv(ING)
    by_id = {r["id"]: r for r in ing_rows}

    row_states = {}
    for rid, raw_text in REPAIR_RAW_BY_ID.items():
        row = by_id.get(rid)
        if row is None:
            raise DriftError(f"repair row {rid} not found in {ING}")
        row_states[rid] = _row_state(row, raw_text, ALIAS_BY_REPAIR_ID[rid])

    # Cure-held rows must already be exactly where the cure put them, in every
    # run -- there is no "pending" state for them.
    for rid, raw_text in CURE_RAW_BY_ID.items():
        row = by_id.get(rid)
        if row is None:
            raise DriftError(f"cure-held row {rid} not found in {ING}")
        if row.get("raw_text") != raw_text:
            raise DriftError(
                f"cure-held row {rid}: raw_text drifted "
                f"(expected {raw_text!r}, found {row.get('raw_text')!r})"
            )
        if not _cure_held_probe(row):
            raise DriftError(
                f"cure-held row {rid} is not on {CURE_CODE}/{CURE_METHOD} "
                f"(found code={row.get('master_ingredient_code')!r} "
                f"method={row.get('match_method')!r}) -- the cure evidence has drifted"
            )

    # No repaired row's raw_text may trigger the "bắp bò" cure: if one did, a
    # later pipeline run would silently overwrite the identity written here.
    for rid, raw_text in REPAIR_RAW_BY_ID.items():
        if CURE_RAW_PATTERN.search(raw_text.lower()):
            raise DriftError(
                f"repair row {rid} raw_text {raw_text!r} matches the 7094 cure pattern -- "
                "its identity is the cure's to set, not this alias fix's"
            )

    # The pinned sets must equal the sets the aliases can actually reach. A row
    # appearing or disappearing means the blast radius is no longer the
    # reviewed one, so nothing may be written.
    matcher = VietnameseIngredientMatcher(catalog_csv_path=MASTER)
    reachable = rows_reachable_by_alias(ing_rows, matcher)
    for key in ALIAS_REPOINTS:
        expected = REPAIR_IDS_BY_ALIAS.get(key, frozenset()) | CURE_IDS_BY_ALIAS.get(key, frozenset())
        if reachable[key] != set(expected):
            raise DriftError(
                f"blast radius drifted for alias {key!r}: reachable "
                f"{sorted(reachable[key] - set(expected))[:5]} extra / "
                f"{sorted(set(expected) - reachable[key])[:5]} missing"
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

    before_by_id = {r["id"]: r for r in ing_csv_rows if r["id"] in REPAIR_IDS | CURE_IDS}
    after_by_id = {r["id"]: r for r in new_ing_csv_rows if r["id"] in REPAIR_IDS | CURE_IDS}

    # Post-transform guards.
    for rid in REPAIR_IDS:
        _, new = ALIAS_REPOINTS[ALIAS_BY_REPAIR_ID[rid]]
        if not _repair_applied_probe(after_by_id[rid], new):
            raise DriftError(f"row {rid} did not reach the {new} fixed state -- refusing to write")
    # Cure-held rows must come through byte-identical.
    for rid in CURE_IDS:
        if after_by_id[rid] != before_by_id[rid]:
            raise DriftError(f"cure-held row {rid} was modified -- refusing to write")
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
        repair_ids = REPAIR_IDS_BY_ALIAS.get(key, frozenset())
        cure_ids = CURE_IDS_BY_ALIAS.get(key, frozenset())
        before = _nutrition_totals(before_by_id[r] for r in repair_ids)
        after = _nutrition_totals(after_by_id[r] for r in repair_ids)
        by_alias[key] = {
            "from": {"code": old, "name": CODE_NAMES[old]},
            "to": {"code": new, "name": CODE_NAMES[new]},
            "alias_state": alias_states[key],
            "rows_reachable": len(repair_ids) + len(cure_ids),
            "rows_repaired": len(repair_ids),
            "rows_cure_held": len(cure_ids),
            "latent": key in LATENT_ALIASES,
            "recipes_affected": len(
                {before_by_id[r]["recipe_id"] for r in repair_ids}
            ),
            "nutrition": {"before": before, "after": after, "delta": _delta(before, after)},
        }

    report = {
        "status": "applied" if apply else "preview",
        "alias_decision": "SAFE_REPOINT",
        "alias_repoint_count": len(ALIAS_REPOINTS),
        "alias_states": alias_states,
        "alias_repoints": {k: {"from": v[0], "to": v[1]} for k, v in ALIAS_REPOINTS.items()},
        "latent_aliases": list(LATENT_ALIASES),
        "aliases_removed": 0,
        "aliases_added": 0,
        "alias_map_size": len(new_alias_map),
        "match_method_semantics": {
            "repaired_rows": f"{PRESET_ALIAS_METHOD} / {PRESET_ALIAS_CONFIDENCE} (unchanged)",
            "cure_held_rows": f"{CURE_METHOD} / {CURE_CONFIDENCE} (unchanged)",
            "row_level_overrides": 0,
        },
        "rows_in_scope": len(REPAIR_IDS) + len(CURE_IDS),
        "rows_repaired_total": len(REPAIR_IDS),
        "rows_repaired_now": len(repair_now),
        "rows_already_applied": len(REPAIR_IDS) - len(repair_now),
        "rows_cure_held_untouched": len(CURE_IDS),
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
        "by_alias": by_alias,
        "repair_row_ids": sorted(REPAIR_IDS),
        "cure_held_row_ids": sorted(CURE_IDS),
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
        "cure_held_outcomes": {
            rid: {
                "raw_text": before_by_id[rid].get("raw_text"),
                "cleaned_name": before_by_id[rid].get("cleaned_name"),
                "decision": "UNCHANGED_CURE_HELD",
                "state": {f: before_by_id[rid].get(f) for f in REPORT_ROW_FIELDS},
            }
            for rid in sorted(CURE_IDS)
        },
        "out_of_scope_note": (
            "Batch A repoints exactly fifteen aliases. Every other 70xx audit finding is "
            "deliberately unchanged here. Two of the deferrals this batch recorded have since "
            "been resolved by the reviewed follow-up "
            "(scripts/eda/apply_meat_band_batch_a_followup_safe_fix.py): the cốt lết family -> "
            "7053 and 'bóng bì' -> 7031, together with 'thịt bò chay lát' -> 20039. Still "
            "deferred: the remaining vegan analogues ('đùi gà chay' -> 7088, 'xúc xích chay' -> "
            "7077, 'nem chua chay' -> 7073, 'thịt cua chay' -> 8069), the vegan seasoning "
            "analogues, 'thịt ba chỉ rút sườn' (fixed in Batch B), 'sườn bò'/'dẻ sườn bò', "
            "'mỡ gà', 'thịt heo quay', 'nạm bò', 'ba chỉ bò', 'chả chiên', 'mỡ nước', 'tóp mỡ', "
            "'gà tre', catalog name_vi corruption, 'xương bò', the 7096 corruption, "
            "cleaner/matcher policy, and stale-code remediation."
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
    skip = ("repair_row_ids", "cure_held_row_ids", "row_outcomes",
            "cure_held_outcomes", "affected_recipe_ids")
    print(json.dumps(
        {k: v for k, v in report.items() if k not in skip},
        ensure_ascii=False, indent=2,
    ))


if __name__ == "__main__":
    main()
