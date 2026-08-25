"""Proposal-origin and bounded discovery-credit records.

The objects distinguish supplied-menu selection from a generated candidate,
record old-closure reducibility, and compute only the maximum *eligible claim
terminal* from explicit evidence factors.  They do not independently decide
validity, novelty, or adoption.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from orion.transfer.v2.canonical import content_digest


def _sorted_unique(values: Sequence[str]) -> tuple[str, ...]:
    return tuple(sorted({str(value) for value in values}))


class EditKind(str, Enum):
    QUESTION_EDIT = "QUESTION_EDIT"
    FORMULATION_OR_REPRESENTATION_EDIT = "FORMULATION_OR_REPRESENTATION_EDIT"
    METHOD_LANGUAGE_EDIT = "METHOD_LANGUAGE_EDIT"
    INSTRUMENT_OR_INTERVENTION_EDIT = "INSTRUMENT_OR_INTERVENTION_EDIT"
    VALIDATION_OR_MEASUREMENT_EDIT = "VALIDATION_OR_MEASUREMENT_EDIT"
    AUTHORITY_OR_ADOPTION_EDIT = "AUTHORITY_OR_ADOPTION_EDIT"


class ReducibilityState(str, Enum):
    OLD_CLOSURE_EQUIVALENT = "OLD_CLOSURE_EQUIVALENT"
    OUTSIDE_REGISTERED_CLOSURE = "OUTSIDE_REGISTERED_CLOSURE"
    CANNOT_CHECK = "CANNOT_CHECK"


class TargetOracleAccess(str, Enum):
    NONE = "NONE"
    DECLARED_MATCHED = "DECLARED_MATCHED"
    DECLARED_UNMATCHED = "DECLARED_UNMATCHED"
    CANNOT_CHECK = "CANNOT_CHECK"


class DiscoveryCreditState(str, Enum):
    PROPOSAL_RECORDED = "PROPOSAL_RECORDED"
    OUTSIDE_REGISTERED_CLOSURE_CANDIDATE = "OUTSIDE_REGISTERED_CLOSURE_CANDIDATE"
    PROTECTED_INSTANCE_EXPANSION = "PROTECTED_INSTANCE_EXPANSION"
    TRANSFERRED_EXPANSION = "TRANSFERRED_EXPANSION"
    VALIDATED_RESIDUAL = "VALIDATED_RESIDUAL"
    EXTERNALLY_ADJUDICATED_NOVEL_DISCOVERY = (
        "EXTERNALLY_ADJUDICATED_NOVEL_DISCOVERY"
    )
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class ProposalOriginRecord:
    proposal_id: str
    frozen_regime_id: str
    frozen_operator_grammar_id: str
    edit_kinds: tuple[EditKind, ...]
    visible_source_ids: tuple[str, ...]
    visible_tension_ids: tuple[str, ...]
    visible_failure_ids: tuple[str, ...]
    generator_identity: str
    generation_trace_ids: tuple[str, ...]
    supplied_candidate_ids: tuple[str, ...]
    newly_constructed_primitive_ids: tuple[str, ...]
    correspondence_map: tuple[tuple[str, str], ...]
    hidden_field_ids: tuple[str, ...]
    target_oracle_access: TargetOracleAccess
    reducibility_state: ReducibilityState
    reducibility_evidence_ids: tuple[str, ...]
    validation_request_ids: tuple[str, ...]
    digest: str

    @property
    def grants_validity_authority(self) -> bool:
        return False

    @property
    def grants_novelty_authority(self) -> bool:
        return False

    @property
    def grants_adoption_authority(self) -> bool:
        return False

    @property
    def selected_from_supplied_menu_only(self) -> bool:
        return bool(self.supplied_candidate_ids) and not self.newly_constructed_primitive_ids

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "ProposalOrigin.v1",
            "proposal_id": self.proposal_id,
            "frozen_regime_id": self.frozen_regime_id,
            "frozen_operator_grammar_id": self.frozen_operator_grammar_id,
            "edit_kinds": [kind.value for kind in self.edit_kinds],
            "visible_source_ids": list(self.visible_source_ids),
            "visible_tension_ids": list(self.visible_tension_ids),
            "visible_failure_ids": list(self.visible_failure_ids),
            "generator_identity": self.generator_identity,
            "generation_trace_ids": list(self.generation_trace_ids),
            "supplied_candidate_ids": list(self.supplied_candidate_ids),
            "newly_constructed_primitive_ids": list(
                self.newly_constructed_primitive_ids
            ),
            "correspondence_map": [list(row) for row in self.correspondence_map],
            "hidden_field_ids": list(self.hidden_field_ids),
            "target_oracle_access": self.target_oracle_access.value,
            "reducibility_state": self.reducibility_state.value,
            "reducibility_evidence_ids": list(self.reducibility_evidence_ids),
            "validation_request_ids": list(self.validation_request_ids),
            "grants_validity_authority": False,
            "grants_novelty_authority": False,
            "grants_adoption_authority": False,
        }

    def verify(self) -> None:
        if not self.proposal_id or not self.frozen_regime_id:
            raise ValueError("proposal and frozen regime identities are required")
        if not self.frozen_operator_grammar_id or not self.generator_identity:
            raise ValueError("operator grammar and generator identities are required")
        if not self.edit_kinds:
            raise ValueError("proposal origin requires at least one edit kind")
        if not self.generation_trace_ids:
            raise ValueError("proposal origin requires a generation trace")
        if not self.validation_request_ids:
            raise ValueError("proposal origin requires protected validation requests")
        if self.reducibility_state is ReducibilityState.OUTSIDE_REGISTERED_CLOSURE:
            if not self.newly_constructed_primitive_ids:
                raise ValueError(
                    "outside-closure proposal requires a newly constructed primitive"
                )
            if not self.reducibility_evidence_ids:
                raise ValueError(
                    "outside-closure proposal requires reducibility evidence"
                )
        if self.target_oracle_access is TargetOracleAccess.DECLARED_UNMATCHED:
            if self.reducibility_state is ReducibilityState.OUTSIDE_REGISTERED_CLOSURE:
                raise ValueError(
                    "unmatched target-oracle access cannot support outside-closure credit"
                )
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("proposal origin digest mismatch")


def _canonical_correspondence(
    values: Mapping[str, str],
) -> tuple[tuple[str, str], ...]:
    rows = tuple(sorted((str(left), str(right)) for left, right in values.items()))
    if any(not left or not right for left, right in rows):
        raise ValueError("correspondence identities must be non-empty")
    if len({left for left, _ in rows}) != len(rows):
        raise ValueError("duplicate correspondence source identity")
    return rows


def build_proposal_origin(
    *,
    proposal_id: str,
    frozen_regime_id: str,
    frozen_operator_grammar_id: str,
    edit_kinds: Sequence[EditKind],
    generator_identity: str,
    generation_trace_ids: Sequence[str],
    validation_request_ids: Sequence[str],
    target_oracle_access: TargetOracleAccess,
    reducibility_state: ReducibilityState,
    visible_source_ids: Sequence[str] = (),
    visible_tension_ids: Sequence[str] = (),
    visible_failure_ids: Sequence[str] = (),
    supplied_candidate_ids: Sequence[str] = (),
    newly_constructed_primitive_ids: Sequence[str] = (),
    correspondence_map: Mapping[str, str] | None = None,
    hidden_field_ids: Sequence[str] = (),
    reducibility_evidence_ids: Sequence[str] = (),
) -> ProposalOriginRecord:
    correspondence = _canonical_correspondence(correspondence_map or {})
    payload = {
        "version": "ProposalOrigin.v1",
        "proposal_id": str(proposal_id),
        "frozen_regime_id": str(frozen_regime_id),
        "frozen_operator_grammar_id": str(frozen_operator_grammar_id),
        "edit_kinds": sorted({EditKind(kind).value for kind in edit_kinds}),
        "visible_source_ids": list(_sorted_unique(visible_source_ids)),
        "visible_tension_ids": list(_sorted_unique(visible_tension_ids)),
        "visible_failure_ids": list(_sorted_unique(visible_failure_ids)),
        "generator_identity": str(generator_identity),
        "generation_trace_ids": list(tuple(str(item) for item in generation_trace_ids)),
        "supplied_candidate_ids": list(_sorted_unique(supplied_candidate_ids)),
        "newly_constructed_primitive_ids": list(
            _sorted_unique(newly_constructed_primitive_ids)
        ),
        "correspondence_map": [list(row) for row in correspondence],
        "hidden_field_ids": list(_sorted_unique(hidden_field_ids)),
        "target_oracle_access": TargetOracleAccess(target_oracle_access).value,
        "reducibility_state": ReducibilityState(reducibility_state).value,
        "reducibility_evidence_ids": list(
            _sorted_unique(reducibility_evidence_ids)
        ),
        "validation_request_ids": list(_sorted_unique(validation_request_ids)),
        "grants_validity_authority": False,
        "grants_novelty_authority": False,
        "grants_adoption_authority": False,
    }
    record = ProposalOriginRecord(
        proposal_id=payload["proposal_id"],
        frozen_regime_id=payload["frozen_regime_id"],
        frozen_operator_grammar_id=payload["frozen_operator_grammar_id"],
        edit_kinds=tuple(EditKind(value) for value in payload["edit_kinds"]),
        visible_source_ids=tuple(payload["visible_source_ids"]),
        visible_tension_ids=tuple(payload["visible_tension_ids"]),
        visible_failure_ids=tuple(payload["visible_failure_ids"]),
        generator_identity=payload["generator_identity"],
        generation_trace_ids=tuple(payload["generation_trace_ids"]),
        supplied_candidate_ids=tuple(payload["supplied_candidate_ids"]),
        newly_constructed_primitive_ids=tuple(
            payload["newly_constructed_primitive_ids"]
        ),
        correspondence_map=correspondence,
        hidden_field_ids=tuple(payload["hidden_field_ids"]),
        target_oracle_access=TargetOracleAccess(payload["target_oracle_access"]),
        reducibility_state=ReducibilityState(payload["reducibility_state"]),
        reducibility_evidence_ids=tuple(payload["reducibility_evidence_ids"]),
        validation_request_ids=tuple(payload["validation_request_ids"]),
        digest=content_digest(payload),
    )
    record.verify()
    return record


@dataclass(frozen=True)
class DiscoveryCreditEvidence:
    proposal_origin_verified: bool
    old_regime_obstruction_verified: bool
    candidate_nonreducible_verified: bool
    protected_hidden_consequence_passed: bool
    held_out_transfer_passed: bool
    donor_first_refusal_survived: bool
    independent_validity_passed: bool
    external_novelty_and_adoption_passed: bool
    cannot_check_reasons: tuple[str, ...] = ()

    def maximum_state(self) -> DiscoveryCreditState:
        if self.cannot_check_reasons:
            return DiscoveryCreditState.CANNOT_CHECK
        if not self.proposal_origin_verified:
            return DiscoveryCreditState.CANNOT_CHECK
        if not (
            self.old_regime_obstruction_verified
            and self.candidate_nonreducible_verified
        ):
            return DiscoveryCreditState.PROPOSAL_RECORDED
        if not self.protected_hidden_consequence_passed:
            return DiscoveryCreditState.OUTSIDE_REGISTERED_CLOSURE_CANDIDATE
        if not self.held_out_transfer_passed:
            return DiscoveryCreditState.PROTECTED_INSTANCE_EXPANSION
        if not (
            self.donor_first_refusal_survived
            and self.independent_validity_passed
        ):
            return DiscoveryCreditState.TRANSFERRED_EXPANSION
        if not self.external_novelty_and_adoption_passed:
            return DiscoveryCreditState.VALIDATED_RESIDUAL
        return DiscoveryCreditState.EXTERNALLY_ADJUDICATED_NOVEL_DISCOVERY


def supplied_menu_is_outside_closure_candidate(
    origin: ProposalOriginRecord,
) -> bool:
    """Return whether origin can even qualify for outside-closure credit."""

    origin.verify()
    return (
        not origin.selected_from_supplied_menu_only
        and origin.reducibility_state is ReducibilityState.OUTSIDE_REGISTERED_CLOSURE
        and origin.target_oracle_access
        not in {TargetOracleAccess.DECLARED_UNMATCHED, TargetOracleAccess.CANNOT_CHECK}
    )


__all__ = [
    "DiscoveryCreditEvidence",
    "DiscoveryCreditState",
    "EditKind",
    "ProposalOriginRecord",
    "ReducibilityState",
    "TargetOracleAccess",
    "build_proposal_origin",
    "supplied_menu_is_outside_closure_candidate",
]
