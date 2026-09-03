#!/usr/bin/env python3
"""P11 external campaign — the 10 frozen arms over a task/session block.

Shared substrate per block:
  chunks      raw evidence units (v1: chat turns grouped per session; V2: trajectory
              state renderings) — the raw-corpus retrieval substrate
  state_units query-agnostic compiled state (hierarchical map-reduce by the frozen
              local compiler lane llama3.1-8b; compiled ONCE per source, before the
              query registry reveal)

Arms (P11_EXTERNAL_EXECUTION_HARNESS_FREEZE_V1.json):
  1 COMPILED_QUERY_CONDITIONED_STATE  BM25 over state units -> top units -> reason+answer
  2 HYBRID_DENSE_BM25_RERANK          BM25 + bge-m3 dense (RRF) -> LLM rerank -> answer
  3 FULL_CONTEXT_NO_RETRIEVAL         whole block text (CANNOT_CHECK when over lane ctx)
  4 REASON_ONLY                       question alone, parametric reasoning
  5 STATE_RETRIEVAL_ONLY              BM25 over state units -> answer-only instruction
  6 FIXED_STATE_REASON_SPLITS         fixed 2-pass: state retrieval draft, then reason pass
  7 SIMPLE_UNCERTAINTY_ROUTING        BM25 confidence routes 5 vs 6 (threshold dev-tuned)
  8 CURRENT_ADAPTIVE_ALLOCATOR        P12 price-aware knapsack policy over unit certs
  9 LEARNED_JOINT_ALLOCATOR_DEV_ONLY  logistic router trained on dev features only
 10 HINDSIGHT_ORACLE_ANALYSIS_ONLY    post hoc best-quality / cheapest-attaining cost

No outcome-dependent logic lives here: hyperparameters arrive frozen from the tuning
driver (dev-only); the oracle is computed by the assembler, never selectable.

Resource vector accounting (frozen prices, charged token-equivalents):
  total_charged = 1.0*llm_in + 4.0*llm_out
                + 0.05*embedded_tokens (dense precompute + queries)
                + 0.02*bm25_indexed_tokens
Local auxiliary prices are frozen in the manifest accounting block BEFORE runs.
"""
from __future__ import annotations

import json
import math
import re
from collections import Counter

from p11_external_lanes_v1 import call, embed

ARMS = (
    "COMPILED_QUERY_CONDITIONED_STATE", "HYBRID_DENSE_BM25_RERANK", "FULL_CONTEXT_NO_RETRIEVAL", "REASON_ONLY",
    "STATE_RETRIEVAL_ONLY", "FIXED_STATE_REASON_SPLITS", "SIMPLE_UNCERTAINTY_ROUTING", "CURRENT_ADAPTIVE_ALLOCATOR",
    "LEARNED_JOINT_ALLOCATOR_DEV_ONLY", "HINDSIGHT_ORACLE_ANALYSIS_ONLY",
)
PRICE_IN, PRICE_OUT, PRICE_EMBED, PRICE_SPARSE = 1.0, 4.0, 0.05, 0.02
LANE_CONTEXT_TOKENS = {"gpt-5.5-codexcli": 272000, "claude-fable-5-cli": 200000, "llama3.1-8b-ollama": 131072}
FULL_CONTEXT_OVERHEAD_TOKENS = 1500  # instructions + question + slack


# --------------------------------------------------------------- BM25 (std-only)

def _tok(s: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", s.lower())


class BM25:
    """Inverted-index BM25 (k1=1.5, b=0.75): one-time build, sparse scoring.

    Scoring touches only docs containing a query term, so 10^5-doc corpora score
    in milliseconds. Build cost is the arm's indexed_tokens charge."""

    def __init__(self, docs: list[str]):
        self.n = len(docs)
        self.dls: list[int] = []
        self.postings: dict[str, list[tuple[int, int]]] = {}
        self.df: Counter = Counter()
        total = 0
        for i, d in enumerate(docs):
            tf = Counter(_tok(d))
            self.dls.append(sum(tf.values()))
            total += sum(tf.values())
            self.df.update(tf.keys())
            for t, c in tf.items():
                self.postings.setdefault(t, []).append((i, c))
        self.avgdl = total / max(1, self.n)
        self.indexed_tokens = total

    def scores(self, query: str) -> list[float]:
        out = [0.0] * self.n
        k1, b = 1.5, 0.75
        for t in set(_tok(query)):
            plist = self.postings.get(t)
            if not plist:
                continue
            idf = math.log(1.0 + (self.n - self.df[t] + 0.5) / (self.df[t] + 0.5))
            for i, c in plist:
                out[i] += idf * c * (k1 + 1) / (c + k1 * (1 - b + b * self.dls[i] / self.avgdl))
        return out


def rrf(rank_lists: list[list[int]], k: int = 60) -> list[float]:
    fused = [0.0] * len(rank_lists[0]) if rank_lists else []
    for rl in rank_lists:
        for pos, idx in enumerate(rl):
            fused[idx] += 1.0 / (k + pos + 1)
    return fused


def _cos(a: list[float], b: list[float]) -> float:
    num = sum(x * y for x, y in zip(a, b))
    da = math.sqrt(sum(x * x for x in a)) or 1.0
    db = math.sqrt(sum(x * x for x in b)) or 1.0
    return num / (da * db)


# ------------------------------------------------------------ prompts (frozen)

COMPILE_MAP_PROMPT = (
    "You are building durable memory for a long interaction history. Extract from the "
    "following segment every durable fact worth remembering later: user facts, preferences, "
    "decisions, events with dates, entities, and stable procedures. Ignore transient filler. "
    "Output ONLY a numbered list, one fact per line, max 12 lines, each <= 40 words.\n\nSEGMENT:\n{}"
)
COMPILE_REDUCE_PROMPT = (
    "You are building durable memory for a long interaction history. Merge and deduplicate "
    "the extracted fact lists below into one consolidated numbered list (max 60 lines, each "
    "<= 40 words), preserving specifics (names, numbers, dates). Output ONLY the list.\n\nFACT LISTS:\n{}"
)
ANSWER_STATE_PROMPT = (
    "Answer the question using the provided memory state. Think briefly, then answer.\n"
    "QUESTION: {}\n\nMEMORY STATE:\n{}\n\nAnswer concisely (one short sentence unless more is needed)."
)
ANSWER_STATE_STRICT_PROMPT = (
    "Answer using ONLY the provided memory state. Do not reason beyond it; if the state does "
    "not contain the answer, say UNKNOWN.\nQUESTION: {}\n\nMEMORY STATE:\n{}\n\nAnswer in one short sentence."
)
ANSWER_HYBRID_PROMPT = (
    "Answer the question using the provided evidence excerpts.\nQUESTION: {}\n\nEVIDENCE:\n{}\n\n"
    "Answer concisely (one short sentence unless more is needed)."
)
ANSWER_FULL_PROMPT = (
    "Here is the full interaction history, then a question. Answer the question from the history.\n"
    "HISTORY:\n{}\n\nQUESTION: {}\n\nAnswer concisely (one short sentence unless more is needed)."
)
REASON_ONLY_PROMPT = (
    "Answer from your own knowledge and reasoning only; no documents are provided.\nQUESTION: {}\n"
    "Answer concisely (one short sentence unless more is needed). If you cannot know, say UNKNOWN."
)
RERANK_PROMPT = (
    "Rank the evidence excerpts by how useful they are for answering the question. "
    "Reply ONLY with the excerpt numbers in descending usefulness, like: 3 1 4 2.\n"
    "QUESTION: {}\n\nEXCERPTS:\n{}"
)
SPLIT_DRAFT_PROMPT = (
    "Draft an answer skeleton using the memory state: identify which facts are needed and what "
    "is missing.\nQUESTION: {}\n\nMEMORY STATE:\n{}\n\nOutput the skeleton only."
)
SPLIT_REFINE_PROMPT = (
    "Refine this draft into a final answer. Reason about what the question actually asks; fix "
    "gaps; do not add unsupported specifics.\nQUESTION: {}\n\nDRAFT:\n{}\n\nFinal answer (one short sentence unless more is needed)."
)
ALLOCATOR_ALLOC_PROMPT = (
    "Using the memory state and the served note, answer the question.\nQUESTION: {}\n\n"
    "MEMORY STATE:\n{}\n\nSERVED NOTE:\n{}\n\nAnswer concisely."
)


# ------------------------------------------------------------- arm plumbing

def _budget_units(state_units: list[str], k: int, max_chars: int) -> str:
    sel = state_units[:k]
    total, out = 0, []
    for u in sel:
        if total + len(u) > max_chars:
            break
        out.append(u)
        total += len(u)
    return "\n".join(out) if out else (state_units[0] if state_units else "EMPTY STATE")


class ArmContext:
    """Everything an arm needs for one block; resource counters accumulate here."""

    def __init__(self, block: dict, lane: str, params: dict, state_text: str,
                 chunk_texts: list[str], dense_index=None):
        self.block = block            # question/question_type/answer(+eval) metadata
        self.lane = lane
        self.p = params               # frozen hyperparameters
        self.state_units = state_text.split("\n") if state_text else []
        self.state_text = state_text
        self.chunks = chunk_texts
        self.bm25_state = BM25([u for u in self.state_units if u.strip()])
        self.bm25_chunks = BM25(self.chunks)
        # per-arm query-vector cache: every arm pays its own query embedding
        # (corpus vectors are precomputed once per source and amortized by the
        # frozen accounting rule — never shared for free across arms)
        self.dense_index = dict(dense_index, qvec_cache={}) if dense_index is not None else None
        self.rv = {f: 0 for f in ("input_tokens", "output_tokens", "wall_latency_ms", "peak_memory_bytes",
                                  "embedding_calls", "sparse_retrieval_calls", "dense_retrieval_calls",
                                  "reranking_calls", "compilation_calls", "materialization_calls",
                                  "preprocessing_time_ms", "state_construction_time_ms",
                                  "explicit_vendor_or_local_cost", "embedded_query_tokens")}
        self.indexed_tokens = self.bm25_chunks.indexed_tokens + self.bm25_state.indexed_tokens

    def _charge_llm(self, rec: dict) -> str:
        self.rv["input_tokens"] += rec["input_tokens"]
        self.rv["output_tokens"] += rec["output_tokens"]
        self.rv["wall_latency_ms"] += int(rec["seconds"] * 1000)
        return rec["output"]

    def top_state(self, question: str, k: int, max_chars: int) -> tuple[str, float]:
        scores = self.bm25_state.scores(question)
        self.rv["sparse_retrieval_calls"] += 1
        order = sorted(range(len(scores)), key=lambda i: -scores[i])
        ranked_units = [self.state_units[i] for i in order if self.state_units[i].strip()]
        if len(order) >= 2 and scores[order[1]] > 0:
            conf = scores[order[0]] / (1.0 + scores[order[1]])
        elif order:
            conf = max(0.0, scores[order[0]])
        else:
            conf = 0.0
        return _budget_units(ranked_units, k, max_chars), conf

    def hybrid_retrieve(self, question: str) -> tuple[str, float]:
        p = self.p
        sparse = self.bm25_chunks.scores(question)
        self.rv["sparse_retrieval_calls"] += 1
        s_order = sorted(range(len(sparse)), key=lambda i: -sparse[i])
        cands: list[int]
        if self.dense_index is not None:
            if question not in self.dense_index["qvec_cache"]:
                rec = embed([question])
                self.rv["embedding_calls"] += rec["embedding_calls"]
                self.rv["embedded_query_tokens"] = self.rv.get("embedded_query_tokens", 0) + rec["embedded_tokens"]
                self.dense_index["qvec_cache"][question] = rec["vectors"][0]
            qv = self.dense_index["qvec_cache"][question]
            self.rv["dense_retrieval_calls"] += 1
            sims = [_cos(qv, v) for v in self.dense_index["vecs"]]
            d_order = sorted(range(len(sims)), key=lambda i: -sims[i])
            fused = rrf([s_order, d_order])
        else:
            fused = rrf([s_order])
        cands = sorted(range(len(fused)), key=lambda i: -fused[i])[: p["rerank_depth"]]
        excerpts = "\n".join(f"[{n}] {self.chunks[i][:900]}" for n, i in enumerate(cands, 1))
        rr = call(self.lane, RERANK_PROMPT.format(question[:600], excerpts))
        self._charge_llm(rr)
        self.rv["reranking_calls"] += 1
        nums = [int(x) for x in re.findall(r"\d+", rr["output"]) if 1 <= int(x) <= len(cands)]
        seen: set[int] = set()
        final_order = [cands[x - 1] for x in nums if not (x in seen or seen.add(x))]
        final_order += [i for i in cands if i not in final_order]
        picked = final_order[: p["top_k"]]
        conf = fused[cands[0]] if cands else 0.0
        return "\n---\n".join(self.chunks[i][: p["chunk_chars"]] for i in picked), conf


# ---------------------------------------------------------------- the arms

def run_arm(arm: str, ctx: ArmContext) -> dict:
    p, lane, q = ctx.p, ctx.lane, ctx.block["question"]
    qtype = ctx.block.get("question_type", "")

    if arm == "COMPILED_QUERY_CONDITIONED_STATE":
        state, _ = ctx.top_state(q, p["state_top_k"], p["state_max_chars"])
        rec = call(lane, ANSWER_STATE_PROMPT.format(q, state))
        return {"answer": ctx._charge_llm(rec)}

    if arm == "HYBRID_DENSE_BM25_RERANK":
        ev, _ = ctx.hybrid_retrieve(q)
        rec = call(lane, ANSWER_HYBRID_PROMPT.format(q, ev))
        return {"answer": ctx._charge_llm(rec)}

    if arm == "FULL_CONTEXT_NO_RETRIEVAL":
        full = "\n".join(ctx.chunks)
        est = (len(full) + len(q)) // 4 + FULL_CONTEXT_OVERHEAD_TOKENS
        if est > LANE_CONTEXT_TOKENS[lane]:
            return {"answer": None, "cannot_check_reason":
                    f"haystack {est} tokens exceeds lane context limit {LANE_CONTEXT_TOKENS[lane]}"}
        rec = call(lane, ANSWER_FULL_PROMPT.format(full, q))
        return {"answer": ctx._charge_llm(rec)}

    if arm == "REASON_ONLY":
        rec = call(lane, REASON_ONLY_PROMPT.format(q))
        return {"answer": ctx._charge_llm(rec)}

    if arm == "STATE_RETRIEVAL_ONLY":
        state, _ = ctx.top_state(q, p["state_top_k"], p["state_max_chars"])
        rec = call(lane, ANSWER_STATE_STRICT_PROMPT.format(q, state))
        return {"answer": ctx._charge_llm(rec)}

    if arm == "FIXED_STATE_REASON_SPLITS":
        state, _ = ctx.top_state(q, p["state_top_k"], p["state_max_chars"])
        d = call(lane, SPLIT_DRAFT_PROMPT.format(q, state))
        draft = ctx._charge_llm(d)
        r = call(lane, SPLIT_REFINE_PROMPT.format(q, draft[:4000]))
        return {"answer": ctx._charge_llm(r)}

    if arm == "SIMPLE_UNCERTAINTY_ROUTING":
        state, conf = ctx.top_state(q, p["state_top_k"], p["state_max_chars"])
        if conf >= p["route_conf_threshold"]:
            rec = call(lane, ANSWER_STATE_STRICT_PROMPT.format(q, state))
            return {"answer": ctx._charge_llm(rec), "route": "state_strict"}
        d = call(lane, SPLIT_DRAFT_PROMPT.format(q, state))
        draft = ctx._charge_llm(d)
        r = call(lane, SPLIT_REFINE_PROMPT.format(q, draft[:4000]))
        return {"answer": ctx._charge_llm(r), "route": "state_reason"}

    if arm == "CURRENT_ADAPTIVE_ALLOCATOR":
        # P12 price-aware knapsack policy applied per state unit: eligibility by
        # priced marginal delta between serving the unit as state vs reasoning over
        # it; budget = frozen reason-pass token budget.
        from p12_price_aware_allocator_v1 import price_aware_selection
        scores = ctx.bm25_state.scores(q)
        ctx.rv["sparse_retrieval_calls"] += 1
        order = sorted(range(len(scores)), key=lambda i: -scores[i])[: p["alloc_window"]]
        ledger = []
        for i in order:
            u = ctx.state_units[i].strip()
            if not u:
                continue
            ledger.append({"sid": str(i),
                           "declared_cost": max(1, len(u) // 4),
                           "reason_serve_certificate": scores[i] / (max(scores) or 1.0),
                           "state_serve_certificate": min(1.0, scores[i] / (max(scores) or 1.0) * p["alloc_state_mult"])})
        chosen = price_aware_selection(ledger, (p["alloc_p_build"], 1.0), p["alloc_budget"])
        sel = [ctx.state_units[int(s)] for s in chosen if int(s) < len(ctx.state_units)]
        state = "\n".join(sel[: p["state_top_k"]]) or _budget_units([u for u in ctx.state_units if u.strip()], 5, p["state_max_chars"])
        note = "no unit met the priced-serve bar; reasoning allocation retained" if not chosen else "priced state subset served"
        rec = call(lane, ALLOCATOR_ALLOC_PROMPT.format(q, state, note))
        return {"answer": ctx._charge_llm(rec)}

    if arm == "LEARNED_JOINT_ALLOCATOR_DEV_ONLY":
        feats = router_features(ctx, q)
        action = router_predict(p["_router_weights"], feats)
        if action == "state":
            state, _ = ctx.top_state(q, p["state_top_k"], p["state_max_chars"])
            rec = call(lane, ANSWER_STATE_STRICT_PROMPT.format(q, state))
        elif action == "reason":
            rec = call(lane, REASON_ONLY_PROMPT.format(q))
        elif action == "split":
            state, _ = ctx.top_state(q, p["state_top_k"], p["state_max_chars"])
            d = call(lane, SPLIT_DRAFT_PROMPT.format(q, state))
            draft = ctx._charge_llm(d)
            rec = call(lane, SPLIT_REFINE_PROMPT.format(q, draft[:4000]))
        else:  # hybrid
            ev, _ = ctx.hybrid_retrieve(q)
            rec = call(lane, ANSWER_HYBRID_PROMPT.format(q, ev))
        return {"answer": ctx._charge_llm(rec), "router_action": action}

    raise ValueError(f"unknown arm {arm}")


# ------------------------------------------- learned router (dev-only training)

def router_features(ctx: "ArmContext", q: str) -> dict:
    _, conf = ctx.top_state(q, 8, 6000)
    qt = ctx.block.get("question_type", "")
    return {
        "bias": 1.0,
        "bm25_conf": min(3.0, conf),
        "log_chunks": math.log1p(len(ctx.chunks)),
        "log_state": math.log1p(len([u for u in ctx.state_units if u.strip()])),
        "temporal": 1.0 if "temporal" in qt else 0.0,
        "update": 1.0 if "update" in qt or "knowledge" in qt else 0.0,
        "multi": 1.0 if "multi" in qt or "dynamic" in qt else 0.0,
        "abs": 1.0 if ctx.block.get("abstention") else 0.0,
    }


FEATURE_ORDER = ["bias", "bm25_conf", "log_chunks", "log_state", "temporal", "update", "multi", "abs"]
ACTIONS = ("state", "reason", "split", "hybrid")


def router_predict(weights: dict, feats: dict) -> str:
    scores = {a: sum(weights[a][f] * feats.get(f, 0.0) for f in FEATURE_ORDER) for a in ACTIONS}
    return max(ACTIONS, key=lambda a: scores[a])


def router_train(samples: list[tuple[dict, str]], epochs: int = 200, lr: float = 0.05) -> dict:
    """Deterministic softmax regression (one-vs-all), pure stdlib."""
    weights = {a: {f: 0.0 for f in FEATURE_ORDER} for a in ACTIONS}
    for _ in range(epochs):
        for feats, gold in samples:
            z = {a: sum(weights[a][f] * feats.get(f, 0.0) for f in FEATURE_ORDER) for a in ACTIONS}
            m = max(z.values())
            ex = {a: math.exp(z[a] - m) for a in ACTIONS}
            s = sum(ex.values()) or 1.0
            for a in ACTIONS:
                y = 1.0 if a == gold else 0.0
                g = ex[a] / s - y
                for f in FEATURE_ORDER:
                    weights[a][f] -= lr * g * feats.get(f, 0.0)
    return weights


def charged_cost(rv: dict, embedded_tokens: int = 0) -> float:
    return (PRICE_IN * rv["input_tokens"] + PRICE_OUT * rv["output_tokens"]
            + PRICE_EMBED * embedded_tokens + PRICE_SPARSE * rv.get("indexed_tokens", 0))
