# When does "bootstrap 95% lower bound > 0" stop being a 2.5% test?

**Date:** 2026-09-02 · **Scientific authority delta:** `NONE`. No theorem, bound or terminal
changes. This calibrates a frozen gate form against the null and reports the number.

## The gate, and the gap

ORION-paper#49 freezes several gates of the form *"family-block bootstrap 95% lower bound > 0"*
and *"paired 95% lower bound > 0"*. `bootstrap_mean_interval` in
`tier_a_analysis_common_v1.py` implements them and is **statistically sound** — deterministic
via SHA-256 indexing, and at n=30 it gives 0.937 coverage of a true mean 0 against a nominal
0.95.

But it returns `(v, v)` for a single value — a **zero-width interval** whose lower bound is
positive whenever `v` is — and it applies **no minimum-n floor**. Nothing in the primitive
prevents a frozen gate from being evaluated on one block.

## Measured against the null (true mean 0, 400 trials per n)

| n | false-positive rate of `lower bound > 0` |
|---|---|
| 1 | **0.507** |
| 2 | 0.258 |
| 3 | 0.125 |
| 5 | 0.075 |
| 8 | 0.068 |
| 12 | 0.025 |
| 20 | 0.035 |
| 30 | 0.015 |

Nominal is 0.025. At **n=1 the gate is a coin flip**: it passes whenever the single block's
value happens to be positive. At n=3 it is five times nominal.

**On precision:** with 400 trials the Monte Carlo standard error is ≈0.008, so n=12, 20 and 30
are all within noise of nominal and this does not establish 12 as an exact threshold. The
robust reading is the other end: **n ≤ 8 is anti-conservative, and n ≤ 3 grossly so.**

## What follows

A frozen gate of this form needs a **preregistered minimum independent-block count**, and the
primitive should refuse below it — returning `CANNOT_CHECK` rather than a degenerate interval
that reads as significance. That is the same discipline applied elsewhere in this programme:
an unmeasurable result must not be reportable as a passing one.

This says nothing about whether any particular lane is underpowered. How many independent
blocks each study has is a separate question, and a protected one. What is established here is
that the gate does not defend itself, so the block count has to be declared before outcomes
rather than discovered after.

## Scope

This is a property of the shared primitive, measured with no protected outcome touched. It
does not alter any study, and no existing caller's behaviour is changed by this report.
