from __future__ import annotations

from collections import Counter

from generate_p4_x_dev_cases import ARCHETYPES, DOMAINS, generate_cases
from p4_x_execution import run_arms

EXPECTED = {
    "P4_X": 200,
    "B1_GENERIC_AUTHORIZATION_PRODUCT": 125,
    "B2_COMPENSATORY_PRODUCT": 25,
    "B3_IDEAL_TYPED_PRODUCT": 200,
}


def main() -> int:
    cases = generate_cases()
    assert len(cases) == 200
    assert len({c["case_id"] for c in cases}) == 200
    assert set(c["domain"] for c in cases) == set(DOMAINS)
    assert set(c["archetype"] for c in cases) == set(ARCHETYPES)

    counts: Counter[str] = Counter()
    b1_failures: Counter[str] = Counter()
    for case in cases:
        gold = case["protected_gold"]["task_terminal"]
        arms = run_arms(case)
        for arm, decision in arms.items():
            counts[arm] += int(decision == gold)
        if arms["B1_GENERIC_AUTHORIZATION_PRODUCT"] != gold:
            b1_failures[case["archetype"]] += 1
        assert arms["B3_IDEAL_TYPED_PRODUCT"] == arms["P4_X"]

    assert dict(counts) == EXPECTED
    assert set(b1_failures) == {
        "CLAIM_SCOPE_OVERREACH",
        "CORRELATED_EVIDENCE_DOUBLE_COUNT",
        "ACTION_AUTHORIZED_SCIENTIFIC_PROMOTION_UNRESOLVED",
    }
    assert all(v == 25 for v in b1_failures.values())

    # Decoy must never change P4-X decision.
    assert all(
        run_arms(c)["P4_X"] == c["protected_gold"]["task_terminal"]
        for c in cases
        if not c["candidate_visible"]["non_load_bearing_latency_sla_met"]
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
