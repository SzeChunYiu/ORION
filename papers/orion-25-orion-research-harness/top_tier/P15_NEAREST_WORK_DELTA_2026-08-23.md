# ORION-25 nearest-work delta — 2026-08-23

**Programme:** #977 / issue #979  
**Status:** current promotion-wave pressure; final submission refresh still required.

## Artifact-centered claim-aware observability

Yin, Du, Prince and Cherukara, *Artifact-centered Claim-aware Observability for Autonomous Scientific Agents*, arXiv:2608.18312, 2026-08-18.

The work argues that tracing model calls alone is insufficient for autonomous science and makes artifacts, claims, evidence bindings, verification records, lineage, archives, runs and steering relations first-class. It explicitly positions itself as complementary to telemetry/provenance standards and notes export to PROV-O/RO-Crate.

**Disposition: ADOPT / donor-own.**

ORION-25 does not claim novelty for claim-aware artifact lineage, explicit claim-evidence binding, verification-record observability or scientific-agent audit graphs.

https://arxiv.org/abs/2608.18312

## RO-Crate 1.3 / Workflow Run RO-Crate

RO-Crate 1.3 is the current 2026 recommendation for packaging/describing research objects; Workflow Run RO-Crate profiles capture provenance of computational workflow execution at multiple granularities including inputs, outputs, tools, steps and intermediate products.

**Disposition: ADOPT / interoperability donor.**

ORION-25 must interoperate with/export to established provenance/research-object representations rather than creating a competing metadata universe.

- https://www.researchobject.org/ro-crate/specification/1.3/index.html
- https://www.researchobject.org/workflow-run-crate/

## Evidence tracing and execution provenance in LLM agents

Wang et al., *From Agent Traces to Trust: Evidence Tracing and Execution Provenance in LLM Agents*, arXiv:2606.04990, 2026.

The survey treats evidence/tool/memory/environment/action/final-answer relations and execution provenance as a broad trust/audit layer.

**Disposition: ADOPT / donor-own.**

ORION-25 does not claim generic execution provenance, tracing or auditability.

https://arxiv.org/abs/2606.04990

## Verification-infrastructure pressure

Recent 2026 work argues that autonomous scientific agents require stronger observable-by-default, scalable verification and attribution infrastructure.

**Disposition: ADOPT as motivation, not novelty.**

https://arxiv.org/abs/2607.26064

## ORION-25 upward residual after absorption

The surviving higher question is not whether an execution can be traced. It is:

> What executable conditions separate **attributable/replayable/agreed execution** from **scientifically admissible evidence** and from **authorized scientific promotion**, particularly when host failures, incomplete execution, stale/replayed receipts or scientifically invalid but perfectly receipted outputs occur?

The protected V1 result demonstrates this separation on a frozen 18-case fault model. The top-tier external claim still requires real interoperability and broad fault injection against actual provenance/replay systems.

## Nonclaims

ORION-25 does not claim first-of-kind status for:

- provenance;
- experiment/workflow packaging;
- claim-aware observability;
- evidence tracing;
- deterministic replay;
- content addressing;
- multi-lane redundancy/agreement;
- signed/attested execution;
- the general proposition that reproducibility is not correctness.

Its paper contribution must be the **scientific evidence-admission semantics and measured failure boundary over those donor layers**.
