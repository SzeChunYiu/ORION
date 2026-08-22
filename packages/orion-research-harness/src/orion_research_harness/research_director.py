from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from orion.core.residuals import Residual, Responsibility
from orion.core.solution import SolutionStatus


class ResearchDirectiveKind(str, Enum):
    CANNOT_CHECK = "CANNOT_CHECK"
    DIAGNOSE_RESPONSIBILITY = "DIAGNOSE_RESPONSIBILITY"
    RESTORE_CAPABILITY = "RESTORE_CAPABILITY"
    VERIFY_EVIDENCE = "VERIFY_EVIDENCE"
    CHECK_EVALUATION_AUTHORITY = "CHECK_EVALUATION_AUTHORITY"
    ASSESS_OCME = "ASSESS_OCME"
    NAVIGATE_OR_REFRAME = "NAVIGATE_OR_REFRAME"
    ASSESS_SATURATION = "ASSESS_SATURATION"
    VERIFY_OR_REOPEN = "VERIFY_OR_REOPEN"


@dataclass(frozen=True)
class ResearchDirective:
    kind: ResearchDirectiveKind
    paper_ids: tuple[str, ...]
    trigger_residual_ids: tuple[str, ...]
    reason: str
    grants_scientific_authority: bool = False
    grants_novelty_authority: bool = False
    grants_promotion_authority: bool = False
    grants_global_task_stop_authority: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "schema": "ORION.HarnessResearchDirective.v1",
            "kind": self.kind.value,
            "paper_ids": list(self.paper_ids),
            "trigger_residual_ids": list(self.trigger_residual_ids),
            "reason": self.reason,
            "grants_scientific_authority": self.grants_scientific_authority,
            "grants_novelty_authority": self.grants_novelty_authority,
            "grants_promotion_authority": self.grants_promotion_authority,
            "grants_global_task_stop_authority": self.grants_global_task_stop_authority,
        }


_NAVIGATION_RESPONSIBILITIES = {
    Responsibility.QUESTION,
    Responsibility.REPRESENTATION,
    Responsibility.SEARCH,
    Responsibility.ROUTING,
    Responsibility.DECOMPOSITION,
    Responsibility.INTERFACE,
    Responsibility.MEASUREMENT,
}

_PRECEDENCE: tuple[tuple[Responsibility, ResearchDirectiveKind, tuple[str, ...], str], ...] = (
    (
        Responsibility.EXECUTION,
        ResearchDirectiveKind.RESTORE_CAPABILITY,
        ("P15",),
        "execution/capability responsibility is non-compensatory; restore a valid host capability boundary before further scientific inference",
    ),
    (
        Responsibility.EVIDENCE,
        ResearchDirectiveKind.VERIFY_EVIDENCE,
        ("P4", "P8"),
        "evidence responsibility requires acquisition/content binding/independent verification before scientific promotion",
    ),
    (
        Responsibility.EVALUATOR,
        ResearchDirectiveKind.CHECK_EVALUATION_AUTHORITY,
        ("P4", "P8", "P14"),
        "evaluator responsibility requires a protected evaluation/authority check before accepting the scientific disposition",
    ),
    (
        Responsibility.METHOD,
        ResearchDirectiveKind.ASSESS_OCME,
        ("P10",),
        "method responsibility opens obstruction-certified method-language assessment; it does not directly license a method-language jump",
    ),
)


def _material(residuals: Sequence[Residual]) -> tuple[Residual, ...]:
    return tuple(item for item in residuals if item.material)


def direct_research(
    *,
    solution_status: SolutionStatus,
    material_residuals: Sequence[Residual],
    resource_bound_hit: bool = False,
    identity_ambiguity_hit: bool = False,
) -> ResearchDirective:
    """Return the next paper-aware research-control action.

    This is a control-plane routing decision only. It cannot close a scientific
    task or mint authority. In particular, a verified solution with no material
    residuals is routed through bounded saturation rather than task stop.
    """

    residuals = _material(material_residuals)
    all_ids = tuple(sorted(item.residual_id for item in residuals))

    if resource_bound_hit or identity_ambiguity_hit:
        reasons: list[str] = []
        if resource_bound_hit:
            reasons.append("recursive resource bound was reached")
        if identity_ambiguity_hit:
            reasons.append("material residual identity is ambiguous")
        return ResearchDirective(
            ResearchDirectiveKind.CANNOT_CHECK,
            ("P1", "P2", "P15"),
            all_ids,
            "; ".join(reasons) + "; do not round an orchestration bound up to scientific closure",
        )

    ambiguous = tuple(
        item
        for item in residuals
        if len(tuple(dict.fromkeys(item.candidate_responsibilities))) != 1
    )
    if ambiguous:
        return ResearchDirective(
            ResearchDirectiveKind.DIAGNOSE_RESPONSIBILITY,
            ("P1", "P5", "P6"),
            tuple(sorted(item.residual_id for item in ambiguous)),
            "one or more material residuals lack a singular causal responsibility; diagnose before selecting a revision/search/evidence mechanic",
        )

    if residuals:
        by_responsibility: dict[Responsibility, list[Residual]] = {}
        for residual in residuals:
            responsibility = residual.candidate_responsibilities[0]
            by_responsibility.setdefault(responsibility, []).append(residual)

        for responsibility, kind, papers, reason in _PRECEDENCE:
            selected = by_responsibility.get(responsibility)
            if selected:
                return ResearchDirective(
                    kind,
                    papers,
                    tuple(sorted(item.residual_id for item in selected)),
                    reason,
                )

        navigable = [
            item
            for item in residuals
            if item.candidate_responsibilities[0] in _NAVIGATION_RESPONSIBILITIES
        ]
        if navigable:
            return ResearchDirective(
                ResearchDirectiveKind.NAVIGATE_OR_REFRAME,
                ("P1", "P2", "P7"),
                tuple(sorted(item.residual_id for item in navigable)),
                "formulation/search/interface responsibility remains open; use typed reframe/navigation routes and keep route-stop separate from task-stop",
            )

        # Future Responsibility enum values fail closed rather than silently
        # inheriting an arbitrary paper mechanic.
        return ResearchDirective(
            ResearchDirectiveKind.DIAGNOSE_RESPONSIBILITY,
            ("P1", "P6"),
            all_ids,
            "material residual responsibility is not mapped by the frozen research-director policy",
        )

    if solution_status is SolutionStatus.SOLVED_VERIFIED:
        return ResearchDirective(
            ResearchDirectiveKind.ASSESS_SATURATION,
            ("P2", "P5", "P7"),
            (),
            "verified answer has no material residuals, but global task stop still requires bounded independent-route/multi-axis saturation",
        )

    return ResearchDirective(
        ResearchDirectiveKind.VERIFY_OR_REOPEN,
        ("P1", "P4", "P7", "P8"),
        (),
        "no material residual is recorded but the solution is not verified; verify evidence or reopen the relevant dependency/obligation instead of claiming closure",
    )


__all__ = [
    "ResearchDirective",
    "ResearchDirectiveKind",
    "direct_research",
]
