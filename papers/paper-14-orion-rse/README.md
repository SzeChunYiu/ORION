# P14 — ORION-RSE

**Stable ID:** ORION-P14  
**Paper issue:** #669  
**Programme:** #670

## Canonical manuscript

`MANUSCRIPT.md` is the current peer-review manuscript and supersedes the stale candidate path on draft PR #715.

## Status

`PEER_REVIEW_PACKAGE_READY / SPECIFICATION_SEPARATED_GOVERNANCE_CONFORMANCE_SUPPORTED / EXTERNAL_SCIENTIFIC_VALIDITY_OPEN`

### P14A — preserved negative

`P14A_CONTROLLED_GOVERNANCE_SUPERIORITY_GATE_NOT_MET` remains permanent. The decisive negative-history discriminator occupied only 1.8375% of the realized mixed benchmark, so the registered aggregate separation gates failed. No threshold was changed.

### P14B — balanced semantic test with circularity boundary

Full ORION-RSE scored 0 false promotions / 1.0 disposition accuracy / 1.0 useful-discovery recall versus `MULTI_REVIEW` at 14.29% false promotion / 0.8571 accuracy over 6,720 balanced cases. However, the original full arm directly reused the gold decision function. P14B therefore remains useful as a semantic discriminator but is **not** treated as implementation-independent evidence.

### P14C — specification-separated successor

Frozen after the circularity issue was identified:

- 28 explicit adjudication cases in a separate specification artifact;
- four variants for each of seven scientific dispositions;
- gold/rationale/id/stratum stripped before every policy call;
- independently implemented full policy;
- six component ablations.

Result:

- full ORION-RSE disposition accuracy: **1.0000**;
- false promotion: **0**;
- useful-discovery recall: **1.0000**;
- strongest non-ORION `MULTI_REVIEW`: **0.857143** accuracy, **0.142857** false promotion;
- all six ablations worse;
- two-evaluation canonical SHA-256: `74032348de7e6508b6c1827aabcf1bf9d354d30b9c6f81c8259fdb3535f01a63`.

Terminal: `P14C_SPECIFICATION_SEPARATED_GOVERNANCE_CONFORMANCE_SUPPORTED`.

## Strongest paper claim

> Against a separately frozen adjudication specification whose gold labels are withheld from policy inputs, the full ORION-RSE implementation conforms strictly better than registered raw-positive, reflection/checklist, donor-aware and interaction-aware partial governance contracts without suppressing valid promotion.

## Artifacts

- `MANUSCRIPT.md`
- `CLAIM_EVIDENCE_LEDGER.md`
- `PEER_REVIEW_READINESS.md`
- P14A negative protocol/receipt/root-cause audit
- P14B balanced semantic protocol/harness/receipt
- P14C specification-separated protocol, case table, harness and result receipt

## Boundary

P14C removes direct implementation circularity but the adjudication specification is internally authored. Broader claims about scientific validity or research-agent superiority require blinded external adjudication, realistic multi-domain packets, matched agent workflows and longitudinal testing.
