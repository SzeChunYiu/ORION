# P1 ScienceAgentBench outcome-analysis freeze V1 — handoff

## Terminal

`P1_SAB_OUTCOME_ANALYSIS_CONTRACT_AND_100K_SYNTHETIC_VALIDATION_READY__OFFICIAL_OUTCOMES_AND_RUNTIME_CANNOT_CHECK__ZERO_OFFICIAL_RECORDS_OPENED`

This additive packet freezes and executes the future outcome-analysis decision
function on generated synthetic nonbenchmark receipts only. It did not retrieve
or inspect the benchmark archive, task text, candidate/program bodies, official
evaluator records, judge responses, credentials, or outcomes. It did not invoke
the official evaluator. It is not benchmark evidence, preregistration custody,
independent review, or scientific promotion.

Scientific authority delta: `NONE`.

## Independent-review repair disposition

The initial PR bytes were `NO-GO`. This revision closes the three reported
analysis-contract defects without opening outcomes:

1. **Exact cost arithmetic:** every accepted decimal becomes an unbounded
   integer coefficient over `10^scale` and then an exact `Fraction`. Arm totals,
   the strongest-comparator denominator, multiplication by exact `3/2`, and the
   pass/fail comparison never use ambient decimal or float precision. The
   adversarial per-attempt RR value
   `1.500000000000000000000000000001` against comparator value `1` now fails;
   the result reports the exact reduced ratio as well as a labeled rounded
   display.
2. **Duplicate JSON names:** `object_pairs_hook` rejects a repeated member at
   any depth. A hostile ledger containing `split=validation` followed by
   `split=verified` produces `CANNOT_CHECK` instead of last-member-wins
   acceptance.
3. **Hash-seed determinism:** artifact hash fields are one fixed tuple, all
   residual set differences are sorted, and subprocess validation proves
   byte-identical canonical `CANNOT_CHECK` results under `PYTHONHASHSEED=1` and
   `777`.

## Byte-bound analysis identity

| Item | Frozen value |
|---|---|
| Population | Verified ScienceAgentBench task IDs `1..102`, exactly once |
| Source identity | dataset revision `9c6e96c9e74572e979b0930ee735041cef528cb7`; verified Parquet SHA-256 `c6f937863a220bd1762a00c20a0f79cc8dfca900b819bdb552150310731ae147`; official source commit `c26e151ed601ba109dc4d35e057ff8e73fec469d` |
| Discipline strata | 27 bioinformatics, 20 computational chemistry, 27 geographical information science, 28 psychology/cognitive science; exact task map in `ANALYSIS_CONTRACT_V1.json` |
| Arms / attempts | `RR`, `OS`, `NR`; attempts `1`, `2`, `3`; one task is the paired inference unit |
| Official records | Exactly 102 task-level parseable receipts, each containing exactly nine `(arm, attempt)` records: 918 nested records total |
| Task solved | For one task-arm, at least one of all three complete attempts has integer `valid_program == 1` and exact decimal `success_rate == 1` |
| Strongest comparator | Larger aggregate solve rate between OS and NR; exact tie selects OS by frozen arm order |
| Point gain | RR minus strongest comparator `>= 0.08` |
| Paired intervals | RR--OS and RR--NR; 100,000 within-discipline paired task-bootstrap replicates; both 95% lower bounds `> 0` |
| Discipline guard | In every discipline, RR--OS and RR--NR each `>= -0.05` |
| Cost guard | RR all-attempt primary generation-cost quantity / strongest-comparator all-attempt quantity `<= 1.5` under one identical prospectively frozen metric identity/allocation rule |
| Missingness | Any missing, duplicate, partial, wrong-split, unparseable, runtime-failed or evaluator-failed task/attempt is gate-level `CANNOT_CHECK`, never solved zero |

Contract SHA-256:
`0cae220a5b2f73156eda63a01f769dfdecbf8ad1fa16bd0995e3f906cff391d4`.
The analyzer hardcodes and verifies this digest before accepting a ledger.

## Exact bootstrap mechanics

- Algorithm: local reference `MT19937_REFERENCE_UINT32_V1`, not Python's
  high-level `random` helpers.
- Seed: decimal `20260824`, reduced to the frozen 32-bit initialization.
- Reference initialization: 624 uint32 words, multiplier `1812433253`, modulo
  `2^32`.
- Index draw: uint32 rejection below `floor(2^32 / n) * n`, then modulo `n`, so
  no modulo bias.
- Stratum order: bioinformatics, computational chemistry, geographical
  information science, psychology/cognitive science; ascending integer task ID
  within each stratum.
- Each replicate draws the original number of tasks with replacement from each
  stratum. The same draw supplies RR, OS, and NR, preserving pairing.
- Interval: empirical percentile; one-indexed nearest rank `ceil(qB)` at
  `q=0.025` and `q=0.975`. With `B=100000`, zero-indexed positions are `2499`
  and `97499`.
- The result reports a SHA-256 over all 100,000 paired contrast-numerator pairs,
  binding the realized deterministic resample stream.

The validator independently checks the standard seed-5489 MT19937 first-five
uint32 known-answer vector.

## Cost identity and the LUNARC/open-weight boundary

Missing billed USD is not zero, and `0/0` is never accepted. The ledger must
bind exactly one cost metric before candidate generation and before any outcome
opening. The canonical metric object and its SHA-256 must also be carried by the
prospectively frozen run plan/candidate seal:

1. **`BILLED_USD`** — unit `USD`; sum authoritative provider-billed USD over
   all attempts with no outcome selection. Per-attempt primary quantity must
   equal the retained billed-USD field.
2. **`ALLOCATED_ACCELERATOR_SECONDS`** — unit `accelerator-second`; for every
   attempt sum exclusive accelerator count times monotonic generation wall
   seconds, forbid overlap double-allocation, then sum all attempts. Billed USD
   remains separately retained when available.

There is no post-outcome fallback between identities. A missing, altered,
non-authoritative, or post-outcome-selected identity/quantity is
`CANNOT_CHECK`. A zero strongest-comparator denominator is
`CANNOT_CHECK_COST_DENOMINATOR_ZERO`. Billed USD and official-evaluator billed
USD are availability-reported separately; missing entries are never included as
zeros.

This analysis capability does **not** amend Runner V1. Runner V1 currently
requires per-attempt `billed_cost_usd` on successful candidate records. An
open-weight/LUNARC route without that value therefore remains blocked before
analysis until an additive, prospectively reviewed run-plan/candidate-seal
amendment carries the same cost-metric binding. Do not weaken or reinterpret the
merged runner from this packet.

## Outcome ledger boundary

`ANALYSIS_CONTRACT_V1.json` fixes all top-level, task-record, attempt-record,
failure, hash, decimal, metric and retention fields. Important properties:

- all artifact identities are lowercase 64-hex SHA-256 strings;
- task IDs are canonical decimal strings, not integers or zero-padded text;
- success rate and cost quantities are exact decimal strings with no sign,
  exponent, non-finite value, Boolean coercion, or implicit rounding;
- duplicate JSON member names are rejected at every nesting depth; a later
  member never overwrites an earlier member;
- OK records require complete outcomes and primary cost; typed
  `CANNOT_CHECK` records retain available partial hashes/costs and keep outcomes
  null;
- any typed evaluator failure makes the complete gate `CANNOT_CHECK` before
  solve rates or bootstrap;
- attempts determine within-task success but never increase inferential `n`;
- all 306 generation attempts per arm contribute to primary cost, independent
  of which attempt solved; and
- decimal strings become unbounded integer coefficients over `10^scale`; cost
  totals, ratios, and the `3/2` gate use exact `Fraction` arithmetic with no
  ambient precision;
- cost totals are exact terminating decimals and ratios include an exact
  reduced fraction plus a separately labeled 12-place half-even display; the
  display never determines pass/fail; and
- validation-reason order is frozen, so canonical result bytes are invariant
  across `PYTHONHASHSEED` values.

## CLI

The production interface has no seed, replicate, threshold, task, discipline,
arm, attempt, cost-identity, or interval override:

```text
python sab_outcome_analysis_v1.py \
  --outcome-ledger /approved/external/run/OUTCOME_LEDGER_V1.json \
  --output /approved/external/run/ANALYSIS_RESULT_V1.json
```

This is documentation only. It was not run on an official ledger. An invalid,
missing or malformed ledger still writes a typed `CANNOT_CHECK` result. A
committed-contract mismatch is a hard error. Future official ledgers and results
remain outside ORION.

## Synthetic validation receipt

`validate_analysis_freeze_v1.py` generates all fixtures in memory or a temporary
directory. It commits no fixture ledger. The focused standard-library run covers:

- the contract digest, exact population/discipline map and record counts;
- the MT19937 known-answer vector;
- one complete 102-task/918-attempt execution using all 100,000 frozen
  bootstrap replicates;
- both strongest-comparator paths and the OS tie break;
- gain `0.08`, discipline `-0.05`, paired-lower-bound and cost `1.5` gates;
- an exact `1.5 + 10^-30` per-attempt RR cost regression, which must fail even
  though the labeled 12-place ratio display rounds to `1.500000000000`;
- all-attempt cost, separate evaluator cost, zero denominators, billed-USD and
  allocated-accelerator-second identities;
- cost-identity/hash drift and missing billed USD under a billed-USD primary;
- missing/duplicate/partial/wrong-split/evaluator-failed records and hostile
  JSON type coercions; and
- duplicate JSON names (`validation` then `verified`) and byte-identical
  `CANNOT_CHECK` output across separate `PYTHONHASHSEED` processes; and
- absence of network, subprocess, high-level random, provider, Docker,
  official-evaluator, NumPy, SciPy or CLI override surfaces.

Receipt terminal:
`P1_SAB_OUTCOME_ANALYSIS_FREEZE_SYNTHETIC_HOSTILE_VALIDATION_PASS__OFFICIAL_OUTCOMES_CANNOT_CHECK__ZERO_OFFICIAL_RECORDS_OPENED`.

## What this closes

- the exact future outcome-ledger schema and complete-record guard;
- task/discipline/arm/attempt identity for analysis;
- strongest-comparator point selection and OS tie break;
- both paired contrasts, reference RNG, seed, replicate count, paired
  stratification, percentile-rank rule and strict lower-bound gates;
- point gain, discipline noninferiority and all-attempt cost thresholds;
- a prospectively hash-bound billed-USD or accelerator-second cost identity,
  with undefined/non-authoritative cost failing closed; and
- deterministic result terminals `PASS`, `FAIL`, or `CANNOT_CHECK` without
  missing-to-zero conversion.

## What remains `CANNOT_CHECK`

- official archive identity/decryption/extracted manifest and lawful runtime;
- final model/provider/tokenizer/prompts/seeds/budgets/credential bindings;
- any Runner V1-compatible open-weight cost-accounting amendment;
- pinned evaluator images/dependencies, authorized visual judge route, and
  stochastic response retention;
- an independently reviewed outcome adapter that transforms all nine official
  evaluator outputs per task into the frozen 102-record ledger without loss;
- external pre-outcome signing/custody of the complete protocol, runner,
  evaluator adapter, cost-metric binding and analysis bytes;
- all official candidates, executions, evaluator records and results;
- independent custody/adjudication, protected replication, manuscript changes,
  superiority, transition authority, or any other scientific promotion.

Until all of those are closed, the scientific terminal remains
`CANNOT_CHECK`; the synthetic `PASS` exercises code paths only.

## Retention boundary

Do not commit any benchmark archive/extracted file, task text, model output,
candidate/program body, official evaluator/gold/rubric/judge body, evaluator
log, credential, container layer, official outcome ledger, or official analysis
result. Keep authorized future material on approved external storage. This PR
contains only the contract, standard-library analyzer/validator, synthetic
receipt, development/handoff prose and hashes. It must remain unmerged pending
review.
