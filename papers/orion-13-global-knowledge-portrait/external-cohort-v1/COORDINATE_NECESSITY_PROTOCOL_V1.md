# ORION13.EXTERNAL_COORDINATE_NECESSITY.v1

**Status:** `DESIGN_ONLY__REFERENCE_OUTCOMES_NOT_OPENED_BY_THIS PACKET`  
**Scientific authority delta:** `NONE`

## Why this protocol is needed

The existing frozen derivation and confirmatory corpora are perfectly confounded with polarity: `{polarity}` is the unique reduct and the other six semantic coordinates are never required to separate opposite verdicts. That is a corpus limitation, not evidence that the other coordinates are useless.

The acquired external `bench23` payload is useful because negation is rare in its source ontologies, but rarity of negation alone does not establish coordinate necessity. The external successor therefore targets **matched-polarity exclusive witnesses** and keeps their adjudication separate from candidate construction.

## Coordinates

The semantic agreement coordinates are:

1. `construct_ids`
2. `measurement_ids`
3. `modality`
4. `polarity`
5. `predicate`
6. `referent_ids`
7. `temporal_context_ids`

This successor's anti-confounding priority is the six non-polarity coordinates.

## Exclusive witness definition

For coordinate `c`, an **exclusive witness pair** is a pair of independently adjudicated cases `(x,y)` such that:

- the gold merge/disposition verdicts of `x` and `y` are opposite;
- their agreement patterns are equal on every semantic coordinate except `c`;
- their agreement bits differ on `c`;
- for every non-polarity target coordinate, the polarity-agreement bit is held fixed within the witness pair.

### Necessity consequence

If an exclusive witness pair exists for `c`, then any deterministic merge rule that observes only the remaining coordinates must assign the same input representation to `x` and `y` and therefore cannot be correct on both. Thus `c` is necessary for universal correctness over any admissible case class containing that witness pair.

This is a logical counterexample statement. It is not a prevalence or average-effect claim.

## Outcome-blind acquisition

Candidate construction must not use the final merge/disposition labels.

Allowed pre-adjudication information:

- ontology/entity structure and typed coordinate values;
- source identity, licenses and immutable digests;
- candidate-pair structural constraints;
- the already-published fact that the old corpus is polarity-confounded.

Forbidden before candidate freeze:

- opening reference labels for the selected candidate pairs if those labels can determine inclusion;
- dropping candidates because their adjudicated relation is inconvenient;
- adding a coordinate-specific witness after seeing which coordinate lacks one.

If `bench23` reference alignments cannot supply negative/opposite relations without a closed-world assumption, absence from a reference alignment must **not** be treated as a gold negative. Such candidates require independent adjudication or another source with explicit negative/disjoint relations.

## Frozen candidate strata

For each non-polarity coordinate `c`, freeze at least **10 structurally eligible candidate witness pairs** before final adjudication, distributed across at least **3 source ontology/domain families** when available.

The 10 are acquisition targets, not guaranteed successful witnesses. After blinded adjudication:

- `>=5` valid exclusive witnesses for `c` across `>=3` source families: coordinate-level stress-test support;
- `1..4` valid exclusive witnesses: `BOUNDED_WITNESS_SUPPORT__INSUFFICIENT_BREADTH`;
- `0` valid exclusive witnesses: `NO_EXCLUSIVE_WITNESS_OBSERVED`;
- fewer than 10 eligible pre-frozen candidates because the source cannot instantiate the stratum: `CANNOT_CHECK_COORDINATE_STRATUM_UNAVAILABLE`.

No candidate replacement is permitted after adjudication begins.

## Independent adjudication

For any candidate whose gold relation is not already explicitly and independently encoded in the source:

- two adjudicators independently label the relation without seeing ORION's merge output;
- disagreements go to a pre-named third adjudicator or a frozen conflict rule;
- adjudicators receive the semantic content needed to judge the relation but not the target coordinate name when feasible;
- all disagreements and abstentions are retained.

Programme-generated labels do not count as external gold.

## Analysis

Run three analyses, in order:

1. **exclusive-witness audit** per coordinate;
2. **reduct/core recomputation** on the complete frozen external case set using the existing discernibility definition;
3. **policy comparison** only after 1–2 are frozen, with the same scoring rule and no coordinate-specific threshold tuning.

A coordinate may be called **stress-test necessary** only when an exclusive witness is independently adjudicated. A coordinate may be called **core on this external corpus** only if it lies in every minimal sufficient reduct of the complete frozen corpus.

Neither phrase implies population prevalence.

## Strongest possible outcomes

- `ALL_SEVEN_COORDINATES_HAVE_EXTERNAL_EXCLUSIVE_WITNESSES`: strongest universal-counterexample stress result; still not a prevalence claim.
- `SOME_COORDINATES_HAVE_EXTERNAL_EXCLUSIVE_WITNESSES`: mixed structural result; report exactly which coordinates.
- `NO_EXCLUSIVE_WITNESSES_OBSERVED`: adverse/negative result for this design; do not replace the cohort.
- `CANNOT_CHECK_*`: source/adjudication cannot establish the required relation.

## Relation to existing evidence

The old result—that polarity alone explains the measured advantage on the two frozen internal corpora—remains controlling for those corpora. This successor does not relabel it. Its purpose is to create the evidence shape that the old corpora lack.
