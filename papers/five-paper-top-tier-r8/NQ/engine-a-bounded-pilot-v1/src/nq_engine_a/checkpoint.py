from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from itertools import pairwise
from typing import Any

from . import EXPECTED_OUTCOME_MARKER, EXPOSURE_MARKER, INDEPENDENCE_TERMINAL
from .augmentation import (
    ConstraintDecision,
    ConstraintProfile,
    canonical_parent,
    evaluate_constraints,
    extension_orbit_representatives,
)
from .canonical import canonical_multiset
from .group import GroupSpec, InputError, Vector
from .normalization import declared_donor_images
from .receipt import canonical_json_sha256

DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
EXPOSURE_MARKERS = [EXPECTED_OUTCOME_MARKER, EXPOSURE_MARKER]
NORMALIZATION_CONTRACT_SHA256 = "e12641cdb09048134f5e25dd41b7153850261482379c7396e1c5860162ad4008"


class CheckpointTerminal(StrEnum):
    CHECKPOINT_SAVED = "CHECKPOINT_SAVED__NOT_GLOBAL"
    CHECKPOINT_LEVEL_COMPLETE = "CHECKPOINT_LEVEL_COMPLETE__NOT_GLOBAL"
    CANNOT_CHECK_RESOURCE_BOUND = "CANNOT_CHECK_RESOURCE_BOUND"
    CANNOT_CHECK_CHECKPOINT_MISMATCH = "CANNOT_CHECK_CHECKPOINT_MISMATCH"


class CheckpointPhase(StrEnum):
    COLLECT_CANDIDATES = "COLLECT_CANDIDATES"
    EVALUATE_CANDIDATES = "EVALUATE_CANDIDATES"
    COMPLETE = "COMPLETE"


class RangeManifestError(ValueError):
    """A donor range cannot be verified or merged safely."""


def _checked_digest(value: object, field: str) -> str:
    if not isinstance(value, str) or DIGEST_RE.fullmatch(value) is None:
        raise InputError(f"{field} must be a lowercase SHA-256 digest")
    return value


def _checked_nonnegative_int(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise InputError(f"{field} must be a nonnegative integer")
    return value


def _profile_payload(profile: ConstraintProfile) -> dict[str, int | None]:
    return {
        "short_zero_sum_cutoff": profile.short_zero_sum_cutoff,
        "forbid_k_disjoint": profile.forbid_k_disjoint,
        "max_factor_states": profile.max_factor_states,
    }


def _records_payload(records: tuple[tuple[Vector, ...], ...]) -> list[list[list[int]]]:
    return [[list(vector) for vector in record] for record in records]


def canonical_records_sha256(records: object) -> str:
    if not isinstance(records, (list, tuple)):
        raise InputError("records must be a list or tuple")
    payload: list[list[list[int]]] = []
    for record in records:
        if not isinstance(record, (list, tuple)):
            raise InputError("each record must be a list or tuple")
        serialized_record: list[list[int]] = []
        for vector in record:
            if not isinstance(vector, (list, tuple)):
                raise InputError("each vector must be a list or tuple")
            serialized_record.append(list(vector))
        payload.append(serialized_record)
    return canonical_json_sha256(payload)


@dataclass(frozen=True, slots=True)
class CheckpointConfig:
    p: int
    d: int
    parent_level: int
    target_level: int
    range_start: int
    range_stop: int
    parent_records_sha256: str
    protocol_sha256: str
    source_manifest_sha256: str
    candidate_edge_budget: int
    profile: ConstraintProfile

    def __post_init__(self) -> None:
        GroupSpec(self.p, self.d)
        parent_level = _checked_nonnegative_int(self.parent_level, "parent_level")
        target_level = _checked_nonnegative_int(self.target_level, "target_level")
        start = _checked_nonnegative_int(self.range_start, "range_start")
        stop = _checked_nonnegative_int(self.range_stop, "range_stop")
        if target_level != parent_level + 1:
            raise InputError("target_level must equal parent_level + 1")
        if start >= stop:
            raise InputError("checkpoint parent range must be nonempty")
        _checked_digest(self.parent_records_sha256, "parent_records_sha256")
        _checked_digest(self.protocol_sha256, "protocol_sha256")
        _checked_digest(self.source_manifest_sha256, "source_manifest_sha256")
        if (
            isinstance(self.candidate_edge_budget, bool)
            or not isinstance(self.candidate_edge_budget, int)
            or self.candidate_edge_budget < 1
        ):
            raise InputError("candidate_edge_budget must be a positive integer")
        if not isinstance(self.profile, ConstraintProfile):
            raise InputError("profile must be a ConstraintProfile")

    def to_dict(self) -> dict[str, Any]:
        return {
            "group": {"p": self.p, "d": self.d},
            "parent_level": self.parent_level,
            "target_level": self.target_level,
            "parent_range": [self.range_start, self.range_stop],
            "parent_records_sha256": self.parent_records_sha256,
            "protocol_sha256": self.protocol_sha256,
            "source_manifest_sha256": self.source_manifest_sha256,
            "candidate_edge_budget": self.candidate_edge_budget,
            "profile": _profile_payload(self.profile),
        }

    @property
    def configuration_sha256(self) -> str:
        return canonical_json_sha256(self.to_dict())


COUNTER_NAMES = (
    "parents_expanded",
    "extension_orbit_representatives",
    "candidate_edges",
    "canonical_parent_rejections",
    "duplicate_children_collapsed",
    "pruned_short_zero_sum",
    "pruned_k_disjoint",
)


@dataclass(frozen=True, slots=True)
class CheckpointState:
    config: CheckpointConfig
    phase: CheckpointPhase
    cursor_parent_index: int
    cursor_representative_index: int
    evaluation_index: int
    candidates: tuple[tuple[Vector, ...], ...]
    accepted_children: tuple[tuple[Vector, ...], ...]
    parents_expanded: int
    extension_orbit_representatives: int
    candidate_edges: int
    canonical_parent_rejections: int
    duplicate_children_collapsed: int
    pruned_short_zero_sum: int
    pruned_k_disjoint: int

    def counters(self) -> dict[str, int]:
        return {name: getattr(self, name) for name in COUNTER_NAMES}

    def _payload(self) -> dict[str, Any]:
        config = self.config.to_dict()
        return {
            "schema_version": "nq-engine-a-checkpoint-state-v1",
            "independence_terminal": INDEPENDENCE_TERMINAL,
            "exposure_markers": EXPOSURE_MARKERS,
            "scientific_terminal": "CANNOT_CHECK",
            "protocol_sha256": config["protocol_sha256"],
            "source_manifest_sha256": config["source_manifest_sha256"],
            "parent_records_sha256": config["parent_records_sha256"],
            "configuration_sha256": self.config.configuration_sha256,
            "group": config["group"],
            "parent_level": config["parent_level"],
            "target_level": config["target_level"],
            "parent_range": config["parent_range"],
            "candidate_edge_budget": config["candidate_edge_budget"],
            "profile": config["profile"],
            "phase": self.phase.value,
            "cursor": {
                "parent_index": self.cursor_parent_index,
                "representative_index": self.cursor_representative_index,
                "evaluation_index": self.evaluation_index,
            },
            "candidates": _records_payload(self.candidates),
            "accepted_children": _records_payload(self.accepted_children),
            "counters": self.counters(),
        }

    def to_dict(self) -> dict[str, Any]:
        payload = self._payload()
        return {**payload, "checkpoint_sha256": canonical_json_sha256(payload)}


@dataclass(frozen=True, slots=True)
class CheckpointAdvance:
    terminal: CheckpointTerminal
    config: CheckpointConfig
    checkpoint: CheckpointState | None
    errors: tuple[str, ...] = ()

    @property
    def full_range_coverage(self) -> bool:
        return self.terminal is CheckpointTerminal.CHECKPOINT_LEVEL_COMPLETE

    @property
    def records_error(self) -> str:
        if self.terminal is CheckpointTerminal.CANNOT_CHECK_CHECKPOINT_MISMATCH:
            return "checkpoint mismatch cannot support child records"
        return "partial checkpoint cannot support child records"

    @property
    def records(self) -> tuple[tuple[Vector, ...], ...]:
        if not self.full_range_coverage or self.checkpoint is None:
            raise RuntimeError(self.records_error)
        return self.checkpoint.accepted_children

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "nq-engine-a-checkpoint-run-v1",
            "terminal": self.terminal.value,
            "authority": "engineering_checkpoint_only",
            "independence_terminal": INDEPENDENCE_TERMINAL,
            "exposure_markers": EXPOSURE_MARKERS,
            "scientific_terminal": "CANNOT_CHECK",
            "parent_level": self.config.parent_level,
            "target_level": self.config.target_level,
            "parent_range": [self.config.range_start, self.config.range_stop],
            "full_range_coverage": self.full_range_coverage,
            "global_coverage": False,
            "checkpoint": None if self.checkpoint is None else self.checkpoint.to_dict(),
            "errors": list(self.errors),
        }


def _state(
    config: CheckpointConfig,
    *,
    phase: CheckpointPhase,
    cursor_parent_index: int,
    cursor_representative_index: int,
    evaluation_index: int,
    candidates: set[tuple[Vector, ...]] | tuple[tuple[Vector, ...], ...],
    accepted_children: list[tuple[Vector, ...]] | tuple[tuple[Vector, ...], ...],
    counters: dict[str, int],
) -> CheckpointState:
    return CheckpointState(
        config=config,
        phase=phase,
        cursor_parent_index=cursor_parent_index,
        cursor_representative_index=cursor_representative_index,
        evaluation_index=evaluation_index,
        candidates=tuple(sorted(candidates)),
        accepted_children=tuple(sorted(accepted_children)),
        **{name: counters[name] for name in COUNTER_NAMES},
    )


def _empty_state(config: CheckpointConfig) -> CheckpointState:
    return _state(
        config,
        phase=CheckpointPhase.COLLECT_CANDIDATES,
        cursor_parent_index=config.range_start,
        cursor_representative_index=0,
        evaluation_index=0,
        candidates=set(),
        accepted_children=[],
        counters=dict.fromkeys(COUNTER_NAMES, 0),
    )


def _config_from_state_payload(payload: dict[str, Any]) -> CheckpointConfig:
    group = payload["group"]
    parent_range = payload["parent_range"]
    profile = payload["profile"]
    if not isinstance(group, dict) or set(group) != {"p", "d"}:
        raise InputError("checkpoint group is invalid")
    if not isinstance(parent_range, list) or len(parent_range) != 2:
        raise InputError("checkpoint parent range is invalid")
    if not isinstance(profile, dict) or set(profile) != {
        "short_zero_sum_cutoff",
        "forbid_k_disjoint",
        "max_factor_states",
    }:
        raise InputError("checkpoint profile is invalid")
    return CheckpointConfig(
        p=group["p"],
        d=group["d"],
        parent_level=payload["parent_level"],
        target_level=payload["target_level"],
        range_start=parent_range[0],
        range_stop=parent_range[1],
        parent_records_sha256=payload["parent_records_sha256"],
        protocol_sha256=payload["protocol_sha256"],
        source_manifest_sha256=payload["source_manifest_sha256"],
        candidate_edge_budget=payload["candidate_edge_budget"],
        profile=ConstraintProfile(**profile),
    )


def _parse_checkpoint(spec: GroupSpec, value: object) -> CheckpointState:
    if not isinstance(value, dict):
        raise InputError("checkpoint must be an object")
    required = {
        "schema_version",
        "independence_terminal",
        "exposure_markers",
        "scientific_terminal",
        "protocol_sha256",
        "source_manifest_sha256",
        "parent_records_sha256",
        "configuration_sha256",
        "group",
        "parent_level",
        "target_level",
        "parent_range",
        "candidate_edge_budget",
        "profile",
        "phase",
        "cursor",
        "candidates",
        "accepted_children",
        "counters",
        "checkpoint_sha256",
    }
    if set(value) != required:
        raise InputError("checkpoint fields do not match the frozen schema")
    if value["schema_version"] != "nq-engine-a-checkpoint-state-v1":
        raise InputError("checkpoint schema version mismatch")
    if value["independence_terminal"] != INDEPENDENCE_TERMINAL:
        raise InputError("checkpoint independence terminal mismatch")
    if value["exposure_markers"] != EXPOSURE_MARKERS:
        raise InputError("checkpoint exposure markers mismatch")
    if value["scientific_terminal"] != "CANNOT_CHECK":
        raise InputError("checkpoint scientific terminal mismatch")
    declared_sha = _checked_digest(value["checkpoint_sha256"], "checkpoint_sha256")
    raw_payload = {key: item for key, item in value.items() if key != "checkpoint_sha256"}
    if canonical_json_sha256(raw_payload) != declared_sha:
        raise InputError("checkpoint payload digest mismatch")
    config = _config_from_state_payload(value)
    if value["configuration_sha256"] != config.configuration_sha256:
        raise InputError("checkpoint configuration digest mismatch")
    cursor = value["cursor"]
    counters = value["counters"]
    if not isinstance(cursor, dict) or set(cursor) != {
        "parent_index",
        "representative_index",
        "evaluation_index",
    }:
        raise InputError("checkpoint cursor is invalid")
    if not isinstance(counters, dict) or set(counters) != set(COUNTER_NAMES):
        raise InputError("checkpoint counters are invalid")
    parsed_counters = {
        name: _checked_nonnegative_int(counters[name], f"counter {name}") for name in COUNTER_NAMES
    }
    candidates = tuple(spec.validate_sequence(record) for record in value["candidates"])
    accepted = tuple(spec.validate_sequence(record) for record in value["accepted_children"])
    if candidates != tuple(sorted(set(candidates))):
        raise InputError("checkpoint candidates must be sorted and unique")
    if accepted != tuple(sorted(set(accepted))):
        raise InputError("checkpoint accepted children must be sorted and unique")
    return _state(
        config,
        phase=CheckpointPhase(value["phase"]),
        cursor_parent_index=_checked_nonnegative_int(cursor["parent_index"], "parent cursor"),
        cursor_representative_index=_checked_nonnegative_int(
            cursor["representative_index"], "representative cursor"
        ),
        evaluation_index=_checked_nonnegative_int(cursor["evaluation_index"], "evaluation cursor"),
        candidates=candidates,
        accepted_children=accepted,
        counters=parsed_counters,
    )


def _validate_parents(
    spec: GroupSpec, parents: object, config: CheckpointConfig
) -> tuple[tuple[Vector, ...], ...]:
    if (spec.p, spec.d) != (config.p, config.d):
        raise InputError("checkpoint group does not match configuration")
    if not isinstance(parents, (list, tuple)):
        raise InputError("parents must be a list or tuple")
    records = tuple(spec.validate_sequence(parent) for parent in parents)
    if config.range_stop > len(records):
        raise InputError("checkpoint parent range exceeds the bound parent list")
    if canonical_records_sha256(records) != config.parent_records_sha256:
        raise InputError("parent record manifest digest mismatch")
    if records != tuple(sorted(set(records))):
        raise InputError("parent records must be sorted and unique")
    for record in records:
        if len(record) != config.parent_level:
            raise InputError("parent record length mismatch")
        if record != canonical_multiset(spec, record):
            raise InputError("parent record is not canonical")
    return records


def _replay_collection_prefix(
    spec: GroupSpec,
    parents: tuple[tuple[Vector, ...], ...],
    config: CheckpointConfig,
    cursor_parent: int,
    cursor_representative: int,
) -> tuple[set[tuple[Vector, ...]], dict[str, int]]:
    if not config.range_start <= cursor_parent <= config.range_stop:
        raise InputError("checkpoint parent cursor is outside its range")
    if cursor_parent == config.range_stop and cursor_representative != 0:
        raise InputError("completed collection cursor must have representative index zero")
    candidates: set[tuple[Vector, ...]] = set()
    counters = dict.fromkeys(COUNTER_NAMES, 0)
    for parent_index in range(config.range_start, cursor_parent + 1):
        if parent_index == config.range_stop:
            break
        parent = parents[parent_index]
        representatives = extension_orbit_representatives(spec, parent)
        limit = len(representatives) if parent_index < cursor_parent else cursor_representative
        if not 0 <= limit <= len(representatives):
            raise InputError("checkpoint representative cursor is outside its parent")
        if limit == 0:
            continue
        counters["parents_expanded"] += 1
        counters["extension_orbit_representatives"] += len(representatives)
        for representative in representatives[:limit]:
            counters["candidate_edges"] += 1
            child = canonical_multiset(spec, (*parent, representative))
            if canonical_parent(spec, child) != parent:
                counters["canonical_parent_rejections"] += 1
                continue
            if child in candidates:
                counters["duplicate_children_collapsed"] += 1
            candidates.add(child)
    return candidates, counters


def _validate_checkpoint_prefix(
    spec: GroupSpec,
    parents: tuple[tuple[Vector, ...], ...],
    checkpoint: CheckpointState,
) -> None:
    candidates, counters = _replay_collection_prefix(
        spec,
        parents,
        checkpoint.config,
        checkpoint.cursor_parent_index,
        checkpoint.cursor_representative_index,
    )
    if tuple(sorted(candidates)) != checkpoint.candidates:
        raise InputError("checkpoint candidates do not match the processed edge prefix")
    for name in COUNTER_NAMES[:5]:
        if counters[name] != getattr(checkpoint, name):
            raise InputError(f"checkpoint counter {name} does not match the processed edge prefix")
    if checkpoint.phase is CheckpointPhase.COLLECT_CANDIDATES:
        if checkpoint.evaluation_index != 0 or checkpoint.accepted_children:
            raise InputError("collection checkpoint contains evaluation output")
        if checkpoint.pruned_short_zero_sum or checkpoint.pruned_k_disjoint:
            raise InputError("collection checkpoint contains pruning counters")
        return
    if checkpoint.cursor_parent_index != checkpoint.config.range_stop:
        raise InputError("evaluation checkpoint has incomplete edge coverage")
    ordered = tuple(sorted(candidates))
    if checkpoint.evaluation_index > len(ordered):
        raise InputError("checkpoint evaluation cursor is outside the candidate set")
    accepted: list[tuple[Vector, ...]] = []
    short_pruned = 0
    factor_pruned = 0
    for child in ordered[: checkpoint.evaluation_index]:
        decision = evaluate_constraints(spec, child, checkpoint.config.profile)
        if decision is ConstraintDecision.CANNOT_CHECK_RESOURCE_BOUND:
            raise InputError("checkpoint crossed a resource-bounded evaluation")
        if decision is ConstraintDecision.PRUNE_SHORT_ZERO_SUM:
            short_pruned += 1
        elif decision is ConstraintDecision.PRUNE_K_DISJOINT:
            factor_pruned += 1
        else:
            accepted.append(child)
    if tuple(accepted) != checkpoint.accepted_children:
        raise InputError("checkpoint accepted children do not match the evaluation prefix")
    if short_pruned != checkpoint.pruned_short_zero_sum:
        raise InputError("checkpoint short-zero-sum counter mismatch")
    if factor_pruned != checkpoint.pruned_k_disjoint:
        raise InputError("checkpoint factor-pruning counter mismatch")
    if checkpoint.phase is CheckpointPhase.COMPLETE and checkpoint.evaluation_index != len(ordered):
        raise InputError("complete checkpoint has incomplete candidate evaluation")


def _mismatch(config: CheckpointConfig, error: Exception) -> CheckpointAdvance:
    return CheckpointAdvance(
        CheckpointTerminal.CANNOT_CHECK_CHECKPOINT_MISMATCH,
        config,
        None,
        (str(error),),
    )


def advance_child_level(
    spec: GroupSpec,
    parents: object,
    config: CheckpointConfig,
    *,
    checkpoint: object | None = None,
    edge_budget: object,
    reference_uninterrupted: bool = False,
) -> CheckpointAdvance:
    try:
        if not isinstance(config, CheckpointConfig):
            raise InputError("config must be a CheckpointConfig")
        records = _validate_parents(spec, parents, config)
        if isinstance(reference_uninterrupted, bool) is False:
            raise InputError("reference_uninterrupted must be boolean")
        if isinstance(edge_budget, bool) or not isinstance(edge_budget, int) or edge_budget < 1:
            raise InputError("invocation edge budget must be a positive integer")
        if reference_uninterrupted:
            if checkpoint is not None:
                raise InputError("uninterrupted reference cannot resume a checkpoint")
        elif edge_budget != config.candidate_edge_budget:
            raise InputError("invocation edge budget does not match the frozen configuration")
        if checkpoint is None:
            current = _empty_state(config)
        else:
            current = _parse_checkpoint(spec, checkpoint)
            if current.config != config:
                raise InputError("checkpoint configuration binding mismatch")
            _validate_checkpoint_prefix(spec, records, current)
    except (InputError, TypeError, ValueError, KeyError) as error:
        return _mismatch(config, error)

    if current.phase is CheckpointPhase.COMPLETE:
        return CheckpointAdvance(CheckpointTerminal.CHECKPOINT_LEVEL_COMPLETE, config, current)

    candidates = set(current.candidates)
    accepted = list(current.accepted_children)
    counters = current.counters()
    parent_index = current.cursor_parent_index
    representative_index = current.cursor_representative_index
    evaluation_index = current.evaluation_index
    phase = current.phase
    processed_this_invocation = 0

    if phase is CheckpointPhase.COLLECT_CANDIDATES:
        while parent_index < config.range_stop:
            if processed_this_invocation >= edge_budget:
                saved = _state(
                    config,
                    phase=phase,
                    cursor_parent_index=parent_index,
                    cursor_representative_index=representative_index,
                    evaluation_index=0,
                    candidates=candidates,
                    accepted_children=accepted,
                    counters=counters,
                )
                return CheckpointAdvance(CheckpointTerminal.CHECKPOINT_SAVED, config, saved)
            parent = records[parent_index]
            representatives = extension_orbit_representatives(spec, parent)
            if representative_index == 0:
                counters["parents_expanded"] += 1
                counters["extension_orbit_representatives"] += len(representatives)
            representative = representatives[representative_index]
            counters["candidate_edges"] += 1
            processed_this_invocation += 1
            child = canonical_multiset(spec, (*parent, representative))
            if canonical_parent(spec, child) != parent:
                counters["canonical_parent_rejections"] += 1
            else:
                if child in candidates:
                    counters["duplicate_children_collapsed"] += 1
                candidates.add(child)
            representative_index += 1
            if representative_index == len(representatives):
                parent_index += 1
                representative_index = 0
        phase = CheckpointPhase.EVALUATE_CANDIDATES
        evaluation_index = 0

    ordered = tuple(sorted(candidates))
    while evaluation_index < len(ordered):
        child = ordered[evaluation_index]
        decision = evaluate_constraints(spec, child, config.profile)
        if decision is ConstraintDecision.CANNOT_CHECK_RESOURCE_BOUND:
            stopped = _state(
                config,
                phase=CheckpointPhase.EVALUATE_CANDIDATES,
                cursor_parent_index=config.range_stop,
                cursor_representative_index=0,
                evaluation_index=evaluation_index,
                candidates=candidates,
                accepted_children=accepted,
                counters=counters,
            )
            return CheckpointAdvance(
                CheckpointTerminal.CANNOT_CHECK_RESOURCE_BOUND, config, stopped
            )
        if decision is ConstraintDecision.PRUNE_SHORT_ZERO_SUM:
            counters["pruned_short_zero_sum"] += 1
        elif decision is ConstraintDecision.PRUNE_K_DISJOINT:
            counters["pruned_k_disjoint"] += 1
        else:
            accepted.append(child)
        evaluation_index += 1
    complete = _state(
        config,
        phase=CheckpointPhase.COMPLETE,
        cursor_parent_index=config.range_stop,
        cursor_representative_index=0,
        evaluation_index=evaluation_index,
        candidates=candidates,
        accepted_children=accepted,
        counters=counters,
    )
    return CheckpointAdvance(CheckpointTerminal.CHECKPOINT_LEVEL_COMPLETE, config, complete)


def _validated_donor_source(
    spec: GroupSpec, records: object, expected_sha256: str
) -> tuple[tuple[Vector, ...], ...]:
    if (spec.p, spec.d) != (5, 3):
        raise RangeManifestError("frozen donor ranges are defined only for C_5^3")
    if not isinstance(records, (list, tuple)):
        raise RangeManifestError("source classes must be a list or tuple")
    parsed = tuple(spec.validate_sequence(record) for record in records)
    if parsed != tuple(sorted(set(parsed))):
        raise RangeManifestError("source classes must be sorted and unique")
    if canonical_records_sha256(parsed) != _checked_digest(expected_sha256, "expected_sha256"):
        raise RangeManifestError("source class manifest digest mismatch")
    if any(record != canonical_multiset(spec, record) for record in parsed):
        raise RangeManifestError("source class is not canonical")
    return parsed


def _single_record_sha256(record: tuple[Vector, ...]) -> str:
    return canonical_records_sha256((record,))


def _donor_output_records(
    spec: GroupSpec,
    classes: tuple[tuple[Vector, ...], ...],
    start: int,
    stop: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    class_entries: list[dict[str, Any]] = []
    output_records: list[dict[str, Any]] = []
    for class_index in range(start, stop):
        source_class = classes[class_index]
        images = declared_donor_images(spec, source_class)
        serialized_images = _records_payload(images)
        class_entries.append(
            {
                "class_index": class_index,
                "source_class_sha256": _single_record_sha256(source_class),
                "donor_image_count": len(images),
                "donor_images_sha256": canonical_json_sha256(serialized_images),
                "donor_images": serialized_images,
            }
        )
        output_records.extend(
            {"class_index": class_index, "image": image} for image in serialized_images
        )
    return class_entries, output_records


def build_donor_range_manifest(
    spec: GroupSpec,
    source_classes: object,
    start: object,
    stop: object,
    *,
    parent_records_sha256: str,
    protocol_sha256: str,
) -> dict[str, Any]:
    classes = _validated_donor_source(spec, source_classes, parent_records_sha256)
    start_index = _checked_nonnegative_int(start, "range start")
    stop_index = _checked_nonnegative_int(stop, "range stop")
    if start_index >= stop_index or stop_index > len(classes):
        raise RangeManifestError("donor range must be nonempty and inside the source class list")
    protocol_digest = _checked_digest(protocol_sha256, "protocol_sha256")
    class_entries, output_records = _donor_output_records(spec, classes, start_index, stop_index)
    payload: dict[str, Any] = {
        "schema_version": "nq-engine-a-donor-range-manifest-v1",
        "terminal": "RANGE_COMPLETE__NOT_GLOBAL",
        "authority": "engineering_donor_range_only",
        "independence_terminal": INDEPENDENCE_TERMINAL,
        "exposure_markers": EXPOSURE_MARKERS,
        "scientific_terminal": "CANNOT_CHECK",
        "group": {"p": spec.p, "d": spec.d},
        "protocol_sha256": protocol_digest,
        "normalization_contract_sha256": NORMALIZATION_CONTRACT_SHA256,
        "source_class_count": len(classes),
        "source_class_manifest_sha256": parent_records_sha256,
        "range": [start_index, stop_index],
        "range_complete": True,
        "full_source_class_coverage": start_index == 0 and stop_index == len(classes),
        "global_coverage": False,
        "class_entries": class_entries,
        "output_record_count": len(output_records),
        "output_sha256": canonical_json_sha256(output_records),
        "output_records": output_records,
    }
    return {**payload, "range_manifest_sha256": canonical_json_sha256(payload)}


def merge_donor_range_manifests(
    spec: GroupSpec,
    source_classes: object,
    manifests: object,
    *,
    expected_ranges: object,
    parent_records_sha256: str,
    protocol_sha256: str,
) -> dict[str, Any]:
    classes = _validated_donor_source(spec, source_classes, parent_records_sha256)
    if not isinstance(expected_ranges, (list, tuple)) or not expected_ranges:
        raise RangeManifestError("expected ranges must be a nonempty ordered sequence")
    ranges: list[tuple[int, int]] = []
    for value in expected_ranges:
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            raise RangeManifestError("expected donor range is invalid")
        start = _checked_nonnegative_int(value[0], "expected range start")
        stop = _checked_nonnegative_int(value[1], "expected range stop")
        if start >= stop:
            raise RangeManifestError("expected donor range must be nonempty")
        ranges.append((start, stop))
    if any(left[1] != right[0] for left, right in pairwise(ranges)):
        raise RangeManifestError("expected donor ranges are not contiguous")
    if ranges[0][0] < 0 or ranges[-1][1] > len(classes):
        raise RangeManifestError("expected donor range cover exceeds the source classes")
    if not isinstance(manifests, (list, tuple)) or len(manifests) != len(ranges):
        raise RangeManifestError("donor range manifest count mismatch")
    verified: list[dict[str, Any]] = []
    for supplied, (start, stop) in zip(manifests, ranges, strict=True):
        if not isinstance(supplied, dict):
            raise RangeManifestError("donor range manifest must be an object")
        expected = build_donor_range_manifest(
            spec,
            classes,
            start,
            stop,
            parent_records_sha256=parent_records_sha256,
            protocol_sha256=protocol_sha256,
        )
        if supplied != expected:
            raise RangeManifestError("donor range manifest failed exact recomputation")
        verified.append(expected)
    merged_records = [record for manifest in verified for record in manifest["output_records"]]
    _, uninterrupted_records = _donor_output_records(spec, classes, ranges[0][0], ranges[-1][1])
    unique = {canonical_json_sha256(record) for record in merged_records}
    equal = merged_records == uninterrupted_records and len(unique) == len(merged_records)
    if not equal:
        raise RangeManifestError("merged donor output differs from uninterrupted union/dedup")
    return {
        "schema_version": "nq-engine-a-donor-range-merge-v1",
        "terminal": "RANGE_COMPLETE__NOT_GLOBAL",
        "authority": "engineering_donor_range_only",
        "independence_terminal": INDEPENDENCE_TERMINAL,
        "exposure_markers": EXPOSURE_MARKERS,
        "scientific_terminal": "CANNOT_CHECK",
        "source_class_manifest_sha256": parent_records_sha256,
        "protocol_sha256": protocol_sha256,
        "covered_range": [ranges[0][0], ranges[-1][1]],
        "range_manifest_sha256": [item["range_manifest_sha256"] for item in verified],
        "output_record_count": len(merged_records),
        "output_sha256": canonical_json_sha256(merged_records),
        "union_dedup_equal_to_uninterrupted": True,
        "global_coverage": False,
    }
