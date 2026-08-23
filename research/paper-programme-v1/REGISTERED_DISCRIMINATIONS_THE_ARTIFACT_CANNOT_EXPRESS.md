# A recurring defect class: registered discriminations the artifact cannot express

**Date:** 2026-08-23
**Authority:** `OUTCOME_BLIND_MEASUREMENT`. No protocol is relabelled, no gate evaluated, no
protected outcome read.

## The pattern

A protocol registers a discrimination — an attack, a coordinate, a contrast — and freezes a gate on
it. The artifact the protocol runs against **cannot express that discrimination at all**. The gate
then reports a number that is a property of the representation, not of the system under test.

The programme already has the vocabulary for this. The P9-U-T4 freeze says it outright: *an attack
cannot fail against a margin that was never measured.* What was missing was the measurement.

Four instances, each measured, each reproducible by a committed script.

## The instances

| Where | Registered discrimination | Measured opportunity |
|---|---|---|
| P9 · D1 v1.3 | `ORDER_PERMUTATION` attack | **0 of 128** cases changed; attacked dataset has the *same manifest digest* as base |
| P9 · D1 v1.3 | opportunity gate over 12 measurable cells | **8 of 12** cells at zero opportunity |
| P3 · public-reference atlas | `measurement_ids`, `temporal_context_ids` | **1 distinct value** across 64 projections, and it is `[]` |
| P3 · public-reference atlas | `referent_ids`, `construct_ids` | 24 and 12 distinct values, yet **0 of 32** cases where the two sides differ |

## What each instance teaches

**P9's order attack cannot change its own dataset.** `p1_method_realization._tuple` computes
`tuple(sorted({str(x) for x in values}))` — verbatim what D1 v1.3's representation contract names as
its `forbidden_normalization`. The attack reverses a sequence and the constructor sorts it back. The
`SEMANTIC_ORBIT` attack over the same machinery *does* change the data, so this is specific rather
than a broken harness. And an order-preserving feature family, built to the contract and round-trip
verified, still measures zero — which locates the loss upstream of every arm.

That normalization is programme-wide: **37 call sites in 30 modules**, spanning study lanes P1, P2,
P3, P5, P7 and P9 and the discovery, engine, knowledge, study and transfer layers. ORION's typed
coordinates are sets. That buys canonical form and order-insensitive digests, and it costs the
ability to express any claim depending on order or multiplicity.

**P3's inert coordinates are inert in two different ways, and the difference decides the fix.**
`measurement_ids` and `temporal_context_ids` carry no content — one distinct value, `[]`, in all 64
projections. But `referent_ids` carries **24** distinct values and `construct_ids` **12**, and
neither ever differs between the two sides of a case. They vary richly *across* cases and cannot
contrast *within* one.

This matters because the ledger's remedy is "freeze an atlas that varies the four coordinates". An
atlas giving `referent_ids` a different value in every case, and the same value on both sides of
each case, **satisfies that condition and reproduces every zero**. The success condition has to read
non-zero **within-case contrast**.

Two coordinates the ledger does not mention behave the same way: `modality` (2 distinct values,
never differs) and `predicate` (3 distinct, never differs).

## The no-alarm case

A measurement that called every coordinate unusable would be measuring nothing. `polarity` has 3
distinct values and **differs between the two sides in 6 of 32 cases** — the only *semantic*
coordinate in the artifact that contrasts. The three others that contrast — `projection_id`,
`source_id`, `source_span` — are identity and provenance fields, not meaning coordinates.

So the atlas has exactly one working semantic discriminator, and the frozen analysis's effect for it
reconciles with blanking it.

## Why this is a contribution and not just a defect list

Each of these is a **precise, checkable boundary on what the programme's representation can express**
— which is exactly what the cross-paper determination theorem says settles whether a question is
decidable at all: *which coordinates does the interface retain?* Answering it by measurement, per
artifact, is more useful than any single gate outcome, and it is the kind of scope statement a
referee should be able to read off the tree rather than reconstruct.

It also changes what work is worth doing. Three of the four instances would have been discovered
only by running an expensive campaign and reading a null — after the compute was spent.

## Reproduce

```bash
PYTHONPATH=src python papers/paper-09-structured-epistemic-learning/verify_order_permutation_is_a_noop_v1.py
PYTHONPATH=src python papers/paper-09-structured-epistemic-learning/derive_d1v1_3_attainability_v1.py
python papers/candidates/cross_paper_preservation_v2/check_set_normalization_boundary.py
python papers/paper-03-global-knowledge-portrait/measure_atlas_coordinate_opportunity.py \
  papers/paper-03-global-knowledge-portrait/gold/adjudicated/public-reference-v1.1-confirmatory/PUBLIC_REFERENCE_GOLD_V1.jsonl
```

Each exits non-zero when its finding stops holding, and each asserts a no-alarm case so that a
script which cries wolf on a healthy artifact fails its own check first.
