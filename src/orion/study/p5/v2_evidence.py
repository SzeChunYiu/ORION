from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
import json
from typing import Any, Iterable

from orion.transfer.staging import (
    CandidateRecord,
    CandidateVerdict,
    MultiStageCandidateGate,
    Stage,
    StageResult,
    StageVerdict,
)


RUN_SCHEMA_VERSION = "orion.p5.staged-acceptance-run-manifest.v2"
ARCHIVE_SCHEMA_VERSION = "orion.p5.staged-result-archive.v2"
RECORD_SCHEMA_VERSION = "orion.p5.staged-result-record.v2"
PROTOCOL_ID = "P5.hidden-cause-staged-acceptance.v2"
V2_SYSTEM_ID = "self_orion_v2_staged_acceptance"

REQUIRED_SPLITS = ("motivating", "replay", "fresh", "protected")
REQUIRED_RESOURCE_KEYS = (
    "max_candidates",
    "max_model_tokens",
    "max_tool_calls",
    "max_wallclock_seconds",
    "max_evaluator_calls",
)
MANDATORY_EXECUTABLE_BASELINES = {
    "p5_v1_acceptance",
    "pace_anytime_valid_acceptance",
    "greedy_accept_if_score_up",
    "direct_self_edit_with_heldout_acceptance",
    "evaluator_only_acceptance",
}
ALLOWED_DISPOSITIONS = {
    "UPSTREAM_PINNED",
    "PROTOCOL_REIMPLEMENTED",
    "NOT_EXECUTABLE_WITH_JUSTIFICATION",
}
ALLOWED_ARM_KINDS = {"SUBJECT", "BASELINE", "ABLATION"}
ALLOWED_DECISIONS = {"ACCEPT", "REJECT", "CANNOT_CHECK"}
HEX = set("0123456789abcdef")


def canonical_bytes(payload: Any) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def content_digest(payload: Any) -> str:
    return sha256(canonical_bytes(payload)).hexdigest()


def _is_lower_hex(value: object, length: int) -> bool:
    return (
        isinstance(value, str)
        and len(value) == length
        and all(ch in HEX for ch in value)
    )


def _iter_unbound(value: Any, path: str = "$") -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _iter_unbound(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _iter_unbound(child, f"{path}[{index}]")
    elif isinstance(value, str) and "UNBOUND" in value.upper():
        yield path


def unbound_paths(payload: Any) -> tuple[str, ...]:
    return tuple(sorted(_iter_unbound(payload)))


def _require_sha256(
    value: object,
    field: str,
    errors: list[str],
) -> None:
    if not _is_lower_hex(value, 64):
        errors.append(f"{field} must be a 64-character lowercase SHA-256 digest")


def _require_nonempty_string(
    value: object,
    field: str,
    errors: list[str],
) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field} must be a non-empty string")


def required_arm_kinds(protocol: dict[str, Any]) -> dict[str, str]:
    required: dict[str, str] = {V2_SYSTEM_ID: "SUBJECT"}
    for baseline in protocol.get("baselines", ()):
        required[str(baseline)] = "BASELINE"
    for ablation in protocol.get("ablations", ()):
        required[str(ablation)] = "ABLATION"
    return required


def validate_run_manifest(
    manifest: dict[str, Any],
    protocol: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    if protocol.get("protocol_id") != PROTOCOL_ID:
        errors.append("unexpected P5 V2 protocol_id")
    if protocol.get("outcome_accessed") is not False:
        errors.append("P5 V2 protocol must remain outcome-blind before run freeze")

    if manifest.get("schema_version") != RUN_SCHEMA_VERSION:
        errors.append("wrong P5 V2 run-manifest schema_version")
    if manifest.get("paper_id") != "P5":
        errors.append("P5 V2 run manifest must have paper_id=P5")
    if manifest.get("protocol_id") != PROTOCOL_ID:
        errors.append("P5 V2 run manifest protocol_id mismatch")
    if manifest.get("protocol_digest") != content_digest(protocol):
        errors.append("protocol_digest does not bind the exact P5 V2 protocol")
    if manifest.get("created_before_outcome_access") is not True:
        errors.append("run manifest must be created_before_outcome_access=true")

    subject = manifest.get("subject_revision")
    if not _is_lower_hex(subject, 40):
        errors.append(
            "subject_revision must be a full 40-character lowercase git SHA"
        )

    _require_sha256(
        manifest.get("hidden_cause_suite_hash"),
        "hidden_cause_suite_hash",
        errors,
    )
    _require_sha256(
        manifest.get("access_policy_hash"),
        "access_policy_hash",
        errors,
    )
    _require_sha256(
        manifest.get("negative_history_root_hash"),
        "negative_history_root_hash",
        errors,
    )
    _require_nonempty_string(manifest.get("artifact_root"), "artifact_root", errors)

    split_hashes = manifest.get("split_hashes")
    if not isinstance(split_hashes, dict):
        errors.append("split_hashes must be an object")
    else:
        missing = sorted(set(REQUIRED_SPLITS) - set(split_hashes))
        if missing:
            errors.append("missing P5 V2 split hashes: " + ", ".join(missing))
        for name in REQUIRED_SPLITS:
            if name in split_hashes:
                _require_sha256(
                    split_hashes[name],
                    f"split_hashes.{name}",
                    errors,
                )

    episode_ids = manifest.get("episode_ids")
    if (
        not isinstance(episode_ids, list)
        or not episode_ids
        or any(not isinstance(item, str) or not item for item in episode_ids)
    ):
        errors.append("episode_ids must be a non-empty list of non-empty strings")
    elif len(episode_ids) != len(set(episode_ids)):
        errors.append("episode_ids must be unique")

    expected_repeats = protocol.get("statistics", {}).get("stochastic_repeats")
    seeds = manifest.get("seeds")
    if (
        not isinstance(seeds, list)
        or any(not isinstance(seed, int) for seed in seeds)
        or len(seeds) != len(set(seeds))
    ):
        errors.append("seeds must be a list of unique integers")
    elif isinstance(expected_repeats, int) and len(seeds) != expected_repeats:
        errors.append(
            f"seeds must contain exactly {expected_repeats} stochastic repeats"
        )

    provider_revisions = manifest.get("model_provider_revisions")
    if not isinstance(provider_revisions, dict) or not provider_revisions:
        errors.append("model_provider_revisions must be a non-empty object")
    else:
        for key, value in provider_revisions.items():
            _require_nonempty_string(
                value,
                f"model_provider_revisions.{key}",
                errors,
            )

    evaluator = manifest.get("evaluator")
    if not isinstance(evaluator, dict):
        errors.append("evaluator must be an object")
    else:
        _require_sha256(
            evaluator.get("artifact_hash"),
            "evaluator.artifact_hash",
            errors,
        )
        _require_nonempty_string(
            evaluator.get("evaluation_epoch"),
            "evaluator.evaluation_epoch",
            errors,
        )
        _require_nonempty_string(
            evaluator.get("lineage_id"),
            "evaluator.lineage_id",
            errors,
        )

    custody = manifest.get("custody")
    if not isinstance(custody, dict):
        errors.append("custody must be an object")
    else:
        lineage_fields = (
            "candidate_lineage_id",
            "evaluator_lineage_id",
            "host_lineage_id",
        )
        lineages: list[str] = []
        for field in lineage_fields:
            value = custody.get(field)
            _require_nonempty_string(value, f"custody.{field}", errors)
            if isinstance(value, str) and value:
                lineages.append(value)
        if len(lineages) == 3 and len(set(lineages)) != 3:
            errors.append("candidate/evaluator/host custody lineages must be distinct")
        if (
            isinstance(evaluator, dict)
            and isinstance(evaluator.get("lineage_id"), str)
            and custody.get("evaluator_lineage_id") != evaluator.get("lineage_id")
        ):
            errors.append(
                "custody.evaluator_lineage_id must match evaluator.lineage_id"
            )
        for field, expected in (
            ("evaluator_frozen_before_candidate", True),
            ("fresh_frozen_before_candidate", True),
            ("candidate_can_read_fresh_labels", False),
            ("candidate_can_write_protected_evaluator", False),
            ("candidate_can_delete_negative_history", False),
        ):
            if custody.get(field) is not expected:
                errors.append(f"custody.{field} must be {str(expected).lower()}")

    pace = manifest.get("pace")
    if not isinstance(pace, dict):
        errors.append("pace must be an object")
    else:
        _require_nonempty_string(pace.get("rule_id"), "pace.rule_id", errors)
        _require_sha256(pace.get("config_hash"), "pace.config_hash", errors)
        error_budget = pace.get("error_budget")
        if (
            not isinstance(error_budget, (int, float))
            or isinstance(error_budget, bool)
            or not (0 < float(error_budget) <= 1)
        ):
            errors.append("pace.error_budget must be numeric in (0, 1]")
        optional_stopping = pace.get("optional_stopping_allowed")
        if optional_stopping is not True:
            errors.append(
                "P5 V2 adaptive acceptance requires "
                "pace.optional_stopping_allowed=true under the bound anytime-valid rule"
            )
        if pace.get("anytime_valid") is not True:
            errors.append("pace.anytime_valid must be true")

    resource_limits = manifest.get("resource_limits")
    if not isinstance(resource_limits, dict):
        errors.append("resource_limits must be an object")
    else:
        if resource_limits.get("matched_across_arms") is not True:
            errors.append("resource_limits.matched_across_arms must be true")
        for key in REQUIRED_RESOURCE_KEYS:
            value = resource_limits.get(key)
            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or value <= 0
            ):
                errors.append(f"resource_limits.{key} must be positive")

    environment = manifest.get("environment")
    if not isinstance(environment, dict):
        errors.append("environment must be an object")
    else:
        for field in ("python", "runner", "hardware"):
            _require_nonempty_string(
                environment.get(field),
                f"environment.{field}",
                errors,
            )
        _require_sha256(
            environment.get("dependencies_hash"),
            "environment.dependencies_hash",
            errors,
        )

    required_arms = required_arm_kinds(protocol)
    arms = manifest.get("study_arms")
    arm_map: dict[str, dict[str, Any]] = {}
    if not isinstance(arms, list) or not arms:
        errors.append("study_arms must be a non-empty list")
    else:
        for index, arm in enumerate(arms):
            if not isinstance(arm, dict):
                errors.append(f"study_arms[{index}] must be an object")
                continue
            system_id = arm.get("system_id")
            if not isinstance(system_id, str) or not system_id:
                errors.append(f"study_arms[{index}].system_id must be non-empty")
                continue
            if system_id in arm_map:
                errors.append(f"duplicate study arm: {system_id}")
                continue
            arm_map[system_id] = arm
            if arm.get("kind") not in ALLOWED_ARM_KINDS:
                errors.append(f"invalid arm kind for {system_id}")
            _require_sha256(
                arm.get("config_hash"),
                f"study_arms[{system_id}].config_hash",
                errors,
            )
            disposition = arm.get("disposition")
            if disposition not in ALLOWED_DISPOSITIONS:
                errors.append(f"invalid disposition for study arm {system_id}")
            if disposition == "NOT_EXECUTABLE_WITH_JUSTIFICATION":
                _require_sha256(
                    arm.get("justification_hash"),
                    f"study_arms[{system_id}].justification_hash",
                    errors,
                )

        missing_arms = sorted(set(required_arms) - set(arm_map))
        if missing_arms:
            errors.append("missing required P5 V2 study arms: " + ", ".join(missing_arms))
        for system_id, expected_kind in required_arms.items():
            arm = arm_map.get(system_id)
            if arm is None:
                continue
            if arm.get("kind") != expected_kind:
                errors.append(
                    f"study arm {system_id} must have kind={expected_kind}"
                )
            if (
                expected_kind in {"SUBJECT", "ABLATION"}
                and arm.get("disposition") == "NOT_EXECUTABLE_WITH_JUSTIFICATION"
            ):
                errors.append(
                    f"{expected_kind.lower()} arm {system_id} cannot be non-executable"
                )

        for baseline in MANDATORY_EXECUTABLE_BASELINES:
            arm = arm_map.get(baseline)
            if (
                arm is not None
                and arm.get("disposition") == "NOT_EXECUTABLE_WITH_JUSTIFICATION"
            ):
                errors.append(f"mandatory baseline {baseline} must be executable")

    remaining = unbound_paths(manifest)
    if remaining:
        errors.append(
            "P5 V2 run manifest contains UNBOUND fields: " + ", ".join(remaining)
        )
    return errors


def run_manifest_digest(
    manifest: dict[str, Any],
    protocol: dict[str, Any],
) -> str:
    errors = validate_run_manifest(manifest, protocol)
    if errors:
        raise ValueError("; ".join(errors))
    return content_digest(manifest)


def _arm_map(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    arms = manifest.get("study_arms")
    if not isinstance(arms, list):
        return {}
    return {
        str(arm["system_id"]): arm
        for arm in arms
        if isinstance(arm, dict) and isinstance(arm.get("system_id"), str)
    }


def _decision_key(payload: dict[str, Any]) -> tuple[str, str, int, str] | None:
    try:
        return (
            str(payload["system_id"]),
            str(payload["episode_id"]),
            int(payload["seed"]),
            str(payload["candidate_id"]),
        )
    except (KeyError, TypeError, ValueError):
        return None


def _record_key(
    payload: dict[str, Any],
) -> tuple[str, str, int, str, str] | None:
    decision_key = _decision_key(payload)
    stage = payload.get("stage")
    if decision_key is None or not isinstance(stage, str):
        return None
    return (*decision_key, stage)


def decision_unsigned_payload(decision: dict[str, Any]) -> dict[str, Any]:
    return {
        "run_manifest_hash": decision.get("run_manifest_hash"),
        "system_id": decision.get("system_id"),
        "episode_id": decision.get("episode_id"),
        "seed": decision.get("seed"),
        "candidate_id": decision.get("candidate_id"),
        "decision": decision.get("decision"),
        "decision_sequence_index": decision.get("decision_sequence_index"),
    }


def validate_result_archive(
    archive: dict[str, Any],
    manifest: dict[str, Any],
    protocol: dict[str, Any],
) -> dict[str, Any]:
    errors = validate_run_manifest(manifest, protocol)
    if errors:
        return {
            "valid": False,
            "errors": ["run manifest invalid: " + error for error in errors],
            "candidate_verdicts": {},
            "false_acceptance_count": 0,
            "fresh_harm_count": 0,
        }

    manifest_hash = content_digest(manifest)
    errors = []

    if archive.get("schema_version") != ARCHIVE_SCHEMA_VERSION:
        errors.append("wrong P5 V2 result-archive schema_version")
    if archive.get("protocol_id") != PROTOCOL_ID:
        errors.append("result archive protocol_id mismatch")
    if archive.get("run_manifest_hash") != manifest_hash:
        errors.append("result archive run_manifest_hash mismatch")
    finalized = archive.get("finalized")
    if not isinstance(finalized, bool):
        errors.append("result archive finalized must be boolean")
        finalized = False
    if finalized:
        _require_sha256(
            archive.get("final_negative_history_hash"),
            "final_negative_history_hash",
            errors,
        )

    records = archive.get("records")
    if not isinstance(records, list):
        errors.append("result archive records must be a list")
        records = []
    decisions = archive.get("decisions")
    if not isinstance(decisions, list):
        errors.append("result archive decisions must be a list")
        decisions = []

    arm_map = _arm_map(manifest)
    active_arms = {
        system_id
        for system_id, arm in arm_map.items()
        if arm.get("disposition") != "NOT_EXECUTABLE_WITH_JUSTIFICATION"
    }
    seeds = set(manifest.get("seeds", ()))
    episodes = set(manifest.get("episode_ids", ()))
    evaluator = manifest["evaluator"]

    result_ids: set[str] = set()
    seen_record_keys: set[tuple[str, str, int, str, str]] = set()
    candidate_records: dict[
        tuple[str, str, int, str],
        dict[Stage, StageResult],
    ] = defaultdict(dict)
    candidate_task_family: dict[tuple[str, str, int, str], str] = {}
    candidate_sequences: dict[
        tuple[str, str, int, str],
        dict[Stage, int],
    ] = defaultdict(dict)
    coverage: set[tuple[str, str, int]] = set()

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"records[{index}] must be an object")
            continue
        prefix = f"records[{index}]"
        if record.get("schema_version") != RECORD_SCHEMA_VERSION:
            errors.append(f"{prefix} wrong schema_version")
        if record.get("protocol_id") != PROTOCOL_ID:
            errors.append(f"{prefix} protocol_id mismatch")
        if record.get("run_manifest_hash") != manifest_hash:
            errors.append(f"{prefix} run_manifest_hash mismatch")
        if record.get("subject_revision") != manifest.get("subject_revision"):
            errors.append(f"{prefix} subject_revision mismatch")
        if record.get("evaluator_hash") != evaluator.get("artifact_hash"):
            errors.append(f"{prefix} evaluator_hash mismatch")
        if record.get("evaluation_epoch") != evaluator.get("evaluation_epoch"):
            errors.append(f"{prefix} evaluation_epoch mismatch")

        result_id = record.get("result_id")
        if not isinstance(result_id, str) or not result_id:
            errors.append(f"{prefix} result_id must be non-empty")
        elif result_id in result_ids:
            errors.append(f"duplicate result_id: {result_id}")
        else:
            result_ids.add(result_id)

        system_id = record.get("system_id")
        if system_id not in active_arms:
            errors.append(f"{prefix} references inactive/unknown study arm {system_id!r}")
        else:
            expected_kind = arm_map[str(system_id)].get("kind")
            if record.get("arm_kind") != expected_kind:
                errors.append(f"{prefix} arm_kind mismatch for {system_id}")

        episode_id = record.get("episode_id")
        if episode_id not in episodes:
            errors.append(f"{prefix} episode_id not frozen in run manifest")
        seed = record.get("seed")
        if seed not in seeds:
            errors.append(f"{prefix} seed not frozen in run manifest")

        _require_sha256(
            record.get("candidate_revision_hash"),
            f"{prefix}.candidate_revision_hash",
            errors,
        )
        _require_sha256(
            record.get("raw_artifact_hash"),
            f"{prefix}.raw_artifact_hash",
            errors,
        )
        _require_sha256(
            record.get("negative_history_digest"),
            f"{prefix}.negative_history_digest",
            errors,
        )

        stage_value = record.get("stage")
        verdict_value = record.get("verdict")
        try:
            stage = Stage(stage_value)
        except (ValueError, TypeError):
            errors.append(f"{prefix} invalid stage")
            continue
        try:
            verdict = StageVerdict(verdict_value)
        except (ValueError, TypeError):
            errors.append(f"{prefix} invalid verdict")
            continue

        score_delta = record.get("score_delta")
        if (
            not isinstance(score_delta, (int, float))
            or isinstance(score_delta, bool)
        ):
            errors.append(f"{prefix}.score_delta must be numeric")
            score_delta = 0.0
        harmful = record.get("harmful")
        if not isinstance(harmful, bool):
            errors.append(f"{prefix}.harmful must be boolean")
            harmful = False
        sequence_index = record.get("sequence_index")
        if (
            not isinstance(sequence_index, int)
            or isinstance(sequence_index, bool)
            or sequence_index < 0
        ):
            errors.append(f"{prefix}.sequence_index must be a non-negative integer")
            sequence_index = 0

        cost = record.get("cost")
        if not isinstance(cost, dict):
            errors.append(f"{prefix}.cost must be an object")
            cost = {}
        for cost_key in (
            "wallclock_seconds",
            "model_tokens",
            "tool_calls",
            "evaluator_calls",
        ):
            value = cost.get(cost_key)
            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or value < 0
            ):
                errors.append(f"{prefix}.cost.{cost_key} must be non-negative")

        metrics = record.get("metrics")
        if not isinstance(metrics, dict):
            errors.append(f"{prefix}.metrics must be an object")
        else:
            for metric_name, value in metrics.items():
                if (
                    not isinstance(value, (int, float))
                    or isinstance(value, bool)
                ):
                    errors.append(
                        f"{prefix}.metrics.{metric_name} must be numeric"
                    )

        record_key = _record_key(record)
        decision_key = _decision_key(record)
        if record_key is None or decision_key is None:
            errors.append(f"{prefix} missing candidate identity fields")
            continue
        if record_key in seen_record_keys:
            errors.append(
                "duplicate candidate stage record: "
                + "/".join(str(item) for item in record_key)
            )
            continue
        seen_record_keys.add(record_key)
        if sequence_index in candidate_sequences[decision_key].values():
            errors.append(
                f"candidate {decision_key} reuses sequence_index {sequence_index}"
            )
        candidate_sequences[decision_key][stage] = sequence_index
        candidate_records[decision_key][stage] = StageResult(
            stage=stage,
            verdict=verdict,
            score_delta=float(score_delta),
            cost=float(cost.get("wallclock_seconds", 0.0))
            if isinstance(cost.get("wallclock_seconds"), (int, float))
            else 0.0,
            harmful=harmful,
        )
        task_family = record.get("task_family")
        if not isinstance(task_family, str) or not task_family:
            errors.append(f"{prefix}.task_family must be non-empty")
        else:
            previous = candidate_task_family.get(decision_key)
            if previous is not None and previous != task_family:
                errors.append(
                    f"candidate {decision_key} changes task_family across stages"
                )
            candidate_task_family[decision_key] = task_family
        if (
            isinstance(system_id, str)
            and isinstance(episode_id, str)
            and isinstance(seed, int)
        ):
            coverage.add((system_id, episode_id, seed))

    decision_map: dict[tuple[str, str, int, str], dict[str, Any]] = {}
    for index, decision in enumerate(decisions):
        if not isinstance(decision, dict):
            errors.append(f"decisions[{index}] must be an object")
            continue
        prefix = f"decisions[{index}]"
        key = _decision_key(decision)
        if key is None:
            errors.append(f"{prefix} missing decision identity fields")
            continue
        if key in decision_map:
            errors.append(f"duplicate candidate decision: {key}")
            continue
        decision_map[key] = decision
        if decision.get("decision") not in ALLOWED_DECISIONS:
            errors.append(f"{prefix} invalid decision")
        decision_sequence_index = decision.get("decision_sequence_index")
        if (
            not isinstance(decision_sequence_index, int)
            or isinstance(decision_sequence_index, bool)
            or decision_sequence_index < 0
        ):
            errors.append(
                f"{prefix}.decision_sequence_index must be a non-negative integer"
            )
        _require_sha256(
            decision.get("decision_artifact_hash"),
            f"{prefix}.decision_artifact_hash",
            errors,
        )
        if (
            _is_lower_hex(decision.get("decision_artifact_hash"), 64)
            and decision.get("decision_artifact_hash")
            != content_digest(decision_unsigned_payload(decision))
        ):
            errors.append(f"{prefix} decision_artifact_hash mismatch")
        if decision.get("run_manifest_hash") != manifest_hash:
            errors.append(f"{prefix} run_manifest_hash mismatch")

    candidate_verdicts: dict[str, str] = {}
    false_acceptance_count = 0
    fresh_harm_count = 0

    gate = MultiStageCandidateGate()
    for key, stages in candidate_records.items():
        system_id, episode_id, seed, candidate_id = key
        record = CandidateRecord(candidate_id=candidate_id)
        for stage in gate.required_stages:
            if stage in stages:
                record.record(stages[stage])
        verdict = gate.evaluate(record)
        label = "|".join((system_id, episode_id, str(seed), candidate_id))
        candidate_verdicts[label] = verdict.value

        fresh = stages.get(Stage.FRESH)
        if fresh is not None and fresh.harmful:
            fresh_harm_count += 1

        decision = decision_map.get(key)
        if system_id == V2_SYSTEM_ID and decision is not None:
            expected = {
                CandidateVerdict.RECOMMEND_HOST_PROMOTION: "ACCEPT",
                CandidateVerdict.REJECT: "REJECT",
                CandidateVerdict.CANNOT_CHECK: "CANNOT_CHECK",
            }.get(verdict)
            if expected is None:
                if finalized:
                    errors.append(
                        f"finalized V2 candidate {label} remains IN_PROGRESS"
                    )
            elif decision.get("decision") != expected:
                errors.append(
                    f"V2 candidate decision mismatch for {label}: "
                    f"expected {expected}"
                )
            decision_sequence = decision.get("decision_sequence_index")
            observed_sequences = candidate_sequences.get(key, {})
            if (
                isinstance(decision_sequence, int)
                and not isinstance(decision_sequence, bool)
                and observed_sequences
                and decision_sequence <= max(observed_sequences.values())
            ):
                errors.append(
                    f"V2 candidate decision for {label} predates retained stage evidence"
                )
            if decision.get("decision") == "ACCEPT":
                ordered_sequences = [
                    observed_sequences.get(stage)
                    for stage in gate.required_stages
                ]
                if (
                    any(value is None for value in ordered_sequences)
                    or ordered_sequences != sorted(ordered_sequences)
                    or len(set(ordered_sequences)) != len(ordered_sequences)
                ):
                    errors.append(
                        f"V2 accepted candidate {label} violates frozen stage chronology"
                    )

        if decision is not None and decision.get("decision") == "ACCEPT":
            fresh = stages.get(Stage.FRESH)
            protected = stages.get(Stage.PROTECTED)
            if finalized and fresh is None:
                errors.append(
                    f"accepted candidate {label} lacks a FRESH evaluation"
                )
            if finalized and protected is None:
                errors.append(
                    f"accepted candidate {label} lacks a PROTECTED evaluation"
                )
            if (
                protected is None
                or protected.harmful
                or protected.verdict is not StageVerdict.PASS
            ):
                false_acceptance_count += 1

    if finalized:
        for key in candidate_records:
            if key not in decision_map:
                errors.append(f"finalized archive missing decision for {key}")
        for key in decision_map:
            if key not in candidate_records:
                errors.append(f"decision has no stage evidence for {key}")

        required_coverage = {
            (system_id, episode_id, seed)
            for system_id in active_arms
            for episode_id in episodes
            for seed in seeds
        }
        missing_coverage = sorted(required_coverage - coverage)
        if missing_coverage:
            errors.append(
                "finalized archive missing arm/episode/seed coverage: "
                + ", ".join(
                    f"{system}/{episode}/{seed}"
                    for system, episode, seed in missing_coverage[:12]
                )
                + (" ..." if len(missing_coverage) > 12 else "")
            )

    decision_counts = Counter(
        decision.get("decision")
        for decision in decision_map.values()
        if decision.get("decision") in ALLOWED_DECISIONS
    )
    return {
        "valid": not errors,
        "errors": errors,
        "run_manifest_hash": manifest_hash,
        "record_count": len(records),
        "candidate_count": len(candidate_records),
        "decision_counts": dict(sorted(decision_counts.items())),
        "candidate_verdicts": dict(sorted(candidate_verdicts.items())),
        "false_acceptance_count": false_acceptance_count,
        "fresh_harm_count": fresh_harm_count,
        "empirical_authority": "CANNOT_CHECK",
    }


def result_archive_digest(
    archive: dict[str, Any],
    manifest: dict[str, Any],
    protocol: dict[str, Any],
) -> str:
    report = validate_result_archive(archive, manifest, protocol)
    if not report["valid"]:
        raise ValueError("; ".join(report["errors"]))
    return content_digest(archive)
