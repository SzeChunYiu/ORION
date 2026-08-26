"""Frozen adjacent-level discriminators for the three GLM-5.2 attribution errors.

A discriminator produces immutable evidence and an updated cause state. It does
not itself authorize a method change.
"""

from __future__ import annotations

import json
from pathlib import Path

from orion.study.p5.discriminators import (
    DISCRIMINATOR_PROTOCOL_ID,
    load_frozen_discriminators,
    validate_discriminator_freeze,
)


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "papers/orion-15-self-orion/protocol/P5_CAUSAL_DISCRIMINATORS_V1.json"


def test_three_error_discriminators_are_frozen_before_repair() -> None:
    freeze = load_frozen_discriminators(ARTIFACT)
    validate_discriminator_freeze(freeze)

    assert freeze["protocol_id"] == DISCRIMINATOR_PROTOCOL_ID
    assert freeze["outcome_accessed"] is False
    assert freeze["authorizes_method_change"] is False
    assert freeze["empirical_authority"] == "CANNOT_CHECK"
    by_id = {entry["error_id"]: entry for entry in freeze["discriminators"]}
    assert set(by_id) == {"P5-HC-002", "P5-HC-012", "P5-HC-018"}

    hc002 = by_id["P5-HC-002"]
    assert hc002["gold"] == "RETRIEVAL_MISS"
    assert hc002["observed_attribution"] == "REPRESENTATION_GAP"
    assert hc002["confusion"] == "retrieval_miss_vs_representation_gap"
    assert "broaden_retrieval_route_or_query_without_representation_change" in hc002["interventions"]
    assert "representation_transform_holding_corpus_fixed" in hc002["interventions"]
    assert "gold_evidence_exists_in_allowed_route_or_index" in hc002["interventions"]
    assert hc002["predictions"]["retrieval_cause"] == "route_or_query_expansion_surfaces_evidence"
    assert hc002["predictions"]["representation_cause"] == "same_corpus_usable_only_after_representation_change"

    hc012 = by_id["P5-HC-012"]
    assert hc012["gold"] == "ENVIRONMENT_DEPENDENCY_TOOL_FAILURE"
    assert hc012["observed_attribution"] == "IMPLEMENTATION_BUG"
    assert hc012["confusion"] == "environment_tool_vs_implementation_bug"
    assert "run_exact_code_in_known_good_environment" in hc012["interventions"]
    assert "substitute_known_good_tool_keeping_code_fixed" in hc012["interventions"]
    assert "static_local_test_independent_of_external_dependency" in hc012["interventions"]
    assert hc012["predictions"]["environment_cause"] == "fixed_code_succeeds_under_good_environment_or_tool"
    assert hc012["predictions"]["implementation_cause"] == "failure_persists_independent_of_environment"

    hc018 = by_id["P5-HC-018"]
    assert hc018["gold"] == "REPRESENTATION_GAP"
    assert hc018["observed_attribution"] == "METHOD_BASIS_GAP"
    assert hc018["confusion"] == "representation_gap_vs_method_basis_gap"
    assert "change_encoding_preserving_method" in hc018["interventions"]
    assert "oracle_known_good_representation_transform" in hc018["interventions"]
    assert "test_method_where_representation_assumptions_hold" in hc018["interventions"]
    assert hc018["predictions"]["representation_cause"] == "method_succeeds_after_representation_repair"
    assert hc018["predictions"]["method_basis_cause"] == "failure_persists_under_adequate_representations"

    for entry in freeze["discriminators"]:
        assert entry["authorizes_method_change"] is False
        assert entry["status"] == "DESIGN_FROZEN"


def test_discriminator_freeze_rejects_method_change_license() -> None:
    freeze = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    freeze["authorizes_method_change"] = True
    try:
        validate_discriminator_freeze(freeze)
    except ValueError as exc:
        assert "method change" in str(exc).lower()
    else:
        raise AssertionError("discriminator freeze must not license a method change")
