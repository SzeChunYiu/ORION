"""A class recorded once is not a class swept, and the record has to say which.

The P6/P7/P8 guard is the fixture throughout, because it is the case that proves
the gap: recorded against P6, present unfound in two other papers for as long as
nobody pointed anything at them.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from orion.programme.failure_class_coverage import (
    PAPER_IDS,
    CoverageReport,
    FailureClass,
    PairState,
    SweepEvidence,
    coverage_matrix,
    load_failure_classes,
    pair_state,
)
from orion.programme.records import Outcome
from orion.programme.self_comparison_scan import Context, scan_source

FAILURES = Path(__file__).resolve().parents[3] / "research" / "failures"

#: The guard as it stood in check_p7_x2_closure_carrying.py before 2026-08-22.
HISTORICAL_GUARD = '''
def main():
    donor_conservativity_violations = 0
    for native_valid in (False, True):
        for carries in (False, True):
            projected_native = native_valid
            if projected_native != native_valid:
                donor_conservativity_violations += 1
    return donor_conservativity_violations
'''


# ---------------------------------------------------------------------------
# The detector
# ---------------------------------------------------------------------------


def test_the_detector_fires_on_the_guard_that_named_the_class():
    findings = scan_source(HISTORICAL_GUARD, path="historical.py")
    assert len(findings) == 1
    f = findings[0]
    assert f.root == "native_valid"
    assert f.constant_value is False
    assert f.function == "main"
    assert "always False" in f.summary


def test_the_detector_does_not_fire_on_a_real_comparison():
    """Without this the sweep's 15 clean verdicts would be worthless."""

    src = '''
def check(a, b):
    projected = a
    if projected != b:
        return 1
    return 0
'''
    assert scan_source(src, path="real.py") == []


def test_a_rebound_operand_is_not_a_self_comparison():
    """`x != x` across a rebinding compares two different values."""

    src = '''
def check(rows):
    seen = 0
    previous = rows[0]
    for row in rows:
        current = row
        if current != previous:
            seen += 1
        previous = row
    return seen
'''
    assert scan_source(src, path="rebound.py") == []


def test_an_alias_captured_before_its_root_is_rebound_is_not_a_self_comparison():
    """`a = b` then `b = something_else`: the two names now hold different values.

    This case is the whole reason the scan checks that the shared root is bound
    only once. The first version of these tests did not cover it, and mutating
    that check away broke nothing -- an unexercised guard inside the module whose
    subject is unexercised guards.
    """

    src = '''
def f(rows):
    b = rows[0]
    a = b
    b = rows[1]
    if a != b:
        return 1
    return 0
'''
    assert scan_source(src, path="rebound_root.py") == []

    # Same shape without the rebinding: now the two names cannot differ.
    stable = '''
def g(rows):
    b = rows[0]
    a = b
    if a != b:
        return 1
    return 0
'''
    findings = scan_source(stable, path="stable_root.py")
    assert len(findings) == 1
    assert findings[0].root == "b"


def test_alias_chains_resolve_to_one_root():
    src = '''
def check(flag):
    a = flag
    b = a
    if a != b:
        return 1
    return 0
'''
    findings = scan_source(src, path="chain.py")
    assert len(findings) == 1
    assert findings[0].root == "flag"


@pytest.mark.parametrize(
    "operator,constant",
    [("!=", False), ("==", True), ("<", False), (">=", True), ("is", True), ("is not", False)],
)
def test_every_reported_operator_is_constant_on_one_binding(operator, constant):
    src = f'''
def check(value):
    alias = value
    if alias {operator} value:
        return 1
    return 0
'''
    findings = scan_source(src, path="ops.py")
    assert len(findings) == 1
    assert findings[0].constant_value is constant


# ---------------------------------------------------------------------------
# The two shapes the first version of the scan walked past
# ---------------------------------------------------------------------------

#: P8 published `ideal_product_mismatches: 0` from this. The operands are not
#: aliases of a name, so an alias-only scan reports the file clean.
IDENTICAL_CALLS = '''
def scientific_terminal(a, b): return a and b
def main():
    mismatches = 0
    for a in (False, True):
        for b in (False, True):
            terminal = scientific_terminal(a, b)
            ideal = scientific_terminal(a, b)
            if terminal != ideal:
                mismatches += 1
    return mismatches
'''

#: The shape that named the class: one rule written twice under two names.
TWIN_BODIES = '''
def donor_valid(state, embedding): return True
def scientific_admissible(state, embedding): return donor_valid(state, embedding)
def ideal_product(state, embedding): return donor_valid(state, embedding)
def main():
    violations = 0
    for s in ():
        if scientific_admissible(s, 1) != ideal_product(s, 1):
            violations += 1
    return violations
'''


def test_two_identical_calls_compared_are_a_defect():
    findings = [f for f in scan_source(IDENTICAL_CALLS, path="p8.py") if f.is_defect]
    assert len(findings) == 1
    assert findings[0].context is Context.COUNTS
    assert "called twice" in findings[0].root


def test_one_rule_written_twice_under_two_names_is_a_defect():
    findings = [f for f in scan_source(TWIN_BODIES, path="p6.py") if f.is_defect]
    assert len(findings) == 1
    assert "identical bodies" in findings[0].root


def test_two_genuinely_different_rules_are_not_flagged():
    src = '''
def a(x): return x + 1
def b(x): return x * 2
def main():
    n = 0
    if a(3) != b(3):
        n += 1
    return n
'''
    assert scan_source(src, path="different.py") == []


def test_calls_on_different_receivers_are_not_a_self_comparison():
    """`left.f(m) != right.f(m)` shares a method name and an argument list.

    A version of this scan that compared only the attribute name reported seven
    such lines in P9 as constant, and every one is a real test.
    """

    src = '''
def verify(left, right, mode):
    if left.fingerprint(mode) != right.fingerprint(mode):
        raise ValueError("must collide")
'''
    assert scan_source(src, path="receivers.py") == []


def test_an_intervening_call_can_change_the_second_result():
    """P6's hidden-read counterexample writes between two identical reads."""

    src = '''
def check_hidden_read_counterexample():
    before_n = hidden_read_m(1)
    hidden_write_n()
    after_n = hidden_read_m(1)
    assert before_n != after_n
    return 1
'''
    assert scan_source(src, path="hidden_read.py") == []


def test_a_determinism_test_is_not_a_defect():
    """`f(x) == f(x)` is trivially true only if f is pure -- which is the claim.

    Five of these are live in the repo. Reporting them as defects would make the
    sweep's clean verdicts worthless in the other direction.
    """

    src = '''
def test_every_system_is_deterministic_given_a_seed():
    first = run(seed=1)
    second = run(seed=1)
    assert first == second
'''
    findings = scan_source(src, path="determinism.py")
    assert len(findings) == 1
    assert findings[0].context is Context.ASSERTS
    assert findings[0].is_defect is False


def test_a_deliberate_tautology_fixture_is_not_a_defect():
    """P6 builds one on purpose, to prove its instrument can still emit FAIL."""

    src = '''
def test_the_instrument_still_fails_a_check_that_accepts_everything():
    tautology = MechanizedCheck(
        accepts=lambda rule: not any(rule(p) != rule(p) for p in space()),
    )
    assert capacity(tautology).outcome is CANNOT_CHECK
'''
    findings = scan_source(src, path="fixture.py")
    assert [f for f in findings if f.is_defect] == []
    # Labelled ASSERTS rather than merely UNCLASSIFIED: the comparison sits inside
    # a comprehension in a lambda, so no enclosing Assert or If reaches it, and
    # only the enclosing test function's name says what it is.
    assert [f.context for f in findings] == [Context.ASSERTS]


def test_adjacent_calls_with_different_arguments_are_not_a_self_comparison():
    """Adjacency alone is not enough -- the two calls must be written identically."""

    src = '''
def main():
    n = 0
    left = fingerprint(a)
    right = fingerprint(b)
    if left != right:
        n += 1
    return n
'''
    assert scan_source(src, path="different_args.py") == []


# ---------------------------------------------------------------------------
# The coverage record
# ---------------------------------------------------------------------------


def _cls(**kw) -> FailureClass:
    base = dict(class_id="c", detector="orion.programme.self_comparison_scan", found_in=frozenset())
    base.update(kw)
    return FailureClass(**base)


def test_a_paper_nobody_looked_at_is_cannot_check_not_clean():
    cls = _cls(found_in=frozenset({6}))
    assert pair_state(cls, 6) is PairState.FOUND
    assert pair_state(cls, 7) is PairState.NOT_SWEPT
    assert PairState.NOT_SWEPT.outcome is Outcome.CANNOT_CHECK
    assert PairState.NOT_SWEPT.blocks
    assert cls.outcome is Outcome.CANNOT_CHECK
    # This is exactly the state the record was in while P7 and P8 carried the guard.
    assert 7 in cls.not_swept and 8 in cls.not_swept


def test_a_sweep_that_ran_and_found_nothing_is_clean():
    cls = _cls(
        found_in=frozenset({6}),
        sweeps=(
            SweepEvidence(
                paper_id=7, detector="orion.programme.self_comparison_scan", run="sweep --json", found=False
            ),
        ),
    )
    assert pair_state(cls, 7) is PairState.SWEPT_CLEAN
    assert PairState.SWEPT_CLEAN.outcome is Outcome.PASS
    assert not PairState.SWEPT_CLEAN.blocks


def test_an_unmechanised_class_cannot_clear_anybody():
    """Sweeping by hand and writing 'checked' is the practice this replaces."""

    cls = _cls(
        detector=None,
        sweeps=(SweepEvidence(paper_id=7, detector="by hand", run="a README", found=False),),
    )
    assert cls.mechanised is False
    assert cls.swept_clean == frozenset()
    assert len(cls.not_swept) == len(PAPER_IDS)


def test_a_sweep_by_a_different_detector_is_refused():
    with pytest.raises(ValueError, match="two different questions"):
        _cls(sweeps=(SweepEvidence(paper_id=7, detector="something.else", run="run", found=False),))


def test_a_repaired_paper_does_not_stop_having_had_the_defect():
    """P6/P7/P8 are FOUND on history, even though the sweep now finds nothing."""

    cls = _cls(
        found_in=frozenset({6, 7, 8}),
        sweeps=tuple(
            SweepEvidence(
                paper_id=p, detector="orion.programme.self_comparison_scan", run="sweep", found=False
            )
            for p in PAPER_IDS
        ),
    )
    for p in (6, 7, 8):
        assert pair_state(cls, p) is PairState.FOUND
    assert cls.swept_clean == frozenset(PAPER_IDS) - {6, 7, 8}
    assert cls.not_swept == frozenset()
    assert cls.outcome is Outcome.PASS


def test_an_undeclared_failure_directory_reads_as_fifteen_open_cells(tmp_path):
    (tmp_path / "2026-08-something").mkdir()
    (tmp_path / "2026-08-something" / "README.md").write_text("prose only")
    classes = load_failure_classes(tmp_path)
    assert len(classes) == 1
    assert classes[0].detector is None
    assert len(classes[0].not_swept) == len(PAPER_IDS)


# ---------------------------------------------------------------------------
# The repository's own record
# ---------------------------------------------------------------------------


def test_the_refutation_capacity_class_is_declared_and_fully_swept():
    declaration = FAILURES / "2026-08-unfalsifiable-check-zero-refutation-capacity" / "CLASS.json"
    raw = json.loads(declaration.read_text())
    assert raw["detector"] == "orion.programme.self_comparison_scan"
    assert sorted(raw["found_in"]) == [6, 7, 8]
    assert {s["paper_id"] for s in raw["sweeps"]} == set(PAPER_IDS)

    cls = next(
        c for c in load_failure_classes(FAILURES) if c.class_id == raw["class_id"]
    )
    assert cls.not_swept == frozenset()
    assert cls.outcome is Outcome.PASS


def test_the_rest_of_the_record_is_honestly_open():
    """The point of the module is that this number is large and visible."""

    report = CoverageReport(coverage_matrix(load_failure_classes(FAILURES)))
    assert report.outcome is Outcome.CANNOT_CHECK
    assert report.not_swept_pairs > 0
    # Every class but the one declared above is still unmechanised.
    assert len(report.matrix.unmechanised) == len(report.matrix.classes) - 1
