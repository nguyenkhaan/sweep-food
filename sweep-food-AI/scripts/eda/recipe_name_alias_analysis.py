"""Phase 2 lexical candidate discovery only; never changes canonical selections."""

import argparse
from collections import Counter, defaultdict
import hashlib
from itertools import combinations
import json
from pathlib import Path
import re
import sys
import unicodedata

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.canonicalize_recipes import build as build_phase1, csv_bytes, normalize_name, read_csv, require

OUTPUT = ROOT / "data/processed/recipes/recipe_name_alias_candidates.csv"
REPORT = ROOT / "reports/eda/recipe_name_alias_analysis.md"
# Explicit discovery-only vocabulary, not aliases and not a semantic ontology.
PROTECTED = frozenset("""cá hồi ngừ lóc chép basa diêu hồng gà vịt ngan ngỗng bò bê
heo lợn dê cừu tôm tép cua ghẹ mực ốc nghêu sò hến lươn ếch trứng nấm đậu
chay mặn keto nướng chiên xào hấp luộc kho hầm om rim ram rang quay nấu
trộn sống tái chín mật ong sữa phô mai tỏi gừng sả ớt tiêu chanh dứa thơm
chua ngọt muối mắm tương cà ri""".split())
SUFFIXES = ("nhanh gọn", "đơn giản", "ngon", "dễ làm", "phiên bản nhà làm",
            "phiên bản nhà tôi", "món ăn sáng cho bé")
RULES = ("punctuation_equal", "token_reorder", "parenthetical_base_equal",
         "descriptive_suffix_equal", "single_token_edit")
FIELDS = (
    "recipe_id_a", "recipe_id_b", "original_name_a", "original_name_b",
    "normalized_name_a", "normalized_name_b", "lexical_name_a", "lexical_name_b",
    "source_url_a", "source_url_b", "rules", "generation_reason", "review_status",
    "token_jaccard", "token_containment", "containment_relation",
    "edit_distance", "edit_similarity", "tokens_only_a", "tokens_only_b",
    "removed_parenthetical_a", "removed_parenthetical_b", "removed_suffix_a",
    "removed_suffix_b", "ingredient_count_a", "ingredient_count_b",
    "ingredient_jaccard", "shared_ingredient_names", "ingredient_names_only_a",
    "ingredient_names_only_b", "review_cautions",
)


def lexical(value):
    # Punctuation becomes boundaries; accents and letters are never stripped.
    value = normalize_name(value)
    return " ".join("".join(" " if unicodedata.category(c).startswith("P") else c
                            for c in value).split())


def distance(a, b):
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        for j, cb in enumerate(b, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (ca != cb)))
        previous = current
    return previous[-1]


def features(recipe):
    name = normalize_name(recipe["canonical_dish_name"])
    clean = lexical(name)
    # Only balanced, nonnested parentheses are eligible; all removal is exposed.
    valid_parens = name.count("(") == name.count(")") == len(re.findall(r"\([^()]*\)", name))
    removed = re.findall(r"\(([^()]*)\)", name) if valid_parens else []
    base = lexical(re.sub(r"\([^()]*\)", " ", name)) if removed else clean
    suffix = next((s for s in SUFFIXES if clean.endswith(" " + s)), "") if valid_parens else ""
    return dict(name=name, clean=clean, tokens=clean.split(), base=base,
                removed=removed, suffix=suffix,
                suffix_base=clean[:-(len(suffix) + 1)] if suffix else clean)


def pair_rules(a, b):
    if not a["clean"] or not b["clean"] or a["name"] == b["name"]:
        return []
    ta, tb = Counter(a["tokens"]), Counter(b["tokens"])
    # Prevent known ingredient/method/diet substitutions or additions.
    if (set(ta) & PROTECTED) != (set(tb) & PROTECTED):
        return []
    rules = []
    if a["clean"] == b["clean"]:
        rules.append("punctuation_equal")
    if ta == tb and a["clean"] != b["clean"]:
        rules.append("token_reorder")
    if (a["removed"] or b["removed"]) and a["base"] == b["base"] and len(a["base"].split()) >= 2:
        rules.append("parenthetical_base_equal")
    if (a["suffix"] or b["suffix"]) and a["suffix_base"] == b["suffix_base"] and len(a["suffix_base"].split()) >= 2:
        rules.append("descriptive_suffix_equal")
    only_a, only_b = list((ta - tb).elements()), list((tb - ta).elements())
    if len(only_a) == len(only_b) == 1 and len(a["tokens"]) == len(b["tokens"]) >= 4:
        x, y = only_a[0], only_b[0]
        union = set(ta) | set(tb)
        # No token insertion/deletion containment, no short-word or accent-only edits.
        bare = lambda s: "".join(c for c in unicodedata.normalize("NFD", s) if not unicodedata.combining(c))
        if (min(len(x), len(y)) >= 4 and bare(x) != bare(y)
                and len(set(ta) & set(tb)) / len(union) >= 0.60
                and distance(x, y) == 1
                and 1 - distance(a["clean"], b["clean"]) / max(len(a["clean"]), len(b["clean"])) >= 0.90):
            rules.append("single_token_edit")
    return rules


def build(recipes, ingredients):
    recipes = sorted(recipes, key=lambda r: r["id"])
    ids = {r["id"] for r in recipes}
    require(len(ids) == len(recipes) and "" not in ids, "Invalid canonical IDs")
    names = [normalize_name(r["canonical_dish_name"]) for r in recipes]
    require(len(set(names)) == len(names) and all(names), "Invalid canonical names")
    require(all(i["recipe_id"] in ids for i in ingredients), "Orphan canonical ingredient")
    data = [features(r) for r in recipes]
    buckets = defaultdict(set)
    for index, f in enumerate(data):
        for kind, key in (("punct", f["clean"]), ("tokens", tuple(sorted(f["tokens"]))),
                          ("paren", f["base"]), ("suffix", f["suffix_base"])):
            if key:
                buckets[(kind, key)].add(index)
        if len(f["tokens"]) >= 4:
            for position in range(len(f["tokens"])):
                buckets[("drop_one", tuple(sorted(f["tokens"][:position] + f["tokens"][position + 1:])))].add(index)
    pairs = set()
    for members in buckets.values():
        pairs.update(combinations(sorted(members), 2))
    ingredient_sets = defaultdict(set)
    for ingredient in ingredients:
        name = normalize_name(ingredient["cleaned_name"])
        if name:
            ingredient_sets[ingredient["recipe_id"]].add(name)
    rows = []
    for ia, ib in sorted(pairs):
        a, b = data[ia], data[ib]
        rules = pair_rules(a, b)
        if not rules:
            continue
        ra, rb = recipes[ia], recipes[ib]
        ta, tb = set(a["tokens"]), set(b["tokens"])
        ga, gb = ingredient_sets[ra["id"]], ingredient_sets[rb["id"]]
        union = ga | gb
        ingredient_score = len(ga & gb) / len(union) if union else None
        edit = distance(a["clean"], b["clean"])
        cautions = []
        if "parenthetical_base_equal" in rules:
            cautions.append("parenthetical wording may specify a meaningful variant")
        if "descriptive_suffix_equal" in rules:
            cautions.append("suffix may encode audience or preparation differences")
        if "token_reorder" in rules:
            cautions.append("word order can change ingredient roles")
        if "single_token_edit" in rules:
            cautions.append("changed word may be a different ingredient, not a typo")
        if ingredient_score is None:
            cautions.append("ingredient evidence unavailable")
        elif ingredient_score < 0.25:
            cautions.append("low ingredient-name overlap (<0.25); inspect source recipes")
        relation = "equal_token_sets" if ta == tb else "a_tokens_contained_in_b" if ta < tb else "b_tokens_contained_in_a" if tb < ta else "neither"
        row = dict(recipe_id_a=ra["id"], recipe_id_b=rb["id"], original_name_a=ra["name"], original_name_b=rb["name"],
                   normalized_name_a=a["name"], normalized_name_b=b["name"], lexical_name_a=a["clean"], lexical_name_b=b["clean"],
                   source_url_a=ra["source_url"], source_url_b=rb["source_url"], rules=";".join(rules),
                   generation_reason="; ".join(rules), review_status="unreviewed_candidate_only",
                   token_jaccard=f"{len(ta & tb) / len(ta | tb):.6f}",
                   token_containment=f"{len(ta & tb) / min(len(ta), len(tb)):.6f}", containment_relation=relation,
                   edit_distance=edit, edit_similarity=f"{1 - edit / max(len(a['clean']), len(b['clean'])):.6f}",
                   tokens_only_a=sorted(ta - tb), tokens_only_b=sorted(tb - ta),
                   removed_parenthetical_a=a["removed"], removed_parenthetical_b=b["removed"],
                   removed_suffix_a=a["suffix"], removed_suffix_b=b["suffix"],
                   ingredient_count_a=len(ga), ingredient_count_b=len(gb),
                   ingredient_jaccard="" if ingredient_score is None else f"{ingredient_score:.6f}",
                   shared_ingredient_names=sorted(ga & gb), ingredient_names_only_a=sorted(ga - gb),
                   ingredient_names_only_b=sorted(gb - ga), review_cautions="; ".join(cautions))
        rows.append({k: json.dumps(v, ensure_ascii=False) if isinstance(v, list) else v for k, v in row.items()})
    return rows


def protected_hashes():
    # All dataset files except this analysis CSV, including all Phase 1 artifacts.
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((ROOT / "data").rglob("*")) if p.is_file() and p != OUTPUT}


def report(rows, count, hashes):
    rule_counts = Counter(rule for row in rows for rule in row["rules"].split(";"))
    lines = ["# Recipe-name alias candidate analysis", "", "## Scope and reproduction", "",
             "This is the lexical discovery snapshot, not the reviewed decision layer. Candidate rows retain their original unreviewed status; subsequent business decisions are in recipe_name_alias_decisions.json and their application is in recipe_name_alias_application_audit.csv.",
             "Discovery reconstructs Phase 1 in memory so reviewed alias application does not change its 5,510-name input. Discovery does not modify canonical outputs or protected source data.", "",
             "```powershell", "python scripts/eda/recipe_name_alias_analysis.py",
             "python scripts/eda/recipe_name_alias_analysis.py --check",
             "python -m unittest discover -s tests -p test_recipe_name_alias_analysis.py -v", "```", "",
             "## Rules and safeguards", "",
             "Names retain Phase 1 NFC/lowercase/whitespace normalization. Unicode punctuation becomes spaces only in analysis keys; accents remain.",
             "Pairs must have different Phase 1 normalized names. Deterministic blocking uses equal normalized keys or equal token multisets after deleting one token.", "",
             "- punctuation_equal: identical punctuation-normalized strings.",
             "- token_reorder: identical token multisets, different order; no token is discarded.",
             "- parenthetical_base_equal: exact base equality after removing balanced nonnested parentheses, at least two base tokens. Removed wording is exposed.",
             "- descriptive_suffix_equal: exact base equality after removing one explicitly listed trailing phrase, at least two base tokens.",
             "- single_token_edit: equal token counts of at least four, exactly one differing token per side; both differing tokens have at least four characters, Levenshtein distance exactly one, token Jaccard >=0.60 and whole-name edit similarity >=0.90. Accent-only differences are excluded.", "",
             "Suffix list: " + ", ".join(SUFFIXES) + ".", "",
             "All rules reject pairs whose protected ingredient/method/diet token sets differ. Protected tokens: " + ", ".join(sorted(PROTECTED)) + ".", "",
             "This finite vocabulary is a conservative screen, not complete semantic detection. Broad containment alone is never a rule. Thus 'canh chua cá' / 'canh chua cá hồi' and 'gà nướng' / 'gà nướng mật ong' are excluded. No abbreviation expansion, ingredient aliases, LLM identity decisions, accent stripping or transitive grouping is used.", "",
             "## Counts and distributions", "", f"Canonical names analyzed: **{count:,}**.",
             f"Unique candidate pairs: **{len(rows)}**. Output contains pairs only, not inferred equivalence groups.",
             f"Distinct recipe IDs involved: **{len({r[k] for r in rows for k in ('recipe_id_a', 'recipe_id_b')})}**.", "",
             "Rule counts overlap when one pair satisfies several rules:", "", "| Rule | Pairs |", "| --- | ---: |"]
    lines.extend(f"| {rule} | {rule_counts[rule]} |" for rule in RULES)
    lines += ["", "Scores are descriptive lexical evidence, not confidence probabilities. Jaccard uses sets; edit similarity is 1 - Levenshtein/max character length, on punctuation-normalized strings. Containment is shared token count divided by smaller set size. Ingredient overlap uses safely normalized cleaned names; blank evidence stays missing.", "",
              "| Metric | Min | Median | Max | <0.5 | 0.5–<0.8 | 0.8–<0.9 | 0.9–1 |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for metric in ("token_jaccard", "edit_similarity", "ingredient_jaccard"):
        values = sorted(float(r[metric]) for r in rows if r[metric] != "")
        if values:
            median = (values[(len(values)-1)//2] + values[len(values)//2]) / 2
            bins = [sum(lo <= v < hi for v in values) for lo, hi in ((0, .5), (.5, .8), (.8, .9), (.9, 1.000001))]
            lines.append(f"| {metric} | {values[0]:.3f} | {median:.3f} | {values[-1]:.3f} | " + " | ".join(map(str, bins)) + " |")
    def examples(items):
        return [f"- **{r['original_name_a']}** / **{r['original_name_b']}** — {r['rules']}; token={r['token_jaccard']}, edit={r['edit_similarity']}, ingredient={r['ingredient_jaccard'] or 'missing'}. IDs: `{r['recipe_id_a']}` / `{r['recipe_id_b']}`. {r['review_cautions']}" for r in items]
    lines += ["", "## Strongest-looking lexical candidates (not confirmed)", ""]
    lines += examples(sorted(rows, key=lambda r: (-float(r["token_jaccard"]), -float(r["edit_similarity"]), r["recipe_id_a"], r["recipe_id_b"]))[:6])
    lines += ["", "## False-positive-looking / caution examples (not rejected)", "",
              "A specific role-ambiguity example is 'Mì trứng tôm thịt heo' / 'Mì tôm Trứng Thịt heo': 'mì trứng' and 'mì tôm' can describe different noodle types, despite identical token multisets. This pair needs source review; it is not classified as equivalent or different.", ""]
    lines += examples(sorted((r for r in rows if r["review_cautions"]), key=lambda r: (float(r["ingredient_jaccard"] or "-1"), r["recipe_id_a"], r["recipe_id_b"]))[:6])
    lines += ["", "## Limitations and validation", "",
              "High token similarity can hide meaningful differences; even punctuation or word order can affect interpretation. Parentheticals may specify regional, dietary or preparation variants. Low ingredient overlap is a review cue, not proof of distinct identity: source recipes and cleaned names vary. Vocabulary guards miss unknown ingredients and methods and can suppress real synonyms. Short typos, abbreviations, regional synonyms, larger reorderings with changed words, and unlisted suffixes are intentionally missed. No precision/recall claim is made without labeled review.", "",
              "Generation checks unique canonical IDs/names and ingredient references, compares full CSV bytes after reversing both inputs, reads back outputs, and checks SHA-256 for all other data files before and after writing. --check compares the report and CSV against disk. No canonical pipeline or consumer is changed.", "",
              "Validation on this dataset: seven focused Phase 2 unittest tests and eleven Phase 1 tests passed. The discovery --check and Phase 1 canonicalization --check passed. Tests cover unsafe containment, cooking/ingredient changes, accent preservation, malformed parentheses, tight edits, evidence, input permutation and input immutability.", "",
              f"Protected dataset files checked: {len(hashes)}. SHA-256 of the sorted path/hash manifest (excludes only the candidate CSV): `{hashlib.sha256(json.dumps(hashes, sort_keys=True).encode('utf-8')).hexdigest()}`.", ""]
    return "\n".join(lines).encode("utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    before = protected_hashes()
    phase1, _ = build_phase1(
        read_csv(ROOT / "data/interim/recipes_crawled_cleaned.csv"),
        read_csv(ROOT / "data/interim/recipe_ingredients.csv"),
        read_csv(ROOT / "data/processed/viendinhduong/master_ingredients_nutrition.csv"))
    recipes = phase1["canonical_recipes.csv"]
    ingredients = phase1["canonical_recipe_ingredients.csv"]
    rows = build(recipes, ingredients)
    content = csv_bytes(rows, FIELDS)
    require(content == csv_bytes(build(recipes[::-1], ingredients[::-1]), FIELDS), "Nondeterministic candidates")
    artifacts = {OUTPUT: content, REPORT: report(rows, len(recipes), before)}
    require(before == protected_hashes(), "Protected data changed before writing")
    for path, value in artifacts.items():
        if args.check:
            require(path.exists() and path.read_bytes() == value, "Artifact mismatch: " + path.name)
        else:
            path.write_bytes(value)
            require(path.read_bytes() == value, "Readback mismatch: " + path.name)
    require(before == protected_hashes(), "Protected data changed")
    counts = Counter(rule for r in rows for rule in r["rules"].split(";"))
    print(json.dumps({"names_analyzed": len(recipes), "candidate_pairs": len(rows),
                      "rule_counts": {rule: counts[rule] for rule in RULES},
                      "validation": "passed: references, deterministic bytes, protected data hashes, artifact readback"}, indent=2))


if __name__ == "__main__":
    main()
