#!/bin/bash
# ORION-19 / P9-U-T3 -- checkpoint custody + execution-environment bootstrap.
#
# WHAT BLOCKER THIS ATTACKS
# -------------------------
# P9_U_T3_FRONTIER_GRID_STATUS_2026-08-21.json records outcome CANNOT_CHECK with
# 0 of 1344 declared cells executed, and names the cause precisely:
#     "open_weight_checkpoint_present": false
#     "outbound_provider_access": "proxy returns 403 to CONNECT for external providers"
# The freeze doc adds that substituting a classical-learner capacity ladder for a
# model-scale ladder "would be a weaker proxy dressed as the measurement, and is
# refused here".
#
# This job does NOT execute grid cells and produces NO scientific result. It
# removes the environmental half of the blocker and records, with digests,
# exactly which of the six declared (F,S) ladder points become executable in
# custody. Anything it cannot obtain is recorded as CANNOT_CHECK with its
# reason -- never as absent-and-fine.
#
# LADDER DECLARED BY THE FREEZE (P9_U_T3_FRONTIER_GRID_FREEZE_2026-08-21.md 2.3)
#   QWEN2_5 : 0.5B -> 1.5B -> 3B -> 7B      (ungated on the hub)
#   LLAMA3_2: 1B -> 3B                       (gated; needs an accepted licence)
#
#SBATCH --job-name=o19-ut3-custody
#SBATCH --account=lu2026-2-51
#SBATCH --partition=gpua40
#SBATCH --gres=gpu:a40:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=06:00:00
#SBATCH --output=/projects/hep/fs9/scratch/scyiu-orion-ci/ut3-custody-logs/%x-%j.out
#SBATCH --error=/projects/hep/fs9/scratch/scyiu-orion-ci/ut3-custody-logs/%x-%j.err

set -uo pipefail
LOGDIR=/projects/hep/fs9/scratch/scyiu-orion-ci/ut3-custody-logs
VENV=/projects/hep/fs9/scratch/scyiu-orion-ci/ut3-venv
STORE=/projects/hep/fs9/scratch/scyiu-orion-ci/ut3-checkpoints
mkdir -p "$LOGDIR" "$STORE"

module purge
module load GCC/13.2.0 Python/3.11.5 CUDA/12.6.0 2>/dev/null || module load Python/3.11.5 2>/dev/null || true

if [ ! -x "$VENV/bin/python" ]; then
  python3 -m venv "$VENV"
fi
PY="$VENV/bin/python"
"$PY" -m pip install -q --upgrade pip
"$PY" -m pip install -q torch --index-url https://download.pytorch.org/whl/cu126 || \
  "$PY" -m pip install -q torch
"$PY" -m pip install -q transformers accelerate huggingface_hub safetensors sentencepiece

export HF_HOME="$STORE/hf"
# keep every cache off $HOME: the home volume is quota'd and the triton cache
# tripped "Disk quota exceeded" on the first run, which cost the GPU smoke probe.
export TRITON_CACHE_DIR="$STORE/triton"
export XDG_CACHE_HOME="$STORE/xdg"
export TORCHINDUCTOR_CACHE_DIR="$STORE/inductor"
mkdir -p "$HF_HOME" "$TRITON_CACHE_DIR" "$XDG_CACHE_HOME" "$TORCHINDUCTOR_CACHE_DIR"

"$PY" - <<'PYEOF'
import json, os, platform, subprocess, time, traceback
from pathlib import Path

STORE = Path(os.environ["HF_HOME"])
OUT = Path("/projects/hep/fs9/scratch/scyiu-orion-ci/ut3-custody-logs/P9_UT3_CHECKPOINT_CUSTODY_RECEIPT_V1.json")

LADDER = [
    ("QWEN2_5", "0.5B", "Qwen/Qwen2.5-0.5B-Instruct"),
    ("QWEN2_5", "1.5B", "Qwen/Qwen2.5-1.5B-Instruct"),
    ("QWEN2_5", "3B",   "Qwen/Qwen2.5-3B-Instruct"),
    ("QWEN2_5", "7B",   "Qwen/Qwen2.5-7B-Instruct"),
    ("LLAMA3_2", "1B",  "meta-llama/Llama-3.2-1B-Instruct"),
    ("LLAMA3_2", "3B",  "meta-llama/Llama-3.2-3B-Instruct"),
]

import torch
from huggingface_hub import snapshot_download

rows = []
for family, scale, repo in LADDER:
    row = {"family": family, "scale": scale, "repo_id": repo}
    t0 = time.time()
    try:
        p = snapshot_download(repo_id=repo, allow_patterns=[
            "*.json", "*.safetensors", "*.model", "*.txt"])
        files = sorted(Path(p).rglob("*"))
        nbytes = sum(f.stat().st_size for f in files if f.is_file())
        row.update({
            "status": "IN_CUSTODY",
            "local_path": str(p),
            "bytes": nbytes,
            "n_files": sum(1 for f in files if f.is_file()),
            "seconds": round(time.time() - t0, 1),
        })
    except Exception as exc:
        row.update({
            "status": "CANNOT_CHECK",
            "reason": f"{type(exc).__name__}: {exc}"[:400],
            "note": ("not obtained; this is CANNOT_CHECK for this ladder point, "
                     "not evidence that the point is unnecessary or that the grid is fine"),
            "seconds": round(time.time() - t0, 1),
        })
    print(f"[{family} {scale}] {row['status']}", flush=True)
    rows.append(row)

# Smoke: prove the environment can actually decode on the allocated GPU. This is
# an environment probe, NOT a grid cell and NOT a measurement of any model.
smoke = {"attempted": False}
first = next((r for r in rows if r["status"] == "IN_CUSTODY"), None)
if first:
    smoke["attempted"] = True
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        tok = AutoTokenizer.from_pretrained(first["repo_id"])
        mdl = AutoModelForCausalLM.from_pretrained(
            first["repo_id"], torch_dtype=torch.bfloat16, device_map="cuda")
        ids = tok("2 + 2 =", return_tensors="pt").to("cuda")
        t0 = time.time()
        out = mdl.generate(**ids, max_new_tokens=8, do_sample=False)
        smoke.update({
            "status": "GPU_DECODE_OK",
            "repo_id": first["repo_id"],
            "decode_seconds": round(time.time() - t0, 3),
            "output_token_count": int(out.shape[-1]),
        })
    except Exception as exc:
        smoke.update({"status": "CANNOT_CHECK",
                      "reason": f"{type(exc).__name__}: {exc}"[:400]})

in_custody = [r for r in rows if r["status"] == "IN_CUSTODY"]
payload = {
    "schema": "orion.p9.ut3-checkpoint-custody-receipt.v1",
    "paper": "orion-19-structured-epistemic-learning",
    "gate_served": "P9-U-T3",
    "produces_scientific_result": False,
    "claim_authority": "NONE. This is an environment and custody receipt. It executes no grid "
                       "cell, scores no quality, and licenses no statement about S*, C*, or any "
                       "crossing. P9-U-T3 remains BLOCKED until cells carry outcomes.",
    "blocker_halves": {
        "open_weight_checkpoint_present": bool(in_custody),
        "outbound_provider_access": "hub reachable from this venue" if in_custody
                                     else "CANNOT_CHECK",
        "still_missing": "a cell executor: instance generation per (k,B), the seven "
                         "representation renderers, majority-vote aggregation over C, and "
                         "verified-answer scoring. Declared but not built.",
    },
    "ladder_declared": [{"family": f, "scale": s, "repo_id": r} for f, s, r in LADDER],
    "ladder_points_in_custody": len(in_custody),
    "ladder_points_declared": len(LADDER),
    "checkpoints": rows,
    "gpu_smoke": smoke,
    "environment": {
        "python": platform.python_version(),
        "torch": torch.__version__,
        "cuda_available": bool(torch.cuda.is_available()),
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "hostname": platform.node(),
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
    },
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n")
print(json.dumps({k: payload[k] for k in
                  ("ladder_points_in_custody", "ladder_points_declared", "blocker_halves")},
                 indent=1))
print(f"wrote {OUT}")
PYEOF
echo "EXIT: $?"
