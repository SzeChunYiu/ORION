from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .epistemic_authority import AuthorityTerminal, authorize_effect
from .epistemic_mechanics import MechanicTerminal, apply_mechanic, certificate_aware_reopen
from .epistemic_navigation import plan_navigation
from .ocme_runtime import OCMETerminal, assess_ocme_episode
from .paper_conformance import paper_contract_conformance
from .paper_control_io import (
    authority_context_from_mapping,
    effect_request_from_mapping,
    mechanic_contract_from_mapping,
    mechanic_state_from_mapping,
    ocme_episode_from_mapping,
    preservation_certificate_from_mapping,
)
from .paper_programme_conformance import paper_programme_conformance
from .paper_programme_runtime import (
    p11_accessible_rank_dimension,
    p12_joint_alloc,
    p13_rcs_action,
    p14_governance_disposition,
)
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


def _json_input(sub, name: str):
    command = sub.add_parser(name)
    command.add_argument("--json")
    command.add_argument("--file")
    return command


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

    _json_input(sub, "mechanic-apply")
    _json_input(sub, "dependency-repair")
    _json_input(sub, "authority-check")
    _json_input(sub, "ocme-assess")

    navigation = _json_input(sub, "navigation-plan")

    saturation = _json_input(sub, "research-saturation")
    saturation.add_argument("--min-independent-flat-routes", type=int, default=2)
    saturation.add_argument("--window", type=int, default=6)

    p11 = sub.add_parser("p11-accessible-rank")
    p11.add_argument("d", type=int)
    p11.add_argument("s", type=int)

    p12 = sub.add_parser("p12-allocate")
    p12.add_argument("state_signal", type=float)
    p12.add_argument("reasoning_signal", type=float)
    p12.add_argument("--budget", type=int, default=2)

    p13 = sub.add_parser("p13-action")
    p13.add_argument("state_class")
    p13.add_argument("task")
    p13.add_argument("--recoverable", action="store_true")

    _json_input(sub, "p14-disposition")
    return parser


def _non_authorizing(schema: str, **payload: object) -> dict[str, object]:
    return {
        "schema": schema,
        **payload,
        "grants_scientific_authority": False,
        "grants_novelty_authority": False,
        "grants_promotion_authority": False,
    }


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
    if args.command == "mechanic-apply":
        raw = _load_json(args.json, args.file)
        if not isinstance(raw, dict):
            raise TypeError("mechanic-apply input must be an object")
        result = apply_mechanic(
            mechanic_state_from_mapping(raw["state"]),
            mechanic_contract_from_mapping(raw["contract"]),
        )
        _print(_non_authorizing("ORION.HarnessP6MechanicExecution.v1", result=jsonable(result)))
        if result.terminal is MechanicTerminal.APPLIED:
            return 0
        return 4 if result.terminal is MechanicTerminal.CANNOT_CHECK else 5
    if args.command == "dependency-repair":
        raw = _load_json(args.json, args.file)
        if not isinstance(raw, dict):
            raise TypeError("dependency-repair input must be an object")
        repaired = certificate_aware_reopen(
            mechanic_state_from_mapping(raw["state"]),
            changed_ids=tuple(str(item) for item in raw.get("changed_ids", ())),
            certificates=tuple(
                preservation_certificate_from_mapping(item)
                for item in raw.get("certificates", ())
            ),
        )
        _print(_non_authorizing("ORION.HarnessP6DependencyRepair.v1", state=jsonable(repaired)))
        return 0
    if args.command == "authority-check":
        raw = _load_json(args.json, args.file)
        if not isinstance(raw, dict):
            raise TypeError("authority-check input must be an object")
        decision = authorize_effect(
            effect_request_from_mapping(raw["effect"]),
            authority_context_from_mapping(raw["context"]),
            confidence=raw.get("confidence"),
            expected_utility=raw.get("expected_utility"),
        )
        _print(_non_authorizing("ORION.HarnessP8AuthorityDecision.v1", decision=jsonable(decision)))
        if decision.terminal is AuthorityTerminal.AUTHORIZED:
            return 0
        return 4 if decision.terminal is AuthorityTerminal.CANNOT_CHECK else 5
    if args.command == "ocme-assess":
        decision = assess_ocme_episode(ocme_episode_from_mapping(_load_json(args.json, args.file)))
        _print(_non_authorizing("ORION.HarnessP10OCMEAssessment.v1", decision=jsonable(decision)))
        return 4 if decision.terminal is OCMETerminal.CANNOT_CHECK else 0
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
    if args.command == "p11-accessible-rank":
        _print(_non_authorizing(
            "ORION.HarnessP11AccessibleRank.v1",
            d=args.d,
            s=args.s,
            rank_dimension=p11_accessible_rank_dimension(args.d, args.s),
        ))
        return 0
    if args.command == "p12-allocate":
        allocation = p12_joint_alloc(args.state_signal, args.reasoning_signal, budget=args.budget)
        _print(_non_authorizing(
            "ORION.HarnessP12Allocation.v1",
            state_signal=args.state_signal,
            reasoning_signal=args.reasoning_signal,
            budget=args.budget,
            allocation=list(allocation),
        ))
        return 0
    if args.command == "p13-action":
        action = p13_rcs_action(args.state_class, args.task, recoverable=args.recoverable)
        _print(_non_authorizing(
            "ORION.HarnessP13ResponsibilityAction.v1",
            state_class=args.state_class,
            task=args.task,
            recoverable=args.recoverable,
            action=action.value,
        ))
        return 4 if action.value == "CANNOT_CHECK" else 0
    if args.command == "p14-disposition":
        raw = _load_json(args.json, args.file)
        if not isinstance(raw, dict):
            raise TypeError("p14-disposition input must be an object")
        disposition = p14_governance_disposition(raw)
        _print(_non_authorizing("ORION.HarnessP14Disposition.v1", disposition=disposition))
        return 4 if disposition == "CANNOT_CHECK" else 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    sys.exit(main())
