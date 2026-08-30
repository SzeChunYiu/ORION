# ORION-19: which comparator the claim should be stated against

Re-read of the paper's own frozen `evidence/D1_PAIRED_EFFECTS_V1.json` and
`P9_NR05_REPRESENTATION_HARDENING_RESULT_2026-08-23.json`. **No new outcome is accessed
and no run is performed.** `grants_authority: NONE`.

## The concern, and what the data says

ORION-19 was flagged as resting on very few independent task families with a comparator
that "partly behaves by construction". The second half is **confirmed by the paper's own
records**, and the first half is real but differently shaped than stated.

## Two of the three comparators are degenerate, by the paper's own flag

`P9_NR05` carries a `constant` field per arm:

| arm | accuracy | `constant` |
|---|---:|---|
| `TYPED_RELATIONAL` (primary) | **1.00** | false |
| `SERIALIZED_CANONICAL` | 0.75 | false |
| `TYPED_SERIALIZED_BAG` | 0.50 | **true** |

And `TRANSCRIPT_BAG` collapses entirely under mutation:

| mutations | accuracy | n |
|---:|---:|---:|
| 0 | 0.50 | 64 |
| 1 | **0.00** | 32 |
| 2 | **0.00** | 32 |

A comparator scoring zero on every mutated case is not measuring the same task.

## But there is a strong comparator, and the effect survives it

| comparator | accuracy | delta | typed-right / comp-right | exact McNemar |
|---|---:|---:|---|---:|
| `TRANSCRIPT_BAG` | 0.25 | 0.75 | 96 / **0** | 2.5e-29 |
| `TYPED_SERIALIZED_BAG` | 0.50 | 0.50 | 64 / **0** | 1.1e-19 |
| **`UNTYPED_PAIR`** | **0.906** | **0.094** | **12 / 0** | **0.00049** |

`UNTYPED_PAIR` scores **90.6%**. It is not degenerate, not constant, and not collapsing
under mutation — and the typed arm still beats it **12–0 with zero reversals**,
bootstrap 95% CI `[0.047, 0.148]` excluding zero.

## What follows for the manuscript

**The headline should be 0.094, not 0.75.** The large deltas are against comparators that
fail by construction; quoting them makes the result look stronger and is easier to attack.
The 0.094 against a 90.6% comparator is the defensible number, and the **12–0 with no
reversals** is what makes it interesting: the typed representation never loses a case the
untyped pair wins.

Stating it this way also pre-empts the reviewer objection rather than waiting for it.

## The remaining limitation, unchanged

All three paired tests treat **n = 128** as independent. The corpus is built by mutation
over a smaller base, so cases within a mutation family are not independent draws, and the
intervals are correspondingly narrower than the design supports. This is the same
inference-unit issue found in ORION-14, where the case-level interval was 5.48× too tight
at the correct clustering unit.

This note does **not** resolve it — the per-case family identifiers needed to cluster are
not in the frozen record. `CANNOT_CHECK_FAMILY_CLUSTERING__IDENTIFIERS_ABSENT`. Recording
it as an open limitation rather than leaving the n = 128 reading unqualified.

`D1_PAIRED_EFFECTS_V1.json` is already honest about its own status
(`POST_HOC_DERIVED_FROM_FROZEN_RAW_PREDICTIONS_NO_NEW_OUTCOME`, "not a preregistered new
endpoint"), and nothing here changes that.
