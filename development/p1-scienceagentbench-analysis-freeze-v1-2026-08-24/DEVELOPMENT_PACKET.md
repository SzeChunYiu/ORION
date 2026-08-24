# P1 ScienceAgentBench outcome-analysis freeze V1 — development packet

**Development question:** Can the 102-task, three-arm, three-attempt
ScienceAgentBench decision rule be frozen as a deterministic, task-paired,
fail-closed analysis contract before any official evaluator outcome is opened?

**Base subject:** `cae0c2699ed61f0c19086375a99a36b58ed42e9b` (freshly fetched
`origin/main` at lane creation).

**Predecessor bindings:** the merged outcome-blind preflight and verified runner
packets under `development/p1-scienceagentbench-preflight-2026-08-24/` and
`development/p1-scienceagentbench-runner-v1-2026-08-24/`.

**Authority:** analysis-contract engineering and synthetic nonbenchmark
validation only. This packet does not access a benchmark archive, task text,
candidate/program body, official evaluator record, judge response, credential,
or official outcome. It does not run the official evaluator or change any
scientific claim. Scientific authority delta: `NONE`.

## Atomic development questions

1. Can the analysis population be fixed to canonical task IDs `1..102`, the
   exact four-discipline assignment, arms `RR/OS/NR`, and attempts `1/2/3`
   without opening task or outcome bodies?
2. Can one parseable task-level official record be required for each of the 102
   tasks, with the exact nine nested `(arm, attempt)` records, so that missing,
   duplicate, partial, wrong-split, runtime-failed, or evaluator-failed input
   becomes `CANNOT_CHECK` rather than solved zero?
3. Can task success be collapsed only after all three attempt outcomes are
   present, using the frozen rule `valid_program == 1` and `success_rate == 1`
   on at least one attempt, while retaining every attempt for cost?
4. Can the stronger comparator be selected solely by the larger aggregate
   task solve rate between OS and NR, with a deterministic OS tie break, while
   both RR--OS and RR--NR inferential contrasts remain mandatory?
5. Can 100,000 paired task-bootstrap replicates be stratified within the exact
   four disciplines with a byte-specified RNG algorithm, seed, sampling order,
   unbiased index draw, and percentile-rank rule?
6. Can the gate require both paired 95% interval lower bounds strictly above
   zero, gain over the stronger comparator at least `0.08`, and every one of
   eight discipline-by-comparator contrasts at least `-0.05`?
7. Can exactly one primary generation-cost identity be prospectively bound as
   either authoritative billed USD or allocated accelerator-seconds under an
   exact non-overlap rule, then sum every attempt and require RR to remain at
   most `1.5` times the stronger comparator, while billed USD/evaluator cost are
   retained separately and missing or zero-denominator cost fails closed?
8. Can all decision paths be challenged using generated synthetic
   nonbenchmark receipts, including one complete 100,000-replicate execution,
   without exposing any official material?

## Incumbent mechanics and negative history recovered

- The outcome-blind preflight fixes the verified population at 102 tasks and
  records discipline counts of 27 bioinformatics, 20 computational chemistry,
  27 geographical information science, and 28 psychology/cognitive science.
- The verified runner fixes RR, OS, and NR, three attempts per task/arm, one
  final candidate per attempt, exact `--split verified`, and all-attempt usage
  accounting. It deliberately performs no statistical analysis.
- Upstream best-run summaries are not admissible for the prospective cost
  guard because they can report the cost of an outcome-selected attempt.
- Some owner-controlled open-weight routes may not produce authoritative
  per-attempt billed USD. Missing billed USD is not zero. The analysis contract
  therefore supports one pre-generation choice between `BILLED_USD` and
  `ALLOCATED_ACCELERATOR_SECONDS`; it hashes the identity, unit, allocation
  rule, and binding phase and forbids post-outcome fallback. This does not amend
  or weaken Runner V1's current billed-cost requirement; until a compatible
  upstream run-plan/candidate-seal amendment is separately reviewed, such a
  route remains `CANNOT_CHECK` before analysis.
- An absent record cannot be interpreted as failure to solve: it is compatible
  with generation failure, runtime failure, evaluator failure, credential
  failure, parser failure, or missing custody. Those states remain
  `CANNOT_CHECK`.
- Attempt rows and model seeds are repeated measurements within task, not new
  independent inference units. The task remains the paired unit.
- The preflight design names a 100,000-replicate stratified task bootstrap but
  leaves RNG bytes and exact percentile mechanics to this pre-outcome freeze.

## Bounded saturation assessment

### Knowledge saturation

The needed knowledge is bounded to the merged preflight population/mask
identity, the verified runner's exact arm-attempt product and accounting
semantics, elementary paired binary estimands, stratified nonparametric
bootstrap mechanics, exact decimal/fraction comparison, and fail-closed input
validation. This packet makes no claim about a new statistical method or about
ScienceAgentBench outcomes.

### Search-universe saturation

The admissible implementation universe is deliberately narrow: Python
standard-library duplicate-rejecting JSON/hash parsing, exact schema/set checks,
a local reference MT19937 uint32 implementation, paired within-stratum
resampling, exact integer-coefficient/`Fraction` gates, and generated synthetic
receipts. NumPy/SciPy,
provider SDKs, network clients, official evaluator imports, subprocesses,
benchmark archives, and outcome adapters are excluded because none is needed
to freeze or validate the decision rule.

### Formulation saturation

The task is not to estimate a publishable effect from current data. It is to
make exactly one future outcome ledger shape and exactly one decision function
admissible before official outcomes exist. The contract stops before outcome
acquisition, runtime custody, independent adjudication, manuscript integration,
or scientific promotion.

## Challenge to the saturation basis

A superficially correct analysis can still be outcome-adaptive or
anti-conservative if it silently changes bootstrap software behavior, samples
arms independently, pools attempts as independent rows, selects only the
stronger-comparator contrast for inference, resolves comparator ties
implicitly, uses a best-attempt cost, treats a missing evaluator receipt as a
zero, drops a bad discipline, applies `>` where `>=` was frozen (or vice versa),
or lets duplicate JSON names, booleans, `NaN`, or exponent strings pass through
last-member-wins parsing/coercion. It can also become byte-nondeterministic when
validation reasons are accumulated by iterating a Python set under different
hash seeds. The hostile validation must target those exact boundaries.

## Missed-knowledge hypotheses

1. A future official parser may emit one file per arm/attempt rather than one
   task aggregate; a separately reviewed adapter must construct and hash the
   required 102 records without changing their 918 nested outcomes.
2. Official `success_rate` serialization may be numeric rather than exact
   decimal text; conversion to the frozen decimal-string ledger must be explicit
   and receipt-bound, never implicit inside the analyzer.
3. Provider cost may arrive late, be zero due to credits, or omit failed calls;
   exact all-attempt billed cost may therefore remain unavailable even when
   scores exist.
4. A stochastic visual judge may yield a runtime-successful but incomplete
   official record. Parseability alone does not license imputation.
5. A future Python implementation could alter high-level random sampling or
   percentile interpolation. The local uint32 generator and nearest-rank rule
   therefore need known-answer and end-to-end checks.
6. Data-dependent strongest-comparator selection can inflate inference if only
   its contrast is required. Requiring positive lower bounds against both OS
   and NR is the frozen multiplicity guard.
7. Cost or interval equality at a threshold can be mishandled by rounded display
   values or a finite ambient decimal context. Unbounded input decimals must be
   parsed as integer coefficients over powers of ten; totals and the `3/2`
   comparison must remain exact Fractions before 12-place display serialization.
8. A complete but wrong task-to-discipline map could make stratification
   reproducible yet scientifically invalid. The exact map and upstream
   mask-manifest digest are bound in the contract.

## Frozen implementation hypothesis

> If the analyzer requires exactly 102 task receipts and exactly 918 nested
> arm-attempt receipts; validates every frozen identity, task, discipline and
> type before computing any metric; collapses success within task-arm; uses one
> paired task draw across all arms within each fixed discipline; fixes a local
> MT19937 implementation, seed `20260824`, 100,000 replicates, and nearest-rank
> 2.5/97.5 percentiles; and compares exact point, discipline and prospectively
> identity-bound cost quantities to the frozen thresholds, then the known
> missingness, pseudoreplication,
> comparator-selection, RNG-drift and best-attempt-cost failures become
> structurally inadmissible.

This is an engineering hypothesis. A synthetic pass does not predict an
official result or create scientific authority.

## Frozen hostile validation cases

- the committed contract hash, canonical `1..102` set, exact discipline map,
  102 task count and 918 nested attempt count are checked;
- reference MT19937 seed `5489` reproduces the first five published uint32
  known-answer values;
- one complete synthetic ledger executes all 100,000 paired stratified
  replicates with seed `20260824` and exact nearest-rank indices 2499/97499;
- OS and NR strongest-comparator paths plus the exact OS tie break are checked;
- primary generation cost sums all 306 attempts per arm under the same frozen
  identity/allocation rule; billed USD and evaluator billed USD are separately
  availability-reported, missing values are not zero, and neither silently
  substitutes for the primary metric;
- both an authoritative billed-USD fixture and an allocated-accelerator-seconds
  fixture are checked; metric-binding drift and missing billed USD under a
  billed-USD primary become `CANNOT_CHECK`;
- point gain below `0.08`, a discipline contrast below `-0.05`, and cost ratio
  above `1.5` each fail the gate;
- the adversarial ratio `1.500000000000000000000000000001` fails under exact
  coefficient/scale and Fraction arithmetic even though its labeled 12-place
  display rounds to `1.500000000000`; the exact reduced ratio is also reported;
- a zero strongest-comparator cost denominator becomes `CANNOT_CHECK` before
  bootstrap;
- missing/duplicate tasks or attempts, wrong split, wrong discipline, extra
  fields, bad hashes, numeric coercions, exponent costs, and Boolean outcomes
  become `CANNOT_CHECK` before metrics;
- duplicate JSON member names at any nesting depth are rejected; specifically,
  a ledger containing `split=validation` followed by `split=verified` becomes
  `CANNOT_CHECK` rather than accepting the last member;
- hostile `CANNOT_CHECK` result bytes are identical across distinct
  `PYTHONHASHSEED` processes, and artifact-hash reasons follow one frozen tuple;
- a typed evaluator/runtime failure retains null outcomes and produces
  `CANNOT_CHECK`, never solved zero;
- unreadable and malformed JSON paths emit typed `CANNOT_CHECK` results; and
- static inspection confirms no network, subprocess, high-level random,
  NumPy/SciPy, provider, Docker, or official-evaluator import and no CLI option
  to override seed or replicate count.

## Reopen triggers

Reopen the design rather than editing outcomes around it if the official
evaluator cannot be losslessly adapted to the frozen task/attempt record shape;
the verified population, source commit, task-to-discipline mapping or official
success definition changes; an owner cannot obtain all-attempt generation cost;
the official evaluator exposes only selected-attempt results; a failure class
cannot be represented without imputation; independent review rejects the
percentile interval or strongest-comparator rule; a reference MT19937
known-answer test fails; or any official outcome is opened before the final
contract/analyzer bytes are externally frozen.
