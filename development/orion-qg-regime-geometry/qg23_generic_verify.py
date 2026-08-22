#!/usr/bin/env python3
"""Independent generic ORION verifier for QG-23 auxiliary-support compactness."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "artifacts/orion-qg-qg23-aux-support-compactness.json"
QG7C = ROOT / "research/extensions/orion-qg/QG7C_CLASSIFICATION_RESULTS.json"
QG7F = ROOT / "research/extensions/orion-qg/QG7F_CHAIN_REPRESENTATION_AUDIT_RESULTS.json"
OUT = ROOT / "artifacts/orion-qg-qg23-generic-verification.json"
TOKEN = "ORIONQG_QG23_GENERIC="
POS = "QG23_TARE_AUXILIARY_SUPPORT_SKELETON_AT_MOST_6_ALL_N_MACHINE_CHECKED"


def canon(v):
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def valid_digest(r):
    u = {k: v for k, v in r.items() if k != "result_digest"}
    return r.get("result_digest") == hashlib.sha256(canon(u).encode()).hexdigest()


def independent_lattice():
    triples = sorted(t for t in itertools.product(range(4), repeat=3) if sum(t) == 3)
    rows = []
    for a, p, c in triples:
        tag_cap = 3 + c
        home_cap = p
        rows.append({
            "anchored": a,
            "phantom": p,
            "comm_s2": c,
            "tag_support_bound": tag_cap,
            "phantom_off_tag_home_bound": home_cap,
            "aux_support_bound": tag_cap + home_cap,
        })
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=SRC)
    ap.add_argument("--output", type=Path, default=OUT)
    x = ap.parse_args()

    src = json.loads(x.input.read_text())
    q7c = json.loads(QG7C.read_text())
    q7f = json.loads(QG7F.read_text())

    m1 = q7c.get("m1_inventory", {})
    t2 = q7c.get("t2_occupancy", {})
    cyc = q7c.get("obligations", {}).get("L4b_shape_classes", {}).get("cyclic_borrow", {})
    rows = independent_lattice()
    max_aux = max(r["aux_support_bound"] for r in rows)

    generic_parent = {
        "three_irreducible_classes": set(m1.get("irreducible_shape_counts", {})) == {"anchored", "phantom", "comm_s2"} and m1.get("unclassified_irreducible") == 0,
        "m1_and_t2_hold": m1.get("holds") is True and t2.get("holds") is True and t2.get("occupancy_failures_from_m1") == 0,
        "occupancy_vector": t2.get("per_shape_anticommuting_tag_qubits") == {"anchored": 1, "comm_s2": 2, "phantom": 1},
        "tag_cap_parent": "wt(s) <= 3 + #comm-s2" in str(t2.get("corollary", "")),
        "home_off_tag_parent": "every home carries none" in str(cyc.get("mechanism", "")),
        "cyclic_borrow_all_n": cyc.get("status") == "CLOSED_ALL_N",
    }
    hostile = {
        "qg7f_green": q7f.get("both_accept") is True and q7f.get("representation_premise_refuted") is True,
        "tag3": q7f.get("frozen_candidate", {}).get("tag_weight") == 3,
        "distinct_overlap": q7f.get("frozen_candidate", {}).get("B_comm_s2_support") == [0, 1] and q7f.get("frozen_candidate", {}).get("C_comm_s2_support") == [1, 2],
    }

    checks = {
        "source_digest": valid_digest(src),
        "source_positive": src.get("terminal") == POS and src.get("auxiliary_support_compactness_authority") is True,
        "parent_independent": all(generic_parent.values()),
        "hostile_independent": all(hostile.values()),
        "ten_triples": len(rows) == 10,
        "source_lattice_equal": src.get("shape_count_lattice") == rows,
        "max_six": max_aux == 6 and src.get("maximum_auxiliary_support") == 6,
        "identity_all_rows": all(r["aux_support_bound"] == 6 - r["anchored"] for r in rows),
        "maximizers_a0": all(r["anchored"] == 0 for r in rows if r["aux_support_bound"] == 6),
        "hostile_not_erased": src.get("overlapping_comm_s2_pairs_allowed") is True,
        "spectators_open": src.get("target_spectator_state") == "OPEN_AND_NOT_BOUNDED_BY_6",
        "authority_separated": src.get("FULL_STATE_DIMENSION_6") is False and src.get("CHAIN_ALL_N") is False and src.get("GLOBAL_BDOUBLEPRIME_COMPLETENESS") is False and src.get("FIFTH_REGIME_FOUND") is False,
        "no_external_authority": src.get("novelty_authority") is False and src.get("r6_authority") is False and src.get("physical_quantum_advantage_claim") is False,
    }
    ok = all(checks.values())
    out = {
        "schema": "ORIONQG.QG23.GenericVerification.v1",
        "decision": "ACCEPT_AUXILIARY_SUPPORT_COMPACTNESS" if ok else "REJECT",
        "all_checks": bool(ok),
        "checks": checks,
        "generic_parent_checks": generic_parent,
        "hostile_checks": hostile,
        "independent_shape_count_lattice": rows,
        "maximum_auxiliary_support": max_aux,
        "source_result_digest": src.get("result_digest"),
        "AUXILIARY_SUPPORT_COMPACTNESS": bool(ok),
        "FULL_STATE_DIMENSION_6": False,
        "CHAIN_ALL_N": False,
        "GLOBAL_BDOUBLEPRIME_COMPLETENESS": False,
        "FIFTH_REGIME_FOUND": False,
        "novelty_authority": False,
        "r6_authority": False,
        "physical_quantum_advantage_claim": False,
    }
    x.output.parent.mkdir(parents=True, exist_ok=True)
    x.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(TOKEN + canon({"decision": out["decision"], "all_checks": ok, "max_auxiliary_support": max_aux, "shape_rows": len(rows)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
