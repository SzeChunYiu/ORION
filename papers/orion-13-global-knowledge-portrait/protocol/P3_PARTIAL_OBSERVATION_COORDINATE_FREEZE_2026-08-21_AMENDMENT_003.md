# ORION-13 Partial-Observation Coordinate Freeze — Amendment 003

**Amends** `P3_PARTIAL_OBSERVATION_COORDINATE_FREEZE_2026-08-21.md`, its twin,
Amendment 001 and its twin, and Amendment 002 and its twin.
**Date** 2026-08-22. **Gate served** `G9_HARM_A3`. **Gates not touched**
`G6_HARM_A1`, `G5_MINING_YIELD`, `G8_NOVELTY`.
**Every amended document is left byte-identical.** This is a separate record with
its own parameter digest; the runner binds to this one while it is in force.

| field | value |
| --- | --- |
| amended parameters digest (2026-08-21) | `28d3e289d3dddddaef142e5756b77a825829836f1eadb900b80e49f985f73691` |
| amendment 001 parameters digest | `d4e97dcfc8a35d97656ec5eee60efc249a8e24dc682dd153c029fd9450b59ac8` |
| amendment 002 parameters digest | `9292414c63a50f0f31ad832b45a891a1eaf90584751f90f10362d941ad36c28e` |
| amendment 003 parameters digest | `a1057b6fe0d1d6fbe1f95c8e2202abe2936c913309aa549036a89a878a4d9b34` |
| runner | `src/orion/study/p3/partial_observation_probe.py` |
| corpus added | `INTACT_RECORD_GOLD` (`research/p3-partial-observation-record-gold-v1/`) |
| arms added | none |
| gates added | none |

## 1. What is being repaired

`G9_HARM_A3` ran `CANNOT_CHECK`, in the runner's own words:

> A3 destroyed 0 correct answers and repaired 9, but no intact corpus supplies
> independent evidence for that zero.

Two holes, one on each side of the gate. `INTACT_DERIVATION`,
`INTACT_HELDOUT_REAL` and `INTACT_HELDOUT_SYNTHETIC` state every coordinate on
both sides of every pair or on neither, so `A3` is `A0` on all of them and its
zero there is structural. `INTACT_HARM_SYNTHETIC` does have one-sided absences
but derives its gold by
`identity:observed-coordinate-precedence-with-completion-invariance`, which is
`A3`'s decision rule, so agreeing with that gold is `A3`'s definition restated.

Amendment 002 named what would discharge the gate and then judged it unbuildable:

> Building one is not a construction task: under partial observation the relation
> is genuinely underdetermined, so an independent gold has to come from
> adjudicators rather than from a rule.

That sentence is the error this amendment corrects.

## 2. The relation is not the inference

What a one-sided absence underdetermines is what a procedure **reading only the
projections** may conclude. It does not underdetermine the relation between the
two source statements. A `ScientificMeaningProjection` is ORION's *view* of a
source; when the extractor carries a coordinate from one source and misses it on
the other, the pair acquires a one-sided absence without either source having
changed. The ambiguity is in the extraction, not in the world.

This is not a new kind of gold for this study. `INTACT_DERIVATION` already
contains it. Its MUSE cases state neither `polarity` nor `modality` on either
side and their gold is `COMPATIBLE` anyway, because
`identity:upstream-coreference-edge` reads the annotator's coreference edge and
not the projections' coordinates. Amendment 003 adds the asymmetric version of
the same idea: gold anchored outside the projections, on pairs whose projections
are silent on one side only.

## 3. The corpus

`research/p3-partial-observation-record-gold-v1/`, built by
`src/orion/study/p3/partial_observation_record_gold_build.py`, 36 cases.

Each case is a **record pair**: two source statements, each stating all nine
identity coordinates, held in the frozen standard emitted beside the corpus. Gold
is the relation between the *records*, by `relation_from_records`, a precedence
rule written out in the builder rather than delegated to `compare_meaning`. An
**extraction loss** then blanks one coordinate on one side of the *projections*
the corpus ships. Gold does not move.

`relation_from_records` is defined only on records that state every coordinate
and raises on anything else. That is not a limitation to route around; it is the
property that makes the gold non-circular. The rule has no branch that reads an
absence, so it has no opinion about what an absence could have hidden, so it
cannot be `A3`'s criterion under another name. Declared rule:
`identity:frozen-source-record-relation`.

| stratum | n | construction | gold |
| --- | --- | --- | --- |
| `LA_LOSS_ON_AGREEING_RECORDS` | 9 | records state the same value of the lost coordinate | `COMPATIBLE` |
| `LD_LOSS_ON_DIFFERING_RECORDS` | 9 | records state different values of the lost coordinate | what that difference makes it |
| `LU_LOSS_A_HIGHER_COORDINATE_DECIDES` | 8 | records differ on `referent_ids`, which survives on both sides; the loss is below it | `DISTINCT_REFERENT` |
| `NL_NO_LOSS` | 10 | no extraction loss | the plain record relation |

**`LA` and `LD` are both present on purpose.** `compare_meaning` reads a
one-sided absence as agreement on eight coordinates and as a distinct value on
`modality`, so `A0` is right on the agreeing records for eight coordinates and on
the differing records for one. Which cells land in the harm denominator is
therefore fixed by `compare_meaning`'s own inconsistency, not by the builder.
Keeping one half of a coordinate's pair and dropping the other would be choosing
cases by their effect on the gate — the circularity of amendment 002 wearing a
different hat — and `verify()` refuses to emit a corpus missing either half.

`LU` is the stratum `A3` was built to get right and `A1` is built to get wrong.
Without it, "`A3` destroyed every answer it could have destroyed" would be
unfalsifiable.

## 4. What the gate now reports

`G9_HARM_A3` (blocking, threshold unchanged at 0). **FAIL.**

| | `INTACT_RECORD_GOLD` |
| --- | --- |
| cases | 36 |
| pairs with a one-sided absence | 26 |
| harm denominator (A0 right, absence present) | 17 |
| `A3` decisions changed | 18 |
| `A3` correct answers destroyed | **9** |
| `A3` wrong answers repaired | 0 |
| `A1` correct answers destroyed, same pairs | 17 |
| supplies independent evidence | **true** |

`G10_BENEFIT_A3`:
`corpora_separating_a3_from_a1_on_gold_not_derived_by_the_criterion_a3_uses` was
`[]` and is now `["INTACT_RECORD_GOLD"]`. On that corpus `A1` and `A3` differ on
8 pairs and `A3` is right on all 8. That is a comparison between two candidate
repairs on gold neither of them wrote. It is not evidence that either is safe.

## 5. The zero was unreachable, and the gate keeps its threshold anyway

`A3` returns `UNRESOLVED` on every pair whose one-sided absence is **decisive**
— whose admissible completions disagree about the relation. So on any such pair
whose gold is determinate and which `A0` already answers correctly, `A3`
necessarily destroys a correct answer. It follows that `G9`'s threshold of zero
can be met, on a corpus that has a harm denominator at all, only if every
partially observed pair `A0` answers correctly has an *undecisive* absence — that
is, only if the corpus's gold is determinate-and-matching exactly where the
completions agree. A gold with that extension **is** the completion-invariance
criterion, whatever rule string the corpus declares.

So `G9` as written is passable only circularly. That is the finding, and it is
the same shape as the caveat this study already carries about `A1` and `G6`, one
arm weaker:

> A1 returns UNRESOLVED on every pair with a one-sided absence, so on any such
> pair whose gold is determinate and which A0 already answers correctly it
> necessarily destroys a correct answer.

The threshold is **not** relaxed. A harm gate that moved its threshold when the
measurement came back negative would be the relabelling this repository keeps
finding. `G9` keeps its statement, keeps its zero, and fails.

## 6. The extensional circularity check

Amendment 002's circularity check read the derivation rule a corpus *declares*
and matched the marker `completion-invariance`. That catches an honest corpus
that says what it does. It does not catch a corpus that declares an innocent rule
and populates its partially observed pairs so that gold and the arm coincide.

`independent_harm_evidence` now also withholds on
`GOLD_COINCIDES_WITH_THE_ARM_WHEREVER_THE_ARM_CAN_FIRE`: the arm reproduces gold
on **every pair it can fire on**, i.e. on every pair with a one-sided absence.
The check is guarded against vacuity — a corpus with no such pair is already
withheld for having no harm denominator — and it can only refuse a pass, never
grant one.

The consequence that matters: editing `INTACT_RECORD_GOLD` into circularity, by
deleting the `LA` and `LD` strata on which its record-anchored gold and `A3`
disagree, returns `G9` to `CANNOT_CHECK`. It cannot turn it into a `PASS`.
`verify()` in the builder refuses the same edit one step earlier, and a test
exhibits both refusals.

## 7. What did not move

No threshold. No gate's subject: `G6_HARM_A1` still names `A1`, `G9_HARM_A3`
still names `A3`. No arm's definition. No case in the four corpora frozen before
this amendment. The 2026-08-21 freeze, its twin, amendment 001 and its twin, and
amendment 002 and its twin are all byte-identical.

**Numbers this amendment moves, and why that is not a relabelling.**
`G5_MINING_YIELD` part (a), `G6_HARM_A1` and `G7_COST_A2` are totals over the
intact corpora, so adding a fifth moves them:

| | amendment 002 | amendment 003 |
| --- | --- | --- |
| `G5` intact failures (A0/A1/A2) | 9 | 18 |
| `G6` pairs A1 could fire on | 27 | 53 |
| `G6` decisions A1 changed | 21 | 47 |
| `G6` correct answers A1 destroyed | 12 | 29 |

Every per-corpus row for the four earlier corpora is unchanged — `G6`'s
`INTACT_HARM_SYNTHETIC` row still reads 27 / 21 / 12 — and both gates keep their
thresholds and their `FAIL`. A gate reading "changes 0 decisions", or "every
failure has a discriminating coordinate", cannot be passed by a corpus added to
it; it can only be left alone or failed harder. That asymmetry is why supplying a
denominator is not a way of manufacturing a positive, and it holds for `G9`
exactly as amendment 001 argued it holds for `G6`.

## 8. External validity

`INTACT_RECORD_GOLD` is synthetic. Its source records are a frozen table the
builder emits, not an upstream expert corpus, because the upstream corpora the
public-reference builder draws on are not reachable from this environment. It
establishes what a decisiveness-aware abstention costs **when gold is anchored
outside the projections**, on pairs of this shape. It establishes nothing about
how often scientific extraction drops a coordinate on one side only. No accuracy,
false-merge, false-split or superiority number over it is evidence about ORION's
competence on scientific text.
