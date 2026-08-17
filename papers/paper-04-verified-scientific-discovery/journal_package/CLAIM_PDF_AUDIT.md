# ORION-P4 independent claim / PDF audit

Audit subject: `b7cfaecfb55d9ad6c12fb59374935769ed8d8787`. Not a #283 verification record.

| ID | Claim | Artifact | Status |
|---|---|---|---|
| P4.H1 | 0/360 vs 180/360 false promotions; effect -0.50, CI [-0.553,-0.447] | `evidence/protected_v2/PUBLICATION_METRICS_V2.json` | SUPPORTED |
| P4.H2 | 60/60 clean promotions both systems | same | SUPPORTED |
| P4.H3 | Superior correct `CANNOT_CHECK` | same (`hypotheses.H3.status`) | **NOT_SUPPORTED** |
| P4.PDF | Independent final PDF proofread of an in-tree PDF | no PDF file in the git tree | **OPEN** |

H3 remains a retained null. The paper-declared terminal `PEER_REVIEW_READY` is recorded but this package stays `SCAFFOLDING` until an in-tree or DOI-bound PDF is present. Release SHA `f2ede371…3ccf` is identity evidence for a remote artifact, not a tracked file this checker can hash.
