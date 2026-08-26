"""P14A's published negative, measured against the worlds its own protocol admits.

Every number pinned here was read off the shipped artifacts
``papers/paper-14-orion-rse/P14A_CONTROLLED_GOVERNANCE_RESULT_RECEIPT_V1.json``
and ``run_p14a_controlled_governance_v1.py``, or produced by driving that
generator's own ``gold``, ``policy`` and ``make_case``.
"""

from __future__ import annotations

import contextlib
import io
import json

import pytest

from orion.programme.gate_attainability import (
    AdmissibleWorld,
    GateReachReason,
    GateRole,
    UnattainableGate,
    measure_gate_attainability,
    require_reachable,
    require_supported_thresholds,
)
from orion.programme.records import Outcome
from orion.study.p14 import governance_gates as p14
from orion.study.p14.gate_audit import audit_p14a_governance_terminal, main, report_as_json


P14A_SUCCESSOR_CLOSURE = (
    p14.REPO_ROOT
    / "papers"
    / "paper-14-orion-rse"
    / "top_tier"
    / "P14A_CLOSURE_BY_SUCCESSOR_VERIFICATION_V1.json"
)


def p14a_successor_closure() -> dict:
    return json.loads(P14A_SUCCESSOR_CLOSURE.read_text(encoding="utf-8"))


def literal_gates(summary: dict) -> dict[str, bool]:
    """``main()``'s seven gate expressions, transcribed character for character.

    The registration in :data:`p14.GATES` reads counts and rates where the
    generator writes booleans; this is the check that the two agree, so an
    attainability verdict below is about P14A's thresholds and not about a
    paraphrase of them.
    """

    strongest = max(p14.BASELINE_ARMS, key=lambda a: summary[a]["disposition_accuracy"])
    full = summary["ORION_RSE_FULL"]
    budgets = {summary[a]["decision_budget_checks"] for a in p14.ARMS}
    return {
        "full_zero_false_promotion": full["false_promotion_rate"] == 0.0,
        "full_useful_discovery_recall_one": full["useful_discovery_recall"] == 1.0,
        "strongest_baseline_false_promotion_ge_0_05": summary[strongest]["false_promotion_rate"]
        >= 0.05,
        "accuracy_gain_ge_0_08": full["disposition_accuracy"]
        - summary[strongest]["disposition_accuracy"]
        >= 0.08,
        "each_ablation_worse": all(
            summary[a]["false_promotion_rate"] > 0.0
            or summary[a]["disposition_accuracy"] < full["disposition_accuracy"]
            for a in p14.ABLATION_ARMS
        ),
        "history_reopen_exact": full["history_reopen_accuracy"] == 1.0,
        "matched_decision_budget": len(budgets) == 1,
    }


def test_the_bench_preserves_the_negative_decision_and_uses_successor_replay_provenance():
    """P14A's old digest stays frozen; the current replay is already classified."""

    result = p14.shipped_bench()
    receipt = p14.shipped_receipt()
    closure = p14a_successor_closure()

    assert p14.SHIPPED_RESULT_DIGEST == receipt["full_result_sha256"]
    assert closure["checks"]["p14a_digest_reproduces"] is False
    assert closure["verdicts"]["p14a_full_result_digest_platform_pinned"] is True
    assert closure["verdicts"]["p14a_decision_layer_reproduces_cross_platform"] is True
    assert result["result_sha256"] in {
        closure["p14a_bar_vs_supremum"]["replay"]["sha256"],
        receipt["full_result_sha256"],
    }
    assert result["terminal"] == p14.SHIPPED_TERMINAL == receipt["terminal"]
    assert result["gates"] == receipt["gates"]
    assert result["strongest_non_orion_baseline"] == receipt["strongest_non_orion_baseline"]
    for arm, published in receipt["summary"].items():
        for key, value in published.items():
            assert result["summary"][arm][key] == pytest.approx(value)


def test_the_registered_gates_are_the_generators_own_expressions():
    for world in p14.declared_worlds() + tuple(p14.capability_cases()):
        result = p14.bench(world.payload)
        assert result["gates"] == literal_gates(result["summary"]), world.world_id


def test_the_graded_orion_arm_is_the_gold_that_grades_it():
    """``policy("ORION_RSE_FULL", c)`` is ``return gold(c)``, so its score is an identity."""

    divergence = p14.orion_arm_divergence()

    assert (divergence.points, divergence.points_changed) == (256, 0)
    assert divergence.applied is False
    assert p14.arm_error_states()["ORION_RSE_FULL"] == ()
    assert p14.shipped_bench()["summary"]["ORION_RSE_FULL"]["disposition_accuracy"] == 1.0


def test_the_whole_comparison_is_one_point_of_the_fact_space():
    states = p14.reachable_states()
    errors = p14.arm_error_states()

    assert len(p14.fact_space()) == 256
    assert len(states) == 144
    assert {arm: len(indices) for arm, indices in errors.items()} == {
        "RAW_POSITIVE": 139,
        "REFLECTION_CHECKLIST": 13,
        "DONOR_AWARE_REVIEW": 5,
        "MULTI_REVIEW": 1,
        "ORION_RSE_FULL": 0,
        "ABLATE_DONOR": 8,
        "ABLATE_FREEZE": 18,
        "ABLATE_INTERACTION": 4,
        "ABLATE_NEGATIVE_HISTORY": 1,
    }
    assert dict(states[errors["MULTI_REVIEW"][0]]) == dict(p14.DISCRIMINATING_STATE)


def test_the_strongest_baseline_is_a_nesting_rather_than_a_comparison():
    assert p14.baseline_error_nesting() is True
    assert p14.shipped_bench()["strongest_non_orion_baseline"] == "MULTI_REVIEW"


def test_both_failing_gates_read_the_same_number():
    """The false-promotion rate and the accuracy gap are one statistic under two thresholds."""

    receipt = p14.receipt(p14.shipped_input())

    assert receipt["strongest_baseline_false_promotion"] == 0.018375
    assert receipt["accuracy_gain"] == pytest.approx(0.018375)
    assert receipt["full_false_promotion"] == 0.0


def test_the_discriminator_cannot_get_common_enough_to_clear_either_threshold():
    supremum = p14.discriminator_supremum()

    assert supremum == pytest.approx(0.04232587750858594)
    assert p14.discriminator_infimum() == pytest.approx(0.009085200732011248)
    assert supremum < 0.05
    assert supremum < 0.08


def test_repeated_draws_of_the_frozen_protocol_stay_under_the_supremum():
    sweep = p14.seed_sweep(range(8))

    assert max(sweep) < p14.discriminator_supremum()
    assert max(sweep) < 0.05


def test_two_gates_have_no_admissible_world_that_satisfies_them():
    reaches = {reach.gate.gate_id: reach for reach in p14.gate_reaches()}

    unattainable = reaches["strongest_baseline_false_promotion_ge_0_05"]
    assert unattainable.reason is GateReachReason.THRESHOLD_UNATTAINABLE
    assert unattainable.satisfying == ()
    assert unattainable.best_value == pytest.approx(0.04025)
    assert unattainable.attainment_margin == pytest.approx(-0.00975)

    gap = reaches["accuracy_gain_ge_0_08"]
    assert gap.reason is GateReachReason.THRESHOLD_UNATTAINABLE
    assert gap.best_value == pytest.approx(0.04025)
    assert gap.attainment_margin == pytest.approx(-0.03975)


def test_every_registered_world_stays_inside_the_declared_ranges():
    """The register is the artifact a reviewer audits, so it has to be auditable."""

    for world in p14.declared_worlds():
        for key, (low, high) in world.payload.as_ranges().items():
            declared_low, declared_high = p14.SHIPPED_SUPPORT[key]
            assert declared_low <= low <= high <= declared_high, (world.world_id, key)
        assert world.admits.strip()


def test_one_world_outside_the_declared_ranges_would_make_the_gate_attainable():
    """Why ``admits`` is load-bearing: the verdict is only as honest as the register."""

    gate = next(g for g in p14.GATES if g.gate_id == "accuracy_gain_ge_0_08")
    widened = p14.declared_worlds() + (
        AdmissibleWorld(
            world_id="history-outside-the-declared-range",
            admits="not admissible: history far above the declared 0.08-0.22",
            payload=p14.shipped_input().with_ranges(history=(0.85, 0.95), new_evidence=(0.0, 0.05)),
        ),
    )
    reach = measure_gate_attainability(
        lambda run: p14.READINGS["accuracy_gain_ge_0_08"](p14.bench(run)["summary"]),
        gate=gate,
        worlds=widened,
    )

    assert reach.reason is GateReachReason.BOTH_OUTCOMES_REACHABLE
    assert reach.satisfying == ("history-outside-the-declared-range",)


def test_the_other_five_gates_have_no_admissible_world_that_fails_them():
    reaches = {reach.gate.gate_id: reach for reach in p14.gate_reaches()}

    for gate_id in (
        "full_zero_false_promotion",
        "full_useful_discovery_recall_one",
        "each_ablation_worse",
        "history_reopen_exact",
        "matched_decision_budget",
    ):
        assert reaches[gate_id].reason is GateReachReason.THRESHOLD_UNCONDITIONAL, gate_id
        assert reaches[gate_id].refuting == (), gate_id


def test_the_terminal_had_one_reachable_value_before_the_seed_was_drawn():
    terminal = p14.terminal_reach()

    assert len(terminal.world_ids) == 5
    assert terminal.clearing == ()
    assert terminal.distinct_terminals == 1
    assert terminal.outcome is Outcome.FAIL
    assert terminal.unattainable == (
        "strongest_baseline_false_promotion_ge_0_05",
        "accuracy_gain_ge_0_08",
    )
    with pytest.raises(UnattainableGate, match="no admissible world satisfies"):
        require_reachable(terminal)


def test_the_emitter_itself_is_capable_of_the_positive_terminal():
    """The half that clears the generator: the branch is live, the pass region is not reachable."""

    response = p14.bench_responsiveness()

    assert response.baseline_verdict == p14.SHIPPED_TERMINAL
    assert response.verdicts_observed == (p14.SHIPPED_TERMINAL, p14.POSITIVE_TERMINAL)
    assert response.exercise.opportunities == 3
    assert response.unmoved == ()
    assert response.inert_cases == ()
    assert response.outcome is Outcome.PASS


def test_the_terminal_tracks_the_discriminator_and_crosses_at_the_frozen_threshold():
    curve = p14.capability_curve()
    supported = [row for row in curve if row[3] == p14.POSITIVE_TERMINAL]

    assert [row[0] for row in curve][:2] == ["declared-support", "material-reopening-rare"]
    assert curve == tuple(sorted(curve, key=lambda row: row[1]))
    assert all(row[2] >= 0.08 for row in supported)
    assert all(row[2] < 0.08 for row in curve if row[3] == p14.SHIPPED_TERMINAL)
    assert curve[0][2] == 0.018375


def test_every_axis_moves_the_contrast_on_at_most_one_sibling_pair():
    """The eight facts have to line up exactly, which is what makes the gap a point."""

    axes = p14.contrast_axis_sensitivity()

    assert len(axes) == 8
    assert max(axis.verdict_changing_pairs for axis in axes) == 1
    assert {axis.axis for axis in axes if axis.verdict_changing_pairs == 0} == {"positive"}


def test_the_audit_blocks_and_names_both_findings():
    report = audit_p14a_governance_terminal()
    payload = report_as_json(report)
    closure = p14a_successor_closure()
    result = p14.shipped_bench()
    receipt = p14.shipped_receipt()

    assert report["digest_reproduced"] is (
        result["result_sha256"] == receipt["full_result_sha256"]
    )
    assert result["result_sha256"] in {
        closure["p14a_bar_vs_supremum"]["replay"]["sha256"],
        receipt["full_result_sha256"],
    }
    assert closure["checks"]["p14a_receipt_numbers_reproduce"] is True
    assert report["outcome"] is Outcome.FAIL
    assert report["grading_outcome"] is Outcome.FAIL
    assert report["responsiveness"].outcome is Outcome.PASS
    assert payload["terminal_reach"]["distinct_terminals"] == 1
    assert payload["discriminator_supremum"] == pytest.approx(0.04232587750858594)


def test_the_audit_exits_three_and_prints_the_margins():
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        code = main([])

    assert code == 3
    assert "reachable terminals: 1" in stream.getvalue()
    assert "-0.039750" in stream.getvalue()

    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        assert main(["--json"]) == 3
    assert '"outcome": "FAIL"' in stream.getvalue()


def test_the_two_failing_thresholds_were_outside_reach_before_the_seed_was_drawn() -> None:
    """The pre-run half: no run, no register of worlds, only the freeze's own bound."""

    support = p14.declared_statistic_support()

    assert support.infimum == pytest.approx(0.009085200732011248)
    assert support.supremum == pytest.approx(0.04232587750858594)
    assert support.derivation.strip()

    reaches = {reach.gate.gate_id: reach for reach in p14.threshold_reaches()}
    assert set(reaches) == set(p14.SUPPORT_BOUNDED_GATES)

    difficulty = reaches["strongest_baseline_false_promotion_ge_0_05"]
    assert difficulty.gate.role is GateRole.PRECONDITION
    assert difficulty.reason is GateReachReason.THRESHOLD_UNATTAINABLE
    assert difficulty.attainment_margin == pytest.approx(-0.007674122491414061)

    gain = reaches["accuracy_gain_ge_0_08"]
    assert gain.gate.role is GateRole.HYPOTHESIS
    assert gain.reason is GateReachReason.THRESHOLD_UNATTAINABLE
    assert gain.attainment_margin == pytest.approx(-0.03767412249141406)


def test_the_preregistration_check_blocks_and_names_both_bars() -> None:
    panel = p14.threshold_panel()

    assert panel.outcome is Outcome.FAIL
    assert panel.unattainable == (
        "strongest_baseline_false_promotion_ge_0_05",
        "accuracy_gain_ge_0_08",
    )
    assert panel.discriminating == ()
    with pytest.raises(UnattainableGate, match="no admissible value satisfies"):
        require_supported_thresholds(panel)


def test_the_declared_bound_and_the_measured_register_reach_the_same_verdict() -> None:
    """Two instruments, one answer: the bound is not a softer paraphrase of the register."""

    declared = {reach.gate.gate_id: reach.reason for reach in p14.threshold_reaches()}
    measured = {
        reach.gate.gate_id: reach.reason
        for reach in p14.gate_reaches()
        if reach.gate.gate_id in set(p14.SUPPORT_BOUNDED_GATES)
    }

    assert declared == measured
    assert set(declared.values()) == {GateReachReason.THRESHOLD_UNATTAINABLE}
