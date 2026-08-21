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
import math
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
    "development/orion-q-max-r0/MAX_R6_EXACT_TARE3_PROSPECTIVE_ERRATUM_1.md": "58947a7aa61f4fc25b82746ee23a4c1a9cc8c0a7",
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


def _terms_from_observed_source(text: str):
    """Mirror p10.load_terms from the already-observed protected source text."""
    one, two = p10.h.parse_ducc(text)
    paulis, max_imag = p10.h.jordan_wigner_paulis(one, two)
    paulis.pop((0, 0), None)
    terms = sorted(
        paulis.items(),
        key=lambda kv: (-abs(kv[1]), kv[0][0], kv[0][1]),
    )
    return terms, max_imag


def _reconstruct_original_targets(witness: dict[str, Any]) -> tuple[tuple[int, int], ...]:
    rs = tuple((int(x), int(z)) for x, z in witness["R"])
    restores = tuple((int(x), int(z)) for x, z in witness["T"])
    permutation = tuple(int(x) for x in witness["target_permutation"])
    if len(rs) != 3 or len(restores) != 3 or sorted(permutation) != [0, 1, 2]:
        raise AssertionError("malformed three-term representation witness")
    permuted = tuple(p10.mul(restores[k], rs[k]) for k in range(3))
    original: list[tuple[int, int] | None] = [None, None, None]
    for k, source_index in enumerate(permutation):
        original[source_index] = permuted[k]
    if any(item is None for item in original):
        raise AssertionError("representation witness did not reconstruct all targets")
    return tuple(item for item in original if item is not None)


def _labels_from_witness(witness: dict[str, Any]) -> tuple[int, ...]:
    raw = witness.get("labels", witness.get("control_labels"))
    if not isinstance(raw, list):
        raise AssertionError("representation witness is missing serialized control labels")
    return tuple(int(value) for value in raw)


def _derived_representation_resources(
    witness: dict[str, Any],
    coefficient_vector: tuple[float, float, float],
) -> dict[str, Any]:
    targets = _reconstruct_original_targets(witness)
    labels = _labels_from_witness(witness)
    cardinality = len(witness["R"])
    label_width = max(1, max(labels, default=0).bit_length())
    lambda_tare3 = math.sqrt(3.0) * math.sqrt(sum(value * value for value in coefficient_vector))
    return {
        "targets": [list(target) for target in targets],
        "coefficient_vector": list(coefficient_vector),
        "Lambda_TARE3_recomputed": float(lambda_tare3),
        "block_cardinality": int(cardinality),
        "Uanti_rotation_count": int(2 * cardinality - 1),
        "control_labels": list(labels),
        "control_register_width": int(label_width),
        "labels_distinct": len(labels) == cardinality and len(set(labels)) == len(labels),
        "labels_in_two_bit_space": all(0 <= label < 4 for label in labels),
    }


def _matched_triple(
    row: dict[str, Any],
    terms,
) -> dict[str, Any]:
    indices = tuple(int(i) for i in row["term_indices"])
    if len(indices) != 3 or len(set(indices)) != 3:
        raise AssertionError({"malformed_term_indices": list(indices)})
    source_targets = tuple(terms[i][0] for i in indices)
    coefficient_vector = tuple(float(terms[i][1]) for i in indices)
    lambda_recomputed = math.sqrt(3.0) * math.sqrt(
        sum(value * value for value in coefficient_vector)
    )

    candidate = _derived_representation_resources(row["joint"], coefficient_vector)
    canonical = _derived_representation_resources(
        row["B_CANONICAL_STRONG"]["witness"], coefficient_vector
    )
    frame_only = _derived_representation_resources(
        row["B_FRAME_ONLY_STRONG"], coefficient_vector
    )
    source_targets_json = [list(target) for target in source_targets]
    representations = {
        "candidate_exact_joint": candidate,
        "B_CANONICAL_STRONG": canonical,
        "B_FRAME_ONLY_STRONG": frame_only,
    }

    checks = {
        "candidate_targets_match_source": candidate["targets"] == source_targets_json,
        "canonical_targets_match_source": canonical["targets"] == source_targets_json,
        "frame_only_targets_match_source": frame_only["targets"] == source_targets_json,
        "source_lambda_matches_selected_row": math.isclose(
            lambda_recomputed,
            float(row["Lambda_TARE3"]),
            rel_tol=1e-12,
            abs_tol=1e-12,
        ),
        "all_block_cardinality_three": all(
            item["block_cardinality"] == 3 for item in representations.values()
        ),
        "all_uanti_rotation_counts_five": all(
            item["Uanti_rotation_count"] == 5 for item in representations.values()
        ),
        "all_control_widths_two": all(
            item["control_register_width"] == 2 for item in representations.values()
        ),
        "all_label_sets_well_formed": all(
            item["labels_distinct"] and item["labels_in_two_bit_space"]
            for item in representations.values()
        ),
        "all_coefficient_vectors_identical": all(
            item["coefficient_vector"] == list(coefficient_vector)
            for item in representations.values()
        ),
        "all_recomputed_lambdas_identical": all(
            math.isclose(
                item["Lambda_TARE3_recomputed"],
                lambda_recomputed,
                rel_tol=0.0,
                abs_tol=0.0,
            )
            for item in representations.values()
        ),
    }

    joint_cost = int(row["joint"]["C_joint"])
    canonical_cost = int(row["B_CANONICAL_STRONG"]["C_joint"])
    frame_cost = int(row["B_FRAME_ONLY_STRONG"]["C_joint"])
    strongest = min(canonical_cost, frame_cost)
    return {
        **row,
        "source_targets": source_targets_json,
        "source_coefficient_vector": list(coefficient_vector),
        "source_Lambda_TARE3_recomputed": float(lambda_recomputed),
        "derived_matched_resources": representations,
        "matched_resource_checks": checks,
        "matched_resources_verified": all(checks.values()),
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
        "prospective_erratum_1_bound": (
            frozen.get("development/orion-q-max-r0/MAX_R6_EXACT_TARE3_PROSPECTIVE_ERRATUM_1.md")
            == "58947a7aa61f4fc25b82746ee23a4c1a9cc8c0a7"
        ),
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
            "schema": "ORIONQ.MAXR6.ExactTARE3ProspectivePrimary.v2",
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

    # First protected coefficient read. The fetcher verifies the configured blob;
    # Erratum 1 additionally recomputes and serializes the identity actually read.
    p10.base.configure_subject(FRESH_CFG)
    observed_text = p10.h.fetch_source()
    observed_source_blob = git_blob_sha(observed_text.encode("utf-8"))
    observed_terms, observed_max_imag = _terms_from_observed_source(observed_text)

    p10_subject = p10.subject_eval("STRETCHED_N2", FRESH_CFG)
    fresh = solver.subject_development("STRETCHED_N2", FRESH_CFG, p10_subject)
    triples = [_matched_triple(row, observed_terms) for row in fresh["triples"]]

    prospective_gates = {
        "observed_source_blob_matches_frozen": observed_source_blob == FRESH_CFG["blob"],
        "top_four_panel_complete": (
            fresh["selected_count"] == solver.TOP_K == 4
            and len(triples) == 4
        ),
        "all_proof_carrying_witnesses_valid": (
            fresh["all_witnesses_valid"] is True
            and all(all(row["joint"]["checks"].values()) for row in triples)
        ),
        "all_matched_resources_derived_and_verified": (
            bool(triples) and all(row["matched_resources_verified"] for row in triples)
        ),
        "strict_win_vs_strongest_comparator": any(
            row["strict_vs_strongest"] for row in triples
        ),
    }
    prospective_supported = all(prospective_gates.values())

    fresh_payload = {
        **fresh,
        "observed_source_blob": observed_source_blob,
        "observed_source_max_imag": float(observed_max_imag),
        "triples": triples,
        "p10_improving_triples": int(p10_subject["improved"]),
        "p10_top8_term_indices": [row["term_indices"] for row in p10_subject["top"]],
    }
    result = {
        "schema": "ORIONQ.MAXR6.ExactTARE3ProspectivePrimary.v2",
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
