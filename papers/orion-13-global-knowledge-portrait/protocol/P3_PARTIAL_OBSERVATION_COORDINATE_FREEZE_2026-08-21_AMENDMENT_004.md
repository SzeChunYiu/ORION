# ORION-13 Partial-Observation Coordinate Freeze — Amendment 004

**Amends** `P3_PARTIAL_OBSERVATION_COORDINATE_FREEZE_2026-08-21.md`, its twin,
Amendment 001 and its twin, Amendment 002 and its twin, and Amendment 003 and its
twin.
**Date** 2026-08-22. **Gate served** `G9_HARM_A3`. **Gates not touched**
`G5_MINING_YIELD`, `G6_HARM_A1`, `G7_COST_A2`, `G8_NOVELTY`, `G10_BENEFIT_A3`.
**Every amended document is left byte-identical.** This is a separate record with
its own parameter digest; the runner binds to this one while it is in force.

| field | value |
| --- | --- |
| amended parameters digest (2026-08-21) | `28d3e289d3dddddaef142e5756b77a825829836f1eadb900b80e49f985f73691` |
| amendment 001 parameters digest | `d4e97dcfc8a35d97656ec5eee60efc249a8e24dc682dd153c029fd9450b59ac8` |
| amendment 002 parameters digest | `9292414c63a50f0f31ad832b45a891a1eaf90584751f90f10362d941ad36c28e` |
| amendment 003 parameters digest | `a1057b6fe0d1d6fbe1f95c8e2202abe2936c913309aa549036a89a878a4d9b34` |
| amendment 004 parameters digest | `2dc106eee03666ccec7ec7df53a96933814418a296e30be43ad1a81f2e089d21` |
| runner | `src/orion/study/p3/partial_observation_probe.py` |
| corpora added | none |
| arms added | **none** |
| gates added | none |
| thresholds moved | none |
| gate outcomes moved | none |

## 1. The question this amendment answers

Amendment 003 left `G9_HARM_A3` reading **FAIL**, with a number and no verdict on
what the number means:

> `A3` correct answers destroyed: **9**. `A3` wrong answers repaired: 0.

A failing harm gate reads as a defect of the arm it names — something a better
candidate would not do. So the natural next move is to look for that better
candidate: a fifth arm, `A4`, that destroys fewer than nine on `INTACT_RECORD_GOLD`
while still abstaining wherever the projections do not determine the relation
(`G10_BENEFIT_A3`'s 0.0 over-resolution rate on all three probe corpora).

**No such arm exists.** Not "was not found": cannot exist. Nine is a floor, not a
defect, and this amendment establishes the bound mechanically and writes it onto
the gate. It adds no arm, because an arm would be a search for something the
bound rules out.

## 2. The bound

### 2.1 What a candidate-visible rule may read

An arm is a function of the two `ScientificMeaningProjection` objects and nothing
else. Three things in a projection are not part of what the relation is about,
and no arm on record reads them:

* **bookkeeping** — `projection_id`, `source_id`, `source_span`. These say which
  record the projection was extracted from. Gold does not read them.
* **the identity of the opaque ids** — every rule in this study, including
  `compare_meaning` itself, reads `referent_ids`, `construct_ids`,
  `measurement_ids`, `temporal_context_ids`, `assumption_ids`, `attribution_id`,
  `discourse_relation` and `predicate` only for *equality*. A renaming applied
  consistently to both sides of a pair is invisible to all of them.
* **the orientation** — a meaning relation is symmetric. `compare_meaning(l, r)`
  and `compare_meaning(r, l)` are the same relation, and so is the relation
  between two source records.

`canonical_pair_form` strips exactly those three: it drops the bookkeeping,
relabels ids by first occurrence (which is a consistent renaming), and takes the
smaller of the two orientations. Two pairs with the same canonical form are the
same evidence.

Everything else in a projection is canonicalised rather than dropped, including
`argument_roles`, which no rule in this study reads. Ignoring a field would
report two pairs as the same evidence on the strength of a choice this module
made, and that is precisely how a ceiling gets overstated — so
`canonicalisation_field_census` computes the split against
`ScientificMeaningProjection` itself and reports any field it neither reads nor
names as bookkeeping under `uncovered`. It is empty, and a field added later
makes it non-empty instead of quietly widening the orbits.

The closed vocabularies are relabelled too, and this is the one step that is not
purely formal, so it is stated separately. `polarity` and `modality` are read by
every rule here only through inequality — `left.polarity != right.polarity`,
`left.modality != right.modality` — plus the `ASSERTED`/`ASSERTED` guard on the
contradiction branch. **The absent values are never relabelled**: `UNKNOWN` is
what a silence looks like, and moving it would erase the thing under study.
Relabelling the *stated* poles says only that a rule may not answer differently
according to which pole happened to survive extraction. Section 2.5 removes even
this step.

### 2.2 The orbits

Grouped by canonical form, `INTACT_RECORD_GOLD`'s 36 cases fall into **27
orbits**. On **9** of them gold is not constant — one for each identity
coordinate:

| coordinate | the two cases | gold | `A0` answers | `A0` is right on |
| --- | --- | --- | --- | --- |
| `referent_ids` | `LA` / `LD` | `COMPATIBLE` / `DISTINCT_REFERENT` | `COMPATIBLE` | `LA` |
| `construct_ids` | `LA` / `LD` | `COMPATIBLE` / `DISTINCT_CONSTRUCT` | `COMPATIBLE` | `LA` |
| `measurement_ids` | `LA` / `LD` | `COMPATIBLE` / `DISTINCT_MEASUREMENT` | `COMPATIBLE` | `LA` |
| `temporal_context_ids` | `LA` / `LD` | `COMPATIBLE` / `CONTEXTUAL_DIFFERENCE` | `COMPATIBLE` | `LA` |
| `attribution_id` | `LA` / `LD` | `COMPATIBLE` / `CONTEXTUAL_DIFFERENCE` | `COMPATIBLE` | `LA` |
| `discourse_relation` | `LA` / `LD` | `COMPATIBLE` / `CONTEXTUAL_DIFFERENCE` | `COMPATIBLE` | `LA` |
| `assumption_ids` | `LA` / `LD` | `COMPATIBLE` / `CONTEXTUAL_DIFFERENCE` | `COMPATIBLE` | `LA` |
| `polarity` | `LA` / `LD` | `COMPATIBLE` / `CONTRADICTORY` | `COMPATIBLE` | `LA` |
| `modality` | `LA` / `LD` | `COMPATIBLE` / `CONTEXTUAL_DIFFERENCE` | `CONTEXTUAL_DIFFERENCE` | `LD` |

The reason is one sentence: **the information that decides is exactly the value
the extraction destroyed.** An `LA` case silences a coordinate on which the two
records agreed; the `LD` case for the same coordinate silences one on which they
differed. Silence is silence, so the projections a reader is handed are the same
evidence — and the gold is not.

This is `INTACT_RECORD_GOLD`'s own construction argued back at it, not a defect
in it. The corpus is *built* to hold both directions of every coordinate, and
`verify()` refuses to emit it missing either half, precisely because dropping one
would be choosing cases by their effect on the gate. Holding both is what makes
the gold non-circular and what makes it non-functional in the projections. The
same property does both.

**No other corpus in this study has a single conflicting orbit.**
`INTACT_DERIVATION`, `INTACT_HELDOUT_REAL`, `INTACT_HELDOUT_SYNTHETIC`,
`INTACT_HARM_SYNTHETIC` and all three probe corpora have zero. That is not
reassurance; it is the reason `G9` could not be measured before amendment 003 and
the reason the bound is visible now.

### 2.3 What the orbits cost

Let `f` be any rule that is a function of the two projections and does not read
bookkeeping, id identity or orientation. `f` gives one answer to a whole orbit.
The runner checks this rather than assuming it:
`arm_is_constant_on_every_orbit` is `true` for `A0`, `A1`, `A2` and `A3` on every
corpus, so the canonicalisation is not stripping something an arm reads.

**(a) Accuracy.** On an orbit of size *n* whose most common gold covers *m*
members, `f` is wrong on at least *n − m*. Summed over `INTACT_RECORD_GOLD`:
**9 of the 36 cases cannot be answered correctly by any candidate-visible rule**,
and the reachable ceiling is **27 of 36**. `A0_orion_current` scores exactly 27.
It is already optimal. `A3` scores 18, `A1` and `A2` score 10.

**(b) Harm.** Each of the nine orbits carries `COMPATIBLE` on one member and a
separation on the other, and `A0` is right on exactly one member of each.
`MeaningRelation` has seven values: `COMPATIBLE`, `UNRESOLVED`, and the five
`NONMERGE_RELATIONS`. So on such an orbit `f` has three options and, because
those seven exhaust the type, no fourth:

1. answer `COMPATIBLE` — a **false merge** on the member whose gold separates;
2. answer any of the five separations — a **false split** on the member whose
   gold is `COMPATIBLE`;
3. answer `UNRESOLVED` — neither, and it destroys the one answer `A0` has right
   on that orbit.

A rule that commits no false merge and no false split must take option 3 on all
nine, and therefore destroys nine correct answers. **The harm floor is 9.** `A3`
destroys exactly 9.

Option 1 is what `A0` does on eight of the nine orbits and option 2 is what it
does on the ninth — which is why `A0` pays zero harm and commits, on
`INTACT_RECORD_GOLD`, the 8 false merges and 1 false split amendment 003 already
reports. Zero harm and zero over-resolution are not jointly available here. That
is the whole finding.

### 2.4 From "no false merge, no false split" to "keeps `A3`'s benefit"

The floor above is stated over the failure kinds. Tying it to `G10_BENEFIT_A3`
takes one more step, and the step is worth stating carefully because the obvious
version of it is wrong.

`G10` is measured on the three probe corpora, and **those share no canonical form
with `INTACT_RECORD_GOLD`** — they are redactions of atlases that populate
different coordinates, and the runner reports the disjointness. So `G10` *as
currently measured* does not by itself force abstention on the nine orbits. A
rule could return `UNRESOLVED` on all 48 probe cases and answer determinately on
the nine orbits, and score 0.0 on `G10` while destroying less than nine. That
rule would be reading the coordinate coverage of three particular atlases.

What forces it is the freeze's **probe-gold rule**, which is corpus-independent.
Take any `LD` case's *record* pair: it states every coordinate, its gold is a
non-merge, `compare_meaning` reproduces that gold, and it has no one-sided
absence — so `redactable_coordinates` admits it on exactly the coordinate the
records differ on, which is the freeze's own section 4.2 construction. Redact
that coordinate and the result **is** the orbit, carrying gold `UNRESOLVED` by
`freeze:probe-gold-is-unresolved-after-redaction`. All nine coordinates, checked
mechanically.

So the freeze already says abstention is right on exactly these pairs, and a rule
that answers determinately there is over-resolving by the study's own criterion —
it would score an over-resolution on a probe built from this corpus's own
records. That the shipped probe corpora do not happen to contain such a case is a
fact about which atlases exist here, not about the rule, and this amendment keeps
the two apart rather than letting the stronger claim borrow the weaker evidence.

### 2.5 The witness, in its sharpest form

The `LA`/`LD` collapse in section 2.2 needs a left/right swap, because the
builder alternates which side the loss falls on, and for `polarity` it needs the
closed-vocabulary relabelling as well. Neither step is load-bearing.
`undecidability_witness_cases(coordinate)` constructs, for each of the nine
coordinates, an `LA` case and an `LD` case that lose the **same** side. `LD`'s
surviving record keeps the base value and `LA`'s records both hold it, so the two
projection pairs come out **identical, value for value**. The only fields that
differ are `projection_id` and `source_span`, which carry the case digest.

Both are legal cases: same standard, same strata, same derivation rule, built by
the same `_case` and accepted by the same `validate_case` and the same
`STRATUM_CONTRACT`. The side a loss falls on is a free choice the standard does
not fix and the derivation rule does not read.

So for every one of the nine coordinates there is a pair of legal cases of this
corpus with *the same projections* and different gold, needing no swap, no
renaming and no argument. Gold is not a function of the projections. A rule that
told those two apart would be reading `projection_id`.

### 2.6 A held-out draw

The bound above was derived after the nine failing cases were known, which is the
condition under which a result is most likely to be an artifact of the cases it
was derived from. `RecordDraw`, `fresh_draw(seed)` and `held_out_corpus(seed)`
redraw everything the standard leaves free — the record vocabulary, which value
of each closed vocabulary each record takes, and which side each extraction loss
falls on — and re-run `verify()` on the result. The default draw emits the
shipped corpus byte for byte; a held-out draw is returned and never written.

Across seeds 7, 11, 23, 41 and 101 every number reproduces:

| | committed | seeds 7 / 11 / 23 / 41 / 101 |
| --- | --- | --- |
| undecidable orbits | 9 | 9 / 9 / 9 / 9 / 9 |
| ceiling (exact agreement) | 27 of 36 | 27 of 36, every seed |
| `A0` exact agreement | 27 | 27, every seed |
| harm floor | 9 | 9, every seed |
| `A1` correct answers destroyed | 17 | 17, every seed |
| `A3` correct answers destroyed | 9 | 9, every seed |

## 3. The arm that was tried, and why it is not registered

The principle was written down before it was measured, and it is stated over the
precedence order the record standard declares rather than over the nine failing
cases:

> **The shared observed frame.** The record standard decides a relation by
> reading the coordinates in precedence order and taking the first on which the
> two records differ. A coordinate stated on one side only is not evidence of a
> difference and not evidence of an agreement; it is not evidence. So restrict
> both projections to the coordinates observed on *both* sides and apply the
> precedence order to that frame. Where a higher-precedence coordinate survives
> on both sides and separates, it decides — which is the `LU` stratum, and the
> reason this rule is not `A1`. Where nothing that survives separates, the pair
> is compatible on everything the extraction preserved.

Measured, it is the best rule in the room on harm and the worst on benefit — and
it is barely distinguishable from `A0`. On `INTACT_RECORD_GOLD` it moves exactly
two of `A0`'s decisions, both on the `modality` orbit, where `compare_meaning`
reads the one-sided absence as a distinct value and this rule drops the
coordinate instead:

| | shared observed frame | `A3` | `A1` |
| --- | --- | --- | --- |
| correct answers destroyed on `INTACT_RECORD_GOLD` | **1** | 9 | 17 |
| wrong answers repaired | 1 | 0 | 0 |
| over-resolution rate, `PROBE_DERIVATION` | **1.0** | 0.0 | 0.0 |
| over-resolution rate, `PROBE_HELDOUT_REAL` | **1.0** | 0.0 | 0.0 |
| over-resolution rate, `PROBE_HELDOUT_SYNTHETIC` | **1.0** | 0.0 | 0.0 |

It destroys 1 instead of 9 by never abstaining at all: it answers a determinate
relation on all 48 probe cases, where the frozen probe gold is `UNRESOLVED`, so
`G10_BENEFIT_A3`'s threshold of 0.0 is missed by the maximum possible margin. On
every one of the nine orbits it takes option 1 of section 2.3 — answer
`COMPATIBLE` — which is to say it is `A0` with the `modality` absence read
merge-ward instead of separation-ward. It surrenders the entire benefit `A3`
exists for.

Both halves reproduce on the held-out draws of section 2.6: 1 destroyed and 1
repaired on every seed, and a determinate answer on every case of every draw.

This is the trade-off, not a near miss, and it is what the bound predicts: the
eight units of harm it saves relative to `A3` are bought with 48
over-resolutions, one per probe case, and by the bound every unit of harm below
9 has to be bought the same way. **It is not registered as an arm.** Registering a rule that fails the benefit gate outright
in order to put a smaller number beside `A3`'s would be exactly the relabelling
this study keeps refusing.

## 4. What the gate now reports

`G9_HARM_A3` (blocking, threshold unchanged at 0). **FAIL**, unchanged.

| field | value |
| --- | --- |
| `correct_answers_destroyed` | 9 |
| `harm_floor_for_any_candidate_visible_rule` | **9** |
| `a3_harm_is_at_the_floor` | **true** |
| `identifiability_ceiling.INTACT_RECORD_GOLD.n_undecidable_orbits` | 9 |
| `identifiability_ceiling.INTACT_RECORD_GOLD.max_exact_agreement_reachable_by_a_candidate_visible_rule` | 27 of 36 |
| `identifiability_ceiling.INTACT_RECORD_GOLD.arms_at_the_ceiling` | `["A0_orion_current"]` |

The threshold is **not** relaxed and the gate is **not** repointed. A harm gate
that moved its threshold on learning that the floor is above zero would be the
relabelling this repository keeps finding, and the floor is not a licence: it
says nothing about whether abstaining is the right call, only that a rule which
abstains where the evidence is genuinely ambiguous must pay for it here. What the
floor changes is what the `FAIL` *means* — not a defect of `A3` awaiting a fifth
arm, but the price of deciding under an extraction that destroyed the deciding
value.

The three earlier structural findings stand and are now one family:

* `A1` must destroy a correct answer on any partially observed pair with
  determinate gold that `A0` answers correctly (amendment 001, `G6`);
* `A3` must destroy one on any such pair whose absence is *decisive*
  (amendment 003, `G9`);
* **no candidate-visible rule at all** can avoid destroying one on a pair whose
  orbit carries conflicting gold, without committing a false merge or a false
  split instead (amendment 004).

Each is stronger than the last, and each is a fact about the gate and the
evidence rather than about the cases.

## 5. What did not move

No threshold. No gate statement. No gate subject. No gate outcome. No arm — the
bodies of `A0`, `A1`, `A2` and `A3` are unchanged line for line and no `A4` is
registered. No corpus and no
case: `record_gold_cases()` with no argument still emits
`research/p3-partial-observation-record-gold-v1/cases.jsonl` byte for byte, and
`standard_document()` still emits the shipped standard byte for byte. The
2026-08-21 freeze, its twin, and amendments 001, 002 and 003 and their twins are
all byte-identical.

Every number the runner published under amendment 003 it publishes under
amendment 004. The amendment adds reported fields — a ceiling block per corpus,
a floor on `G9` — and moves nothing.

## 6. External validity

The bound is a bound over `INTACT_RECORD_GOLD` and its held-out redraws, which
are synthetic. It says that on pairs of *this shape* — two source records that
state every coordinate, one coordinate destroyed on one side by extraction — the
relation is not recoverable from the projections, and it quantifies what that
costs any rule. It says nothing about how often scientific extraction drops a
coordinate on one side only, and no accuracy, false-merge, false-split,
superiority or optimality number over this corpus is evidence about ORION's
competence on scientific text. In particular, "`A0` is optimal here" is a
statement about 36 synthetic cases and about a ceiling those cases impose; it is
not a claim that `compare_meaning`'s absence reading is right, and section 2.3
says in the same breath what `A0` pays for its optimality: 8 false merges and 1
false split.
