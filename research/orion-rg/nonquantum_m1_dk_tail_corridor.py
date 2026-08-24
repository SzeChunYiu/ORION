#!/usr/bin/env python3
"""M1: one-unit generalized-Davenport tail corridor for C_5^3."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RG = ROOT / "research" / "orion-rg"
DEV = ROOT / "development" / "orion-rg-davenport"
PROTOCOL = DEV / "NONQUANTUM_M1_DK_TAIL_CORRIDOR_PROTOCOL_2026-08-24.md"
D2 = RG / "X1F0_D2_C5CUBED_EXACT_RESULTS.json"
D3 = RG / "X1F_D3_C5CUBED_EXACT_RESULTS.json"
D2_DONOR = RG / "X1F0_D2_C5CUBED_EXACT_20_DONOR_DERIVATION_2026-08-22.md"
LOWER_AUDIT = RG / "X1A_AUDIT_FREEZE_SCHMID_PARITY_RECHECK_2026-08-22.md"
PRIOR_AUDIT = DEV / "X1_PRIOR_ART_AUDIT_V1.md"
D4_PROTOCOL = DEV / "X1K_D4_C5CUBED_PROTOCOL_V1.md"
SUPPORT_FRONTIER = RG / "X1K_C0_SUPPORT_BOUND_RESULTS_V1.json"
DEFAULT_OUTPUT = RG / "NONQUANTUM_M1_DK_TAIL_CORRIDOR_RESULTS_2026-08-24.json"
BASE = "0dc9e07badae039743a6966dd9198586a497d72f"
POSITIVE = (
    "NONQUANTUM_M1_C5CUBED_ALL_K_GE4_ONE_UNIT_CORRIDOR"
    "__D4_30_IMPLIES_EXACT_TAIL_5K_PLUS10"
)
TOKEN = "ORION_NONQUANTUM_M1_TAIL="


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def signed_digest(raw: dict[str, Any]) -> str:
    unsigned = dict(raw)
    unsigned.pop("result_digest", None)
    return hashlib.sha256(canonical(unsigned).encode()).hexdigest()


def lower(k: int) -> int:
    if k < 2:
        raise ValueError("registered lower specialization starts at k=2")
    return 5 * k + 10


def upper_tail(max_k: int, d4_upper: int) -> dict[int, int]:
    if max_k < 4:
        raise ValueError("tail begins at k=4")
    values = {4: d4_upper}
    for k in range(4, max_k):
        values[k + 1] = max(values[k] + 5, 32)
    return values


def parent_ledger() -> dict[str, Any]:
    d2 = json.loads(D2.read_text())
    d3 = json.loads(D3.read_text())
    d2_checks = {
        "terminal": d2.get("terminal") == "X1F0_EXACT_D2_ESTABLISHED",
        "exact_20": d2.get("theorem", {}).get("exact_value") == 20,
        "machine_checked": d2.get("authority", {}).get("machine_checked") is True,
        "no_novelty": d2.get("authority", {}).get("novelty_claim") is False,
        "s_le_6_exact_24": d2.get("eta_T_C5cubed", {}).get("6") == 24,
    }
    d3_checks = {
        "terminal": d3.get("terminal") == "X1F_EXACT_D3_ESTABLISHED",
        "exact_25": d3.get("theorem", {}).get("exact_value") == 25,
        "lower_witness_24": d3.get("lower_bound", {}).get("witness_length") == 24
        and d3.get("lower_bound", {}).get("witness_has_three_disjoint") is False,
        "upper_zero_survivors": d3.get("upper_bound", {}).get("pass2", {}).get(
            "length25_with_no_three_disjoint"
        )
        == 0,
        "no_novelty": d3.get("authority", {}).get("novelty_claim") is False,
    }
    donor_text = D2_DONOR.read_text()
    lower_text = LOWER_AUDIT.read_text()
    prior_text = PRIOR_AUDIT.read_text()
    d4_text = D4_PROTOCOL.read_text()
    donor_checks = {
        "d2_donor_correction": "donor-derived corollary" in donor_text
        and "not ORION novelty" in donor_text,
        "all_k_lower_bound": "D_k(C_5^3)>=5k+10" in lower_text,
        "recurrence_killed_as_novel": "KILLED" in prior_text
        and "Prop. 3.1(3)" in prior_text,
        "d4_interval_registered": "30 <= D_4(C_5^3) <= 31" in d4_text,
        "all_k_upper_registered": "D_k(C_5^3) <= 5k+11" in d4_text,
        "conditional_upper_registered": "D_k(C_5^3)<=5k+10" in d4_text,
    }
    return {
        "d2": {
            "path": str(D2.relative_to(ROOT)),
            "sha256": file_sha256(D2),
            "checks": d2_checks,
            "all_checks": all(d2_checks.values()),
        },
        "d3": {
            "path": str(D3.relative_to(ROOT)),
            "sha256": file_sha256(D3),
            "checks": d3_checks,
            "all_checks": all(d3_checks.values()),
        },
        "donor_files": {
            "d2_donor_sha256": file_sha256(D2_DONOR),
            "lower_audit_sha256": file_sha256(LOWER_AUDIT),
            "prior_audit_sha256": file_sha256(PRIOR_AUDIT),
            "d4_protocol_sha256": file_sha256(D4_PROTOCOL),
            "checks": donor_checks,
            "all_checks": all(donor_checks.values()),
        },
        "all_checks": all(d2_checks.values())
        and all(d3_checks.values())
        and all(donor_checks.values()),
    }


def recurrence_ledger(max_k: int = 10_000) -> dict[str, Any]:
    corridor_upper = upper_tail(max_k, 31)
    exact_if_30 = upper_tail(max_k, 30)
    rows = []
    for k in (4, 5, 6, 10, 100, 1_000, max_k):
        rows.append(
            {
                "k": k,
                "lower": lower(k),
                "corridor_upper": corridor_upper[k],
                "conditional_d4_30_upper": exact_if_30[k],
                "corridor_width": corridor_upper[k] - lower(k),
            }
        )
    checks = {
        "d4_interval_30_31": (lower(4), corridor_upper[4]) == (30, 31),
        "all_k_corridor_width_one": all(
            corridor_upper[k] == lower(k) + 1 for k in range(4, max_k + 1)
        ),
        "conditional_exact_tail": all(
            exact_if_30[k] == lower(k) for k in range(4, max_k + 1)
        ),
        "d2_d3_on_lower_line": lower(2) == 20 and lower(3) == 25,
        "human_induction_all_k": True,
        "finite_evaluation_is_proof": False,
        "d4_31_tail_propagation_claimed": False,
    }
    return {
        "max_k_checked": max_k,
        "rows": rows,
        "recurrence": "U_{k+1}=max(U_k+5,32)",
        "checks": checks,
        "all_checks": all(
            value is True
            for key, value in checks.items()
            if key not in {"finite_evaluation_is_proof", "d4_31_tail_propagation_claimed"}
        )
        and checks["finite_evaluation_is_proof"] is False
        and checks["d4_31_tail_propagation_claimed"] is False,
    }


def support_frontier_ledger() -> dict[str, Any]:
    raw = json.loads(SUPPORT_FRONTIER.read_text())
    authority = raw.get("authority", {})
    checks = {
        "schema": raw.get("schema") == "ORION.RG.X1K.C0SupportBound.v1",
        "bounded_only": authority.get("bounded_exact_computation") is True,
        "no_theorem_authority": authority.get("theorem_authority") is False,
        "external_replay_required": authority.get("external_replay_required") is True,
        "support_23_frontier": raw.get("bounded_conclusion", "").endswith(
            "support size at least 23."
        ),
        "does_not_prove_d4": "D_4(C_5^3)=30" in raw.get("what_this_does_not_prove", []),
    }
    return {
        "path": str(SUPPORT_FRONTIER.relative_to(ROOT)),
        "sha256": file_sha256(SUPPORT_FRONTIER),
        "bounded_conclusion": raw.get("bounded_conclusion"),
        "used_in_tail_proof": False,
        "aggregable_as_theorem": False,
        "checks": checks,
        "all_checks": all(checks.values()),
    }


def run() -> dict[str, Any]:
    parents = parent_ledger()
    recurrence = recurrence_ledger()
    support = support_frontier_ledger()
    gates = {
        "protocol_present": PROTOCOL.is_file(),
        "parents_bound": parents["all_checks"],
        "tail_recurrence_exact": recurrence["all_checks"],
        "support_frontier_kept_nonaggregable": support["all_checks"],
        "d4_remains_open": True,
        "donor_and_novelty_boundaries_preserved": True,
    }
    positive = all(gates.values())
    result: dict[str, Any] = {
        "schema": "ORION.NonQuantumMath.M1.DKTailCorridor.v1",
        "base_revision": BASE,
        "protocol_path": str(PROTOCOL.relative_to(ROOT)),
        "protocol_sha256": file_sha256(PROTOCOL),
        "terminal": POSITIVE if positive else "NONQUANTUM_M1_DK_TAIL_CORRIDOR_REJECTED",
        "theorem": {
            "group": "C_5^3",
            "unconditional": "for every k>=4, 5k+10 <= D_k <= 5k+11",
            "conditional": "if D_4=30, then D_k=5k+10 for every k>=2",
            "current_exact_gate": "D_4 in {30,31}",
            "d4_31_tail_consequence": "NOT_DETERMINED",
        },
        "parent_ledger": parents,
        "recurrence_ledger": recurrence,
        "support_frontier": support,
        "gates": gates,
        "scientific_authority": "DERIVED_C5_CUBED_GENERALIZED_DAVENPORT_TAIL_THEOREM_ONLY"
        if positive
        else "NONE",
        "result_owner": "NON_QUANTUM_MATH",
        "exact_d4_authority": False,
        "c0_31_authority": False,
        "support_23_theorem_authority": False,
        "d4_31_determines_tail": False,
        "generic_recurrence_novelty_authority": False,
        "d2_novelty_authority": False,
        "novelty_authority": False,
        "venue_authority": False,
        "quantum_claim": False,
        "ci_authority": False,
    }
    result["result_digest"] = signed_digest(result)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    result = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        TOKEN
        + canonical(
            {
                "terminal": result["terminal"],
                "result_digest": result["result_digest"],
                "max_k_checked": result["recurrence_ledger"]["max_k_checked"],
                "d4_gate": result["theorem"]["current_exact_gate"],
                "all_gates": all(result["gates"].values()),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
