# The QG residual is real — and it is probe degeneracy, not depth

The referee's null destroyed every headline number in this lane
(`QG_RETRACTION_SELECTION_HEADLINES_V1.md`), but **two** quantities survived it:
the adaptive depth distribution and budget-2 regret. That residual was the only
demonstrated TARE-specific signal. This settles what it is.

Instrument: `research/extensions/orion-qg/qg_residual_null_analysis.py`.

## The residual is real

| | depth-3 classes | distinct coverage masks (of 384) |
|---|---|---|
| **real** | **16** | **168** |
| **null A** — independent row shuffle, 40 seeds | 8–10 (mean 8.9) | **384, every seed** |
| **null B** — one global column permutation, 40 seeds | **16, every seed** | **168, every seed** |

Real sits **above all 40** row-shuffle draws. So unlike the retracted headlines,
this is not null-reproducible.

## But null B reproduces it exactly, which localises it completely

Null B permutes the 384 probe **columns by a single global permutation**. That
destroys the association between probe index and frame identity while preserving
every inter-probe correlation. It returns **16 and 168 on every seed —
bit-identical to real**.

Therefore the residual is a function **only of the multiset of partitions the
probe family realises**. Nothing about *which frame* carries *which index*
enters. Any claim about frame semantics is excluded by this.

## The mechanism, and it is unflattering

The real probe family realises **168 distinct partitions** of the 5,895
same-class pairs. A random alignment realises **all 384**, in every one of 40
seeds.

**TARE's 384 probes are ~56 % redundant.** That redundancy is the entire
residual: fewer distinct partitions means less separating power, which makes
identification *harder* than random. The null is easier precisely because it is
less degenerate.

So the honest reading of `D_* = 3` is not that TARE's identification problem is
deep. It is that **the probe family is redundant, and the redundancy costs a
probe** — a random alignment of the same margins resolves most classes in 2.

## What this is good for

Stated positively, it is an actionable design fact rather than a structural
insight: a probe family engineered to realise distinct partitions would recover
the lost probe. The redundancy is a property of how the 384 probes were
constructed (`8 swap patterns x 48 aux rows`, which are not independent), not of
the compilation problem.

## Status

This closes the last open question in the QG lane. Together with the retraction
and the cost-model verdict (`QG_COST_UNITS_STATEMENT_V1.md`, verdict (c)):

- the **arithmetic** is correct throughout — every number rebuilt from primitives
  with zero discrepancies;
- the **headline separation claims** are retracted as null-reproducible;
- the **cost units** have no external physical referent, and the regret figure
  reduces to `t_r x 5` on a coordinate the probe family cannot vary;
- the **one real residual** is instrument redundancy.

`novelty_claim: false`, `NOT_R6`. Recorded as a closed negative.
