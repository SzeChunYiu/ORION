#!/usr/bin/env python3
"""Independent generic-harness verifier for QG-6 syndrome-rank inference.

This verifier intentionally does not import the production R6M/R6I `_DELTA` arrays.
It reconstructs the documented state equations from the primitive local Pauli algebra.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
ORION_Q = REPO_ROOT / "research" / "extensions" / "orion-q"
sys.path.insert(0, str(ORION_Q))

import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402

PROTOCOL_PATH = (
    REPO_ROOT
    / "development"
    / "orion-qg-regime-geometry"
    / "QG6_SYNDROME_DIMENSION_COMPRESSION_PROTOCOL_V1.md"
)
R6S_PATH = ORION_Q / "MAX_R6S_ALL_N_COMPOSITION_RESULTS.json"
DEFAULT_INPUT = REPO_ROOT / "artifacts" / "orion-qg-qg6-syndrome-rank.json"
DEFAULT_OUTPUT = REPO_ROOT / "artifacts" / "orion-qg-qg6-generic-verification.json"
TOKEN_PREFIX = "ORIONQG_QG6_GENERIC_VERIFY="


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def gf2_rank(values: Iterable[int]) -> int:
    basis: dict[int, int] = {}
    for raw in values:
        x = int(raw)
        while x:
            pivot = x.bit_length() - 1
            if pivot in basis:
                x ^= basis[pivot]
            else:
                basis[pivot] = x
                break
    return len(basis)


def sy(a: int, b: int) -> int:
    return int(p10.h.local_symp(a, b))


def mul(a: int, b: int) -> int:
    return int(p10.h.local_mul(a, b))


def wt(a: int) -> int:
    return int(p10.h.local_wt(a))


def r6m_delta(values: tuple[int, ...]) -> int:
    a0, a1, b0, b1, c0, c1, s = values
    return (
        (sy(a0, a1) << 0)
        | (sy(b0, b1) << 1)
        | (sy(c0, c1) << 2)
        | ((sy(s, a0) ^ sy(s, b0)) << 3)
        | ((sy(s, a0) ^ sy(s, c0)) << 4)
        | ((sy(s, a1) ^ sy(s, b1)) << 5)
        | ((sy(s, a1) ^ sy(s, c1)) << 6)
        | (sy(s, a0) << 7)
        | (sy(s, a1) << 8)
    )


def r6i_delta(values: tuple[int, ...]) -> int:
    a0, a1, b0, b1, s0, s1 = values
    return (
        (sy(a0, a1) << 0)
        | (sy(b0, b1) << 1)
        | ((sy(s0, a0) ^ sy(s0, b0)) << 2)
        | ((sy(s1, a0) ^ sy(s1, b0)) << 3)
        | ((sy(s0, a1) ^ sy(s0, b1)) << 4)
        | ((sy(s1, a1) ^ sy(s1, b1)) << 5)
        | (sy(s0, a0) << 6)
        | (sy(s1, a0) << 7)
        | (sy(s0, a1) << 8)
        | (sy(s1, a1) << 9)
    )


def independent_r6m() -> dict[str, Any]:
    names = ("A0", "A1", "B0", "B1", "C0", "C1")
    changes = {name: set() for name in names}
    for values in itertools.product(range(4), repeat=7):
        old = r6m_delta(values)
        for slot, name in enumerate(names):
            rewritten = list(values)
            rewritten[slot] = 0
            changes[name].add(old ^ r6m_delta(tuple(rewritten)))
    return {
        "rows": 4**7,
        "ranks": {name: gf2_rank(changes[name]) for name in names},
        "changes": {name: sorted(changes[name]) for name in names},
    }


def independent_r6i() -> dict[str, Any]:
    changes = {"A": set(), "B": set()}
    for values in itertools.product(range(4), repeat=6):
        old = r6i_delta(values)
        changes["A"].add(old ^ r6i_delta((0, 0, values[2], values[3], values[4], values[5])))
        changes["B"].add(old ^ r6i_delta((values[0], values[1], 0, 0, values[4], values[5])))
    return {
        "rows": 4**6,
        "ranks": {name: gf2_rank(changes[name]) for name in ("A", "B")},
        "changes": {name: sorted(changes[name]) for name in ("A", "B")},
    }


def independent_r6i_cost() -> dict[str, Any]:
    count = 0
    max_delta = -10**9
    violations: list[dict[str, Any]] = []
    histogram: Counter[int] = Counter()
    for central in range(3):
        multipliers = [4, 4, 4]
        multipliers[central] = 2
        for a, b in itertools.product(range(4), repeat=2):
            if a == 0 and b == 0:
                continue
            r2 = mul(a, b)
            for p0, p1, p2, s0, s1 in itertools.product(range(4), repeat=5):
                count += 1
                old = (
                    multipliers[0] * wt(a)
                    + multipliers[1] * wt(b)
                    + multipliers[2] * wt(r2)
                    + wt(mul(p0, a))
                    + wt(mul(p1, b))
                    + wt(mul(p2, r2))
                )
                new = wt(p0) + wt(p1) + wt(p2)
                delta = new - old
                histogram[delta] += 1
                max_delta = max(max_delta, delta)
                if delta > -4:
                    violations.append(
                        {
                            "central": central,
                            "a": a,
                            "b": b,
                            "p": [p0, p1, p2],
                            "s": [s0, s1],
                            "delta": delta,
                        }
                    )
    return {
        "count": count,
        "max_delta": max_delta,
        "violations": violations,
        "histogram": {str(k): v for k, v in sorted(histogram.items())},
    }


def verify_result_digest(raw: dict[str, Any]) -> bool:
    observed = raw.get("result_digest")
    unsigned = dict(raw)
    unsigned.pop("result_digest", None)
    expected = hashlib.sha256(canonical(unsigned).encode("utf-8")).hexdigest()
    return observed == expected


def run(input_path: Path) -> dict[str, Any]:
    raw = json.loads(input_path.read_text(encoding="utf-8"))
    r6m_ind = independent_r6m()
    r6i_ind = independent_r6i()
    cost_ind = independent_r6i_cost()
    r6s = json.loads(R6S_PATH.read_text(encoding="utf-8"))

    r6m_prod = raw.get("r6m", {})
    r6i_prod = raw.get("r6i", {})
    r6m_slots = r6m_prod.get("slots", {})
    r6i_blocks = r6i_prod.get("blocks", {})

    checks: dict[str, bool] = {
        "schema": raw.get("schema") == "ORION.QG.QG6.SyndromeRank.v1",
        "base_revision": raw.get("base_revision") == "164462bf7c7f3d3c2e559fa5aaf19726bb6ec388",
        "protocol_sha256": raw.get("protocol_sha256") == sha256_file(PROTOCOL_PATH),
        "result_digest": verify_result_digest(raw),
        "r6m_rows": r6m_ind["rows"] == r6m_prod.get("local_option_rows") == 16384,
        "r6i_rows": r6i_ind["rows"] == r6i_prod.get("local_option_rows") == 4096,
        "r6m_rank2": all(value == 2 for value in r6m_ind["ranks"].values()),
        "r6i_rank5": all(value == 5 for value in r6i_ind["ranks"].values()),
        "r6m_production_matches_independent": all(
            r6m_slots.get(name, {}).get("rank") == r6m_ind["ranks"][name]
            and r6m_slots.get(name, {}).get("change_vectors") == r6m_ind["changes"][name]
            for name in ("A0", "A1", "B0", "B1", "C0", "C1")
        ),
        "r6i_production_matches_independent": all(
            r6i_blocks.get(name, {}).get("rank") == r6i_ind["ranks"][name]
            and r6i_blocks.get(name, {}).get("change_vectors") == r6i_ind["changes"][name]
            for name in ("A", "B")
        ),
        "r6i_cost_count": cost_ind["count"] == 46080,
        "r6i_cost_max_delta": cost_ind["max_delta"] == -4,
        "r6i_cost_zero_violations": not cost_ind["violations"],
        "r6i_cost_matches_production": (
            r6i_prod.get("local_cost_corroboration", {}).get("case_count") == cost_ind["count"]
            and r6i_prod.get("local_cost_corroboration", {}).get("max_delta") == cost_ind["max_delta"]
            and r6i_prod.get("local_cost_corroboration", {}).get("delta_histogram") == cost_ind["histogram"]
        ),
        "r6s_receipt_hash": r6m_prod.get("r6s_binding", {}).get("receipt_sha256") == sha256_file(R6S_PATH),
        "r6s_authority": str(r6s.get("authority", "")).startswith(
            "MAX_R6S_ALL_N_COMPOSITION_THEOREM_MACHINE_CHECKED"
        ),
        "r6s_required_gates": all(
            r6s.get("gates", {}).get(key) is True
            for key in (
                "lemma_e_zero_violations",
                "lemma_b_w3_to_w8_zero_failures",
                "bindings_exact",
                "no_new_subject_data",
            )
        ),
        "r6i_promotion_still_pending": r6i_prod.get("support_theorem_status") == "PENDING_QG1_INDEPENDENT_DUAL_HARNESS",
        "no_chemistry": raw.get("chemistry_sources_read") is False,
        "no_protected_subject": raw.get("protected_subject_read") is False,
        "no_novelty_authority": raw.get("novelty_authority") is False,
    }
    decision = "ACCEPT" if all(checks.values()) else "REJECT"
    return {
        "schema": "ORION.QG.QG6.GenericVerification.v1",
        "decision": decision,
        "checks": checks,
        "r6m_independent": r6m_ind,
        "r6i_independent": r6i_ind,
        "r6i_cost_independent": cost_ind,
        "source_result_digest": raw.get("result_digest"),
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args(argv)
    result = run(Path(args.input))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TOKEN_PREFIX + canonical({"decision": result["decision"], "path": str(out)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
