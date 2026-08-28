# Closure chain composition — ORION17.CLOSURE_CHAIN_COMPOSITION.v1

Top-tier promotion target from issue #1649. `scientific_authority_delta: NONE`.

## What is already frozen

The pairwise closure-carrying transform/composition theory, exact bridge composition, and
nonclosure countermodels. `transitions/P7_CLOSURE_RETENTION_V1.json` additionally records
real evidence in which `exact-containment` achieves **0 false closure retentions and 0
unnecessary reopenings**, while `donor-coarse` is wrong in both directions (27,348 and
22,298 on numpy).

All of it is **pairwise**. #1649 asks for arbitrary finite chains of heterogeneous
transforms.

## Setting

A chain `T_1, ..., T_n` of transforms. Each carries a closure obligation set, and each
adjacent pair `(T_i, T_{i+1})` may have a **bridge contract** that is *exact* when it
transports every obligation of `T_i` to an obligation of `T_{i+1}` with no loss and no
invention.

Each transform is stamped with an **epoch** `e(T_i)`. A chain is **epoch-monotone** when
`e(T_1) <= ... <= e(T_n)`.

## Theorem C1 (chain preservation)

If every adjacent bridge is exact **and** the chain is epoch-monotone, the chain preserves
closure: an obligation discharged at `T_1` remains discharged at `T_n`.

*Proof.* Induction on `n`. For `n = 2` this is the frozen pairwise result. Assume it for
the prefix `T_1..T_{n-1}`, so any obligation discharged at `T_1` is discharged at
`T_{n-1}`. The bridge `(T_{n-1}, T_n)` is exact, so it transports that discharge to `T_n`
without loss, and epoch-monotonicity ensures `T_n` does not precede `T_{n-1}`, so no
obligation is re-opened by ordering. ∎

## Theorem C2 (epoch-monotonicity is not decorative)

Pairwise exactness **alone** does not suffice. There is a chain of length 3 in which both
adjacent bridges are exact, the chain is not epoch-monotone, and closure fails at `T_3`.

*Construction.* Let `T_2` carry epoch 2 and `T_3` carry epoch 1. The bridge `(T_2, T_3)` is
exact as a transport of obligations, but `T_3`'s stamp precedes `T_2`'s, so an obligation
discharged against `T_2`'s state is presented to a transform whose state is *older*. The
discharge does not transfer, and closure fails while every pairwise contract holds. ∎

This is the load-bearing content of the promotion. Chains are **not** the transitive
closure of pairwise guarantees; an order assumption is doing real work, and naming it is
the contribution.

## Theorem C3 (affected-obligation revalidation)

When a chain link fails, the obligations requiring revalidation are exactly the affected
closure downstream of the failing link, and by `ORION16` N4 no nonnegative weighting of
revalidation obligations yields a cheaper sound set.

*Proof.* Obligations upstream of the failure are discharged by C1 applied to the good
prefix; obligations downstream depend on the failed link and are exactly the reachable set.
Minimality is `ORION16` N4 on the chain's obligation graph. ∎

## Corollary C4 (the composition ladder)

Exactness and monotonicity are **independent** requirements: dropping exactness loses
obligations at a single bridge, dropping monotonicity loses them across an ordering
inversion, and each failure has a different location. Only the conjunction preserves
closure over arbitrary finite chains.

## Scope — prospective versus retrospective

**Prospective.** C1–C4 are proved here and verified by exhaustive enumeration over chains
of length 2–5, all bridge-exactness patterns and all epoch orderings, under a protocol
frozen before that verification runs.

**Retrospective, licensing nothing.** `P7_CLOSURE_RETENTION_V1.json` records
`outcome_accessed: true`, so **no frozen test is run against it** and none is reported as
evidence.

**#1649's stop rule for this lane** is the general one: a chain theorem earns promotion only
with real multi-hop chain evidence. The frozen retention campaign is **pairwise** — it
measures single-transition closure retention, not multi-hop chains — so it cannot supply
the multi-hop evidence this theorem would need. The bounded paper is retained.

## What would refute this

An epoch-monotone chain of exact bridges that loses closure; a chain of exact bridges that
preserves closure under an ordering inversion, which would make C2's assumption
unnecessary; or a revalidation set smaller than the downstream closure that is still sound.
