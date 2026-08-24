# Paper 1 protected RR1 direct-execution successor V2 handoff

## Current verdict

`FROZEN_REPAIRED_NOT_RESUBMITTED`. This PR is an additive, body-free repair
packet based on `51f13ba973df184c0e022356c9260b99a3cc58f0`. It must remain open and
unmerged pending review. No command below was executed by this lane and nothing
here grants resubmission, protected-body, outcome, production, scientific, or
merge authority.

## Pre-resubmission gates

An authorized future operator must verify all of the following before using the
frozen command:

1. the exact successor snapshot is deployed at `/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-exec-successor-v2-20260824` with no symlink,
   alias, case, path, or byte drift;
2. `SHA256SUMS` validates the canonical trampoline and complete body-free
   packet;
3. the immutable donor at `/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-51f13ba9/development/p1-scienceagentbench-protected-rr1-direct-route-freeze-v1-2026-08-24` retains launcher/module/contract hashes
   `a540954aaa4ce638190162f39268bf660d7baac7d4e8841d4f56ba5441300219`,
   `7ff4868a744af526384e199dab659a76a67f83ab51ee813ce65f53026b220a91`,
   and `a091bf0617d657ee7f8c2bcab08acda96d16246407d791d6a90704efffedc398`;
4. `FAILED_JOB_3537740_NO_GENERATION_CERTIFICATE_V1.json` validates before any
   resubmission, preserving generation ordinal 1 and the prior scheduler cost;
5. `$RUN`, `runtime-parent`, `capture-parent`, `final-parent`, and `logs` exist as
   canonical private directories of exact mode `0700`, while `evidence`,
   `capture`, `result`, `SBATCH_STDOUT_V1.txt`, and `SBATCH_STDERR_V1.txt` do not
   yet exist, and neither `PARSE_SBATCH_JOB_ID_STDOUT_V1.txt` nor
   `PARSE_SBATCH_JOB_ID_STDERR_V1.txt` exists; and
6. the five immutable input paths still pass the unchanged donor runtime's
   canonical path, size, and SHA-256 checks.

Frozen topology:

```text
RUN=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824
runtime evidence=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824/runtime-parent/evidence
scheduler capture=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824/capture-parent/capture
final result=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824/final-parent/result
logs=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824/logs
sbatch stdout=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824/logs/SBATCH_STDOUT_V1.txt
sbatch stderr=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824/logs/SBATCH_STDERR_V1.txt
parser stdout=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824/logs/PARSE_SBATCH_JOB_ID_STDOUT_V1.txt
parser stderr=/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824/logs/PARSE_SBATCH_JOB_ID_STDERR_V1.txt
```

## Exact future submission shape — not authorization

Submission and runtime cwd, `PWD`, and `SLURM_SUBMIT_DIR` must remain exactly
`/projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-exec-successor-v2-20260824`. The trampoline is the only submitted file.

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
```

The trampoline rejects any other argv and attests its spooled bytes against the
canonical successor source before it verifies and `exec`s the unchanged donor
launcher by absolute path. It never resolves runtime code relative to the spool
file and never changes cwd to the donor. It fixes
`PATH=/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin:/usr/bin:/bin`,
verifies `/usr/bin/bash` and `/usr/bin/sha256sum` against hashes
`ec6d007d48ef11bc47ad3f372b4b20ff2f0d4e63867e7e4cc0f1b17b19fa88b2`
and `1950eda10a1bb0c6c2a086ba009b847edec6f30d25eb311b9154ae08819041a9`,
and requires `command -v python3` to resolve through the frozen command path to
`/lunarc/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3.11`
with SHA-256
`34f2f9f9561850d15d8060a2565c3a81046425faaba575687d3b75e1212d0f77`.

`umask 077` plus `set -o noclobber` makes all four bridge files create-only mode
`0600`; nonzero `sbatch`/parser exits stop. Absolute `/usr/bin/stat` plus Bash
predicates require each stderr file to exist as a regular non-symlink exact
mode-`0600` empty file.
The operator first unsets `BASH_ENV`, `ENV`, `PYTHONPATH`, `PYTHONHOME`, and
`PYTHONSTARTUP`. Exact `sbatch --export=NIL` then exports only Slurm/SPANK
variables and does not invoke `get-user-env`, preventing inherited `BASH_ENV`
startup before the trampoline body. Never use `RAW=$(sbatch ...)`: Bash command
substitution strips trailing LFs and cannot preserve the accepted byte grammar.
The V2
`parse-sbatch-job-id --input-path` route instead holds and rechecks an owned
regular link-count-one mode-`0600` file at the one exact frozen path under an
owned mode-`0700` parent. It
accepts only a canonical positive decimal byte string with exactly one final
LF. Missing LF, semicolon/cluster suffix, zero or leading zero, CR, whitespace,
extra line, symlink, hardlink, or other text fails closed with no stdout.
Every operator-side finalizer invocation runs under exact `python3 -I -S`, so
system/user `sitecustomize` is not a pre-module route. Parser success writes
only the exact digits plus one LF to its private stdout file. Empty parser stderr, Bash-builtin
one-line `read`, canonical-positive-decimal regex, and exact EOF are required
before `JOBID` exists. Start `watch-capture` immediately with that unchanged
ID; `<EXACT_NEW_SLURM_JOB_ID>` below is that value and no other.

Start the watcher immediately after this validation; do not wait for the job
terminal or perform a different identity lookup first.

## Frozen post-job sequence — not executed

After an authorized job exists, the V2 watcher shape is:

```bash
/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3 -I -S \
  /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-exec-successor-v2-20260824/development/p1-scienceagentbench-protected-rr1-execution-successor-v2-2026-08-24/protected_rr1_one_tuple_finalizer_v2.py \
  watch-capture \
  --job-id "$JOBID" \
  --output-root /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824/capture-parent/capture
```

The watcher retries only zero rows, nonterminal empty/`gpua40i` partition
profiles, and terminal rows with enumerated empty/`Unknown` readiness
sentinels. It fails immediately on wrong nonblank partition or malformed rows.
Only a fully strict terminal `Partition=gpua40i` row starts the unchanged
2-second/20-second/240-second post-terminal capture sequence.

If and only if the private runtime evidence and scheduler capture complete, the
V2 finalization shape is:

```bash
/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0/bin/python3 -I -S \
  /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/repo-exec-successor-v2-20260824/development/p1-scienceagentbench-protected-rr1-execution-successor-v2-2026-08-24/protected_rr1_one_tuple_finalizer_v2.py \
  finalize \
  --evidence-root /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824/runtime-parent/evidence \
  --capture-root /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824/capture-parent/capture \
  --output-root /projects/hep/fs10/scratch/scyiu/orion_p1_sab_protected_rr1_direct_route_v1_20260824/live-rr1-exec-successor-v2-20260824/final-parent/result
```

The three path values must be distinct, canonical, and privately custodied; the
result root must not exist. The finalizer does not submit jobs, generate,
contact a network/API, read credentials or protected packet bodies, invoke the
official evaluator, open outcomes, or finalize the 918-tuple population.

## Exact operator success gates and stop rule

Proceed through the three stages only on exit zero plus the corresponding exact
body-free terminal:

```text
job:       P1_SAB_PROTECTED_RR1_ONE_TUPLE_CAPTURED__SCHEDULER_FINALIZATION_PENDING
watcher:   P1_SAB_PROTECTED_RR1_POST_JOB_SCHEDULER_CAPTURE_PASS
finalizer: P1_SAB_PROTECTED_RR1_ONE_TUPLE_POST_JOB_FINALIZATION_PASS
```

Hard-stop on a missing or wrong terminal, any nonzero exit, any typed watcher or
finalizer `CANNOT_CHECK`, cleanup drift, evidence drift, path drift, hash drift,
or a pre-existing/reused runtime, capture, or final result root. Do not delete,
overwrite, rename into place, or reuse a failed root to continue the sequence.
No downstream PASS can cure a failed upstream gate.

## Failed-job retry ledger

Job `3537740` was `FAILED`, exit `2:0`, before Python or any generation route.
Its body-free evidence hashes and byte counts are frozen in
`FAILED_JOB_3537740_NO_GENERATION_CERTIFICATE_V1.json`. Accounting is exact:

- scheduler GPU allocation seconds already consumed: `1`;
- generation attempts consumed: `0`;
- plan-clock allocated-accelerator-seconds: `0`;
- repaired resubmission generation ordinal: `1`;
- hidden second sample: `false`;
- scheduler cost erased: `false`.

The certificate is a necessary pre-resubmission record, not permission to
resubmit.

## Claim boundary

A future V2 PASS would establish only one tuple's bounded scheduler and runtime
metadata conformance. It would not establish official correctness, comparative
superiority, production admissibility, whole-node or 918-tuple exclusivity,
independent review, or scientific validity. Until a future authorized execution
and finalization, scheduler finalization remains not re-executed, production
admissibility is `CANNOT_CHECK`, scientific authority delta is `NONE`, and the
Runner V2 population ledger remains `NOT_FINALIZED_918_TUPLES`.
