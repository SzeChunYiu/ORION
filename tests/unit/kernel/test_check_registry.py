from __future__ import annotations

import hashlib
from pathlib import Path

from orion.kernel.apply import grade_and_apply
from orion.kernel.checks import claude_lane
from orion.kernel.evidence import expected_binding, resolve_evidence_refs
from orion.kernel.gate import AnswerAuthority, CheckOutcome, run_discriminating_check
from orion.kernel.registry import load_registered_checks
from orion.mechanics.answers import AnswerRecord
from orion.mechanics.model import MechanicDimension
from orion.mechanics.program import current_program_cells, observe_mechanics_program

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_registry_loads_lane_modules():
    checks = load_registered_checks()
    assert set(checks) >= {check.check_id for check in claude_lane.CHECKS}
    for check in checks.values():
        assert check.frozen_at_round is not None
        assert check.lane.strip()


def test_every_registered_check_is_admissible_on_its_own_fixture():
    """Each shipped check must survive its full admission gauntlet.

    `run_discriminating_check` internally re-judges the check against its
    positive fixture, its declared near-miss negatives and the host battery
    before consulting the target cell — so a PASSED here proves admissibility,
    not merely fixture agreement.
    """

    for check in load_registered_checks().values():
        outcome, reasons = run_discriminating_check(check, check.positive_fixture)
        assert outcome is CheckOutcome.PASSED, (check.check_id, reasons)


def _pinned_evidence() -> tuple[str, str]:
    target = REPO_ROOT / "README.md"
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    ref = f"orion:README.md@{digest[:16]}"
    (resolution,) = resolve_evidence_refs((ref,), {"orion": REPO_ROOT})
    assert resolution.resolved, resolution
    return ref, expected_binding(resolution)


def _cross_lane_record(lane: str) -> AnswerRecord:
    ref, digest = _pinned_evidence()
    return AnswerRecord(
        record_id=f"{lane}-transition-demo-1",
        mechanic_id="SEARCH.ROUTE_STOP.v0",
        dimension=MechanicDimension.TRANSITION_MODEL,
        lane=lane,
        evidence_refs=(ref,),
        evidence_bindings=((ref, digest),),
        payload=(
            (
                "transition_semantics",
                (
                    "typed outcomes ROUTE_CONTINUE | ROUTE_REFORMULATE | ROUTE_BUDGET_STOP; deterministic given (route id, per-item decision-coordinate deltas, remaining budget)",
                ),
            ),
        ),
    )


def _grade(record: AnswerRecord):
    cells = current_program_cells()
    before = observe_mechanics_program(cells).open_question_count
    result = grade_and_apply(
        cells,
        (record,),
        evidence_roots={"orion": REPO_ROOT},
        checks=dict(load_registered_checks()),
    )
    after = observe_mechanics_program(result.cells).open_question_count
    (grading,) = result.gradings
    return grading, before, after


def test_same_lane_record_is_never_verified_by_these_checks():
    grading, before, after = _grade(_cross_lane_record("claude"))
    assert grading.authority is AnswerAuthority.EVIDENCE_BOUND
    assert grading.check_outcome is CheckOutcome.LANE_NOT_INDEPENDENT
    assert after == before


def test_cross_lane_record_with_contract_shape_reaches_verified():
    grading, before, after = _grade(_cross_lane_record("chatgpt"))
    assert grading.check_outcome is CheckOutcome.PASSED
    assert grading.authority is AnswerAuthority.VERIFIED
    assert before - after == 1


def test_no_raw_default_cell_passes_any_check():
    """The universal default envelopes must never satisfy a check.

    Validated against the real decomposition, not fixtures: every program cell
    carries only default-layer content before answers land, so a check any of
    them satisfies would license verified closure from shared scaffolding —
    the false-positive mode that makes a checker worse than no checker.
    """

    checks = load_registered_checks().values()
    for cell in current_program_cells():
        for check in checks:
            assert not check.predicate(cell), (check.check_id, cell.mechanic_id)


def test_cross_lane_record_with_assurance_prose_stays_evidence_bound():
    """The near-miss register: confident prose without contract structure."""

    ref, digest = _pinned_evidence()
    record = AnswerRecord(
        record_id="chatgpt-nearmiss-1",
        mechanic_id="SEARCH.ROUTE_STOP.v0",
        dimension=MechanicDimension.TRANSITION_MODEL,
        lane="chatgpt",
        evidence_refs=(ref,),
        evidence_bindings=((ref, digest),),
        payload=(
            (
                "transition_semantics",
                ("this transition is implemented carefully and behaves correctly in all tested scenarios",),
            ),
        ),
    )
    grading, before, after = _grade(record)
    assert grading.check_outcome is CheckOutcome.FAILED
    assert grading.authority is AnswerAuthority.EVIDENCE_BOUND
    assert after == before


def test_the_handoff_check_separates_a_declaration_from_a_relabelling():
    """A field is not its own schema.

    The battery's junk and envelope members set field_id, description and
    schema_ref to one identical string — what a restated question looks like
    forced into a typed shape. Requiring the schema reference to exist apart
    from the field it describes separates a declaration from a relabelling,
    without asserting the schema is correct.
    """

    from orion.kernel.battery import host_battery
    from orion.kernel.checks.claude_lane import _handoff_contract
    from orion.mechanics.model import HandoffField, MechanicCell, MechanicDimension

    def _cell(**fields):
        return MechanicCell(mechanic_id="probe", purpose="p", scope="s", **fields)

    assert not any(
        _handoff_contract(item) for item in host_battery(MechanicDimension.HANDOFF)
    )
    assert not _handoff_contract(
        _cell(handoff_fields=(HandoffField("payload", "stuff", "stuff"),))
    )
    assert not _handoff_contract(
        _cell(handoff_fields=(HandoffField("payload", "d", "prose about handoff"),))
    )
    assert not _handoff_contract(
        _cell(handoff_fields=(HandoffField("nogroup", "d", "orion://a/b"),))
    )
    assert _handoff_contract(
        _cell(
            handoff_fields=(
                HandoffField("probe:group:field", "d", "orion://mechanic/probe/f"),
            )
        )
    )
