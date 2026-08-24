# Binary identification envelopes under observational nonseparation

**Protocol:** `P3.PUBLIC.OAEI.CROSS_CONSTRUCT.IDENTIFICATION_ENVELOPE.DEV.V3`  
**Authority:** formal development note; not claimed as a new general result in
decision theory or partial identification

## Setup

Let (w\in\mathcal W) be a licensed scientific world, let (X(w)) be the
observation retained by a system, and let
(Y(w)\in\{\mathsf G,\mathsf O\}) denote the binary relation truth
(`GLUE` or `OBSTRUCTION`). For observation (x), define its fibre and sharp
identified set by

\[
  F_x=\{w:X(w)=x\},\qquad I(x)=\{Y(w):w\in F_x\}.
\]

An envelope rule (E) has distribution-free coverage on the licensed world
class when (Y(w)\in E(X(w))) for every (w\in\mathcal W).

## Proposition

An envelope rule has distribution-free coverage if and only if

\[
  I(x)\subseteq E(x)
\]

for every observation (x) attained by a licensed world. Consequently,
(I(x)) is the unique inclusion-minimal covering envelope. In particular, if a
fibre contains one `GLUE` world and one `OBSTRUCTION` world, every covering
envelope at that observation must contain both relations.

### Proof

If (E) covers every licensed world, then for any (y\in I(x)) there is a
world (w\in F_x) with (Y(w)=y). Coverage gives
(y=Y(w)\in E(X(w))=E(x)), hence (I(x)\subseteq E(x)). Conversely, if the
inclusion holds, then every world (w) satisfies
(Y(w)\in I(X(w))\subseteq E(X(w))). Minimality follows immediately. ∎

## Consequences for P3

1. A singleton or point action is coverage-valid only after an additional
   identification assumption makes truth constant on the relevant observation
   fibre.
2. Agreement between two algorithms is not itself such an assumption,
   especially when both reuse labels or share parser and representation
   failures. V2 supplied 304 public counterexamples to its agreement-to-point
   licensing rule.
3. The V3 envelope `{GLUE, OBSTRUCTION}` therefore provides coverage one for
   binary-expressible truth by construction. It is a coverage baseline, not a
   discovery or superiority result.
4. Coverage is not free: an always-unresolved action incurred mean harm `0.25`
   in every frozen loss regime, versus AML harms `0.025201`, `0.025268`, and
   `0.056478` on the V3 scorable census.

## Scientific boundary

The proposition is the standard fibre/identified-set argument specialized to
P3. A publishable new contribution would require a nontrivial, independently
testable condition under which observable ontology structure licenses a proper
subenvelope while preserving coverage and action-harm noninferiority on
source-disjoint families.
