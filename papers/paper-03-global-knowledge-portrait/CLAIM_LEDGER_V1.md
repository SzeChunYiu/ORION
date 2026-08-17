# ORION-P3 Claim Ledger V1

**Status:** ACTIVE. Claims are promoted only when the named artifact has the stated authority.

| ID | Claim | Required artifact | Current authority/status |
|---|---|---|---|
| P3.C1 | ORION represents source-local scientific meaning with explicit referent/construct/measurement/context/modality/attribution coordinates. | `src/orion/knowledge/semantics.py`, local semantic tests | **IMPLEMENTED / LOCAL_ENGINEERING** |
| P3.C2 | ORION can distinguish aligned meanings from distinct referents, constructs, measurements, contextual differences and asserted contradictions. | `compare_meaning` hostile/unit tests | **IMPLEMENTED / LOCAL_ENGINEERING** |
| P3.C3 | ORION prevents invalid literature bridges when the pivot referent/construct/measurement changes. | `bridge_compatible` tests | **IMPLEMENTED / LOCAL_ENGINEERING** |
| P3.C4 | Public expert/manual resources can supply externally grounded structured cases without a new paid annotation campaign. | source registry + frozen public-reference gold/manifest | **EXECUTED / EXTERNAL-PUBLIC AUTHORITY** — 32-case atlas frozen on `main` |
| P3.C5 | On the frozen public-reference atlas, ORION's typed mapping calculus reduces false merges versus flat predicate canonicalization while retaining accepted mappings. | `gold/adjudicated/public-reference-v1/` + `evidence/public-reference-v1/` | **SUPPORTED IN FROZEN NARROW SCOPE** — false merge 0.000 vs 0.125; paired delta -0.125, 95% CI [-0.250,-0.03125] |
| P3.C6 | Every individual semantic-coordinate family has measurable marginal value. | targeted coordinate ablation results on authoritative cases | **PARTIAL ONLY** — obstruction and modality/polarity/attribution/discourse are supported on the current atlas; zero effects for referent/construct/measurement/context are coverage-limited and do not license necessity or dispensability claims |
| P3.C7 | ORION improves raw-text end-to-end scientific integration relative to model/RAG/schema baselines. | original `P3.cross-domain-atlas.v1` expert-gold model run | **CANNOT_CHECK / stronger follow-up** |
| P3.C8 | ORION improves downstream scientific answer quality. | frozen downstream task and external result artifact | **CANNOT_CHECK** |
| P3.C9 | The public-reference atlas is independently reproducible. | immutable source registry, portable gold manifest, deterministic evaluator, independent replay | **SATISFIED FOR PUBLIC-REFERENCE ROUTE** — byte-identical second freeze; portable gold SHA-256 `35f9e39b75ff53b7f0ec82cd03ebcaaa82509ee0aea3f5b96aac3fd62c854ed8` |

## Promotion rule

A manuscript sentence may not state a stronger authority than this ledger.

In particular:

- local exact worlds cannot be cited as real-world adequacy;
- public-reference mapping results concern already-structured projections, not raw-text extraction quality;
- the 32-case atlas covers three case families and cannot be described as completion of the original eight-family end-to-end gold study;
- zero ablation effect on an unsupported/weakly supported coordinate is not evidence that the coordinate is unnecessary;
- an LLM/proxy/simulated label cannot be cited as gold;
- `CANNOT_CHECK` claims C7/C8 remain explicit in Results/Limitations until their named artifacts exist.

## Frozen public-reference evidence

Canonical artifacts:

- `gold/adjudicated/public-reference-v1/PUBLIC_REFERENCE_GOLD_V1.jsonl`;
- `gold/adjudicated/public-reference-v1/PUBLIC_REFERENCE_FREEZE_MANIFEST_V1.json`;
- `evidence/public-reference-v1/BUILD_REPORT.json`;
- `evidence/public-reference-v1/SUMMARY.json`;
- `evidence/public-reference-v1/ANALYSIS.json`;
- `evidence/public-reference-v1/PROVENANCE.env` and `SHA256SUMS`.

`P3.public-reference-mapping.v1` therefore closes C4, C5 and C9 in their stated narrow scope. It provides partial evidence for C6 and no authority for C7/C8.
