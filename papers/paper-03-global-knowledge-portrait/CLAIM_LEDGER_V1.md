# ORION-P3 Claim Ledger V1

**Status:** ACTIVE. Claims are promoted only when the named artifact has the stated authority.  
**Manuscript map (2026-08-17):** `CLAIM_LEDGER_MANUSCRIPT_MAP_V1.md`. Checkbox audit: `evidence/JOURNAL_READINESS_CHECKBOX_AUDIT_2026-08-17.md`. Remaining `CANNOT_CHECK`: `evidence/CANNOT_CHECK_REMAINING_V1.md`.

| ID | Claim | Required artifact | Current authority/status |
|---|---|---|---|
| P3.C1 | ORION represents source-local scientific meaning with explicit referent/construct/measurement/context/modality/attribution coordinates. | `src/orion/knowledge/semantics.py`, local semantic tests | **IMPLEMENTED / LOCAL_ENGINEERING** |
| P3.C2 | ORION can distinguish aligned meanings from distinct referents, constructs, measurements, contextual differences and asserted contradictions. | `compare_meaning` hostile/unit tests | **IMPLEMENTED / LOCAL_ENGINEERING** |
| P3.C3 | ORION prevents invalid literature bridges when the pivot referent/construct/measurement changes. | `bridge_compatible` tests | **IMPLEMENTED / LOCAL_ENGINEERING** |
| P3.C4 | Public expert/manual resources can supply externally grounded structured cases without a new paid annotation campaign. | source registry + frozen public-reference gold/manifest | **EXECUTED / EXTERNAL-PUBLIC AUTHORITY** |
| P3.C5 | On a prospectively execution-frozen public-reference holdout, ORION's typed mapping calculus reduces false merges versus flat predicate canonicalization while remaining non-inferior in false splits to an exact-coordinate conservative control. | `gold/adjudicated/public-reference-v1.1-confirmatory/` + `evidence/public-reference-v1.1-confirmatory/` | **CONFIRMED IN FROZEN NARROW SCOPE** — disjoint n=32; false merge 0.000 vs 0.1875; paired delta -0.1875, 95% CI [-0.34375,-0.0625]; false-split delta 0.000 [0.000,0.000]; predeclared primary verdict PASS |
| P3.C6 | Every individual semantic-coordinate family has measurable marginal value. | targeted coordinate ablation results on authoritative cases | **PARTIAL ONLY** — obstruction and modality/polarity/attribution/discourse are supported on both public-reference samples; zero effects for referent/construct/measurement/context are coverage-limited and do not license necessity or dispensability claims |
| P3.C7 | ORION improves raw-text end-to-end scientific integration relative to model/RAG/schema baselines. | original `P3.cross-domain-atlas.v1` expert-gold model run | **CANNOT_CHECK / stronger follow-up** |
| P3.C8 | ORION improves downstream scientific answer quality. | frozen downstream task and external result artifact | **CANNOT_CHECK** |
| P3.C9 | The public-reference mapping result is independently reproducible and prospectively replicable. | immutable source registry, portable gold manifests, execution-frozen confirmatory manifest, deterministic evaluator, independent replay | **SATISFIED FOR PUBLIC-REFERENCE ROUTE** — primary gold SHA `35f9e39b...54ed8`; disjoint confirmatory gold SHA `13a76c68...2782b`; execution identities frozen before confirmatory outputs |

## Promotion rule

A manuscript sentence may not state a stronger authority than this ledger.

In particular:

- local exact worlds cannot be cited as real-world adequacy;
- public-reference mapping results concern already-structured projections, not raw-text extraction quality;
- both 32-case public-reference atlases cover only three case families and cannot be described as completion of the original eight-family end-to-end gold study;
- the initial 32 cases are not pooled into the confirmatory verdict;
- zero ablation effect on an unsupported/weakly supported coordinate is not evidence that the coordinate is unnecessary;
- an LLM/proxy/simulated label cannot be cited as gold;
- `CANNOT_CHECK` claims C7/C8 remain explicit in Results/Limitations until their named artifacts exist.

## Frozen public-reference evidence

Initial mapping evidence:

- `gold/adjudicated/public-reference-v1/`;
- `evidence/public-reference-v1/`.

Prospectively frozen disjoint confirmation:

- `protocol/PUBLIC_REFERENCE_CONFIRMATORY_EXECUTION_V1.json`;
- `gold/adjudicated/public-reference-v1.1-confirmatory/`;
- `evidence/public-reference-v1.1-confirmatory/`.

The confirmatory holdout was selected/frozen with zero overlap before confirmatory system outputs, then executed only after the exact gold hash, source revisions, evaluator Git blobs, margins and pass rule were bound in an `EXECUTION_FROZEN` manifest. `P3.C5` is therefore promoted from an initial narrow result to a replicated narrow mapping result. This still provides no authority for C7/C8.
