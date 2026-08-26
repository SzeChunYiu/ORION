"""P12 campaign — GENERATION process. Never reads gold.

Runs one episode per task family per arm per model family, following the
allocation frozen in P12_CAMPAIGN_PREREG_V1.md. Writes candidate programs only.

Scoring is a SEPARATE process (p12_score.py) because the eval scripts must read
benchmark/eval_programs/gold_results/, which this process must not. Splitting
them is what makes the guard real rather than decorative: this process cannot
reach gold even by accident, and the scorer never sees a prompt.
"""
from __future__ import annotations
import csv, json, statistics, sys, time
from collections import defaultdict
from pathlib import Path

BENCH = Path("/projects/hep/fs10/scratch/scyiu/sab_benchmark/benchmark")
CSV = Path("/home/scyiu/orion-work/sab/ScienceAgentBench.csv")
OUT = Path("/projects/hep/fs10/scratch/scyiu/p12_stopgo/episodes")
EXCLUDED = {3, 32, 46, 53, 54, 84}
DENIED = ("gold_programs", "scoring_rubrics", "gold_results")

MODELS = {
    "Qwen": "/home/scyiu/orion-work/models/qwen2.5-1.5b-instruct-q4_k_m.gguf",
    "Llama": "/home/scyiu/orion-work/models/Llama-3.2-3B-Instruct-Q4_K_M.gguf",
}
ACTIONS = {
    "A_RETAIN_MINIMAL": {"state": 0, "reason": 0},
    "A_STATE_MAX": {"state": 2, "reason": 0},
    "A_REASON_MAX": {"state": 0, "reason": 2},
    "A_BALANCED": {"state": 1, "reason": 1},
}
ARMS = ("ADAPTIVE", "ONE_SIGNAL_STATE", "ONE_SIGNAL_REASON")


class GoldLeak(RuntimeError): ...


def guard(path: Path) -> Path:
    hit = set(Path(path).parts) & set(DENIED)
    if hit:
        raise GoldLeak(f"generation attempted to read {sorted(hit)}: {path}")
    return path


def multiplicity(r): return len([s for s in r["subtask_categories"].split(",") if s.strip()])


def difficulty_priors(rows):
    by = defaultdict(list)
    for r in rows:
        by[r["subtask_categories"]].append(len(r["task_inst"]) + len(r["domain_knowledge"]))
    med = {f: statistics.median(v) for f, v in by.items()}
    vals = sorted(med.values())
    lo, hi = vals[len(vals)//3], vals[2*len(vals)//3]
    return {f: ("LOW" if m <= lo else "HIGH" if m >= hi else "MID") for f, m in med.items()}


def action_for(arm, mult, mult_med, diff):
    hm, hd = mult >= mult_med, diff == "HIGH"
    if arm == "ONE_SIGNAL_STATE": return "A_STATE_MAX" if hm else "A_RETAIN_MINIMAL"
    if arm == "ONE_SIGNAL_REASON": return "A_REASON_MAX" if hd else "A_RETAIN_MINIMAL"
    if hm and hd: return "A_BALANCED"
    if hm: return "A_STATE_MAX"
    if hd: return "A_REASON_MAX"
    return "A_RETAIN_MINIMAL"


def build_prompt(row, action):
    """Action units become prompt structure. Identical terminal step for all arms."""
    a = ACTIONS[action]
    parts = ["You are a scientific coding assistant. Write one complete Python program.\n"]
    for _ in range(a["state"]):
        parts.append("First restate the input data layout and the exact output file required.\n")
    for _ in range(a["reason"]):
        parts.append("Think step by step about the analysis before writing code.\n")
    parts.append(f"\nTask: {row['task_inst']}\n")
    if row["domain_knowledge"].strip():
        parts.append(f"\nDomain notes: {row['domain_knowledge'][:600]}\n")
    parts.append(f"\nData is under: benchmark/datasets/\nWrite the result to: {row['output_fname']}\n")
    # common terminal rule: identical closing instruction across every arm
    parts.append("\nRespond with Python code only.\n```python\n")
    return "".join(parts)


def main() -> int:
    try:
        guard(BENCH / "gold_programs" / "x.py")
    except GoldLeak:
        pass
    else:
        print("FATAL: guard did not fire", file=sys.stderr); return 2

    rows = [r for r in csv.DictReader(CSV.open()) if int(r["instance_id"]) not in EXCLUDED]
    prior = difficulty_priors(rows)
    mult_med = statistics.median([multiplicity(r) for r in rows])

    # one episode per family: the protocol's inference unit is task_family
    per_family = {}
    for r in rows:
        per_family.setdefault(r["subtask_categories"], r)
    chosen = list(per_family.values())
    OUT.mkdir(parents=True, exist_ok=True)

    from llama_cpp import Llama
    for fam_name, model_path in MODELS.items():
        t0 = time.time()
        llm = Llama(model_path=model_path, n_ctx=4096, n_threads=32, verbose=False)
        print(f"[{fam_name}] loaded in {time.time()-t0:.0f}s", flush=True)
        for r in chosen:
            m, d = multiplicity(r), prior[r["subtask_categories"]]
            for arm in ARMS:
                act = action_for(arm, m, mult_med, d)
                key = f"{fam_name}__{arm}__{r['instance_id']}"
                dest = OUT / f"{key}.json"
                if dest.exists():
                    continue
                t1 = time.time()
                o = llm(build_prompt(r, act), max_tokens=1600, temperature=0.0, stop=["```"])
                dest.write_text(json.dumps({
                    "model_family": fam_name, "arm": arm, "action": act,
                    "instance_id": r["instance_id"], "domain": r["domain"],
                    "family": r["subtask_categories"], "output_fname": r["output_fname"],
                    "eval_script_name": r["eval_script_name"],
                    "gen_seconds": round(time.time()-t1, 1),
                    "completion_tokens": o["usage"]["completion_tokens"],
                    "program": o["choices"][0]["text"],
                }, indent=2) + "\n")
                print(f"  {key} act={act} {time.time()-t1:.0f}s", flush=True)
    print("GENERATION_COMPLETE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
