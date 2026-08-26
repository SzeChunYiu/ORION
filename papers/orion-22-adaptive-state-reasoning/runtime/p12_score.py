"""P12 campaign — SCORING process. Reads gold; never sees a prompt.

Runs each generated program in an isolated working directory, then runs the
task's eval script against whatever it produced. The eval scripts legitimately
read benchmark/eval_programs/gold_results/, which is exactly why this is a
separate process from generation: the generator is guarded against gold, and
the scorer is guarded against prompts.

An episode that crashes is an OUTCOME (score 0), not a missing datum. Dropping
crashes would silently select for arms whose programs happen to run.
"""
from __future__ import annotations
import json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

BENCH = Path("/projects/hep/fs10/scratch/scyiu/sab_benchmark/benchmark")
EPI = Path("/projects/hep/fs10/scratch/scyiu/p12_stopgo/episodes")
OUT = Path("/projects/hep/fs10/scratch/scyiu/p12_stopgo/scores")
PY_BIN = "/home/scyiu/orion-work/venv/bin/python"
TIMEOUT = 180


def score_one(ep: dict, workdir: Path) -> dict:
    prog = workdir / "candidate.py"
    prog.write_text(ep["program"])
    # datasets must be reachable at the relative path the tasks name
    (workdir / "benchmark").mkdir(exist_ok=True)
    ds = workdir / "benchmark" / "datasets"
    if not ds.exists():
        os.symlink(BENCH / "datasets", ds)
    (workdir / "pred_results").mkdir(exist_ok=True)

    run = subprocess.run([PY_BIN, "candidate.py"], cwd=workdir,
                         capture_output=True, text=True, timeout=TIMEOUT)
    produced = (workdir / ep["output_fname"]).exists()

    evalp = BENCH / "eval_programs" / ep["eval_script_name"]
    ev_ok, ev_val, ev_err = False, None, ""
    if produced and evalp.is_file():
        shutil.copy(evalp, workdir / "eval.py")
        # eval scripts read benchmark/eval_programs/gold_results relatively
        egp = workdir / "benchmark" / "eval_programs"
        if not egp.exists():
            os.symlink(BENCH / "eval_programs", egp)
        try:
            r = subprocess.run(
                [PY_BIN, "-c", "import eval as e; print(e.eval())"],
                cwd=workdir, capture_output=True, text=True, timeout=TIMEOUT)
            ev_ok = r.returncode == 0
            ev_val = r.stdout.strip()[:200]
            ev_err = r.stderr.strip()[-200:]
        except subprocess.TimeoutExpired:
            ev_err = "eval timeout"
    return {
        "model_family": ep["model_family"], "arm": ep["arm"], "action": ep["action"],
        "instance_id": ep["instance_id"], "domain": ep["domain"], "family": ep["family"],
        "program_ran": run.returncode == 0,
        "program_stderr_tail": run.stderr.strip()[-200:],
        "produced_output": produced,
        "eval_ran": ev_ok, "eval_value": ev_val, "eval_stderr_tail": ev_err,
        # outcome: eval executed cleanly on a produced artifact
        "outcome": 1.0 if (produced and ev_ok) else 0.0,
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    eps = sorted(EPI.glob("*.json"))
    print(f"episodes to score: {len(eps)}", flush=True)
    for f in eps:
        dest = OUT / f.name
        if dest.exists():
            continue
        ep = json.loads(f.read_text())
        with tempfile.TemporaryDirectory(dir="/tmp") as td:
            try:
                res = score_one(ep, Path(td))
            except subprocess.TimeoutExpired:
                res = {"model_family": ep["model_family"], "arm": ep["arm"],
                       "action": ep["action"], "instance_id": ep["instance_id"],
                       "domain": ep["domain"], "family": ep["family"],
                       "program_ran": False, "produced_output": False,
                       "eval_ran": False, "outcome": 0.0,
                       "program_stderr_tail": "candidate timeout"}
            except Exception as exc:  # a crash is an outcome, not a gap
                res = {"model_family": ep["model_family"], "arm": ep["arm"],
                       "action": ep["action"], "instance_id": ep["instance_id"],
                       "domain": ep["domain"], "family": ep["family"],
                       "program_ran": False, "produced_output": False,
                       "eval_ran": False, "outcome": 0.0,
                       "program_stderr_tail": f"{type(exc).__name__}: {exc}"[:200]}
        dest.write_text(json.dumps(res, indent=2) + "\n")
        print(f"  {f.stem} outcome={res['outcome']} ran={res.get('program_ran')} "
              f"produced={res.get('produced_output')}", flush=True)
    print("SCORING_COMPLETE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
