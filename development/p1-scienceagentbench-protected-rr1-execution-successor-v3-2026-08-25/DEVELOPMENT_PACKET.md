# Paper 1 protected RR1 direct-execution successor V3 development packet

## Frozen status and authority boundary

This additive packet is based on main `bbc73f0860b1b76a2c4fe4449f7a30d0866cb247` and is
`FROZEN_REPAIRED_NOT_RESUBMITTED`. It repairs the exact dynamic-loader defect
observed in body-free job `3537828` and a separately reproduced Slurm 23.11
configuration-parser incompatibility. It does not itself authorize submission,
protected-body access, generation, evaluation, outcome access, production
admission, or the 918-tuple campaign.

The V1 donor route and the merged V2 successor remain byte-unchanged. V3 uses
fresh immutable roots:

```text
ROOT=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-exec-successor-v3-20260825
RUN=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v3-20260825
LANE=development/p1-scienceagentbench-protected-rr1-execution-successor-v3-2026-08-25
```

The failed V2 run root is retained and must never be reused.

## Job 3537828: exact adverse result

Job `3537828` was `FAILED`, exit `127:0`, elapsed one second on `cg14`, with one
A40 allocated. Its exact Slurm stderr was:

```text
python3: error while loading shared libraries: libpython3.11.so.1.0: cannot open shared object file: No such file or directory
```

Bindings:

```text
stdout bytes=0 sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
stderr bytes=127 sha256=439ddcf58763e070b3c96ce803b56b4a9694761bfda8e14cd5cd2b7078f8ab10
watcher stderr bytes=176 sha256=7218b38260f25767f7691ec5524ccfbf32b0cb555f5cb94b09954f496d1063b5
capture CANNOT_CHECK bytes=6321 sha256=83a97ac2e2ff92c241f9824b476969b441aead00ef456820eddc3053bb81648c
watcher detail sha256=1d733d9de0d4dc259545dc0992b1e1f495e9c82d057339fd58b4e90ab849857e
```

The original launcher reached its Python `exec`, but the ELF loader stopped
before a Python interpreter or user code started. No runtime evidence file,
server, model open, tokenization, completion, generation, evaluator, official
outcome, or protected-body access occurred. The job used one scheduler
GPU-second. Together with job `3537740`, cumulative scheduler cost is two
GPU-seconds, while generation attempts consumed remain zero. A repaired retry
is generation ordinal `1`, infrastructure submission ordinal `3`, and not a
hidden second sample.

`FAILED_JOB_3537828_NO_GENERATION_CERTIFICATE_V1.json` retains those facts and
the full body-free scheduler-capture hashes.

## Root cause and exact loader repair

`sbatch --export=NIL` correctly removed inherited environment variables. V2
restored the frozen Python `PATH` but did not restore the EasyBuild directory
needed to resolve the executable's `NEEDED libpython3.11.so.1.0` entry.

V3 requires both `LD_LIBRARY_PATH` and `LD_PRELOAD` to be absent on trampoline
entry, completes every source, cwd, donor, tool, and argv check, then assigns
exactly:

```text
LD_LIBRARY_PATH=/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/lib
```

It never appends an ambient value. It binds:

```text
logical directory=/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/lib
canonical directory=/lunarc/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/lib
directory mode=0755 uid=1400 gid=1400 nlink=4
exact top-level entries=libpython3.11.so,libpython3.11.so.1.0,libpython3.so,pkgconfig,python3.11
libpython3.11.so -> libpython3.11.so.1.0
logical file=/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/lib/libpython3.11.so.1.0
canonical file=/lunarc/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/lib/libpython3.11.so.1.0
bytes=22160208 mode=0755 uid=1400 gid=1400 nlink=1
sha256=398cbf957b8584d4e06ce374b888555149d517ea1037f7ca44d62f855a5b83c5
ABI file=/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/lib/libpython3.so
ABI bytes=15352 mode=0755 uid=1400 gid=1400 nlink=1
ABI sha256=9ce9dfd0670cd9e05cdee0478b0a82425b1fd45abe7bdef807a4e7ba2a331f93
```

Bash, `sha256sum`, `readlink`, `cmp`, `stat`, and `wc` are hash-bound. The
trampoline binds raw equality between canonical and spooled bytes and also a
normalized self-hash, so identically stale copies fail closed. After the
library assignment it runs a body-free `python3 -B -I -S` loader probe importing
`ctypes`, `tarfile`, and `zlib`; merged stdout/stderr must contain exactly zero
bytes as measured by the hash-bound `wc -c` before the unchanged V1 donor
launcher can execute.

A live read-only clean-environment discriminator produced:

```text
without LD: rc=127 stdout=0 bytes stderr=189 bytes
with exact LD: rc=0 stdout=V3_PYTHON_RUNTIME_OK\n stderr=0 bytes
```

The unchanged server builder derives this exact runtime order:

```text
/sw/pkg/ollama/0.32.14/lib/ollama:/sw/pkg/ollama/0.32.14/lib/ollama/cuda_v13:/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/lib
```

Slurm's `CUDA_VISIBLE_DEVICES` remains unchanged; V3 does not synthesize it.

## Watcher and scheduler-parser determination

The watcher CANNOT_CHECK from job `3537828` remains truthful. The failed job's
post-job `scontrol -dd` lacks `GresDetail`; V3 does not relax the successful-job
GPU identity requirement and does not reinterpret that downstream failure as a
PASS.

A separate body-free replay found that the captured 8041-byte
`scontrol show config` output contains valid Slurm 23.11 uppercase/underscore,
indexed, blank, section, and controller-status lines. V2 rejected every
unrelated non-`Key = Value` line, so a successful repaired job would have met a
latent parser blocker. V3 preserves the raw bytes and exact header, extracts
only the frozen required configuration allowlist, rejects a missing, empty,
duplicate, or case-aliased required key, and tolerates unrelated dialect lines.
Partition, node, `sacct`, and successful-job `GresDetail` checks remain strict.

## Immutable donor and predecessor bindings

The runtime donor stays:

```text
/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-51f13ba9/development/p1-scienceagentbench-protected-rr1-direct-route-freeze-v1-2026-08-24
```

```text
launcher sha256=a540954aaa4ce638190162f39268bf660d7baac7d4e8841d4f56ba5441300219
module sha256=7ff4868a744af526384e199dab659a76a67f83ab51ee813ce65f53026b220a91
contract sha256=a091bf0617d657ee7f8c2bcab08acda96d16246407d791d6a90704efffedc398
```

The V3 contract also binds the V2 trampoline, finalizer, contract, failure
certificate, and `SHA256SUMS`; their mutation is forbidden.

## Fresh runtime topology

```text
$RUN/runtime-parent                 mode 0700
$RUN/runtime-parent/evidence        absent before submission
$RUN/capture-parent                 mode 0700
$RUN/capture-parent/capture         absent before watch-capture
$RUN/final-parent                   mode 0700
$RUN/final-parent/result            absent before finalize
$RUN/logs                           mode 0700
```

Bridge files are create-only mode `0600`. Capture files are O_EXCL/fsync/reread
bound and sealed `0400`. Output-root reuse, symlinks, hardlinks, alias paths,
wrong ownership, wrong mode, or hash drift fail closed.

## Exact operator boundary

The operator shell must set `umask 077`, `errexit`, `nounset`, `pipefail`, and
`noclobber`; unset Bash/Python startup variables and `LD_PRELOAD`; and set the
exact Python library path for operator-side parser/watcher/finalizer Python.
The job is still submitted with `--export=NIL`; only the V3 trampoline supplies
the exact job-side loader binding.

The three exact success terminals, in order, remain:

```text
P1_SAB_PROTECTED_RR1_ONE_TUPLE_CAPTURED__SCHEDULER_FINALIZATION_PENDING
P1_SAB_PROTECTED_RR1_POST_JOB_SCHEDULER_CAPTURE_PASS
P1_SAB_PROTECTED_RR1_ONE_TUPLE_POST_JOB_FINALIZATION_PASS
```

Any nonzero exit, missing/different terminal, typed CANNOT_CHECK, evidence drift,
cleanup drift, or root reuse is a hard stop. A failed earlier gate is never
repaired or promoted by a later stage.

## Validation and nonclaims

The V3 validator uses invented metadata and body-free read-only scheduler
formats only. It must run under normal, `-O`, and `-I -S` modes; no pytest is
required. It submits zero jobs, invokes zero generations, opens zero protected
bodies, invokes no evaluator, and opens no official outcomes.

A future one-tuple PASS would establish only the contract's bounded scheduler
and runtime facts for task `1`, arm `RR`, attempt `1`, seed `101`. It would not
establish model superiority, production admissibility, task execution success,
official evaluation, or the 918-tuple population result.
