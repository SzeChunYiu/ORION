# ORION-08 nearest-work matrix — V4

Supersedes `NEAREST_WORK_MATRIX_V3.md`, which was headed "ORION-04 nearest-work matrix"
(legacy numbering) and predated the 2026-08 agent-memory literature. Rebuilt after the
submission-date refresh recorded in `submission/literature-closure-v1/`.

**Nothing here refutes ORION-08's results.** The V3 deltas mostly survive; two rows are
contested and one is directly hit, and the paper's strongest positioning turned out to be
unstated in V3 and is stated here.

## Row-by-row

| Neighbouring area | Existing contribution | ORION-08 does **not** claim | Residual ORION-08 delta |
|---|---|---|---|
| typed / provenance-aware agent memory | stores or distinguishes roles, sources, types, truth-bearing content; shared provenance-aware memory for multi-agent workflows [MAP-Graph, arXiv:2608.10509]; provenance-sensitivity auditing in action selection [arXiv:2607.20827] | invention of typed or provenance-aware memory | matched-information decision tests where the visible factual payload is fixed and only the explicit binding varies |
| stale-memory / state-revision benchmarks | STALE and the implicit-policy-adaptation gap [arXiv:2605.06527]; budgeted verification of stale inherited constraints [arXiv:2608.25553] | first stale-state benchmark | applicability-scope test where irrelevant context change is a hostile control and the question is which coordinates licensed the old failure |
| value of information | classical decision theory; agent work applying VoI to clarification | invention of VoI or active acquisition | type-conditioned inputs to otherwise identical VoI under a shared stopping rule |
| provenance / lineage tracking | records transformations and source history; supersession and revocation at the store | invention of lineage or provenance | exact constructed test that full-path transport validity catches deep evidence splices missed by last-hop checks |
| uncertainty-aware / Pareto decision-making | uncertainty-aware planners; **matched-budget verification with a random-record control** [arXiv:2608.25553] | first uncertainty-aware planner, **and no longer priority on matched-budget verification with a random control** | matched-budget verification targeted specifically at *unresolved Pareto ambiguity*, with the budget varying the epistemic type rather than the inspection slot |
| governed / versioned memory | scope, version, access and supersession control | generic memory governance | remint/transport decision with an explicit **no-value regime** in which the typed mechanism must tie re-derivation exactly |
| constraint decay in long contexts | governance decay under compaction [arXiv:2606.22528]; omission-vs-commission constraint decay [arXiv:2604.20911] | first account of constraint loss | constraints here are *present and wrong*, not lost — a different failure mode |

## What changed from V3, explicitly

1. **The Pareto/matched-budget row is corrected.** V3 claimed "matched-budget verification
   … with paired regret against random verification" as a delta. arXiv:2608.25553 runs
   matched-budget verification with a random-record control. The delta is narrowed to what
   survives: the budget varies the *epistemic type*, not which record is inspected.
2. **Two rows gained closer parents** (typed/provenance-aware memory; stale-memory).
3. **A seventh row is added** for constraint decay, which V3 did not cover.

## The positioning V3 omitted

This is the paper's strongest claim to distinctness and it appears nowhere in V3:

**Exact and exhaustive, not sampled.** The binding-sufficiency lattice checks **2,233,980
world-action configurations in exact rational arithmetic** and returns a proved
biconditional — a zero-regret policy on binding `B` exists **iff** every positive-mass
fibre has a common optimal action. Every parent found estimates a rate with intervals.
Proving a condition and estimating a rate are different epistemic objects.

**Mechanism identification, which the nearest parent explicitly disclaims.**
arXiv:2608.25553 states it "does not identify why native allocation selects what it
selects, it does not establish mediation", and lists mechanism non-isolation as its
Limitation 9. Mechanism isolation under matched information is ORION-08's entire design.

**Cross-family composition.** Every parent found is single-family; ORION-08's object is the
family-level contract across six preregistered studies.

Stronger still, and recorded separately in
`theory/binding-sufficiency-lattice-v1/transfer-v1/`: the lattice **predicts that parent's
result on both sides**, including its null control, from fibre purity alone.

## Discipline

The theorem itself is **not claimed as novel** — `THEORY.md` calls it "generic
decision-sufficiency / Blackwell-style donor theory. No novelty is claimed", and that
stands. The instantiation, the cross-family contract, and the measured transfer are the
contribution.
