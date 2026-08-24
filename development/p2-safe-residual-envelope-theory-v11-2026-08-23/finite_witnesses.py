#!/usr/bin/env python3
"""Verify finite witnesses for the P2 V11 residual-envelope theory."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


TAU = 0.010858985820770889
HARM = 0.05
K = 6
N = 7
V10_SHA256 = "c69e5634b8d0e82a1fa393dbae276d728e9a2f7ba4c9db81a27c0329e2e66742"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def gate(rows: list[dict[str, float]]) -> dict[str, bool]:
    assert len(rows) == N
    mean = lambda key: sum(row[key] for row in rows) / N
    return {
        "mean_cre20": mean("c") >= TAU,
        "mean_r10": mean("q") >= TAU,
        "mean_wss95": mean("s") >= 0,
        "positive_cre20": sum(row["c"] > 0 for row in rows) >= K,
        "positive_r10": sum(row["q"] > 0 for row in rows) >= K,
        "worst_r10_harm": min(row["q"] for row in rows) >= -HARM,
        "absolute_wss95": all(row["a"] > 0 for row in rows),
    }


def main() -> int:
    here = Path(__file__).resolve().parent
    v10_path = here.parent / "p2-title-emphasis-conflict-resolved-v10-2026-08-23" / "RESULT_V10.json"
    if sha256_file(v10_path) != V10_SHA256:
        raise RuntimeError("V10 result binding drift")
    v10 = json.loads(v10_path.read_text())

    passing = [{"c": 0.02, "q": 0.02, "s": 0.001, "a": 0.5} for _ in range(N)]
    passing_gates = gate(passing)
    assert all(passing_gates.values())

    harm_only = [{"c": 0.02, "q": 0.03, "s": 0.001, "a": 0.5} for _ in range(6)]
    harm_only.append({"c": 0.02, "q": -0.051, "s": 0.001, "a": 0.5})
    harm_gates = gate(harm_only)
    assert all(value for key, value in harm_gates.items() if key != "worst_r10_harm")
    assert not harm_gates["worst_r10_harm"]

    scalar_compensation = []
    for weights in ((1.0, 1.0, 1.0), (0.5, 2.0, 4.0), (3.0, 0.25, 0.75)):
        wc, wq, ws = weights
        q = TAU - 1e-6
        c = 1e6
        s = 1.0
        score = wc * c + wq * q + ws * s
        assert q < TAU and score > 1e5
        scalar_compensation.append({"weights": list(weights), "failed_r10": q, "compensated_score": score})

    v10_rows = []
    for review, delta in sorted(v10["controller_delta_by_review"].items()):
        v10_rows.append({
            "review": review,
            "c": delta["cre20"],
            "q": delta["recall_at_010"],
            "s": delta["wss_at_95"],
            "a": v10["absolute_controller_wss95_by_review"][review],
        })
    v10_gates = gate(v10_rows)
    expected = {
        "mean_cre20": False,
        "mean_r10": False,
        "mean_wss95": True,
        "positive_cre20": False,
        "positive_r10": False,
        "worst_r10_harm": True,
        "absolute_wss95": True,
    }
    assert v10_gates == expected

    # Two extensions agree on a finite observed table. The positive extension
    # assigns a passing seven-review family outside the observed set.
    observed = {row["review"]: (row["c"], row["q"], row["s"]) for row in v10_rows}
    negative_extension = {**observed, **{f"unseen-{i}": (-0.02, -0.02, -0.001) for i in range(N)}}
    positive_extension = {**observed, **{f"unseen-{i}": (0.02, 0.02, 0.001) for i in range(N)}}
    assert all(negative_extension[key] == positive_extension[key] for key in observed)
    assert all(gate(passing).values())

    # Donor fibre witness: one donor state cannot implement two distinct
    # actions, while a new binary signal separates the two worlds.
    donor_state = {"w0": 0, "w1": 0}
    candidate_action = {"w0": 0, "w1": 1}
    constant_donor_rules = ({0: 0}, {0: 1})
    assert all(any(rule[donor_state[w]] != candidate_action[w] for w in donor_state) for rule in constant_donor_rules)
    new_signal = {"w0": 0, "w1": 1}
    separating_rule = {0: 0, 1: 1}
    assert all(separating_rule[new_signal[w]] == candidate_action[w] for w in new_signal)

    # Acquisition ceiling witness: reordering cannot add an unacquired gold
    # identity, while a new route can.
    gold = {"g1", "g2"}
    donor_acquired = {"g1"}
    reordered = list(reversed(sorted(donor_acquired)))
    new_route_acquired = donor_acquired | {"g2"}
    assert len(set(reordered) & gold) / len(gold) == 0.5
    assert len(new_route_acquired & gold) / len(gold) == 1.0

    receipt: dict[str, Any] = {
        "identity": "P2_V11_FINITE_THEORY_WITNESS_RECEIPT",
        "v10_result_sha256": V10_SHA256,
        "passing_gate_witness": {"rows": N, "gates": passing_gates},
        "harm_noncompensation_witness": {"rows": N, "gates": harm_gates},
        "scalar_compensation_witnesses": scalar_compensation,
        "v10_gate_reconstruction": {"rows": N, "gates": v10_gates, "matches_result": True},
        "finite_extension_nonidentification": {
            "observed_worlds": len(observed),
            "extensions_agree_on_observed": True,
            "positive_unseen_family_passes": True,
            "interpretation": "logical compatibility only, not evidence that the unseen family exists",
        },
        "donor_fibre_witness": {
            "donor_state_tied": True,
            "candidate_not_donor_factorable": True,
            "new_signal_separates": True,
        },
        "acquisition_ceiling_witness": {
            "reordering_ceiling": 0.5,
            "new_route_ceiling": 1.0,
        },
        "all_passed": True,
    }
    (here / "FINITE_WITNESS_RECEIPT_V11.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print("P2_V11_FINITE_WITNESSES_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
