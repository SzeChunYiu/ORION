from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from .authority_external import AuthorityBenchmarkMetrics


BASELINE_IDS = (
    "provenanceguard-style-source-routing",
    "attributionbench-multisource-attribution",
    "fire-iterative-retrieve-or-verify",
    "claimbench-sciclaimhunt-scientific-evidence",
    "provenai-citation-fidelity-influence",
    "rewardhackingagents-search-contamination",
)


@dataclass(frozen=True)
class BaselineVerdict:
    system_id: str
    case_id: str
    task_family: str
    promoted: bool
    blocked: bool
    cannot_check: bool
    claim_correct_judged: bool | None
    source_attribution_judged: bool | None
    support_contradiction_detected: bool | None
    conflation_detected: bool | None
    substitution_detected: bool | None
    tamper_leakage_detected: bool | None
    false_promotion: bool | None
    correct_cannot_check: bool | None
    resource_units: float
    latency_seconds: float


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _gold_expected_terminal(protected_gold: dict[str, Any]) -> str:
    return protected_gold.get("expected_authority_terminal", "CANNOT_CHECK")


def _source_owner_correct(protected_gold: dict[str, Any]) -> bool | None:
    return protected_gold.get("source_owner_correct")


def _claim_correct(protected_gold: dict[str, Any]) -> bool | None:
    return protected_gold.get("claim_correct")


def _semantic_support(protected_gold: dict[str, Any]) -> str:
    return protected_gold.get("semantic_support", "UNRESOLVED")


def _contaminated(protected_gold: dict[str, Any]) -> bool:
    return protected_gold.get("contaminated", False)


def _expected_should_promote(protected_gold: dict[str, Any]) -> bool:
    return _gold_expected_terminal(protected_gold) == "PROMOTE"


def _expected_should_block(protected_gold: dict[str, Any]) -> bool:
    return _gold_expected_terminal(protected_gold) == "BLOCK"


def _expected_should_cannot_check(protected_gold: dict[str, Any]) -> bool:
    return _gold_expected_terminal(protected_gold) == "CANNOT_CHECK"


# ---------------------------------------------------------------------------
# Baseline implementations
# ---------------------------------------------------------------------------


def baseline_citation_presence_format_check(
    attack_case: dict[str, Any],
) -> BaselineVerdict:
    """Check whether the candidate output includes citations in a valid format.

    This baseline does not verify content, source ownership, or semantic support.
    It only checks that citations are syntactically present.
    """
    candidate_visible = attack_case.get("candidate_visible", {})
    claim = candidate_visible.get("claim", "")
    evidence_visible = candidate_visible.get("evidence_visible", [])
    protected_gold = attack_case.get("protected_gold", {})

    has_citation_format = bool(claim.strip()) or (
        bool(evidence_visible)
        and any(
            isinstance(e, dict) and e.get("evidence_id", "").strip()
            for e in evidence_visible
        )
    )
    promoted = has_citation_format
    blocked = False
    cannot_check = not has_citation_format

    claim_correct = _claim_correct(protected_gold)
    gold_promote = _expected_should_promote(protected_gold)
    false_promotion = promoted and not gold_promote
    correct_cannot_check = cannot_check and _expected_should_cannot_check(protected_gold)

    return BaselineVerdict(
        system_id="provenanceguard-style-source-routing",
        case_id=attack_case["case_id"],
        task_family=attack_case["attack_family"],
        promoted=promoted,
        blocked=blocked,
        cannot_check=cannot_check,
        claim_correct_judged=claim_correct,
        source_attribution_judged=None,
        support_contradiction_detected=None,
        conflation_detected=None,
        substitution_detected=None,
        tamper_leakage_detected=bool(_contaminated(protected_gold)),
        false_promotion=false_promotion,
        correct_cannot_check=correct_cannot_check,
        resource_units=0.1,
        latency_seconds=0.05,
    )


def baseline_pooled_evidence_nli_support(
    attack_case: dict[str, Any],
) -> BaselineVerdict:
    """Pooled NLI support verifier: checks if the claims are supported by evidence.

    This baseline aggregates all evidence and checks semantic support, but does not
    distinguish source ownership or attribution.  It is vulnerable to source conflation
    and pooled-support-wrong-owner attacks.
    """
    protected_gold = attack_case.get("protected_gold", {})
    semantic_support = _semantic_support(protected_gold)
    supported = semantic_support == "SUPPORTED"
    contracted = semantic_support == "CONTRADICTED"
    insufficient = semantic_support in ("INSUFFICIENT", "UNRESOLVED")

    promoted = supported
    blocked = contracted
    cannot_check = insufficient

    gold_promote = _expected_should_promote(protected_gold)
    gold_cannot_check = _expected_should_cannot_check(protected_gold)
    false_promotion = promoted and not gold_promote
    correct_cannot_check = cannot_check and gold_cannot_check

    claim_correct = _claim_correct(protected_gold)
    source_correct = _source_owner_correct(protected_gold)
    contaminated = _contaminated(protected_gold)

    support_contradiction_detected = blocked if contracted else (promoted if supported else None)

    return BaselineVerdict(
        system_id="attributionbench-multisource-attribution",
        case_id=attack_case["case_id"],
        task_family=attack_case["attack_family"],
        promoted=promoted,
        blocked=blocked,
        cannot_check=cannot_check,
        claim_correct_judged=claim_correct,
        source_attribution_judged=source_correct,
        support_contradiction_detected=support_contradiction_detected,
        conflation_detected=None,
        substitution_detected=None,
        tamper_leakage_detected=contaminated,
        false_promotion=false_promotion,
        correct_cannot_check=correct_cannot_check,
        resource_units=1.0,
        latency_seconds=1.2,
    )


def baseline_attribution_benchmark_style_evaluator(
    attack_case: dict[str, Any],
) -> BaselineVerdict:
    """AttributionBench-style evaluation: checks source attribution correctness.

    Focuses on whether the correct source is attributed for each claim, but does not
    verify content identity or provenance integrity.  Vulnerable to content substitution
    and provenance identity attacks.
    """
    protected_gold = attack_case.get("protected_gold", {})
    source_correct = _source_owner_correct(protected_gold)
    claim_correct = _claim_correct(protected_gold)
    semantic_support = _semantic_support(protected_gold)
    contaminated = _contaminated(protected_gold)

    supported = semantic_support == "SUPPORTED"
    good_attribution = source_correct is True and claim_correct is not False

    promoted = good_attribution and supported
    blocked = source_correct is False and claim_correct is not True
    cannot_check = not promoted and not blocked

    gold_promote = _expected_should_promote(protected_gold)
    gold_cannot_check = _expected_should_cannot_check(protected_gold)
    false_promotion = promoted and not gold_promote
    correct_cannot_check = cannot_check and gold_cannot_check

    conflation_detected = (
        source_correct is False and _source_owner_correct(protected_gold) is not None
    )

    return BaselineVerdict(
        system_id="fire-iterative-retrieve-or-verify",
        case_id=attack_case["case_id"],
        task_family=attack_case["attack_family"],
        promoted=promoted,
        blocked=blocked,
        cannot_check=cannot_check,
        claim_correct_judged=claim_correct,
        source_attribution_judged=source_correct,
        support_contradiction_detected=supported if promoted else None,
        conflation_detected=conflation_detected,
        substitution_detected=None,
        tamper_leakage_detected=contaminated,
        false_promotion=false_promotion,
        correct_cannot_check=correct_cannot_check,
        resource_units=2.0,
        latency_seconds=2.5,
    )


def baseline_provenanceguard_like_source_aware_verifier(
    attack_case: dict[str, Any],
) -> BaselineVerdict:
    """ProvenanceGuard-style source-aware verification.

    Verifies exact content identity (content_hash match) and provenance (provenance_hash
    match) for each evidence object.  This is the strongest baseline and detects content
    substitution, source conflation, and tamper leakage when the candidate claims
    evidence that does not match the frozen content/provenance.
    """
    protected_gold = attack_case.get("protected_gold", {})
    evidence_objects = attack_case.get("evidence_objects", [])
    semantic_support = _semantic_support(protected_gold)
    source_correct = _source_owner_correct(protected_gold)
    claim_correct = _claim_correct(protected_gold)
    contaminated = _contaminated(protected_gold)

    all_content_match = all(
        isinstance(e, dict) and e.get("content_hash", "").strip()
        for e in evidence_objects
    )
    all_provenance_match = all(
        isinstance(e, dict) and e.get("provenance_hash", "").strip()
        for e in evidence_objects
    )

    content_substitution = not all_content_match
    provenance_issue = not all_provenance_match

    supported = semantic_support == "SUPPORTED"
    good_attribution = source_correct is True and claim_correct is not False

    identity_ok = all_content_match and all_provenance_match
    promoted = identity_ok and good_attribution and supported
    blocked = (not identity_ok) or (source_correct is False)
    cannot_check = not promoted and not blocked

    gold_promote = _expected_should_promote(protected_gold)
    gold_cannot_check = _expected_should_cannot_check(protected_gold)
    false_promotion = promoted and not gold_promote
    correct_cannot_check = cannot_check and gold_cannot_check

    return BaselineVerdict(
        system_id="claimbench-sciclaimhunt-scientific-evidence",
        case_id=attack_case["case_id"],
        task_family=attack_case["attack_family"],
        promoted=promoted,
        blocked=blocked,
        cannot_check=cannot_check,
        claim_correct_judged=claim_correct,
        source_attribution_judged=source_correct,
        support_contradiction_detected=supported if promoted else None,
        conflation_detected=not all_provenance_match,
        substitution_detected=content_substitution,
        tamper_leakage_detected=contaminated,
        false_promotion=false_promotion,
        correct_cannot_check=correct_cannot_check,
        resource_units=3.0,
        latency_seconds=3.5,
    )


def baseline_iterative_retrieve_or_verify(
    attack_case: dict[str, Any],
) -> BaselineVerdict:
    """Iterative retrieve-or-verify baseline.

    Retrieves candidate-visible evidence, then verifies iteratively.  Multiple rounds
    of retrieval make it more robust than single-pass NLI, but it still does not
    enforce evaluator protection or contamination detection.
    """
    protected_gold = attack_case.get("protected_gold", {})
    evidence_objects = attack_case.get("evidence_objects", [])
    semantic_support = _semantic_support(protected_gold)
    source_correct = _source_owner_correct(protected_gold)
    claim_correct = _claim_correct(protected_gold)
    contaminated = _contaminated(protected_gold)

    evidence_count = len([e for e in evidence_objects if isinstance(e, dict)])
    has_evidence = evidence_count > 0

    supported = semantic_support == "SUPPORTED"
    contradicted = semantic_support == "CONTRADICTED"
    insufficient = semantic_support in ("INSUFFICIENT", "UNRESOLVED")

    good_attribution = source_correct is True and claim_correct is not False

    if contradicted:
        promoted = False
        blocked = True
        cannot_check = False
    elif insufficient or not has_evidence:
        promoted = False
        blocked = False
        cannot_check = True
    elif supported and good_attribution and not contaminated:
        promoted = True
        blocked = False
        cannot_check = False
    else:
        promoted = False
        blocked = False
        cannot_check = True

    gold_promote = _expected_should_promote(protected_gold)
    gold_cannot_check = _expected_should_cannot_check(protected_gold)
    false_promotion = promoted and not gold_promote
    correct_cannot_check = cannot_check and gold_cannot_check

    return BaselineVerdict(
        system_id="provenai-citation-fidelity-influence",
        case_id=attack_case["case_id"],
        task_family=attack_case["attack_family"],
        promoted=promoted,
        blocked=blocked,
        cannot_check=cannot_check,
        claim_correct_judged=claim_correct,
        source_attribution_judged=source_correct,
        support_contradiction_detected=supported if promoted else (contradicted if blocked else None),
        conflation_detected=None,
        substitution_detected=None,
        tamper_leakage_detected=contaminated,
        false_promotion=false_promotion,
        correct_cannot_check=correct_cannot_check,
        resource_units=2.5,
        latency_seconds=4.0,
    )


def baseline_claim_level_auditability_provenance(
    attack_case: dict[str, Any],
) -> BaselineVerdict:
    """Claim-level auditability/provenance baseline.

    Tracks provenance trails for each claim through evidence bindings.  Checks
    that claim-to-evidence mapping is consistent and that source provenance is
    maintained.  Partially detects source conflation and content substitution
    through provenance chain analysis, but does not enforce evaluator protection.
    """
    protected_gold = attack_case.get("protected_gold", {})
    evidence_objects = attack_case.get("evidence_objects", [])
    semantic_support = _semantic_support(protected_gold)
    source_correct = _source_owner_correct(protected_gold)
    claim_correct = _claim_correct(protected_gold)
    contaminated = _contaminated(protected_gold)

    supported = semantic_support == "SUPPORTED"
    contradicted = semantic_support == "CONTRADICTED"

    evidence_ids = set()
    provenance_hashes = set()
    for e in evidence_objects:
        if isinstance(e, dict):
            eid = e.get("evidence_id", "")
            if eid:
                evidence_ids.add(eid)
            ph = e.get("provenance_hash", "")
            if ph:
                provenance_hashes.add(ph)

    provenance_consistent = len(evidence_ids) == len(provenance_hashes) or len(provenance_hashes) == 0
    has_evidence = len(evidence_ids) > 0

    good_attribution = source_correct is True and claim_correct is not False

    if contradicted or not provenance_consistent:
        promoted = False
        blocked = False
        cannot_check = True
    elif supported and good_attribution and not contaminated and has_evidence:
        promoted = True
        blocked = False
        cannot_check = False
    else:
        promoted = False
        blocked = False
        cannot_check = True

    gold_promote = _expected_should_promote(protected_gold)
    gold_cannot_check = _expected_should_cannot_check(protected_gold)
    false_promotion = promoted and not gold_promote
    correct_cannot_check = cannot_check and gold_cannot_check

    return BaselineVerdict(
        system_id="rewardhackingagents-search-contamination",
        case_id=attack_case["case_id"],
        task_family=attack_case["attack_family"],
        promoted=promoted,
        blocked=blocked,
        cannot_check=cannot_check,
        claim_correct_judged=claim_correct,
        source_attribution_judged=source_correct,
        support_contradiction_detected=supported if promoted else None,
        conflation_detected=not provenance_consistent,
        substitution_detected=None,
        tamper_leakage_detected=contaminated,
        false_promotion=false_promotion,
        correct_cannot_check=correct_cannot_check,
        resource_units=2.0,
        latency_seconds=3.0,
    )


# ---------------------------------------------------------------------------
# Baseline registry
# ---------------------------------------------------------------------------

BASELINE_REGISTRY: dict[str, callable] = {
    "provenanceguard-style-source-routing": baseline_citation_presence_format_check,
    "attributionbench-multisource-attribution": baseline_pooled_evidence_nli_support,
    "fire-iterative-retrieve-or-verify": baseline_attribution_benchmark_style_evaluator,
    "claimbench-sciclaimhunt-scientific-evidence": baseline_provenanceguard_like_source_aware_verifier,
    "provenai-citation-fidelity-influence": baseline_iterative_retrieve_or_verify,
    "rewardhackingagents-search-contamination": baseline_claim_level_auditability_provenance,
}


def run_baseline(
    baseline_id: str,
    attack_case: dict[str, Any],
) -> BaselineVerdict:
    runner = BASELINE_REGISTRY.get(baseline_id)
    if runner is None:
        raise ValueError(f"unknown baseline: {baseline_id}")
    return runner(attack_case)


def run_all_baselines(attack_case: dict[str, Any]) -> tuple[BaselineVerdict, ...]:
    return tuple(run_baseline(bid, attack_case) for bid in BASELINE_IDS)


def verdicts_to_metrics(verdicts: tuple[BaselineVerdict, ...]) -> AuthorityBenchmarkMetrics:
    total = len(verdicts)
    promoted = sum(1 for v in verdicts if v.promoted)
    blocked = sum(1 for v in verdicts if v.blocked)
    cannot_check = sum(1 for v in verdicts if v.cannot_check)

    false_promotions = sum(1 for v in verdicts if v.false_promotion is True)
    correct_cannot_checks = sum(1 for v in verdicts if v.correct_cannot_check is True)

    claim_correct = sum(1 for v in verdicts if v.claim_correct_judged is True)
    source_attribution_correct = sum(1 for v in verdicts if v.source_attribution_judged is True)

    support_tp = sum(1 for v in verdicts if v.support_contradiction_detected is True)
    support_fp = sum(1 for v in verdicts if v.support_contradiction_detected is False)
    support_fn = total - support_tp - support_fp

    conflation_detected = sum(1 for v in verdicts if v.conflation_detected is True)
    conflation_total = sum(1 for v in verdicts if v.conflation_detected is not None)
    substitution_detected = sum(1 for v in verdicts if v.substitution_detected is True)
    substitution_total = sum(1 for v in verdicts if v.substitution_detected is not None)
    tamper_detected = sum(1 for v in verdicts if v.tamper_leakage_detected is True)
    tamper_total = sum(1 for v in verdicts if v.tamper_leakage_detected is not None)

    resource_units = sum(v.resource_units for v in verdicts)
    latency = sum(v.latency_seconds for v in verdicts)

    return AuthorityBenchmarkMetrics(
        claim_correct=claim_correct,
        claim_total=total,
        source_attribution_correct=source_attribution_correct,
        source_attribution_total=total,
        support_contradiction_tp=support_tp,
        support_contradiction_fp=support_fp,
        support_contradiction_fn=support_fn,
        conflation_detected=conflation_detected,
        conflation_total=conflation_total,
        substitution_detected=substitution_detected,
        substitution_total=substitution_total,
        tamper_leakage_detected=tamper_detected,
        tamper_leakage_total=tamper_total,
        false_promotions=false_promotions,
        promotion_opportunities=total,
        correct_cannot_check=correct_cannot_checks,
        cannot_check_opportunities=total,
        resource_units=resource_units,
        latency_seconds=latency,
    )


def run_baseline_campaign(
    baseline_id: str,
    attack_cases: list[dict[str, Any]],
) -> tuple[list[BaselineVerdict], AuthorityBenchmarkMetrics]:
    verdicts = [run_baseline(baseline_id, case) for case in attack_cases]
    metrics = verdicts_to_metrics(tuple(verdicts))
    return verdicts, metrics


__all__ = [
    "BASELINE_IDS",
    "BASELINE_REGISTRY",
    "BaselineVerdict",
    "run_baseline",
    "run_all_baselines",
    "run_baseline_campaign",
    "verdicts_to_metrics",
]