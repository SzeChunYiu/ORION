#!/usr/bin/env python3
"""Outcome-exposed recovery replay of the frozen FiberGuard R18 protocol.

The implementation was written after the former positive prose was retracted.
It reads only the prospectively frozen protocol and pinned ASlib bytes; it does
not import the withdrawn result file or infer any target metric from it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
from typing import Any, Iterable

import numpy as np
import sklearn

import fiberguard_paired_route_r18_data as data_module
import fiberguard_paired_route_r18_policy as policy
import fiberguard_paired_route_r18_sources as sources

SCHEMA = "ORION.FiberGuard.PairedRoute.R18.v1"
RECOVERY_TERMINALS = {
    "FIBERGUARD_R18_PAIRED_ROUTE_PASS_MAXSAT_VALIDATION_AND_QBF_TEST",
    "FIBERGUARD_R18_MAXSAT_VALIDATION_PASS__QBF_TEST_FAIL",
    "FIBERGUARD_R18_DEVELOPMENT_ONLY__MAXSAT19_FAIL",
    "FIBERGUARD_R18_NO_PAIRED_ROUTE_VALUE",
}


def _json_default(value: Any):
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(f"not JSON serializable: {type(value)!r}")


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=_json_default,
    )


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _deduplicate_specs(specs: Iterable[dict[str, Any]]) -> tuple[dict[str, Any], ...]:
    result: dict[str, dict[str, Any]] = {}
    for spec in specs:
        result[policy.model_key(spec)] = dict(spec)
    return tuple(result[key] for key in sorted(result))


def _reference_specs(protocol: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    refs = protocol["frozen_reference_baselines"]
    return (dict(refs["knn"]), dict(refs["extra_trees"]))


def _small_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        key: metrics[key]
        for key in (
            "n",
            "mean_total_cost",
            "median_total_cost",
            "p95_total_cost",
            "mean_total_excess",
            "solve_rate",
            "timeout_rate",
            "non_ok_rate",
            "catastrophic_rate",
            "mean_feature_cost",
            "route_change_coverage",
            "certificate_failure_rate",
        )
        if key in metrics
    }


def _route_summary(route: dict[str, Any]) -> dict[str, Any]:
    return {
        "metrics": _small_metrics(route["metrics"]),
        "quantiles": route.get("quantiles", {}),
    }


def _scenario_header(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "scenario": data["scenario"],
        "instance_count": len(data["instances"]),
        "algorithm_count": len(data["algorithms"]),
        "feature_count": len(data["feature_names"]),
        "acquisition_step": data["acquisition_step"],
        "declared_measure": data["measure"],
        "cutoff": data["cutoff"],
        "par10": data["par10"],
        "source_audit": data["source_audit"],
        "run_audit": data["run_audit"],
    }


def evaluate_development(data: dict[str, Any], protocol: dict[str, Any]) -> dict[str, Any]:
    model_specs = policy.canonical_model_specs(protocol)
    reference_specs = _reference_specs(protocol)
    predictions = policy.build_scenario_predictions(
        data,
        _deduplicate_specs(model_specs),
        _deduplicate_specs(reference_specs),
    )
    fallback = policy.fallback_metrics(data, predictions)
    candidates: list[dict[str, Any]] = []
    for spec in model_specs:
        full = policy.full_model_metrics(data, predictions, spec)
        for alpha in protocol["alpha"]:
            for mode in protocol["route_modes"]:
                route = policy.route_candidate(data, predictions, spec, float(alpha), str(mode))
                feasible, failures = policy.candidate_feasible(
                    route, full, fallback, float(alpha), protocol
                )
                candidates.append(
                    {
                        "model": dict(spec),
                        "model_key": policy.model_key(spec),
                        "alpha": float(alpha),
                        "route_mode": str(mode),
                        "feasible": feasible,
                        "failed_constraints": list(failures),
                        "route": _route_summary(route),
                        "full_model": _small_metrics(full),
                        "no_feature_fallback": _small_metrics(fallback),
                        "objective": list(
                            policy.development_objective(
                                route, spec, float(alpha), str(mode)
                            )
                        ),
                    }
                )
    if len(candidates) != int(protocol["development_selection"]["candidate_count"]):
        raise AssertionError(f"candidate count drift: {len(candidates)}")
    feasible_rows = [row for row in candidates if row["feasible"]]
    selection_pool = feasible_rows if feasible_rows else candidates
    selected = min(selection_pool, key=lambda row: tuple(row["objective"]))
    selected_spec = dict(selected["model"])
    selected_alpha = float(selected["alpha"])
    selected_mode = str(selected["route_mode"])

    selected_full = policy.full_model_metrics(data, predictions, selected_spec)
    paired_modes = {
        str(mode): _route_summary(
            policy.route_candidate(
                data, predictions, selected_spec, selected_alpha, str(mode)
            )
        )
        for mode in protocol["route_modes"]
    }
    one_sided = policy.one_sided_candidate(
        data, predictions, selected_spec, selected_alpha
    )
    oracle_route = policy.oracle_contextual_route(data, predictions, selected_spec)
    references = {}
    for name, spec in protocol["frozen_reference_baselines"].items():
        references[name] = _small_metrics(
            policy.full_model_metrics(data, predictions, dict(spec))
        )
    return {
        **_scenario_header(data),
        "candidate_count": len(candidates),
        "feasible_candidate_count": len(feasible_rows),
        "development_pass": bool(feasible_rows),
        "selected_tuple": {
            "model": selected_spec,
            "model_key": selected["model_key"],
            "alpha": selected_alpha,
            "route_mode": selected_mode,
        },
        "selected_route": selected["route"],
        "selected_full_model": _small_metrics(selected_full),
        "no_feature_fallback": _small_metrics(fallback),
        "paired_modes_at_selected_model_alpha": paired_modes,
        "one_sided_learned_certificate": {
            "metrics": _small_metrics(one_sided["metrics"]),
            "authority": "LEARNED_ARM_ONLY__NO_FALLBACK_GUARANTEE",
        },
        "oracle_contextual_route": _small_metrics(oracle_route["metrics"]),
        "reference_full_selectors": references,
        "candidate_table": candidates,
        "transform_audit": predictions["transform_audit"],
    }


def evaluate_frozen_panel(
    data: dict[str, Any],
    protocol: dict[str, Any],
    selected_tuple: dict[str, Any],
) -> dict[str, Any]:
    selected_spec = dict(selected_tuple["model"])
    alpha = float(selected_tuple["alpha"])
    selected_mode = str(selected_tuple["route_mode"])
    refs = _reference_specs(protocol)
    predictions = policy.build_scenario_predictions(
        data,
        _deduplicate_specs((selected_spec,)),
        _deduplicate_specs(refs),
    )
    full = policy.full_model_metrics(data, predictions, selected_spec)
    fallback = policy.fallback_metrics(data, predictions)
    selected_route = policy.route_candidate(
        data, predictions, selected_spec, alpha, selected_mode
    )
    gate = policy.panel_gate(selected_route, full, fallback, alpha, protocol)
    paired_modes = {
        str(mode): _route_summary(
            policy.route_candidate(
                data, predictions, selected_spec, alpha, str(mode)
            )
        )
        for mode in protocol["route_modes"]
    }
    one_sided = policy.one_sided_candidate(data, predictions, selected_spec, alpha)
    oracle_route = policy.oracle_contextual_route(data, predictions, selected_spec)
    references = {}
    for name, spec in protocol["frozen_reference_baselines"].items():
        references[name] = _small_metrics(
            policy.full_model_metrics(data, predictions, dict(spec))
        )
    return {
        **_scenario_header(data),
        "frozen_tuple": selected_tuple,
        "panel_pass": gate["pass"],
        "panel_gate": gate,
        "selected_route": _route_summary(selected_route),
        "selected_full_model": _small_metrics(full),
        "no_feature_fallback": _small_metrics(fallback),
        "paired_modes_at_frozen_model_alpha": paired_modes,
        "one_sided_learned_certificate": {
            "metrics": _small_metrics(one_sided["metrics"]),
            "authority": "LEARNED_ARM_ONLY__NO_FALLBACK_GUARANTEE",
        },
        "oracle_contextual_route": _small_metrics(oracle_route["metrics"]),
        "reference_full_selectors": references,
        "transform_audit": predictions["transform_audit"],
    }


def choose_terminal(
    development: dict[str, Any],
    validation: dict[str, Any],
    test: dict[str, Any],
) -> str:
    if not development["development_pass"]:
        return "FIBERGUARD_R18_NO_PAIRED_ROUTE_VALUE"
    if not validation["panel_pass"]:
        return "FIBERGUARD_R18_DEVELOPMENT_ONLY__MAXSAT19_FAIL"
    if not test["panel_pass"]:
        return "FIBERGUARD_R18_MAXSAT_VALIDATION_PASS__QBF_TEST_FAIL"
    return "FIBERGUARD_R18_PAIRED_ROUTE_PASS_MAXSAT_VALIDATION_AND_QBF_TEST"


def _input_hashes(script_path: Path, protocol_path: Path) -> dict[str, str]:
    names = (
        "fiberguard_paired_route_r18_sources.py",
        "fiberguard_paired_route_r18_data.py",
        "fiberguard_paired_route_r18_policy.py",
        script_path.name,
    )
    result = {name: sha256_file(script_path.with_name(name)) for name in names}
    result[protocol_path.name] = sha256_file(protocol_path)
    return result


def build_comment(result: dict[str, Any]) -> str:
    selected = result["development"]["selected_tuple"]
    lines = [
        "## R18 outcome-exposed recovery replay",
        "",
        f"Execution commit: `{result['prospective_binding']['protocol_execution_commit']}`",
        f"Terminal: `{result['terminal']}`",
        "",
        "This is recovery corroboration under the previously frozen protocol, not a new prospective first result. The former positive prose was withdrawn before this replay and was not an implementation input.",
        "",
        f"Development tuple: `{selected['model_key']}`, alpha `{selected['alpha']}`, mode `{selected['route_mode']}`.",
        "",
        "| Panel | Pass | Routed mean | Full mean | Fallback mean | Route coverage | Certificate failure |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for key in ("development", "validation", "test"):
        panel = result[key]
        route = panel["selected_route"]["metrics"]
        passed = panel.get("development_pass", panel.get("panel_pass", False))
        lines.append(
            "| {name} | {passed} | {route:.6g} | {full:.6g} | {fallback:.6g} | {coverage:.4f} | {failure:.4f} |".format(
                name=panel["scenario"],
                passed=str(bool(passed)).lower(),
                route=route["mean_total_cost"],
                full=panel["selected_full_model"]["mean_total_cost"],
                fallback=panel["no_feature_fallback"]["mean_total_cost"],
                coverage=route["route_change_coverage"],
                failure=route["certificate_failure_rate"],
            )
        )
    lines.extend(
        [
            "",
            "Authority remains marginal under exchangeability; strongest-baseline completeness, external independence, production value, and journal authority remain false.",
            "",
            "Result-subject SHA-256 (canonical JSON before adding this field): "
            f"`{result['result_subject_sha256']}`.",
        ]
    )
    return "\n".join(lines) + "\n"


def _scenario_header_from_panel(panel: dict[str, Any]) -> dict[str, Any]:
    return {
        "instance_count": panel["instance_count"],
        "algorithm_count": panel["algorithm_count"],
        "feature_count": panel["feature_count"],
        "acquisition_step": panel["acquisition_step"],
        "declared_measure": panel["declared_measure"],
        "cutoff": panel["cutoff"],
        "par10": panel["par10"],
    }


def build_result(
    aslib_root: Path,
    protocol_path: Path,
    execution_commit: str,
) -> dict[str, Any]:
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    sources.validate_protocol(protocol)
    data_self_test = data_module.self_test()
    policy_self_test = policy.self_test()
    scenarios = protocol["scenarios"]
    development_data = data_module.load_scenario(
        aslib_root, scenarios["development"], protocol
    )
    validation_data = data_module.load_scenario(
        aslib_root, scenarios["validation"], protocol
    )
    test_data = data_module.load_scenario(aslib_root, scenarios["test"], protocol)

    development = evaluate_development(development_data, protocol)
    selected_tuple = development["selected_tuple"]
    validation = evaluate_frozen_panel(validation_data, protocol, selected_tuple)
    test = evaluate_frozen_panel(test_data, protocol, selected_tuple)
    terminal = choose_terminal(development, validation, test)
    if terminal not in RECOVERY_TERMINALS:
        raise AssertionError(f"unregistered terminal: {terminal}")

    result: dict[str, Any] = {
        "schema": SCHEMA,
        "terminal": terminal,
        "prospective_binding": {
            "original_protocol_commits": [
                "bc3387916139af8a739a910eb58c354f73fb2a24",
                "c2df6e2b47b69f387a33e0ebe5e272fc8a1aad74",
                "1040eaaa56ab5daf087dc01fc9988c7f3a4f2045",
            ],
            "protocol_execution_commit": execution_commit,
            "protocol_sha256": sha256_file(protocol_path),
            "result_absent_from_protocol_inputs": True,
            "withdrawn_positive_prose_used_as_input": False,
            "outcome_exposed_recovery": True,
            "prospective_first_result": False,
        },
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scikit_learn": sklearn.__version__,
            "platform": platform.platform(),
        },
        "implementation_sha256": _input_hashes(Path(__file__), protocol_path),
        "development": development,
        "validation": validation,
        "test": test,
        "scenarios": {
            development["scenario"]: _scenario_header_from_panel(development),
            validation["scenario"]: _scenario_header_from_panel(validation),
            test["scenario"]: _scenario_header_from_panel(test),
        },
        "controls": {
            "synthetic_data_loader_self_test": data_self_test["status"] == "GREEN",
            "synthetic_policy_self_test": policy_self_test["status"] == "GREEN",
            "source_blobs_verified_before_model_fit": True,
            "official_fold_repetition_1_only": True,
            "ten_test_folds_each_with_separate_calibration_fold": True,
            "proper_training_outcomes_only_fit_models_and_fallback": True,
            "development_only_selects_model_alpha_route_tuple": True,
            "validation_and_test_do_not_retune_tuple": True,
            "scenario_specific_solver_models_refit": True,
            "same_statewise_virtual_best_baseline_within_each_scenario": True,
            "learned_and_routed_arms_pay_feature_cost": True,
            "no_feature_fallback_pays_no_feature_cost": True,
            "timeout_and_non_ok_reported_separately": True,
            "declared_PAR10_non_ok_values_checked": True,
            "candidate_denominator_is_99": development["candidate_count"] == 99,
            "all_three_paired_modes_reported_on_every_panel": all(
                set(panel[key]) == set(protocol["route_modes"])
                for panel, key in (
                    (development, "paired_modes_at_selected_model_alpha"),
                    (validation, "paired_modes_at_frozen_model_alpha"),
                    (test, "paired_modes_at_frozen_model_alpha"),
                )
            ),
            "one_sided_reference_preserved_without_fallback_claim": True,
            "former_positive_terminal_not_used_to_construct_runner": True,
            "recovery_authority_not_laundered_as_prospective": True,
        },
        "authority": {
            "paired_certificates": "MARGINAL_UNDER_EXCHANGEABILITY",
            "interval_no_harm": "POINTWISE_ON_JOINT_VALIDITY_EVENT",
            "worst_case_fibre_safety": False,
            "conditional_routed_case_coverage": False,
            "family_shift_validity": False,
            "pathwise_randomization_safety": False,
            "strongest_algorithm_selection_baseline_complete": False,
            "external_independence": False,
            "production_value": False,
            "grants_journal_authority": False,
            "recovery_status": "OUTCOME_EXPOSED_CORROBORATION",
        },
    }
    payload_without_digest = canonical_json(result)
    result["result_subject_sha256"] = hashlib.sha256(
        payload_without_digest.encode()
    ).hexdigest()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aslib-root", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--protocol-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--comment-output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.comment_output.exists():
        raise FileExistsError("R18 recovery outputs are write-once")
    result = build_result(args.aslib_root, args.protocol, args.protocol_commit)
    payload = canonical_json(result) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(payload, encoding="utf-8", errors="strict")
    args.comment_output.write_text(build_comment(result), encoding="utf-8")
    print(
        f"{result['terminal']} sha256={hashlib.sha256(payload.encode()).hexdigest()} "
        "authority=OUTCOME_EXPOSED_RECOVERY_CORROBORATION"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
