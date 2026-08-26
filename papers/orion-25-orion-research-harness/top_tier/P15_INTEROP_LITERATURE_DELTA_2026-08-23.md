# P15 provenance/interoperability literature delta — 2026-08-23

This delta is submission-facing and donor-first. It does not assign novelty authority by itself.

## Donor layers that P15 must absorb

### W3C PROV

- PROV-DM: https://www.w3.org/TR/prov-dm/
- PROV Primer: https://www.w3.org/TR/prov-primer/

PROV owns the domain-agnostic interchange model for entities, activities, agents, usage, generation, derivation, association and responsibility. Its purpose is to represent and interchange asserted provenance so downstream systems can assess quality/trust/reproducibility. P15 therefore must not claim invention of entity/activity/agent provenance, provenance exchange or generic trust assessment.

### RO-Crate 1.3 and Workflow Run RO-Crate

- RO-Crate 1.3 Recommendation, published 2026-06-22: https://www.researchobject.org/ro-crate/specification/1.3/index.html
- Workflow Run / Provenance Run Crate 0.5: https://www.researchobject.org/workflow-run-crate/profiles/provenance_run_crate/
- Process Run Crate 0.5: https://www.researchobject.org/workflow-run-crate/profiles/process_run_crate/

RO-Crate owns portable research-object packaging; Workflow Run/Provenance Run Crate owns interoperable process/workflow execution provenance, including internal tool executions represented by `CreateAction` entities with `instrument` links. P15 must interoperate with these representations rather than replace them.

### Current Python interoperability libraries

- `prov` latest 3.x release (PyPI data verified 2026-08-07): https://pypi.org/project/prov/
- `rocrate` 0.15.1 (released 2026-07-10): https://pypi.org/project/rocrate/
- open ro-crate-py issue for explicit RO-Crate 1.3 support: https://github.com/ResearchObject/ro-crate-py/issues/258

The `prov` library supports W3C PROV-DM plus PROV-JSON, PROV-JSONLD, PROV-O and PROV-XML serialization/deserialization. `rocrate` 0.15.1 documents support through RO-Crate 1.2 while the 1.3 support issue remains open; P15 must not claim library-level 1.3 validation where the donor implementation does not yet provide it.

## Upward residual after donor absorption

P15's surviving question is not "can execution provenance be represented?" It is:

> **After provenance is represented and round-tripped correctly through standard donor formats, what additional evidence is required before an execution may be admitted as scientific evidence or an authorized scientific claim?**

The key non-implication remains:

`interoperable provenance + replay/attestation != scientific validity != scientific claim authority`.

A P15 interoperability result is valuable only if it demonstrates all of the following simultaneously:

1. donor provenance round-trips execution facts without P15-only hidden state;
2. P15 accepts donor provenance as execution evidence rather than forcing a proprietary provenance format;
3. donor provenance alone does not decide scientific validity when the scientific contract/evaluator is absent;
4. adding an independent scientific-validity/authority record yields the same fail-closed SEI disposition as the native representation;
5. real workflow receipts and hostile invalid-science cases both survive the conversion.

## Claim ceiling

Even a successful interoperability study does not establish superiority over all provenance/workflow/attestation systems. It can close the interoperability and representation-independence gaps and strengthen the claim that P15 is a **scientific-admission layer above provenance**, while production host fault breadth, cryptographic attestation products, overhead at larger scale and independent external adjudication remain separate gates.
