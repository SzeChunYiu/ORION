"""Guards for the ORION-P2 frozen measurement + statistical plan.

The plan is only useful if it cannot silently drift away from the frozen
protocol it binds or from the statistics library it quotes. Every check here
exists because a specific drift would otherwise go unnoticed: a metric added to
the protocol and never measured, a margin edited out of range, a precision
number typed by hand, or an oracle metric with no field to compute it from.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers" / "orion-12-open-world-scientific-discovery" / "protocol"
PROTOCOL_PATH = PAPER / "PROTOCOL_V1.json"
PLAN_PATH = PAPER / "STATISTICAL_PLAN_V1.json"
MEASUREMENT_PATH = PAPER / "MEASUREMENT_PLAN_V1.md"
STATS_MODULE = ROOT / "research" / "paper-programme-v1" / "protocols" / "publication_stats.py"

# The frozen protocol scopes the primary to three benchmark families in its own
# `multiplicity` field, even though it lists five task families. Pinning the set
# as a literal keeps the test from demanding primaries the protocol contradicts.
PRIMARY_BEARING_FAMILIES = {
    "autoresearchbench_deep",
    "autoresearchbench_wide",
    "offline_complete_gold",
}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_stats_module():
    spec = importlib.util.spec_from_file_location("publication_stats", STATS_MODULE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_plan_parses_and_stays_outcome_blind() -> None:
    plan = _load_json(PLAN_PATH)
    assert plan["schema_version"] == "orion.p2.statistical-plan.v1"
    assert plan["paper_id"] == "P2"
    assert plan["binds_protocol_id"] == _load_json(PROTOCOL_PATH)["protocol_id"]
    assert plan["plan_status"] == "DESIGN_FROZEN"
    assert plan["outcome_accessed"] is False


def test_protocol_remains_untouched_by_this_lane() -> None:
    protocol = _load_json(PROTOCOL_PATH)
    assert protocol["protocol_status"] == "DESIGN_FROZEN"
    assert protocol["outcome_accessed"] is False
    assert protocol["execution_bindings"]["subject_revision"] == "UNBOUND"


def test_every_protocol_metric_is_registered_with_a_role_and_direction() -> None:
    protocol = _load_json(PROTOCOL_PATH)
    registry = _load_json(PLAN_PATH)["metric_registry"]
    declared = set(protocol["metrics"]["primary"]) | set(protocol["metrics"]["secondary"])
    assert declared <= set(registry), f"unmeasured protocol metrics: {sorted(declared - set(registry))}"

    allowed_roles = {"family_primary", "primary_safety_guard", "secondary", "secondary_non_inferential"}
    for name in sorted(declared):
        entry = registry[name]
        assert entry["role"] in allowed_roles, name
        assert entry["direction"] in {"higher_better", "lower_better", "context_dependent_reported_not_optimized"}, name
        assert entry["denominator_validity"], name
        assert entry["degrades_to"], name
        assert entry["statistical_unit"], name


def test_exactly_one_family_primary_per_primary_bearing_family() -> None:
    plan = _load_json(PLAN_PATH)
    families = plan["primary_bearing_families"]
    assert set(families) == PRIMARY_BEARING_FAMILIES

    registry = plan["metric_registry"]
    for family, spec in families.items():
        metric = spec["family_primary"]
        assert registry[metric]["role"] == "family_primary"
        assert registry[metric]["family"] == family
        assert spec["tested_once"] is True

    owners = [entry["family"] for entry in registry.values() if entry["role"] == "family_primary"]
    assert sorted(owners) == sorted(PRIMARY_BEARING_FAMILIES), "a family primary must be owned by exactly one family"

    # Families the protocol excludes from the primary must say so, not be silent.
    protocol_families = set(_load_json(PROTOCOL_PATH)["task_families"])
    for family in sorted(protocol_families - PRIMARY_BEARING_FAMILIES):
        entry = plan["non_primary_bearing_families"][family]
        assert entry["carries_confirmatory_primary"] is False
        assert entry["role"]


def test_safety_guard_is_primary_but_not_a_family_primary() -> None:
    plan = _load_json(PLAN_PATH)
    guard = plan["primary_safety_guard"]
    metric = guard["metric"]
    assert metric in _load_json(PROTOCOL_PATH)["metrics"]["primary"]
    assert plan["metric_registry"][metric]["role"] == "primary_safety_guard"
    assert guard["direction"] == "lower_better"
    holm_metrics = {name for family in plan["multiplicity"]["holm_families"] for name in family["metrics"]}
    assert metric not in holm_metrics, "the guard is tested once and must not enter a Holm family"


def test_margins_are_numeric_in_range_and_correctly_ordered() -> None:
    margins = _load_json(PLAN_PATH)["margins"]
    delta_sup = margins["superiority_margin_delta_sup"]
    delta_safety = margins["safety_guard_margin_delta_safety"]
    delta_ni = margins["non_inferiority_margin_delta_ni"]
    for value in (delta_sup, delta_safety, delta_ni):
        assert isinstance(value, (int, float)) and not isinstance(value, bool)
        assert 0.0 < float(value) < 1.0
    assert delta_ni < delta_sup, "a non-inferiority claim must clear a tighter band than a superiority claim"
    assert delta_safety <= delta_sup, "a recall gain cannot be bought with a larger closure regression"

    for spec in _load_json(PLAN_PATH)["primary_bearing_families"].values():
        assert spec["superiority_margin"] == delta_sup
        assert spec["direction"] in {"higher_better", "lower_better"}

    ceiling = _load_json(PLAN_PATH)["non_inferiority_rule"]["cost_admissibility"]["cost_ratio_ceiling"]
    assert isinstance(ceiling, (int, float)) and ceiling >= 1.0


def test_every_baseline_and_ablation_is_covered() -> None:
    protocol = _load_json(PROTOCOL_PATH)
    plan = _load_json(PLAN_PATH)

    baselines = plan["baselines"]
    families = set(protocol["task_families"])
    for name in protocol["baselines"]:
        entry = baselines[name]
        applies = set(entry["applies_to"])
        assert applies, f"{name} must apply somewhere"
        assert applies <= families, f"{name} names an unknown family"
        assert entry["role"] in {"comparator", "promotion_gate"}

    gates = [
        name
        for name, entry in baselines.items()
        if isinstance(entry, dict) and entry["role"] == "promotion_gate"
    ]
    assert gates == ["bm25_keyword"], "the strong lexical baseline is the promotion gate"
    assert PRIMARY_BEARING_FAMILIES <= set(baselines["bm25_keyword"]["applies_to"])

    ablations = plan["ablations"]
    hypotheses = {protocol["primary_hypothesis"]["id"]} | {item["id"] for item in protocol["secondary_hypotheses"]}
    for name in protocol["ablations"]:
        entry = ablations[name]
        assert entry["hypothesis"] in hypotheses, name
        assert entry["predeclared_expected_direction"], name
        assert entry["primary_readout"] in plan["metric_registry"], name

    negative = ablations["coverage_diagnostic_controls_stopping"]
    assert negative["ablation_class"] == "negative_safety_ablation"
    assert "improves" not in negative["predeclared_expected_direction"]


def test_precision_numbers_match_the_statistics_library() -> None:
    module = _load_stats_module()
    plan = _load_json(PLAN_PATH)
    precision = plan["precision_plan"]
    assert precision["planning_function"].endswith("required_n_for_proportion_half_width")

    tiers = precision["precision_tiers"]
    assert tiers, "the plan must quote at least one precision tier"
    for tier in tiers:
        expected = module.required_n_for_proportion_half_width(tier["half_width"], tier["assumed_p"])
        assert tier["required_n"] == expected, (
            f"{tier['tier']}: plan says {tier['required_n']}, library says {expected}"
        )
        assert tier["assumed_p"] == 0.5, "assumed_p is frozen at 0.5; a smaller value anticipates an outcome"

    # Tighter half-width must cost more samples, or the tier ladder is nonsense.
    ordered = sorted(tiers, key=lambda item: item["half_width"])
    ns = [item["required_n"] for item in ordered]
    assert ns == sorted(ns, reverse=True)

    committed = precision["family_n_policy"]["offline_complete_gold"]
    expected_n = module.required_n_for_proportion_half_width(committed["committed_half_width"], 0.5)
    assert committed["committed_required_n"] == expected_n


def test_uncertainty_and_repeat_rules_are_frozen() -> None:
    plan = _load_json(PLAN_PATH)
    paired = plan["uncertainty"]["paired_differences"]
    assert paired["resamples"] == 10000
    assert paired["confidence"] == 0.95
    assert isinstance(paired["analysis_seed"], int)
    assert plan["uncertainty"]["standalone_binary_rates"]["estimator"] == "wilson_interval"
    assert plan["uncertainty"]["reimplementation_forbidden"] is True

    repeats = plan["pairing_and_repeats"]
    assert repeats["stochastic_repeats"] == _load_json(PROTOCOL_PATH)["statistics"]["stochastic_repeats"]
    assert repeats["repeat_collapse_rule"] == "mean"
    assert repeats["collapse_before_bootstrap"] is True
    assert "best_of_n" in repeats["forbidden_collapse_rules"]
    assert repeats["pairwise_complete_deletion"]["rule"]


def test_multiplicity_families_are_disjoint_and_cost_is_non_inferential() -> None:
    plan = _load_json(PLAN_PATH)
    multiplicity = plan["multiplicity"]
    assert multiplicity["correction"] == "holm"

    seen: set[str] = set()
    for family in multiplicity["holm_families"]:
        metrics = family["metrics"]
        assert family["test_count"] == len(metrics)
        assert not (set(metrics) & seen), f"{family['family_id']} reuses a metric from another Holm family"
        seen.update(metrics)
        for name in metrics:
            assert plan["metric_registry"][name]["role"] == "secondary"

    for name in multiplicity["non_inferential_metrics"]:
        assert plan["metric_registry"][name]["role"] == "secondary_non_inferential"
        assert name not in seen, "a non-inferential cost metric must not inflate a Holm family"


def test_budget_and_exclusion_policies_are_symmetric_and_retain_failures() -> None:
    plan = _load_json(PLAN_PATH)

    budget = plan["matched_budget_policy"]
    assert set(budget["capped_resources"]) == {"query_count", "tool_calls", "model_tokens", "wallclock_seconds"}
    for resource in budget["capped_resources"]:
        ladder = budget["frozen_ladder"][resource]
        assert ladder == sorted(ladder)
        assert budget["absolute_ceiling_per_task"][resource] == ladder[-1]
    assert budget["cap_hit_rule"]["outcome"] == "RETAINED"
    assert budget["cap_hit_rule"]["discarding_truncated_runs_is_forbidden"] is True

    exclusion = plan["exclusion_policy"]
    assert exclusion["symmetric"] is True and exclusion["predeclared"] is True
    retained = set(exclusion["retained_always"])
    for required in ("agent_timeout", "malformed_output", "abstention", "provider_unavailability", "candidate_caused_failure"):
        assert required in retained, f"{required} must be retained, not excluded"
    assert exclusion["excludable_only"]["class"] == "host_infrastructure_outage"
    assert exclusion["excludable_only"]["visible_in_archive"] is True
    assert 0.0 < exclusion["exclusion_budget"]["max_excluded_fraction_per_family"] < 1.0


def test_decision_rule_forbids_promoting_a_null() -> None:
    plan = _load_json(PLAN_PATH)
    decision = plan["decision_rule"]
    outcomes = {item["id"]: item for item in decision["outcomes"]}
    assert {"PROMOTE_SUPERIORITY", "PROMOTE_NON_INFERIORITY_WITH_SAFETY", "SHRINK", "REFRAME", "CANNOT_CHECK"} <= set(outcomes)

    shrink_text = json.dumps(outcomes["SHRINK"]).lower()
    assert "not_supported" in shrink_text
    assert "forbidden_action" in outcomes["SHRINK"]

    null_rule = decision["if_orion_does_not_beat_simple_retrieval"].lower()
    assert "shrink" in null_rule and "reframe" in null_rule
    assert "never" in null_rule or "under no condition" in null_rule

    assert "REFRAME" in outcomes and "lexical" in json.dumps(outcomes["REFRAME"]).lower()
    for forbidden in ("changing any margin", "promoting an exploratory metric to secondary or primary"):
        assert forbidden in decision["forbidden_after_outcome_access"]


def test_every_oracle_metric_has_at_least_one_required_binding() -> None:
    plan = _load_json(PLAN_PATH)
    bindings = plan["required_bindings"]
    ids = [item["id"] for item in bindings]
    assert len(ids) == len(set(ids))
    for binding in bindings:
        for key in ("field", "type", "meaning", "metrics_enabled"):
            assert binding[key], f"{binding['id']} is missing {key}"
        assert set(binding["metrics_enabled"]) <= set(plan["metric_registry"])

    known = set(ids)
    oracle_metrics = [name for name, entry in plan["metric_registry"].items() if "oracle_id" in entry]
    assert oracle_metrics, "the oracle-dependent metrics must be marked"
    for name in oracle_metrics:
        entry = plan["metric_registry"][name]
        assert entry["oracle_id"] in plan["oracles"]
        assert entry["required_binding_ids"], f"{name} has an oracle but no field to compute it from"
        assert set(entry["required_binding_ids"]) <= known

    enabled = {name for binding in bindings for name in binding["metrics_enabled"]}
    for name in oracle_metrics:
        assert name in enabled, f"no binding declares it enables {name}"


def test_oracle_thresholds_are_numbers_not_placeholders() -> None:
    oracles = _load_json(PLAN_PATH)["oracles"]
    assert set(oracles) == {"O1", "O2", "O3", "O4"}

    o1 = oracles["O1"]
    assert isinstance(o1["marginal_yield_threshold"], int) and o1["marginal_yield_threshold"] >= 1
    assert isinstance(o1["exhaustion_grace_attempts"], int) and o1["exhaustion_grace_attempts"] >= 0
    assert float(o1["min_remaining_budget_units"]) > 0
    assert set(o1["denominators"]) == {"false_positive_rate", "false_negative_rate"}

    assert oracles["O2"]["never_scored_as"].startswith("0")
    assert "identity.py" in oracles["O3"]["mechanism_source"]
    for state in ("CONTENT_CHANGED", "NEW_SCHEMA", "NEW_FRAME", "ALREADY_READ", "UNSEEN"):
        assert state in oracles["O3"]["definition"]
    assert "merge_identities" in oracles["O3"]["identity_requirement"]
    assert any("evidence of absence" in rule for rule in oracles["O4"]["accounting_rules"])


def test_exploratory_diagnostics_are_separate_and_unpromotable() -> None:
    plan = _load_json(PLAN_PATH)
    exploratory = plan["exploratory_diagnostics"]
    registry = set(plan["metric_registry"])
    for name in exploratory:
        if name == "note":
            continue
        assert name not in registry, f"{name} must stay out of the confirmatory registry"
    assert plan["multiplicity"]["exploratory_never_promoted"] is True


def test_every_frozen_figure_and_table_is_bound_to_what_it_may_render() -> None:
    protocol = _load_json(PROTOCOL_PATH)
    plan = _load_json(PLAN_PATH)
    bindings = plan["figure_bindings"]
    registry = set(plan["metric_registry"])
    exploratory = {name for name in plan["exploratory_diagnostics"] if name != "note"}

    assert list(bindings["figures"]) == protocol["plots"], "figure bindings must cover the frozen plot list exactly once, in order"
    assert list(bindings["tables"]) == protocol["tables"], "table bindings must cover the frozen table list exactly once, in order"

    allowed_roles = {"schematic", "manifest", "exploratory", "secondary", "primary_safety_guard", "family_primary"}
    for group in ("figures", "tables"):
        for name, entry in bindings[group].items():
            assert entry["role"] in allowed_roles, name
            assert entry["kind"] in {"schematic", "manifest", "result"}, name
            assert set(entry["renders_metrics"]) <= registry, f"{name} renders an unregistered metric"
            assert set(entry.get("renders_exploratory", [])) <= exploratory, name
            if entry["kind"] == "result":
                assert entry["renders_metrics"] or entry.get("renders_exploratory"), f"{name} claims to be a result but renders nothing"
            else:
                assert not entry["renders_metrics"], f"{name} carries no result and must render no metric"

    # A caption's declared role must be reachable from what the figure renders,
    # otherwise a secondary panel can be captioned as a primary result.
    rank = {"secondary_non_inferential": 0, "secondary": 1, "primary_safety_guard": 2, "family_primary": 3}
    for group in ("figures", "tables"):
        for name, entry in bindings[group].items():
            metrics = entry["renders_metrics"]
            if not metrics or entry["role"] in {"schematic", "manifest", "exploratory"}:
                continue
            best = max(rank[plan["metric_registry"][m]["role"]] for m in metrics)
            assert rank[entry["role"]] <= best, f"{name} is captioned above the strongest role it renders"

    assert set(bindings["caption_must_state"]) >= {"n", "aggregation_unit", "uncertainty_definition", "role"}

    # Every confirmatory metric must be renderable somewhere, or it is frozen
    # into the plan and then never shown.
    rendered = {m for group in ("figures", "tables") for entry in bindings[group].values() for m in entry["renders_metrics"]}
    declared = set(protocol["metrics"]["primary"]) | set(protocol["metrics"]["secondary"])
    assert declared <= rendered, f"never rendered: {sorted(declared - rendered)}"


def test_margins_are_held_once_and_agree_across_the_plan() -> None:
    plan = _load_json(PLAN_PATH)
    margins = plan["margins"]

    guard = plan["primary_safety_guard"]
    assert guard["margin_ref"] == "margins.safety_guard_margin_delta_safety"
    assert guard["margin"] == margins["safety_guard_margin_delta_safety"]

    ni_rule = plan["non_inferiority_rule"]
    assert ni_rule["margin_ref"] == "margins.non_inferiority_margin_delta_ni"
    assert ni_rule["margin"] == margins["non_inferiority_margin_delta_ni"]

    # The prose must not restate a margin literal, or an edit to the machine
    # value leaves a stale number that still reads as authoritative.
    literal = repr(float(margins["non_inferiority_margin_delta_ni"]))
    assert literal not in ni_rule["pass_condition"]


def test_holm_membership_agrees_in_both_directions() -> None:
    plan = _load_json(PLAN_PATH)
    registry = plan["metric_registry"]
    declared: dict[str, str] = {}
    for family in plan["multiplicity"]["holm_families"]:
        for name in family["metrics"]:
            declared[name] = family["family_id"]

    for name, family_id in declared.items():
        assert registry[name].get("holm_family") == family_id, (
            f"{name} is listed under {family_id} but its registry entry says {registry[name].get('holm_family')}"
        )
    for name, entry in registry.items():
        if "holm_family" in entry:
            assert declared.get(name) == entry["holm_family"], f"{name} claims a Holm family that does not list it"


def test_measurement_plan_numbers_match_the_machine_values() -> None:
    text = MEASUREMENT_PATH.read_text(encoding="utf-8")
    plan = _load_json(PLAN_PATH)
    margins = plan["margins"]

    # Any number the prose states must be the number the plan enforces.
    for label, value in (
        ("delta_sup", margins["superiority_margin_delta_sup"]),
        ("delta_safety", margins["safety_guard_margin_delta_safety"]),
        ("delta_ni", margins["non_inferiority_margin_delta_ni"]),
        ("cost_ratio_ceiling", plan["non_inferiority_rule"]["cost_admissibility"]["cost_ratio_ceiling"]),
    ):
        assert str(value) in text, f"{label}={value} is enforced by the plan but absent from the measurement plan prose"

    assert str(plan["precision_plan"]["family_n_policy"]["offline_complete_gold"]["committed_required_n"]) in text
    assert str(plan["pairing_and_repeats"]["stochastic_repeats"]) in text
    pct = plan["exclusion_policy"]["exclusion_budget"]["max_excluded_fraction_per_family"]
    assert f"{pct:.0%}".replace("%", "%") in text or f"{int(pct * 100)}%" in text

    o1 = plan["oracles"]["O1"]
    assert str(o1["marginal_yield_threshold"]) in text
    assert str(o1["exhaustion_grace_attempts"]) in text


def test_measurement_plan_documents_every_metric_and_lists_bindings() -> None:
    text = MEASUREMENT_PATH.read_text(encoding="utf-8")
    protocol = _load_json(PROTOCOL_PATH)
    for name in set(protocol["metrics"]["primary"]) | set(protocol["metrics"]["secondary"]):
        assert name in text, f"{name} is undocumented in the measurement plan"

    assert "REQUIRED BINDINGS" in text.upper()
    # Require the summary-table row, not a bare substring: the id also appears in
    # prose, so a containment check would pass a table that lost the row.
    for binding in _load_json(PLAN_PATH)["required_bindings"]:
        assert f"| {binding['id']} |" in text, f"binding {binding['id']} has no row in the measurement plan"

    for oracle_id in ("O1", "O2", "O3", "O4"):
        assert oracle_id in text
    assert "SYNTHETIC - ILLUSTRATIVE ONLY" in text
    assert len(text.splitlines()) <= 200, "the measurement plan must stay a distilled document"


def test_strictness_deltas_are_declared_not_silent() -> None:
    plan = _load_json(PLAN_PATH)
    deltas = plan["stricter_than_analysis_standard"]
    assert len(deltas) >= 5
    topics = {item["topic"] for item in deltas}
    for expected in ("pairwise_complete_deletion", "repeat_collapse", "cost_metrics", "non_inferiority_margin", "cannot_check"):
        assert expected in topics
    for item in deltas:
        assert item["standard_says"] and item["this_plan_adds"]
    assert "REQUIRED BINDINGS" in MEASUREMENT_PATH.read_text(encoding="utf-8").upper()
