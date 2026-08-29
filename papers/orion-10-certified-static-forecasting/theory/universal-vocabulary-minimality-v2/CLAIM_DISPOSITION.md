# ORION-10 universal vocabulary minimality v2 — claim disposition

**Terminal:** `ABSTRACT_UNIVERSAL_THEOREM_PROVED__NAMED_ORION_VOCABULARY_STILL_OPEN`  
**Scientific authority delta:** `NONE`

## Earned statement

For an arbitrary instance set \(X\), a frozen vocabulary \(\Psi:X\to Y\), and
any cost codomain with at least two values, **every** cost function on \(X\)
factors through \(\Psi\) if and only if \(\Psi\) is injective. Equivalently,
the discrete partition is the unique vocabulary that is exact for all possible
costs.

This removes the finite-\(n\) qualifier from the abstract result enumerated in
`vocabulary-minimality-v1/`: the conclusion holds for all finite \(n\) and
arbitrary cardinality.

## Why this is a theorem rather than an extrapolation

The negative direction is witnessed by any merged pair: assign the two worlds
different binary costs. The positive direction defines the explanatory function
on the image of an injective vocabulary by inversion. Neither argument depends
on \(n\), enumeration, formula size, or the cost alphabet beyond having two
distinct values.

The accompanying checker exhaustively regresses the finite specialization
through \(n=8\), including all 4,140 set partitions at \(n=8\), but that
enumeration is a control, not the proof.

## Claim ceiling — the important part

This does **not** close the named ORION-10 all-\(n\) problem. The repository's
fixed-cost question for \(B'\), \(B''\), and the QG parent quotient is strictly
harder: it asks whether those named vocabularies merge worlds whose *particular
ORION exact cost* differs, across an unbounded family.

The existing scoped \(B'\) attempt remains
`CANNOT_CHECK_FIBRE_CONSTANCY_ON_SELECTED_WITNESSES`: 676 of 740 evaluated
instances were not serialized, and the 64 available rows were selected on the
gap being studied. No missing row is reconstructed here.

Therefore:

- abstract universal-over-all-costs theorem: **PROVED for all cardinalities**;
- named \(B'\)/\(B''\) fixed-cost all-\(n\) theorem: **OPEN / CANNOT_CHECK from
  current evidence**;
- manuscript promotion: **NONE**;
- novelty authority: **NONE**.

The distinction is deliberate. A general theorem with a stronger quantifier over
cost functions does not magically supply the ORION-specific witness family that
the manuscript still needs.
