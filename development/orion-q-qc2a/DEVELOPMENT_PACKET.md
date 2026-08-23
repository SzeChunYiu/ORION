# ORION-Q QC-2A invariant-obstruction benchmark — development packet (#639)

**Development question:** Can ORION add a quantum-specific exact-world adapter that distinguishes certified method-language obstruction from ordinary search failure, without changing P9 paper authority or smuggling evaluator gold into model-visible quantum data?

**Programme:** #633. **Research saturation:** #638. **Protocol issue:** #639.

## Atomic development fibres

1. Define the smallest quantum target/state payload needed for exact obstruction tests without overloading `P9StructuralWorld.surface_label`.
2. Implement independent finite-state witnesses for two first-wave obstruction families: entanglement under local product operations and intrinsically complex relative phase under real operations.
3. Define evaluator-side obstruction labels separately from model-visible target/state payloads.
4. Generate deterministic hostile/clean cases with opaque IDs and explicit source/basis contracts.
5. Make global phase an explicit semantic equivalence for the phase family.
6. Prove that verifier outputs are invariant to opaque ID/surface reminting and cannot read evaluator gold.
7. Keep P9/P10 authority boundaries intact: the adapter is benchmark scaffolding only and cannot issue novelty, scientific, or method-adoption authority.
8. Defer Clifford/magic, resource lower bounds, representation switching, learned P9/P10 baselines, and real QSVT targets until the first two verifier families are green.

## Incumbent ORION mechanics and negative history

- `src/orion/study/p9/structural_world.py` already freezes evaluator-only gold, typed atoms/relations/mechanics, failure history, view projections, fingerprints, and surface reminting.
- `src/orion/study/p9/generated_worlds.py` already uses paired hostile worlds with identical restricted views and different evaluator gold; quantum generators should copy this discipline rather than invent a second leakage policy.
- `src/orion/study/p9/m0_tasks.py` separates evaluator target/identity from model-visible task payloads and has negative history around candidate-order leakage.
- P9's `RESEARCH_PROGRAMME_V3.md` explicitly names invariant/preservation violations and representation-failure-vs-mechanism-failure as planned exact-world expansions.
- P9 does not own generic operator/library discovery, program synthesis, or broad reusable mechanics; donor systems must be absorbed.

## Donor saturation assessment for this implementation atom

Knowledge saturation is **bounded, not global**. The current S0 sweep has already found direct parents that occupy weak formulations:

- DreamCoder-style quantum library learning already promotes reusable composite gates;
- QSynth already synthesizes recursive quantum program families with logical verification;
- evolutionary quantum DSL work already reconstructs scalable algorithm families from small examples;
- RL+ZX and AlphaTensor-Quantum already exploit representation-specific search;
- LLM+evolution+external-verifier quantum encoding search already exists.

Therefore this implementation does **not** claim novelty for gate-library growth, program synthesis, learned gadgets, or verifier-guided search. It freezes a narrower discriminator: a machine-checkable diagnosis that a declared language preserves an invariant incompatible with the target.

Search-universe saturation is not yet sufficient for a real quantum novelty claim. It is sufficient for this closed verifier tranche because the mathematical obstruction facts are elementary and the implementation does not claim a new quantum algorithm.

Formulation saturation: the narrow question is whether the benchmark can faithfully encode `EXPRESSIVITY_OBSTRUCTION` vs reachable/insufficient cases. It is not yet whether ORION can autonomously invent a novel quantum method.

## Challenge to the saturation basis

The implementation should be considered conceptually invalid and research reopened if any close system is found that already supplies the exact ORION-Q discriminator **and** our proposed benchmark adds no independent falsification value, or if the benchmark's labels can be inferred from names/metadata rather than quantum structure.

The current no-man-zone residual may also collapse if later S0 research shows that autonomous invariant diagnosis + minimal language edit + false-escalation control is already standard quantum synthesis practice. That would narrow the later research claim but does not invalidate the verifier utilities themselves.

## Miss hypotheses

1. Treating a finite search timeout as evidence of expressivity impossibility.
2. Encoding the hidden obstruction family in target names, file names, gate labels, or candidate IDs.
3. Mishandling global phase and falsely declaring a real-up-to-phase state to require complex gates.
4. Treating one entangled target as evidence that every candidate entangling edit is sufficient.
5. Letting evaluator gold enter a model-visible fingerprint.
6. Counting a renamed/allowed composition as a new primitive.
7. Building a quantum-specific benchmark that cannot later map cleanly to P9's view/identifiability machinery.
8. Adding heavy quantum dependencies before the exact finite tests justify them.

## Frozen implementation hypothesis

> If quantum obstruction cases bind a model-visible normalized state target and a frozen language capability contract, while evaluator-only gold is derived independently by exact invariant witnesses, then ORION can create hostile benchmark cases where `local-only -> entangled target` and `real-only -> intrinsically complex target` are certified expressivity obstructions, while matched reachable controls remain non-obstructions, without exposing the gold through IDs or surface labels.

This is benchmark/engineering evidence only. It does not establish P9/P10 learning value or quantum novelty.

## Frozen first-wave semantics

### F1 — local-product / entanglement

- Initial state and target are two-qubit pure states.
- Declared language capability: arbitrary local one-qubit unitaries only; no cross-partition interaction.
- Invariant: Schmidt rank across the declared bipartition is preserved by local unitaries.
- For the first tranche, inputs use product initial states. A target with nonzero two-qubit determinant `a00*a11 - a01*a10` is entangled and therefore unreachable under the declared language.
- Reachable clean controls are product states.

### F2 — real-unitary / complex phase

- Initial state is real up to global phase.
- Declared language capability: real-valued unitaries only.
- Invariant: real-up-to-global-phase is preserved.
- A target is real up to global phase iff all pairwise products `a_i * conj(a_j)` have zero imaginary part (within the frozen numeric tolerance).
- Targets violating this invariant require a phase-generating capability; real-reachable controls do not.

### Numeric policy

The first wave uses small normalized complex vectors and a single frozen tolerance `1e-10`. It avoids numerical matrix search. Witnesses are direct algebraic invariants. Reopen if tolerance sensitivity changes any generated gold label.

## Frozen hostile tests

- Bell-state target is certified entanglement obstruction from a product initial state under local-only capability.
- Product-state target is not falsely certified as entanglement obstruction.
- `( |0> + i|1> ) / sqrt(2)` is not real up to global phase.
- A globally phased real state remains classified real-up-to-global-phase.
- Rephasing a target cannot change the obstruction label.
- Zero vector and materially unnormalized vectors are rejected rather than classified.
- Opaque ID/surface reminting does not change semantic witness output.
- Evaluator obstruction label is absent from model-visible payload/fingerprint.
- Corrupt/unknown capability contracts fail closed.
- No object can authorize novelty/adoption/scientific truth.

## Reopen triggers

Reopen the development packet if:

- any generated case's gold changes under global rephasing;
- the same model-visible payload can carry contradictory evaluator gold without an explicit hostile-pair reason;
- metadata/IDs reveal obstruction class;
- numerical tolerance rather than algebraic structure determines protected labels;
- a verifier needs target-family names to classify;
- integration requires weakening P9's evaluator/model separation;
- S0 donor saturation collapses the intended discriminator;
- implementation expands beyond F1/F2 before this packet is amended and re-frozen.
