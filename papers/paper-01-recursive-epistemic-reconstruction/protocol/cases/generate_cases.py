#!/usr/bin/env python3
"""
Assisted case generator for ORION-P1 expansion from n=48 to n=385 (TIER_B).

This script uses parametric templates to generate new cases following the
HIDDEN_SHIFT_CASE_SCHEMA_V1.json schema. Each generated case MUST be reviewed
by hand before committing to ensure:
1. The scenario is coherent and non-trivial
2. The hidden shift is genuine (not obvious)
3. The root_success_rubric is precise and falsifiable
4. The closure chain is consistent

Usage:
    python3 generate_cases.py --family hidden_parent_domain --count 56 --start 149
    python3 generate_cases.py --all  # Generate all 337 cases
"""

import argparse
import json
import math
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Literal

CASES_ROOT = Path(__file__).parent / "test"
TEMPLATE_ROOT = Path(__file__).parent / "templates"
OUTPUT_ROOT = Path(__file__).parent / "test_expanded"


class TaskFamily(str, Enum):
    """The six P1 task families."""

    HIDDEN_PARENT_DOMAIN = "hidden_parent_domain"
    HIDDEN_REPRESENTATION_OR_COORDINATE_SYSTEM = "hidden_representation_or_coordinate_system"
    HIDDEN_DECOMPOSITION_OR_INTERFACE = "hidden_decomposition_or_interface"
    HIDDEN_MEASUREMENT_OR_OPERATIONALIZATION = "hidden_measurement_or_operationalization"
    EVIDENCE_ONLY_NEGATIVE_CONTROL = "evidence_only_negative_control"
    EXECUTION_ONLY_NEGATIVE_CONTROL = "execution_only_negative_control"


class ResponsibilityFamily(str, Enum):
    """Responsibility families for hidden shift cases."""

    SEARCH = "SEARCH"
    REPRESENTATION = "REPRESENTATION"
    DECOMPOSITION = "DECOMPOSITION"
    MEASUREMENT = "MEASUREMENT"
    EVIDENCE = "EVIDENCE"  # For negative controls where reframe is WRONG
    EXECUTION = "EXECUTION"  # For negative controls where reframe is WRONG


@dataclass
class CaseTemplate:
    """Template for generating cases."""

    family: TaskFamily
    responsibility_family: ResponsibilityFamily
    target_coordinate_base: str  # e.g., "causal_inference"
    reframe_required: bool
    scenario_template: str  # Template with {placeholders}
    resources_template: list[str]  # Template resources
    rubric_template: str  # Template rubric
    notes_template: str

    def generate(
        self,
        case_id: str,
        params: dict,
        seed: int,
    ) -> dict:
        """Generate a case from this template with given parameters."""

        # Build parameter map for substitution
        param_map = {
            "case_id": case_id,
            "seed": seed,
            **params,
        }

        # Substitute in scenario
        scenario = self.scenario_template.format(**param_map)

        # Build resources
        resources = []
        for resource_tmpl in self.resources_template:
            try:
                resource = resource_tmpl.format(**param_map)
                resources.append(resource)
            except KeyError:
                # Skip resources with missing params
                resources.append(resource_tmpl)

        # Build closure chain
        closure_chain = self._build_closure_chain(params, seed)

        # Build target coordinates
        target_coords = [
            f"W.{self.responsibility_family.value}",
            f"{self.target_coordinate_base}:{params.get('specific_coord', 'default')}",
        ]

        # Build rubric
        rubric = self.rubric_template.format(**param_map)

        # Build notes
        notes = self.notes_template.format(**param_map)

        # Construct the case
        case = {
            "case_id": case_id,
            "task_family": self.family.value,
            "public_prompt": scenario,
            "observable_resources": resources + closure_chain["resources"],
            "protected_gold": {
                "reframe_required": self.reframe_required,
                "responsibility_family": self.responsibility_family.value,
                "target_coordinates": target_coords,
                "dependencies_to_reopen": closure_chain["to_reopen"],
                "root_success_rubric": rubric,
                "dependency_depth": closure_chain["depth"],
            },
            "budget_class": "p1_standard_v1",
            "adjudication_status": "MECHANICAL_GOLD",
            "source_provenance": [
                "CONSTRUCTED_FOR_ORION_P1",
                "no external dataset; every figure is authored for this benchmark and is not an empirical finding",
            ],
            "notes": notes,
        }

        return case

    def _build_closure_chain(self, params: dict, seed: int) -> dict:
        """Build a closure chain from parameters."""
        depth = params.get("dependency_depth", 1)

        # Generate closure IDs
        base_name = params.get("closure_base", "decision")
        closures = [f"closure:{base_name}-{i}" for i in range(depth)]

        # Build closure resources
        resources = []
        for i, closure_id in enumerate(closures):
            if i == 0:
                resources.append(f"{closure_id} — closed; records the {params.get('primary_decision', 'decision')}")
            else:
                resources.append(f"{closure_id} — closed; derived from {closures[i-1]}")

        # Add independent closures
        for indep in params.get("independent_closures", []):
            resources.append(f"{indep} — closed; {params.get('independent_closure_desc', 'independent decision')}")

        return {
            "resources": resources,
            "to_reopen": closures[: params.get("reopen_depth", depth)],
            "depth": depth,
        }


# TEMPLATES FOR EACH FAMILY
# These are parametric templates that generate cases with variations

TEMPLATES: dict[TaskFamily, list[CaseTemplate]] = {
    # Hidden parent domain cases
    TaskFamily.HIDDEN_PARENT_DOMAIN: [
        CaseTemplate(
            family=TaskFamily.HIDDEN_PARENT_DOMAIN,
            responsibility_family=ResponsibilityFamily.SEARCH,
            target_coordinate_base="parent_domain",
            reframe_required=True,
            scenario_template=(
                "A {intervention_noun} was {deployed_verb} and {stat} of {total} {units} "
                "{outcome_verb} during {period}. Since then, the {participating_units} report "
                "{delta}% {metric_change} than the rest. The reading so far: this gap is "
                "the effect of the {intervention_noun}. Report the effect of the {intervention_noun} "
                "on {metric}."
            ),
            resources_template=[
                "{data_file} — {total} {units}; {stat} {participated_verb} during {period}; "
                "{participation_desc}",
                "{pre_period_file} — in the {pre_duration} before the {intervention_noun} existed, "
                "those same {participating_units} already reported {pre_delta}% {metric_change} than the rest",
                "{covariates_file} — {covariate_desc}",
                "{design_note} — no {unit} was assigned at random, and every {participating_unit} "
                "has been on the {intervention_noun} continuously since {period}",
            ],
            rubric_template=(
                "PASS iff the answer refuses the raw {delta}% contrast, uses the {pre_delta}% "
                "pre-period gap to show the two groups differed before the {intervention_noun} existed, "
                "and either reports an adjusted estimate under a stated identifying assumption "
                "(a difference of the pre and post gaps is about {adjusted_delta} percentage points) "
                "or declares the effect unidentified and names a design that would identify it. "
                "FAIL if the answer reports {delta}%, or dismisses the finding as mere correlation "
                "without producing either an adjusted estimate or a design."
            ),
            notes_template=(
                "A solver that keeps the framing reports {delta}% as the effect; the pre-period record "
                "shows most of that gap predates the {intervention_noun}."
            ),
        ),
        # Additional templates can be added here for variety
    ],

    # Hidden representation cases
    TaskFamily.HIDDEN_REPRESENTATION_OR_COORDINATE_SYSTEM: [
        CaseTemplate(
            family=TaskFamily.HIDDEN_REPRESENTATION_OR_COORDINATE_SYSTEM,
            responsibility_family=ResponsibilityFamily.REPRESENTATION,
            target_coordinate_base="representation",
            reframe_required=True,
            scenario_template=(
                "A {tool_noun} {aggregates_verb} {count} {measurement_unit} {measurements}, "
                "reported in {units}, to produce a {output_desc}. The approach on the table: "
                "{wrong_approach}. Report the {output_noun}."
            ),
            resources_template=[
                "{data_file} — {pattern_desc}",
                "{tool_file} — computes the {wrong_approach}",
                "{reported_file} — {reported_value}",
                "{correct_file} — the {correct_approach_data}",
            ],
            rubric_template=(
                "PASS iff the {output_noun} is computed using the {correct_approach}, "
                "giving a value of {correct_value}, and the answer explains why the "
                "{wrong_approach} fails. FAIL if the answer reports {reported_value}, "
                "removes data as outliers, or reports the {measurement_unit} as too variable to summarise."
            ),
            notes_template=(
                "A solver that keeps the {wrong_approach} framing reports {reported_value}, "
                "which is incorrect because {reason}."
            ),
        ),
    ],

    # Hidden decomposition cases
    TaskFamily.HIDDEN_DECOMPOSITION_OR_INTERFACE: [
        CaseTemplate(
            family=TaskFamily.HIDDEN_DECOMPOSITION_OR_INTERFACE,
            responsibility_family=ResponsibilityFamily.DECOMPOSITION,
            target_coordinate_base="decomposition",
            reframe_required=True,
            scenario_template=(
                "{problem_desc}. The approach on the table: {wrong_solution}. "
                "Diagnose the defect and specify the fix."
            ),
            resources_template=[
                "{context_file} — {context_desc}",
                "{evidence_file} — {evidence_desc}",
                "{trial_file} — {trial_result}",
                "{usage_file} — {usage_pattern}",
            ],
            rubric_template=(
                "PASS iff the specified design implements {correct_decomposition}, "
                "and the answer states why {wrong_solution} is incorrect. "
                "FAIL if the fix is {wrong_solution} or a variant."
            ),
            notes_template=(
                "A solver that keeps the {wrong_solution} framing publishes {consequence}."
            ),
        ),
    ],

    # Hidden measurement cases
    TaskFamily.HIDDEN_MEASUREMENT_OR_OPERATIONALIZATION: [
        CaseTemplate(
            family=TaskFamily.HIDDEN_MEASUREMENT_OR_OPERATIONALIZATION,
            responsibility_family=ResponsibilityFamily.MEASUREMENT,
            target_coordinate_base="measurement",
            reframe_required=True,
            scenario_template=(
                "{context_desc}. The approach on the table: {wrong_measurement}. "
                "Report the {metric_noun}."
            ),
            resources_template=[
                "{data_file} — {data_pattern}",
                "{measurement_file} — implements {wrong_measurement}",
                "{reported_file} — {reported_value}",
                "{correct_file} — the {correct_measurement_data}",
            ],
            rubric_template=(
                "PASS iff the {metric_noun} is computed using {correct_measurement}, "
                "giving {correct_value}, and the answer explains the flaw in {wrong_measurement}. "
                "FAIL if the answer reports {reported_value} or uses {wrong_measurement}."
            ),
            notes_template=(
                "A solver that keeps the {wrong_measurement} framing reports {reported_value}, "
                "which is incorrect because {reason}."
            ),
        ),
    ],

    # Evidence-only negative controls (reframe is WRONG)
    TaskFamily.EVIDENCE_ONLY_NEGATIVE_CONTROL: [
        CaseTemplate(
            family=TaskFamily.EVIDENCE_ONLY_NEGATIVE_CONTROL,
            responsibility_family=ResponsibilityFamily.EVIDENCE,
            target_coordinate_base="negative_control",
            reframe_required=False,
            scenario_template=(
                "{scenario_desc}. The current line is: {task_desc}."
            ),
            resources_template=[
                "{evidence_file} — {evidence_desc}",
                "{context_file} — {context_desc}",
            ],
            rubric_template=(
                "PASS iff the answer solves the {task_desc} without reframing. "
                "FAIL if the answer reframes the problem or claims the domain/representation/decomposition is wrong."
            ),
            notes_template=(
                "Evidence-only negative control: all information is provided; reframe is the wrong move."
            ),
        ),
    ],

    # Execution-only negative controls (reframe is WRONG)
    TaskFamily.EXECUTION_ONLY_NEGATIVE_CONTROL: [
        CaseTemplate(
            family=TaskFamily.EXECUTION_ONLY_NEGATIVE_CONTROL,
            responsibility_family=ResponsibilityFamily.EXECUTION,
            target_coordinate_base="negative_control",
            reframe_required=False,
            scenario_template=(
                "{scenario_desc}. The current line is: find the defect and repair it. "
                "Name the defect and give the repair."
            ),
            resources_template=[
                "{evidence_file} — {evidence_desc}",
                "{context_file} — {context_desc}",
            ],
            rubric_template=(
                "PASS iff the answer names the {defect_desc} as the defect and repairs it by "
                "{correct_repair}. FAIL if the answer adds a {wrong_repair}, marks the tests as "
                "{wrong_mark}, or changes the {wrong_change}."
            ),
            notes_template=(
                "Execution-only negative control: the defect is in the code, not the formulation. "
                "Reframing is the wrong move."
            ),
        ),
    ],
}


def generate_cases_for_family(
    family: TaskFamily,
    count: int,
    start_id: int,
    seed_base: int = 0,
) -> list[dict]:
    """Generate cases for a specific family."""
    templates = TEMPLATES.get(family, [])
    if not templates:
        raise ValueError(f"No templates found for family {family}")

    cases = []
    for i in range(count):
        case_id = f"p1-c{start_id + i}"
        # Cycle through templates
        template = templates[i % len(templates)]

        # Generate parameters (in a real implementation, this would use
        # more sophisticated parameter generation)
        params = generate_params_for_template(template, i, seed_base + i)

        case = template.generate(case_id, params, seed_base + i)
        cases.append(case)

    return cases


def generate_params_for_template(template: CaseTemplate, index: int, seed: int) -> dict:
    """Generate parameters for a template.

    This is a placeholder. In a real implementation, this would:
    1. Use a large database of scenario variations
    2. Ensure coherence across all parameters
    3. Avoid repetition across cases

    For now, return placeholder params that would need manual review.
    """
    # Placeholder - in real use, this would pull from a curated scenario database
    return {
        "placeholder": "REQUIRES_MANUAL_REVIEW",
        "index": index,
        "seed": seed,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", choices=[f.value for f in TaskFamily], help="Task family")
    parser.add_argument("--count", type=int, help="Number of cases to generate")
    parser.add_argument("--start", type=int, default=149, help="Starting case ID")
    parser.add_argument("--all", action="store_true", help="Generate all 337 cases")
    parser.add_argument("--out", type=Path, default=OUTPUT_ROOT, help="Output directory")
    args = parser.parse_args(argv)

    if args.all:
        # Generate all 337 cases: 56 per family
        all_cases = []
        start_id = 149
        for family in TaskFamily:
            cases = generate_cases_for_family(family, 56, start_id)
            all_cases.extend(cases)
            start_id += 56

        # Write all cases
        args.out.mkdir(parents=True, exist_ok=True)
        for case in all_cases:
            case_file = args.out / f"{case['case_id']}.json"
            case_file.write_text(json.dumps(case, indent=2) + "\n")

        print(f"Generated {len(all_cases)} cases in {args.out}")
        return 0

    if args.family and args.count:
        family = TaskFamily(args.family)
        cases = generate_cases_for_family(family, args.count, args.start)

        # Write cases
        args.out.mkdir(parents=True, exist_ok=True)
        for case in cases:
            case_file = args.out / f"{case['case_id']}.json"
            case_file.write_text(json.dumps(case, indent=2) + "\n")

        print(f"Generated {len(cases)} cases for {family.value} in {args.out}")
        return 0

    parser.error("Must specify --family with --count, or --all")


if __name__ == "__main__":
    raise SystemExit(main())
