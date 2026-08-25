from __future__ import annotations

import pytest

from orion.discovery.model_chronology import (
    HistoricalEligibilityEvidence,
    HistoricalEligibilityState,
    ModelChronologyState,
    TriangulationEvidence,
    TriangulationState,
    build_model_chronology_contract,
)


def _contract(**overrides):
    values = {
        "contract_id": "mc-1",
        "episode_id": "episode-1",
        "cutoff_event_id": "before-result",
        "model_provider": "provider",
        "model_name": "model",
        "model_revision_or_digest": "digest",
        "pretraining_corpus_disclosure_state": "DISCLOSED",
        "prompt_digest": "prompt-digest",
        "memory_state_id": "empty-memory",
        "web_access_state": "DISABLED",
        "state": ModelChronologyState.CHRONOLOGY_COMPATIBLE,
        "contamination_probe_ids": ("probe-1",),
    }
    values.update(overrides)
    return build_model_chronology_contract(**values)


def test_chronology_compatible_requires_resolved_fields_and_probes() -> None:
    contract = _contract()
    assert contract.state is ModelChronologyState.CHRONOLOGY_COMPATIBLE
    assert not contract.grants_rediscovery_authority

    with pytest.raises(ValueError, match="unresolved"):
        _contract(unresolved_field_ids=("training-corpus",))

    with pytest.raises(ValueError, match="contamination probes"):
        _contract(contamination_probe_ids=())


def test_contamination_detected_requires_bound_probe() -> None:
    with pytest.raises(ValueError, match="bound probe"):
        _contract(
            state=ModelChronologyState.CONTAMINATION_DETECTED,
            contamination_probe_ids=(),
        )


def test_historical_eligibility_is_non_compensatory() -> None:
    eligible = HistoricalEligibilityEvidence(
        source_state_reconstructible=True,
        model_chronology_compatible=True,
        contemporaneous_actions_represented=True,
        hidden_consequences_available=True,
        framework_equivalence_defined=True,
        independent_verifier_available=True,
    )
    assert eligible.state() is HistoricalEligibilityState.ELIGIBLE

    missing_model = HistoricalEligibilityEvidence(
        source_state_reconstructible=True,
        model_chronology_compatible=False,
        contemporaneous_actions_represented=True,
        hidden_consequences_available=True,
        framework_equivalence_defined=True,
        independent_verifier_available=True,
    )
    assert (
        missing_model.state()
        is HistoricalEligibilityState.MECHANISM_EXTRACTION_ONLY
    )

    blocked = HistoricalEligibilityEvidence(
        source_state_reconstructible=True,
        model_chronology_compatible=True,
        contemporaneous_actions_represented=True,
        hidden_consequences_available=True,
        framework_equivalence_defined=True,
        independent_verifier_available=True,
        blocker_ids=("rights-unresolved",),
    )
    assert blocked.state() is HistoricalEligibilityState.CANNOT_CHECK


@pytest.mark.parametrize(
    ("historical", "counterfactual", "prospective", "expected"),
    [
        (False, False, False, TriangulationState.NO_DISCOVERY_EVIDENCE),
        (True, False, False, TriangulationState.HISTORICAL_RECONSTRUCTION_ONLY),
        (
            False,
            True,
            False,
            TriangulationState.COUNTERFACTUAL_MECHANISM_TRANSFER_ONLY,
        ),
        (
            False,
            False,
            True,
            TriangulationState.PROSPECTIVE_SINGLE_DISCOVERY_ONLY,
        ),
        (
            True,
            True,
            True,
            TriangulationState.TRIANGULATED_DISCOVERY_MECHANISM_SUPPORTED,
        ),
    ],
)
def test_triangulation_states(
    historical: bool,
    counterfactual: bool,
    prospective: bool,
    expected: TriangulationState,
) -> None:
    evidence = TriangulationEvidence(historical, counterfactual, prospective)
    assert evidence.state() is expected


def test_triangulation_cannot_check_overrides_positive_lanes() -> None:
    evidence = TriangulationEvidence(
        historical_supported=True,
        counterfactual_supported=True,
        prospective_supported=True,
        cannot_check_reasons=("external-custody-missing",),
    )
    assert evidence.state() is TriangulationState.CANNOT_CHECK
