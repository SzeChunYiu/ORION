#!/usr/bin/env python3
"""
P1 Case Validator — Schema conformance and quality checks.

Validates authored cases against:
1. HIDDEN_SHIFT_CASE_SCHEMA_V1.json schema
2. Family balance requirements
3. Deduplication (scenario concept overlap)
4. Rubric invariants (PASS/IFF criteria well-formed)

Usage:
    python3 validate_cases.py --case-dir test_expanded/ --check schema
    python3 validate_cases.py --case-dir test_expanded/ --check all
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Literal


class CheckType(str, Enum):
    """Types of validation checks."""

    SCHEMA = "schema"
    BALANCE = "balance"
    DEDUP = "dedup"
    RUBRIC = "rubric"
    ALL = "all"


@dataclass
class ValidationError:
    """A validation error for a specific case."""

    case_id: str
    check_type: CheckType
    message: str
    severity: Literal["error", "warning"] = "error"


@dataclass
class ValidationResult:
    """Result of running validation checks."""

    errors: list[ValidationError] = None
    warnings: list[ValidationError] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []

    def add_error(self, case_id: str, check_type: CheckType, message: str) -> None:
        self.errors.append(ValidationError(case_id, check_type, message, "error"))

    def add_warning(self, case_id: str, check_type: CheckType, message: str) -> None:
        self.warnings.append(ValidationError(case_id, check_type, message, "warning"))

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0

    @property
    def total_issues(self) -> int:
        return len(self.errors) + len(self.warnings)


class CaseValidator:
    """Validates P1 cases against schema and quality requirements."""

    def __init__(self, schema_path: Path | None = None):
        # Schema would be loaded from HIDDEN_SHIFT_CASE_SCHEMA_V1.json
        # For now, we'll implement inline checks
        self.required_families = [
            "hidden_parent_domain",
            "hidden_representation_or_coordinate_system",
            "hidden_decomposition_or_interface",
            "hidden_measurement_or_operationalization",
            "evidence_only_negative_control",
            "execution_only_negative_control",
        ]
        self.required_fields = [
            "case_id",
            "task_family",
            "public_prompt",
            "observable_resources",
            "protected_gold",
            "budget_class",
            "adjudication_status",
        ]
        self.required_protected_gold_fields = [
            "reframe_required",
            "responsibility_family",
            "target_coordinates",
            "dependencies_to_reopen",
            "root_success_rubric",
            "dependency_depth",
        ]

    def validate_schema(self, case: dict, case_path: Path) -> ValidationResult:
        """Validate case against HIDDEN_SHIFT_CASE_SCHEMA_V1.json."""
        result = ValidationResult()
        case_id = case.get("case_id", case_path.stem)

        # Check required top-level fields
        for field in self.required_fields:
            if field not in case:
                result.add_error(case_id, CheckType.SCHEMA, f"Missing required field: {field}")

        # Check task_family is valid
        if "task_family" in case and case["task_family"] not in self.required_families:
            result.add_error(
                case_id,
                CheckType.SCHEMA,
                f"Invalid task_family: {case['task_family']}",
            )

        # Check protected_gold structure
        if "protected_gold" in case:
            gold = case["protected_gold"]
            for field in self.required_protected_gold_fields:
                if field not in gold:
                    result.add_error(
                        case_id,
                        CheckType.SCHEMA,
                        f"Missing protected_gold field: {field}",
                    )

            # Check data types
            if "target_coordinates" in gold and not isinstance(gold["target_coordinates"], list):
                result.add_error(
                    case_id,
                    CheckType.SCHEMA,
                    "target_coordinates must be a list",
                )
            if "dependencies_to_reopen" in gold and not isinstance(gold["dependencies_to_reopen"], list):
                result.add_error(
                    case_id,
                    CheckType.SCHEMA,
                    "dependencies_to_reopen must be a list",
                )

        # Check budget_class and adjudication_status values
        if "budget_class" in case and case["budget_class"] != "p1_standard_v1":
            result.add_warning(
                case_id,
                CheckType.SCHEMA,
                f"Unexpected budget_class: {case['budget_class']}",
            )
        if "adjudication_status" in case and case["adjudication_status"] not in [
            "MECHANICAL_GOLD",
            "DOUBLE_ANNOTATED",
            "ADJUDICATED",
            "PILOT_ONLY",
        ]:
            result.add_error(
                case_id,
                CheckType.SCHEMA,
                f"Invalid adjudication_status: {case['adjudication_status']}",
            )

        return result

    def validate_rubric(self, case: dict, case_path: Path) -> ValidationResult:
        """Validate rubric well-formedness."""
        result = ValidationResult()
        case_id = case.get("case_id", case_path.stem)

        if "protected_gold" not in case:
            return result

        rubric = case["protected_gold"].get("root_success_rubric", "")
        if not rubric:
            result.add_error(case_id, CheckType.RUBRIC, "Empty root_success_rubric")
            return result

        # Check for PASS/IFF pattern
        if "PASS iff" not in rubric and "PASS when" not in rubric:
            result.add_warning(
                case_id,
                CheckType.RUBRIC,
                "Rubric should start with 'PASS iff' or 'PASS when'",
            )

        # Check for FAIL condition
        if "FAIL if" not in rubric:
            result.add_warning(
                case_id,
                CheckType.RUBRIC,
                "Rubric should include explicit 'FAIL if' condition",
            )

        # Check rubric length (should be substantive but not verbose)
        rubric_words = len(rubric.split())
        if rubric_words < 20:
            result.add_warning(
                case_id,
                CheckType.RUBRIC,
                f"Rubric seems too short ({rubric_words} words)",
            )
        elif rubric_words > 150:
            result.add_warning(
                case_id,
                CheckType.RUBRIC,
                f"Rubric seems too long ({rubric_words} words) — consider simplifying",
            )

        return result

    def validate_balance(self, cases: list[dict]) -> ValidationResult:
        """Validate family balance."""
        result = ValidationResult()

        # Count by family
        family_counts: dict[str, int] = {}
        for case in cases:
            family = case.get("task_family", "unknown")
            family_counts[family] = family_counts.get(family, 0) + 1

        total = len(cases)
        target_per_family = total // len(self.required_families)
        tolerance = 0.1  # 10% tolerance

        for family in self.required_families:
            count = family_counts.get(family, 0)
            deviation = abs(count - target_per_family) / target_per_family if target_per_family > 0 else 1
            if deviation > tolerance:
                result.add_warning(
                    "balance",
                    CheckType.BALANCE,
                    f"{family}: {count} cases (target: {target_per_family}, deviation: {deviation*100:.1f}%)",
                )

        return result

    def validate_dedup(self, cases: list[dict]) -> ValidationResult:
        """Check for duplicate scenarios based on key fields."""
        result = ValidationResult()

        # Track seen scenario concepts (simplified check)
        seen_concepts: dict[str, str] = {}  # concept -> case_id

        for case in cases:
            case_id = case.get("case_id", "unknown")
            prompt = case.get("public_prompt", "")

            # Extract concept (first sentence, simplified)
            concept = prompt.split(".")[0].strip() if prompt else ""
            if not concept:
                result.add_error(case_id, CheckType.DEDUP, "Empty public_prompt")
                continue

            if concept in seen_concepts:
                result.add_error(
                    case_id,
                    CheckType.DEDUP,
                    f"Duplicate scenario concept with {seen_concepts[concept]}",
                )
            seen_concepts[concept] = case_id

        return result

    def validate_case(self, case_path: Path, checks: set[CheckType]) -> ValidationResult:
        """Validate a single case file."""
        result = ValidationResult()

        try:
            case = json.loads(case_path.read_text())
        except Exception as e:
            result.add_error(case_path.stem, CheckType.SCHEMA, f"Failed to parse: {e}")
            return result

        if CheckType.SCHEMA in checks or CheckType.ALL in checks:
            schema_result = self.validate_schema(case, case_path)
            result.errors.extend(schema_result.errors)
            result.warnings.extend(schema_result.warnings)

        if CheckType.RUBRIC in checks or CheckType.ALL in checks:
            rubric_result = self.validate_rubric(case, case_path)
            result.errors.extend(rubric_result.errors)
            result.warnings.extend(rubric_result.warnings)

        return result

    def validate_directory(
        self,
        case_dir: Path,
        checks: set[CheckType],
    ) -> ValidationResult:
        """Validate all case files in a directory."""
        result = ValidationResult()

        # Load all cases
        cases = []
        for case_file in sorted(case_dir.glob("p1-c*.json")):
            try:
                case = json.loads(case_file.read_text())
                cases.append(case)
            except Exception as e:
                result.add_error(case_file.stem, CheckType.SCHEMA, f"Failed to parse: {e}")

        # Run per-case checks
        for case_file in sorted(case_dir.glob("p1-c*.json")):
            case_result = self.validate_case(case_file, checks)
            result.errors.extend(case_result.errors)
            result.warnings.extend(case_result.warnings)

        # Run aggregate checks
        if CheckType.BALANCE in checks or CheckType.ALL in checks:
            balance_result = self.validate_balance(cases)
            result.errors.extend(balance_result.errors)
            result.warnings.extend(balance_result.warnings)

        if CheckType.DEDUP in checks or CheckType.ALL in checks:
            dedup_result = self.validate_dedup(cases)
            result.errors.extend(dedup_result.errors)
            result.warnings.extend(dedup_result.warnings)

        return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-dir", type=Path, default=Path("test"), help="Directory containing case files")
    parser.add_argument(
        "--check",
        choices=[c.value for c in CheckType],
        default=CheckType.ALL.value,
        help="Type of check to run",
    )
    args = parser.parse_args(argv)

    validator = CaseValidator()
    check_type = CheckType(args.check)
    checks = {check_type} if check_type != CheckType.ALL else set(CheckType)

    result = validator.validate_directory(args.case_dir, checks)

    # Print results
    print(f"Validation complete: {result.total_issues} issues")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Warnings: {len(result.warnings)}")

    if result.errors:
        print("\n=== ERRORS ===")
        for err in result.errors:
            print(f"[{err.case_id}] {err.check_type.value}: {err.message}")

    if result.warnings:
        print("\n=== WARNINGS ===")
        for warn in result.warnings:
            print(f"[{warn.case_id}] {warn.check_type.value}: {warn.message}")

    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
