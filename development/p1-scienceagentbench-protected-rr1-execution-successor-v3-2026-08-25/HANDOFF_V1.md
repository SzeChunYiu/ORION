# Paper 1 protected RR1 successor V3 operator handoff

## Status

This is a receipt-bound handoff for additive lane `development/p1-scienceagentbench-protected-rr1-execution-successor-v3-2026-08-25` at base `bbc73f0860b1b76a2c4fe4449f7a30d0866cb247`.
The packet is `FROZEN_REPAIRED_NOT_RESUBMITTED`; repository text alone is not a
live result or scientific authority.

Fresh immutable paths:

```text
ROOT=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-exec-successor-v3-20260825
RUN=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v3-20260825
```

Never reuse the V1 or V2 run roots. Preserve the failed V2 deployment staging
directory and every prior body-free failure receipt.

## Pre-deployment gates

1. Fetch current `main` and verify the PR head and base have not moved.
2. Verify every V1/V2 predecessor hash in `FINALIZER_CONTRACT_V3.json`.
3. Run `bash -n` on the V3 trampoline.
4. Run `validate_protected_rr1_one_tuple_finalizer_v3.py` under normal, `-O`,
   and `-I -S`; require exact V3 synthetic PASS markers.
5. Verify `SHA256SUMS`, the body-free export manifest, and the synthetic receipt.
6. Confirm the V3 ROOT and RUN are absent.
7. Build a new 60-file snapshot: 49 predecessor files plus 11 V3 files; 15
   subordinate directories; 57 files mode `0400`; three launchers/trampolines
   mode `0500`; root/directories mode `0500`; zero symlinks or special files.
8. Produce and retain the sorted combined manifest and archive SHA-256 before
   any submission.

## Loader discriminator

The deployment host must reverify:

```text
/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/lib/libpython3.11.so.1.0
canonical=/lunarc/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/lib/libpython3.11.so.1.0
bytes=22160208 mode=0755 uid=1400 gid=1400 nlink=1
sha256=398cbf957b8584d4e06ce374b888555149d517ea1037f7ca44d62f855a5b83c5
/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/lib mode=0755 uid=1400 gid=1400 nlink=4
exact top-level entries=libpython3.11.so,libpython3.11.so.1.0,libpython3.so,pkgconfig,python3.11
libpython3.11.so -> libpython3.11.so.1.0
libpython3.so bytes=15352 mode=0755 uid=1400 gid=1400 nlink=1
libpython3.so sha256=9ce9dfd0670cd9e05cdee0478b0a82425b1fd45abe7bdef807a4e7ba2a331f93
```

Clean-environment Python without the library path must reproduce exit `127`;
the same command with the exact single-directory `LD_LIBRARY_PATH` must exit
zero with the exact body-free marker. The deployed trampoline's probe must then
exit zero with exactly zero merged stdout/stderr bytes. Any directory custody,
top-level namespace, library, ABI file, tool, output, or source-self-binding
drift stops deployment.

## Private parent creation

With `umask 077`, create only the fresh RUN and these mode-`0700` directories:

```text
$RUN/runtime-parent
$RUN/capture-parent
$RUN/final-parent
$RUN/logs
```

The three child output roots must not exist.

## Exact submission and capture shape

Run from `ROOT` with:

```bash
umask 077
set -Eeuo pipefail
set -o noclobber
unset BASH_ENV ENV PYTHONPATH PYTHONHOME PYTHONSTARTUP LD_PRELOAD
export LD_LIBRARY_PATH=/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/lib
cd /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-exec-successor-v3-20260825

sbatch --parsable \
  --export=NIL \
  --output=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v3-20260825/logs/slurm-%j.out \
  --error=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v3-20260825/logs/slurm-%j.err \
  /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-exec-successor-v3-20260825/development/p1-scienceagentbench-protected-rr1-execution-successor-v3-2026-08-25/run_protected_rr1_direct_execution_trampoline_v3.sh \
  --masked-packet /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/private-inputs/MASKED_PACKET.json \
  --recovered-packet /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/private-inputs/RECOVERED_PACKET.json \
  --model /projects/hep/fs10/scratch/scyiu/orion_p1_sab_exact_model_v1_20260824/model/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf \
  --llama-server /sw/pkg/ollama/0.32.14/lib/ollama/llama-server \
  --cuda-backend /sw/pkg/ollama/0.32.14/lib/ollama/cuda_v13/libggml-cuda.so \
  --output-root /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v3-20260825/runtime-parent/evidence \
  > /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v3-20260825/logs/SBATCH_STDOUT_V1.txt \
  2> /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v3-20260825/logs/SBATCH_STDERR_V1.txt
```

Require the sbatch stderr file to be a regular non-symlink mode-`0600` empty
file. Parse the exact one-line positive decimal job ID using:

```bash
/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3 -I -S \
  /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-exec-successor-v3-20260825/development/p1-scienceagentbench-protected-rr1-execution-successor-v3-2026-08-25/protected_rr1_one_tuple_finalizer_v3.py \
  parse-sbatch-job-id --input-path /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v3-20260825/logs/SBATCH_STDOUT_V1.txt \
  > /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v3-20260825/logs/PARSE_SBATCH_JOB_ID_STDOUT_V1.txt \
  2> /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v3-20260825/logs/PARSE_SBATCH_JOB_ID_STDERR_V1.txt
```

Require parser exit zero, empty mode-`0600` parser stderr, one canonical decimal
line with exactly one LF, and EOF. Pass that unchanged job ID immediately to:

```bash
/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3 -I -S \
  /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-exec-successor-v3-20260825/development/p1-scienceagentbench-protected-rr1-execution-successor-v3-2026-08-25/protected_rr1_one_tuple_finalizer_v3.py \
  watch-capture --job-id "$JOBID" \
  --output-root /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v3-20260825/capture-parent/capture
```

Only after exact job and watcher success terminals may the operator run:

```bash
/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3 -I -S \
  /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-exec-successor-v3-20260825/development/p1-scienceagentbench-protected-rr1-execution-successor-v3-2026-08-25/protected_rr1_one_tuple_finalizer_v3.py \
  finalize \
  --evidence-root /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v3-20260825/runtime-parent/evidence \
  --capture-root /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v3-20260825/capture-parent/capture \
  --output-root /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v3-20260825/final-parent/result
```

## Hard stops

Stop on any nonzero command, output-root reuse, missing/different exact terminal,
CANNOT_CHECK, `LD_LIBRARY_PATH`/library/tool drift, unexpected `LD_PRELOAD`,
raw or normalized source drift, wrong job identity, wrong partition/GRES,
scheduler config missing/empty/duplicate/case-aliased required-key drift,
non-overlap failure, runtime evidence drift, process drift, or cleanup drift.

Do not relax missing `GresDetail` for a candidate successful job. Do not treat
job `3537828`'s downstream watcher CANNOT_CHECK as its primary failure; its
primary result is the exact pre-Python loader exit `127`.

## Retry accounting

Before a repaired retry:

```text
prior scheduler GPU-seconds=2
prior generation attempts consumed=0
next infrastructure submission ordinal=3
repaired generation ordinal=1
hidden second sample=false
```

A further infrastructure failure remains a result to diagnose and certify; it
is never rewritten as positive. A successful generation still requires exact
post-job capture and finalization before any scientific interpretation.

## Scientific boundary

Even complete V3 success is one protected tuple only. It does not authorize the
918-tuple campaign, official evaluator, task execution, production admission,
or a broad superiority claim. Those decisions require their own receipts and
predeclared gates.
