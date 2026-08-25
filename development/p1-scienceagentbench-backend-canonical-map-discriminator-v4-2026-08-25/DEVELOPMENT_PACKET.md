# Paper 1 protected RR1 backend canonical-map discriminator V4 development packet

## Frozen status and authority boundary

This additive packet is based on the merged V3 commit
`a2fdc2854740dcde0652a17e447d8a9c1328208f`. Its status is
`FROZEN_BODY_FREE_DISCRIMINATOR_NOT_EXECUTED`. It freezes one body-free,
fail-closed discriminator for a specific V3 residual; it does not authorize a
protected retry, protected-body access, tokenization, completion, generation,
evaluation, outcome access, production admission, or the 918-tuple campaign.

The V3 result remains adverse. V4 is post-outcome diagnosis only and never a
promotion, repair, reinterpretation, or deletion of job `3537893`.

Fresh immutable roots are:

```text
ROOT=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-exec-successor-v4-20260825
RUN=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v4-20260825
OUTPUT=$RUN/evidence
LOG=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v4-20260825-submit-logs
```

ROOT, RUN, and LOG were absent at the body-free checkpoint. That observation
is not a future precondition receipt: all three must be rechecked immediately
before deployment, and OUTPUT must also be absent. LOG is a distinct
non-authorizing operator-log root because Slurm opens stdout/stderr before the
trampoline can create RUN.

## Job 3537893: exact adverse result

V3 job `3537893` was `FAILED`, exit `1:0`, elapsed 88 seconds on `cg14`,
with one A40 allocated. Primary stdout was empty:

```text
bytes=0
sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

Primary stderr was exactly 126 bytes with SHA-256
`c2e312de73f990fe41cbe1a078cea8a61d7b50c69d339fc798babf6425c402cb`
and terminal:

```text
P1_SAB_PROTECTED_RR1_DIRECT_ROUTE_CANNOT_CHECK detail_sha256=e4d5bcb685476587bb3af200163542287bdfcd92352247f9cc680889ec6f0582
```

The audit established this source-derived typed detail, whose bytes are exactly
bound by the retained `failure_detail_sha256`:

```text
PreflightError:staged CUDA backend is not mapped into the live server process
```

`PREFLIGHT_CANNOT_CHECK_V1.json` was 505 bytes with SHA-256
`a4f1f1884c0a22d053c7d452f10ec5bee8ae7ff174a836bec429127c92c01e7f`.
Other retained body-free runtime bindings were:

```text
STAGED_RUNTIME_INPUT_V1.json bytes=5466
sha256=1c34b96449ddf60ff279bd4f4651cdafcd2f7b999ac03e6c60bba401c3b1e296

SERVER_CLEANUP_V1.json bytes=798
sha256=f82ba8d1b6929893c3caa75028a0e7059b39eb1a638cc38522375699ca4be550
```

The watcher then truthfully emitted a downstream CANNOT_CHECK with
`failure_code=EVIDENCE_PARSE_INVALID` and detail SHA-256
`1d733d9de0d4dc259545dc0992b1e1f495e9c82d057339fd58b4e90ab849857e`.
The decoded detail was:

```text
FinalizationError:captured post-job scontrol -dd lacks required -dd keys
```

Its stdout was empty. Its stderr was 176 bytes with SHA-256
`7218b38260f25767f7691ec5524ccfbf32b0cb555f5cb94b09954f496d1063b5`.
`SCHEDULER_CAPTURE_CANNOT_CHECK_V1.json` was 15,672 bytes with SHA-256
`79121b600e49b6f450f0119dca51ff5b72d8a6661a95c354ce9b222bd4e63707`.
The watcher result is not substituted for the primary staged-runtime failure.

Before the staged-runtime failure, V3 opened, validated, and staged both frozen
protected packet bodies (`MASKED_PACKET` and `RECOVERED_PACKET`). No body bytes
are disclosed or retained in this V4 packet, and the V4 audit agents did not
read their content. No protected prompt was sent, and no tokenize request,
completion request, generation invocation, official evaluator, or official
outcome was reached. The cumulative scheduler cost across jobs `3537740`,
`3537828`, and `3537893` is 90 allocated GPU-seconds. Generation attempts
consumed remain zero. A separately authorized repaired protected retry would
still be generation ordinal `1`; this body-free discriminator is not that retry
or a hidden sample.

`FAILED_JOB_3537893_NO_GENERATION_CERTIFICATE_V1.json` retains these facts.
It deliberately makes no model-map claim for the failed job because the
backend check failed first.

## Atomic development questions

1. Does each frozen logical runtime path resolve to the frozen canonical path
   and the same live device/inode identity?
2. Does the exact frozen loopback server start with the exact frozen argv,
   loader path, backend environment, file bytes, custody, and one A40?
3. After body-free readiness only, are the server and CUDA backend identities
   present in `/proc/<pid>/maps` under only their frozen logical or canonical
   paths?
4. Is the model identity independently present under only its frozen logical
   or canonical path, without retroactively claiming that fact for job
   `3537893`?
5. Are both map attestations identical across an intervening GPU identity
   check, do a final full-byte/custody and listener rebind still match, and is
   the owned server process group absent afterward?
6. Can every failure produce only a typed, body-free CANNOT_CHECK receipt and
   never fall through to a protected or generative operation?

## Bounded post-outcome diagnosis

A body-free, read-only filesystem probe found that the site exposes `/sw` as
the logical namespace and `/lunarc/sw` as the canonical namespace. For the
frozen server and CUDA backend, the logical and canonical leaves resolve to the
same live device/inode identity. Linux may render the canonical pathname in
`/proc/<pid>/maps` even when argv and `GGML_BACKEND_PATH` use the logical path.

That observation motivates a discriminator, not a conclusion about the failed
job. A path-string-only absence check cannot distinguish:

```text
IDENTITY_NOT_MAPPED
```

from:

```text
IDENTITY_MAPPED_UNDER_FROZEN_CANONICAL_ALIAS
```

V4 therefore binds file bytes and custody first, requires logical/canonical
resolution and device/inode equality, and then matches `/proc/<pid>/maps` on
device plus inode. For each server, backend, and model identity, every matched
mapping must use exactly one of the two frozen path strings. A path row with
the frozen string but the wrong identity, or the frozen identity under any
third alias, fails closed. Server, backend, and model mappings are
independently required. Passing this discriminator
would show only that a fresh body-free process satisfies this bounded mapping
contract; it would not show that V3 should have passed.

## Frozen runtime bindings

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

`BACKEND_CANONICAL_MAP_DISCRIMINATOR_CONTRACT_V1.json` freezes the exact
server argv. Its effective server library path is exactly:

```text
/sw/pkg/ollama/0.32.14/lib/ollama:/sw/pkg/ollama/0.32.14/lib/ollama/cuda_v13:/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/lib
```

It is not appended to ambient state. `GGML_BACKEND_PATH` is exactly the frozen
logical backend path. All common proxy variables are empty, and the only
listener is one server-owned `127.0.0.1:8080` socket.

## Body-free execution and output contract

The only HTTP requests allowed are:

```text
GET /health
GET /slots
```

The slots response must contain exactly one slot. No request body is sent.
`POST /tokenize`, `POST /completion`, protected/task-bearing traffic, and
external network access are forbidden. Before and after the singular A40
identity capture, the server executable, exact argv, backend environment,
server mapping, backend mapping, and model mapping must be identical.

The output root must be absolute and new. A success or CANNOT_CHECK receipt is
create-only, fsynced, reread byte-for-byte, sealed mode `0400`, and its output
root is sealed mode `0500`. When capture is available, server stdout/stderr are
retained only as byte count and SHA-256 in the body-free receipt. If capture
itself cannot be bound, the receipt instead retains the explicit
`CANNOT_CHECK_LOG_STREAM_UNAVAILABLE` status and only a failure-detail SHA-256;
it never invents byte counts or stream hashes. Cleanup is mandatory on both
success and failure.

The exact success terminal is:

```text
P1_SAB_BACKEND_CANONICAL_MAP_DISCRIMINATOR_PASS
```

The failure terminal prefix is:

```text
P1_SAB_BACKEND_CANONICAL_MAP_DISCRIMINATOR_CANNOT_CHECK
```

Any nonzero exit, different terminal, runtime drift, wrong listener, wrong GPU,
missing mapping, unbound alias, reattestation drift, output-root reuse, or
cleanup failure is a hard stop. A CANNOT_CHECK never authorizes a later stage.

## Saturation assessment, challenge, and reopen triggers

The implementation basis is deliberately narrow: frozen bytes/custody,
`realpath`, `stat` device/inode identity, `/proc/<pid>/{exe,cmdline,environ,maps,fd}`,
`/proc/<pid>/net/{tcp,tcp6}`, body-free loopback readiness, singular
`nvidia-smi` identity, and process-group cleanup. This is saturated for the stated alias
discriminator, not for general dynamic-loader, mount-namespace, deleted-file,
container, or scheduler causality.

The strongest challenge is that device/inode equality alone could be falsely
permissive if an unbound alias is mapped, or falsely flat if a different mount
namespace changes device numbering. The implementation answers the first by
allowing only the two frozen paths and the second by deriving the file and map
identities inside the same live job/process context. It reattests mappings
twice, then re-hashes every runtime file and reattests the exclusive TCP/TCP6
listener rather than treating one transient read as sufficient.

Prior search could have missed the relevant representation because V3 compared
the staged logical pathname to the kernel-rendered mapping pathname before
asking whether both names denote the same file identity. V4 reopens rather
than relaxes if any of these occur:

- logical/canonical `realpath`, device, inode, bytes, hash, or custody drift;
- a third mapping alias or a frozen path paired with a different identity;
- server, backend, or model identity absent after body-free readiness;
- process, argv, environment, listener, GPU, second-attestation, or final
  full-byte/custody rebind drift;
- any tokenize/completion/generation/protected-body counter above zero;
- incomplete cleanup or any output-custody failure.

## Frozen implementation hypothesis and validation boundary

The frozen hypothesis is: **if the V3 failure was caused only by logical versus
canonical pathname rendering, a fresh exact body-free server will map the
frozen backend identity under `/sw` or `/lunarc/sw`, with the same device/inode
as the hash-bound file; otherwise the discriminator will emit CANNOT_CHECK.**

Synthetic validation uses invented filesystem/process metadata and no pytest.
It must pass under normal Python, `-O`, and `-I -S`, and `bash -n` must accept
the trampoline. Validation submits zero jobs, opens zero protected bodies,
sends zero tokenize/completion requests, invokes zero generations and zero
evaluators, and opens zero official outcomes. Repository validation is not a
live LUNARC result.
