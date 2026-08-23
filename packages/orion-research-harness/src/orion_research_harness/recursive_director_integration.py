from __future__ import annotations

from typing import Any, Iterable, Mapping

from orion.core.research_resolution import UnresolvedClass
from orion.core.residuals import Residual, ResidualKind, Responsibility
from orion.core.solution import SolutionStatus

from . import recursive_runner as _rr
from .research_director import ResearchDirectiveKind, direct_research
from .research_resolution import build_resolution_obligation


_INSTALLED = False


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _dedupe_reason_codes(values: Iterable[str]) -> tuple[str, ...]:
    """Preserve first occurrence while preventing duplicate-ID construction failure."""

    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        code = str(value).strip()
        if code and code not in seen:
            seen.add(code)
            out.append(code)
    return tuple(out)


def _material_residuals_from_record(record: Mapping[str, Any]) -> tuple[Residual, ...]:
    final_state = _mapping(record.get("final_state"))
    knowledge = _mapping(final_state.get("knowledge"))
    raw_rows = knowledge.get("residuals", ())
    if isinstance(raw_rows, (str, bytes)) or not isinstance(raw_rows, (list, tuple)):
        return ()
    residuals: list[Residual] = []
    for raw in raw_rows:
        row = _mapping(raw)
        if not row or row.get("material", True) is not True:
            continue
        raw_responsibilities = row.get("candidate_responsibilities", ())
        if isinstance(raw_responsibilities, (str, bytes)) or not isinstance(
            raw_responsibilities, (list, tuple)
        ):
            responsibilities: tuple[Responsibility, ...] = ()
        else:
            responsibilities = tuple(
                Responsibility(str(item)) for item in raw_responsibilities
            )
        raw_metadata = row.get("metadata", ())
        metadata: list[tuple[str, str]] = []
        if isinstance(raw_metadata, (list, tuple)):
            for item in raw_metadata:
                if isinstance(item, (list, tuple)) and len(item) == 2:
                    metadata.append((str(item[0]), str(item[1])))
        residuals.append(
            Residual(
                residual_id=str(row.get("residual_id", "")),
                kind=ResidualKind(str(row.get("kind", ResidualKind.UNCLASSIFIED.value))),
                description=str(row.get("description", "")),
                material=True,
                candidate_responsibilities=responsibilities,
                metadata=tuple(metadata),
            )
        )
    return tuple(residuals)


def _solution_status_from_record(record: Mapping[str, Any]) -> SolutionStatus:
    solution = _mapping(record.get("final_solution"))
    raw = solution.get("status")
    if raw is None:
        return SolutionStatus.CANNOT_CHECK
    return SolutionStatus(str(raw))


def _class_for_directive(kind: ResearchDirectiveKind, record: Mapping[str, Any]) -> UnresolvedClass:
    if bool(record.get("resource_bound_hit", False)):
        return UnresolvedClass.RESOURCE
    if bool(record.get("identity_ambiguity_hit", False)):
        return UnresolvedClass.RESPONSIBILITY
    if kind is ResearchDirectiveKind.RESTORE_CAPABILITY:
        return UnresolvedClass.CAPABILITY
    if kind in {ResearchDirectiveKind.VERIFY_EVIDENCE, ResearchDirectiveKind.VERIFY_OR_REOPEN}:
        return UnresolvedClass.EVIDENCE
    if kind is ResearchDirectiveKind.CHECK_EVALUATION_AUTHORITY:
        return UnresolvedClass.AUTHORITY
    if kind is ResearchDirectiveKind.ASSESS_OCME:
        return UnresolvedClass.METHOD
    if kind is ResearchDirectiveKind.NAVIGATE_OR_REFRAME:
        return UnresolvedClass.COVERAGE
    if kind is ResearchDirectiveKind.DIAGNOSE_RESPONSIBILITY:
        return UnresolvedClass.RESPONSIBILITY
    return UnresolvedClass.UNKNOWN


def _resolution_for_nonrun_outcome(outcome: Mapping[str, Any]) -> dict[str, object] | None:
    status = str(outcome.get("status", ""))
    if status not in {"PENDING_CAPABILITY", "HOST_CAPABILITY_FAILED"}:
        return None
    problem_id = str(outcome.get("problem_id", "unknown-problem"))
    request = _mapping(outcome.get("request"))
    request_id = str(request.get("request_id", ""))
    obligation = build_resolution_obligation(
        subject_id=problem_id,
        unresolved_class=UnresolvedClass.CAPABILITY,
        reason_codes=(status,),
        required_object_ids=((request_id,) if request_id else ()),
        blocker_ids=((request_id,) if status == "HOST_CAPABILITY_FAILED" and request_id else ()),
    )
    return obligation.as_dict()


def install_research_director_integration() -> None:
    """Attach paper-aware next-action and V4 unresolved-resolution projections."""

    global _INSTALLED
    if _INSTALLED:
        return
    original = _rr.run_problem_recursive

    def run_problem_recursive_with_director(
        workspace,
        problem_data,
        *,
        max_iterations: int = 3,
        require_verified_answer: bool = True,
        limits=None,
    ):
        outcome = original(
            workspace,
            problem_data,
            max_iterations=max_iterations,
            require_verified_answer=require_verified_answer,
            limits=limits,
        )
        if not isinstance(outcome, Mapping):
            return outcome

        run_id = outcome.get("run_id")
        if not isinstance(run_id, str) or not run_id:
            resolution = _resolution_for_nonrun_outcome(outcome)
            return dict(outcome) if resolution is None else {**dict(outcome), "resolution_obligation": resolution}

        record = workspace.load_run(run_id)
        solution_status = _solution_status_from_record(record)
        directive = direct_research(
            solution_status=solution_status,
            material_residuals=_material_residuals_from_record(record),
            resource_bound_hit=bool(record.get("resource_bound_hit", False)),
            identity_ambiguity_hit=bool(record.get("identity_ambiguity_hit", False)),
        )
        projected = {**dict(outcome), "research_directive": directive.as_dict()}

        public_status = str(outcome.get("status", ""))
        unresolved = (
            public_status.startswith("CANNOT_CHECK")
            or solution_status
            in {SolutionStatus.CANNOT_CHECK, SolutionStatus.PROVISIONAL, SolutionStatus.BLOCKED}
        )
        if unresolved:
            reason_codes = _dedupe_reason_codes(
                str(row.get("stop_reason"))
                for row in record.get("stop_records", ())
                if isinstance(row, Mapping) and row.get("stop_reason")
            )
            if not reason_codes:
                reason_codes = (public_status or solution_status.value,)
            obligation = build_resolution_obligation(
                subject_id=str(
                    outcome.get("problem_id")
                    or _mapping(record.get("problem")).get("problem_id")
                    or "unknown-problem"
                ),
                unresolved_class=_class_for_directive(directive.kind, record),
                reason_codes=reason_codes,
                attempt_ids=(run_id,),
                blocker_ids=tuple(
                    dict.fromkeys(
                        str(item) for item in outcome.get("residual_ids", ()) if str(item)
                    )
                ),
            )
            projected["resolution_obligation"] = obligation.as_dict()
        return projected

    _rr.run_problem_recursive = run_problem_recursive_with_director
    _rr._research_director_integration_installed = True
    _rr._research_resolution_v4_installed = True
    _INSTALLED = True


install_research_director_integration()


__all__ = ["_dedupe_reason_codes", "install_research_director_integration"]
