"""P8's shipped authority receipts, measured against inputs they should have refused.

The bench's terminal was a string literal beside its four rates until 2026-08-21;
the tests that pinned that state carry their before-values in their docstrings.
It is now derived, and the three inputs registered as having to withhold it do.
The ceiling, the transcribed gold and the inert X4 donor axis are unrepaired, and
the audit still blocks on them.

Every number pinned here was read off the shipped artifacts
``research/extensions/p8-method-authority/P9_P10_ANTI_LAUNDERING_SUMMARY_V1.json``
and ``research/claim_expansion/p8/P8_X4_AUTHORITY_LIFTING_RESULT_V1.json``, or off
the scripts that produced them.
"""

from __future__ import annotations

import contextlib
import io
import json

import pytest

from orion.programme.records import Outcome
from orion.programme.terminal_responsiveness import (
    SelfIssuedAuthority,
    require_earned,
    require_responsive,
)
from orion.study.p8 import authority_terminals as p8
from orion.study.p8.terminal_audit import audit_p8_authority_receipts, main, report_as_json
from orion.transfer.v2 import p8_method_authority as authority

X4_RESULT = p8.REPO_ROOT / "research/claim_expansion/p8/P8_X4_AUTHORITY_LIFTING_RESULT_V1.json"


def test_emitter_reproduces_the_committed_summary_exactly():
    """The fidelity anchor: a failure below is about P8, not about a local fixture."""

    emitted = p8.bench_emitter(p8.BenchInput(panel=p8.shipped_panel()))

    assert emitted == p8.shipped_summary()
    assert emitted["terminal"] == p8.SHIPPED_TERMINAL
    assert emitted["result_digest"] == p8.SHIPPED_RESULT_DIGEST
    assert emitted["contract_accuracy"] == 1.0
    assert emitted["illicit_coercion_block_rate"] == 1.0


def test_the_terminal_is_no_longer_a_literal_in_the_emitting_source():
    """Before 2026-08-21 this asserted the two literals, which is what it found.

    ``'terminal':'P8_P9_P10_ANTI_LAUNDERING_CLEAR'`` and
    ``'claim_ceiling':panel['claim_ceiling']`` were both in the emitted dict
    display. The source check is kept because it is cheap and reads the shipped
    file; what it pins is the repair, and the measurement that the terminal now
    *moves* is two tests below.
    """

    source = p8.BENCH_SCRIPT.read_text()

    assert f"'terminal':'{p8.SHIPPED_TERMINAL}'" not in source
    assert "'claim_ceiling':panel['claim_ceiling']" not in source
    assert "'terminal':terminal" in source
    assert "assess_guard" in source and "worst_outcome" in source
    assert f"'{p8.DECLARED_CEILING_FIELD}':panel['claim_ceiling']" in source


def test_the_terminal_moves_on_every_registered_withholding_case():
    """Before 2026-08-21: ``violations == 3``, all three ``contradicted``, ``FAIL``.

    The register is unchanged and so are the rates it drives to zero; what
    changed is that the terminal is derived from them, so each case now reaches
    a different word instead of leaving ``CLEAR`` standing.
    """

    response = p8.bench_responsiveness()

    assert response.baseline_verdict == p8.SHIPPED_TERMINAL
    assert response.verdicts_observed == (
        p8.SHIPPED_TERMINAL,
        "P8_P9_P10_ANTI_LAUNDERING_VIOLATED",
    )
    assert response.exercise.opportunities == 3
    assert response.exercise.violations == 0
    assert response.inert_cases == ()
    assert response.unmoved == ()
    assert response.contradicted == ()
    assert response.outcome is Outcome.PASS

    require_responsive(response)


def test_laundering_every_capability_zeroes_the_block_rate_and_the_terminal_with_it():
    """The measurement that named the failure: the mechanism is wrong, the panel is not.

    Before 2026-08-21 the last assertion here was
    ``receipt["terminal"] == p8.SHIPPED_TERMINAL`` --- a block rate of 0.0 with
    all seven named attacks succeeding, published as ``CLEAR``.
    """

    launder = {
        kind: frozenset(authority.AuthorityCoordinate) for kind in authority.CapabilityKind
    }
    receipt = p8.bench_emitter(p8.BenchInput(panel=p8.shipped_panel(), legal=launder))

    assert receipt["illicit_coercion_block_rate"] == 0.0
    assert receipt["contract_accuracy"] == pytest.approx(8 / 15)
    assert receipt["terminal"] == "P8_P9_P10_ANTI_LAUNDERING_VIOLATED"
    assert [row["id"] for row in receipt["rows"] if not row["pass"]] == [
        "p9_confidence_to_validity",
        "p9_applicability_to_adoption",
        "p10_generation_to_novelty",
        "p7_library_stop_to_global_stop",
        "p6_fibre_to_applicability",
        "p4_validity_to_novelty",
        "novelty_to_correctness",
    ]


def test_removing_revocation_zeroes_its_accuracy_and_the_terminal_with_it():
    """Before 2026-08-21 the terminal was ``CLEAR`` here too, at revocation accuracy 0.0."""

    inert = {defeater: () for defeater in authority.DefeaterKind}
    receipt = p8.bench_emitter(p8.BenchInput(panel=p8.shipped_panel(), defeater_coords=inert))

    assert receipt["revocation_accuracy"] == 0.0
    assert receipt["terminal"] == "P8_P9_P10_ANTI_LAUNDERING_VIOLATED"


def test_overrides_do_not_leak_out_of_the_emitter():
    before_legal, before_defeaters = authority.LEGAL, authority.DEFEATER_COORDS

    p8.bench_responsiveness()

    assert authority.LEGAL is before_legal
    assert authority.DEFEATER_COORDS is before_defeaters
    assert p8.bench_emitter(p8.BenchInput(panel=p8.shipped_panel())) == p8.shipped_summary()


def test_the_declared_ceiling_is_still_whatever_the_panel_says_it_is():
    """Unrepaired on purpose, and now emitted under a field name that admits it.

    The value is still ``panel['claim_ceiling']``, so an injected ceiling the
    suite has no right to still comes back verbatim and the bound still fails.
    What the rename subtracts is the reader's inference that the run set it.
    """

    bound = p8.bench_declared_ceiling()
    receipt = p8.bench_emitter(p8.BenchInput(panel=p8.shipped_panel()))

    assert bound.field == p8.DECLARED_CEILING_FIELD == "declared_claim_ceiling_from_input"
    assert bound.emitted == p8.OVERREACHING_CEILING
    assert bound.subject_controlled
    assert bound.outcome is Outcome.FAIL
    with pytest.raises(SelfIssuedAuthority, match="chose its own ceiling"):
        require_earned(bound)

    assert "claim_ceiling" not in receipt
    assert receipt[p8.DECLARED_CEILING_FIELD] == p8.shipped_panel()["claim_ceiling"]
    assert "not one it earned" in receipt["declared_claim_ceiling_note"]


def test_the_frozen_gold_is_the_graded_tables_transcribed():
    divergence = p8.panel_gold_divergence()

    assert divergence.points == 15
    assert divergence.points_changed == 0
    assert not divergence.applied


def test_every_panel_case_reads_one_table_lookup():
    """Named separately from the divergence: this is what the 1.0 rates measure."""

    space = p8.panel_space()
    coercion = [point for point in space if point["kind"] == "coercion"]
    revocation = [point for point in space if point["kind"] == "revocation"]

    assert (len(coercion), len(revocation)) == (11, 4)
    assert all(p8.mechanism_verdict(point) == point["expected"] for point in space)


def test_the_x4_donor_axis_multiplies_every_count_by_thirteen():
    axis = p8.x4_donor_axis()

    assert len(p8.x4_space()) == 39936
    assert axis.values == 13
    assert axis.comparable_pairs == 239616
    assert axis.verdict_changing_pairs == 0
    assert axis.inert
    assert axis.multiplier == 13


def test_the_shipped_x4_checker_still_reproduces_its_published_digest():
    """Run the published script itself, so the donor result is about the artifact."""

    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        p8.x4_module().main()
    emitted = json.loads(buffer.getvalue())
    published = json.loads(X4_RESULT.read_text())

    assert emitted["canonical_rows_sha256"] == published["canonical_rows_sha256"]
    assert emitted["state_evaluations"] == published["state_evaluations"] == 39936
    # The headline #656 quotes, and the count of distinct facts behind it.
    assert emitted["heterogeneous_chain_successes"] == 169
    assert emitted["heterogeneous_chain_widening_countermodels"] == 169
    assert p8.x4_module().scientific_terminal.__code__.co_argcount == 7


def test_the_two_x4_violation_counters_are_zero_for_any_rule():
    """``ideal`` is the same call as ``terminal``; ``projected_native`` is an alias."""

    published = json.loads(X4_RESULT.read_text())
    assert published["donor_conservativity_violations"] == 0
    assert published["ideal_product_mismatches"] == 0

    source = p8.X4_CHECKER.read_text()
    assert "ideal = scientific_terminal(native, flags, narrowing, blocker" in source
    assert "projected_native = native" in source
    assert "if projected_native != native:" in source


def test_the_audit_still_blocks_and_reports_every_registered_receipt():
    """Before 2026-08-21 the responsiveness leg reported one distinct verdict and blocked.

    It now passes. The audit still blocks --- on the input-supplied ceiling, on a
    declared gold that is the graded tables transcribed, and on the inert donor
    axis --- so the repair moved one leg and added nothing.
    """

    report = audit_p8_authority_receipts()
    payload = report_as_json(report)

    assert payload["outcome"] == "FAIL"
    assert payload["responsiveness"]["verdicts_observed"] == [
        p8.SHIPPED_TERMINAL,
        "P8_P9_P10_ANTI_LAUNDERING_VIOLATED",
    ]
    assert payload["responsiveness"]["assessment"]["outcome"] == "PASS"
    assert payload["ceiling"]["subject_controlled"] is True
    assert payload["gold_outcome"] == "FAIL"
    assert payload["donor_axis"]["inert"] is True
    assert main(["--json"]) == 3
