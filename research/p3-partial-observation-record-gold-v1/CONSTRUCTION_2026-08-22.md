# P3 partial-observation record-gold corpus — construction

**Atlas id** `partial-observation-record-gold-v1`
**Protocol id** `P3.partial-observation-record-gold-corpus.v1`
**Builder** `src/orion/study/p3/partial_observation_record_gold_build.py`
**Gate served** `G9_HARM_A3` (blocking) of
`papers/paper-03-global-knowledge-portrait/protocol/P3_PARTIAL_OBSERVATION_COORDINATE_FREEZE_2026-08-21_AMENDMENT_003.md`
**Derivation rule** `identity:frozen-source-record-relation`
**Cases** 36. **Synthetic.**

## 1. Why this corpus exists

`G9_HARM_A3` asks whether `A3_decisive_absence_only` — the arm that abstains only
where the admissible completions of a one-sided absence disagree — destroys
answers `compare_meaning` already gets right. Before this corpus the gate ran
`CANNOT_CHECK`, with two different holes:

* `INTACT_DERIVATION`, `INTACT_HELDOUT_REAL` and `INTACT_HELDOUT_SYNTHETIC` state
  every coordinate on both sides of every pair or on neither. `A3` is `A0` on all
  of them; its zero harm there is structural.
* `INTACT_HARM_SYNTHETIC` has one-sided absences, but its gold is derived by
  `identity:observed-coordinate-precedence-with-completion-invariance` — abstain
  where the completions disagree. That is `A3`'s decision rule. Agreeing with
  that gold is `A3`'s definition restated, and the probe correctly refuses to
  read a number off it.

## 2. The idea: gold anchored to the record, not to the projection

Amendment 002 judged the discharging corpus unbuildable because "under partial
observation the relation is genuinely underdetermined". That is true of the
*inference* and false of the *relation*.

A `ScientificMeaningProjection` is ORION's view of a source statement. When the
extractor carries a coordinate from one source and misses it on the other, the
pair acquires a one-sided absence **without either source having changed**. The
ambiguity is in the extraction. The relation between the two statements is fixed
by the statements.

The study already contains gold of this kind. The MUSE cases of
`INTACT_DERIVATION` state neither `polarity` nor `modality` on either side, and
their gold is `COMPATIBLE` anyway, because `identity:upstream-coreference-edge`
reads the annotator's coreference edge rather than the projections' coordinates.
This corpus is the asymmetric version of the same construction.

Every case is therefore a **record pair** plus an **extraction loss**:

1. two source records, each stating all nine identity coordinates, drawn from the
   frozen table in `PARTIAL_OBSERVATION_RECORD_STANDARD.json`;
2. gold = `relation_from_records(left_record, right_record)`;
3. the shipped projections = those records with one coordinate blanked on one
   side.

Both records travel with the case, under
`partial_observation_record_gold.left_record` / `.right_record`, so a reader can
recompute gold without the builder.

## 3. Why the gold rule is not A3's rule

`relation_from_records` is **defined only on records that state every
coordinate** and raises `RecordCorpusError` on anything else. It has no branch
that reads an absence, so it has no opinion about what an absence could have
hidden, so it cannot be a completion-invariance criterion under another name.
Gold is attached to the record; the extraction loss is applied afterwards and
never reaches the rule.

The rule is written out in the builder rather than delegated to `compare_meaning`
so that gold is not defined by the system under test, and
`rule_agreement_on_records` checks the two against each other on all 36 record
pairs — where both are defined — so that the corpus is not measuring a rule ORION
does not have. They agree on 36 of 36.

## 4. The strata

| stratum | n | construction | gold |
| --- | --- | --- | --- |
| `LA_LOSS_ON_AGREEING_RECORDS` | 9 | records state the same value of the lost coordinate, agree everywhere else | `COMPATIBLE` |
| `LD_LOSS_ON_DIFFERING_RECORDS` | 9 | records state different values of the lost coordinate, agree everywhere else | what that difference makes it |
| `LU_LOSS_A_HIGHER_COORDINATE_DECIDES` | 8 | records differ on `referent_ids`, which survives on both sides; the loss is of a lower-precedence coordinate | `DISTINCT_REFERENT` |
| `NL_NO_LOSS` | 10 | no extraction loss; nine cases whose records differ on one coordinate each, one whose records agree everywhere | the plain record relation |

`LA` and `LD` are a census: one case per coordinate in each, both directions,
nine coordinates. `LU` covers every coordinate that has one strictly above it in
the precedence order, i.e. all but `referent_ids`. `NL` is the control an
observedness-sensitive arm must not fire on.

## 5. Both directions of every coordinate, on purpose

`compare_meaning` reads a one-sided absence as **agreement** on eight coordinates
and as a **distinct value** on `modality`. So:

* on `LA` (records agree), `A0` lands on the record's answer for the eight
  merge-ward coordinates and misses it on `modality`;
* on `LD` (records differ), `A0` misses the record's answer for the eight
  merge-ward coordinates and lands on it for `modality`.

Which cells end up in the harm denominator is therefore fixed by
`compare_meaning`'s own eight-to-one inconsistency, not by the builder — **but
only while both cells exist**. Keeping a coordinate's `LA` case and dropping its
`LD` case, or the reverse, would be choosing cases by their effect on the gate:
that is the circularity `G9` exists to catch, wearing a different hat.
`coordinate_balance` counts the cells and `verify` refuses to emit a corpus
missing either half of any coordinate's pair.

## 6. What the build measures

Measured by `construction_receipts` and reported in `BUILD_REPORT.json`; the
probe is the authority for the gate numbers and reproduces these.

| | |
| --- | --- |
| cases | 36 |
| pairs with a one-sided absence | 26 |
| harm denominator (`A0` right **and** an absence present) | 17 |
| `A1_observedness_asymmetric` correct answers destroyed | 17 |
| `A3_decisive_absence_only` correct answers destroyed | **9** |
| pairs `A1` destroys and `A3` spares | 8 |
| `A3` reproduces gold on every pair it can fire on | **false** |
| gold coincides with completion-invariance | **false** (18 pairs off the diagonal) |

The nine `A3` destroys are the eight merge-ward coordinates of `LA` plus
`modality` of `LD` — exactly the cells where `A0`'s reading of a silence happens
to land on the record's answer and the loss is decisive. `A3` spares the eight
`LU` pairs that `A1` destroys, which is what `A3` was built to do and the first
time in this study that it is measured on gold neither arm wrote.

## 7. The zero was not reachable

`A3` returns `UNRESOLVED` on every pair whose one-sided absence is decisive. So
on any such pair whose gold is determinate and which `A0` answers correctly, `A3`
*must* destroy a correct answer. `G9`'s threshold of zero can therefore be met
only by a corpus whose partially observed pairs have determinate gold exactly
where the completions agree — which is the completion-invariance criterion in
extension, whatever rule it declares.

This is reported, not repaired. The corpus does not tune itself towards the
threshold and the gate does not move the threshold towards the corpus. `G9`
fails.

## 8. Guards the builder refuses on

`verify()` raises `RecordCorpusError` rather than emitting the corpus when:

* a stratum's contract is broken (number of one-sided absences, gold
  determinacy, or whether the loss is decisive);
* a shipped gold is not the relation between the case's own records;
* the corpus has no one-sided absence at all;
* a coordinate is present on agreeing records but not on differing records, or
  the reverse;
* every partially observed pair with determinate gold has an *undecisive* loss —
  i.e. the corpus's gold coincides with `A3`'s criterion, whatever it declares;
* no partially observed pair has an undecisive loss, so `A1` and `A3` are
  indistinguishable here;
* no partially observed pair is one `A0` answers correctly, i.e. there is no harm
  denominator;
* `A3` reproduces gold on every pair it can fire on, so its harm would follow
  from a perfect score by arithmetic;
* the derivation rule and `compare_meaning` disagree on any record pair;
* a shipped projection is not its record minus the declared coordinate;
* this module and the probe disagree about which value means "absent";
* the measured absence reading does not match the freeze's declared table.

Every one of those can only make the corpus harder to build. None of them checks
that `A3` comes out well; the two that mention `A3` refuse a corpus on which `A3`
*cannot be measured*, and both refuse in the direction that withholds a pass.

## 9. Identifiability

`shape_invariants` pins every construction-level feature constant across all 36
cases: one `case_id` length and prefix, one `projection_id` length, one
`source_span` length, one source record, one authority kind, one derivation rule,
one predicate. The `case_id` digest is all-digit and fixed-width for the reason
`p3_coordinate_necessity_build` uses one: a hex digest's leading non-digit run
varies across cases, which an identifiability probe reads as a construction cue
for whatever the digest correlates with.

## 10. External validity

The cases are **synthetic**. The source records are a frozen table this builder
emits, not an upstream expert corpus, because the upstream corpora the
public-reference builder draws on are not reachable from this environment.

This corpus can establish what a decisiveness-aware abstention costs **when gold
is anchored outside the projections**, on pairs of this shape. It cannot
establish that extraction drops a coordinate on one side only at any particular
rate in public scientific corpora, and it may not be substituted for the
public-reference atlas in any external-validity claim. No accuracy, false-merge,
false-split or superiority number over it is evidence about ORION's competence on
scientific text.

## 11. Reproduce

```
python -m orion.study.p3.partial_observation_record_gold_build --repo-root . --write
python -m orion.study.p3.partial_observation_probe --repo-root . \
    --output papers/paper-03-global-knowledge-portrait/evidence/partial-observation-t5/P3_PARTIAL_OBSERVATION_RESULT_2026-08-22_AMENDMENT_003.json \
    --probe-output papers/paper-03-global-knowledge-portrait/evidence/partial-observation-t5/PROBE_CASES_2026-08-22_AMENDMENT_003.jsonl
```

The probe exits 3: `G5_MINING_YIELD`, `G6_HARM_A1`, `G8_NOVELTY` and
`G9_HARM_A3` all fail, and the study's job was to replace `CANNOT_CHECK`s with
demonstrated failures rather than to produce a pass.
