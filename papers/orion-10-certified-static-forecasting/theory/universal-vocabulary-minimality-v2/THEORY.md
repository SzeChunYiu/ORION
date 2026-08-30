# ORION10.UNIVERSAL_VOCABULARY_MINIMALITY.v2 — all-cardinality theorem

**Paper:** ORION-10 — Certified Static Forecasting  
**Status:** `ABSTRACT_UNIVERSAL_THEOREM_PROVED__NAMED_ORION_VOCABULARY_STILL_OPEN`  
**Scientific authority delta:** `NONE`

This is an additive theorem companion to
`theory/vocabulary-minimality-v1/`. V1 exhaustively checked finite instance
sets of size 2 through 6 and found that the discrete partition is the only
vocabulary exact for every cost function. The finite enumeration suggested an
all-\(n\) statement. No further computation is needed: the statement follows
directly from the fibre criterion already proved in
`certificate-explanation-gap-v1/THEORY.md`.

## Setting

Let \(X\) be any set of instances and let \(\Psi:X\to Y\) be a frozen
explanation vocabulary. A \(\Psi\)-only explanation of a cost
\(c:X\to Z\) is a function \(f:Y\to Z\) satisfying

\[
c = f\circ\Psi.
\]

Assume only that the cost codomain \(Z\) contains at least two distinct values.
No finiteness assumption is made on \(X\) or \(Y\).

Call \(\Psi\) **universally exact** when every cost function \(c:X\to Z\)
admits an exact \(\Psi\)-only explanation.

## Theorem 1 — universal exactness iff injectivity

For any \(X,Y,\Psi\) as above, \(\Psi\) is universally exact **if and only if**
\(\Psi\) is injective.

### Proof

**If.** Suppose \(\Psi\) is injective. For any cost \(c:X\to Z\), define
\(f\) on the image \(\Psi(X)\) by

\[
f(\Psi(x)) := c(x).
\]

Injectivity makes this well-defined. Extend \(f\) arbitrarily from
\(\Psi(X)\) to the rest of \(Y\). Then \(f(\Psi(x))=c(x)\) for every
\(x\in X\), so \(c=f\circ\Psi\).

**Only if.** Suppose \(\Psi\) is not injective. Then some distinct
\(x,x'\in X\) satisfy \(\Psi(x)=\Psi(x')\). Choose two distinct values
\(z_0,z_1\in Z\), and define one binary-valued cost with
\(c(x)=z_0\) and \(c(x')=z_1\) (arbitrary elsewhere). Every function
\(f\circ\Psi\) gives the same value at \(x\) and \(x'\), so it cannot equal
this \(c\). Therefore \(\Psi\) is not universally exact. ∎

## Corollary 1 — the discrete partition is the unique universal vocabulary

The fibres of an injective \(\Psi\) are all singletons. Conversely, a
singleton-fibre partition is induced by an injective vocabulary. Hence the
discrete partition is the unique partition that is exact for every possible
cost function.

For a finite instance set \(|X|=n\), any universally exact vocabulary therefore
has exactly \(n\) fibres. This is the all-\(n\) version of V1's enumerated
\(n=2,\ldots,6\) result. For an infinite \(X\), universal exactness similarly
requires \(|\Psi(X)|=|X|\); the theorem is cardinality-independent.

## Corollary 2 — binary costs already witness every failure

The negative direction needs only a two-valued cost. Therefore no richer cost
alphabet, formula language, operator set, interaction order, or expression-size
budget can rescue a non-injective vocabulary from the universal claim.

This is the strongest possible abstract version of the fibre-constancy
criterion: if even one pair of worlds is merged, there exists a cost problem for
which that merge destroys exact explainability.

## What this closes

It closes the **abstract universal** question left finite in
`vocabulary-minimality-v1`: the finite Bell-partition enumeration was not hiding
an exceptional larger \(n\). The result holds for every finite \(n\) and for
arbitrary sets.

The V1 enumerator remains useful as an executable regression and witness
generator, but it is no longer the source of authority for the all-\(n\)
abstract statement; the proof above is.

## What this does not close

This theorem must not be confused with ORION-10's harder, paper-specific
all-\(n\) question.

- It does **not** prove that the named vocabularies \(B'\), \(B''\), or any
  future fixed ORION vocabulary fail on every problem size for the repository's
  fixed exact cost.
- It does **not** fill the 676 of 740 QG-7 instances that were evaluated but not
  serialized. The existing
  `CANNOT_CHECK_FIBRE_CONSTANCY_ON_SELECTED_WITNESSES` remains controlling for
  the scoped \(B'\) test.
- It does **not** change QG7D's `all_n_theorem_authority: false` for the named
  parent-quotient identity.
- It grants no novelty authority: the proof is elementary measurability /
  factorization through fibres.

The paper-specific route still requires either a symbolic construction of
equal-vocabulary/different-cost witnesses for an infinite family, or complete
unselected data sufficient to establish the relevant fibre structure.

## Independent executable regression

`check_universal_vocabulary_minimality_v2.py` does not serve as the proof.
It independently enumerates every set partition through \(n=8\), verifies the
Bell counts, constructs a binary mixed-fibre witness for every non-discrete
partition, and checks every binary cost on every discrete partition. Its role is
to catch implementation or statement drift around the finite specialization of
the theorem.
