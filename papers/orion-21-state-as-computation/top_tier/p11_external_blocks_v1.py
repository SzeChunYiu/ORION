#!/usr/bin/env python3
"""P11 external campaign — per-block input assembly (shared by tuning + protected).

FROZEN block/chunk definitions (before outcomes):
  LONGMEMEVAL_CLEANED block = one registry question; chunks = its 53 haystack
    sessions rendered "role: content" with the session date prefix.
  LONGMEMEVAL_V2 block = one registry question over its domain source corpus;
    chunks = trajectory STATE PIECES: each trajectory state rendering split on
    whitespace boundaries into pieces of <= CHUNK_CHAR_LIMIT chars (1200).

Dense precompute: every chunk of a source is embedded once (bge-m3, batches of
EMBED_BATCH), cached to disk as float32 binary + json meta, and charged to the
amortized preprocessing ledger (never free, never rebuilt per arm).

Compiled state: loaded from the files sealed in COMPILATION_RECEIPT_V1.json.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
from array import array
from pathlib import Path

BASE = Path(os.environ.get("P11_BASE", str(Path.home() / "orion-p11-campaign")))
DATA = BASE / "data"
RECEIPTS = BASE / "receipts"
DENSE = BASE / "dense_cache"
CHUNK_CHAR_LIMIT = 1200
EMBED_BATCH = 64

from p11_external_lanes_v1 import embed  # noqa: E402


def H(x: str) -> str:
    return hashlib.sha256(x.encode()).hexdigest()


# ------------------------------------------------------------------ v1 blocks

def v1_records() -> dict[str, dict]:
    recs = json.loads((DATA / "LONGMEMEVAL_CLEANED" / "longmemeval_s_cleaned.json").read_text())
    return {r["question_id"]: r for r in recs}


def v1_block(rec: dict) -> dict:
    chunks = []
    for sid, date, sess in zip(rec["haystack_session_ids"],
                               rec.get("haystack_dates", [""] * 999),
                               rec["haystack_sessions"]):
        parts = [f"[{date}]"]
        for t in sess:
            parts.append(f"{t.get('role', 'user')}: {t.get('content', '')}")
        chunks.append("\n".join(parts))
    return {"qid": rec["question_id"], "question": rec["question"],
            "question_type": rec["question_type"], "answer": rec["answer"],
            "benchmark": "LONGMEMEVAL_CLEANED", "chunks": chunks,
            "source_key": f"v1/{rec['question_id']}"}


# ------------------------------------------------------------------ V2 blocks

def v2_questions() -> dict[str, dict]:
    qs = [json.loads(l) for l in (DATA / "LONGMEMEVAL_V2" / "questions.jsonl").read_text().splitlines() if l.strip()]
    return {q["id"]: q for q in qs}


def _state_pieces(states: list) -> list[str]:
    pieces = []
    for s in states:
        text = s if isinstance(s, str) else json.dumps(s, sort_keys=True)
        if len(text) <= CHUNK_CHAR_LIMIT:
            pieces.append(text)
            continue
        # whitespace-boundary split
        words = text.split(" ")
        cur = ""
        for w in words:
            if len(cur) + len(w) + 1 > CHUNK_CHAR_LIMIT and cur:
                pieces.append(cur)
                cur = w
            else:
                cur = w if not cur else cur + " " + w
        if cur:
            pieces.append(cur)
    return pieces


class V2Corpora:
    def __init__(self):
        self.small = json.loads((DATA / "LONGMEMEVAL_V2" / "haystacks__lme_v2_small.json").read_text())
        self._traj_cache: dict[str, dict] = {}
        self._piece_cache: dict[str, list[str]] = {}

    def corpus_ids(self, qids: list[str]) -> list[str]:
        return sorted({t for q in qids for t in self.small[q]})

    def traj(self, tid: str) -> dict:
        if tid not in self._traj_cache:
            self.warm_trajectories({tid})
        return self._traj_cache[tid]

    def warm_trajectories(self, ids: set[str]) -> None:
        if set(self._traj_cache) >= ids:
            return
        with open(DATA / "LONGMEMEVAL_V2" / "trajectories.jsonl") as f:
            for line in f:
                t = json.loads(line)
                if t["id"] in ids:
                    self._traj_cache[t["id"]] = t
                    if len(ids - set(self._traj_cache)) == 0:
                        break

    def chunks_for_corpus(self, corpus: str, ids: list[str]) -> list[str]:
        key = f"{corpus}:{H(','.join(ids))[:16]}"
        if key in self._piece_cache:
            return self._piece_cache[key]
        out: list[str] = []
        self.warm_trajectories(set(ids))
        for tid in ids:
            t = self._traj_cache[tid]
            head = f"TRAJ {tid} domain={t['domain']} goal={str(t.get('goal', ''))[:400]}"
            out.append(head)
            out.extend(_state_pieces(t.get("states", [])))
        self._piece_cache[key] = out
        return out

    def block(self, q: dict, corpus: str, corpus_ids: list[str]) -> dict:
        return {"qid": q["id"], "question": q["question"],
                "question_type": q.get("question_type", ""),
                "answer": q.get("answer", ""), "eval_function": q.get("eval_function", ""),
                "benchmark": "LONGMEMEVAL_V2", "chunks": self.chunks_for_corpus(corpus, corpus_ids),
                "source_key": f"v2/{corpus}"}


# --------------------------------------------------------------- dense precompute

def get_dense_index(source_key: str, chunks: list[str]) -> dict:
    """Embed all chunks once per source; disk-cached; returns {"vecs": [...], ...}."""
    DENSE.mkdir(parents=True, exist_ok=True)
    sig = H(source_key + "|" + str(len(chunks)) + "|" + H(chunks[0][:200] if chunks else "") + "|" + H(chunks[-1][-200:] if chunks else ""))
    base_fp = DENSE / f"{source_key.replace('/', '__')}_{sig[:12]}"
    meta_fp = base_fp.with_suffix(".json")
    vec_fp = base_fp.with_suffix(".f32")
    if meta_fp.exists() and vec_fp.exists():
        meta = json.loads(meta_fp.read_text())
        arr = array("f")
        arr.frombytes(vec_fp.read_bytes())
        dim = meta["dim"]
        vecs = [arr[i * dim:(i + 1) * dim].tolist() for i in range(meta["n"])]
        return {"vecs": vecs, "dim": dim, "n": meta["n"],
                "embedded_tokens": meta["embedded_tokens"],
                "embedding_calls": meta["embedding_calls"], "precompute_ms": meta["precompute_ms"],
                "cache": "hit"}
    t0 = time.time()
    vecs: list[list[float]] = []
    embedded_tokens = 0
    calls = 0
    for i in range(0, len(chunks), EMBED_BATCH):
        batch = [c[:6000] for c in chunks[i:i + EMBED_BATCH]]
        rec = embed(batch)
        got = rec.get("vectors") or []
        if len(got) != len(batch):
            raise RuntimeError(f"embed batch size mismatch: {len(got)} != {len(batch)}")
        vecs.extend(got)
        embedded_tokens += rec.get("embedded_tokens", sum(len(b) for b in batch) // 4)
        calls += rec.get("embedding_calls", 1)
    dim = len(vecs[0]) if vecs else 0
    arr = array("f", [x for v in vecs for x in v])
    vec_fp.write_bytes(arr.tobytes())
    meta_fp.write_text(json.dumps({"source": source_key, "n": len(chunks), "dim": dim,
                                   "embedded_tokens": embedded_tokens,
                                   "embedding_calls": calls,
                                   "precompute_ms": int((time.time() - t0) * 1000),
                                   "chunk_char_limit": CHUNK_CHAR_LIMIT}))
    return {"vecs": vecs, "dim": dim, "n": len(chunks),
            "embedded_tokens": embedded_tokens, "embedding_calls": calls,
            "precompute_ms": int((time.time() - t0) * 1000), "cache": "built"}


# ------------------------------------------------------------- compiled state

def load_states() -> dict[str, dict]:
    receipt = json.loads((RECEIPTS / "COMPILATION_RECEIPT_V1.json").read_text())
    out = {}
    for src, info in receipt["state_files"].items():
        out[src] = {"text": Path(info["path"]).read_text(), "sha256": info["sha256"],
                    "n_chars": info["n_chars"]}
    return out


def state_for(states: dict, source_key: str) -> str:
    s = states.get(source_key)
    if s is None:
        raise KeyError(f"no compiled state for {source_key}; have {sorted(states)}")
    return s["text"]
