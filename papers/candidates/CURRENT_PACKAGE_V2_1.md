# ORION-16–ORION-18 current normative package V2.1

**Date:** 2026-08-18  
**Supersession rule:** where an older V1/V2 artifact conflicts with a path named here, this package is normative.

## Programme

- Donor-complete architecture: `DONOR_COMPLETE_ORION_ENVELOPE_V1.md`
- Strong-baseline protocol: `DONOR_PRODUCT_EVALUATION_PROTOCOL_V2.md`
- Literature/ownership closure: `LITERATURE_CLOSURE_V2_2026-08-18.md`
- Canonical bibliography: `CANONICAL_BIBLIOGRAPHY_V2.md`
- Six-role adversarial review: `EXPERT_CLOSURE_REVIEW_V2.md`
- Venue paths: `VENUE_DECISION_V2.md`
- Submission summaries: `SUBMISSION_PACKAGE_V2.md`
- Normative completion terminal: `THEORY_COMPLETION_TERMINAL_V2_1.md`

## ORION-16 normative artifacts

- Final manuscript: `orion-16-formal-epistemic-structures-and-mechanics/manuscript/FINAL_V2_1.md`
- Formal core: `orion-16-formal-epistemic-structures-and-mechanics/manuscript/FORMAL_CORE_V2_1.md`
- Claim ledger: `orion-16-formal-epistemic-structures-and-mechanics/CLAIM_LEDGER_V2_1.md`
- Normative assumption checker: `orion-16-formal-epistemic-structures-and-mechanics/formal/check_theory_closure_v2_1.py`
- Supporting V2 checker: `orion-16-formal-epistemic-structures-and-mechanics/formal/check_theory_closure_v2.py`
- Reproduction: `orion-16-formal-epistemic-structures-and-mechanics/REPRODUCE_V2_1.md`
- Readiness: `orion-16-formal-epistemic-structures-and-mechanics/JOURNAL_READINESS_V2_1.md`

ORION-16 V2.1 incorporates the independent mathematical-completion lane's spurious-edge/minimality and footprint-fidelity objections. The V2 theorem wording without those premises is historical, not normative.

## ORION-17 normative artifacts

- Final manuscript: `orion-17-epistemic-navigation-open-worlds/manuscript/FINAL.md`
- Formal core: `orion-17-epistemic-navigation-open-worlds/manuscript/FORMAL_CORE_V2.md`
- Claim ledger: `orion-17-epistemic-navigation-open-worlds/CLAIM_LEDGER_V2.md`
- Theory checker: `orion-17-epistemic-navigation-open-worlds/formal/check_theory_closure_v2.py`
- Frozen contract cases: `orion-17-epistemic-navigation-open-worlds/benchmark/instances_v2.jsonl`
- Contract executor: `orion-17-epistemic-navigation-open-worlds/formal/check_contract_manifest_v2.py`
- Reproduction: `orion-17-epistemic-navigation-open-worlds/REPRODUCE_V2_1.md`
- Readiness: `orion-17-epistemic-navigation-open-worlds/JOURNAL_READINESS_V2.md`

The 8 contract cases are absorbed from the parallel mathematical-completion lane and include hidden branch, unknown/censored coverage, deceptive route diversity, dead-end revisit, beneficial representation change, harmful/unnecessary reframe, and non-retrieval experimental-design transfer.

## ORION-18 normative artifacts

- Final manuscript: `orion-18-epistemic-authority-autonomous-science/manuscript/FINAL.md`
- Formal core: `orion-18-epistemic-authority-autonomous-science/manuscript/FORMAL_CORE_V2_1.md`
- Supporting V2 core: `orion-18-epistemic-authority-autonomous-science/manuscript/FORMAL_CORE_V2.md`
- Claim ledger: `orion-18-epistemic-authority-autonomous-science/CLAIM_LEDGER_V2.md`
- Theory checker: `orion-18-epistemic-authority-autonomous-science/formal/check_theory_closure_v2_1.py`
- Supporting V2 checker: `orion-18-epistemic-authority-autonomous-science/formal/check_theory_closure_v2.py`
- Frozen authority cases: `orion-18-epistemic-authority-autonomous-science/benchmark/authority_cases_v2.jsonl`
- Contract executor: `orion-18-epistemic-authority-autonomous-science/formal/check_contract_manifest_v2.py`
- Reproduction: `orion-18-epistemic-authority-autonomous-science/REPRODUCE_V2_1.md`
- Readiness: `orion-18-epistemic-authority-autonomous-science/JOURNAL_READINESS_V2.md`

The 17 authority cases are absorbed from the parallel mathematical-completion lane and include clean authorized cases across all five domains, paired blocked cases, five explicit laundering attacks, `CANNOT_CHECK`, and a clean registered-coercion control.

## CI

Four candidate pytest wrappers are normative:

- `tests/unit/candidates/test_p6_p8_candidate_embedding.py`
- `tests/unit/candidates/test_p6_p8_theory_closure_v21.py`
- `tests/unit/candidates/test_p8_formal_core_primitives.py`
- `tests/unit/candidates/test_p6_p8_merged_review_suites.py`

Together they run live schema/native ORION embeddings, previous finite checks, preservation ladder, donor envelope, ORION-16 V2.1 assumption regressions, ORION-17/ORION-18 frozen contract manifests, ORION-18 primitive closure, and the merged hostile-review suites.

## Status vocabulary

`THEORY_FINISHED` means the declared formal object and known hostile theorem boundaries are closed.

It does not mean:

- every external donor implementation has been reimplemented inside this repository;
- a real-system superiority experiment has already been run;
- external peer review/acceptance occurred;
- Papers VI–VIII have been constitutionally promoted to flagships.

ORION remains free to absorb more donors. Any new donor that invalidates a theorem reopens the relevant theory; a donor that merely supplies a stronger implementation becomes part of the product baseline.
