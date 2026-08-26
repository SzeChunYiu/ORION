# ORION-ORION-14 threat model V1

## Protected object

The protected object is the validity of a **scientific-authority transition**, not merely an answer string. The attacker/candidate may generate claims, evidence references, explanations, code patches or checker proposals, but may not control the final evidence binding, protected evaluator/holdout, hidden attack label, or host promotion decision.

## Threat families

1. **Attribution laundering:** correct or plausible claim is attached to the wrong source.
2. **Content substitution:** stable-looking evidence identity resolves to changed or adversarial content.
3. **Cross-source conflation:** pooled evidence supports a statement that no assigned source individually supports.
4. **Behavioral laundering:** evidence is cited but did not influence the answer path.
5. **Weak/self-authored verification:** checker accepts non-empty/restated material or shares prohibited lineage with the answer.
6. **Post-hoc verification:** checker/evaluator is changed after candidate outcomes are known.
7. **Search-time contamination:** benchmark answer, label or identifying metadata becomes available through browsing/retrieval.
8. **Evaluator/guard tampering:** candidate changes metric, evaluator, protected registry or test semantics.
9. **Holdout leakage:** candidate reads labels/answers or a derived artifact that reveals them.
10. **Insufficient evidence:** the scientifically valid state is unresolved; the system must not manufacture promotion.
11. **Trivial refusal:** a system blocks every case. Clean-positive coverage prevents this from being scored as a security win.

## Assumptions

- The independent host/verifier can keep protected files/labels outside candidate write authority.
- Access/patch/search telemetry is trustworthy enough for the scoped benchmark; compromise of the host itself is outside V1.
- No finite attack battery proves universal security. The claim is bounded to registered and held-out hostile families under the frozen custody model.

## Invalidating events

The run cannot support the headline claim if the candidate can write the protected evaluator, final attack labels leak before candidate completion, evaluator identity changes post-outcome without a new protocol version, or the exact subject/evidence content cannot be reconstructed.
