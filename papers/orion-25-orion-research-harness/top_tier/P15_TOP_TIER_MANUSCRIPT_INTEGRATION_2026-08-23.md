# P15 top-tier manuscript integration — 2026-08-23

This note bridges the current `MANUSCRIPT.md` (which already contains the bounded SEI fault result) to the later provenance-interoperability and attestation-composition evidence. It changes no scientific terminal.

## One-sentence paper identity

**P15 defines the scientific evidence-admission boundary above execution provenance and attestation.** Provenance and signatures can make execution attributable, portable, replayable and tamper-evident; they do not, by themselves, establish scientific validity or claim authority.

## Revised empirical arc

### 1. SEI fault study — keep as the foundation

Retain the existing 18-case prospective benchmark as the first empirical section:

- plain log/exit policy: 27.8% exact, 13 false authorized-science decisions;
- structured receipt/provenance: 72.2%, 5 false authorized-science decisions;
- replay/agreement product: 72.2%, 4 false authorized-science decisions;
- SEI: 18/18 exact, 0 false authorized science.

The two load-bearing scientific witnesses remain:

- complete/replayable execution can still be scientifically invalid;
- lane agreement can be wrong while lane disagreement can coexist with independent scientific validity.

### 2. Provenance interoperability — add immediately after SEI

Use `P15_PROVENANCE_INTEROP_RESULT_RECEIPT_V1.md` to answer the obvious reviewer objection: perhaps SEI works only because it uses a proprietary execution record.

It does not. Across 22 cases:

- W3C PROV-JSON normalized round trip = 1.0;
- RO-Crate 1.3 / Workflow-Run projection round trip = 1.0;
- native/import SEI disagreements = 0;
- scientific-field leakage = 0;
- real receipt false promotion/rejection = 0;
- independent implementation agrees.

Interpretation: provenance representation and scientific admission compose, but remain separate layers.

### 3. Chained Ed25519 attestation — new primary systems result

Use `P15_ATTESTATION_COMPOSITION_RESULT_RECEIPT_V2.md` as the strongest systems extension.

The chain is:

`execution -> environment -> publication`.

On the frozen 22-case corpus:

- base verification 1.0;
- truncation 66/66 detected;
- substitution 22/22;
- splice 22/22;
- reorder 22/22;
- replay 22/22;
- stale reuse 22/22;
- valid-workload chain false rejection 0;
- scientific-disposition false rejection 0;
- chain + SEI gold agreement 22/22;
- independent checker agrees.

This result should be framed as **attestation composition above provenance**, not as a new signature scheme.

### 4. Full-key-compromise negative — make it prominent

Do not hide the `A-COMPROMISE-FULL` result in limitations. It is the theorem-like systems boundary the paper needs:

- 6 forged-clean fact sets re-signed with genuine keys;
- signature detections 0/6;
- false promotion 6/6 if signature validity is interpreted as fact/scientific truth;
- chain + SEI also false-promotes 6/6 if key custody is silently supplied as a true premise.

Required wording:

> A signature verifies a statement under a key. It does not verify key custody, fact truth, scientific validity or claim authority. Those are distinct premises/contracts.

This negative makes the composition result stronger, not weaker: P15 states exactly where cryptographic evidence stops.

## Abstract replacement target

The abstract should be updated from the current SEI-only ending to something approximately like:

> Autonomous research systems increasingly produce rich provenance, deterministic replays, multi-lane agreement and cryptographic attestations. These mechanisms establish important facts about execution, but can be silently over-read as evidence of scientific validity. We introduce Scientific Execution Integrity (SEI), a typed admission boundary separating attributable execution, replay, agreement, attestation, scientific validity and claim authority. In a prospectively frozen 18-case fault study, plain logs, structured provenance and replay/agreement achieve 27.8%, 72.2% and 72.2% exact scientific dispositions, while SEI is 18/18 with zero false scientific authorization. The separation survives real provenance interoperability: W3C PROV-JSON and RO-Crate/Workflow-Run round-trip execution facts on 22 cases with zero native/import decision disagreement or scientific-field leakage. A separately frozen three-link Ed25519 execution→environment→publication chain detects all registered truncation, substitution, splice, reorder, replay and stale-chain attacks with zero observed false rejection on the valid workload and exact independent-checker agreement. A full-key-compromise arm deliberately fails: forged facts re-signed with genuine keys are not detected, showing that signature validity does not establish key custody or fact truth. We claim bounded scientific evidence-admission semantics above provenance and attestation, not production-scale correctness or cryptographic truth.

## Contribution-list edits

Expand the current four contributions to six:

1. execution-to-science separation semantics;
2. executable lifecycle/fault invariants;
3. prospectively frozen 18-case SEI benchmark;
4. bounded SEI comparative result;
5. real provenance interoperability with independent implementation;
6. cryptographic chain composition plus explicit full-key-compromise boundary.

## Related-work edits

Add a dedicated attestation subsection. Donor ownership should be explicit:

- W3C PROV / RO-Crate own provenance representation;
- content-addressed execution/replay systems own execution reproducibility;
- Ed25519 / generic attestation systems own cryptographic statement authenticity;
- P15 owns none of those primitives.

P15's residual is the **non-laundering admission relation between execution evidence and scientific evidence/authority**.

## Results section order

1. SEI fault corpus and comparator result.
2. Provenance interoperability.
3. Attestation chain composition.
4. Full-key-compromise boundary.
5. Resource/overhead limitations and production roadmap.

## Sentences that must be removed or revised

Remove or revise current manuscript sentences saying:

- real-system interoperability remains entirely future work;
- independent implementation remains entirely future work;
- cryptographic proof-of-execution/attestation comparison is wholly unexecuted;
- P15 has only an 18-case semantics/fault study.

Do **not** replace them with:

- "attestation proves correctness";
- "signatures make scientific claims trustworthy";
- "key custody is verified";
- "production-scale reliability is established";
- "P15 is superior to existing provenance/attestation products."

## Remaining top-tier experiment

Do not add another small synthetic attestation benchmark. The missing experiment is **production breadth/cost**:

- broader process/host failure families (I/O readiness races, cap sentinels, cleanup/reap/finalization, retry accounting, stale publication, timeout/signal classes);
- larger valid workloads to estimate false rejection;
- runtime/storage overhead;
- if possible, one real production provenance/attestation stack as an interoperability/composition comparator, without pretending it provides the scientific layer P15 tests.

## Submission-day checklist

- update manuscript abstract/contributions/results using only bound receipts;
- regenerate claim ledger/figures directly from current receipts;
- run clean-environment SEI + provenance + attestation replay;
- refresh provenance/attestation/reproducibility literature immediately before submission;
- reconcile P13/P15 ownership: P13 owns responsibility-relative state/certificate reuse; P15 owns execution-evidence admission/attestation;
- run PDF clipping/content-binding audits;
- bind exact manuscript, result receipts, environment and final PDF bytes;
- keep `promotion_allowed=false` until those final gates are independently closed.
