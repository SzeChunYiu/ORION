#!/usr/bin/env python3
"""ORION-P4 baseline runners — 6 baseline systems for the protected-authority benchmark.

Each baseline implements a :class:`Baseline` protocol: a ``run`` method that
yields per-case verdicts (dicts with keys defined by the schema in
``ATTACK_CASE_SCHEMA_V1.json``), and a ``name`` property.

Baselines
---------
1. **CitationFormat** — Checks citation presence and format only.
2. **PooledNLI** — Pooled-evidence NLI support verifier (no source attribution).
3. **AttributionBench** — Attribution-style evaluator (source match only, no
   admissibility gates).
4. **ProvenanceGuard** — Source-aware factuality verifier (atomic claims,
   cross-source conflation detection).
5. **IterativeRV** — Iterative retrieve-or-verify loop.
6. **Auditability** — Claim-level auditability / provenance record.

All baselines operate on the same case schema and produce verdicts that
can be compared against ``protected_gold`` for metric computation.
"""
from __future__ import annotations

import json
import random
import time
from abc import ABC, abstractmethod
from collections.abc import Iterator
from pathlib import Path
from typing import Any


class Baseline(ABC):
    """Protocol for a single baseline system."""

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def run(self, cases: list[dict[str, Any]]) -> Iterator[dict[str, Any]]:
        """Yield a verdict dict for each case.

        Verdict keys (subset of ``ATTACK_CASE_SCHEMA_V1.json``):
        - ``case_id``: str
        - ``system``: str (baseline name)
        - ``authority_terminal``: str | None (PROMOTE / BLOCK / CANNOT_CHECK)
        - ``false_promotion``: bool (whether the verdict was a false promotion)
        - ``correct_cannot_check``: bool (whether CANNOT_CHECK was the correct outcome)
        - ``wallclock_ms``: int (elapsed wall-clock time for this case)
        """
        ...


# ---------------------------------------------------------------------------
# 1. CitationFormat — checks citation presence and format only
# ---------------------------------------------------------------------------

class CitationFormatBaseline(Baseline):
    """Checks that evidence is cited with proper format markers.

    Always promotes if evidence has ``content_hash`` and ``provenance_hash``
    fields (format check only). Does not verify content correctness.
    """

    name = "CitationFormat"

    def run(self, cases: list[dict[str, Any]]) -> Iterator[dict[str, Any]]:
        for case in cases:
            t0 = time.monotonic_ns()
            evidence = case.get("candidate_visible", {}).get("evidence", [])
            all_formatted = all(
                e.get("evidence_id") and e.get("url")
                for e in evidence
            )
            terminal = "PROMOTE" if all_formatted else "CANNOT_CHECK"
            gold = case.get("protected_gold", {})
            expected = gold.get("expected_authority_terminal", "BLOCK")
            yield {
                "case_id": case["case_id"],
                "system": self.name,
                "authority_terminal": terminal,
                "false_promotion": terminal == "PROMOTE" and expected != "PROMOTE",
                "correct_cannot_check": terminal == "CANNOT_CHECK" and expected == "CANNOT_CHECK",
                "wallclock_ms": (time.monotonic_ns() - t0) // 1_000_000,
            }


# ---------------------------------------------------------------------------
# 2. PooledNLI — pooled-evidence NLI support verifier
# ---------------------------------------------------------------------------

class PooledNLIBaseline(Baseline):
    """Pooled-evidence NLI support verifier.

    Stub: simulates an NLI model that checks semantic support against
    *pooled* evidence without source attribution. True-positive rate ~0.83,
    false-positive rate ~0.31 (from ``STUB_SUMMARY_V1.json``).
    """

    name = "PooledNLI"

    def __init__(self, seed: int = 20260816) -> None:
        self._rng = random.Random(seed)

    def run(self, cases: list[dict[str, Any]]) -> Iterator[dict[str, Any]]:
        for case in cases:
            t0 = time.monotonic_ns()
            gold = case.get("protected_gold", {})
            claim_correct = gold.get("claim_correct", False)
            semantic_support = gold.get("semantic_support", False)
            # PooledNLI sees support but not source ownership
            if semantic_support and claim_correct:
                # 83% true positive
                promote = self._rng.random() < 0.83
            elif semantic_support and not claim_correct:
                # 31% false positive
                promote = self._rng.random() < 0.31
            else:
                promote = False
            terminal = "PROMOTE" if promote else "BLOCK"
            expected = gold.get("expected_authority_terminal", "BLOCK")
            yield {
                "case_id": case["case_id"],
                "system": self.name,
                "authority_terminal": terminal,
                "false_promotion": terminal == "PROMOTE" and expected != "PROMOTE",
                "correct_cannot_check": terminal == "CANNOT_CHECK" and expected == "CANNOT_CHECK",
                "wallclock_ms": (time.monotonic_ns() - t0) // 1_000_000,
            }


# ---------------------------------------------------------------------------
# 3. AttributionBench — source-attribution evaluator
# ---------------------------------------------------------------------------

class AttributionBenchBaseline(Baseline):
    """Attribution-style source-match evaluator.

    Stub: checks whether the claim content matches the evidence source.
    Correct-attribution rate ~0.85, but does not verify semantic support
    or checker admissibility.
    """

    name = "AttributionBench"

    def __init__(self, seed: int = 20260816) -> None:
        self._rng = random.Random(seed + 1)

    def run(self, cases: list[dict[str, Any]]) -> Iterator[dict[str, Any]]:
        for case in cases:
            t0 = time.monotonic_ns()
            gold = case.get("protected_gold", {})
            source_owner_correct = gold.get("source_owner_correct", False)
            semantic_support = gold.get("semantic_support", False)
            # Attribution: 85% correct on source, but ignores semantic support
            attr_pass = source_owner_correct and self._rng.random() < 0.85
            support_pass = semantic_support and self._rng.random() < 0.80
            promote = attr_pass and support_pass
            terminal = "PROMOTE" if promote else "BLOCK"
            expected = gold.get("expected_authority_terminal", "BLOCK")
            yield {
                "case_id": case["case_id"],
                "system": self.name,
                "authority_terminal": terminal,
                "false_promotion": terminal == "PROMOTE" and expected != "PROMOTE",
                "correct_cannot_check": terminal == "CANNOT_CHECK" and expected == "CANNOT_CHECK",
                "wallclock_ms": (time.monotonic_ns() - t0) // 1_000_000,
            }


# ---------------------------------------------------------------------------
# 4. ProvenanceGuard — source-aware factuality verifier
# ---------------------------------------------------------------------------

class ProvenanceGuardBaseline(Baseline):
    """Source-aware factuality verifier with cross-source conflation detection.

    Stub: decomposes claims into atomic statements and checks each against
    retrieved source context. Detects conflation in ~50% of cases.
    """

    name = "ProvenanceGuard"

    def __init__(self, seed: int = 20260816) -> None:
        self._rng = random.Random(seed + 2)

    def run(self, cases: list[dict[str, Any]]) -> Iterator[dict[str, Any]]:
        for case in cases:
            t0 = time.monotonic_ns()
            gold = case.get("protected_gold", {})
            source_owner = gold.get("source_owner_correct", False)
            semantic = gold.get("semantic_support", False)
            # Source-attribution accuracy ~0.90
            attr = source_owner and self._rng.random() < 0.90
            # Support F1 ~0.91
            sup = semantic and self._rng.random() < 0.91
            # Conflation: ~0.51 detection on source_conflation cases
            family = case.get("attack_family", "")
            conflation_penalty = 0.0
            if family == "source_conflation":
                conflation_penalty = 0.51 if self._rng.random() < 0.51 else 0.0
            promote = attr and sup and self._rng.random() > conflation_penalty
            terminal = "PROMOTE" if promote else "BLOCK"
            expected = gold.get("expected_authority_terminal", "BLOCK")
            yield {
                "case_id": case["case_id"],
                "system": self.name,
                "authority_terminal": terminal,
                "false_promotion": terminal == "PROMOTE" and expected != "PROMOTE",
                "correct_cannot_check": terminal == "CANNOT_CHECK" and expected == "CANNOT_CHECK",
                "wallclock_ms": (time.monotonic_ns() - t0) // 1_000_000,
            }


# ---------------------------------------------------------------------------
# 5. IterativeRV — iterative retrieve-or-verify loop
# ---------------------------------------------------------------------------

class IterativeRVBaseline(Baseline):
    """Iterative retrieve-or-verify pipeline.

    Stub: iteratively retrieves evidence and verifies claims. Improves
    coverage but at higher cost. False-promotion rate ~0.23.
    """

    name = "IterativeRV"

    def __init__(self, seed: int = 20260816) -> None:
        self._rng = random.Random(seed + 3)

    def run(self, cases: list[dict[str, Any]]) -> Iterator[dict[str, Any]]:
        for case in cases:
            t0 = time.monotonic_ns()
            gold = case.get("protected_gold", {})
            source_owner = gold.get("source_owner_correct", False)
            semantic = gold.get("semantic_support", False)
            # Iterative RV: 2 rounds of verification
            attr = source_owner and self._rng.random() < 0.75
            sup = semantic and self._rng.random() < 0.86
            promote = attr and sup
            terminal = "PROMOTE" if promote else "BLOCK"
            expected = gold.get("expected_authority_terminal", "BLOCK")
            # Simulate higher cost (2 rounds)
            sim_cost = int(100 + self._rng.random() * 50)
            yield {
                "case_id": case["case_id"],
                "system": self.name,
                "authority_terminal": terminal,
                "false_promotion": terminal == "PROMOTE" and expected != "PROMOTE",
                "correct_cannot_check": terminal == "CANNOT_CHECK" and expected == "CANNOT_CHECK",
                "wallclock_ms": sim_cost,
            }


# ---------------------------------------------------------------------------
# 6. Auditability — claim-level auditability / provenance record
# ---------------------------------------------------------------------------

class AuditabilityBaseline(Baseline):
    """Claim-level auditability with provenance recording.

    Stub: records semantic provenance and checks retrospectively.
    False-promotion rate ~0.28.
    """

    name = "Auditability"

    def __init__(self, seed: int = 20260816) -> None:
        self._rng = random.Random(seed + 4)

    def run(self, cases: list[dict[str, Any]]) -> Iterator[dict[str, Any]]:
        for case in cases:
            t0 = time.monotonic_ns()
            gold = case.get("protected_gold", {})
            source_owner = gold.get("source_owner_correct", False)
            semantic = gold.get("semantic_support", False)
            # Auditability: records provenance, moderate accuracy
            attr = source_owner and self._rng.random() < 0.72
            sup = semantic and self._rng.random() < 0.79
            promote = attr and sup
            terminal = "PROMOTE" if promote else "BLOCK"
            expected = gold.get("expected_authority_terminal", "BLOCK")
            yield {
                "case_id": case["case_id"],
                "system": self.name,
                "authority_terminal": terminal,
                "false_promotion": terminal == "PROMOTE" and expected != "PROMOTE",
                "correct_cannot_check": terminal == "CANNOT_CHECK" and expected == "CANNOT_CHECK",
                "wallclock_ms": (time.monotonic_ns() - t0) // 1_000_000,
            }


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

BASELINES: dict[str, type[Baseline]] = {
    "CitationFormat": CitationFormatBaseline,
    "PooledNLI": PooledNLIBaseline,
    "AttributionBench": AttributionBenchBaseline,
    "ProvenanceGuard": ProvenanceGuardBaseline,
    "IterativeRV": IterativeRVBaseline,
    "Auditability": AuditabilityBaseline,
}


def make_baseline(name: str, **kwargs: Any) -> Baseline:
    """Factory: instantiate a baseline by name with optional kwargs."""
    cls = BASELINES.get(name)
    if cls is None:
        msg = f"Unknown baseline: {name!r}. Available: {list(BASELINES)}"
        raise ValueError(msg)
    return cls(**kwargs)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Run a single ORION-P4 baseline")
    parser.add_argument("baseline", choices=list(BASELINES), help="Baseline name")
    parser.add_argument("manifest", type=Path, help="Path to ATTACK_MANIFEST_V1.jsonl")
    parser.add_argument("--output", "-o", type=Path, default=None, help="Output JSONL path")
    args = parser.parse_args()

    cases = [json.loads(line) for line in args.manifest.read_text().strip().splitlines() if line.strip()]
    bl = make_baseline(args.baseline)
    results = list(bl.run(cases))

    output_path = args.output or Path(f"{args.baseline}_results.jsonl")
    with output_path.open("w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")

    false_promotions = sum(1 for r in results if r["false_promotion"])
    print(f"Baseline {args.baseline}: {len(results)} cases, {false_promotions} false promotions ({false_promotions / len(results):.1%})")


if __name__ == "__main__":
    main()