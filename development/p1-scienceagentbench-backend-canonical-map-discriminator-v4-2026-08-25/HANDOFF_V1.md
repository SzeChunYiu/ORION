# Paper 1 protected RR1 backend canonical-map discriminator V4 operator handoff

## Status and hard boundary

This is a receipt-bound handoff for additive lane
`development/p1-scienceagentbench-backend-canonical-map-discriminator-v4-2026-08-25`
at merged V3 base `a2fdc2854740dcde0652a17e447d8a9c1328208f`.
The packet is `FROZEN_BODY_FREE_DISCRIMINATOR_NOT_EXECUTED`. Repository text,
synthetic validation, and the prior read-only alias probe are not a live
discriminator PASS.

V4 is scoped for at most one body-free A40 discriminator job if separately
authorized after the frozen contract's required owner review and preconditions.
It does not authorize a protected retry, protected-body access, tokenization,
completion, generation, evaluation, outcome access, production admission, or
the 918-tuple campaign.

Fresh immutable paths are:

```text
ROOT=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-exec-successor-v4-20260825
RUN=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v4-20260825
OUTPUT=$RUN/evidence
LOG=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v4-20260825-submit-logs
```

ROOT, RUN, and LOG were absent at the checkpoint. Recheck ROOT, RUN, OUTPUT,
and LOG immediately before deployment. Never reuse any V1, V2, V3, or
attempted V4 root.

## Adverse predecessor retained exactly

Job `3537893` is `FAILED`, exit `1:0`, elapsed 88 seconds on `cg14`, one A40.
Its primary stderr binding is:

```text
bytes=126
sha256=c2e312de73f990fe41cbe1a078cea8a61d7b50c69d339fc798babf6425c402cb
P1_SAB_PROTECTED_RR1_DIRECT_ROUTE_CANNOT_CHECK detail_sha256=e4d5bcb685476587bb3af200163542287bdfcd92352247f9cc680889ec6f0582
```

The decoded body-free detail is exactly:

```text
PreflightError:staged CUDA backend is not mapped into the live server process
```

Primary stdout is empty with SHA-256
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
`PREFLIGHT_CANNOT_CHECK_V1.json` is 505 bytes with SHA-256
`a4f1f1884c0a22d053c7d452f10ec5bee8ae7ff174a836bec429127c92c01e7f`.

The watcher CANNOT_CHECK is a downstream result, not the primary failure:

```text
failure_code=EVIDENCE_PARSE_INVALID
detail_sha256=1d733d9de0d4dc259545dc0992b1e1f495e9c82d057339fd58b4e90ab849857e
decoded=FinalizationError:captured post-job scontrol -dd lacks required -dd keys
stderr bytes=176 sha256=7218b38260f25767f7691ec5524ccfbf32b0cb555f5cb94b09954f496d1063b5
stdout bytes=0 sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
SCHEDULER_CAPTURE_CANNOT_CHECK_V1.json bytes=15672
sha256=79121b600e49b6f450f0119dca51ff5b72d8a6661a95c354ce9b222bd4e63707
```

Before the staged-runtime failure, V3 opened, validated, and staged both frozen
protected packet bodies (`MASKED_PACKET` and `RECOVERED_PACKET`). No body bytes
are disclosed or retained in this V4 packet, and the V4 audit agents did not
read their content. No protected prompt was sent; no tokenize, completion,
generation, evaluator, or outcome operation occurred. Cumulative protected-job
scheduler cost is 90 GPU-seconds and generation attempts consumed remain zero.
V4 is post-outcome diagnosis only; do not change or promote job `3537893`, and
do not claim that its model was mapped because its backend check failed first.

## Clean-checkout pre-deployment gates

1. Fetch current `main`; require
   `a2fdc2854740dcde0652a17e447d8a9c1328208f` to be the bound V3 predecessor
   and verify the V4 PR head/base have not moved.
2. In an isolated clean checkout, verify the packet manifest and `SHA256SUMS`.
3. Require `bash -n run_backend_canonical_map_discriminator_v1.sh` to pass.
4. Run `validate_backend_canonical_map_discriminator_v1.py` under normal
   Python, `-O`, `-I -S`, and exact `/usr/bin/python3 -I -S`. Require its exact
   synthetic success prefix:

   ```text
   P1_SAB_BACKEND_CANONICAL_MAP_DISCRIMINATOR_V1_SYNTHETIC_VALIDATION_PASS
   ```

   and require `tests=23` plus exact counters
   `protected_bodies=0 tokenize=0 completion=0 generation=0 jobs=0 outcomes=0
   production_admissibility=CANNOT_CHECK scientific_authority=NONE` in all
   four modes.
5. Reverify that the contract freezes the exact server, backend, model, argv,
   loader environment, body-free request allowlist, and one-A40 allocation.
6. Confirm ROOT, RUN, OUTPUT, and LOG are absent. A stale empty directory still
   counts as reuse and stops deployment.
7. Deploy a new read-only snapshot from the clean checkout. Preserve its sorted
   byte/SHA-256 manifest and archive hash before any submission.
8. With `umask 077`, create only LOG mode `0700`. Leave RUN and OUTPUT absent.
   The frozen trampoline atomically creates RUN mode `0700`; only then does the
   core create OUTPUT. The operator must not precreate RUN or OUTPUT.

Any mismatch stops. Do not edit a deployed snapshot in place.

## Runtime identity recheck

Immediately before submission, reverify all three frozen leaves:

```text
server logical=/sw/pkg/ollama/0.32.14/lib/ollama/llama-server
server canonical=/lunarc/sw/pkg/ollama/0.32.14/lib/ollama/llama-server
bytes=15096 mode=0755 uid=424 gid=400 nlink=1
sha256=234b05b2138264f8fb263c3205e85f4c290e8afe5067e280a4f6f90cdac5696b

backend logical=/sw/pkg/ollama/0.32.14/lib/ollama/cuda_v13/libggml-cuda.so
backend canonical=/lunarc/sw/pkg/ollama/0.32.14/lib/ollama/cuda_v13/libggml-cuda.so
bytes=249110896 mode=0755 uid=424 gid=400 nlink=1
sha256=fbe27c15253195c10559d98c6ba9c6d476a65d2bbf0240307b4a46d8aa17cefb

model logical=canonical=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_exact_model_v1_20260824/model/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf
bytes=18556689568 mode=0400 uid=6350 gid=6300 nlink=1
sha256=fadc3e5f8d42bf7e894a785b05082e47daee4df26680389817e2093056f088ad
```

For server and backend, require each logical leaf to resolve to the frozen
canonical leaf and require logical/canonical device plus inode equality. For
the model, require the single frozen path and its custody. Record the fresh
device/inode values in operator-side body-free deployment evidence; do not
substitute historical values.

## Exact body-free submission shape

From ROOT, with `umask 077`, submit exactly one body-free discriminator job:

```bash
if /usr/bin/env | /usr/bin/grep -q '^SBATCH_'; then
  printf '%s\n' 'CANNOT_CHECK: inherited SBATCH_* variable' >&2
  exit 1
fi
sbatch --parsable \
  --chdir=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-exec-successor-v4-20260825 \
  --job-name=p1_sab_backend_map_v1 \
  --account=lu2026-2-51 \
  --partition=gpua40i \
  --gres=gpu:a40:1 \
  --nodes=1 \
  --ntasks=1 \
  --cpus-per-task=8 \
  --mem=64G \
  --time=01:00:00 \
  --signal=B:TERM@120 \
  --export=NIL \
  --output=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v4-20260825-submit-logs/slurm-%j.out \
  --error=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v4-20260825-submit-logs/slurm-%j.err \
  /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-exec-successor-v4-20260825/development/p1-scienceagentbench-backend-canonical-map-discriminator-v4-2026-08-25/run_backend_canonical_map_discriminator_v1.sh
```

The trampoline must receive zero argv. It freezes OUTPUT internally, atomically
creates RUN mode `0700`, and execs the core with exactly these two core args:

```text
--output-root /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v4-20260825/evidence
```

Its failure prefix is:

```text
P1_SAB_BACKEND_CANONICAL_MAP_DISCRIMINATOR_TRAMPOLINE_V1_CANNOT_CHECK
```

LOG is non-authorizing operator log custody only. Preserve the mode-`0700` LOG
root and its Slurm stdout/stderr on every outcome; neither file substitutes for
the create-only core receipt.

On successful handoff it execs the core, whose exact success terminal is:

```text
P1_SAB_BACKEND_CANONICAL_MAP_DISCRIMINATOR_PASS
```

The core may send only `GET /health` and `GET /slots` to
`127.0.0.1:8080`. It must report zero protected-body, tokenize, completion,
generation, evaluator, and outcome counts. It must prove one visible
`NVIDIA A40`, exact process/argv/environment/listener identity, identical
server/backend/model map attestations before and after the GPU identity
capture, and a final matching full-byte/custody plus listener rebind.

## Receipt and cleanup gates

Require exactly one of these create-only mode-`0400` receipts under OUTPUT:

```text
BACKEND_CANONICAL_MAP_DISCRIMINATOR_RESULT_V1.json
BACKEND_CANONICAL_MAP_DISCRIMINATOR_CANNOT_CHECK_V1.json
```

OUTPUT must be mode `0500` after receipt creation. A PASS receipt is admissible
only with the exact success terminal, exit zero, exact schema/status/authority,
frozen contract SHA-256, exact zero counters, frozen runtime hashes and
custody, logical/canonical device-inode equality, only frozen map aliases,
independently present server/backend/model mappings, singular A40 identity,
and confirmed process plus process-group absence.

A nonzero exit, missing/different terminal, trampoline CANNOT_CHECK, core
CANNOT_CHECK, reused root, unexpected file, wrong mode, runtime drift, third
mapping alias, frozen path with wrong device/inode, absent server, backend, or model
mapping, reattestation drift, non-loopback listener, proxy drift, wrong GPU, or
cleanup failure is a hard stop. Preserve its body-free receipt and logs; do not
retry in place.

## Interpretation boundary

A live PASS would establish only that a fresh exact body-free server maps the
frozen server, backend, and model identities under their allowed
logical/canonical path sets in that one job. It would not establish why job
`3537893` failed, repair
or promote that job, authorize a protected retry, establish task execution or
official evaluation, support production admission, or establish any model or
ORION superiority claim.
