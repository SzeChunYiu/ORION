"""P5.causal-repair.v2 acceptance doctrine scaffolding.

Replay gain cannot compensate fresh harm. Greedy replay-only cannot promote.
Missing fresh transfer blocks. Negative-history recurrence is checked.
The only positive terminal is host-only RECOMMEND_HOST_PROMOTION.
"""

from __future__ import annotations

import json
from pathlib import Path

from orion.study.p5.causal_repair import (
    PROTOCOL_ID,
    CausalRepairGate,
    CausalRepairRecord,
    CausalRepairStage,
    CausalRepairVerdict,
    ChangeClass,
    NegativeHistory,
    StageObservation,
    StageVerdict,
    live_campaign_preflight,
)


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "papers/orion-15-self-orion/protocol/PROTOCOL_CAUSAL_REPAIR_V2.json"
POLICY = ROOT / "papers/orion-15-self-orion/protocol/CAUSAL_REPAIR_POLICY_V2.md"
V1 = ROOT / "papers/orion-15-self-orion/protocol/PROTOCOL_V1.json"
V2 = ROOT / "papers/orion-15-self-orion/protocol/PROTOCOL_V2.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _pass(stage: CausalRepairStage, *, delta: float = 0.0) -> StageObservation:
    return StageObservation(stage=stage, verdict=StageVerdict.PASS, score_delta=delta)


def _complete_record(
    candidate_id: str,
    *,
    change_class: ChangeClass = ChangeClass.REPRESENTATION_REPAIR,
    fingerprint: str = "fp-rep-1",
    lower_causes_ruled_out: bool = True,
    discriminator_evidence_bound: bool = True,
) -> CausalRepairRecord:
    record = CausalRepairRecord(
        candidate_id=candidate_id,
        change_class=change_class,
        candidate_fingerprint=fingerprint,
        lower_causes_ruled_out=lower_causes_ruled_out,
        discriminator_evidence_bound=discriminator_evidence_bound,
    )
    for stage in CausalRepairGate.required_stages:
        record.record(_pass(stage, delta=0.1))
    return record


def test_causal_repair_protocol_is_additive_and_does_not_rewrite_v1_or_v2() -> None:
    v1 = _load(V1)
    v2 = _load(V2)
    protocol = _load(PROTOCOL)

    assert v1["protocol_id"] == "P5.hidden-cause-fresh-transfer.v1"
    assert v2["protocol_id"] == "P5.hidden-cause-staged-acceptance.v2"
    assert protocol["protocol_id"] == PROTOCOL_ID == "P5.causal-repair.v2"
    assert protocol["parent_protocol_id"] == v2["protocol_id"]
    assert protocol["v1_protocol_mutated"] is False
    assert protocol["v2_protocol_mutated"] is False
    assert protocol["outcome_accessed"] is False
    assert protocol["protocol_status"] == "DESIGN_FROZEN"
    assert protocol["empirical_authority"] == "CANNOT_CHECK"
    assert protocol["stage_order"] == [
        "STATIC",
        "DIAGNOSE",
        "DISCRIMINATE",
        "CANDIDATE",
        "REPLAY",
        "FRESH",
        "PROTECTED",
    ]
    assert protocol["global_decision_rules"]["terminal"] == "RECOMMEND_HOST_PROMOTION"
    assert protocol["global_decision_rules"]["self_merge_authority"] is False
    assert set(protocol["execution_bindings"].values()) == {"UNBOUND"}
    assert "replay_only" in protocol["ablations"]
    assert "greedy_accept_if_replay_score_rises" in protocol["ablations"]
    assert "no_negative_history_recurrence_check" in protocol["ablations"]
    text = POLICY.read_text(encoding="utf-8")
    assert "P5.causal-repair.v2" in text
    assert "RECOMMEND_HOST_PROMOTION" in text
    assert "never self-merge" in text.lower() or "never self-merges" in text.lower()


def test_greedy_replay_only_must_not_promote() -> None:
    gate = CausalRepairGate()
    history = NegativeHistory()
    record = CausalRepairRecord(
        candidate_id="greedy-replay",
        change_class=ChangeClass.IMPLEMENTATION_REPAIR,
        candidate_fingerprint="fp-greedy",
        discriminator_evidence_bound=True,
        greedy_replay_acceptance=True,
    )
    record.record(_pass(CausalRepairStage.STATIC))
    record.record(_pass(CausalRepairStage.DIAGNOSE))
    record.record(_pass(CausalRepairStage.DISCRIMINATE))
    record.record(_pass(CausalRepairStage.CANDIDATE))
    record.record(_pass(CausalRepairStage.REPLAY, delta=0.9))

    receipt = gate.evaluate(record, history)
    assert receipt.verdict is CausalRepairVerdict.BLOCK
    assert "greedy_replay_only" in receipt.blockers
    assert receipt.verdict is not CausalRepairVerdict.RECOMMEND_HOST_PROMOTION
    assert receipt.terminal_authority == "HOST_ONLY_RECOMMENDATION"
    assert not hasattr(receipt, "merge")
    assert not hasattr(receipt, "promote")


def test_missing_fresh_transfer_blocks() -> None:
    gate = CausalRepairGate()
    history = NegativeHistory()
    record = CausalRepairRecord(
        candidate_id="no-fresh",
        change_class=ChangeClass.IMPLEMENTATION_REPAIR,
        candidate_fingerprint="fp-no-fresh",
        discriminator_evidence_bound=True,
    )
    for stage in (
        CausalRepairStage.STATIC,
        CausalRepairStage.DIAGNOSE,
        CausalRepairStage.DISCRIMINATE,
        CausalRepairStage.CANDIDATE,
        CausalRepairStage.REPLAY,
        CausalRepairStage.PROTECTED,
    ):
        record.record(_pass(stage, delta=0.2))

    receipt = gate.evaluate(record, history)
    assert receipt.verdict is CausalRepairVerdict.BLOCK
    assert "missing_fresh_transfer" in receipt.blockers
    assert "FRESH" in receipt.missing_stages


def test_negative_history_recurrence_blocks_repeat_harmful_fingerprint() -> None:
    gate = CausalRepairGate()
    history = NegativeHistory()
    rejected = CausalRepairRecord(
        candidate_id="harm-v1",
        change_class=ChangeClass.METHOD_BASIS_CHANGE,
        candidate_fingerprint="fp-recurring",
        discriminator_evidence_bound=True,
        lower_causes_ruled_out=True,
    )
    rejected.record(
        StageObservation(
            stage=CausalRepairStage.FRESH,
            verdict=StageVerdict.FAIL,
            score_delta=-0.4,
            harmful=True,
        )
    )
    first = gate.evaluate(rejected, history)
    assert first.verdict is CausalRepairVerdict.REJECT
    assert history.contains_fingerprint("fp-recurring")

    repeat = _complete_record("harm-v2", fingerprint="fp-recurring")
    second = gate.evaluate(repeat, history)
    assert second.verdict is CausalRepairVerdict.BLOCK
    assert "negative_history_recurrence" in second.blockers


def test_replay_gain_cannot_compensate_fresh_harm() -> None:
    gate = CausalRepairGate()
    history = NegativeHistory()
    record = CausalRepairRecord(
        candidate_id="replay-overfit",
        change_class=ChangeClass.RETRIEVAL_ROUTING_REPAIR,
        candidate_fingerprint="fp-overfit",
        discriminator_evidence_bound=True,
    )
    record.record(_pass(CausalRepairStage.STATIC))
    record.record(_pass(CausalRepairStage.DIAGNOSE))
    record.record(_pass(CausalRepairStage.DISCRIMINATE))
    record.record(_pass(CausalRepairStage.CANDIDATE))
    record.record(_pass(CausalRepairStage.REPLAY, delta=0.8))
    record.record(
        StageObservation(
            stage=CausalRepairStage.FRESH,
            verdict=StageVerdict.PASS,
            score_delta=-0.3,
            harmful=True,
        )
    )
    record.record(_pass(CausalRepairStage.PROTECTED, delta=0.1))

    receipt = gate.evaluate(record, history)
    assert receipt.verdict is CausalRepairVerdict.REJECT
    assert "FRESH" in receipt.harmful_stages


def test_method_basis_change_without_ruling_out_lower_causes_is_blocked() -> None:
    gate = CausalRepairGate()
    history = NegativeHistory()
    record = _complete_record(
        "broad-rewrite",
        change_class=ChangeClass.METHOD_BASIS_CHANGE,
        fingerprint="fp-method",
        lower_causes_ruled_out=False,
    )
    receipt = gate.evaluate(record, history)
    assert receipt.verdict is CausalRepairVerdict.BLOCK
    assert "lower_causes_not_ruled_out" in receipt.blockers


def test_complete_protected_cycle_only_recommends_host_promotion() -> None:
    gate = CausalRepairGate()
    history = NegativeHistory()
    record = _complete_record("all-pass")
    receipt = gate.evaluate(record, history)
    assert receipt.verdict is CausalRepairVerdict.RECOMMEND_HOST_PROMOTION
    assert receipt.terminal_authority == "HOST_ONLY_RECOMMENDATION"
    assert receipt.self_merge_authority is False
    assert history.contains_fingerprint("fp-rep-1") is False


def test_live_campaign_without_credentials_is_cannot_check(monkeypatch) -> None:
    monkeypatch.delenv("GLM_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    status = live_campaign_preflight()
    assert status["status"] == "CANNOT_CHECK"
    assert status["authority"] == "CANNOT_CHECK"
    assert "GLM_API_KEY" not in str(status.values())


def test_unbound_fresh_split_identities_remain_cannot_check_until_host_freeze() -> None:
    protocol = _load(PROTOCOL)
    splits = protocol["fresh_transfer_split_identities"]
    assert splits["motivating_split_hash"] == "UNBOUND"
    assert splits["replay_split_hash"] == "UNBOUND"
    assert splits["fresh_split_hash"] == "UNBOUND"
    assert splits["protected_split_hash"] == "UNBOUND"
    assert splits["fresh_axis_requirement"] == "at_least_one_of_task_domain_model_environment"
