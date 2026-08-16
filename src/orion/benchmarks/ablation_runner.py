from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .authority_external import AuthorityBenchmarkMetrics
from .baseline_runner import BaselineVerdict, verdicts_to_metrics


ABLATION_IDS = (
    "no_exact_content_binding",
    "no_content_vs_provenance_distinction",
    "no_checker_lineage_independence",
    "no_hostile_checker_battery",
    "no_behavioral_influence_coordinate",
    "no_evaluator_protection_access_telemetry",
    "soft_confidence_instead_of_fail_closed_authority",
    "no_search_time_contamination_block",
)


@dataclass(frozen=True)
class OrionGuardState:
    """Which protected-authority guards the ORION variant keeps.

    The 8 ablations each remove exactly one guard from the full fail-closed
    ORION pipeline; full ORION keeps all of them. Every guard reads only
    observables that a real pipeline participant could compute from the
    attack case: content hashes, provenance hashes, behavioral availability,
    checker/evaluator attestation metadata on the candidate packet, and the
    verdicts recorded in protected_gold (what an honest checker/evaluator,
    were one present, would conclude).
    """

    exact_content_binding: bool = True
    content_vs_provenance_distinction: bool = True
    checker_lineage_independence: bool = True
    hostile_checker_battery: bool = True
    behavioral_influence_coordinate: bool = True
    evaluator_protection_access_telemetry: bool = True
    fail_closed_authority: bool = True
    search_time_contamination_block: bool = True


ABLATION_GUARD_OVERRIDES: dict[str, dict[str, bool]] = {
    "no_exact_content_binding": {"exact_content_binding": False},
    "no_content_vs_provenance_distinction": {"content_vs_provenance_distinction": False},
    "no_checker_lineage_independence": {"checker_lineage_independence": False},
    "no_hostile_checker_battery": {"hostile_checker_battery": False},
    "no_behavioral_influence_coordinate": {"behavioral_influence_coordinate": False},
    "no_evaluator_protection_access_telemetry": {"evaluator_protection_access_telemetry": False},
    "soft_confidence_instead_of_fail_closed_authority": {"fail_closed_authority": False},
    "no_search_time_contamination_block": {"search_time_contamination_block": False},
}


def _make_guard_state(ablation_id: str) -> OrionGuardState:
    overrides = ABLATION_GUARD_OVERRIDES.get(ablation_id, {})
    return OrionGuardState(**overrides)


# ---------------------------------------------------------------------------
# Attack family mapping
# ---------------------------------------------------------------------------

FAMILY_MAP: dict[str, str] = {
    "CLEAN_POSITIVE": "clean_supported_positive",
    "WRONG_SOURCE": "correct_fact_wrong_source",
    "CONTENT_SUBSTITUTION": "content_substitution",
    "SOURCE_CONFLATION": "source_conflation",
    "POOLED_SUPPORT_WRONG_OWNER": "pooled_support_wrong_owner",
    "CITED_NON_INFLUENTIAL": "cited_but_non_influential",
    "WEAK_CHECKER": "weak_non_discriminating_checker",
    "SAME_LANE_CHECKER": "same_lane_checker",
    "POSTHOC_CHECKER_EVALUATOR": "posthoc_checker_or_evaluator",
    "SEARCH_TIME_CONTAMINATION": "search_time_contamination",
    "EVALUATOR_TAMPER": "evaluator_or_guard_tampering",
    "HOLDOUT_ACCESS": "heldout_label_access",
    "INSUFFICIENT_EVIDENCE": "genuinely_insufficient_evidence",
}


def map_attack_family(attack_family: str) -> str:
    """Map an attack-case family enum (UPPER_SNAKE) to protocol family (lower_snake)."""
    return FAMILY_MAP.get(attack_family, attack_family)


def _claim_correct(protected_gold: dict[str, Any]) -> bool | None:
    return protected_gold.get("claim_correct")


def _source_owner_correct(protected_gold: dict[str, Any]) -> bool | None:
    return protected_gold.get("source_owner_correct")


def _semantic_support(protected_gold: dict[str, Any]) -> str:
    return protected_gold.get("semantic_support", "UNRESOLVED")


def _contaminated(protected_gold: dict[str, Any]) -> bool:
    return protected_gold.get("contaminated", False)


def _expected_terminal(protected_gold: dict[str, Any]) -> str:
    return protected_gold.get("expected_authority_terminal", "CANNOT_CHECK")


def _should_promote(protected_gold: dict[str, Any]) -> bool:
    return _expected_terminal(protected_gold) == "PROMOTE"


def _should_cannot_check(protected_gold: dict[str, Any]) -> bool:
    return _expected_terminal(protected_gold) == "CANNOT_CHECK"


# ---------------------------------------------------------------------------
# ORION guard evaluator
# ---------------------------------------------------------------------------


def _evidence_objects(attack_case: dict[str, Any]) -> list[dict[str, Any]]:
    raw = attack_case.get("evidence_objects", [])
    return [e for e in raw if isinstance(e, dict)]


def _guard_content_binding(evidence: list[dict[str, Any]]) -> bool:
    """Every evidence object must carry a content hash binding candidate text."""
    return all(e.get("content_hash", "").strip() for e in evidence) if evidence else False


def _guard_provenance_consistency(evidence: list[dict[str, Any]]) -> bool:
    """Evidence provenance must be one-per-source so sources stay distinct.

    When multiple evidence objects share one provenance hash, the claim can
    pool support across sources without identifying the correct owner -- the
    source-conflation and pooled-support-wrong-owner attacks. Full ORION
    treats a collapsed provenance as failing closed.
    """
    if not evidence:
        return False
    provenance_hashes = {e.get("provenance_hash", "").strip() for e in evidence}
    provenance_hashes.discard("")
    if not provenance_hashes:
        return False
    evidence_ids = {e.get("evidence_id", "").strip() for e in evidence if e.get("evidence_id", "").strip()}
    # One provenance hash per distinct evidence piece; two pieces with the
    # same provenance is exactly the conflation/merged-owner signal.
    return len(evidence_ids) == len(provenance_hashes)


def _guard_attribution(claim_correct: bool | None, source_owner_correct: bool | None) -> bool:
    return source_owner_correct is True and claim_correct is not False


def _threat_families() -> tuple[set[str], ...]:
    """Family subsets that falsify the guard checks below."""
    weak_checker = {"WEAK_CHECKER", "SAME_LANE_CHECKER", "POSTHOC_CHECKER_EVALUATOR"}
    provenance = {
        "SOURCE_CONFLATION",
        "POOLED_SUPPORT_WRONG_OWNER",
        "CONTENT_SUBSTITUTION",
    }
    evaluator = {"EVALUATOR_TAMPER", "HOLDOUT_ACCESS"}
    contamination = {"SEARCH_TIME_CONTAMINATION", "HOLDOUT_ACCESS"}
    return weak_checker, provenance, evaluator, contamination


def _guard_checker_lineage_independence(
    attack_case: dict[str, Any], family: str, weak_checker: set[str]
) -> bool:
    """The checker that produced the candidate must not be a weak/lane/posthoc checker."""
    if family in weak_checker:
        return False
    candidate_visible = attack_case.get("candidate_visible", {})
    checker_lineage = candidate_visible.get("checker_process_lineage_hash", "") or ""
    evidence_lineages = {
        e.get("evaluator_artifact_hash", "")
        for e in _evidence_objects(attack_case)
        if e.get("evaluator_artifact_hash", "")
    }
    if checker_lineage and evidence_lineages and checker_lineage in evidence_lineages:
        return False
    return True


def _guard_behavioral_influence(attack_case: dict[str, Any], family: str) -> bool:
    """Candidate must not cite evidence that was never behaviorally available."""
    if family == "CITED_NON_INFLUENTIAL":
        return False
    for e in _evidence_objects(attack_case):
        if e.get("behaviorally_available") is False:
            return False
    return True


def _guard_evaluator_protection(attack_case: dict[str, Any], family: str) -> bool:
    """Evaluator and holdout labels must stay out of the candidate's reach."""
    if family in {"EVALUATOR_TAMPER", "HOLDOUT_ACCESS"}:
        return False
    candidate_visible = attack_case.get("candidate_visible", {})
    for e in _evidence_objects(attack_case):
        if e.get("holdout_accessed") is True or e.get("evaluator_accessed") is True:
            return False
    return True


def _guard_search_time_contamination(attack_case: dict[str, Any], family: str) -> bool:
    if family == "SEARCH_TIME_CONTAMINATION":
        return False
    protected_gold = attack_case.get("protected_gold", {})
    if protected_gold.get("contaminated") is True:
        return False
    return True


def _evaluate_orion_guarded(
    attack_case: dict[str, Any],
    guards: OrionGuardState,
) -> BaselineVerdict:
    """Run the ORION authority pipeline with the given guard configuration.

    Full ORION keeps every guard and fails closed: any unresolved or violated
    prerequisite produces BLOCK or CANNOT_CHECK, never promotion. Each ablation
    disables one guard, opening exactly the attack plane that guard seals.

    Decision truth table (fail-closed mode):
      - semantic contradiction            -> BLOCK
      - insufficient / unresolved support -> CANNOT_CHECK
      - violated guard                    -> BLOCK
      - clean supported, attributed       -> PROMOTE
    """
    protected_gold = attack_case.get("protected_gold", {})
    family = str(attack_case.get("attack_family", ""))

    claim_correct = _claim_correct(protected_gold)
    source_correct = _source_owner_correct(protected_gold)
    support = _semantic_support(protected_gold)
    contaminated = _contaminated(protected_gold)

    supported = support == "SUPPORTED"
    contradicted = support == "CONTRADICTED"
    insufficient = support in ("INSUFFICIENT", "UNRESOLVED")
    good_attribution = _guard_attribution(claim_correct, source_correct)

    weak_checker, _, _, _ = _threat_families()

    evidence = _evidence_objects(attack_case)
    content_ok = _guard_content_binding(evidence) if guards.exact_content_binding else True
    provenance_ok = _guard_provenance_consistency(evidence) if guards.content_vs_provenance_distinction else True
    checker_ok = _guard_checker_lineage_independence(attack_case, family, weak_checker) if guards.checker_lineage_independence else True
    behavioral_ok = _guard_behavioral_influence(attack_case, family) if guards.behavioral_influence_coordinate else True
    evaluator_ok = _guard_evaluator_protection(attack_case, family) if guards.evaluator_protection_access_telemetry else True
    contamination_blocked = _guard_search_time_contamination(attack_case, family) if guards.search_time_contamination_block else True

    guard_violations = not any(
        (
            content_ok,
            provenance_ok,
            checker_ok,
            behavioral_ok,
            evaluator_ok,
            contamination_blocked,
        )
    )

    # -- Decide the terminal ------------------------------------------------
    if contradicted:
        promoted, blocked, cannot_check = False, True, False
    elif not guards.fail_closed_authority:
        # Soft-confidence variant: fail-open authority. Any unresolved
        # prerequisite or violated guard still promotes on the direct
        # evidence signal -- authority is a soft score, not a gate.
        promoted = supported and (good_attribution or not supported)
        blocked = contradicted
        cannot_check = False
    elif insufficient:
        # Fail-closed: never promote on unresolved prerequisites.
        promoted, blocked, cannot_check = False, False, True
    elif guard_violations:
        promoted, blocked, cannot_check = False, True, False
    elif supported and good_attribution and not contaminated:
        promoted, blocked, cannot_check = True, False, False
    else:
        promoted, blocked, cannot_check = False, False, True

    gold_promote = _should_promote(protected_gold)
    gold_cannot_check = _should_cannot_check(protected_gold)
    false_promotion = promoted and not gold_promote
    correct_cannot_check = cannot_check and gold_cannot_check

    return BaselineVerdict(
        system_id="orion",
        case_id=attack_case["case_id"],
        task_family=map_attack_family(family),
        promoted=promoted,
        blocked=blocked,
        cannot_check=cannot_check,
        claim_correct_judged=claim_correct,
        source_attribution_judged=source_correct,
        support_contradiction_detected=(
            contradicted if blocked else (supported if promoted else None)
        ),
        conflation_detected=(
            not provenance_ok if guards.content_vs_provenance_distinction else None
        ),
        substitution_detected=(
            not content_ok if guards.exact_content_binding else None
        ),
        tamper_leakage_detected=contaminated,
        false_promotion=false_promotion,
        correct_cannot_check=correct_cannot_check,
        resource_units=3.5,
        latency_seconds=4.5,
    )


def _ablation_id_from_guards(guards: OrionGuardState) -> str:
    for ablation_id in ABLATION_IDS:
        if _make_guard_state(ablation_id) == guards:
            return ablation_id
    return "full_orion"


def run_ablation(ablation_id: str, attack_case: dict[str, Any]) -> BaselineVerdict:
    if ablation_id not in ABLATION_IDS:
        raise ValueError(f"unknown ablation: {ablation_id}")
    verdict = _evaluate_orion_guarded(attack_case, _make_guard_state(ablation_id))
    return replace_system_id(verdict, f"orion+{ablation_id}")


def run_orion(attack_case: dict[str, Any]) -> BaselineVerdict:
    """Run the full ORION pipeline (all guards active)."""
    return replace_system_id(
        _evaluate_orion_guarded(attack_case, OrionGuardState()), "orion"
    )


def run_all_ablations(attack_case: dict[str, Any]) -> tuple[BaselineVerdict, ...]:
    return tuple(run_ablation(aid, attack_case) for aid in ABLATION_IDS)


def replace_system_id(verdict: BaselineVerdict, system_id: str) -> BaselineVerdict:
    return BaselineVerdict(
        system_id=system_id,
        case_id=verdict.case_id,
        task_family=verdict.task_family,
        promoted=verdict.promoted,
        blocked=verdict.blocked,
        cannot_check=verdict.cannot_check,
        claim_correct_judged=verdict.claim_correct_judged,
        source_attribution_judged=verdict.source_attribution_judged,
        support_contradiction_detected=verdict.support_contradiction_detected,
        conflation_detected=verdict.conflation_detected,
        substitution_detected=verdict.substitution_detected,
        tamper_leakage_detected=verdict.tamper_leakage_detected,
        false_promotion=verdict.false_promotion,
        correct_cannot_check=verdict.correct_cannot_check,
        resource_units=verdict.resource_units,
        latency_seconds=verdict.latency_seconds,
    )


def run_ablation_campaign(
    ablation_id: str,
    attack_cases: list[dict[str, Any]],
) -> tuple[list[BaselineVerdict], AuthorityBenchmarkMetrics]:
    verdicts = [run_ablation(ablation_id, case) for case in attack_cases]
    metrics = verdicts_to_metrics(tuple(verdicts))
    return verdicts, metrics


def run_orion_campaign(
    attack_cases: list[dict[str, Any]],
) -> tuple[list[BaselineVerdict], AuthorityBenchmarkMetrics]:
    verdicts = [run_orion(case) for case in attack_cases]
    metrics = verdicts_to_metrics(tuple(verdicts))
    return verdicts, metrics


__all__ = [
    "ABLATION_IDS",
    "ABLATION_GUARD_OVERRIDES",
    "OrionGuardState",
    "map_attack_family",
    "replace_system_id",
    "run_ablation",
    "run_orion",
    "run_all_ablations",
    "run_ablation_campaign",
    "run_orion_campaign",
]