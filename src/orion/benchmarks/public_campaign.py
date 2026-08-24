"""Fail-closed integrity runner for P6-P15 public-data campaigns.

The module validates a frozen campaign bundle.  It deliberately does not infer
independent custody, legal permission, semantic gold correctness, or statistical
power from public availability, hashes, containers, or same-owner execution.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
import hashlib
import json
import math
from pathlib import PurePosixPath
from typing import Callable, Iterable
from urllib.parse import urlparse


class CampaignTerminal(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    CANNOT_CHECK = "CANNOT_CHECK"


class ObservationOutcome(str, Enum):
    PASS = "PASS"
    NULL = "NULL"
    HARMFUL = "HARMFUL"
    FAIL = "FAIL"
    CANNOT_CHECK = "CANNOT_CHECK"


class ArmRole(str, Enum):
    TREATMENT = "TREATMENT"
    BASELINE = "BASELINE"
    ABLATION = "ABLATION"
    EXACT_ORACLE = "EXACT_ORACLE"


class InferenceUnit(str, Enum):
    SOURCE_TASK = "SOURCE_TASK"
    REPOSITORY = "REPOSITORY"
    ONTOLOGY_PAIR = "ONTOLOGY_PAIR"
    TASK_FAMILY = "TASK_FAMILY"


class IntervalMethod(str, Enum):
    PAIRED_BLOCK_BOOTSTRAP = "PAIRED_BLOCK_BOOTSTRAP"
    PAIRED_EXACT = "PAIRED_EXACT"
    CLUSTER_ROBUST_PAIRED = "CLUSTER_ROBUST_PAIRED"


class CustodyMode(str, Enum):
    SAME_OWNER_PUBLIC = "SAME_OWNER_PUBLIC"
    INDEPENDENT_ATTESTED = "INDEPENDENT_ATTESTED"
    PROTECTED_EXTERNAL_ATTESTED = "PROTECTED_EXTERNAL_ATTESTED"


class SurfaceKind(str, Enum):
    MANUSCRIPT = "MANUSCRIPT"
    ACTIVE_AUTHORITY = "ACTIVE_AUTHORITY"
    CLAIM_LEDGER = "CLAIM_LEDGER"
    RESULT = "RESULT"
    RENDERED_PDF = "RENDERED_PDF"


@dataclass(frozen=True)
class SourceBinding:
    source_id: str
    url: str
    pinned_revision: str
    sha256: str
    license_expression: str
    license_url: str
    citation: str
    redistribution_allowed: bool
    redistributed_content: bool
    retrieved_at_utc: str
    task_ids: tuple[str, ...]
    exclusions: tuple[str, ...]


@dataclass(frozen=True)
class ArmSpec:
    arm_id: str
    role: ArmRole
    implementation_sha256: str
    resource_budget: tuple[tuple[str, float], ...]
    model_id: str
    tool_access: tuple[str, ...]


@dataclass(frozen=True)
class EvaluatorBinding:
    evaluator_id: str
    version: str
    artifact_sha256: str
    official: bool


@dataclass(frozen=True)
class GoldBinding:
    gold_id: str
    artifact_sha256: str
    label_schema_sha256: str
    task_ids: tuple[str, ...]
    access_scope: str


@dataclass(frozen=True)
class CustodyBinding:
    mode: CustodyMode
    execution_owner_id: str
    evaluator_custodian_id: str
    attestation_sha256: str


@dataclass(frozen=True)
class CampaignFreeze:
    campaign_id: str
    paper_ids: tuple[str, ...]
    protocol_sha256: str
    frozen_at_utc: str
    inference_unit: InferenceUnit
    inference_unit_assignments: tuple[tuple[str, str], ...]
    split_assignments: tuple[tuple[str, str], ...]
    estimand: str
    gate: str
    sources: tuple[SourceBinding, ...]
    arms: tuple[ArmSpec, ...]
    evaluator: EvaluatorBinding
    gold: GoldBinding
    custody: CustodyBinding
    seeds: tuple[int, ...]


@dataclass(frozen=True)
class SourceFetchReceipt:
    source_id: str
    terminal: CampaignTerminal
    observed_sha256: str
    blocker: str


@dataclass(frozen=True)
class Observation:
    task_id: str
    split_id: str
    arm_id: str
    seed: int
    inference_unit_id: str
    outcome: ObservationOutcome
    raw_output_sha256: str
    raw_output_retained: bool
    evaluator_version: str
    environment: tuple[tuple[str, str], ...]
    resource_usage: tuple[tuple[str, float], ...]

    @property
    def record_id(self) -> str:
        return f"{self.task_id}|{self.split_id}|{self.arm_id}|{self.seed}"


@dataclass(frozen=True)
class GateResult:
    terminal: CampaignTerminal
    decision_id: str
    evaluator_output_sha256: str
    included_record_count: int
    included_record_ids_sha256: str
    included_raw_outputs_sha256: str
    included_observations_sha256: str
    subject_arm_id: str
    comparator_arm_id: str
    interval_method: IntervalMethod
    confidence_level: float
    inference_unit_count: int
    effect_estimate: float
    ci_lower: float
    ci_upper: float
    subject_cost: float
    comparator_cost: float
    cost_ratio: float
    omitted_record_ids: tuple[str, ...]
    rationale: str


@dataclass(frozen=True)
class ReplayBinding:
    fresh_container: bool
    container_image_sha256: str
    original_environment_sha256: str
    replay_environment_sha256: str
    original_predictions_sha256: str
    replay_predictions_sha256: str
    original_result_sha256: str
    replay_result_sha256: str
    gate_result_sha256: str


@dataclass(frozen=True)
class AuthoritySurface:
    kind: SurfaceKind
    path: str
    file_sha256: str
    declared_terminal: CampaignTerminal
    evidence_sha256: str


@dataclass(frozen=True)
class CampaignReceipt:
    campaign_id: str
    terminal: CampaignTerminal
    blockers: tuple[str, ...]
    gate_rationale: str
    observation_counts: tuple[tuple[str, int], ...]
    source_receipts: tuple[SourceFetchReceipt, ...]
    freeze_sha256: str
    observations_sha256: str
    gate_result_sha256: str
    replay_sha256: str
    authority_surfaces_sha256: str
    independent_authority: str
    authority_boundary: str
    receipt_sha256: str


Fetcher = Callable[[SourceBinding], bytes]
SurfaceReader = Callable[[str], bytes]
SurfaceTextReader = Callable[[str], str]

_PAPER_IDS = frozenset(f"P{number}" for number in range(6, 16))
_REQUIRED_ENVIRONMENT = frozenset(
    {"container_image_sha256", "os", "runtime", "dependency_lock_sha256"}
)
_UNKNOWN_LICENSE_MARKERS = ("UNKNOWN", "CANNOT_CHECK", "UNLICENSED", "TBD")
_UNKNOWN_IDENTITY_MARKERS = frozenset(
    {"UNKNOWN", "CANNOT_CHECK", "TBD", "UNSET", "N/A", "NA", "NULL"}
)
_SURFACE_BINDING_PREFIX = b"ORION_SURFACE_BINDING_V1|"


def _valid_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _valid_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _identity_missing(value: str, *, allow_none: bool = False) -> bool:
    normalized = value.strip().upper()
    if not normalized:
        return True
    if normalized == "NONE":
        return not allow_none
    return normalized in _UNKNOWN_IDENTITY_MARKERS


def _timestamp(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        return None
    return parsed


def _canonical_sha256(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _source_metadata_blockers(source: SourceBinding) -> list[str]:
    blockers: list[str] = []
    prefix = f"source:{source.source_id or '<missing>'}"
    if _identity_missing(source.source_id):
        blockers.append("source_id_missing")
    if not _valid_url(source.url):
        blockers.append(f"{prefix}:url_invalid")
    if _identity_missing(source.pinned_revision):
        blockers.append(f"{prefix}:pinned_revision_missing")
    if not _valid_sha256(source.sha256):
        blockers.append(f"{prefix}:sha256_invalid")
    license_upper = source.license_expression.upper()
    if not source.license_expression.strip() or any(
        marker in license_upper for marker in _UNKNOWN_LICENSE_MARKERS
    ):
        blockers.append(f"{prefix}:license_ambiguous")
    if not _valid_url(source.license_url):
        blockers.append(f"{prefix}:license_url_invalid")
    if not source.citation.strip():
        blockers.append(f"{prefix}:citation_missing")
    if _timestamp(source.retrieved_at_utc) is None:
        blockers.append(f"{prefix}:retrieval_time_invalid")
    if not source.task_ids or any(not item.strip() for item in source.task_ids):
        blockers.append(f"{prefix}:task_ids_missing")
    if len(source.task_ids) != len(set(source.task_ids)):
        blockers.append(f"{prefix}:task_ids_duplicated")
    if source.redistributed_content and not source.redistribution_allowed:
        blockers.append(f"{prefix}:redistribution_prohibited")
    return blockers


def fetch_and_hash_sources(
    freeze: CampaignFreeze,
    fetcher: Fetcher,
) -> tuple[SourceFetchReceipt, ...]:
    """Fetch source bytes without writing them and bind each to the frozen hash.

    A source with incomplete licence metadata is not fetched.  The caller owns
    any cache and must independently comply with upstream terms.
    """

    receipts: list[SourceFetchReceipt] = []
    for source in freeze.sources:
        blockers = _source_metadata_blockers(source)
        if blockers:
            receipts.append(
                SourceFetchReceipt(
                    source_id=source.source_id,
                    terminal=CampaignTerminal.CANNOT_CHECK,
                    observed_sha256="",
                    blocker=";".join(blockers),
                )
            )
            continue
        try:
            payload = fetcher(source)
        except Exception as exc:  # external fetch failures are evidence gaps
            receipts.append(
                SourceFetchReceipt(
                    source_id=source.source_id,
                    terminal=CampaignTerminal.CANNOT_CHECK,
                    observed_sha256="",
                    blocker=f"fetch_failed:{type(exc).__name__}",
                )
            )
            continue
        observed = hashlib.sha256(payload).hexdigest()
        if observed != source.sha256:
            receipts.append(
                SourceFetchReceipt(
                    source_id=source.source_id,
                    terminal=CampaignTerminal.CANNOT_CHECK,
                    observed_sha256=observed,
                    blocker="source_hash_mismatch",
                )
            )
        else:
            receipts.append(
                SourceFetchReceipt(
                    source_id=source.source_id,
                    terminal=CampaignTerminal.PASS,
                    observed_sha256=observed,
                    blocker="",
                )
            )
    return tuple(receipts)


def _freeze_blockers(freeze: CampaignFreeze, result_created_at_utc: str) -> list[str]:
    blockers: list[str] = []
    if not freeze.campaign_id.strip():
        blockers.append("campaign_id_missing")
    if not freeze.paper_ids or not set(freeze.paper_ids).issubset(_PAPER_IDS):
        blockers.append("paper_scope_must_be_p6_through_p15")
    if len(freeze.paper_ids) != len(set(freeze.paper_ids)):
        blockers.append("paper_ids_duplicated")
    if not _valid_sha256(freeze.protocol_sha256):
        blockers.append("protocol_sha256_invalid")
    frozen_at = _timestamp(freeze.frozen_at_utc)
    result_at = _timestamp(result_created_at_utc)
    if frozen_at is None or result_at is None or frozen_at >= result_at:
        blockers.append("protocol_not_frozen_before_result")
    if not isinstance(freeze.inference_unit, InferenceUnit):
        blockers.append("inference_unit_not_allowed")
    if not freeze.estimand.strip() or not freeze.gate.strip():
        blockers.append("estimand_or_gate_missing")
    if not freeze.sources:
        blockers.append("sources_missing")
    source_ids = [source.source_id for source in freeze.sources]
    if len(source_ids) != len(set(source_ids)):
        blockers.append("source_ids_duplicated")
    for source in freeze.sources:
        blockers.extend(_source_metadata_blockers(source))
        retrieved_at = _timestamp(source.retrieved_at_utc)
        if retrieved_at is not None and result_at is not None and retrieved_at >= result_at:
            blockers.append(f"source:{source.source_id}:retrieved_not_before_result")

    source_tasks = [task for source in freeze.sources for task in source.task_ids]
    if len(source_tasks) != len(set(source_tasks)):
        blockers.append("task_id_bound_to_multiple_sources")
    assignments = dict(freeze.split_assignments)
    if len(assignments) != len(freeze.split_assignments):
        blockers.append("task_split_assignment_duplicated")
    if set(assignments) != set(source_tasks):
        blockers.append("frozen_task_split_coverage_mismatch")
    if any(not split.strip() for split in assignments.values()):
        blockers.append("split_id_missing")
    unit_assignments = dict(freeze.inference_unit_assignments)
    if len(unit_assignments) != len(freeze.inference_unit_assignments):
        blockers.append("inference_unit_assignment_duplicated")
    if set(unit_assignments) != set(source_tasks):
        blockers.append("inference_unit_task_coverage_mismatch")
    if any(not unit_id.strip() for unit_id in unit_assignments.values()):
        blockers.append("inference_unit_identity_missing")
    if freeze.inference_unit is InferenceUnit.SOURCE_TASK and any(
        unit_assignments.get(task_id) != task_id for task_id in source_tasks
    ):
        blockers.append("source_task_inference_units_must_equal_frozen_task_ids")

    if not freeze.arms:
        blockers.append("arms_missing")
    arm_ids = [arm.arm_id for arm in freeze.arms]
    if len(arm_ids) != len(set(arm_ids)) or any(not item.strip() for item in arm_ids):
        blockers.append("arm_ids_invalid_or_duplicated")
    roles = [arm.role for arm in freeze.arms]
    if ArmRole.TREATMENT not in roles or not any(
        role in {ArmRole.BASELINE, ArmRole.EXACT_ORACLE} for role in roles
    ):
        blockers.append("treatment_and_strong_comparator_required")
    budgets = [tuple(sorted(arm.resource_budget)) for arm in freeze.arms]
    if not budgets or any(not budget for budget in budgets) or len(set(budgets)) != 1:
        blockers.append("arm_resource_budgets_not_exactly_matched")
    tool_access = [tuple(sorted(arm.tool_access)) for arm in freeze.arms]
    if tool_access and len(set(tool_access)) != 1:
        blockers.append("arm_tool_access_not_exactly_matched")
    model_ids = [arm.model_id for arm in freeze.arms]
    if model_ids and len(set(model_ids)) != 1:
        blockers.append("arm_models_not_exactly_matched")
    for arm in freeze.arms:
        if not _valid_sha256(arm.implementation_sha256):
            blockers.append(f"arm:{arm.arm_id}:implementation_sha256_invalid")
        if _identity_missing(arm.model_id, allow_none=True):
            blockers.append(f"arm:{arm.arm_id}:model_identity_missing")
        if (
            not arm.tool_access
            or any(not tool.strip() for tool in arm.tool_access)
            or len(arm.tool_access) != len(set(arm.tool_access))
        ):
            blockers.append(f"arm:{arm.arm_id}:tool_access_missing_or_invalid")
        budget_keys = [key for key, _ in arm.resource_budget]
        if len(budget_keys) != len(set(budget_keys)):
            blockers.append(f"arm:{arm.arm_id}:resource_budget_fields_duplicated")
        if any(
            not key.strip() or not math.isfinite(value) or value < 0
            for key, value in arm.resource_budget
        ):
            blockers.append(f"arm:{arm.arm_id}:resource_budget_invalid")

    if not freeze.evaluator.official:
        blockers.append("official_evaluator_required")
    if _identity_missing(freeze.evaluator.evaluator_id) or _identity_missing(
        freeze.evaluator.version
    ):
        blockers.append("evaluator_identity_or_version_missing")
    if not _valid_sha256(freeze.evaluator.artifact_sha256):
        blockers.append("evaluator_sha256_invalid")
    if not freeze.gold.gold_id.strip() or not freeze.gold.access_scope.strip():
        blockers.append("gold_identity_or_access_scope_missing")
    if not _valid_sha256(freeze.gold.artifact_sha256):
        blockers.append("gold_artifact_sha256_invalid")
    if not _valid_sha256(freeze.gold.label_schema_sha256):
        blockers.append("gold_label_schema_sha256_invalid")
    if set(freeze.gold.task_ids) != set(source_tasks):
        blockers.append("gold_task_coverage_mismatch")
    if not isinstance(freeze.custody.mode, CustodyMode):
        blockers.append("custody_mode_missing_or_invalid")
    if (
        _identity_missing(freeze.custody.execution_owner_id)
        or _identity_missing(freeze.custody.evaluator_custodian_id)
    ):
        blockers.append("custody_identity_missing")
    if freeze.custody.mode in {
        CustodyMode.INDEPENDENT_ATTESTED,
        CustodyMode.PROTECTED_EXTERNAL_ATTESTED,
    } and not _valid_sha256(freeze.custody.attestation_sha256):
        blockers.append("external_custody_attestation_sha256_invalid")
    if (
        freeze.custody.mode
        in {
            CustodyMode.INDEPENDENT_ATTESTED,
            CustodyMode.PROTECTED_EXTERNAL_ATTESTED,
        }
        and freeze.custody.execution_owner_id.strip()
        == freeze.custody.evaluator_custodian_id.strip()
    ):
        blockers.append("external_custody_owner_and_custodian_must_differ")
    if not freeze.seeds or len(freeze.seeds) != len(set(freeze.seeds)):
        blockers.append("seeds_missing_or_duplicated")
    return blockers


def _observation_blockers(
    freeze: CampaignFreeze,
    observations: tuple[Observation, ...],
) -> list[str]:
    blockers: list[str] = []
    assignments = dict(freeze.split_assignments)
    unit_assignments = dict(freeze.inference_unit_assignments)
    arm_ids = {arm.arm_id for arm in freeze.arms}
    arms_by_id = {arm.arm_id: arm for arm in freeze.arms}
    expected = {
        (task_id, split_id, arm_id, seed)
        for task_id, split_id in freeze.split_assignments
        for arm_id in arm_ids
        for seed in freeze.seeds
    }
    observed_keys = [
        (item.task_id, item.split_id, item.arm_id, item.seed) for item in observations
    ]
    observed = set(observed_keys)
    if len(observed_keys) != len(observed):
        blockers.append("execution_records_duplicated")
    if observed != expected:
        blockers.append("execution_record_cartesian_coverage_mismatch")

    for item in observations:
        prefix = f"record:{item.record_id}"
        if assignments.get(item.task_id) != item.split_id:
            blockers.append(f"{prefix}:split_drift")
        if item.arm_id not in arm_ids or item.seed not in freeze.seeds:
            blockers.append(f"{prefix}:unfrozen_arm_or_seed")
        if not item.inference_unit_id.strip():
            blockers.append(f"{prefix}:inference_unit_id_missing")
        if unit_assignments.get(item.task_id) != item.inference_unit_id:
            blockers.append(f"{prefix}:inference_unit_identity_drift")
        if not isinstance(item.outcome, ObservationOutcome):
            blockers.append(f"{prefix}:outcome_invalid")
        if not _valid_sha256(item.raw_output_sha256):
            blockers.append(f"{prefix}:raw_output_sha256_invalid")
        if not item.raw_output_retained:
            blockers.append(f"{prefix}:raw_output_not_retained")
        if item.evaluator_version != freeze.evaluator.version:
            blockers.append(f"{prefix}:evaluator_version_drift")
        environment = dict(item.environment)
        if len(environment) != len(item.environment):
            blockers.append(f"{prefix}:environment_fields_duplicated")
        if not _REQUIRED_ENVIRONMENT.issubset(environment):
            blockers.append(f"{prefix}:environment_incomplete")
        if any(_identity_missing(environment.get(key, "")) for key in _REQUIRED_ENVIRONMENT):
            blockers.append(f"{prefix}:environment_value_missing")
        for key in ("container_image_sha256", "dependency_lock_sha256"):
            if key in environment and not _valid_sha256(environment[key]):
                blockers.append(f"{prefix}:{key}_invalid")
        usage_keys = [key for key, _ in item.resource_usage]
        if len(usage_keys) != len(set(usage_keys)):
            blockers.append(f"{prefix}:resource_usage_fields_duplicated")
        if any(
            not key.strip() or not math.isfinite(value) or value < 0
            for key, value in item.resource_usage
        ):
            blockers.append(f"{prefix}:resource_usage_invalid")
        usage = dict(item.resource_usage)
        if "cost" not in usage:
            blockers.append(f"{prefix}:cost_missing")
        arm = arms_by_id.get(item.arm_id)
        if arm is not None:
            budget_dimensions = {dimension for dimension, _ in arm.resource_budget}
            if set(usage) != budget_dimensions | {"cost"}:
                blockers.append(f"{prefix}:unfrozen_resource_dimension")
            for dimension, ceiling in arm.resource_budget:
                if dimension not in usage:
                    blockers.append(f"{prefix}:budget_dimension_missing:{dimension}")
                elif math.isfinite(usage[dimension]) and usage[dimension] > ceiling:
                    blockers.append(f"{prefix}:resource_budget_exceeded:{dimension}")
    unit_ids_by_case: dict[tuple[str, str, int], set[str]] = {}
    for item in observations:
        unit_ids_by_case.setdefault((item.task_id, item.split_id, item.seed), set()).add(
            item.inference_unit_id
        )
    if any(len(unit_ids) != 1 for unit_ids in unit_ids_by_case.values()):
        blockers.append("paired_arms_disagree_on_inference_unit_identity")
    environments_by_case: dict[tuple[str, str, int], set[str]] = {}
    for item in observations:
        environments_by_case.setdefault((item.task_id, item.split_id, item.seed), set()).add(
            _canonical_sha256(sorted(item.environment))
        )
    if any(len(environments) != 1 for environments in environments_by_case.values()):
        blockers.append("paired_arms_disagree_on_environment")
    return blockers


def _observation_binding_rows(
    observations: tuple[Observation, ...],
) -> list[tuple[str, str, str, str]]:
    return sorted(
        (
            item.record_id,
            item.raw_output_sha256,
            item.outcome.value
            if isinstance(item.outcome, ObservationOutcome)
            else str(item.outcome),
            item.inference_unit_id,
        )
        for item in observations
    )


def _environment_bundle_sha256(observations: tuple[Observation, ...]) -> str:
    return _canonical_sha256(
        sorted((item.record_id, sorted(item.environment)) for item in observations)
    )


def _replay_blockers(
    replay: ReplayBinding,
    gate_result: GateResult,
    observations: tuple[Observation, ...],
) -> list[str]:
    blockers: list[str] = []
    digest_fields = {
        "container_image": replay.container_image_sha256,
        "original_environment": replay.original_environment_sha256,
        "replay_environment": replay.replay_environment_sha256,
        "original_predictions": replay.original_predictions_sha256,
        "replay_predictions": replay.replay_predictions_sha256,
        "original_result": replay.original_result_sha256,
        "replay_result": replay.replay_result_sha256,
        "gate_result": replay.gate_result_sha256,
    }
    for field, value in digest_fields.items():
        if not _valid_sha256(value):
            blockers.append(f"replay:{field}_sha256_invalid")
    if not replay.fresh_container:
        blockers.append("replay:not_fresh_container")
    if replay.original_predictions_sha256 != replay.replay_predictions_sha256:
        blockers.append("replay:prediction_digest_mismatch")
    if replay.original_result_sha256 != replay.replay_result_sha256:
        blockers.append("replay:result_digest_mismatch")
    expected_predictions = _canonical_sha256(_observation_binding_rows(observations))
    if replay.original_predictions_sha256 != expected_predictions:
        blockers.append("replay:predictions_not_bound_to_execution_records")
    expected_environment = _environment_bundle_sha256(observations)
    if replay.original_environment_sha256 != expected_environment:
        blockers.append("replay:original_environment_not_bound_to_execution_records")
    if replay.replay_environment_sha256 != expected_environment:
        blockers.append("replay:environment_digest_mismatch")
    if replay.original_result_sha256 != gate_result.evaluator_output_sha256:
        blockers.append("replay:original_result_not_bound_to_gate")
    if replay.replay_result_sha256 != gate_result.evaluator_output_sha256:
        blockers.append("replay:replay_result_not_bound_to_gate")
    if replay.gate_result_sha256 != _canonical_sha256(asdict(gate_result)):
        blockers.append("replay:gate_result_digest_mismatch")
    for item in observations:
        environment = dict(item.environment)
        if environment.get("container_image_sha256") != replay.container_image_sha256:
            blockers.append(f"record:{item.record_id}:container_image_not_bound_to_replay")
    return blockers


def _surface_blockers(
    surfaces: tuple[AuthoritySurface, ...],
    gate_result: GateResult,
    surface_reader: SurfaceReader,
    surface_text_reader: SurfaceTextReader,
) -> list[str]:
    blockers: list[str] = []
    kinds = [surface.kind for surface in surfaces]
    if Counter(kinds) != Counter(SurfaceKind):
        blockers.append("authority_surface_set_incomplete_or_duplicated")
    paths = [surface.path for surface in surfaces]
    if len(paths) != len(set(paths)):
        blockers.append("authority_surface_paths_aliased")
    if len({surface.file_sha256 for surface in surfaces}) != len(surfaces):
        blockers.append("authority_surface_file_hashes_aliased")
    for surface in surfaces:
        prefix = f"surface:{getattr(surface.kind, 'value', surface.kind)}"
        parsed_path = PurePosixPath(surface.path)
        if (
            not surface.path.strip()
            or parsed_path.is_absolute()
            or ".." in parsed_path.parts
            or str(parsed_path) != surface.path
            or not _valid_sha256(surface.file_sha256)
        ):
            blockers.append(f"{prefix}:path_or_file_sha256_invalid")
        terminal_value = (
            surface.declared_terminal.value
            if isinstance(surface.declared_terminal, CampaignTerminal)
            else str(surface.declared_terminal)
        )
        semantic_marker = (
            f"ORION_SURFACE_BINDING_V1|{terminal_value}|{surface.evidence_sha256}"
        ).encode("ascii")
        try:
            surface_bytes = surface_reader(surface.path)
            observed_file_sha256 = hashlib.sha256(surface_bytes).hexdigest()
        except Exception as exc:
            blockers.append(f"{prefix}:read_failed:{type(exc).__name__}")
        else:
            if observed_file_sha256 != surface.file_sha256:
                blockers.append(f"{prefix}:file_sha256_mismatch")
            raw_markers = [
                line.strip()
                for line in surface_bytes.splitlines()
                if _SURFACE_BINDING_PREFIX in line
            ]
            if raw_markers != [semantic_marker]:
                blockers.append(f"{prefix}:semantic_binding_missing_or_mismatched")
        try:
            extracted_text = surface_text_reader(surface.path)
        except Exception as exc:
            blockers.append(f"{prefix}:text_extract_failed:{type(exc).__name__}")
        else:
            text_marker = semantic_marker.decode("ascii")
            extracted_markers = [
                line.strip()
                for line in extracted_text.splitlines()
                if "ORION_SURFACE_BINDING_V1|" in line
            ]
            if extracted_markers != [text_marker]:
                blockers.append(f"{prefix}:extracted_semantic_binding_mismatch")
        if surface.declared_terminal is not gate_result.terminal:
            blockers.append(f"{prefix}:terminal_mismatch")
        if surface.evidence_sha256 != gate_result.evaluator_output_sha256:
            blockers.append(f"{prefix}:evidence_digest_mismatch")
    return blockers


def run_fail_closed_campaign(
    *,
    freeze: CampaignFreeze,
    source_receipts: Iterable[SourceFetchReceipt],
    observations: Iterable[Observation],
    gate_result: GateResult,
    replay: ReplayBinding,
    authority_surfaces: Iterable[AuthoritySurface],
    surface_reader: SurfaceReader,
    surface_text_reader: SurfaceTextReader,
    result_created_at_utc: str,
) -> CampaignReceipt:
    """Audit a complete campaign bundle and emit PASS/FAIL/CANNOT_CHECK.

    PASS is only the frozen local/public scientific gate.  Independent and
    protected authority always remains CANNOT_CHECK at this layer.
    """

    source_receipts = tuple(sorted(source_receipts, key=lambda item: item.source_id))
    observations = tuple(sorted(observations, key=lambda item: item.record_id))
    authority_surfaces = tuple(
        sorted(
            authority_surfaces,
            key=lambda item: str(getattr(item.kind, "value", item.kind)),
        )
    )
    blockers = _freeze_blockers(freeze, result_created_at_utc)

    receipt_ids = [receipt.source_id for receipt in source_receipts]
    if Counter(receipt_ids) != Counter(source.source_id for source in freeze.sources):
        blockers.append("source_fetch_receipts_incomplete_or_duplicated")
    for receipt in source_receipts:
        source = next(
            (item for item in freeze.sources if item.source_id == receipt.source_id), None
        )
        if receipt.terminal is not CampaignTerminal.PASS:
            blockers.append(f"source:{receipt.source_id}:fetch_or_hash_not_pass")
        elif source is None or receipt.observed_sha256 != source.sha256:
            blockers.append(f"source:{receipt.source_id}:receipt_hash_mismatch")
        elif receipt.blocker:
            blockers.append(f"source:{receipt.source_id}:pass_receipt_contains_blocker")

    blockers.extend(_observation_blockers(freeze, observations))
    blockers.extend(_replay_blockers(replay, gate_result, observations))

    if not gate_result.decision_id.strip() or not gate_result.rationale.strip():
        blockers.append("gate_identity_or_rationale_missing")
    if not isinstance(gate_result.terminal, CampaignTerminal):
        blockers.append("gate_terminal_invalid")
    if not _valid_sha256(gate_result.evaluator_output_sha256):
        blockers.append("gate_evaluator_output_sha256_invalid")
    if gate_result.included_record_count != len(observations):
        blockers.append("gate_did_not_include_every_execution_record")
    expected_record_ids_sha256 = _canonical_sha256(
        sorted(item.record_id for item in observations)
    )
    if gate_result.included_record_ids_sha256 != expected_record_ids_sha256:
        blockers.append("gate_record_identity_binding_mismatch")
    expected_raw_outputs_sha256 = _canonical_sha256(
        sorted(item.raw_output_sha256 for item in observations)
    )
    if gate_result.included_raw_outputs_sha256 != expected_raw_outputs_sha256:
        blockers.append("gate_raw_output_binding_mismatch")
    expected_observations_sha256 = _canonical_sha256(
        _observation_binding_rows(observations)
    )
    if gate_result.included_observations_sha256 != expected_observations_sha256:
        blockers.append("gate_observation_association_binding_mismatch")
    if gate_result.omitted_record_ids:
        blockers.append("gate_omitted_execution_records")

    arms_by_id = {arm.arm_id: arm for arm in freeze.arms}
    subject = arms_by_id.get(gate_result.subject_arm_id)
    comparator = arms_by_id.get(gate_result.comparator_arm_id)
    if subject is None or subject.role is not ArmRole.TREATMENT:
        blockers.append("gate_subject_arm_not_frozen_treatment")
    if comparator is None or comparator.role not in {
        ArmRole.BASELINE,
        ArmRole.EXACT_ORACLE,
    }:
        blockers.append("gate_comparator_arm_not_frozen_comparator")
    if not isinstance(gate_result.interval_method, IntervalMethod):
        blockers.append("gate_interval_method_not_paired_or_blocked")
    if not math.isclose(gate_result.confidence_level, 0.95):
        blockers.append("gate_confidence_level_not_95_percent")
    numeric_values = (
        gate_result.effect_estimate,
        gate_result.ci_lower,
        gate_result.ci_upper,
        gate_result.subject_cost,
        gate_result.comparator_cost,
        gate_result.cost_ratio,
    )
    if not all(math.isfinite(value) for value in numeric_values):
        blockers.append("gate_nonfinite_estimate_interval_or_cost")
    if not gate_result.ci_lower <= gate_result.effect_estimate <= gate_result.ci_upper:
        blockers.append("gate_confidence_interval_order_invalid")

    frozen_inference_units = set(dict(freeze.inference_unit_assignments).values())
    if gate_result.inference_unit_count != len(frozen_inference_units):
        blockers.append("gate_inference_unit_count_mismatch")
    costs_by_arm: dict[str, float] = {}
    for item in observations:
        costs_by_arm[item.arm_id] = costs_by_arm.get(item.arm_id, 0.0) + dict(
            item.resource_usage
        ).get("cost", 0.0)
    observed_subject_cost = costs_by_arm.get(gate_result.subject_arm_id)
    observed_comparator_cost = costs_by_arm.get(gate_result.comparator_arm_id)
    if observed_subject_cost is None or not math.isclose(
        gate_result.subject_cost, observed_subject_cost
    ):
        blockers.append("gate_subject_cost_mismatch")
    if observed_comparator_cost is None or not math.isclose(
        gate_result.comparator_cost, observed_comparator_cost
    ):
        blockers.append("gate_comparator_cost_mismatch")
    expected_cost_ratio = (
        math.inf
        if gate_result.comparator_cost == 0 and gate_result.subject_cost > 0
        else (
            1.0
            if gate_result.comparator_cost == 0
            else gate_result.subject_cost / gate_result.comparator_cost
        )
    )
    if not math.isfinite(expected_cost_ratio) or not math.isclose(
        gate_result.cost_ratio, expected_cost_ratio
    ):
        blockers.append("gate_cost_ratio_mismatch")
    blockers.extend(
        _surface_blockers(
            authority_surfaces,
            gate_result,
            surface_reader,
            surface_text_reader,
        )
    )

    blockers = list(dict.fromkeys(blockers))
    terminal = CampaignTerminal.CANNOT_CHECK if blockers else gate_result.terminal
    counts = Counter(
        item.outcome.value if isinstance(item.outcome, ObservationOutcome) else "INVALID"
        for item in observations
    )
    freeze_sha256 = _canonical_sha256(asdict(freeze))
    observations_sha256 = _canonical_sha256([asdict(item) for item in observations])
    gate_result_sha256 = _canonical_sha256(asdict(gate_result))
    replay_sha256 = _canonical_sha256(asdict(replay))
    authority_surfaces_sha256 = _canonical_sha256(
        [asdict(item) for item in authority_surfaces]
    )
    unsigned = {
        "campaign_id": freeze.campaign_id,
        "terminal": terminal.value,
        "blockers": blockers,
        "gate_rationale": gate_result.rationale,
        "observation_counts": sorted(counts.items()),
        "source_receipts": [asdict(item) for item in source_receipts],
        "freeze_sha256": freeze_sha256,
        "observations_sha256": observations_sha256,
        "gate_result_sha256": gate_result_sha256,
        "replay_sha256": replay_sha256,
        "authority_surfaces_sha256": authority_surfaces_sha256,
        "independent_authority": "CANNOT_CHECK",
        "authority_boundary": (
            "Public availability, hashes, official evaluators, containers and "
            "same-owner replay do not establish protected custody, independent "
            "semantic adjudication, external proof review or legal permission."
        ),
    }
    return CampaignReceipt(
        campaign_id=freeze.campaign_id,
        terminal=terminal,
        blockers=tuple(blockers),
        gate_rationale=gate_result.rationale,
        observation_counts=tuple(sorted(counts.items())),
        source_receipts=source_receipts,
        freeze_sha256=freeze_sha256,
        observations_sha256=observations_sha256,
        gate_result_sha256=gate_result_sha256,
        replay_sha256=replay_sha256,
        authority_surfaces_sha256=authority_surfaces_sha256,
        independent_authority="CANNOT_CHECK",
        authority_boundary=unsigned["authority_boundary"],
        receipt_sha256=_canonical_sha256(unsigned),
    )


__all__ = [
    "ArmRole",
    "ArmSpec",
    "AuthoritySurface",
    "CampaignFreeze",
    "CampaignReceipt",
    "CampaignTerminal",
    "CustodyBinding",
    "CustodyMode",
    "EvaluatorBinding",
    "GateResult",
    "GoldBinding",
    "InferenceUnit",
    "IntervalMethod",
    "Observation",
    "ObservationOutcome",
    "ReplayBinding",
    "SourceBinding",
    "SourceFetchReceipt",
    "SurfaceReader",
    "SurfaceTextReader",
    "SurfaceKind",
    "fetch_and_hash_sources",
    "run_fail_closed_campaign",
]
