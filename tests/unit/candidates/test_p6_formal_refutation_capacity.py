"""P6's two graph checkers, and the refutation capacity they now have.

`papers/paper-06-.../formal/check_finite_models.py::check_reopening` and
`check_theory_closure_v2_1.py::check_root_inclusive_safety` are the two places
where P6's formal core asserts something about a reopening operator. Until
2026-08-22 their assertions were `(A \\ B) & B == {}`, `x == x`, `A <= A | B` and
`B <= A | B` -- the defining properties of the operators that built their own
right-hand sides. Every wrong graph operator substituted for `descendants` was
accepted, and the published `(543, 130320)` and `(960, 2048)` did not move for
any of them.

This file is split in two, and the split is the point.

*What the repair bought* is pinned as refutations that must not go away: the
per-check refuted sets, the panel coverage, and the substitution table that
re-derives the before column on every run.

*What the repair did not buy* is pinned just as hard. `check_reopening` still
implements V1's non-root-inclusive operator, and two of its three assertions
still accept V2.1's `Aff_D(E,X)`; the V2.1 check still enumerates only forward
DAGs, so nothing it says about node "a" being downstream is falsifiable; its
`certified` axis is still constant. A test that pinned only the good news would
let those quietly stop being reported.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from itertools import combinations
from pathlib import Path
from typing import Any

import pytest

from orion.programme.records import Outcome
from orion.programme.refutation_capacity import (
    MechanizedCheck,
    UnrefutableCheck,
    divergence_of,
    measure_refutation_capacity,
    require_refutable,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FORMAL = REPO_ROOT / "papers/paper-06-formal-epistemic-structures-and-mechanics/formal"

#: The signature `REPRODUCE.md` publishes for the primary deterministic checker.
FINITE_MODEL_SIGNATURE = (
    "P6 finite-model checks: PASS",
    "  DAGs enumerated: 543",
    "  reopening cases: 130320",
    "  scientific-projection separated-commutation cases: 1536",
    "  ordered-history distinction / independent trace equivalence: confirmed",
    "  non-escalation compositions: 8192",
    "  residual-obligation preservation fixture: confirmed",
    "  recursive self-loop countermodel: detected",
    "  candidate-controlled authorization countermodel: detected",
)


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def audit() -> Any:
    return _load("p6_formal_refutation_audit", FORMAL / "refutation_audit.py")


@pytest.fixture(scope="module")
def reports(audit: Any) -> dict[str, dict[str, Any]]:
    payload = audit.report_as_json(audit.audit_p6_graph_checkers())
    return {str(item["checker_id"]): item for item in payload["checkers"]}


def _capacities(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item["check_id"]): item for item in report["capacities"]}


def _run(relative_path: str) -> str:
    completed = subprocess.run(
        [sys.executable, str(REPO_ROOT / relative_path)],
        cwd=REPO_ROOT,
        env={**os.environ, "PYTHONPATH": str(REPO_ROOT / "src")},
        check=True,
        capture_output=True,
        text=True,
        timeout=90,
    )
    return completed.stdout


# ---------------------------------------------------------------------------
# The published numbers, which the repair had to leave alone
# ---------------------------------------------------------------------------


def test_the_finite_model_signature_is_byte_for_byte_what_reproduce_publishes() -> None:
    output = _run(
        "papers/paper-06-formal-epistemic-structures-and-mechanics/formal/check_finite_models.py"
    )
    assert output.splitlines() == list(FINITE_MODEL_SIGNATURE)


def test_the_theory_closure_signature_is_unchanged() -> None:
    output = _run(
        "papers/paper-06-formal-epistemic-structures-and-mechanics/formal/"
        "check_theory_closure_v2_1.py"
    )
    lines = output.splitlines()
    assert lines[0] == "P6 THEORY CLOSURE V2.1: PASS"
    assert "root_inclusive_safety: (960, 2048)" in lines


def test_the_two_repaired_functions_return_their_published_counts(audit: Any) -> None:
    assert audit.finite_models.check_reopening() == (543, 130320)
    assert audit.theory_closure.check_root_inclusive_safety() == (960, 2048)


# ---------------------------------------------------------------------------
# What the repair bought
# ---------------------------------------------------------------------------


def test_every_live_wrong_operator_was_accepted_before_and_none_after(
    reports: dict[str, dict[str, Any]],
) -> None:
    """The failure record's own diagnostic, re-derived rather than quoted."""

    for checker_id, live_count in (
        ("check_finite_models.check_reopening", 8),
        ("check_theory_closure_v2_1.check_root_inclusive_safety", 7),
    ):
        entry = reports[checker_id]["operator_substitution"]
        assert len(entry["live"]) == live_count, entry
        assert entry["accepted_before_repair"] == entry["live"]
        assert entry["accepted_after_repair"] == []
        assert entry["rejected_inert_after_repair"] == []


def test_the_reopening_checks_refute_exactly_these_operators(
    reports: dict[str, dict[str, Any]],
) -> None:
    capacities = _capacities(reports["check_finite_models.check_reopening"])
    assert set(capacities["reopening.sufficiency"]["refuted"]) == {
        "retain_everything",
        "direct_successors_only",
        "depth_capped_at_two",
        "ancestors_reopened",
        "first_node_immune",
    }
    assert set(capacities["reopening.minimality"]["refuted"]) == {
        "retain_nothing",
        "ancestors_reopened",
        "undirected_reachability",
        "first_node_always_reopened",
    }
    assert capacities["reopening.exactness"]["survivors"] == []
    for capacity in capacities.values():
        assert Outcome(capacity["outcome"]) is Outcome.PASS


def test_sufficiency_and_minimality_are_not_the_same_claim(
    reports: dict[str, dict[str, Any]],
) -> None:
    """Each direction rejects an operator the other accepts, so both are load-bearing."""

    capacities = _capacities(reports["check_finite_models.check_reopening"])
    sufficiency = set(capacities["reopening.sufficiency"]["refuted"])
    minimality = set(capacities["reopening.minimality"]["refuted"])
    assert "first_node_immune" in sufficiency - minimality
    assert "first_node_always_reopened" in minimality - sufficiency


def test_the_root_inclusive_checks_refute_exactly_these_operators(
    reports: dict[str, dict[str, Any]],
) -> None:
    capacities = _capacities(
        reports["check_theory_closure_v2_1.check_root_inclusive_safety"]
    )
    assert set(capacities["root_inclusive_safety.root_term"]["refuted"]) == {
        "nothing_affected",
        "descendants_only",
    }
    assert set(capacities["root_inclusive_safety.descendant_term"]["refuted"]) == {
        "nothing_affected",
        "descendants_only",
        "changed_roots_only",
        "direct_successors_only",
        "depth_capped_at_two",
        "ancestors_instead_of_descendants",
    }
    assert set(capacities["root_inclusive_safety.minimality"]["refuted"]) == {
        "full_reset",
        "ancestors_instead_of_descendants",
        "undirected_reachability",
        "one_extra_claim",
    }
    for capacity in capacities.values():
        assert Outcome(capacity["outcome"]) is Outcome.PASS


def test_full_reset_is_now_rejected_which_is_the_direction_nothing_checked(
    reports: dict[str, dict[str, Any]],
) -> None:
    """Corollary 2.1 and Corollary 4.1 both call full reset non-minimal.

    Before the repair neither check bounded the reopened set from above, so the
    operator the corollaries name as the wrong one passed both.
    """

    reopening = _capacities(reports["check_finite_models.check_reopening"])
    closure = _capacities(reports["check_theory_closure_v2_1.check_root_inclusive_safety"])
    assert "retain_nothing" in reopening["reopening.minimality"]["refuted"]
    assert "full_reset" in closure["root_inclusive_safety.minimality"]["refuted"]


def test_no_declared_false_operator_walks_through_either_panel(
    reports: dict[str, dict[str, Any]],
) -> None:
    for report in reports.values():
        coverage = report["coverage"]
        assert coverage["unrefuted"] == []
        assert Outcome(coverage["outcome"]) is Outcome.PASS
    assert len(reports) == 2


def test_the_audit_exits_zero(audit: Any) -> None:
    assert audit.main([]) == 0


# ---------------------------------------------------------------------------
# What the repair did not buy
# ---------------------------------------------------------------------------


def test_check_reopening_still_implements_the_non_root_inclusive_operator(
    audit: Any,
) -> None:
    """V2.1's `Aff_D(E,X)` is a different operator, and only one assertion sees it.

    `descendants` subtracts the changed set, so a certified claim that both
    changed and sits downstream of another changed claim keeps its
    certification. That is the gap FORMAL_CORE_V2.1's root-inclusive correction
    closes, and it is not what this V1 check is about -- so V2.1's operator is
    deliberately absent from the false-theory register. What the repair bought is
    only that the check can now tell the two apart at all: sufficiency and
    minimality still accept both.
    """

    divergence = divergence_of(
        audit.root_inclusive_reopening,
        theory_id="root_inclusive_reopening",
        reference=audit.reference_retained,
        space=audit.REOPENING_SPACE,
    )
    assert divergence.points_changed == 49504
    assert divergence.points == 130320

    accepted = {
        check.check_id: check.accepts(audit.root_inclusive_reopening)
        for check in audit.REOPENING_CHECKS
    }
    assert accepted == {
        "reopening.sufficiency": True,
        "reopening.minimality": True,
        "reopening.exactness": False,
    }


def test_the_root_inclusive_gap_is_reachable_in_most_enumerated_cases(audit: Any) -> None:
    """The gap is not a corner: 5,138 of 8,145 changed sets contain a descendant."""

    pairs = overlapping = 0
    for edges in audit._dags(audit.NODE_COUNT):
        for changed_raw in audit.finite_models.powerset(range(audit.NODE_COUNT)):
            if not changed_raw:
                continue
            changed = frozenset(int(value) for value in changed_raw)
            pairs += 1
            specified, _ = audit._specified(audit.NODE_COUNT, edges, changed)
            if specified & changed:
                overlapping += 1
    assert (pairs, overlapping) == (8145, 5138)


def test_nothing_the_v2_1_check_says_about_node_a_is_falsifiable(
    audit: Any, reports: dict[str, dict[str, Any]]
) -> None:
    """`all_forward_dags` only emits earlier-to-later edges, so "a" is a universal source.

    An operator that hides "a" from `descendants` is the shipped operator under
    another name over this space. The probe reports it as inert rather than
    scoring its acceptance as a miss, and this pins that the space -- not the
    assertion -- is what makes it unfalsifiable.
    """

    entry = reports["check_theory_closure_v2_1.check_root_inclusive_safety"][
        "operator_substitution"
    ]
    assert entry["inert"] == ["claim_a_never_downstream"]
    assert "claim_d_never_downstream" in entry["live"]

    ever_downstream = {node: 0 for node in audit.NODES}
    for edges in audit.theory_closure.all_forward_dags():
        for size in range(1, len(audit.NODES) + 1):
            for combo in combinations(audit.NODES, size):
                for node in audit.theory_closure.descendants(edges, frozenset(combo)):
                    ever_downstream[node] += 1
    assert ever_downstream["a"] == 0
    assert ever_downstream["d"] > 0


def test_the_v2_1_check_never_varies_which_claims_are_certified(
    reports: dict[str, dict[str, Any]],
) -> None:
    """`certified` is hard-coded to every node, so a partial certification is untested."""

    axes = {
        str(item["axis"]): item
        for item in reports["check_theory_closure_v2_1.check_root_inclusive_safety"]["axes"]
    }
    assert axes["certified"]["values"] == 1
    assert axes["certified"]["varied"] is False
    assert axes["edges"]["verdict_changing_pairs"] > 0
    assert axes["changed"]["verdict_changing_pairs"] > 0


def test_no_reopening_check_adds_register_coverage_over_the_others(
    reports: dict[str, dict[str, Any]],
) -> None:
    """Honest marginal capacity: one check alone would cover the whole register.

    `reopening.exactness` rejects all eight on its own, and sufficiency and
    minimality between them reject all eight too. The three earn their place by
    naming three separate theorems and by separating wrong operators from each
    other, not by adding coverage -- and saying so is the point of measuring.
    """

    capacities = _capacities(reports["check_finite_models.check_reopening"])
    exactness = set(capacities["reopening.exactness"]["refuted"])
    others = set(capacities["reopening.sufficiency"]["refuted"]) | set(
        capacities["reopening.minimality"]["refuted"]
    )
    assert exactness == others
    assert len(exactness) == len(audit_register_size(reports))


def audit_register_size(reports: dict[str, dict[str, Any]]) -> list[str]:
    capacities = _capacities(reports["check_finite_models.check_reopening"])
    return [item["theory_id"] for item in capacities["reopening.exactness"]["divergences"]]


# ---------------------------------------------------------------------------
# The instrument itself
# ---------------------------------------------------------------------------


def test_a_reinstated_tautology_is_reported_as_such(audit: Any) -> None:
    """The pre-repair assertion, measured over the same register, comes out FAIL.

    `not retained.intersection(downstream)` with `retained` defined from
    `downstream` does not read the operator at all, so the transcription ignores
    its argument -- which is the whole finding.
    """

    def accepts_pre_repair(rule: Any) -> bool:
        # `rule` is deliberately unused. Both sides of the assertion came from
        # `descendants`, so the operator under test never entered it, and a
        # faithful transcription cannot use its argument.
        for point in audit.REOPENING_SPACE:
            node_count, edges, changed, certified = audit._point(point)
            downstream = audit.finite_models.descendants(node_count, edges, changed)
            retained = certified - downstream
            if retained & downstream:
                return False
        return True

    capacity = measure_refutation_capacity(
        MechanizedCheck(
            check_id="reopening.pre_repair_sufficiency",
            asserts="the assertion as it stood: a set difference does not meet what it removed",
            accepts=accepts_pre_repair,
        ),
        reference=audit.reference_retained,
        reference_id=audit.REOPENING_REFERENCE_ID,
        theories=audit.FALSE_REOPENING_THEORIES,
        space=audit.REOPENING_SPACE,
    )
    assert capacity.refuted == ()
    assert capacity.outcome is Outcome.FAIL
    with pytest.raises(UnrefutableCheck, match="reject no declared false"):
        require_refutable([capacity], label="check_finite_models.check_reopening")
