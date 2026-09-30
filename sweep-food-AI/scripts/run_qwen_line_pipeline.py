import csv
import json
import logging
import os
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from nlp.nutrition import restore_missing_nutrition
from nlp.qwen_matching import (
    build_mapper_rules,
    eligible_for_qwen_recovery,
    qwen_candidate_eligibility,
    map_clean_to_master as _map_clean_to_master,
    resolve_cleaned_name_update,
    resolve_qwen_row,
)

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("qwen_pipeline")

MODEL_ID = "Qwen/Qwen2.5-3B-Instruct"
device = "cuda" if torch.cuda.is_available() else "cpu"

INTERIM_ING_CSV = "data/interim/recipe_ingredients.csv"
INTERIM_ING_JSON = "data/interim/recipe_ingredients.json"
PROCESSED_ING_CSV = "data/processed/recipes/recipe_ingredients.csv"
PROCESSED_ING_JSON = "data/processed/recipes/recipe_ingredients.json"

MASTER_CSV = "data/processed/viendinhduong/master_ingredients_nutrition.csv"
RECIPES_CSV = "data/processed/recipes/recipes.csv"
RECIPES_JSON = "data/processed/recipes/recipes.json"
CRAWLED_CLEANED_CSV = "data/interim/recipes_crawled_cleaned.csv"
CRAWLED_CLEANED_JSON = "data/interim/recipes_crawled_cleaned.json"

# Load Master Nutrition
with open(MASTER_CSV, "r", encoding="utf-8-sig") as f:
    master_rows = list(csv.DictReader(f))
    master_dict = {r["code"]: r for r in master_rows}
    logger.info(f"Loaded {len(master_dict)} items from Master Nutrition Table.")

# A1 root-cause fix: hard-coded (code, name) mapper pairs are only usable if
# they still identify the same catalog entry today. A pair whose code is
# absent or whose name has drifted is disabled rather than applied blindly.
QWEN_MAPPER_RULES, QWEN_MAPPER_DISABLED_RULES = build_mapper_rules(master_dict)
if QWEN_MAPPER_DISABLED_RULES:
    logger.warning(
        "Disabled %d stale Qwen mapper rule(s) whose hard-coded code/name no longer "
        "matches the master catalog (existence alone is not identity validation): %s",
        len(QWEN_MAPPER_DISABLED_RULES),
        [(terms, code, name, "catalog now: " + str(actual)) for terms, code, name, actual in QWEN_MAPPER_DISABLED_RULES],
    )

# Load Ingredient Data
with open(INTERIM_ING_CSV, "r", encoding="utf-8-sig") as f:
    ing_rows = list(csv.DictReader(f))
    fieldnames = list(ing_rows[0].keys())
    logger.info(f"Loaded {len(ing_rows):,} ingredient rows from {INTERIM_ING_CSV}.")

# Step 1: Identify Recoverable Unmatched Rows (Group 1: 614 rows)
recover_rules = [
    r"\b(hành lá|hành hoa|ngò rí|rau mùi|ngò gai|hành trắng|đầu hành|húng lủi|bạc hà)\b",
    r"\b(cải thảo|bắp cải|cải thìa|cải xanh|cải con|cải xoong|cải ngồng)\b",
    r"\b(xoài keo|xoài xanh|xoài|chanh|tắc|quất|thanh long|dưa hấu)\b",
    r"\b(cà bi|cà chua bi|cà chua)\b",
    r"\b(cà rốt|carrot)\b",
    r"\b(đậu bắp|đậu que|đậu cove|đậu đũa)\b",
    r"\b(tiêu trắng|tiêu sọ|tiêu đen|tiêu hạt)\b",
    r"\b(nạc dăm|cá cơm khô|tôm càng|cua biển|chả huế|cá thác lác)\b",
    r"\b(tàu hũ ki|tàu hủ ki|váng đậu|mì căn|phù trúc)\b",
    r"\b(bột màu điều|xốt mè|mayonnaise|vani|dầu điều|bột chiên)\b",
    r"\b(nước ấm|nước vo gạo|nước dùng)\b"
]
combined_pattern = re.compile("|".join(recover_rules), re.I)

target_unmatched_indices = []
for idx, r in enumerate(ing_rows):
    m_code = (r.get("master_ingredient_code") or "").strip()
    m_name = (r.get("master_ingredient_name") or "").strip()
    status = (r.get("match_method") or "").strip()

    if not m_code or m_code == "None" or not m_name or m_name == "None" or status == "UNMATCHED":
        raw_text = r.get("raw_text", "").strip()
        cleaned_name = r.get("cleaned_name", "").strip()
        if combined_pattern.search(f"{raw_text} {cleaned_name}"):
            target_unmatched_indices.append((idx, raw_text))

logger.info(f"Identified {len(target_unmatched_indices)} target unmatched rows for LLM extraction.")
unique_raw_texts = sorted(list(set(raw for _, raw in target_unmatched_indices if raw)))
logger.info(f"Deduplicated to {len(unique_raw_texts)} unique raw texts for Qwen 2.5 3B.")

# Step 2: Initialize Qwen 2.5 3B or Load Cache
QWEN_CACHE_FILE = "data/interim/qwen_extracted_map.json"
llm_extracted_map = {}

if os.path.exists(QWEN_CACHE_FILE):
    try:
        with open(QWEN_CACHE_FILE, "r", encoding="utf-8") as f:
            llm_extracted_map = json.load(f)
        logger.info(f"Loaded {len(llm_extracted_map)} cached LLM extractions from {QWEN_CACHE_FILE}.")
    except Exception as e:
        logger.warning(f"Failed to read cache: {e}")

if len(llm_extracted_map) < len(unique_raw_texts) * 0.8:
    logger.info(f"Initializing {MODEL_ID} on {device}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, local_files_only=True, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.float16,
        device_map="auto",
        local_files_only=True,
        trust_remote_code=True
    )

    SYSTEM_PROMPT = """You are an expert culinary entity extractor for Vietnamese recipes.
Your task is to extract ONLY the clean, canonical culinary ingredient name from each numbered input line.

EXTRACTION RULES:
- Remove preparation actions (e.g. xát nhỏ, băm nhỏ, thái lát, chiên trứng, phi thơm).
- Remove commercial brand names (e.g. Aji-Quick, Knorr, Maggi, Chinsu, Meizan). If input has brand + product like 'Aji-Quick Bột Chiên Giòn', remove the brand and keep 'bột chiên giòn'.
- Remove quantities, units, and descriptors (e.g. tươi, ngon, loại 1, 100g, 2 muỗng).
- Preserve specific food identity: 'cải thảo', 'bắp cải', 'đậu bắp', 'củ sen', 'ngó sen', 'lá cà ri', 'cá cam', 'cá nục', 'nạc dăm', 'bột chiên giòn', 'hành lá', 'hạt tiêu', 'xoài', 'tắc'.
- Output format: exactly one numbered line per item matching the input index:
1. <canonical_ingredient>
2. <canonical_ingredient>
Do not output explanations, notes, or JSON.
"""

    BATCH_SIZE = 20
    t_start_llm = time.perf_counter()
    logger.info(f"Running fast numbered-line LLM extraction across {len(unique_raw_texts)} unique strings...")

    for batch_start in range(0, len(unique_raw_texts), BATCH_SIZE):
        batch_items = unique_raw_texts[batch_start:batch_start + BATCH_SIZE]
        user_content = "Extract the canonical ingredient name for each line:\n"
        for i, s in enumerate(batch_items, 1):
            user_content += f"{i}. {s}\n"

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ]

        prompt_text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer([prompt_text], return_tensors="pt").to(device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=256,
                do_sample=False
            )

        output_ids = outputs[0][len(inputs.input_ids[0]):]
        res_text = tokenizer.decode(output_ids, skip_special_tokens=True).strip()

        # Parse numbered lines
        lines = [ln.strip() for ln in res_text.splitlines() if ln.strip()]
        for ln in lines:
            m = re.match(r"^(\d+)[\.\:\-\)]\s*(.+)$", ln)
            if m:
                item_idx = int(m.group(1)) - 1
                canonical_name = m.group(2).strip().lower()
                # Clean any trailing punctuation or quotes
                canonical_name = re.sub(r"[\"\'\.\,\;]", "", canonical_name).strip()
                if 0 <= item_idx < len(batch_items):
                    orig_raw = batch_items[item_idx]
                    llm_extracted_map[orig_raw] = canonical_name

        logger.info(f"Processed {min(batch_start + len(batch_items), len(unique_raw_texts))}/{len(unique_raw_texts)} items (Mapped: {len(llm_extracted_map)})")

    t_llm_elapsed = time.perf_counter() - t_start_llm
    logger.info(f"LLM extraction completed in {t_llm_elapsed:.2f}s ({len(unique_raw_texts)/t_llm_elapsed:.1f} items/sec).")

    # Save cache
    with open(QWEN_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(llm_extracted_map, f, ensure_ascii=False, indent=2)
    logger.info(f"Cached {len(llm_extracted_map)} extracted items to {QWEN_CACHE_FILE}.")

    # Free LLM GPU memory
    del model
    del tokenizer
    torch.cuda.empty_cache()
    logger.info("Freed LLM from GPU memory.")

# Step 3: Semantic Mapper from Canonical Name -> Master Nutrition Code (see
# nlp/qwen_matching.py for the validated rule table and root-cause fixes).
def map_clean_to_master(clean_name):
    return _map_clean_to_master(clean_name, QWEN_MAPPER_RULES)

# Step 4: Apply LLM-recovered entities and systemic mismatch cures
updated_rows_count = 0
llm_recovered_count = 0
mismatch_cured_count = 0
weight_capped_count = 0
rejected_dangling_candidate_count = 0
preserved_cleaned_name_count = 0
rejected_eligibility_reasons = defaultdict(int)

# A3 diagnostic: rows the previous (buggy) `status == "UNMATCHED"` condition
# would have let Qwen recovery overwrite even though a master link was
# already populated. eligible_for_qwen_recovery() below now protects them.
protected_populated_link_count = sum(
    1 for r in ing_rows
    if (r.get("match_method") or "").strip() == "UNMATCHED" and not eligible_for_qwen_recovery(r)
)
if protected_populated_link_count:
    logger.info(f"Protecting {protected_populated_link_count:,} populated links with stale UNMATCHED status from recovery overwrite.")

for idx, r in enumerate(ing_rows):
    raw_t = r.get("raw_text", "").strip()
    raw_l = raw_t.lower()
    clean_n = (r.get("cleaned_name") or "").strip().lower()
    m_code = (r.get("master_ingredient_code") or "").strip()
    m_name = (r.get("master_ingredient_name") or "").strip()
    m_name_l = m_name.lower()
    status = (r.get("match_method") or "").strip()

    try:
        w = float(r.get("estimated_weight_g") or 0.0)
    except:
        w = 0.0
    try:
        qty = float(r.get("required_quantity") or 0.0)
    except:
        qty = 1.0
    if qty <= 0:
        qty = 1.0
    original_w = w

    candidate = None
    cleaned_name_update = None

    # A. CURE SYSTEMIC MISMATCHES (candidate detection only; validated below)
    if re.search(r"\bđậu bắp\b", raw_l):
        candidate = ("20086", "Đậu bắp (Bắp còi)", "STANDARDIZED_CURE")
        if "trái" in raw_l or "quả" in raw_l:
            w = qty * 10.0
    elif re.search(r"\bcá cam\b", raw_l):
        candidate = ("20104", "Cá cam tươi (Amberjack)", "STANDARDIZED_CURE")
    elif re.search(r"\bcá nục chuối\b", raw_l):
        candidate = ("8021", "Cá nục", "STANDARDIZED_CURE")
    elif re.search(r"\bbột chiên giòn\b", raw_l) and ("bột năng" in m_name_l or not m_code):
        candidate = ("13045", "Bột chiên giòn", "STANDARDIZED_CURE")
    elif re.search(r"\bbột chiên xù\b", raw_l) and ("bột năng" in m_name_l or not m_code):
        candidate = ("13067", "Bột chiên xù", "STANDARDIZED_CURE")
    elif re.search(r"\bcủ sen\b", raw_l) and not re.search(r"\bhạt sen\b", raw_l):
        candidate = ("20103", "Củ sen tươi (Lotus root)", "STANDARDIZED_CURE")
    elif re.search(r"\bngó sen\b", raw_l) and not re.search(r"\bhạt sen\b", raw_l):
        candidate = ("4059", "Ngó sen", "STANDARDIZED_CURE")
    elif re.search(r"\bbắp bò\b", raw_l):
        candidate = ("7094", "Thịt bắp bò", "STANDARDIZED_CURE")
    elif re.search(r"\b(hạt điều đỏ|bột hạt điều|hạt điều màu)\b", raw_l) and "3015" in str(m_code):
        candidate = ("13056", "Bột hạt điều (dầu điều)", "STANDARDIZED_CURE")
    elif str(m_code) == "8041" and not re.search(r"\b(ốc|thịt ốc)\b", raw_l):
        if re.search(r"\b(ớt bột|bột ớt)\b", raw_l):
            candidate = ("20018", "Ớt bột Hàn Quốc (gochugaru)", "STANDARDIZED_CURE")
        elif re.search(r"\btương ớt\b", raw_l):
            candidate = ("13021", "Tương ớt", "STANDARDIZED_CURE")
        elif re.search(r"\bkim chi\b", raw_l):
            candidate = ("4117", "Dưa cải muối chua", "STANDARDIZED_CURE")
        elif re.search(r"\b(bánh gạo|miến|mì)\b", raw_l):
            candidate = ("1017", "Bột gạo", "STANDARDIZED_CURE")
        elif re.search(r"\b(gốc hành|hành lá)\b", raw_l):
            candidate = ("4019", "Hành hoa, tươi", "STANDARDIZED_CURE")
        elif re.search(r"\bgốc ngò\b", raw_l):
            candidate = ("4073", "Rau mùi (ngò rí)", "STANDARDIZED_CURE")
        elif re.search(r"\bgốc sả\b", raw_l):
            candidate = ("13024", "Sả", "STANDARDIZED_CURE")
        elif re.search(r"\bphú quốc\b", raw_l) and "nước mắm" in raw_l:
            candidate = ("13017", "Nước mắm", "STANDARDIZED_CURE")
        else:
            candidate = ("20018", "Ớt bột Hàn Quốc (gochugaru)", "STANDARDIZED_CURE")
    elif str(m_code) == "8011" and not re.search(r"\bcá hồi\b", raw_l) and re.search(r"\b(hồi|hoa hồi|tai hồi)\b", raw_l):
        candidate = ("20010", "Hoa hồi (đại hồi)", "STANDARDIZED_CURE")
    elif re.search(r"\bmía\b", raw_l) and str(m_code) == "10001":
        candidate = ("14040", "Nước mía", "STANDARDIZED_CURE")
    elif re.search(r"\bnấm chân gà\b", raw_l):
        candidate = ("4128", "Nấm mỡ (Nấm tây)", "STANDARDIZED_CURE")

    # B. RECOVER UNMATCHED VIA QWEN LINE-BY-LINE EXTRACTION
    # A3 root-cause fix: only when the row has neither a code nor a name
    # already, never merely because match_method says UNMATCHED.
    elif eligible_for_qwen_recovery(r) and raw_t in llm_extracted_map:
        clean_extracted = llm_extracted_map[raw_t]
        code_match, name_match = map_clean_to_master(clean_extracted)
        candidate_eligible, rejection_reason = qwen_candidate_eligibility(
            raw_t, clean_extracted, code_match,
        )
        if code_match and name_match and not candidate_eligible:
            rejected_eligibility_reasons[rejection_reason] += 1
            logger.info("Qwen recovery rejected: raw=%r output=%r reason=%s",
                        raw_t, clean_extracted, rejection_reason)
        if code_match and name_match and candidate_eligible:
            candidate = (code_match, name_match, "QWEN_LLM_MATCH")
            # A6 root-cause fix: Qwen sometimes narrows the name and drops an
            # identity/state qualifier ("xoài keo" -> "xoài"). The baseline is
            # re-derived from raw_text by the grammar parser, NOT read from
            # r["cleaned_name"], because a historical row may already store a
            # damaged Qwen output and comparing against that would confirm the
            # loss instead of catching it. A rejected rewrite yields None,
            # which stage_qwen_update() treats as "leave cleaned_name alone" --
            # the validated match/code/weight update on this row still applies.
            cleaned_name_update = resolve_cleaned_name_update(raw_t, clean_extracted)
            if cleaned_name_update is None:
                preserved_cleaned_name_count += 1

    # C. LEAF & SPICE WEIGHT CAPS
    is_leaf = bool(re.search(r"\b(lá lốt|lá cà ri|lá chanh|lá chúc|lá bạc hà|lá mơ|lá húng)\b", raw_l))
    is_garlic_clove = bool(re.search(r"\b(múi tỏi|tép tỏi)\b", raw_l))
    is_root_herb = bool(re.search(r"\b(gốc ngò|gốc hành)\b", raw_l))
    is_chili = bool(re.search(r"\b(ớt hiểm|ớt chỉ thiên)\b", raw_l) and ("quả" in raw_l or "trái" in raw_l))
    is_star_anise = bool(re.search(r"\b(bông hồi|tai hồi|hoa hồi)\b", raw_l))

    if is_leaf:
        if w > qty * 2.0 or w >= 40.0:
            w = max(1.0, qty * 1.5)
    elif is_garlic_clove:
        if w >= 50.0:
            w = max(3.0, qty * 4.0)
    elif is_root_herb:
        if w >= 50.0:
            w = max(2.0, qty * 3.0)
    elif is_chili:
        if w >= 40.0:
            w = max(2.0, qty * 2.0)
    elif is_star_anise:
        if w >= 30.0:
            w = max(1.0, qty * 1.5)

    # D. VALIDATE AND COMMIT (A4/A5 root-cause fix)
    # A candidate is only ever applied once its code is confirmed against the
    # live master catalog; a dangling/invalid candidate is rejected and the
    # row's existing matching fields are left untouched. match_confidence is
    # stamped only for a row whose matching fields actually changed, never
    # for an independent weight-only correction.
    weight_changed = w != original_w
    if candidate is not None or weight_changed:
        updates = resolve_qwen_row(r, master_dict, w, candidate, cleaned_name_update)
        match_applied = candidate is not None and "master_ingredient_code" in updates
        if match_applied or weight_changed:
            r.update(updates)
            updated_rows_count += 1
        if match_applied:
            if candidate[2] == "QWEN_LLM_MATCH":
                llm_recovered_count += 1
            else:
                mismatch_cured_count += 1
        elif candidate is not None:
            rejected_dangling_candidate_count += 1
        if weight_changed and not match_applied:
            weight_capped_count += 1

logger.info(f"Total rows modified: {updated_rows_count:,}")
logger.info(f"  - Qwen LLM recovered rows: {llm_recovered_count:,}")
logger.info(f"  - Systemic mismatch cured: {mismatch_cured_count:,}")
logger.info(f"  - Leaf/spice weights capped: {weight_capped_count:,}")
logger.info(f"  - Rejected dangling/invalid candidates (no mutation): {rejected_dangling_candidate_count:,}")
logger.info("  - Rejected Qwen recovery eligibility: %s", dict(rejected_eligibility_reasons))
logger.info(f"  - Populated links protected from stale-UNMATCHED overwrite: {protected_populated_link_count:,}")
logger.info(f"  - cleaned_name rewrites rejected as lossy (match still applied): {preserved_cleaned_name_count:,}")

# Restore nulls also on inherited rows that did not need a matching update.
ing_rows = restore_missing_nutrition(ing_rows, master_dict)

# Step 5: Save Updated Ingredient Datasets
for csv_path, json_path in [(INTERIM_ING_CSV, INTERIM_ING_JSON), (PROCESSED_ING_CSV, PROCESSED_ING_JSON)]:
    logger.info(f"Saving to {csv_path} and {json_path}...")
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(ing_rows)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(ing_rows, f, ensure_ascii=False, indent=2)

# Step 6: Recalculate Recipe Nutrition Rollups
# Legacy policy: sum known contributions; missing fields do not make totals unknown.
logger.info("Recalculating recipe rollup totals...")
recipe_rollups = defaultdict(lambda: {"calories": 0.0, "protein": 0.0, "fat": 0.0, "carbs": 0.0, "weight": 0.0})

for r in ing_rows:
    rid = r.get("recipe_id")
    if not rid:
        continue
    try:
        recipe_rollups[rid]["calories"] += float(r.get("calories") or 0.0)
        recipe_rollups[rid]["protein"] += float(r.get("protein_g") or 0.0)
        recipe_rollups[rid]["fat"] += float(r.get("fat_g") or 0.0)
        recipe_rollups[rid]["carbs"] += float(r.get("carbs_g") or 0.0)
        recipe_rollups[rid]["weight"] += float(r.get("estimated_weight_g") or 0.0)
    except:
        pass

for r_csv, r_json in [(RECIPES_CSV, RECIPES_JSON), (CRAWLED_CLEANED_CSV, CRAWLED_CLEANED_JSON)]:
    if os.path.exists(r_csv):
        with open(r_csv, "r", encoding="utf-8-sig") as f:
            recipes = list(csv.DictReader(f))
            r_fields = list(recipes[0].keys())

        updated_recipes = 0
        for rec in recipes:
            rid = rec.get("id") or rec.get("recipe_id")
            if rid in recipe_rollups:
                t = recipe_rollups[rid]
                if "total_calories" in rec:
                    rec["total_calories"] = str(round(t["calories"], 1))
                if "total_protein_g" in rec:
                    rec["total_protein_g"] = str(round(t["protein"], 1))
                elif "total_protein" in rec:
                    rec["total_protein"] = str(round(t["protein"], 1))
                if "total_fat_g" in rec:
                    rec["total_fat_g"] = str(round(t["fat"], 1))
                elif "total_fat" in rec:
                    rec["total_fat"] = str(round(t["fat"], 1))
                if "total_carbs_g" in rec:
                    rec["total_carbs_g"] = str(round(t["carbs"], 1))
                elif "total_carbs" in rec:
                    rec["total_carbs"] = str(round(t["carbs"], 1))
                if "total_weight_g" in rec:
                    rec["total_weight_g"] = str(round(t["weight"], 1))
                updated_recipes += 1

        with open(r_csv, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=r_fields, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(recipes)
        with open(r_json, "w", encoding="utf-8") as f:
            json.dump(recipes, f, ensure_ascii=False, indent=2)
        logger.info(f"Updated {updated_recipes:,} recipes in {r_csv}")

logger.info("PIPELINE COMPLETED SUCCESSFULLY!")
