#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from orion.transfer.v2.epistemic_computation import (
    ComputationActionState,
    assess_computation_action,
    build_computation_action,
    select_epistemic_computation,
)
from orion.transfer.v2.social_evidence import (
    ContributionState,
    TruthfulnessState,
    assess_contribution_credit,
    assess_social_evidence_independence,
    build_social_contribution,
    build_social_evidence_record,
)
from orion.transfer.v2.uncertainty_containment import (
    ValidityState,
    assess_containment,
    build_validity_envelope,
)

ROOT = Path(__file__).resolve().parent
PANEL = ROOT / "T4_T6_COUNTERMODELS_V1.json"
SUMMARY = ROOT / "T4_T6_COUNTERMODEL_SUMMARY_V1.json"


def _action(name: str, *, value: float, cost: float, requirements=(), discharges=(), authorities=()):
    return build_computation_action(
        action_id=name,
        claim_id="claim:t46",
        kind="CALLER_DECLARED",
        expected_decision_value=value,
        cost=cost,
        hard_requirements=requirements,
        discharges_obligations=discharges,
        required_authorities=authorities,
    )


def _compute(kind: str):
    if kind == "compute_mandatory":
        verify = _action("protected-verify", value=0.0, cost=2.0, discharges=("must-verify",), authorities=("host",))
        llm = _action("call-llm", value=10.0, cost=1.0)
        assessments = (
            assess_computation_action(verify, requirement_states={}, available_authorities=("host",)),
            assess_computation_action(llm, requirement_states={}),
        )
        return select_epistemic_computation((verify, llm), assessments, active_hard_obligations=("must-verify",))
    if kind == "compute_uncovered":
        plan = _action("plan", value=100.0, cost=1.0)
        return select_epistemic_computation(
            (plan,),
            (assess_computation_action(plan, requirement_states={}),),
            active_hard_obligations=("must-verify",),
        )
    if kind == "compute_unresolved":
        verify = _action("verify", value=0.0, cost=1.0, requirements=("ready",), discharges=("must-verify",))
        assessment = assess_computation_action(
            verify,
            requirement_states={"ready": ComputationActionState.UNRESOLVED},
        )
        return select_epistemic_computation((verify,), (assessment,), active_hard_obligations=("must-verify",))
    if kind == "compute_tie":
        left = _action("retrieve", value=4.0, cost=1.0)
        right = _action("diagnose", value=5.0, cost=2.0)
        assessments = tuple(assess_computation_action(item, requirement_states={}) for item in (left, right))
        return select_epistemic_computation((left, right), assessments)
    if kind == "compute_stop":
        wait = _action("wait", value=1.0, cost=1.0)
        plan = _action("plan", value=1.0, cost=2.0)
        assessments = tuple(assess_computation_action(item, requirement_states={}) for item in (wait, plan))
        return select_epistemic_computation((wait, plan), assessments)
    raise ValueError(kind)


def _envelope():
    return build_validity_envelope(
        envelope_id="env:t46",
        claim_id="claim:t46",
        subject_id="model:t46",
        context_states={
            "supported": ValidityState.SUPPORTED,
            "invalid": ValidityState.INVALID,
            "unresolved": ValidityState.UNRESOLVED,
        },
        evidence_ids=("evidence:validity",),
    )


def _social_record(report_id: str, agent_id: str, *, direct=(), upstream=(), truth=TruthfulnessState.SATISFIED):
    return build_social_evidence_record(
        report_id=report_id,
        agent_id=agent_id,
        claim_id="claim:t46",
        direct_observation_ids=direct,
        upstream_source_ids=upstream,
        truthfulness_state=truth,
    )


def _social(kind: str):
    if kind == "social_correlated":
        return assess_social_evidence_independence(
            (
                _social_record("r1", "a", direct=("oa",), upstream=("shared",)),
                _social_record("r2", "b", direct=("ob",), upstream=("shared",)),
            )
        )
    if kind == "social_independent":
        return assess_social_evidence_independence(
            (
                _social_record("r1", "a", direct=("oa",), upstream=("sa",)),
                _social_record("r2", "b", direct=("ob",), upstream=("sb",)),
            )
        )
    if kind == "social_unresolved":
        return assess_social_evidence_independence(
            (
                _social_record("r1", "a", direct=("oa",), upstream=()),
                _social_record("r2", "b", direct=("ob",), upstream=("sb",), truth=TruthfulnessState.UNRESOLVED),
            )
        )
    if kind == "social_unreliable":
        return assess_social_evidence_independence(
            (
                _social_record("r1", "a", direct=("oa",), upstream=("sa",), truth=TruthfulnessState.VIOLATED),
                _social_record("r2", "b", direct=("ob",), upstream=("sb",)),
            )
        )
    raise ValueError(kind)


def _contribution(name: str, state: ContributionState):
    return build_social_contribution(
        contribution_id=f"c:{name}",
        contributor_id=name,
        outcome_id="outcome:t46",
        state=state,
        evidence_ids=(f"e:{name}",),
    )


def _credit(kind: str):
    if kind == "credit_unresolved":
        return assess_contribution_credit(
            (_contribution("visible", ContributionState.OBSERVED), _contribution("hidden", ContributionState.UNRESOLVED))
        )
    if kind == "credit_shared":
        return assess_contribution_credit(
            (_contribution("left", ContributionState.OBSERVED), _contribution("right", ContributionState.OBSERVED))
        )
    if kind == "credit_exclusive":
        return assess_contribution_credit(
            (_contribution("visible", ContributionState.OBSERVED), _contribution("other", ContributionState.ABSENT))
        )
    raise ValueError(kind)


def evaluate(case: dict[str, object]) -> tuple[str, str | None]:
    kind = str(case["kind"])
    if kind.startswith("compute_"):
        report = _compute(kind)
        return report.status.value, report.selected_action_id
    if kind.startswith("contain_"):
        context = {
            "contain_supported": "supported",
            "contain_invalid": "invalid",
            "contain_unresolved": "unresolved",
            "contain_missing": "missing",
        }[kind]
        report = assess_containment(_envelope(), context_id=context)
        return report.status.value, None
    if kind.startswith("social_"):
        report = _social(kind)
        return report.status.value, None
    report = _credit(kind)
    return report.status.value, report.exclusive_contributor_id


def run(panel: dict[str, object]) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for case in panel["cases"]:
        actual_status, actual_selected = evaluate(case)
        expected_status = str(case["expected_status"])
        expected_selected = case.get("expected_selected")
        passed = actual_status == expected_status and actual_selected == expected_selected
        rows.append(
            {
                "id": case["id"],
                "kind": case["kind"],
                "expected_status": expected_status,
                "actual_status": actual_status,
                "expected_selected": expected_selected,
                "actual_selected": actual_selected,
                "pass": passed,
            }
        )
    n_pass = sum(bool(row["pass"]) for row in rows)
    return {
        "result_version": "P6_T4_T6_COUNTERMODEL_SUMMARY_V1",
        "protocol_id": panel["protocol_id"],
        "n_cases": len(rows),
        "n_pass": n_pass,
        "accuracy": n_pass / len(rows),
        "rows": rows,
        "terminal": panel["expected_terminal"] if n_pass == len(rows) else "T4_T6_COUNTERMODEL_FAILURE",
        "claim_ceiling": panel["claim_ceiling"],
        "grants_scientific_authority": False,
        "grants_self_orion_adoption": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    panel = json.loads(PANEL.read_text())
    result = run(panel)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        SUMMARY.write_text(text)
    if args.check:
        if not SUMMARY.exists() or SUMMARY.read_text() != text:
            raise SystemExit("T4/T6 countermodel summary drift")
    if not args.write and not args.check:
        print(text, end="")


if __name__ == "__main__":
    main()
