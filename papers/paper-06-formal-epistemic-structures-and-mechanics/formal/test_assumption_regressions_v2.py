import unittest

from check_assumption_regressions_v2 import (
    AuthorityToken,
    CERTIFIED,
    Mechanic,
    contains_cycle,
    evaluate_countermodel_case,
    exhaustive_commutation_check,
    independent_ordered_histories,
    trace_equivalent_by_independent_swap,
    minimality_witness,
    rank_decreases,
    selective_reopen,
    self_authorization_countermodel,
    step_is_non_escalating,
)


class P6CheckerTests(unittest.TestCase):
    def test_selective_reopening_preserves_unrelated_claims(self):
        statuses = {"q1": CERTIFIED, "q2": CERTIFIED, "q3": CERTIFIED}
        result = selective_reopen(statuses, {("x", "q1"), ("q1", "q2"), ("z", "q3")}, {"x"})
        self.assertNotEqual(result["q1"], CERTIFIED)
        self.assertNotEqual(result["q2"], CERTIFIED)
        self.assertEqual(result["q3"], CERTIFIED)

    def test_minimality_requires_descendant_witness(self):
        edges = {("x", "q")}
        self.assertTrue(minimality_witness(edges, {"x"}, "q"))
        self.assertFalse(minimality_witness(edges, {"x"}, "unrelated"))

    def test_strongly_separated_footprint_faithful_mechanics_commute(self):
        left = Mechanic("left", frozenset({"a"}), frozenset({"b"}), lambda s: {"b": 1 - s["a"]})
        right = Mechanic("right", frozenset({"c"}), frozenset({"d"}), lambda s: {"d": s["c"]})
        self.assertTrue(exhaustive_commutation_check(left, right, ("a", "b", "c", "d")))

    def test_undeclared_write_is_rejected(self):
        bad = Mechanic("bad", frozenset({"a"}), frozenset({"b"}), lambda s: {"c": s["a"]})
        with self.assertRaises(ValueError):
            bad.apply({"a": 0, "b": 0, "c": 0})

    def test_narrowing_does_not_escalate(self):
        root = AuthorityToken("host", "assert", frozenset({"a", "b"}), "host")
        narrowed = AuthorityToken("agent", "assert", frozenset({"a"}), "host")
        self.assertTrue(step_is_non_escalating(frozenset({root}), frozenset({root, narrowed}), frozenset({"host"})))

    def test_forged_cross_domain_token_escalates(self):
        root = AuthorityToken("host", "assert", frozenset({"a"}), "host")
        forged = AuthorityToken("agent", "self_modify", frozenset({"registry"}), "agent")
        self.assertFalse(step_is_non_escalating(frozenset({root}), frozenset({root, forged}), frozenset({"host"})))

    def test_rank_descent_and_cycle_detection(self):
        self.assertTrue(rank_decreases({("a", "b"), ("b", "c")}, {"a": 2, "b": 1, "c": 0}))
        self.assertFalse(contains_cycle({("a", "b"), ("b", "c")}))
        self.assertTrue(contains_cycle({("a", "a")}))

    def test_self_authorization_countermodel_needs_both_controls(self):
        self.assertTrue(self_authorization_countermodel(True, True))
        self.assertFalse(self_authorization_countermodel(True, False))

    def test_machine_readable_countermodel_is_executed(self):
        case = {
            "kind": "self_authorization",
            "candidate_controls_policy": True,
            "candidate_controls_evidence": True,
        }
        self.assertEqual(evaluate_countermodel_case(case), "DETECTED")

    def test_commutation_is_projection_equality_not_literal_history_equality(self):
        left = Mechanic("left", frozenset({"a"}), frozenset({"b"}), lambda s: {"b": s["a"]})
        right = Mechanic("right", frozenset({"c"}), frozenset({"d"}), lambda s: {"d": s["c"]})
        lr, rl = independent_ordered_histories(left, right)
        self.assertNotEqual(lr, rl)
        self.assertTrue(trace_equivalent_by_independent_swap(
            lr, rl, frozenset({frozenset({"left", "right"})})
        ))


if __name__ == "__main__":
    unittest.main()
