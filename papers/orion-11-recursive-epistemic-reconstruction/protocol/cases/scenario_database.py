#!/usr/bin/env python3
"""
P1 Scenario Database — Managed inventory of case scenarios per family.

This module provides:
1. Scenario catalog structure for each task family
2. Deduplication keys to prevent repetitive cases
3. Family balance tracking
4. Schema conformance validation

Usage:
    from scenario_database import ScenarioDatabase
    db = ScenarioDatabase()
    db.add_scenario(...)
    db.validate_balance()
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Literal


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
    EVIDENCE = "EVIDENCE"
    EXECUTION = "EXECUTION"


@dataclass
class DedupKey:
    """Keys for detecting duplicate scenarios."""

    # Core scenario concept (what problem is being solved?)
    scenario_concept: str
    # Domain/context (e.g., "causal inference in A/B testing")
    domain_context: str
    # Specific mechanic (e.g., "pre-period confounding")
    specific_mechanic: str


@dataclass
class ScenarioSlot:
    """A scenario slot is a unique case scenario waiting to be authored."""

    family: TaskFamily
    responsibility_family: ResponsibilityFamily
    dedup_key: DedupKey
    title: str  # Human-readable title for tracking
    status: Literal["draft", "authored", "reviewed", "approved"] = "draft"
    authored_case_id: str | None = None  # e.g., "p1-c149"

    def to_dict(self) -> dict:
        return {
            "family": self.family.value,
            "responsibility_family": self.responsibility_family.value,
            "dedup_key": {
                "scenario_concept": self.dedup_key.scenario_concept,
                "domain_context": self.dedup_key.domain_context,
                "specific_mechanic": self.dedup_key.specific_mechanic,
            },
            "title": self.title,
            "status": self.status,
            "authored_case_id": self.authored_case_id,
        }


@dataclass
class ScenarioDatabase:
    """Managed inventory of scenario slots across all families."""

    slots: list[ScenarioSlot] = field(default_factory=list)

    def add_slot(self, slot: ScenarioSlot) -> None:
        """Add a scenario slot after deduplication check."""
        # Check for duplicates
        for existing in self.slots:
            if (
                existing.dedup_key.scenario_concept == slot.dedup_key.scenario_concept
                and existing.dedup_key.domain_context == slot.dedup_key.domain_context
                and existing.dedup_key.specific_mechanic == slot.dedup_key.specific_mechanic
            ):
                raise ValueError(
                    f"Duplicate scenario: {slot.title} shares dedup key with {existing.title}"
                )
        self.slots.append(slot)

    def count_by_family(self, family: TaskFamily | None = None) -> dict[str, int]:
        """Count slots by family."""
        if family:
            return {family.value: sum(1 for s in self.slots if s.family == family)}
        return {
            f.value: sum(1 for s in self.slots if s.family == f)
            for f in TaskFamily
        }

    def count_by_status(self, status: str) -> int:
        """Count slots by status."""
        return sum(1 for s in self.slots if s.status == status)

    def get_slots_for_family(self, family: TaskFamily) -> list[ScenarioSlot]:
        """Get all slots for a family."""
        return [s for s in self.slots if s.family == family]

    def validate_balance(self, target_n: int, tolerance: float = 0.1) -> dict:
        """
        Validate family balance within tolerance.

        Returns dict with balance status and any imbalances.
        """
        counts = self.count_by_family()
        target_per_family = target_n // len(TaskFamily)

        imbalances = {}
        for f in TaskFamily:
            count = counts.get(f.value, 0)
            if abs(count - target_per_family) / target_per_family > tolerance:
                imbalances[f.value] = {
                    "current": count,
                    "target": target_per_family,
                    "deviation_pct": (count - target_per_family) / target_per_family * 100,
                }

        return {
            "balanced": len(imbalances) == 0,
            "target_per_family": target_per_family,
            "imbalances": imbalances,
        }

    def to_json(self, path: Path) -> None:
        """Export database to JSON."""
        data = {
            "slots": [slot.to_dict() for slot in self.slots],
            "summary": {
                "total": len(self.slots),
                "by_family": self.count_by_family(),
                "by_status": {
                    status: self.count_by_status(status)
                    for status in ["draft", "authored", "reviewed", "approved"]
                },
            },
        }
        path.write_text(json.dumps(data, indent=2) + "\n")


# TARGET DISTRIBUTIONS for each stage
STAGE_TARGETS = {
    "TIER_D": 97,  # Current 48 + 51 new
    "TIER_C": 171,  # TIER_D + 74 new
    "TIER_B": 385,  # TIER_C + 214 new
}

TARGET_PER_FAMILY = {
    "TIER_D": 97 // 6,  # 16 per family (1 family gets 17)
    "TIER_C": 171 // 6,  # 28 per family (3 families get 29)
    "TIER_B": 385 // 6,  # 64 per family (1 family gets 65)
}


__all__ = [
    "TaskFamily",
    "ResponsibilityFamily",
    "DedupKey",
    "ScenarioSlot",
    "ScenarioDatabase",
    "STAGE_TARGETS",
    "TARGET_PER_FAMILY",
]
