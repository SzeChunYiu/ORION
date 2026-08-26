"""P14C's published positive, asked what P14A's negative could not be asked.

Every number pinned here was read off the shipped artifacts
``papers/paper-14-orion-rse/P14C_ADJUDICATION_CASES_V1.json``,
``run_p14c_specification_separated_governance_v1.py``,
``P14C_SPECIFICATION_SEPARATED_RESULT_RECEIPT_V1.json`` and
``P14C_PROTOCOL_ADJUDICATION_V2.json``, or produced by driving that runner's own
``full_policy``, ``ablated``, ``facts_only`` and ``score``.
"""

from __future__ import annotations

import contextlib
import io

import pytest

from orion.programme.gate_attainability import (
    GateReachReason,
    GateRole,
    UnattainableGate,
    require_reachable,
    require_supported_thresholds,
)
from orion.programme.records import Outcome
from orion.study.p14 import governance_gates as p14a
from orion.study.p14 import specification_conformance as p14c


def literal_gates(summary: dict) -> dict[str, bool]:
    """``main()``'s eight gate expressions, transcribed character for character.

    :data:`p14c.GATES` reads counts and rates where the runner writes booleans;
    this is the check that the two agree, so an attainability verdict below is
    about P14C's thresholds and not about a paraphrase of them.
    """

    module = p14c.runner_module()
    cases = list(p14c.frozen_cases())
    strongest = max(p14c.BASELINE_ARMS, key=lambda a: float(summary[a]["disposition_accuracy"]))
    full = summary["ORION_RSE_FULL"]
    return {
        "full_accuracy_one": full["disposition_accuracy"] == 1.0,
        "full_zero_false_promotion": full["false_promotion_rate"] == 0.0,
        "full_discovery_recall_one": full["useful_discovery_recall"] == 1.0,
        "retain_and_reopen_exact": full["retain_negative_accuracy"] == 1.0
        and full["supported_reopen_accuracy"] == 1.0,
        "strongest_baseline_false_promotion_ge_0_10": summary[strongest]["false_promotion_rate"]
        >= 0.10,
        "accuracy_advantage_ge_0_10": full["disposition_accuracy"]
        - summary[strongest]["disposition_accuracy"]
        >= 0.10,
        "every_ablation_worse": all(
            summary[a]["disposition_accuracy"] < full["disposition_accuracy"]
            for a in p14c.ABLATION_ARMS
        ),
        "gold_stripped_from_policy_input": all(
            "gold_disposition" not in module.facts_only(dict(c)) for c in cases
        ),
    }


def test_the_bench_reproduces_the_committed_canonical_digest() -> None:
    """The fidelity anchor: a failure below is about P14C, not about a local fixture."""

    result = p14c.shipped_bench()
    receipt = p14c.shipped_receipt()
    adjudication = p14c.shipped_adjudication()

    assert result["result_sha256"] == p14c.SHIPPED_RESULT_DIGEST
    assert receipt["canonical_sha256"] == p14c.SHIPPED_RESULT_DIGEST
    assert adjudication["scientific_payload_sha256_run_a"] == p14c.SHIPPED_RESULT_DIGEST
    assert adjudication["scientific_payload_sha256_run_b"] == p14c.SHIPPED_RESULT_DIGEST
    assert result["terminal"] == p14c.SHIPPED_TERMINAL == receipt["terminal"]
    assert result["strongest_non_orion_baseline"] == receipt["strongest_non_orion_baseline"]
    for arm, published in receipt["summary"].items():
        for key, value in published.items():
            assert result["summary"][arm][key] == pytest.approx(value), (arm, key)


def test_the_registered_gates_are_the_runners_own_expressions() -> None:
    for world in p14c.subject_worlds():
        result = p14c.bench(world.payload)
        assert result["gates"] == literal_gates(result["summary"]), world.world_id


def test_the_separation_is_one_stratum_and_the_table_fixes_its_share() -> None:
    """P14A left this share to a Bernoulli mixture; P14C writes it into the table."""

    counts = p14c.arm_error_counts()

    assert len(p14c.frozen_cases()) == 28
    assert counts == {
        "RAW_POSITIVE": 16,
        "REFLECTION_CHECKLIST": 12,
        "DONOR_AWARE_REVIEW": 8,
        "MULTI_REVIEW": 4,
        "ORION_RSE_FULL": 0,
        "ABLATE_EVIDENCE_INTEGRITY": 1,
        "ABLATE_FREEZE": 1,
        "ABLATE_IDENTIFIABILITY": 1,
        "ABLATE_DONOR": 4,
        "ABLATE_INTERACTION": 4,
        "ABLATE_NEGATIVE_HISTORY": 4,
    }
    assert p14c.discriminating_stratum_share() == pytest.approx(4 / 28)
    assert counts["MULTI_REVIEW"] / 28 == pytest.approx(p14c.discriminating_stratum_share())


def test_the_successor_makes_the_same_quantity_three_times_p14as_ceiling() -> None:
    """The whole difference between the two benchmarks, in one comparison."""

    share = p14c.discriminating_stratum_share()

    assert share == pytest.approx(0.14285714285714285)
    assert p14a.discriminator_supremum() == pytest.approx(0.04232587750858594)
    assert share > p14a.discriminator_supremum()
    assert share > 0.05
    assert share > 0.08


def test_the_terminal_could_have_been_the_other_word() -> None:
    """The property P14A's conjunction did not have, measured the same way."""

    terminal = p14c.terminal_reach()

    assert len(terminal.world_ids) == 7
    assert terminal.clearing == ("full-contract",)
    assert terminal.distinct_terminals == 2
    assert terminal.outcome is Outcome.PASS
    assert terminal.unattainable == ()
    require_reachable(terminal)


def test_only_the_full_contract_clears_every_gate() -> None:
    for subject in p14c.SUBJECT_IMPLEMENTATIONS:
        result = p14c.bench(subject)
        expected = (
            p14c.SHIPPED_TERMINAL if subject == p14c.SUBJECT_SLOT else p14c.NEGATIVE_TERMINAL
        )
        assert result["terminal"] == expected, subject


def test_every_registered_subject_is_one_the_protocol_admits() -> None:
    """The register is the artifact a reviewer audits, so it has to be auditable."""

    registered = {world.payload for world in p14c.subject_worlds()}

    assert registered == set(p14c.SUBJECT_IMPLEMENTATIONS)
    assert registered == {p14c.SUBJECT_SLOT} | set(p14c.ABLATED_FACT)
    for world in p14c.subject_worlds():
        assert world.admits.strip()


def test_the_superiority_gate_can_still_fail_and_the_difficulty_gate_cannot() -> None:
    """The asymmetry roles exist for: a claim must discriminate, a certificate may not."""

    reaches = {reach.gate.gate_id: reach for reach in p14c.gate_reaches()}

    advantage = reaches["accuracy_advantage_ge_0_10"]
    assert advantage.gate.role is GateRole.HYPOTHESIS
    assert advantage.reason is GateReachReason.BOTH_OUTCOMES_REACHABLE
    assert advantage.outcome is Outcome.PASS
    assert set(advantage.refuting) == {
        "ablate-donor",
        "ablate-interaction",
        "ablate-negative-history",
    }
    assert advantage.best_value == pytest.approx(4 / 28)
    assert advantage.attainment_margin == pytest.approx(4 / 28 - 0.10)

    difficulty = reaches["strongest_baseline_false_promotion_ge_0_10"]
    assert difficulty.gate.role is GateRole.PRECONDITION
    assert difficulty.reason is GateReachReason.THRESHOLD_UNCONDITIONAL
    assert difficulty.outcome is Outcome.PASS


def test_one_hypothesis_gate_has_no_registered_subject_that_can_fail_it() -> None:
    """Reported, not hidden: an ablation removes a check, so none of them abstains."""

    assert p14c.unexercised_hypothesis_gates() == ("full_discovery_recall_one",)
    recall = next(
        reach
        for reach in p14c.gate_reaches()
        if reach.gate.gate_id == "full_discovery_recall_one"
    )
    assert recall.reason is GateReachReason.THRESHOLD_UNCONDITIONAL
    assert recall.outcome is Outcome.FAIL
    assert p14c.terminal_reach().distinct_terminals == 2


def test_p14cs_own_thresholds_were_inside_reach_before_the_run() -> None:
    panel = p14c.threshold_panel()

    assert panel.outcome is Outcome.PASS
    assert panel.unattainable == ()
    assert panel.unconditional_hypotheses == ()
    assert panel.discriminating == ("accuracy_advantage_ge_0_10",)
    require_supported_thresholds(panel)


def test_p14as_frozen_thresholds_are_reachable_here_and_are_met() -> None:
    """The resolution: the same bars, unedited, on an instrument that can move them."""

    inherited = {gate.gate_id for gate in p14c.INHERITED_GATES}
    assert inherited == {"strongest_baseline_false_promotion_ge_0_05", "accuracy_gain_ge_0_08"}
    assert p14c.INHERITED_GATES == tuple(
        gate for gate in p14a.GATES if gate.gate_id in set(p14a.SUPPORT_BOUNDED_GATES)
    )
    assert {gate.gate_id: gate.threshold for gate in p14c.INHERITED_GATES} == {
        "strongest_baseline_false_promotion_ge_0_05": 0.05,
        "accuracy_gain_ge_0_08": 0.08,
    }

    panel = p14c.inherited_threshold_panel()
    assert panel.outcome is Outcome.PASS
    assert panel.unattainable == ()
    assert panel.discriminating == ("accuracy_gain_ge_0_08",)
    require_supported_thresholds(panel)

    assert p14c.inherited_reading() == {
        "strongest_baseline_false_promotion_ge_0_05": pytest.approx(4 / 28),
        "accuracy_gain_ge_0_08": pytest.approx(4 / 28),
    }
    assert p14c.inherited_gates_met() == {
        "strongest_baseline_false_promotion_ge_0_05": True,
        "accuracy_gain_ge_0_08": True,
    }


def test_the_same_two_thresholds_are_unreachable_on_p14as_own_benchmark() -> None:
    """The pair is the finding: unmeasurable there, met here, with nothing edited."""

    before = p14a.threshold_panel()
    after = p14c.inherited_threshold_panel()

    assert before.outcome is Outcome.FAIL
    assert before.unattainable == (
        "strongest_baseline_false_promotion_ge_0_05",
        "accuracy_gain_ge_0_08",
    )
    assert after.outcome is Outcome.PASS
    with pytest.raises(UnattainableGate):
        require_supported_thresholds(before)
    require_supported_thresholds(after)


def test_the_inherited_gates_discriminate_across_subjects_here() -> None:
    reaches = {reach.gate.gate_id: reach for reach in p14c.inherited_gate_reaches()}

    gain = reaches["accuracy_gain_ge_0_08"]
    assert gain.reason is GateReachReason.BOTH_OUTCOMES_REACHABLE
    assert set(gain.satisfying) == {
        "full-contract",
        "ablate-evidence-integrity",
        "ablate-freeze",
        "ablate-identifiability",
    }
    assert set(gain.refuting) == {"ablate-donor", "ablate-interaction", "ablate-negative-history"}


def test_the_audit_passes_and_names_what_it_did_not_establish() -> None:
    report = p14c.audit_p14c_conformance_terminal()
    payload = p14c.report_as_json(report)

    assert report["digest_reproduced"] is True
    assert report["outcome"] is Outcome.PASS
    assert report["inherited_outcome"] is Outcome.PASS
    assert payload["terminal_reach"]["distinct_terminals"] == 2
    assert payload["unexercised_hypothesis_gates"] == ["full_discovery_recall_one"]
    assert payload["discriminating_stratum_share"] == pytest.approx(4 / 28)
    assert payload["p14a_discriminator_supremum"] == pytest.approx(0.04232587750858594)


def test_the_audit_exits_zero_and_prints_both_thresholds() -> None:
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        code = p14c.main([])
    text = stream.getvalue()

    assert code == 0
    assert "reachable terminals: 2" in text
    assert "strongest_baseline_false_promotion_ge_0_05" in text
    assert "accuracy_gain_ge_0_08" in text
    assert "MET" in text

    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        assert p14c.main(["--json"]) == 0
    assert '"outcome": "PASS"' in stream.getvalue()


# --- the shipped adjudication receipt, bound to the instruments that produced it ---


ADJUDICATION = (
    p14c.PAPER / "P14_GATE_ATTAINABILITY_ADJUDICATION_V1.json"
)


def adjudication() -> dict:
    import json

    return json.loads(ADJUDICATION.read_text(encoding="utf-8"))


def test_the_paper_ships_the_adjudication_and_it_reaches_its_positive_terminal() -> None:
    receipt = adjudication()

    assert receipt["schema"] == "ORION.P14.GateAttainabilityAdjudication.v1"
    assert receipt["terminal"] == (
        "P14A_SUPERIORITY_GATES_UNMEASURABLE__"
        "QUESTION_ANSWERED_BY_P14C_AT_UNCHANGED_THRESHOLDS"
    )
    assert all(receipt["gates"].values())
    assert receipt["edits_no_frozen_result"] is True


def test_the_receipts_numbers_are_the_instruments_numbers() -> None:
    """A committed receipt that has drifted from the instrument is a claim nobody checks."""

    receipt = adjudication()

    assert receipt["p14a"]["terminal_retained_verbatim"] == p14a.SHIPPED_TERMINAL
    assert receipt["p14a"]["full_result_sha256"] == p14a.SHIPPED_RESULT_DIGEST
    assert receipt["p14a"]["evidential_disposition"] == "CANNOT_CHECK"
    assert receipt["p14a"]["declared_statistic_support"]["supremum"] == pytest.approx(
        p14a.discriminator_supremum()
    )
    assert set(receipt["p14a"]["failed_gates"]) == set(p14a.SUPPORT_BOUNDED_GATES)
    for gate_id, entry in receipt["p14a"]["failed_gates"].items():
        assert entry["reason"] == "THRESHOLD_UNATTAINABLE", gate_id
        assert entry["satisfying_worlds"] == [], gate_id
        assert entry["attainment_margin"] < 0.0, gate_id

    assert receipt["p14c"]["canonical_sha256"] == p14c.SHIPPED_RESULT_DIGEST
    assert receipt["p14c"]["terminal_reach"]["distinct_terminals"] == 2
    assert receipt["p14c"]["discriminating_stratum_share"] == pytest.approx(
        p14c.discriminating_stratum_share()
    )
    assert receipt["p14c"]["hypothesis_gates_without_refutation_capacity"] == list(
        p14c.unexercised_hypothesis_gates()
    )

    inherited = receipt["inherited_p14a_thresholds_on_p14c"]
    assert inherited["thresholds_unchanged"] == {
        gate.gate_id: gate.threshold for gate in p14c.INHERITED_GATES
    }
    assert inherited["met"] == p14c.inherited_gates_met()
    assert all(inherited["met"].values())


def test_p14as_frozen_receipt_is_untouched_by_the_adjudication() -> None:
    """The rule the whole exercise is bound by: a protected negative is not edited."""

    import json

    published = json.loads(
        (p14c.PAPER / "P14A_CONTROLLED_GOVERNANCE_RESULT_RECEIPT_V1.json").read_text(
            encoding="utf-8"
        )
    )
    closure = json.loads(
        (
            p14c.PAPER
            / "top_tier"
            / "P14A_CLOSURE_BY_SUCCESSOR_VERIFICATION_V1.json"
        ).read_text(encoding="utf-8")
    )

    assert published["terminal"] == "P14A_CONTROLLED_GOVERNANCE_SUPERIORITY_GATE_NOT_MET"
    assert published["seed"] == 2026082114
    assert published["full_result_sha256"] == p14a.SHIPPED_RESULT_DIGEST
    assert published["gates"]["strongest_baseline_false_promotion_ge_0_05"] is False
    assert published["gates"]["accuracy_gain_ge_0_08"] is False
    assert published["summary"]["MULTI_REVIEW"]["false_promotion_rate"] == 0.018375
    assert p14a.shipped_bench()["result_sha256"] in {
        closure["p14a_bar_vs_supremum"]["replay"]["sha256"],
        published["full_result_sha256"],
    }
    assert closure["checks"]["p14a_receipt_numbers_reproduce"] is True
    assert closure["verdicts"]["p14a_full_result_digest_platform_pinned"] is True
