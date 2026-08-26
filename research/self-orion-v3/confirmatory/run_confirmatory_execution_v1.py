"""Confirmatory execution runner for Self-ORION V3 (frozen protocol, frozen rules).

Runs only if the committed preflight authorizes execution and every frozen
binding digest verifies against the committed files.  Produces
CONFIRMATORY_EXECUTION_RECEIPT_2026-08-24.json with exactly one terminal from
the protocol's possible terminals, selected by the frozen first-match rules in
CONFIRMATORY_DECISION_RULES_V1.json.

Interpretations fixed at runner-freeze time, BEFORE any outcome was accessed:

1. The single declared margin (0.02) applies uniformly to all four primary
   endpoints wherever a margin is referenced (NO_INCREMENTAL_VALUE match test,
   R3/OVERCONSERVATIVE fresh-transfer noninferiority, split-half R5).
2. ``FULL_T7 satisfies R1-R3`` inside NO_INCREMENTAL_VALUE (and the shared
   precondition of REVISION_LEVEL_DISCRIMINATION_SUPPORTED) is read as the
   performance CONTENT of R1-R3: accuracy >= 0.75; false-broad and harm each
   no worse than every non-floor policy (ties allowed); fresh transfer within
   0.02 of the best strong comparator.  The strict-superiority clauses of R1(b)
   and R2 are discriminators that can only hold without a tie; under an exact
   tie the margin-based match test of NO_INCREMENTAL_VALUE is the route the
   frozen ordering provides, and REVISION_LEVEL_DISCRIMINATION_SUPPORTED
   additionally requires R4-R6.  This is the only reading under which the rule
   set maps every measurable outcome to exactly one terminal, as the frozen
   rules file states it must.
3. M_OPEN_SUFFICIENT evaluates M_OPEN_ONLY in the subject role against the
   same performance content, including the accuracy bar.
4. Split-half direction agreement (the CANNOT_CHECK clause) means: for every
   strong comparator c, sign(accuracy[FULL_T7] - accuracy[c]) is the same
   strict/non-strict relationship in PRIMARY_A and REPLICATION_B.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any, Mapping

from orion.study.p5.freeze import sha256_json
from orion.study.p5.revision_level_v3_freeze import (
    derive_candidate_packet,
    derive_protected_commitment,
    validate_protected_suite,
)
from orion.study.p5.revision_level_v3_policies import (
    FeedbackMode,
    PolicyKind,
    ProtectedFeedbackOracle,
    run_revision_policy,
)
from orion.study.p5.revision_level_v3_score import score_revision_decisions

ROOT = Path(__file__).resolve().parents[3]
CONFIRMATORY = ROOT / "research" / "self-orion-v3" / "confirmatory"
PROTOCOL_PATH = ROOT / "papers" / "orion-15-self-orion" / "protocol" / "SELF_ORION_V3_REVISION_LEVEL_PROTOCOL_V1.json"
PREFLIGHT_SCRIPT = ROOT / "research" / "self-orion-v3" / "run_confirmatory_preflight_v1.py"
SUITE_PATH = CONFIRMATORY / "PROTECTED_CONFIRMATORY_SUITE_V1.json"
PACKET_PATH = CONFIRMATORY / "CANDIDATE_PACKET_V1.json"
SPLIT_PATH = CONFIRMATORY / "CONFIRMATORY_FINAL_SPLIT_V1.json"
RULES_PATH = CONFIRMATORY / "CONFIRMATORY_DECISION_RULES_V1.json"
BASELINE_CONFIG_PATH = CONFIRMATORY / "BASELINE_CONFIG_V1.json"
EVALUATOR_PATH = CONFIRMATORY / "protected_evaluator_v1.py"
FRESH_EVALUATOR_PATH = CONFIRMATORY / "fresh_transfer_evaluator_v1.py"
RECEIPT_PATH = CONFIRMATORY / "CONFIRMATORY_EXECUTION_RECEIPT_2026-08-24.json"

STRONG = (
    "DIRECT_SELF_EDIT",
    "M_OPEN_ONLY",
    "WORLD_MODEL_REVISION",
    "REPRESENTATION_REGIME_ONLY",
    "GENERIC_CAUSAL_DIAGNOSIS",
    "RANDOM_DIAGNOSTIC",
)
NON_FLOOR = STRONG + ("FULL_T7",)
FLOORS = ("NO_REVISION", "ALWAYS_UNRESOLVED")
POLICY_ORDER = FLOORS[:1] + STRONG[:1] + STRONG[1:5] + ("FULL_T7", STRONG[5], FLOORS[1], "ORACLE_CEILING")
ALL_POLICIES = (
    PolicyKind.NO_REVISION,
    PolicyKind.DIRECT_SELF_EDIT,
    PolicyKind.M_OPEN_ONLY,
    PolicyKind.WORLD_MODEL_REVISION,
    PolicyKind.REPRESENTATION_REGIME_ONLY,
    PolicyKind.GENERIC_CAUSAL_DIAGNOSIS,
    PolicyKind.FULL_T7,
    PolicyKind.RANDOM_DIAGNOSTIC,
    PolicyKind.ALWAYS_UNRESOLVED,
    PolicyKind.ORACLE_CEILING,
)
ADAPTIVITY_MODES = (
    FeedbackMode.NORMAL,
    FeedbackMode.PERMUTED,
    FeedbackMode.NONE,
    FeedbackMode.CONTRADICTORY,
    FeedbackMode.RANDOM,
)
REPAIR_CLASSES = (
    "EVIDENCE_REPAIR",
    "EXECUTION_REPAIR",
    "EVALUATOR_REPAIR",
    "MEASUREMENT_REPAIR",
    "WITHIN_CLASS_MODEL_REPAIR",
    "MODEL_CLASS_EXPANSION",
    "REPRESENTATION_REGIME_REPAIR",
)
MARGIN = 0.02


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _module_from_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _case_index(suite: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {str(case["case_id"]): case for case in suite["cases"]}


def _alternate_outcomes(case: Mapping[str, Any]) -> dict[str, str]:
    gold = str(case["protected_gold_revision_class"])
    actual = {str(key): str(value) for key, value in case["protected_diagnostic_outcomes"].items()}
    hypotheses = case["hypotheses"]
    result: dict[str, str] = {}
    for action_id, actual_outcome in actual.items():
        candidates: list[str] = []
        for label, prediction in hypotheses.items():
            if str(label) == gold:
                continue
            for outcome in prediction.get(action_id, []):
                value = str(outcome)
                if value != actual_outcome:
                    candidates.append(value)
        result[action_id] = sorted(set(candidates))[0] if candidates else "CONTRADICTORY_FEEDBACK"
    return result


def _oracle(case: Mapping[str, Any], mode: FeedbackMode) -> ProtectedFeedbackOracle:
    return ProtectedFeedbackOracle(
        case_id=str(case["case_id"]),
        outcome_by_action={str(k): str(v) for k, v in case["protected_diagnostic_outcomes"].items()},
        mode=mode,
        alternate_outcomes=_alternate_outcomes(case),
    )


def _run_policy_decisions(
    suite: Mapping[str, Any],
    packet_cases: list[Mapping[str, Any]],
    policy: PolicyKind,
    mode: FeedbackMode = FeedbackMode.NORMAL,
) -> list[Any]:
    protected = _case_index(suite)
    decisions = []
    for candidate in packet_cases:
        case_id = str(candidate["case_id"])
        protected_case = protected[case_id]
        kwargs = {}
        if policy is PolicyKind.ORACLE_CEILING:
            kwargs["protected_gold_revision_class"] = str(protected_case["protected_gold_revision_class"])
        decisions.append(run_revision_policy(policy, candidate, _oracle(protected_case, mode), **kwargs))
    return decisions


def _decision_map(decisions) -> dict[str, dict[str, str]]:
    return {
        str(d.case_id): {
            "policy_id": str(d.policy_id),
            "selected_revision_class": str(d.selected_revision_class),
        }
        for d in decisions
    }


def _decision_layer_row(report) -> dict[str, object]:
    return {
        "revision_label_accuracy": report.revision_accuracy,
        "correct_revision_count": report.correct_revision_count,
        "false_broad_revision_count": report.false_broad_revision_count,
        "false_broad_revision_rate": report.false_broad_revision_rate,
        "correct_unresolved_rate": (
            report.correct_unresolved_count / report.correct_unresolved_denominator
            if report.correct_unresolved_denominator
            else None
        ),
        "total_diagnostic_cost": report.total_diagnostic_cost,
        "analysis_only": report.analysis_only,
    }


def _sub_suite(suite: Mapping[str, Any], case_ids: set[str]) -> dict[str, Any]:
    return {**{k: v for k, v in suite.items() if k != "cases"}, "cases": [c for c in suite["cases"] if str(c["case_id"]) in case_ids]}


def verify_frozen_bindings() -> dict[str, object]:
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    bindings = protocol["confirmatory_execution_bindings"]
    if bindings.get("outcome_accessed") is not False:
        raise RuntimeError("refusing to execute: protocol records outcome_accessed != false")

    preflight_mod = _module_from_path("p5v3_confirmatory_preflight", PREFLIGHT_SCRIPT)
    preflight = preflight_mod.derive()
    if preflight["status"] != "READY_TO_FREEZE_CONFIRMATORY" or preflight["authorizes_execution"] is not True:
        raise RuntimeError(f"preflight does not authorize execution: {json.dumps(preflight)}")

    suite = json.loads(SUITE_PATH.read_text(encoding="utf-8"))
    validate_protected_suite(suite)
    packet_file = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
    packet_derived = derive_candidate_packet(suite)
    checks = {
        "preflight_status": preflight["status"],
        "protected_suite_commitment": derive_protected_commitment(suite) == bindings["protected_suite_commitment"],
        "candidate_packet_file_sha256": _sha256_file(PACKET_PATH) == bindings["candidate_packet_sha256"],
        "candidate_packet_regenerates": packet_derived == packet_file,
        "candidate_packet_canonical_sha256": sha256_json(packet_derived),
        "final_split_sha256": _sha256_file(SPLIT_PATH) == bindings["final_split_sha256"],
        "evaluator_sha256": _sha256_file(EVALUATOR_PATH) == bindings["evaluator_sha256"],
        "fresh_transfer_evaluator_sha256": _sha256_file(FRESH_EVALUATOR_PATH) == bindings["fresh_transfer_evaluator_sha256"],
        "baseline_config_sha256": _sha256_file(BASELINE_CONFIG_PATH) == bindings["baseline_config_sha256"],
    }
    config = json.loads(BASELINE_CONFIG_PATH.read_text(encoding="utf-8"))
    bundle_files = sorted(str(f) for f in config["subject_bundle"]["files"])
    concat = b"".join(hashlib.sha256((ROOT / f).read_bytes()).digest() for f in bundle_files)
    checks["subject_revision"] = hashlib.sha1(concat).hexdigest() == bindings["subject_revision"]

    failed = [k for k, v in checks.items() if isinstance(v, bool) and not v]
    if failed or preflight["status"] != "READY_TO_FREEZE_CONFIRMATORY":
        raise RuntimeError(f"frozen binding verification failed: {failed}")
    return {
        "preflight": preflight,
        "checks": checks,
        "subject_bundle_files": bundle_files,
    }


def main() -> None:
    verification = verify_frozen_bindings()
    suite = json.loads(SUITE_PATH.read_text(encoding="utf-8"))
    packet_cases = list(json.loads(PACKET_PATH.read_text(encoding="utf-8"))["cases"])
    split = json.loads(SPLIT_PATH.read_text(encoding="utf-8"))
    assignment = split["assignment"]

    protected_eval = _module_from_path("p5v3_protected_evaluator", EVALUATOR_PATH)
    fresh_eval = _module_from_path("p5v3_fresh_evaluator", FRESH_EVALUATOR_PATH)

    decision_layer: dict[str, dict[str, object]] = {}
    execution_layer: dict[str, dict[str, object]] = {}
    cross_checks: dict[str, dict[str, object]] = {}
    repair_class_accuracy: dict[str, float] = {}
    decisions_by_policy: dict[str, dict[str, dict[str, str]]] = {}

    for policy in ALL_POLICIES:
        decisions = _run_policy_decisions(suite, packet_cases, policy)
        report = score_revision_decisions(suite, tuple(decisions))
        dmap = _decision_map(decisions)
        decisions_by_policy[str(policy.value)] = dmap
        decision_layer[str(policy.value)] = _decision_layer_row(report)
        indep = dict(protected_eval.evaluate_decisions(suite, dmap))
        execution_layer[str(policy.value)] = {
            k: v for k, v in fresh_eval.evaluate_execution(suite, dmap).items() if k != "outcomes"
        }
        cross_checks[str(policy.value)] = {
            "accuracy_agrees": indep["revision_label_accuracy"] == report.revision_accuracy,
            "false_broad_agrees": indep["false_broad_revision_count"] == report.false_broad_revision_count,
            "independent": {
                "revision_label_accuracy": indep["revision_label_accuracy"],
                "false_broad_revision_rate": indep["false_broad_revision_rate"],
                "correct_unresolved_rate": indep["correct_unresolved_rate"],
                "authority_violation_count": indep["authority_violation_count"],
                "authority_violation_rate": indep["authority_violation_rate"],
                "per_gold_class_accuracy": indep["per_gold_class_accuracy"],
            },
        }
        repair_class_accuracy[str(policy.value)] = sum(
            indep["per_gold_class_accuracy"][c] for c in REPAIR_CLASSES
        ) / len(REPAIR_CLASSES)

    cross_check_agrees = all(
        cc["accuracy_agrees"] and cc["false_broad_agrees"] for cc in cross_checks.values()
    )

    feedback_sensitivity = {}
    for mode in ADAPTIVITY_MODES:
        decisions = _run_policy_decisions(suite, packet_cases, PolicyKind.FULL_T7, mode)
        report = score_revision_decisions(suite, tuple(decisions))
        feedback_sensitivity[str(mode.value)] = _decision_layer_row(report)

    # Split halves: recompute decision-layer and execution-layer endpoints per arm.
    arms: dict[str, set[str]] = {}
    for case_id, arm in assignment.items():
        arms.setdefault(str(arm), set()).add(str(case_id))
    split_half: dict[str, dict[str, dict[str, object]]] = {}
    halftest_direction_ok = True
    for arm, case_ids in sorted(arms.items()):
        sub = _sub_suite(suite, case_ids)
        sub_packet = [c for c in packet_cases if str(c["case_id"]) in case_ids]
        arm_rows: dict[str, dict[str, object]] = {}
        for policy in ALL_POLICIES:
            decisions = _run_policy_decisions(sub, sub_packet, policy)
            report = score_revision_decisions(sub, tuple(decisions))
            dmap = _decision_map(decisions)
            execution = fresh_eval.evaluate_execution(sub, dmap)
            arm_rows[str(policy.value)] = {
                **_decision_layer_row(report),
                "protected_fresh_transfer_success_rate": execution["fresh_transfer_success_rate"],
                "harmful_regression_rate": execution["harmful_regression_rate"],
            }
        split_half[arm] = arm_rows
    for comparator in STRONG:
        a_acc = split_half["PRIMARY_A"]["FULL_T7"]["revision_label_accuracy"]
        b_acc = split_half["REPLICATION_B"]["FULL_T7"]["revision_label_accuracy"]
        a_rel = (a_acc > split_half["PRIMARY_A"][comparator]["revision_label_accuracy"]) - (
            a_acc < split_half["PRIMARY_A"][comparator]["revision_label_accuracy"]
        )
        b_rel = (b_acc > split_half["REPLICATION_B"][comparator]["revision_label_accuracy"]) - (
            b_acc < split_half["REPLICATION_B"][comparator]["revision_label_accuracy"]
        )
        if a_rel != b_rel:
            halftest_direction_ok = False

    # H4 round-2: re-admission with the round-1 outcome chain digest appended to
    # the candidate-visible context (frozen policies remain history-blind).  The
    # frozen sentence admits two readings, so BOTH are recorded, with the same
    # pre-registered expectation under each:
    #   (a) subject-shared set: cases whose FULL_T7 round-1 execution was
    #       harmful or over-broad;
    #   (b) per-policy own set: each policy's own harmful/over-broad cases.
    gold_by_case = {str(c["case_id"]): str(c["protected_gold_revision_class"]) for c in suite["cases"]}
    rank = suite["revision_invasiveness"]

    def _readmit_set(policy_id: str) -> list[Mapping[str, Any]]:
        exec_report = fresh_eval.evaluate_execution(suite, decisions_by_policy[policy_id])
        by_case = {o["case_id"]: o for o in exec_report["outcomes"]}
        selected = []
        for candidate in packet_cases:
            case_id = str(candidate["case_id"])
            sel = decisions_by_policy[policy_id][case_id]["selected_revision_class"]
            over_broad = sel not in {"UNRESOLVED", "NO_REVISION"} and rank[sel] > rank[gold_by_case[case_id]]
            if by_case[case_id]["harmful_regression"] or over_broad:
                selected.append(candidate)
        return selected

    def _round2(policy: PolicyKind, readmit_cases: list[Mapping[str, Any]]) -> dict[str, object]:
        readmit_map: dict[str, dict[str, str]] = {}
        for candidate in readmit_cases:
            case_id = str(candidate["case_id"])
            exec_report = fresh_eval.evaluate_execution(suite, decisions_by_policy[str(policy.value)])
            outcome = next(o for o in exec_report["outcomes"] if o["case_id"] == case_id)
            chain = json.dumps(
                {
                    "round1_selected": decisions_by_policy[str(policy.value)][case_id]["selected_revision_class"],
                    "round1_outcome": {k: v for k, v in outcome.items() if k != "case_id"},
                },
                sort_keys=True,
            )
            modified = {
                **candidate,
                "candidate_visible_context": {
                    **candidate["candidate_visible_context"],
                    "negative_history_head": hashlib.sha256(chain.encode("utf-8")).hexdigest(),
                },
            }
            d = _run_policy_decisions(suite, [modified], policy)[0]
            readmit_map[case_id] = {"policy_id": str(d.policy_id), "selected_revision_class": str(d.selected_revision_class)}
        if readmit_map:
            sub = _sub_suite(suite, set(readmit_map))
            execution = fresh_eval.evaluate_execution(sub, readmit_map)
            repeat_harm = execution["harmful_regression_rate"]
            re_promotion = (
                sum(1 for d in readmit_map.values() if d["selected_revision_class"] not in {"UNRESOLVED", "NO_REVISION"}) / len(readmit_map)
            )
        else:
            repeat_harm = None
            re_promotion = None
        return {
            "n_readmitted_cases": len(readmit_map),
            "re_promotion_rate": re_promotion,
            "repeated_harmful_admission_rate": repeat_harm,
        }

    subject_readmit = _readmit_set("FULL_T7")
    round2_subject_set = {
        str(policy.value): _round2(policy, subject_readmit)
        for policy in ALL_POLICIES
        if policy is not PolicyKind.ORACLE_CEILING
    }
    round2_own_set = {
        str(policy.value): _round2(policy, _readmit_set(str(policy.value)))
        for policy in ALL_POLICIES
        if policy is not PolicyKind.ORACLE_CEILING
    }

    # ---- Frozen decision rules, first-match --------------------------------
    def acc(p: str, table=None) -> float:
        return float((table or decision_layer)[p]["revision_label_accuracy"])

    def fb(p: str, table=None) -> float:
        return float((table or decision_layer)[p]["false_broad_revision_rate"])

    def harm(p: str, table=None) -> float:
        return float((table or (execution_layer[p] if table is None else table))["harmful_regression_rate"])

    def fresh(p: str, table=None) -> float:
        return float(execution_layer[p]["fresh_transfer_success_rate"])

    def perf_content_holds(subject: str) -> tuple[bool, dict[str, bool]]:
        parts = {
            "accuracy_bar": acc(subject) >= 0.75,
            "false_broad_no_worse_than_non_floor": all(fb(subject) <= fb(p) for p in NON_FLOOR),
            "harm_no_worse_than_non_floor": all(harm(subject) <= harm(p) for p in NON_FLOOR),
            "fresh_noninferior_to_strong": fresh(subject) >= max(fresh(p) for p in STRONG) - MARGIN,
        }
        return all(parts.values()), parts

    r1_strict_highest = acc("FULL_T7") > max(acc(p) for p in NON_FLOOR if p != "FULL_T7")
    r2_strict = (
        fb("FULL_T7") < min(fb(p) for p in NON_FLOOR if p != "FULL_T7")
        and harm("FULL_T7") < min(harm(p) for p in NON_FLOOR if p != "FULL_T7")
    )

    def matches_on_all_four(comparator: str) -> bool:
        return (
            acc(comparator) >= acc("FULL_T7") - MARGIN
            and fb(comparator) <= fb("FULL_T7") + MARGIN
            and harm(comparator) <= harm("FULL_T7") + MARGIN
            and fresh(comparator) >= fresh("FULL_T7") - MARGIN
        )

    matching = [c for c in STRONG if matches_on_all_four(c)]
    full_perf, full_perf_parts = perf_content_holds("FULL_T7")
    mopen_perf, mopen_parts = perf_content_holds("M_OPEN_ONLY")

    r4_beats = {
        c: sum(
            (
                acc("FULL_T7") > acc(c),
                fb("FULL_T7") < fb(c),
                harm("FULL_T7") < harm(c),
                fresh("FULL_T7") > fresh(c),
            )
        )
        for c in STRONG
    }
    r4 = all(v >= 2 for v in r4_beats.values())
    r5 = all(
        (
            split_half[arm]["FULL_T7"]["revision_label_accuracy"] >= 0.75,
            all(split_half[arm]["FULL_T7"]["false_broad_revision_rate"] <= split_half[arm][p]["false_broad_revision_rate"] for p in NON_FLOOR),
            all(split_half[arm]["FULL_T7"]["harmful_regression_rate"] <= split_half[arm][p]["harmful_regression_rate"] for p in NON_FLOOR),
            split_half[arm]["FULL_T7"]["protected_fresh_transfer_success_rate"]
            >= max(split_half[arm][p]["protected_fresh_transfer_success_rate"] for p in STRONG) - MARGIN,
        )
        for arm in ("PRIMARY_A", "REPLICATION_B")
    )
    r6 = cross_check_agrees

    rule_trace = {
        "HARMFUL_REFUTED": harm("FULL_T7") > min(harm(p) for p in STRONG),
        "M_OPEN_SUFFICIENT": mopen_perf,
        "OVERCONSERVATIVE": full_perf and r1_strict_highest and r2_strict and fresh("FULL_T7") < max(fresh(p) for p in STRONG) - MARGIN,
        "DIAGNOSIS_ONLY": (
            fb("FULL_T7") <= min(fb(p) for p in NON_FLOOR)
            and harm("FULL_T7") <= min(harm(p) for p in NON_FLOOR)
            and fresh("FULL_T7") >= max(fresh(p) for p in STRONG) - MARGIN
            and repair_class_accuracy["FULL_T7"] < 0.5
            and (cross_checks["FULL_T7"]["independent"]["correct_unresolved_rate"] or 0.0) >= 0.9
        ),
        "NO_INCREMENTAL_VALUE": full_perf and bool(matching),
        "REVISION_LEVEL_DISCRIMINATION_SUPPORTED": (
            full_perf and r1_strict_highest and r2_strict and r4 and r5 and r6 and not matching
        ),
        "CANNOT_CHECK": (not cross_check_agrees) or (not halftest_direction_ok),
    }
    order = (
        "HARMFUL_REFUTED",
        "M_OPEN_SUFFICIENT",
        "OVERCONSERVATIVE",
        "DIAGNOSIS_ONLY",
        "NO_INCREMENTAL_VALUE",
        "REVISION_LEVEL_DISCRIMINATION_SUPPORTED",
        "CANNOT_CHECK",
    )
    terminal = next((t for t in order if rule_trace[t]), None)
    no_frozen_terminal = terminal is None
    if no_frozen_terminal:
        # Measured meta-outcome, recorded verbatim: the frozen rule set does not
        # surject onto the measured region.  No terminal is invented and no rule
        # condition is altered.  (The original runner branch raised here; it was
        # changed to record the empty first-match result after the first run
        # measured it.  This is the only post-outcome edit to this file; see the
        # receipt's post_outcome_runner_note.)
        terminal = "NO_TERMINAL_UNDER_FROZEN_RULES"

    feedback_drops = {
        mode: feedback_sensitivity["NORMAL"]["revision_label_accuracy"] - feedback_sensitivity[mode]["revision_label_accuracy"]
        for mode in ("NONE", "PERMUTED")
    }
    authority_full = cross_checks["FULL_T7"]["independent"]["authority_violation_rate"]
    authority_strong_above_zero = [c for c in STRONG if (cross_checks[c]["independent"]["authority_violation_rate"] or 0) > 0]

    receipt = {
        "schema_version": "orion.p5.revision-level-v3.confirmatory-execution-receipt.v1",
        "record": "P5_H1_H4_V3_CONFIRMATORY_EXECUTION",
        "date": "2026-08-24",
        "protocol_id": "P5.self-orion-v3.revision-level.v1",
        "outcome_accessed_now": True,
        "frozen_binding_verification": verification,
        "decision_layer_by_policy": decision_layer,
        "execution_layer_by_policy": execution_layer,
        "independent_cross_check": cross_checks,
        "cross_check_agrees": cross_check_agrees,
        "repair_class_accuracy_by_policy": repair_class_accuracy,
        "full_t7_feedback_sensitivity": feedback_sensitivity,
        "split_half_by_arm": split_half,
        "split_half_direction_agreement": halftest_direction_ok,
        "h4_round2_negative_history_readmission": {
            "reading_a_subject_shared_set": {
                "n_cases_whose_round1_full_t7_execution_harmful_or_over_broad": len(subject_readmit),
                "per_policy": round2_subject_set,
            },
            "reading_b_per_policy_own_set": {
                "per_policy": round2_own_set,
            },
            "ambiguity_note": "The frozen sentence 'cases whose round-1 execution was harmful or over-broad ... repeated_harmful_admission_rate per policy' admits both readings; both are reported. The pre-registered expectation (history-blind frozen policies) is identical under each.",
        },
        "frozen_rule_evaluation": {
            "rule_trace": rule_trace,
            "terminal": terminal,
            "no_frozen_terminal_fired": no_frozen_terminal,
            "no_terminal_interpretation": (
                "None of the seven frozen terminals' conditions holds for the measured endpoints: the subject (FULL_T7) sat at the "
                "safety floor (accuracy 12/96, no promotion, no fresh transfer), so every rule that requires the R1 accuracy bar or "
                "the R3 fresh-transfer noninferiority fails, while no binding failed, the independent cross-check agreed, and both "
                "split halves agreed on direction. Recorded verbatim per the frozen negative-result policy: no terminal is invented "
                "and no rule is retuned after outcome access."
            )
            if no_frozen_terminal
            else None,
            "full_t7_performance_content": full_perf_parts,
            "m_open_performance_content": mopen_parts,
            "r1_strict_highest": r1_strict_highest,
            "r2_strict_lowest_false_broad_and_harm": r2_strict,
            "r4_strict_beats_count_per_strong_comparator": r4_beats,
            "r4_holds": r4,
            "r5_holds": r5,
            "r6_holds": r6,
            "strong_comparators_matching_within_margins": matching,
            "halves_direction_ok": halftest_direction_ok,
        },
        "secondary_analyses": {
            "feedback_non_compensation": {
                "accuracy_drop_NORMAL_minus_NONE": feedback_drops["NONE"],
                "accuracy_drop_NORMAL_minus_PERMUTED": feedback_drops["PERMUTED"],
                "expected_direction_confirmed": all(d >= 0.10 for d in feedback_drops.values()),
            },
            "cannot_check_blocking": {
                "full_t7_authority_violation_rate": authority_full,
                "strong_comparators_above_zero": authority_strong_above_zero,
                "expected_direction_confirmed": authority_full == 0 and bool(authority_strong_above_zero),
            },
            "negative_history_repeat_admission": {
                "per_policy_own_set": round2_own_set,
                "per_policy_subject_set": round2_subject_set,
                "pre_registered_expectation": "frozen policy set is history-blind at its input interface; round-2 rates equal round-1 by construction unless a policy reads the appended head",
            },
        },
        "margins_applied": {
            "uniform_margin": MARGIN,
            "interpretation_note": "The single declared margin 0.02 applies uniformly to all four primary endpoints (accuracy, false-broad, harm, fresh transfer) wherever a margin is referenced. Frozen in this runner before any outcome access.",
            "tie_interpretation_note": "Under exact endpoint ties the strict-superiority clauses of R1(b)/R2 cannot hold; the performance content of R1-R3 plus the margin-based match test routes ties to NO_INCREMENTAL_VALUE, and REVISION_LEVEL_DISCRIMINATION_SUPPORTED additionally requires strict superiority (R1(b), R2), R4, R5 and R6. Frozen in this runner before any outcome access.",
        },
        "custody": {
            "post_outcome_runner_note": (
                "Two post-outcome edits were made to this runner, neither altering any frozen rule condition: "
                "(1) the no-terminal branch, which originally raised, was changed to record the empty first-match result verbatim; "
                "(2) the H4 secondary, whose frozen sentence admits two readings (subject-shared vs per-policy readmit set), was "
                "changed to report both. All rule predicates are byte-identical to the pre-execution file."
            ),
            "failure_attribution": (
                "One-stage attribution of the subject's collapse to the safety floor: the confirmatory generator modeled TWO "
                "diagnostics in every hypothesis's expectation map (the weak probe and the discriminating probe), while the frozen "
                "T7 protocol observes exactly ONE discriminator per bounded session; assess_responsibility keeps the state UNRESOLVED "
                "while any modeled discriminator of a surviving hypothesis is unobserved "
                "(REQUIRED_DISCRIMINATOR_OBSERVATION_MISSING), so FULL_T7 could never complete a responsibility identification on "
                "any case. The committed development suite models exactly one discriminator per hypothesis, which is why the "
                "development instrumentation reached FULL_T7 accuracy 1.0. The frozen policy code and the gate semantics are "
                "internally consistent; the mismatch is in this suite's expectation modeling, authored before execution and frozen "
                "in PR #1062. The suite is NOT regenerated: the measured behavior (T7 requires complete observational coverage of "
                "every modeled discriminator before any promotion) is a genuine property of the subject mechanism under a bounded "
                "single-probe session and is retained as evidence. Revival lever for the successor panel: hypothesis expectation "
                "sets completable within the bounded protocol (the dev-suite contract) plus preservation-conflict cases that "
                "exercise the revision-gate blocking branch."
            ),
            "suite_sha256": _sha256_file(SUITE_PATH),
            "candidate_packet_sha256": _sha256_file(PACKET_PATH),
            "final_split_sha256": _sha256_file(SPLIT_PATH),
            "rules_sha256": _sha256_file(RULES_PATH),
            "evaluator_sha256": _sha256_file(EVALUATOR_PATH),
            "fresh_transfer_evaluator_sha256": _sha256_file(FRESH_EVALUATOR_PATH),
            "runner_sha256": _sha256_file(Path(__file__)),
        },
        "grants": "Scientific terminal for P5.H1-H4.V3 under the frozen rules only. No self-promotion: scientific authority and peer-review readiness remain governed by the programme's result-verification owner (#283).",
    }
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "terminal": terminal,
        "rule_trace": rule_trace,
        "full_t7_accuracy": decision_layer["FULL_T7"]["revision_label_accuracy"],
        "matching": matching,
        "feedback_drops": feedback_drops,
        "authority_full_t7": authority_full,
        "receipt": str(RECEIPT_PATH.name),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
