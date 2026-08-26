"""P11H's battery, asked the question P11G was never asked before it ran.

``research/failures/2026-08-unwinnable-attack-predetermined-survival/`` records
that P11G's four scientific gates hold in every world its freeze admits, so its
survival was arithmetic. These tests pin the two properties whose absence made
that possible, on the successor:

* every P11H threshold is inside the reach of the statistic it reads, and at
  least one *hypothesis* gate could have gone either way; and
* the terminal has two reachable values over the register --- the P14 pattern,
  ``distinct_terminals >= 2``.

Both are checked against the protocol's own declared support, before any outcome
is read, which is the step P11G and P14A both skipped.
"""

from __future__ import annotations

import copy
import hashlib
import json

import pytest

from orion.programme.gate_attainability import (
    GateReachReason,
    GateRole,
    UnattainableGate,
    assess_threshold_panel,
    measure_terminal_reach,
    require_reachable,
    require_supported_thresholds,
)
from orion.programme.records import Outcome
from orion.study.p11 import successor_reach as p11h


# Diagnostic-only digest for the current exact lock. The historical receipt's
# 61ec... digest and adverse ``delta64`` gate remain immutable.
CURRENT_LOCKED_SCIENTIFIC_SHA256 = (
    "31654d231bacd5f926b36a9a180c1ef6f7696e71e0d7d039f1552ed898a7970f"
)


def assert_p11h_locked_replay_boundary(
    published: dict[str, object], fresh: dict[str, object], runner
) -> str:
    """Allow only the known tree-estimator and tree-derived replay boundary."""

    digest = hashlib.sha256(runner.canonical_text(fresh).encode("utf-8")).hexdigest()
    historical_digest = hashlib.sha256(
        runner.canonical_text(published).encode("utf-8")
    ).hexdigest()
    assert historical_digest == "61ecf79f652b74447dd70caa4cf019f2e35f67559583144d68d44cd7f92dd6dd"
    assert digest in {historical_digest, CURRENT_LOCKED_SCIENTIFIC_SHA256}
    assert fresh["scientific_gates"] == published["scientific_gates"]
    assert fresh["scientific_terminal"] == published["scientific_terminal"]

    historical_without_tree = copy.deepcopy(published)
    fresh_without_tree = copy.deepcopy(fresh)
    for historical_rung, fresh_rung in zip(
        historical_without_tree["ladder_readings"], fresh_without_tree["ladder_readings"]
    ):
        for rung in (historical_rung, fresh_rung):
            rung["curves"].pop("UNIVERSAL_EXTRA_TREES")
            rung.pop("pooled_curve")
            rung.pop("delta64_vs_pool")
            rung["decomposition"].pop("published_gap_at_64")
            rung["decomposition"]["tree_family"].pop("representation_gap")
            rung["decomposition"]["tree_family"].pop("state_share")
    assert fresh_without_tree == historical_without_tree
    return digest


@pytest.fixture(scope="module")
def runner():
    return p11h.p11h_module()


@pytest.fixture(scope="module")
def panel():
    return p11h.threshold_panel()


@pytest.fixture(scope="module")
def terminal():
    return p11h.terminal_reach()


@pytest.fixture(scope="module")
def receipt():
    if not p11h.P11H_RESULT.exists():  # pragma: no cover - executed protocol is committed
        pytest.skip("P11H has not been executed in this tree")
    return json.loads(p11h.P11H_RESULT.read_text(encoding="utf-8"))


def test_p11h_carries_p11gs_own_thresholds_unedited(runner):
    """The bars are not moved. Only the support of the statistic they read is."""

    p11g = p11h.PAPER_DIR / "P11G_DETERMINISTIC_TREE_DECODER_PROTOCOL_V1.md"
    text = p11g.read_text(encoding="utf-8")
    assert "0.95" in text and ">= 0.20" in text
    assert runner.TARGET_ACCURACY == 0.95
    assert runner.DELTA64_THRESHOLD == 0.20


def test_every_threshold_is_inside_its_own_statistics_reach(panel):
    """The check whose absence is ``UNATTAINABLE_GATE_PREDETERMINED_TERMINAL``."""

    require_supported_thresholds(panel)
    assert panel.outcome is Outcome.PASS
    assert panel.unattainable == ()
    assert panel.unconditional_hypotheses == ()


def test_at_least_one_hypothesis_gate_could_have_gone_either_way(panel):
    """A battery of preconditions certifies an instrument and asserts nothing."""

    assert panel.discriminating, "no hypothesis gate discriminates, so the panel carries no claim"
    for reach in panel.reaches:
        if reach.gate.role is GateRole.HYPOTHESIS:
            assert reach.reason is GateReachReason.BOTH_OUTCOMES_REACHABLE
            assert reach.attainment_margin > 0
            assert reach.refutation_margin < 0


def test_the_declared_support_brackets_each_threshold_strictly(panel):
    """A threshold on the boundary of its support is a gate one rounding from arithmetic."""

    for reach in panel.reaches:
        if reach.gate.role is not GateRole.HYPOTHESIS:
            continue
        support = reach.support
        assert support.infimum < reach.gate.threshold < support.supremum
        assert support.width > 0
        assert support.derivation.strip()


def test_the_terminal_had_two_reachable_values(terminal):
    """The P14 pattern. P11G's own ``terminal_reach`` reports ``1`` here."""

    require_reachable(terminal)
    assert terminal.distinct_terminals >= 2
    assert terminal.outcome is Outcome.PASS
    assert 0 < len(terminal.clearing) < len(terminal.world_ids)


def test_the_attack_wins_in_some_admissible_world_and_loses_in_others(terminal):
    """A survived attack is evidence only for as long as the attack could have won."""

    hypothesis = [
        reach for reach in terminal.reaches if reach.gate.role is GateRole.HYPOTHESIS
    ]
    assert hypothesis
    losing = {
        world
        for reach in hypothesis
        for world in reach.refuting
    }
    assert losing, "no admissible draw brings a hypothesis gate down: the attack cannot win"
    assert set(terminal.clearing), "no admissible draw clears every gate: the defence cannot win"


def test_the_instrument_precondition_certifies_a_live_attack(terminal):
    """``attack_live_on_ladder`` is *meant* to hold everywhere, and is a PRECONDITION.

    The gate P11G never wrote: it says the pooled attack registers a win
    somewhere on the frozen ladder, so a defeat elsewhere is a measurement rather
    than arithmetic. Unconditional is ``PASS`` for a precondition and ``FAIL``
    for a hypothesis, which is the whole reason the role is declared.
    """

    live = next(
        reach for reach in terminal.reaches if reach.gate.gate_id == "attack_live_on_ladder"
    )
    assert live.gate.role is GateRole.PRECONDITION
    assert live.outcome is Outcome.PASS
    assert live.reason in (
        GateReachReason.THRESHOLD_UNCONDITIONAL,
        GateReachReason.BOTH_OUTCOMES_REACHABLE,
    )


def test_a_ladder_of_only_wide_regimes_reproduces_the_p11g_defect(terminal):
    """The negative control: restricted to regimes the attack cannot win, P11H fails too.

    This is the test that says the battery is measuring reachability rather than
    asserting it. Drop every world in which a hypothesis gate falls and the same
    apparatus reports ``THRESHOLD_UNCONDITIONAL`` and one reachable terminal ---
    which is exactly what it reports about P11G.
    """

    surviving = set(terminal.clearing)
    worlds = [world for world in p11h.admissible_worlds() if world.world_id in surviving]
    assert len(worlds) >= 2
    narrowed = measure_terminal_reach(
        p11h.gate_reaches(worlds=worlds), label="P11H restricted to surviving draws"
    )
    assert narrowed.distinct_terminals == 1
    assert narrowed.outcome is Outcome.FAIL
    # and it fails for P11G's exact reason, on P11G's exact two statistics:
    # the hostile gates become satisfied by every world in the narrowed register.
    assert set(narrowed.unconditional) >= {
        "pooled_universal_threshold_ge_256",
        "delta64_ge_0_20",
    }
    assert narrowed.unattainable == ()
    with pytest.raises(UnattainableGate):
        require_reachable(narrowed)
    # the full register is the same apparatus on a wider set, so the PASS above
    # is a property of the ladder rather than of the measurement.
    assert terminal.distinct_terminals == 2


def test_an_unattainable_threshold_is_refused_by_the_panel(panel):
    """The panel is not decorative: move one bar out of reach and it raises."""

    from dataclasses import replace

    reaches = list(panel.reaches)
    broken = replace(
        reaches[-1], gate=replace(reaches[-1].gate, threshold=reaches[-1].support.supremum + 1.0)
    )
    hostile = assess_threshold_panel(reaches[:-1] + [broken], label="hostile")
    assert hostile.outcome is Outcome.FAIL
    with pytest.raises(UnattainableGate):
        require_supported_thresholds(hostile)


def test_every_registered_world_states_why_the_freeze_admits_it():
    """A world nobody can see is admissible widens the gate rather than measuring it."""

    worlds = p11h.admissible_worlds()
    runner = p11h.p11h_module()
    expected = len(runner.LADDER)
    assert len(worlds) == expected * (expected - 1) // 2
    assert len({world.world_id for world in worlds}) == len(worlds)
    for world in worlds:
        assert world.admits.strip()
        assert len(world.payload) == runner.N_PROTECTED


def test_the_pooled_gate_is_not_a_function_of_which_arm_was_carried(runner):
    """P11G's terminal moved with the arm placed in its gate. P11H reads the pool.

    The combination rule is frozen inside this protocol's own positive gate, so
    the statistic dominates every registered arm by construction and no arm
    choice can lower it.
    """

    rungs = runner.measure_ladder(p11h.PREFLIGHT_SEED)
    strictly_better_than_p11gs_arm = 0
    for rung in rungs:
        for size in runner.GATE_SIZES:
            pooled = rung["pooled_curve"][str(size)]
            # the receipt's pooled curve really is the frozen combination rule,
            # not some other number that happens to be published beside it
            assert pooled == max(
                rung["curves"][arm][str(size)] for arm in runner.UNIVERSAL_POOL
            )
            for arm in runner.UNIVERSAL_POOL:
                assert pooled >= rung["curves"][arm][str(size)]
            if pooled > rung["curves"]["UNIVERSAL_EXTRA_TREES"][str(size)]:
                strictly_better_than_p11gs_arm += 1
    # and pooling is not decorative: somewhere on the ladder the pool is strictly
    # stronger than the single arm P11G carried into its gate.
    assert strictly_better_than_p11gs_arm > 0


def test_the_recorded_preflight_reproduces(runner):
    """The preflight artifact is content-addressed against a fresh run of the same code."""

    if not p11h.P11H_PREFLIGHT.exists():  # pragma: no cover - artifact is committed
        pytest.skip("P11H preflight artifact not written in this tree")
    recorded = json.loads(p11h.P11H_PREFLIGHT.read_text(encoding="utf-8"))
    fresh = p11h.preflight()
    assert recorded["preflight_seed"] == fresh["preflight_seed"] == p11h.PREFLIGHT_SEED
    assert recorded["execution_seed"] == runner.EXECUTION_SEED
    assert recorded["preflight_seed"] != recorded["execution_seed"]
    assert recorded["ladder_readings"] == fresh["ladder_readings"]
    assert recorded["threshold_panel"] == fresh["threshold_panel"]
    assert recorded["distinct_terminals"] == fresh["distinct_terminals"] >= 2


def test_the_shipped_receipt_and_current_locked_replay_are_not_conflated(receipt, runner):
    """Preserve the old bytes while pinning the current decision-stable replay."""

    published = receipt["scientific_payload"]
    fresh = runner.scientific_payload(published["seed"])
    digest = assert_p11h_locked_replay_boundary(published, fresh, runner)
    assert receipt["replay"]["first_sha256"] == receipt["replay"]["second_sha256"]
    assert receipt["replay"]["first_sha256"] == (
        "61ecf79f652b74447dd70caa4cf019f2e35f67559583144d68d44cd7f92dd6dd"
    )
    assert (fresh == published) is (digest == receipt["replay"]["first_sha256"])
    assert receipt["replay"]["byte_identical"] is True
    assert receipt["replay"]["fresh_python_subprocesses"] == 2


def test_the_receipt_terminal_is_the_protocols_own_expression(receipt, runner):
    """Recompute the verdict from the published statistics rather than trusting the string."""

    published = receipt["scientific_payload"]
    values = published["gate_statistics"]
    gates = runner.gate_booleans(values)
    assert gates == published["scientific_gates"]
    assert runner.scientific_terminal(gates) == published["scientific_terminal"]
    assert receipt["terminal"] in (
        runner.SURVIVED_TERMINAL,
        runner.PREVAILED_TERMINAL,
        runner.PRECONDITION_TERMINAL,
    )


def test_the_executed_draw_is_one_of_the_registered_admissible_worlds(receipt, runner):
    """The run has to be a draw from the register the attainability was measured over."""

    published = receipt["scientific_payload"]
    drawn = tuple(published["protected_regimes"])
    assert drawn == tuple(runner.drawn_regimes(published["seed"]))
    registered = {tuple(world.payload) for world in p11h.admissible_worlds()}
    assert drawn in registered


def test_the_receipt_carries_the_decoder_held_fixed_control(receipt):
    """The decomposition the adjudication asked a successor to compute in its own receipt."""

    for rung in receipt["scientific_payload"]["ladder_readings"]:
        decomposition = rung["decomposition"]
        published = decomposition["published_gap_at_64"]
        tree = decomposition["tree_family"]
        assert tree["decoder_family_gap"] + tree["representation_gap"] == pytest.approx(published)
        assert "linear_family_representation_gap" in decomposition


def test_the_instrument_precondition_holds_in_the_executed_run(receipt):
    """A negative is only a result if the run's own instrument certified itself."""

    gates = receipt["scientific_payload"]["scientific_gates"]
    roles = receipt["scientific_payload"]["gate_roles"]
    for gate_id, role in roles.items():
        if role == "PRECONDITION":
            assert gates[gate_id] is True, f"{gate_id} did not certify the instrument"


def test_the_audit_reports_the_successor_and_still_blocks_on_p11g(receipt):
    """The successor is a reading in P11G's audit, and it does not lower the exit code.

    P11G's four gates hold in every world P11G admits and that is permanent. A
    successor re-asks the question under a protocol whose attack has a reachable
    win; it cannot make the predecessor's emptiness smaller. Letting P11H's
    ``PASS`` offset P11G's ``FAIL`` would be the compensation the audit's
    roll-up exists to refuse, so this pins that it does not.
    """

    from orion.study.p11.attack_audit import audit_p11g_attack_terminal, report_as_json
    from orion.study.p11 import decoder_attack_reach as p11g

    if p11g.shipped_scientific_sha256() != p11g.SHIPPED_SCIENTIFIC_SHA256:
        # P11G fidelity is checked before the audit can report P11H. The
        # successor remains available through its own disposition and cannot
        # compensate for the predecessor's CANNOT_CHECK replay boundary.
        with pytest.raises(p11g.P11GFidelityError, match="shipped runner has moved"):
            audit_p11g_attack_terminal()
        successor = p11h.successor_disposition()
        assert successor["retires_unwinnable_attack_finding"] is True
        assert successor["terminal"] == receipt["terminal"]
        return

    report = audit_p11g_attack_terminal()
    assert report["outcome"] is Outcome.FAIL
    assert report["terminal_reach"].outcome is Outcome.FAIL
    assert report["terminal_reach"].distinct_terminals == 1

    successor = report["successor"]
    assert successor["preflight_recorded"] is True
    assert successor["executed"] is True
    assert successor["panel_outcome"] == "PASS"
    assert successor["distinct_terminals"] >= 2
    assert successor["discriminating_hypothesis_gates"]
    assert successor["retires_unwinnable_attack_finding"] is True
    assert successor["terminal"] == receipt["terminal"]

    assert json.loads(json.dumps(report_as_json(report)))["outcome"] == "FAIL"


def test_the_successor_disposition_does_not_claim_retirement_without_an_execution(monkeypatch):
    """``retires`` is false until a preflighted protocol has actually been run."""

    monkeypatch.setattr(p11h, "P11H_RESULT", p11h.P11H_RESULT.with_name("does-not-exist.json"))
    disposition = p11h.successor_disposition()
    assert disposition["executed"] is False
    assert disposition["terminal"] is None
    assert disposition["retires_unwinnable_attack_finding"] is False
