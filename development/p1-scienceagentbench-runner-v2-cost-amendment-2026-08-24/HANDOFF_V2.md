# P1 ScienceAgentBench Runner V2 allocated-cost amendment — handoff

## Terminal

`P1_SAB_RUNNER_V2_ALLOCATED_COST_SYNTHETIC_HOSTILE_VALIDATION_PASS__OFFICIAL_RUN_AND_OUTCOMES_CANNOT_CHECK__ZERO_TASKS_RUN__ZERO_OUTCOMES_OPENED`

## What is frozen

- Additive amendment only; Runner V1 bytes are unchanged and hash-checked.
- The amendment accepts only the open-weight LUNARC
  `ALLOCATED_ACCELERATOR_SECONDS` route.
- Metric identity, exact Analysis Freeze allocation rule, prospective binding
  phase, LUNARC/SLURM/exclusive-GPU route, identical RR/OS/NR GPU count and exact
  `CLOCK_MONOTONIC_RAW` boundaries are canonical-hash bound before generation.
- Exactly 918 task/arm/attempt receipts are required. Every record repeats the
  same metric identity/hash and timing-provenance hash.
- Per attempt primary quantity is derived exactly as GPU count times monotonic
  elapsed nanoseconds divided by `1e9`; input floats and noncanonical decimals
  are rejected.
- Billed USD is separate: canonical value plus `AVAILABLE`, or JSON null plus
  `CANNOT_CHECK`. Missing is never imputed as zero.
- Both OS and NR all-attempt totals must be positive, so the later
  outcome-selected strongest comparator cannot have a zero denominator.
- All four CLI paths must be pairwise distinct by resolved path and, where
  existing, device/inode identity. Symlink/hardlink aliases and either output
  overwriting an input or the other output fail before validation/write.
- Run plan and candidate ledger are each read once; their hashes and parsed
  strict-JSON objects come from the same immutable byte buffers.
- The output is a deterministic 102 x 9 generation-cost projection using the
  exact Analysis Freeze V1 metric and generation field names/types. It contains
  no evaluator or outcome fields and is not presented as a full outcome ledger.

## What is unchanged

`BILLED_USD` stays on merged Runner V1. This amendment refuses that metric; it
does not copy, shadow, widen or reinterpret Runner V1. The following upstream
identities must still match:

```text
Runner V1 contract  e191540f131b3e7e33b0c040900bea94336dbd0d704b247b547a5c361b6e242f
Runner V1 module    15d6f511be9b3b1dbac408cc41812b0f72e1dd7aa700983035438efb8ed416df
Analysis contract   0cae220a5b2f73156eda63a01f769dfdecbf8ad1fa16bd0995e3f906cff391d4
Analysis merge      957bc82ff2bcffa61a0bab96bc76fc6f811a9d10
```

## Focused verification

From a clean checkout at the branch head:

```bash
python3 -m py_compile \
  development/p1-scienceagentbench-runner-v2-cost-amendment-2026-08-24/sab_runner_v2_cost_amendment.py \
  development/p1-scienceagentbench-runner-v2-cost-amendment-2026-08-24/validate_runner_v2_cost_amendment.py

python3 \
  development/p1-scienceagentbench-runner-v2-cost-amendment-2026-08-24/validate_runner_v2_cost_amendment.py

(cd development/p1-scienceagentbench-runner-v2-cost-amendment-2026-08-24 \
  && shasum -a 256 -c SHA256SUMS)

git diff --check origin/main...HEAD
```

Expected focused terminal:

```text
Ran 35 tests
OK
P1_SAB_RUNNER_V2_ALLOCATED_COST_SYNTHETIC_HOSTILE_VALIDATION_PASS tests=32 official_tasks=0 official_outcomes=0
```

Do not run pytest or CI for this packet.

## Future metadata-only invocation

This command validates existing metadata; it does not generate a candidate or
invoke an evaluator:

```bash
python3 \
  development/p1-scienceagentbench-runner-v2-cost-amendment-2026-08-24/sab_runner_v2_cost_amendment.py \
  --run-plan /approved/external/run-plan-allocated-v2.json \
  --candidate-ledger /approved/external/candidate-ledger-allocated-v2.json \
  --output-ledger /approved/external/analysis-generation-cost-projection-v2.json \
  --output-receipt /approved/external/candidate-cost-seal-receipt-v2.json
```

All paths must be absolute. Production plans, ledgers and receipts stay outside
the repository.

## Review-required next steps

1. Obtain review of the amendment PR and do not activate unmerged bytes.
2. Before any generation, owner/external custody must freeze the complete V2
   plan, metric object/hash, route object/hash and measurement object/hash.
3. Independently inspect the future LUNARC generation adapter to prove
   `clock_gettime_ns(CLOCK_MONOTONIC_RAW)` occurs at the exact frozen boundaries
   and that each GPU allocation is exclusive/no-overlap. This packet validates
   receipts; it does not instrument or prove a future adapter by itself.
4. Seal all 918 candidate records and retain nullable billed USD without
   imputation.
5. A separately reviewed outcome adapter may copy this projection verbatim into
   the merged Analysis Freeze outcome ledger and add the unavailable
   evaluator/result fields only after authorized evaluation.
6. External pre-outcome signing/custody must bind runner, plan, generator,
   projection, evaluator adapter and analyzer bytes before any outcome opening.

## Remaining `CANNOT_CHECK`

- exact production model/tokenizer/prompt/seed/budget/credential bindings;
- a concrete production LUNARC generation adapter and observed monotonic timing;
- official candidate generation, archive/runtime/evaluator authorization and
  evaluator identity;
- any full outcome-ledger adapter or official outcome;
- independent custody/adjudication/replication;
- any cost ratio, pass/fail analysis, manuscript change, superiority or
  transition authority.

Synthetic verification is conformance evidence only. Scientific authority
delta remains `NONE`.
