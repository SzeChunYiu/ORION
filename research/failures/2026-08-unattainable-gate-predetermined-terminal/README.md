# A preregistered negative whose two failing gates were above the protocol's own ceiling

**Observed:** 2026-08-21, auditing P14A — the one paper in the batch that ships a
real negative — for whether its instrument could have produced a positive.

## Failure

P14A is the honest case on every property the other eight records deny. Its
terminal is derived, not a literal:

```python
terminal = "P14A_CONTROLLED_GOVERNANCE_SUPERIORITY_SUPPORTED" if all(gates.values()) \
           else "P14A_CONTROLLED_GOVERNANCE_SUPERIORITY_GATE_NOT_MET"
```

Its thresholds were frozen before execution, its seed is published, its result
reproduces to the digest, it selects its comparator prospectively, and it lands
on the negative side and says so: `P14A_CONTROLLED_GOVERNANCE_RESULT_RECEIPT_V1.json`
records `..._GATE_NOT_MET` with `strongest_non_orion_baseline: MULTI_REVIEW` and
two of seven gates `false`. The paper then writes its own root-cause audit and
declines to edit the result.

The question none of that answers is whether either failing gate had a value the
protocol was able to reach.

`orion.study.p14.governance_gates` loads the shipped generator and drives its own
`gold`, `policy` and `make_case`, replaying `main()`'s aggregation with only the
eight sampling ranges lifted out as a parameter. At the shipped ranges it emits
the committed payload byte for byte —
`3ac625b799eeb00acee68deecb45ab9ae771b977dbf6303a0795cb80057a28fe` — and matches
every number the receipt publishes.

### The two failing gates are one number

`MULTI_REVIEW` reproduces the gold adjudication except on cases where a positive
is a same-evidence rereading of a live negative history. Enumerated over the 144
fact states `make_case` can emit — 112 of the 256 assignments never occur,
because `donor_owned`, `interaction_only` and `live_negative_history` are drawn
as `positive and rng.random() < rate` — that exception is **one state**:

| arm | states of 144 where it disagrees with gold |
| --- | --- |
| `RAW_POSITIVE` | 139 |
| `REFLECTION_CHECKLIST` | 13 |
| `DONOR_AWARE_REVIEW` | 5 |
| `MULTI_REVIEW` | **1** |
| `ORION_RSE_FULL` | **0** |

The four baselines are nested refinements — `MULTI_REVIEW`'s error set is a
subset of all three others — so `max(baselines, key=disposition_accuracy)` has
nowhere else to land, and the "prospectively selected strongest baseline" is a
fixed choice for every family mixture with positive support.

That one state is also `MULTI_REVIEW`'s only false promotion. So the two gates
that failed are the *same* statistic under two thresholds:

- `strongest_baseline_false_promotion_ge_0_05` reads its frequency;
- `accuracy_gain_ge_0_08` reads `1.0 − (1 − its frequency)`, the same number.

The receipt prints both as `0.018375`, and they are equal because they are one
quantity.

### The protocol's own support cannot put that number above either threshold

The eight facts are independent Bernoulli draws, so the state's prevalence is a
product of eight family rates, each monotone in a different declared parameter.
`main()` mixes every family's draw half-and-half with a fixed base, so the
reachable rates are a band around the base rather than the declared range:

| declared `sampled` range | realized `rates` range | at the corner |
| --- | --- | --- |
| `positive` 0.35–0.65 | 0.425–0.575 | 0.575 |
| `bad_evidence` 0.05–0.18 | 0.075–0.140 | 0.075 |
| `unfrozen` 0.05–0.18 | 0.075–0.140 | 0.075 |
| `nonidentifiable` 0.04–0.14 | 0.060–0.110 | 0.060 |
| `donor` 0.10–0.28 | 0.140–0.230 | 0.140 |
| `interaction` 0.08–0.22 | 0.115–0.185 | 0.115 |
| `history` 0.08–0.22 | 0.115–0.185 | 0.185 |
| `new_evidence` 0.25–0.65 | 0.350–0.550 | 0.350 |

The supremum of the product over that whole box is **0.042326**. The thresholds
are **0.05** and **0.08**.

Measured rather than argued, over five worlds the freeze admits:

| admissible world | statistic | `>= 0.05` | `>= 0.08` |
| --- | --- | --- | --- |
| the shipped run, seed 2026082114 | 0.018375 | False | False |
| the declared ranges at another seed | 0.023500 | False | False |
| every rate from the favourable **half** of its range | 0.028750 | False | False |
| every rate from the favourable **tenth** of its range | 0.038375 | False | False |
| every family pinned at the extremal **corner** | **0.040250** | **False** | **False** |

and over 2,000 independent seeds of the frozen protocol:

| | |
| --- | --- |
| minimum | 0.015250 |
| mean | 0.020781 |
| maximum | **0.027750** |
| seeds reaching 0.05 | **0 / 2000** |
| seeds reaching 0.08 | **0 / 2000** |

The corner is a probability-zero event — every one of 20 families would have to
land on the endpoint of all eight uniforms at once — and even there, Hoeffding
over the 8,000 pooled cases bounds `P(realized ≥ 0.08) ≤ 1.4e-10`. The
attainment margins are **−0.00975** and **−0.03975**.

### The other five gates have no admissible world that fails them

`policy("ORION_RSE_FULL", c)` is

```python
if name=="ORION_RSE_FULL":
    return gold(c)
```

— the graded arm is the adjudication function that produces the answer key.
`divergence_of(orion_arm, reference=gold, space=…)` returns **0 changed points of
256**: the identity arm `TreatmentContrast` is named for, asked about a rule.
Three gates read that arm's own error rates, so each is true for every input that
exists:

| gate | reads | value for any input |
| --- | --- | --- |
| `full_zero_false_promotion` | ORION false promotion | `0.0` |
| `full_useful_discovery_recall_one` | ORION recall | `1.0` |
| `history_reopen_exact` | ORION reopen accuracy | `1.0` |

`matched_decision_budget` is `len(set(budget_receipts.values())) == 1` over
`{a: BUDGET_CHECKS for a in arms}` — a constant dict, so a constant `True`.
`each_ablation_worse` is the one gate with a live predicate; each registered
ablation errs on 8, 18, 4 and 1 of the 144 states, and each arm's most likely
error state keeps a per-case probability of at least 0.0117, 0.0056, 0.0091 and
0.0091 everywhere in the declared support, so across 8,000 cases the gate is
`True` with probability at least `1 − 3e-32`.

So `all(gates.values())` is `False` for every seed and every family draw the
frozen protocol permits. The published terminal is the only terminal the
artifact could ever have printed, and the paper's negative is arithmetic that was
settled when the ranges were written, not a measurement of the governance
contract.

### The instrument was not incapable — its pass region is outside the freeze

This is the half that clears the generator, and it is why this is not P8.
Re-opening the declared sampling ranges and nothing else — same seed, same nine
arms, same seven thresholds, same terminal expression, same loaded module — walks
the statistic up and the terminal flips:

| sampling support | discriminator sup | statistic | terminal |
| --- | --- | --- | --- |
| the declared ranges | 0.042326 | 0.018375 | `GATE_NOT_MET` |
| material reopening rare | 0.049814 | 0.027000 | `GATE_NOT_MET` |
| live negative history common | 0.102955 | 0.051750 | `GATE_NOT_MET` |
| both | 0.121170 | 0.074500 | `GATE_NOT_MET` |
| retained negative common | 0.150032 | 0.104000 | **`SUPPORTED`** |
| clean packets, live history | 0.182018 | 0.142250 | **`SUPPORTED`** |
| balanced retained-negative strata | 0.243743 | 0.220125 | **`SUPPORTED`** |

`measure_receipt_responsiveness` over the three worlds a reader can agree the
full contract should win in: **3 of 3 moved the verdict, 0 inert, 2 distinct
terminals, `PASS`**. The branch is live, the arithmetic is right, and the
crossing sits at exactly the preregistered 0.08 — which is 1.9× the ceiling of
the support the protocol froze.

### What the paper's own audit says, and what it does not

`P14A_OUTCOME_ROOT_CAUSE_V1.md` gets the mechanism right and stops one step
short. It names the cause a "benchmark-discriminator prevalence problem" and
states that "the maximum possible aggregate accuracy gap against this strongest
baseline **in the realized benchmark** was also 0.018375" — a statement about the
run that happened. The measurement above is the stronger one: the maximum over
the protocol's entire declared support is 0.042326, so no realization of this
benchmark could have cleared either gate. The difference between "this draw came
out short" and "no draw could clear it" is the difference between a null and a
tautology, and only the second disqualifies the negative as evidence.

The audit also does not mention that the graded arm is the answer key. The lane
found that separately — `P14B_PROTOCOL_CONFORMANCE_CORRECTION_V1.md` records
"the `ORION_RSE_FULL` arm reused the same adjudication function that generated
protected gold" as the reason P14B is non-authoritative, and P14C separates the
specification in response. The same circularity is present in P14A, is measured
here at 0/256, and is why four of its seven gates cannot fail.

## Failure class

`UNATTAINABLE_GATE_PREDETERMINED_TERMINAL`

A preregistered gate publishes a threshold and a run publishes which side of it
the measurement fell. The threshold is above every value the protocol's own
declared sampling support can produce, so the reported side was fixed before the
seed was drawn. The freeze is real, the seed is real, the digest is stable, the
comparator is selected prospectively, the terminal is derived from a live
conjunction — and the conjunction has one reachable value.

This extends the family rather than repeating it:

- `2026-08-unreachable-operator-inert-ablation/` — the **independent** variable
  never varied.
- `2026-08-vacuous-guard-zero-denominator/` — the **dependent** variable never
  varied.
- `2026-08-unapplied-treatment-vacuous-null/` — the **cause** did not vary.
- `2026-08-label-recoverable-from-construction-cue/` — both varied and the
  correlation was with the construction.
- `2026-08-invertible-commitment-vacuous-custody/` — the **commitment** opened.
- `2026-08-unfalsifiable-check-zero-refutation-capacity/` — the **predicate**
  could not be false.
- `2026-08-supplied-premise-unbuilt-decision/` — the **decision** was never made.
- `2026-08-unconditional-terminal-self-issued-authority/` — the **verdict** had
  no predicate at all.
- here — **the predicate had no reachable pass region.** The verdict is a
  function of the run, which is all `terminal_responsiveness` asks and P14A
  passes; what is empty is the intersection of the pass region with the set of
  runs the preregistration admits. A gate that cannot pass is worth exactly as
  much as a guard that cannot fail, and a programme that publishes negatives has
  to measure both directions of the same question.

Four properties let it survive review, and the first two are why this one is
harder to see than any of the eight above.

1. **A negative looks like integrity.** Every review reflex in this repository
   is tuned to a claimed positive: demand the denominator, demand the falsifier,
   demand the withheld input. A paper that reports `GATE_NOT_MET` against its own
   system, retains the result verbatim and writes its own root-cause audit
   triggers none of them. Nobody asks a negative to prove it could have been a
   positive.
2. **Preregistration is exactly the right practice, and it is what hid this.**
   The thresholds were frozen before execution, which is what makes them
   credible; and freezing a threshold without measuring the support of the
   statistic it reads is how a bar gets set above the instrument's ceiling with
   no step at which anybody would have noticed.
3. **The near-miss reads as a near-miss.** `0.018375` against `0.05` looks like a
   benchmark that came up 2.7× short and could plausibly clear the bar with more
   families, more cases or a different seed. It cannot: 2,000 seeds top out at
   `0.027750`, and the extremal corner of the entire declared support reaches
   `0.040250`. More data moves the estimate toward `0.0208`, not toward `0.05`.
4. **The five unconditional gates make the receipt look discriminating.** Five
   `true`s and two `false`s reads as a panel that separated what held from what
   did not. Four of the five cannot be anything but `true`, three of them because
   the arm they grade is the grader.

## Correct response

1. Do not read a preregistered gate's verdict before establishing that the
   protocol could have produced the other one.
   `orion.programme.gate_attainability` takes a statistic, a frozen threshold and
   a register of **admissible worlds** — inputs a reader can read and agree the
   freeze permits — and reports which of them satisfy it.
2. Return three values, and fail in both directions. No admissible world
   satisfying the gate is `THRESHOLD_UNATTAINABLE`; every admissible world
   satisfying it is `THRESHOLD_UNCONDITIONAL`; both are `FAIL`. An empty register
   is `Outcome.CANNOT_CHECK`, which by `Outcome.blocks` stops a promotion exactly
   as `FAIL` does. The verdict is built from `GuardExercise` rather than beside
   it — the opportunities are the registered worlds and the violations are the
   ones that fell short — so "nobody registered a world" and "the guard was never
   pressed" are one state with one answer.
3. Report the margin, not the boolean. `attainment_margin` is `−0.00975` and
   `−0.03975` here; a serialized `false` says only that the run lost, and the
   distance is what says the bar was never in reach.
4. Require every world to state why the freeze admits it. `admits` is mandatory
   for the same reason `opportunity_definition` is: registering one world outside
   the declared ranges turns an unattainable gate into an attainable one, which
   widens the protocol instead of measuring it. `tests/unit/study/p14/` pins both
   halves: every registered world's ranges lie inside the declared ones, and one
   world that does not would flip the same gate to `BOTH_OUTCOMES_REACHABLE`.
5. Ask the terminal separately from the gates, by intersecting per-world readings
   rather than per-gate verdicts. Attainability does not compose: seven
   individually reachable thresholds can still have no world that clears all
   seven at once, and `distinct_terminals == 1` is the number a receipt's reader
   actually needs.
6. Keep the responsiveness measurement beside it and do not let either offset the
   other. P14A is `PASS` on `measure_receipt_responsiveness` and `FAIL` on
   attainability, and that pair *is* the diagnosis — a responsive emitter whose
   pass region lies outside its own preregistration. Collapsing them into one
   verdict loses exactly the distinction that separates this from P8.
7. Ask whether the graded arm can disagree with the thing grading it.
   `divergence_of(arm, reference=gold, space=…)` returns `0` of `256` for
   `ORION_RSE_FULL`, the same instrument that named P6's "independent" verifier a
   paraphrase and P8's declared gold a transcription.
8. Point the instrument at the shipped artifact. `governance_gates` loads
   `run_p14a_controlled_governance_v1.py` from `papers/` and reproduces its
   committed `full_result_sha256` before transcribing a claim; a test re-evaluates
   `main()`'s seven gate expressions character for character against the
   registration in every world. An instrument that only ever runs on its own
   fixture is the failure it was written to catch.
9. Enumerate the fact space before quoting a benchmark's case count. 8,000 cases
   over 20 families is 144 distinct states, and the entire ORION-versus-baseline
   comparison lives on one of them; `axis_sensitivity` on the arm contrast shows
   every one of the eight axes moving it on at most one sibling pair.
10. Do not repair P14A. Its thresholds are frozen, its result is retained
    verbatim by the paper's own rule, and editing either would be the thing the
    programme forbids. What is owed is a statement in the manuscript and the
    claim ledger that the P14A negative is uninformative about the governance
    contract rather than evidence against it — a change to `papers/`, which
    belongs to that lane. The diagnosis, the instrument and the blocking audit
    are done here.

## General lesson candidate

**A negative is evidence only for as long as the protocol could have produced a
positive.** Prospective freezing, a published seed, a stable digest, a
prospectively selected comparator, an honest root-cause audit and a refusal to
edit the result all survive an unreachable threshold intact — every one of them
held here — because none of them is a statement about the support of the
statistic the threshold reads.

The sharper form: **freeze the threshold and the support together, or you have
frozen an outcome.** A threshold is a claim about a distribution, and a
preregistration that fixes the bar without fixing — and measuring — the range the
statistic can occupy has not preregistered a test; it has preregistered its
answer. Every gate in this repository with a numeric threshold should be asked
for the supremum (or infimum) of its statistic over the protocol's own admissible
inputs, and any gate whose threshold sits outside that interval should be
rewritten or removed before a run is read from it.

Stated once for the family this extends: `UNREACHABLE_OPERATOR_INERT_ABLATION`
is a mechanism that never ran, `VACUOUS_GUARD_ZERO_DENOMINATOR` an outcome that
could not vary, `UNAPPLIED_TREATMENT_VACUOUS_NULL` a cause that did not vary,
`LABEL_RECOVERABLE_FROM_CONSTRUCTION_CUE` a label explained by the construction,
`INVERTIBLE_COMMITMENT_VACUOUS_CUSTODY` a seal that opened,
`UNFALSIFIABLE_CHECK_ZERO_REFUTATION_CAPACITY` a predicate that could not be
false, `SUPPLIED_PREMISE_UNBUILT_DECISION` a decision nobody made,
`UNCONDITIONAL_TERMINAL_SELF_ISSUED_AUTHORITY` a verdict with no predicate — and
this one a **threshold no admissible run could reach**.

## Discharged since

Two of the residuals below were closed on 2026-08-22 in the paper lane, by the
instrument this record specifies rather than by prose.

**The papers/ statement is written** (Correct response 10). P14A's terminal,
seed, thresholds and receipt are retained verbatim and nothing is relabelled
positive; what the manuscript, the chapter, the README, the readiness report and
the claim ledger now say is that its evidential disposition is `CANNOT_CHECK` —
a measurement the frozen protocol could not take, not evidence against the
governance contract. `papers/paper-14-orion-rse/P14_GATE_ATTAINABILITY_ADJUDICATION_V1.json`
carries the margins, the supremum, the terminal reach and the responsiveness
measurement beside each other, produced by `verify_p14_gate_attainability_v1.py`
over instruments that reproduce the committed digest first.

**P14C is audited** (residual 5). `orion.study.p14.specification_conformance`
loads the shipped P14C runner and frozen table, reproduces
`74032348…f01a63`, and asks the reach question over the coordinate P14C actually
leaves free — which of the seven registered implementations sits in the graded
slot. Exactly one clears all eight gates and six fail at least one, so its
conjunction prints two terminals where P14A's printed one. Its
`accuracy_advantage_ge_0_10` fails for the donor, interaction and
negative-history ablations, and its `strongest_baseline_false_promotion_ge_0_10`
holds by construction — a difficulty *precondition*, which
`gate_attainability.GateRole` now distinguishes from a hypothesis, because a
certificate that always holds is a benchmark built to be measurable while a claim
that always holds has decided itself. One residual is reported rather than
absorbed: `full_discovery_recall_one` is satisfied by all seven subjects, since
an ablation removes a check and a policy reading fewer facts promotes more rather
than fewer, so no registered implementation abstains.

**P14B is audited too, and it is the mirror image.** `orion.study.p14.balanced_governance`
loads the shipped P14B generator, reproduces `784d57e6…d679e66`, and asks the
same question of a **positive** terminal — the case this record's own instrument
had never been pointed at, and the one
`orion.programme.registry_coverage` names as its sharpest unexamined panel. The
terminal survives: the four component ablations P14B's protocol registers, placed
in the graded slot, make the conjunction print both its words, and no threshold
is outside reach. What does not survive is the count. Four of the eight gates are
satisfied by every world the freeze admits — `full_discovery_recall_one` because
exactly three of the 256 fact assignments are adjudicated `SUPPORTED_RESIDUAL` by
gold and none of the nine registered policies declines any of them, and
`matched_budget` because the runner writes one literal into all nine arms; both
are hypothesis gates. The other two are preconditions, where holding everywhere
is the intended behaviour: the difficulty bar P14A could not reach in any
admissible world is cleared 2.9x here in every one, which is what P14B was frozen
to fix and did fix. So "eight gates, all true" is four readings and four
constants. This is the *other* half of the class: P14A's failure was a threshold
no run could reach, P14B's is a threshold no run could miss, and a receipt
serializes both as a boolean.

**And the question P14A could not measure is answered at P14A's own bars.** P14C
fixes the composition P14A sampled: four cases per semantic stratum makes the
`RETAIN_NEGATIVE` share exactly `4/28 = 0.142857`, against P14A's ceiling of
`0.042326` for the same quantity. Registered verbatim on that benchmark, `0.05`
lands inside `[0.142857, 0.142857]` and `0.08` strictly inside `[0.0, 0.142857]`,
and both are met at `0.142857`. No threshold was moved; the instrument was.

The pre-run half of Correct response 1 is now buildable without a run:
`gate_attainability.assess_threshold_support` takes a frozen threshold and the
protocol's own bound on the statistic it reads and returns the same three
reasons, and `require_supported_thresholds` refuses a battery with an
unattainable bar or with no discriminating hypothesis left in it. Pointed at
P14A it returns `-0.007674` and `-0.037674` from the declared support alone —
the check that would have cost a sentence at freeze time.

## Residuals and reopen coordinates

- P14A's *result* is still not repaired, and must not be. The audit blocks, which
  is the honest state; the paper lane changed the reading and the successor took
  the measurement, and neither touched the protected artifact.
- The shipped receipt is not *wrong*: `MULTI_REVIEW` really does false-promote
  `0.018375` of cases and the full contract really does not. What is denied is
  that comparing that number to `0.05` and `0.08` measured anything.
- P14A's `replay_status` records "one protected execution completed; second
  replay deferred", so gate 8 of the protocol's eight — byte-identical two-run
  replay — was never evaluated and does not appear in the emitted `gates` dict at
  all. Seven of eight preregistered conditions reached the terminal. The digest
  reproduces on a second execution here, so the omission is a bookkeeping gap
  rather than a failed condition, but it is a gate that was frozen and then not
  computed.
- The same nesting holds in P14B and P14C: both compare arms that are
  coarsenings of one adjudication rule, so their gaps are prevalences of the
  classes the coarsening drops. P14B is already labelled non-authoritative for
  the circularity, and is now audited by this instrument as well (see
  **Discharged since**): its terminal is reachable in both directions and four of
  its eight gates are not. P14C is now audited by this instrument too, and the
  nesting is why its separation is exactly the
  `RETAIN_NEGATIVE` stratum's share of the table; what the audit adds is that the
  share is *fixed by the freeze* rather than sampled, so the thresholds read
  against it are inside reach instead of above it.
- `each_ablation_worse` is the only P14A gate with a live predicate on both
  sides, and its pass probability is `1 − 3e-32`. It is reported as
  `THRESHOLD_UNCONDITIONAL` over the registered worlds, which is accurate but is
  a measured near-certainty rather than an identity, unlike the other four.
- Reopen if `run_p14a_controlled_governance_v1.py` changes: the pinned
  `full_result_sha256` will red first.
