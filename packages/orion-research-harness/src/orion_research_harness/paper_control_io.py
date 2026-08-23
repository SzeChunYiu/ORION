from __future__ import annotations

from typing import Any, Mapping, Sequence

from .epistemic_authority import (
    AuthorityContext,
    BlockerDetermination,
    Coercion,
    EffectRequest,
    HardAuthorityObligation,
    Judgment,
    JudgmentType,
    RootClass,
    RootGrant,
    SupportFamily,
)
from .epistemic_mechanics import (
    AuthorityGrant,
    ClaimStatus,
    EpistemicMechanicState,
    HardObligation,
    MechanicContract,
    PreservationCertificate,
)
from .ocme_runtime import (
    LowerLevelResult,
    MethodEdit,
    OCMEEpisode,
    ObstructionCertificate,
    ObstructionKind,
    OutsideClosureVerification,
    TransferEvidence,
)


def _mapping(value: object, *, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be an object")
    return value


def _array(value: object, *, name: str) -> Sequence[Any]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise TypeError(f"{name} must be an array")
    return value


def _strings(value: object, *, name: str) -> tuple[str, ...]:
    rows = _array(value, name=name)
    out = tuple(str(item) for item in rows)
    if any(not item.strip() for item in out):
        raise ValueError(f"{name} entries must be non-empty")
    return out


def _pairs(value: object, *, name: str) -> tuple[tuple[str, str], ...]:
    if isinstance(value, Mapping):
        return tuple((str(key), str(item)) for key, item in value.items())
    rows: list[tuple[str, str]] = []
    for index, item in enumerate(_array(value, name=name)):
        pair = _array(item, name=f"{name}[{index}]")
        if len(pair) != 2:
            raise ValueError(f"{name}[{index}] must have two entries")
        rows.append((str(pair[0]), str(pair[1])))
    return tuple(rows)


def _hard_obligation(value: object) -> HardObligation:
    raw = _mapping(value, name="hard_obligation")
    return HardObligation(
        obligation_id=str(raw["obligation_id"]),
        required_evidence_ids=_strings(raw.get("required_evidence_ids", ()), name="required_evidence_ids"),
        required_authority_ids=_strings(raw.get("required_authority_ids", ()), name="required_authority_ids"),
        active=raw.get("active", True),
    )


def _mechanic_authority(value: object) -> AuthorityGrant:
    raw = _mapping(value, name="mechanic_authority")
    return AuthorityGrant(
        authority_id=str(raw["authority_id"]),
        scope_ids=_strings(raw.get("scope_ids", ()), name="scope_ids"),
        root_id=str(raw["root_id"]),
        epoch=raw["epoch"],
    )


def mechanic_state_from_mapping(value: object) -> EpistemicMechanicState:
    raw = _mapping(value, name="mechanic_state")
    statuses = tuple((key, ClaimStatus(status)) for key, status in _pairs(raw.get("claim_statuses", {}), name="claim_statuses"))
    return EpistemicMechanicState(
        coordinate_values=_pairs(raw.get("coordinate_values", {}), name="coordinate_values"),
        claim_statuses=statuses,
        dependencies=_pairs(raw.get("dependencies", ()), name="dependencies"),
        evidence_ids=_strings(raw.get("evidence_ids", ()), name="evidence_ids"),
        provenance_ids=_strings(raw.get("provenance_ids", ()), name="provenance_ids"),
        hard_obligations=tuple(_hard_obligation(item) for item in _array(raw.get("hard_obligations", ()), name="hard_obligations")),
        authorities=tuple(_mechanic_authority(item) for item in _array(raw.get("authorities", ()), name="authorities")),
        protected_root_ids=_strings(raw.get("protected_root_ids", ()), name="protected_root_ids"),
        epoch=raw["epoch"],
        history=_strings(raw.get("history", ()), name="history"),
    )


def mechanic_contract_from_mapping(value: object) -> MechanicContract:
    raw = _mapping(value, name="mechanic_contract")
    recursive: list[tuple[str, int]] = []
    for index, item in enumerate(_array(raw.get("recursive_calls", ()), name="recursive_calls")):
        pair = _array(item, name=f"recursive_calls[{index}]")
        if len(pair) != 2:
            raise ValueError("recursive call requires target and rank")
        recursive.append((str(pair[0]), int(pair[1])))
    return MechanicContract(
        mechanic_id=str(raw["mechanic_id"]),
        read_ids=_strings(raw.get("read_ids", ()), name="read_ids"),
        write_ids=_strings(raw.get("write_ids", ()), name="write_ids"),
        write_values=_pairs(raw.get("write_values", {}), name="write_values"),
        required_evidence_ids=_strings(raw.get("required_evidence_ids", ()), name="required_evidence_ids"),
        required_authority_ids=_strings(raw.get("required_authority_ids", ()), name="required_authority_ids"),
        emitted_obligations=tuple(_hard_obligation(item) for item in _array(raw.get("emitted_obligations", ()), name="emitted_obligations")),
        discharge_obligation_ids=_strings(raw.get("discharge_obligation_ids", ()), name="discharge_obligation_ids"),
        authority_additions=tuple(_mechanic_authority(item) for item in _array(raw.get("authority_additions", ()), name="authority_additions")),
        read_obligation_ids=_strings(raw.get("read_obligation_ids", ()), name="read_obligation_ids"),
        write_obligation_ids=_strings(raw.get("write_obligation_ids", ()), name="write_obligation_ids"),
        read_authority_ids=_strings(raw.get("read_authority_ids", ()), name="read_authority_ids"),
        write_authority_ids=_strings(raw.get("write_authority_ids", ()), name="write_authority_ids"),
        audit_rank=raw.get("audit_rank", 0),
        recursive_calls=tuple(recursive),
    )


def preservation_certificate_from_mapping(value: object) -> PreservationCertificate:
    raw = _mapping(value, name="preservation_certificate")
    return PreservationCertificate(
        certificate_id=str(raw["certificate_id"]),
        claim_id=str(raw["claim_id"]),
        changed_ids=_strings(raw.get("changed_ids", ()), name="changed_ids"),
        issuer_id=str(raw["issuer_id"]),
        scope_ids=_strings(raw.get("scope_ids", ()), name="scope_ids"),
        epoch=raw["epoch"],
        proof_id=str(raw["proof_id"]),
        lineage_ids=_strings(raw.get("lineage_ids", ()), name="lineage_ids"),
    )


def judgment_type_from_mapping(value: object) -> JudgmentType:
    raw = _mapping(value, name="judgment_type")
    return JudgmentType(
        domain=str(raw["domain"]),
        kind=str(raw["kind"]),
        scope_ids=_strings(raw.get("scope_ids", ()), name="scope_ids"),
        content_contract=str(raw["content_contract"]),
        epoch=raw["epoch"],
    )


def effect_request_from_mapping(value: object) -> EffectRequest:
    raw = _mapping(value, name="effect")
    return EffectRequest(
        effect_id=str(raw["effect_id"]),
        domain=str(raw["domain"]),
        operation=str(raw["operation"]),
        scope_ids=_strings(raw.get("scope_ids", ()), name="scope_ids"),
        payload_digest=str(raw["payload_digest"]),
        epoch=raw["epoch"],
    )


def authority_context_from_mapping(value: object) -> AuthorityContext:
    raw = _mapping(value, name="authority_context")
    judgments = []
    for item in _array(raw.get("judgments", ()), name="judgments"):
        row = _mapping(item, name="judgment")
        judgments.append(Judgment(str(row["judgment_id"]), judgment_type_from_mapping(row["judgment_type"]), _strings(row.get("support_premise_ids", ()), name="support_premise_ids")))
    obligations = []
    for item in _array(raw.get("hard_obligations", ()), name="hard_obligations"):
        row = _mapping(item, name="hard_authority_obligation")
        obligations.append(HardAuthorityObligation(str(row["obligation_id"]), judgment_type_from_mapping(row["required_type"]), _strings(row.get("additional_premise_ids", ()), name="additional_premise_ids")))
    roots = []
    for item in _array(raw.get("roots", ()), name="roots"):
        row = _mapping(item, name="root_grant")
        roots.append(RootGrant(str(row["grant_id"]), str(row["domain"]), _strings(row.get("scope_ids", ()), name="scope_ids"), str(row["root_id"]), RootClass(str(row["root_class"])), row["epoch"], str(row["payload_digest"])))
    coercions = []
    for item in _array(raw.get("coercions", ()), name="coercions"):
        row = _mapping(item, name="coercion")
        coercions.append(Coercion(
            str(row["coercion_id"]),
            judgment_type_from_mapping(row["input_type"]),
            judgment_type_from_mapping(row["output_type"]),
            str(row["issuer_root_id"]),
            _strings(row.get("semantic_premise_ids", ()), name="semantic_premise_ids"),
            _strings(row.get("lineage_ids", ()), name="lineage_ids"),
            row["valid_from_epoch"],
            row["valid_through_epoch"],
            allow_scope_widening=row.get("allow_scope_widening", False),
        ))
    blocker_raw = raw.get("blocker_determinations", {})
    blocker_pairs = _pairs(blocker_raw, name="blocker_determinations")
    blockers = tuple((name, BlockerDetermination(value)) for name, value in blocker_pairs)
    families = []
    for item in _array(raw.get("support_families", ()), name="support_families"):
        row = _mapping(item, name="support_family")
        support_sets = tuple(_strings(support, name="support_set") for support in _array(row.get("support_sets", ()), name="support_sets"))
        families.append(SupportFamily(str(row["certificate_id"]), support_sets))
    return AuthorityContext(
        judgments=tuple(judgments),
        hard_obligations=tuple(obligations),
        roots=tuple(roots),
        coercions=tuple(coercions),
        blocker_determinations=blockers,
        required_blocker_type_ids=_strings(raw.get("required_blocker_type_ids", ()), name="required_blocker_type_ids"),
        valid_premise_ids=_strings(raw.get("valid_premise_ids", ()), name="valid_premise_ids"),
        revoked_premise_ids=_strings(raw.get("revoked_premise_ids", ()), name="revoked_premise_ids"),
        support_families=tuple(families),
        history=_strings(raw.get("history", ()), name="history"),
    )


def ocme_episode_from_mapping(value: object) -> OCMEEpisode:
    raw = _mapping(value, name="ocme_episode")
    lower = []
    for item in _array(raw.get("lower_level_results", ()), name="lower_level_results"):
        row = _mapping(item, name="lower_level_result")
        lower.append(LowerLevelResult(str(row["check_id"]), str(row["route_kind"]), row["succeeded"], _strings(row.get("evidence_ids", ()), name="evidence_ids")))
    obstruction = None
    if raw.get("obstruction") is not None:
        row = _mapping(raw["obstruction"], name="obstruction")
        obstruction = ObstructionCertificate(str(row["certificate_id"]), ObstructionKind(str(row["kind"])), str(row["target_id"]), _strings(row.get("old_closure_ids", ()), name="old_closure_ids"), _strings(row.get("evidence_ids", ()), name="evidence_ids"), row["independently_verified"], row["all_registered_baselines_exhausted"], row.get("timeout_only", False))
    edit = None
    if raw.get("candidate_edit") is not None:
        row = _mapping(raw["candidate_edit"], name="candidate_edit")
        edit = MethodEdit(str(row["edit_id"]), _strings(row.get("semantic_operator_ids", ()), name="semantic_operator_ids"), _strings(row.get("claimed_new_reach_ids", ()), name="claimed_new_reach_ids"), row["expands_to_old_closure"], _strings(row.get("access_model_ids", ()), name="access_model_ids"))
    outside = None
    if raw.get("outside_closure") is not None:
        row = _mapping(raw["outside_closure"], name="outside_closure")
        outside = OutsideClosureVerification(str(row["verification_id"]), str(row["edit_id"]), str(row["verifier_id"]), str(row["candidate_issuer_id"]), row["outside_old_closure"], _strings(row.get("evidence_ids", ()), name="evidence_ids"))
    transfer = None
    if raw.get("transfer") is not None:
        row = _mapping(raw["transfer"], name="transfer")
        transfer = TransferEvidence(_strings(row.get("held_out_ids", ()), name="held_out_ids"), _strings(row.get("positive_transfer_ids", ()), name="positive_transfer_ids"), _strings(row.get("frozen_access_model_ids", ()), name="frozen_access_model_ids"), row["false_expansion_rate"], row["false_expansion_guard"], row["semantic_preservation"], row["strong_baseline_same_reach"], _strings(row.get("evidence_ids", ()), name="evidence_ids"))
    return OCMEEpisode(
        episode_id=str(raw["episode_id"]),
        problem_model_frozen=raw["problem_model_frozen"],
        verifier_available=raw["verifier_available"],
        access_model_frozen=raw["access_model_frozen"],
        resource_model_frozen=raw["resource_model_frozen"],
        lower_level_results=tuple(lower),
        obstruction=obstruction,
        candidate_edit=edit,
        outside_closure=outside,
        transfer=transfer,
        problem_solving_gain=raw["problem_solving_gain"],
        donor_same_reach=raw["donor_same_reach"],
        independent_reproduction=raw["independent_reproduction"],
    )


__all__ = [
    "authority_context_from_mapping",
    "effect_request_from_mapping",
    "mechanic_contract_from_mapping",
    "mechanic_state_from_mapping",
    "ocme_episode_from_mapping",
    "preservation_certificate_from_mapping",
]
