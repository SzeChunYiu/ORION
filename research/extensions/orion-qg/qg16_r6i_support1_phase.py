#!/usr/bin/env python3
"""QG-16: objective-indexed all-n support1 phase for frozen R6I.

The protocol was frozen before this checker ran.  The checker derives the
objective cone from exact local resource vectors rather than copying the
registered half-spaces.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
ORION_Q = ROOT / "research/extensions/orion-q"
sys.path.insert(0, str(ORION_Q))

import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import max_r6i_exact_rank2_shared_tag_dp as r6i  # noqa: E402

ISSUE = "SzeChunYiu/ORION#811"
PROTOCOL = ROOT / "development/orion-qg-regime-geometry/QG16_R6I_SUPPORT1_PHASE_PROTOCOL_V1.md"
V6_RECEIPT = ROOT / "development/orion-qg-regime-geometry/QG9_V6_PROTECTED_RUN_RECEIPT_2026-08-21.json"
V6_RESULT = ROOT / "research/extensions/orion-qg/QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json"
SUPPORT2_RECEIPT = ROOT / "development/orion-qg-regime-geometry/QG9_SUPPORT2_PROTECTED_RUN_RECEIPT_2026-08-21.json"
DEFAULT_OUT = ROOT / "artifacts/orion-qg-qg16-r6i-support1-phase.json"
TOKEN = "ORIONQG_QG16="

LETTERS = range(4)
MUL = [[int(r6i._MUL[a, b]) for b in LETTERS] for a in LETTERS]
SY = [[int(r6i._SYMP[a, b]) for b in LETTERS] for a in LETTERS]
LW = [int(r6i._LW[a]) for a in LETTERS]
ANTI_BASES = tuple((a, b) for a in (1, 2, 3) for b in (1, 2, 3) if a != b)


def canonical(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def mul(a: int, b: int) -> int:
    return MUL[a][b]


def symp(a: int, b: int) -> int:
    return SY[a][b]


def wt(a: int) -> int:
    return LW[a]


def local_frame(a: int, b: int):
    return a, b, mul(a, b)


def restore_delta_zeroing(p: tuple[int, int, int], a: int, b: int) -> int:
    r = local_frame(a, b)
    old = sum(wt(mul(p[k], r[k])) for k in range(3))
    new = sum(wt(p[k]) for k in range(3))
    return new - old


def commuting_resource_domain() -> dict[str, Any]:
    rows = []
    witnesses: dict[tuple[int, int, int], dict[str, Any]] = {}
    for a, b in itertools.product(LETTERS, repeat=2):
        if a == b == 0 or symp(a, b) != 0:
            continue
        r = local_frame(a, b)
        active = tuple(k for k in range(3) if r[k] != 0)
        if len(active) != 2:
            raise AssertionError({"commuting_active_branch_count": [a, b, r, active]})
        for p in itertools.product(LETTERS, repeat=3):
            dr = restore_delta_zeroing(p, a, b)
            for central in range(3):
                rc = int(central in active)
                rn = len(active) - rc
                v = (rc, rn, dr)
                row = {
                    "a": a,
                    "b": b,
                    "frame": list(r),
                    "targets": list(p),
                    "central": central,
                    "refund_c": rc,
                    "refund_nc": rn,
                    "delta_restore": dr,
                }
                rows.append(row)
                witnesses.setdefault(v, row)

    vectors = sorted(set((r["refund_c"], r["refund_nc"], r["delta_restore"]) for r in rows))

    # w is uniformly worse/equal than v for nonnegative (t_c,t_nc,t_r) when
    # it refunds no more frame support and incurs no less Restore increase.
    worst = []
    for v in vectors:
        dominated_by_worse = False
        for w in vectors:
            if w == v:
                continue
            if w[0] <= v[0] and w[1] <= v[1] and w[2] >= v[2] and (w[0] < v[0] or w[1] < v[1] or w[2] > v[2]):
                dominated_by_worse = True
                break
        if not dominated_by_worse:
            worst.append(v)

    worst = sorted(worst)
    return {
        "domain_size": len(rows),
        "expected_domain_1728": len(rows) == 1728,
        "resource_vector_count": len(vectors),
        "all_vectors": [list(v) for v in vectors],
        "worst_vectors": [list(v) for v in worst],
        "worst_vector_witnesses": {str(v): witnesses[v] for v in worst},
        "expected_two_worst_vectors": worst == [(0, 2, 2), (1, 1, 2)],
        "max_restore_delta": max(r["delta_restore"] for r in rows),
        "min_restore_delta": min(r["delta_restore"] for r in rows),
    }


def alignment_resource_domain() -> dict[str, Any]:
    total = 0
    max_dr = -999
    frame_zero = True
    witness = None
    for old in ANTI_BASES:
        ro = local_frame(*old)
        for new in ANTI_BASES:
            rn = local_frame(*new)
            for p in itertools.product(LETTERS, repeat=3):
                for central in range(3):
                    # Every branch is nonidentity for both anticommuting bases.
                    m = [4, 4, 4]
                    m[central] = 2
                    old_frame = sum(m[k] * wt(ro[k]) for k in range(3))
                    new_frame = sum(m[k] * wt(rn[k]) for k in range(3))
                    frame_zero &= old_frame == new_frame == 10
                    old_restore = sum(wt(mul(p[k], ro[k])) for k in range(3))
                    new_restore = sum(wt(mul(p[k], rn[k])) for k in range(3))
                    dr = new_restore - old_restore
                    total += 1
                    if dr > max_dr:
                        max_dr = dr
                        witness = {"old": list(old), "new": list(new), "targets": list(p), "central": central, "delta_restore": dr}
    return {
        "domain_size": total,
        "expected_domain_6912": total == 6912,
        "frame_coordinate_delta_zero": frame_zero,
        "max_delta_restore": max_dr,
        "max_is_3": max_dr == 3,
        "max_witness": witness,
    }


def support2_core_audit() -> dict[str, Any]:
    expected = {1: 6, 2: 120, 3: 666, 4: 1968}
    rows = {}
    all_one = True
    for n in range(1, 5):
        keys = [(x, z) for x in range(1 << n) for z in range(1 << n) if (x, z) != (0, 0) and p10.wt((x, z)) <= 2]
        pairs = [(a, b) for a in keys for b in keys if p10.symp(a, b) == 1]
        hist: dict[int, int] = {}
        for a, b in pairs:
            la = p10.codes(a, n)
            lb = p10.codes(b, n)
            k = sum(int(symp(la[q], lb[q]) == 1) for q in range(n))
            hist[k] = hist.get(k, 0) + 1
            all_one &= k == 1
        rows[str(n)] = {"pair_count": len(pairs), "expected_pair_count": expected[n], "anti_core_count_histogram": {str(k): v for k, v in sorted(hist.items())}}
    return {"rows": rows, "all_pair_counts_match": all(rows[str(n)]["pair_count"] == expected[n] for n in expected), "every_pair_exactly_one_anti_core": all_one}


def parent_bindings() -> dict[str, Any]:
    v6r = json.loads(V6_RECEIPT.read_text())
    v6 = json.loads(V6_RESULT.read_text())
    s2 = json.loads(SUPPORT2_RECEIPT.read_text())
    checks = {
        "v6_terminal": v6r.get("terminal") == "QG9_RANK2_ALL_N_SUPPORT1_SUFFICIENCY_MACHINE_CHECKED",
        "v6_both_accept": v6r.get("both_accept") is True,
        "v6_support_bound": v6r.get("support_bound") == 1 and v6r.get("intrinsic_support_number") == 1,
        "v6_result_terminal": v6.get("terminal") == "QG9_RANK2_ALL_N_SUPPORT1_SUFFICIENCY_MACHINE_CHECKED",
        "v6_unit_constants": v6.get("finite_lemmas", {}).get("deletion", {}).get("max_delta_commuting") == -4 and v6.get("finite_lemmas", {}).get("core_alignment", {}).get("max_restore_increase") == 3 and v6.get("finite_lemmas", {}).get("distinct_qubit_tag", {}).get("minimum_cost_all_basis_pairs") == 8 and v6.get("finite_lemmas", {}).get("original_feasible_tag_cost_floor") == 4,
        "support2_terminal": s2.get("terminal") == "QG9_RANK2_ALL_N_SUPPORT2_SUFFICIENCY_MACHINE_CHECKED" and s2.get("both_accept") is True,
    }
    return {
        "checks": checks,
        "all_bound": all(checks.values()),
        "v6_receipt_sha256": sha(V6_RECEIPT),
        "v6_result_sha256": sha(V6_RESULT),
        "support2_receipt_sha256": sha(SUPPORT2_RECEIPT),
    }


def derive_facets(worst_vectors: list[list[int]], alignment_restore: int, tag_extra_support: int) -> list[dict[str, Any]]:
    facets = []
    for rc, rn, dr in worst_vectors:
        # credit >= alignment_restore * t_r
        coeff_align = {"t_c": rc, "t_nc": rn, "t_tag": 0, "t_r": -(dr + alignment_restore)}
        # credit >= tag_extra_support * t_tag
        coeff_tag = {"t_c": rc, "t_nc": rn, "t_tag": -tag_extra_support, "t_r": -dr}
        facets.append({"kind": "ALIGNMENT", "resource_vector": [rc, rn, dr], "coefficients_ge_zero": coeff_align})
        facets.append({"kind": "TAG_RELOCATION", "resource_vector": [rc, rn, dr], "coefficients_ge_zero": coeff_tag})
    facets.sort(key=lambda x: (x["kind"], x["resource_vector"]))
    return facets


def expected_facets() -> list[dict[str, int]]:
    return sorted([
        {"t_c": 1, "t_nc": 1, "t_tag": 0, "t_r": -5},
        {"t_c": 0, "t_nc": 2, "t_tag": 0, "t_r": -5},
        {"t_c": 1, "t_nc": 1, "t_tag": -2, "t_r": -2},
        {"t_c": 0, "t_nc": 2, "t_tag": -2, "t_r": -2},
    ], key=lambda d: (d["t_c"], d["t_nc"], d["t_tag"], d["t_r"]))


def frac(v: int, d: int = 1) -> Fraction:
    return Fraction(v, d)


def margin(coeff: dict[str, int], theta: dict[str, Fraction]) -> Fraction:
    return sum(Fraction(coeff[k]) * theta[k] for k in ("t_c", "t_nc", "t_tag", "t_r"))


def fjson(x: Fraction) -> dict[str, int]:
    return {"numerator": x.numerator, "denominator": x.denominator}


def classify_controls(facets: list[dict[str, Any]]) -> dict[str, Any]:
    controls = {
        "O0": {"t_nc": frac(4), "t_c": frac(2), "t_tag": frac(2), "t_r": frac(1)},
        "O_in": {"t_nc": frac(5), "t_c": frac(3), "t_tag": frac(2), "t_r": frac(1)},
        "O_tag_out": {"t_nc": frac(4), "t_c": frac(2), "t_tag": frac(5, 2), "t_r": frac(1)},
        "O_restore_out": {"t_nc": frac(4), "t_c": frac(2), "t_tag": frac(2), "t_r": frac(5, 4)},
        "O_nc_out": {"t_nc": frac(3, 2), "t_c": frac(3, 2), "t_tag": frac(1), "t_r": frac(1)},
    }
    out = {}
    for name, theta in controls.items():
        ms = [margin(f["coefficients_ge_zero"], theta) for f in facets]
        out[name] = {
            "theta": {k: fjson(v) for k, v in theta.items()},
            "facet_margins": [fjson(v) for v in ms],
            "inside": all(v >= 0 for v in ms),
            "strict_interior": all(v > 0 for v in ms),
            "on_boundary": any(v == 0 for v in ms) and all(v >= 0 for v in ms),
            "minimum_margin": fjson(min(ms)),
        }
    return out


def simplified_under_central_cheaper(facets: list[dict[str, Any]]) -> dict[str, Any]:
    # Under t_c <= t_nc, 2*t_nc >= t_c+t_nc.  Therefore for identical RHS,
    # the (0,2,...) facets are implied by the (1,1,...) facets.
    kept = [f for f in facets if f["resource_vector"][:2] == [1, 1]]
    removed = [f for f in facets if f["resource_vector"][:2] == [0, 2]]
    return {
        "assumption": "t_c <= t_nc",
        "kept_coefficients": [f["coefficients_ge_zero"] for f in kept],
        "removed_as_redundant": [f["coefficients_ge_zero"] for f in removed],
        "proof": "2*t_nc >= t_c+t_nc under t_c<=t_nc, with identical right-hand obligations",
        "valid": len(kept) == 2 and len(removed) == 2,
    }


def main() -> int:
    resources = commuting_resource_domain()
    alignment = alignment_resource_domain()
    cores = support2_core_audit()
    parents = parent_bindings()
    facets = derive_facets(resources["worst_vectors"], alignment["max_delta_restore"], 2)
    facet_coeffs = sorted([f["coefficients_ge_zero"] for f in facets], key=lambda d: (d["t_c"], d["t_nc"], d["t_tag"], d["t_r"]))
    controls = classify_controls(facets)
    simple = simplified_under_central_cheaper(facets)

    gates = {
        "protocol_present": PROTOCOL.is_file(),
        "parents_bound": parents["all_bound"],
        "commuting_domain_1728": resources["expected_domain_1728"],
        "two_worst_resource_vectors": resources["expected_two_worst_vectors"],
        "restore_delta_max2": resources["max_restore_delta"] == 2,
        "alignment_domain_6912": alignment["expected_domain_6912"],
        "alignment_frame_delta_zero": alignment["frame_coordinate_delta_zero"],
        "alignment_max3": alignment["max_is_3"],
        "support2_pair_counts": cores["all_pair_counts_match"],
        "exactly_one_anti_core": cores["every_pair_exactly_one_anti_core"],
        "four_facets_derived": len(facets) == 4 and facet_coeffs == expected_facets(),
        "simplification_valid_under_tc_le_tnc": simple["valid"],
        "O0_inside_on_boundary": controls["O0"]["inside"] and controls["O0"]["on_boundary"],
        "Oin_strict": controls["O_in"]["strict_interior"],
        "Otag_out": not controls["O_tag_out"]["inside"],
        "Orestore_out": not controls["O_restore_out"]["inside"],
        "Onc_out": not controls["O_nc_out"]["inside"],
    }

    terminal = "QG16_R6I_OBJECTIVE_INDEXED_SUPPORT1_CONE_ALL_N_MACHINE_CHECKED" if all(gates.values()) else "QG16_R6I_SUPPORT1_PHASE_CERTIFICATE_GAP"
    result = {
        "schema": "ORION.QG.QG16.R6ISupport1Phase.v1",
        "issue": ISSUE,
        "protocol_sha256": sha(PROTOCOL),
        "parent_bindings": parents,
        "commuting_deletion_resources": resources,
        "core_alignment_resources": alignment,
        "support2_core_audit": cores,
        "composition_obligations": {"alignment_restore_units": 3, "additional_tag_support_units": 2},
        "facets": facets,
        "full_cone_coefficients_ge_zero": facet_coeffs,
        "simplified_under_central_cheaper": simple,
        "controls": controls,
        "unit_objective_tag_facet_margin": controls["O0"]["minimum_margin"],
        "global_phase_boundary_sharpness": "OPEN",
        "outside_cone_semantics": "THIS_PROOF_CERTIFICATE_DOES_NOT_APPLY__NOT_SUPPORT2_REQUIRED",
        "support_bound_inside_cone": 1,
        "intrinsic_support_number_inside_cone": 1,
        "gates": gates,
        "terminal": terminal,
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
        "chemistry_sources_read": False,
        "protected_subject_read": False,
        "network_access": False,
    }
    result["result_digest"] = hashlib.sha256(canonical(result).encode()).hexdigest()
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default=str(DEFAULT_OUT))
    ns = ap.parse_args()
    p = Path(ns.output)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(TOKEN + canonical({"terminal": terminal, "result_digest": result["result_digest"], "worst_vectors": resources["worst_vectors"], "all_gates": all(gates.values()), "O0": controls["O0"], "O_in": controls["O_in"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
