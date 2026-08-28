# Scientific Execution Integrity: Separating Attributable Execution from Valid Scientific Evidence

## Abstract

Autonomous research systems increasingly combine language models, tools, code execution, workflow engines, memory, experiment runners and multi-agent checks. This creates an execution-accountability problem: a scientific result can appear well logged, reproducible, or even independently repeated while still being invalid as scientific evidence. Existing provenance, workflow packaging, claim-aware observability and execution-tracing systems provide increasingly rich records of *what happened*. They do not, by provenance alone, establish that the recorded result satisfies the scientific contract needed for a claim, nor that a valid result is authorized for promotion.

We introduce **Scientific Execution Integrity (SEI)** as a fail-closed interface separating five levels that are often conflated in research automation: attributable execution, replayable execution, agreement between executions, scientific validity, and scientific claim authority. SEI treats provenance and replay as evidence about execution rather than substitutes for scientific correctness. We instantiate the interface in a prospectively frozen 18-case fault benchmark spanning host failure, output truncation, pre-reap publication, cleanup omission, stale and duplicated receipts, digest mismatch, invalid retry accounting, incomplete coverage, scientifically invalid but fully receipted output, and dual-lane agreement on the same invalid result. The protocol, case facts and independent gold dispositions were frozen before the reference checker was implemented.

On this bounded benchmark, a nominal log/exit-status policy achieves 27.8% exact disposition accuracy and falsely authorizes 13 results; a structured execution-receipt policy and a replay/agreement policy each achieve 72.2% accuracy but still admit two scientifically invalid results. The SEI reference contract obtains 18/18 exact dispositions, with zero false scientific authorization and zero false rejection of clean authorized cases. Executable witnesses also show that complete execution properties can be identical for valid and invalid scientific results, and that lane agreement can coexist with invalid science while lane disagreement can coexist with independently verified valid science.

The contribution is not a new provenance format. RO-Crate, Workflow Run RO-Crate, execution-provenance systems and recent claim-aware scientific-agent observability are treated as donor layers. SEI instead specifies the evidence-admission boundary that must sit above those layers. Our present result is three bounded studies rather than one, and real-system
interoperability is no longer among what remains required. Broad fault
injection, overhead measurement and production comparators still are, and
nothing below claims production superiority.

**The three-study arc.** All three are executed and receipt-bound on the same
frozen 22-case corpus — the 18 hostile SEI cases plus 4 real ORION workflow
receipts — each with an independent second implementation and deterministic
replay.

1. **SEI fault benchmark** (run `32645458435`) — the bounded comparative result
   this manuscript already carried.
2. **W3C PROV / RO-Crate 1.3 interoperability** (run `32655587115`) — the SEI
   admission boundary survives representation through standard research-object
   and provenance structures, so the separation is not obtained only by forcing
   users into an ORION-specific receipt format.
3. **Ed25519 attestation composition V2** (canonical run `32664075763`, with an
   independent deterministic-replay run `32665597624` whose artifact-member
   SHA-256 digests are identical).

**The third study's load-bearing result is a negative, and it is the reason the
arc matters.** Composed-signature validity is evidence about the key set, not
about key custody or fact truth. Under full key-set compromise the signature
layer detects `0/6`; hostile chain-as-science collapse false-promotes `12`
cases; the properly scoped cryptographic-only reading stays `CANNOT_CHECK`.
False rejection over the full valid workload is `0/11` at the chain layer and
`0/5` at disposition level.

That negative is the paper's own argument against reading attestation as
scientific validity: a correct signature over a compromised key set verifies
exactly as well as one over an honest set. Sections 3.2-3.3 measure that
statement: detection is flat in chain length (`1.000` at `k = 1, 2, 3`) while forged
chains accepted under one compromised domain fall `1.00` to `0.00` from `d = 1` to
`d = 2`, so the `0/6` above is the `d = 1` row rather than an unexplained limit. Active authority for all three:
`P15_ACTIVE_CLAIM_AUTHORITY_V3.json`.

## 1. Introduction

A research agent may perform an experiment, save every command, hash every input and output, reproduce the same result twice, and still be scientifically wrong. This possibility is easy to acknowledge informally but difficult to preserve in an automated research architecture. Engineering systems naturally reward observability and repeatability: a process that exits successfully, produces a receipt and replays deterministically looks healthier than one that crashes. Scientific authority, however, asks a different question. Was the right experiment performed? Was its output complete? Was the result interpreted under the correct specification? Did a representation or evaluator error invalidate the measurement? Does the evidence actually discharge the obligation required by the claim? Is any actor authorized to promote that claim?

The distinction becomes increasingly important as autonomous systems span multiple execution layers. Language-model agents invoke tools; tools spawn processes; processes produce files; workflow systems record provenance; independent lanes may repeat the computation; evaluators score outputs; and a research controller decides whether a result becomes evidence. A failure at any layer can be hidden by success at another. A host failure may be mistaken for a scientific negative. A truncated output may be parsed as a complete result. A stale receipt may be replayed under a new invocation. Two lanes may deterministically reproduce the same conceptual error. Conversely, two lanes may disagree even when an independent formal verifier establishes that one result is correct.

This paper asks a narrow but foundational systems question:

> **What must a research-execution layer establish before an execution record may enter scientific evidence, and which guarantees must remain explicitly outside that layer?**

Our answer is a layered interface, **Scientific Execution Integrity (SEI)**. The central design rule is that lower guarantees do not silently escalate:

\[
\text{attributable execution}
\not\Rightarrow
\text{replayable execution}
\not\Rightarrow
\text{agreement}
\not\Rightarrow
\text{scientific validity}
\not\Rightarrow
\text{authorized claim}.
\]

The arrows are not statements that the concepts are unrelated. Attribution and replay are valuable evidence. Agreement can increase confidence in reproducibility. The claim is instead a typing boundary: each higher judgment requires its own registered premises and authority.

### Contributions

This manuscript contributes four bounded objects.

1. **A five-level execution-to-science separation.** We define execution integrity independently from scientific validity and claim authority, making missing evidence fail closed rather than converting it into a scientific result.
2. **Executable invariants for research execution.** The reference contract enforces host/science separation, exact invocation/result binding, publication after required finalization phases, and explicit non-implications from coverage and agreement to scientific validity.
3. **A prospectively frozen fault benchmark.** Eighteen cases were frozen before checker implementation and include clean successes as well as hostile execution and scientific-validity failures, preventing an always-reject policy from winning.
4. **A bounded comparative result.** Plain log, structured receipt, replay/agreement and SEI semantics receive the same case facts. Richer execution provenance removes execution-laundering failures but still cannot, without using the independent scientific contract, distinguish scientifically invalid from valid fully receipted executions.

The paper does **not** claim generic provenance, claim-aware observability, deterministic replay, content addressing, multi-agent agreement or signed execution as novel. Nor does the V1 result establish superiority over production provenance/workflow systems. Those systems are donor layers with which a mature SEI implementation should interoperate.

## 2. Related work and ownership boundary

### 2.1 Research-object and workflow provenance

RO-Crate provides a portable research-object packaging and metadata model, while Workflow Run RO-Crate profiles capture execution provenance at multiple granularities, including inputs, outputs, tools, steps and intermediate products. These are appropriate interoperability targets for SEI. ORION-25 does not introduce a competing metadata vocabulary as its contribution.

### 2.2 Agent execution provenance and evidence tracing

Recent agent research connects retrieved evidence, tool calls, memory, observations, intermediate claims, actions and final answers into auditable execution graphs. This work owns the general execution-provenance and traceability problem. SEI consumes such a graph as evidence about execution state.

### 2.3 Claim-aware scientific-agent observability

Very recent work makes claims, artifacts, evidence bindings and verification records first-class objects for scientific-agent observability and explicitly proposes complementing conventional telemetry/provenance standards. This closes another tempting but incorrect novelty route for ORION-25: claim-aware lineage itself is donor territory.

### 2.4 Reproducibility and replication

Reproducibility systems answer whether an execution can be repeated under a declared environment and inputs. Replication and scientific validation may additionally test whether a scientific claim survives independent data, assumptions or evaluators. SEI treats these as distinct contracts. A reproducibility receipt is evidence for one layer, not a universal scientific-success token.

### 2.5 ORION-25 residual

After donor absorption, the surviving object is the **admission relation** between execution evidence and scientific evidence. We study when an execution result may be admitted, held as invalid, or marked `CANNOT_CHECK`, and when a scientifically valid result still lacks claim-promotion authority.

## 3. Model

Let an invocation be identified by a content-bound record

\[
I=(id, occurrence, input, tool, environment, budget, policy).
\]

An execution record contains process and artifact facts such as spawn status, exit status, output bounds, reaping/finalization state, cleanup state, retry accounting, digests and coverage. We write

\[
E(I)\in\{\text{valid execution},\text{invalid execution},\text{unknown}\}.
\]

A scientific contract is a separate externally supplied predicate or adjudication interface

\[
S(I,R)\in\{\text{valid science},\text{invalid science},\text{unknown}\},
\]

where `R` is the candidate result. Finally, claim authority is represented by

\[
A(I,R,C)\in\{\text{authorized},\text{not authorized},\text{unknown}\}
\]

for claim `C`.

SEI emits five operational dispositions:

- `AUTHORIZED_SCIENCE`;
- `VALID_BUT_NOT_AUTHORIZED`;
- `INVALID_SCIENCE`;
- `EXECUTION_INVALID`;
- `CANNOT_CHECK`.

The reference decision ordering is intentionally asymmetric. Execution integrity is checked before scientific validity because a scientifically meaningful evaluator should not be asked to certify bytes whose provenance/completeness is itself untrustworthy. Scientific validity is checked before claim authority because authority cannot repair an invalid result. Missing scientific or authority evidence produces `CANNOT_CHECK` rather than promotion.

### 3.1 Execution-integrity conditions

The V1 interface requires:

- successful spawn/host capability under the registered access model;
- no unresolved timeout/termination failure;
- correct exit semantics;
- complete bounded output rather than silent truncation;
- process reap before final authoritative publication;
- required cleanup/unregistration;
- valid retry accounting;
- exact invocation/input/result binding;
- unique and fresh occurrence identity;
- declared execution coverage.

These are not proposed as a universal minimal set. They instantiate the failure classes present in the ORION harness programme and define the V1 benchmark boundary.

### 3.2 What attestation attests: trust domains, not chain length

Section 3.1 constrains a single execution. The composition study adds a chain of role
attestations over it, and the abstract already records that study's negative: composed
signature validity is evidence about the key set, not about key custody. That statement
is qualitative. It can be measured, and the measurement locates the boundary precisely.

Write `k` for the number of attestation roles in the chain and `d` for the number of
**independent trust domains** holding their keys. The V2 composer derives every role key
from a shared seed, `sha256(b"P15-ATTESTATION-COMPOSITION-V2-KEY-" + role + case_id)`.
Anyone able to run the composer derives every role key, so **the composition operates at
`d = 1` regardless of `k`.**

Varying each axis separately (`experiments/execution-integrity-v1/`) separates two
readings that the qualitative statement leaves entangled:

| axis varied | measurement | outcome |
|---|---|---|
| chain length `k` at `d = 1` | detection over signature, key, chaining, order, splice and fact tampering | **flat**: 1.000 at `k = 1, 2, 3` |
| trust domains `d` at `k = 3`, one domain compromised | forged chains accepted | **1.00 → 0.00 → 0.00** for `d = 1, 2, 3` |

Detection does not improve with chain length. Every link is independently signed and
chained, so a tamper anywhere is caught by that link's own signature check irrespective
of how many links surround it. Resistance to compromise, by contrast, steps sharply on
the first genuine separation of key custody.

This gives the abstract's `0/6` full-compromise detection a mechanism rather than
leaving it as an unexplained limit: it is the `d = 1` row. One compromise yields the
entire key set, so the chain can be rewritten wholesale, and the effect disappears at
`d = 2` where the attacker holds only part of it.

We do not claim a general trust-domain theorem. The measurement is on `n = 4` real
workflow receipts under single-domain compromise with `k` fixed at 3, and `d = 2` versus
`d = 3` is flat only because a single compromise already fails to forge. `k = 5` is
untested; the flat result in `k` makes it uninformative rather than merely unfinished.

### 3.3 Content integrity is attested; liveness is not

The independent checker verifies an **artifact**, not a **run**. It carries no binding to
the process that produced the bytes. Killing the composer mid-execution while a previous
valid artifact remains on disk leaves that artifact verifying green
(`HOST_PROCESS_FAULT_RESULT_V1.json`, `SIGKILL` and `SIGTERM` cases).

That is correct behaviour for an artifact verifier and it is not a defect in the
attestation. It is a boundary a consumer must not cross: a pipeline treating a green
checker as evidence that *this* execution succeeded obtains a false success signal from a
correct verifier. Liveness must be established by the orchestrator that launched the run.

The observation also bears on the previous subsection. No value of `k` establishes
liveness, because chain length says nothing about whether the process ran; a witness in a
different trust domain does. Content integrity and execution liveness are distinct
properties, and only the first is attested here.

## 4. Five executable invariants

### H15.1 Host/science separation

A host or execution-integrity failure cannot be represented as scientific success solely because output text resembles a result. The V1 benchmark includes spawn failure, timeout and nonzero completion with plausible output.

### H15.2 Exact binding

A result must belong to the invocation under adjudication. Stale receipt reuse, duplicate occurrence identity, mismatched result digest and incomplete output all block authoritative execution success in V1.

### H15.3 Publication atomicity

Authoritative publication occurs only after the lifecycle phases required by the registered execution contract. V1 contains pre-reap finalization, cleanup omission and corrupted retry accounting as counterexamples.

### H15.4 Coverage and receipt completeness do not imply scientific validity

The pair `SEI-CLEAN-AUTH` and `SEI-COMPLETE-INVALID-SCIENCE` is deliberately identical on the frozen execution/replay coordinates. Both are attributable, complete and replayable. Only the independent scientific contract differs. Any policy that promotes solely from execution evidence must therefore give them the same scientific decision and be wrong on at least one.

### H15.5 Agreement does not imply validity

`SEI-DUAL-AGREE-WRONG` records two agreeing lanes whose independently checked science is invalid. Conversely, `SEI-DUAL-DISAGREE-VERIFIED` contains lane disagreement but an independent scientific verifier and valid promotion authority. Agreement is therefore a reproducibility/consistency coordinate, not the scientific correctness oracle in the declared interface.

## 5. Prospective fault benchmark

### 5.1 Chronology

The protocol was committed first. The 18 case-fact records were committed next, followed by a separate gold-disposition file. Only then was the reference checker implemented. CI executes the checker twice and requires byte-identical output before recording a GREEN terminal.

### 5.2 Fault classes

The frozen cases cover clean authorized science, valid science without promotion authority, host/spawn failure, timeout, nonzero misleading output, truncation, publication before reap, cleanup omission, retry corruption, stale replay, duplicate occurrence, digest forgery, coverage omission, fully receipted invalid science, dual-lane agreement on invalid science, dual-lane disagreement with unknown validity, dual-lane disagreement resolved by an independent verifier, and valid science with unavailable claim authority.

### 5.3 Comparator semantics

`plain_logs` approximates nominal process-success logic: spawn, no timeout, exit 0, and output present.

`structured_receipt` additionally requires the V1 execution-integrity conditions. It intentionally stops at execution validity.

`replay_agreement` adds deterministic replay and, for dual-lane cases, agreement. It therefore represents a stronger reproducibility product.

`SEI` performs the same execution checks, then consults the independent scientific contract, then separately consults claim authority.

All comparators receive the same case record. No system gets hidden execution facts. The scientific fields are visible to all; the benchmark asks whether a semantics uses them rather than treating execution success as scientific authority.

## 6. Results

The protected CI run `32645458435` emitted `P15_SEI_BOUNDED_FAULT_V1_GREEN` and reproduced byte-for-byte on a second execution.

| System | Exact disposition accuracy | False authorized science | Execution-invalid admitted | Invalid science admitted | Valid/no-authority laundering |
|---|---:|---:|---:|---:|---:|
| Plain logs | 27.8% | 13 | 8 | 2 | 1 |
| Structured receipt | 72.2% | 5 | 0 | 2 | 1 |
| Replay/agreement | 72.2% | 4 | 0 | 2 | 1 |
| SEI | 100% | 0 | 0 | 0 | 0 |

The progression is informative. Structured receipts eliminate the execution-integrity failures that nominal exit/output semantics launder into success. Adding replay/agreement helps distinguish some ambiguous execution states but still admits both invalid-science cases. In particular, lane agreement does not repair the invalid scientific contract. It also rejects one independently verified valid result because the lanes disagree, illustrating that agreement can be too strong if treated as correctness rather than as a separate property.

SEI emits two `AUTHORIZED_SCIENCE` cases, one `VALID_BUT_NOT_AUTHORIZED`, two `INVALID_SCIENCE`, eleven `EXECUTION_INVALID` and two `CANNOT_CHECK` cases, exactly matching frozen gold.

These numbers should not be read as prevalence estimates. The corpus is adversarial and deliberately balanced around failure semantics. The result establishes the logical/system boundary on V1, not an expected production error rate.

## 7. Relationship to the ORION research harness

The ORION research harness motivated several V1 fault classes and contains implementation tests for bounded output, strict receipts, race-safe publication, invalid-content recovery and execution coverage. The paper result is nevertheless kept separate from implementation self-certification. A reference semantics passing a finite benchmark does not prove that every host/process race in the implementation conforms to it.

This separation is intentional. Production harness evaluation should treat the SEI contract as an external oracle: inject faults into the implementation, derive receipts, and ask whether the implementation's admitted scientific evidence matches the independent contract. The implementation should not generate its own gold.

The ORION-Q dual harness supplies a second architectural pressure: lane agreement is useful, but it must be typed as agreement rather than scientific correctness. The V1 benchmark encodes both agreement-with-invalidity and disagreement-with-independent-validity cases for this reason.

## 8. External promotion programme

A top-tier systems claim requires substantially more than V1.

First, SEI must interoperate with real research-object/provenance infrastructure. The natural direction is to import/export execution evidence through RO-Crate/Workflow Run RO-Crate or equivalent provenance structures while retaining scientific validity/authority as separate contracts.

Second, the benchmark must move from semantic case records to fault injection against actual systems. This includes host/process faults, output-boundary attacks, stale/replayed artifacts, lifecycle races and scientifically invalid-but-well-receipted outputs. Comparator systems should be configured according to their strongest documented semantics rather than artificially weakened.

Third, the study must measure false rejection and overhead. A system that rejects every execution is safe but useless. Storage, runtime, receipt size, replay overhead and recovery cost should be reported separately rather than hidden in one post-hoc scalar.

Fourth, implementation and adjudication must be independent. A second implementation of the SEI contract or an external evaluator should reproduce dispositions from the same frozen fault artifacts.

## 9. Limitations

V1 is a bounded semantic fault model. The 18 cases were authored to exercise known distinctions and therefore cannot estimate natural failure prevalence. The comparator policies are semantic abstractions, not production implementations of RO-Crate, workflow engines or attested-execution systems. The result also assumes that an independent scientific contract can be supplied. In open-ended science, that contract may itself return `CANNOT_CHECK` or require expert adjudication.

SEI also does not solve epistemic authority in general. It merely keeps execution integrity from impersonating scientific validity and keeps scientific validity from impersonating claim authority. The richer scientific-discharge semantics are owned elsewhere in ORION (notably ORION-18), while research-decision governance is studied by ORION-24.

## 10. Conclusion

Research execution is becoming more observable, reproducible and agentic. That progress makes a clean boundary more—not less—important. A complete trace can document a bad experiment perfectly. Two independent lanes can reproduce the same wrong result. A scientifically valid result can still lack authority to become a published claim.

Scientific Execution Integrity treats these as typed stages. In a prospectively frozen adversarial benchmark, that separation eliminates the false scientific promotions retained by nominal logs, structured execution receipts and replay/agreement semantics while preserving clean valid cases. The next step is not to invent a new provenance format; it is to test whether this admission boundary composes with real provenance/workflow infrastructure and survives broad production fault injection at acceptable cost.
