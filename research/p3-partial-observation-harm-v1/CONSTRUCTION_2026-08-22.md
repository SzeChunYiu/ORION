# Construction: P3 partial-observation harm corpus v1

| field | value |
| --- | --- |
| atlas id | `partial-observation-harm-v1` |
| protocol id | `P3.partial-observation-harm-corpus.v1` |
| location | `research/p3-partial-observation-harm-v1/` |
| cases file | `research/p3-partial-observation-harm-v1/cases.jsonl` (33 cases) |
| standard | `research/p3-partial-observation-harm-v1/PARTIAL_OBSERVATION_HARM_STANDARD.json` |
| builder | `src/orion/study/p3/partial_observation_harm_build.py` |
| build report | `research/p3-partial-observation-harm-v1/BUILD_REPORT.json` |
| case schema | unchanged: `orion.p3.public-reference-case.v1` |
| serves | `G6_HARM_A1` of `P3_PARTIAL_OBSERVATION_COORDINATE_FREEZE_2026-08-21`, via amendment 001 |

**This is a construction record, not a pre-registration.** It was written with the
build. The thing that *was* pre-registered is the gate this corpus feeds:
`G6_HARM_A1`'s statement and its threshold of zero were fixed on 2026-08-21,
before the corpus existed, and neither is touched. What was not pre-registered is
which cases would exist — and because the gate reads "changes **0** decisions", a
corpus added to it can only leave it standing or fail it. There is no corpus that
makes it pass. That asymmetry is why building the denominator after the fact does
not put the outcome in the builder's hands.

## 1. What is being repaired

`orion.study.p3.partial_observation_probe` reported `G6_HARM_A1` as
`CANNOT_CHECK`, saying:

> A1 cannot fire on any intact pair because no intact pair has a one-sided
> absence; 0 changes is a structural zero, not a demonstration of safety.

The gate is a harm guard: it exists to show that the candidate repair
`A1_observedness_asymmetric` — abstain when a coordinate is stated on one side of
a pair and not the other — does not destroy answers the current rule gets right.
Demonstrating that requires cases the repair *could* break. None of the three
corpora P3 owns has one. Amendment 001 of the freeze records the evidence that a
one-sided absence is admissible rather than definitionally excluded; this document
records how the cases were built.

## 2. The derivation rule

Gold is derived from the emitted standard table by
`identity:observed-coordinate-precedence-with-completion-invariance`, implemented
as `gold_from_standard` and written out rather than delegated to
`compare_meaning`, so that gold is not defined by the system under test.

1. Two projections whose predicates are not the same entry of the table are
   `UNRESOLVED`. They are not yet the kind of pair the coordinates describe.
2. Otherwise: complete every coordinate that is stated on exactly one side with
   each admissible value of that coordinate in the table. If the relation read off
   the completed pair is not the **same for every completion**, the pair is
   `UNRESOLVED`. Nothing in the two projections separates the world in which the
   silence hides an agreement from the world in which it hides a difference.
3. Otherwise it is that constant relation, read in precedence order: referent,
   then construct, then measurement, then the contextual coordinates (temporal,
   attribution, discourse, assumption, modal force), then polarity.

Step 2 is the whole point and it is **decidable**, not argued: the admissible
value table is finite and frozen, so "the answer does not depend on the absent
coordinate" is checked by enumeration, case by case, and the enumerated relation
sets are in `BUILD_REPORT.json` under `construction_receipts`.

Rule 3 agrees with `compare_meaning` on every fully observed pair, by design and
by check: `rule_agreement_on_fully_observed` compares the two on all 85 completed
pairs the corpus generates and the build refuses to emit on any disagreement. That
agreement is what makes `H_UNDECISIVE_ABSENCE` a harm denominator — A0 gets those
cases right, so an arm that moves them is destroying something.

## 3. The four strata

Every case states all nine identity coordinates on both sides except where the
stratum says otherwise, and no case has more than one one-sided absence.

### 3.1 `H_UNDECISIVE_ABSENCE` — 12 cases, gold determinate

One coordinate absent on exactly one side, where a **strictly higher-precedence**
coordinate already decides the pair. Six are decided at `referent_ids` (which
differ, both sides stated) with the absence at `construct_ids`,
`measurement_ids`, `temporal_context_ids`, `attribution_id`,
`discourse_relation` or `assumption_ids`. Six are decided at `construct_ids` with
the absence at `measurement_ids`, `temporal_context_ids`, `attribution_id`,
`discourse_relation`, `assumption_ids` or `modality`. Gold is
`DISTINCT_REFERENT` or `DISTINCT_CONSTRUCT` and is constant over every admissible
completion, because the precedence rule returns before it reads the absent
coordinate.

These are the cases A1 can damage: the thing it abstains over cannot change the
answer.

### 3.2 `D_DECISIVE_ABSENCE` — 9 cases, gold `UNRESOLVED`

One coordinate absent on exactly one side and everything else equal, so the
absent coordinate is exactly what the answer turns on. The completions disagree —
the mirror's value gives `COMPATIBLE`, a different admissible value gives a
separation — so gold is `UNRESOLVED`. One case per coordinate.

This stratum is a nine-cell census of the absence-reading inconsistency the freeze
names in section 1.2, measured on **authored** cases rather than on redactions.
Measured result: eight coordinates merge-ward (`compare_meaning` returns
`COMPATIBLE`), one — `modality` — separation-ward (`CONTEXTUAL_DIFFERENCE`),
matching the freeze's declared table in all nine cells. The builder refuses to
emit if any cell disagrees with that table.

### 3.3 `S_INCOMPARABLE` — 6 cases, gold `UNRESOLVED`

One coordinate absent on exactly one side, and the two predicates are not the same
normalized relation, so the pair is `UNRESOLVED` for a reason that has nothing to
do with the absence. `compare_meaning` returns `UNRESOLVED` too, so A1 fires here
and costs nothing.

Without this stratum, "A1 changed every pair it could fire on" would be
unfalsifiable. The builder refuses to emit a corpus in which the count of pairs
the rule can fire on equals the count it changes.

### 3.4 `C_FULLY_OBSERVED` — 6 cases, no absence at all

Nothing missing on either side; three gold `COMPATIBLE`, three gold
`DISTINCT_REFERENT`. A1 must not fire on these. Without them `fraction_changed`
would have no denominator A1 was supposed to leave alone.

## 4. What the builder refuses to emit

`verify` raises rather than writing when any of these fails, so a corpus that
cannot serve the gate never reaches the gate:

- a stratum's cases do not have the number of one-sided absences the stratum
  contract states (1, 1, 1, 0);
- `H`/`C` gold is not determinate, or `D`/`S` gold is not `UNRESOLVED`;
- `compare_meaning` does not reproduce gold on `H`/`C`/`S`, or does reproduce it
  on `D`;
- the corpus has no one-sided absence at all — it would leave `G6` exactly as
  vacuous as it was;
- no pair on which an abstain-on-asymmetry rule could destroy a correct answer —
  a harm gate over such a corpus could not report a harm even if one existed;
- every pair the rule can fire on is a pair it changes;
- the derivation rule and `compare_meaning` disagree on any fully observed pair;
- this module and the probe disagree about which value means "absent";
- the measured absence reading disagrees with the freeze's declared table.

## 5. Shape

`case_id` is `poharm-` plus a 16-digit content digest: constant length, constant
hyphen count, constant alphabetic prefix. All-digit for the reason
`p3_coordinate_necessity_build` uses an all-digit digest — a hex digest's leading
non-digit run varies across cases and an identifiability probe reads that as a
construction cue. `projection_id` and `source_span` are fixed-width, one source
record per case, one authority kind, one derivation rule.

Each case carries a `partial_observation` block naming its stratum, absent
coordinate and absent side. That block makes the stratum recoverable from the
case file, which is deliberate: it is audit metadata, and no arm reads it. The
arms are handed two `ScientificMeaningProjection` objects and nothing else.

## 6. Measured on this corpus

From `BUILD_REPORT.json` and from the probe's own run:

| quantity | value |
| --- | --- |
| cases | 33 |
| pairs with a one-sided absence | 27 |
| coordinates never one-sided | none — all nine are covered |
| A1 could fire on | 27 pairs |
| A1 decisions changed | 21 |
| A1 correct answers destroyed | **12** |
| A0 `P3.OVERRESOLVED_UNRESOLVED_CASE` | 9 violations of 15 opportunities, rate 0.6 |
| A0 false merges / false splits | 0 / 0 |
| absence reading | 8 merge-ward, 1 separation-ward |

`G6_HARM_A1` moves from `CANNOT_CHECK` (vacuous) to `FAIL` (measured). A1 is not
safe.

### 6.1 What this corpus cannot evaluate, and why

A1 abstains on *any* one-sided absence. A rule that abstained only where the
absence is **decisive** — which is what step 2 of the derivation rule does — would
not pay A1's cost on `H_UNDECISIVE_ABSENCE`. That looks like an obvious
improvement and this corpus **cannot** establish it: gold here is *defined* by
that rule, so scoring it against this gold is circular by construction, exactly
as the coordinate-necessity atlas cannot score the arms whose answer its own rule
derives. Naming the candidate is fair; measuring it needs a corpus whose gold does
not come from it.

Note also that A1 and A2 are indistinguishable on this corpus: every pair with a
one-sided absence also has an absence of the kind A2 fires on, and the six
`C_FULLY_OBSERVED` pairs have neither, so the two arms make identical decisions on
all 33. The corpus separates abstention from harm; it does not separate the two
abstention rules from each other. The three symmetric atlases are where A2's
distinct cost is visible.

## 7. External validity — the bound, stated here so it travels

The cases are **synthetic**. Gold follows from the emitted standard table by the
rule above, not from an upstream expert corpus. This corpus can establish that
`compare_meaning` misreads a one-sided absence in a specific way, and that an
abstain-on-asymmetry repair destroys correct answers at a specific rate on pairs
of that shape. It **cannot** establish that such pairs are frequent in public
scientific corpora. It is a harm-gate denominator, not an accuracy benchmark: gold
on the determinate strata is derived by a precedence rule that coincides with what
`compare_meaning` does on fully observed pairs, so the current system answers those
by construction. It may not be substituted for the public-reference atlas in any
external-validity claim, and no accuracy, false-merge, false-split or superiority
number over it is evidence about ORION's competence.

## 8. Out of scope, and not done

- No frozen atlas, adjudicated case or committed P3 result is edited.
- `research/p3-coordinate-necessity-v1/cases.jsonl` is **not** extended. Its own
  freeze forbids adding gold-`UNRESOLVED` cases (it would move the abstention
  denominator and the coordinate denominator at once, confounding both) and its
  recorded `cases_hash`, identifiability results and before/after ablation table
  all assume its 56 cases. The new cases are a separate corpus with its own
  identity — the same move that freeze itself made.
- No threshold is relaxed and no zero-denominator report is converted into a pass.
