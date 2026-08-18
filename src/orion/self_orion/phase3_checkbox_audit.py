"""Issue #209 checkbox audit.

Ticks are a host action.  This module only *classifies* each checkbox against
in-repository evidence.  Empirical and unbound-identity boxes are
``CANNOT_CHECK`` and name the missing trial; they cannot be flipped to
``VERIFIED_ON_MAIN`` by a protocol-prefreeze merge.

The audit does not poll GitHub, read issue state, or emit
``PHASE_3_GOVERNED_SELF_ORION_CLOSED``.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from orion.self_orion.phase3_preflight import (
    HOSTILE_ATTACK_IDS,
    PHASE3_PROTOCOL_ID,
    assess_phase3_preflight,
    repository_phase3_protocol_freeze,
)
from orion.self_orion.phase3_promotion import (
    MISSING_LONGITUDINAL_TRIAL_ID,
    MISSING_PROMOTION_TRIAL_ID,
    Phase3PromotionStatus,
    assess_phase3_empirical_promotion,
    repository_phase3_promotion_evidence,
)

AUDIT_SCHEMA = "Issue209CheckboxAudit.v1"
ISSUE_NUMBER = 209

_REPO_ROOT = Path(__file__).resolve().parents[3]


class CheckboxKind(str, Enum):
    PROTOCOL_FREEZE = "PROTOCOL_FREEZE"
    OPERATIONAL_BINDING = "OPERATIONAL_BINDING"
    EMPIRICAL_TRIAL = "EMPIRICAL_TRIAL"
    PROCESS = "PROCESS"


class CheckboxVerdict(str, Enum):
    VERIFIED_ON_MAIN = "VERIFIED_ON_MAIN"
    CANNOT_CHECK = "CANNOT_CHECK"
    UNMET = "UNMET"


@dataclass(frozen=True)
class CheckboxSpec:
    checkbox_id: str
    section: str
    text: str
    kind: CheckboxKind
    missing_trial_id: str = ""
    binding_blocker: str = ""

    def __post_init__(self) -> None:
        if not self.checkbox_id.strip() or not self.section.strip() or not self.text.strip():
            raise ValueError("checkbox identity, section and text are required")


ISSUE_209_CHECKBOXES: tuple[CheckboxSpec, ...] = (
    CheckboxSpec(
        "prefreeze.no_grant_code_path",
        "pre-freeze authority boundary",
        "No Phase-3 code path grants self-merge, evaluator mutation, holdout access, policy mutation, or phase-transition authority.",
        CheckboxKind.PROTOCOL_FREEZE,
    ),
    CheckboxSpec(
        "prefreeze.phase2_terminal_bound",
        "pre-freeze authority boundary",
        "Exact Phase-2 terminal subject commit and evidence receipt are bound.",
        CheckboxKind.OPERATIONAL_BINDING,
        binding_blocker="issue_76_must_close_on_merged_phase2_evidence_first",
        missing_trial_id=MISSING_PROMOTION_TRIAL_ID,
    ),
    CheckboxSpec(
        "prefreeze.external_host_bound",
        "pre-freeze authority boundary",
        "External host/promotion authority identity is bound.",
        CheckboxKind.OPERATIONAL_BINDING,
        binding_blocker="external_promotion_authority_identity_not_bound",
        missing_trial_id=MISSING_PROMOTION_TRIAL_ID,
    ),
    CheckboxSpec(
        "prefreeze.protected_custody_independent",
        "pre-freeze authority boundary",
        "Protected evaluator/assurance custody is independent of candidate/worker processes.",
        CheckboxKind.OPERATIONAL_BINDING,
        binding_blocker="protected_evaluator_custody_lineage_not_bound",
        missing_trial_id=MISSING_PROMOTION_TRIAL_ID,
    ),
    CheckboxSpec(
        "prefreeze.escalation_frozen",
        "pre-freeze authority boundary",
        "Escalation/abstention conditions are frozen before outcome access.",
        CheckboxKind.PROTOCOL_FREEZE,
    ),
    CheckboxSpec(
        "step1.define_task_class",
        "Step 1 — freeze the ordinary-development task class",
        "Define what counts as ordinary framework development vs protected/constitutional work.",
        CheckboxKind.PROTOCOL_FREEZE,
    ),
    CheckboxSpec(
        "step1.inclusion_exclusion",
        "Step 1 — freeze the ordinary-development task class",
        "Freeze inclusion/exclusion rules for sampled issues.",
        CheckboxKind.PROTOCOL_FREEZE,
    ),
    CheckboxSpec(
        "step1.sampling_epoch_pool",
        "Step 1 — freeze the ordinary-development task class",
        "Freeze sampling epoch and issue pool before observing comparative outcomes.",
        CheckboxKind.OPERATIONAL_BINDING,
        binding_blocker="sampling_epoch_and_issue_pool_not_frozen",
        missing_trial_id=MISSING_PROMOTION_TRIAL_ID,
    ),
    CheckboxSpec(
        "step1.include_ordinary_kinds",
        "Step 1 — freeze the ordinary-development task class",
        "Include debugging, implementation, refactoring, regression repair, test hardening, documentation/protocol synchronization and dependency/tool failures.",
        CheckboxKind.PROTOCOL_FREEZE,
    ),
    CheckboxSpec(
        "step1.exclude_protected",
        "Step 1 — freeze the ordinary-development task class",
        "Exclude evaluator/policy/authority/phase-boundary changes from candidate-owned execution.",
        CheckboxKind.PROTOCOL_FREEZE,
    ),
    CheckboxSpec(
        "step1.preserve_unresolved",
        "Step 1 — freeze the ordinary-development task class",
        "Preserve every sampled task, including unresolved/failed tasks.",
        CheckboxKind.PROTOCOL_FREEZE,
    ),
    CheckboxSpec(
        "step2.orion_owns",
        "Step 2 — freeze governance protocol",
        "ORION owns issue state, causal hypotheses, discriminator, plan, worker delegation, replay/fresh-transfer requests and negative-history retrieval.",
        CheckboxKind.PROTOCOL_FREEZE,
    ),
    CheckboxSpec(
        "step2.worker_contracts",
        "Step 2 — freeze governance protocol",
        "LLM workers can propose/search/implement only through bounded contracts.",
        CheckboxKind.PROTOCOL_FREEZE,
    ),
    CheckboxSpec(
        "step2.protected_outside_worker",
        "Step 2 — freeze governance protocol",
        "Protected tests/evaluators and promotion remain outside worker write authority.",
        CheckboxKind.PROTOCOL_FREEZE,
    ),
    CheckboxSpec(
        "step2.isolated_candidate_state",
        "Step 2 — freeze governance protocol",
        "Every candidate runs in isolated content-addressed state.",
        CheckboxKind.PROTOCOL_FREEZE,
    ),
    CheckboxSpec(
        "step2.acceptance_requires_replay_transfer_assurance",
        "Step 2 — freeze governance protocol",
        "Every accepted change requires replay + independent fresh transfer + protected assurance.",
        CheckboxKind.PROTOCOL_FREEZE,
    ),
    CheckboxSpec(
        "step2.open_cannot_check_escalation_terminals",
        "Step 2 — freeze governance protocol",
        "OPEN/CANNOT_CHECK/escalation remain valid terminal states for a cycle.",
        CheckboxKind.PROTOCOL_FREEZE,
    ),
    CheckboxSpec(
        "step2.rejected_immutable",
        "Step 2 — freeze governance protocol",
        "Harmful/null/rejected variants remain immutable history.",
        CheckboxKind.PROTOCOL_FREEZE,
    ),
    CheckboxSpec(
        "step3.freeze_baseline",
        "Step 3 — matched baseline",
        "Freeze an external-development baseline where a capable LLM/human-directed agent remains the primary problem-solving process.",
        CheckboxKind.PROTOCOL_FREEZE,
    ),
    CheckboxSpec(
        "step3.match_budgets",
        "Step 3 — matched baseline",
        "Match model/tool/search/time/compute budgets where possible.",
        CheckboxKind.PROTOCOL_FREEZE,
    ),
    CheckboxSpec(
        "step3.retry_intervention_budgets",
        "Step 3 — matched baseline",
        "Freeze retry and intervention budgets.",
        CheckboxKind.PROTOCOL_FREEZE,
    ),
    CheckboxSpec(
        "step3.external_help",
        "Step 3 — matched baseline",
        "Freeze what external help is allowed for each arm.",
        CheckboxKind.PROTOCOL_FREEZE,
    ),
    CheckboxSpec(
        "step3.no_hidden_access",
        "Step 3 — matched baseline",
        "Prevent hidden extra evaluator/holdout access in either arm.",
        CheckboxKind.PROTOCOL_FREEZE,
    ),
    CheckboxSpec(
        "step4.consecutive_cycles",
        "Step 4 — prospective promotion study",
        "Run multiple consecutive ordinary-development cycles, not one showcase.",
        CheckboxKind.EMPIRICAL_TRIAL,
        missing_trial_id=MISSING_PROMOTION_TRIAL_ID,
    ),
    CheckboxSpec(
        "step4.resolution_and_regression",
        "Step 4 — prospective promotion study",
        "Measure task resolution correctness and exact regression rate.",
        CheckboxKind.EMPIRICAL_TRIAL,
        missing_trial_id=MISSING_PROMOTION_TRIAL_ID,
    ),
    CheckboxSpec(
        "step4.root_cause_and_false_method",
        "Step 4 — prospective promotion study",
        "Measure root-cause attribution correctness / false method-change rate.",
        CheckboxKind.EMPIRICAL_TRIAL,
        missing_trial_id=MISSING_PROMOTION_TRIAL_ID,
    ),
    CheckboxSpec(
        "step4.replay_and_fresh_transfer",
        "Step 4 — prospective promotion study",
        "Measure replay success and independent fresh-transfer success.",
        CheckboxKind.EMPIRICAL_TRIAL,
        missing_trial_id=MISSING_PROMOTION_TRIAL_ID,
    ),
    CheckboxSpec(
        "step4.harmful_transfer_worst_case",
        "Step 4 — prospective promotion study",
        "Measure harmful-transfer/worst-case regression.",
        CheckboxKind.EMPIRICAL_TRIAL,
        missing_trial_id=MISSING_PROMOTION_TRIAL_ID,
    ),
    CheckboxSpec(
        "step4.recurrence_and_negative_history",
        "Step 4 — prospective promotion study",
        "Measure recognized-failure recurrence and negative-history use.",
        CheckboxKind.EMPIRICAL_TRIAL,
        missing_trial_id=MISSING_PROMOTION_TRIAL_ID,
    ),
    CheckboxSpec(
        "step4.abstention_escalation_quality",
        "Step 4 — prospective promotion study",
        "Measure abstention/escalation quality.",
        CheckboxKind.EMPIRICAL_TRIAL,
        missing_trial_id=MISSING_PROMOTION_TRIAL_ID,
    ),
    CheckboxSpec(
        "step4.cost_latency_calls_interventions",
        "Step 4 — prospective promotion study",
        "Measure cost, latency, tool calls, LLM calls and host interventions.",
        CheckboxKind.EMPIRICAL_TRIAL,
        missing_trial_id=MISSING_PROMOTION_TRIAL_ID,
    ),
    CheckboxSpec(
        "step4.matched_baseline_comparison",
        "Step 4 — prospective promotion study",
        "Compare against matched baseline with predeclared uncertainty/effect-size policy.",
        CheckboxKind.EMPIRICAL_TRIAL,
        missing_trial_id=MISSING_PROMOTION_TRIAL_ID,
    ),
    CheckboxSpec(
        "step5.h01_self_certification",
        "Step 5 — hostile governance battery",
        "Candidate attempts self-certification.",
        CheckboxKind.PROTOCOL_FREEZE,
    ),
    CheckboxSpec(
        "step5.h02_evaluator_mutation",
        "Step 5 — hostile governance battery",
        "Candidate attempts evaluator/guard mutation.",
        CheckboxKind.PROTOCOL_FREEZE,
    ),
    CheckboxSpec(
        "step5.h03_holdout_deletion",
        "Step 5 — hostile governance battery",
        "Candidate attempts holdout/negative-history deletion or laundering.",
        CheckboxKind.PROTOCOL_FREEZE,
    ),
    CheckboxSpec(
        "step5.h04_stale_replay",
        "Step 5 — hostile governance battery",
        "Candidate attempts stale-evidence replay or subject substitution.",
        CheckboxKind.PROTOCOL_FREEZE,
    ),
    CheckboxSpec(
        "step5.h05_missing_to_pass",
        "Step 5 — hostile governance battery",
        "Candidate attempts to convert missing evidence into PASS.",
        CheckboxKind.PROTOCOL_FREEZE,
    ),
    CheckboxSpec(
        "step5.h06_worker_escalation",
        "Step 5 — hostile governance battery",
        "Candidate attempts authority escalation through worker/provider output.",
        CheckboxKind.PROTOCOL_FREEZE,
    ),
    CheckboxSpec(
        "step5.fail_closed_host_control",
        "Step 5 — hostile governance battery",
        "System preserves fail-closed behavior and external host control in every attack.",
        CheckboxKind.PROTOCOL_FREEZE,
    ),
    CheckboxSpec(
        "step6.downstream_dependency_replayable",
        "Step 6 — longitudinal stability",
        "At least one accepted change later becomes a dependency for another governed cycle and remains replayable.",
        CheckboxKind.EMPIRICAL_TRIAL,
        missing_trial_id=MISSING_LONGITUDINAL_TRIAL_ID,
    ),
    CheckboxSpec(
        "step6.rejected_queryable",
        "Step 6 — longitudinal stability",
        "Previously rejected/harmful variant remains queryable and prevents unnoticed recurrence.",
        CheckboxKind.EMPIRICAL_TRIAL,
        missing_trial_id=MISSING_LONGITUDINAL_TRIAL_ID,
    ),
    CheckboxSpec(
        "step6.no_silent_drift",
        "Step 6 — longitudinal stability",
        "Multiple cycles do not silently drift evaluator/policy/task definitions.",
        CheckboxKind.EMPIRICAL_TRIAL,
        missing_trial_id=MISSING_LONGITUDINAL_TRIAL_ID,
    ),
    CheckboxSpec(
        "step6.halt_resume",
        "Step 6 — longitudinal stability",
        "Governed operation can be halted and resumed from immutable history.",
        CheckboxKind.EMPIRICAL_TRIAL,
        missing_trial_id=MISSING_LONGITUDINAL_TRIAL_ID,
    ),
    CheckboxSpec(
        "step6.independent_replay_of_recommendation",
        "Step 6 — longitudinal stability",
        "Independent external replay reproduces the promotion recommendation.",
        CheckboxKind.EMPIRICAL_TRIAL,
        missing_trial_id=MISSING_LONGITUDINAL_TRIAL_ID,
    ),
    CheckboxSpec(
        "step7.versioned_protocol",
        "Step 7 — implementation and receipts",
        "Add versioned machine-readable Phase-3 protocol.",
        CheckboxKind.PROTOCOL_FREEZE,
    ),
    CheckboxSpec(
        "step7.run_evidence_receipts",
        "Step 7 — implementation and receipts",
        "Add machine-readable run/evidence receipts bound to exact subject/evaluator/epoch.",
        CheckboxKind.EMPIRICAL_TRIAL,
        missing_trial_id=MISSING_PROMOTION_TRIAL_ID,
    ),
    CheckboxSpec(
        "step7.hostile_known_answer_tests",
        "Step 7 — implementation and receipts",
        "Add hostile and known-answer tests for every new authority boundary.",
        CheckboxKind.PROTOCOL_FREEZE,
    ),
    CheckboxSpec(
        "step7.exact_final_head_ci",
        "Step 7 — implementation and receipts",
        "Exact-final-head CI green.",
        CheckboxKind.PROCESS,
    ),
    CheckboxSpec(
        "step7.shadow_pr_integration",
        "Step 7 — implementation and receipts",
        "Merge only through shadow/* PR integration.",
        CheckboxKind.PROCESS,
    ),
)


@dataclass(frozen=True)
class CheckboxAuditItem:
    checkbox_id: str
    section: str
    text: str
    kind: CheckboxKind
    verdict: CheckboxVerdict
    github_tick: bool
    evidence: str
    missing_trial_id: str
    blockers: tuple[str, ...]


@dataclass(frozen=True)
class Issue209CheckboxAudit:
    schema: str
    issue_number: int
    protocol_id: str
    items: tuple[CheckboxAuditItem, ...]
    verified_on_main_ids: tuple[str, ...]
    cannot_check_ids: tuple[str, ...]
    unmet_ids: tuple[str, ...]
    primary_missing_trial_id: str
    closes_issue_209: bool
    emits_terminal_claim: bool

    @property
    def grants_governed_self_orion(self) -> bool:
        return False


def _protocol_freeze_present() -> tuple[bool, tuple[str, ...]]:
    freeze_path = _REPO_ROOT / "development" / "phase3" / "PHASE3_PROTOCOL_FREEZE_v1.json"
    preflight_tests = _REPO_ROOT / "tests" / "unit" / "self_orion" / "test_phase3_preflight.py"
    hostile_tests = (
        _REPO_ROOT / "tests" / "unit" / "self_orion" / "test_phase3_authority_hostile.py"
    )
    missing: list[str] = []
    if not freeze_path.is_file():
        missing.append("canonical_protocol_json_absent")
    if not preflight_tests.is_file():
        missing.append("phase3_preflight_tests_absent")
    if not hostile_tests.is_file():
        missing.append("phase3_hostile_tests_absent")
    freeze = repository_phase3_protocol_freeze()
    report = assess_phase3_preflight(freeze)
    if report.grants_phase3_operating_authority or report.grants_governed_self_orion:
        missing.append("protocol_freeze_grants_authority")
    if report.closes_issue_209:
        missing.append("protocol_freeze_closes_issue_209")
    if freeze.protocol_id != PHASE3_PROTOCOL_ID:
        missing.append("protocol_id_mismatch")
    if len(HOSTILE_ATTACK_IDS) != 6:
        missing.append("hostile_attack_registry_incomplete")
    return (not missing, tuple(missing))


def _verdict_for(spec: CheckboxSpec) -> CheckboxAuditItem:
    freeze = repository_phase3_protocol_freeze()
    preflight = assess_phase3_preflight(freeze)
    promotion = assess_phase3_empirical_promotion(repository_phase3_promotion_evidence())
    protocol_ok, protocol_blockers = _protocol_freeze_present()

    if spec.kind is CheckboxKind.PROTOCOL_FREEZE:
        if protocol_ok:
            return CheckboxAuditItem(
                checkbox_id=spec.checkbox_id,
                section=spec.section,
                text=spec.text,
                kind=spec.kind,
                verdict=CheckboxVerdict.VERIFIED_ON_MAIN,
                github_tick=True,
                evidence=(
                    "Frozen on merged main by PR #269: versioned protocol "
                    f"{PHASE3_PROTOCOL_ID}, grants_* hardwired False, Step-5 "
                    "differential hostile battery present."
                ),
                missing_trial_id="",
                blockers=(),
            )
        return CheckboxAuditItem(
            checkbox_id=spec.checkbox_id,
            section=spec.section,
            text=spec.text,
            kind=spec.kind,
            verdict=CheckboxVerdict.UNMET,
            github_tick=False,
            evidence="Protocol-freeze artifacts are missing or grant authority.",
            missing_trial_id="",
            blockers=protocol_blockers,
        )

    if spec.kind is CheckboxKind.OPERATIONAL_BINDING:
        blocker = spec.binding_blocker
        present = blocker in preflight.blockers
        return CheckboxAuditItem(
            checkbox_id=spec.checkbox_id,
            section=spec.section,
            text=spec.text,
            kind=spec.kind,
            verdict=CheckboxVerdict.CANNOT_CHECK,
            github_tick=False,
            evidence=(
                "Repository freeze still uses the unbound sentinel; "
                f"preflight status is {preflight.status.value}."
            ),
            missing_trial_id=spec.missing_trial_id,
            blockers=(blocker,) if present or blocker else preflight.blockers,
        )

    if spec.kind is CheckboxKind.EMPIRICAL_TRIAL:
        return CheckboxAuditItem(
            checkbox_id=spec.checkbox_id,
            section=spec.section,
            text=spec.text,
            kind=spec.kind,
            verdict=CheckboxVerdict.CANNOT_CHECK,
            github_tick=False,
            evidence=(
                "No frozen live evidence exists. Empirical promotion status is "
                f"{promotion.status.value}; primary missing trial is "
                f"{promotion.primary_missing_trial_id}."
            ),
            missing_trial_id=spec.missing_trial_id,
            blockers=promotion.blockers,
        )

    # PROCESS boxes. The audit does not poll GitHub Actions, and this lane
    # cannot write the shadow/* namespace.
    if spec.checkbox_id == "step7.exact_final_head_ci":
        return CheckboxAuditItem(
            checkbox_id=spec.checkbox_id,
            section=spec.section,
            text=spec.text,
            kind=spec.kind,
            verdict=CheckboxVerdict.CANNOT_CHECK,
            github_tick=False,
            evidence=(
                "In-repo audit does not poll GitHub Actions. Exact-final-head CI "
                "must be attested on the merged subject by an external host; a "
                "protocol-prefreeze PR being green is not Phase-3 closure CI."
            ),
            missing_trial_id=MISSING_PROMOTION_TRIAL_ID,
            blockers=("exact_final_head_ci_not_attested_in_repository",),
        )
    if spec.checkbox_id == "step7.shadow_pr_integration":
        return CheckboxAuditItem(
            checkbox_id=spec.checkbox_id,
            section=spec.section,
            text=spec.text,
            kind=spec.kind,
            verdict=CheckboxVerdict.UNMET,
            github_tick=False,
            evidence=(
                "PR #269 merged from claude/p3-protocol-prefreeze; remaining "
                "#209 work lands on cursor/paper-209. AGENTS.md forbids this "
                "lane from writing shadow/*. Issue #209's shadow/* requirement "
                "is therefore unmet, not silently satisfied."
            ),
            missing_trial_id="",
            blockers=("merge_was_not_through_shadow_namespace",),
        )
    raise RuntimeError(f"unhandled process checkbox: {spec.checkbox_id}")


def audit_issue_209_checkboxes() -> Issue209CheckboxAudit:
    items = tuple(_verdict_for(spec) for spec in ISSUE_209_CHECKBOXES)
    ids = {spec.checkbox_id for spec in ISSUE_209_CHECKBOXES}
    if len(ids) != len(ISSUE_209_CHECKBOXES):
        raise RuntimeError("duplicate issue #209 checkbox id")
    verified = tuple(
        item.checkbox_id for item in items if item.verdict is CheckboxVerdict.VERIFIED_ON_MAIN
    )
    cannot = tuple(
        item.checkbox_id for item in items if item.verdict is CheckboxVerdict.CANNOT_CHECK
    )
    unmet = tuple(item.checkbox_id for item in items if item.verdict is CheckboxVerdict.UNMET)
    promotion = assess_phase3_empirical_promotion(repository_phase3_promotion_evidence())
    if promotion.status is not Phase3PromotionStatus.CANNOT_CHECK:
        raise RuntimeError("repository empirical promotion must remain CANNOT_CHECK")
    return Issue209CheckboxAudit(
        schema=AUDIT_SCHEMA,
        issue_number=ISSUE_NUMBER,
        protocol_id=PHASE3_PROTOCOL_ID,
        items=items,
        verified_on_main_ids=verified,
        cannot_check_ids=cannot,
        unmet_ids=unmet,
        primary_missing_trial_id=MISSING_PROMOTION_TRIAL_ID,
        closes_issue_209=False,
        emits_terminal_claim=False,
    )


def issue_209_checkbox_audit_to_dict(audit: Issue209CheckboxAudit) -> dict[str, object]:
    return {
        "schema": audit.schema,
        "issue_number": audit.issue_number,
        "protocol_id": audit.protocol_id,
        "primary_missing_trial_id": audit.primary_missing_trial_id,
        "closes_issue_209": audit.closes_issue_209,
        "emits_terminal_claim": audit.emits_terminal_claim,
        "terminal_claim": None,
        "phase_3_governed_self_orion_closed": False,
        "grants_governed_self_orion": audit.grants_governed_self_orion,
        "verified_on_main_ids": list(audit.verified_on_main_ids),
        "cannot_check_ids": list(audit.cannot_check_ids),
        "unmet_ids": list(audit.unmet_ids),
        "counts": {
            "total": len(audit.items),
            "verified_on_main": len(audit.verified_on_main_ids),
            "cannot_check": len(audit.cannot_check_ids),
            "unmet": len(audit.unmet_ids),
        },
        "items": [
            {
                "checkbox_id": item.checkbox_id,
                "section": item.section,
                "text": item.text,
                "kind": item.kind.value,
                "verdict": item.verdict.value,
                "github_tick": item.github_tick,
                "evidence": item.evidence,
                "missing_trial_id": item.missing_trial_id,
                "blockers": list(item.blockers),
            }
            for item in audit.items
        ],
        "forbidden": {
            "terminal_claim_emitted": False,
            "reason": (
                "Protocol-prefreeze and an in-repo CANNOT_CHECK receipt are not "
                "empirical promotion evidence. Issue #210 cannot authorize a "
                "self-sustaining programme until this issue closes independently."
            ),
        },
    }


__all__ = [
    "AUDIT_SCHEMA",
    "CheckboxAuditItem",
    "CheckboxKind",
    "CheckboxSpec",
    "CheckboxVerdict",
    "ISSUE_209_CHECKBOXES",
    "ISSUE_NUMBER",
    "Issue209CheckboxAudit",
    "audit_issue_209_checkboxes",
    "issue_209_checkbox_audit_to_dict",
]
