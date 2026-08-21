# A transfer margin whose comparator answered every protected case with one word

**Observed:** 2026-08-21, tracing why P9-U-T4 (#662) is blocked — "the
representation-length and format-prior attacks are named as hostile alternatives
but have not been run" — against a merged paper whose headline is a `+0.75` and a
`+0.50` on a whole held-out domain, reproduced to a content digest and carrying
zero independent-verification discrepancies.

## Failure

P9's D1 result is the paper's external test. `P9_SCIENTIFIC_CLOSURE_RECEIPT_V1.md`
publishes it as `D1_TYPED_STRUCTURE_TRANSFER_SUPPORTED`:

```
transcript bag:                          0.25
untyped pair:                            0.90625
typed relational:                        1.0
same-information typed serialization:    0.5
typed minus transcript:                 +0.75
typed minus same-information serialization: +0.50
```

`main.tex` calls the last line the load-bearing one: "The same-information
contrast is the important one for interpretation. The serialized arm contains the
same typed semantic fields, so the `\DOneTypedMinusSerialized` difference cannot
be described as simple information addition. It instead shows that explicit
relational comparison makes those fields more useful to the selected classical
learner on this held-out-domain protocol."

Read the shipped archive's own `test_predictions`
(`research/extensions/p9-structured-neural/execution/D1_EXECUTION_RESULT_V1_2.json`,
`result_digest sha256:34003fb8…`, rebuilt byte-for-byte here before anything was
transcribed). Its 128-case protected split carries 32 `ALIGNED`, 64
`OBSTRUCTION`, 32 `UNRESOLVED`:

| arm | accuracy | distinct predictions on 128 cases | what it emitted | macro informedness | departures from its own modal answer |
| --- | --- | --- | --- | --- | --- |
| `TYPED_RELATIONAL` | 1.0 | 3 | 32/64/32 | 1.000000 | — |
| `UNTYPED_PAIR` | 0.90625 | 3 | 44/52/32 | 0.895833 | 76/128 |
| `TYPED_SERIALIZED_BAG` | 0.5 | **1** | `OBSTRUCTION` ×128 | **0.000000** | **0/128** |
| `TRANSCRIPT_BAG` | 0.25 | **1** | `ALIGNED` ×128 | **0.000000** | **0/128** |

Both arms the headline differences are taken against emit a single label on every
protected case. A constant predictor's accuracy *is* the prior of the label it
emits, so those two numbers are identities:

```
0.25 = 32/128 = prior(ALIGNED)
0.5  = 64/128 = prior(OBSTRUCTION)
```

and therefore

```
typed_minus_transcript                     = 1 - prior(ALIGNED)     = 0.75
typed_minus_same_information_serialized    = 1 - prior(OBSTRUCTION) = 0.50
```

Neither difference contains a fact about a representation. Both are statistics of
how the protected split was composed.

### The split is what moves them

Re-score the *archived predictions* on re-composed protected splits. No model is
refitted, no representation is touched, no feature family is changed and no case
is invented — every composition is a sub-multiset of the 128 cases the artifact
already scored (`python -m orion.study.p9.transfer_audit`):

| protected split composition | n | transcript | serialized | untyped | typed | `typed − transcript` | `typed − serialized` | D1 terminal |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| as frozen, 32/64/32 | 128 | 0.250000 | 0.500000 | 0.90625 | 1.0 | **0.750000** | **0.500000** | `…TRANSFER_SUPPORTED` |
| balanced 32/32/32 | 96 | 0.333333 | 0.333333 | 0.947917 | 1.0 | 0.666667 | 0.666667 | `…TRANSFER_SUPPORTED` |
| aligned-heavy 32/2/2 | 36 | 0.888889 | 0.055556 | 1.000000 | 1.0 | 0.111111 | 0.944444 | `…TRANSFER_NARROWED` |
| aligned-dominant 32/1/1 | 34 | 0.941176 | 0.029412 | 1.000000 | 1.0 | **0.058824** | 0.970588 | `D1_NO_TYPED_TRANSFER_ADVANTAGE` |
| obstruction-heavy 2/64/2 | 68 | 0.029412 | 0.941176 | 0.823529 | 1.0 | 0.970588 | **0.058824** | `…TRANSFER_SUPPORTED` |
| unresolved-heavy 2/2/32 | 36 | 0.055556 | 0.055556 | 1.000000 | 1.0 | 0.944444 | 0.944444 | `…TRANSFER_SUPPORTED` |

The published margin sweeps `0.0588 → 0.9706`, and the scientific terminal moves
through all three of its non-error values, with the experiment held fixed. Over
the same six compositions the **informedness** margin against each constant arm
is `1.000000` in every row — span exactly `0.0` beside a span of `0.9118`. The
only arm for which both statistics move together is `UNTYPED_PAIR` (published
span `0.1765`, informedness span `0.1231`).

### The transcript arm could not have answered, and it is provable before any fit

`_surface_tokens` mints every action identity as
`"s" + sha256(f"{seed}|surface|{side}|{index}")[:16]`, and the seed carries the
split and the domain. So across train and test:

| | distinct reminted surface tokens |
| --- | --- |
| train (numerical + graph) | 1,728 |
| protected test (workflows) | 768 |
| **shared** | **0** |

A `DictVectorizer` learns its vocabulary on train and silently drops every key it
did not see. Counting the *distinct in-vocabulary feature signatures* each view
presents on the protected split — no estimator, no solver, no seed involved:

| view | protected feature keys | surviving the fitted vocabulary | distinct protected rows |
| --- | --- | --- | --- |
| `TRANSCRIPT_BAG` | 515 | **3** | **1** |
| `TYPED_SERIALIZED_BAG` | 127 | 26 | 7 |
| `UNTYPED_PAIR` | 48 | 48 | 9 |
| `TYPED_RELATIONAL` | 26 | 26 | 13 |

The three transcript keys that survive are `left_action_count`,
`right_action_count` and `same_action_count`, and on the protected split they take
the values `2`, `2` and `True` on all 128 cases. The design matrix has **one
distinct row**. No model can give a second answer. Running the frozen grid
verbatim confirms it, and shows what the reported number actually depends on:

| config | distinct predictions | emitted | accuracy |
| --- | --- | --- | --- |
| `logistic-C0.1` (**the selected one**) | 1 | `ALIGNED` | **0.25** |
| `logistic-C1` | 1 | `UNRESOLVED` | 0.25 |
| `logistic-C10` | 1 | `UNRESOLVED` | 0.25 |
| `tree-depth3` | 1 | `ALIGNED` | 0.25 |
| `tree-depth6` | 1 | `ALIGNED` | 0.25 |
| `rf-depth6` | 1 | `OBSTRUCTION` | 0.50 |
| `rf-none` | 1 | `OBSTRUCTION` | 0.50 |

Seven of seven are constant. The published `0.25` versus a possible `0.50` is
decided entirely by which of the three labels the fit happens to settle on, and
`typed_minus_transcript` is `0.75` or `0.50` accordingly.

`TYPED_SERIALIZED_BAG` is the weaker version of the same thing: 7 distinguishable
protected rows rather than 1, and on the official run it still answered
`OBSTRUCTION` 128 times. That arm is also the one number in D1 that does not
reproduce here. Replaying the official protocol v1.2 on this checkout —
`scikit-learn 1.9.0` as the result environment records, but CPython 3.11.15 /
`numpy 2.4.6` / `scipy 1.17.1` against the official 3.12.13 / 2.5.2 / 1.18.0:

| arm | official | replayed here |
| --- | --- | --- |
| `TRANSCRIPT_BAG` | 0.25 | 0.25 |
| `UNTYPED_PAIR` | 0.90625 | 0.90625 |
| `TYPED_RELATIONAL` | 1.0 | 1.0 |
| `TYPED_SERIALIZED_BAG` | **0.5** | **0.75** |

Same dataset digest, same selected `logistic-C1`. The one arm whose output is not
a response to its input is the one arm that is numerically unstable across
environments, because a model with 26 live features and no signal is choosing
between labels on almost nothing.

### The paired statistics inherit the same arithmetic

`analyze_d1_paired_effects.py` is the manuscript's robustness analysis, and
`main.tex` quotes it: "all `\DOneTranscriptDiscordantWins` discordant cases favor
typed relational and none favor transcript (exact McNemar `p=…`)". Against a
constant arm, discordance is not an observation:

| comparator | b (typed right, comparator wrong) | c | exact McNemar p |
| --- | --- | --- | --- |
| `TRANSCRIPT_BAG` | 96 | **0** | 2.524×10⁻²⁹ |
| `TYPED_SERIALIZED_BAG` | 64 | **0** | 1.084×10⁻¹⁹ |
| `UNTYPED_PAIR` | 12 | 0 | 4.883×10⁻⁴ |

For a perfect candidate and a constant comparator, `b = n - prior(c)·n` and
`c = 0` by construction, so `p = 2·2^-b` is a function of the split's label prior
and nothing else. The first two rows are `2·2⁻⁹⁶` and `2·2⁻⁶⁴` written out. The
third is a measurement.

### What the existing instruments do and do not do

Every one was run against this contrast, and all of them clear it:

| instrument | verdict on D1 |
| --- | --- |
| `orion.study.p1.arm_validity.assess_arm_discrimination` | `DISCRIMINATED`, 4 distinct behaviour groups |
| `orion.programme.guard_exercise.assess_guard` | `PASS` / `HELD_UNDER_EXERCISE`, denominator 128 |
| `orion.study.p3.treatment_contrast.assess_coordinate_necessity` | `PASS` / `COORDINATE_LOAD_BEARING` — 128/128 treated, 96 decisions changed vs transcript, 32 vs serialized |
| `orion.programme.benchmark_identifiability.audit_label_identifiability` | `CANNOT_CHECK` / `NO_PROBE_SCORED` on all three labels — the fitted cue signatures do not occur on the protected split, which is the same vocabulary disjointness seen from the probe side, not a leak |
| `orion.programme.commitment_custody` | nothing is sealed in D1 |
| `orion.programme.refutation_capacity.divergence_of` | see below — it catches a *different*, already-recorded failure in the same file |
| `orion.programme.decided_premises` | D1 supplies no premise as a parameter; the per-coordinate comparison is computed from the payload |
| `orion.programme.terminal_responsiveness.measure_receipt_responsiveness` | `CANNOT_CHECK` / `NEVER_EXERCISED` on a smaller-split register — the traced margins do not move, because they are functions of *proportions*, which a smaller split preserves |

P3's is the instructive one. Its instrument is designed for exactly this shape of
question and returns `PASS`: the treatment altered the model's input on 128 of 128
cases and moved the decision on 96 of them, which is a real, applied treatment.
What did not vary is not the cause and not the input — it is the *comparator's
answer*, and no module in the repository was positioned to ask about that.

`benchmark_identifiability` already contains the decisive sentence, one level out:
"Informedness is 0 for every constant predictor and 1 only for a rule that
separates the label exactly, so it says what accuracy on a skewed label cannot."
It says it about leak probes. Nothing said it about an arm of a superiority
contrast.

### The half that is already recorded

Two facts about the *typed* side belong here for completeness, and neither is new.

`run_d1` emits `D1_EVALUATOR_FAILURE` when its "exact typed relational
comparator" scores below 1.0. That comparator recomputes the evaluator's own gold
rule over the same coordinates. Measured with P6's instrument over the whole
enumerated dataset:

```
divergence_of(exact_relational_comparator, reference=classify_methods, space=512 instances)
  -> points 512, points_changed 0
```

The branch cannot be taken. That is
`2026-08-unfalsifiable-check-zero-refutation-capacity/`, reproduced in P9's
sibling file, and it is measured here with the existing instrument rather than a
second one.

And the typed arm's 1.0 is not surprising once its feature space is written out.
`_typed_relational_features` emits 26 keys, of which **16** — `{coordinate}:equal`
and `{coordinate}:unknown` for the eight comparison coordinates — are the gold
classifier's own per-coordinate predicate. The D1 label is recovered from **two
derived bits** of that vector (`any unknown`, `all equal`) on **512 of 512**
instances. This record does not claim that is the failure; the paper reports the
closed-form comparator openly as a ceiling. It is the reason a 1.0 was available
to be differenced against a constant.

## Failure class

`UNRESPONSIVE_COMPARATOR_PRIOR_VALUED_MARGIN`

A superiority margin is published as candidate-minus-comparator on a protected
split. The comparator's input varied, its score is arithmetically correct, its
denominator is real — and it emitted one label over the entire split, so its
accuracy is identically the prior of that label and the reported difference is
`1 − prior`. The margin is a statistic of how the evaluation set was composed,
and re-composing it moves the number across nearly its whole range without
touching the experiment.

This is the ninth variance an experiment has to establish, and the eight beside it
are why it is a distinct one:

- `2026-08-unreachable-operator-inert-ablation/` — the **mechanism** never ran.
- `2026-08-vacuous-guard-zero-denominator/` — the **dependent** variable could not vary.
- `2026-08-unapplied-treatment-vacuous-null/` — the **cause** did not vary.
- `2026-08-label-recoverable-from-construction-cue/` — the **label** was explained by the construction.
- `2026-08-invertible-commitment-vacuous-custody/` — the **commitment** opened.
- `2026-08-unfalsifiable-check-zero-refutation-capacity/` — the **predicate** could not be false.
- `2026-08-supplied-premise-unbuilt-decision/` — the **decision** was never made.
- `2026-08-unconditional-terminal-self-issued-authority/` — the **verdict** had no predicate behind it.
- here — the candidate varied, the comparator's *input* varied, and the
  **reference level** did not. A difference needs two measurements, and this one
  has one measurement and a label prior.

The sharpest way to see the difference from P3 is that P3's instrument is *run*
here and returns `PASS`. An unapplied treatment has no contrast; this has a
contrast, on 128 of 128 cases, and one of its two endpoints is a property of the
answer sheet.

Three properties let it survive review.

1. **A degenerate arm is invisible in a score table.** `0.25` sits beside
   `0.90625` and `1.0` and reads as an ordering of representations. Only asking
   how many distinct answers each arm gave separates "read the cases and did
   badly" from "gave one answer"; the D1 archive carries the predictions that
   answer it and no artifact asked.
2. **The weaker the baseline, the more impressive and the less informative the
   margin.** `+0.75` is the largest number in the paper and the one carrying the
   least evidence; `+0.09375`, against the only comparator that responded, is the
   smallest and the only real one. The reporting convention rewards exactly the
   wrong arm.
3. **Every downstream statistic launders it.** A paired bootstrap over a constant
   comparator, a McNemar test with `c = 0` on 96 discordant cases, and a
   `p = 2.5×10⁻²⁹` are all arithmetically correct restatements of `32/128`. Adding
   significance machinery to a prior does not make it a measurement.

## Correct response

1. Ask what the comparator *did*, not what it scored.
   `orion.programme.comparator_response.score_comparator` takes gold labels and an
   arm's predictions and reports the distinct answers it gave, its macro
   informedness, and how many cases it answered with something other than its own
   most frequent answer. `ComparatorResponse` requires a written
   `response_definition` for the reason `GuardExercise.opportunity_definition` and
   `SealedSecret.domain_rationale` are required: an arm whose inputs nobody can
   state cannot be shown to have read them.
2. Return three values. `measure_contrast_margin` is `CANNOT_CHECK` when either
   arm is constant, when the split's gold never varies, when nothing was scored,
   or when the claimed margin is finer than one case; `FAIL` when the candidate
   does not beat the best constant on the split; `PASS` only when the comparator
   departed from its own modal answer. `CANNOT_CHECK` blocks a promotion exactly
   as `FAIL` does.
3. Build the verdict from `GuardExercise` rather than beside it. Opportunities are
   the comparator's departures and violations are the ones it got wrong, so "the
   comparator gave one answer" and "the guard was never pressed" are one state
   with one answer, and `GuardAssessment` already refuses to pair `PASS` with a
   vacuity reason.
4. Decompose the published number. `earned_margin` is the candidate over the
   better of the comparator and a constant; `prior_supplied` is the rest. On D1's
   transcript contrast that is `0.50` earned and `0.25` supplied — a quarter of
   the headline is the comparator guessing worse than not guessing.
5. Report informedness beside accuracy, and prefer it. It is 0 for every constant
   predictor, 1 only for exact separation, and it does not move when the split is
   re-composed. It is the statistic `2026-08-label-recoverable-from-construction-cue/`
   already chose for probes, asked here about an arm.
6. Re-score the frozen predictions on re-composed splits before quoting a
   difference. `measure_composition_sensitivity` is the evaluation-set counterpart
   of `axis_sensitivity`: an axis that changes no verdict multiplies every count,
   and a split composition that changes the margin *is* the margin.
   `composition_valued` is true exactly when the accuracy margin moved and the
   informedness margin did not move at all.
7. Refuse to hold the number. `EarnedMargin` cannot be constructed while its
   contrast blocks, so publishing `+0.50` as evidence that relational
   organization is load-bearing requires deleting the type rather than forgetting
   a check — the refusal `AuditedScore` makes about a leaking benchmark and
   `DecidedResult` about a supplied premise.
8. `require_responsive_comparator(contrasts, label=…)` raises before any margin is
   read as superiority, naming the arms that never answered — the
   comparison-side counterpart of `require_operators_exercised`,
   `require_treatment_applied`, `require_refutable`, `require_decided` and
   `require_responsive`.
9. Point the instrument at the shipped artifact. `orion.study.p9.transfer_margins`
   loads `D1_EXECUTION_RESULT_V1_2.json` from the repository and rebuilds the
   committed `result_digest` from its own bytes before transcribing a claim;
   `python -m orion.study.p9.transfer_audit` audits it and exits 3. An instrument
   that only ever runs on its own fixture is the failure it was written to catch.
10. Fix the control before re-running the comparison, and it is **not** fixed
    here. A transcript arm on a whole-domain holdout with independently reminted
    surface tokens cannot carry information by construction, so it is a
    memorisation control — which is what its own source comment calls it — and
    must not be an arm of a superiority contrast. The same-information serialized
    arm needs a vocabulary that survives the holdout (canonical paths without
    domain-specific values, or a shared value alphabet) before its difference from
    the relational arm can be attributed to relational organization rather than to
    out-of-vocabulary tokens. Both are changes to a frozen protocol, a merged
    result and a pinned digest, and belong to whoever owns them. The diagnosis and
    the instrument are done here, and the audit blocks until the control responds.

## What this costs P9 and what it does not

Less than it looks, and the paper's own caution should be preserved.

Nothing in `CLAIM_LEDGER_V1.md` is contradicted about D0/M1/A5/A2/A4. The M1
information lattice, the affine-composition residual and the explicit-inference
closures are separate results with separate protocols and are untouched here.
`P9_SCIENTIFIC_CLOSURE_RECEIPT_V1.md` already declines to claim the general
serialization principle, and `main.tex` already cites it as prior work.

What this record removes is exactly the sentence #662's P9-U-T4 asks to be
defended: that the `+0.50` shows "explicit relational comparison makes those
fields more useful". It shows that a bag of held-out-domain tokens has no fitted
vocabulary on a held-out domain.

What survives is real and is the stronger claim in the paper: `UNTYPED_PAIR`
answered 76 of 128 protected cases off its modal label, reached `0.90625` with
informedness `0.8958`, and the typed relational arm beat it by `0.09375`. That is
the one D1 margin computed against an arm that read the cases. It is also the
comparison that is hardest to explain away, because the untyped arm sees the same
coordinates, the same holdout and the same vocabulary — it differs from the typed
arm only in whether the values or their shapes are visible.

## General lesson candidate

**A difference is evidence only when both of its terms are measurements.** A
content digest, a frozen protocol, an independent pre-artifact expectation with
zero discrepancies, a paired bootstrap, an exact McNemar test and a whole-domain
holdout all survive a constant baseline intact — every one of them held here —
because none of them is a statement about whether the comparator answered.

The sharper form: **ask every baseline how many distinct answers it gave.** A
score table shows one number per arm and hides the arity of each arm's output,
and the arm with the lowest score is the one most likely to have an arity of one.
Any arm whose predictions take a single value on the evaluation set has an
accuracy that is a label prior; report it as `prior(c)` rather than as a rate, and
the difference beside it stops looking like a result.

The version specific to held-out-domain designs: **a holdout that removes a
control's entire feature vocabulary has not tested the control, it has deleted
it.** Reminting, domain-disjoint identifiers and protected splits are all good
instruments for defeating memorisation, and each of them can turn a comparison arm
into a constant. Before differencing against such an arm, count how many distinct
in-vocabulary rows the protected split presents to it — one row means one answer,
and that is knowable before a single model is fitted.

Stated once for the family this extends: `UNREACHABLE_OPERATOR_INERT_ABLATION` is a
mechanism that never ran, `VACUOUS_GUARD_ZERO_DENOMINATOR` an outcome that could
not vary, `UNAPPLIED_TREATMENT_VACUOUS_NULL` a cause that did not vary,
`LABEL_RECOVERABLE_FROM_CONSTRUCTION_CUE` a label explained by the construction,
`INVERTIBLE_COMMITMENT_VACUOUS_CUSTODY` a seal that opened,
`UNFALSIFIABLE_CHECK_ZERO_REFUTATION_CAPACITY` a predicate that could not be false,
`SUPPLIED_PREMISE_UNBUILT_DECISION` a decision that was never made,
`UNCONDITIONAL_TERMINAL_SELF_ISSUED_AUTHORITY` a verdict with no predicate behind it
— and this one a **comparison with only one side**.

## Residuals and reopen coordinates

- The control repair is not made here (see Correct response 10). The audit blocks
  on it, which is the honest state.
- `D1_EXECUTION_RESULT_V1_2.json` is *not* wrong as shipped. With the shipped
  arms the transcript accuracy really is 0.25 and the serialized accuracy really
  is 0.5 in the official environment. What is denied is that the differences
  against them measure a representation.
- `TYPED_SERIALIZED_BAG` does not reproduce on this checkout (0.75 against the
  official 0.5) with the same dataset digest and the same selected configuration.
  `RESULT_EXECUTION_ENVIRONMENT_V1.md`'s reproduction rule says a later
  environment changing numerical behaviour "is a new reproduction discrepancy to
  investigate"; that investigation is not done here, and the diagnosis above
  predicts it will be found in the arm's 7-cell in-vocabulary design rather than
  in the protocol.
- The `+0.09375` untyped margin is quotable by this instrument and is *not*
  audited for the other eight failure shapes. In particular the typed arm's
  features contain the gold's own per-coordinate predicate; that is disclosed by
  the paper as a closed-form ceiling but it has not been asked whether the untyped
  contrast is identifiable in the sense of `benchmark_identifiability`.
- The M1 view comparison (`SURFACE 0.5`, `TOPOLOGY 0.5`, `TYPED 0.6666667`,
  `CURRENT 0.6701389`, `SEMANTIC 0.8368056`) is a sibling design with the same
  arm-versus-arm reporting shape and is **not** audited here. It should be, by the
  same instrument, before any view difference is quoted.
- `research/development/cannot_check_inventory.json` needs one regeneration to
  cover this module's five new `CANNOT_CHECK` sites. It was already out of date
  against other lanes' modules before this work (594 derived versus 586 committed
  with this module removed), so the regeneration is a shared action and is not
  taken here.
- Reopen if the D1 protocol's protected split composition, `_surface_tokens`, the
  feature families or the frozen model grid change: the pinned `result_digest`
  and `dataset_manifest_digest` will red first.
