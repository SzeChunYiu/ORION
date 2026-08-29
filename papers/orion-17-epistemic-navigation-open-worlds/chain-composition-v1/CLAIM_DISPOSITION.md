# Claim disposition — ORION17.CLOSURE_CHAIN_COMPOSITION.v1

Protocol and theory frozen before verification ran. Terminal: **T1_CHAIN_COMPOSITION_LAW_HOLDS**.
Promotion status: **CHAIN_THEOREM_ESTABLISHED__PROMOTION_NOT_EARNED__BOUNDED_PAPER_RETAINED**.

## Result

4,662 cases — chains of length 2–5, every bridge-exactness pattern, every epoch assignment.

| | |
|---|---|
| C1 violations (all-exact monotone chains losing closure) | **0** |
| C3 violations (revalidation set ≠ downstream closure) | **0** |
| **C2 countermodels exhibited** | **308** |
| failures from inexactness alone (monotone epochs) | 456 |
| failures from ordering alone (all bridges exact) | 308 |

All four controls pass.

## What the law says

Exactness and epoch-monotonicity are **jointly sufficient and separately necessary**.
Chains are *not* the transitive closure of pairwise guarantees: 308 chains have every
adjacent bridge exact and still lose closure, purely from an ordering inversion. The two
failure modes separate cleanly — 456 cases fail only from inexactness, 308 only from
ordering — so neither assumption is implied by the other.

That is the promotion's content. The frozen pairwise theory does not give chains for free,
and naming the order assumption is what makes the chain theorem true rather than assumed.

## A correction to my own construction

`THEORY.md` states C2's countermodel as a **length-3** construction. The sweep found the
minimal witness is **length 2**: `epochs = [2, 1]` with the single bridge exact.

C2 is not refuted — countermodels exist at every length including 3 — but my construction
was more elaborate than necessary, and the honest reading is stronger than what I wrote: a
*single* exact bridge with inverted epochs already loses closure. The theory text overstated
the machinery required. I am recording this rather than quietly adopting the better witness,
because the discrepancy is between my stated proof and the exhaustive search, and the search
is right.

## Controls

- **U1** — C2 asserts a countermodel *exists*, so the sweep had to actually produce one.
  It produced **308**. An existence claim that passes because nothing contradicted it is
  not evidence, which is why this control fails the run rather than the claim.
- **U2** — planted inexact bridges detected as losing closure: **456/456**.
- **U3** — every all-exact monotone chain preserved closure, none flagged: **52/52**.
- **U4** — both failure modes occur separately, so C4's independence is demonstrated
  rather than asserted.

## The retrospective evidence, and why it cannot help here

`transitions/P7_CLOSURE_RETENTION_V1.json` records `outcome_accessed: true`, so **no frozen
test was run against it.**

Beyond that, it is the **wrong shape**: it measures *pairwise* single-transition closure
retention — `exact-containment` at 0 false retentions and 0 unnecessary reopenings against
`donor-coarse` at 27,348 and 22,298 — not multi-hop chains. A chain promotion needs
multi-hop evidence, and no campaign in this paper produces it.

## Why promotion is not earned

The theorem is established; the evidence a chain claim would require does not exist. #1649's
general rule for this lane is that a chain theorem earns promotion only with real multi-hop
chain evidence. ORION-17 remains in the bounded lane and **no multi-hop deployment claim is
made**.

## Authority

`MEASUREMENT_AND_PROOF_ONLY`. `scientific_authority_delta: NONE`. No submission authority.
Nothing frozen is retracted. Outcomes were read once.
