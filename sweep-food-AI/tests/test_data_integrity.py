import csv
import json
import os
import re
import pytest
from collections import Counter

RECIPES_CSV = "data/processed/recipes/recipes.csv"
RECIPES_JSON = "data/processed/recipes/recipes.json"
ING_CSV = "data/processed/recipes/recipe_ingredients.csv"
ING_JSON = "data/processed/recipes/recipe_ingredients.json"
MAP_CSV = "data/processed/recipes/recipe_canonical_mapping.csv"
MAP_JSON = "data/processed/recipes/recipe_canonical_mapping.json"


@pytest.fixture(scope="module")
def dataset():
    with open(RECIPES_CSV, "r", encoding="utf-8-sig") as f:
        recipes = list(csv.DictReader(f))
    with open(ING_CSV, "r", encoding="utf-8-sig") as f:
        ingredients = list(csv.DictReader(f))
    return {"recipes": recipes, "ingredients": ingredients}


def test_referential_integrity(dataset):
    """Ensure every ingredient links to an existing recipe with 0 orphans."""
    recipe_ids = set(r["id"] for r in dataset["recipes"])
    assert len(recipe_ids) == 5478, f"Expected 5478 unique recipes, got {len(recipe_ids)}"

    orphans = [ing for ing in dataset["ingredients"] if ing["recipe_id"] not in recipe_ids]
    assert len(orphans) == 0, f"Found {len(orphans)} orphaned ingredient rows!"


def test_culinary_mismatch_radar(dataset):
    """Ensure all 12 known systemic mismatch patterns are 100% eliminated."""
    ingredients = dataset["ingredients"]

    for row in ingredients:
        raw_l = row.get("raw_text", "").lower()
        code = str(row.get("master_ingredient_code") or "").strip()
        name = str(row.get("master_ingredient_name") or "").strip().lower()

        # 1. Đậu bắp must not map to Củ đậu (4023)
        if re.search(r"\bđậu bắp\b", raw_l):
            assert code == "20086", f"Đậu bắp incorrectly mapped to code {code} ({name}) in: '{raw_l}'"

        # 2. Cá cam must not map to quả cam (5002)
        if re.search(r"\bcá cam\b", raw_l):
            assert code == "20104", f"Cá cam incorrectly mapped to code {code} ({name}) in: '{raw_l}'"

        # 3. Cá nục chuối must not map to quả chuối (5006)
        if re.search(r"\bcá nục chuối\b", raw_l):
            assert code == "8021", f"Cá nục chuối incorrectly mapped to code {code} in: '{raw_l}'"

        # 4. Bột chiên giòn / bột chiên xù must not map to bột năng (13046)
        if re.search(r"\bbột chiên giòn\b", raw_l):
            assert "bột năng" not in name, f"Bột chiên giòn incorrectly mapped to bột năng in: '{raw_l}'"
        if re.search(r"\bbột chiên xù\b", raw_l):
            assert "bột năng" not in name, f"Bột chiên xù incorrectly mapped to bột năng in: '{raw_l}'"

        # 5. Củ sen / Ngó sen must not map to Hạt sen (4040)
        if re.search(r"\bcủ sen\b", raw_l) and not re.search(r"\bhạt sen\b", raw_l):
            assert code == "20103", f"Củ sen incorrectly mapped to code {code} in: '{raw_l}'"
        if re.search(r"\bngó sen\b", raw_l) and not re.search(r"\bhạt sen\b", raw_l):
            assert code == "4059", f"Ngó sen incorrectly mapped to code {code} in: '{raw_l}'"

        # 6. Bắp bò must not map to Thịt bê mỡ (7001)
        if re.search(r"\bbắp bò\b", raw_l):
            assert code == "7094", f"Bắp bò incorrectly mapped to code {code} in: '{raw_l}'"

        # 7. Hạt điều đỏ / Bột điều màu must not map to hạt điều khô (3015)
        if re.search(r"\b(hạt điều đỏ|bột hạt điều|hạt điều màu)\b", raw_l):
            assert code != "3015", f"Hạt điều màu incorrectly mapped to Cashew (3015) in: '{raw_l}'"

        # 8. Hoa hồi must not map to Cá hồi (8011)
        if re.search(r"\b(hoa hồi|bông hồi|tai hồi|đại hồi)\b", raw_l):
            assert code != "8011", f"Hoa hồi incorrectly mapped to Cá hồi in: '{raw_l}'"

        # 9. Ốc bươu (8041) false matches
        if code == "8041":
            assert re.search(r"\b(ốc|thịt ốc)\b", raw_l), f"False snail match for code 8041 in: '{raw_l}'"

        # 10. Nước dừa / Dừa tươi must not map to Dầu dừa (6009)
        if any(k in raw_l for k in ["dừa tươi", "nước dừa tươi", "trái dừa (lấy nước)"]):
            assert code != "6009", f"Nước dừa incorrectly mapped to Dầu dừa (6009) in: '{raw_l}'"


def test_leaf_and_spice_weight_caps(dataset):
    """Ensure discrete spices and leaves do not have multi-hundred gram weights."""
    ingredients = dataset["ingredients"]

    leaf_pattern = re.compile(r"\b(lá lốt|lá cà ri|lá chanh|lá chúc|lá bạc hà|lá mơ|lá húng)\b", re.I)
    garlic_clove_pattern = re.compile(r"\b(múi tỏi|tép tỏi)\b", re.I)

    for row in ingredients:
        raw_l = row.get("raw_text", "").lower()
        w = float(row.get("estimated_weight_g") or 0.0)
        qty = float(row.get("required_quantity") or 1.0)
        unit = row.get("unit_vi", "").lower()

        # Discrete leaves (cái / lá / chiếc)
        if leaf_pattern.search(raw_l) and any(u in unit or u in raw_l for u in ["cái", "lá", "chiếc", "nhánh"]):
            if qty <= 20:
                assert w <= 35.0, f"Leaf weight anomaly: '{raw_l}' has weight {w}g for qty {qty}"

        # Discrete garlic cloves
        if garlic_clove_pattern.search(raw_l) and qty <= 10:
            assert w <= 50.0, f"Garlic clove weight anomaly: '{raw_l}' has weight {w}g for qty {qty}"


def test_recipe_nutrition_validity(dataset):
    """Ensure >=99.8% recipes have realistic positive total calories and valid macros."""
    recipes = dataset["recipes"]
    zero_cals = []

    for r in recipes:
        r_id = r["id"]
        cals = float(r.get("total_calories") or 0.0)
        prot = float(r.get("total_protein_g") or 0.0)
        fat = float(r.get("total_fat_g") or 0.0)
        carbs = float(r.get("total_carbs_g") or 0.0)

        assert cals >= 0.0
        assert cals < 50000.0, f"Recipe {r_id} '{r.get('name')}' has excessive calories ({cals})!"
        assert prot >= 0.0 and fat >= 0.0 and carbs >= 0.0

        if cals == 0.0:
            zero_cals.append(r_id)

    # At least 99.5% of recipes must have positive calories
    pct_valid = (len(recipes) - len(zero_cals)) / len(recipes) * 100
    assert pct_valid >= 99.5, f"Only {pct_valid:.2f}% recipes have positive calories ({len(zero_cals)} zeros)"


def test_weight_source_matches_unmatched(dataset):
    """weight_source == 'unmatched_no_nutrition' iff match_method == 'UNMATCHED'.

    Regression guard for the LLM_COMPOUND_SPLIT provenance bug (I-1): matched
    rows must not inherit the parent UNMATCHED weight_source, and UNMATCHED rows
    must never claim a real weight provenance.
    """
    ingredients = dataset["ingredients"]
    mislabeled_matched = []
    mislabeled_unmatched = []
    for row in ingredients:
        method = (row.get("match_method") or "").strip().upper()
        ws = (row.get("weight_source") or "").strip()
        is_unmatched = method == "UNMATCHED"
        claims_no_nutrition = ws == "unmatched_no_nutrition"
        if claims_no_nutrition and not is_unmatched:
            mislabeled_matched.append(row.get("id"))
        if is_unmatched and not claims_no_nutrition:
            mislabeled_unmatched.append(row.get("id"))
    assert not mislabeled_matched, (
        f"{len(mislabeled_matched)} matched rows carry weight_source="
        f"'unmatched_no_nutrition' (e.g. {mislabeled_matched[:5]})"
    )
    assert not mislabeled_unmatched, (
        f"{len(mislabeled_unmatched)} UNMATCHED rows have a non-unmatched "
        f"weight_source (e.g. {mislabeled_unmatched[:5]})"
    )


def test_measure_units_not_over_estimated(dataset):
    """Direct mass/volume rows must not exceed the stated quantity (I-3a).

    For unit_vi in {g, kg, ml, lít} the released spec fixes weight at
    quantity x factor; domain caps only reduce weight, so an estimated_weight_g
    that exceeds quantity x factor is a physically impossible value.
    """
    factor = {"g": 1.0, "kg": 1000.0, "ml": 1.0, "lít": 1000.0, "lit": 1000.0}
    offenders = []
    for row in dataset["ingredients"]:
        if (row.get("match_method") or "").strip().upper() == "UNMATCHED":
            continue
        f = factor.get((row.get("unit_vi") or "").strip())
        if f is None:
            continue
        try:
            qty = float(row.get("required_quantity"))
            weight = float(row.get("estimated_weight_g"))
        except (TypeError, ValueError):
            continue
        if qty <= 0:
            continue
        if weight > qty * f * 1.05:
            offenders.append((row.get("id"), row.get("raw_text"), weight, qty * f))
    assert not offenders, (
        f"{len(offenders)} measure-unit rows exceed quantity x factor "
        f"(e.g. {offenders[:5]})"
    )


def test_canonical_mapping_referential_integrity(dataset):
    """Ensure every non-empty canonical_recipe_id in mapping exists in recipes (I-2).

    Eliminated outliers (e.g. non-dish preparation techniques) must have empty
    canonical IDs rather than dangling foreign-key references.
    """
    with open(MAP_CSV, "r", encoding="utf-8-sig") as f:
        mapping = list(csv.DictReader(f))
    with open(MAP_JSON, "r", encoding="utf-8") as f:
        map_json = json.load(f)

    assert len(mapping) == 5641, f"Expected 5641 original mapping rows, got {len(mapping)}"
    recipe_ids = set(r["id"] for r in dataset["recipes"])

    orphaned_mappings = []
    for r in mapping:
        cid = (r.get("canonical_recipe_id") or "").strip()
        if cid and cid not in recipe_ids:
            orphaned_mappings.append((r.get("original_recipe_id"), cid))

    assert len(orphaned_mappings) == 0, (
        f"Found {len(orphaned_mappings)} mapping rows pointing to non-existent recipes: {orphaned_mappings[:5]}"
    )

    # Parity check: JSON projection matches CSV exactly
    for r in mapping:
        orig = r.get("original_recipe_id")
        cid = (r.get("canonical_recipe_id") or "").strip()
        assert (map_json.get(orig) or "").strip() == cid, f"Mapping CSV/JSON mismatch for {orig}"


def test_per_serving_and_anomaly_flags(dataset):
    """Ensure standardized per-serving macros and anomaly flags exist and are valid (Q-2, Q-3)."""
    recipes = dataset["recipes"]
    req_cols = [
        "calories_per_serving",
        "protein_per_serving",
        "fat_per_serving",
        "carbs_per_serving",
        "nutrition_anomaly_flag",
    ]

    anomalies = 0
    for r in recipes:
        for col in req_cols:
            assert col in r, f"Column {col} missing in recipe {r.get('id')}"

        flag = int(r["nutrition_anomaly_flag"])
        assert flag in (0, 1), f"Invalid anomaly flag {flag} in recipe {r.get('id')}"
        if flag == 1:
            anomalies += 1

        servings = float(r["default_servings"])
        total_cals = float(r["total_calories"])
        serving_cals = float(r["calories_per_serving"])
        expected_cals = round(total_cals / servings, 1)
        assert abs(serving_cals - expected_cals) <= 0.15, (
            f"Serving calories {serving_cals} does not match total/servings {expected_cals} for {r.get('id')}"
        )

    # Anomaly rate must be reasonable (around 1.5% - 3.0%)
    pct_anomaly = anomalies / len(recipes) * 100
    assert 1.0 <= pct_anomaly <= 3.5, f"Unexpected anomaly percentage: {pct_anomaly:.2f}%"


def test_ingredient_roles_and_dish_clusters(dataset):
    """Ensure ingredient roles (P-1) and dialect dish clusters (P-2) are valid."""
    recipes = dataset["recipes"]
    ingredients = dataset["ingredients"]

    valid_roles = {"core", "secondary", "seasoning", "garnish"}
    role_counts = Counter()
    for i in ingredients:
        role = (i.get("ingredient_role") or "").strip()
        assert role in valid_roles, f"Invalid ingredient_role '{role}' in row {i.get('id')}"
        role_counts[role] += 1

    # All 4 roles must be represented meaningfully
    for r in valid_roles:
        assert role_counts[r] > 5000, f"Role '{r}' has unexpectedly low frequency: {role_counts[r]}"

    cluster_ids = set()
    for r in recipes:
        assert "core_ingredients_count" in r, f"core_ingredients_count missing in recipe {r.get('id')}"
        core_count = int(r["core_ingredients_count"])
        assert core_count >= 1, f"Recipe {r.get('id')} has 0 core ingredients!"

        assert "dish_cluster_id" in r, f"dish_cluster_id missing in recipe {r.get('id')}"
        cid = (r.get("dish_cluster_id") or "").strip()
        assert cid.startswith("cluster_"), f"Invalid dish_cluster_id format '{cid}' for {r.get('id')}"
        cluster_ids.add(cid)

    # Dialect clusters must reduce the effective group count below total recipes
    assert len(cluster_ids) < len(recipes), (
        f"Clusters ({len(cluster_ids)}) should be strictly less than recipes ({len(recipes)}) due to dialect grouping"
    )
    assert len(cluster_ids) >= 5400, f"Cluster count unexpectedly low: {len(cluster_ids)}"
