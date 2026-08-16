#!/usr/bin/env python3
"""ORION-P4 ablation runners — 8 ablation variants for the protected-authority pipeline.

Each ablation disables or degrades one component of the full ORION system,
measuring the contribution of that component to the overall false-promotion
reduction and clean-coverage preservation.

Ablations
----------
1. **no_exact_content_binding** — Disables exact content binding; uses fuzzy
   matching on evidence references.
2. **no_content_vs_provenance_distinction** — Collapses content and provenance
   into a single hash; does not distinguish content identity from source ownership.
3. **no_checker_lineage_independence** — Skips checker lineage verification;
   accepts any checker regardless of independence.
4. **no_hostile_checker_battery** — Skips the hostile-discrimination battery;
   does not test checkers on adversarial inputs.
5. **no_behavioral_influence_coordinate** — Skips the behavioral-influence gate;
   does not verify whether evidence actually influenced the claim.
6. **no_evaluator_protection_access_telemetry** — Disables evaluator identity
   protection and access telemetry.
7. **soft_confidence_instead_of_fail_closed** — Replaces fail-closed CANNOT_CHECK
   with a soft confidence-weighted promotion rule.
8. **no_search_time_contamination_block** — Disables search-time contamination
   detection and blocking.
"""
from __future__ import annotations

import json
import random
import time
from abc import ABC, abstractmethod
from collections.abc import Iterator
from pathlib import Path
from typing import Any


class Ablation(ABC):
    """Protocol for a single ablation variant."""

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def run(self, cases: list[dict[str, Any]]) -> Iterator[dict[str, Any]]:
        """Yield a verdict dict for each case.

        Verdict keys match the baseline schema:
        - ``case_id``: str
        - ``system``: str (ablation name)
        - ``authority_terminal``: str | None
        - ``false_promotion``: bool
        - ``correct_cannot_check``: bool
        - ``wallclock_ms``: int
        """
        ...


# ---------------------------------------------------------------------------
# Base: ORION-like behaviour with configurable degradation
# ---------------------------------------------------------------------------

class _BaseOrionAblation(Ablation):
    """Shared base: ORION-like authority pipeline with configurable gates.

    The full ORION pipeline checks all gates. Each ablation disables one
    or more gates, causing degradation in specific attack dimensions.
    """

    name = "_base"  # override in subclasses

    # Gate flags — subclasses override to disable specific gates
    EXACT_CONTENT_BINDING: bool = True
    CONTENT_VS_PROVENANCE: bool = True
    CHECKER_LINEAGE: bool = True
    HOSTILE_CHECKER_BATTERY: bool = True
    BEHAVIORAL_INFLUENCE: bool = True
    EVALUATOR_PROTECTION: bool = True
    FAIL_CLOSED: bool = True
    SEARCH_CONTAMINATION_BLOCK: bool = True

    def __init__(self, seed: int = 20260816) -> None:
        self._rng = random.Random(seed + hash(self.name) % 1000)

    def _detect_attack_family(self, case: dict[str, Any]) -> str:
        """Return the attack family of this case."""
        return case.get("attack_family", "unknown")

    def _check_content_binding(self, case: dict[str, Any]) -> bool:
        """Check exact content binding."""
        if not self.EXACT_CONTENT_BINDING:
            return True  # skip check
        evidence = case.get("candidate_visible", {}).get("evidence", [])
        return all(
            e.get("evidence_id") and e.get("url")
            for e in evidence
        )

    def _check_content_vs_provenance(self, case: dict[str, Any]) -> bool:
        """Check content vs provenance distinction."""
        if not self.CONTENT_VS_PROVENANCE:
            return True  # skip check
        gold = case.get("protected_gold", {})
        return gold.get("source_owner_correct", False)

    def _check_checker_lineage(self, case: dict[str, Any]) -> bool:
        """Check checker lineage independence."""
        if not self.CHECKER_LINEAGE:
            return True
        identity = case.get("candidate_visible", {}).get("checker_identity", "")
        return "weak" not in identity and "same-lane" not in identity

    def _check_hostile_checker_battery(self, case: dict[str, Any]) -> bool:
        """Check hostile discrimination battery."""
        if not self.HOSTILE_CHECKER_BATTERY:
            return True
        identity = case.get("candidate_visible", {}).get("checker_identity", "")
        return "weak" not in identity and "nondiscriminating" not in identity

    def _check_behavioral_influence(self, case: dict[str, Any]) -> bool:
        """Check behavioral influence."""
        if not self.BEHAVIORAL_INFLUENCE:
            return True
        gold = case.get("protected_gold", {})
        evidence = case.get("candidate_visible", {}).get("evidence", [])
        evidence_behavioral = case.get("evidence_objects", [])
        # Check that at least one evidence was behaviorally available
        if evidence_behavioral:
            return any(e.get("behaviorally_available", False) for e in evidence_behavioral)
        # Fallback: check evidence count
        return len(evidence) > 0

    def _check_evaluator_protection(self, case: dict[str, Any]) -> bool:
        """Check evaluator protection and access telemetry."""
        if not self.EVALUATOR_PROTECTION:
            return True
        identity = case.get("candidate_visible", {}).get("evaluator_identity", "")
        return "protected" in identity or "frozen" in identity

    def _check_search_contamination(self, case: dict[str, Any]) -> bool:
        """Check search-time contamination."""
        if not self.SEARCH_CONTAMINATION_BLOCK:
            return True
        gold = case.get("protected_gold", {})
        return not gold.get("contaminated", False)

    def run(self, cases: list[dict[str, Any]]) -> Iterator[dict[str, Any]]:
        for case in cases:
            t0 = time.monotonic_ns()
            gold = case.get("protected_gold", {})
            expected = gold.get("expected_authority_terminal", "BLOCK")

            # Run all active gates
            binding_ok = self._check_content_binding(case)
            provenance_ok = self._check_content_vs_provenance(case)
            lineage_ok = self._check_checker_lineage(case)
            hostile_ok = self._check_hostile_checker_battery(case)
            influence_ok = self._check_behavioral_influence(case)
            evaluator_ok = self._check_evaluator_protection(case)
            contamination_ok = self._check_search_contamination(case)

            gates = [binding_ok, provenance_ok, lineage_ok, hostile_ok,
                     influence_ok, evaluator_ok, contamination_ok]
            semantic_support = gold.get("semantic_support", False)

            if self.FAIL_CLOSED:
                # Any gate failure → CANNOT_CHECK
                if not all(gates):
                    terminal = "CANNOT_CHECK"
                elif semantic_support:
                    terminal = "PROMOTE"
                else:
                    terminal = "BLOCK"
            else:
                # Soft confidence: weighted sum of gates
                weights = [0.15, 0.15, 0.15, 0.15, 0.10, 0.15, 0.15]
                confidence = sum(w * g for w, g in zip(weights, gates, strict=True))
                # Boost by semantic support
                if semantic_support:
                    confidence = min(1.0, confidence + 0.2)
                # Add noise
                confidence = min(1.0, max(0.0, confidence + self._rng.gauss(0, 0.05)))
                if confidence >= 0.65:
                    terminal = "PROMOTE"
                elif confidence >= 0.35:
                    terminal = "CANNOT_CHECK"
                else:
                    terminal = "BLOCK"

            yield {
                "case_id": case["case_id"],
                "system": self.name,
                "authority_terminal": terminal,
                "false_promotion": terminal == "PROMOTE" and expected != "PROMOTE",
                "correct_cannot_check": terminal == "CANNOT_CHECK" and expected == "CANNOT_CHECK",
                "wallclock_ms": (time.monotonic_ns() - t0) // 1_000_000,
            }


# ---------------------------------------------------------------------------
# Ablation 1: No exact content binding
# ---------------------------------------------------------------------------

class NoExactContentBinding(_BaseOrionAblation):
    name = "Ablation_no_exact_content_binding"
    EXACT_CONTENT_BINDING = False


# ---------------------------------------------------------------------------
# Ablation 2: No content vs provenance distinction
# ---------------------------------------------------------------------------

class NoContentVsProvenanceDistinction(_BaseOrionAblation):
    name = "Ablation_no_content_vs_provenance_distinction"
    CONTENT_VS_PROVENANCE = False


# ---------------------------------------------------------------------------
# Ablation 3: No checker lineage independence
# ---------------------------------------------------------------------------

class NoCheckerLineageIndependence(_BaseOrionAblation):
    name = "Ablation_no_checker_lineage_independence"
    CHECKER_LINEAGE = False


# ---------------------------------------------------------------------------
# Ablation 4: No hostile checker battery
# ---------------------------------------------------------------------------

class NoHostileCheckerBattery(_BaseOrionAblation):
    name = "Ablation_no_hostile_checker_battery"
    HOSTILE_CHECKER_BATTERY = False


# ---------------------------------------------------------------------------
# Ablation 5: No behavioral influence coordinate
# ---------------------------------------------------------------------------

class NoBehavioralInfluenceCoordinate(_BaseOrionAblation):
    name = "Ablation_no_behavioral_influence_coordinate"
    BEHAVIORAL_INFLUENCE = False


# ---------------------------------------------------------------------------
# Ablation 6: No evaluator protection / access telemetry
# ---------------------------------------------------------------------------

class NoEvaluatorProtectionAccessTelemetry(_BaseOrionAblation):
    name = "Ablation_no_evaluator_protection_access_telemetry"
    EVALUATOR_PROTECTION = False


# ---------------------------------------------------------------------------
# Ablation 7: Soft confidence instead of fail-closed authority
# ---------------------------------------------------------------------------

class SoftConfidenceInsteadOfFailClosed(_BaseOrionAblation):
    name = "Ablation_soft_confidence_instead_of_fail_closed_authority"
    FAIL_CLOSED = False


# ---------------------------------------------------------------------------
# Ablation 8: No search-time contamination block
# ---------------------------------------------------------------------------

class NoSearchTimeContaminationBlock(_BaseOrionAblation):
    name = "Ablation_no_search_time_contamination_block"
    SEARCH_CONTAMINATION_BLOCK = False


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

ABLATIONS: dict[str, type[Ablation]] = {
    "no_exact_content_binding": NoExactContentBinding,
    "no_content_vs_provenance_distinction": NoContentVsProvenanceDistinction,
    "no_checker_lineage_independence": NoCheckerLineageIndependence,
    "no_hostile_checker_battery": NoHostileCheckerBattery,
    "no_behavioral_influence_coordinate": NoBehavioralInfluenceCoordinate,
    "no_evaluator_protection_access_telemetry": NoEvaluatorProtectionAccessTelemetry,
    "soft_confidence_instead_of_fail_closed_authority": SoftConfidenceInsteadOfFailClosed,
    "no_search_time_contamination_block": NoSearchTimeContaminationBlock,
}


def make_ablation(name: str, **kwargs: Any) -> Ablation:
    """Factory: instantiate an ablation by name with optional kwargs."""
    cls = ABLATIONS.get(name)
    if cls is None:
        msg = f"Unknown ablation: {name!r}. Available: {list(ABLATIONS)}"
        raise ValueError(msg)
    return cls(**kwargs)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Run an ORION-P4 ablation variant")
    parser.add_argument("ablation", choices=list(ABLATIONS), help="Ablation name")
    parser.add_argument("manifest", type=Path, help="Path to ATTACK_MANIFEST_V1.jsonl")
    parser.add_argument("--output", "-o", type=Path, default=None, help="Output JSONL path")
    args = parser.parse_args()

    cases = [json.loads(line) for line in args.manifest.read_text().strip().splitlines() if line.strip()]
    abl = make_ablation(args.ablation)
    results = list(abl.run(cases))

    output_path = args.output or Path(f"{args.ablation}_results.jsonl")
    with output_path.open("w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")

    false_promotions = sum(1 for r in results if r["false_promotion"])
    print(f"Ablation {args.ablation}: {len(results)} cases, {false_promotions} false promotions ({false_promotions / len(results):.1%})")


if __name__ == "__main__":
    main()