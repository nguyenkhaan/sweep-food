"""Non-destructive recipe canonicalization; see reports/eda/recipe_canonicalization.md."""

import argparse
import csv
import hashlib
import io
import json
import math
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
import unicodedata
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
MACROS = ("calories", "protein_g", "fat_g", "carbs_g")
MASTER_MACROS = ("energy_kcal", "protein_g", "fat_g", "carbs_g")
REVIEW_FIELDS = (
    "original_recipe_id", "original_recipe_name", "canonical_recipe_id",
    "canonical_dish_name", "canonical_group_id", "selected_source_url",
    "selection_score", "selection_reason", "duplicate_group_size",
    "resolution_status", "review_reason", "ingredient_names", "ingredient_evidence",
)
# All components are maximized, in order. Fractions avoid rounded-rate ties.
RANK_FIELDS = (
    "has_ingredients", "ingredient_coverage", "valid_match_rate",
    "negative_unmatched_rate", "negative_fallback_rate",
    "negative_missing_quantity_rate", "negative_nutrition_anomaly_rate",
    "negative_recipe_nutrition_anomalies", "valid_servings", "valid_source_url",
)


def normalize_name(value):
    return " ".join(unicodedata.normalize("NFC", value).lower().split())


def number(value):
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (TypeError, ValueError):
        return None


def positive(value):
    parsed = number(value)
    return parsed is not None and parsed > 0


def nutrition_bad(row, fields=MACROS):
    values = [number(row.get(key)) for key in fields]
    if any(value is None or value < 0 for value in values):
        return True
    calories, protein, fat, carbs = values
    expected = 4 * protein + 9 * fat + 4 * carbs
    return (expected != 0 if calories == 0 else abs(calories - expected) / calories > 0.30)


def valid_url(value):
    try:
        url = urlsplit(value)
        return url.scheme in {"http", "https"} and bool(url.hostname)
    except ValueError:
        return False


def quality(recipe, ingredients, master):
    count = len(ingredients)
    denominator = count or 1
    declared = number(recipe["ingredients_count"])
    named = sum(bool(normalize_name(i["cleaned_name"])) for i in ingredients)
    coverage = Fraction(named, max(count, int(declared or 0), 1))
    unmatched = sum(i["match_method"].strip().upper() == "UNMATCHED" for i in ingredients)
    valid = sum(i["master_ingredient_code"] in master and bool(i["match_method"].strip())
                and i["match_method"].strip().upper() != "UNMATCHED" for i in ingredients)
    missing = sum(not positive(i["required_quantity"]) for i in ingredients)
    fallback = sum(not positive(i["required_quantity"]) and number(i["estimated_weight_g"]) == 10
                   for i in ingredients)
    anomaly = 0
    for ingredient in ingredients:
        master_row = master.get(ingredient["master_ingredient_code"])
        weight = number(ingredient["estimated_weight_g"])
        masses = [number(ingredient[key]) for key in MACROS[1:]]
        impossible_mass = (weight is not None and all(x is not None for x in masses)
                           and sum(masses) > weight + 0.1)
        anomaly += bool(nutrition_bad(ingredient) or not positive(weight) or impossible_mass
                        or master_row is None or nutrition_bad(master_row, MASTER_MACROS))
    recipe_anomalies = int(nutrition_bad(recipe, tuple("total_" + k for k in MACROS)))
    for key in MACROS:
        values = [number(i[key]) for i in ingredients]
        total = number(recipe["total_" + key])
        # Totals are published to one decimal: allow accumulated rounding.
        recipe_anomalies += int(total is None or any(v is None for v in values)
                                or abs(total - math.fsum(v for v in values if v is not None)) > 0.1 * max(count, 1))
    rank = (int(count > 0), coverage, Fraction(valid, denominator),
            -Fraction(unmatched, denominator), -Fraction(fallback, denominator),
            -Fraction(missing, denominator), -Fraction(anomaly, denominator),
            -recipe_anomalies, int(positive(recipe["default_servings"])),
            int(valid_url(recipe["source_url"])))
    audit = {
        "ingredient_row_count": count, "named_ingredient_count": named,
        "declared_ingredient_count": recipe["ingredients_count"],
        "valid_master_match_count": valid, "unmatched_count": unmatched,
        "missing_required_quantity_count": missing, "fallback_10g_count": fallback,
        "weight_10g_count": sum(number(i["estimated_weight_g"]) == 10 for i in ingredients),
        "nutrition_anomaly_count": anomaly,
        "unmatched_with_code_count": sum(i["match_method"].strip().upper() == "UNMATCHED"
                                         and bool(i["master_ingredient_code"]) for i in ingredients),
        "qwen_match_count": sum(i["match_method"] == "QWEN_LLM_MATCH" for i in ingredients),
        **dict(zip(RANK_FIELDS, map(str, rank))),
    }
    return rank, audit


def require(condition, message):
    if not condition:
        raise ValueError(message)


def build(recipes, ingredients, masters, alias_groups=None):
    ids = [r["id"] for r in recipes]
    require(all(ids) and len(ids) == len(set(ids)), "Missing or duplicate source recipe IDs")
    ingredient_ids = [i["id"] for i in ingredients]
    require(all(ingredient_ids) and len(ingredient_ids) == len(set(ingredient_ids)),
            "Missing or duplicate source ingredient IDs")
    source_by_id = {r["id"]: r for r in recipes}
    require(all(i["recipe_id"] in source_by_id for i in ingredients), "Orphan source ingredient")
    master = {m["code"]: m for m in masters}
    require(len(master) == len(masters) and "" not in master, "Invalid master IDs")
    by_recipe, groups = defaultdict(list), defaultdict(list)
    for ingredient in ingredients:
        by_recipe[ingredient["recipe_id"]].append(ingredient)
    for recipe in recipes:
        name = normalize_name(recipe["name"])
        # Blank names never collapse together; namespace cannot collide with a name.
        key = (alias_groups or {}).get(name, ("name", name)) if name else ("unnamed", recipe["id"])
        groups[key].append(recipe)
    scores = {r["id"]: quality(r, by_recipe[r["id"]], master) for r in recipes}
    canonical, mapping, reviews = [], [], []
    duplicate_groups = involved = manual = 0
    for group_key, candidates in sorted(groups.items()):
        candidates = sorted(candidates, key=lambda r: r["id"])
        candidates.sort(key=lambda r: scores[r["id"]][0], reverse=True)
        winner = candidates[0]
        winner_id = winner["id"]
        name = normalize_name(winner["name"])
        # Lead-approved policy: a nonempty normalized name confirms dish identity.
        # Ingredient composition affects quality, never membership or confirmation.
        review = not name
        if len(candidates) > 1:
            duplicate_groups += 1
            involved += len(candidates)
            manual += int(review)
        reason = "singleton retained"
        if len(candidates) > 1:
            runner = scores[candidates[1]["id"]][0]
            decisive = next((field for field, a, b in zip(RANK_FIELDS, scores[winner_id][0], runner)
                             if a != b), "recipe_id ascending tie-break")
            reason = "best lexicographic quality; decisive versus runner-up: " + decisive
        status = "provisional_review" if review else "automatic"
        if review:
            reason += "; missing normalized name; isolated by source ID pending review"
        shared = {"canonical_recipe_id": winner_id, "canonical_dish_name": name,
                  "canonical_group_id": json.dumps(group_key, ensure_ascii=False),
                  "selected_source_url": winner["source_url"],
                  "selection_score": json.dumps(list(map(str, scores[winner_id][0]))),
                  "selection_reason": reason, "duplicate_group_size": len(candidates),
                  "resolution_status": status}
        canonical.append({**winner, **shared})
        for position, candidate in enumerate(candidates, 1):
            candidate_id = candidate["id"]
            mapping.append({"original_recipe_id": candidate_id, "original_recipe_name": candidate["name"],
                            "original_source_url": candidate["source_url"], **shared,
                            "candidate_rank": position,
                            "candidate_score": json.dumps(list(map(str, scores[candidate_id][0]))),
                            **scores[candidate_id][1]})
            if review:
                reviews.append({"original_recipe_id": candidate_id, "original_recipe_name": candidate["name"],
                                **shared, "review_reason": "missing normalized name prevents name-based grouping",
                                "ingredient_names": json.dumps(sorted({normalize_name(i["cleaned_name"])
                                    for i in by_recipe[candidate_id] if normalize_name(i["cleaned_name"])}), ensure_ascii=False),
                                "ingredient_evidence": json.dumps([
                                    {k: i[k] for k in ("id", "raw_text", "cleaned_name", "master_ingredient_code", "match_method")}
                                    for i in sorted(by_recipe[candidate_id], key=lambda i: i["id"])], ensure_ascii=False)})
    selected = {r["id"]: r for r in canonical}
    canonical_ingredients = [{**i, "canonical_recipe_id": i["recipe_id"],
                             "canonical_dish_name": selected[i["recipe_id"]]["canonical_dish_name"]}
                            for i in ingredients if i["recipe_id"] in selected]
    require(len(selected) == len(canonical) == len(groups), "Canonical uniqueness failed")
    require(len({r["canonical_group_id"] for r in canonical}) == len(groups), "Group uniqueness failed")
    require(set(selected) <= set(ids), "Invalid selected recipe")
    require(Counter(m["original_recipe_id"] for m in mapping) == Counter(ids), "Mapping coverage failed")
    require(all(m["canonical_recipe_id"] in selected for m in mapping), "Invalid mapping target")
    targets = defaultdict(set)
    for m in mapping:
        targets[m["canonical_group_id"]].add(m["canonical_recipe_id"])
    require(all(len(t) == 1 for t in targets.values()), "Multiple selections per group")
    require(all(m["original_recipe_id"] == m["canonical_recipe_id"] for m in mapping
                if m["duplicate_group_size"] == 1), "Singleton lost")
    for row in canonical:
        require(all(row[k] == value for k, value in source_by_id[row["id"]].items()),
                "Source recipe values changed")
    original_selected = sorted([i for i in ingredients if i["recipe_id"] in selected], key=lambda i: i["id"])
    require([{k: i[k] for k in original_selected[0]} for i in sorted(canonical_ingredients, key=lambda i: i["id"])]
            == original_selected if original_selected else not canonical_ingredients, "Ingredient preservation failed")
    summary = {"original_recipes": len(recipes), "duplicate_candidate_groups": duplicate_groups,
               "recipes_in_duplicate_groups": involved, "canonical_recipes": len(canonical),
               "automatically_resolved_duplicate_groups": duplicate_groups - manual,
               "manual_review_duplicate_groups": manual,
               "total_review_groups": len({r["canonical_group_id"] for r in reviews}),
               "canonical_ingredient_rows": len(canonical_ingredients)}
    outputs = {"canonical_recipes.csv": sorted(canonical, key=lambda r: r["id"]),
               "canonical_recipe_ingredients.csv": sorted(canonical_ingredients, key=lambda r: (r["recipe_id"], r["id"])),
               "recipe_canonical_mapping.csv": sorted(mapping, key=lambda r: r["original_recipe_id"]),
               "recipe_canonical_review.csv": sorted(reviews, key=lambda r: r["original_recipe_id"])}
    return outputs, summary


def resolve_reviewed_id(original_id, expected_normalized_name, phase1_mapping, source_by_id, representatives):
    """Resolve a decision's originally-reviewed recipe id to its CURRENT Phase-1 representative.

    The reviewed decision keeps the exact recipe id a human looked at, forever;
    only this *resolution* (which physical duplicate presently represents that
    recipe's group) is allowed to drift when a processed-data correction shifts
    an intra-group quality tie-break. Every failure mode fails loudly instead of
    silently reinterpreting a stale, unrelated or ambiguous id.
    """
    require(original_id in source_by_id,
            f"Reviewed recipe id no longer exists in source data: {original_id!r}")
    require(original_id in phase1_mapping,
            f"Reviewed recipe id missing from Phase-1 mapping: {original_id!r}")
    current_name = normalize_name(source_by_id[original_id]["name"])
    require(current_name == expected_normalized_name,
            f"Reviewed recipe {original_id!r} changed normalized dish identity: "
            f"decision recorded {expected_normalized_name!r}, source name now normalizes to {current_name!r}")
    entry = phase1_mapping[original_id]
    require(entry["canonical_dish_name"] == expected_normalized_name,
            f"Reviewed recipe {original_id!r} now groups under a different dish identity "
            f"(cross-group movement): decision recorded {expected_normalized_name!r}, "
            f"current Phase-1 group is {entry['canonical_dish_name']!r}")
    resolved = entry["canonical_recipe_id"]
    require(resolved in representatives,
            f"Reviewed recipe {original_id!r} resolved to {resolved!r}, which is not a Phase-1 representative")
    require(representatives[resolved]["canonical_group_id"] == entry["canonical_group_id"],
            f"Reviewed recipe {original_id!r} resolved to a representative "
            f"({resolved!r}) outside its own duplicate group; refusing ambiguous resolution")
    return resolved


def compose_reviewed_aliases(recipes, ingredients, masters, decisions):
    """Rebuild Phase 1, then union only explicitly approved relationships.

    Reviewed decisions record the exact ids a human compared; they are never
    rewritten here. When corrected processed data changes which duplicate wins
    a group, each reviewed id is resolved to its current representative at
    read time (see resolve_reviewed_id), so historical review provenance stays
    truthful while canonicalization still tolerates representative drift.
    """
    phase1, phase1_summary = build(recipes, ingredients, masters)
    representatives = {r["id"]: r for r in phase1["canonical_recipes.csv"]}
    phase1_mapping = {r["original_recipe_id"]: r for r in phase1["recipe_canonical_mapping.csv"]}
    source_by_id = {r["id"]: r for r in recipes}
    parent = {identifier: identifier for identifier in representatives}

    def find(identifier):
        while parent[identifier] != identifier:
            identifier = parent[identifier]
        return identifier

    seen = set()
    resolved_pairs = {}
    for decision in decisions:
        a, b = decision["recipe_id_a"], decision["recipe_id_b"]
        require(a != b, "Invalid reviewed endpoints: identical recipe ids")
        pair = tuple(sorted((a, b)))
        require(pair not in seen, "Duplicate reviewed relationship")
        seen.add(pair)
        require(decision["decision"] in {"approved", "rejected"} and decision["reason"].strip(),
                "Invalid review decision or missing reason")
        resolved_a = resolve_reviewed_id(a, decision["normalized_name_a"], phase1_mapping, source_by_id, representatives)
        resolved_b = resolve_reviewed_id(b, decision["normalized_name_b"], phase1_mapping, source_by_id, representatives)
        resolved_pairs[pair] = (resolved_a, resolved_b)
        if decision["decision"] == "approved":
            ra, rb = sorted((find(resolved_a), find(resolved_b)))
            parent[rb] = ra
    for decision in decisions:
        if decision["decision"] == "rejected":
            pair = tuple(sorted((decision["recipe_id_a"], decision["recipe_id_b"])))
            resolved_a, resolved_b = resolved_pairs[pair]
            require(find(resolved_a) != find(resolved_b),
                    "Rejected pair connected through approved aliases")
    components = defaultdict(list)
    for identifier in sorted(parent):
        components[find(identifier)].append(identifier)
    merged = [members for members in components.values() if len(members) > 1]
    aliases = {}
    for members in merged:
        names = sorted(representatives[i]["canonical_dish_name"] for i in members)
        for name in names:
            aliases[name] = ("reviewed_alias", *names)
    outputs, summary = build(recipes, ingredients, masters, aliases)
    for row in outputs["canonical_recipes.csv"] + outputs["recipe_canonical_mapping.csv"]:
        original = row.get("original_recipe_id", row.get("id"))
        old = phase1_mapping[original]
        row["phase1_canonical_recipe_id"] = old["canonical_recipe_id"]
        row["phase1_canonical_dish_name"] = old["canonical_dish_name"]
        row["canonicalization_phase"] = "reviewed_alias" if old["canonical_dish_name"] in aliases else "same_name"
        if row["canonicalization_phase"] == "reviewed_alias":
            row["resolution_status"] = "reviewed_approved"
            row["selection_reason"] += "; approved reviewed alias component"
    final_mapping = {r["original_recipe_id"]: r["canonical_recipe_id"] for r in outputs["recipe_canonical_mapping.csv"]}
    audit = []
    for decision in sorted(decisions, key=lambda d: (d["recipe_id_a"], d["recipe_id_b"])):
        a, b = decision["recipe_id_a"], decision["recipe_id_b"]
        require((final_mapping[a] == final_mapping[b]) == (decision["decision"] == "approved"),
                "Final mapping violates reviewed decision")
        audit.append({**decision, "final_canonical_recipe_id_a": final_mapping[a],
                      "final_canonical_recipe_id_b": final_mapping[b]})
    require(all(r["id"] in representatives for r in outputs["canonical_recipes.csv"]),
            "Final representative is not a Phase 1 winner")
    outputs["recipe_name_alias_application_audit.csv"] = audit
    summary["automatically_resolved_duplicate_groups"] = sum(
        r["duplicate_group_size"] > 1 and r["resolution_status"] == "automatic"
        for r in outputs["canonical_recipes.csv"])
    summary["reviewed_alias_groups"] = len(merged)
    summary["phase1"] = phase1_summary
    summary["phase2"] = {"canonical_recipes_before": len(representatives),
                          "approved_alias_pairs": sum(d["decision"] == "approved" for d in decisions),
                          "rejected_alias_pairs": sum(d["decision"] == "rejected" for d in decisions),
                          "merged_alias_groups": len(merged),
                          "canonical_dishes_removed": len(representatives) - summary["canonical_recipes"],
                          "transitive_groups": [members for members in merged if len(members) > 2]}
    return outputs, summary


def csv_bytes(rows, fieldnames=None):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames or (list(rows[0]) if rows else ["original_recipe_id", "review_reason"]),
                            lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


def protected_hashes(root):
    paths = set()
    for directory in ("data/raw", "data/interim"):
        paths.update(p for p in (root / directory).rglob("*") if p.is_file())
    paths.update(p for p in (root / "data/processed").rglob("*")
                 if p.is_file() and p.name in {"ingredient_alias_map.json", "master_ingredients_nutrition.csv"})
    paths.update(root / "data/processed/recipes" / name for name in
                 ("recipes.csv", "recipes.json", "recipe_ingredients.csv", "recipe_ingredients.json")
                 if (root / "data/processed/recipes" / name).exists())
    paths.update(root / "data/processed/recipes" / name for name in
                 ("recipe_name_alias_decisions.json", "recipe_name_alias_candidates.csv")
                 if (root / "data/processed/recipes" / name).exists())
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate existing artifacts without writing")
    args = parser.parse_args()
    before = protected_hashes(ROOT)
    recipes = read_csv(ROOT / "data/processed/recipes/recipes.csv")
    ingredients = read_csv(ROOT / "data/processed/recipes/recipe_ingredients.csv")
    masters = read_csv(ROOT / "data/processed/viendinhduong/master_ingredients_nutrition.csv")
    decision_path = ROOT / "data/processed/recipes/recipe_name_alias_decisions.json"
    decision_bytes = decision_path.read_bytes()
    decision_document = json.loads(decision_bytes)
    require(decision_document["policy_version"] == 1, "Unsupported alias policy version")
    decisions = decision_document["relationships"]
    candidates = read_csv(ROOT / "data/processed/recipes/recipe_name_alias_candidates.csv")
    require({tuple(sorted((r["recipe_id_a"], r["recipe_id_b"]))) for r in candidates} ==
            {tuple(sorted((r["recipe_id_a"], r["recipe_id_b"]))) for r in decisions},
            "Reviewed decisions do not cover the candidate snapshot exactly")
    outputs, summary = compose_reviewed_aliases(recipes, ingredients, masters, decisions)
    repeated, repeated_summary = compose_reviewed_aliases(list(reversed(recipes)), list(reversed(ingredients)),
                                                         list(reversed(masters)), list(reversed(decisions)))
    artifacts = {name: csv_bytes(rows, REVIEW_FIELDS if name == "recipe_canonical_review.csv" else None)
                 for name, rows in outputs.items()}
    require(artifacts == {name: csv_bytes(rows, REVIEW_FIELDS if name == "recipe_canonical_review.csv" else None)
                          for name, rows in repeated.items()}
            and summary == repeated_summary, "Determinism failed")
    require(before == protected_hashes(ROOT), "Protected inputs changed during generation")
    summary["validation"] = "passed: unique selections, mapping coverage, references, singleton retention, unchanged source values, input-order-independent bytes, protected hashes"
    summary["protected_sha256"] = before
    summary["reviewed_decisions_sha256"] = hashlib.sha256(decision_bytes).hexdigest()
    summary["output_sha256"] = {name: hashlib.sha256(data).hexdigest() for name, data in artifacts.items()}
    artifacts["recipe_canonicalization_summary.json"] = (json.dumps(summary, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    output_dir = ROOT / "data/processed/recipes"
    for name, content in artifacts.items():
        path = output_dir / name
        if args.check:
            require(path.exists() and path.read_bytes() == content, "Artifact differs: " + name)
        else:
            path.write_bytes(content)
            require(path.read_bytes() == content, "Output read-back failed: " + name)
    require(before == protected_hashes(ROOT), "Protected inputs changed during writing")
    require(decision_path.read_bytes() == decision_bytes, "Reviewed decisions changed during generation")
    print(json.dumps({k: v for k, v in summary.items() if not k.endswith("sha256")}, indent=2))


if __name__ == "__main__":
    main()
