# P1 ScienceAgentBench LUNARC generation adapter V1 — handoff

## Terminal

`P1_SAB_LUNARC_GENERATION_ADAPTER_SYNTHETIC_HOSTILE_VALIDATION_PASS tests=34 official_tasks=0 official_outcomes=0`

## What this increment closes

- `GenerationAttemptCapture.call_model()` enforces exact RR, OS and NR phase
  order and places exactly two injected raw-clock reads around the complete
  first-to-final model-operation interval.
- The default reader is exactly
  `time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW)`. Missing raw-clock support,
  floats, Booleans, negatives and decreasing values fail closed; there is no
  clock, server-timing or telemetry fallback.
- Successful capture remains
  `TIMING_CAPTURED__ALLOCATION_FINALIZATION_PENDING`. It cannot write the Runner
  V2 exclusivity token. Successful and `CANNOT_CHECK` receipts are mutually
  exclusive one-shot terminal emissions; a phase or metadata failure cannot be
  corrected and retried inside the same capture.
- Finalization requires 918 capture tuples and 918 scheduler tuples, one unique
  SLURM job or array element per tuple, matching in-job snapshots, matched frozen
  GPU counts, scheduler-confirmed consumable exclusive GRES and nonoverlapping
  half-open allocation intervals for each node/GPU key. Running or pending jobs
  cannot be finalized; each record must carry one normalized terminal state.
- Cross-job allocation overlap uses scheduler UTC intervals. Raw-monotonic
  coordinates from different jobs, hosts or boots are never compared.
- Only after scheduler finalization does the adapter project
  `EXCLUSIVE_NO_OVERLAP_CONFIRMED` into a complete V2 ledger. The unchanged V2
  validator revalidates all 918 records.
- The adapter seal hash-binds the exact run-plan snapshot, capture ledger,
  scheduler evidence, allocation index, final V2 ledger, this adapter/contract,
  unchanged Runner V2 and unchanged Runner V1.
- Finalizer outputs use new-file-only creation. If a later output destination is
  won by another writer, earlier unchanged outputs from that invocation are
  rolled back rather than leaving an unsealed V2 ledger.

## Driver integration interface

A separately frozen generation driver imports `sab_lunarc_generation_adapter_v1.py`,
constructs one `GenerationAttemptCapture`, and calls only:

```python
rr0 = capture.call_model("RR_PHASE0", lambda: client.complete(rr0_request))
rr1 = capture.call_model("RR_PHASE1", lambda: client.complete(build_rr1(rr0)))
receipt = capture.finish(base_candidate_record)
```

OS uses only `OS_PHASE1`; NR uses `NR_PHASE0` then `NR_PHASE1`. Prompt/request
construction before the first operation is outside the interval. All state
processing between phases remains inside it. A generation exception records an
immediate end read but permits only `cannot_check_sidecar()`, never a V2 record.

`run_lunarc_attempt_v1.sh` maps one new output directory and one wrapper
invocation to one tuple, retains a raw `scontrol show job -dd` snapshot and
invokes exactly one frozen driver. The snapshot and SLURM environment are not
exclusivity proof. An independently retained post-job `sacct`/`scontrol` export
and scheduler-config snapshot must be normalized into the exact
scheduler-evidence schema before finalization. The finalizer CLI requires both
raw snapshot files and rejects either file when its SHA-256 does not match the
corresponding scheduler-evidence field.

## Focused verification

From a clean checkout at this branch head:

```bash
python3 -m py_compile \
  development/p1-scienceagentbench-lunarc-generation-adapter-v1-2026-08-24/sab_lunarc_generation_adapter_v1.py \
  development/p1-scienceagentbench-lunarc-generation-adapter-v1-2026-08-24/validate_lunarc_generation_adapter_v1.py

bash -n \
  development/p1-scienceagentbench-lunarc-generation-adapter-v1-2026-08-24/run_lunarc_attempt_v1.sh

python3 \
  development/p1-scienceagentbench-lunarc-generation-adapter-v1-2026-08-24/validate_lunarc_generation_adapter_v1.py

(cd development/p1-scienceagentbench-lunarc-generation-adapter-v1-2026-08-24 \
  && shasum -a 256 -c SHA256SUMS)

git diff --check origin/main...HEAD
```

Do not run pytest or CI for this bounded packet.

## Remaining `CANNOT_CHECK`

- exact production model, tokenizer, prompts, seeds, budgets and driver bytes;
- live `CLOCK_MONOTONIC_RAW` observations from an authorized generation run;
- real LUNARC scheduler/GRES configuration and all 918 allocation records;
- protected archive/task/runtime authorization and all candidate metadata;
- official evaluator identity, invocation or outcome;
- external custody/signing, replication, cost ratios, task success, manuscript
  changes, superiority or scientific transition authority.

The earlier adverse Ollama evidence remains adverse. The distinct direct-server
synthetic witness remains non-composable and does not establish production
admissibility. This packet is synthetic conformance evidence only;
`scientific_authority_delta = NONE`.
