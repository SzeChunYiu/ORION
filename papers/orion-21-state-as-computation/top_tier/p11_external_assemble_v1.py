#!/usr/bin/env python3
"""P11 external campaign — final-analysis input assembler (post-run, rule-frozen).

Builds ORION.A2.P11ExternalResultInput.v1 for analyze_p11_external_final_v1.py from:
  results/PROTECTED_RUNLINES.jsonl   per-(benchmark|pool|qid|lane|arm) outcomes
  results/ORACLE_LINES.json          hindsight oracle (analysis-only arm)
  receipts/TUNING_FREEZE_V1.json     dev evidence (pre-outcome)
  receipts/EXECUTION_MANIFEST_V1.json GREEN-sealed manifest

PRE-REGISTERED RULES (frozen in this file before any protected outcome):
  candidate = COMPILED_QUERY_CONDITIONED_STATE (fixed by hypothesis).
  single strongest-baseline id for the final gate = pooled-development winner:
    among the frozen baseline-set arms that are STRUCTURALLY EXECUTABLE on every
    protected cell (estimated prompt tokens within each lane's context limit —
    a mechanical pre-outcome property), pick max mean dev quality pooled over
    BOTH benchmarks' development registries (as recorded in TUNING_FREEZE_V1
    dev evidence), ties -> lower pooled mean charged -> lexicographic arm id.
    Per-benchmark LOBO selections remain recorded in the tuning freeze; the
    final gate's single-id contract is satisfied by this pooled-dev rule, which
    uses no protected outcome.
  block_id = "{benchmark}|{pool}|{qid}|{lane}" (unique); model_family_id = the
  lane's family class. All 10 arms must be present per block; the hindsight
  oracle enters as analysis-only and can never be candidate or baseline.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

BASE = Path(os.environ.get("P11_BASE", str(Path.home() / "orion-p11-campaign")))
RESULTS = BASE / "results"
RECEIPTS = BASE / "receipts"

HERE = Path(__file__).resolve().parent
import validate_p11_external_execution_manifest_v1 as VAL  # noqa: E402
import p11_external_arms_v1 as ARMS  # noqa: E402

CANDIDATE = "COMPILED_QUERY_CONDITIONED_STATE"
BASELINE_SET = ["HYBRID_DENSE_BM25_RERANK", "FULL_CONTEXT_NO_RETRIEVAL",
                "REASON_ONLY", "STATE_RETRIEVAL_ONLY"]
FAMILY = {"gpt-5.5-codexcli": "GPT_CLASS", "claude-fable-5-cli": "CLAUDE_OR_GEMINI_CLASS",
          "llama3.1-8b-ollama": "OPEN_WEIGHT"}


def H_file(p: Path) -> str:
    import hashlib
    return hashlib.sha256(p.read_bytes()).hexdigest()


def pooled_dev_winner(tuning: dict) -> tuple[str, dict]:
    """Pooled-dev baseline selection among structurally executable arms."""
    evidence = {}
    for bench in ("LONGMEMEVAL_CLEANED", "LONGMEMEVAL_V2"):
        ev = tuning["tuned"][bench]["dev_evidence"]
        for arm in BASELINE_SET:
            e = evidence.setdefault(arm, {"qualities": [], "charged": []})
            e["qualities"].append(ev["baseline_dev_quality"][arm])
            e["charged"].append(ev["baseline_dev_mean_charged"][arm])
    # structural executability: FULL_CONTEXT needs whole-haystack in context on
    # every protected cell; other baseline-set arms retrieve small selections.
    # The estimate mirrors the arms module's own FULL_CONTEXT formula exactly.
    executable = {a: True for a in BASELINE_SET}
    lines = [json.loads(l) for l in (RESULTS / "PROTECTED_RUNLINES.jsonl").read_text().splitlines() if l.strip()]
    v1_qids = sorted({r["qid"] for r in lines if r["benchmark"] == "LONGMEMEVAL_CLEANED"})
    v2_present = any(r["benchmark"] == "LONGMEMEVAL_V2" for r in lines)
    over = ARMS.FULL_CONTEXT_OVERHEAD_TOKENS
    if v2_present:
        executable["FULL_CONTEXT_NO_RETRIEVAL"] = False  # ~45M-token corpora
    if v1_qids:
        import p11_external_blocks_v1 as BL
        recs = BL.v1_records()
        for qid in v1_qids:
            b = BL.v1_block(recs[qid])
            full = "\n".join(b["chunks"])
            est = (len(full) + len(b["question"])) // 4 + over
            if any(est > lim for lim in ARMS.LANE_CONTEXT_TOKENS.values()):
                executable["FULL_CONTEXT_NO_RETRIEVAL"] = False
                break
    stats = {}
    for arm, e in evidence.items():
        stats[arm] = (sum(e["qualities"]) / len(e["qualities"]),
                      sum(e["charged"]) / len(e["charged"]))
    best = min(sorted(a for a in BASELINE_SET if executable[a]),
               key=lambda a: (-stats[a][0], stats[a][1], a))
    detail = {a: {"executable": executable[a], "pooled_dev_quality": stats[a][0],
                  "pooled_dev_mean_charged": stats[a][1]} for a in BASELINE_SET}
    return best, detail


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.parse_args()

    manifest_fp = RECEIPTS / "EXECUTION_MANIFEST_V1.json"
    manifest = json.loads(manifest_fp.read_text())
    VAL.validate(manifest)  # must still be GREEN
    tuning = json.loads((RECEIPTS / "TUNING_FREEZE_V1.json").read_text())
    baseline, baseline_detail = pooled_dev_winner(tuning)

    lines = [json.loads(l) for l in (RESULTS / "PROTECTED_RUNLINES.jsonl").read_text().splitlines() if l.strip()]
    oracle = json.loads((RESULTS / "ORACLE_LINES.json").read_text())
    oracle_by = {(o["benchmark"], o["pool"], o["qid"], o["lane"]): o for o in oracle}

    cells: dict[tuple, dict[str, dict]] = defaultdict(dict)
    meta = {}
    for r in lines:
        key = (r["benchmark"], r["pool"], r["qid"], r["lane"])
        cells[key][r["arm"]] = {"quality": r.get("score"),
                                "total_charged_cost": round(float(r.get("charged", 0.0)) + 1e-9, 6),
                                "cannot_check_reason": r.get("cannot_check_reason")}
        meta[key] = {"benchmark": r["benchmark"], "model_family_id": FAMILY[r["lane"]]}
    blocks = []
    for key in sorted(cells):
        bench, pool, qid, lane = key
        m = cells[key]
        o = oracle_by.get(key)
        m["HINDSIGHT_ORACLE_ANALYSIS_ONLY"] = {
            "quality": o.get("score") if o else None,
            "total_charged_cost": round(float((o or {}).get("charged", 0.0)) + 1e-9, 6),
            "cannot_check_reason": (o or {}).get("cannot_check_reason")}
        blocks.append({"block_id": f"{bench}|{pool}|{qid}|{lane}",
                       "benchmark": bench,
                       "model_family_id": meta[key]["model_family_id"],
                       "arm_metrics": {a: m.get(a, {"quality": None, "total_charged_cost": 1e-9,
                                                     "cannot_check_reason": "missing runline"})
                                       for a in VAL.ARMS}})
    packet = {"schema": "ORION.A2.P11ExternalResultInput.v1",
              "protected_outcomes_unsealed": True,
              "candidate_and_baseline_selected_before_protected_scoring": True,
              "candidate_arm_id": CANDIDATE,
              "strongest_baseline_arm_id": baseline,
              "execution_manifest_validation_sha256": H_file(manifest_fp),
              "blocks": blocks}
    out = RESULTS / "FINAL_ANALYSIS_INPUT_V1.json"
    out.write_text(json.dumps(packet, indent=2, sort_keys=True))
    print(json.dumps({"out": str(out), "blocks": len(blocks),
                      "candidate": CANDIDATE, "baseline": baseline,
                      "baseline_selection": baseline_detail}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
