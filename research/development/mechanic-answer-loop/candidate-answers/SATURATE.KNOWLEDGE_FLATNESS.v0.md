# Candidate answer — SATURATE.KNOWLEDGE_FLATNESS.v0

**Target dimensions:** METRICS, MATHEMATICS, INVARIANTS.
**Incumbent evidence:** RAKL `publication/papers/paper-01-epistemic-mechanics/sections/02_compatibility_authority.tex` @ `bd4ce50f` (§Why the geometry/value distinction matters for saturation) and `sections/04b_open_world_stopping.tex` (stopping tied to decision coordinates).

## Proposed step-specific contract

**Metrics — a saturation vector, never an average.** Substantive knowledge growth is counted per coordinate, separately:

```text
Δ = (new mechanisms, new derivations, new independent evidence roots,
     new contradictions/counterexamples, new negative results,
     novelty-boundary updates, assumption-scope changes,
     unresolved-fiber updates, discovery-route changes)
```

**Flatness is a product condition:** every coordinate is zero under a stable basis. Direction: `NON_COMPENSATORY_GATE` per coordinate. Threshold semantics: exact zero after typed deduplication, over a declared window of challenge rounds.

**Mathematics — decision-coordinate stability.** A new source is bibliographic redundancy iff it would change no claim, proof, evidence root, contradiction, novelty boundary, assumption, unresolved fiber or discovery route; if it changes even one, the state is not flat regardless of prior screening recall (04b). Flatness of raw counts ("nodes stopped increasing") is explicitly inadmissible; "average confidence stopped increasing" is worse — it can hide counterexamples (incumbent's scalar-inadequacy argument transported to stopping).

**Invariants.**
- An absent fact is not automatically false (open-world KG boundary, 04b): missing coverage is a coverage residual, not evidence of flatness.
- Flatness is certified only relative to a declared bounded basis and horizon (fixed point relative to the declared closure/discovery operator, which can expand).
- Resource exhaustion never rounds up to flatness (`CANNOT_CHECK` path already in the failure envelope; this cell makes the distinction metric-level).

## Known-answer test candidates

1. Rounds adding only duplicate evidence for existing claims → all Δ coordinates zero → flat.
2. Rounds adding one counterexample while claim count is unchanged → not flat (the counterexample coordinate fires), even though "knowledge size" is static.
3. Hostile: feed a stream where average authority rises while a negative result appears → any implementation reporting flatness is refuted.

## Not licensed

Whether repeated flatness over k rounds suffices on live literature (false-flatness rate) is an empirical open coordinate; this contract fixes semantics, not the live threshold k.
