# Far-domain recursive audit — 2026-08-16

## Verdict

The first-pass ideas were directionally useful but several primitives are already occupied. This pass therefore **contracts novelty before implementation** and keeps only ORION-specific compositions as candidate mechanics.

### Struck as standalone novelty

- structural/far-domain analogy retrieval;
- active diagnosis or information-gain test selection;
- causal failure attribution / counterfactual repair;
- bandit route allocation / conservative baseline-safe exploration;
- bidirectional lenses / round-trip laws / cycle consistency;
- proof-carrying agent actions / diverse validator quorum;
- defeater representation itself;
- anytime-valid e-process acceptance for self-evolving agents;
- generic multi-stage evaluation.

### Surviving candidates worth local falsification

1. **Shared:** structural retrieval separated from transfer authority by explicit assumptions + falsifiers, optionally requiring distinct-domain cross-confirmation.
2. **P1:** responsibility diagnosability before responsibility assignment, followed by responsibility-scoped epistemic licensing.
3. **P2:** conservative route exploration that preserves ORION's censoring and route/task non-authority semantics.
4. **P3:** typed scientific round-trip/cycle consistency used as a GLUE/OBSTRUCTION gate, not as a universal canonicalizer.
5. **P4:** protected evidence-action planning over unresolved scientific-authority defeaters; not a new certificate/quorum system.
6. **P5:** non-compensatory fresh/protected stages; PACE absorbs anytime-valid acceptance, so P5 must differentiate on fresh transfer, protected custody, negative history and host authority.

## Primary-source pressure absorbed

- arXiv:2604.05396 — cross-domain analogical transfer is conditionally useful, so analogy retrieval is not enough.
- Forecast@ICML 2026 `Analogical Deep Research` — structural analogy retrieval and cross-confirming analogies are already explicit research objects.
- arXiv:2607.01431 (`IsoSci`) — isomorphic structure can still require domain-specific knowledge; this directly motivates explicit transfer assumptions.
- arXiv:2509.04708 — diagnosability and active fault identification are established.
- arXiv:2605.25338 / arXiv:2607.18754 — agent causal attribution, recovery and rerun are established.
- arXiv:1602.04282 / 1611.06426 / 2002.03221 / 2002.00467 — conservative/safe bandit exploration, including IR, is established.
- arXiv:2601.04573 — partial-state bidirectional lenses with well-behaved properties are established.
- arXiv:2606.04104 / 2606.08021 / 2607.16109 — proof-carrying actions, semantic quorum and correlated epistemic-quorum failure are established.
- arXiv:2606.11462 — structured defeater management is established.
- arXiv:2606.08106 (`PACE`) — anytime-valid self-evolving-agent acceptance is established and must be added to P5 nearest work.
- arXiv:2608.02636 — validation, robustness and transfer can disagree during self-evolution; additional rounds are not monotone improvement.

## Research-to-code boundary

All code in this wave is an **experimental internal solver package** under `src/orion/transfer/`. It intentionally does not edit P1/P2/P4/P5 paper trees while concurrent lanes own them, and it does not alter any frozen publication protocol.

A local green falsifier means only that the proposed mechanic behaves correctly on its known-answer counterexample. It does not mean the mechanism is novel, superior on real tasks, or ready to enter a manuscript.
