import itertools
import random
import unittest

from evidence_license_evaluator import (
    ValidationError,
    evaluate_document,
    least_fixed_point,
    validate_document,
)


def system(claims, rules, refutations=None, licenses=None):
    return {
        "version": "1.0",
        "licenses": licenses or ["THEOREM", "POST_OUTCOME", "PROSPECTIVE"],
        "claims": claims,
        "rules": rules,
        "refutations": refutations or [],
    }


class EvidenceLicenseEvaluatorTests(unittest.TestCase):
    def test_unsupported_cycle_remains_empty(self):
        document = system(
            [{"id": "a", "seeds": []}, {"id": "b", "seeds": []}],
            [
                {"id": "a_to_b", "body": ["a"], "head": "b", "cap": ["THEOREM"]},
                {"id": "b_to_a", "body": ["b"], "head": "a", "cap": ["THEOREM"]},
            ],
        )
        result = evaluate_document(document)
        self.assertEqual(result["final_labels"], {"a": [], "b": []})

    def test_seeded_cycle_propagates_only_permitted_license(self):
        document = system(
            [
                {"id": "a", "seeds": ["THEOREM", "PROSPECTIVE"]},
                {"id": "b", "seeds": []},
            ],
            [
                {
                    "id": "a_to_b",
                    "body": ["a"],
                    "head": "b",
                    "cap": ["THEOREM"],
                },
                {
                    "id": "b_to_a",
                    "body": ["b"],
                    "head": "a",
                    "cap": ["THEOREM"],
                },
            ],
        )
        result = evaluate_document(document)
        self.assertEqual(result["final_labels"]["b"], ["THEOREM"])

    def test_refutation_preserves_alternative_derivation(self):
        document = system(
            [
                {"id": "left", "seeds": ["THEOREM"]},
                {"id": "right", "seeds": ["THEOREM"]},
                {"id": "conclusion", "seeds": []},
            ],
            [
                {"id": "l", "body": ["left"], "head": "conclusion", "cap": ["THEOREM"]},
                {"id": "r", "body": ["right"], "head": "conclusion", "cap": ["THEOREM"]},
            ],
            ["left"],
        )
        result = evaluate_document(document)
        self.assertEqual(result["final_labels"]["conclusion"], ["THEOREM"])
        self.assertNotIn(
            {"claim": "conclusion", "license": "THEOREM"}, result["retracted"]
        )

    def test_post_outcome_cap_blocks_prospective(self):
        document = system(
            [
                {"id": "source", "seeds": ["POST_OUTCOME", "PROSPECTIVE"]},
                {"id": "repair", "seeds": []},
            ],
            [
                {
                    "id": "repair_rule",
                    "body": ["source"],
                    "head": "repair",
                    "cap": ["POST_OUTCOME"],
                }
            ],
        )
        result = evaluate_document(document)
        self.assertEqual(result["final_labels"]["repair"], ["POST_OUTCOME"])

    def test_validation_rejects_unknown_license(self):
        document = system([{"id": "a", "seeds": ["UNKNOWN"]}], [])
        with self.assertRaises(ValidationError):
            validate_document(document)

    def test_validation_rejects_missing_schema_required_fields(self):
        document = system([{"id": "a", "seeds": []}], [])
        for field in ("rules", "refutations"):
            malformed = dict(document)
            del malformed[field]
            with self.subTest(field=field), self.assertRaises(ValidationError):
                validate_document(malformed)

    def test_validation_rejects_missing_claim_seeds(self):
        document = system([{"id": "a"}], [])
        with self.assertRaises(ValidationError):
            validate_document(document)

    def test_semantic_validation_rejects_unknown_claim_references(self):
        unknown_body = system(
            [{"id": "a", "seeds": ["THEOREM"]}],
            [{"id": "r", "body": ["missing"], "head": "a", "cap": ["THEOREM"]}],
        )
        unknown_refutation = system(
            [{"id": "a", "seeds": ["THEOREM"]}], [], ["missing"]
        )
        for document in (unknown_body, unknown_refutation):
            with self.subTest(document=document), self.assertRaises(ValidationError):
                validate_document(document)

    def test_random_small_systems_match_exhaustive_least_fixed_point(self):
        rng = random.Random(20260825)
        for _ in range(80):
            claim_ids = ["a", "b", "c"]
            licenses = ["L0", "L1"]
            claims = [
                {"id": claim, "seeds": [license for license in licenses if rng.random() < 0.25]}
                for claim in claim_ids
            ]
            rules = []
            for index in range(4):
                body = rng.sample(claim_ids, rng.choice([1, 2]))
                rules.append(
                    {
                        "id": f"r{index}",
                        "body": body,
                        "head": rng.choice(claim_ids),
                        "cap": [license for license in licenses if rng.random() < 0.7],
                    }
                )
            normalized = validate_document(system(claims, rules, licenses=licenses))
            calculated, _ = least_fixed_point(normalized, [])

            fixed_points = []
            pairs = list(itertools.product(claim_ids, licenses))
            for mask in range(1 << len(pairs)):
                candidate = {claim: set() for claim in claim_ids}
                for bit, (claim, license_name) in enumerate(pairs):
                    if mask & (1 << bit):
                        candidate[claim].add(license_name)
                next_candidate = {
                    claim: set(next(item["seeds"] for item in normalized["claims"] if item["id"] == claim))
                    for claim in claim_ids
                }
                for rule in normalized["rules"]:
                    transfer = set(rule["cap"])
                    for premise in rule["body"]:
                        transfer.intersection_update(candidate[premise])
                    next_candidate[rule["head"]].update(transfer)
                if next_candidate == candidate:
                    fixed_points.append(candidate)

            self.assertTrue(fixed_points)
            least = min(fixed_points, key=lambda point: sum(len(value) for value in point.values()))
            self.assertEqual(calculated, least)


if __name__ == "__main__":
    unittest.main()
