# P9-U-T3 freeze: the prospective S*(k,q) / C*(k,q) grid

- **Record id**: `P9_U_T3_FRONTIER_GRID_FREEZE`
- **Date frozen**: 2026-08-21
- **Status at freeze time**: **no cell of this grid has an outcome.** Not one language model has
  been run against any cell, in this session or anywhere in this repository. That is the property
  that makes this a prediction rather than a description, and it is the reason the freeze is worth
  writing today: a grid written after a crossing is visible is a drawing of the crossing.
- **Gate served**: `P9-U-T3` — *"scale/compute crossing is on-grid and prospectively defined"*
  (`src/orion/programme/superiority_terminals.py:420-426`, issue #662).
- **Ledger blocker being addressed**: "The critical scale S*(k,q) and critical inference budget
  C*(k,q) grid is not prospectively defined, so a crossing could not be shown to be on-grid rather
  than fitted."
- **Ledger unblock being executed**: "Freeze the relational-complexity × representation ×
  model-scale × inference-budget grid before outcomes, and preserve any null cell rather than
  fitting an exponent post hoc."
- **Machine-readable twin**: `P9_U_T3_FRONTIER_GRID_FREEZE_2026-08-21.json`, carrying the same
  parameter block and its sha256. The runner recomputes it and refuses to run on a mismatch.
- **Runner**: `python -m orion.study.p9.frontier_grid --repo-root . --output <path>`
  (`--outcomes <path>` to score an outcome file once one exists).

---

## 1. What this freeze is, and what it is not

This document defines a grid and the rules for reading a frontier off it. It **does not** execute
the grid, and it makes **no** claim that any crossing exists.

The environment cannot execute it: no open-weight checkpoint is present in this repository, and
this sandbox's proxy returns `403` to `CONNECT` for external providers. Stating that plainly is
the honest position; substituting a classical-learner capacity ladder for a model-scale ladder and
calling the result `S*` would be a weaker proxy dressed as the measurement, and is refused here.

So the runner's verdict on today's evidence is fixed in advance and is
`T3_GRID_DECLARED_NO_CELL_EXECUTED` → `CANNOT_CHECK`, with the denominator printed: **0 of 1344
declared cells have an outcome.** `P9-U-T3` remains **BLOCKED**. What this freeze removes from the
blocker is only its first half — the grid now exists, and it exists before any outcome — and the
runner exists to score it the moment cells are executed.

## 2. Coordinates

The performance surface named in `successor/P9_U_MANUSCRIPT.tex` is `Q(k, R, F, S, N, C)`. This
freeze fixes every axis.

### 2.1 `k` — relational complexity (4 levels)

`k` is the number of comparison coordinates that must be jointly examined to decide an instance's
label. It is not a proxy: D1's own generator already realises `k = 1` (single-coordinate
corruption) and `k = 2` (the double-corruption family), and the same generator extends to `k = 4`
and `k = 8` by widening the corrupted coordinate set.

`k ∈ {1, 2, 4, 8}`.

### 2.2 `R` — representation family (7 levels)

Five representation families plus two controls, taken from the manuscript's own list:

| `R` | what the model is shown |
|---|---|
| `FLAT_TEXT_SERIALIZATION` | canonical path=value token stream, values verbatim |
| `REVERSIBLE_INDEXED_SERIALIZATION` | the same stream with values replaced by a reversible per-instance index |
| `TYPED_TUPLE_SET` | typed coordinate → value mapping per side |
| `TYPED_GRAPH_STATE` | typed state with the dependency topology as an explicit graph |
| `QUERY_MATCHED_INTERFACE` | a query interface exposing one coordinate comparison per call |
| `LENGTH_ONLY_CONTROL` | cardinality and presence only — no values (the `H_LEN` arm of the T4 freeze, lifted to the successor grid) |
| `ARCHITECTURE_PRIOR_CONTROL` | flat text, but the comparison prior supplied in the system prompt rather than in the representation |

### 2.3 `F` and `S` — model family and scale (6 family/scale points)

| `F` | ladder (`S`, ascending, in parameters) |
|---|---|
| `QWEN2_5` | `0.5B` → `1.5B` → `3B` → `7B` |
| `LLAMA3_2` | `1B` → `3B` |

Two families, as `P9-U-T2` requires. Ladders are **declared here in full**; `S*` may only ever take
a value on its family's ladder.

### 2.4 `C` — inference budget (4 levels)

`C ∈ {1, 4, 16, 64}` sampled solutions per instance, aggregated by majority vote over verified
answers. `C` is counted in decode calls, and the representation-construction cost is charged to the
same accounting as required by the manuscript's matched-information section.

### 2.5 Domain block (2 levels)

`B ∈ {FORMAL_RELATIONAL, NON_FORMAL_PROCEDURAL}` — one formal and one non-formal procedural
domain, so that `P9-U-T5`'s block uncertainty is estimable from the same grid rather than assumed.

### 2.6 `N` — sample budget: fixed, and out of scope

`N` is **held at 4 in-context examples for every cell**. `N*(k,q)` is explicitly **not** estimated
by this freeze and no statement about it is licensed by any result over this grid. `P9-U-T3` names
`S*` and `C*` only.

### 2.7 `q` — verified quality targets

`q ∈ {0.70, 0.85, 0.95}`. `q` is not a cell axis; it is the level at which a frontier is read off
the executed surface.

### 2.8 Cell count

`4 (k) × 7 (R) × 6 (F,S) × 4 (C) × 2 (B) = 1344` cells. Each cell is scored over the **same**
frozen instance set for its `(k, B)` pair, so cells are paired and a crossing is a within-instance
comparison. The task instance is the scientific independent unit; decodes, seeds and remints are
technical repeats.

## 3. Frontier estimators, fixed now

For a series holding everything but `S` fixed:

> `S*(k, q | R, F, C, B) = min { S ∈ ladder(F) : Q(k, R, F, S, C, B) ≥ q }`,
> and `RIGHT_CENSORED` when no ladder point reaches `q`.

For a series holding everything but `C` fixed:

> `C*(k, q | R, F, S, B) = min { C ∈ {1,4,16,64} : Q(k, R, F, S, C, B) ≥ q }`,
> and `RIGHT_CENSORED` when no budget reaches `q`.

**On-grid rule.** A frontier value is *on-grid* iff it is a declared ladder point whose cell status
is `EXECUTED`. There is no interpolation between ladder points, no extrapolation beyond them, and
no fitted functional form anywhere in the definition of `S*` or `C*`. A frontier that is not
on-grid does not exist.

**Non-monotonicity is recorded, never smoothed.** If `Q ≥ q` at some ladder point and `Q < q` at a
larger one in the same series, the series is flagged `NON_MONOTONE`, the frontier is reported as
the first crossing point, and the flag travels with every downstream statement.

## 4. Crossing detection, fixed now

A **scale crossing** of `R1` over `R2` at `(k, q, F, C, B)` is declared iff

1. `S*(k,q | R1, F, C, B)` and `S*(k,q | R2, F, C, B)` are both **on-grid** (neither censored), and
2. `S*(R1) < S*(R2)` on the declared ladder, and
3. the Fisher exact two-sided test on the paired per-instance verified counts at `S*(R2)` — the
   scale where `R2` first reaches `q` — gives a Holm–Bonferroni-adjusted `p < 0.05`.

A **compute crossing** is the same statement with `C*` in place of `S*`.

**Multiplicity.** Holm–Bonferroni over the family of all crossing tests actually evaluated, family
size counted and reported. Declared here, before the family size is known.

**Null-cell preservation.** Every one of the 1344 declared cells must appear in the outcome file
with an explicit status from `{EXECUTED, NOT_RUN, INFEASIBLE_RESOURCE, INFEASIBLE_CONTEXT}`. A cell
missing from the outcome file makes the grid `CANNOT_CHECK` — silent absence is the failure this
rule exists to prevent. A `(k, q, R-pair)` combination in which either frontier is censored is
reported as `NO_CROSSING_DETECTABLE` and is **preserved as a result**, not dropped: the paper does
not promote a frontier by selecting only cells where a crossing occurs.

**Exponent discipline.** A power-law exponent may be reported only as a secondary description, only
with the functional form fixed here — ordinary least squares of `log(1 − Q)` on `log(S)` within one
`(k, R, F, C, B)` series with at least 3 `EXECUTED` points, reported with residual standard
deviation and `R²` — and may **never** be used to define `S*`, to fill a censored frontier, or to
declare a crossing.

## 5. Three-valued verdict, fixed now

| verdict string | outcome | when |
|---|---|---|
| `T3_GRID_DECLARED_NO_CELL_EXECUTED` | `CANNOT_CHECK` | zero declared cells have an outcome — **today's state** |
| `T3_GRID_INCOMPLETE` | `CANNOT_CHECK` | some declared cell is missing from the outcome file, or has no status |
| `T3_NO_EVALUABLE_CROSSING_TEST` | `CANNOT_CHECK` | every cell is accounted for, but no `(k,q,R-pair)` test had two on-grid frontiers — a crossing rate with denominator zero |
| `T3_OFF_GRID_CROSSING_CLAIMED` | `FAIL` | a claimed crossing rests on an interpolated, extrapolated, fitted or censored frontier |
| `T3_CROSSINGS_ON_GRID` | `PASS` | every declared cell is accounted for, at least one crossing test was evaluable, and every crossing claimed is between two on-grid, non-censored, `EXECUTED` ladder points |

`T3_CROSSINGS_ON_GRID` says the crossings are *on-grid*, which is all `P9-U-T3` asks. It says
nothing about whether a crossing was found: a fully executed grid with zero crossings is
`T3_CROSSINGS_ON_GRID` with `crossings_found = 0`, and that is a scientific result the freeze
commits in advance to reporting as one.

The runner exits `0` on `PASS`, `3` on `FAIL`, `4` on `CANNOT_CHECK`.

## 6. Outcome-file contract

A cell key is the tuple `(k, R, F, S, C, B)` rendered as
`k{k}|{R}|{F}|{S}|C{C}|{B}`. An outcome file is a JSON object:

```json
{
  "schema": "P9.UT3FrontierGridOutcomes.v1",
  "parameters_sha256": "<must equal the freeze twin's>",
  "cells": {
    "k1|TYPED_TUPLE_SET|QWEN2_5|1.5B|C4|FORMAL_RELATIONAL": {
      "status": "EXECUTED", "n_items": 128, "n_verified_correct": 96
    }
  }
}
```

`Q` is computed by the runner as `n_verified_correct / n_items` and is **not** read from the file:
a cell that reports a quality it did not compute from counts is not admissible. A cell with
`status != "EXECUTED"` must omit the counts, and contributes a censored point.

## 7. Anti-tuning commitments

1. Every axis level, ladder, threshold, `q` level, cell-key format, estimator, crossing rule,
   multiplicity correction and verdict string above is hashed into the JSON twin. The runner
   recomputes the digest and refuses to run on a mismatch.
2. The grid is fixed before any cell is executed. If it is ever changed, this file is superseded by
   a new dated freeze naming what changed and why, and any result produced under this version
   stands beside the new one.
3. No cell is dropped for being null, censored, or uninteresting.
4. No existing P9 result, receipt, protocol or evidence artifact is modified. Only new files are
   added.
