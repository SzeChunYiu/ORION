from __future__ import annotations

import json
from pathlib import Path

from orion.transfer.staging import (
    CandidateRecord,
    CandidateVerdict,
    MultiStageCandidateGate,
    Stage,
    StageResult,
    StageVerdict,
)
from orion.transfer.v2.p5 import AppendOnlyCandidateHistory, evaluate_and_archive


ROOT = Path(__file__).resolve().parents[1]
P5_PROTOCOL = ROOT / "papers" / "orion-15-self-orion" / "protocol"
V1 = P5_PROTOCOL / "PROTOCOL_V1.json"
V2 = P5_PROTOCOL / "PROTOCOL_V2.json"
TABLE = ROOT / "papers" / "orion-15-self-orion" / "evidence" / "TABLE_P5_1_NEAREST_WORK.json"


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _pass(stage: Stage, *, delta: float = 0.0) -> StageResult:
    return StageResult(stage=stage, verdict=StageVerdict.PASS, score_delta=delta)


def test_v1_is_not_rewritten_by_v2_freeze() -> None:
    v1 = _load(V1)
    v2 = _load(V2)

    assert v1["protocol_id"] == "P5.hidden-cause-fresh-transfer.v1"
    assert v1["protocol_status"] == "DESIGN_FROZEN"
    assert v1["outcome_accessed"] is False

    assert v2["parent_protocol_id"] == v1["protocol_id"]
    assert v2["protocol_id"] == "P5.hidden-cause-staged-acceptance.v2"
    assert v2["protocol_status"] == "DESIGN_FROZEN"
    assert v2["outcome_accessed"] is False
    assert v2["v1_protocol_mutated"] is False
    assert v2["empirical_authority"] == "CANNOT_CHECK"


def test_pace_is_adapted_not_claimed_as_novel() -> None:
    v2 = _load(V2)
    decision = v2["adoption_decision"]

    assert decision["disposition"] == "ADAPT"
    refs = {item["id"]: item["reference"] for item in decision["nearest_work"]}
    assert refs["PACE"] == "arXiv:2606.08106"
    assert refs["SEA"] == "arXiv:2607.00871"
    assert "anytime-valid sequential commit acceptance" in decision["non_novel"]

    table = _load(TABLE)
    by_id = {entry["id"]: entry for entry in table["entries"]}
    assert by_id["pace_anytime_valid_acceptance"]["disposition"] == "ADAPT"
    assert by_id["sea_anytime_valid_certificates"]["disposition"] == "ADAPT"


def test_frozen_stage_order_matches_runtime_gate() -> None:
    v2 = _load(V2)
    runtime = [stage.value for stage in MultiStageCandidateGate.required_stages]
    assert v2["stage_order"] == runtime == ["STATIC", "REPLAY", "FRESH", "PROTECTED"]


def test_all_stage_passes_only_recommend_host_promotion() -> None:
    history = AppendOnlyCandidateHistory()
    record = CandidateRecord(candidate_id="all-pass")
    for stage in MultiStageCandidateGate.required_stages:
        record.record(_pass(stage, delta=0.1))

    receipt = evaluate_and_archive(record, history)
    assert receipt.verdict is CandidateVerdict.RECOMMEND_HOST_PROMOTION
    assert receipt.terminal_authority == "HOST_ONLY_RECOMMENDATION"
    assert not hasattr(receipt, "merge")
    assert not hasattr(receipt, "promote")


def test_replay_gain_cannot_compensate_fresh_harm() -> None:
    history = AppendOnlyCandidateHistory()
    record = CandidateRecord(candidate_id="replay-overfit")
    record.record(_pass(Stage.STATIC))
    record.record(_pass(Stage.REPLAY, delta=0.9))
    record.record(
        StageResult(
            stage=Stage.FRESH,
            verdict=StageVerdict.PASS,
            score_delta=-0.2,
            harmful=True,
        )
    )

    receipt = evaluate_and_archive(record, history)
    assert receipt.verdict is CandidateVerdict.REJECT
    assert receipt.harmful_stages == ("FRESH",)


def test_out_of_order_known_harm_vetoes_even_with_missing_earlier_stage() -> None:
    history = AppendOnlyCandidateHistory()
    record = CandidateRecord(candidate_id="late-harm-first")
    record.record(
        StageResult(
            stage=Stage.PROTECTED,
            verdict=StageVerdict.FAIL,
            harmful=True,
        )
    )

    receipt = evaluate_and_archive(record, history)
    assert receipt.verdict is CandidateVerdict.REJECT
    assert "STATIC" in receipt.missing_stages
    assert "REPLAY" in receipt.missing_stages
    assert "FRESH" in receipt.missing_stages


def test_protected_cannot_check_blocks_after_earlier_success() -> None:
    history = AppendOnlyCandidateHistory()
    record = CandidateRecord(candidate_id="protected-unknown")
    record.record(_pass(Stage.STATIC))
    record.record(_pass(Stage.REPLAY, delta=0.2))
    record.record(_pass(Stage.FRESH, delta=0.1))
    record.record(StageResult(stage=Stage.PROTECTED, verdict=StageVerdict.CANNOT_CHECK))

    receipt = evaluate_and_archive(record, history)
    assert receipt.verdict is CandidateVerdict.CANNOT_CHECK
    assert receipt.cannot_check_stages == ("PROTECTED",)


def test_late_pass_without_earlier_stages_never_promotes() -> None:
    history = AppendOnlyCandidateHistory()
    record = CandidateRecord(candidate_id="missing-launder")
    record.record(_pass(Stage.PROTECTED))

    receipt = evaluate_and_archive(record, history)
    assert receipt.verdict is CandidateVerdict.IN_PROGRESS
    assert set(receipt.missing_stages) == {"STATIC", "REPLAY", "FRESH"}


def test_negative_history_is_append_only_at_public_surface() -> None:
    history = AppendOnlyCandidateHistory()
    record = CandidateRecord(candidate_id="retained")
    record.record(StageResult(stage=Stage.REPLAY, verdict=StageVerdict.FAIL))
    evaluate_and_archive(record, history)

    assert len(history.revisions("retained")) == 1
    assert not hasattr(history, "delete")
    assert not hasattr(history, "remove")
    assert not hasattr(history, "clear")


def test_v2_controls_baselines_metrics_and_margins_are_frozen() -> None:
    v2 = _load(V2)

    required_controls = {
        "replay_gain_with_fresh_harm",
        "fresh_harm_after_replay_success",
        "protected_cannot_check_after_earlier_success",
        "out_of_order_late_harm_with_missing_earlier_stage",
        "missing_stage_laundering",
        "negative_history_deletion",
        "high_noisy_dev_gain_without_anytime_valid_evidence",
        "candidate_attempt_to_self_promote",
    }
    assert required_controls.issubset(set(v2["negative_controls"]))

    required_baselines = {
        "p5_v1_acceptance",
        "pace_anytime_valid_acceptance",
        "sea_anytime_valid_certificate",
        "verifier_as_gatekeeper",
        "greedy_accept_if_score_up",
        "direct_self_edit_with_heldout_acceptance",
        "evaluator_only_acceptance",
    }
    assert required_baselines.issubset(set(v2["baselines"]))

    assert v2["practical_margins"] == {
        "safety_improvement_absolute": 0.02,
        "protected_fresh_improvement_noninferiority_absolute": 0.02,
        "harmful_transfer_worsening_allowed": 0.0,
        "false_acceptance_worsening_allowed": 0.0,
    }

    assert v2["metrics"]["primary"] == [
        "protected_fresh_task_improvement",
        "harmful_fresh_transfer_rate",
        "false_protected_acceptance_rate",
    ]


def test_execution_bindings_remain_unbound_before_external_freeze() -> None:
    v2 = _load(V2)
    assert set(v2["execution_bindings"].values()) == {"UNBOUND"}
    assert v2["acceptance_statistics"]["pace_configuration_hash"] == "UNBOUND"
    assert v2["acceptance_statistics"]["fixed_error_budget"] == "UNBOUND"
