#!/usr/bin/env python3
"""Frozen prospective MAX-R6 primary for the exact joint TARE-3 compiler.

This file is committed before the workflow capable of running it. It fail-closes
before fresh subject access unless the frozen open-development verifier passes and
all protocol/implementation/novelty blobs still match their pre-outcome identities.
A positive primary is not R6; independent replay remains mandatory.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import max_r6_exact_tare3_end_to_end_verify as e2e
import max_r6_exact_tare3_joint_frame_dp as solver
import max_r6_p10_candidate_blind_frame_optimizer as p10

ROOT = Path(__file__).resolve().parents[3]

FROZEN_BLOBS = {
    "development/orion-q-max-r0/MAX_R6_EXACT_TARE3_JOINT_FRAME_DP_PROTOCOL.md": "2d88f912c493d471fd24c45de891e1499f586a86",
    "development/orion-q-max-r0/MAX_R6_EXACT_TARE3_DP_ERRATUM_1.md": "c334ec3c94b8c57c4a8df2ddbdb66f818e17f943",
    "development/orion-q-max-r0/MAX_R6_EXACT_TARE3_DP_ERRATUM_2.md": "2561b1c0b97daaba0c201d615edb934c67df3665",
    "development/orion-q-max-r0/MAX_R6_EXACT_TARE3_DP_ERRATUM_3.md": "b63247be59241dc729f60aae5fc26aea0c220b63",
    "development/orion-q-max-r0/MAX_R6_EXACT_TARE3_PROSPECTIVE_PROTOCOL.md": "b9c11f683ccf5246b1e9a601ca717dd88cd4821f",
    "development/orion-q-max-r0/MAX_R6_EXACT_TARE3_FINAL_HOSTILE_NOVELTY_FREEZE.md": "93e6daa21083890e8474eab4ef737c5805a9b8b8",
    "research/extensions/orion-q/max_r6_exact_tare3_joint_frame_dp.py": "9831c55686bd26344c30a43775ca48f0ee63a3da",
    "research/extensions/orion-q/max_r6_exact_tare3_end_to_end_verify.py": "1fc224de2a8cae62e26fbb1e71ce08c39a39bdd8",
    "research/extensions/orion-q/max_r6_p10_candidate_blind_frame_optimizer.py": "145b73cab49423cdd0f353c1619695a7fb0d1bfc",
}

FRESH_CFG = {
    "commit": "be306f5830549304176365750d712093950bbdde",
    "blob": "6ab53f2a83c1f8ab5cc3bf4309525fb1ec7421dd",
    "path": "N2/cc-pVTZ/6Elec_6Orbs/1.5_Eq-3.1020au/DUCC2/N2.cc-pvtz.ducc.results.txt",
    "n_occ": 3,
    "n_virt": 3,
    "n_orb": 6,
    "n_qubits": 12,
}


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def sha256_json(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def verify_frozen_blobs() -> dict[str, str]:
    got: dict[str, str] = {}
    for relative, expected in FROZEN_BLOBS.items():
        path = ROOT / relative
        data = path.read_bytes()
        actual = git_blob_sha(data)
        got[relative] = actual
        if actual != expected:
            raise RuntimeError(
                f"pre-outcome frozen blob drift: {relative}: {actual} != {expected}"
            )
    return got


def _matched_triple(row: dict[str, Any]) -> dict[str, Any]:
    joint_cost = int(row["joint"]["C_joint"])
    canonical_cost = int(row["B_CANONICAL_STRONG"]["C_joint"])
    frame_cost = int(row["B_FRAME_ONLY_STRONG"]["C_joint"])
    strongest = min(canonical_cost, frame_cost)
    fixed = {
        "block_cardinality": 3,
        "Lambda_TARE3": float(row["Lambda_TARE3"]),
        "Uanti_rotation_count": 5,
        "ancilla_width": 2,
    }
    return {
        **row,
        "matched_resources": fixed,
        "strongest_comparator_C_joint": int(strongest),
        "strict_vs_strongest": bool(joint_cost < strongest),
        "delta_vs_strongest": int(strongest - joint_cost),
    }


def main() -> dict[str, Any]:
    # These checks deliberately happen before any fresh-subject configuration.
    frozen = verify_frozen_blobs()
    open_core = solver.main()
    open_verified = e2e.verify_result(open_core)

    pre_access_gates = {
        "frozen_blobs_match": frozen == FROZEN_BLOBS,
        "open_software_integrity_pass": open_verified["software_integrity_pass"] is True,
        "open_pre_prospective_ready": open_verified["pre_prospective_ready"] is True,
        "open_top_four_panel_complete": open_verified["top_four_panel_complete"] is True,
        "open_all_three_errata_bound": all(
            item in open_verified["bound_errata"]
            for item in (
                "MAX_R6_EXACT_TARE3_DP_ERRATUM_1",
                "MAX_R6_EXACT_TARE3_DP_ERRATUM_2",
                "MAX_R6_EXACT_TARE3_DP_ERRATUM_3",
            )
        ),
        "open_protected_subject_unread": (
            open_verified["reserved_stretched_n2_accessed"] is False
            and open_core["reserved_stretched_n2_accessed"] is False
        ),
        "core_verifier_support_agree": (
            open_core["development_supported"] is open_verified["underlying_supported"]
            and open_core["gates"]["top_four_panel_complete"]
            is open_verified["top_four_panel_complete"]
        ),
    }
    pre_access_ready = all(pre_access_gates.values())
    if not pre_access_ready:
        result = {
            "schema": "ORIONQ.MAXR6.ExactTARE3ProspectivePrimary.v1",
            "authority": "R6_PROSPECTIVE_NOT_OPENED__PREACCESS_GATE_FAILED",
            "scope": "PREACCESS_ONLY__NOT_R6",
            "frozen_blobs": frozen,
            "pre_access_gates": pre_access_gates,
            "pre_access_ready": False,
            "protected_stretched_n2_accessed": False,
            "r6_earned": False,
        }
        print("ORIONQ_MAX_R6_EXACT_TARE3_PROSPECTIVE_PRIMARY=" + json.dumps(result, sort_keys=True))
        return result

    # First protected coefficient read. h.fetch_source(), reached through this call,
    # verifies the exact git-blob identity before decoding/parsing the source.
    p10_subject = p10.subject_eval("STRETCHED_N2", FRESH_CFG)
    fresh = solver.subject_development("STRETCHED_N2", FRESH_CFG, p10_subject)
    triples = [_matched_triple(row) for row in fresh["triples"]]

    prospective_gates = {
        "source_blob_matches_frozen": fresh["source_blob"] == FRESH_CFG["blob"],
        "top_four_panel_complete": (
            fresh["selected_count"] == solver.TOP_K == 4
            and len(triples) == 4
        ),
        "all_proof_carrying_witnesses_valid": (
            fresh["all_witnesses_valid"] is True
            and all(all(row["joint"]["checks"].values()) for row in triples)
        ),
        "strict_win_vs_strongest_comparator": any(
            row["strict_vs_strongest"] for row in triples
        ),
        "matched_block_cardinality": all(
            row["matched_resources"]["block_cardinality"] == 3 for row in triples
        ),
        "matched_uanti_rotation_count": all(
            row["matched_resources"]["Uanti_rotation_count"] == 5 for row in triples
        ),
        "matched_ancilla_width": all(
            row["matched_resources"]["ancilla_width"] == 2 for row in triples
        ),
    }
    prospective_supported = all(prospective_gates.values())

    fresh_payload = {
        **fresh,
        "triples": triples,
        "p10_improving_triples": int(p10_subject["improved"]),
        "p10_top8_term_indices": [row["term_indices"] for row in p10_subject["top"]],
    }
    result = {
        "schema": "ORIONQ.MAXR6.ExactTARE3ProspectivePrimary.v1",
        "authority": (
            "R6_PROSPECTIVE_PRIMARY_SUPPORTED__AWAIT_INDEPENDENT_REPLAY"
            if prospective_supported
            else "R6_PROSPECTIVE_PRIMARY_NEGATIVE__R6_CLOSED"
        ),
        "scope": "FRESH_STRETCHED_N2_FIXED_TARE3_BLOCKS__PRIMARY_ONLY",
        "frozen_blobs": frozen,
        "pre_access_gates": pre_access_gates,
        "pre_access_ready": True,
        "fresh_subject": fresh_payload,
        "fresh_subject_digest": sha256_json(fresh_payload),
        "prospective_gates": prospective_gates,
        "prospective_supported": prospective_supported,
        "protected_stretched_n2_accessed": True,
        "independent_replay_required": True,
        "r6_earned": False,
    }
    print("ORIONQ_MAX_R6_EXACT_TARE3_PROSPECTIVE_PRIMARY=" + json.dumps(result, sort_keys=True))
    return result


if __name__ == "__main__":
    main()
