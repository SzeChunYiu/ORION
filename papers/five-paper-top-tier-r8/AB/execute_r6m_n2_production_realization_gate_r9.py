#!/usr/bin/env python3
"""Execute the fail-closed AB realization gate on the frozen R6M n=2 panel.

This is a finite application audit, not a production-transfer proof.  It binds
and replays the current R6M optimizer on the smallest registered n=2 hostile
panel, independently compares every outer configuration with the exhaustive
brute-force evaluator, and then asks the AB realization checker what authority
that computation has.  The current R6M sources define an optimizer and an
argmin, not an extensional shortening-move registry, so the certificate must
remain fail closed.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
AB_DIR = Path(__file__).resolve().parent
R6_DIR = ROOT / "research" / "extensions" / "orion-q"
sys.path.insert(0, str(R6_DIR))
sys.path.insert(0, str(AB_DIR))

import max_r6m_exact_three_tare2_shared_factor_dp as r6m  # noqa: E402
from finite_production_realization_gate_r9_v2 import check_instance  # noqa: E402

SOURCE_COMMIT = "1e18787841d99d76a3c7661505838d2eca8780db"
PANEL_NAME = "n2_a"
INPUT_SCHEMA = "ORION.AB.FiniteProductionRealizationInstanceR9.v1"

SOURCE_BINDINGS: tuple[dict[str, str], ...] = (
    {
        "role": "r6m_protocol",
        "path": "development/orion-q-max-r0/MAX_R6M_EXACT_THREE_TARE2_SHARED_FACTOR_DP_PROTOCOL.md",
        "git_blob_sha1": "48214ac16ce956a109cbce39a25d59b77eb95b3a",
        "sha256": "33465bd585f09a8d936aaa38d90beb4916943f826eb970bfeced102eeac93986",
    },
    {
        "role": "r6m_runner",
        "path": "research/extensions/orion-q/max_r6m_exact_three_tare2_shared_factor_dp.py",
        "git_blob_sha1": "ead51fc9d03e25acf3d65557cb0f08fd1eb98873",
        "sha256": "7c6579db5f4afbc1738e8b3d96aa3730023bc3831d1fc4950ab34e071c0e3d90",
    },
    {
        "role": "r6m_registered_result",
        "path": "research/extensions/orion-q/MAX_R6M_EXACT_THREE_TARE2_SHARED_FACTOR_DP_RESULTS.json",
        "git_blob_sha1": "e7b6253a74f6ffb588a09304767f0281292f9616",
        "sha256": "5f182cd6fc66d3e1a748c1ee407b020011bb40dad045ab22b0d4f1db094fcb28",
    },
    {
        "role": "support_two_protocol",
        "path": "development/orion-q-max-r0/MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_PROTOCOL.md",
        "git_blob_sha1": "b8f8b9fdf6fa8c35c5f83553436e96741514eb6c",
        "sha256": "831585f6f5f13630ecc71201450895effee532b71684776347e2de84d156af5c",
    },
    {
        "role": "support_two_runner",
        "path": "research/extensions/orion-q/max_r6p_weight2_frame_donor_closure.py",
        "git_blob_sha1": "8ba39b8b2bb082c7207c57f4dabcf4dc263b17f3",
        "sha256": "1006ab0293727ebb994b1202118bc60e779eb5432f820222c6ffbf22304d5965",
    },
    {
        "role": "support_two_registered_result",
        "path": "research/extensions/orion-q/MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_RESULTS.json",
        "git_blob_sha1": "1562625a91d177d83c49fbfd32bc790871c323e8",
        "sha256": "3eef07d16353b606a133d7fb977d5039ad1c639c7a531a47ae82be4be9051190",
    },
    {
        "role": "q1_manuscript",
        "path": "papers/Q-paper-01-tare-expressivity/MANUSCRIPT_V3_REFINED.md",
        "git_blob_sha1": "6c4c59452397024d96cf6d103f474b7b0a07e536",
        "sha256": "8522ab344c105866798ca64019f2e5bdf75f4c4445c0c6a0525a573a0c2b5377",
    },
    {
        "role": "q1_claim_ledger",
        "path": "papers/Q-paper-01-tare-expressivity/CLAIM_LEDGER_V3.md",
        "git_blob_sha1": "67459ecca65f160b52af470fe6a2582f6af95ed3",
        "sha256": "f278639f2606404be4276f20dc9f17e49e5b7702f906f7a4cb4a4c46074c994a",
    },
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def git_blob_sha1(value: bytes) -> str:
    header = f"blob {len(value)}\0".encode("ascii")
    return hashlib.sha1(header + value).hexdigest()


def verify_source_bindings() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for expected in SOURCE_BINDINGS:
        data = (ROOT / expected["path"]).read_bytes()
        observed_sha256 = sha256_bytes(data)
        observed_blob = git_blob_sha1(data)
        sha256_match = observed_sha256 == expected["sha256"]
        blob_match = observed_blob == expected["git_blob_sha1"]
        if not (sha256_match and blob_match):
            raise AssertionError(
                {
                    "source_binding_mismatch": expected["role"],
                    "expected_sha256": expected["sha256"],
                    "observed_sha256": observed_sha256,
                    "expected_git_blob_sha1": expected["git_blob_sha1"],
                    "observed_git_blob_sha1": observed_blob,
                }
            )
        rows.append(
            {
                **expected,
                "observed_sha256": observed_sha256,
                "observed_git_blob_sha1": observed_blob,
                "sha256_match": sha256_match,
                "git_blob_sha1_match": blob_match,
            }
        )
    return rows


def candidate_count_per_outer_configuration() -> tuple[int, dict[str, int]]:
    """Count every feasible (S, orientation, frame-A/B/C) tuple at n=2."""
    keys = [(x, z) for x in range(4) for z in range(4)]
    total = 0
    pair_count_histogram: dict[str, int] = {}
    for shared_tag in keys:
        if shared_tag == (0, 0):
            continue
        for orientation in ((0, 1), (1, 0)):
            pairs = [
                (r0, r1)
                for r0 in keys
                for r1 in keys
                if r6m.p10.symp(r0, r1) == 1
                and r6m.p10.symp(shared_tag, r0) == orientation[0]
                and r6m.p10.symp(shared_tag, r1) == orientation[1]
            ]
            key = str(len(pairs))
            pair_count_histogram[key] = pair_count_histogram.get(key, 0) + 1
            total += len(pairs) ** 3
    return total, dict(sorted(pair_count_histogram.items(), key=lambda row: int(row[0])))


def enumerate_outer_configuration_minima() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    target_pairs = r6m._HOSTILE_N2_PANELS[PANEL_NAME]
    terms = r6m._synthetic_terms(target_pairs)
    states: list[dict[str, Any]] = []
    cost_histogram: dict[str, int] = {}
    for perm_b, perm_c in itertools.product((0, 1), repeat=2):
        for centrals in itertools.product((0, 1), repeat=3):
            dp_cost = r6m._dp_config_cost(
                terms,
                r6m._SYNTHETIC_MATCHING,
                perm_b,
                perm_c,
                centrals,
                2,
            )
            brute_cost = r6m._brute_config_n2(
                target_pairs,
                perm_b,
                perm_c,
                centrals,
            )
            if dp_cost is None or brute_cost is None or int(dp_cost) != int(brute_cost):
                raise AssertionError(
                    {
                        "n2_dp_brute_mismatch": {
                            "panel": PANEL_NAME,
                            "perm_b": perm_b,
                            "perm_c": perm_c,
                            "centrals": centrals,
                            "dp_cost": dp_cost,
                            "brute_cost": brute_cost,
                        }
                    }
                )
            cost = int(dp_cost)
            cost_histogram[str(cost)] = cost_histogram.get(str(cost), 0) + 1
            state_id = f"{PANEL_NAME}:pb{perm_b}:pc{perm_c}:c{''.join(map(str, centrals))}"
            states.append(
                {
                    "id": state_id,
                    "feasible": True,
                    "support": cost,
                    "abstract_support": cost,
                    "semantics": "R6M_N2_A_FROZEN_TARGET_PANEL_AND_MATCHING",
                    "objective_rank": [cost],
                    "abstraction": "R6M_OUTER_CONFIGURATION_MINIMUM",
                    "outer_configuration": {
                        "relative_permutation_B": perm_b,
                        "relative_permutation_C": perm_c,
                        "centrals": list(centrals),
                    },
                    "inner_argmin": "EXHAUSTIVE_N2_GLOBAL_PAULI_FRAME_AND_SHARED_TAG_ENUMERATION",
                    "dp_cost": cost,
                    "independent_brute_cost": int(brute_cost),
                    "agreement": True,
                }
            )
    states.sort(key=lambda row: row["id"])
    if len(states) != 32:
        raise AssertionError({"outer_configuration_count": len(states), "expected": 32})
    per_outer, pair_histogram = candidate_count_per_outer_configuration()
    summary = {
        "panel": PANEL_NAME,
        "n_qubits": 2,
        "target_pairs": [[list(left), list(right)] for left, right in target_pairs],
        "matching": [list(pair) for pair in r6m._SYNTHETIC_MATCHING],
        "outer_configurations": len(states),
        "relative_permutation_configurations": 4,
        "central_configurations": 8,
        "feasible_inner_candidates_per_outer_configuration": per_outer,
        "feasible_inner_candidate_evaluations": per_outer * len(states),
        "pair_count_histogram_over_nonzero_tag_and_orientation": pair_histogram,
        "cost_histogram": dict(sorted(cost_histogram.items(), key=lambda row: int(row[0]))),
        "minimum_cost": min(row["support"] for row in states),
        "maximum_cost": max(row["support"] for row in states),
        "all_dp_brute_agree": all(row["agreement"] for row in states),
    }
    return states, summary


def build_certificate(
    source_rows: list[dict[str, Any]],
    states: list[dict[str, Any]],
    enumeration: dict[str, Any],
) -> dict[str, Any]:
    maximum = max(row["support"] for row in states)
    witnesses = [row["id"] for row in states if row["support"] == maximum]
    binding_manifest = {
        "source_commit": SOURCE_COMMIT,
        "bindings": [
            {
                "role": row["role"],
                "path": row["path"],
                "git_blob_sha1": row["git_blob_sha1"],
                "sha256": row["sha256"],
            }
            for row in source_rows
        ],
    }
    return {
        "schema": INPUT_SCHEMA,
        "instance_id": "R6M_N2_A_CURRENT_RUNNER_FAIL_CLOSED_V1",
        "claimed_weak_terminal_bound": maximum,
        "states": states,
        "weak_moves": [],
        "production_moves": [],
        "weak_terminal_witnesses": witnesses,
        "production_registry": {
            "declared_complete": False,
            "source_manifest_sha256": sha256_bytes(canonical_json(binding_manifest).encode("utf-8")),
            "completeness_argument": (
                "The bound R6M implementation exhaustively enumerates feasible candidates and returns a "
                "deterministic argmin, but it does not define an extensional shortening-move registry. "
                "Enumerating the current runner cannot prove that this missing production registry is complete."
            ),
        },
        "require_production_confluence": False,
        "source_binding": binding_manifest,
        "finite_enumeration": enumeration,
        "language_separation": {
            "abstract_support_reduction_language": "NO_REGISTERED_R6M_WEAK_SHORTENING_LANGUAGE",
            "current_r6m_computation": "FINITE_FEASIBILITY_AND_OBJECTIVE_ARGMIN",
            "production_shortening_move_registry": "ABSENT",
            "reason_no_moves_are_invented": (
                "Changing an outer optimizer choice or selecting a lower-cost candidate is not a declared "
                "semantics-preserving production rewrite."
            ),
        },
        "authority": {
            "finite_n2_runner_enumeration": True,
            "dp_vs_independent_brute_agreement": True,
            "production_registry_complete": False,
            "production_lower_transfer_established": False,
            "computed_certificate_waste_interpretable": False,
            "quantum_compiler_result": False,
            "journal_authority": False,
        },
    }


def main() -> None:
    source_rows = verify_source_bindings()
    states, enumeration = enumerate_outer_configuration_minima()
    certificate = build_certificate(source_rows, states, enumeration)
    result = check_instance(certificate)
    issue_types = sorted(row["type"] for row in result["issues"])
    expected_issues = ["PRODUCTION_REGISTRY_NOT_DECLARED_COMPLETE"]
    if issue_types != expected_issues:
        raise AssertionError({"unexpected_gate_issues": issue_types, "expected": expected_issues})
    if result["terminal"] != "FINITE_PRODUCTION_REALIZATION_CERTIFICATE_REJECTED":
        raise AssertionError({"unexpected_terminal": result["terminal"]})
    if result["authority"]["production_application_authority"] is not False:
        raise AssertionError("fail-closed certificate must not grant production application authority")

    certificate_path = AB_DIR / "R6M_N2_PRODUCTION_REALIZATION_CERTIFICATE_R9.json"
    result_path = AB_DIR / "R6M_N2_PRODUCTION_REALIZATION_GATE_R9_RESULTS.json"
    certificate_text = json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    certificate_path.write_text(certificate_text, encoding="utf-8")

    receipt = {
        **result,
        "execution_receipt": {
            "source_commit": SOURCE_COMMIT,
            "source_bindings": source_rows,
            "certificate_file": certificate_path.name,
            "certificate_file_sha256": sha256_bytes(certificate_text.encode("utf-8")),
            "enumeration": enumeration,
            "expected_issue_types": expected_issues,
            "terminal_preserved_fail_closed": True,
        },
        "authority_boundary": {
            "finite_current_runner_replay": True,
            "extensional_production_move_registry": False,
            "external_registry_completeness": False,
            "production_lower_transfer": False,
            "computed_certificate_waste_interpretable": False,
            "quantum_compiler_claim": False,
            "journal_or_novelty_authority": False,
        },
    }
    result_text = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    result_path.write_text(result_text, encoding="utf-8")
    print(result_text, end="")


if __name__ == "__main__":
    main()
