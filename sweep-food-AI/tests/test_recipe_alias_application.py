"""Reviewed aliases compose over Phase 1 without changing quality ranking."""
import unittest

from scripts.canonicalize_recipes import (
    compose_reviewed_aliases, csv_bytes, normalize_name, read_csv, resolve_reviewed_id, ROOT,
)
from test_recipe_canonicalization import recipe, ingredient, MASTER


def decision(a, b, status="approved"):
    return dict(recipe_id_a=a["id"], recipe_id_b=b["id"],
                normalized_name_a=normalize_name(a["name"]), normalized_name_b=normalize_name(b["name"]),
                decision=status, reason="Explicit test review")


class ReviewedAliasTests(unittest.TestCase):
    def test_approved_name_forms_and_provenance(self):
        for first, second in (("bò xào nấm", "nấm xào bò"),
                              ("salad bò-đậu rồng", "salad bò đậu rồng"),
                              ("canh cải cúc", "canh cải cúc (tần ô)")):
            with self.subTest(first=first):
                a, b = recipe("a", first), recipe("b", second)
                extra = recipe("c", first)
                ingredients = [ingredient("a"), ingredient("b", match_method="UNMATCHED"),
                               ingredient("c", match_method="UNMATCHED")]
                out, summary = compose_reviewed_aliases([a, b, extra], ingredients, MASTER, [decision(a, b)])
                self.assertEqual([r["id"] for r in out["canonical_recipes.csv"]], ["a"])
                mapping = out["recipe_canonical_mapping.csv"]
                self.assertEqual({r["original_recipe_id"] for r in mapping}, {"a", "b", "c"})
                self.assertEqual({r["canonical_recipe_id"] for r in mapping}, {"a"})
                self.assertEqual(mapping[2]["phase1_canonical_recipe_id"], "a")
                self.assertEqual(summary["phase2"]["canonical_dishes_removed"], 1)

    def test_explicit_rejection(self):
        a = recipe("a", "Mì trứng tôm thịt heo")
        b = recipe("b", "Mì tôm Trứng Thịt heo")
        out, _ = compose_reviewed_aliases([a, b], [ingredient("a"), ingredient("b")], MASTER, [decision(a, b, "rejected")])
        self.assertEqual(len(out["canonical_recipes.csv"]), 2)
        self.assertNotEqual(out["recipe_name_alias_application_audit.csv"][0]["final_canonical_recipe_id_a"],
                            out["recipe_name_alias_application_audit.csv"][0]["final_canonical_recipe_id_b"])

    def test_transitive_rejection_stops_generation(self):
        a, b, c = recipe("a", "one"), recipe("b", "two"), recipe("c", "three")
        with self.assertRaisesRegex(ValueError, "Rejected pair connected"):
            compose_reviewed_aliases([a, b, c], [], MASTER,
                                    [decision(a, b), decision(b, c), decision(a, c, "rejected")])

    def test_transitive_selection_and_permutation(self):
        recipes = [recipe("a", "one"), recipe("b", "two"), recipe("c", "three")]
        ingredients = [ingredient("a", match_method="UNMATCHED"), ingredient("b"), ingredient("c")]
        decisions = [decision(recipes[0], recipes[1]), decision(recipes[1], recipes[2])]
        out, summary = compose_reviewed_aliases(recipes, ingredients, MASTER, decisions)
        reverse, other = compose_reviewed_aliases(recipes[::-1], ingredients[::-1], MASTER[::-1], decisions[::-1])
        self.assertEqual(summary, other)
        self.assertEqual({k: csv_bytes(v) for k, v in out.items()}, {k: csv_bytes(v) for k, v in reverse.items()})
        self.assertEqual(out["canonical_recipes.csv"][0]["id"], "b")
        self.assertEqual(summary["phase2"]["transitive_groups"], [["a", "b", "c"]])

    def test_stale_review_fails(self):
        a, b = recipe("a", "one"), recipe("b", "two")
        stale = dict(decision(a, b), normalized_name_a="other")
        with self.assertRaisesRegex(ValueError, "changed normalized dish identity"):
            compose_reviewed_aliases([a, b], [], MASTER, [stale])

    def test_actual_reviewed_layer(self):
        import json
        decisions = json.loads((ROOT / "data/processed/recipes/recipe_name_alias_decisions.json").read_text(encoding="utf-8"))["relationships"]
        self.assertEqual(sum(d["decision"] == "approved" for d in decisions), 31)
        rejected = [d for d in decisions if d["decision"] == "rejected"]
        self.assertEqual(len(rejected), 1)
        self.assertEqual({rejected[0]["normalized_name_a"], rejected[0]["normalized_name_b"]},
                         {normalize_name("Mì trứng tôm thịt heo"), normalize_name("Mì tôm Trứng Thịt heo")})


class RepresentativeDriftTests(unittest.TestCase):
    """A reviewed decision keeps the exact id a human looked at; only its
    resolution to the CURRENT Phase-1 representative may drift when corrected
    processed data changes an intra-group quality tie-break. These guard the
    fix/canonical-cutover redesign that replaced hand-editing decisions.json /
    recipe_name_alias_candidates.csv with resolve_reviewed_id().
    """

    def _drift_scenario(self):
        # Group "one" has three duplicates; a2 is the only valid match and
        # therefore the current Phase-1 winner, but the decision was recorded
        # against "a1" (a non-winning member) -- exactly what happens when a
        # later data correction flips the intra-group tie-break.
        a1, a2, a3 = recipe("a1", "one"), recipe("a2", "one"), recipe("a3", "one")
        b1 = recipe("b1", "two")
        ingredients = [
            ingredient("a1", match_method="UNMATCHED"),
            ingredient("a2"),
            ingredient("a3", match_method="UNMATCHED"),
            ingredient("b1", match_method="UNMATCHED"),
        ]
        decisions = [dict(recipe_id_a="a1", recipe_id_b="b1", normalized_name_a="one",
                           normalized_name_b="two", decision="approved", reason="Explicit test review")]
        return [a1, a2, a3, b1], ingredients, decisions

    def test_stale_representative_resolves_within_same_group(self):
        recipes, ingredients, decisions = self._drift_scenario()
        out, _ = compose_reviewed_aliases(recipes, ingredients, MASTER, decisions)
        self.assertEqual([r["id"] for r in out["canonical_recipes.csv"]], ["a2"])
        mapping = {m["original_recipe_id"]: m["canonical_recipe_id"] for m in out["recipe_canonical_mapping.csv"]}
        self.assertEqual(mapping, {"a1": "a2", "a2": "a2", "a3": "a2", "b1": "a2"})

    def test_review_decision_remains_valid_after_representative_flip(self):
        recipes, ingredients, decisions = self._drift_scenario()
        out, _ = compose_reviewed_aliases(recipes, ingredients, MASTER, decisions)
        audit = out["recipe_name_alias_application_audit.csv"][0]
        # The audit trail still names the originally reviewed ids verbatim...
        self.assertEqual(audit["recipe_id_a"], "a1")
        self.assertEqual(audit["recipe_id_b"], "b1")
        # ...and shows they now resolve together, satisfying the approved decision.
        self.assertEqual(audit["final_canonical_recipe_id_a"], "a2")
        self.assertEqual(audit["final_canonical_recipe_id_b"], "a2")

    def test_canonical_output_stays_deterministic_under_representative_drift(self):
        recipes, ingredients, decisions = self._drift_scenario()
        out, summary = compose_reviewed_aliases(recipes, ingredients, MASTER, decisions)
        reverse, other = compose_reviewed_aliases(recipes[::-1], ingredients[::-1], MASTER[::-1], decisions[::-1])
        self.assertEqual(summary, other)
        self.assertEqual({k: csv_bytes(v) for k, v in out.items()}, {k: csv_bytes(v) for k, v in reverse.items()})

    def test_cross_group_stale_id_is_rejected(self):
        # "x" genuinely exists but is an unrelated dish; a decision that claims
        # it belongs to group "one" must be refused, not silently honored.
        a, b, x = recipe("a", "one"), recipe("b", "two"), recipe("x", "completely different dish")
        decisions = [dict(recipe_id_a="x", recipe_id_b="b", normalized_name_a="one",
                           normalized_name_b="two", decision="approved", reason="Explicit test review")]
        with self.assertRaisesRegex(ValueError, "changed normalized dish identity"):
            compose_reviewed_aliases([a, b, x], [], MASTER, decisions)

    def test_missing_reviewed_id_is_rejected(self):
        a = recipe("a", "one")
        decisions = [dict(recipe_id_a="does-not-exist", recipe_id_b="a", normalized_name_a="one",
                           normalized_name_b="one", decision="approved", reason="Explicit test review")]
        with self.assertRaisesRegex(ValueError, "no longer exists in source data"):
            compose_reviewed_aliases([a], [], MASTER, decisions)

    def test_ambiguous_resolution_target_is_rejected(self):
        # Direct unit test of the ambiguity guard: a resolved representative
        # whose duplicate-group id disagrees with the reviewed recipe's own
        # group must never be accepted, even if both dicts are individually
        # well-formed. This defends resolve_reviewed_id against ever silently
        # picking a representative from the wrong group.
        source_by_id = {"orig": {"id": "orig", "name": "One"}}
        phase1_mapping = {"orig": {"canonical_recipe_id": "winner", "canonical_dish_name": "one",
                                    "canonical_group_id": "group-1"}}
        representatives = {"winner": {"canonical_group_id": "group-2"}}
        with self.assertRaisesRegex(ValueError, "outside its own duplicate group"):
            resolve_reviewed_id("orig", "one", phase1_mapping, source_by_id, representatives)


if __name__ == "__main__":
    unittest.main()
