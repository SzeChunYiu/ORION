"""The grid's blocker is measured on this machine, not asserted in a constant.

``ENVIRONMENT_BOUNDARY`` records what the 2026-08-21 freeze expected: no
open-weight checkpoint, provider access refused, grid not executable here. Two of
those are claims about a machine, and nothing checked them. An environment that
later acquired a checkpoint would still have been told it had none, and the grid
would have stayed ``CANNOT_CHECK`` on a stale sentence rather than on a fact --
a blocker outliving the condition it describes, which is the failure this
programme keeps finding elsewhere.

So the declaration stays as a record of what was expected, and the same facts are
measured beside it. These tests pin that the probe measures rather than restates,
and that a disagreement would be reported loudly instead of resolved in the
constant's favour.
"""

from __future__ import annotations

from pathlib import Path

from orion.study.p9 import frontier_grid as grid

REPO_ROOT = Path(__file__).resolve().parents[4]


def test_the_probe_reads_the_machine_rather_than_the_constant(tmp_path: Path) -> None:
    """Pointed at an empty tree it must still answer, and answer about that tree."""

    empty = grid.probe_environment(tmp_path)
    assert empty["measured_on_this_machine"] is True
    assert empty["open_weight_checkpoint_present"] is False
    assert empty["checkpoints_found"] == []

    (tmp_path / "model.safetensors").write_bytes(b"not a real checkpoint")
    seen = grid.probe_environment(tmp_path)
    assert seen["open_weight_checkpoint_present"] is True
    assert seen["checkpoints_found"] == ["model.safetensors"]


def test_a_checkpoint_alone_does_not_make_the_grid_executable(tmp_path: Path) -> None:
    """A checkpoint nothing can load is not a scale ladder.

    Both halves are required, so finding weights on disk cannot by itself flip
    the grid into claiming it can walk a model-scale ladder.
    """

    (tmp_path / "model.safetensors").write_bytes(b"not a real checkpoint")
    probe = grid.probe_environment(tmp_path)
    assert probe["open_weight_checkpoint_present"] is True
    if not probe["loading_runtimes_present"]:
        assert probe["grid_executable_here"] is False


def test_the_declared_boundary_is_checked_against_the_measurement() -> None:
    agreement = grid.environment_agreement(REPO_ROOT)
    assert set(agreement) >= {"declared", "measured", "agrees", "disagreements", "detail"}
    assert agreement["declared"] == dict(grid.ENVIRONMENT_BOUNDARY)
    # On this machine they agree; the point is that the comparison happens.
    assert agreement["agrees"] is (not agreement["disagreements"])


def test_a_stale_declaration_is_reported_rather_than_absorbed(tmp_path: Path, monkeypatch) -> None:
    """The case the constant could not have noticed.

    If the machine acquires what the freeze said it lacked, the report must say
    the declaration is stale and that the grid should be executed here -- not
    quietly keep reporting the frozen sentence.
    """

    (tmp_path / "model.safetensors").write_bytes(b"not a real checkpoint")
    monkeypatch.setattr(grid, "CHECKPOINT_RUNTIMES", ("json",))  # always importable
    agreement = grid.environment_agreement(tmp_path)
    assert agreement["agrees"] is False
    assert "open_weight_checkpoint_present" in agreement["disagreements"]
    assert "grid_executable_here" in agreement["disagreements"]
    assert "should be executed here" in agreement["detail"]


def test_the_grid_report_carries_the_agreement() -> None:
    payload = grid.assess_grid({}, (), repo_root=REPO_ROOT)
    assert payload["outcome"] == "CANNOT_CHECK"
    assert payload["verdict"] == grid.VERDICT_NO_CELL_EXECUTED
    assert payload["environment_agreement"]["measured"]["measured_on_this_machine"] is True


def test_the_surrogate_is_still_refused() -> None:
    """The one thing that must not change: no capacity ladder wearing S*."""

    assert "not a model-scale ladder" in grid.ENVIRONMENT_BOUNDARY["surrogate_refused"]
