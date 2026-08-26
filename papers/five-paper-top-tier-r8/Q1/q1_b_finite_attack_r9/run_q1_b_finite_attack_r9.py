#!/usr/bin/env python3
"""Generate the immutable Q1-B finite attack, controls, and typed receipt."""

from __future__ import annotations

import hashlib
import json
import platform
from collections import Counter
from pathlib import Path
from typing import Any

import z3

from q1_b_semantic_evaluator_r9 import evaluate_witness
from q1_b_solver_r9 import (
    RESOURCE_EXHAUSTED,
    SOURCE_COMMIT,
    SOURCE_MANUSCRIPT_SHA256,
    apply_block_permutation,
    apply_coordinate_permutation,
    apply_letter_relabeling,
    apply_target_swap,
    broken_two_tag_support_control,
    declared_n3_instances,
    lower_control_instance,
    simple_support_one_instance,
    solve_instance,
    tied_optimum_witnesses,
)


HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[4]
PAPER = ROOT / "papers/Q-paper-01-tare-expressivity"
DATE = "2026-08-26"


def _canonical_bytes(payload: Any) -> bytes:
    return (json.dumps(payload, sort_keys=True, indent=2) + "\n").encode()


def _write_json(name: str, payload: Any) -> Path:
    path = HERE / name
    path.write_bytes(_canonical_bytes(payload))
    return path


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def _source_manifest() -> dict[str, Any]:
    expected = {
        "manuscript": {
            "path": "papers/Q-paper-01-tare-expressivity/MANUSCRIPT_V3_REFINED.md",
            "blob_sha": "6c4c59452397024d96cf6d103f474b7b0a07e536",
            "sha256": SOURCE_MANUSCRIPT_SHA256,
        },
        "definition": {
            "path": "papers/Q-paper-01-tare-expressivity/HUMAN_PROOF_R6S_2026-08-22.md",
            "blob_sha": "a22754e8afef0e9914b75b37f0aee673ccd2ca95",
            "sha256": "ad4f3704cfac4569b74725cb8608ed5f5ba88b847d2d8a2820b3e184d9d1dae6",
        },
        "claim_ledger": {
            "path": "papers/Q-paper-01-tare-expressivity/CLAIM_LEDGER_V3.md",
            "blob_sha": "67459ecca65f160b52af470fe6a2582f6af95ed3",
            "sha256": "f278639f2606404be4276f20dc9f17e49e5b7702f906f7a4cb4a4c46074c994a",
        },
        "nearest_work": {
            "path": "papers/Q-paper-01-tare-expressivity/NEAREST_WORK_DELTA_V3.md",
            "blob_sha": "1bb4fc5129a6fdb5203c81e10d5cc6fbde300d84",
            "sha256": "9b24ddccfed873dd2319aa2f2cafff9bc80638941fd0008b827cf57efde42b7b",
        },
    }
    for binding in expected.values():
        path = ROOT / binding["path"]
        actual = {"blob_sha": _blob_sha(path), "sha256": _sha(path)}
        if actual != {key: binding[key] for key in actual}:
            raise RuntimeError(f"source binding drift: {binding['path']}: {actual}")
    return {
        "schema": "ORION.Q1B.SourceManifestR9.v1",
        "repository": "SzeChunYiu/ORION",
        "commit_sha": SOURCE_COMMIT,
        "selected_by": "PR #1428 issuecomment-5428931879",
        "selection_authority": "BOUNDED_INTERNAL_SELECTION_NOT_EXTERNAL_AUTHORITY",
        "files": expected,
        "opaque_registered_tree_bindings_not_traversed": {
            "implementation_result_tree": "81c0d03d5f3da35c6f35dfdd6d523ac8f180847c",
            "support_one_protocol_tree": "c97cf3f12c6c9f8707bc75a9788a7e3a97352964",
        },
        "grammar_transcription": {
            "instance": "six phase-free target Paulis in three two-target blocks",
            "frames": "two nonidentity anticommuting frame Paulis per block",
            "shared_tag": "one nonidentity Tag with common branch orientation",
            "production_moves": [
                "target permutation in each block",
                "central branch choice in each block",
            ],
            "frame_objective": "sum m*(w(R)-1), central m=2 and noncentral m=4",
            "tag_objective": "2*w(S)",
            "restore": "T_jk=P_j,pi_j(k)*R_jk phase-free",
            "restore_objective": "per branch and coordinate F3=1 for three equal nonidentity letters, otherwise ordinary nonidentity count",
        },
        "forbidden_sources": {
            "registered_solver_read_or_imported": False,
            "registered_canonicalizer_read_or_imported": False,
            "registered_witness_generator_read_or_imported": False,
            "registered_support_two_checker_read_or_imported": False,
            "registered_result_receipts_read": False,
            "q1_a_work_read": False,
        },
    }


def _run_controls() -> tuple[dict[str, Any], dict[str, Any]]:
    support_one_instance = simple_support_one_instance()
    support_one = solve_instance(support_one_instance, timeout_ms=30_000)
    lower_instance = lower_control_instance()
    lower = solve_instance(lower_instance, timeout_ms=30_000)
    omitted = solve_instance(
        lower_instance, timeout_ms=30_000, allow_target_permutation=False
    )
    ties = tied_optimum_witnesses(
        lower_instance,
        support_cap=2,
        objective=int(lower["exact_optimum"]),
        limit=2,
        timeout_ms=30_000,
    )
    broken = broken_two_tag_support_control()

    orbit_inputs = {
        "letter_X_Z_swap": apply_letter_relabeling(
            lower_instance, {"I": "I", "X": "Z", "Y": "Y", "Z": "X"}
        ),
        "coordinate_reverse": apply_coordinate_permutation(lower_instance, (1, 0)),
        "block_2_0_1": apply_block_permutation(lower_instance, (2, 0, 1)),
        "first_block_target_swap": apply_target_swap(lower_instance, 0),
    }
    orbit_rows = {
        name: solve_instance(instance, timeout_ms=30_000)
        for name, instance in orbit_inputs.items()
    }
    base_signature = {
        "exact_optimum": lower["exact_optimum"],
        "minimum_support_among_optima": lower["minimum_support_among_optima"],
        "support_bounded_objectives": lower["support_bounded_objectives"],
    }
    leakage = [
        name
        for name, result in orbit_rows.items()
        if {
            "exact_optimum": result["exact_optimum"],
            "minimum_support_among_optima": result[
                "minimum_support_among_optima"
            ],
            "support_bounded_objectives": result["support_bounded_objectives"],
        }
        != base_signature
    ]

    forced_resource = solve_instance(declared_n3_instances()[0], timeout_ms=1)
    negative = {
        "schema": "ORION.Q1B.NegativeControlManifestR9.v1",
        "support_one": {
            "instance": support_one_instance.as_dict(),
            "result": support_one,
            "semantic_evaluation": evaluate_witness(
                support_one_instance, support_one["witness"]
            ),
        },
        "support_two_lower": {
            "selection": "first matching of six unique n=2 targets sampled by the source-manuscript SHA-256 prefix",
            "registered_witness_used": False,
            "instance": lower_instance.as_dict(),
            "result": lower,
            "semantic_evaluation": evaluate_witness(lower_instance, lower["witness"]),
        },
        "broken_shared_tag": broken,
        "omitted_target_permutation": {
            "full_objective": lower["exact_optimum"],
            "omitted_move_objective": omitted["exact_optimum"],
            "terminal": "OMITTED_PRODUCTION_MOVE_DEGRADES_OPTIMUM",
        },
        "objective_tie": {
            "objective": lower["exact_optimum"],
            "distinct_witnesses": len(ties),
            "witness_sha256": [row["witness_sha256"] for row in ties],
            "terminal": "OBJECTIVE_TIE_PRESERVED",
        },
        "forced_resource_exhaustion": forced_resource,
    }
    orbit = {
        "schema": "ORION.Q1B.OrbitReceiptR9.v1",
        "base_instance": lower_instance.as_dict(),
        "base_signature": base_signature,
        "global_branch_symmetry": "orientation fixed to zero; global branch exchange maps orientation one bijectively while target permutation and central choice remain explicit",
        "orbits": {
            name: {
                "instance": orbit_inputs[name].as_dict(),
                "result_signature": {
                    "exact_optimum": result["exact_optimum"],
                    "minimum_support_among_optima": result[
                        "minimum_support_among_optima"
                    ],
                    "support_bounded_objectives": result[
                        "support_bounded_objectives"
                    ],
                },
            }
            for name, result in orbit_rows.items()
        },
        "symmetry_leakage_cases": leakage,
        "terminal": "ORBIT_INVARIANCE_GREEN" if not leakage else "SYMMETRY_LEAKAGE",
    }
    return negative, orbit


def main() -> int:
    source_path = _write_json("Q1_B_SOURCE_MANIFEST_R9.json", _source_manifest())
    negative, orbit = _run_controls()
    negative_path = _write_json("Q1_B_NEGATIVE_CONTROL_MANIFEST_R9.json", negative)
    orbit_path = _write_json("Q1_B_ORBIT_RECEIPT_R9.json", orbit)

    rows = []
    semantic_disagreements = []
    exhausted = []
    support_three = []
    for instance in declared_n3_instances():
        result = solve_instance(instance, timeout_ms=120_000)
        if result["terminal"] == RESOURCE_EXHAUSTED:
            exhausted.append(instance.instance_id)
            rows.append({**instance.as_dict(), **result})
            continue
        evaluation = evaluate_witness(instance, result["witness"])
        if not evaluation["valid"] or evaluation["objective"] != result["exact_optimum"]:
            semantic_disagreements.append(instance.instance_id)
        if result["minimum_support_among_optima"] >= 3:
            support_three.append(instance.instance_id)
        rows.append(
            {
                **instance.as_dict(),
                **result,
                "semantic_evaluation": evaluation,
            }
        )

    histogram = Counter(
        str(row["minimum_support_among_optima"])
        for row in rows
        if row.get("minimum_support_among_optima") is not None
    )
    if exhausted:
        terminal = RESOURCE_EXHAUSTED
    elif semantic_disagreements:
        terminal = "SEMANTIC_EVALUATOR_DISAGREEMENT"
    elif orbit["symmetry_leakage_cases"]:
        terminal = "SYMMETRY_LEAKAGE"
    elif support_three:
        terminal = "SUPPORT3_COUNTEREXAMPLE"
    else:
        terminal = "NO_SUPPORT3_COUNTEREXAMPLE_IN_DECLARED_FINITE_DOMAIN"

    result_document = {
        "schema": "ORION.Q1B.FiniteAttackResultR9.v1",
        "source_commit": SOURCE_COMMIT,
        "finite_domain": {
            "n": 3,
            "targets": list(_source_bound_targets_for_receipt()),
            "matching_count": 15,
            "complete_over": "all perfect matchings of the six digest-selected unique targets",
        },
        "instances": rows,
        "minimum_support_histogram": dict(sorted(histogram.items())),
        "support_three_counterexamples": support_three,
        "semantic_evaluator_disagreements": semantic_disagreements,
        "resource_exhausted_instances": exhausted,
        "terminal": terminal,
    }
    result_path = _write_json("Q1_B_RESULT_R9.json", result_document)

    environment = {
        "schema": "ORION.Q1B.EnvironmentManifestR9.v1",
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "z3": z3.get_version_string(),
        "command": "python papers/five-paper-top-tier-r8/Q1/q1_b_finite_attack_r9/run_q1_b_finite_attack_r9.py",
        "solver_random_seed": 7331,
        "main_query_timeout_ms": 120000,
        "forced_resource_control_timeout_ms": 1,
    }
    environment_path = _write_json("Q1_B_ENVIRONMENT_MANIFEST_R9.json", environment)

    implementation_paths = [
        HERE / "q1_b_solver_r9.py",
        HERE / "q1_b_semantic_evaluator_r9.py",
        HERE / "run_q1_b_finite_attack_r9.py",
    ]
    result_manifest = {
        "schema": "ORION.Q1B.ResultManifestR9.v1",
        "files": {
            path.name: _sha(path)
            for path in implementation_paths + [result_path, orbit_path]
        },
        "result_terminal": terminal,
        "result_sha256": _sha(result_path),
        "orbit_sha256": _sha(orbit_path),
    }
    result_manifest_path = _write_json(
        "Q1_B_RESULT_MANIFEST_R9.json", result_manifest
    )

    receipt = {
        "schema": "ORION.Q1.FiniteAttackReceiptR9.v1",
        "source_binding": {
            "repository": "SzeChunYiu/ORION",
            "commit_sha": SOURCE_COMMIT,
            "manuscript_blob_sha": "6c4c59452397024d96cf6d103f474b7b0a07e536",
            "definition_blob_sha": "a22754e8afef0e9914b75b37f0aee673ccd2ca95",
            "claim_ledger_blob_sha": "67459ecca65f160b52af470fe6a2582f6af95ed3",
        },
        "implementation_independence": {
            "language_and_solver": f"Python {platform.python_version()} + Z3 {z3.get_version_string()} finite integer encoding",
            "registered_code_imported": False,
            "registered_canonicalizer_imported": False,
            "registered_witnesses_used_as_inputs": False,
            "neutral_interchange_only": True,
            "independence_explanation": "The R6M grammar was transcribed directly from content-bound paper definitions into fresh integer constraints. No registered implementation/result tree was traversed. A separate Z3-free evaluator recomputes every committed witness, but both implementations were authored in the same lane.",
        },
        "finite_domain": {
            "instance_generator": "six unique full-alphabet n=3 targets selected by the canonical manuscript SHA-256 prefix; deterministic recursion enumerates all perfect matchings",
            "scope_parameters": {
                "n": 3,
                "support_caps_proved": [1, 2, 3],
                "target_set_count": 1,
                "unique_targets": 6,
                "all_perfect_matchings": 15,
                "phase_free_frame_alphabet": "{I,X,Y,Z}^3 minus identity",
                "phase_free_tag_alphabet": "{I,X,Y,Z}^3 minus identity",
                "target_permutations": "all 2^3",
                "central_branch_choices": "all 2^3",
            },
            "instance_count": 15,
            "symmetry_group": "global branch exchange (orientation fixed), plus audited X/Z relabel, coordinate, block and target-swap orbits",
            "canonicalization_method": "fresh recursive perfect-matching generator and source-digest target selector; no registered canonicalizer",
            "completeness_argument": "Three qubits is the smallest qubit count on which a frame can have support three. For the one deterministically digest-selected six-target subject, every one of its 15 perfect matchings is present. Within every matching, the solver spans the full phase-free frame and Tag alphabets, every target permutation, every central-branch choice, and proves exact optima separately at support caps one, two, and three. This is complete only for that declared finite subject, not for all n=3 target sets.",
        },
        "controls": {
            "support_two_positive": negative["support_two_lower"]["result"][
                "minimum_support_among_optima"
            ]
            == 2,
            "support_one_cases": negative["support_one"]["result"][
                "minimum_support_among_optima"
            ]
            == 1,
            "support_two_lower_witnesses": negative["support_two_lower"]["result"][
                "support_bounded_objectives"
            ]
            == {"1": 8, "2": 7},
            "broken_shared_tag_negative": negative["broken_shared_tag"][
                "minimum_support"
            ]
            == 3,
            "omitted_move_negative": negative["omitted_target_permutation"][
                "omitted_move_objective"
            ]
            > negative["omitted_target_permutation"]["full_objective"],
            "objective_ties": negative["objective_tie"]["distinct_witnesses"] >= 2,
            "metamorphic_relabeling": not orbit["symmetry_leakage_cases"],
            "outside_scope_support_three": negative["broken_shared_tag"][
                "minimum_support"
            ]
            == 3,
            "resource_terminal_preserved": negative["forced_resource_exhaustion"][
                "terminal"
            ]
            == RESOURCE_EXHAUSTED,
        },
        "results": {
            "instances_checked": len(rows),
            "minimum_support_histogram": result_document[
                "minimum_support_histogram"
            ],
            "support_three_counterexamples": support_three,
            "semantic_evaluator_disagreements": semantic_disagreements,
            "solver_disagreements": [],
            "symmetry_leakage_cases": orbit["symmetry_leakage_cases"],
            "resource_exhausted_instances": exhausted,
        },
        "manifests": {
            "source_manifest_sha256": _sha(source_path),
            "result_manifest_sha256": _sha(result_manifest_path),
            "environment_manifest_sha256": _sha(environment_path),
            "negative_control_manifest_sha256": _sha(negative_path),
        },
        "terminal": terminal,
        "typed_terminal": (
            "Q1_B_NO_SUPPORT3_COUNTEREXAMPLE_IN_DECLARED_FINITE_DOMAIN__"
            "BOUNDED_CORROBORATION_ONLY"
            if terminal == "NO_SUPPORT3_COUNTEREXAMPLE_IN_DECLARED_FINITE_DOMAIN"
            else f"Q1_B_{terminal}"
        ),
        "authority": {
            "finite_domain_only": True,
            "proves_all_size_theorem": False,
            "grants_production_resource_authority": False,
            "grants_journal_authority": False,
            "same_program_independence": "CANNOT_CHECK",
            "journal_authority": "CANNOT_CHECK",
            "scientific_disposition": "BOUNDED_CORROBORATIVE_ONLY",
        },
    }
    receipt_path = _write_json("Q1_B_FINITE_ATTACK_RECEIPT_R9.json", receipt)

    sums = [
        f"{_sha(path)}  {path.name}"
        for path in sorted(
            [
                source_path,
                negative_path,
                orbit_path,
                result_path,
                environment_path,
                result_manifest_path,
                receipt_path,
                *implementation_paths,
            ],
            key=lambda path: path.name,
        )
    ]
    (HERE / "Q1_B_SHA256SUMS").write_text("\n".join(sums) + "\n")
    print(receipt["typed_terminal"])
    return 0 if terminal == "NO_SUPPORT3_COUNTEREXAMPLE_IN_DECLARED_FINITE_DOMAIN" else 3


def _source_bound_targets_for_receipt() -> tuple[str, ...]:
    first = declared_n3_instances()[0]
    return tuple(sorted(target for block in first.blocks for target in block))


if __name__ == "__main__":
    raise SystemExit(main())
