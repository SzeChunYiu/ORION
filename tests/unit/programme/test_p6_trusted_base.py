"""P6's disclosed trusted base must match what its formal code imports."""

from __future__ import annotations

from pathlib import Path

from orion.programme.p6_trusted_base import (
    DISCLOSED_KERNEL,
    DISCLOSED_SOLVER,
    EXIT_CANNOT_CHECK,
    EXIT_PASS,
    derive,
    main,
)

LIMITS = (
    Path(__file__).resolve().parents[3]
    / "papers/paper-06-formal-epistemic-structures-and-mechanics/manuscript/sections/07-limits.tex"
)


def test_disclosure_matches_the_imports() -> None:
    orion, external = derive()
    assert orion == set(DISCLOSED_KERNEL)
    assert external == set(DISCLOSED_SOLVER)


def test_checker_passes_on_the_live_tree() -> None:
    assert main([]) == EXIT_PASS


def test_missing_tree_is_not_a_pass() -> None:
    assert main(["--root", str(Path("/nonexistent"))]) == EXIT_CANNOT_CHECK


def test_every_disclosed_module_is_named_in_the_paper() -> None:
    """A disclosure the reader cannot see is not a disclosure."""
    text = LIMITS.read_text()
    for module in DISCLOSED_KERNEL:
        leaf = module.split(".")[-1].replace("_", r"\_")
        assert leaf in text, f"{module} is trusted but not stated in the limits section"
    for solver in DISCLOSED_SOLVER:
        assert solver.upper() in text or solver in text


def test_the_external_review_boundary_is_still_stated() -> None:
    """The other half of the box; it must not be lost while adding the first."""
    text = LIMITS.read_text().lower()
    assert "proof review remains outstanding" in text


def test_the_solver_is_marked_unreviewed() -> None:
    text = LIMITS.read_text().lower()
    assert "not reviewed here" in text
