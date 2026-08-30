# ORION-10 vocabulary minimality — claim disposition

**Terminal:** `VOCABULARY_MINIMALITY_IS_DISCRETE` · **scientific_authority_delta: NONE**

Answers RUN_QUEUE (PR #1762) item 9: *"enumerate scoped explanation vocabularies under the
fibre criterion to seek the smallest complexity that separates every exact-cost fibre."*

The answer is an impossibility, not a number.

## What was computed

The criterion is taken from `theory/certificate-explanation-gap-v1/THEORY.md` and not
re-derived. Theorem 2 there establishes that the complete set of Ψ-measurable functions is
the set of assignments of one value per fibre — so a formula over Ψ, of any size in any
language, computes only a function of Ψ, and an exact Ψ-only explanation exists **iff cost
is constant on every Ψ-fibre**.

Item 9's question is the *universal* one: is any vocabulary coarser than the discrete
partition exact for **every** cost function? The per-cost question is trivial — a cost
function's own level sets always suffice — so all the content is in the quantifier. That is
also the shape `THEORY.md` calls **Route 2**: a vocabulary-level impossibility that does not
depend on formula size.

## Result

| n | partitions | universally exact | only the discrete one? | refuted |
|---|---|---|---|---|
| 2 | 2 | 1 | yes | 1 |
| 3 | 5 | 1 | yes | 4 |
| 4 | 15 | 1 | yes | 14 |
| 5 | 52 | 1 | yes | 51 |
| 6 | 203 | 1 | yes | 202 |

The partition counts are the Bell numbers B(2)…B(6) = 2, 5, 15, 52, 203, which is an
independent check that the enumerator is complete.

**Every coarsening is refuted by an exhibited witness pair** — two worlds sharing a fibre and
carrying different cost — because Route 2 asks for exhibited instances, not a count. The
smallest sufficient complexity is therefore **n**: full separation.

## Two independent routes agree

The constructed witness (pick any block of size ≥ 2 and split its cost) is cross-checked
against brute-force enumeration of *every* cost function over the same partitions. They agree
at every n. A construction that had only ever been checked against itself would not be
evidence.

## The scoped half, now attempted — and it returns CANNOT_CHECK

The disclaimer below said a named vocabulary still needs its own witness exhibition on the
real instance space. `check_bprime_fibre_criterion_v1.py` attempts exactly that against
`research/extensions/orion-qg/QG7_BPRIME_COMPLETENESS_RESULTS.json`, read as data only.

**Terminal: `CANNOT_CHECK_FIBRE_CONSTANCY_ON_SELECTED_WITNESSES`**, and the reason is worth
more than a pass would have been.

Keyed on the scalar `f_B'`, the 64 serialised witnesses show **zero cost-mixed fibres**. The
relationship is exact and uniform: `C_Dxx = f_B' − 1` in all 64, `C_D+ − C_Dxx = 1` in all 64,
`C_DP = C_Dxx` in all 64, across 8 panels, all replay-confirmed.

Read naively that says the vocabulary determines the cost — which would sit oddly beside
`THEORY.md`'s reading of these same 64 as proof that `B'` is *insufficient*.

**The naive reading is wrong, and selection is why.** The 64 are selected precisely on
`C_D++ < min(C_D+, f_B')`. Cost constancy within an `f_B'` fibre, on a subset chosen for
having a gap, is what the selection produces — not evidence about the space. Of 740 instances
evaluated, **676 are not serialised**, and those are the ones that would test the criterion.

This is the same failure shape as testing a gate against a degraded baseline: a
selection-conditioned sample cannot support a universal claim, in either direction.

**What would settle it:** serialise `f_B'` and `C_D++` for all 740 evaluated instances, not
only the 64 candidates, and re-run the fibre grouping over the unselected majority.

## What this does not claim

- **Nothing about `B'` or `B''`.** This is the universal statement over the frozen abstract
  space. A named ORION-10 vocabulary still needs its own witness exhibition on the real
  instance space; that is the work item 9's phrase *"scoped"* points at and it is not done
  here.
- **Not that the per-cost problem is hard.** For one fixed cost function the level sets are
  sufficient and cheap.
- **No promotion.** The manuscript's `improving but not yet an all-n theorem` status is
  unchanged by this artifact.

## Why it is still worth having

`THEORY.md` narrows productive next moves to exactly two: enlarge Ψ, or prove a
vocabulary-level lower bound. This closes the *universal* half of the second route on the
abstract space — no coarsening survives — which means the programme's repeated vocabulary
enlargements cannot terminate in a universally-exact coarse vocabulary. Any future
sufficiency claim must therefore be scoped to a named cost family, not stated universally.
