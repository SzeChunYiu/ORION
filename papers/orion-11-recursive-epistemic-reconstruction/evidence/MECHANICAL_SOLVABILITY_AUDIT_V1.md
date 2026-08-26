# Mechanical Solvability Audit V1 — ORION-P1 hidden-shift suite

Machine-readable companion: `mechanical_solvability_audit_v1.json`.

**Suite audited.** `suite_fingerprint` at audit start — PILOT `dea059632c7489db…`, TEST `fa1378c3d5502…`.
At completion — PILOT `dea059632c7489db…` (unchanged), TEST `988ef483518c6da2…`. A concurrent agent reworded
`public_prompt` strings repeatedly during this audit, so `suite_fingerprint` (which covers the prompt) moved
twice and is a **moving target here**.

This audit depends only on `observable_resources` and the gold family/coordinates, and a line-by-line diff of
every resource entry across every observed revision shows **zero** changes — every number and token quoted below
is verbatim throughout. The stable binding value to re-check when replaying this audit is therefore a hash over
exactly those fields:

```
binding_hash_resources_and_gold = 29244cc674c8049e1c876161e419a52f41c2b536f0197870f218142dccd880ee
```

Both blind-responder probes were re-run against the final post-edit revision and hold at full strength
(probe 1: 66/66 for the phrase and 66/66 for the bare word `framing`; probe 2: 10/11 DECOMPOSITION with 0/55
false positives).

**Method.** Read the 66 `PublicView`s only (`case_id`, `public_prompt`, `observable_resources`, `budget_class`).
Per-case family hypotheses were written down **before** any `protected_gold` was opened; gold was then consulted
only to check (a) whether the found signal points at the right family and (b) whether the answer
`root_success_rubric` demands is derivable from quoted figures.

**One structural constraint governs everything below.** `observable_resources` are one-line English *descriptions
of files*, not the files. A non-LLM procedure can therefore only compute on numbers and tokens quoted verbatim in
those descriptions. Every computation in this audit respects that; where a rubric demands a quantity that requires
the underlying data (c016, c017, c123), the case is marked down for it.

---

## Headline

| | count |
|---|---|
| SOLVABLE | **55 / 66** |
| PARTIAL | **9 / 66** |
| UNSOLVABLE | **2 / 66** |
| Cases with a blind-responder shortcut | **32 / 66** |
| Pre-gold family prediction accuracy | **61 / 66** |
| Case-content arithmetic defects found | **5** |

**Verdict criterion.** SOLVABLE requires all three of: (a) a computation over quoted numbers/tokens fires as
anomalous against the stated framing, (b) it yields the corrected quantity or procedure `root_success_rubric`
demands, **and (c) its relation kind selects the responsible family.** All three are required because the
question is whether a procedure can infer the *responsible coordinate*, not whether it can satisfy the rubric —
and the two come apart on the five cases where the public signal mis-points the family (c016, c017, c105, c110,
c118). Those five are graded on conjunct (c): two UNSOLVABLE, three PARTIAL. `verdict: SOLVABLE` and
`gold_family_matches: false` never co-occur, and the generator asserts it.

The prior conclusion — *"any channel rich enough for a mechanical detector is rich enough for a blind
responder"* — is **false as a general claim about this suite, and true of exactly half of it.** Those are two
separate findings and both matter:

1. On the 33 hidden-shift cases in PARENT / REPRESENTATION / MEASUREMENT, there is a real arithmetic channel that
   a blind responder cannot touch. `p1-c109` is not a lucky case; it is a representative of a family of them.
2. On the other 33 — the 11 EVIDENCE controls, 11 EXECUTION controls and 11 DECOMPOSITION cases — the
   discriminating signal is **template, not epistemics**, and a responder reading no content at all recovers it.

---

## THE LEAK — read this first

A classifier that reads **only resource path stems and two fixed template phrases**, never a single number and
never a word of descriptive resource text, scores **31/66 exact family** against a chance baseline of 11/66. It
abstains on 33 cases and is right on 31 of the 33 it commits to (94% precision).

### Probe 1 — CRITICAL. `reframe_required` is 66/66 predictable from one phrase.

```
rule:   reframe_required == ("The team's framing is" appears in public_prompt)
result: TP=44  FP=0  TN=22  FN=0   →  66/66 exact
reads:  a fixed 21-character string. No numbers. No resources. No case-specific content.
```

Every one of the 44 hidden-shift cases contains that phrase; not one of the 22 negative controls does. Per the
`PublicView` docstring in `src/orion/study/p1/cases.py`, the family is withheld precisely because *"knowing which
is which is the answer to H2."* **H2 is currently answerable with zero comprehension.** This survived the
concurrent prompt rewording untouched — 28 prompts were rewritten and the phrase was preserved verbatim in all
44 hidden-shift cases.

**It is worse than a sentence template — it is lexical at the single-word level.** A greedy scan over every word
appearing in ≥5 prompts finds **two individual words that each separate the suite perfectly on their own**:
`framing` (66/66) and `team's` (66/66). No other word reaches 58/66. And separators exist in the *control*
direction too, both at perfect precision: `"The plan is"` appears in 17 controls and 0 hidden-shift cases;
`"Carry out the plan"` appears in 12 controls and 0 hidden-shift cases — presence of either certifies a negative
control. Consequently **"rewrite the framing sentence" is not a sufficient repair**; the repair must stop those
tokens co-varying with `reframe_required` in both directions.

### Probe 2 — CRITICAL. A filename glob recovers a whole hidden-shift family.

```
rule:   hidden_decomposition_or_interface == any resource path stem matches /(proposal|trial)/
result: 10/11 DECOMPOSITION,  0/55 on every other family   (precision 1.00, recall 0.91)
reads:  resource path stems only — everything after the em dash discarded.
```

`payments/timeout-trial.md`, `billing/skip-proposal.diff`, `store/replica-trial.md`, `app/global-cap-trial.md`,
`pricing/doubles-proposal.md`, `stream/memory-trial.md`, `cluster/worker-trial.md`, `orders/sweeper-proposal.md`,
`batch/rotation-proposal.md`, `limiter/table-proposal.diff`. The one DECOMPOSITION case without such a stem
(`p1-c138`) is the one the probe misses — and is also the only DECOMPOSITION case this audit marks PARTIAL.

To be precise about the severity: a case *about a remedy that failed* will naturally tend to name a remedy
artefact, so naming one is not itself illegitimate. The defect is that the correlation is **perfect** — no
non-DECOMPOSITION case anywhere in the suite carries a `proposal` or `trial` stem, so the convention functions
as a label. The repair is decoys, not renaming alone.

### Probe 3 — HIGH. The two control families split on prompt phrasing.

```
rule:   within controls, EVIDENCE if the prompt endorses the instrument
        ("the right instrument" / "the agreed route" / "the agreed arbiter" / "genuinely the ones worth measuring"),
        else EXECUTION
result: 21/22 correct
```

### Probe 4 — HIGH. `derived from closure:` never appears in a negative control.

```
rule:   reframe_required == any resource contains "derived from closure:"
result: TP=30  FP=0  TN=22  FN=14   →  52/66, zero false positives on controls
```

Its *presence* alone certifies a hidden shift. Gold `dependency_depth` is 0 for all 22 controls and ≥1 for all
44 hidden-shift cases, and the closure chain is the public shadow of that field.

### What the leak does not reach

The combined blind classifier **abstains on all 33 PARENT / REPRESENTATION / MEASUREMENT cases.** Nothing in
path stems, resource counts, prompt lengths or template phrasing separates those three families. There the
arithmetic is doing genuine work, and that is where the LLM-free arm has a defensible claim.

### Recommended repairs

- Rewrite the framing sentence per case so no fixed phrase co-varies with `reframe_required`. Give some controls
  a stated framing that happens to be correct; give some hidden-shift cases a plan-style prompt.
- Rename remedy artefacts to neutral, per-domain names (`payments/latency-change-2026-01.md`, not
  `payments/timeout-trial.md`), and plant decoy `*-proposal` / `*-trial` resources in non-DECOMPOSITION cases.
- Add `derived from closure:` chains to some negative controls, or drop the phrase in favour of neutral wording.
- Add the three probes above to the degeneracy suite as **regression tests that must fail**, so the leak cannot
  silently return.

---

## Per-family narrative

### EVIDENCE-only controls — 11/11 SOLVABLE (`absent_input_obtainable_by_capability`)

Uniform two-legged signature, arithmetic on one leg and lexical on the other: **one resource states a required
input is absent or covers only a fraction of the needed window; a second names a costed, already-authorised route
that reconstitutes it.** The fractions are quoted and always damning — 5 of 14 benchmark artefacts (c009),
22,400 of 210,000 enrolments = 10.7% (c015), 0.4% of production rows (c102), 7 days of retention against a 42-day
window = 17% (c112), lot codes on 41% of units (c125), one cost row per service per day for three same-day changes
(c130), 900 runs with 0 usable order records (c117), 0 of 118 corrupt rows attributable (c003). The obtainability
leg is a named capability with a stated cost: *"can be provisioned in two days"*, *"a documented 3-hour job"*,
*"a documented 6-hour restore"*, *"the runner supports enabling it"*, *"can be digitised in a week"*,
*"a deterministic hash of the person's id and the recorded salt"*.

Three carry an extra arithmetic kicker worth reusing: c102's staging plans are *identical* across all three
candidates at 40 ms (3 candidates, 1 outcome — zero discriminating power); c125's missingness is deterministic in
line, not random (the 59% gap coincides exactly with lines 2, 4 and 5, whose scanners were out); c130's daily
granularity admits 1 observation for 3 candidates.

### EXECUTION-only controls — 11/11 SOLVABLE (`single_change_localised_by_coincidence_and_counterfactual`)

Also uniform: **one resource names a single mechanism whose scope coincides exactly with the symptom, and a
second supplies the counterfactual.** The coincidences are exact and checkable — env-var flip on 2026-02-19 ==
first zero-row night (c006); 9 failing modules == 9 case-mismatched names, with 140 matching ones passing (c101);
pages in groups of 5 == 5 regions (c107); 3h55m of lock wait == the "four hours late" symptom (c132); a 3.1%
currency move over 14 months == a 3% shortfall over 14 months, against <0.2% for every other currency (c141).
The counterfactuals are equally mechanical: revert restores 0.91 (c011); one worker reproduces bit-for-bit
(c012); ablating one line takes 40 h to 38 min (c116); a frozen directory gives 2.8% on 5/5 repeats (c129);
30 of 30 clean nights (c132); `SELECT count(*) … IS NULL` returns 4,102 against a "100% pass" (c135).

Two are pure token-level and need no domain knowledge at all: `WHERE col != NULL` is vacuous in three-valued
logic (c135), and `deploy_cmd | tee deploy.log` without `pipefail` returns tee's status (c136).

### DECOMPOSITION / INTERFACE — 10 SOLVABLE, 1 PARTIAL (`named_remedy_shown_insufficient`)

**The framing's own remedy is present as a named resource and a second resource shows it does not remove the
failure mode.** Three sub-shapes, all arithmetic:

- *Worsens it.* 41 duplicates / 90 days = 0.456/day at a 30 s timeout; the 10 s trial gave 63 / 14 days =
  4.5/day, a 9.9× increase (c004). Doubling workers moved abandoned share 38% → 41% (c113).
- *Only delays it.* 4 GiB → 16 GiB is 4.0× capacity and moved first crash 3.5 h → 13 h, a 3.71× increase —
  time-to-failure proportional to capacity is the signature of unbounded accumulation, and the producer-consumer
  shortfall is a sustained 2,800 items/s (c111). Two extra replicas moved p99 34 s → 33 s, a 3% move against a
  91% pool-wait share (c018).
- *Cannot change the measured property.* The table refactor still requires a redeploy, so 34/34 numeric changes
  need a release before and after (c147). The sweeper cannot tell "not yet published" from "published but not
  yet visible" (c114). Adding 14 stand-ins to the 48 already built cannot remove a draw that happens inside the
  arithmetic (c104). Rotation every 24 h cannot bind a 90-minute leak-to-misuse interval, 16× too slow, while the
  credential holds wildcard authority against 4 resources actually used and 41 touched (c133).

Several also carry `capability_present_but_unused_at_interface`: the gateway already accepts a caller-supplied
reference (c004); the client library already takes an abortable per-call handle that the code passes and never
closes (c113); the provider already issues scoped credentials (c133); reporting already tolerates 15-minute-old
figures (c018).

**`p1-c138` is PARTIAL** — the only case in the family with no remedy artefact. Its mechanical signal
(producer CI verifies shape while name, type and shape were untouched, so validation's domain is disjoint from
what changed; 4 consumers wrong for 6 days with 0 errors; the social control already failed with 2 of 4 teams
off the list) localises correctly, but the step to "each message carries a compatibility marker gated in producer
CI" is a design act, not a computation.

### MEASUREMENT — 11/11 SOLVABLE

The strongest family for a mechanical arm. Five reusable kinds, every demanded answer derivable from quoted
figures:

- **`aggregate_ignores_stated_exposure_weights` (4).** The report's weights are stated and the true exposure
  weights are stated separately; re-weighting flips the verdict. c139: equal-weight 99.95% versus
  0.71 × 99.20% + 0.29 × 100% = **99.43%**. c140: bench mix reproduces the headline
  (0.78 × 0.86 + 0.14 × 0.31 + 0.08 × 0.22 = **0.7318** ≈ 0.71) and the production mix sinks it
  (0.41 × 0.86 + 0.33 × 0.31 + 0.26 × 0.22 = **0.5121**, 0.14 below the 0.65 bar; 0.270 on the 59% that is
  multi-hop or negation). c115: 180 ms panel versus 2,310 ms pooled p99, 12.8×, with 3 of 60 hosts carrying 82%
  of slow requests. c001: 41,000/13.6M = 0.3015% per session versus 9.1% per person, a factor of 30, with the
  denominator chosen arithmetically by the quoted 0.81-versus-0.06 complaint correlation.
- **`reported_score_lacks_its_computable_baseline` (2).** c121: base rate 1.9% ⇒ a constant "not fraud" rule
  scores 98.1%, so the reported 94% is **4.1 points below** the trivial baseline; the bucket table gives the
  calibration map directly (0.325 → 7.8%, 0.625 → 11.2%, 0.925 → 19.4%, overstatements of 4.2×, 5.6×, 4.8×).
  c148: chance agreement from the 91% majority marginal is 0.91² + 0.09² = 0.8362, so
  **κ = (0.880 − 0.8362)/(1 − 0.8362) = 0.267** — the 88% headline sits 4.4 points above chance.
- **`metric_terminates_before_the_outcome_it_names` (2).** c131: 42 minutes to first status change versus
  19.4 h = 1,164 minutes to final close, 27.7×, with agents *instructed* to acknowledge within the hour and an
  acknowledgement being a status change. c007: the counter admits all statuses and each of up to 4 re-sends, so
  a 0.4% → 6.1% 5xx move can account for the whole 22% rise while completed journeys fell 11%.
- **`evaluation_shares_units_or_information_with_the_evaluated` (2).** c002: 8.4 − 6.9 = 1.5 unblinded versus
  7.1 − 7.0 = 0.1 blinded, a 15× collapse under a correction touching only the procedure. c126: corrected refit
  0.63 versus live 0.61 (|Δ| = 0.02) against an offline-live gap of 0.32, with drift independently excluded at 3%.
- **`non_additive_quantity_summed` (1).** c118: 41.2M summed versus 6.9M month-distinct = 5.97× overstatement;
  6.9M / 1.9 devices per person = **3.63M** people, exactly the rubric's figures.

### REPRESENTATION — 9 SOLVABLE, 2 PARTIAL

- **`summary_outside_the_support_of_its_own_data` (3).** The cleanest mechanical trigger in the suite. c109:
  every reading lies in [352,359] ∪ [1,9], i.e. within 17° of north, yet the reported mean is 181.4° — outside the
  circular convex hull, where no mean of a set can lie; `atan2(−0.4, 7.9) = −2.90° = 357.10°` recovers it, and the
  reported sd of 176 is 0.978 of the 180° half-range. c122: the series is a running total, so volume =
  (4,090,930,004 − 4,090,112,331) + 812 = **818,485**, a factor of 5,000 below the reported 4.1 billion, and the
  reset is placed exactly — at 240 samples/hour the interval is 15 s, so sample 96 falls at 96 × 15 s = 24 minutes
  past the hour, matching the logged 14:24 restart. c013: 71 rows report gaps of −1430 to −1400 minutes, and a
  duration cannot be negative.
- **`error_vanishes_where_the_missing_transform_is_the_identity` (2).** c119: 94% of misassignments sit north of
  55° where the longitude scale factor is ~0.5, against ~0.9 at 25° — a 5× larger distortion exactly where the
  errors are. c124: the path agrees on straight runs (constant heading ⇒ constant body-to-floor rotation) and
  diverges up to 6 m immediately after every turn (heading swinging 90°/s ⇒ time-varying rotation). Error present
  **iff** the transform is non-trivial: the transform is at fault, not the data.
- **`estimate_changes_under_an_operation_that_must_not_change_it` (2).** c137: reordering the same 4.2M rows
  changes the total by up to 2,300 units while the gap being explained is 1,842 — the discrepancy lies *inside*
  the method's own noise and carries no information. c146: the suite supplies its own permutation null and it
  **reproduces the finding** — independently shuffling each share column still yields negative correlations of
  similar size to the reported −0.41/−0.58/−0.33, while the unconstrained byte counts correlate positively.
- **Singletons (4).** c110 (`rank_and_moment_statistics_disagree`: r = 0.61 collapses to 0.04 on deleting 2 of 60
  points — 3.3% of the sample, a 93% collapse — while 51% of 1,770 pairs concordant gives τ = 0.02).
  c010 (`summary_collapses_distinguishable_distributions`: teams A and B share average 3.1 while A is bimodal at
  both ends and B is 78% massed at the midpoint). c120 (`one_value_carried_by_distinct_encodings`: `43 61 66 c3 a9`
  in 220 rows versus `43 61 66 65 cc 81` in 190 rows, never merging under lowercase-and-trim). c014 (below).

### PARENT DOMAIN — 6 SOLVABLE, 3 PARTIAL, 2 UNSOLVABLE

The weakest family, and the interesting one. Two kinds are genuinely mechanical:

- **`response_nonlinear_where_the_framing_assumes_proportionality` (2).** c008: arrival steps of 1.25× and 1.20×
  give wait steps of 2.34× and 5.00× while CPU steps exactly track arrivals at 1.25× and 1.20× — waiting grows an
  order of magnitude faster than usage, and bracketing 250 ms between the 150/s (96 ms) and 180/s (480 ms) points
  puts the limit strictly below 180/s. c142: successive slopes of the sweep are 0.4, 0.7, 1.5, 3.3, 5.2, 1.8 per
  unit — a 13× ratio identifying a transition band between 0.40 and 0.55; the 0.90 requirement holds only below
  ≈0.243, not the 0.45 the budget buys.
- **`constraints_fully_enumerated_matching_a_closed_form` (3).** The resources *close* the constraint set, which
  is the mechanical mark. c106: two independent lists with measured overlap ⇒
  74 × 61 / 29 = **155.66**, union 74 + 61 − 29 = 106, unlogged ≈ **50** — three arithmetic operations on three
  quoted integers. c134: n = 40, fixed random order, irrevocable, and *absolute figures not comparable across
  days* ⇒ k = round(40/e) = **15**, success ≈ 1/e = **0.368**, both from n alone. c123 is the exception (below).

The remaining five are where the mechanical arm genuinely runs out:

- **`p1-c123` PARTIAL** — the constraint closure is mechanical and greedy is provably non-optimal (past hand
  repairs of 6, 9 and 4 bound the published 214 at ≥4 above optimum), but the 60×60 matrix is described and not
  quoted, so neither the optimal assignment nor the dual-potential certificate the rubric demands can be produced.
- **`p1-c127` PARTIAL** — the trigger is crisp (stated need 1.4× → 3.8× while measured use stayed flat; median
  team uses 31% ⇒ 3.2× overstatement; grants free and never reclaimed), but the rubric demands a *new rule* under
  which honesty is dominant. Designing a mechanism is generative, not computational, and every named alternative
  is an explicit FAIL.
- **`p1-c143` PARTIAL** — see defects below.
- **`p1-c016` and `p1-c017` UNSOLVABLE** — see below.

---

## UNSOLVABLE cases

### `p1-c016` — rater effects read as MEASUREMENT, and the model cannot be fitted

A trigger fires: reviewer means span 2.4–4.6, a spread of 2.2 points on a 4-point scale (55% of range);
assignment is by component ownership, never at random; 7 authors got >70% of their reviews from one reviewer;
overlap ratings differ by 1.3 with consistent sign per pair. Two independent failures follow.
(1) The rubric requires a rater-facet model **fitted on the overlap**, but the overlap is summarised (11%,
mean 1.3, consistent sign) with no per-reviewer offsets or per-PR pairs quoted — and the rubric explicitly FAILS
*"means rescaled with any fixed weights"*, which is the only correction the quoted summaries permit.
(2) Reading every word before any gold check, I placed this in **MEASUREMENT**. The step to psychometrics is a
domain-term step, not a computation.

### `p1-c017` — censoring reads as MEASUREMENT, and the estimator cannot be evaluated

The trigger is arithmetic: the aggregate keeps 82 of 120 units and discards 38 (31.7%) that are stated to be
9 months younger on average, so the exclusion is systematic in the variable being estimated and 14 months is a
lower bound. But the rubric requires the 38 retained as partially observed lifetimes under a product-limit
estimator, and no per-unit lifetimes, install dates or risk sets are quoted — while dropping or imputing them is
an explicit FAIL. As with c016, my own pre-gold reading landed on **MEASUREMENT**, not PARENT_DOMAIN.

**The shared lesson:** both cases are PARENT_DOMAIN cases whose public evidence is indistinguishable from a
MEASUREMENT defect. If an LLM that read every word landed in the wrong family, a deterministic rule will not do
better. These two are the honest ceiling on the LLM-free arm.

---

## Case-content defects found

Five inconsistencies between quoted figures and what the case or its rubric asserts. These were found *from the
numbers*, and they are actionable regardless of the solvability question.

1. **`p1-c014` — the stated discriminator is arithmetically false.** `ensemble/symmetry-check.md` claims that
   averaging the complements and subtracting from 1 "gives a different pooled number than averaging the
   originals". The arithmetic mean is exactly complement-symmetric by linearity: mean(1 − pᵢ) = 1 − mean(pᵢ).
   Numerically, (0.9996 + 0.9991 + 0.9989 + 0.9993 + 0.38)/5 = 0.87538 and 1 − 0.87538 = **0.12462**, identical
   to the direct mean 0.6231/5 = **0.12462**. `root_success_rubric` requires the answer to *"cite the symmetry
   check to show that plain averaging is not invariant under swapping the event for its complement"* — i.e. it
   requires asserting a false claim, and any solver that verifies it finds it does not hold.

2. **`p1-c013` — the reported mean is incompatible with the reported rows.** With 71 of 900 rows near −1415, a
   raw mean of +121.4 forces the other 829 rows to average (121.4 × 900 + 71 × 1415)/829 = **253.0** minutes, so
   the wraparound-corrected mean is (829 × 253.0 + 71 × 25)/900 = **235.0** minutes — not the 8–12 the rubric
   demands. For the corrected mean to be ≈10, the raw mean would have to be about 10 − 71 × 1440/900 = **−103.6**,
   not +121.4. A mechanically correct solver reaches 235.0 and is graded FAIL. *(The representation diagnosis is
   unaffected and remains the cleanest trigger in the suite — negative durations are flatly out of support.)*

3. **`p1-c143` — the inspection-paradox reconciliation does not close.** The rubric demands the relation
   E[probed] = E[L²]/E[L] stated as *"consistent with mean 18.6 and standard deviation 44.1"*. It is not:
   E[L²] = 44.1² + 18.6² = 1,944.81 + 345.96 = 2,290.77, so E[L²]/E[L] = 2,290.77/18.6 = **123.2** minutes, not
   the 47.0 the probes report — off by 2.6×. The direction (probe mean > table mean) is right and the corrected
   answer 18.6 is quoted, so the case survives as PARTIAL, but a procedure that *computes* the check finds it fails.

4. **`p1-c139` — soft.** `sre/customer-claim.md` says 3.9 hours of failed calls "matches 99.2%". Over a ~2,184-hour
   quarter, 3.9 h is 0.18%, i.e. 99.82%; 0.8% of a quarter would be ~17.5 h. Not reconcilable from quoted numbers.
   The exposure-weighting computation does not depend on it, so the verdict stands.

5. **`p1-c142` — minor.** The rubric endorses holding failure probability "at or below 0.30", but the sweep gives
   0.86 reachability at p = 0.30, which does not meet the prompt's own "above 0.90" requirement. The interpolated
   bound is ≈0.243.

---

## Relation-kind taxonomy

21 kinds.

> **Read the purity claim carefully — it is weaker than it looks.** Kinds were assigned *after* gold was checked,
> so "every kind maps to exactly one family" is a post-hoc construction, not a result. Three qualifications:
> (i) 8 of the 21 kinds are singletons and **cannot** span a boundary by construction; (ii) the three largest
> kinds — `absent_input_obtainable_by_capability`, `single_change_localised_by_coincidence_and_counterfactual`,
> `named_remedy_shown_insufficient` — are exactly the leaky template families, where the purity *is* the template
> rather than the epistemics; (iii) that leaves **10 multi-case kinds covering 25 cases** where purity is a
> non-trivial claim, and even there it was fitted, not predicted. The only out-of-sample number in this audit is
> the pre-gold family prediction of **61/66**, with misses on c016, c017, c105, c110, c118. Build on the table
> below, but treat purity as a hypothesis to be tested on new cases, not as an established property.

| # cases | relation kind | family | reusable? |
|---|---|---|---|
| 11 | `absent_input_obtainable_by_capability` | EVIDENCE | yes — strongest general rule in the suite |
| 11 | `single_change_localised_by_coincidence_and_counterfactual` | EXECUTION | yes |
| 10 | `named_remedy_shown_insufficient` | DECOMPOSITION | yes, **but leaks via filename** |
| 4 | `aggregate_ignores_stated_exposure_weights` | MEASUREMENT | yes — highest-value kind for the arm |
| 4 | `sampling_frame_correlated_with_the_quantity_estimated` | PARENT | partly — 2 of its 4 are UNSOLVABLE |
| 3 | `summary_outside_the_support_of_its_own_data` | REPRESENTATION | yes — cleanest arithmetic trigger |
| 3 | `constraints_fully_enumerated_matching_a_closed_form` | PARENT | yes |
| 2 | `evaluation_shares_units_or_information_with_the_evaluated` | MEASUREMENT | yes |
| 2 | `metric_terminates_before_the_outcome_it_names` | MEASUREMENT | yes |
| 2 | `reported_score_lacks_its_computable_baseline` | MEASUREMENT | yes |
| 2 | `response_nonlinear_where_the_framing_assumes_proportionality` | PARENT | yes |
| 2 | `error_vanishes_where_the_missing_transform_is_the_identity` | REPRESENTATION | yes |
| 2 | `estimate_changes_under_an_operation_that_must_not_change_it` | REPRESENTATION | yes |
| 1 | `summary_collapses_distinguishable_distributions` | REPRESENTATION | thin |
| 1 | `rank_and_moment_statistics_disagree` | REPRESENTATION | thin |
| 1 | `one_value_carried_by_distinct_encodings` | REPRESENTATION | thin |
| 1 | `pooling_operator_lacks_a_required_invariance` | REPRESENTATION | thin — and its evidence is false (c014) |
| 1 | `non_additive_quantity_summed` | MEASUREMENT | thin |
| 1 | `reported_input_is_strategic_not_measured` | PARENT | thin |
| 1 | `structure_finer_than_the_reporting_granularity` | PARENT | thin |
| 1 | `validation_checks_a_property_other_than_the_one_that_changed` | DECOMPOSITION | thin |

**8 of 21 kinds cover exactly one case.** All eight sit in the three families the blind classifier cannot reach —
which is consistent both with those families carrying the real signal and with the taxonomy being under-determined
there. The implementation lane should treat the 13 multi-case kinds as the buildable set (58 cases) and the eight
singletons as hypotheses awaiting more cases.

### Cross-family near-collisions the lane must guard against

These did not break purity but came close, and a naive rule will trip on them:

- `summary_outside_the_support_of_its_own_data` nearly fires on **c118** (41.2M summed exceeds the 6.9M month
  total, so it is out of support too) — which is MEASUREMENT, not REPRESENTATION. c118 is the case my own
  pre-gold reading mis-filed for exactly this reason.
- "a corrected re-run is reported and the effect collapses" spans **c002/c126** (MEASUREMENT) and
  **c110/c137/c146** (REPRESENTATION). The separating feature is whether the correction changes *which units are
  in the set* (MEASUREMENT) or changes *nothing about the data, only order/subset/permutation* (REPRESENTATION) —
  and c110 sits awkwardly on that line, since it deletes two rows.
- `sampling_frame_correlated_with_the_quantity_estimated` (PARENT: c016, c017, c105, c143) is semantically
  adjacent to `evaluation_shares_units_or_information_with_the_evaluated` (MEASUREMENT: c002, c126). The
  mechanical distinction is that the MEASUREMENT pair contaminates the *evaluator*, the PARENT set contaminates
  the *population frame* — a distinction two of the four PARENT cases (c016, c017) do not survive.

---

## Verdicts by family

| family | SOLVABLE | PARTIAL | UNSOLVABLE | blind shortcut |
|---|---|---|---|---|
| EVIDENCE (control) | 11 | 0 | 0 | 11 |
| EXECUTION (control) | 11 | 0 | 0 | 11 |
| DECOMPOSITION | 10 | 1 (c138) | 0 | 10 |
| MEASUREMENT | 10 | 1 (c118) | 0 | 0 |
| REPRESENTATION | 8 | 3 (c013, c014, c110) | 0 | 0 |
| PARENT DOMAIN | 5 | 4 (c105, c123, c127, c143) | 2 (c016, c017) | 0 |
| **total** | **55** | **9** | **2** | **32** |

The five cases where the public signal **mis-points the family** (`gold_family_matches: false`) are c016 and
c017 (UNSOLVABLE) and c105, c110, c118 (PARTIAL). In every one, reading the full public content with complete
comprehension and before any gold check, I landed in the wrong family: c016 and c017 read as MEASUREMENT rather
than PARENT_DOMAIN, c105 as MEASUREMENT rather than PARENT_DOMAIN, c110 as MEASUREMENT rather than
REPRESENTATION, and c118 as REPRESENTATION rather than MEASUREMENT. For c105, c110 and c118 the rubric-demanded
*answer* is fully derivable from quoted figures — which is why they are PARTIAL and not UNSOLVABLE — but a
deterministic rule keyed on the relation kind would file all three under the wrong coordinate.

---

## Bottom line for the parallel implementation lane

- **Build against the 13 multi-case kinds**, not the 21. They cover 58 cases and every one is expressible as
  arithmetic over quoted figures.
- **The three highest-yield general rules**, in order: `absent_input_obtainable_by_capability` (absence fraction
  ∩ named costed capability), `named_remedy_shown_insufficient` (remedy artefact ∩ evidence it fails), and
  `aggregate_ignores_stated_exposure_weights` (report weights ∩ stated exposure weights ⇒ re-weight and compare
  to the threshold). Together these are 25 cases.
- **Do not report a score on the 33 leaky cases as evidence for the LLM-free arm** until probes 1–3 are closed.
  Any detector's performance there is confounded with template recognition, and a blind baseline will match it.
  The 33 PARENT / REPRESENTATION / MEASUREMENT cases are the only clean measurement surface the suite currently has.
- **Fix c013, c014 and c143 before scoring anything.** Two of the three require a solver to assert something the
  arithmetic contradicts, so a *correct* mechanical answer is graded FAIL — which will read as a detector failure
  and send the lane chasing a defect that is in the case, not the code.
