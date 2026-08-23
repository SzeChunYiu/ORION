# ORION-RSE donor saturation addendum — rounds G/H

**Date:** 2026-08-20

**Parent ledger:** `DONOR_SATURATION_PROGRESS_V1.md`

**Terminal:** `MATERIAL_PARENT_DISCOVERY_CONTINUES__RSSI_NARROWED_AGAIN`

This addendum records two additional independent changed-vocabulary searches. Both produced material parents. Therefore the two-consecutive-no-material-change gate is still unmet.

---

## Round G — failure memory / negative knowledge under changing context

### Material parent

**Hanchun Wang, `Negative Knowledge as Failure-aware Shared Memory for AutoResearch`, arXiv:2606.21024, ICML 2026 AI4Research Workshop.**

The work makes failed research attempts first-class, bounded, typed records in a shared bank. A downstream research agent explicitly adopts or rejects those records before proposing the next experiment. It reports same-task retry gains and cross-task transfer on nonlinear PDE research tasks.

Additional relevant work:

- ACL 2026 Meta-Cognitive Memory Abstraction treats memory abstraction/reuse itself as learnable and explicitly targets negative transfer under distribution shift;
- classical iterated action/observation belief-change literature already models failed actions, uncertain action histories and non-elementary interaction between update and revision.

### New claim strikes

ORION-RSE cannot claim novelty for:

- storing failed scientific attempts as structured negative knowledge;
- requiring a downstream agent to consult/adopt/reject failure records;
- transferring negative research knowledge across tasks;
- treating failure memory as shared scientific infrastructure;
- recognizing that changing context can make naive memory reuse harmful.

### Residual refinement

The surviving failure-related question is narrower:

> after the **available scientific operator/action/framework space changes**, can the system determine whether an old negative-knowledge record's failure cause still applies, explicitly preserve/re-scope/reopen it, and demonstrate that this avoids both stale blacklisting and repeated known failures?

This is an applicability/migration problem, not a negative-memory invention claim.

Round disposition: `MATERIAL_CHANGE`.

---

## Round H — epistemic lineage / semantic rollback / co-evolving verifier

### Material parent 1

**Jun He & Deying Yu, `Replicating Belief, Not Bits: Epistemic State Replication for Agentic Systems`, arXiv:2607.09748 (2026).**

Key mechanisms:

- epistemic node state `K=(L,B)` separating an immutable evidence log `L` from stochastic evolving belief lineage `B`;
- Semantic Linearizability using verifier-bounded semantic compatibility;
- Bounded Eventual Coherence;
- structured epistemic deltas;
- Verifiable Semantic Rollbacks that prune faulty premises without context amnesia.

This is a direct parent for semantic belief lineage, evidence/log separation and rollback across evolving agent state.

### Material parent 2

**CoEvoSkills, arXiv:2604.01687 (2026).**

Key mechanisms:

- self-evolving structured multi-file skills;
- a separately instantiated, information-isolated surrogate verifier;
- verifier/test co-evolution driven by an opaque hidden-oracle failure bit;
- persistent skill-refinement context;
- cross-model transfer.

### Additional parent

**Self-Modifying Lean Proof Agents with Verifier-Grounded Benchmark Coevolution, arXiv:2607.17352 (2026)** remains a major direct parent for mutable scientific/reasoning workflow plus trusted checker and coevolving curriculum.

### New claim strikes

ORION-RSE cannot claim novelty for:

- immutable evidence log + mutable belief lineage;
- verifier-bounded semantic compatibility of evolving epistemic state;
- semantic rollback of faulty premises;
- self-evolving skills with an isolated verifier;
- verifier/test escalation driven by hidden-oracle failure;
- coevolution of agent capability and evaluation curriculum under a protected signal.

### RSSI narrowed again

`Recursive Scientific Standing Integrity` can remain a useful **benchmark property**, but not a broad new theoretical primitive.

The current candidate incremental residual is now:

> **scientific-standing migration under recursive framework evolution, where standing includes not only semantic belief but evidence applicability, dependency/obligation closure, negative-history applicability and external scientific authority; the migrated state must then support a second-generation successor without protected-evidence leakage.**

The difference from ESR is not “lineage” or “semantic rollback.” The proposed ORION residual must require scientific-status and authority semantics that ESR does not claim, and must be demonstrated in recursive scientific discovery rather than distributed-agent state replication.

The difference from CoEvoSkills / self-modifying Lean agents is not “isolated verification.” ORION must preserve/reopen scientific commitments across changes to the research framework and prove a future-generation effect under disjoint protected suites.

Round disposition: `MATERIAL_CHANGE`.

---

## Current donor-saturation state

Eight materially changing search rounds have now been recorded across the base ledger and this addendum.

The mandatory freeze criterion remains unmet:

```text
required: 2 consecutive NO_MATERIAL_CHANGE rounds
observed: 8 material-changing rounds in the recorded programme
```

Do not freeze novelty.

The next action is to build an exact interaction benchmark and strongest donor meta-product **before** spending more effort on a universal formalism. The benchmark itself can reveal whether a real integration residual exists.
