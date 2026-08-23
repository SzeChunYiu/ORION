"""P11G's survived hostile attack, measured against the worlds its own protocol admits.

Every number pinned here was read off the shipped artifacts
``papers/paper-11-state-as-computation/P11G_DETERMINISTIC_TREE_DECODER_RESULT_V1.json``,
``run_p11g_deterministic_tree_decoder_v1.py`` and
``P11C_STRONGER_DECODER_ATTACK_PROTOCOL_V1.md``, or produced by replaying that
runner's own RNG stream with the decoder swapped.
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
    UnattainableGate,
    measure_gate_attainability,
    require_reachable,
)
from orion.programme.records import Outcome
from orion.study.p11 import decoder_attack_reach as p11
from orion.study.p11.attack_audit import audit_p11g_attack_terminal, main, report_as_json


def literal_gates(cells: tuple[p11.CellReading, ...]) -> dict[str, bool]:
    """The runner's four ``scientific_gates`` expressions, transcribed.

    :data:`p11.GATES` reads accuracies and counts where the runner writes
    thresholds and booleans; this is the check that the two agree, so an
    attainability verdict below is about P11G's own gates and not a paraphrase.
    """

    def threshold(reading: p11.CellReading) -> int | None:
        for size, value in reading.attack:
            if value >= 0.95:
                return size
        return None

    def compiled_threshold(reading: p11.CellReading) -> int | None:
        for size, value in reading.defence:
            if value >= 0.95:
                return size
        return None

    return {
        "no_answer_laundering": not any(c.laundering_failures for c in cells),
        "compiled_by_64": all(
            compiled_threshold(c) is not None and compiled_threshold(c) <= 64 for c in cells
        ),
        "tree_threshold_ge_256": all(
            threshold(c) is None or threshold(c) >= 256 for c in cells
        ),
        "delta64_ge_0_20": all(c.delta64 >= 0.20 for c in cells),
    }


def test_the_shipped_runner_reproduces_the_digest_it_published():
    """The fidelity anchor: a failure below is about P11G, not about a local fixture."""

    receipt = p11.shipped_receipt()
    digest = p11.require_fidelity()

    assert digest == p11.SHIPPED_SCIENTIFIC_SHA256
    assert digest == receipt["replay"]["first_sha256"] == receipt["replay"]["second_sha256"]
    assert receipt["terminal"] == p11.SHIPPED_TERMINAL


def test_the_replay_reproduces_every_published_curve_value():
    published = p11.shipped_receipt()["scientific_payload"]["cells"]
    readings = p11.measure(p11.shipped_spec())

    assert p11.shipped_curves_match()
    for reading, cell in zip(readings, published):
        assert list(reading.cell) == cell["cell"]
        assert reading.universal_dimension == cell["universal_dimension"]
        for size in p11.GATE_TRAIN_SIZES:
            assert reading.attack_at(size) == cell["curves"][p11.REPORTED_ARM][str(size)]
            assert reading.defence_at(size) == cell["curves"][p11.DEFENCE_ARM][str(size)]
    assert [r.delta64 for r in readings] == [
        c["compiled_minus_tree_at_64"] for c in published
    ]


def test_the_registered_gates_are_the_runners_own_expressions():
    """Pinned over every world in both registers, admissible and not."""

    worlds = list(p11.admissible_worlds()) + list(p11.capability_cases())
    for world in worlds:
        cells = p11.measure(world.payload)
        assert p11.gate_booleans(world.payload) == literal_gates(cells), world.payload


def test_the_shipped_world_recomputes_the_published_gates_and_terminal():
    spec = p11.shipped_spec()
    published = p11.shipped_receipt()["scientific_payload"]["scientific_gates"]

    assert p11.gate_booleans(spec) == published
    assert p11.terminal_of(spec) == p11.SHIPPED_TERMINAL


def test_no_registered_gate_can_land_on_its_own_boundary():
    """The readings are exact, not approximations of the runner's comparisons.

    A mean of three test accuracies over 4,096 points is a multiple of
    ``1/12288``, and neither ``0.95`` nor ``0.20`` is one, so ``AT_MOST`` and
    ``<`` cannot disagree on any attainable value. Without this the accuracy
    readings would be a paraphrase of the thresholds rather than the thresholds.
    """

    module = p11.p11g_module()
    lattice = module.N_TEST * module.N_QUERIES
    for gate in p11.GATES:
        if gate.threshold == 0.0:
            continue
        assert (gate.threshold * lattice) % 1 != 0, gate.gate_id


def test_the_attack_has_no_reachable_win_in_any_admissible_world():
    """The finding. Both hostile gates hold in every world the freeze admits."""

    reaches = {reach.gate.gate_id: reach for reach in p11.gate_reaches()}
    hostile = ("tree_threshold_ge_256", "delta64_ge_0_20")

    for gate_id in hostile:
        reach = reaches[gate_id]
        assert reach.reason is GateReachReason.THRESHOLD_UNCONDITIONAL, gate_id
        assert reach.outcome is Outcome.FAIL
        assert reach.refuting == ()
        assert len(reach.satisfying) == len(p11.admissible_worlds())

    assert p11.closest_refuting_margin(reaches["tree_threshold_ge_256"]) > 0.29
    assert p11.closest_refuting_margin(reaches["delta64_ge_0_20"]) > 0.17


def test_the_terminal_had_one_reachable_value():
    terminal = p11.terminal_reach()

    assert terminal.distinct_terminals == 1
    assert terminal.outcome is Outcome.FAIL
    assert terminal.unattainable == ()
    assert set(terminal.unconditional) == {gate.gate_id for gate in p11.GATES}
    assert len(terminal.clearing) == len(terminal.world_ids)

    with pytest.raises(UnattainableGate, match="every admissible world satisfies"):
        require_reachable(terminal)


def test_the_attack_arm_is_not_incapable_only_placed_where_it_cannot_win():
    """The half that clears the arm: shrink the bank and the same conjunction flips."""

    responsiveness = p11.attack_responsiveness()

    assert responsiveness.outcome is Outcome.PASS
    assert responsiveness.baseline_verdict == p11.SHIPPED_TERMINAL
    assert set(responsiveness.verdicts_observed) == {p11.SHIPPED_TERMINAL, p11.NOT_MET_TERMINAL}
    assert responsiveness.unmoved == ()
    assert responsiveness.exercise.opportunities == len(p11.capability_cases())


def test_a_bank_the_protocol_does_admit_leaves_the_gates_standing():
    """The register is not a fuzz corpus: banks large enough that the attack loses, lose.

    Without this the responsiveness result above would only show that *some*
    perturbation moves the terminal, which any live branch satisfies.
    """

    for keep in (50, 100, 300, 1000):
        spec = replace(p11.shipped_spec(), bank_columns=keep)
        assert p11.terminal_of(spec) == p11.SHIPPED_TERMINAL, keep


def test_the_registered_pool_contained_an_arm_that_beats_the_gate():
    """Three registered universal arms on P11G's own stream; one of them flips the terminal."""

    pool = p11.registered_pool()
    thresholds = {
        arm: tuple(c.censored_attack_threshold for c in readings)
        for arm, readings in pool.items()
    }

    assert thresholds["UNIVERSAL_EXTRA_TREES"] == (256, 256)
    assert thresholds["UNIVERSAL_L2"] == (256, 256)
    assert thresholds["UNIVERSAL_L1"] == (128, 256)

    assert p11.best_of_arms_thresholds() == (128, 256)
    assert p11.best_of_arms_gate() is False
    assert p11.terminal_under_arm("UNIVERSAL_L1") == p11.NOT_MET_TERMINAL
    assert p11.terminal_under_arm(p11.REPORTED_ARM) == p11.SHIPPED_TERMINAL


def test_p11c_applied_its_own_combination_rule_to_its_own_frozen_data():
    """The premise this module was built on --- an unapplied rule --- is retired by P11C.

    Read off ``P11C_STRONGER_DECODER_ATTACK_RESULT_V1.json``: the rule's own
    statistic is a field of every cell and the gate it feeds is a field of the
    payload. Both are transcribed from the shipped artifact, not asserted here.
    """

    application = p11.p11c_rule_application()
    published = json.loads(p11.P11C_RESULT.read_text(encoding="utf-8"))

    assert application["applied"] is True
    assert application["thresholds"] == (256, 256)
    assert application["gate"] is True
    assert application["terminal"] == "P11C_STRONGER_DECODER_GAP_SUPPORTED"
    assert application["thresholds"] == tuple(
        cell[p11.P11C_RULE_STATISTIC] for cell in published["cells"]
    )
    assert p11.P11C_RECEIPT.is_file()
    assert application["terminal"] in p11.P11C_RECEIPT.read_text(encoding="utf-8")


def test_p11cs_rule_does_not_bind_p11g_and_every_reason_is_still_in_the_freezes():
    """The finding is an argument from freeze text, so the freeze text is the test.

    ``_quote`` raises if a protocol stops containing the words, which is what
    stops this becoming an argument from memory: re-freeze either side and the
    binding has to be re-argued rather than silently inherited.
    """

    binding = p11.rule_binding()

    assert binding.binds is False
    assert binding.applied_to_its_own_data is True
    assert binding.p11c_best_of_arms_thresholds == (256, 256)
    assert binding.p11c_gate is True

    aspects = {row.aspect for row in binding.divergences}
    assert {"gate the rule feeds", "claim the rule serves"} <= aspects
    assert len(binding.divergences) >= 3

    for row in binding.divergences:
        assert row.p11c.text in p11.P11C_PROTOCOL.read_text(encoding="utf-8")
        assert row.p11g.text in p11.P11G_PROTOCOL.read_text(encoding="utf-8")
    for quote in binding.non_crossing:
        assert quote.text in (p11.PAPER_DIR / quote.source).read_text(encoding="utf-8")

    # The three the task of separating two freezes actually turns on.
    assert any("4x the compiled threshold" in row.p11c.text for row in binding.divergences)
    assert any("`>=256`" in row.p11g.text for row in binding.divergences)
    assert any(
        "does not settle the frozen ExtraTrees attack" in quote.text
        for quote in binding.non_crossing
    )


def test_a_freeze_that_stops_saying_it_takes_the_finding_down_with_it(tmp_path):
    """Fail-closed: the conclusion may not outlive the words it was read from."""

    with pytest.raises(p11.P11GFidelityError, match="no longer contains the frozen words"):
        p11._quote(p11.P11G_PROTOCOL, "a sentence no frozen protocol contains")


def test_the_receipt_publishes_one_value_of_an_axis_the_terminal_depends_on():
    """The mirror of P6's inert donor axis, and the reason a declaration is owed."""

    assert p11.receipt_universal_arms() == (p11.REPORTED_ARM,)

    axes = p11.one_value_decision_axes()
    assert len(axes) == 1
    entry = axes[0]
    assert entry["axis"] == "decoder_arm"
    assert entry["values_in_receipt"] == [p11.REPORTED_ARM]
    assert entry["registered_values"] == list(p11.REGISTERED_UNIVERSAL_ARMS)
    assert entry["verdict_changing_pairs"] == 2
    assert entry["terminals"]["UNIVERSAL_L1"] == p11.NOT_MET_TERMINAL


def test_a_one_value_axis_the_terminal_depends_on_must_be_declared_in_the_record():
    """The guard the resolution owes: a future receipt cannot publish one again in silence.

    Every requirement is recomputed from the replayed runner --- the arm names,
    each arm's censored threshold pair, the terminal each prints --- so the
    declaration cannot say something the numbers do not, and the audit blocks
    while any of it is missing.
    """

    required = p11.arm_disclosure_requirements()
    body = p11.ARM_PLACEMENT_ADJUDICATION.read_text(encoding="utf-8")

    assert p11.arm_disclosure_gaps() == ()
    assert "decoder_arm" in required
    assert "`UNIVERSAL_L1` | 128, >=256 | " + p11.NOT_MET_TERMINAL in required
    assert "`UNIVERSAL_EXTRA_TREES` | >=256, >=256 | " + p11.SHIPPED_TERMINAL in required
    for item in required:
        assert item in body, item

    # And it is a live check, not a rubber stamp: take the declaration away and
    # every requirement comes back as a gap.
    original = p11.ARM_PLACEMENT_ADJUDICATION
    try:
        p11.ARM_PLACEMENT_ADJUDICATION = original.with_name("does-not-exist.md")
        gaps = p11.arm_disclosure_gaps()
    finally:
        p11.ARM_PLACEMENT_ADJUDICATION = original
    assert gaps[0].startswith("missing: ")
    assert set(required) <= set(gaps)
    assert p11.arm_disclosure_gaps() == ()


def test_a_declaration_that_omits_one_registered_arm_is_still_a_gap(tmp_path):
    """The axis is declared only when every registered value is, not the reported one."""

    partial = tmp_path / "partial.md"
    body = p11.ARM_PLACEMENT_ADJUDICATION.read_text(encoding="utf-8")
    partial.write_text(
        body.replace("`UNIVERSAL_L1` | 128, >=256 | " + p11.NOT_MET_TERMINAL, "elided"),
        encoding="utf-8",
    )
    original = p11.ARM_PLACEMENT_ADJUDICATION
    try:
        p11.ARM_PLACEMENT_ADJUDICATION = partial
        gaps = p11.arm_disclosure_gaps()
    finally:
        p11.ARM_PLACEMENT_ADJUDICATION = original

    assert gaps == ("`UNIVERSAL_L1` | 128, >=256 | " + p11.NOT_MET_TERMINAL,)


def test_the_terminal_is_a_function_of_which_registered_arm_was_carried_forward():
    axis = p11.arm_axis()

    assert axis.values == len(p11.REGISTERED_UNIVERSAL_ARMS)
    assert axis.varied
    assert not axis.inert
    assert axis.verdict_changing_pairs == 2
    assert axis.multiplier == 1


def test_part_of_the_published_gap_is_the_change_of_decoder_family():
    """P11G moves the representation and the learner at once; this splits them."""

    rows = p11.decoder_family_share()
    published = p11.shipped_receipt()["scientific_payload"]["cells"]

    assert [row["cell"] for row in rows] == [cell["cell"] for cell in published]
    for row, cell in zip(rows, published):
        assert row["published_gap_at_64"] == cell["compiled_minus_tree_at_64"]
        assert row["decoder_family_gap_at_64"] > 0.0
        assert row["representation_gap_at_64"] > 0.0
        assert row["decoder_family_share"] == pytest.approx(
            row["decoder_family_gap_at_64"] / row["published_gap_at_64"]
        )
    assert rows[0]["decoder_family_share"] < 0.20
    assert rows[1]["decoder_family_share"] > 0.40


def test_the_frozen_resource_envelope_is_not_what_loses_the_attack():
    """An 11x larger ensemble does not move the reading into reach.

    The record measures the same thing at 4,096 trees, a 43x ensemble, where
    ``n=64`` accuracy in the first cell moves from ``0.5376`` to ``0.5356``.
    1,024 is pinned here because it makes the same point for a third of the
    wall time, and a test nobody will wait for is a test that gets skipped.
    """

    base = p11.shipped_spec()
    bigger = replace(base, n_trees=1024)

    assert p11.terminal_of(bigger) == p11.SHIPPED_TERMINAL
    assert p11.gate_values(bigger)["tree_threshold_ge_256"] < 0.70


def test_an_admissible_world_must_say_why_the_freeze_admits_it():
    for world in p11.admissible_worlds():
        assert world.admits.strip()
        assert isinstance(world.payload, p11.AttackSpec)
        assert world.payload.arm == p11.REPORTED_ARM
        assert world.payload.n_trees == p11.p11g_module().N_TREES
        assert world.payload.max_features == "sqrt"
        assert world.payload.bank_columns is None


def test_a_world_outside_the_freeze_would_flip_the_verdict_to_reachable():
    """The register is the artifact a reviewer audits, in both directions.

    Registering one inadmissible bank as if the protocol permitted it turns the
    unconditional gate into a discriminating one, which widens the protocol
    instead of measuring it. Pinning that here is what makes the register above
    a claim rather than a convenience.
    """

    widened = p11.admissible_worlds() + (
        AdmissibleWorld(
            world_id="inadmissible-compiled-bank",
            admits="NOT admitted: the protocol pins the complete parity bank",
            payload=replace(p11.shipped_spec(), bank_columns=0),
        ),
    )
    gate = next(g for g in p11.GATES if g.gate_id == "delta64_ge_0_20")
    reach = measure_gate_attainability(
        lambda spec: p11.READINGS["delta64_ge_0_20"](p11.measure(spec)),
        gate=gate,
        worlds=widened,
    )

    assert reach.reason is GateReachReason.BOTH_OUTCOMES_REACHABLE
    assert reach.outcome is Outcome.PASS


def test_an_unregistered_arm_is_refused():
    with pytest.raises(ValueError, match="unregistered arm"):
        p11.AttackSpec(seed=1, arm="UNIVERSAL_TRANSFORMER")


def test_the_audit_blocks_on_attainability_and_reports_the_transplant_as_a_reading():
    """What rolls up, and what does not.

    The attainability verdict blocks and always did. The transplanted rule is
    retained verbatim and reported --- ``[128, 256]``, gate ``False`` --- and no
    longer rolls up, because :func:`rule_binding` reads it against a freeze that
    does not govern P11G. What rolls up in its place is stricter than a boolean
    about somebody else's rule: the record has to declare the axis.
    """

    report = audit_p11g_attack_terminal()

    assert report["scientific_sha256"] == p11.SHIPPED_SCIENTIFIC_SHA256
    assert report["curves_reproduced"] is True
    assert report["terminal_reach"].outcome is Outcome.FAIL
    assert report["responsiveness"].outcome is Outcome.PASS
    assert report["outcome"] is Outcome.FAIL

    assert report["transplanted_rule_gate"] is False
    assert report["best_of_arms_thresholds"] == (128, 256)
    assert report["rule_binding"].binds is False
    assert report["arm_disclosure_gaps"] == ()
    assert report["disclosure_outcome"] is Outcome.PASS
    assert len(report["one_value_decision_axes"]) == 1

    payload = report_as_json(report)
    assert json.loads(json.dumps(payload))["outcome"] == "FAIL"
    assert payload["best_of_arms_thresholds"] == [128, 256]
    assert payload["rule_binding"]["binds"] is False
    assert payload["disclosure_outcome"] == "PASS"


def test_the_audit_blocks_again_if_the_axis_declaration_disappears():
    """The guard is in the terminal decision path of the audit, not only in a test."""

    original = p11.ARM_PLACEMENT_ADJUDICATION
    try:
        p11.ARM_PLACEMENT_ADJUDICATION = original.with_name("does-not-exist.md")
        report = audit_p11g_attack_terminal()
        assert report["disclosure_outcome"] is Outcome.FAIL
        assert report["arm_disclosure_gaps"]
        assert report["outcome"] is Outcome.FAIL
    finally:
        p11.ARM_PLACEMENT_ADJUDICATION = original

    assert audit_p11g_attack_terminal()["disclosure_outcome"] is Outcome.PASS


def test_the_audit_cli_exits_three_and_renders():
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        code = main([])
    rendered = stream.getvalue()

    assert code == 3
    assert "reachable terminals: 1" in rendered
    assert p11.SHIPPED_SCIENTIFIC_SHA256 in rendered
    assert "P11C's best-of-arms rule does not bind P11G" in rendered
    assert "86.7% decoder / 13.3% state" not in rendered
    assert "13.3% decoder / 86.7% state" in rendered

    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        assert main(["--json"]) == 3
    payload = json.loads(stream.getvalue())
    assert payload["disclosure_outcome"] == "PASS"
    assert payload["rule_binding"]["binds"] is False


def test_the_paper_states_the_arm_dependence_in_its_own_prose():
    """Not only in an audit: the manuscript and the chapter have to carry it.

    An audit nobody publishes is not a disclosure. These are the two surfaces a
    reader of the paper actually sees.
    """

    manuscript = (p11.PAPER_DIR / "MANUSCRIPT.md").read_text(encoding="utf-8")
    chapter_path = (
        p11.PAPER_DIR / "manuscript/sections/05-hostile-decoder-substitution.md"
    )
    chapter = chapter_path.read_text(encoding="utf-8")

    # The chapter reaches the PDF through a two-line .tex shim, so the .md is the
    # published surface and not a second copy of it. Asserting the shim still
    # points here is what stops the two from forking into a file readers see and
    # a file this test reads -- and this assertion exists because the path above
    # was stale from the tree move in 4dc4f50 until 2026-08-22, so the test
    # raised FileNotFoundError rather than checking anything. The disclosure
    # survived that gap intact; nothing was enforcing that it would.
    shim = chapter_path.with_suffix(".tex").read_text(encoding="utf-8")
    assert f"\\markdownInput{{sections/{chapter_path.name}}}" in shim
    ledger = (p11.PAPER_DIR / "CLAIM_EVIDENCE_LEDGER.md").read_text(encoding="utf-8")

    for text in (manuscript, chapter):
        assert "UNIVERSAL_L1" in text
        assert "n=128" in text or "**128**" in text
        assert "P11G_ARM_PLACEMENT_ADJUDICATION_V1.md" in text
        # the decomposition, in both directions
        assert "+0.0614" in text and "+0.4010" in text
        assert "86.7%" in text and "55.4%" in text

    rows = [line for line in ledger.splitlines() if line.startswith("|")]
    assert not [row for row in rows if "HOSTILE NONLINEAR / PRIMARY" in row]
    assert [row for row in rows if "HOSTILE NONLINEAR / ARM-SCOPED" in row]
    assert [row for row in rows if "NOT AUTHORIZED" in row and "universal-state decoding" in row]
