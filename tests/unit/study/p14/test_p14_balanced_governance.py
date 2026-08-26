"""P14B's published positive, asked how many of its eight gates could have said no.

Every number pinned here was read off the shipped artifacts
``papers/orion-24-orion-rse/run_p14b_balanced_governance_v1.py`` and
``P14B_BALANCED_GOVERNANCE_RESULT_RECEIPT_V1.json``, or produced by driving that
generator's own ``gold``, ``policy`` and ``case_for``.

Each attainability verdict is paired with a mutation that should break it. A
verdict nobody tried to falsify is the failure this whole module family exists to
name, so the register, the thresholds and the arms' rates are each perturbed in
turn and the assertion is required to fail.
"""

from __future__ import annotations

import contextlib
import io
import json
from dataclasses import replace

import pytest

from orion.programme.gate_attainability import (
    AdmissibleWorld,
    GateReachReason,
    GateRole,
    UnattainableGate,
    assess_threshold_panel,
    assess_threshold_support,
    measure_gate_attainability,
    measure_terminal_reach,
    require_reachable,
    require_supported_thresholds,
)
from orion.programme.records import Outcome
from orion.study.p14 import balanced_governance as p14b
from orion.study.p14 import governance_gates as p14a
from orion.study.p14 import specification_conformance as p14c

SHARE = 1 / 7


def literal_gates(summary: dict) -> dict[str, bool]:
    """``main()``'s seven gate expressions, transcribed character for character.

    :data:`p14b.GATES` reads counts and rates where the generator writes
    booleans; this is the check that the two agree, so an attainability verdict
    below is about P14B's thresholds and not about a paraphrase of them.
    """

    strongest = max(
        p14b.BASELINE_ARMS, key=lambda a: summary[a]["disposition_accuracy"]
    )
    full = summary["ORION_RSE_FULL"]
    return {
        "full_zero_false_promotion": full["false_promotion_rate"] == 0.0,
        "full_discovery_recall_one": full["useful_discovery_recall"] == 1.0,
        "strongest_baseline_false_promotion_ge_0_05": summary[strongest][
            "false_promotion_rate"
        ]
        >= 0.05,
        "accuracy_advantage_ge_0_08": full["disposition_accuracy"]
        - summary[strongest]["disposition_accuracy"]
        >= 0.08,
        "retain_and_reopen_exact": full["retain_negative_accuracy"] == 1.0
        and full["supported_reopen_accuracy"] == 1.0,
        "each_ablation_worse": all(
            summary[a]["disposition_accuracy"] < full["disposition_accuracy"]
            for a in p14b.ABLATION_ARMS
        ),
        "matched_budget": len(
            {summary[a]["decision_budget_checks"] for a in p14b.ARMS}
        )
        == 1,
    }


# ---------------------------------------------------------------------------
# Fidelity: every verdict below is about the shipped artifact
# ---------------------------------------------------------------------------


def test_the_bench_reproduces_the_committed_replay_digest() -> None:
    result = p14b.shipped_bench()
    receipt = p14b.shipped_receipt()

    assert result["result_sha256"] == p14b.SHIPPED_RESULT_DIGEST
    assert receipt["replay_sha256"] == p14b.SHIPPED_RESULT_DIGEST
    assert receipt["byte_identical_two_run_replay"] is True
    assert result["terminal"] == p14b.SHIPPED_TERMINAL == receipt["terminal"]
    assert receipt["seed"] == p14b.shipped_input().seed == 2026082115
    assert receipt["total_cases"] == 6720

    for block in ("summary", "ablations"):
        for arm, published in receipt[block].items():
            for key, value in published.items():
                assert result["summary"][arm][key] == pytest.approx(value), (arm, key)


def test_the_registered_gates_are_the_generators_own_expressions() -> None:
    for world in p14b.declared_worlds():
        result = p14b.bench(world.payload)
        assert result["gates"] == literal_gates(result["summary"]), world.world_id


def test_the_receipt_asserts_one_gate_the_generators_terminal_never_conjoins() -> None:
    """Eight gates published; ``all(gates.values())`` ranges over seven of them."""

    fidelity = p14b.receipt_matches_replay()

    assert fidelity["digest_reproduced"] is True
    assert fidelity["terminal_matches"] is True
    assert fidelity["summary_fields_mismatched"] == []
    assert fidelity["runner_gates_match_receipt"] is True
    assert fidelity["gates_only_the_receipt_asserts"] == ["byte_identical_replay"]
    assert len(fidelity["gates_the_runner_computes"]) == 7
    assert len(p14b.GATES) == 8
    assert len(p14b.shipped_receipt()["gates"]) == 8


# ---------------------------------------------------------------------------
# The terminal: it could have gone either way
# ---------------------------------------------------------------------------


def test_the_terminal_could_have_been_the_other_word() -> None:
    terminal = p14b.terminal_reach()

    assert len(terminal.world_ids) == 7
    assert terminal.distinct_terminals == 2
    assert terminal.outcome is Outcome.PASS
    assert terminal.unattainable == ()
    assert set(terminal.clearing) == {
        "shipped-run",
        "alternate-seed-20260821",
        "alternate-seed-2026082116",
    }
    require_reachable(terminal)


def test_breaking_the_register_breaks_the_terminals_verdict() -> None:
    """MUTATION: drop the four ablations, leaving only worlds that clear every gate.

    The guard this exercises is ``TerminalReach.distinct_terminals``. If the
    register that supplies the negative side is removed the terminal must stop
    reporting two words, or the PASS above was a property of the assertion rather
    than of the benchmark.
    """

    seeds = p14b.seed_only_terminal_reach()

    assert seeds.distinct_terminals == 1
    assert seeds.outcome is Outcome.FAIL
    assert set(seeds.clearing) == set(seeds.world_ids)
    with pytest.raises(UnattainableGate):
        require_reachable(seeds)


def test_only_the_full_contract_clears_every_gate() -> None:
    for subject in p14b.SUBJECT_IMPLEMENTATIONS:
        run = p14b.BenchInput(seed=p14b.shipped_input().seed, subject=subject)
        expected = (
            p14b.SHIPPED_TERMINAL
            if subject == p14b.SUBJECT_SLOT
            else p14b.NEGATIVE_TERMINAL
        )
        assert p14b.bench(run)["terminal"] == expected, subject


def test_every_registered_world_is_one_the_protocol_admits() -> None:
    """The register is the artifact a reviewer audits, so it has to be auditable."""

    worlds = p14b.declared_worlds()
    subjects = {world.payload.subject for world in worlds}
    seeds = {world.payload.seed for world in worlds}

    assert subjects == set(p14b.SUBJECT_IMPLEMENTATIONS)
    assert subjects == {p14b.SUBJECT_SLOT} | set(p14b.ABLATED_FACT)
    assert seeds == {p14b.shipped_input().seed} | set(p14b.ALTERNATE_SEEDS)
    assert len({world.world_id for world in worlds}) == len(worlds)
    for world in worlds:
        assert world.admits.strip()
    with pytest.raises(ValueError):
        p14b.BenchInput(seed=1, subject="NOT_A_REGISTERED_IMPLEMENTATION")


# ---------------------------------------------------------------------------
# The count: four of the eight gates carry a reading, and four do not
# ---------------------------------------------------------------------------


def test_four_of_the_eight_gates_could_have_gone_either_way() -> None:
    """The finding the receipt's "eight gates, all true" does not say."""

    assert p14b.discriminating_gates() == (
        "full_zero_false_promotion",
        "accuracy_advantage_ge_0_08",
        "retain_and_reopen_exact",
        "each_ablation_worse",
    )
    assert len(p14b.discriminating_gates()) == 4
    assert len(p14b.GATES) == 8

    reaches = {reach.gate.gate_id: reach for reach in p14b.gate_reaches()}
    assert tuple(
        gate_id
        for gate_id, reach in reaches.items()
        if reach.reason is GateReachReason.THRESHOLD_UNCONDITIONAL
    ) == (
        "full_discovery_recall_one",
        "strongest_baseline_false_promotion_ge_0_05",
        "matched_budget",
        "byte_identical_replay",
    )


def test_two_hypothesis_gates_have_no_admissible_world_that_can_fail_them() -> None:
    """Unconditional and load-bearing: these two are counted as evidence."""

    assert p14b.unexercised_hypothesis_gates() == (
        "full_discovery_recall_one",
        "matched_budget",
    )
    reaches = {reach.gate.gate_id: reach for reach in p14b.gate_reaches()}
    for gate_id in p14b.unexercised_hypothesis_gates():
        reach = reaches[gate_id]
        assert reach.gate.role is GateRole.HYPOTHESIS, gate_id
        assert reach.reason is GateReachReason.THRESHOLD_UNCONDITIONAL, gate_id
        assert reach.outcome is Outcome.FAIL, gate_id
        assert reach.refuting == (), gate_id


def test_the_two_unconditional_preconditions_are_certificates_not_claims() -> None:
    """Unconditional is what a precondition is supposed to be, and only that."""

    reaches = {reach.gate.gate_id: reach for reach in p14b.gate_reaches()}
    for gate_id in (
        "strongest_baseline_false_promotion_ge_0_05",
        "byte_identical_replay",
    ):
        reach = reaches[gate_id]
        assert reach.gate.role is GateRole.PRECONDITION, gate_id
        assert reach.reason is GateReachReason.THRESHOLD_UNCONDITIONAL, gate_id
        assert reach.outcome is Outcome.PASS, gate_id


def test_the_difficulty_precondition_p14a_could_not_meet_is_met_everywhere_here() -> None:
    """P14B's whole reason to exist, as one comparison of the same statistic."""

    reaches = {reach.gate.gate_id: reach for reach in p14b.gate_reaches()}
    difficulty = reaches["strongest_baseline_false_promotion_ge_0_05"]

    assert difficulty.gate.threshold == 0.05
    assert difficulty.best_value == pytest.approx(SHARE)
    assert p14b.stratum_share() == pytest.approx(SHARE)
    assert p14a.discriminator_supremum() == pytest.approx(0.04232587750858594)
    assert p14b.stratum_share() > p14a.discriminator_supremum()
    # The same threshold, the same statistic, unreachable there and unconditional here.
    assert p14a.threshold_panel().unattainable == tuple(p14a.SUPPORT_BOUNDED_GATES)


# ---------------------------------------------------------------------------
# Why the four unconditional gates are unconditional, derived not observed
# ---------------------------------------------------------------------------


def test_no_registered_arm_can_miss_a_promotable_case() -> None:
    """The derivation ``full_discovery_recall_one``'s declared support rests on."""

    states = p14b.promotable_states()

    assert len(p14b.fact_space()) == 256
    assert len(states) == 3
    assert p14b.arms_missing_a_promotable_state() == {arm: 0 for arm in p14b.ARMS}
    for world in p14b.declared_worlds():
        summary = p14b.bench(world.payload)["summary"]
        for arm in p14b.ARMS:
            assert summary[arm]["useful_discovery_recall"] == 1.0, (world.world_id, arm)


def test_breaking_the_recall_reading_breaks_the_unconditional_verdict() -> None:
    """MUTATION: make one registered world's subject miss a promotable case.

    The guard is ``GateReach.reason``'s ``THRESHOLD_UNCONDITIONAL`` branch. A
    single world whose recall falls short must turn the verdict into
    ``BOTH_OUTCOMES_REACHABLE``; if it does not, the verdict was never reading
    the arms' rates.
    """

    gate = next(g for g in p14b.GATES if g.gate_id == "full_discovery_recall_one")
    worlds = p14b.declared_worlds()
    honest = measure_gate_attainability(
        p14b.RUN_READINGS["full_discovery_recall_one"], gate=gate, worlds=worlds
    )
    assert honest.reason is GateReachReason.THRESHOLD_UNCONDITIONAL

    def abstaining(run: p14b.BenchInput) -> float:
        value = p14b.RUN_READINGS["full_discovery_recall_one"](run)
        return 0.5 if run.subject == "ABLATE_DONOR" else value

    mutated = measure_gate_attainability(abstaining, gate=gate, worlds=worlds)
    assert mutated.reason is GateReachReason.BOTH_OUTCOMES_REACHABLE
    assert mutated.refuting == ("ablate-donor",)
    assert mutated.outcome is Outcome.PASS
    # ... and the honest reading is unchanged by having asked.
    assert p14b.unexercised_hypothesis_gates() == (
        "full_discovery_recall_one",
        "matched_budget",
    )


def test_the_budget_gate_is_a_module_literal_not_a_measurement() -> None:
    module = p14b.runner_module()

    assert module.BUDGET == 7
    for world in p14b.declared_worlds():
        summary = p14b.bench(world.payload)["summary"]
        assert {summary[arm]["decision_budget_checks"] for arm in p14b.ARMS} == {7}
    assert p14b.shipped_receipt()["decision_budget_checks_per_arm"] == 7


def test_breaking_the_budget_reading_breaks_the_unconditional_verdict() -> None:
    """MUTATION: give one world two distinct budget receipts."""

    gate = next(g for g in p14b.GATES if g.gate_id == "matched_budget")
    worlds = p14b.declared_worlds()
    assert (
        measure_gate_attainability(
            p14b.RUN_READINGS["matched_budget"], gate=gate, worlds=worlds
        ).reason
        is GateReachReason.THRESHOLD_UNCONDITIONAL
    )

    def unmatched(run: p14b.BenchInput) -> float:
        return 2.0 if run.subject == "ABLATE_FREEZE" else 1.0

    mutated = measure_gate_attainability(unmatched, gate=gate, worlds=worlds)
    assert mutated.reason is GateReachReason.BOTH_OUTCOMES_REACHABLE
    assert mutated.refuting == ("ablate-freeze",)


def test_the_replay_gate_is_measured_by_running_the_generator_twice() -> None:
    """Not read back off the receipt's own claim: two executions, compared as bytes."""

    assert p14b.replay_is_byte_identical(p14b.shipped_input()) == 1.0
    for world in p14b.declared_worlds():
        assert p14b.replay_is_byte_identical(world.payload) == 1.0


def test_breaking_the_replay_reading_breaks_the_unconditional_verdict() -> None:
    """MUTATION: make one world's second execution differ."""

    gate = next(g for g in p14b.GATES if g.gate_id == "byte_identical_replay")
    worlds = p14b.declared_worlds()
    assert (
        measure_gate_attainability(
            p14b.RUN_READINGS["byte_identical_replay"], gate=gate, worlds=worlds
        ).reason
        is GateReachReason.THRESHOLD_UNCONDITIONAL
    )

    mutated = measure_gate_attainability(
        lambda run: 0.0 if run.seed == 20260821 else 1.0, gate=gate, worlds=worlds
    )
    assert mutated.reason is GateReachReason.BOTH_OUTCOMES_REACHABLE
    assert mutated.refuting == ("alternate-seed-20260821",)


# ---------------------------------------------------------------------------
# The four that do discriminate, and what makes each of them move
# ---------------------------------------------------------------------------


def test_each_discriminating_gate_is_refuted_by_a_named_ablation() -> None:
    reaches = {reach.gate.gate_id: reach for reach in p14b.gate_reaches()}
    ablations = {
        "ablate-donor",
        "ablate-freeze",
        "ablate-interaction",
        "ablate-negative-history",
    }

    assert set(reaches["full_zero_false_promotion"].refuting) == ablations
    assert set(reaches["each_ablation_worse"].refuting) == ablations
    # ABLATE_FREEZE costs only the frozen-failure third of one stratum, so it
    # still clears the 0.08 margin: the gate is not a proxy for "is an ablation".
    assert set(reaches["accuracy_advantage_ge_0_08"].refuting) == ablations - {
        "ablate-freeze"
    }
    assert reaches["retain_and_reopen_exact"].refuting == ("ablate-negative-history",)
    assert reaches["accuracy_advantage_ge_0_08"].best_value == pytest.approx(SHARE)


def test_breaking_the_advantage_threshold_breaks_its_discriminating_verdict() -> None:
    """MUTATION: move the frozen 0.08 above the statistic's ceiling and below its floor.

    The guard is ``ThresholdReach.reason``. Raising the bar past ``1/7`` must
    make it ``THRESHOLD_UNATTAINABLE`` --- P14A's defect --- and dropping it to
    ``0.0`` must make it ``THRESHOLD_UNCONDITIONAL``. A threshold that reports
    ``BOTH_OUTCOMES_REACHABLE`` either way is not being compared to anything.
    """

    gate = next(g for g in p14b.GATES if g.gate_id == "accuracy_advantage_ge_0_08")
    support = p14b.declared_supports()["accuracy_advantage_ge_0_08"]

    assert gate.threshold == 0.08
    assert assess_threshold_support(gate, support=support).reason is (
        GateReachReason.BOTH_OUTCOMES_REACHABLE
    )
    assert assess_threshold_support(
        replace(gate, threshold=0.20), support=support
    ).reason is GateReachReason.THRESHOLD_UNATTAINABLE
    assert assess_threshold_support(
        replace(gate, threshold=0.0), support=support
    ).reason is GateReachReason.THRESHOLD_UNCONDITIONAL
    # The frozen gate is untouched by having asked.
    assert (
        next(g for g in p14b.GATES if g.gate_id == "accuracy_advantage_ge_0_08").threshold
        == 0.08
    )


def test_breaking_an_arms_rate_breaks_the_terminals_two_words() -> None:
    """MUTATION: give every registered world a passing reading on every gate.

    The guard is the intersection ``TerminalReach.clearing`` performs. If no
    world refutes anything the conjunction must collapse to one word, which is
    what P14A's did.
    """

    worlds = p14b.declared_worlds()
    always = tuple(
        measure_gate_attainability(
            lambda _run, gate=gate: (
                gate.threshold - 1.0
                if gate.direction.value == "AT_MOST"
                else gate.threshold + 1.0
            ),
            gate=gate,
            worlds=worlds,
        )
        for gate in p14b.GATES
    )
    collapsed = measure_terminal_reach(always, label="mutated")

    assert collapsed.distinct_terminals == 1
    assert collapsed.outcome is Outcome.FAIL
    assert len(collapsed.clearing) == len(worlds)
    with pytest.raises(UnattainableGate):
        require_reachable(collapsed)
    # ... and the real terminal still prints two words.
    assert p14b.terminal_reach().distinct_terminals == 2


def test_removing_the_admissible_register_is_refused_not_defaulted() -> None:
    """MUTATION: an empty register must raise rather than report a clean gate."""

    gate = next(g for g in p14b.GATES if g.gate_id == "full_zero_false_promotion")
    with pytest.raises(UnattainableGate):
        measure_gate_attainability(
            p14b.RUN_READINGS["full_zero_false_promotion"], gate=gate, worlds=[]
        )
    with pytest.raises(ValueError):
        AdmissibleWorld(world_id="unjustified", admits="  ", payload=p14b.shipped_input())


# ---------------------------------------------------------------------------
# The pre-run panel: every bar inside reach, and the battery still carries four
# ---------------------------------------------------------------------------


def test_no_p14b_threshold_was_outside_its_statistics_reach() -> None:
    """The defect P14B was frozen to fix, and it did fix it."""

    panel = p14b.threshold_panel()

    assert panel.unattainable == ()
    assert panel.discriminating == (
        "full_zero_false_promotion",
        "accuracy_advantage_ge_0_08",
        "retain_and_reopen_exact",
        "each_ablation_worse",
    )


def test_the_pre_run_panel_fails_on_two_unconditional_hypothesis_gates() -> None:
    panel = p14b.threshold_panel()

    assert panel.unconditional_hypotheses == (
        "full_discovery_recall_one",
        "matched_budget",
    )
    assert panel.outcome is Outcome.FAIL
    with pytest.raises(UnattainableGate) as excinfo:
        require_supported_thresholds(panel)
    assert "full_discovery_recall_one" in str(excinfo.value)
    assert "matched_budget" in str(excinfo.value)


def test_breaking_the_declared_support_breaks_the_panels_verdict() -> None:
    """MUTATION: widen the recall support to an interval a run could fall short in.

    The guard is ``ThresholdPanel.unconditional_hypotheses``. With the two
    degenerate intervals opened the panel must pass; if it fails anyway, the FAIL
    above was not caused by the supports it names.
    """

    # Each interval is opened on the side the gate's own direction can fall
    # short on: recall is AT_LEAST 1.0 so its floor drops, the budget count is
    # AT_MOST 1.0 so its ceiling rises. Opening both downward leaves
    # ``matched_budget`` unconditional, which is what a mutation is for.
    widened = {
        "full_discovery_recall_one": (0.0, 1.0),
        "matched_budget": (1.0, 2.0),
    }
    supports = dict(p14b.declared_supports())
    opened = []
    for gate in p14b.GATES:
        support = supports[gate.gate_id]
        if gate.gate_id in widened:
            low, high = widened[gate.gate_id]
            support = replace(support, infimum=low, supremum=high)
        opened.append(assess_threshold_support(gate, support=support))
    mutated = assess_threshold_panel(opened, label="mutated")

    assert mutated.unconditional_hypotheses == ()
    assert mutated.outcome is Outcome.PASS
    require_supported_thresholds(mutated)
    # ... and the honest panel still fails.
    assert p14b.threshold_panel().outcome is Outcome.FAIL


def test_every_declared_support_states_a_derivation_a_reader_can_re_run() -> None:
    supports = p14b.declared_supports()

    assert set(supports) == {gate.gate_id for gate in p14b.GATES}
    for gate_id, support in supports.items():
        assert support.derivation.strip(), gate_id
        assert support.statistic.strip(), gate_id
        assert support.infimum <= support.supremum, gate_id

    # Each interval has to contain what the register actually measured.
    for reach in p14b.gate_reaches():
        support = supports[reach.gate.gate_id]
        for reading in reach.readings:
            assert support.infimum - 1e-12 <= reading.value <= support.supremum + 1e-12, (
                reach.gate.gate_id,
                reading.world_id,
            )


def test_the_baselines_nest_so_the_comparator_selection_has_nowhere_to_land() -> None:
    strata = p14b.arm_error_strata()

    assert strata["ORION_RSE_FULL"] == ()
    assert strata["MULTI_REVIEW"] == (p14b.DISCRIMINATING_STRATUM,)
    assert set(strata["MULTI_REVIEW"]) < set(strata["DONOR_AWARE_REVIEW"])
    assert set(strata["DONOR_AWARE_REVIEW"]) < set(strata["REFLECTION_CHECKLIST"])
    assert set(strata["REFLECTION_CHECKLIST"]) < set(strata["RAW_POSITIVE"])
    assert strata["ABLATE_NEGATIVE_HISTORY"] == (p14b.DISCRIMINATING_STRATUM,)
    for world in p14b.declared_worlds():
        assert p14b.bench(world.payload)["strongest_non_orion_baseline"] == "MULTI_REVIEW"


# ---------------------------------------------------------------------------
# The graded arm is the answer key
# ---------------------------------------------------------------------------


def test_the_graded_arm_is_the_gold_that_grades_it() -> None:
    """Measured, not quoted: it is why the subject's side of every gate is fixed."""

    divergence = p14b.graded_arm_divergence()

    assert divergence.points == 256
    assert divergence.points_changed == 0
    assert divergence.applied is False
    # The same construction P14A's audit measures on its own graded arm.
    assert p14a.orion_arm_divergence().points_changed == 0


def test_breaking_the_graded_arm_breaks_the_divergence_verdict() -> None:
    """MUTATION: an arm that is not the answer key must report divergent points."""

    from orion.programme.refutation_capacity import divergence_of

    module = p14b.runner_module()
    mutated = divergence_of(
        lambda point: module.policy("MULTI_REVIEW", dict(point)),
        theory_id="MULTI_REVIEW",
        reference=lambda point: module.gold(dict(point)),
        space=p14b.fact_space(),
    )

    assert mutated.points_changed > 0
    assert mutated.applied is True
    assert p14b.graded_arm_divergence().points_changed == 0


# ---------------------------------------------------------------------------
# The audit, and the receipt it is written into
# ---------------------------------------------------------------------------


def test_the_audit_reports_both_answers_and_does_not_let_either_offset_the_other() -> None:
    report = p14b.audit_p14b_balanced_terminal()
    payload = p14b.report_as_json(report)

    assert report["digest_reproduced"] is True
    assert report["terminal_reach"].outcome is Outcome.PASS
    assert report["threshold_panel"].outcome is Outcome.FAIL
    assert report["grading_outcome"] is Outcome.FAIL
    assert report["outcome"] is Outcome.FAIL
    assert payload["terminal_reach"]["distinct_terminals"] == 2
    assert payload["seed_only_terminal_reach"]["distinct_terminals"] == 1
    assert payload["discriminating_gates"] == [
        "full_zero_false_promotion",
        "accuracy_advantage_ge_0_08",
        "retain_and_reopen_exact",
        "each_ablation_worse",
    ]
    assert payload["unexercised_hypothesis_gates"] == [
        "full_discovery_recall_one",
        "matched_budget",
    ]
    assert json.dumps(payload, sort_keys=True)


def test_the_audit_exits_three_and_names_the_count() -> None:
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        code = p14b.main([])
    text = stream.getvalue()

    assert code == 3
    assert "reachable terminals: 2" in text
    assert "gates that could have gone either way: 4/8" in text
    assert "full_discovery_recall_one, matched_budget" in text

    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        assert p14b.main(["--json"]) == 3
    assert '"outcome": "FAIL"' in stream.getvalue()


def test_the_recall_gate_carries_the_same_defect_p14c_reports_for_its_own() -> None:
    """The pair is the point: two P14 successors, one unexercised gate each."""

    assert "full_discovery_recall_one" in p14c.unexercised_hypothesis_gates()
    assert "full_discovery_recall_one" in p14b.unexercised_hypothesis_gates()
    assert p14c.unexercised_hypothesis_gates() == ("full_discovery_recall_one",)
    assert p14b.unexercised_hypothesis_gates() == (
        "full_discovery_recall_one",
        "matched_budget",
    )


# ---------------------------------------------------------------------------
# Nothing frozen is edited
# ---------------------------------------------------------------------------


def test_p14bs_frozen_receipt_is_untouched_by_the_audit() -> None:
    """The rule the whole exercise is bound by: a protected result is not rewritten."""

    published = p14b.shipped_receipt()

    assert published["terminal"] == "P14B_BALANCED_GOVERNANCE_SUPERIORITY_SUPPORTED"
    assert published["seed"] == 2026082115
    assert published["replay_sha256"] == p14b.SHIPPED_RESULT_DIGEST
    assert published["gates"] == {
        "full_zero_false_promotion": True,
        "full_discovery_recall_one": True,
        "strongest_baseline_false_promotion_ge_0_05": True,
        "accuracy_advantage_ge_0_08": True,
        "retain_and_reopen_exact": True,
        "each_ablation_worse": True,
        "matched_budget": True,
        "byte_identical_replay": True,
    }
    assert all(published["gates"].values())
    assert {gate.gate_id for gate in p14b.GATES} == set(published["gates"])
    assert {gate.gate_id: gate.threshold for gate in p14b.GATES} == {
        "full_zero_false_promotion": 0.0,
        "full_discovery_recall_one": 1.0,
        "strongest_baseline_false_promotion_ge_0_05": 0.05,
        "accuracy_advantage_ge_0_08": 0.08,
        "retain_and_reopen_exact": 1.0,
        "each_ablation_worse": 4.0,
        "matched_budget": 1.0,
        "byte_identical_replay": 1.0,
    }
    for arm, rates in published["summary"].items():
        assert rates["useful_discovery_recall"] == 1.0, arm


def test_the_adjudication_now_carries_a_p14b_key() -> None:
    receipt = json.loads(
        (p14b.PAPER / "P14_GATE_ATTAINABILITY_ADJUDICATION_V1.json").read_text(
            encoding="utf-8"
        )
    )

    assert set(receipt) >= {"p14a", "p14b", "p14c"}
    assert receipt["edits_no_frozen_result"] is True
    assert all(receipt["gates"].values())

    block = receipt["p14b"]
    assert block["terminal_retained_verbatim"] == p14b.SHIPPED_TERMINAL
    assert block["replay_sha256"] == p14b.SHIPPED_RESULT_DIGEST
    assert block["committed_digest_reproduced"] is True
    assert block["terminal_reach"]["distinct_terminals"] == 2
    assert block["gates_that_discriminate"] == list(p14b.discriminating_gates())
    assert block["gates_published"] == len(p14b.GATES) == 8
    assert block["hypothesis_gates_without_refutation_capacity"] == list(
        p14b.unexercised_hypothesis_gates()
    )
    assert block["evidential_disposition"] == "TERMINAL_REACHABLE__GATE_COUNT_INFLATED"
