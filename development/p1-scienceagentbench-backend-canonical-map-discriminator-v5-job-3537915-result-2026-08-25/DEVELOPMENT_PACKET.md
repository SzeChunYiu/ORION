# Paper 1 backend canonical-map discriminator V5 job-3537915 result

## Exact result and authority boundary

The V5 freeze was squash-merged as PR `#1264` at
`e47ffa7689e48667d167fe0658b37753ebb67a4c`. The separately authorized,
body-free LUNARC execution was job `3537915`.

The scheduler result is exactly:

```text
state=FAILED
exit=1:0
elapsed=00:01:24
node=cg14
allocated=one A40 GRES
terminal=P1_SAB_BACKEND_CANONICAL_MAP_DISCRIMINATOR_V2_CANNOT_CHECK failure_code=GPU_IDENTITY_INVALID detail_sha256=37a3b93da155ad4641b63864fd78781f9144c3813a2b02fae9ba0924a98025a2
```

This is a typed, body-free `CANNOT_CHECK`, not a discriminator PASS. It gives
no production admission, protected-execution result, official task outcome,
model comparison, ORION comparison, or scientific-authority increment. It
does, however, resolve the principal V4 branch ambiguity: the completed
`nvidia-smi` call returned nonzero, rather than zero with nonempty stderr.

## Immutable deployment and submission

The deployment archive was cut from merged commit
`e47ffa7689e48667d167fe0658b37753ebb67a4c` and contained the eleven-file V5
packet plus the four exact job-3537910 predecessor surfaces required by test
32:

```text
bytes=215040
sha256=5fcf011c3e6a477eb219449f056c676a90e1472b3868cd2a726ba0ee9426e915
```

Before deployment, ROOT, RUN, OUTPUT, LOG, and the upload path were all absent.
The new deployment root was sealed mode `0500`; payloads were mode `0400`
except the zero-argv trampoline, mode `0500`. All deployed file hashes matched,
all ten V5 `SHA256SUMS` entries verified before and after sealing, and the
direct validator passed 32 tests under the exact LUNARC Python 3.11.5 in
normal, optimized, and isolated modes. The upload was unlinked after sealing;
RUN, OUTPUT, and LOG remained absent.

Separately, `POST_MERGE_CLEAN_ARCHIVE_EVIDENCE.txt` binds a clean archive of
the same merged commit and passes all four frozen host modes plus all ten
checksums. This four-mode record is local clean-archive evidence; it is not
misdescribed as four remote LUNARC reruns.

Immediately before submission, the runner, core, and contract bindings were
rechecked, RUN/OUTPUT/LOG were absent, and the operator created only a new
mode-`0700` LOG. The exact zero-argv trampoline was submitted from ROOT with
`--export=NIL`, exact `--chdir`, and LOG-only scheduler streams. The scheduler
record binds one node, one task, eight CPUs, 64 GiB, one A40 GRES, and the
frozen one-hour limit.

`SUBMIT_LINE_AND_RESIDUAL_EVIDENCE.txt` independently records Slurm's retained
`SubmitLine`, including `--export=NIL`, the exact chdir, stream templates, and
zero-argv trampoline. It also records final elapsed seconds and an explicit
post-job residual-process count of zero.

## Receipt and stream bindings

The create-only result surface is:

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `JOB_3537915_BACKEND_CANONICAL_MAP_DISCRIMINATOR_CANNOT_CHECK_V2.json` | 1,883 | `2b421bb1ed442ac15689975658b4a4320611276cc4dfad6649d9b85f68d67cf3` |
| `slurm-3537915.err` | 172 | `c80d3ab5044472895eace3c7faa096eaa1f7441108696d98b51c50a10f53870e` |
| `slurm-3537915.out` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

The receipt was mode `0400` under a mode-`0500` OUTPUT. The server and process
group were absent after cleanup; no residual `llama-server` or V2 discriminator
process was found.

## What V5 newly establishes

The completed GPU capture is exactly:

```text
status=COMPLETED
argv=[/usr/bin/nvidia-smi,--query-gpu=index,uuid,name,--format=csv,noheader,nounits]
return_code=6
stdout.bytes=22
stdout.sha256=cda3a19e75eacfb91b9b2c2f85080bddea247dd500abec231f6212e3d8fff3bd
stderr.bytes=76
stderr.sha256=0a0daacddae467fe5f39a91401c306cb9b469459f8ba6d7e78d485c2d925c76a
stdout_parse_attempted=false
failure_subcode=NVIDIA_SMI_NONZERO_RETURN
```

NVIDIA's [`nvidia-smi` documentation](https://docs.nvidia.com/deploy/nvidia-smi/index.html#return-value)
(accessed 2026-08-25) defines return code 6 generically as “A query to find an
object was unsuccessful.” This identifies the return-code class, not the
missing object or root cause.

`NVIDIA_SMI_RETURN_VALUE_SOURCE_V1.txt` commits the narrow RETURN VALUE excerpt
and binds the URL, access date, original 218,860-byte HTML hash, and original
line range; validators therefore do not depend on an external uncommitted
download.

The declared 22-byte candidate `No devices were found\n` has exactly the
retained stdout byte count and SHA-256. That is a candidate-set hash match
under the usual collision-resistance assumption; the raw stdout was not
retained, and the packet does not relabel it as independently retained
plaintext. No stderr candidate is asserted.

The completed stages were exactly:

```text
CONTRACT_BOUND
RUNTIME_FILES_BOUND
SERVER_STARTED
SERVER_READY_BODY_FREE
CANONICAL_MAP_ATTESTATION_1
SERVER_CLEANUP_PASS
```

Thus the exact server process, argv, allowlisted environment, loopback
listener, and frozen server/backend/model identities again passed the first
body-free mapping attestation. GPU identity did not bind. The second mapping
attestation, byte-identical reattestation, final runtime-file rebind, and final
listener rebind did not occur. The first attestation is a bounded
code-semantic witness only, not a full discriminator result or causal repair.

## Accounting

- Protected scheduler cost remains 90 GPU-seconds.
- Body-free discriminator cost is now `86 + 84 = 170` GPU-seconds.
- Combined scheduler cost is now `90 + 170 = 260` GPU-seconds.
- Protected infrastructure submissions remain three.
- Protected generation attempts consumed remain zero.
- Completed body-free discriminator submissions are now two.
- Job `3537915` is not a protected retry, protected-generation attempt, hidden
  sample, production run, or official evaluation.

## Smallest next body-free discriminator

V6 should discriminate visibility loss without approaching any protected or
task-bearing surface. On one fresh, separately authorized allocation it should
retain bounded diagnostics at three phases: before server launch, after the
body-free readiness/first-map attestation, and after cleanup.

At each phase, bind:

1. exact `nvidia-smi` argv, return code, and stdout/stderr `{bytes,sha256}`;
2. a declared-candidate enum for stable known messages, never guessed text;
3. scheduler visibility variables with an explicit allowlist;
4. `/dev/nvidia*` path type, major/minor, mode, ownership, and openability,
   without reading device bodies;
5. `/proc/self/cgroup` and device-controller membership as structured hashes
   plus a minimal safe classifier; and
6. server-process and mapping state only at the already body-free gates.

The phase matrix distinguishes allocation/cgroup absence (failure before
server), server-lifecycle interaction (pre-server pass followed by post-ready
failure), and transient node state (phase disagreement or cleanup recovery).
The job must stop after the first create-only receipt. It must not open a
protected packet, issue tokenize/completion requests, generate, evaluate, or
read official outcomes.

## Reopen conditions

Reopen if any receipt/log/deployment binding differs; if return code 6 is
described as identifying the missing object; if the stdout candidate is called
retained plaintext; if the first map attestation is promoted; if cost or job
ordinals are altered; or if any future diagnostic reaches protected/task
routes.
