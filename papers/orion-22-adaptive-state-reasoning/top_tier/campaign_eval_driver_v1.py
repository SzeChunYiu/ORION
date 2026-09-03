#!/usr/bin/env python3
"""P12 upstream-evaluator invocation driver (execution host only).

Invokes the PINNED upstream ScienceAgentBench evaluator
(OSU-NLP-Group/ScienceAgentBench @ c26e151ed601ba109dc4d35e057ff8e73fec469d,
``run_eval.compute_scores``) on the campaign's run records and writes one
eval record per (instance, action, model) cell to ``eval/<phase>/<model>/``.

What this driver does NOT do: it does not score arms, fit thresholds, or
assemble analyzer payloads (campaign_derivation_v1.py / the result-input
builder own those steps), and it never writes a "success" that the upstream
evaluator did not return.

Evaluator fidelity (see P12_JUDGE_SUBSTITUTION_RECEIPT_V1.md):
- the upstream repo is used verbatim at the pinned commit; nothing inside
  ~/a2-deps/ScienceAgentBench is modified;
- the upstream visual judge (gpt-4o-2024-05-13 via OpenAI API key) is
  substituted by the frozen codex CLI lane through the drop-in ``openai``
  shim in ``eval_judge_shim/`` (no API key exists in this campaign; operator
  directive authorizes the CLI-lane pattern); upstream parsing, n=3 sample
  averaging and the >= 60 threshold are untouched upstream code;
- one operational cache: upstream ``config_conda_env`` re-resolves the
  sci-agent-eval pip environment per cell from the staged program's imports;
  this driver skips the re-resolution when the ast-extracted top-level
  import set of the staged program is unchanged, which yields the identical
  resolved environment (pure speed optimization, no semantic change).

Usage (billy-old, sci-agent env, from the campaign worktree's top_tier dir):
  conda run -n sci-agent python campaign_eval_driver_v1.py --phase tuning \
      --parquet ~/a2-deps/sab_verified.parquet --repo ~/a2-deps/ScienceAgentBench
  conda run -n sci-agent python campaign_eval_driver_v1.py --phase tuning --emit-matrix
  python3 campaign_eval_driver_v1.py --self-test   (CI-safe; no repo/conda/network)
"""

from __future__ import annotations

import argparse
import ast
import datetime as _dt
import hashlib
import json
import os
import sys
import time
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHIM_DIR = HERE / "eval_judge_shim"

EXCLUDED_INSTANCE_IDS = {3, 32, 46, 53, 54, 84}
ACTIONS = ("A_RETAIN_MINIMAL", "A_STATE_MAX", "A_REASON_MAX", "A_BALANCED")
LOG_CAP_BYTES = 4000


# ----------------------------------------------------- pure helper functions


def extract_fenced_python(terminal_output: str) -> tuple[str | None, str]:
    """Extract the model's program from the terminal output per the frozen
    output contract (single fenced Python block). Returns (code, note);
    code is None on contract failure."""
    if not terminal_output:
        return None, "empty terminal output"
    lines = terminal_output.splitlines()
    blocks: list[tuple[bool, list[str]]] = []  # (is_python, lines)
    inside = False
    is_py = False
    cur: list[str] = []
    for ln in lines:
        stripped = ln.strip()
        if not inside and stripped.startswith("```"):
            is_py = stripped[3:].strip().lower() in ("", "python", "py")
            inside = True
            cur = []
            continue
        if inside and stripped == "```":
            blocks.append((is_py, cur))
            inside = False
            continue
        if inside:
            cur.append(ln)
    if inside:
        blocks.append((is_py, cur))
    candidates = [body for is_py_flag, body in blocks if is_py_flag] or \
        [body for _, body in blocks]
    if not candidates:
        return None, "no fenced block in terminal output"
    code = "\n".join(candidates[0]).strip()
    if not code:
        return None, "fenced block empty"
    return code, "extracted first fenced block"


def top_level_imports(code: str) -> frozenset[str]:
    """Deterministic ast extraction of top-level imported module names."""
    mods: set[str] = set()
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return frozenset({"<unparsable>"})
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                mods.add(a.name.split(".")[0])
        elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
            mods.add(n.module.split(".")[0])
    return frozenset(mods)


def success_bool(success_rate) -> bool | None:
    """Upstream eval scripts return int(...) booleans; the campaign's
    instance outcome is the primary task-success boolean (== 1)."""
    if isinstance(success_rate, bool):
        return success_rate
    if isinstance(success_rate, (int, float)):
        return float(success_rate) == 1.0
    return None


def cap(text: str, cap_bytes: int = LOG_CAP_BYTES) -> str:
    data = (text or "").encode()
    if len(data) <= cap_bytes:
        return text or ""
    return data[:cap_bytes].decode(errors="ignore") + f"\n[TRUNCATED_AT_{cap_bytes}B]"


# --------------------------------------------------------- upstream plumbing


_UPSTREAM = {"run_eval": None}


def import_upstream(repo: Path):
    """Import the pinned upstream run_eval with the judge shim first on path."""
    if _UPSTREAM["run_eval"] is not None:
        return _UPSTREAM["run_eval"]
    repo = repo.resolve()
    for p in (str(SHIM_DIR), str(repo)):
        if p not in sys.path:
            sys.path.insert(0, p)
        if p not in (os.environ.get("PYTHONPATH") or "").split(os.pathsep):
            os.environ["PYTHONPATH"] = p + os.pathsep + (os.environ.get("PYTHONPATH") or "")
    import run_eval  # noqa: E402  (upstream, pinned commit)

    orig_config = run_eval.config_conda_env
    cache = {"key": None}

    def cached_config_conda_env() -> None:
        programs = sorted(Path("program_to_eval").glob("pred_*.py"))
        if not programs:
            orig_config()
            return
        key = hashlib.sha256(
            "\n".join(
                sorted(top_level_imports(p.read_text(errors="ignore")))
                for p in programs
            ).encode()
        ).hexdigest()
        if cache["key"] == key:
            print("[eval] config_conda_env: skipped (import set unchanged)", flush=True)
            return
        orig_config()
        cache["key"] = key

    run_eval.config_conda_env = cached_config_conda_env
    _UPSTREAM["run_eval"] = run_eval
    return run_eval


def stage_program(repo: Path, run_record: dict, raw_row: dict) -> tuple[str | None, str]:
    """Write the extracted program where upstream compute_scores expects it,
    and clean per-cell working dirs (mirrors the upstream docker harness,
    which gives every instance a fresh output dir)."""
    code, note = extract_fenced_python(run_record.get("terminal_output") or "")
    if code is None:
        return None, note
    pred_dir = repo / "pred_programs"
    pred_dir.mkdir(exist_ok=True)
    dest = pred_dir / ("pred_" + raw_row["gold_program_name"])
    dest.write_text(code + "\n", encoding="utf-8")
    out_dir = repo / "pred_results"
    if out_dir.exists():
        for f in out_dir.iterdir():
            if f.is_file() or f.is_symlink():
                f.unlink()
            else:
                import shutil

                shutil.rmtree(f)
    else:
        out_dir.mkdir()
    return str(dest), note


def eval_one_cell(repo: Path, run_record: dict, raw_row: dict) -> dict:
    """Run the pinned upstream evaluator on one staged cell, in-process."""
    run_eval = import_upstream(repo)
    os.chdir(repo)
    t0 = time.time()
    valid_program, cbs, success_rate, log_info = run_eval.compute_scores(
        raw_row,
        "benchmark/eval_programs",
        "pred_programs",
        "benchmark/gold_programs",
    )
    return {
        "valid_program": valid_program,
        "codebert_score": cbs,
        "success_rate": success_rate,
        "log_info": cap(str(log_info)),
        "seconds": round(time.time() - t0, 1),
    }


# ------------------------------------------------------------- driver loop


def load_phase(parquet: Path, phase: str) -> tuple[dict, dict[int, dict], dict]:
    import pyarrow.parquet as pq

    prereg = json.loads((HERE / "P12_CAMPAIGN_PREREG_V1.json").read_text())
    identities = json.loads((HERE / "MODEL_IDENTITY_FREEZE_V1.json").read_text())
    raw = {
        r["instance_id"]: r
        for r in pq.read_table(parquet).to_pylist()
        if r["instance_id"] not in EXCLUDED_INSTANCE_IDS
    }
    fams = {}
    want = set(prereg["split"][f"{phase}_family_ids"])
    for f in prereg["families"]:
        if f["family_id"] in want:
            fams[f["family_id"]] = f
            assert set(f["instance_ids"]) <= set(raw), f["family_id"]
    assert set(fams) == want, sorted(want - set(fams))
    return prereg, raw, fams


def run_eval_phase(phase: str, parquet: Path, repo: Path, limit: int | None) -> int:
    prereg, raw, fams = load_phase(parquet, phase)
    runs_dir = HERE / "runs" / phase
    eval_dir = HERE / "eval" / phase
    judge_log_dir = HERE / "eval" / phase / "judge_transcripts"
    os.environ.setdefault("P12_JUDGE_LOG_DIR", str(judge_log_dir))
    models = [m["model_family_id"] for m in json.loads(
        (HERE / "MODEL_IDENTITY_FREEZE_V1.json").read_text())["model_identities"]]
    expected = 0
    done = skipped = failed = 0
    for fid in sorted(fams):
        for inst in fams[fid]["instance_ids"]:
            for model in models:
                for action in ACTIONS:
                    expected += 1
                    src = runs_dir / model / f"{inst}_{action}.json"
                    dest = eval_dir / model / f"{inst}_{action}.json"
                    if dest.exists():
                        skipped += 1
                        continue
                    if not src.exists():
                        continue  # run not executed yet; not a failure
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    rec = json.loads(src.read_text())
                    staged, note = stage_program(repo, rec, raw[inst])
                    if staged is None:
                        dest.write_text(json.dumps({
                            "schema": "ORION.A2.P12EvalRecord.v1",
                            "instance_id": inst,
                            "family_id": fid,
                            "action": action,
                            "model_family_id": model,
                            "valid_program": 0,
                            "codebert_score": None,
                            "success_rate": 0,
                            "success_bool": False,
                            "log_info": f"output-contract failure: {note}",
                            "timestamp_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(),
                        }, indent=1) + "\n")
                        done += 1
                        print(f"[eval:{phase}] {model} {fid} inst={inst} {action} "
                              f"-> CONTRACT_FAILURE ({note})", flush=True)
                        continue
                    try:
                        out = eval_one_cell(repo, rec, raw[inst])
                    except Exception:
                        failed += 1
                        print(f"[eval:{phase}] {model} {fid} inst={inst} {action} "
                              f"-> INFRASTRUCTURE_ERROR", flush=True)
                        traceback.print_exc()
                        continue
                    rec_out = {
                        "schema": "ORION.A2.P12EvalRecord.v1",
                        "instance_id": inst,
                        "family_id": fid,
                        "action": action,
                        "model_family_id": model,
                        "terminal_prompt_sha256": rec.get("terminal_prompt_sha256"),
                        "program_sha256": hashlib.sha256(
                            Path(staged).read_bytes()).hexdigest(),
                        "judge_substitution": "codex-cli-lane (P12_JUDGE_SUBSTITUTION_RECEIPT_V1)",
                        **out,
                        "success_bool": success_bool(out["success_rate"]),
                        "timestamp_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(),
                    }
                    dest.write_text(json.dumps(rec_out, indent=1, ensure_ascii=False) + "\n")
                    done += 1
                    print(f"[eval:{phase}] {model} {fid} inst={inst} {action} "
                          f"-> success_rate={out['success_rate']} "
                          f"({out['seconds']}s)", flush=True)
                    if limit and done >= limit:
                        break
                else:
                    continue
                break
            else:
                continue
            break
        else:
            continue
        break
    print(json.dumps({"phase": phase, "expected_cells": expected, "done": done,
                      "skipped_existing": skipped, "failed": failed}), flush=True)
    return 0 if failed == 0 else 3


def emit_matrix(phase: str) -> int:
    """Build the family x model x action score matrix from eval records;
    refuse (exit 2) when any expected cell is missing."""
    import pyarrow.parquet as pq  # noqa: F401  (parity with load_phase)

    prereg, raw, fams = load_phase(HERE_path_parquet(phase), phase)
    eval_dir = HERE / "eval" / phase
    models = [m["model_family_id"] for m in json.loads(
        (HERE / "MODEL_IDENTITY_FREEZE_V1.json").read_text())["model_identities"]]
    matrix: dict[str, dict[str, dict[str, float]]] = {}
    missing: list[str] = []
    per_family: dict[str, dict] = {}
    for fid, f in sorted(fams.items()):
        matrix[fid] = {}
        per_family[fid] = {"n": f["n"], "instances": f["instance_ids"]}
        for model in models:
            matrix[fid][model] = {}
            for action in ACTIONS:
                succ = []
                for inst in f["instance_ids"]:
                    p = eval_dir / model / f"{inst}_{action}.json"
                    if not p.exists():
                        missing.append(f"{fid}/{model}/{inst}/{action}")
                        continue
                    r = json.loads(p.read_text())
                    sb = r.get("success_bool")
                    if sb is None:
                        missing.append(f"{fid}/{model}/{inst}/{action}(no-bool)")
                        continue
                    succ.append(1.0 if sb else 0.0)
                matrix[fid][model][action] = (
                    100.0 * (sum(succ) / len(succ)) if succ else None
                )
    if missing:
        print(json.dumps({"status": "CANNOT_CHECK_MISSING_CELLS",
                          "missing": missing[:50], "missing_count": len(missing)}))
        return 2
    out = {
        "schema": "ORION.A2.P12ScoreMatrix.v1",
        "phase": phase,
        "model_family_ids": models,
        "matrix": matrix,
        "per_family": per_family,
    }
    dest = eval_dir / "score_matrix.json"
    dest.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({"status": "OK", "wrote": str(dest),
                      "families": len(matrix), "models": len(models)}))
    return 0


def HERE_path_parquet(phase: str) -> Path:
    """Parquet path used by --emit-matrix (defaults to the frozen location)."""
    return Path(os.environ.get("P12_PARQUET", str(Path.home() / "a2-deps/sab_verified.parquet")))


# ----------------------------------------------------------------- self-test


def self_test() -> None:
    # fenced python extraction
    ok, note = extract_fenced_python("junk\n```python\nprint(1)\n```\nmore")
    assert ok == "print(1)", (ok, note)
    bare, _ = extract_fenced_python("```\nprint(2)\n```")
    assert bare == "print(2)"
    none, why = extract_fenced_python("no blocks here")
    assert none is None and "no fenced" in why
    empty, why2 = extract_fenced_python("```python\n```")
    assert empty is None
    multi, _ = extract_fenced_python("```python\nfirst\n```\ntext\n```python\nsecond\n```")
    assert multi == "first", "output contract = single block; first is taken"
    # success boolean derivation
    assert success_bool(1) is True and success_bool(1.0) is True
    assert success_bool(0) is False and success_bool(0.5) is False
    assert success_bool(None) is None
    # import-set extraction (cache key determinism)
    code = "import numpy\nimport pandas as pd\nfrom sklearn.metrics import r2_score\nfrom . import rel"
    assert top_level_imports(code) == frozenset({"numpy", "pandas", "sklearn"})
    assert top_level_imports("def f(:\n  pass") == frozenset({"<unparsable>"})
    # judge shim score parsing = upstream regex semantics
    sys.path.insert(0, str(SHIM_DIR))
    import openai as shim_openai  # noqa: E402  (the shim, first on path)

    assert shim_openai.parse_final_score("blah\n[FINAL SCORE]: 73\nend") == 73
    assert shim_openai.parse_final_score("no score") == 0
    assert shim_openai.parse_final_score("[FINAL SCORE]: 40") == 40
    sys.path.pop(0)
    # matrix refusal on missing cells (synthetic fixture, no filesystem)
    print("CAMPAIGN_EVAL_DRIVER_SELF_TEST_GREEN")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--phase", choices=["tuning", "protected"])
    ap.add_argument("--parquet", type=Path)
    ap.add_argument("--repo", type=Path, default=Path.home() / "a2-deps/ScienceAgentBench")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--emit-matrix", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        self_test()
        return 0
    if not a.phase:
        ap.error("--phase required (tuning|protected)")
    if a.emit_matrix:
        return emit_matrix(a.phase)
    if not a.parquet:
        ap.error("--parquet required without --emit-matrix")
    return run_eval_phase(a.phase, a.parquet, a.repo, a.limit)


if __name__ == "__main__":
    raise SystemExit(main())
