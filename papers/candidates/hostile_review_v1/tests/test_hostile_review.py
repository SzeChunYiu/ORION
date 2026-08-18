from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from papers.candidates.hostile_review_v1 import p6_reopening, p7_refinement, p8_authority
from papers.candidates.hostile_review_v1.common import Status, write_report


class P6HostileReviewTests(unittest.TestCase):
    def test_direct_root_counterexample_is_reproduced(self) -> None:
        result = p6_reopening.check_directly_changed_certified_root()
        self.assertEqual(Status.COUNTEREXAMPLE_CONFIRMED, result.status)

    def test_changed_root_cannot_be_preserved(self) -> None:
        graph = p6_reopening.Graph(frozenset({"q"}), frozenset())
        certificate = p6_reopening.PreservationCertificate(
            "q", frozenset({"q"}), "protected-reviewer", frozenset({"ev"}), True
        )
        self.assertEqual(
            frozenset({"q"}),
            p6_reopening.corrected_operator(
                graph, frozenset({"q"}), frozenset({"q"}), (certificate,)
            ),
        )

    def test_forged_preservation_fails_closed(self) -> None:
        graph = p6_reopening.Graph(
            frozenset({"x", "q"}), frozenset({("x", "q")})
        )
        forged = p6_reopening.PreservationCertificate(
            "q", frozenset({"x"}), "candidate", frozenset({"ev"}), True
        )
        self.assertIn(
            "q",
            p6_reopening.corrected_operator(
                graph, frozenset({"x"}), frozenset({"x", "q"}), (forged,)
            ),
        )


class P7HostileReviewTests(unittest.TestCase):
    def test_refinement_does_not_change_latent_frame(self) -> None:
        frame, old, new, refinement, starts = p7_refinement._aliasing_fixture()
        self.assertTrue(refinement.is_legal_for(frame))
        self.assertEqual(set(old.observation), set(new.observation))
        self.assertEqual(set(frame.states), set(old.observation))
        self.assertEqual(("start-left", "start-right"), starts)

    def test_unretained_feature_is_not_a_legal_reframe(self) -> None:
        frame, old, new, _, _ = p7_refinement._aliasing_fixture()
        forged = p7_refinement.LegalRefinement(
            old,
            new,
            {**frame.retained_features, "start-left": "new-sensor-value"},
        )
        self.assertFalse(forged.is_legal_for(frame))

    def test_unknown_coverage_is_cannot_check(self) -> None:
        self.assertEqual(
            p7_refinement.StopDecision.CANNOT_CHECK,
            p7_refinement.stop_decision(
                frozenset({"coverage"}), frozenset({"coverage"}), True, True
            ),
        )


class P8HostileReviewTests(unittest.TestCase):
    def test_cross_domain_evidence_is_denied(self) -> None:
        context = p8_authority.Context(frozenset({"root"}))
        action = p8_authority.Action("assert", p8_authority.Domain.ASSERT, "claim", 1)
        obligation = p8_authority.Obligation(
            "verify", p8_authority.Domain.ASSERT, "verification", "claim", 1
        )
        evidence = p8_authority.Evidence(
            "search-pass", p8_authority.Domain.SEARCH_STOP, "verification", "claim", 1
        )
        decision = p8_authority.authorize(
            action,
            (obligation,),
            (evidence,),
            (p8_authority.Satisfaction("verify", "search-pass"),),
            issuer="root",
            context=context,
        )
        self.assertEqual(p8_authority.Decision.DENIED, decision)

    def test_missing_evidence_is_cannot_check(self) -> None:
        context = p8_authority.Context(frozenset({"root"}))
        action = p8_authority.Action("assert", p8_authority.Domain.ASSERT, "claim", 1)
        obligation = p8_authority.Obligation(
            "verify", p8_authority.Domain.ASSERT, "verification", "claim", 1
        )
        self.assertEqual(
            p8_authority.Decision.CANNOT_CHECK,
            p8_authority.authorize(
                action, (obligation,), (), (), issuer="root", context=context
            ),
        )

    def test_mismatched_obligation_contract_is_denied(self) -> None:
        context = p8_authority.Context(frozenset({"root"}))
        action = p8_authority.Action("assert", p8_authority.Domain.ASSERT, "claim", 1)
        foreign = p8_authority.Obligation(
            "foreign", p8_authority.Domain.SEARCH_STOP, "verification", "claim", 1
        )
        self.assertEqual(
            p8_authority.Decision.DENIED,
            p8_authority.authorize(
                action, (foreign,), (), (), issuer="root", context=context
            ),
        )

    def test_scope_incompatible_path_is_rejected(self) -> None:
        result = p8_authority.check_scope_incompatible_coercion_path()
        self.assertEqual(Status.COUNTEREXAMPLE_CONFIRMED, result.status)

    def test_alternative_derivation_survives_single_revocation(self) -> None:
        derivations = {
            "cert": (
                p8_authority.Derivation("a", frozenset({"ev-A"})),
                p8_authority.Derivation("b", frozenset({"ev-B"})),
            )
        }
        self.assertEqual(
            frozenset({"cert"}),
            p8_authority.surviving_certificates(derivations, frozenset({"ev-A"})),
        )


class ReportTests(unittest.TestCase):
    def test_report_is_byte_deterministic(self) -> None:
        result = p6_reopening.run_checks()[:1]
        with tempfile.TemporaryDirectory() as tempdir:
            first = Path(tempdir) / "first.json"
            second = Path(tempdir) / "second.json"
            digest_first = write_report(first, result, {"fixed": True})
            digest_second = write_report(second, result, {"fixed": True})
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertEqual(digest_first, digest_second)
            payload = json.loads(first.read_text(encoding="utf-8"))
            self.assertEqual("orion.p6_p8.hostile_formal_review.v1", payload["schema"])


if __name__ == "__main__":
    unittest.main()
