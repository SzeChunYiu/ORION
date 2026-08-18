"""The merged #8 execution path cannot launch an unbound live trial.

`test_phase2_preflight.py` proves `assess_phase2_preflight` refuses an unbound or
divergent freeze. That is a property of the function. It says nothing about the
workflow that actually spends provider budget, and the workflow is the artifact
an operator triggers.

The gap is narrow and specific: `p5_phase2_live_execution.yml` builds its
`Phase2ClosurePreflight` without passing `frozen_packet=`, so the packet-identity
comparison has no expectation to compare against. That must resolve to
`BIND_FROZEN_PACKET`, and the workflow must abort on it before any packet is
built or any task is run. These tests pin exactly that, so a later edit that
either supplies a fabricated binding or moves the abort below execution fails
here rather than in a live run.

This file elects no canonical registry and binds no subject. It asserts only
that the merged execution path stays closed while #8's external bindings are
absent.
"""

from __future__ import annotations

import re
from pathlib import Path

from orion.self_orion.phase2_preflight import (
    DEEP_TARGET_TASK,
    WIDE_LITERATURE_TASK,
    FrozenPacketBinding,
    Phase2ClosurePreflight,
    Phase2PreflightStatus,
    assess_phase2_preflight,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "p5_phase2_live_execution.yml"

# Well-formed and mutually distinct, so nothing here fails for being hash-shaped
# wrong. The point is that shape is not enough.
SUBJECT_HASH = "1" * 64
PROVIDER_HASH = "2" * 64
EVALUATOR_HASH = "3" * 64


def _workflow_text() -> str:
    return WORKFLOW_PATH.read_text(encoding="utf-8")


def _workflow_preflight_call(text: str) -> str:
    """The literal `Phase2ClosurePreflight(...)` call as the workflow writes it."""

    start = text.index("Phase2ClosurePreflight(")
    depth = 0
    for offset in range(start, len(text)):
        character = text[offset]
        if character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
            if depth == 0:
                return text[start : offset + 1]
    raise AssertionError("unterminated Phase2ClosurePreflight( call in the workflow")


def _workflow_preflight() -> Phase2ClosurePreflight:
    """Rebuild the workflow's preflight in-process, run-time values substituted.

    Only values the runner computes at execution time are substituted (the three
    hashes, the epoch, the budget). Every value the workflow hard-codes is copied
    verbatim, and the absence of `frozen_packet=` -- the property under test -- is
    reproduced by not passing it.
    """

    call = _workflow_preflight_call(_workflow_text())
    protocol_id = re.search(r"protocol_id='([^']+)'", call)
    baseline_id = re.search(r"baseline_id='([^']+)'", call)
    assert protocol_id is not None, "workflow no longer hard-codes protocol_id"
    assert baseline_id is not None, "workflow no longer hard-codes baseline_id"
    return Phase2ClosurePreflight(
        protocol_id=protocol_id.group(1),
        subject_revision_hash=SUBJECT_HASH,
        provider_manifest_hash=PROVIDER_HASH,
        evaluator_artifact_hash=EVALUATOR_HASH,
        evaluation_epoch_id="github-actions-000000-attempt-1",
        baseline_id=baseline_id.group(1),
        resource_budget_units=32.0,
    )


def test_workflow_supplies_no_frozen_packet_binding() -> None:
    call = _workflow_preflight_call(_workflow_text())
    assert "frozen_packet=" not in call
    assert "tasks=" not in call


def test_workflow_preflight_cannot_reach_ready_to_execute() -> None:
    report = assess_phase2_preflight(_workflow_preflight())
    assert report.status is not Phase2PreflightStatus.READY_TO_EXECUTE_SHADOW_TRIAL
    assert report.status is Phase2PreflightStatus.BIND_FROZEN_PACKET
    assert report.blockers == ("frozen_packet_binding_absent",)
    assert report.grants_phase2_closure is False
    assert report.grants_governed_self_orion is False


def test_workflow_aborts_before_building_or_running_a_packet() -> None:
    text = _workflow_text()
    abort = text.index("Phase-2 preflight did not reach READY_TO_EXECUTE_SHADOW_TRIAL")
    build = text.index("build_frozen_live_trial_packet(preflight)")
    run = text.index("harness.runner.run(packet)")
    assert abort < build < run
    assert "raise RuntimeError" in text[text.rindex("\n", 0, abort) : abort]


def test_no_alarm_a_fully_bound_workflow_preflight_would_reach_ready() -> None:
    """The gate is closed by the missing binding, not closed unconditionally.

    Without this control the three assertions above would still pass if
    `assess_phase2_preflight` had regressed into refusing everything, and a gate
    that never opens is indistinguishable from a gate that is broken.
    """

    preflight = _workflow_preflight()
    bound = Phase2ClosurePreflight(
        protocol_id=preflight.protocol_id,
        subject_revision_hash=preflight.subject_revision_hash,
        provider_manifest_hash=preflight.provider_manifest_hash,
        evaluator_artifact_hash=preflight.evaluator_artifact_hash,
        evaluation_epoch_id=preflight.evaluation_epoch_id,
        baseline_id=preflight.baseline_id,
        resource_budget_units=preflight.resource_budget_units,
        frozen_packet=FrozenPacketBinding(
            packet_fingerprint="4" * 64,
            subject_revision_hash=preflight.subject_revision_hash,
            provider_manifest_hash=preflight.provider_manifest_hash,
            evaluator_artifact_hash=preflight.evaluator_artifact_hash,
            evaluation_epoch_id=preflight.evaluation_epoch_id,
            baseline_id=preflight.baseline_id,
            resource_budget_units=preflight.resource_budget_units,
            task_ids=(WIDE_LITERATURE_TASK.task_id, DEEP_TARGET_TASK.task_id),
            ground_truth_bound_task_ids=tuple(
                task.task_id
                for task in (WIDE_LITERATURE_TASK, DEEP_TARGET_TASK)
                if task.ground_truth_bound
            ),
        ),
    )
    report = assess_phase2_preflight(bound)
    assert report.status is Phase2PreflightStatus.READY_TO_EXECUTE_SHADOW_TRIAL
    assert report.blockers == ()
