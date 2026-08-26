# ORION-13 Partial-Observation Coordinate Freeze — Amendment 002

**Amends** `P3_PARTIAL_OBSERVATION_COORDINATE_FREEZE_2026-08-21.md`, its twin
`P3_PARTIAL_OBSERVATION_COORDINATE_FREEZE_2026-08-21.json`, and Amendment 001
and its twin.
**Date** 2026-08-22. **Gate served** `G9_HARM_A3` (new). **Gate not touched**
`G6_HARM_A1`.
**Every amended document is left byte-identical.** This is a separate record with
its own parameter digest; the runner binds to this one while it is in force.

| field | value |
| --- | --- |
| amended parameters digest (2026-08-21) | `28d3e289d3dddddaef142e5756b77a825829836f1eadb900b80e49f985f73691` |
| amendment 001 parameters digest | `d4e97dcfc8a35d97656ec5eee60efc249a8e24dc682dd153c029fd9450b59ac8` |
| amendment 002 parameters digest | `9292414c63a50f0f31ad832b45a891a1eaf90584751f90f10362d941ad36c28e` |
| runner | `src/orion/study/p3/partial_observation_probe.py` |
| arm added | `A3_decisive_absence_only` |
| gates added | `G9_HARM_A3` (blocking), `G10_BENEFIT_A3` (non-blocking) |

## 1. What is being repaired

Amendment 001 gave `G6_HARM_A1` a denominator and the gate came back `FAIL`, in
the runner's own words:

> A1 could fire on 27 intact pairs, moved 21 decisions and destroyed 12 correct
> answers.

The twelve destroyed answers are exactly the `H_UNDECISIVE_ABSENCE` stratum of
`research/p3-partial-observation-harm-v1/`. On those pairs a strictly
higher-precedence coordinate already decides the relation, and the coordinate
that is stated on one side only could not have changed it whatever the silent
source would have said.

`A1_observedness_asymmetric` returns `UNRESOLVED` whenever
`_one_sided_absences(left, right)` is non-empty. It abstains on the *presence*
of an absence. That is a defect in A1's design, not in the measurement that
caught it: what warrants abstention is not that a source was silent but that the
silence is what the answer turns on. A1's harm on the `H` stratum is not
incidental, it is necessary — on any pair with a one-sided absence whose gold is
determinate and which A0 already answers correctly, A1 must destroy a correct
answer.

## 2. The arm

`A3_decisive_absence_only` abstains only when the absence changes the answer.

> Complete every coordinate stated on exactly one side with each of two
> witnesses — the value the other side states, and a synthetic value distinct
> from it — and run `compare_meaning` on every combination. If the relation is
> the same for all of them, return it. Otherwise return `UNRESOLVED`.

Two witnesses per absence is a complete enumeration rather than a sample. Every
branch of `compare_meaning` tests an absent coordinate only for equality with the
mirror value — the three `left.X and right.X` guards, `_same_or_empty`, the
`modality` inequality and the `polarity` inequality all do — so the relation, as
a function of what the silent source might have said, takes at most the two
values these witnesses produce.

The witness values are derived from the coordinate's own type and from the value
the other side states, and from nothing else. In particular they are not drawn
from any corpus's vocabulary. A rule that asked "could the silence have hidden
one of *these* values" would be reading its answer off whichever table it was
handed, and section 4 is about exactly that hazard.

A0, A1 and A2 are untouched. A1's measured harm is a finding and stays
reproducible.

## 3. `G6_HARM_A1` is not repointed

`G6_HARM_A1` names `A1_observedness_asymmetric`. It keeps its statement, its
threshold of zero, its arm, its denominator and its `FAIL`. Pointing a failing
gate at the arm that repairs the arm it was about would turn a failure into a
pass by changing the gate's subject, which is a relabelling and not a repair. The
new arm gets new gates and answers for itself.

## 4. The circularity, and what was done about it

`research/p3-partial-observation-harm-v1/` derives its gold by the rule
`identity:observed-coordinate-precedence-with-completion-invariance`: a pair is
`UNRESOLVED` when the relation is not constant over the admissible completions of
what one source did not state. That is A3's decision rule. The corpus's own
construction document, and the caveat the runner has carried since amendment 001,
both say a decisiveness-aware arm cannot be scored on it. That warning is correct
and this amendment keeps it.

**4.1 Accuracy is refused.** A3 reproduces gold on all 33 cases. That is its
definition restated. No accuracy number for A3 over this corpus appears in the
result, in the gates, or in any claim.

**4.2 Harm is a different question in general.** Harm asks whether a decision A0
already got right was moved to a wrong one. No gold-derivation rule fixes that:
it is a three-way comparison between A0, the candidate and gold. An arm can be
inaccurate overall without being harmful, and harmful without being inaccurate
overall. So "score its harm, not its accuracy" is a real distinction and not a
dodge.

**4.3 On this corpus the distinction collapses anyway.** If a candidate
reproduces gold on every case of a corpus, there is no case left on which it can
be wrong, so its harm there is zero by arithmetic. A3 reproduces gold on all 33.
Its zero harm on this corpus is entailed by the circular accuracy and carries
nothing the accuracy number did not already carry. Reporting it as evidence of
safety would be the identity-dressed-as-a-measurement defect this lane exists to
catch. **It is not reported as such.**

**4.4 The two functions are not identical.** `arm_decisive_absence_only` and
`gold_from_standard` differ in their inner relation rule (`compare_meaning`, the
system under test, against the builder's independently written
`relation_from_observed`), in their completion set (two witnesses derived from the
pair against three values from the frozen corpus vocabulary), and in their domain
(A3 answers a pair with several one-sided absences; `gold_from_standard` raises
on one). They disagree on a pair whose stated side uses a value outside that
vocabulary: `gold_from_standard` finds every completion distinct from the mirror
and calls the pair determinate, A3 includes the mirror among the completions and
abstains. So the circularity is a fact about this corpus's coverage — every value
it states is drawn from the vocabulary, and no pair has two absences — and not a
fact about A3 being gold. A test exhibits the disagreeing pair.

**4.5 Nowhere else can score it either.** `INTACT_DERIVATION`,
`INTACT_HELDOUT_REAL` and `INTACT_HELDOUT_SYNTHETIC` contain no one-sided absence
at all, so A3 is A0 on every one of their pairs and its zero harm there is the
same structural zero `G6_HARM_A1` carried before amendment 001. The three probe
corpora have gold `UNRESOLVED` on all 48 cases, so any arm that abstains
unconditionally is right on all of them — A1, A2 and A3 all do, and are
indistinguishable there — and A0 answers none of the 48 correctly, so those
corpora carry no harm denominator either.

**4.6 The check is mechanical, not asserted.** The runner reads
`expected.authority.derivation.rule` off each corpus's own case records and
matches the marker `completion-invariance`; it counts each arm's exact agreement
with gold; and it computes a per-arm harm denominator, the pairs A0 answers
correctly that have a one-sided absence in them. No corpus id is hard-coded as
circular, so a corpus added later is classified by what it declares.

## 5. What the gates report

`G9_HARM_A3` (blocking). A3 destroys 0 correct answers on every intact corpus and
repairs 9 of A0's, and **no intact corpus supplies independent evidence for that
zero**. The gate runs `CANNOT_CHECK`. The repair is designed and unfalsified; it
is not demonstrated safe.

It is discharged by an intact corpus with one-sided absences whose gold is fixed
by adjudication, or by any rule that does not ask whether the completions agree,
containing at least one partially observed pair A0 answers correctly. Nothing in
this repository is such a corpus. Building one is not a construction task: under
partial observation the relation is genuinely underdetermined, so an independent
gold has to come from adjudicators rather than from a rule.

`G10_BENEFIT_A3` (non-blocking). A3's `ORION-13.OVERRESOLVED_UNRESOLVED_CASE`
violation rate is 0.0 on all three probe corpora, so it keeps the benefit A1 was
reaching for: it still abstains everywhere the frozen probe gold says abstention
is right. A1 and A2 score the same 0.0, so this is not evidence that A3 is better
than A1, and the gate carries the separation counts that say so. The only corpus
that separates A3 from A1 at all is `INTACT_HARM_SYNTHETIC`, which is the corpus
section 4 rules out.

## 6. What did not move

No threshold. No gate's subject. No arm's definition except by addition. No case
in any of the four corpora. `G5_MINING_YIELD`'s census is computed over the three
arms it was frozen over, and A3's own census — empty on every corpus — is
reported beside it rather than folded into it, so a published three-arm finding
does not silently become a four-arm one. Every number `G1`–`G8` reported under
amendment 001 is reproduced byte-for-byte, including `G6_HARM_A1`'s 27 / 21 / 12
and `G7_COST_A2`'s per-corpus costs.
