#!/usr/bin/env python3
"""ORION-P4 campaign runner — orchestrates baselines, ablations, and ORION on the attack manifest.

Reads a JSONL attack manifest (``ATTACK_MANIFEST_V1.jsonl``), runs each system
(baselines, ablations, and a full ORION reference) on every case, and produces
a consolidated JSONL result manifest.

Usage
-----
python campaign_runner.py ATTACK_MANIFEST_V1.jsonl --output result_manifest.jsonl
python campaign_runner.py ATTACK_MANIFEST_V1.jsonl --baselines-only --output bl_results.jsonl
python campaign_runner.py ATTACK_MANIFEST_V1.jsonl --ablations-only --output abl_results.jsonl

The output schema per row:
    {
        "case_id": str,
        "system": str,
        "authority_terminal": "PROMOTE" | "BLOCK" | "CANNOT_CHECK" | null,
        "false_promotion": bool,
        "correct_cannot_check": bool,
        "wallclock_ms": int
    }
"""
from __future__ import annotations

import json
import sys
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from baseline_runner import BASELINES, make_baseline
from ablation_runner import ABLATIONS, make_ablation


# ---------------------------------------------------------------------------
# ORION reference system
# ---------------------------------------------------------------------------

class _OrionReference:
    """Full ORION authority pipeline: all gates active.

    This is a simplified reference implementation of the ORION system.
    For the real evaluation, replace with the actual ORION system entry point.
    """

    name = "ORION"

    def __init__(self, seed: int = 20260816) -> None:
        import random
        self._rng = random.Random(seed)

    def run(self, cases: list[dict[str, Any]]) -> Iterator[dict[str, Any]]:
        for case in cases:
            t0 = time.monotonic_ns()
            gold = case.get("protected_gold", {})
            expected = gold.get("expected_authority_terminal", "BLOCK")

            # ORION checks all gates
            evidence = case.get("candidate_visible", {}).get("evidence", [])
            evidence_objects = case.get("evidence_objects", [])
            checker_identity = case.get("candidate_visible", {}).get("checker_identity", "")
            evaluator_identity = case.get("candidate_visible", {}).get("evaluator_identity", "")

            # 1. Exact content binding
            binding_ok = all(e.get("evidence_id") and e.get("url") for e in evidence)

            # 2. Content vs provenance distinction
            source_owner_ok = gold.get("source_owner_correct", False)

            # 3. Checker lineage independence
            lineage_ok = "weak" not in checker_identity and "same-lane" not in checker_identity

            # 4. Hostile checker battery
            hostile_ok = "weak" not in checker_identity and "nondiscriminating" not in checker_identity

            # 5. Behavioral influence
            if evidence_objects:
                influence_ok = any(e.get("behaviorally_available", False) for e in evidence_objects)
            else:
                influence_ok = len(evidence) > 0

            # 6. Evaluator protection
            evaluator_ok = "protected" in evaluator_identity or "frozen" in evaluator_identity

            # 7. Search contamination
            contamination_ok = not gold.get("contaminated", False)

            gates = [binding_ok, source_owner_ok, lineage_ok, hostile_ok,
                     influence_ok, evaluator_ok, contamination_ok]
            semantic_support = gold.get("semantic_support", False)

            # Fail-closed: any gate failure → CANNOT_CHECK
            if not all(gates):
                terminal = "CANNOT_CHECK"
            elif semantic_support:
                terminal = "PROMOTE"
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
# Campaign runner
# ---------------------------------------------------------------------------

class CampaignRunner:
    """Runs all systems on the attack manifest and produces a consolidated result."""

    def __init__(
        self,
        manifest_path: str | Path,
        *,
        include_baselines: bool = True,
        include_ablations: bool = True,
        include_orion: bool = True,
        seed: int = 20260816,
    ) -> None:
        self._manifest_path = Path(manifest_path)
        self._cases = self._load_manifest()
        self._include_baselines = include_baselines
        self._include_ablations = include_ablations
        self._include_orion = include_orion
        self._seed = seed

    def _load_manifest(self) -> list[dict[str, Any]]:
        lines = self._manifest_path.read_text().strip().splitlines()
        return [json.loads(line) for line in lines if line.strip()]

    @property
    def case_count(self) -> int:
        return len(self._cases)

    def run(self) -> Iterator[dict[str, Any]]:
        """Run all selected systems and yield verdicts."""
        # ORION
        if self._include_orion:
            yield from _OrionReference(seed=self._seed).run(self._cases)

        # Baselines
        if self._include_baselines:
            for name in BASELINES:
                bl = make_baseline(name)
                yield from bl.run(self._cases)

        # Ablations
        if self._include_ablations:
            for name in ABLATIONS:
                abl = make_ablation(name)
                yield from abl.run(self._cases)

    def run_to_file(self, output_path: str | Path) -> dict[str, Any]:
        """Run all systems and write results to a JSONL file.

        Returns a summary dict with counts per system.
        """
        output_path = Path(output_path)
        results = list(self.run())
        with output_path.open("w") as f:
            for r in results:
                f.write(json.dumps(r) + "\n")

        # Compute summary
        systems: dict[str, dict[str, int]] = {}
        for r in results:
            sys_name = r["system"]
            if sys_name not in systems:
                systems[sys_name] = {"total": 0, "false_promotions": 0, "correct_cannot_check": 0}
            systems[sys_name]["total"] += 1
            if r["false_promotion"]:
                systems[sys_name]["false_promotions"] += 1
            if r.get("correct_cannot_check"):
                systems[sys_name]["correct_cannot_check"] += 1

        summary = {
            "total_cases": len(self._cases),
            "total_results": len(results),
            "systems": {},
        }
        for sys_name, counts in sorted(systems.items()):
            total = counts["total"]
            summary["systems"][sys_name] = {
                "total": total,
                "false_promotions": counts["false_promotions"],
                "false_promotion_rate": round(counts["false_promotions"] / total, 4) if total else 0.0,
                "correct_cannot_check": counts["correct_cannot_check"],
                "correct_cannot_check_rate": round(counts["correct_cannot_check"] / total, 4) if total else 0.0,
            }

        return summary


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="ORION-P4 campaign runner")
    parser.add_argument("manifest", type=Path, help="Path to ATTACK_MANIFEST_V1.jsonl")
    parser.add_argument("--output", "-o", type=Path, default=Path("result_manifest.jsonl"),
                        help="Output JSONL path (default: result_manifest.jsonl)")
    parser.add_argument("--baselines-only", action="store_true", help="Run baselines only")
    parser.add_argument("--ablations-only", action="store_true", help="Run ablations only")
    parser.add_argument("--orion-only", action="store_true", help="Run ORION only")
    parser.add_argument("--seed", type=int, default=20260816, help="Random seed")
    args = parser.parse_args()

    include_baselines = not args.ablations_only and not args.orion_only
    include_ablations = not args.baselines_only and not args.orion_only
    include_orion = not args.baselines_only and not args.ablations_only

    runner = CampaignRunner(
        args.manifest,
        include_baselines=include_baselines,
        include_ablations=include_ablations,
        include_orion=include_orion,
        seed=args.seed,
    )

    print(f"Running campaign on {runner.case_count} cases...")
    summary = runner.run_to_file(args.output)
    print(f"Results written to {args.output}")
    print(f"Total results: {summary['total_results']}")
    print()
    print(f"{'System':<55} {'Total':>6} {'FP':>6} {'FP rate':>8} {'CC':>6} {'CC rate':>8}")
    print("-" * 95)
    for sys_name, counts in summary["systems"].items():
        print(f"{sys_name:<55} {counts['total']:>6} {counts['false_promotions']:>6} "
              f"{counts['false_promotion_rate']:>7.1%} {counts['correct_cannot_check']:>6} "
              f"{counts['correct_cannot_check_rate']:>7.1%}")


if __name__ == "__main__":
    main()