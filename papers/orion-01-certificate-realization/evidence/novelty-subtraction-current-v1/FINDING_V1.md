# ORION-01 current primary-source novelty subtraction V1

**Date:** 2026-08-30. Discharges the #1701 box "Run current primary-source
novelty subtraction for the exact theorem claims."

`NOVELTY_AUDIT_V1.md` already exists and is substantially correct — it concedes
`zsf(H;H\{0}) = D(H)-1`, names Olson for `D(F_2^d)`, and identifies a
"subset-alphabet" donor. This pass verifies its `UNVERIFIED` rows against
primary sources and reports what a **current** search adds. Two corrections and
one defence follow.

## Correction 1 — the subset variant is 1969, not 2010

The audit names **Freeze–Schmid (2010)** as the "nearest donor for the
subset-alphabet variant". Girard–Plagne, *The Davenport constant of balls and
boxes* (arXiv:2510.20412, 2025-10-23), p. 2, states of `D(X)` for `X` a subset
of an abelian group: *"this variant was first introduced by van Emde Boas in
[13], where it is however denoted by `μ(G, X)`"* — that is,

> P. van Emde Boas, *A combinatorial problem on finite abelian groups II*,
> Mathematisch Centrum Amsterdam ZW 1969-007 (1969).

The subset-restricted Davenport constant therefore predates the audit's stated
nearest donor by **forty-one years**. Attributing it to Freeze–Schmid is a
citation a referee in this area would catch immediately.

## Correction 2 — an active modern line is absent

Neither `NOVELTY_AUDIT_V1.md` nor `v3-bounded-closeout-2026-08-29/NOVELTY_AUDIT_V2.md`
cites any of:

- A. Plagne and S. Tringali, *The Davenport constant of a box*, Acta Arith.
  171.3 (2015), 197–220.
- G. Deng and S. Wang, *On the Davenport constant of a two-dimensional box*,
  AIMS Math. 6 (2021), 1101–1109.
- B. Girard and A. Plagne, *The Davenport constant of balls and boxes*,
  arXiv:2510.20412 (2025).

V2 contains no 2025 reference at all. This is the live literature on exactly the
"Davenport constant restricted to an allowed alphabet" object, and it is the
first place a referee will look.

## Verified: the Olson row

The audit's `D(F_2^d) = d+1` row was marked `UNVERIFIED`. Girard–Plagne p. 2
gives `D(G) >= sum(n_i - 1) + 1` and states this is an **equality for p-groups**,
citing van Emde Boas and Olson, *A combinatorial problem on finite Abelian
groups I / II*, J. Number Theory 1 (1969), 8–10 and 195–199. For `G = F_2^d`
this is `D = d + 1`, hence `d(F_2^d) = d`. **The row is now verified against the
primary attribution.**

## Defence — `zsf(H;A)` is NOT the subset Davenport constant

This matters more than either correction, because the corrections invite the
inference that ORION-01's object is already named in the literature. It is not.

- Girard–Plagne's `D(X)` is the maximal length of a **minimal zero-sum**
  sequence over `X`.
- ORION-01's `zsf(H;A)` is the maximal length of a **zero-sum-free** sequence
  over `A`.

For the full group these differ by one. **For a subset they can diverge without
bound**, and the same page says so: *"it can happen that `D(X)` is finite and yet
we can build arbitrarily long sequences of elements of `X` with no non-empty
zero-sum subsequence."*

So the two invariants are genuinely distinct on subsets, and `D(X)` results do
not transfer to `zsf(H;A)`. ORION-01 works in a finite `H`, where `zsf` is
finite and the pathology does not arise — but that is a hypothesis doing real
work, and the manuscript should say so rather than let a reader assume the
objects coincide.

## Recommended manuscript actions

1. Re-attribute the subset variant to van Emde Boas (1969), keeping
   Freeze–Schmid as a later generalisation.
2. Cite Plagne–Tringali (2015) and Girard–Plagne (2025) as the current line.
3. State the `zsf` / `D(X)` distinction explicitly, with the finiteness of `H`
   named as what rules out the divergence.

None of this weakens the theorem. Action 3 strengthens it, by closing the
nearest-miss reading before a referee opens it.

## Scope

Subtraction only — no theorem is verified here (see
`evidence/independent-proof-checker-v1/` for Lemma 3). Retrieval covers the
arXiv primary record; van Emde Boas (1969) is a Mathematisch Centrum report and
was verified through Girard–Plagne's citation of it, not read directly.
`scientific_authority_delta: NONE`.

**Terminal:** `NOVELTY_SUBTRACTION_CURRENT__TWO_CITATION_CORRECTIONS__OBJECT_DISTINCT_FROM_SUBSET_DAVENPORT`
