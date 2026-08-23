# P15 Claim–Evidence Ledger

**Stable ID:** ORION-P15  
**Current authority:** `P15_ACTIVE_CLAIM_AUTHORITY_V3.json`  
**Lifecycle:** `BOUNDED_SCIENTIFIC_RESULT_EARNED`

Historical V1/V2 lifecycle files are retained as pre-result records; they no longer describe the current scientific state.

| Candidate statement | Current authority | Maximum authorized wording |
|---|---|---|
| execution-invalid cases can be kept outside authorized scientific success | **SUPPORTED / BOUNDED** | on the frozen 18-case SEI fault corpus, SEI is 18/18 exact with 0 false authorized science |
| structured provenance alone establishes scientific validity | **NEGATIVE / FALSE** | provenance can make execution attributable without deciding scientific validity or claim authority |
| replay + lane agreement establishes correctness | **NEGATIVE / FALSE** | agreement/replay is execution evidence; the frozen corpus contains agreement-with-invalid-science and disagreement-with-independent-validity witnesses |
| P15 scientific admission survives standard provenance representation changes | **SUPPORTED / BOUNDED / INDEPENDENT** | W3C PROV-JSON and RO-Crate/Workflow-Run round-trip normalized execution facts at 1.0 with 0 native/import disposition disagreement and 0 scientific-field leakage on 22 cases |
| cryptographic chain composition detects registered tamper/replay attacks | **SUPPORTED / BOUNDED / INDEPENDENT** | three-link Ed25519 chain detects all frozen truncate/substitute/splice/reorder/replay/stale attacks with 0 observed valid-workload false rejection; independent checker agrees |
| a valid signature proves the signed execution facts are true | **NEGATIVE / FALSE** | full-key-compromise arm has 0/6 signature detections and 6/6 false promotions if valid signatures are treated as scientific truth |
| key custody is established by successful signature verification | **NEGATIVE / FALSE** | key custody is an additional premise; it is not derived by the signature layer |
| chain + SEI is universally safe under compromised keys | **NEGATIVE / FALSE** | the frozen full-compromise arm yields 6/6 false promotions because the scientific contract inherits unregistered key-custody/fact-truth premises |
| the current P15 evidence establishes production-scale reliability | **NOT AUTHORIZED** | current evidence is bounded to the registered small hostile/interoperability/attestation corpora |
| P15 is superior to a real production provenance/attestation platform | **NOT AUTHORIZED** | no matched production-scale superiority study has been executed |
| P15 is top-tier submission ready | **NOT AUTHORIZED** | final production-breadth/overhead, clean replay, nearest-work and package-binding gates remain open |

## Bound scientific evidence

### SEI fault study

`top_tier/P15_SEI_RESULT_RECEIPT_V1.md`

- terminal `P15_SEI_BOUNDED_FAULT_V1_GREEN`;
- 18 frozen cases;
- SEI exact accuracy 1.0;
- false authorized science 0;
- plain logs false authorize 13; structured receipt/provenance 5; replay/agreement 4;
- explicit witnesses separate execution integrity, scientific validity and claim authority.

### Provenance interoperability

`top_tier/P15_PROVENANCE_INTEROP_RESULT_RECEIPT_V1.md`

- terminal `P15_PROVENANCE_INTEROP_V1_SUPPORTED`;
- independent terminal GREEN;
- 22 cases;
- W3C PROV-JSON round trip 1.0;
- RO-Crate/Workflow-Run projection round trip 1.0;
- native/import disagreements 0;
- scientific-field leakage 0;
- real-receipt false promotion/rejection 0.

### Attestation chain composition

`top_tier/P15_ATTESTATION_COMPOSITION_RESULT_RECEIPT_V2.md`

- run `32665597624`, artifact `9500055966`;
- terminal `P15_ATTESTATION_COMPOSITION_V2_SUPPORTED`;
- independent terminal `P15_ATTESTATION_COMPOSITION_V2_SECOND_CHECKER_GREEN`;
- execution→environment→publication chain;
- base verification 1.0;
- truncate 66/66, substitute 22/22, splice 22/22, reorder 22/22, replay 22/22, stale 22/22 detected;
- valid-workload false rejections 0;
- chain + SEI frozen-gold agreement 22/22;
- full key compromise: 0/6 signature detections, 6/6 false promotions if key custody/fact truth are silently assumed.

## Strongest authorized paper-level claim

> On the registered bounded studies, execution integrity, provenance representation, cryptographic attestation, scientific validity and claim authority are distinct layers. SEI prevents execution/replay/agreement evidence from self-authorizing science; the separation survives W3C PROV and RO-Crate/Workflow-Run import; and a three-link Ed25519 chain detects the registered non-compromise tamper/replay attacks without observed false rejection while explicitly failing to establish fact truth under full key compromise.

## Donor boundary

P15 absorbs, rather than claims ownership of:

- structured execution receipts and content addressing;
- deterministic replay;
- W3C PROV;
- RO-Crate / Workflow-Run provenance;
- Ed25519 signatures and generic attestation;
- independent lane agreement.

P15's residual is the **scientific evidence-admission separation above those mechanisms** and the failure modes created when one layer is allowed to self-promote into the next.

## Remaining claim gates

- broader production host/process fault campaign;
- runtime/storage/false-rejection overhead on larger valid workloads;
- clean-environment independent replay;
- immediate submission-day nearest-work refresh;
- final manuscript/evidence/environment/PDF binding.

Negative and boundary outcomes remain first-class evidence. In particular, the full-key-compromise result must not be removed or softened in order to claim cryptographic closure.
