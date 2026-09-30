"""Regression tests for the canonical-data cutover.

These guard the specific defect fixed on fix/canonical-cutover: canonical
recipe/ingredient outputs must be generated from the CURRENT processed
recipe data (not stale interim data), the exported JSON must be an exact
mirror of the generated CSV, and the canonical artifacts on disk must not
be allowed to silently drift stale relative to the processed inputs that
web/app.py's canonical-preference loader depends on.
"""

import csv
import hashlib
import inspect
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent


def load_csv(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def sha256_of(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class CanonicalizationSourceTests(unittest.TestCase):
    """canonicalize_recipes.py must read processed inputs, not preserved interim."""

    def test_main_reads_processed_recipe_and_ingredient_inputs(self):
        import scripts.canonicalize_recipes as mod

        source = inspect.getsource(mod.main)
        self.assertIn('read_csv(ROOT / "data/processed/recipes/recipes.csv")', source)
        self.assertIn('read_csv(ROOT / "data/processed/recipes/recipe_ingredients.csv")', source)
        self.assertNotIn("data/interim/recipes_crawled_cleaned.csv", source)
        self.assertNotIn("data/interim/recipe_ingredients.csv", source)


class CanonicalJsonParityTests(unittest.TestCase):
    """Exported canonical JSON must be an exact mirror of the canonical CSVs."""

    def test_canonical_recipes_json_matches_csv(self):
        csv_rows = load_csv(ROOT_DIR / "data/processed/recipes/canonical_recipes.csv")
        json_rows = load_json(ROOT_DIR / "data/processed/recipes/canonical_recipes.json")
        self.assertEqual(csv_rows, json_rows)
        self.assertGreater(len(json_rows), 0)

    def test_canonical_ingredients_json_matches_csv(self):
        csv_rows = load_csv(ROOT_DIR / "data/processed/recipes/canonical_recipe_ingredients.csv")
        json_rows = load_json(ROOT_DIR / "data/processed/recipes/canonical_recipe_ingredients.json")
        self.assertEqual(csv_rows, json_rows)
        self.assertGreater(len(json_rows), 0)

    def test_canonical_mapping_json_matches_csv(self):
        csv_rows = load_csv(ROOT_DIR / "data/processed/recipes/recipe_canonical_mapping.csv")
        json_map = load_json(ROOT_DIR / "data/processed/recipes/recipe_canonical_mapping.json")
        expected = {r["original_recipe_id"]: r["canonical_recipe_id"] for r in csv_rows}
        self.assertEqual(expected, json_map)


class CanonicalReferentialIntegrityTests(unittest.TestCase):
    """Canonical ingredient/recipe IDs and mapping targets must stay consistent."""

    @classmethod
    def setUpClass(cls):
        cls.recipes = load_csv(ROOT_DIR / "data/processed/recipes/canonical_recipes.csv")
        cls.ingredients = load_csv(ROOT_DIR / "data/processed/recipes/canonical_recipe_ingredients.csv")
        cls.mapping = load_csv(ROOT_DIR / "data/processed/recipes/recipe_canonical_mapping.csv")
        cls.source_recipes = load_csv(ROOT_DIR / "data/processed/recipes/recipes.csv")

    def test_no_orphan_canonical_ingredients(self):
        recipe_ids = {r["id"] for r in self.recipes}
        orphans = [i["id"] for i in self.ingredients if i["recipe_id"] not in recipe_ids]
        self.assertEqual(orphans, [])

    def test_canonical_recipe_ids_are_unique(self):
        ids = [r["id"] for r in self.recipes]
        self.assertEqual(len(ids), len(set(ids)))

    def test_mapping_covers_every_source_recipe_exactly_once(self):
        source_ids = {r["id"] for r in self.source_recipes}
        mapping_ids = {r["original_recipe_id"] for r in self.mapping}
        self.assertEqual(mapping_ids, source_ids)

    def test_mapping_targets_are_valid_canonical_recipes(self):
        recipe_ids = {r["id"] for r in self.recipes}
        targets = {r["canonical_recipe_id"] for r in self.mapping}
        self.assertTrue(targets <= recipe_ids)


class CanonicalFreshnessTests(unittest.TestCase):
    """Canonical artifacts must not silently drift stale relative to processed inputs.

    This is the exact mechanism of the bug fixed here: canonical_recipes.csv /
    canonical_recipe_ingredients.csv were byte-identical to a pre-fix snapshot
    while web/app.py preferred them over the corrected processed JSON. The
    generator already records the processed-input hashes it last consumed in
    recipe_canonicalization_summary.json['protected_sha256']; if those stop
    matching the live processed files, the canonical outputs are stale and
    web/app.py is silently serving outdated data.
    """

    def test_recorded_input_hashes_match_live_processed_files(self):
        summary = load_json(ROOT_DIR / "data/processed/recipes/recipe_canonicalization_summary.json")
        protected = summary["protected_sha256"]
        for rel_path in (
            "data/processed/recipes/recipes.csv",
            "data/processed/recipes/recipe_ingredients.csv",
        ):
            with self.subTest(path=rel_path):
                self.assertEqual(protected[rel_path], sha256_of(ROOT_DIR / rel_path),
                                  f"{rel_path} changed since canonical outputs were last generated; "
                                  "rerun scripts.canonicalize_recipes and scripts.export_canonical_json")

    def test_web_app_canonical_preference_targets_fresh_files(self):
        """web/app.py prefers canonical JSON whenever it exists; that file must be fresh."""
        app_source = (ROOT_DIR / "web/app.py").read_text(encoding="utf-8")
        self.assertIn("CANONICAL_RECIPES_JSON if os.path.exists(CANONICAL_RECIPES_JSON) else RECIPES_JSON",
                      app_source)
        canonical_recipes_json = ROOT_DIR / "data/processed/recipes/canonical_recipes.json"
        self.assertTrue(canonical_recipes_json.exists())
        summary = load_json(ROOT_DIR / "data/processed/recipes/recipe_canonicalization_summary.json")
        self.assertEqual(summary["protected_sha256"]["data/processed/recipes/recipes.csv"],
                          sha256_of(ROOT_DIR / "data/processed/recipes/recipes.csv"))


class CanonicalPropagatesProcessedFixesTests(unittest.TestCase):
    """Corrections already present in processed data must be visible canonically."""

    @classmethod
    def setUpClass(cls):
        cls.ingredients = load_csv(ROOT_DIR / "data/processed/recipes/canonical_recipe_ingredients.csv")

    def test_unmatched_invariant_is_visible_in_canonical_output(self):
        violations = [i["id"] for i in self.ingredients
                      if i.get("match_method", "").strip().upper() == "UNMATCHED"
                      and i.get("master_ingredient_code", "").strip()]
        self.assertEqual(violations, [],
                          "Canonical output does not reflect the processed UNMATCHED invariant fix")

    def test_fixed_alias_targets_are_visible_in_canonical_output(self):
        codes = {i["master_ingredient_code"] for i in self.ingredients}
        # 20070 (Whipping cream) is the corrected target for "kem tuoi" / "kem sua beo";
        # this only proves canonical output was regenerated from the fixed alias map,
        # not that the alias mapping itself is semantically correct (out of scope here).
        self.assertIn("20070", codes)


class CanonicalIdempotencyTests(unittest.TestCase):
    """Regeneration must be deterministic; --check must accept its own output."""

    def test_check_flag_accepts_current_on_disk_artifacts(self):
        result = subprocess.run(
            [sys.executable, "-B", "-m", "scripts.canonicalize_recipes", "--check"],
            cwd=ROOT_DIR, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class KnownRepresentativeFlipsResolveCorrectlyTests(unittest.TestCase):
    """The two representative flips found while fixing the canonical cutover
    must still produce one merged canonical group each, using the ORIGINAL
    (never hand-edited) reviewed decision ids -- proving resolve_reviewed_id
    tolerates the drift without any identity edit to decisions.json /
    recipe_name_alias_candidates.csv.
    """

    KNOWN_GROUPS = (
        # canh cai chua suon non <-> canh suon non cai chua
        ("47d8d0d4-e9ec-4472-93fa-bf86fbe12861", "273507d7-586a-4628-99dc-b6d01c99b114",
         "59084284-f8dd-47e4-8bbc-69a370a6cd50", "77260cee-2908-4850-960e-b684624f9d47"),
        # canh khoai so rau muong <-> canh rau muong khoai so
        ("676e4a43-1ea7-450c-80f9-fa7262ba68e9", "7d31961f-22a2-47cd-ae6e-396b2d2ce360"),
    )

    def test_known_groups_share_a_single_canonical_representative(self):
        mapping = {r["original_recipe_id"]: r["canonical_recipe_id"]
                   for r in load_csv(ROOT_DIR / "data/processed/recipes/recipe_canonical_mapping.csv")}
        for group in self.KNOWN_GROUPS:
            with self.subTest(group=group):
                targets = {mapping[rid] for rid in group}
                self.assertEqual(len(targets), 1, f"Group {group} did not resolve to one representative: {targets}")


class HistoricalReviewProvenanceNotRewrittenTests(unittest.TestCase):
    """Reviewed-decision identity must never be silently rewritten to route
    around a representative drift; only resolve_reviewed_id() may bridge it.
    """

    def test_decisions_file_still_names_the_originally_reviewed_ids(self):
        decisions = load_json(ROOT_DIR / "data/processed/recipes/recipe_name_alias_decisions.json")["relationships"]
        pairs = {(d["recipe_id_a"], d["recipe_id_b"]) for d in decisions}
        self.assertIn(("47d8d0d4-e9ec-4472-93fa-bf86fbe12861", "77260cee-2908-4850-960e-b684624f9d47"), pairs)
        self.assertIn(("676e4a43-1ea7-450c-80f9-fa7262ba68e9", "7d31961f-22a2-47cd-ae6e-396b2d2ce360"), pairs)

    def test_decisions_file_bytes_match_what_generation_actually_read(self):
        summary = load_json(ROOT_DIR / "data/processed/recipes/recipe_canonicalization_summary.json")
        live_hash = sha256_of(ROOT_DIR / "data/processed/recipes/recipe_name_alias_decisions.json")
        self.assertEqual(summary["reviewed_decisions_sha256"], live_hash,
                          "recipe_name_alias_decisions.json differs from the bytes canonicalization last "
                          "read; the reviewed decisions must never be edited by generation")


if __name__ == "__main__":
    unittest.main()
