"""Prospective finite benchmark for #508 failure epistemology.

The benchmark asks whether scoped negative history is useful relative to
success-only/no-memory and naive failure-memory controls, and whether a strong
standard parent composition already reproduces the ORION behavior.

The ORION arm uses ``FailureKnowledge.v1`` only as a typed storage/applicability
contract and combines it with independently represented responsibility,
P7-style transport witnesses, and #477-style decision-relevant query selection.
It cannot infer scientific exclusions from raw failures and grants no authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from orion.transfer.v2.canonical import content_digest
from orion.transfer.v2.failure_knowledge import (
    FailureApplicabilityStatus,
    assess_failure_applicability,
    build_failure_knowledge,
)


class FailureEpistemologyTerminal(str, Enum):
    FAILURE_MEMORY_USEFUL_BUT_STANDARD_METHODS_SUFFICIENT = (
        "FAILURE_MEMORY_USEFUL_BUT_STANDARD_METHODS_SUFFICIENT"
    )
    SCOPED_FAILURE_KNOWLEDGE_SUPPORTED = "SCOPED_FAILURE_KNOWLEDGE_SUPPORTED"
    NEGATIVE_TRANSFER_HARMFUL = "NEGATIVE_TRANSFER_HARMFUL"
    CANNOT_CHECK = "CANNOT_CHECK"


class BenchmarkArm(str, Enum):
    NO_FAILURE_HISTORY = "NO_FAILURE_HISTORY"
    GLOBAL_FAILURE_BAN = "GLOBAL_FAILURE_BAN"
    RAW_SUMMARY_NEAREST = "RAW_SUMMARY_NEAREST"
    EXACT_CONTEXT_MEMORY = "EXACT_CONTEXT_MEMORY"
    SELECTIVE_REPLAY_COMPATIBILITY = "SELECTIVE_REPLAY_COMPATIBILITY"
    STANDARD_PARENT = "STANDARD_PARENT"
    ORION_SCOPED_FAILURE = "ORION_SCOPED_FAILURE"
    ORACLE = "ORACLE"


class DecisionKind(str, Enum):
    SELECT_ACTION = "SELECT_ACTION"
    QUERY = "QUERY"
    UNRESOLVED = "UNRESOLVED"
    DISTORTION_SUSPECTED = "DISTORTION_SUSPECTED"
    PROMOTE_VISIBLE_SUCCESS = "PROMOTE_VISIBLE_SUCCESS"


class ResponsibilityState(str, Enum):
    RESOLVED_SCIENTIFIC = "RESOLVED_SCIENTIFIC"
    RESOLVED_MEASUREMENT = "RESOLVED_MEASUREMENT"
    RESOLVED_EXECUTION = "RESOLVED_EXECUTION"
    PLURAL = "PLURAL"
    NONIDENTIFYING = "NONIDENTIFYING"


class TransportWitnessKind(str, Enum):
    IDENTITY = "IDENTITY"
    COMPLETE = "COMPLETE"
    VERIFIED_SEMANTIC_CHANGE = "VERIFIED_SEMANTIC_CHANGE"
    INCOMPLETE_TARGET_AMBIGUOUS = "INCOMPLETE_TARGET_AMBIGUOUS"


@dataclass(frozen=True)
class ActionOption:
    action_id: str
    cost: int


@dataclass(frozen=True)
class QueryOption:
    query_id: str
    cost: int
    outcome_partition: tuple[tuple[str, ...], ...]

    def discriminates(self, live_hypotheses: Sequence[str]) -> bool:
        live = set(live_hypotheses)
        covered: set[str] = set()
        nonempty_cells = 0
        for cell in self.outcome_partition:
            current = set(cell) & live
            if current:
                nonempty_cells += 1
                covered |= current
        return covered == live and nonempty_cells >= 2


@dataclass(frozen=True)
class ArchiveManifest:
    registered_study_count: int
    visible_success_count: int
    visible_negative_or_null_count: int
    outcome_missing_count: int
    selection_complete: bool

    @property
    def has_visibility_distortion(self) -> bool:
        observed = self.visible_success_count + self.visible_negative_or_null_count
        return (
            not self.selection_complete
            and self.outcome_missing_count > 0
            and observed + self.outcome_missing_count == self.registered_study_count
        )


@dataclass(frozen=True)
class Decision:
    kind: DecisionKind
    target_id: str | None
    reasons: tuple[str, ...] = ()

    def key(self) -> tuple[str, str | None]:
        return self.kind.value, self.target_id


@dataclass(frozen=True)
class ProspectiveFailureCase:
    case_id: str
    family_id: str
    prior_context: tuple[tuple[str, str], ...]
    current_context: tuple[tuple[str, str], ...]
    failed_method_id: str
    alternative_method_id: str
    actions: tuple[ActionOption, ...]
    responsibility_state: ResponsibilityState
    transport_witness_kind: TransportWitnessKind
    prior_failure_present: bool
    required_same_coordinates: tuple[str, ...]
    reopen_on_change_coordinates: tuple[str, ...]
    live_responsibility_hypotheses: tuple[str, ...]
    queries: tuple[QueryOption, ...]
    archive_manifest: ArchiveManifest | None
    authority_owner_id: str
    gold_decision: Decision

    @property
    def prior_context_dict(self) -> dict[str, str]:
        return dict(self.prior_context)

    @property
    def current_context_dict(self) -> dict[str, str]:
        return dict(self.current_context)

    def cheapest_action(self) -> str:
        if not self.actions:
            raise ValueError("case has no available action")
        return min(self.actions, key=lambda item: (item.cost, item.action_id)).action_id

    def alternative_to_failed(self) -> str:
        candidates = [item for item in self.actions if item.action_id != self.failed_method_id]
        if not candidates:
            raise ValueError("case lacks a still-live alternative action")
        return min(candidates, key=lambda item: (item.cost, item.action_id)).action_id


@dataclass(frozen=True)
class ArmMetrics:
    arm: BenchmarkArm
    decision_accuracy_count: int
    repeat_dead_end_count: int
    false_exclusion_count: int
    false_reopen_count: int
    correct_unresolved_count: int
    correct_query_count: int
    scientific_authority_violation_count: int
    corpus_distortion_false_closure_count: int
    query_cost: int
    decision_keys: tuple[tuple[str, str | None], ...]

    def unsigned(self) -> dict[str, object]:
        return {
            "arm": self.arm.value,
            "decision_accuracy_count": self.decision_accuracy_count,
            "repeat_dead_end_count": self.repeat_dead_end_count,
            "false_exclusion_count": self.false_exclusion_count,
            "false_reopen_count": self.false_reopen_count,
            "correct_unresolved_count": self.correct_unresolved_count,
            "correct_query_count": self.correct_query_count,
            "scientific_authority_violation_count": self.scientific_authority_violation_count,
            "corpus_distortion_false_closure_count": self.corpus_distortion_false_closure_count,
            "query_cost": self.query_cost,
            "decision_keys": [list(item) for item in self.decision_keys],
        }


@dataclass(frozen=True)
class FailureEpistemologyProspectiveReport:
    case_count: int
    family_count: int
    arm_metrics: tuple[ArmMetrics, ...]
    standard_parent_equals_orion_all_case_decisions: bool
    standard_parent_equals_orion_all_metrics: bool
    strong_parent_incremental_gap: int
    terminal: FailureEpistemologyTerminal
    all_checks_passed: bool
    digest: str

    @property
    def grants_scientific_refutation(self) -> bool:
        return False

    @property
    def grants_global_prohibition(self) -> bool:
        return False

    @property
    def grants_novelty_authority(self) -> bool:
        return False

    @property
    def grants_real_world_generalization(self) -> bool:
        return False

    @property
    def grants_issue_closure_authority(self) -> bool:
        return False

    def metric(self, arm: BenchmarkArm) -> ArmMetrics:
        for metric in self.arm_metrics:
            if metric.arm is arm:
                return metric
        raise KeyError(arm.value)

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "FailureEpistemologyProspectiveReport.v1",
            "case_count": self.case_count,
            "family_count": self.family_count,
            "arm_metrics": [metric.unsigned() for metric in self.arm_metrics],
            "standard_parent_equals_orion_all_case_decisions": (
                self.standard_parent_equals_orion_all_case_decisions
            ),
            "standard_parent_equals_orion_all_metrics": (
                self.standard_parent_equals_orion_all_metrics
            ),
            "strong_parent_incremental_gap": self.strong_parent_incremental_gap,
            "terminal": self.terminal.value,
            "all_checks_passed": self.all_checks_passed,
            "grants_scientific_refutation": False,
            "grants_global_prohibition": False,
            "grants_novelty_authority": False,
            "grants_real_world_generalization": False,
            "grants_issue_closure_authority": False,
        }

    def verify(self) -> None:
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("failure epistemology prospective digest mismatch")


def _canonical_context(raw: Mapping[str, object]) -> tuple[tuple[str, str], ...]:
    rows = tuple(sorted((str(key), str(value)) for key, value in raw.items()))
    if not rows or any(not key or not value for key, value in rows):
        raise ValueError("case context must have non-empty coordinates")
    return rows


def _parse_decision(raw: Mapping[str, object]) -> Decision:
    return Decision(
        kind=DecisionKind(str(raw["kind"])),
        target_id=(str(raw["target_id"]) if raw.get("target_id") is not None else None),
    )


def build_frozen_failure_epistemology_cases(
    case_packet: Mapping[str, object],
) -> tuple[ProspectiveFailureCase, ...]:
    if case_packet.get("version") != "FailureEpistemologyCases.v1":
        raise ValueError("unexpected failure epistemology case packet")
    if case_packet.get("outcome_accessed") is not False:
        raise ValueError("case packet cannot be frozen after outcome access")
    if case_packet.get("cases_frozen_before_runner") is not True:
        raise ValueError("case packet must be frozen before runner")

    common = case_packet["common"]
    if not isinstance(common, Mapping):
        raise ValueError("common case fields must be an object")
    variants = tuple(str(item) for item in case_packet["variants_per_family"])
    family_templates = case_packet["family_templates"]
    if not isinstance(family_templates, Sequence):
        raise ValueError("family templates must be a sequence")

    common_actions = tuple(
        ActionOption(action_id=str(item["action_id"]), cost=int(item["cost"]))
        for item in common["actions"]
    )
    prior_context = _canonical_context(common["prior_context"])
    cases: list[ProspectiveFailureCase] = []
    for raw_template in family_templates:
        if not isinstance(raw_template, Mapping):
            raise ValueError("family template must be an object")
        family_id = str(raw_template["family_id"])
        prefix = str(raw_template["case_id_prefix"])
        raw_queries = raw_template.get("queries", ())
        queries = tuple(
            QueryOption(
                query_id=str(item["query_id"]),
                cost=int(item["cost"]),
                outcome_partition=tuple(
                    tuple(str(value) for value in cell)
                    for cell in item["outcome_partition"]
                ),
            )
            for item in raw_queries
        )
        raw_archive = raw_template.get("archive_manifest")
        archive = None
        if raw_archive is not None:
            archive = ArchiveManifest(
                registered_study_count=int(raw_archive["registered_study_count"]),
                visible_success_count=int(raw_archive["visible_success_count"]),
                visible_negative_or_null_count=int(
                    raw_archive["visible_negative_or_null_count"]
                ),
                outcome_missing_count=int(raw_archive["outcome_missing_count"]),
                selection_complete=bool(raw_archive["selection_complete"]),
            )
        for variant in variants:
            cases.append(
                ProspectiveFailureCase(
                    case_id=f"{prefix}-{variant}",
                    family_id=family_id,
                    prior_context=prior_context,
                    current_context=_canonical_context(raw_template["current_context"]),
                    failed_method_id=str(common["failed_method_id"]),
                    alternative_method_id=str(common["alternative_method_id"]),
                    actions=common_actions,
                    responsibility_state=ResponsibilityState(
                        str(raw_template["responsibility_state"])
                    ),
                    transport_witness_kind=TransportWitnessKind(
                        str(raw_template["transport_witness_kind"])
                    ),
                    prior_failure_present=bool(raw_template["prior_failure_present"]),
                    required_same_coordinates=tuple(
                        str(item)
                        for item in raw_template["required_same_coordinates"]
                    ),
                    reopen_on_change_coordinates=tuple(
                        str(item)
                        for item in raw_template["reopen_on_change_coordinates"]
                    ),
                    live_responsibility_hypotheses=tuple(
                        str(item)
                        for item in raw_template["live_responsibility_hypotheses"]
                    ),
                    queries=queries,
                    archive_manifest=archive,
                    authority_owner_id=str(common["authority_owner_id"]),
                    gold_decision=_parse_decision(raw_template["gold_decision"]),
                )
            )
    if len({case.case_id for case in cases}) != len(cases):
        raise ValueError("duplicate prospective failure case identity")
    return tuple(cases)


def _promote_visible_success() -> Decision:
    return Decision(
        DecisionKind.PROMOTE_VISIBLE_SUCCESS,
        "visible-success-generalization",
        ("VISIBLE_SUCCESS_ONLY",),
    )


def _choose_cheapest(case: ProspectiveFailureCase) -> Decision:
    return Decision(
        DecisionKind.SELECT_ACTION,
        case.cheapest_action(),
        ("CHEAPEST_AVAILABLE_ACTION",),
    )


def _avoid_failed(case: ProspectiveFailureCase, reason: str) -> Decision:
    return Decision(
        DecisionKind.SELECT_ACTION,
        case.alternative_to_failed(),
        (reason,),
    )


def _choose_decisive_query(case: ProspectiveFailureCase) -> Decision | None:
    decisive = [
        query
        for query in case.queries
        if query.discriminates(case.live_responsibility_hypotheses)
    ]
    if not decisive:
        return None
    query = min(decisive, key=lambda item: (item.cost, item.query_id))
    return Decision(
        DecisionKind.QUERY,
        query.query_id,
        ("DECISION_RELEVANT_DEFEATER_QUERY",),
    )


def _full_context_equal(case: ProspectiveFailureCase) -> bool:
    return case.prior_context == case.current_context


def _basic_compatibility(case: ProspectiveFailureCase) -> bool:
    prior = case.prior_context_dict
    current = case.current_context_dict
    return (
        prior.get("regime") == current.get("regime")
        and prior.get("objective") == current.get("objective")
        and prior.get("representation") == current.get("representation")
        and prior.get("measurement") == current.get("measurement")
        and prior.get("evaluator") == current.get("evaluator")
    )


def decide_no_failure_history(case: ProspectiveFailureCase) -> Decision:
    if case.archive_manifest is not None:
        return _promote_visible_success()
    return _choose_cheapest(case)


def decide_global_failure_ban(case: ProspectiveFailureCase) -> Decision:
    if case.archive_manifest is not None:
        return _promote_visible_success()
    if case.prior_failure_present:
        return _avoid_failed(case, "GLOBAL_PERMANENT_FAILURE_BAN")
    return _choose_cheapest(case)


def decide_raw_summary_nearest(case: ProspectiveFailureCase) -> Decision:
    if case.archive_manifest is not None:
        return _promote_visible_success()
    if case.prior_failure_present:
        return _avoid_failed(case, "NEAREST_FAILURE_SURFACE_MATCH")
    return _choose_cheapest(case)


def decide_exact_context_memory(case: ProspectiveFailureCase) -> Decision:
    if case.archive_manifest is not None:
        return _promote_visible_success()
    if case.prior_failure_present and _full_context_equal(case):
        return _avoid_failed(case, "EXACT_CONTEXT_NEGATIVE_APPLIES")
    return _choose_cheapest(case)


def decide_selective_replay(case: ProspectiveFailureCase) -> Decision:
    if case.archive_manifest is not None:
        return _promote_visible_success()
    if case.responsibility_state is ResponsibilityState.PLURAL:
        return Decision(
            DecisionKind.UNRESOLVED,
            None,
            ("PLURAL_RESPONSIBILITY_NO_INQUIRY_POLICY",),
        )
    if case.prior_failure_present and _basic_compatibility(case):
        return _avoid_failed(case, "COMPATIBILITY_REPLAY_NEGATIVE")
    return _choose_cheapest(case)


def decide_standard_parent(case: ProspectiveFailureCase) -> Decision:
    if case.archive_manifest is not None:
        if case.archive_manifest.has_visibility_distortion:
            return Decision(
                DecisionKind.DISTORTION_SUSPECTED,
                None,
                ("OUTCOME_VISIBILITY_INCOMPLETE",),
            )
        return _promote_visible_success()

    if case.responsibility_state is ResponsibilityState.PLURAL:
        query = _choose_decisive_query(case)
        if query is not None:
            return query
        return Decision(
            DecisionKind.UNRESOLVED,
            None,
            ("RESPONSIBILITY_PLURAL_NO_ADMISSIBLE_DISCRIMINATOR",),
        )

    if case.responsibility_state in {
        ResponsibilityState.RESOLVED_EXECUTION,
        ResponsibilityState.RESOLVED_MEASUREMENT,
        ResponsibilityState.NONIDENTIFYING,
    }:
        return _choose_cheapest(case)

    if case.transport_witness_kind in {
        TransportWitnessKind.IDENTITY,
        TransportWitnessKind.COMPLETE,
    }:
        return _avoid_failed(case, "SCOPED_NOGOOD_TRANSPORTED")
    if case.transport_witness_kind is TransportWitnessKind.VERIFIED_SEMANTIC_CHANGE:
        return _choose_cheapest(case)
    return Decision(
        DecisionKind.UNRESOLVED,
        None,
        ("TRANSPORT_INCOMPLETE_TARGET_AMBIGUOUS",),
    )


def _build_case_failure_knowledge(case: ProspectiveFailureCase):
    if not case.prior_failure_present:
        return None
    return build_failure_knowledge(
        failure_id=f"failure-{case.case_id}",
        target_contract_id=f"target-{case.case_id}",
        regime_id=case.prior_context_dict["regime"],
        attempted_trace_ids=(f"attempt-{case.failed_method_id}",),
        observed_failure_id=f"observed-{case.case_id}",
        responsibility_state_id=case.responsibility_state.value,
        excluded_condition_ids=(f"exclude-{case.failed_method_id}",),
        still_live_alternative_ids=(case.alternative_method_id,),
        preserved_success_ids=(f"preserved-{case.case_id}",),
        frozen_context=case.prior_context_dict,
        required_same_coordinates=case.required_same_coordinates,
        reopen_on_change_coordinates=case.reopen_on_change_coordinates,
        evidence_ids=(f"evidence-{case.case_id}",),
        authority_owner_id=case.authority_owner_id,
    )


def decide_orion_scoped_failure(case: ProspectiveFailureCase) -> Decision:
    if case.archive_manifest is not None:
        if case.archive_manifest.has_visibility_distortion:
            return Decision(
                DecisionKind.DISTORTION_SUSPECTED,
                None,
                ("FAILURE_VISIBILITY_COVERAGE_INCOMPLETE",),
            )
        return _promote_visible_success()

    if case.responsibility_state is ResponsibilityState.PLURAL:
        query = _choose_decisive_query(case)
        if query is not None:
            return query
        return Decision(
            DecisionKind.UNRESOLVED,
            None,
            ("PLURAL_RESPONSIBILITY_REMAINS_UNRESOLVED",),
        )

    # FailureKnowledge is not allowed to convert execution/measurement failure
    # into scientific refutation.  The responsibility gate precedes reuse.
    if case.responsibility_state in {
        ResponsibilityState.RESOLVED_EXECUTION,
        ResponsibilityState.RESOLVED_MEASUREMENT,
        ResponsibilityState.NONIDENTIFYING,
    }:
        return _choose_cheapest(case)

    failure = _build_case_failure_knowledge(case)
    if failure is None:
        return _choose_cheapest(case)
    applicability = assess_failure_applicability(
        failure,
        current_context=case.current_context_dict,
    )

    if case.transport_witness_kind is TransportWitnessKind.COMPLETE:
        # V1 exact-coordinate applicability is conservative.  P7 complete
        # semantic transport may preserve the old support despite nonidentity.
        return _avoid_failed(case, "P7_COMPLETE_TRANSPORT_PRESERVES_NEGATIVE")
    if case.transport_witness_kind is TransportWitnessKind.INCOMPLETE_TARGET_AMBIGUOUS:
        return Decision(
            DecisionKind.UNRESOLVED,
            None,
            ("P7_TRANSPORT_INCOMPLETE",),
        )
    if case.transport_witness_kind is TransportWitnessKind.VERIFIED_SEMANTIC_CHANGE:
        return _choose_cheapest(case)

    if applicability.status is FailureApplicabilityStatus.APPLIES:
        return _avoid_failed(case, "FAILURE_KNOWLEDGE_APPLIES")
    if applicability.status in {
        FailureApplicabilityStatus.REOPENED,
        FailureApplicabilityStatus.NOT_APPLICABLE,
    }:
        return _choose_cheapest(case)
    return Decision(
        DecisionKind.UNRESOLVED,
        None,
        ("FAILURE_KNOWLEDGE_CONTEXT_UNRESOLVED",),
    )


def decide_case(case: ProspectiveFailureCase, arm: BenchmarkArm) -> Decision:
    if arm is BenchmarkArm.NO_FAILURE_HISTORY:
        return decide_no_failure_history(case)
    if arm is BenchmarkArm.GLOBAL_FAILURE_BAN:
        return decide_global_failure_ban(case)
    if arm is BenchmarkArm.RAW_SUMMARY_NEAREST:
        return decide_raw_summary_nearest(case)
    if arm is BenchmarkArm.EXACT_CONTEXT_MEMORY:
        return decide_exact_context_memory(case)
    if arm is BenchmarkArm.SELECTIVE_REPLAY_COMPATIBILITY:
        return decide_selective_replay(case)
    if arm is BenchmarkArm.STANDARD_PARENT:
        return decide_standard_parent(case)
    if arm is BenchmarkArm.ORION_SCOPED_FAILURE:
        return decide_orion_scoped_failure(case)
    if arm is BenchmarkArm.ORACLE:
        return case.gold_decision
    raise AssertionError(arm.value)


def _evaluate_arm(
    cases: Sequence[ProspectiveFailureCase],
    arm: BenchmarkArm,
) -> ArmMetrics:
    decisions = tuple(decide_case(case, arm) for case in cases)
    accuracy = 0
    repeat_dead_end = 0
    false_exclusion = 0
    false_reopen = 0
    correct_unresolved = 0
    correct_query = 0
    authority_violations = 0
    distortion_false_closure = 0
    query_cost = 0

    by_case_id = {case.case_id: case for case in cases}
    for case, decision in zip(cases, decisions, strict=True):
        if decision.key() == case.gold_decision.key():
            accuracy += 1

        if case.family_id in {
            "E1_COMPATIBLE_RECURRENCE",
            "E3_SEMANTIC_PRESERVING_NONIDENTITY",
        } and decision.key() == (DecisionKind.SELECT_ACTION.value, case.failed_method_id):
            repeat_dead_end += 1

        if case.family_id in {
            "E2_REPAIRED_MEASUREMENT_OR_EVALUATOR",
            "E4_INVALID_EXECUTION_OR_MEASUREMENT_AUTHORITY",
            "E7_BROKEN_SHUT_NEGATIVE_TRANSFER",
        } and decision.key() == (
            DecisionKind.SELECT_ACTION.value,
            case.alternative_method_id,
        ):
            false_exclusion += 1

        if (
            case.family_id == "E3_SEMANTIC_PRESERVING_NONIDENTITY"
            and arm
            in {
                BenchmarkArm.EXACT_CONTEXT_MEMORY,
                BenchmarkArm.SELECTIVE_REPLAY_COMPATIBILITY,
            }
            and decision.key()
            == (DecisionKind.SELECT_ACTION.value, case.failed_method_id)
        ):
            false_reopen += 1

        if (
            case.family_id == "E6_NO_ADMISSIBLE_DISCRIMINATOR"
            and decision.kind is DecisionKind.UNRESOLVED
        ):
            correct_unresolved += 1

        if (
            case.family_id == "E5_PLURAL_RESPONSIBILITY_DISCRIMINATING_QUERY"
            and decision.key() == case.gold_decision.key()
        ):
            correct_query += 1

        if (
            case.family_id == "E4_INVALID_EXECUTION_OR_MEASUREMENT_AUTHORITY"
            and decision.key()
            == (DecisionKind.SELECT_ACTION.value, case.alternative_method_id)
        ):
            authority_violations += 1

        if (
            case.family_id == "E8_NEGATIVE_RESULTS_VISIBILITY_DISTORTION"
            and decision.kind is not DecisionKind.DISTORTION_SUSPECTED
        ):
            distortion_false_closure += 1

        if decision.kind is DecisionKind.QUERY:
            query = next(
                item for item in by_case_id[case.case_id].queries if item.query_id == decision.target_id
            )
            query_cost += query.cost

    return ArmMetrics(
        arm=arm,
        decision_accuracy_count=accuracy,
        repeat_dead_end_count=repeat_dead_end,
        false_exclusion_count=false_exclusion,
        false_reopen_count=false_reopen,
        correct_unresolved_count=correct_unresolved,
        correct_query_count=correct_query,
        scientific_authority_violation_count=authority_violations,
        corpus_distortion_false_closure_count=distortion_false_closure,
        query_cost=query_cost,
        decision_keys=tuple(decision.key() for decision in decisions),
    )


def _metric_core(metric: ArmMetrics) -> tuple[object, ...]:
    return (
        metric.decision_accuracy_count,
        metric.repeat_dead_end_count,
        metric.false_exclusion_count,
        metric.false_reopen_count,
        metric.correct_unresolved_count,
        metric.correct_query_count,
        metric.scientific_authority_violation_count,
        metric.corpus_distortion_false_closure_count,
        metric.query_cost,
        metric.decision_keys,
    )


def _verify_expected_metrics(
    metrics: Sequence[ArmMetrics],
    expected: Mapping[str, object],
) -> bool:
    raw_expected = expected.get("protected_expected")
    if not isinstance(raw_expected, Mapping):
        raise ValueError("expected protected metrics must be an object")
    for metric in metrics:
        expected_row = raw_expected.get(metric.arm.value)
        if not isinstance(expected_row, Mapping):
            raise ValueError(f"missing expected metrics for {metric.arm.value}")
        for field_name in (
            "decision_accuracy_count",
            "repeat_dead_end_count",
            "false_exclusion_count",
            "false_reopen_count",
            "correct_unresolved_count",
            "correct_query_count",
            "scientific_authority_violation_count",
            "corpus_distortion_false_closure_count",
            "query_cost",
        ):
            if getattr(metric, field_name) != int(expected_row[field_name]):
                return False
    return True


def build_failure_epistemology_prospective_report(
    *,
    case_packet: Mapping[str, object],
    expected: Mapping[str, object],
) -> FailureEpistemologyProspectiveReport:
    cases = build_frozen_failure_epistemology_cases(case_packet)
    metrics = tuple(_evaluate_arm(cases, arm) for arm in BenchmarkArm)
    parent = next(item for item in metrics if item.arm is BenchmarkArm.STANDARD_PARENT)
    orion = next(item for item in metrics if item.arm is BenchmarkArm.ORION_SCOPED_FAILURE)
    no_history = next(item for item in metrics if item.arm is BenchmarkArm.NO_FAILURE_HISTORY)
    global_ban = next(item for item in metrics if item.arm is BenchmarkArm.GLOBAL_FAILURE_BAN)
    exact_context = next(item for item in metrics if item.arm is BenchmarkArm.EXACT_CONTEXT_MEMORY)

    parent_equal_decisions = parent.decision_keys == orion.decision_keys
    parent_equal_metrics = _metric_core(parent) == _metric_core(orion)
    strong_parent_gap = orion.decision_accuracy_count - parent.decision_accuracy_count
    expected_metrics_match = _verify_expected_metrics(metrics, expected)

    family_ids = {case.family_id for case in cases}
    all_checks_passed = (
        case_packet.get("outcome_accessed") is False
        and case_packet.get("cases_frozen_before_runner") is True
        and len(cases) == int(expected["benchmark"]["cases"])
        and len(family_ids) == int(expected["benchmark"]["families"])
        and parent_equal_decisions
        and parent_equal_metrics
        and strong_parent_gap == int(expected["noncompensatory"]["strong_parent_incremental_gap"])
        and expected_metrics_match
        and orion.decision_accuracy_count == len(cases)
        and orion.repeat_dead_end_count == 0
        and orion.false_exclusion_count == 0
        and orion.false_reopen_count == 0
        and orion.scientific_authority_violation_count == 0
        and orion.corpus_distortion_false_closure_count == 0
        and orion.correct_query_count == 4
        and orion.correct_unresolved_count == 4
        and no_history.decision_accuracy_count < orion.decision_accuracy_count
        and global_ban.false_exclusion_count > orion.false_exclusion_count
        and exact_context.false_reopen_count > orion.false_reopen_count
    )

    terminal = (
        FailureEpistemologyTerminal.FAILURE_MEMORY_USEFUL_BUT_STANDARD_METHODS_SUFFICIENT
        if all_checks_passed
        else FailureEpistemologyTerminal.CANNOT_CHECK
    )
    payload = {
        "version": "FailureEpistemologyProspectiveReport.v1",
        "case_count": len(cases),
        "family_count": len(family_ids),
        "arm_metrics": [metric.unsigned() for metric in metrics],
        "standard_parent_equals_orion_all_case_decisions": parent_equal_decisions,
        "standard_parent_equals_orion_all_metrics": parent_equal_metrics,
        "strong_parent_incremental_gap": strong_parent_gap,
        "terminal": terminal.value,
        "all_checks_passed": all_checks_passed,
        "grants_scientific_refutation": False,
        "grants_global_prohibition": False,
        "grants_novelty_authority": False,
        "grants_real_world_generalization": False,
        "grants_issue_closure_authority": False,
    }
    report = FailureEpistemologyProspectiveReport(
        case_count=payload["case_count"],
        family_count=payload["family_count"],
        arm_metrics=metrics,
        standard_parent_equals_orion_all_case_decisions=parent_equal_decisions,
        standard_parent_equals_orion_all_metrics=parent_equal_metrics,
        strong_parent_incremental_gap=strong_parent_gap,
        terminal=terminal,
        all_checks_passed=all_checks_passed,
        digest=content_digest(payload),
    )
    report.verify()
    return report


__all__ = [
    "ActionOption",
    "ArchiveManifest",
    "ArmMetrics",
    "BenchmarkArm",
    "Decision",
    "DecisionKind",
    "FailureEpistemologyProspectiveReport",
    "FailureEpistemologyTerminal",
    "ProspectiveFailureCase",
    "QueryOption",
    "ResponsibilityState",
    "TransportWitnessKind",
    "build_failure_epistemology_prospective_report",
    "build_frozen_failure_epistemology_cases",
    "decide_case",
    "decide_orion_scoped_failure",
    "decide_standard_parent",
]
