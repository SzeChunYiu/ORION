# Paper 1 protected RR1 direct-execution successor V2 development packet

## Frozen status and question

This additive lane repairs two infrastructure defects exposed by body-free live
job `3537740`: Slurm spooled the submitted launcher so its `BASH_SOURCE`-based
adjacency resolved under `/var/spool`, and the post-job watcher treated an
accounting-readiness transient as a partition contradiction. The lane is based
on main `51f13ba973df184c0e022356c9260b99a3cc58f0` and is
`FROZEN_REPAIRED_NOT_RESUBMITTED`.

It does **not** authorize or perform `sbatch`, protected-body access, generation,
evaluation, outcome access, production admission, 918-tuple finalization, or
merge. The original direct-route launcher, module, and contract remain
byte-unchanged in their V1 lane.

## Defect 1: spooled-script trampoline

The only file that may eventually be submitted is:

```text
/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-exec-successor-v2-20260824/development/p1-scienceagentbench-protected-rr1-execution-successor-v2-2026-08-24/run_protected_rr1_direct_execution_trampoline_v2.sh
```

It retains the original ten `#SBATCH` lines byte-for-byte and in order,
including `#SBATCH --signal=B:TERM@120`. It does not use `BASH_SOURCE` or
`--wrap`. It requires submission and runtime cwd, `PWD`, and
`SLURM_SUBMIT_DIR` all to be the exact canonical successor snapshot root:

```text
/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-exec-successor-v2-20260824
```

The spooled `$0` must be an absolute regular non-symlink file whose raw bytes
and SHA-256 equal the canonical trampoline at that root. This comparison is
only source attestation; `$0` never supplies a dirname or module path.

The trampoline independently verifies and executes the immutable donor at:

```text
/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-51f13ba9/development/p1-scienceagentbench-protected-rr1-direct-route-freeze-v1-2026-08-24/run_protected_rr1_direct_route_v1.sh
```

Frozen donor hashes are:

```text
launcher a540954aaa4ce638190162f39268bf660d7baac7d4e8841d4f56ba5441300219
module   7ff4868a744af526384e199dab659a76a67f83ab51ee813ce65f53026b220a91
contract a091bf0617d657ee7f8c2bcab08acda96d16246407d791d6a90704efffedc398
```

The trampoline admits no caller-controlled `PATH`. It verifies these exact
runtime bindings before donor execution:

```text
/usr/bin/bash
sha256=ec6d007d48ef11bc47ad3f372b4b20ff2f0d4e63867e7e4cc0f1b17b19fa88b2

/usr/bin/sha256sum
sha256=1950eda10a1bb0c6c2a086ba009b847edec6f30d25eb311b9154ae08819041a9

PATH=/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin:/usr/bin:/bin
command -v python3=/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3
python real target=/lunarc/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3.11
python real target sha256=34f2f9f9561850d15d8060a2565c3a81046425faaba575687d3b75e1212d0f77
```

All trampoline hashing and byte comparison uses absolute utilities or Bash
builtins; no unqualified `sha256sum`, `cut`, `readlink`, or `cmp` remains. The
last operation is `exec /usr/bin/bash "$ORIGINAL_LAUNCHER" "$@"`; therefore the
unchanged original launcher remains the runtime launcher and its own
`BASH_SOURCE/HERE` resolves the unchanged adjacent donor module truthfully.
No `cd` to the donor occurs.

## Exact prospective submission freeze

The runtime topology is exactly:

```text
RUN=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824
runtime parent (0700): $RUN/runtime-parent
runtime evidence root (absent before submission): $RUN/runtime-parent/evidence
capture parent (0700): $RUN/capture-parent
capture root (absent before watch-capture): $RUN/capture-parent/capture
final parent (0700): $RUN/final-parent
final result root (absent before finalize): $RUN/final-parent/result
logs root (0700): $RUN/logs
sbatch raw stdout (new mode 0600): $RUN/logs/SBATCH_STDOUT_V1.txt
sbatch raw stderr (new mode 0600): $RUN/logs/SBATCH_STDERR_V1.txt
parser stdout (new mode 0600): $RUN/logs/PARSE_SBATCH_JOB_ID_STDOUT_V1.txt
parser stderr (new mode 0600): $RUN/logs/PARSE_SBATCH_JOB_ID_STDERR_V1.txt
```

The trampoline accepts only the following six ordered flag/path pairs. Missing,
extra, reordered, relative, aliased, or changed arguments fail before the donor
launcher executes.

The exact frozen future command shape is below. It is a receipt-bound handoff,
**not authorization to execute it**:

```bash
umask 077
set -Eeuo pipefail
set -o noclobber
unset BASH_ENV ENV PYTHONPATH PYTHONHOME PYTHONSTARTUP
cd /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-exec-successor-v2-20260824
sbatch --parsable \
  --export=NIL \
  --output=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824/logs/slurm-%j.out \
  --error=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824/logs/slurm-%j.err \
  /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-exec-successor-v2-20260824/development/p1-scienceagentbench-protected-rr1-execution-successor-v2-2026-08-24/run_protected_rr1_direct_execution_trampoline_v2.sh \
  --masked-packet /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/private-inputs/MASKED_PACKET.json \
  --recovered-packet /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/private-inputs/RECOVERED_PACKET.json \
  --model /projects/hep/fs10/scratch/scyiu/orion_p1_sab_exact_model_v1_20260824/model/Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf \
  --llama-server /sw/pkg/ollama/0.32.14/lib/ollama/llama-server \
  --cuda-backend /sw/pkg/ollama/0.32.14/lib/ollama/cuda_v13/libggml-cuda.so \
  --output-root /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824/runtime-parent/evidence \
  > /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824/logs/SBATCH_STDOUT_V1.txt \
  2> /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824/logs/SBATCH_STDERR_V1.txt

[[ -f /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824/logs/SBATCH_STDERR_V1.txt && ! -L /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824/logs/SBATCH_STDERR_V1.txt && "$(/usr/bin/stat -c %a -- /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824/logs/SBATCH_STDERR_V1.txt)" == 600 && ! -s /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824/logs/SBATCH_STDERR_V1.txt ]]

/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3 -I -S \
  /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-exec-successor-v2-20260824/development/p1-scienceagentbench-protected-rr1-execution-successor-v2-2026-08-24/protected_rr1_one_tuple_finalizer_v2.py \
  parse-sbatch-job-id \
  --input-path /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824/logs/SBATCH_STDOUT_V1.txt \
  > /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824/logs/PARSE_SBATCH_JOB_ID_STDOUT_V1.txt \
  2> /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824/logs/PARSE_SBATCH_JOB_ID_STDERR_V1.txt

[[ -f /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824/logs/PARSE_SBATCH_JOB_ID_STDERR_V1.txt && ! -L /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824/logs/PARSE_SBATCH_JOB_ID_STDERR_V1.txt && "$(/usr/bin/stat -c %a -- /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824/logs/PARSE_SBATCH_JOB_ID_STDERR_V1.txt)" == 600 && ! -s /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824/logs/PARSE_SBATCH_JOB_ID_STDERR_V1.txt ]]
exec 3< /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824/logs/PARSE_SBATCH_JOB_ID_STDOUT_V1.txt
IFS= read -r JOBID <&3
[[ "$JOBID" =~ ^[1-9][0-9]*$ ]]
EXTRA=''
if IFS= read -r EXTRA <&3 || [[ -n "$EXTRA" ]]; then exit 2; fi
exec 3<&-

/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3 -I -S \
  /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-exec-successor-v2-20260824/development/p1-scienceagentbench-protected-rr1-execution-successor-v2-2026-08-24/protected_rr1_one_tuple_finalizer_v2.py \
  watch-capture --job-id "$JOBID" \
  --output-root /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824/capture-parent/capture

/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3 -I -S \
  /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-exec-successor-v2-20260824/development/p1-scienceagentbench-protected-rr1-execution-successor-v2-2026-08-24/protected_rr1_one_tuple_finalizer_v2.py \
  finalize \
  --evidence-root /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824/runtime-parent/evidence \
  --capture-root /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824/capture-parent/capture \
  --output-root /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824/final-parent/result
```

The first five paths are the previously verified immutable inputs. The sixth is
the single predeclared new private runtime evidence root. Repository code does
not create the private parent topology, run this command, or open these files.

`set -o noclobber` and `umask 077` make all four bridge files create-only mode
`0600`; a nonzero `sbatch` or parser exit stops immediately, and absolute
`/usr/bin/stat` plus Bash file predicates require each stderr file to exist as
a regular non-symlink mode-`0600` empty file. The operator unsets Bash/Python startup variables and
`sbatch --export=NIL` exports only Slurm/SPANK variables without invoking
`get-user-env`, so inherited `BASH_ENV` cannot run in the spooled trampoline.
Command substitution must not capture raw `sbatch` stdout because it strips
trailing LFs. Instead,
`parse-sbatch-job-id --input-path` descriptor-safely requires an absolute file
at the one frozen path under an owned mode-`0700` parent, owned regular
link-count-one mode `0600`,
then accepts only one canonical positive decimal line with **exactly one** final
LF. Missing LF, zero, leading zeros, a semicolon/cluster suffix, CR, surrounding
whitespace, extra lines, symlink, hardlink, or other text fails with a body-free
typed terminal and no stdout. Every operator-side finalizer invocation runs
with exact `-I -S`; parser success is
redirected to its own private file and must be exactly the digits plus one LF.
Bash builtin `read` consumes exactly that one line, the regex and EOF checks
reject drift, and the resulting `JOBID` is passed unchanged to `watch-capture`
immediately; no
separate lookup, suffix stripping, or identity rewrite is allowed.

The three exact success terminals, in order, are:

```text
P1_SAB_PROTECTED_RR1_ONE_TUPLE_CAPTURED__SCHEDULER_FINALIZATION_PENDING
P1_SAB_PROTECTED_RR1_POST_JOB_SCHEDULER_CAPTURE_PASS
P1_SAB_PROTECTED_RR1_ONE_TUPLE_POST_JOB_FINALIZATION_PASS
```

The watcher starts immediately after the validated parsable job ID is obtained;
it does not wait for the first terminal. Each stage requires exit zero and its
exact terminal. A missing or different terminal, nonzero exit, typed watcher or
finalizer `CANNOT_CHECK`, cleanup/evidence/path/hash drift, or any attempt to
reuse an output root is a hard stop. No later stage may reinterpret or repair a
failed earlier gate.

## Defect 2: narrow accounting readiness

Every poll retains its exact argv, monotonic timestamp, row count, raw SHA-256,
state, partition, classification, and terminal flag. The unchanged bounds remain
5 seconds and 1440 polls.

Permitted retry profiles are only:

- zero-byte `sacct` stdout: `NO_ROW`;
- any well-formed nonterminal state with `Partition=""`:
  `PRETERMINAL_EMPTY_PARTITION`;
- any well-formed nonterminal state with `Partition="gpua40i"`:
  `PRETERMINAL_PARTITION_READY`;
- a terminal row containing an exact empty/`Unknown` sentinel in an enumerated
  readiness field: `TERMINAL_ACCOUNTING_INCOMPLETE_ENUMERATED_SENTINEL`.

The terminal sentinel fields are `Partition` (empty only), plus `ExitCode`,
`DerivedExitCode`, `Submit`, `Eligible`, `Start`, `End`, `TimelimitRaw`,
`NodeList`, `NNodes`, `NCPUS`, `ReqCPUS`, `ReqMem`, `ReqTRES`, `AllocTRES`, and
`Account` (empty or exact `Unknown`). Empty `NTasks` remains valid under the
unchanged strict parser and is not an incompleteness sentinel. Blank
`Constraints`, `Reservation`, and `Reason` remain legitimate. No broad
exception-to-retry route exists.

Only a fully strict terminal row with exact `Partition=gpua40i` receives
`TERMINAL_COMPLETE_gpua40i`, derives node/start/end, and starts post-terminal
capture. A wrong nonblank partition, malformed identity/state, step, array,
duplicate/multiple row, wrong field count, or other malformed nonempty strict
field fails immediately and is retained as rejected body-free poll provenance.
Incomplete-row exhaustion emits the same typed terminal timeout.

The existing custody and timing guarantees remain unchanged: first post-job
`scontrol` starts within 2 seconds, each command has a 20-second monotonic cap,
the capture sequence has a 240-second cap, terminal raw bytes are retained on
later failure, raw files are O_EXCL/fsync/reread/inode-bound and sealed mode
`0400`, and final outputs remain deterministic and fail-closed.

## Job 3537740 and retry accounting

`FAILED_JOB_3537740_NO_GENERATION_CERTIFICATE_V1.json` records only body-free
facts:

```text
state=FAILED
exit=2:0
stdout bytes=0 sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
stderr bytes=132 sha256=3564291c418af0c4eeb863bd3ab40e422f0545f289eb8dc52bc717d0267bb2c6
capture CANNOT_CHECK bytes=1526 sha256=11ac40ec96f00d17d6b5661ede6dcf0113a806c94b135458896d8a929a86d8b8
capture detail sha256=d1063759a7d33bfd69e51c0e2941ae0059ab8a72e3e408e5b4860fc8800d0709
```

The last digest binds the exact body-free detail
`FinalizationError:polled sacct partition differs from the freeze` without
retaining it in the certificate.

The job stopped before Python, runtime-root creation, model open, server start,
tokenization, completion, or generation. It consumed one scheduler GPU-second,
but zero model-generation attempts and zero plan-clock allocated-accelerator
seconds. A repaired resubmission would therefore be generation ordinal 1, not a
hidden second sample. The scheduler cost is retained and is not erased.

## Additive V2 boundary

V2 has its own contract, output schema, module, validator, trampoline, failure
certificate, manifest, receipt, and checksums. Donor runtime/evidence filenames
remain V1 because they are emitted or consumed by the unchanged direct route;
V2 changes only finalizer-owned schema identities and watcher provenance. The
merged V1 finalizer packet is hash-bound as a predecessor and is not modified.

Production admissibility remains `CANNOT_CHECK`; scientific authority delta is
`NONE`; the Runner V2 population ledger remains `NOT_FINALIZED_918_TUPLES`.
