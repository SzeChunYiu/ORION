#!/usr/bin/env python3
"""P11 external campaign — protected run (primary + fresh registries, all lanes).

Runs the 9 non-oracle frozen arms over every protected block:

  LONGMEMEVAL_CLEANED  primary 8 questions, fresh 8 questions (per-question haystacks)
  LONGMEMEVAL_V2       primary 4 web questions, fresh 4 enterprise questions
  lanes                gpt-5.5-codexcli, claude-fable-5-cli, llama3.1-8b-ollama

Arm order within a block: deterministic SHA-256 ordering per block
(arm_order_rule = SHA256_DETERMINISTIC_PER_SESSION), applied identically on every
lane. Resumable: one JSONL line per (benchmark, pool, qid, lane, arm); reruns skip
lines already present. Outcomes (answers, scores) are only written by this runner
and only after the manifest-bound inputs (tuning freeze, revealed registry,
compilation receipt) exist.

Accounting (frozen; see manifest accounting block):
  per-arm charged = PRICE_IN*in + PRICE_OUT*out + PRICE_EMBED*query_embeds
                    + PRICE_SPARSE*indexed_tokens
  + amortized compilation share (state-using arms; per source over its blocks)
  + amortized dense-precompute share (dense arms; per source over its blocks)
  The hindsight oracle is assembled AFTER arm outcomes by --finalize (analysis-only).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import resource
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BASE = Path(os.environ.get("P11_BASE", str(Path.home() / "orion-p11-campaign")))
RESULTS = BASE / "results"
RECEIPTS = BASE / "receipts"

from p11_external_arms_v1 import (ARMS, ArmContext, charged_cost, run_arm,  # noqa: E402
                                  LANE_CONTEXT_TOKENS)
import p11_external_blocks_v1 as BL  # noqa: E402
from p11_external_judge_v1 import score, JUDGE_LEDGER  # noqa: E402

LANES = ("gpt-5.5-codexcli", "claude-fable-5-cli", "llama3.1-8b-ollama")
NON_ORACLE_ARMS = [a for a in ARMS if a != "HINDSIGHT_ORACLE_ANALYSIS_ONLY"]
STATE_USING_ARMS = {"COMPILED_QUERY_CONDITIONED_STATE", "STATE_RETRIEVAL_ONLY",
                    "FIXED_STATE_REASON_SPLITS", "SIMPLE_UNCERTAINTY_ROUTING",
                    "CURRENT_ADAPTIVE_ALLOCATOR"}
N_THREADS = int(os.environ.get("P11_RUN_THREADS", "6"))


def H(x: str) -> str:
    return hashlib.sha256(x.encode()).hexdigest()


def arm_order(block_key: str) -> list[str]:
    return sorted(NON_ORACLE_ARMS, key=lambda a: H(f"{block_key}|{a}"))


def load_inputs() -> tuple[dict, dict, dict]:
    import validate_p11_external_execution_manifest_v1 as VAL
    manifest = json.loads((RECEIPTS / "EXECUTION_MANIFEST_V1.json").read_text())
    VAL.validate(manifest)  # seal: refuse to run unless the manifest is GREEN
    tuning = json.loads((RECEIPTS / "TUNING_FREEZE_V1.json").read_text())
    registry = json.loads((RECEIPTS / "REGISTRY_FREEZE_V1.json").read_text())
    states = BL.load_states()
    return tuning, registry, states


def protected_blocks(registry: dict) -> list[dict]:
    out = []
    v1, v2 = registry["benchmarks"]["LONGMEMEVAL_CLEANED"], registry["benchmarks"]["LONGMEMEVAL_V2"]
    recs = BL.v1_records()
    for pool in ("primary_registry", "fresh_query_registry"):
        for qid in v1[pool]["question_ids"]:
            b = BL.v1_block(recs[qid])
            b["pool"] = "primary" if pool.startswith("primary") else "fresh"
            out.append(b)
    qs = BL.v2_questions()
    corpora = BL.V2Corpora()
    for pool, dom in (("primary_registry", "web"), ("fresh_query_registry", "enterprise")):
        ids = v2[pool]["question_ids"]
        corpus_ids = corpora.corpus_ids(ids)
        for qid in ids:
            b = corpora.block(qs[qid], dom, corpus_ids)
            b["pool"] = "primary" if pool.startswith("primary") else "fresh"
            out.append(b)
    return out


def compile_amortization() -> dict[str, float]:
    """Charged compilation cost per source; divided by its block count by caller."""
    receipt = json.loads((RECEIPTS / "COMPILATION_RECEIPT_V1.json").read_text())
    from p11_external_arms_v1 import PRICE_IN, PRICE_OUT
    cin = receipt["compile_input_tokens"]
    cout = receipt["compile_output_tokens"]
    total = PRICE_IN * cin + PRICE_OUT * cout
    per_src = receipt.get("per_source_compile_tokens", {})
    out = {"__total__": round(total, 3)}
    for src, rec in per_src.items():
        out[src] = round(PRICE_IN * rec["in"] + PRICE_OUT * rec["out"], 3)
    if not per_src:
        n = len(receipt.get("state_files", {})) or 1
        share = total / n
        for src in receipt.get("state_files", {}):
            out[src] = round(share, 3)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lanes", default=",".join(LANES))
    ap.add_argument("--finalize", action="store_true",
                    help="assemble oracle + aggregate run lines into PROTECTED_RESULTS_V1.json")
    a = ap.parse_args()
    RESULTS.mkdir(parents=True, exist_ok=True)
    lanes = [l for l in a.lanes.split(",") if l]

    if a.finalize:
        return finalize()

    tuning, registry, states = load_inputs()
    blocks = protected_blocks(registry)
    print(f"protected blocks: {len(blocks)}; lanes: {lanes}", flush=True)
    comp_amort = compile_amortization()
    block_counts: dict[str, int] = {}
    for b in blocks:
        block_counts[b["source_key"]] = block_counts.get(b["source_key"], 0) + 1

    runlines = RESULTS / "PROTECTED_RUNLINES.jsonl"
    done = set()
    if runlines.exists():
        for line in runlines.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                done.add((r["benchmark"], r["pool"], r["qid"], r["lane"], r["arm"]))

    jobs = []
    for b in blocks:
        b["_state_text"] = BL.state_for(states, b["source_key"])
        b["_dense"] = None
    # dense precompute per unique source (v1: per block; V2: per corpus)
    for b in blocks:
        if b["_dense"] is None:
            try:
                di = BL.get_dense_index(b["source_key"], b["chunks"])
                for b2 in blocks:
                    if b2["source_key"] == b["source_key"]:
                        b2["_dense"] = di
                print(f"dense ready {b['source_key']} n={di['n']} tok={di['embedded_tokens']}",
                      flush=True)
            except Exception as exc:  # noqa: BLE001
                print(f"dense FAILED {b['source_key']}: {exc}", flush=True)

    params_by_bench = {"LONGMEMEVAL_CLEANED": tuning["tuned"]["LONGMEMEVAL_CLEANED"]["params"],
                       "LONGMEMEVAL_V2": tuning["tuned"]["LONGMEMEVAL_V2"]["params"]}
    for b in blocks:
        for lane in lanes:
            for arm in arm_order(f"{b['benchmark']}|{b['pool']}|{b['qid']}"):
                key = (b["benchmark"], b["pool"], b["qid"], lane, arm)
                if key in done:
                    continue
                jobs.append((b, lane, arm))
    print(f"pending arm-runs: {len(jobs)}", flush=True)

    def one(job):
        b, lane, arm = job
        params = dict(params_by_bench[b["benchmark"]])
        if arm == "LEARNED_JOINT_ALLOCATOR_DEV_ONLY":
            params["_router_weights"] = tuning["tuned"][b["benchmark"]]["router_weights"]
        ctx = ArmContext(b, lane, params, b["_state_text"], b["chunks"], b["_dense"])
        t0 = time.time()
        try:
            res = run_arm(arm, ctx)
        except Exception as exc:  # noqa: BLE001
            res = {"answer": None, "cannot_check_reason": f"runner error: {exc}"[:300]}
        rv = dict(ctx.rv)
        rv["indexed_tokens"] = ctx.indexed_tokens
        rv["peak_memory_bytes"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
        rv["state_construction_time_ms"] = 0  # compiled pre-run; amortized below
        sc = score(b["benchmark"], b, res.get("answer"))
        charged = charged_cost(rv, rv.get("embedded_query_tokens", 0))
        if arm in STATE_USING_ARMS or (arm == "LEARNED_JOINT_ALLOCATOR_DEV_ONLY"
                                       and res.get("router_action") in ("state", "split")):
            charged += comp_amort.get(b["source_key"], comp_amort["__total__"]) / \
                max(1, block_counts[b["source_key"]])
        if arm == "HYBRID_DENSE_BM25_RERANK" or (
                arm == "LEARNED_JOINT_ALLOCATOR_DEV_ONLY" and res.get("router_action") == "hybrid"):
            di = b["_dense"]
            if di:
                from p11_external_arms_v1 import PRICE_EMBED
                charged += PRICE_EMBED * di["embedded_tokens"] / max(1, block_counts[b["source_key"]])
        rec = {"benchmark": b["benchmark"], "pool": b["pool"], "qid": b["qid"],
               "question_type": b.get("question_type", ""), "lane": lane, "arm": arm,
               "answer": res.get("answer"),
               "cannot_check_reason": res.get("cannot_check_reason") or sc.get("cannot_check_reason"),
               "router_action": res.get("router_action"), "score": sc["score"],
               "judge": sc.get("judge"), "rv": rv,
               "charged": round(charged, 3),
               "wall_total_ms": int((time.time() - t0) * 1000)}
        return rec

    n = 0
    with ThreadPoolExecutor(max_workers=N_THREADS) as ex:
        for rec in ex.map(one, jobs):
            with open(runlines, "a") as f:
                f.write(json.dumps(rec) + "\n")
            n += 1
            if n % 25 == 0:
                print(f"completed {n}/{len(jobs)}", flush=True)
    print(f"DONE protected arm-runs: {n} (skipped {len(done)})", flush=True)
    print("judge ledger:", json.dumps(JUDGE_LEDGER), flush=True)
    return 0


def finalize() -> int:
    """Assemble hindsight oracle + per-arm aggregates -> PROTECTED_RESULTS_V1.json."""
    lines = [json.loads(l) for l in (RESULTS / "PROTECTED_RUNLINES.jsonl").read_text().splitlines() if l.strip()]
    oracle_lines = []
    for (bench, pool, qid, lane), grp in _group(lines, ("benchmark", "pool", "qid", "lane")):
        scored = [r for r in grp if r.get("score") is not None]
        if not scored:
            oracle_lines.append({"benchmark": bench, "pool": pool, "qid": qid, "lane": lane,
                                 "arm": "HINDSIGHT_ORACLE_ANALYSIS_ONLY", "score": None,
                                 "cannot_check_reason": "no scoreable arm in cell",
                                 "charged": 0.0})
            continue
        best_q = max(r["score"] for r in scored)
        cands = [r for r in scored if r["score"] == best_q]
        best = min(cands, key=lambda r: r["charged"])
        oracle_lines.append({"benchmark": bench, "pool": pool, "qid": qid, "lane": lane,
                             "arm": "HINDSIGHT_ORACLE_ANALYSIS_ONLY", "score": best_q,
                             "oracle_quality_arm": best["arm"],
                             "oracle_cheapest_charged": best["charged"],
                             "charged": best["charged"],
                             "cannot_check_reason": None})
    out = {"schema": "ORION.A2.P11ProtectedResults.v1",
           "n_runlines": len(lines), "n_oracle_lines": len(oracle_lines),
           "judge_ledger": JUDGE_LEDGER,
           "runlines_file": "PROTECTED_RUNLINES.jsonl"}
    (RESULTS / "ORACLE_LINES.json").write_text(json.dumps(oracle_lines, indent=2))
    (RESULTS / "PROTECTED_RESULTS_V1.json").write_text(json.dumps(out, indent=2))
    print(json.dumps({"runlines": len(lines), "oracle": len(oracle_lines)}, indent=2))
    return 0


def _group(lines: list[dict], keys: tuple[str, ...]) -> dict[tuple, list[dict]]:
    out: dict[tuple, list[dict]] = {}
    for r in lines:
        out.setdefault(tuple(r[k] for k in keys), []).append(r)
    return out


if __name__ == "__main__":
    sys.exit(main())
