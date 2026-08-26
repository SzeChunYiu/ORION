# P3 Partial-Observation Coordinate Freeze — Amendment 001

**Amends** `P3_PARTIAL_OBSERVATION_COORDINATE_FREEZE_2026-08-21.md` and its twin
`P3_PARTIAL_OBSERVATION_COORDINATE_FREEZE_2026-08-21.json`.
**Date** 2026-08-22. **Gate served** `G6_HARM_A1`.
**The amended document and its twin are left byte-identical.** This is a separate
record with its own parameter digest; the runner binds to this one while it is in
force.

| field | value |
| --- | --- |
| amended parameters digest | `28d3e289d3dddddaef142e5756b77a825829836f1eadb900b80e49f985f73691` |
| amendment parameters digest | `d4e97dcfc8a35d97656ec5eee60efc249a8e24dc682dd153c029fd9450b59ac8` |
| runner | `src/orion/study/p3/partial_observation_probe.py` |
| corpus builder | `src/orion/study/p3/partial_observation_harm_build.py` |
| corpus | `research/p3-partial-observation-harm-v1/` |

## 1. What is being repaired

The runner reported gate `G6_HARM_A1` as `CANNOT_CHECK`, in its own words:

> A1 cannot fire on any intact pair because no intact pair has a one-sided
> absence; 0 changes is a structural zero, not a demonstration of safety.

That report is correct and section 7.2 of the amended freeze pre-declared it. The
gate exists to establish that the candidate repair `A1_observedness_asymmetric`
does not break cases the current rule gets right. With no intact pair carrying a
one-sided absence, A1 cannot fire on one, so the gate's zero measures the corpora
and not the arm.

## 2. Whether the zero is definitional — the question this amendment turns on

If a one-sided absence were excluded by what "intact" means, the zero would be
correct by construction, the honest deliverable would be to say so, and this
amendment would not exist. It is not excluded. Four independent pieces of
evidence, none of which depends on the others:

1. **The type places no constraint across a pair.**
   `ScientificMeaningProjection` is a per-source object. Observedness of a
   coordinate is a property of one projection. Nothing in the dataclass, in
   `projection_from_dict`, or in `validate_case` relates the observedness of a
   coordinate on the left to its observedness on the right. A corpus of
   symmetrically observed pairs is one corpus the type admits, not the only one.

2. **`compare_meaning` carries branches reachable only on a one-sided absence.**
   `_same_or_empty`, the three `left.X and right.X` guards on `attribution_id`,
   `discourse_relation` and `assumption_ids`, and the `Polarity.UNKNOWN` test all
   have inputs that reach them **only** when a coordinate is stated on one side
   and not the other. Section 1.2 of the amended freeze is built on the
   observation that those branches disagree with each other about what an absence
   means — eight read it as agreement, one as a distinct value. Code that
   disagrees with itself on inputs that cannot exist would be a different and
   smaller finding than the one the freeze makes. The freeze's own diagnosis
   presupposes the inputs are reachable.

3. **The study already constructs such pairs and treats them as pairs.** Every
   probe case is a pair with exactly one coordinate observed on one side only.
   They are scored by the same `compare_meaning`, classified by the same
   `classify_identity_decision`, and counted in the same guard denominators as
   intact cases. The probe corpora are redactions rather than authored cases, but
   that is a fact about their provenance, not about their admissibility.

4. **The census says the zero is a construction artifact of three corpora.** Per
   coordinate, across all 120 pairs of the three corpora, every count of "observed
   on exactly one side" is zero, and the counts of "observed on both" and
   "observed on neither" partition each corpus into whole strata: 32/0/0 for
   `referent_ids`, 19/0/13 for `construct_ids`, `polarity` and `modality` on the
   confirmatory atlas, and so on. Both sides of every pair were populated by one
   template. That is a property of the builders, not of the concept.

So a one-sided absence can legitimately occur in an intact corpus, and the
amendment supplies one.

## 3. What is added

A fourth intact corpus, `INTACT_HARM_SYNTHETIC`, at
`research/p3-partial-observation-harm-v1/cases.jsonl`. 33 cases, four strata,
gold derived from a frozen table by one stated rule that does not call
`compare_meaning`. Its construction is documented in
`research/p3-partial-observation-harm-v1/CONSTRUCTION_2026-08-22.md` and its
receipts in `BUILD_REPORT.json`.

| stratum | n | one-sided absence | gold | what it is for |
| --- | --- | --- | --- | --- |
| `H_UNDECISIVE_ABSENCE` | 12 | 1 per pair, on a coordinate below the deciding one | determinate | the pairs an abstain-on-asymmetry rule can damage |
| `D_DECISIVE_ABSENCE` | 9 | 1 per pair, on the only coordinate that could separate | `UNRESOLVED` | one cell per coordinate: the absence-reading defect on authored cases |
| `S_INCOMPARABLE` | 6 | 1 per pair | `UNRESOLVED` | pairs A1 fires on harmlessly |
| `C_FULLY_OBSERVED` | 6 | none | determinate | pairs A1 must leave alone |

## 4. Why supplying this denominator cannot manufacture a positive

`G6_HARM_A1` reads *"A1 changes **0** decisions on the intact corpora."* Adding a
corpus to a gate of that shape can only leave it where it stands or make it fail.
There is no corpus, adversarial or friendly, that turns it into a pass. The
threshold is not touched, no case is edited, no check is loosened, and the three
corpora frozen on 2026-08-21 are unchanged down to the byte. The only thing that
changes is that the gate now has something to measure.

## 5. Changes to the runner, exhaustively

1. `INTACT_SOURCES` gains `INTACT_HARM_SYNTHETIC`. `INTACT_ORDER` gains it last.
2. `PROBE_OF` does **not** gain it, and `run_campaign` only builds a probe for a
   corpus that has an entry there. The redaction of section 4.2 is defined on a
   parent with no one-sided absence; redacting a parent that already has one
   yields a probe case with two, which C2 rejects, and the campaign would abort on
   `CONSTRUCTION_PRECONDITION_FAILED` rather than report the malformed case.
3. `redactable_coordinates` gains the same condition on the case, as
   defence-in-depth: a parent with a one-sided absence is not redactable. This is
   a **no-op on the three probed corpora** — their one-sided-absence census is
   zero — and `build_probe` still emits exactly 12, 8 and 28 cases.
4. `G6_HARM_A1` additionally reports `correct_answers_destroyed` and a per-corpus
   breakdown. No threshold, arm, coordinate, absent value or probe gold moves.
5. `SYMMETRIC_INTACT_ORDER` and `PARTIALLY_OBSERVED_INTACT_ORDER` name the two
   groups, so assertions that pin the symmetric corpora's properties stay attached
   to the corpora they are true of.

## 6. Outcome, recorded after the run

| gate | before | after |
| --- | --- | --- |
| `G1_CONSTRUCTION` | PASS | PASS |
| `G2_CHANNEL_OPENED` | PASS | PASS |
| `G3_FAILURE_ON_REAL_CASES` | PASS (12/12, rate 1.0) | PASS (12/12, rate 1.0) |
| `G4_HELD_OUT` | PASS | PASS |
| `G5_MINING_YIELD` | CANNOT_CHECK | **FAIL** |
| `G6_HARM_A1` | CANNOT_CHECK, vacuous | **FAIL**, not vacuous |
| `G7_COST_A2` | PASS | PASS |
| `G8_NOVELTY` | FAIL by construction | FAIL by construction |
| overall | FAIL | FAIL |

Verdicts are unchanged: `CHANNEL_OPENED_FAILURE_DEMONSTRATED`,
`FAILURE_CARRIES_TO_HELDOUT_STRATA`,
`T5_NOT_DISCHARGED__CANDIDATE_IS_NOT_A_NEW_IDENTITY_AXIS`. Every number over
`INTACT_DERIVATION`, `INTACT_HELDOUT_REAL`, `INTACT_HELDOUT_SYNTHETIC` and all
three probe corpora is byte-identical to the 2026-08-21 run.

### 6.1 `G6_HARM_A1` — A1 is not safe, and this is the measurement that says so

A1 could fire on **27** intact pairs. It moved **21** decisions and destroyed
**12** correct answers. The 12 are `H_UNDECISIVE_ABSENCE`: pairs whose answer is
determined by a coordinate stated on both sides, which A0 already answers
correctly, and on which A1 abstains because some *other*, non-deciding coordinate
is missing on one side. The 9 further changes are `D_DECISIVE_ABSENCE`, where A1's
abstention replaces an A0 answer that was itself wrong; those are changes and are
counted as such, but they destroy nothing.

This is a real harm finding and is reported as one. **The gate fired, and the
exercise succeeded.**

### 6.2 The finding generalises past this corpus

A1 returns `UNRESOLVED` on *every* pair with a one-sided absence. So on any such
pair whose gold is determinate and which A0 already answers correctly, A1
necessarily destroys a correct answer. `G6_HARM_A1` can therefore be passed
non-vacuously only by a corpus in which **no** partially observed pair has a
determinate answer. That is a property of the gate and the arm, not of the cases
chosen here, and it means the pre-declared vacuity of section 7.2 was structural
in a second, sharper sense than the one recorded there.

### 6.2.1 What the corpus cannot decide

A rule that abstained only where the absence is **decisive** would not pay A1's
cost on the twelve. That is the obvious next candidate and this corpus cannot
score it: gold here is *defined* by that rule, so the comparison is circular by
construction. Naming it is fair; measuring it needs a corpus whose gold does not
come from it.

A1 and A2 are also indistinguishable here — identical decision kinds on all 33
cases, because every pair with a one-sided absence also has an absence of the kind
A2 fires on, and the six fully observed pairs have neither. The corpus separates
abstention from harm, not the two abstention rules from each other; A2's distinct
cost stays visible only on the three symmetric atlases, where `G7_COST_A2` is
unchanged.

### 6.3 `G5_MINING_YIELD` part (a) — the empty yield was incidental, not structural

Part (a) had no failures to mine. Two reasons stacked. All three arms can err only
by abstaining, and abstention where gold is determinate is
`ABSTAINED_ON_SEPARABLE` / `ABSTAINED_ON_MERGEABLE`, neither of which is one of
the four failure kinds; so the only possible intact failure was one `A0` itself
commits. And `A0` answers every symmetric intact pair correctly, which is the
published P3 negative. Neither reason survives a partially observed intact pair:
on `D_DECISIVE_ABSENCE`, A0 commits 8 `MERGED_WHERE_GOLD_UNRESOLVED` and 1
`SEPARATED_WHERE_GOLD_UNRESOLVED`. Part (a) now reports 9 failures, all 9 with an
empty discriminating-coordinate set, and fails.

That `FAIL` is the study's own thesis restated, not a contradiction of it: nothing
in the nine coordinates can separate those pairs, because what is missing is a
third value on an existing axis. `G8_NOVELTY` already says so, `G5` is
non-blocking, and the verdict rule that would have read part (a) as
`NO_NEW_COORDINATE_DEMANDED_BY_ANY_FAILURE_ON_RECORD` requires a `PASS` and still
does not fire.

### 6.4 What is measured on the intact side for the first time

- `P3.OVERRESOLVED_UNRESOLVED_CASE` has a denominator on an **intact** corpus: 15
  opportunities, 9 violations by A0, rate 0.6. On the three symmetric corpora it
  remains `CANNOT_CHECK` at 0 of 0, unchanged.
- The absence-reading split of section 1.2 is measured on authored cases rather
  than quoted: 8 coordinates merge-ward, 1 (`modality`) separation-ward, one cell
  per coordinate, matching the freeze's declared table in all nine cells.

## 7. Claim scope, unchanged and extended

`PARTIAL_OBSERVATION_OF_FROZEN_ATLASES_ONLY` still governs the probe. The added
corpus is **synthetic** and carries the same bound: it establishes what
`compare_meaning` does with a one-sided absence and what an abstain-on-asymmetry
repair costs on pairs of that shape. It establishes nothing about how often
scientific sources state a coordinate on one side only. It is not an accuracy
benchmark, may not be substituted for the public-reference atlas in any
external-validity claim, and no accuracy, false-merge, false-split or superiority
number over it is evidence about ORION's competence on scientific text.

## 8. What this amendment does not do

- It does not edit any adjudicated case, any frozen atlas, or the
  `coordinate-necessity-v1` corpus. That corpus's own freeze forbids adding cases
  to it that would move its ablation and abstention denominators, and adding
  partially observed cases there would have done both while breaking its recorded
  `cases_hash` and its identifiability results. The new cases are a separate
  corpus with its own identity, which is the same move that freeze made when it
  needed a denominator the frozen atlases could not supply.
- It does not relax a threshold, widen an opportunity definition, or convert an
  honest zero-denominator report into a pass. `over_resolution` still reports "0
  opportunities" on the three symmetric intact corpora, and `false_merge` still
  reports "0 opportunities" on every probe corpus. Those remain
  `CANNOT_CHECK`.
- It does not discharge P3-U-T5. `G8_NOVELTY` fails by construction and the
  verdict is unchanged.
