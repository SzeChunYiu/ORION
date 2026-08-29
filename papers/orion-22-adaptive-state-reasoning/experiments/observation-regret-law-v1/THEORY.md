# The observation regret law — ORION22.OBSERVATION_REGRET_LAW.v1

Top-tier promotion target from issue #1649. Frozen before outcome access.
`scientific_authority_delta: NONE`.

## What is already frozen

`ORION22.OBSERVATION_ALIASING_ROBUSTNESS.v1` established a **qualitative** boundary: of 36
price-blind observation classes, 23 have an empty common-optimum intersection, so no
price-blind policy — however chosen — can be zero-regret on them.

That says *whether* zero regret is possible. It does not say *how much* regret is forced,
nor *how much* refinement buys. #1649 asks for the quantitative law.

## Setting

An environment `e` has action set `A`, cost `c_e(a)`, optimum `opt_e = min_a c_e(a)` and
optimal set `O(e) = argmin_a c_e(a)`. An observation class `z` is a set `E_z` of
environments a policy cannot tell apart, so a deterministic policy commits to one action
for the whole class.

The **regret floor** of the class is

    R*(z) = min_{a in A} max_{e in E_z} ( c_e(a) - opt_e ).

## Theorem Q1 (the floor is exactly what no policy can beat)

Every deterministic observation-based policy incurs worst-case regret at least `R*(z)` on
class `z`, and some action attains it.

*Proof.* A policy sees only `z`, so it selects a single `a` for all of `E_z`; its
worst-case regret on the class is `max_{e in E_z}(c_e(a) - opt_e) >= R*(z)` by definition
of the minimum, and the minimising `a` attains it. ∎

## Theorem Q2 (Q1 subsumes the aliasing result)

`R*(z) = 0` if and only if `∩_{e in E_z} O(e)` is nonempty.

*Proof.* `R*(z) = 0` iff some `a` has `c_e(a) = opt_e` for every `e in E_z`, which is
exactly membership of `a` in every `O(e)`. ∎

So the 23 empty-intersection classes are precisely the classes with `R*(z) > 0`, and the
frozen qualitative finding is the zero-level set of a quantity this packet computes.

## Theorem Q3 (refinement is monotone, and its gain is exact)

If class `z` is partitioned into sub-classes `P` by a finer observation surface, the
refined system's floor is `max_{p in P} R*(p)`, and

    R*(z) >= max_{p in P} R*(p).

The **gain** from that refinement is exactly `R*(z) - max_{p in P} R*(p) >= 0`.

*Proof.* Each sub-class is a subset of `E_z`, so its inner maximum is over fewer
environments and its minimax value cannot exceed `R*(z)`; the refined policy is free to
choose a different action per sub-class, so the system floor is the worst sub-class. ∎

## Corollary Q4 (full refinement)

Refining to singletons gives `R* = 0` for every class, since `O(e)` is nonempty. Price
awareness is one such refinement: making `(p_build, p_serve)` readable splits each class
into per-regime singletons.

This is why `P12_PRICE_AWARE_SUCCESSOR_V1` reaches zero positive regret with **zero new
free parameters** — under Q3 and Q4 that is forced, not fortunate.

## The quantitative predictions this packet tests

1. **Floor respected.** The frozen allocator's measured worst-case regret on each class is
   `>= R*(z)`. A measurement below the floor would refute Q1.
2. **Floor is tight.** Some action attains `R*(z)` on every class — the floor is achieved,
   not merely approached.
3. **Zero-set agreement.** `{z : R*(z) = 0}` equals the 13 classes with nonempty
   common-optimum intersection, and `{z : R*(z) > 0}` equals the 23 empty ones, reproducing
   the frozen result as the zero level set rather than assuming it.
4. **Refinement gain is exact.** Splitting by price yields `max_p R*(p) = 0`, so the gain
   equals `R*(z)` exactly, for every class.

## Scope, fixed in advance

This is the frozen charging family of `p12_transfer_cases_v1` and its expanded pool.
#1649's stop rule is explicit: *if the law does not transfer beyond the frozen charging
family, retain it as a scoped information-boundary result and stop broadening.* No
multi-domain transfer is attempted here and none is claimed; the law is stated for this
family and the packet says so before any number is read.

## What would refute this

A measured regret strictly below `R*(z)`; a class where no action attains `R*(z)`; a
disagreement between the zero set of `R*` and the frozen intersection result; or a
price-refined sub-class with `R* > 0`.
