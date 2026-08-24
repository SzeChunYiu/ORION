"""Generate deterministic receipts for the locally discharged theorem tranche."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .ledger import build_theorem_ledger
from .manifest import build_content_manifest, render_sha256sums
from .theorems import TheoremResult, run_local_theorems


def canonical_json(payload: object) -> str:
    return json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def _core_results() -> tuple[TheoremResult, ...]:
    return run_local_theorems()


def build_receipt(results: tuple[TheoremResult, ...] | None = None) -> dict[str, object]:
    results = _core_results() if results is None else results
    theorem_payload = [result.as_json() for result in results]
    core = {
        "schema_version": "orion.foundations.local-derivations.v1",
        "issue": 1220,
        "authority_delta": "NONE",
        "p1_rr1_coordination": "UNTOUCHED",
        "theorems": theorem_payload,
        "summary": {
            "total": len(results),
            "local_proved": sum(result.passed for result in results),
            "counterexample_or_open": sum(not result.passed for result in results),
        },
    }
    digest = hashlib.sha256(canonical_json(core).encode("utf-8")).hexdigest()
    return {**core, "canonical_core_sha256": digest}


def build_assumption_ledger(
    results: tuple[TheoremResult, ...] | None = None,
) -> dict[str, object]:
    results = _core_results() if results is None else results
    return {
        "schema_version": "orion.foundations.assumption-ledger.v1",
        "issue": 1220,
        "authority": "LOCAL_FINITE_DERIVATION_ONLY",
        "entries": [
            {
                "theorem_id": result.theorem_id,
                "assumptions": list(result.assumptions),
                "local_status": result.status,
                "outside_assumption_policy": "COUNTERMODEL_OR_CANNOT_CHECK",
            }
            for result in results
        ],
    }


def build_countermodel_atlas(
    results: tuple[TheoremResult, ...] | None = None,
) -> dict[str, object]:
    results = _core_results() if results is None else results
    explicit = [
        {
            "theorem_id": result.theorem_id,
            "statement": result.statement,
            "witness": result.witness,
            "detail": result.detail,
        }
        for result in results
        if result.witness is not None
    ]
    named = [
        {
            "countermodel_id": "CM-V",
            "target": "OSTC-T8",
            "difference": "native artifact validity",
            "outcomes": ["ESTABLISH", "DENY"],
        },
        {
            "countermodel_id": "CM-S",
            "target": "OSTC-T2/OSTC-T8",
            "difference": "hidden target distinction erased by the interface",
            "outcomes": ["ESTABLISH", "REOPEN"],
        },
        {
            "countermodel_id": "CM-E",
            "target": "OSTC-T5/OSTC-T8",
            "difference": "target-bound authority or bridge",
            "outcomes": ["ESTABLISH", "DENY"],
        },
        {
            "countermodel_id": "CM-B",
            "target": "OSTC-T8/OSTC-T11",
            "difference": "unresolved blocker or surviving support family",
            "outcomes": ["ESTABLISH", "CANNOT_CHECK"],
        },
        {
            "countermodel_id": "CM-OPEN-WORLD",
            "target": "OSTC-T12",
            "difference": "unseen material route",
            "outcomes": ["TASK_CLOSED", "TASK_OPEN"],
        },
        {
            "countermodel_id": "CM-SELF-PROMOTION",
            "target": "OSTC-T19",
            "difference": "protected fresh assurance",
            "outcomes": ["ADOPT", "REJECT"],
        },
        {
            "countermodel_id": "CM-EXECUTION-SCIENCE",
            "target": "OSTC-T20",
            "difference": "scientific validity under identical execution integrity",
            "outcomes": ["ESTABLISH", "BLOCK"],
        },
    ]
    return {
        "schema_version": "orion.foundations.countermodel-atlas.v1",
        "issue": 1220,
        "authority": "FINITE_WITNESS_ATLAS",
        "explicit_witnesses": explicit,
        "named_minimal_families": named,
    }


def _write(path: Path | None, payload: dict[str, Any]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(payload), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--assumptions-output", type=Path)
    parser.add_argument("--countermodels-output", type=Path)
    parser.add_argument("--theorem-ledger-output", type=Path)
    parser.add_argument("--manifest-output", type=Path)
    parser.add_argument("--sha256sums-output", type=Path)
    args = parser.parse_args()

    results = _core_results()
    receipt = build_receipt(results)
    _write(args.output, receipt)
    _write(args.assumptions_output, build_assumption_ledger(results))
    _write(args.countermodels_output, build_countermodel_atlas(results))
    _write(
        args.theorem_ledger_output,
        build_theorem_ledger(results, receipt["canonical_core_sha256"]),
    )
    if args.manifest_output is not None:
        root = Path(__file__).resolve().parents[3]
        manifest = build_content_manifest(root)
        _write(args.manifest_output, manifest)
        if args.sha256sums_output is not None:
            args.sha256sums_output.write_text(
                render_sha256sums(manifest, args.manifest_output),
                encoding="utf-8",
            )
    elif args.sha256sums_output is not None:
        parser.error("--sha256sums-output requires --manifest-output")
    failed = receipt["summary"]["counterexample_or_open"]  # type: ignore[index]
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
