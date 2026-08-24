# Failure and repair log

This log retains adverse or failed checks from development and execution. No
failed probe is deleted or silently normalized.

## F01 — login-shell Ollama was not on `PATH`

- **Observed:** the initial LUNARC inventory printed no `command -v ollama`
  result in the login shell.
- **Cause:** Ollama is site-provided as an environment module, not a base-shell
  executable.
- **Repair:** load the exact `ollama/0.32.14` module in the batch job.
- **Verification:** `/sw/pkg/ollama/0.32.14/bin/ollama`, client version
  `0.32.14`, 39,138,928 bytes, SHA-256
  `d0758d38ac5882a2c68fd930d0c1220af1952469fa9f30c268746d4021709bf4`.

## F02 — first long-context fixture exceeded the frozen context window

- **Observed:** source tokenizer precheck of the initial 1,800-line fixture
  reported `raw_tokens 41556` against `num_ctx=32768`.
- **Cause:** the filler lines tokenize into substantially more than whitespace
  word count suggests.
- **Repair:** before job submission, reduce the frozen filler to 1,200 lines,
  redistribute all six markers, and raise the meaningful lower-bound check to
  24,000 tokens.
- **Verification:** the pinned source tokenizer then reported exactly 27,756 raw
  prompt tokens, below 32,768 with room for the 128-token response. The live
  Ollama-reported count is independently retained in the smoke receipt.

## F03 — GNU `find -printf` was unavailable on the local macOS host

- **Observed terminal:** `find: -printf: unknown primary or operator`.
- **Cause:** BSD `find` does not implement GNU `-printf`.
- **Repair:** use portable `find ... -print`; this did not alter any scientific
  fixture, hash, or remote execution.

## F04 — no owner-authoritative currency conversion exposed by LUNARC probes

- **Observed:** `projinfo` exposes project use/allocation in hours and SLURM
  exposes accounting TRES including `billing`; neither command exposes an
  owner-authoritative allocation-to-USD/SEK conversion. No cost/rate/billing
  environment variable was present.
- **Repair:** none is scientifically admissible. The final billed-USD field is
  null with
  `CANNOT_CHECK_OWNER_AUTHORITATIVE_ALLOCATION_COST_CONVERSION_UNAVAILABLE`.
  GPU seconds, SLURM billing units, and sampled energy remain separate receipts.

## F05 — single-stream model download became low-throughput

- **Observed:** after 9 minutes the resumable single `curl` had staged
  5,995,323,392 bytes and its rolling average had fallen to about 10.4 MB/s,
  with a displayed 19-minute remaining estimate.
- **Cause:** the single HTTP transfer showed bursty per-connection throughput;
  the artifact server advertised and honored byte ranges.
- **Repair:** stop the single stream, retain an exact 4,639,172,392-byte prefix
  (two equal eighths), and fetch the remaining six disjoint, exhaustive ranges
  in parallel. Final assembly remains gated by exact byte count and the original
  full-file SHA-256, so range concurrency cannot weaken artifact identity.

## F06 — first parallel downloader exited on an unbound PID accumulator

- **Observed terminal:**
  `parallel-download.sh: line 9: pids: unbound variable`.
- **Cause:** `set -u` encountered `pids="$pids $!"` before `pids` was initialized.
- **Repair:** retain the already-running part-2 transfer, initialize `pids=""`,
  start parts 3–7, wait/poll all six parts, require each to be exactly
  2,319,586,196 bytes, assemble in ordinal order, require 18,556,689,568 total
  bytes, and verify the full expected SHA-256 before job submission.

## F07 — pre-submit review found an unstable remote manifest ordering

- **Observed:** static review found that the first job-script draft opened
  `REMOTE_RUN_SHA256SUMS.tmp` before `find`, so the in-progress manifest could
  hash itself; the exit trap would also append to `cleanup.log` after hashing.
- **Cause:** manifest creation preceded final cleanup and did not exclude its
  temporary output.
- **Repair:** emit the terminal, run cleanup explicitly, disable the exit trap,
  restore fail-closed shell options, and only then hash all stable files while
  excluding `REMOTE_RUN_SHA256SUMS` itself. This defect was repaired before the
  submitted job and produced no accepted receipt.

## F08 — monitoring wrapper misquoted an `awk` field reference

- **Observed terminal after successful assembly:**
  `bash: line 1: $1: unbound variable`.
- **Cause:** nested local/remote quoting allowed the remote strict shell to
  expand an intended `awk` `$1` field reference.
- **Repair:** do not repeat the 18.6 GB transfer or assembly. The preceding
  `model.sha256` line already recorded the exact expected full-file digest;
  the batch script independently rechecks byte count and SHA-256 using its own
  correctly single-quoted `awk` program before allocating inference authority.

## F09 — initial `gpua40` queue excluded the only idle node

- **Observed:** job `3533950` remained `PENDING (Resources)` on `gpua40`.
  `scontrol` reported `ExcNodeList=cg[01-02]`; the otherwise idle A40 node was
  `cg02`. The scheduler projected `StartTime=2026-08-24T17:16:06` on `cg04`.
- **First repair attempt and exact adverse terminal:** updating the same pending
  job to a two-partition request failed without mutation:
  `Multiple partition job request not supported when a partition is set in the association for job 3533950`.
- **Shortest accepted repair:** no duplicate job was submitted. After inspecting
  `gpua40i` association/capacity, update the same job ID to the single
  `gpua40i` partition. Job `3533950` entered `RUNNING` immediately at
  `2026-08-24T13:56:21+02:00`. The execution receipt retains the actual final
  partition and node.

## Remote execution failures

## F10 — job 3533950 reached `zip(..., strict=True)` TypeError after ten valid calls

- **Observed:** job `3533950` completed model import and ten generation calls,
  then failed before the long-context call with exit `1:0`. Exact terminal:
  `TypeError: zip() takes no keyword arguments` at
  `positions = dict(zip(..., strict=True))`. The job-level failure receipt bound
  the failed harness command and line 123; no pass receipt was emitted.
- **Causal boundary:** this traceback is compatible with a `zip`
  implementation or interpreter lacking support for `strict`. The exact
  original submitted harness and batch-script bytes are not retained, so exact
  byte reproduction is
  `CANNOT_CHECK_EXACT_ORIGINAL_SUBMITTED_BYTES_NOT_RETAINED`; no specific
  interpreter cause is established.
- **Repair:** replace the version-specific keyword with an explicit length
  assertion followed by ordinary `zip`. Preserve failed job `3533950` in the
  packet, re-run focused local compilation, and submit one clean whole smoke on
  the already-proven `gpua40i` route. This describes the applied source change,
  not proof that the unavailable original bytes were reproduced. No failed
  output is promoted.

## F11 — first loopback readiness probe raced server startup

- **Observed terminal in job 3533950 stderr:**
  `curl: (7) Failed to connect to 127.0.0.1 port 11471: Connection refused`.
- **Cause:** the first one-second readiness iteration ran before Ollama bound
  the loopback socket.
- **Repair:** the bounded readiness loop retried and succeeded; all ten model
  calls returned HTTP 200. This expected transient did not cause the job
  failure, but it is retained rather than hidden.

## F12 — remote compatibility compile made a hash-glob directory

- **Observed after the repaired code passed remote construction:**
  `sha256sum: .../code/__pycache__: Is a directory`.
- **Cause:** `python3 -m py_compile` created `__pycache__`, while the ad hoc
  verification command and first batch draft used a broad `code/*` hash glob.
- **Repair:** remove the remote cache, hash only `-type f` entries in sorted
  order, and update the batch pre-run manifest to the same file-only rule. This
  occurred before the clean rerun and emitted no accepted receipt.

## F13 — clean rerun inherited a scheduler-side `cg13` exclusion

- **Observed:** repaired job `3533966` was pending on `gpua40i` with
  `ExcNodeList=cg13` and a projected `2026-08-24T19:56:24` start, although
  `cg13` had no allocated GPU in `AllocTRES`.
- **Cause:** the immediate source of the exclusion field was not established;
  no explicit exclusion exists in the submitted script. It is reported as a
  scheduler-state fact, not explained speculatively.
- **Shortest repair:** update the same pending job with an empty
  `ExcNodeList`; do not submit a duplicate. Job `3533966` entered `RUNNING` on
  `cg13` at `2026-08-24T14:07:58+02:00`.

## F14 — partition-filtered allocation probe was unsupported

- **Observed terminal:**
  `Error: Cannot tell you about partition gpua40i.` with return code 255 from
  `projinfo -p gpua40i lu2026-2-51`.
- **Cause:** this site helper does not expose that partition-filtered view.
- **Repair:** retain the failed command/terminal, run the supported unpartitioned
  `projinfo lu2026-2-51`, and pair it with SLURM association/configuration
  fields. These still expose hours/TRES but no authoritative currency
  conversion, so billed USD remains `CANNOT_CHECK`.

## F15 — same-seed byte replay failed on the pinned GPU route

- **Observed in job `3533966`:** both replay request SHA-256 values were exactly
  `68b4bf4bf0c5c59e603bb1c17d0c40edb552ea2173739d4910765b2a5d7e702d`
  and both used seed 101, but response-text SHA-256 values were
  `3c9ae2bcb19e36b9b3c6f15aa0436ba7284dc6b6ffe6f80450079dbe0c5cf42c`
  and `ebeedd347bd50185bc414a472b0a2d616eaf1345c20c72866ecdf0502f8005b2`.
  The harness intentionally returned 2 and the job ended `FAILED 2:0`.
- **Competing mechanisms:** GPU/kernel nondeterminism, Ollama/llama.cpp prompt
  cache behavior, or incomplete seed determinism are all compatible with this
  witness; the smoke does not identify which mechanism caused it.
- **Correct response:** do not weaken the frozen replay gate or relabel the job
  as a pass. Preserve the adverse receipt. Different-seed sensitivity still
  passed with three distinct outputs, and the long-context witness independently
  passed all six markers at 27,764 reported prompt tokens.
- **Next discriminator:** a separately preregistered CPU-only versus GPU,
  cold-model versus warm-cache replay matrix would localize the mechanism. It
  was not run here because it would be a new experiment, not a repair of this
  frozen smoke.

## F16 — first remote-manifest verification used the wrong working directory

- **Observed:** `sha256sum -c` reported every `./...` manifest entry as
  `No such file or directory` and concluded that 44 files could not be read.
- **Cause:** the manifest intentionally uses paths relative to each job
  directory, but the first verification ran from the login home directory.
- **Repair:** change into each job directory before `sha256sum -c`. Both job
  manifests then printed `REMOTE_MANIFESTS_PASS`; no file or digest changed.

## F17 — RR phase 1 exhausted its frozen output cap

- **Observed in job `3533966`:** `rr_phase1` reported
  `eval_count=512`, `done_reason=length`, and response-text SHA-256
  `78507b28d1181697cc6ca458dfc647486cd163d75fe6a92f6d597251b1ffd479`.
  The other arm calls stopped normally.
- **Cause:** the generated RR program exceeded the frozen 512-token output cap;
  whether the excess came from verbosity or task formulation is not identified.
- **Correct response:** preserve this as a second adverse gate failure. Do not
  raise the cap after seeing the output, and do not claim a complete RR final
  candidate. A future prospectively frozen run can select a larger *matched*
  cap for all arms, but this smoke cannot be retroactively repaired.
