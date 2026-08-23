# ORION

ORION is an evidence-governed recursive research operating system descended from the RAKL project.

Its fundamental machinery is not a fixed list of research tricks. ORION repeatedly **searches, absorbs, reconstructs, detects residuals, diagnoses responsibility, reframes the responsible layer, reopens dependent work, and searches again**. The same machinery can be applied to ORION itself under stricter self-development governance.

```text
FRAME
  -> SEARCH
  -> ABSORB
  -> RECONSTRUCT
  -> DETECT
  -> DIAGNOSE
  -> REFRAME
  -> REOPEN
  -> RECURSE
  -> BOUNDED SATURATION
```

ORION deliberately absorbs knowledge from any relevant discipline. External disciplines remain contextual projections rather than authorities over the whole system; ORION maps their concepts, assumptions, evidence and failure modes into a provenance-preserving global portrait and may derive its own representation when the synthesis warrants it.

---

## Research dashboard

**Research status snapshot: 2026-08-22.**

ORION is now running several connected research programmes rather than only building the core framework. The most mature scientific programme is quantum compilation and resource geometry, while parallel programmes study research control, typed epistemic state, method spaces, structured reasoning, novelty, cross-domain transfer and recursive scientific evolution.

A core rule across all programmes is that **claim strength follows evidence strength**. A proxy improvement is not called a circuit improvement; a finite-domain result is not called an all-instance theorem; donor-owned mechanisms are not relabeled as ORION novelty; and refutations remain first-class results.

### Programme overview

| Programme | Main question | Current state | Where to look |
|---|---|---|---|
| **ORION-Q — quantum compilation** | Can structured Pauli/block-encoding representations be characterized and improved without hiding implementation cost? | **Core registered programme closed with receipted terminals; strong mathematical results, but no general quantum-advantage or R6 novelty claim.** | [`research/extensions/orion-q/`](research/extensions/orion-q/) · [`development/orion-q-max-r0/`](development/orion-q-max-r0/) |
| **ORION-QG — quantum regime geometry** | When is a restricted quantum compiler exactly optimal, what mechanisms create the trade regimes, and can membership be forecast without full optimization? | **Active extension programme.** Several all-`n` theorems are closed; classification and objective-boundary questions continue. | [`research/extensions/orion-qg/`](research/extensions/orion-qg/) · [`development/orion-qg-regime-geometry/`](development/orion-qg-regime-geometry/) |
| **Recursive negative-result recovery** | Can failed/negative scientific results be recursively diagnosed, donor-compared, repaired or formally saturated instead of discarded? | **Substantial closed quantum case study plus reusable harness/receipt machinery.** | [`papers/Q-paper-02-recursive-recovery/`](papers/Q-paper-02-recursive-recovery/) · [`packages/orion-research-harness/`](packages/orion-research-harness/) |
| **Typed partial knowledge / epistemic state** | Which typed uncertainty, failure and evidence states are load-bearing for research decisions under incomplete knowledge? | **Multiple synthetic mechanism-isolation families completed; broader real-domain transfer remains open.** | [`research/extensions/p6-higher-order-epistemic-mechanics/`](research/extensions/p6-higher-order-epistemic-mechanics/) · related N-lane records |
| **Method-space and method-authority research** | How should ORION discover, compare, transport and authorize methods without laundering evidence or stronger oracles? | **Ongoing extension research with absorbed/negative/positive lanes.** | [`research/extensions/p7-method-space/`](research/extensions/p7-method-space/) · [`research/extensions/p8-method-authority/`](research/extensions/p8-method-authority/) |
| **Structured reasoning / neural methods** | Which structures actually improve problem solving, and which apparent gains disappear under stronger controls? | **Ongoing programme family.** | [`research/extensions/p9-structured-neural/`](research/extensions/p9-structured-neural/) · [`research/extensions/p10-structured-reasoning/`](research/extensions/p10-structured-reasoning/) |
| **Meta-ORION / recursive scientific evolution** | Can ORION improve research skills and research-control mechanisms while preserving protected evidence boundaries? | **Active R&D; synthetic self-evolving-system evidence exists, real-science superiority is not claimed.** | [`research/extensions/meta-orion-recursive-scientific-evolution/`](research/extensions/meta-orion-recursive-scientific-evolution/) |
| **Cross-domain transfer and novelty** | Which research mechanics survive transfer across domains, and how can novelty be separated from donor recomposition? | **Ongoing.** | [`research/cross-domain-mechanic-transfer-v1/`](research/cross-domain-mechanic-transfer-v1/) · [`research/novelty/`](research/novelty/) |

---

## Quantum research: strongest findings so far

The quantum programme has evolved from searching for apparent algorithm/resource wins into a more precise theory of **representation geometry**: which Pauli/block-encoding compilation families are sufficient, where they fail, what coupling mechanisms cause the failure, and how the answer changes with the resource objective.

### 1. R6M shared-Tag TARE: support two is sufficient for every `n`

For the frozen three-block TARE-M2/shared-one-bit-Tag grammar under the frozen support-count objective, ORION has a machine-checked all-`n` result:

```text
C_DP == C_D++  for every n
```

where `C_DP` is the unrestricted exact dynamic-programming optimum and `D++` restricts auxiliary frame Paulis to global support `<= 2`.

The proof localizes the exact obstruction to support two: support `>= 3` can always be exchanged away without increasing cost, while the support-two boundary is exactly where the previously discovered Tag/frame coupling trade can occur.

Primary receipt: [`research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json`](research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json).

**Status:** **ALL-`n` MACHINE-CHECKED THEOREM within the frozen grammar/objective.** Not a universal statement about all quantum compilers or other cost models.

### 2. R6I dependent-triple TARE: intrinsic support number is one

The later QG-9 ladder progressively sharpened the R6I support bound from `<= 5` to `<= 4`, `<= 3`, `<= 2`, and finally:

```text
C_DP == C_cap1  for every n
kappa_R6I = 1
```

The final proof uses a global move unavailable to the earlier block-local exchange arguments: localize each block to one anticommuting core and then relocate the shared Tag.

**Status:** **ALL-`n` MACHINE-CHECKED THEOREM for the frozen R6I family.**

### 3. The important optimization variable is the coupling between representation components

The early intuition that “simpler auxiliary frames should always be better” was false. Exact counterexamples exposed several coupling trades:

- **Tag-anchor split:** allow different frame anchors and pay for a larger shared Tag.
- **Frame-for-Tag borrow:** spend frame support at a cheap central multiplier to compress the shared Tag and improve Restore alignment.
- **Phantom borrow:** allow the borrow home outside the block's own target support.
- **Split + borrow hybrid:** combine a weight-two Tag with phantom borrowing.

These are not failures of the support-two theorem; they explain the internal geometry of the support-two optimum.

**Current frontier:** support-two sufficiency is closed for R6M, while the simplest complete closed-form taxonomy of all support-two optima is still being refined in QG.

### 4. Resource geometry depends on the **(family, objective)** pair

Low-support sufficiency is not a universal law. Reweighting the resource objective can change which representations are optimal and can make higher-support constructions pay.

QG therefore treats compiler behaviour as a phase diagram over both representation family and objective weights. Machine-checked objective cones now identify regions where low-support theorems remain valid, while global phase-boundary sharpness remains an active question in some families.

**Status:** **theorem-backed in declared objective cones; not universal outside them.**

### 5. Split-TARE coefficient majorization

For the frozen equal-size split-TARE coefficient problem, sorted-contiguous coefficient partitioning minimizes the outer-LCU subnormalization. Exhaustive deterministic checks found no counterexample in the declared test domains.

Primary receipt: [`research/extensions/orion-q/MAX_R4B_TARE_SPLIT_MAJORISATION_RESULTS.json`](research/extensions/orion-q/MAX_R4B_TARE_SPLIT_MAJORISATION_RESULTS.json).

**Boundary:** this optimizes the coefficient/normalization coordinate, not total compiled circuit resources.

### 6. Real public Hamiltonians show both positives and negatives

ORION deliberately tests fresh public Hamiltonians so that synthetic proxy gains cannot silently become physical claims.

- **H2:** a frozen “large direct-unitary coverage within 1% normalization slack” hypothesis was **refuted**.
- **H2O DUCC, 20 qubits / 8,082 nonidentity Pauli terms:** an implementation-aware split compiler reduced the frozen structural implementation metric from `8078` to `4972` (about **38.45%**) while adding only about `9.1e-6` relative normalization overhead.
- **H4 / equilibrium N2:** simple weight-one donor constructions remain exactly optimal on the frozen checked matchings, and the structural theory explains why the richer trades do not pay there.

Primary H2O receipt: [`research/extensions/orion-q/MAX_R4D_H2O_DUCC_CONFIRMATION_RESULTS.json`](research/extensions/orion-q/MAX_R4D_H2O_DUCC_CONFIRMATION_RESULTS.json).

**Status:** strong real-Hamiltonian compiler evidence, **not** a full fault-tolerant quantum advantage claim.

### 7. Grouped sparse-QSVT taught us not to confuse normalization with implementation cost

Anticommuting Pauli grouping can strictly reduce the LCU-style normalization:

```text
Lambda_G <= sum_j |c_j|
```

and the frozen diagnostic proxy showed a broad favorable regime. But when realistic grouped-unitary synthesis cost was introduced, the apparent advantage could disappear.

This negative result changed the programme's evaluation standard: quantum candidates are now compared on **resource vectors** rather than a hidden scalar or normalization alone.

Primary diagnostic receipt: [`research/extensions/orion-q/MAX_R4A_GROUPED_SPARSE_QSVT_CONFIRMATORY_RESULTS.json`](research/extensions/orion-q/MAX_R4A_GROUPED_SPARSE_QSVT_CONFIRMATORY_RESULTS.json).

### 8. Hardware/compiler assumptions can reverse the winner

On the N2 proof-replayed comparison, one successor reduced internal two-qubit structure substantially, but the full outer result changed sign across two reasonable compilation projections:

- worse under the declared Clifford+T projection;
- better under the declared native two-qubit projection.

Therefore “best representation” is often a **Pareto frontier**, not a hardware-independent total ordering.

Primary receipt: [`research/extensions/orion-q/MAX_R5B_N2_PROOF_OUTER_REPLAY_RESULTS.json`](research/extensions/orion-q/MAX_R5B_N2_PROOF_OUTER_REPLAY_RESULTS.json).

---

## Quantum regime geometry: active frontier

ORION-QG asks a broader question than “which compiler is cheaper?”:

> Can we derive a structural map telling us **which regime an instance belongs to**, why, and when a cheap forecast can replace full exact optimization?

### Closed / strong results

- **R6M support-two all-`n` normal form:** closed in ORION-Q.
- **R6I support-one all-`n` normal form:** closed by the latest QG-9 ladder.
- **Objective-indexed low-support cones:** machine-checked for declared resource-weight regions.
- **SixLCU regime boundary:** transferred successfully; an all-instance boundary theorem exists for the admitted family.
- **Prospective forecasting:** several regime predictions were frozen before referee computation and later confirmed.

### Important refutations

- The original two-trade closed-form TARE map was not the final taxonomy; adversarial search found phantom and hybrid configurations.
- “Regime boundaries are always low-order” is false. In the StabPrep family, the frozen natural feature vocabulary contains feature-identical cells with different labels, so no classifier in that vocabulary can exactly determine donor-optimality.
- Random panels are not enough for closure: targeted adversarial grammars found rare regimes that broad random testing missed.

### Open questions

- Complete the remaining all-`n` classification link for the support-two TARE trade taxonomy.
- Characterize sharp objective phase boundaries outside currently certified cones.
- Identify which structural property makes a compiler family's regime boundary feature-determined.
- Extend regime-geometry transfer to additional quantum compilation/synthesis families with exact referees.
- Upgrade resource comparisons from structural/projection models to stronger end-to-end compiled models where feasible.

Main record: [`development/orion-qg-regime-geometry/QG_WAVE2_RECORD.md`](development/orion-qg-regime-geometry/QG_WAVE2_RECORD.md).

---

## Research-control findings

ORION is also studying the process that produced the quantum results.

### Negative results are treated as outputs, not discarded attempts

The quantum programme repeatedly produced candidates that looked promising but were later:

- donor-equivalent;
- proxy-only;
- resource-model dependent;
- falsified on a fresh subject;
- or saturated by a stronger exact family.

Those outcomes remain committed with the same receipt discipline as positive results. The programme closure does **not** claim general quantum novelty or quantum advantage.

Main closure record: [`development/orion-q-max-r0/PROGRAMME_CLOSURE_PACKET_2026-08-21.md`](development/orion-q-max-r0/PROGRAMME_CLOSURE_PACKET_2026-08-21.md).

### Protected self-evolving research skills

A synthetic protected skill-stream experiment across 40,000 held-out tasks found that non-compensatory protected admission could retain useful skill transfer while eliminating protected-invalid deployments in the tested system and slightly improving verified-valid success.

Main milestone: [`research/extensions/orion-q/MAX_R3E_MILESTONE.md`](research/extensions/orion-q/MAX_R3E_MILESTONE.md).

**Boundary:** this is a synthetic research-system mechanism result. It does **not** show that ORION already discovers better real quantum science than specialist systems.

### Research harness and replay

The repository contains a host-capability research harness with deterministic receipts, replay, protected custody, failure recovery and campaign adapters. Scientific terminals are designed to be replayable independently rather than existing only as prose conclusions.

See [`packages/orion-research-harness/`](packages/orion-research-harness/) and the development verification records.

---

## Progress model

ORION does not use a single percentage-complete score for science. Different research questions close under different terminal modes:

| Marker | Meaning |
|---|---|
| **THEOREM / MACHINE-CHECKED** | General statement within a frozen formal family/objective has a proof/checking chain. |
| **VERIFIED DOMAIN CLOSURE** | Exact equality or classification is established on all declared finite domains, but an all-instance theorem is still open. |
| **REAL-SUBJECT CONFIRMATION** | A result survived a frozen external/public subject under declared semantics. |
| **PROXY / DIAGNOSTIC POSITIVE** | Worth pursuing, but insufficient for a compiled/physical claim. |
| **NEGATIVE / REFUTED** | Frozen hypothesis failed; counterexample and responsibility are retained. |
| **DONOR ABSORBED** | Stronger or equivalent prior mechanism owns the object; no ORION novelty is claimed. |
| **SATURATED** | Registered successor space added no exact value beyond the current envelope. |
| **OPEN** | A specific proof, comparator, resource model, transfer or novelty obligation remains. |

This vocabulary is intentional: a mature research programme should make it easy to distinguish “we know this” from “this is promising” and from “this failed.”

---

## Papers and research narratives

The repo is organizing the quantum work into distinct publication stories rather than mixing scientific and methodological claims.

- **Quantum mathematics / compiler theory:** exact expressivity and regime geometry of structured TARE/Pauli compilation.
- **Recursive recovery methodology:** how negative quantum results were frozen, diagnosed, donor-compared, replayed and either repaired or saturated.
- **Research instruments:** host-capability receipts, typed campaign control and controller/host agreement.
- **Typed partial knowledge:** mechanism-isolation studies of epistemic state under incomplete information.

See [`papers/`](papers/) and the quantum publication plan in [`papers/Q-paper-02-recursive-recovery/PUBLICATION_PLAN.md`](papers/Q-paper-02-recursive-recovery/PUBLICATION_PLAN.md).

---

## Current ORION platform status

The original minimum-kernel milestone remains achieved: ORION contains a modular solver, provider-neutral LLM/retrieval/verification ports, bounded-saturation gating, development-governance checks and a synchronized framework-paper tree.

Since that bootstrap stage, the repository has also accumulated substantial research infrastructure:

- proof/receipt-driven experiment programmes;
- exact and hostile verification lanes;
- reusable research harness/campaign machinery;
- protected-subject custody;
- independent replay records;
- research-paper claim/evidence ledgers;
- recursive negative-result recovery;
- domain extensions that can drive ORION itself as the research subject.

This is still **not** a claim that general autonomous research is solved. Live-provider reliability, open-web recall, real-domain transfer, robust global portrait reconstruction, route-level stopping, general novelty authority and governed Self-ORION remain active research problems.

---

## Repository map

```text
docs/
  00-foundation/       invariant principles and constitutional boundaries
  01-engine/           recursive epistemic reconstruction mechanics
  02-knowledge/        knowledge absorption and global-portrait mechanics
  03-evaluation/       benchmarks, evidence, authority and falsification
  04-self-development/ governed Self-ORION mechanics
  05-runtime/          LLM/retrieval/verifier integration boundary

development/           frozen protocols, closure packets, readiness and replay records

papers/                research manuscripts, publication packages, claim/evidence ledgers

research/
  assimilation/        knowledge/mechanism assimilation studies
  claim_expansion/     controlled claim-expansion programmes
  domains/             recursively organized external-domain research programmes
  extensions/          major research extensions (ORION-Q, ORION-QG, P6-P10, Meta-ORION, ...)
  failures/            failure cases and learned guards
  knowledge/           knowledge-structure research
  novelty/             novelty and donor-subtraction research
  development/         research used to develop ORION itself

packages/
  orion-research-harness/  replayable host-capability research orchestration

src/orion/
  core/                typed K/W/M state and invariant objects
  engine/              recursive operators and solver orchestration
  providers/           replaceable LLM/retrieval/verification ports + adapters
  runtime/             composition root for live integrations
  development/         development-governance contracts
  self_orion/          proposal-only self-development machinery

tests/
  unit/
  integration/
  hostile/

provenance/
  rakl/                migration ledger and immutable source references
```

Every substantial node should recursively own its `README/specification/evidence/benchmarks/history` material rather than scattering one subject across unrelated top-level folders.

---

## Development phases

1. **LLM-led bootstrap** — build the minimum working ORION consistent with the core principles. **Minimum kernel achieved.**
2. **Shadow Self-ORION** — ORION diagnoses itself and proposes improvements while external development remains primary. **Mechanisms and research controls actively under study.**
3. **Governed Self-ORION** — ORION becomes the primary problem-solving process for ordinary framework development; LLMs become major internal workers/proposers rather than the architecture itself. **Not yet generally authorized.**
4. **Self-sustaining research programme** — object knowledge, search-universe knowledge and method knowledge co-evolve under protected evaluation. **Research prototypes and bounded demonstrations exist; general closure remains open.**

The legacy `SzeChunYiu/RAKL` repository remains the provenance source for migrated mechanics, experiments, papers and negative history. ORION is a clean-generation reconstruction, not a history rewrite.

---

## Claim boundary

The repository contains theorem-grade mathematics, verified finite-domain results, real-public-subject confirmations, synthetic mechanism studies, proxy resource studies, refutations and donor absorptions. They are **not interchangeable**.

In particular, current ORION quantum work does **not** claim:

- a general quantum computational advantage;
- a universally superior block-encoding/compiler;
- a fundamentally new quantum algorithm solely from the grouped-QSVT/TARE compositions;
- that every low-support theorem survives arbitrary resource objectives;
- or that ORION is already a generally superior autonomous quantum scientist.

The strongest current scientific contribution is better described as **exact regime geometry of structured quantum compilation**: low-support normal forms, explicit coupling trades, objective-dependent phase boundaries, proof-carrying exact optimization and increasingly theorem-backed structural forecasting.
