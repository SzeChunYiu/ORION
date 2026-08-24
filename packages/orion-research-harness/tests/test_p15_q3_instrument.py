import json
from dataclasses import replace

import pytest

from orion_research_harness.cli import main
from orion_research_harness.frontier_benchmark import (
    DeferredAlignment,
    FrontierDecisionItem,
    FrontierDeferredScore,
    FrontierInstrumentDecision,
)
from orion_research_harness.p15_q3_instrument import (
    P15Q3InstrumentReceipt,
    receipt_from_mapping,
)
from orion_research_harness.protocol import content_digest
from orion_research_harness.scientific_execution_integrity import (
    ScientificDisposition,
    ScientificExecutionRecord,
)


def execution(**updates):
    raw = {
        "record_id": "P15-CASE-001",
        "spawn_ok": True,
        "host_ok": True,
        "timeout": False,
        "exit_zero": True,
        "output_present": True,
        "output_complete": True,
        "reaped": True,
        "finalized_after_reap": True,
        "cleanup_complete": True,
        "retry_accounting_valid": True,
        "invocation_match": True,
        "input_digest_match": True,
        "result_digest_match": True,
        "occurrence_unique": True,
        "fresh": True,
        "coverage_complete": True,
        "scientific_contract_available": True,
        "scientific_contract_valid": True,
        "claim_authority_available": True,
        "claim_authority": True,
    }
    raw.update(updates)
    return ScientificExecutionRecord.from_mapping(raw)


def frontier():
    item = FrontierDecisionItem.create(
        item_id="Q3-I1", programme_id="Q3", question="Which move is licensed?",
        evidence_digest="e" * 64, admissible_evidence=("E1",),
        diagnosis_coordinates=("D1", "D2"), move_coordinates=("M1", "M2"),
        deferred_scoring_rule="frozen-rule", freeze_epoch="2026-08-24T00:00:00Z",
    )
    left = FrontierInstrumentDecision.create(
        item=item, instrument_id="lane-a", diagnosis=("D1",), move=("M1",),
        decision_epoch="2026-08-24T01:00:00Z",
    )
    right = FrontierInstrumentDecision.create(
        item=item, instrument_id="lane-b", diagnosis=("D1",), move=("M1",),
        decision_epoch="2026-08-24T01:01:00Z",
    )
    score = FrontierDeferredScore.create(
        item=item, decision=left, resolving_evidence_digest="a" * 64,
        alignment=DeferredAlignment.ALIGNED, resolution_epoch="2026-08-24T02:00:00Z",
    )
    return item, left, right, score


def _plain(obj, names):
    return {
        name: (
            getattr(obj, name).value
            if hasattr(getattr(obj, name), "value")
            else list(getattr(obj, name))
            if isinstance(getattr(obj, name), tuple)
            else getattr(obj, name)
        )
        for name in names
    }


def payload():
    record = execution()
    item, left, right, score = frontier()
    item_names = (
        "schema", "item_id", "programme_id", "question", "evidence_digest",
        "admissible_evidence", "diagnosis_coordinates", "move_coordinates",
        "deferred_scoring_rule", "outcome_unknown_at_freeze", "freeze_epoch", "item_digest",
    )
    decision_names = (
        "schema", "item_digest", "instrument_id", "evidence_digest", "diagnosis", "move",
        "cannot_check", "decision_epoch", "decision_digest",
    )
    score_names = (
        "schema", "item_digest", "decision_digest", "resolving_evidence_digest", "alignment",
        "scorer_rule", "resolution_epoch", "score_digest",
    )
    return {
        "execution": record.as_dict(),
        "item": _plain(item, item_names),
        "decisions": [_plain(left, decision_names), _plain(right, decision_names)],
        "scores": [_plain(score, score_names)],
    }


def test_sei_preserves_all_negative_and_cannot_check_boundaries():
    assert execution(timeout=True).disposition() is ScientificDisposition.EXECUTION_INVALID
    assert (
        execution(scientific_contract_available=False).disposition()
        is ScientificDisposition.CANNOT_CHECK
    )
    assert (
        execution(scientific_contract_valid=False).disposition()
        is ScientificDisposition.DECLARED_INVALID_SCIENCE
    )
    assert (
        execution(claim_authority_available=False).disposition()
        is ScientificDisposition.CANNOT_CHECK
    )
    assert (
        execution(claim_authority=False).disposition()
        is ScientificDisposition.DECLARED_VALID_BUT_NOT_AUTHORIZED
    )


def test_sei_rejects_coercion_and_unknown_fields():
    raw = execution().as_dict()
    raw["fresh"] = "true"
    with pytest.raises(TypeError, match="fresh must be a boolean"):
        ScientificExecutionRecord.from_mapping(raw)
    raw = execution().as_dict()
    raw["independently_verified"] = True
    with pytest.raises(ValueError, match="fields must be exact"):
        ScientificExecutionRecord.from_mapping(raw)


def test_shared_receipt_binds_both_instruments_and_never_grants_authority():
    record = execution()
    item, left, right, score = frontier()
    receipt = P15Q3InstrumentReceipt.create(
        execution=record, item=item, decisions=(left, right), deferred_scores=(score,)
    )
    assert receipt.execution_disposition == "DECLARED_AUTHORIZED_SCIENCE"
    assert receipt.execution_content_digest
    assert receipt.frontier_relation.value == "AGREE"
    assert receipt.as_dict()["grants_scientific_authority"] is False
    assert receipt.as_dict()["grants_independent_authority"] is False
    assert receipt.as_dict()["independent_authority"] == "CANNOT_CHECK"
    assert receipt.as_dict()["public_data_confers_custody"] is False


def test_execution_content_digest_prevents_same_id_disposition_collision():
    item, left, right, _ = frontier()
    first = execution(scientific_contract_valid=False, claim_authority=False)
    second = execution(scientific_contract_valid=False, claim_authority=True)
    first_receipt = P15Q3InstrumentReceipt.create(
        execution=first, item=item, decisions=(left, right)
    )
    second_receipt = P15Q3InstrumentReceipt.create(
        execution=second, item=item, decisions=(left, right)
    )
    assert first_receipt.execution_record_id == second_receipt.execution_record_id
    assert first_receipt.execution_disposition == second_receipt.execution_disposition
    assert first_receipt.execution_content_digest != second_receipt.execution_content_digest
    assert first_receipt.receipt_digest != second_receipt.receipt_digest


def test_receipt_validation_rejects_forged_fields():
    item, left, right, _ = frontier()
    receipt = P15Q3InstrumentReceipt.create(
        execution=execution(), item=item, decisions=(left, right)
    )
    with pytest.raises(ValueError, match="declared P15 disposition"):
        replace(receipt, execution_disposition="AUTHORIZED_SCIENCE").validate()
    with pytest.raises(ValueError, match="exact lowercase SHA-256"):
        replace(receipt, execution_content_digest="not-a-digest").validate()


def test_declared_inputs_never_emit_unqualified_authority_label():
    disposition = execution().disposition().value
    assert disposition == "DECLARED_AUTHORIZED_SCIENCE"
    assert disposition != "AUTHORIZED_SCIENCE"


def test_shared_receipt_revalidates_direct_execution_dataclass_inputs():
    item, left, right, _ = frontier()
    malformed = replace(execution(), fresh="true")
    with pytest.raises(TypeError, match="fresh must be a boolean"):
        P15Q3InstrumentReceipt.create(
            execution=malformed, item=item, decisions=(left, right)
        )


def test_shared_receipt_revalidates_direct_frontier_boolean_inputs():
    item, left, right, _ = frontier()
    malformed = replace(
        left, cannot_check="false", diagnosis=(), move=(), decision_digest=""
    )
    malformed = replace(malformed, decision_digest=content_digest(malformed.unsigned()))
    with pytest.raises(TypeError, match="cannot_check must be a boolean"):
        P15Q3InstrumentReceipt.create(
            execution=execution(), item=item, decisions=(malformed, right)
        )


def test_resolution_must_follow_both_frozen_decisions():
    item, left, _, score = frontier()
    later_right = FrontierInstrumentDecision.create(
        item=item, instrument_id="lane-b", diagnosis=("D1",), move=("M1",),
        decision_epoch="2026-08-24T03:00:00Z",
    )
    with pytest.raises(ValueError, match="after both decision epochs"):
        P15Q3InstrumentReceipt.create(
            execution=execution(), item=item, decisions=(left, later_right),
            deferred_scores=(score,),
        )


def test_shared_receipt_rejects_posthoc_coordinates_and_time_order():
    item, left, right, _ = frontier()
    out_of_vocabulary = FrontierInstrumentDecision.create(
        item=item, instrument_id="lane-c", diagnosis=("POSTHOC",), move=("M1",),
        decision_epoch="2026-08-24T01:02:00Z",
    )
    with pytest.raises(ValueError, match="out-of-vocabulary diagnosis"):
        P15Q3InstrumentReceipt.create(
            execution=execution(), item=item, decisions=(left, out_of_vocabulary)
        )
    before_freeze = FrontierInstrumentDecision.create(
        item=item, instrument_id="lane-c", diagnosis=("D1",), move=("M1",),
        decision_epoch="2026-08-23T23:59:00Z",
    )
    with pytest.raises(ValueError, match="after the frozen item epoch"):
        P15Q3InstrumentReceipt.create(
            execution=execution(), item=item, decisions=(left, before_freeze)
        )


def test_shared_receipt_rejects_bad_digests_and_conflicting_scores():
    item, left, right, score = frontier()
    bad_item = FrontierDecisionItem.create(
        item_id="Q3-I2", programme_id="Q3", question="Which move?",
        evidence_digest="not-sha256", admissible_evidence=("E1",),
        diagnosis_coordinates=("D1",), move_coordinates=("M1",),
        deferred_scoring_rule="frozen-rule", freeze_epoch="2026-08-24T00:00:00Z",
    )
    bad_left = FrontierInstrumentDecision.create(
        item=bad_item, instrument_id="a", diagnosis=("D1",), move=("M1",),
        decision_epoch="2026-08-24T01:00:00Z",
    )
    bad_right = FrontierInstrumentDecision.create(
        item=bad_item, instrument_id="b", diagnosis=("D1",), move=("M1",),
        decision_epoch="2026-08-24T01:01:00Z",
    )
    with pytest.raises(ValueError, match="item evidence_digest"):
        P15Q3InstrumentReceipt.create(
            execution=execution(), item=bad_item, decisions=(bad_left, bad_right)
        )
    with pytest.raises(ValueError, match="at most one deferred score"):
        P15Q3InstrumentReceipt.create(
            execution=execution(), item=item, decisions=(left, right),
            deferred_scores=(score, score),
        )
    other_score = FrontierDeferredScore.create(
        item=item, decision=right, resolving_evidence_digest="b" * 64,
        alignment=DeferredAlignment.MISALIGNED,
        resolution_epoch="2026-08-24T02:01:00Z",
    )
    with pytest.raises(ValueError, match="common resolving evidence"):
        P15Q3InstrumentReceipt.create(
            execution=execution(), item=item, decisions=(left, right),
            deferred_scores=(score, other_score),
        )


def test_shared_receipt_rejects_identity_and_digest_mismatch():
    raw = payload()
    raw["decisions"][1]["instrument_id"] = "lane-a"
    with pytest.raises(ValueError, match="identities must be distinct"):
        receipt_from_mapping(raw)
    raw = payload()
    raw["item"]["item_digest"] = "0" * 64
    with pytest.raises(ValueError, match="item digest mismatch"):
        receipt_from_mapping(raw)


def test_cli_parser_rejects_extra_fields_and_string_booleans():
    raw = payload()
    raw["item"]["outcome_unknown_at_freeze"] = "true"
    with pytest.raises(TypeError, match="outcome_unknown_at_freeze must be a boolean"):
        receipt_from_mapping(raw)
    raw = payload()
    raw["decisions"][0]["grants_authority"] = False
    with pytest.raises(ValueError, match="decision fields must be exact"):
        receipt_from_mapping(raw)


def test_cli_emits_the_same_content_bound_receipt(tmp_path, capsys):
    path = tmp_path / "input.json"
    path.write_text(json.dumps(payload()))
    assert main(["instrument-receipt", str(path)]) == 0
    emitted = json.loads(capsys.readouterr().out)
    expected = receipt_from_mapping(payload()).as_dict()
    assert emitted == expected
