# Candidate answer — DETECT.CONTRADICTION.v0

**Target dimensions:** MATHEMATICS, TRANSITION_MODEL, INVARIANTS, OUTPUTS.
**Incumbent evidence:** RAKL `publication/papers/paper-01-epistemic-mechanics/sections/02_compatibility_authority.tex` @ `bd4ce50f` (§Typed transition maps and aligned contradiction; §Contradiction without explosion).

## Proposed step-specific contract

**Mathematics.** For charts/claims \(C_i, C_j\) at comparison level \(\ell\):

```text
Contradict_l(Ci,Cj) = Overlap(Ci,Cj) AND Align_l(Ci,Cj) AND NOT Compat_l(Ci,Cj)
```

A contradiction predicate is evaluable only after overlap and alignment obligations are discharged. If alignment fails, the typed outcome is `NOT_COMPARABLE_UNDER_REGISTERED_MAP`, never `CONTRADICTS_EXISTING`.

**Outputs (typed severity ladder).** Three distinct outcomes, strictly ordered by obligation:

```text
RAW_CONFLICT  ⊇  ALIGNED_CONTRADICTION  ⊇  DECISIVE_REFUTATION
```

RAW_CONFLICT may be textual; ALIGNED_CONTRADICTION requires compatible scope/representation via a registered transition map (with assumptions, validity regime, error semantics, evidence, failure mode); DECISIVE_REFUTATION additionally requires evidence of sufficient authority for the target claim and regime.

**Invariants.**
- No explosion: a recorded contradiction licenses no arbitrary consequences; conflicting claims coexist as typed objects with the contradiction stored as an obstruction (Belnap/Dung lineage in the incumbent).
- Different words do not imply different concepts; different concepts do not imply contradiction (already constitutional; this cell is where it becomes executable).
- Demotion path: a DECISIVE_REFUTATION downgraded by certificate revocation reverts to ALIGNED_CONTRADICTION, never silently disappears.

**Transition model.** Input: claim pair + registered transition maps + authority state. Deterministic given those inputs; set-valued only when multiple registered maps yield different alignment verdicts, which itself emits a `MAP_AMBIGUITY` residual.

## Known-answer test candidates

1. Two claims with disjoint regimes and no registered map → `NOT_COMPARABLE_UNDER_REGISTERED_MAP`, not a contradiction.
2. Same claims plus a registered alignment map that succeeds and exposes incompatibility → `ALIGNED_CONTRADICTION`.
3. Hostile: force explosion — assert an unrelated claim's status changed because a contradiction was recorded → must fail.

## Not licensed

Nothing here establishes live extraction quality (whether real text can be mapped into charts); that remains an ABSORB-side empirical obligation.
