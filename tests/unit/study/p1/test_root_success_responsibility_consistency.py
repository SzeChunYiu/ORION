"""Root success must be responsibility-consistent (issue #986).

The P1 campaign's only non-floor cell was a proxy false positive. On `p1-c111`
gold responsibility is INTERFACE; the shared lexical detector matched an
EXECUTION marker ("crashes"); a system repaired the execution symptom, cleared
the only material cue it could see, and `solved()` returned True. The resulting
record simultaneously carried `root_success=True`, `responsibility_correct=False`
and `failure_mode=MISSED_REFRAME` — a record cannot be both a root success and a
missed reframe.

These tests pin the predicate, not the vocabulary. Extending the marker table so
the detector "sees" INTERFACE on this case would be outcome-tuning and is
explicitly forbidden by FLOOR_EFFECT_DIAGNOSIS_20260823.md.
"""

from __future__ import annotations

import json
from pathlib import Path

from orion.study.p1.cases import (
    AdjudicationStatus,
    HiddenShiftCase,
    ProtectedGold,
    Split,
    TaskFamily,
)
from orion.study.p1.metrics import FailureMode, ScoreStatus, score_case
from orion.study.p1.systems import SystemTrace

ROOT = Path(__file__).resolve().parents[4]
SCORED = (
    ROOT
    / "papers/orion-11-recursive-epistemic-reconstruction/results/raw/test_scored.jsonl"
)
SUITE = "fingerprint-under-test"


def _case(responsibility: str = "INTERFACE") -> HiddenShiftCase:
    return HiddenShiftCase(
        case_id="p1-consistency-001",
        task_family=TaskFamily.HIDDEN_DECOMPOSITION,
        public_prompt="the batch job crashes on the third shard every night",
        observable_resources=("resource.one",),
        protected_gold=ProtectedGold(
            reframe_required=True,
            responsibility_family=responsibility,
            target_coordinates=("W.interfaces", "interface:demand_signal"),
            dependencies_to_reopen=("dep.alpha",),
            root_success_rubric="the demand signal is renegotiated at the interface",
            dependency_depth=1,
        ),
        budget_class="standard",
        adjudication_status=AdjudicationStatus.ADJUDICATED,
        split=Split.TEST,
    )


def _trace(case: HiddenShiftCase, *, responsibility: str, **overrides) -> SystemTrace:
    payload = {
        "case_id": case.case_id,
        "system_id": "system-under-test",
        "seed": 0,
        "reframed": True,
        "responsibility_family": responsibility,
        "target_coordinates": case.protected_gold.target_coordinates,
        "reopened": case.protected_gold.dependencies_to_reopen,
        "root_solved": True,
        "max_recursion_depth": 1,
    }
    payload.update(overrides)
    return SystemTrace(**payload)


def _score(case: HiddenShiftCase, trace: SystemTrace):
    return score_case(
        case,
        trace,
        system_id="system-under-test",
        seed=0,
        suite_fingerprint=SUITE,
    )


def test_clearing_the_wrong_responsibility_is_not_a_root_success() -> None:
    """The c111 shape: cue cleared in a family gold does not name."""

    case = _case(responsibility="INTERFACE")
    score = _score(case, _trace(case, responsibility="EXECUTION"))

    assert score.status is ScoreStatus.SCORED
    assert score.responsibility_correct is False
    assert score.root_success is False, (
        "a system that cleared an EXECUTION symptom did not solve an INTERFACE root"
    )


def test_unclaimed_responsibility_is_not_a_root_success() -> None:
    """An unlabelled clearing names no root, so it cannot have cleared one."""

    case = _case(responsibility="INTERFACE")
    score = _score(case, _trace(case, responsibility=""))

    assert score.responsibility_correct is False
    assert score.root_success is False


def test_responsibility_consistent_clearing_still_succeeds() -> None:
    """The predicate tightens; it must not zero genuine successes.

    Without this the fix could pass by making root_success unreachable.
    """

    case = _case(responsibility="INTERFACE")
    score = _score(case, _trace(case, responsibility="INTERFACE"))

    assert score.responsibility_correct is True
    assert score.root_success is True


def test_root_success_never_coexists_with_missed_reframe() -> None:
    """The contradiction the frozen archive actually recorded.

    Reproduces the exact `p1-c111` / `static_react_tool_workflow` trace shape:
    the system never reframed, named EXECUTION against INTERFACE gold, and still
    reported the root as solved.
    """

    case = _case(responsibility="INTERFACE")
    score = _score(
        case,
        _trace(
            case,
            responsibility="EXECUTION",
            reframed=False,
            target_coordinates=(),
            reopened=(),
            max_recursion_depth=0,
        ),
    )

    assert score.failure_mode is FailureMode.MISSED_REFRAME
    assert score.root_success is False, (
        "MISSED_REFRAME and root_success are mutually exclusive by construction"
    )


def test_frozen_archive_successes_are_exactly_the_known_false_positive() -> None:
    """Guards the scope of the defect against the real campaign archive.

    Every `root_success=True` record in the 2,880-record frozen archive is
    `p1-c111` with `responsibility_correct=False`. The archive is retired to
    instrument-validation status and is deliberately NOT rewritten; this test
    documents that the historical bytes carry the defect the scorer no longer
    reproduces.
    """

    if not SCORED.exists():  # pragma: no cover - archive is committed
        raise AssertionError(f"CANNOT_CHECK: frozen archive missing at {SCORED}")

    rows = [json.loads(line) for line in SCORED.read_text(encoding="utf-8").splitlines() if line]
    assert len(rows) == 2880
    successes = [row for row in rows if row.get("root_success")]

    assert {row["case_id"] for row in successes} == {"p1-c111"}
    assert all(row["responsibility_correct"] is False for row in successes)
    assert all(row["failure_mode"] == "MISSED_REFRAME" for row in successes)


def test_rescoring_the_frozen_archive_under_the_fixed_predicate_yields_no_successes() -> None:
    """The direction of effect, stated: the headline moves 1/48 -> 0/48.

    This is the honest direction. It is recorded here so the change cannot be
    mistaken for one that flatters the result.
    """

    if not SCORED.exists():  # pragma: no cover - archive is committed
        raise AssertionError(f"CANNOT_CHECK: frozen archive missing at {SCORED}")

    rows = [json.loads(line) for line in SCORED.read_text(encoding="utf-8").splitlines() if line]
    consistent = [
        row
        for row in rows
        if row.get("root_success") and row.get("responsibility_correct") is True
    ]
    assert consistent == [], (
        "no archived success survives responsibility consistency; the campaign floor is 0/48"
    )
