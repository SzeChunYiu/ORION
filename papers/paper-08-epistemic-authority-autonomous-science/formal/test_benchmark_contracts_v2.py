import unittest

from check_benchmark_contracts_v2 import (
    AuthorityCertificate,
    AuthoritySystem,
    AuthorizationRequest,
    Domain,
    Verdict,
    additive_blocker_counterexample,
    embedding_is_typed,
    evaluate_authority_case,
    self_promotion_countermodel,
)


class P8CheckerTests(unittest.TestCase):
    def setUp(self):
        self.assert_root = AuthorityCertificate(
            "root", "host", Domain.ASSERT, frozenset({"claim"}), frozenset({"e"})
        )
        self.system = AuthoritySystem(
            {"root": self.assert_root}, frozenset({"host"}), frozenset(), set()
        )

    def test_same_domain_complete_obligations_authorize(self):
        request = AuthorizationRequest(
            "a", Domain.ASSERT, "claim", frozenset({"support"}), frozenset({"support"})
        )
        self.assertEqual(self.system.authorize(request, "root"), Verdict.AUTHORIZED)

    def test_wrong_domain_token_cannot_launder_authority(self):
        request = AuthorizationRequest(
            "a", Domain.REFRAME, "claim", frozenset(), frozenset()
        )
        self.assertEqual(self.system.authorize(request, "root"), Verdict.UNAUTHORIZED)

    def test_registered_coercion_is_explicit(self):
        self.system.coercions = frozenset({(Domain.ASSERT, Domain.REFRAME)})
        request = AuthorizationRequest(
            "a", Domain.REFRAME, "claim", frozenset(), frozenset()
        )
        self.assertEqual(self.system.authorize(request, "root"), Verdict.AUTHORIZED)

    def test_transitive_coercion_has_one_semantics_in_system_and_case_oracle(self):
        self.system.coercions = frozenset({
            (Domain.ASSERT, Domain.MAP_MERGE),
            (Domain.MAP_MERGE, Domain.REFRAME),
        })
        request = AuthorizationRequest(
            "a", Domain.REFRAME, "claim", frozenset(), frozenset()
        )
        self.assertEqual(self.system.authorize(request, "root"), Verdict.AUTHORIZED)
        case = {
            "domain": "REFRAME",
            "source_signal_domain": "ASSERT",
            "hard_obligations": [],
            "satisfied": [],
            "defeaters": [],
            "registered_coercions": [["ASSERT", "MAP_MERGE"], ["MAP_MERGE", "REFRAME"]],
        }
        self.assertEqual(evaluate_authority_case(case), Verdict.AUTHORIZED)

    def test_missing_known_hard_obligation_is_unauthorized(self):
        request = AuthorizationRequest(
            "a", Domain.ASSERT, "claim", frozenset({"support"}), frozenset()
        )
        self.assertEqual(self.system.authorize(request, "root"), Verdict.UNAUTHORIZED)

    def test_unknown_hard_obligation_is_cannot_check(self):
        request = AuthorizationRequest(
            "a", Domain.ASSERT, "claim", frozenset({"support"}), frozenset(),
            unknown_obligations=frozenset({"support"}),
        )
        self.assertEqual(self.system.authorize(request, "root"), Verdict.CANNOT_CHECK)

    def test_defeater_is_reject(self):
        request = AuthorizationRequest(
            "a", Domain.ASSERT, "claim", frozenset(), frozenset(),
            active_defeaters=frozenset({"forgery"}),
        )
        self.assertEqual(self.system.authorize(request, "root"), Verdict.REJECT)

    def test_revocation_propagates_but_preserves_unrelated(self):
        child = AuthorityCertificate(
            "child", "checker", Domain.ASSERT, frozenset({"claim"}), frozenset({"e2"}), frozenset({"root"})
        )
        unrelated = AuthorityCertificate(
            "other", "host", Domain.SEARCH_STOP, frozenset({"route"}), frozenset({"s"})
        )
        self.system.certificates.update({"child": child, "other": unrelated})
        affected = self.system.revoke("root")
        self.assertEqual(affected, {"root", "child"})
        self.assertNotIn("other", self.system.revoked)

    def test_finite_additive_penalty_can_be_overwhelmed(self):
        n, score = additive_blocker_counterexample(10, -100, 1)
        self.assertEqual(n, 110)
        self.assertGreaterEqual(score, 10)

    def test_self_promotion_countermodel_requires_control_of_policy_and_evidence(self):
        self.assertTrue(self_promotion_countermodel(True, True))
        self.assertFalse(self_promotion_countermodel(True, False))

    def test_all_five_gate_embeddings_are_typed(self):
        self.assertTrue(embedding_is_typed())

    def test_hostile_manifest_cases_are_executed_not_only_parsed(self):
        hostile = {
            "domain": "REFRAME",
            "source_signal_domain": "ASSERT",
            "hard_obligations": ["typed-responsibility"],
            "satisfied": ["typed-responsibility"],
            "defeaters": [],
        }
        unknown = {
            "domain": "ASSERT",
            "source_signal_domain": "ASSERT",
            "hard_obligations": ["independent-check"],
            "satisfied": [],
            "unknown_obligations": ["independent-check"],
            "defeaters": [],
        }
        self.assertEqual(evaluate_authority_case(hostile), Verdict.UNAUTHORIZED)
        self.assertEqual(evaluate_authority_case(unknown), Verdict.CANNOT_CHECK)


if __name__ == "__main__":
    unittest.main()
