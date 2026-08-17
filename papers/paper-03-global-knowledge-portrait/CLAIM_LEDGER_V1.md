# ORION-P3 Claim Ledger V1

**Status:** ACTIVE. Claims are promoted only when the named artifact has the stated authority.

| ID | Claim | Required artifact | Current authority/status |
|---|---|---|---|
| P3.C1 | ORION represents source-local scientific meaning with explicit referent/construct/measurement/context/modality/attribution coordinates. | `src/orion/knowledge/semantics.py`, local semantic tests | **IMPLEMENTED / LOCAL_ENGINEERING** |
| P3.C2 | ORION can distinguish aligned meanings from distinct referents, constructs, measurements, contextual differences and asserted contradictions. | `compare_meaning` hostile/unit tests | **IMPLEMENTED / LOCAL_ENGINEERING** |
| P3.C3 | ORION prevents invalid literature bridges when the pivot referent/construct/measurement changes. | `bridge_compatible` tests | **IMPLEMENTED / LOCAL_ENGINEERING** |
| P3.C4 | Public expert/manual resources can supply externally grounded structured cases without a new paid annotation campaign. | `PUBLIC_REFERENCE_SOURCE_REGISTRY_V1.json` + upstream immutable locators | **DESIGN_GROUNDED; final case manifest pending** |
| P3.C5 | On the frozen public-reference atlas, ORION reduces false merges versus flat canonicalization while retaining useful integrations. | frozen `cases.jsonl`, baseline outputs, paired statistics | **CANNOT_CHECK until atlas freeze/run** |
| P3.C6 | Referent/construct/measurement/context coordinates have measurable marginal value. | coordinate ablation results on frozen atlas | **CANNOT_CHECK until atlas freeze/run** |
| P3.C7 | ORION improves raw-text end-to-end scientific integration relative to model/RAG/schema baselines. | original `P3.cross-domain-atlas.v1` expert-gold model run | **CANNOT_CHECK / stronger follow-up** |
| P3.C8 | ORION improves downstream scientific answer quality. | frozen downstream task and external result artifact | **CANNOT_CHECK** |
| P3.C9 | The public-reference atlas is independently reproducible. | immutable source registry, case manifest, deterministic evaluator, independent replay | **PARTIAL; replay pending final atlas** |

## Promotion rule

A manuscript sentence may not state a stronger authority than this ledger.

In particular:

- local exact worlds cannot be cited as real-world adequacy;
- a public-reference design document cannot be cited as an empirical result;
- an LLM/proxy/simulated label cannot be cited as gold;
- `CANNOT_CHECK` claims remain explicit in Results/Limitations until their named artifact exists.

## Public-reference route boundary

`P3.public-reference-mapping.v1` is intended to close **C5/C6** without paid new annotation by reusing already-human/expert-annotated public resources. It does not automatically close **C7/C8**.
