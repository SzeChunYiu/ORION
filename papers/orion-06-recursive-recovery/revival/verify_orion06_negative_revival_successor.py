#!/usr/bin/env python3
"""Verify the current-main adoption of the executed ORION-06 revival bundle.

The pre-execution coverage audit is immutable: four rows remain marked
``UNFINISHED`` in that historical receipt.  This successor verifier joins that
audit to the independently verified LUNARC execution without rewriting either
source object.  It fails closed if a recorded negative disappears, if an
execution outcome is promoted, or if the named cross-domain ``CANNOT_CHECK``
gate is relabelled as solved or unsolvable.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any, Sequence


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
COVERAGE_REL = Path(
    "papers/orion-06-recursive-recovery/revival/ORION06_NEGATIVE_COVERAGE_RESULT.json"
)
BUNDLE_REPORT_REL = Path(
    "development/orion-05-06-negative-revival-r1-2026-08-27/"
    "ORION06_REVIVAL_BUNDLE_VERIFICATION_V1.json"
)
BUNDLE_VERIFIER_REL = Path(
    "development/orion-05-06-negative-revival-r1-2026-08-27/verify_orion06_revival_r1_bundle.py"
)
COMMITTED_SUCCESSOR_REL = Path(
    "papers/orion-06-recursive-recovery/revival/ORION06_NEGATIVE_REVIVAL_R1_SUCCESSOR.json"
)

EXPECTED_ROWS = {
    "R2_KNOWN_OPERATOR_TRANSFER",
    "R3B_JOINT_OBLIGATION_BINDING",
    "R4C_H2_REGIME_LIMITED",
    "R5B_PROOF_OUTER_REPLAY",
    "R6I_EXACT_RANK2",
    "R6K_EXACT_RESTORE_FACTOR",
    "N1C_TYPED_FAILURE_STATE",
}
EXECUTED_ROWS = {
    "R4C_H2_REGIME_LIMITED",
    "R5B_PROOF_OUTER_REPLAY",
    "R6I_EXACT_RANK2",
    "R6K_EXACT_RESTORE_FACTOR",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _bounded_authority(authority: dict[str, Any]) -> bool:
    forbidden = (
        "prospective_confirmation",
        "external_independence",
        "cross_domain_effectiveness",
        "productivity_superiority",
        "novelty",
        "journal_or_submission",
        "submission_authorized",
        "final_freeze",
    )
    return all(authority.get(key) in (None, False) for key in forbidden)


def build(root: Path = ROOT) -> dict[str, Any]:
    root = Path(root).resolve()
    coverage_path = root / COVERAGE_REL
    committed_coverage = json.loads(coverage_path.read_text())
    coverage_verifier = load_module(
        "orion06_negative_coverage_successor_source",
        root / "papers/orion-06-recursive-recovery/revival/verify_orion06_negative_coverage.py",
    )
    rebuilt_coverage = coverage_verifier.build_audit(root)
    if committed_coverage != rebuilt_coverage:
        raise AssertionError("pre-execution negative-coverage receipt drift")

    source_rows = committed_coverage["standalone_rows"]
    source_ids = {row["id"] for row in source_rows}
    if source_ids != EXPECTED_ROWS or len(source_rows) != len(EXPECTED_ROWS):
        raise AssertionError({"recorded_negative_denominator_drift": sorted(source_ids)})
    unfinished = {row["id"] for row in source_rows if row["revival_outcome"] == "UNFINISHED"}
    if unfinished != EXECUTED_ROWS:
        raise AssertionError({"unfinished_denominator_drift": sorted(unfinished)})

    bundle_verifier = load_module(
        "orion06_negative_revival_bundle_successor_source",
        root / BUNDLE_VERIFIER_REL,
    )
    rebuilt_bundle = bundle_verifier.verify(root)
    committed_bundle = json.loads((root / BUNDLE_REPORT_REL).read_text())
    if rebuilt_bundle != committed_bundle:
        raise AssertionError("executed revival bundle verification drift")
    if rebuilt_bundle["unsolvable"] != [] or not _bounded_authority(rebuilt_bundle["authority"]):
        raise AssertionError("executed bundle widened authority")

    rows: list[dict[str, Any]] = []
    for source in source_rows:
        row = dict(source)
        row["pre_execution_revival_outcome"] = source["revival_outcome"]
        row["original_negative_preserved"] = True
        if source["id"] in EXECUTED_ROWS:
            attempt = rebuilt_bundle["attempts"][source["id"]]
            row["revival_outcome"] = attempt["outcome"]
            row["execution_evidence"] = {
                "bundle_report": BUNDLE_REPORT_REL.as_posix(),
                "attempt": attempt,
            }
        else:
            if source["revival_outcome"] != "RETAINED_NEGATIVE":
                raise AssertionError({"unexecuted_row_was_promoted": source["id"]})
            row["execution_evidence"] = {
                "kind": "exact parent/donor comparison already bound in source receipt",
                "artifact": source["artifact"],
                "artifact_sha256": source["artifact_sha256"],
            }
        rows.append(row)

    outcomes = Counter(row["revival_outcome"] for row in rows)
    expected_outcomes = Counter(
        {
            "IMPROVED": 2,
            "CORRECT_SUBTRACTION": 1,
            "RETAINED_NEGATIVE": 4,
        }
    )
    if outcomes != expected_outcomes:
        raise AssertionError({"successor_outcome_partition_drift": dict(outcomes)})

    gate = dict(committed_coverage["cross_domain_general_method"])
    if gate.get("revival_outcome") != "CANNOT_CHECK":
        raise AssertionError("cross-domain gate was not retained as CANNOT_CHECK")
    gate["classification"] = "CANNOT_CHECK"
    gate["not_unsolvable"] = True
    gate["triage"] = "blocked on a named external evaluation resource"
    gate["next_executable_condition"] = (
        "prospectively admit matched non-quantum formal and computational or "
        "empirical Domain-B/C programmes with independent scoring"
    )

    authority = {
        "prospective_confirmation": False,
        "external_independence": False,
        "cross_domain_effectiveness": False,
        "productivity_superiority": False,
        "novelty": False,
        "journal_or_submission": False,
        "submission_authorized": False,
        "final_freeze": False,
    }
    return {
        "schema": "ORION.ORION06.NegativeRevivalR1Successor.v1",
        "date": "2026-08-28",
        "terminal": ("ORION06_RECORDED_NEGATIVE_REVIVAL_COVERAGE_COMPLETE__PAPER_FREEZE_WITHHELD"),
        "scientific_authority_delta": "NONE",
        "source_receipts": {
            "pre_execution_coverage": {
                "path": COVERAGE_REL.as_posix(),
                "sha256": sha256_file(coverage_path),
            },
            "executed_bundle_verification": {
                "path": BUNDLE_REPORT_REL.as_posix(),
                "sha256": sha256_file(root / BUNDLE_REPORT_REL),
                "pre_outcome_protocol_commit": rebuilt_bundle["source_chronology"][
                    "pre_outcome_protocol_commit"
                ],
                "execution_commit": rebuilt_bundle["source_chronology"]["execution_commit"],
            },
        },
        "coverage": {
            "recorded_negative_rows": len(rows),
            "mechanistically_adjudicated_rows": len(rows),
            "cannot_check_gates": 1,
            "outcomes": dict(sorted(outcomes.items())),
            "unsolvable_count": 0,
        },
        "rows": rows,
        "cannot_check": [gate],
        "unsolvable": [],
        "paper_freeze": {
            "status": "WITHHELD",
            "reason": (
                "bounded negative-revival coverage is not whole-paper science, "
                "external authority, or submission custody"
            ),
            "remaining_gates": [
                "protected prospective new-subject confirmation for the R4C/R5B mechanism claims",
                "the named cross-domain independently scored comparison",
                "current independent novelty and external-authority review",
                "current manuscript/PDF/package byte binding and visual QA",
            ],
        },
        "authority": authority,
    }


def verify_committed(root: Path = ROOT) -> dict[str, Any]:
    root = Path(root).resolve()
    rebuilt = build(root)
    committed = json.loads((root / COMMITTED_SUCCESSOR_REL).read_text())
    if committed != rebuilt:
        raise AssertionError("committed ORION-06 successor receipt drift")
    return rebuilt


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build(args.root)
    target = Path(args.root).resolve() / COMMITTED_SUCCESSOR_REL
    if args.write:
        target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        committed = json.loads(target.read_text())
        if committed != report:
            raise AssertionError("committed ORION-06 successor receipt drift")
    print("ORION06_NEGATIVE_REVIVAL_SUCCESSOR=PASS")
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
