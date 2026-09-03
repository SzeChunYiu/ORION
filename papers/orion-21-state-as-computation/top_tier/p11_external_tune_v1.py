#!/usr/bin/env python3
"""P11 external campaign — development-only tuning driver (LOBO).

FROZEN BEFORE ANY PROTECTED OUTCOME (this file + TUNING_FREEZE_V1.json predate the
protected run; dev scores below are development, not protected, results):

  tuning lane      gpt-5.5-codexcli (one lane only, recorded)
  candidate arm    COMPILED_QUERY_CONDITIONED_STATE (fixed by hypothesis, not selected)
  baseline set     {HYBRID_DENSE_BM25_RERANK, FULL_CONTEXT_NO_RETRIEVAL, REASON_ONLY,
                    STATE_RETRIEVAL_ONLY} — strongest baseline per target benchmark is
                    selected on the OTHER benchmark's dev registry (LOBO), never on the
                    protected benchmark
  LOBO             params for target benchmark T are tuned ONLY on the other
                    benchmark's development registry
  grids            state_top_k {3,5,8} x state_max_chars {2000,4000,8000} via candidate;
                    rerank_depth {4,8} x top_k {2,4} x chunk_chars {600,900} via hybrid;
                    route_conf_threshold {0.8,1.2,2.0}; alloc_window {8,16} x
                    alloc_state_mult {1.0,1.5} x alloc_budget {2000,4000}
  selection        mean dev quality; ties -> lower mean charged cost -> lexicographically
                    smallest param tuple (fully deterministic)
  router           softmax router trained on dev blocks; label = per-block best action
                    (max quality, tie -> cheapest action); features frozen in arms module

Dev scores are development results; nothing here touches primary/fresh registries.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BASE = Path(os.environ.get("P11_BASE", str(Path.home() / "orion-p11-campaign")))
RECEIPTS = BASE / "receipts"

from p11_external_arms_v1 import (ARMS, ArmContext, charged_cost, run_arm,  # noqa: E402
                                  router_features, router_train, PRICE_IN, PRICE_OUT,
                                  PRICE_EMBED, PRICE_SPARSE)
import p11_external_blocks_v1 as BL  # noqa: E402
import p11_external_registry_builder_v1 as RB  # noqa: E402
from p11_external_judge_v1 import score  # noqa: E402

TUNING_LANE = "gpt-5.5-codexcli"
CANDIDATE = "COMPILED_QUERY_CONDITIONED_STATE"
BASELINE_SET = ["HYBRID_DENSE_BM25_RERANK", "FULL_CONTEXT_NO_RETRIEVAL",
                "REASON_ONLY", "STATE_RETRIEVAL_ONLY"]
STATE_GRID = list(itertools.product([3, 5, 8], [2000, 4000, 8000]))
HYBRID_GRID = list(itertools.product([4, 8], [2, 4], [600, 900]))
ROUTE_GRID = [0.8, 1.2, 2.0]
ALLOC_GRID = list(itertools.product([8, 16], [1.0, 1.5], [2000, 4000]))
N_THREADS = int(os.environ.get("P11_TUNE_THREADS", "8"))


def dev_blocks(benchmark: str, states: dict) -> list[dict]:
    """Assemble the OTHER benchmark's dev registry blocks (LOBO training set)."""
    v1, v2 = RB.build_v1(), RB.build_v2()
    if benchmark == "LONGMEMEVAL_CLEANED":
        # tune v1 params on V2 web dev
        qs = BL.v2_questions()
        corpora = BL.V2Corpora()
        web_ids = v2["development_registry"]["question_ids"]
        corpus_ids = corpora.corpus_ids(web_ids)
        out = []
        for qid in web_ids:
            out.append(corpora.block(qs[qid], "web", corpus_ids))
        return out
    recs = BL.v1_records()
    out = []
    for qid in v1["development_registry"]["question_ids"]:
        out.append(BL.v1_block(recs[qid]))
    return out


def base_params(sp=None, hp=None) -> dict:
    sp = sp or (5, 4000)
    hp = hp or (8, 4, 900)
    return {"state_top_k": sp[0], "state_max_chars": sp[1],
            "rerank_depth": hp[0], "top_k": hp[1], "chunk_chars": hp[2],
            "route_conf_threshold": 1.2, "alloc_window": 8, "alloc_state_mult": 1.0,
            "alloc_p_build": 0.05, "alloc_budget": 2000}


def run_one(arm: str, block: dict, params: dict, state_text: str, dense_index) -> dict:
    t0 = time.time()
    ctx = ArmContext(block, TUNING_LANE, params, state_text, block["chunks"], dense_index)
    try:
        res = run_arm(arm, ctx)
    except Exception as exc:  # noqa: BLE001 — dev-time defect surfaced, not silenced
        res = {"answer": None, "cannot_check_reason": f"dev runner error: {exc}"[:300]}
    res["rv"] = dict(ctx.rv)
    res["rv"]["indexed_tokens"] = ctx.indexed_tokens
    sc = score(block["benchmark"], block, res.get("answer"))
    res["score"] = sc["score"]
    res["cannot_check_reason"] = res.get("cannot_check_reason") or sc.get("cannot_check_reason")
    res["charged"] = round(charged_cost(res["rv"], res["rv"].get("embedded_query_tokens", 0)), 3)
    res["wall_total_ms"] = int((time.time() - t0) * 1000)
    return res


def mean_quality(runs: list[dict]) -> float:
    vals = [r["score"] for r in runs if r.get("score") is not None]
    return sum(vals) / len(vals) if vals else 0.0


def mean_cost(runs: list[dict]) -> float:
    return sum(r.get("charged", 0.0) for r in runs) / max(1, len(runs))


def tune_pass(target: str, states: dict, log) -> dict:
    """Tune on the OTHER benchmark's dev; return params + dev evidence."""
    blocks = dev_blocks(target, states)
    for b in blocks:
        b["_state_text"] = BL.state_for(states, b["source_key"])
    dense_by_block: dict[str, dict] = {}
    for b in blocks:
        try:
            di = BL.get_dense_index(b["source_key"], b["chunks"])
            dense_by_block[b["source_key"]] = di
            log(f"[{target}] dense precompute {di['cache']} src={b['source_key']} "
                f"n={di['n']} emb_tok={di['embedded_tokens']}")
        except Exception as exc:  # noqa: BLE001
            log(f"[{target}] dense precompute FAILED src={b['source_key']}: {exc} "
                f"— hybrid grid runs without dense for this source")

    def sweep(arm, param_fn, grid):
        results = {}
        with ThreadPoolExecutor(max_workers=N_THREADS) as ex:
            futs = {}
            for g in grid:
                params = param_fn(g)
                for b in blocks:
                    futs[ex.submit(run_one, arm, b, params, b["_state_text"],
                                   dense_by_block.get(b["source_key"]))] = (g, b["qid"])
            for fut, (g, qid) in futs.items():
                res = fut.result()
                results.setdefault(g, []).append(res)
        return results

    def pick(results):
        best = None
        for g, runs in sorted(results.items()):
            key = (-mean_quality(runs), mean_cost(runs))
            if best is None or key < best[0]:
                best = (key, g, runs)
        return best[1], best[2]

    # candidate state grid
    state_res = sweep(CANDIDATE, lambda g: base_params(sp=g), STATE_GRID)
    best_sp, cand_runs = pick(state_res)
    log(f"[{target}] best state params {best_sp} q={mean_quality(cand_runs):.3f} "
        f"c={mean_cost(cand_runs):.1f}")
    # hybrid grid (with tuned state params for nothing — hybrid uses own params)
    hyb_res = sweep("HYBRID_DENSE_BM25_RERANK", lambda g: base_params(hp=g), HYBRID_GRID)
    best_hp, hyb_runs = pick(hyb_res)
    log(f"[{target}] best hybrid params {best_hp} q={mean_quality(hyb_runs):.3f}")
    # route threshold (uses tuned state params)
    params0 = base_params(sp=best_sp, hp=best_hp)
    route_res = sweep("SIMPLE_UNCERTAINTY_ROUTING",
                      lambda g: dict(params0, route_conf_threshold=g), ROUTE_GRID)
    best_rt, _ = pick(route_res)
    # allocator grid
    alloc_res = sweep("CURRENT_ADAPTIVE_ALLOCATOR",
                      lambda g: dict(params0, alloc_window=g[0], alloc_state_mult=g[1],
                                     alloc_budget=g[2]), ALLOC_GRID)
    best_ap, _ = pick(alloc_res)
    params = dict(params0, route_conf_threshold=best_rt,
                  alloc_window=best_ap[0], alloc_state_mult=best_ap[1], alloc_budget=best_ap[2])
    # baseline selection on the SAME (other-benchmark) dev
    base_runs = {}
    with ThreadPoolExecutor(max_workers=N_THREADS) as ex:
        futs = {ex.submit(run_one, a, b, params, b["_state_text"],
                          dense_by_block.get(b["source_key"])): a
                for a in BASELINE_SET for b in blocks}
        for fut, a in futs.items():
            base_runs.setdefault(a, []).append(fut.result())
    baseline = min(sorted(BASELINE_SET),
                   key=lambda a: (-mean_quality(base_runs[a]), mean_cost(base_runs[a])))
    log(f"[{target}] strongest baseline (LOBO dev): {baseline} "
        f"q={mean_quality(base_runs[baseline]):.3f}")
    # router training labels: per-block best action
    actions = ("state", "reason", "split", "hybrid")
    action_runs = {}
    with ThreadPoolExecutor(max_workers=N_THREADS) as ex:
        futs = {}
        for b in blocks:
            for act in actions:
                def _run_action(act=act, b=b):
                    ctx = ArmContext(b, TUNING_LANE, params, b["_state_text"],
                                     b["chunks"], dense_by_block.get(b["source_key"]))
                    from p11_external_arms_v1 import (ANSWER_STATE_STRICT_PROMPT, REASON_ONLY_PROMPT,
                                                      SPLIT_DRAFT_PROMPT, SPLIT_REFINE_PROMPT,
                                                      ANSWER_HYBRID_PROMPT)
                    from p11_external_lanes_v1 import call
                    if act == "state":
                        st, _ = ctx.top_state(b["question"], params["state_top_k"],
                                              params["state_max_chars"])
                        rec = call(TUNING_LANE, ANSWER_STATE_STRICT_PROMPT.format(b["question"], st))
                    elif act == "reason":
                        rec = call(TUNING_LANE, REASON_ONLY_PROMPT.format(b["question"]))
                    elif act == "split":
                        st, _ = ctx.top_state(b["question"], params["state_top_k"],
                                              params["state_max_chars"])
                        d = call(TUNING_LANE, SPLIT_DRAFT_PROMPT.format(b["question"], st))
                        draft = ctx._charge_llm(d)
                        rec = call(TUNING_LANE, SPLIT_REFINE_PROMPT.format(b["question"], draft[:4000]))
                    else:
                        ev, _ = ctx.hybrid_retrieve(b["question"])
                        rec = call(TUNING_LANE, ANSWER_HYBRID_PROMPT.format(b["question"], ev))
                    ans = ctx._charge_llm(rec)
                    sc = score(b["benchmark"], b, ans)
                    rv = dict(ctx.rv)
                    rv["indexed_tokens"] = ctx.indexed_tokens
                    return {"act": act, "score": sc["score"],
                            "charged": charged_cost(rv, rv.get("embedded_query_tokens", 0))}
                futs[ex.submit(_run_action)] = b["qid"]
        for fut, qid in futs.items():
            action_runs.setdefault(qid, []).append(fut.result())
    samples = []
    block_by_qid = {b["qid"]: b for b in blocks}
    for qid, runs in sorted(action_runs.items()):
        b = block_by_qid[qid]
        ctx = ArmContext(b, TUNING_LANE, params, b["_state_text"], b["chunks"],
                         dense_by_block.get(b["source_key"]))
        feats = router_features(ctx, b["question"])
        scored = [r for r in runs if r.get("score") is not None]
        if not scored:
            continue
        best_q = max(r["score"] for r in scored)
        cands = [r for r in scored if r["score"] == best_q]
        best = min(cands, key=lambda r: r["charged"])
        samples.append((feats, best["act"]))
    weights = router_train(samples)
    return {"params": params, "router_weights": weights, "router_samples": len(samples),
            "strongest_baseline": baseline,
            "dev_evidence": {
                "candidate_dev_quality": mean_quality(cand_runs),
                "candidate_dev_mean_charged": mean_cost(cand_runs),
                "baseline_dev_quality": {a: mean_quality(base_runs[a]) for a in BASELINE_SET},
                "baseline_dev_mean_charged": {a: mean_cost(base_runs[a]) for a in BASELINE_SET},
                "state_grid_quality": {str(g): mean_quality(v) for g, v in state_res.items()},
                "hybrid_grid_quality": {str(g): mean_quality(v) for g, v in hyb_res.items()},
            }}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.parse_args()
    def log(msg):
        print(msg, flush=True)
    states = BL.load_states()
    log(f"loaded {len(states)} compiled states")
    out = {"schema": "ORION.A2.P11TuningFreeze.v1",
           "tuning_lane": TUNING_LANE, "candidate_arm": CANDIDATE,
           "baseline_set": BASELINE_SET,
           "grids": {"state": [list(x) for x in STATE_GRID],
                     "hybrid": [list(x) for x in HYBRID_GRID],
                     "route": ROUTE_GRID, "alloc": [list(x) for x in ALLOC_GRID]},
           "selection_rule": "max mean dev quality; ties -> lower mean charged -> lexicographic",
           "lobo": "params for benchmark T tuned only on the other benchmark's dev registry"}
    v1 = tune_pass("LONGMEMEVAL_CLEANED", states, log)   # tuned on V2 web dev
    v2 = tune_pass("LONGMEMEVAL_V2", states, log)         # tuned on v1 dev
    out["tuned"] = {"LONGMEMEVAL_CLEANED": v1, "LONGMEMEVAL_V2": v2}
    fp = RECEIPTS / "TUNING_FREEZE_V1.json"
    fp.write_text(json.dumps(out, indent=2, sort_keys=True))
    log(f"wrote {fp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
