"""Protocol is DESIGN_FROZEN with outcome_accessed false; V1 is not rewritten."""

from __future__ import annotations

from orion.study.p1_causal.hypotheses import COMPETING_HYPOTHESES, HypothesisId
from orion.study.p1_causal.protocol import (
    PROTOCOL_ID,
    load_protocol,
    protocol_sha256,
)


def test_protocol_frozen_before_outcomes() -> None:
    payload = load_protocol()
    assert payload["protocol_id"] == PROTOCOL_ID
    assert payload["protocol_status"] == "DESIGN_FROZEN"
    assert payload["outcome_accessed"] is False
    assert payload["v1_protocol_mutated"] is False
    assert payload["v1_results_mutated"] is False
    assert payload["execution_bindings"]["subject_revision"] == "UNBOUND"
    assert payload["statistics"]["practical_margin"]["responsibility_accuracy_superiority"] == 0.10
    digest = protocol_sha256()
    assert digest == "fd608b19080a23072ecad9b6f83194b75d6a6867657920698310f8c0d74148b6"


def test_hypotheses_h_r1_through_h_r6_frozen() -> None:
    assert [item.hypothesis_id for item in COMPETING_HYPOTHESES] == list(HypothesisId)
    confusable = {
        item.hypothesis_id.value: item.confusable_with for item in COMPETING_HYPOTHESES
    }
    assert HypothesisId.H_R2 in confusable[HypothesisId.H_R1.value]
