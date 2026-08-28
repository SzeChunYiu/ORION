#!/usr/bin/env python3
"""Build the bounded ORION-05/06 recorded-negative revival ledger."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FIRST_BUNDLE_REL = Path(
    "development/orion-05-06-negative-revival-r1-2026-08-27/evidence/"
    "run-506b84e6c47558764b95f4482ce6691bb3757723-v2"
)
SECOND_BUNDLE_REL = Path(
    "development/orion-05-06-negative-revival-r1-2026-08-27/evidence/"
    "run-e9d4ee1df73ff22fb5742ff2cd9c200b0a5f29f9-v1"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _evidence(root: Path, relative: Path) -> dict[str, str]:
    return {"path": relative.as_posix(), "sha256": sha256_file(root / relative)}


def _authority() -> dict[str, bool]:
    return {
        "prospective_confirmation": False,
        "external_independence": False,
        "novelty": False,
        "journal_or_submission": False,
        "final_freeze": False,
    }


def build(root: Path = ROOT) -> dict[str, Any]:
    root = Path(root).resolve()
    first = root / FIRST_BUNDLE_REL
    second = root / SECOND_BUNDLE_REL
    r13 = json.loads((first / "r13/result/ORION05_R13_RESULT.json").read_text())
    xover = json.loads(
        (first / "xover/result/ORION05_XOVER_BUDGET_REVIVAL_RESULT.json").read_text()
    )
    coverage = json.loads(
        (first / "o06/ORION06_NEGATIVE_COVERAGE_AUDIT.json").read_text()
    )
    new_resources = json.loads(
        (second / "results/ORION06_NEW_RESOURCE_REVIVAL.json").read_text()
    )
    replays = json.loads(
        (second / "results/ORION06_METHOD_LANGUAGE_REPLAYS.json").read_text()
    )
    coverage_by_id = {row["id"]: row for row in coverage["standalone_rows"]}
    new_by_id = new_resources["attempts"]

    rows: list[dict[str, Any]] = [
        {
            "paper": "ORION-05",
            "negative_id": "R12_EXACT_BUT_NO_PRODUCTION_VALUE",
            "mechanism_stage": "CANDIDATE_ENUMERATION_ORDER",
            "strongest_parent": "unrestricted 512-state exact DP referee",
            "lever": "parent-certificate-guided first-candidate ordering with parent cost charged",
            "attempt_kind": "PROSPECTIVELY_FROZEN_HELDOUT_RETEST",
            "revival_outcome": "IMPROVED_COMPLETION_ONLY",
            "evidence": _evidence(
                root,
                FIRST_BUNDLE_REL / "r13/result/ORION05_R13_RESULT.json",
            ),
            "job_ids": ["3550007"],
            "mechanistic_result": (
                "24/24 held-out H4/N2 cells completed at the exact parent cost; "
                "the parent is required and its runtime is charged"
            ),
            "original_negative_preserved": r13["r12_null_preserved"],
            "residual_boundary": (
                "standalone production value remains false; this is completion repair, "
                "not acceleration or external value"
            ),
            "classification": "SAVE_WORTHY_NEGATIVE_REPAIRED_WITHOUT_AUTHORITY_PROMOTION",
            "authority": _authority(),
        },
        {
            "paper": "ORION-05",
            "negative_id": "PR1498_XOVER_N6_TIMEOUT_FRONTIER",
            "mechanism_stage": "EXHAUSTIVE_SEARCH_COMPUTE_BUDGET",
            "strongest_parent": "unrestricted exact DP referee on the identical target cell",
            "lever": "unchanged legacy direct D++ with a matched 3x wall budget",
            "attempt_kind": "FROZEN_MATCHED_BUDGET_RETEST",
            "revival_outcome": xover["revival_outcome"],
            "evidence": _evidence(
                root,
                FIRST_BUNDLE_REL
                / "xover/result/ORION05_XOVER_BUDGET_REVIVAL_RESULT.json",
            ),
            "job_ids": ["3550008"],
            "mechanistic_result": (
                "the exact parent returned cost 19, while legacy direct D++ timed out "
                "again after 1800 seconds"
            ),
            "original_negative_preserved": (
                xover["original_verdict_preserved"] == "RUN_INCOMPLETE"
            ),
            "residual_boundary": (
                "one frozen n=6 cell is budget evidence only; it is not a universal "
                "infeasibility proof or a whole-panel crossover"
            ),
            "classification": "RETAINED_NEGATIVE",
            "authority": _authority(),
        },
    ]

    for negative_id in (
        "R2_KNOWN_OPERATOR_TRANSFER",
        "R3B_JOINT_OBLIGATION_BINDING",
        "N1C_TYPED_FAILURE_STATE",
    ):
        source = coverage_by_id[negative_id]
        rows.append(
            {
                "paper": "ORION-06",
                "negative_id": negative_id,
                "mechanism_stage": source["mechanism_stage"],
                "strongest_parent": source["strongest_parent_or_comparator"],
                "lever": "the recorded exact strongest-parent comparison itself",
                "attempt_kind": "ALREADY_EXECUTED_EXACT_PARENT_OR_DONOR_SUBTRACTION",
                "revival_outcome": "RETAINED_NEGATIVE",
                "evidence": {
                    "path": source["artifact"],
                    "sha256": source["artifact_sha256"],
                },
                "job_ids": [],
                "mechanistic_result": source["mechanistic_disposition"],
                "original_negative_preserved": True,
                "residual_boundary": (
                    "no additional same-claim lever remains after exact parent/donor "
                    "equivalence; a new experiment would require a different claim"
                ),
                "classification": "CORRECT_SUBTRACTION_OR_PARENT_SUFFICIENT",
                "authority": _authority(),
            }
        )

    for negative_id, job_id in (
        ("R4C_H2_REGIME_LIMITED", "3550252"),
        ("R5B_PROOF_OUTER_REPLAY", "3550252"),
    ):
        source = coverage_by_id[negative_id]
        result = new_by_id[negative_id]
        rows.append(
            {
                "paper": "ORION-06",
                "negative_id": negative_id,
                "mechanism_stage": result["mechanism_stage"],
                "strongest_parent": next(
                    row["strongest_parent"]
                    for row in json.loads(
                        (
                            root
                            / "papers/orion-06-recursive-recovery/revival/"
                            "ORION06_NEGATIVE_REVIVAL_R1_PROTOCOL.json"
                        ).read_text()
                    )["attempts"]
                    if row["source_negative_id"] == negative_id
                ),
                "lever": result["lever"],
                "attempt_kind": "FROZEN_EXACT_OPEN_SUBJECT_MECHANISM_RETEST",
                "revival_outcome": result["revival_outcome"],
                "evidence": _evidence(
                    root,
                    SECOND_BUNDLE_REL / "results/ORION06_NEW_RESOURCE_REVIVAL.json",
                ),
                "source_negative": {
                    "path": source["artifact"],
                    "sha256": source["artifact_sha256"],
                },
                "job_ids": [job_id],
                "mechanistic_result": result["terminal"],
                "original_negative_preserved": result["original_negative_preserved"],
                "residual_boundary": (
                    result.get("residual")
                    or "the H2 subject was already open; no prospective authority follows"
                ),
                "classification": "SAVE_WORTHY_NEGATIVE_REPAIRED_WITHOUT_AUTHORITY_PROMOTION",
                "authority": result["authority"],
            }
        )

    r6_rows = (
        (
            "R6I_EXACT_RANK2",
            replays["R6I_EXACT_RANK2"],
            "3550253",
            SECOND_BUNDLE_REL / "results/R6K_FRESH_RESULTS.json",
            "fresh exact replay of joint Restore factoring",
        ),
        (
            "R6K_EXACT_RESTORE_FACTOR",
            replays["R6K_EXACT_RESTORE_FACTOR"],
            "3550254",
            SECOND_BUNDLE_REL / "results/R6L_FRESH_RESULTS.json",
            "fresh exact replay of the three-TARE2 arity-swap donor",
        ),
    )
    for negative_id, result, job_id, evidence_path, lever in r6_rows:
        source = coverage_by_id[negative_id]
        rows.append(
            {
                "paper": "ORION-06",
                "negative_id": negative_id,
                "mechanism_stage": result["mechanism_stage"],
                "strongest_parent": source["strongest_parent_or_comparator"],
                "lever": lever,
                "attempt_kind": "RETROSPECTIVE_EXACT_REPLAY_OUTCOME_ALREADY_PUBLIC",
                "revival_outcome": result["revival_outcome"],
                "evidence": _evidence(root, evidence_path),
                "adjudication": _evidence(
                    root,
                    SECOND_BUNDLE_REL
                    / "results/ORION06_METHOD_LANGUAGE_REPLAYS.json",
                ),
                "job_ids": [job_id, "3550255"],
                "mechanistic_result": {
                    "strict_by_subject": result["strict_by_subject"],
                    "scientifically_equal_to_known_receipt": result[
                        "replay_scientifically_equal_to_known_receipt"
                    ],
                },
                "original_negative_preserved": result["original_negative_preserved"],
                "residual_boundary": (
                    "retrospective same-subject evidence; no prospective confirmation, "
                    "R6 authority, or novelty follows"
                ),
                "classification": (
                    "CORRECT_SUBTRACTION"
                    if result["revival_outcome"] == "CORRECT_SUBTRACTION"
                    else "RETAINED_NEGATIVE"
                ),
                "authority": result["authority"],
            }
        )

    cross_domain = coverage["cross_domain_general_method"]
    cannot_check = [
        {
            "paper": "ORION-06",
            "gate_id": "CROSS_DOMAIN_GENERAL_METHOD",
            "mechanism_stage": cross_domain["mechanism_stage"],
            "classification": "CANNOT_CHECK",
            "named_blocker": cross_domain["precondition"],
            "strongest_parent": cross_domain["strongest_parent_or_comparator"],
            "next_executable_condition": (
                "admit matched prospective non-quantum formal and computational or "
                "empirical Domain-B/C programmes with independent scoring"
            ),
            "not_unsolvable": True,
            "authority": _authority(),
        }
    ]

    by_outcome: dict[str, int] = {}
    for row in rows:
        by_outcome[row["revival_outcome"]] = by_outcome.get(row["revival_outcome"], 0) + 1
    if len(rows) != 9 or len(cannot_check) != 1:
        raise AssertionError("negative revival ledger row count drift")
    if not all(row["original_negative_preserved"] is True for row in rows):
        raise AssertionError("an original negative was not preserved")

    return {
        "schema": "ORION.ORION0506.RecordedNegativeRevivalLedger.v1",
        "date": "2026-08-28",
        "scope": ["ORION-05", "ORION-06"],
        "scientific_authority_delta": "NONE",
        "source_verifiers": [
            _evidence(
                root,
                Path(
                    "development/orion-05-06-negative-revival-r1-2026-08-27/"
                    "BUNDLE_VERIFICATION_V1.json"
                ),
            ),
            _evidence(
                root,
                Path(
                    "development/orion-05-06-negative-revival-r1-2026-08-27/"
                    "ORION06_REVIVAL_BUNDLE_VERIFICATION_V1.json"
                ),
            ),
        ],
        "summary": {
            "recorded_negative_rows": len(rows),
            "cannot_check_gates": len(cannot_check),
            "outcomes": by_outcome,
            "unsolvable_count": 0,
        },
        "rows": rows,
        "cannot_check": cannot_check,
        "unsolvable": [],
        "paper_freeze_status": "WITHHELD_PENDING_PORTFOLIO_WIDE_INTEGRATION",
        "authority": _authority(),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    ledger = build(args.root)
    args.output.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n")
    print("ORION0506_NEGATIVE_REVIVAL_LEDGER=BUILT")
    print(json.dumps(ledger["summary"], sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
