# Candidate answer — CROSS.AUTHORITY.v0

**Target dimensions:** MATHEMATICS, INVARIANTS, STORAGE, PROVENANCE, TRANSITION_MODEL.
**Incumbent evidence:** RAKL `publication/papers/paper-01-epistemic-mechanics/sections/02_compatibility_authority.tex` @ `bd4ce50f` (§Authority as a product order; §Uncertainty and authority occupy different axes; §Authority update and revocation).

## Proposed step-specific contract

**Mathematics — authority is a product order, not a scalar.** Authority coordinates (incumbent axes: grounding G, representation R, mechanism M, identification I, and D) each carry a local partial order; the authority order is the product order, which admits incomparable states. Incumbent theorem (elementary, with proof): **no faithful scalarization of incomparability exists** — any real-valued score forces an order on genuinely incomparable epistemic states. A scalar may exist only as a declared *policy projection*, never as the stored authority object.

**Invariants.**
- Uncertainty and authority occupy different axes: `high authority, high uncertainty` is a legal state; neither implies the other.
- Non-escalation: search/generation output cannot raise any authority coordinate; only certificates from the protected verification path can.
- Certificate history is append-only; **current authority is a view**: with certificates \(\mathcal C_t(c)\) monotone in \(t\) and a validity predicate \(\nu_t\), revocation flips validity without erasing history. Recomputing the authority view under a changed policy must be possible without loss.

**Storage/provenance.** Store certificates and challenges as immutable events keyed by claim; derive current authority by reduction over valid certificates. (This is the same append-only-events + derived-view shape as the answer-loop's ANSWER.STORAGE fiber — one storage discipline, two consumers.)

**Transition model.** Deterministic: (certificate event | revocation event | policy change) → recomputed view. No operation mutates a stored certificate.

## Known-answer test candidates

1. Two states \(\alpha=(3,1,0,2,1)\), \(\beta=(2,1,3,1,1)\) (incumbent example): neither dominates; any API forced to order them must refuse or expose the policy projection explicitly.
2. Revoke a calibration certificate: dependent claim's authority view drops; history still contains the certificate; re-adding validity restores the view exactly.
3. Hostile: attempt to write authority directly from a search/LLM result → must fail closed.

## Not licensed

Which concrete coordinate set ORION adopts (RAKL's five axes vs a reconstructed set) is a design decision for the owning wave; this answer licenses the *structure* (product order + append-only certificates + views), not the axis inventory.
