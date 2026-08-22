from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .epistemic_navigation import plan_navigation
from .paper_conformance import paper_contract_conformance
from .paper_programme_conformance import paper_programme_conformance
from .paper_runtime_io import (
    jsonable,
    navigation_state_from_mapping,
    research_rounds_from_mapping,
)
from .paper_structure import run_paper_structure
from .research_saturation import assess_evidence_derived_saturation
from .workspace import ResearchWorkspace


def _print(value: object) -> None:
    print(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False))


def _load_json(raw: str | None, path: str | None) -> object:
    if raw is not None and path is not None:
        raise SystemExit("use only one of --json or --file")
    if path is not None:
        return json.loads(Path(path).read_text())
    if raw is None:
        raise SystemExit("one of --json or --file is required")
    return json.loads(raw)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="orion-harness-paper",
        description="Operational paper-contract surfaces for the shared ORION research harness",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("paper-contract-conformance")
    sub.add_parser("paper-programme-conformance")

    structure = sub.add_parser("paper-structure")
    structure.add_argument("workspace")
    structure.add_argument("source_path")
    structure.add_argument("method_id")
    structure.add_argument("--source-id")
    structure.add_argument("--source-version", default="local-source-v1")
    structure.add_argument("--chunk-size", type=int, default=12000)
    structure.add_argument("--chunk-overlap", type=int, default=800)

    navigation = sub.add_parser("navigation-plan")
    navigation.add_argument("--json")
    navigation.add_argument("--file")

    saturation = sub.add_parser("research-saturation")
    saturation.add_argument("--json")
    saturation.add_argument("--file")
    saturation.add_argument("--min-independent-flat-routes", type=int, default=2)
    saturation.add_argument("--window", type=int, default=6)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "paper-contract-conformance":
        report = paper_contract_conformance()
        _print(report)
        return 0 if report["paper_contract_operational"] else 4
    if args.command == "paper-programme-conformance":
        report = paper_programme_conformance()
        _print(report)
        return 0 if report["paper_programme_operational"] else 4
    if args.command == "paper-structure":
        workspace = ResearchWorkspace.load(args.workspace)
        outcome = run_paper_structure(
            workspace,
            source_path=args.source_path,
            method_id=args.method_id,
            source_id=args.source_id or f"local:{args.source_path}",
            source_version=args.source_version,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
        )
        _print(outcome)
        status = str(outcome["status"])
        if status == "PENDING_CAPABILITY":
            return 2
        if status == "HOST_CAPABILITY_FAILED":
            return 3
        if status.startswith("CANNOT_CHECK"):
            return 4
        return 0
    if args.command == "navigation-plan":
        state = navigation_state_from_mapping(_load_json(args.json, args.file))
        decision = plan_navigation(state)
        _print(
            {
                "schema": "ORION.HarnessEpistemicNavigationDecision.v1",
                "state": jsonable(state),
                "decision": jsonable(decision),
                "grants_scientific_authority": False,
                "grants_novelty_authority": False,
            }
        )
        return 0 if decision.action.value != "CANNOT_CHECK" else 4
    if args.command == "research-saturation":
        rounds = research_rounds_from_mapping(_load_json(args.json, args.file))
        report = assess_evidence_derived_saturation(
            rounds,
            min_independent_flat_routes=args.min_independent_flat_routes,
            window=args.window,
        )
        report_payload = jsonable(report)
        report_payload["grants_absolute_completeness"] = report.grants_absolute_completeness
        report_payload["grants_self_promotion"] = report.grants_self_promotion
        _print(
            {
                "schema": "ORION.HarnessResearchSaturationAssessment.v1",
                "rounds": jsonable(rounds),
                "report": report_payload,
                "grants_scientific_authority": False,
                "grants_novelty_authority": False,
                "grants_global_task_stop_authority": False,
            }
        )
        return 0 if report.bounded_saturated else 4
    raise AssertionError(args.command)


if __name__ == "__main__":
    sys.exit(main())
