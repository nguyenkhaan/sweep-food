"""Focused regressions for conservative grouping and quality selection."""
import copy
import csv
import io
import unittest

from scripts.canonicalize_recipes import REVIEW_FIELDS, build, csv_bytes, normalize_name, quality


def recipe(identifier, name="Soup"):
    return dict(id=identifier, name=name, ingredients_count="1", default_servings="2",
                source_url="https://example.org/" + identifier, total_calories="40",
                total_protein_g="10", total_fat_g="0", total_carbs_g="0")


def ingredient(identifier, **changes):
    return dict(dict(id="i" + identifier, recipe_id=identifier, cleaned_name="bean",
                     raw_text="100 g bean", master_ingredient_code="1", match_method="EXACT_CATALOG_MATCH",
                     required_quantity="100", estimated_weight_g="100", calories="40",
                     protein_g="10", fat_g="0", carbs_g="0"), **changes)


MASTER = [dict(code="1", energy_kcal="40", protein_g="10", fat_g="0", carbs_g="0")]


class CanonicalizationTests(unittest.TestCase):
    def test_normalization_preserves_identity_words_accents_and_punctuation(self):
        self.assertEqual(normalize_name("  CA\u0301   Kho  "), "cá kho")
        self.assertNotEqual(normalize_name("cá kho"), normalize_name("ca kho"))
        self.assertNotEqual(normalize_name("soup vegan"), normalize_name("soup"))
        self.assertNotEqual(normalize_name("a-b"), normalize_name("a b"))

    def test_quality_beats_id_and_unmatched_with_code_is_not_valid(self):
        rows = [recipe("a"), recipe("z")]
        ingredients = [ingredient("a", match_method="UNMATCHED"), ingredient("z")]
        original = copy.deepcopy((rows, ingredients, MASTER))
        outputs, summary = build(rows, ingredients, MASTER)
        self.assertEqual(outputs["canonical_recipes.csv"][0]["id"], "z")
        self.assertEqual(summary["automatically_resolved_duplicate_groups"], 1)
        self.assertEqual(outputs["recipe_canonical_mapping.csv"][0]["valid_master_match_count"], 0)
        self.assertEqual((rows, ingredients, MASTER), original)

    def test_ties_singletons_and_permutation(self):
        rows = [recipe("z"), recipe("a"), recipe("x", "Other")]
        ingredients = [ingredient(r["id"]) for r in rows]
        out, _ = build(rows, ingredients, MASTER)
        reverse, _ = build(rows[::-1], ingredients[::-1], MASTER)
        self.assertEqual({k: csv_bytes(v) for k, v in out.items()},
                         {k: csv_bytes(v) for k, v in reverse.items()})
        self.assertEqual([r["id"] for r in out["canonical_recipes.csv"]], ["a", "x"])

    def test_composition_difference_is_automatically_confirmed(self):
        out, summary = build([recipe("a"), recipe("b")],
                             [ingredient("a"), ingredient("b", cleaned_name="beef")], MASTER)
        self.assertEqual(summary["automatically_resolved_duplicate_groups"], 1)
        self.assertEqual(summary["manual_review_duplicate_groups"], 0)
        self.assertEqual(summary["total_review_groups"], 0)
        self.assertEqual(out["recipe_canonical_review.csv"], [])
        self.assertEqual(out["canonical_recipes.csv"][0]["resolution_status"], "automatic")
        self.assertEqual(out["canonical_recipes.csv"][0]["id"], "a")
        self.assertEqual({r["original_recipe_id"] for r in out["recipe_canonical_mapping.csv"]}, {"a", "b"})
        self.assertNotIn("provisional", out["canonical_recipes.csv"][0]["selection_reason"])

    def test_normalized_variants_group_but_different_names_do_not(self):
        rows = [recipe("a", "  SOUP  "), recipe("b", "soup"), recipe("c", "soup vegan")]
        out, summary = build(rows, [ingredient(r["id"]) for r in rows], MASTER)
        self.assertEqual(summary["duplicate_candidate_groups"], 1)
        self.assertEqual(summary["automatically_resolved_duplicate_groups"], 1)
        self.assertEqual([r["id"] for r in out["canonical_recipes.csv"]], ["a", "c"])

    def test_empty_ingredient_sets_do_not_require_review(self):
        out, summary = build([recipe("a"), recipe("b")], [], MASTER)
        self.assertEqual(summary["automatically_resolved_duplicate_groups"], 1)
        self.assertEqual(summary["total_review_groups"], 0)
        self.assertEqual(out["canonical_recipes.csv"][0]["id"], "a")

    def test_empty_review_csv_retains_schema(self):
        header = next(csv.reader(io.StringIO(csv_bytes([], REVIEW_FIELDS).decode())))
        self.assertEqual(header, list(REVIEW_FIELDS))

    def test_empty_names_remain_separate(self):
        out, summary = build([recipe("a", ""), recipe("b", " ")], [], MASTER)
        self.assertEqual(summary["canonical_recipes"], 2)
        self.assertEqual(len(out["recipe_canonical_review.csv"]), 2)
        self.assertEqual(summary["total_review_groups"], 2)
        self.assertTrue(all(r["review_reason"] == "missing normalized name prevents name-based grouping"
                            for r in out["recipe_canonical_review.csv"]))
        self.assertTrue(all(r["original_recipe_id"] == r["canonical_recipe_id"]
                            for r in out["recipe_canonical_mapping.csv"]))

    def test_explicit_ten_grams_is_not_fallback(self):
        _, metrics = quality(recipe("a"), [ingredient("a", estimated_weight_g="10")], {"1": MASTER[0]})
        self.assertEqual(metrics["fallback_10g_count"], 0)
        _, metrics = quality(recipe("a"), [ingredient("a", required_quantity="NaN", estimated_weight_g="10")], {"1": MASTER[0]})
        self.assertEqual(metrics["fallback_10g_count"], 1)

    def test_missing_master_nutrition_and_invalid_codes_are_visible(self):
        master = {"1": dict(MASTER[0], fat_g="NaN")}
        _, metrics = quality(recipe("a"), [ingredient("a")], master)
        self.assertEqual(metrics["nutrition_anomaly_count"], 1)
        _, metrics = quality(recipe("a"), [ingredient("a", master_ingredient_code="999")], master)
        self.assertEqual(metrics["valid_master_match_count"], 0)

    def test_bad_references_and_duplicate_ids_fail(self):
        with self.assertRaisesRegex(ValueError, "Orphan"):
            build([recipe("a")], [ingredient("b")], MASTER)
        with self.assertRaisesRegex(ValueError, "duplicate source recipe"):
            build([recipe("a"), recipe("a")], [], MASTER)


if __name__ == "__main__":
    unittest.main()
