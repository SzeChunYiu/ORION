from __future__ import annotations

from pathlib import Path

from orion.kernel.gate import DiscriminatingCheck
from orion.kernel.store import EntryKind, LedgerStore
from orion.kernel.workorder import build_work_order, write_work_order
from orion.mechanics.model import MechanicCell, MechanicDimension
from orion.mechanics.workflow import ORION_WORKFLOW_ROOT_ID

TARGET = "T.WORK.v1"


def _program() -> tuple[MechanicCell, ...]:
    return (
        MechanicCell(
            mechanic_id=ORION_WORKFLOW_ROOT_ID,
            purpose="root",
            scope="one root problem",
            child_mechanic_ids=(TARGET,),
        ),
        MechanicCell(mechanic_id=TARGET, purpose="store step output", scope="one step"),
    )


def _check(lane: str) -> DiscriminatingCheck:
    return DiscriminatingCheck(
        check_id=f"{lane}.storage.v0",
        dimension=MechanicDimension.STORAGE,
        lane=lane,
        predicate=lambda cell: any("ledger" in item for item in cell.storage_contracts),
        positive_fixture=MechanicCell(
            mechanic_id="p", purpose="p", scope="s", storage_contracts=("ledger",)
        ),
        frozen_at_round=0,
    )


def test_the_order_states_the_bar_an_answer_must_clear() -> None:
    """A request that named the question but hid the acceptance criterion would
    invite answers that cannot pass, and the refusals would look like the
    answerer's failure rather than the request's."""

    order = build_work_order(_program(), checks={"c": _check("verifier")}, limit=200)
    item = next(
        item for item in order.items if item.dimension is MechanicDimension.STORAGE
    )
    assert item.writable_fields == ("storage_contracts",)
    assert item.checked_by == ("c",)
    assert item.question


def test_a_lane_is_not_asked_for_work_its_own_check_would_judge() -> None:
    """Handing a lane work it cannot have verified generates effort guaranteed
    to stall at EVIDENCE_BOUND."""

    order = build_work_order(_program(), checks={"c": _check("claude")}, limit=200)
    storage = [
        item for item in order.items if item.dimension is MechanicDimension.STORAGE
    ]
    assert storage
    assert not any(
        item.dimension is MechanicDimension.STORAGE
        for item in order.for_lane("claude")
    )
    assert any(
        item.dimension is MechanicDimension.STORAGE
        for item in order.for_lane("self-orion")
    )


def test_dimensions_no_check_can_judge_are_named_not_hidden() -> None:
    """Answering them produces content that cannot rise above EVIDENCE_BOUND."""

    order = build_work_order(_program(), checks={"c": _check("verifier")}, limit=200)
    assert MechanicDimension.MATHEMATICS.value in order.unverifiable_dimensions
    assert MechanicDimension.STORAGE.value not in order.unverifiable_dimensions


def test_unverifiable_items_are_excluded_from_a_lane_request() -> None:
    order = build_work_order(_program(), checks={}, limit=50)
    assert order.for_lane("any") == ()


def test_prior_attempts_are_reported_so_work_is_not_repeated(tmp_path: Path) -> None:
    store = LedgerStore(tmp_path / "state")
    store.append(
        EntryKind.ANSWER,
        {"mechanic_id": TARGET, "dimension": "STORAGE", "lane": "self-orion"},
    )
    order = build_work_order(
        _program(), checks={"c": _check("verifier")}, store=store, limit=200
    )
    item = next(
        item
        for item in order.items
        if item.mechanic_id == TARGET and item.dimension is MechanicDimension.STORAGE
    )
    assert item.already_attempted_by == ("self-orion",)


def test_the_order_is_writable_for_an_external_lane(tmp_path: Path) -> None:
    order = build_work_order(_program(), checks={"c": _check("verifier")}, limit=20)
    path = write_work_order(order, tmp_path / "orders" / "open.json")
    assert path.is_file() and path.read_text(encoding="utf-8").startswith("{")
