"""Phase 2 discovers lexical candidates without making identity decisions."""

import copy
import unittest

from scripts.eda.recipe_name_alias_analysis import build, distance, features, pair_rules


def recipe(identifier, name):
    return dict(id=identifier, name=name, canonical_dish_name=name,
                source_url="https://example.org/" + identifier)


def rules(a, b):
    return pair_rules(features(recipe("a", a)), features(recipe("b", b)))


class AliasCandidateTests(unittest.TestCase):
    def test_punctuation_and_reordering(self):
        self.assertIn("punctuation_equal", rules("cá-kho", "cá kho"))
        self.assertIn("token_reorder", rules("bò xào nấm", "nấm xào bò"))

    def test_phase_one_same_name_is_not_candidate(self):
        self.assertEqual(rules("  CÁ KHO", "ca\u0301 kho"), [])

    def test_parentheses_and_suffix_evidence(self):
        self.assertIn("parenthetical_base_equal", rules("bún bò (phiên bản nhà làm)", "bún bò"))
        self.assertIn("descriptive_suffix_equal", rules("bún bò đơn giản", "bún bò"))
        self.assertEqual(rules("bún bò (món chay)", "bún bò"), [])
        self.assertEqual(rules("bún bò (phiên bản nhà làm", "bún bò"), [])

    def test_unsafe_containment_and_methods(self):
        for a, b in (("canh chua cá", "canh chua cá hồi"),
                     ("gà nướng", "gà nướng mật ong"),
                     ("cá kho tiêu", "cá chiên tiêu"),
                     ("canh rau thịt bò", "canh rau thịt gà")):
            with self.subTest(a=a, b=b):
                self.assertEqual(rules(a, b), [])

    def test_tight_edit_and_accent_guard(self):
        self.assertIn("single_token_edit", rules("bánh chocolate nhân kem", "bánh choclate nhân kem"))
        self.assertEqual(rules("bánh chocolate", "bánh choclate"), [])
        self.assertEqual(rules("bánh nhân quả chuối", "bánh nhân quả chuôi"), [])
        self.assertEqual(distance("abc", "ac"), 1)

    def test_determinism_evidence_and_no_mutation(self):
        recipes = [recipe("b", "bún bò (phiên bản nhà làm)"), recipe("a", "bún bò")]
        ingredients = [dict(recipe_id="a", cleaned_name="bò"), dict(recipe_id="b", cleaned_name="nấm")]
        before = copy.deepcopy((recipes, ingredients))
        rows = build(recipes, ingredients)
        self.assertEqual(rows, build(recipes[::-1], ingredients[::-1]))
        self.assertEqual((recipes, ingredients), before)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["review_status"], "unreviewed_candidate_only")
        self.assertEqual(rows[0]["ingredient_jaccard"], "0.000000")
        self.assertIn("phiên bản nhà làm", rows[0]["removed_parenthetical_b"])

    def test_invalid_ids_names_and_references(self):
        with self.assertRaises(ValueError):
            build([recipe("a", "bún bò"), recipe("a", "bún gà")], [])
        with self.assertRaises(ValueError):
            build([recipe("a", "bún bò"), recipe("b", "BÚN BÒ")], [])
        with self.assertRaises(ValueError):
            build([recipe("a", "bún bò")], [dict(recipe_id="b", cleaned_name="bò")])


if __name__ == "__main__":
    unittest.main()
