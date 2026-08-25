"""Chronology and triangulation records for historical discovery research.

Source-date filtering and model-knowledge filtering are represented separately.
The records are fail-closed and non-authorizing; external custody and scientific
validity remain outside this module.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from orion.transfer.v2.canonical import content_digest


def _sorted_unique(values: Sequence[str]) -> tuple[str, ...]:
    return tuple(sorted({str(value) for value in values}))


class ModelChronologyState(str, Enum):
    CHRONOLOGY_COMPATIBLE = "CHRONOLOGY_COMPATIBLE"
    CONTAMINATION_DETECTED = "CONTAMINATION_DETECTED"
    CONTAMINATION_NOT_RULED_OUT = "CONTAMINATION_NOT_RULED_OUT"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class ModelChronologyContract:
    contract_id: str
    episode_id: str
    cutoff_event_id: str
    model_provider: str
    model_name: str
    model_revision_or_digest: str
    pretraining_cutoff_claim: str | None
    pretraining_corpus_disclosure_state: str
    posttraining_source_ids: tuple[str, ...]
    retrieval_cutoff: str | None
    retrieval_index_digest: str | None
    prompt_digest: str
    memory_state_id: str
    tool_version_ids: tuple[str, ...]
    web_access_state: str
    benchmark_exposure_audit_ids: tuple[str, ...]
    masking_control_ids: tuple[str, ...]
    contamination_probe_ids: tuple[str, ...]
    candidate_visible_metadata_ids: tuple[str, ...]
    unresolved_field_ids: tuple[str, ...]
    state: ModelChronologyState
    digest: str

    @property
    def grants_rediscovery_authority(self) -> bool:
        return False

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "ModelChronologyContract.v1",
            "contract_id": self.contract_id,
            "episode_id": self.episode_id,
            "cutoff_event_id": self.cutoff_event_id,
            "model_provider": self.model_provider,
            "model_name": self.model_name,
            "model_revision_or_digest": self.model_revision_or_digest,
            "pretraining_cutoff_claim": self.pretraining_cutoff_claim,
            "pretraining_corpus_disclosure_state": self.pretraining_corpus_disclosure_state,
            "posttraining_source_ids": list(self.posttraining_source_ids),
            "retrieval_cutoff": self.retrieval_cutoff,
            "retrieval_index_digest": self.retrieval_index_digest,
            "prompt_digest": self.prompt_digest,
            "memory_state_id": self.memory_state_id,
            "tool_version_ids": list(self.tool_version_ids),
            "web_access_state": self.web_access_state,
            "benchmark_exposure_audit_ids": list(self.benchmark_exposure_audit_ids),
            "masking_control_ids": list(self.masking_control_ids),
            "contamination_probe_ids": list(self.contamination_probe_ids),
            "candidate_visible_metadata_ids": list(
                self.candidate_visible_metadata_ids
            ),
            "unresolved_field_ids": list(self.unresolved_field_ids),
            "state": self.state.value,
            "grants_rediscovery_authority": False,
        }

    def verify(self) -> None:
        required = (
            self.contract_id,
            self.episode_id,
            self.cutoff_event_id,
            self.model_provider,
            self.model_name,
            self.model_revision_or_digest,
            self.pretraining_corpus_disclosure_state,
            self.prompt_digest,
            self.memory_state_id,
            self.web_access_state,
        )
        if any(not value for value in required):
            raise ValueError("model chronology contract has an empty required field")
        if self.state is ModelChronologyState.CHRONOLOGY_COMPATIBLE:
            if self.unresolved_field_ids:
                raise ValueError(
                    "chronology-compatible state cannot retain unresolved fields"
                )
            if not self.contamination_probe_ids:
                raise ValueError(
                    "chronology-compatible state requires contamination probes"
                )
        if self.state is ModelChronologyState.CONTAMINATION_DETECTED:
            if not self.contamination_probe_ids:
                raise ValueError(
                    "contamination-detected state requires a bound probe identity"
                )
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("model chronology digest mismatch")


def build_model_chronology_contract(
    *,
    contract_id: str,
    episode_id: str,
    cutoff_event_id: str,
    model_provider: str,
    model_name: str,
    model_revision_or_digest: str,
    pretraining_corpus_disclosure_state: str,
    prompt_digest: str,
    memory_state_id: str,
    web_access_state: str,
    state: ModelChronologyState,
    pretraining_cutoff_claim: str | None = None,
    posttraining_source_ids: Sequence[str] = (),
    retrieval_cutoff: str | None = None,
    retrieval_index_digest: str | None = None,
    tool_version_ids: Sequence[str] = (),
    benchmark_exposure_audit_ids: Sequence[str] = (),
    masking_control_ids: Sequence[str] = (),
    contamination_probe_ids: Sequence[str] = (),
    candidate_visible_metadata_ids: Sequence[str] = (),
    unresolved_field_ids: Sequence[str] = (),
) -> ModelChronologyContract:
    payload = {
        "version": "ModelChronologyContract.v1",
        "contract_id": str(contract_id),
        "episode_id": str(episode_id),
        "cutoff_event_id": str(cutoff_event_id),
        "model_provider": str(model_provider),
        "model_name": str(model_name),
        "model_revision_or_digest": str(model_revision_or_digest),
        "pretraining_cutoff_claim": (
            str(pretraining_cutoff_claim)
            if pretraining_cutoff_claim is not None
            else None
        ),
        "pretraining_corpus_disclosure_state": str(
            pretraining_corpus_disclosure_state
        ),
        "posttraining_source_ids": list(_sorted_unique(posttraining_source_ids)),
        "retrieval_cutoff": str(retrieval_cutoff) if retrieval_cutoff is not None else None,
        "retrieval_index_digest": (
            str(retrieval_index_digest)
            if retrieval_index_digest is not None
            else None
        ),
        "prompt_digest": str(prompt_digest),
        "memory_state_id": str(memory_state_id),
        "tool_version_ids": list(_sorted_unique(tool_version_ids)),
        "web_access_state": str(web_access_state),
        "benchmark_exposure_audit_ids": list(
            _sorted_unique(benchmark_exposure_audit_ids)
        ),
        "masking_control_ids": list(_sorted_unique(masking_control_ids)),
        "contamination_probe_ids": list(_sorted_unique(contamination_probe_ids)),
        "candidate_visible_metadata_ids": list(
            _sorted_unique(candidate_visible_metadata_ids)
        ),
        "unresolved_field_ids": list(_sorted_unique(unresolved_field_ids)),
        "state": ModelChronologyState(state).value,
        "grants_rediscovery_authority": False,
    }
    contract = ModelChronologyContract(
        contract_id=payload["contract_id"],
        episode_id=payload["episode_id"],
        cutoff_event_id=payload["cutoff_event_id"],
        model_provider=payload["model_provider"],
        model_name=payload["model_name"],
        model_revision_or_digest=payload["model_revision_or_digest"],
        pretraining_cutoff_claim=payload["pretraining_cutoff_claim"],
        pretraining_corpus_disclosure_state=payload[
            "pretraining_corpus_disclosure_state"
        ],
        posttraining_source_ids=tuple(payload["posttraining_source_ids"]),
        retrieval_cutoff=payload["retrieval_cutoff"],
        retrieval_index_digest=payload["retrieval_index_digest"],
        prompt_digest=payload["prompt_digest"],
        memory_state_id=payload["memory_state_id"],
        tool_version_ids=tuple(payload["tool_version_ids"]),
        web_access_state=payload["web_access_state"],
        benchmark_exposure_audit_ids=tuple(
            payload["benchmark_exposure_audit_ids"]
        ),
        masking_control_ids=tuple(payload["masking_control_ids"]),
        contamination_probe_ids=tuple(payload["contamination_probe_ids"]),
        candidate_visible_metadata_ids=tuple(
            payload["candidate_visible_metadata_ids"]
        ),
        unresolved_field_ids=tuple(payload["unresolved_field_ids"]),
        state=ModelChronologyState(payload["state"]),
        digest=content_digest(payload),
    )
    contract.verify()
    return contract


class HistoricalEligibilityState(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    MECHANISM_EXTRACTION_ONLY = "MECHANISM_EXTRACTION_ONLY"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class HistoricalEligibilityEvidence:
    source_state_reconstructible: bool
    model_chronology_compatible: bool
    contemporaneous_actions_represented: bool
    hidden_consequences_available: bool
    framework_equivalence_defined: bool
    independent_verifier_available: bool
    blocker_ids: tuple[str, ...] = ()

    def state(self) -> HistoricalEligibilityState:
        if self.blocker_ids:
            return HistoricalEligibilityState.CANNOT_CHECK
        values = (
            self.source_state_reconstructible,
            self.model_chronology_compatible,
            self.contemporaneous_actions_represented,
            self.hidden_consequences_available,
            self.framework_equivalence_defined,
            self.independent_verifier_available,
        )
        if all(values):
            return HistoricalEligibilityState.ELIGIBLE
        return HistoricalEligibilityState.MECHANISM_EXTRACTION_ONLY


class TriangulationState(str, Enum):
    NO_DISCOVERY_EVIDENCE = "NO_DISCOVERY_EVIDENCE"
    HISTORICAL_RECONSTRUCTION_ONLY = "HISTORICAL_RECONSTRUCTION_ONLY"
    COUNTERFACTUAL_MECHANISM_TRANSFER_ONLY = (
        "COUNTERFACTUAL_MECHANISM_TRANSFER_ONLY"
    )
    PROSPECTIVE_SINGLE_DISCOVERY_ONLY = "PROSPECTIVE_SINGLE_DISCOVERY_ONLY"
    HISTORICAL_PLUS_COUNTERFACTUAL = "HISTORICAL_PLUS_COUNTERFACTUAL"
    HISTORICAL_PLUS_PROSPECTIVE = "HISTORICAL_PLUS_PROSPECTIVE"
    COUNTERFACTUAL_PLUS_PROSPECTIVE = "COUNTERFACTUAL_PLUS_PROSPECTIVE"
    TRIANGULATED_DISCOVERY_MECHANISM_SUPPORTED = (
        "TRIANGULATED_DISCOVERY_MECHANISM_SUPPORTED"
    )
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class TriangulationEvidence:
    historical_supported: bool
    counterfactual_supported: bool
    prospective_supported: bool
    cannot_check_reasons: tuple[str, ...] = ()

    def state(self) -> TriangulationState:
        if self.cannot_check_reasons:
            return TriangulationState.CANNOT_CHECK
        key = (
            self.historical_supported,
            self.counterfactual_supported,
            self.prospective_supported,
        )
        table = {
            (False, False, False): TriangulationState.NO_DISCOVERY_EVIDENCE,
            (True, False, False): TriangulationState.HISTORICAL_RECONSTRUCTION_ONLY,
            (False, True, False): TriangulationState.COUNTERFACTUAL_MECHANISM_TRANSFER_ONLY,
            (False, False, True): TriangulationState.PROSPECTIVE_SINGLE_DISCOVERY_ONLY,
            (True, True, False): TriangulationState.HISTORICAL_PLUS_COUNTERFACTUAL,
            (True, False, True): TriangulationState.HISTORICAL_PLUS_PROSPECTIVE,
            (False, True, True): TriangulationState.COUNTERFACTUAL_PLUS_PROSPECTIVE,
            (True, True, True): TriangulationState.TRIANGULATED_DISCOVERY_MECHANISM_SUPPORTED,
        }
        return table[key]


__all__ = [
    "HistoricalEligibilityEvidence",
    "HistoricalEligibilityState",
    "ModelChronologyContract",
    "ModelChronologyState",
    "TriangulationEvidence",
    "TriangulationState",
    "build_model_chronology_contract",
]
