#!/usr/bin/env python3
"""P11 external campaign — query-agnostic state compilation (hierarchical map-reduce).

FROZEN TOPOLOGY (fixed before any outcome was observed; sealed in
COMPILATION_RECEIPT_V1.json before the fresh-query registry reveal):

  LONGMEMEVAL_CLEANED  unit = session (natural unit; avg ~2.6k tok, max ~6k)
                       map: one COMPILE_MAP call per session (all 53 per question)
                       reduce: map outputs grouped <=10 per group -> group lists ->
                       final per-question state (the question's haystack is its block)
  LONGMEMEVAL_V2       unit = trajectory segment (avg traj ~214k tok; split on state
                       boundaries at <= MAP_SEGMENT_EST_TOKENS est tokens)
                       map: one COMPILE_MAP call per segment
                       reduce: segments' outputs -> per-trajectory list (groups <=10)
                       then per-corpus: trajectory lists grouped <=20 -> group lists
                       -> final per-corpus state (web, enterprise), shared by every
                       question on that corpus (the V2 design point)

Compiler lane: llama3.1-8b-ollama (FIXED local compiler — an infrastructure
identity shared across all model families, like bge-m3). num_ctx: 32768 (map),
16384 (reduce); identical decoding options otherwise (temp 0.6, top_p 0.9, seed 42).

Work-queue execution: `--plan` writes the deterministic task list; `--work PORT`
claims tasks by atomic rename (NFS-safe) and appends results; `--finalize`
assembles COMPILATION_RECEIPT_V1.json. No outcome field is read anywhere.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

BASE = Path(os.environ.get("P11_BASE", str(Path.home() / "orion-p11-campaign")))
DATA = BASE / "data"
QUEUE = BASE / "compile_queue"
DONE = QUEUE / "done"
RESULTS = BASE / "results"
RECEIPTS = BASE / "receipts"

MAP_SEGMENT_EST_TOKENS = 24000
REDUCE_GROUP = 10
CORPUS_REDUCE_GROUP = 20
MAP_NUM_CTX = 32768
REDUCE_NUM_CTX = 16384

from p11_external_arms_v1 import COMPILE_MAP_PROMPT, COMPILE_REDUCE_PROMPT  # noqa: E402
from p11_external_lanes_v1 import _est_tokens, _ollama_call  # noqa: E402


def H(x: str) -> str:
    return hashlib.sha256(x.encode()).hexdigest()


# ------------------------------------------------------------------ plan build

def _v1_questions() -> list[dict]:
    """Exact frozen selection (greedy pairwise source-disjoint, sha256 id order)."""
    import p11_external_registry_builder_v1 as rb
    return rb.build_v1()


def _v2() -> dict:
    import p11_external_registry_builder_v1 as rb
    return rb.build_v2()


def _render_session(sess: list[dict], date: str) -> str:
    parts = [f"[{date}]"]
    for t in sess:
        parts.append(f"{t.get('role', 'user')}: {t.get('content', '')}")
    return "\n".join(parts)


def _render_traj(t: dict) -> str:
    head = f"TRAJECTORY {t['id']} domain={t['domain']} goal={t.get('goal', '')[:800]}"
    states = t.get("states", [])
    return head + "\n" + "\n=== STATE ===\n".join(
        s if isinstance(s, str) else json.dumps(s, sort_keys=True) for s in states)


def _split_segments(text: str, est_limit: int) -> list[str]:
    """Split on === STATE === boundaries, packing states to the est-token limit."""
    head, *rest = text.split("\n=== STATE ===\n")
    states = [head] + rest
    segs, cur, cur_tok = [], head, _est_tokens(head)
    for s in states[1:]:
        st = _est_tokens(s)
        if cur_tok + st > est_limit and cur.strip():
            segs.append(cur)
            cur, cur_tok = "", 0
        cur += "\n=== STATE ===\n" + s
        cur_tok += st
    if cur.strip():
        segs.append(cur)
    return segs or [text]


def build_plan() -> list[dict]:
    tasks: list[dict] = []
    v1 = _v1_questions()
    v1_by_pool = {"dev": v1["development_registry"]["question_ids"],
                  "primary": v1["primary_registry"]["question_ids"],
                  "fresh": v1["fresh_query_pool"]["question_ids"]}
    recs = json.loads((DATA / "LONGMEMEVAL_CLEANED" / "longmemeval_s_cleaned.json").read_text())
    by_qid = {r["question_id"]: r for r in recs}
    for pool, qids in v1_by_pool.items():
        for qid in qids:
            r = by_qid[qid]
            src_sha = H("".join(sorted(r["haystack_session_ids"])))
            map_ids = []
            for i, (sid, date, sess) in enumerate(
                    zip(r["haystack_session_ids"], r.get("haystack_dates", [""] * 999),
                        r["haystack_sessions"])):
                text = _render_session(sess, date)
                tid = f"v1/{pool}/{qid}/map/{i:03d}_{sid}"
                tasks.append({"task_id": tid, "kind": "map", "source": f"v1/{qid}",
                              "source_sha256": src_sha, "est_in": _est_tokens(text),
                              "prompt_kind": "COMPILE_MAP_PROMPT", "text": text})
                map_ids.append(tid)
            # reduce level: groups of REDUCE_GROUP -> group lists, then final
            level = [map_ids]
            lvl = 0
            while len(level[-1]) > 1:
                prev = level[-1]
                nxt = []
                for g in range(0, len(prev), REDUCE_GROUP):
                    grp = prev[g:g + REDUCE_GROUP]
                    tid = f"v1/{pool}/{qid}/reduce{lvl + 1}/{g // REDUCE_GROUP:03d}"
                    tasks.append({"task_id": tid, "kind": "reduce", "source": f"v1/{qid}",
                                  "source_sha256": src_sha, "est_in": 0,
                                  "prompt_kind": "COMPILE_REDUCE_PROMPT",
                                  "input_task_ids": grp})
                    nxt.append(tid)
                level.append(nxt)
                lvl += 1
    # V2 corpora
    v2 = _v2()
    small = json.loads((DATA / "LONGMEMEVAL_V2" / "haystacks__lme_v2_small.json").read_text())
    web_qids = v2["development_registry"]["question_ids"] + v2["primary_registry"]["question_ids"]
    ent_qids = v2["fresh_query_pool"]["question_ids"]
    corpora = {"web": sorted({t for q in web_qids for t in small[q]}),
               "enterprise": sorted({t for q in ent_qids for t in small[q]})}
    need = set(corpora["web"]) | set(corpora["enterprise"])
    trajs = {}
    with open(DATA / "LONGMEMEVAL_V2" / "trajectories.jsonl") as f:
        for line in f:
            t = json.loads(line)
            if t["id"] in need:
                trajs[t["id"]] = t
    for corp, tids in corpora.items():
        traj_final_ids = []
        for tid_traj in tids:
            t = trajs[tid_traj]
            text = _render_traj(t)
            segs = _split_segments(text, MAP_SEGMENT_EST_TOKENS)
            map_ids = []
            for i, seg in enumerate(segs):
                tid = f"v2/{corp}/{tid_traj}/map/{i:03d}"
                tasks.append({"task_id": tid, "kind": "map", "source": f"v2/{corp}",
                              "source_sha256": H(corp), "est_in": _est_tokens(seg),
                              "prompt_kind": "COMPILE_MAP_PROMPT", "text": seg})
                map_ids.append(tid)
            prev = map_ids
            lvl = 0
            while len(prev) > 1:  # per-trajectory reduce
                nxt = []
                for g in range(0, len(prev), REDUCE_GROUP):
                    grp = prev[g:g + REDUCE_GROUP]
                    tid = f"v2/{corp}/{tid_traj}/reduce{lvl + 1}/{g // REDUCE_GROUP:03d}"
                    tasks.append({"task_id": tid, "kind": "reduce", "source": f"v2/{corp}/{tid_traj}",
                                  "source_sha256": H(f"{corp}/{tid_traj}"), "est_in": 0,
                                  "prompt_kind": "COMPILE_REDUCE_PROMPT", "input_task_ids": grp})
                    nxt.append(tid)
                prev = nxt
                lvl += 1
            traj_final_ids.append(prev[0] if prev else "")
        # corpus-level reduce over trajectory lists
        prev = traj_final_ids
        lvl = 0
        while len(prev) > 1:
            nxt = []
            for g in range(0, len(prev), CORPUS_REDUCE_GROUP):
                grp = prev[g:g + CORPUS_REDUCE_GROUP]
                tid = f"v2/{corp}/corpus_reduce{lvl + 1}/{g // CORPUS_REDUCE_GROUP:03d}"
                tasks.append({"task_id": tid, "kind": "reduce", "source": f"v2/{corp}",
                              "source_sha256": H(corp), "est_in": 0,
                              "prompt_kind": "COMPILE_REDUCE_PROMPT", "input_task_ids": grp})
                nxt.append(tid)
            prev = nxt
            lvl += 1
    for t in tasks:
        t["task_sha256"] = H(json.dumps(t, sort_keys=True))
    return tasks


# ------------------------------------------------------------------- execution

def _ollama_call_ctx(num_ctx: int, prompt: str) -> dict:
    url = os.environ.get("P11_OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
    payload = json.dumps({"model": "llama3.1:8b", "prompt": prompt, "stream": False,
                          "options": {"num_ctx": num_ctx, "temperature": 0.6,
                                      "top_p": 0.9, "seed": 42}}).encode()
    t0 = time.time()
    req = urllib.request.Request(url + "/api/generate", data=payload,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=7200) as resp:
        p = json.loads(resp.read().decode())
    return {"output": p.get("response", "").strip(), "rc": 0,
            "seconds": round(time.time() - t0, 3),
            "input_tokens": int(p.get("prompt_eval_count", 0)),
            "output_tokens": int(p.get("eval_count", 0)),
            "token_accounting_method": "ollama_native"}


def _task_prompt(task: dict, outputs: dict) -> str:
    if task["kind"] == "map":
        return COMPILE_MAP_PROMPT.format(task["text"])
    lists = []
    for itid in task["input_task_ids"]:
        out = outputs.get(itid, {}).get("output", "")
        lists.append(out if out else "(empty)")
    return COMPILE_REDUCE_PROMPT.format("\n\n--- NEXT LIST ---\n\n".join(lists))


def run_worker(port: int, poll_s: int, idle_exit_s: int) -> int:
    os.environ["P11_OLLAMA_URL"] = f"http://127.0.0.1:{port}"
    QUEUE.mkdir(parents=True, exist_ok=True)
    DONE.mkdir(parents=True, exist_ok=True)
    outputs_path = QUEUE / f"outputs_{port}.jsonl"
    index: dict[str, dict] = {}
    idle_since: float | None = None
    handled = 0
    while True:
        claimed = None
        claimed_name = None
        for pf in sorted(QUEUE.glob("task_*.json")):
            try:
                os.rename(pf, DONE / pf.name)
                claimed = json.loads((DONE / pf.name).read_text())
                claimed_name = pf.name
                break
            except OSError:
                continue
        if claimed is None:
            if idle_since is None:
                idle_since = time.time()
            if time.time() - idle_since > idle_exit_s:
                break
            time.sleep(poll_s)
            continue
        idle_since = None
        # gather upstream outputs (rescan all worker outputs on miss)
        upstream: dict[str, dict] = {}
        missing = False
        for itid in claimed.get("input_task_ids", []):
            rec = index.get(itid) or _rescan(index)
            rec = index.get(itid)
            if rec is None:
                print(f"[{port}] upstream {itid} not ready; deferring {claimed['task_id']}",
                      flush=True)
                os.rename(DONE / claimed_name, QUEUE / claimed_name)
                claimed = None
                missing = True
                break
            upstream[itid] = rec
        if missing:
            time.sleep(poll_s)
            continue
        prompt = _task_prompt(claimed, upstream)
        rec = None
        for attempt in range(3):
            try:
                rec = _ollama_call_ctx(MAP_NUM_CTX if claimed["kind"] == "map" else REDUCE_NUM_CTX,
                                       prompt)
                if rec["output"].strip():
                    break
            except (OSError, ValueError) as exc:
                print(f"[{port}] call failed ({exc}); retrying", flush=True)
                time.sleep(30 * (2 ** attempt))
        rec = rec or {"output": "", "rc": -1, "seconds": 0.0, "input_tokens": 0,
                      "output_tokens": 0, "token_accounting_method": "failed"}
        rec.update({"task_id": claimed["task_id"], "task_sha256": claimed["task_sha256"],
                    "kind": claimed["kind"], "source": claimed["source"],
                    "attempts": attempt + 1, "ts": time.time()})
        with open(outputs_path, "a") as f:
            f.write(json.dumps(rec) + "\n")
        index[claimed["task_id"]] = rec
        handled += 1
        print(f"[{port}] {claimed['task_id']} in={rec['input_tokens']} "
              f"out={rec['output_tokens']} {rec['seconds']}s", flush=True)
    print(f"[{port}] worker done, handled={handled}", flush=True)
    return 0


def _rescan(index: dict[str, dict]) -> dict | None:
    for pf in sorted(QUEUE.glob("outputs_*.jsonl")):
        try:
            for line in pf.read_text().splitlines():
                if line.strip():
                    rec = json.loads(line)
                    if rec.get("output", "").strip():
                        index.setdefault(rec["task_id"], rec)
        except (OSError, ValueError):
            continue
    return None


def cmd_plan() -> int:
    tasks = build_plan()
    QUEUE.mkdir(parents=True, exist_ok=True)
    DONE.mkdir(parents=True, exist_ok=True)
    plan_path = QUEUE / "PLAN.json"
    plan_path.write_text(json.dumps(tasks, indent=0))
    n_map = sum(1 for t in tasks if t["kind"] == "map")
    n_red = len(tasks) - n_map
    est_in = sum(t["est_in"] for t in tasks)
    for t in tasks:
        (QUEUE / f"task_{t['task_id'].replace('/', '__')}.json").write_text(json.dumps(t))
    print(json.dumps({"tasks": len(tasks), "map": n_map, "reduce": n_red,
                      "est_map_input_tokens": est_in,
                      "plan_sha256": H(plan_path.read_text())}, indent=2))
    return 0


def cmd_finalize() -> int:
    outputs: dict[str, dict] = {}
    for pf in sorted(QUEUE.glob("outputs_*.jsonl")):
        for line in pf.read_text().splitlines():
            if line.strip():
                rec = json.loads(line)
                if rec.get("output", "").strip():
                    outputs[rec["task_id"]] = rec
    tasks = json.loads((QUEUE / "PLAN.json").read_text())
    finals = [t for t in tasks if t["source"].startswith("v1/") and "/reduce" in t["task_id"]
              and _is_final(tasks, t)] + [t for t in tasks if t["source"].startswith("v2/")
              and "corpus_reduce" in t["task_id"] and _is_final(tasks, t)]
    states = {}
    for t in finals:
        states[t["source"]] = outputs[t["task_id"]]["output"]
    tot_in = sum(r["input_tokens"] for r in outputs.values())
    tot_out = sum(r["output_tokens"] for r in outputs.values())
    tot_s = sum(r["seconds"] for r in outputs.values())
    n_missing = sum(1 for t in tasks if t["task_id"] not in outputs)
    receipt = {
        "schema": "ORION.A2.P11CompilationReceipt.v1",
        "finalized_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "compiler_identity": "llama3.1-8b-ollama (FIXED local compiler; temp 0.6 top_p 0.9 seed 42)",
        "topology": {
            "v1": "map per session -> reduce groups<=10 -> final per question-haystack",
            "v2": "map per <=24k-est-token trajectory segment -> per-trajectory reduce -> corpus reduce groups<=20 -> final per corpus",
            "num_ctx": {"map": MAP_NUM_CTX, "reduce": REDUCE_NUM_CTX},
        },
        "tasks_total": len(tasks), "tasks_done": len(outputs), "tasks_missing": n_missing,
        "compile_input_tokens": tot_in, "compile_output_tokens": tot_out,
        "compile_wall_s_serial_sum": round(tot_s, 1),
        "states": {k: {"n_chars": len(v), "sha256": H(v)} for k, v in sorted(states.items())},
        "state_files": {},
    }
    st_dir = BASE / "compiled_state"
    st_dir.mkdir(exist_ok=True)
    for k, v in sorted(states.items()):
        fp = st_dir / (k.replace("/", "__") + ".txt")
        fp.write_text(v)
        receipt["state_files"][k] = {"path": str(fp), "sha256": H(v), "n_chars": len(v)}
    out = RECEIPTS / "COMPILATION_RECEIPT_V1.json"
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True))
    print(json.dumps({"receipt": str(out), "states": len(states),
                      "tasks_missing": n_missing,
                      "compile_in_tok": tot_in, "compile_out_tok": tot_out}, indent=2))
    return 0 if n_missing == 0 and len(states) >= 26 else 1


def _is_final(tasks: list[dict], t: dict) -> bool:
    return not any(t["task_id"] in other.get("input_task_ids", []) for other in tasks)


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("plan")
    w = sub.add_parser("work")
    w.add_argument("--port", type=int, default=11434)
    w.add_argument("--poll-s", type=int, default=5)
    w.add_argument("--idle-exit-s", type=int, default=600)
    sub.add_parser("finalize")
    a = ap.parse_args()
    if a.cmd == "plan":
        return cmd_plan()
    if a.cmd == "work":
        return run_worker(a.port, a.poll_s, a.idle_exit_s)
    return cmd_finalize()


if __name__ == "__main__":
    sys.exit(main())
