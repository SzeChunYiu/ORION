# An ablation that reported a zero-width null without applying its treatment

**Observed:** 2026-08-21, tracing why P3's `P3.C6` — "necessity of every
coordinate" — is `CANNOT_CHECK` for four of six coordinates while the analysis
that produced it reports the tightest null an experiment can print.

## Failure

`papers/paper-03-global-knowledge-portrait/evidence/public-reference-v1/ANALYSIS.json`
records, for four of the six ablation arms:

```json
"remove_referent":        {"accuracy_ablation_minus_full":
                           {"candidate_minus_baseline": 0.0,
                            "ci95_low": 0.0, "ci95_high": 0.0}},
"remove_construct":       ... identical ...,
"remove_measurement":     ... identical ...,
"remove_temporal_context":... identical ...
```

Four arms, one number, one interval of width zero. Read as coordinate necessity,
that is four coordinates shown not to matter. It is two, and two absences.

`orion.study.p3_public_reference_analysis.ablated_relation` ablates by
`replace(projection, measurement_ids=())`. Instrumenting the *inputs* the arms
hand to `compare_meaning`, rather than the rates that come out, separates them —
measured on the frozen `public-reference-v1.1-confirmatory` atlas, n=32:

| ablation arm | field it empties | cases where that field is populated | cases the treatment altered | decisions changed |
| --- | --- | --- | --- | --- |
| `remove_referent` | `referent_ids` | 32 / 32 | **32** | 0 |
| `remove_construct` | `construct_ids` | 19 / 32 | **19** | 0 |
| `remove_measurement` | `measurement_ids` | **0 / 32** | **0** | 0 |
| `remove_temporal_context` | `temporal_context_ids` | **0 / 32** | **0** | 0 |
| `remove_modality_polarity_attribution_discourse` | four scalar fields | 19 / 32 | 19 | 6 |
| `force_compatibility_without_obstruction` | none — overrides the rule | — | 32 | 6 |

The exploratory `public-reference-v1` atlas gives the same shape: treated counts
of 32 / 21 / **0** / **0** on the four coordinate arms, and 4 decision changes on
each of the two obstruction arms.

The last arm alters no projection: it short-circuits the comparison where the two
predicates are equal, which on both atlases is all 32 cases. Its treated set is
the cases where that branch binds — a different measurement, not an exemption
from measuring.

`measurement_ids` and `temporal_context_ids` are empty on every case of both
frozen atlases. `replace(projection, measurement_ids=())` on an empty tuple is
the identity. Those two arms evaluate `compare_meaning(left, right)` on inputs
byte-identical to the full system's, so their difference vector is 32 zeros by
construction, and the paired bootstrap over 32 zeros returns `0.0` with a
`[0.0, 0.0]` interval. The arm is the full system compared against itself.

The rule under test is not the problem. Both coordinates are live in
`orion.knowledge.semantics.compare_meaning` and both flip a decision when the
data reaches them:

```text
measurement_ids differ:      DISTINCT_MEASUREMENT  → ablated → CONTEXTUAL_DIFFERENCE
temporal_context_ids differ: CONTEXTUAL_DIFFERENCE → ablated → COMPATIBLE
```

The coordinate is load-bearing in the code and absent from the corpus, and
`ANALYSIS.json` cannot distinguish that from a coordinate that was removed and
turned out not to matter — which is exactly what `remove_referent` is. That arm
stripped a coordinate populated on 32 of 32 cases and changed no decision. It is
a real negative, it is the more interesting of the two facts, and today it is
printed in the same characters as the two arms that measured nothing.

Two more denominators in the same artifact, found by the same instrument:

- **The false-merge denominator is the whole atlas, not the pairs that admit a
  false merge.** `_rates` divides by `n`. Only 6 of 32 gold relations are
  non-mergeable, so the headline `flat_predicate_canonicalization` false-merge
  rate of `0.1875` and the frozen `paired_absolute_difference: -0.1875` in
  `P3_BOUNDED_PUBLICATION_TRACK_V1.json` **understate the effect 5.33-fold**: the
  flat comparator false-merges on **6 of 6** — every case where a false merge was
  available — and ORION on 0 of 6. As with P2, the honest denominator makes the
  real result stronger, not weaker.
- **The false-split guard's comparator cannot false-split.**
  `flat_predicate_baseline` returns `COMPATIBLE` or `UNRESOLVED`;
  `exact_coordinate_baseline` returns `COMPATIBLE` or `UNRESOLVED`. Neither has a
  branch that returns a non-merge relation, and measured across both atlases
  each emits **0 separations on 32 of 32 cases**. So
  `false_split_orion_minus_exact = 0.0 [0.0, 0.0]` — the evidence behind P3-U-T2,
  "no unacceptable false-split/plurality penalty" — is a non-inferiority
  comparison against an arm structurally incapable of paying the penalty, on any
  corpus. ORION's own side is real: it separates 6 times, wrongly 0 times, across
  26 mergeable pairs. The comparison is not.
- **Abstention calibration has no denominator at all.** The gold relations are
  `{COMPATIBLE: 26, CONTRADICTORY: 6}`; there are **0** gold-`UNRESOLVED` pairs,
  so #651's "unresolved calibration" measures caution, not calibration, and an
  abstention on this atlas is always an error and never a success.

## Failure class

`UNAPPLIED_TREATMENT_VACUOUS_NULL`

An experimental arm reports a null — often the most confident-looking null
available, a point estimate of exactly zero with a zero-width interval — when its
treatment made no difference to the input it claims to vary. The number is
structural, not measured, and it is indistinguishable from the genuine null it
sits next to in the same table.

This is the data-level form of `UNREACHABLE_OPERATOR_INERT_ABLATION`
(`research/failures/2026-08-unreachable-operator-inert-ablation/`) and it evades
that failure's instrument. There, the ablated operator was never reached; here
the ablation operator ran on every one of 32 cases, and `replace(x, f=())` on an
already-empty `f` is the identity. Operator coverage answers "did the code run",
truthfully and uselessly. The question that separates these arms is one layer in:
**did the treatment change anything**.

It is also the independent-variable twin of `VACUOUS_GUARD_ZERO_DENOMINATOR`
(`research/failures/2026-08-vacuous-guard-zero-denominator/`). That record's
subject is a dependent variable that could not vary; this one's is an independent
variable that did not. P3 carries both at once, in one file, and every integrity
property holds over both: the atlas is content-hashed, the authority policy
forbids LLM gold, the confirmatory set shares no case id with the exploratory
one, an independent evaluator agreed on 32 of 32, and the bootstrap seed is
frozen at `20260817`.

A third property let it survive: **a zero-width interval reads as strength.**
`0.0 [0.0, 0.0]` looks like the cleanest possible measurement. It is the exact
signature of resampling a difference vector that is identically zero, which is
what you get when you resample a run against itself.

## Correct response

1. Do not report an ablation's difference before establishing that the arm's
   input differed from the control's.
   `orion.study.p3.treatment_contrast.contrast_from_runs` measures that from the
   two runs — comparing inputs, not configuration names — and
   `require_treatment_applied(contrasts, label=...)` **raises**, naming the arms
   whose treatment was the identity. Against either frozen atlas it names
   `remove_measurement` and `remove_temporal_context`.
2. Return three values. `assess_coordinate_necessity` gives `PASS` when the
   coordinate was removed and decisions moved, `FAIL` when it was removed and
   nothing moved — a real negative worth publishing — and `CANNOT_CHECK` when it
   was never removed. `NecessityAssessment` refuses at construction to pair
   `PASS` with any vacuity reason, so the substitution cannot return by edit.
3. Carry the resolution with the null. A contrast over 2 treated cases and one
   over 200 are the same point estimate; `TreatmentContrast.resolution` is the
   part `[0.0, 0.0]` hides, and `min_treated_cases` lets a caller state the floor
   below which a negative is not worth asserting.
4. Give the guards their real denominators.
   `orion.study.p3.identity_opportunity.IdentityDecisionKind` is total, so
   abstentions and gold-`UNRESOLVED` pairs appear in the ledger instead of
   dissolving into a rate, and only pairs whose gold admits the violation enter
   it. Reuses `orion.programme.guard_exercise` rather than restating it.
5. Make "the comparator could have paid this penalty" a denominator condition,
   not a footnote. An arm that never separates anywhere in the atlas gets zero
   false-split opportunities, so `assess_non_inferiority` returns
   `COMPARATOR_NEVER_EXERCISED` and P3-U-T2 blocks — which is the honest state of
   that gate as currently instrumented.
6. Point the instrument at the shipped artifact, not only at a fixture.
   `python -m orion.study.p3.public_reference_audit --cases <atlas>.jsonl` audits
   either frozen atlas and exits 3. An instrument that only ever runs on its own
   test data is the failure it was written to catch.
7. Repair the corpus so `measurement_ids` and `temporal_context_ids` are
   populated on cases whose correct answer depends on them, and add gold-
   `UNRESOLVED` and separating-comparator cases. That is the atlas lane's call
   (#280's V2 atlas, whose `GOLD_STATUS.json` is already `CANNOT_CHECK` with
   `v2_experiment_executed: false`) and is **not** done here; the diagnosis and
   the instrument are.

## General lesson candidate

**An experiment must verify that its treatment was applied, not that its
treatment was configured.** The name of an arm, the presence of the ablation
branch, and the execution of the ablation code are all compatible with the arm
handing the system under test exactly the control's input. Only comparing the two
inputs settles it, and that comparison is cheap and almost never made.

The sharper form: **a difference of exactly zero should be treated as a
diagnostic before it is treated as a result.** Real effects are rarely exactly
zero and real nulls rarely have zero-width intervals; both are the arithmetic
signature of comparing something with itself. Every arm in this repo that reports
a point estimate of `0.0` with a `[0.0, 0.0]` interval should be asked what its
treatment changed and over how many cases.

Stated once for the family this now completes: `UNREACHABLE_OPERATOR_INERT_ABLATION`
is a mechanism that never ran, `VACUOUS_GUARD_ZERO_DENOMINATOR` is an outcome that
could not vary, and `UNAPPLIED_TREATMENT_VACUOUS_NULL` is a cause that did not
vary. **Every reported comparison needs both of its variances established — the
one it manipulated and the one it measured — and neither is visible in a rate.**
