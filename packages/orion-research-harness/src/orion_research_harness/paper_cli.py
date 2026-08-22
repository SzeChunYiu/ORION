from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from orion.core.research_resolution import UnresolvedClass

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
from .paper_structure_consensus import run_paper_structure_consensus
from .research_director import ResearchDirectiveKind, direct_research_from_mapping
from .research_resolution import (
    assimilate_negative_result,
    build_resolution_obligation,
    resolution_plan_from_mapping,
)
from .research_saturation import assess_evidence_derived_saturation
from .research_v3_conformance import research_v3_conformance
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


def _structure_input(sub, name: str):
    structure = sub.add_parser(name)
    structure.add_argument("workspace")
    structure.add_argument("source_path")
    structure.add_argument("method_id")
    structure.add_argument("--source-id")
    structure.add_argument("--source-version", default="local-source-v1")
    structure.add_argument("--chunk-size", type=int, default=12000)
    structure.add_argument("--chunk-overlap", type=int, default=800)
    return structure


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="orion-harness-paper",
        description="Operational paper-contract surfaces for the shared ORION research harness",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("paper-contract-conformance")
    sub.add_parser("paper-programme-conformance")
    sub.add_parser("research-v3-conformance")

    _structure_input(sub, "paper-structure")
    _structure_input(sub, "paper-structure-consensus")

    _json_input(sub, "research-direct")
    _json_input(sub, "resolution-plan")
    _json_input(sub, "mechanic-apply")
    _json_input(sub, "dependency-repair")
    _json_input(sub, "authority-check")
    _json_input(sub, "ocme-assess")
    _json_input(sub, "navigation-plan")

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


def _resolution(
    *,
    subject_id: str,
    unresolved_class: UnresolvedClass,
    reason_codes: tuple[str, ...],
    required_object_ids: tuple[str, ...] = (),
    blocker_ids: tuple[str, ...] = (),
) -> dict[str, object]:
    return build_resolution_obligation(
        subject_id=subject_id,
        unresolved_class=unresolved_class,
        reason_codes=reason_codes,
        required_object_ids=required_object_ids,
        blocker_ids=blocker_ids,
    ).as_dict()


def _run_structure_command(args, *, consensus: bool) -> int:
    workspace = ResearchWorkspace.load(args.workspace)
    runner = run_paper_structure_consensus if consensus else run_paper_structure
    outcome = runner(
        workspace,
        source_path=args.source_path,
        method_id=args.method_id,
        source_id=args.source_id or f"local:{args.source_path}",
        source_version=args.source_version,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )
    status = str(outcome["status"])
    projected = dict(outcome)
    if status in {"PENDING_CAPABILITY", "HOST_CAPABILITY_FAILED"}:
        request = outcome.get("request", {})
        request_id = str(request.get("request_id", "")) if isinstance(request, dict) else ""
        projected["resolution_obligation"] = _resolution(
            subject_id=args.method_id,
            unresolved_class=UnresolvedClass.CAPABILITY,
            reason_codes=(status,),
            required_object_ids=((request_id,) if request_id else ()),
            blocker_ids=((request_id,) if status == "HOST_CAPABILITY_FAILED" and request_id else ()),
        )
    elif status.startswith("CANNOT_CHECK"):
        projected["resolution_obligation"] = _resolution(
            subject_id=args.method_id,
            unresolved_class=(
                UnresolvedClass.COVERAGE
                if "COVERAGE" in status
                else UnresolvedClass.EVIDENCE
            ),
            reason_codes=(status,),
        )
    _print(projected)
    if status == "PENDING_CAPABILITY":
        return 2
    if status == "HOST_CAPABILITY_FAILED":
        return 3
    if status.startswith("CANNOT_CHECK"):
        return 4
    return 0


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
    if args.command == "research-v3-conformance":
        report = research_v3_conformance()
        _print(report)
        return 0 if report["operational"] else 4
    if args.command == "paper-structure":
        return _run_structure_command(args, consensus=False)
    if args.command == "paper-structure-consensus":
        return _run_structure_command(args, consensus=True)
    if args.command == "resolution-plan":
        raw = _load_json(args.json, args.file)
        if not isinstance(raw, dict):
            raise TypeError("resolution-plan input must be an object")
        _print(resolution_plan_from_mapping(raw))
        return 0
    if args.command == "research-direct":
        directive = direct_research_from_mapping(_load_json(args.json, args.file))
        payload = directive.as_dict()
        if directive.kind is ResearchDirectiveKind.CANNOT_CHECK:
            payload["resolution_obligation"] = _resolution(
                subject_id="research-directive",
                unresolved_class=UnresolvedClass.RESPONSIBILITY,
                reason_codes=(directive.reason,),
                blocker_ids=directive.trigger_residual_ids,
            )
        _print(payload)
        return 4 if directive.kind is ResearchDirectiveKind.CANNOT_CHECK else 0
    if args.command == "mechanic-apply":
        raw = _load_json(args.json, args.file)
        if not isinstance(raw, dict):
            raise TypeError("mechanic-apply input must be an object")
        result = apply_mechanic(
            mechanic_state_from_mapping(raw["state"]),
            mechanic_contract_from_mapping(raw["contract"]),
        )
        payload = _non_authorizing("ORION.HarnessP6MechanicExecution.v1", result=jsonable(result))
        if result.terminal is MechanicTerminal.CANNOT_CHECK:
            payload["resolution_obligation"] = _resolution(
                subject_id=str(raw.get("contract", {}).get("mechanic_id", "p6-mechanic")),
                unresolved_class=UnresolvedClass.EVIDENCE,
                reason_codes=tuple(str(item) for item in result.reasons) or ("P6_CANNOT_CHECK",),
            )
        _print(payload)
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
        payload = _non_authorizing("ORION.HarnessP8AuthorityDecision.v1", decision=jsonable(decision))
        if decision.terminal is AuthorityTerminal.CANNOT_CHECK:
            payload["resolution_obligation"] = _resolution(
                subject_id=str(raw.get("effect", {}).get("effect_id", "p8-effect")),
                unresolved_class=UnresolvedClass.AUTHORITY,
                reason_codes=tuple(str(item) for item in decision.reasons) or ("P8_CANNOT_CHECK",),
            )
        _print(payload)
        if decision.terminal is AuthorityTerminal.AUTHORIZED:
            return 0
        return 4 if decision.terminal is AuthorityTerminal.CANNOT_CHECK else 5
    if args.command == "ocme-assess":
        raw = _load_json(args.json, args.file)
        if not isinstance(raw, dict):
            raise TypeError("ocme-assess input must be an object")
        decision = assess_ocme_episode(ocme_episode_from_mapping(raw))
        payload = _non_authorizing("ORION.HarnessP10OCMEAssessment.v1", decision=jsonable(decision))
        if decision.terminal is OCMETerminal.CANNOT_CHECK:
            payload["resolution_obligation"] = _resolution(
                subject_id=str(raw.get("episode_id", "p10-episode")),
                unresolved_class=UnresolvedClass.METHOD,
                reason_codes=tuple(str(item) for item in decision.reasons) or ("P10_CANNOT_CHECK",),
            )
        elif decision.terminal is OCMETerminal.OCME_DONOR_SUBSUMED:
            evidence_ids = tuple(
                str(item)
                for item in (
                    list((raw.get("obstruction") or {}).get("evidence_ids", ()))
                    + list((raw.get("transfer") or {}).get("evidence_ids", ()))
                )
            ) or ("e:ocme-donor-subsumed",)
            payload["negative_result"] = assimilate_negative_result(
                result_id=f"negative:{raw.get('episode_id', 'p10')}:donor",
                subject_id=str(raw.get("episode_id", "p10-episode")),
                negative_kind="DONOR_SUBSUMED",
                evidence_ids=evidence_ids,
                reason_codes=tuple(str(item) for item in decision.reasons) or ("DONOR_SUBSUMED",),
            ).as_dict()
        elif decision.terminal is OCMETerminal.OCME_IMPOSSIBILITY_BOUNDARY:
            payload["negative_result"] = assimilate_negative_result(
                result_id=f"negative:{raw.get('episode_id', 'p10')}:impossibility",
                subject_id=str(raw.get("episode_id", "p10-episode")),
                negative_kind="IMPOSSIBILITY_BOUNDARY",
                evidence_ids=tuple(str(item) for item in (raw.get("obstruction") or {}).get("evidence_ids", ())) or ("e:ocme-impossibility",),
                reason_codes=tuple(str(item) for item in decision.reasons) or ("IMPOSSIBILITY_BOUNDARY",),
            ).as_dict()
        _print(payload)
        return 4 if decision.terminal is OCMETerminal.CANNOT_CHECK else 0
    if args.command == "navigation-plan":
        state = navigation_state_from_mapping(_load_json(args.json, args.file))
        decision = plan_navigation(state)
        payload = {
            "schema": "ORION.HarnessEpistemicNavigationDecision.v1",
            "state": jsonable(state),
            "decision": jsonable(decision),
            "grants_scientific_authority": False,
            "grants_novelty_authority": False,
        }
        if decision.action.value == "CANNOT_CHECK":
            payload["resolution_obligation"] = _resolution(
                subject_id=state.active_chart.chart_id,
                unresolved_class=UnresolvedClass.COVERAGE,
                reason_codes=tuple(str(item) for item in decision.reasons) or ("P7_CANNOT_CHECK",),
            )
        _print(payload)
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
        payload = {
            "schema": "ORION.HarnessResearchSaturationAssessment.v1",
            "rounds": jsonable(rounds),
            "report": report_payload,
            "grants_scientific_authority": False,
            "grants_novelty_authority": False,
            "grants_global_task_stop_authority": False,
        }
        if not report.bounded_saturated:
            payload["resolution_obligation"] = _resolution(
                subject_id="research-saturation",
                unresolved_class=UnresolvedClass.COVERAGE,
                reason_codes=tuple(str(item) for item in report.reasons) or ("SATURATION_OPEN",),
            )
        _print(payload)
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
        payload = _non_authorizing(
            "ORION.HarnessP13ResponsibilityAction.v1",
            state_class=args.state_class,
            task=args.task,
            recoverable=args.recoverable,
            action=action.value,
        )
        if action.value == "CANNOT_CHECK":
            payload["resolution_obligation"] = _resolution(
                subject_id=f"p13:{args.state_class}:{args.task}",
                unresolved_class=UnresolvedClass.RESPONSIBILITY,
                reason_codes=("P13_RESPONSIBILITY_NOT_RESOLVED",),
            )
        _print(payload)
        return 0
    if args.command == "p14-disposition":
        raw = _load_json(args.json, args.file)
        if not isinstance(raw, dict):
            raise TypeError("p14-disposition input must be an object")
        disposition = p14_governance_disposition(raw)
        payload = _non_authorizing("ORION.HarnessP14Disposition.v1", disposition=disposition)
        if disposition == "CANNOT_CHECK":
            payload["resolution_obligation"] = _resolution(
                subject_id="p14-governance",
                unresolved_class=UnresolvedClass.EVIDENCE,
                reason_codes=("P14_GOVERNANCE_EVIDENCE_INSUFFICIENT",),
            )
        _print(payload)
        return 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    sys.exit(main())
