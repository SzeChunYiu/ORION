"""End-to-end evaluation runner for ORION Paper 3.

Command-line entry point for the P3 evaluation protocol:

    python -m orion.study.evaluate \
        --gold <gold.json> \
        --output <results_dir> \
        [--seeds 0 1 2 3 4]

Pipeline per (system, seed):
  1. Load gold annotations (P3.cross-domain-atlas.v1 schema).
  2. Run the system (full ORION, one of the 6 baselines, or one of the
     8 ablations) over each case to produce integration results.
  3. Score against gold with orion.study.metrics.compute_all_metrics.
  4. Aggregate runs (bootstrap CI across seeds).
  5. Emit a normalized RESULT_RECORD_SCHEMA_V1.json-compliant record.

The full model-backed run (prompting the frozen model family) is the executor's
job; this runner supplies the deterministic shell: schema, orchestration,
scoring, aggregation, and record emission. Systems that are not yet bound to a
model backend record status=INVALID with a failure_class explaining why.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Sequence

from orion.study import statistics as stats
from orion.study.ablations import ALL_ABLATIONS
from orion.study.baselines import (
    ALL_BASELINES,
    Baseline,
    IntegrationResult,
    SourceDocument,
)

# The full ORION system is registered at runtime via --systems.
FULL_SYSTEM_ID = "ORION_FULL"

RESULT_SCHEMA_VERSION = "orion.publication-result-record.v1"
MANIFEST_SCHEMA_VERSION = "orion.run-manifest.v1"

ALL_SYSTEM_IDS: list[str] = [FULL_SYSTEM_ID] + [b.system_id() for b in ALL_BASELINES] + [
    a.system_id() for a in ALL_ABLATIONS
]


# ── gold loading ──────────────────────────────────────────────────────────────

def load_gold(path: str | Path) -> list[dict[str, object]]:
    """Load gold annotations from a JSON file.

    Accepts either:
      - a list of annotation dicts (P3 annotation schema), or
      - an object {"annotations": [...]}.
    """
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("annotations"), list):
        return payload["annotations"]
    raise ValueError(f"Unrecognized gold file shape: {path}")


def _to_source_documents(case: dict[str, object]) -> tuple[SourceDocument, ...]:
    """Convert a gold case's source documents into SourceDocument tuples."""
    sources = case.get("sources")
    if sources is None:
        # Fallback: extract any 'source_a'/'source_b' text fields directly.
        sources = []
        for key in ("source_a", "source_b"):
            if key in case:
                text = str(case[key])
                sources.append({
                    "document_id": f"{key}",
                    "document_version": "v1",
                    "text": text,
                    "discipline": str(case.get("discipline", "")),
                })
        if not sources:
            raise ValueError(f"Gold case has no sources: {case.get('case_id', '?')}")
    return tuple(
        SourceDocument(
            document_id=str(d.get("document_id", f"doc_{i}")),
            document_version=str(d.get("document_version", "v1")),
            text=str(d.get("text", "")),
            discipline=str(d.get("discipline", "")),
            span_start=int(d.get("span_start", 0)),
            span_end=int(d.get("span_end", 0)),
            text_hash=str(d.get("text_hash", "")),
        )
        for i, d in enumerate(sources)
    )


# ── run orchestration ─────────────────────────────────────────────────────────

def _run_system(system: Baseline, case: dict[str, object],
                seed: int) -> IntegrationResult:
    """Run a system over a single gold case and return its integration result."""
    sources = _to_source_documents(case)
    # The IntegrationResult has a frozen dataclass; we carry the seed in notes.
    base = system.integrate(sources)
    seed_note = f"seed={seed}" if base.notes else f"RUN seed={seed}"
    return IntegrationResult(
        system_id=base.system_id,
        case_id=str(case.get("case_id", "?")),
        mapping_relation=base.mapping_relation,
        referent_relation=base.referent_relation,
        construct_relation=base.construct_relation,
        measurement_relation=base.measurement_relation,
        context_relation=base.context_relation,
        polarity_relation=base.polarity_relation,
        modality_relation=base.modality_relation,
        attribution_relation=base.attribution_relation,
        discourse_relation=base.discourse_relation,
        contradiction_verdict=base.contradiction_verdict,
        integration_verdict=base.integration_verdict,
        preservation_conditions=base.preservation_conditions,
        recoverability_target=base.recoverability_target,
        notes=base.notes + (" | " + seed_note if base.notes else seed_note),
    )


def _prediction_dict(result: IntegrationResult) -> dict[str, object]:
    """Serialize an IntegrationResult to a plain dict for metric scoring."""
    d = asdict(result)
    d.pop("case_id", None)
    d.pop("system_id", None)
    d.pop("notes", None)
    # Convert tuples to lists for JSON compatibility and metric access.
    for key, val in d.items():
        if isinstance(val, tuple):
            d[key] = list(val)
    return d


def evaluate_system_once(
    gold: Sequence[dict[str, object]],
    system: Baseline,
    seed: int,
) -> tuple[list[dict[str, object]], dict[str, float]]:
    """Run one system over gold for one seed; returns (preds, metrics)."""
    preds = [_prediction_dict(_run_system(system, case, seed)) for case in gold]
    return preds, compute_flat_metrics(gold, preds)


def compute_flat_metrics(
    gold: Sequence[dict[str, object]],
    preds: Sequence[dict[str, object]],
) -> dict[str, float]:
    """Compute all P3 metrics, returning a flat dict of metric_name -> float."""
    from orion.study.metrics import compute_all_metrics
    return compute_all_metrics(gold, preds)


# ── result record emission ────────────────────────────────────────────────────

def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _record_for(
    system_id: str,
    task_id: str,
    metadata: dict[str, object],
    metrics: dict[str, float],
    status: str = "PASS",
    failure_class: str | None = None,
    raw_text: str = "",
) -> dict[str, object]:
    """Build a normalized result record per RESULT_RECORD_SCHEMA_V1.json."""
    cost_values = {
        "wallclock_seconds": float(metadata.get("wallclock_seconds", 0)),
        "model_tokens": float(metadata.get("model_tokens", 0)),
        "tool_calls": float(metadata.get("tool_calls", 0)),
        "reported_currency_cost": float(metadata.get("reported_currency_cost", 0)),
    }
    return {
        "schema_version": RESULT_SCHEMA_VERSION,
        "paper_id": "P3",
        "protocol_id": "P3.cross-domain-atlas.v1",
        "run_manifest_hash": metadata.get("run_manifest_hash", ""),
        "result_id": f"P3-{system_id}-{task_id}-{metadata.get('seed', 0)}",
        "system_id": system_id,
        "task_id": task_id,
        "task_family": metadata.get("task_family", ""),
        "seed": int(metadata.get("seed", 0)),
        "status": status,
        "metrics": {k: float(v) for k, v in metrics.items()},
        "cost": cost_values,
        "failure_class": failure_class,
        "raw_artifact_hash": _sha256_hex(raw_text.encode("utf-8")),
        "notes": metadata.get("notes", ""),
    }


# ── manifest ──────────────────────────────────────────────────────────────────

def build_manifest(systems: list[str], seeds: list[int],
                   gold_path: str | Path) -> dict[str, object]:
    """Build the run manifest for this evaluation run."""
    gold_text = Path(gold_path).read_text(encoding="utf-8")
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "paper_id": "P3",
        "protocol_id": "P3.cross-domain-atlas.v1",
        "systems": systems,
        "seeds": seeds,
        "gold_hash": _sha256_hex(gold_text.encode("utf-8")),
        "resource_policy": {
            "frozen_model_family": "deepseek-v4-pro",
            "context_budget_per_case": "TBD",
            "retrieval_allowance": "TBD",
        },
    }


# ── CLI ───────────────────────────────────────────────────────────────────────

def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="orion.study.evaluate",
        description="ORION Paper 3 evaluation runner",
    )
    parser.add_argument("--gold", required=True, type=Path,
                        help="Path to gold annotations JSON")
    parser.add_argument("--output", required=True, type=Path,
                        help="Output directory for result records")
    parser.add_argument("--systems", nargs="*", default=ALL_SYSTEM_IDS,
                        help="Which systems to evaluate (default: all)")
    parser.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2, 3, 4],
                        help="Stochastic seeds (default: 0 1 2 3 4)")
    parser.add_argument("--sample", type=int, default=0,
                        help="If >0, only evaluate the first N gold cases "
                             "(for smoke tests).")
    args = parser.parse_args(argv)

    gold = load_gold(args.gold)
    if args.sample > 0:
        gold = gold[: args.sample]

    args.output.mkdir(parents=True, exist_ok=True)

    # Registry: full ORION + baselines + ablations.
    systems: dict[str, Baseline] = {b.system_id(): b for b in ALL_BASELINES}
    systems.update({a.system_id(): a for a in ALL_ABLATIONS})
    # A stub for the full ORION system — replaced by the executor's actual
    # implementation. Without a registered backend it records INVALID.
    from orion.study.baselines import IntegrationResult as _IR, SourceDocument as _SD
    class _FullOrion(Baseline):
        def system_id(self) -> str:
            return FULL_SYSTEM_ID
        def integrate(self, sources: Sequence[SourceDocument]) -> IntegrationResult:
            return _IR(system_id=FULL_SYSTEM_ID, case_id="",
                       notes="ORION_FULL_NOT_YET_BOUND")
    systems.setdefault(FULL_SYSTEM_ID, _FullOrion())

    manifest = build_manifest(list(systems.keys()), args.seeds, args.gold)
    manifest_hash = _sha256_hex(json.dumps(manifest, sort_keys=True).encode("utf-8"))
    manifest["run_manifest_hash"] = manifest_hash
    (args.output / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")

    records: list[dict[str, object]] = []
    for sys_id in args.systems:
        system = systems.get(sys_id)
        if system is None:
            print(f"SKIP unknown system: {sys_id}", file=sys.stderr)
            continue
        run_metrics: list[dict[str, float]] = []
        for seed in args.seeds:
            status = "PASS"
            failure_class = None
            try:
                _, metrics = evaluate_system_once(gold, system, seed)
            except NotImplementedError as exc:  # Model backend not bound.
                status = "INVALID"
                failure_class = f"MODEL_BACKEND_UNBOUND: {exc}"
                metrics = {}
            except Exception as exc:
                status = "INVALID"
                failure_class = f"{type(exc).__name__}: {exc}"
                metrics = {}
            run_metrics.append(metrics)
            record = _record_for(
                sys_id,
                task_id="cross-domain-atlas-v1",
                metadata={"seed": seed, "task_family": "cross-domain-atlas",
                          "run_manifest_hash": manifest_hash,
                          "wallclock_seconds": 0.0, "model_tokens": 0,
                          "notes": f"case_families={len(gold)}"
                          },
                metrics=metrics,
                status=status,
                failure_class=failure_class,
                raw_text=f"{sys_id}|{seed}",
            )
            # If a model backend is present, this record would be written per
            # (system, seed); we keep it in-memory to aggregate below.
            records.append(record)

    # Aggregate across seeds per system.
    per_system: dict[str, list[dict[str, float]]] = {}
    for rec in records:
        if rec["status"] == "PASS":
            per_system.setdefault(str(rec["system_id"]), []).append(
                dict(rec["metrics"]))
    aggregates: dict[str, dict[str, dict[str, float]]] = {}
    for sys_id, run_metrics in per_system.items():
        aggregates[sys_id] = stats.aggregate_across_runs(run_metrics)

    (args.output / "aggregates.json").write_text(
        json.dumps(aggregates, indent=2), encoding="utf-8")
    (args.output / "results.jsonl").write_text(
        "\n".join(json.dumps(r, sort_keys=True) for r in records) + "\n",
        encoding="utf-8")

    # Print a summary table to stdout.
    header = f"{'system':<28}{'seeds':>6}  {'fm_rate':>9}  {'vi_rate':>9}"
    print(header)
    print("-" * len(header))
    for sys_id in sorted(per_system):
        agg = aggregates[sys_id].get("false_merge_rate", {})
        vi = aggregates[sys_id].get("valid_integration_rate", {})
        fm_mean = agg.get("mean", float("nan"))
        vi_mean = vi.get("mean", float("nan"))
        n = agg.get("n_runs", 0)
        print(f"{sys_id:<28}{int(n):>6}  {fm_mean:>9.4f}  {vi_mean:>9.4f}")
    print(f"\n{n_ok(records)}/{len(records)} records PASS; "
          f"outputs written to {args.output}")
    return 0


def n_ok(records: Sequence[dict[str, object]]) -> int:
    return sum(1 for r in records if r.get("status") == "PASS")


if __name__ == "__main__":
    raise SystemExit(main())