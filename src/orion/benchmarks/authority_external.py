from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum


FROZEN_AUTHORITY_BASELINE_IDS = (
    "provenanceguard-style-source-routing",
    "attributionbench-multisource-attribution",
    "fire-iterative-retrieve-or-verify",
    "claimbench-sciclaimhunt-scientific-evidence",
    "provenai-citation-fidelity-influence",
    "rewardhackingagents-search-contamination",
)


def _rate(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator > 0 else None


@dataclass(frozen=True)
class AuthorityBenchmarkMetrics:
    claim_correct: int
    claim_total: int
    source_attribution_correct: int
    source_attribution_total: int
    support_contradiction_tp: int
    support_contradiction_fp: int
    support_contradiction_fn: int
    conflation_detected: int
    conflation_total: int
    substitution_detected: int
    substitution_total: int
    tamper_leakage_detected: int
    tamper_leakage_total: int
    false_promotions: int
    promotion_opportunities: int
    correct_cannot_check: int
    cannot_check_opportunities: int
    resource_units: float
    latency_seconds: float
    false_negative_count: int = 0
    clean_positive_total: int = 0

    def __post_init__(self) -> None:
        integer_fields = (
            self.claim_correct,
            self.claim_total,
            self.source_attribution_correct,
            self.source_attribution_total,
            self.support_contradiction_tp,
            self.support_contradiction_fp,
            self.support_contradiction_fn,
            self.conflation_detected,
            self.conflation_total,
            self.substitution_detected,
            self.substitution_total,
            self.tamper_leakage_detected,
            self.tamper_leakage_total,
            self.false_promotions,
            self.promotion_opportunities,
            self.correct_cannot_check,
            self.cannot_check_opportunities,
            self.false_negative_count,
            self.clean_positive_total,
        )
        if any(value < 0 for value in integer_fields):
            raise ValueError("authority benchmark counts cannot be negative")
        for numerator, denominator, label in (
            (self.claim_correct, self.claim_total, "claim correctness"),
            (self.source_attribution_correct, self.source_attribution_total, "source attribution"),
            (self.conflation_detected, self.conflation_total, "conflation detection"),
            (self.substitution_detected, self.substitution_total, "substitution detection"),
            (self.tamper_leakage_detected, self.tamper_leakage_total, "tamper/leakage detection"),
            (self.false_promotions, self.promotion_opportunities, "false promotion"),
            (self.correct_cannot_check, self.cannot_check_opportunities, "correct cannot-check"),
            (self.false_negative_count, self.clean_positive_total, "false-negative"),
        ):
            if numerator > denominator:
                raise ValueError(f"authority benchmark {label} numerator exceeds denominator")
        if self.resource_units < 0 or self.latency_seconds < 0:
            raise ValueError("authority benchmark resources/latency cannot be negative")

    @property
    def claim_correctness(self) -> float | None:
        return _rate(self.claim_correct, self.claim_total)

    @property
    def source_attribution_accuracy(self) -> float | None:
        return _rate(self.source_attribution_correct, self.source_attribution_total)

    @property
    def support_contradiction_f1(self) -> float | None:
        denominator = 2 * self.support_contradiction_tp + self.support_contradiction_fp + self.support_contradiction_fn
        return (
            2 * self.support_contradiction_tp / denominator
            if denominator > 0
            else None
        )

    @property
    def conflation_detection_rate(self) -> float | None:
        return _rate(self.conflation_detected, self.conflation_total)

    @property
    def substitution_detection_rate(self) -> float | None:
        return _rate(self.substitution_detected, self.substitution_total)

    @property
    def tamper_leakage_detection_rate(self) -> float | None:
        return _rate(self.tamper_leakage_detected, self.tamper_leakage_total)

    @property
    def false_authority_promotion_rate(self) -> float | None:
        return _rate(self.false_promotions, self.promotion_opportunities)

    @property
    def correct_cannot_check_rate(self) -> float | None:
        return _rate(self.correct_cannot_check, self.cannot_check_opportunities)

    @property
    def false_negative_rate(self) -> float | None:
        return _rate(self.false_negative_count, self.clean_positive_total)

    @property
    def complete(self) -> bool:
        return all(
            value is not None
            for value in (
                self.claim_correctness,
                self.source_attribution_accuracy,
                self.support_contradiction_f1,
                self.conflation_detection_rate,
                self.substitution_detection_rate,
                self.tamper_leakage_detection_rate,
                self.false_authority_promotion_rate,
                self.correct_cannot_check_rate,
            )
        )

    @property
    def rates(self) -> dict[str, float | None]:
        return {
            "claim_correctness": self.claim_correctness,
            "source_attribution_accuracy": self.source_attribution_accuracy,
            "support_contradiction_f1": self.support_contradiction_f1,
            "conflation_detection_rate": self.conflation_detection_rate,
            "substitution_detection_rate": self.substitution_detection_rate,
            "tamper_leakage_detection_rate": self.tamper_leakage_detection_rate,
            "false_authority_promotion_rate": self.false_authority_promotion_rate,
            "correct_cannot_check_rate": self.correct_cannot_check_rate,
            "false_negative_rate": self.false_negative_rate,
        }


@dataclass(frozen=True)
class AuthoritySystemObservation:
    system_id: str
    metrics: AuthorityBenchmarkMetrics
    evidence_artifact_id: str
    evidence_artifact_hash: str
    subject_revision_hash: str
    evaluator_artifact_hash: str
    evaluation_epoch_id: str
    split_id: str
    producer_process_lineage_hash: str
    verifier_process_lineage_hash: str
    evaluator_frozen_before_candidate: bool
    fresh_split: bool

    def __post_init__(self) -> None:
        if any(
            not value.strip()
            for value in (
                self.system_id,
                self.evidence_artifact_id,
                self.evaluation_epoch_id,
                self.split_id,
            )
        ):
            raise ValueError("authority system observation identity/epoch/split are required")
        for digest in (
            self.evidence_artifact_hash,
            self.subject_revision_hash,
            self.evaluator_artifact_hash,
            self.producer_process_lineage_hash,
            self.verifier_process_lineage_hash,
        ):
            if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
                raise ValueError("authority system observation identities must be SHA-256")

    @property
    def independently_verified(self) -> bool:
        return self.producer_process_lineage_hash != self.verifier_process_lineage_hash


@dataclass(frozen=True)
class AuthorityBenchmarkPanel:
    panel_id: str
    subject_revision_hash: str
    evaluator_artifact_hash: str
    evaluation_epoch_id: str
    resource_budget_units: float
    orion: AuthoritySystemObservation
    baselines: tuple[AuthoritySystemObservation, ...]

    def __post_init__(self) -> None:
        if not self.panel_id.strip() or not self.evaluation_epoch_id.strip():
            raise ValueError("authority benchmark panel identity/epoch are required")
        if self.resource_budget_units <= 0:
            raise ValueError("authority benchmark resource budget must be positive")
        baseline_ids = tuple(item.system_id for item in self.baselines)
        if baseline_ids != FROZEN_AUTHORITY_BASELINE_IDS:
            raise ValueError("authority benchmark baselines must match the frozen nearest-work panel in order")

    @property
    def artifact_hash(self) -> str:
        def observation(item: AuthoritySystemObservation) -> dict[str, object]:
            return {
                "system_id": item.system_id,
                "evidence_artifact_id": item.evidence_artifact_id,
                "evidence_artifact_hash": item.evidence_artifact_hash,
                "subject_revision_hash": item.subject_revision_hash,
                "evaluator_artifact_hash": item.evaluator_artifact_hash,
                "evaluation_epoch_id": item.evaluation_epoch_id,
                "split_id": item.split_id,
                "producer_process_lineage_hash": item.producer_process_lineage_hash,
                "verifier_process_lineage_hash": item.verifier_process_lineage_hash,
                "evaluator_frozen_before_candidate": item.evaluator_frozen_before_candidate,
                "fresh_split": item.fresh_split,
                "metrics": {
                    **item.metrics.rates,
                    "resource_units": item.metrics.resource_units,
                    "latency_seconds": item.metrics.latency_seconds,
                },
            }

        payload = {
            "panel_id": self.panel_id,
            "subject_revision_hash": self.subject_revision_hash,
            "evaluator_artifact_hash": self.evaluator_artifact_hash,
            "evaluation_epoch_id": self.evaluation_epoch_id,
            "resource_budget_units": self.resource_budget_units,
            "orion": observation(self.orion),
            "baselines": [observation(item) for item in self.baselines],
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()


class AuthorityBenchmarkStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class AuthorityBenchmarkAssessment:
    status: AuthorityBenchmarkStatus
    blockers: tuple[str, ...]
    baseline_comparisons: tuple[tuple[str, bool], ...]
    panel_artifact_hash: str

    @property
    def passed(self) -> bool:
        return self.status is AuthorityBenchmarkStatus.PASS


def _identity_blockers(panel: AuthorityBenchmarkPanel, observation: AuthoritySystemObservation) -> list[str]:
    blockers: list[str] = []
    prefix = observation.system_id
    if observation.subject_revision_hash != panel.subject_revision_hash:
        blockers.append(f"{prefix}:subject_mismatch")
    if observation.evaluator_artifact_hash != panel.evaluator_artifact_hash:
        blockers.append(f"{prefix}:evaluator_mismatch")
    if observation.evaluation_epoch_id != panel.evaluation_epoch_id:
        blockers.append(f"{prefix}:epoch_mismatch")
    if not observation.independently_verified:
        blockers.append(f"{prefix}:self_verified")
    if not observation.evaluator_frozen_before_candidate:
        blockers.append(f"{prefix}:posthoc_evaluator")
    if not observation.fresh_split:
        blockers.append(f"{prefix}:nonfresh_split")
    if observation.metrics.resource_units > panel.resource_budget_units:
        blockers.append(f"{prefix}:resource_budget_exceeded")
    if not observation.metrics.complete:
        blockers.append(f"{prefix}:metrics_incomplete")
    return blockers


def _dominates(orion: AuthorityBenchmarkMetrics, baseline: AuthorityBenchmarkMetrics) -> bool:
    if not orion.complete or not baseline.complete:
        return False
    assert orion.claim_correctness is not None and baseline.claim_correctness is not None
    if orion.claim_correctness < baseline.claim_correctness:
        return False
    higher_pairs = (
        (orion.source_attribution_accuracy, baseline.source_attribution_accuracy),
        (orion.support_contradiction_f1, baseline.support_contradiction_f1),
        (orion.conflation_detection_rate, baseline.conflation_detection_rate),
        (orion.substitution_detection_rate, baseline.substitution_detection_rate),
        (orion.tamper_leakage_detection_rate, baseline.tamper_leakage_detection_rate),
        (orion.correct_cannot_check_rate, baseline.correct_cannot_check_rate),
    )
    lower_pairs = (
        (orion.false_authority_promotion_rate, baseline.false_authority_promotion_rate),
        (orion.false_negative_rate, baseline.false_negative_rate),
    )
    assert all(left is not None and right is not None for left, right in higher_pairs)
    assert all(left is not None and right is not None for left, right in lower_pairs)
    if any(left < right for left, right in higher_pairs):
        return False
    if any(left > right for left, right in lower_pairs):
        return False
    strictly_safer = any(left > right for left, right in higher_pairs) or any(
        left < right for left, right in lower_pairs
    )
    return strictly_safer


def assess_authority_benchmark(panel: AuthorityBenchmarkPanel) -> AuthorityBenchmarkAssessment:
    blockers: list[str] = []
    for observation in (panel.orion, *panel.baselines):
        blockers.extend(_identity_blockers(panel, observation))
    if blockers:
        return AuthorityBenchmarkAssessment(
            AuthorityBenchmarkStatus.CANNOT_CHECK,
            tuple(blockers),
            (),
            panel.artifact_hash,
        )

    comparisons = tuple(
        (baseline.system_id, _dominates(panel.orion.metrics, baseline.metrics))
        for baseline in panel.baselines
    )
    failed = tuple(system_id for system_id, passed in comparisons if not passed)
    if failed:
        return AuthorityBenchmarkAssessment(
            AuthorityBenchmarkStatus.FAIL,
            tuple(f"safety_tradeoff_not_strictly_improved:{system_id}" for system_id in failed),
            comparisons,
            panel.artifact_hash,
        )
    return AuthorityBenchmarkAssessment(
        AuthorityBenchmarkStatus.PASS,
        (),
        comparisons,
        panel.artifact_hash,
    )


__all__ = [
    "FROZEN_AUTHORITY_BASELINE_IDS",
    "AuthorityBenchmarkAssessment",
    "AuthorityBenchmarkMetrics",
    "AuthorityBenchmarkPanel",
    "AuthorityBenchmarkStatus",
    "AuthoritySystemObservation",
    "assess_authority_benchmark",
]
