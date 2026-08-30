# Claim disposition — ORION06.CLAIM_PRESERVING_RECOVERY.v1

**Terminal:** `CLAIM_PRESERVING_CAUSAL_COVERAGE_PROVED__CROSS_DOMAIN_RECOVERY_UNTESTED`  
**Scientific authority delta:** `NONE`

## Closed by this packet

- A repair of the same claim identity must intervene on at least one declared causal ancestor
  of every failed load-bearing predicate.
- If one failed predicate has no admissible identity-preserving repair ancestor, the old
  claim has a **no-repair certificate** in the declared action language.
- Minimum weighted ancestor cover is a rigorous lower bound on repair cost.
- Actions whose causal-effect set is contained in another no-more-expensive action can be
  removed from at least one minimum causal-coverage solution.
- Changing question/population/estimand/protocol semantics/primary metric/threshold/protected
  corpus/terminal semantics after failure creates a different claim identity rather than
  evidence that the failed identity was repaired.

## Still open

- Causal coverage is necessary, not sufficient: an ancestor action may still fail or create
  a new failure.
- Historical ORION-06 failures need their own bound causal action maps before this theorem
  can classify a specific revival attempt.
- Lean/mathlib + Defects4J + exact ORION cross-domain execution remains required for a broad
  productivity/comparative claim.
- No superiority over naive retry, donor repair, debugging tools or research agents is
  earned here.

## Protocol consequence

A future recovery benchmark should compute the causal-coverage lower bound **before**
protected re-evaluation, retain attempts whose selected actions miss failed ancestors as
structurally incapable controls, and preserve identity-mutating successful runs as separately
named successors rather than favourable repairs of the old claim.
