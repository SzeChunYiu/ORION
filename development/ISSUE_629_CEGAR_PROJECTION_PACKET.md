# Development packet — issue #629 counterexample-guided scientific projection evolution

## Development question

Can ORION demonstrate an exact two-generation **working-state refinement cycle** in which a coarse scientific projection is refined by protected counterexamples, succeeds on held-out instances of known standing distinctions, then correctly detects and repairs insufficiency when a new standing-relevant distinction appears—while explicitly crediting CEGAR as the refinement mechanism and full lineage as the fidelity baseline?

This is an integration benchmark, not a new abstraction-refinement algorithm.

## Atomic fibres

1. define an abstraction specification as a registered set of lineage coordinates;
2. start F0 with no lineage coordinate beyond current answer/standing;
3. use DPAIR-1..3 protected counterexamples to identify spurious merges;
4. refine F0 one coordinate family at a time using a deterministic CEGAR oracle;
5. freeze F1 after all DPAIR-1..3 training counterexamples are separated;
6. verify F1 on disjoint-seed held-out DPAIR-1..3;
7. introduce DPAIR-4 obligation-provenance debt only after F1 freeze;
8. show F1's fixed projection merges the new pair and reaches the exact 1/2 ceiling;
9. retain reconstructive lineage containing the obligation provenance;
10. use the DPAIR-4 protected counterexample to refine F1 into F2;
11. verify F2 on disjoint held-out DPAIR-4;
12. compare projection coordinate count with full-lineage fidelity; do not claim superiority over full history merely for matching correctness;
13. keep the protected family/gold identity outside the candidate projection.

## Incumbent mechanics and negative history

- CEGAR is established prior art for counterexample-driven abstraction refinement in programs, MDPs, POMDPs and structured argumentation.
- Predictive-state / causal-state / sufficient-statistic theory owns the concept of retaining exactly future-relevant distinctions.
- Event sourcing / ESR-style lineage is a direct parent for reconstructive history.
- The #629 pair benchmark already proves current summary is insufficient for three future-standing families and that full history/compact typed lineage closes them.
- The D4 delayed-debt extension already makes those information losses causally affect successor scientific actions.

The only remaining purpose of this packet is to test **recursive projection evolution when the registered future distinction family expands**.

## Parent-domain recovery

Mandatory parents:

- Clarke et al. CEGAR;
- Chadha & Viswanathan CEGAR for MDPs;
- Zhang, Wu & Lin CEGAR for POMDPs;
- assumption-based argumentation CEGAR;
- truth-maintenance/justification systems;
- event-sourced replay;
- epistemic-state replication;
- dynamic assurance/change impact;
- predictive/causal state representations.

The implementation should look unsurprising to those fields. The ORION research question is the scientific-standing target and multi-generation protected evaluation.

## Saturation assessment

RSE-0 is frozen to an interaction-only residual after two no-material-change rounds. The #629-specific searches for predictive/bisimulation/state-sufficiency parents and CEGAR produced known mechanisms but did not change the no-man's-land discriminator.

One new obligation-provenance family is sufficient for the second-generation non-vacuity test: it is deliberately absent from F1's training distinction set and uses the same current-state/different-future-standing construction.

## Challenge to saturation basis

A fake recursive result could occur if:

- F1 is secretly given DPAIR-4's coordinate before freeze;
- the refinement oracle sees protected family labels instead of a counterexample witness;
- the new pair differs in current visible fields;
- F2 simply stores the protected outcome label;
- full history is denied the raw obligation provenance;
- DPAIR-4 uses a different current score/standing across variants;
- held-out DPAIR-4 shares exact IDs with the refinement instance;
- refinement success is measured on the same counterexample used to add the coordinate.

The implementation must separate development/refinement seed from held-out verification seed.

## Miss hypotheses

A stronger existing system may already implement generic proof/justification objects whose schema handles new obligation types without projection-schema refinement. If so, that system becomes the stronger donor state and this F1->F2 result is only a demonstration of why generic justification structure is better than fixed bespoke coordinates.

## Reopen triggers

Reopen if:

- the CEGAR loop requires hand-labeling protected gold directly into state;
- F1 can solve DPAIR-4 without the missing distinction through a surface shortcut;
- full-lineage baseline does not solve all generations;
- F2 fails disjoint held-out DPAIR-4;
- coordinate count grows one-per-instance rather than one reusable family distinction;
- a donor generic justification representation subsumes the entire second-generation effect under matched cost.

## Frozen implementation hypothesis

A stdlib-only research module can exhibit:

```text
F0: 0 registered lineage coordinate families
  -> DPAIR-1..3 counterexamples
F1: 3 registered coordinate families
  -> 100% held-out DPAIR-1..3 future-standing accuracy
  -> DPAIR-4 unseen family: 50% ceiling
  -> protected DPAIR-4 counterexample
F2: 4 registered coordinate families
  -> 100% held-out DPAIR-1..4 future-standing accuracy
```

Full reconstructive lineage must remain 100% throughout.

This is a bounded CEGAR/application result. It does not establish that four coordinates are universal, minimal for all science, or superior to a generic donor justification graph.