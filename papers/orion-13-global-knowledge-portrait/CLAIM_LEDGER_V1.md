# ORION-13 Claim Ledger V1

> **Record of the pre-rewrite manuscript, 2026-08-22.** The manuscript was
> subsequently rewritten so that its claims are about the mapping rule rather
> than about a named system, so that internal status tokens and claim
> identifiers do not appear in its prose, and so that repository paths,
> artifact filenames and content digests live only in Data and code
> availability. The claim wording below is the wording that was in force when
> this ledger was cut. **No number, authority, supporting artifact or status in
> this table changed in that rewrite**, and none has been edited here: a ledger
> is a record of what was allowed and on what evidence, so it is annotated
> rather than restated. Where a row names `ORION` as the subject of a claim,
> the rewritten manuscript states the same claim about the mechanism -- the
> implementation is named once, in Method, as the artifact under test. Where a
> row is marked `CANNOT_CHECK`, the manuscript now says the outcome remains
> undetermined, in those words; the boundary between "could not be determined"
> and "determined to be false" is stated in plain English in Method and is
> unchanged in substance.

**Status:** ACTIVE — scoped submission track selected in `SCOPED_PUBLICATION_TRACK_V1.md`. Claims are promoted only when the named artifact has the stated authority.  
**Manuscript map (2026-08-18):** `CLAIM_LEDGER_MANUSCRIPT_MAP_V1.md`. Historical checkbox audit: `evidence/JOURNAL_READINESS_CHECKBOX_AUDIT_2026-08-17.md`. Broad follow-up `CANNOT_CHECK` coordinates remain preserved rather than promoted.

| ID | Claim | Required artifact | Current authority/status |
|---|---|---|---|
| ORION-13.C1 | ORION represents source-local scientific meaning with explicit referent/construct/measurement/context/modality/attribution coordinates. | `src/orion/knowledge/semantics.py`, local semantic tests | **IMPLEMENTED / LOCAL_ENGINEERING** |
| ORION-13.C2 | ORION can distinguish aligned meanings from distinct referents, constructs, measurements, contextual differences and asserted contradictions. | `compare_meaning` hostile/unit tests | **IMPLEMENTED / LOCAL_ENGINEERING** |
| ORION-13.C3 | ORION prevents invalid literature bridges when the pivot referent/construct/measurement changes. | `bridge_compatible` tests | **IMPLEMENTED / LOCAL_ENGINEERING** |
| ORION-13.C4 | Public expert/manual resources can supply externally grounded structured cases without a new paid annotation campaign. | source registry + frozen public-reference gold/manifest | **EXECUTED / EXTERNAL-PUBLIC AUTHORITY** |
| ORION-13.C5 | On a prospectively execution-frozen public-reference holdout, ORION's typed mapping calculus reduces false merges versus flat predicate canonicalization while remaining non-inferior in false splits to an exact-coordinate conservative control. | `gold/adjudicated/public-reference-v1.1-confirmatory/` + `evidence/public-reference-v1.1-confirmatory/` | **CONFIRMED IN FROZEN NARROW SCOPE** — disjoint n=32; false merge 0.000 vs 0.1875; paired delta -0.1875, 95% CI [-0.34375,-0.0625]; false-split delta 0.000 [0.000,0.000]; predeclared primary verdict PASS |
| ORION-13.C6 | Every individual semantic-coordinate family has measurable marginal value. | targeted coordinate ablation results on authoritative cases | **PARTIAL ONLY / NOT A SCOPED HEADLINE CLAIM** — obstruction and modality/polarity/attribution/discourse are supported on both public-reference samples; zero effects for referent/construct/measurement/context are coverage-limited and do not license necessity or dispensability claims |
| ORION-13.C7 | ORION improves raw-text end-to-end scientific integration relative to model/RAG/schema baselines. | original `ORION-13.cross-domain-atlas.v1` expert-gold model run | **NOT_CLAIMED / FOLLOW_UP — CANNOT_CHECK** |
| ORION-13.C8 | ORION improves downstream scientific answer quality. | frozen downstream task and external result artifact | **NOT_CLAIMED / FOLLOW_UP — CANNOT_CHECK** |
| ORION-13.C9 | The public-reference mapping result is independently reproducible and prospectively replicable. | immutable source registry, portable gold manifests, execution-frozen confirmatory manifest, deterministic evaluator, independent replay | **SATISFIED FOR PUBLIC-REFERENCE ROUTE** — primary gold SHA `35f9e39b...54ed8`; disjoint confirmatory gold SHA `13a76c68...2782b`; execution identities frozen before confirmatory outputs |
| ORION-13.C10 | After granting a strong semantic integration product structured construct, measurement, context, provenance and missingness information, explicit claim-relative scientific identity authority yields correct registered integration decisions across the heterogeneous ORION-13-X contract family. | `research/claim_expansion/p3/P3_X_*` protected freeze/result/verification artifacts; `manuscript/sections/56-p3x-successor.tex` | **SUPPORTED_BOUNDED_EXACT_HETEROGENEOUS_CONTRACTS** — ORION-13-X 400/400, strong semantic product 250/400, canonical matching 50/400; ORION-13-X minus strong product +0.375, 95% domain-stratified bootstrap CI [0.3275,0.4225]; zero false GLUE; clean coverage 1.0 |
| ORION-13.C11 | An information-equivalent implementation carrying the same scientific-identity coordinates and rule agrees extensionally with ORION-13-X on the registered contract family. | ORION-13-X ideal typed-product arm and independent verification | **PORTABILITY / REPRESENTATION-INDEPENDENCE — SUPPORTED_BOUNDED** — ideal product 400/400 with zero decision mismatches |

## Strongest allowed headline

> **Scientific identity is a target-bound authorization relation above representational compatibility. On the registered structured-integration contracts, making that identity relation explicit eliminates the false integrations produced by weaker semantic products while preserving clean integration, and the same decisions are recoverable in an information-equivalent implementation.**

This headline is supported by ORION-13.C5, ORION-13.C10 and ORION-13.C11 together. It does not claim raw-text extraction superiority or downstream answer-quality improvement.

> **Annotation (2026-09-02, brief-report supersession).** The block above is the
> pre-rewrite full-paper headline and is retained as history only. The shipped
> publication object is the F1000Research Brief Report
> (`manuscript/brief-report-final/`, venue decision of 2026-09-01), whose frozen
> conclusion is strictly narrower and is the operative publication headline:
> *"These panels support a bounded observation: the complete polarity-sensitive
> non-merge condition avoids the six false agreements created by the registered
> flat rule. They do not establish population error rates, superiority over
> deployed integration systems, the independent value of every coordinate,
> raw-text extraction performance or downstream scientific utility."*
> No manuscript sentence may state authority above the brief-report conclusion
> while the brief report is the filing object. The preserved
> `evidence/null-and-baseline-battery-v1/BATTERY_V1.json` additionally bounds
> the mechanism evidence (minimal predicate/modality/polarity rule reproduces
> all decisions; registered flat rule is constant always-merge; exact McNemar
> p=0.03125 confirmatory / p=0.125 initial) and the manuscript now discloses
> these facts. Reopening the wider headline requires the full-paper successor
> programme, not a wording change.
| ORION-13.C10 | In the separate protected zero-error representation-transition programme, ORION-JUMP adds no incremental value over the verified representation-regime revision parent on either disjoint frozen split; Paper III therefore retains correspondence/preservation/obstruction/reopening semantics while making no distinct representation-invention claim. | `research/extensions/orion-jump-recursive-atoms/zero_error_jump/ZERO_ERROR_JUMP_EXPECTED_V2.json`; merged #598 science tree | **MERGED STRONGEST-PARENT EQUIVALENCE / NEGATIVE OWNERSHIP BOUNDARY** — not pooled with ORION-13/ORION-13-X; no general representation-invention authority |

## Promotion rule

A manuscript sentence may not state a stronger authority than this ledger.

In particular:

- local exact worlds cannot be cited as real-world adequacy;
- public-reference mapping results concern already-structured projections, not raw-text extraction quality;
- both 32-case public-reference atlases cover only three case families and cannot be described as completion of the original eight-family end-to-end gold study;
- the initial 32 cases are not pooled into the confirmatory verdict;
- zero ablation effect on an unsupported/weakly supported coordinate is not evidence that the coordinate is unnecessary;
- an LLM/proxy/simulated label cannot be cited as gold;
- ORION-13.C10 may be stated only at the prospectively frozen exact-contract scope; it does not authorize raw-text or deployed ontology claims;
- ORION-13.C11 is a portability result, not evidence that centralization is uniquely expressive;
- ORION-13.C7/ORION-13.C8 remain visible as `NOT_CLAIMED / FOLLOW_UP — CANNOT_CHECK`; their absence from the scoped headline does not turn missing evidence into PASS;
- any future manuscript edit that promotes C7/C8 or universal coordinate necessity reopens the corresponding expert/raw-text/targeted-atlas evidence gate.
- ORION-13.C7/ORION-13.C8 remain visible as `NOT_CLAIMED / FOLLOW_UP — CANNOT_CHECK`; their absence from the scoped submission claim does not turn missing evidence into PASS;
- the zero-error Jump strongest-parent tie cannot be relabelled as a ORION-13 positive, a universal impossibility of representation invention, or authority to adopt a new representation;
- any future manuscript edit that promotes C7/C8, universal coordinate necessity, or a distinct representation-invention mechanism reopens the corresponding evidence gate.

## Frozen public-reference evidence

Initial mapping evidence:

- `gold/adjudicated/public-reference-v1/`;
- `evidence/public-reference-v1/`.

Prospectively frozen disjoint confirmation:

- `protocol/PUBLIC_REFERENCE_CONFIRMATORY_EXECUTION_V1.json`;
- `gold/adjudicated/public-reference-v1.1-confirmatory/`;
- `evidence/public-reference-v1.1-confirmatory/`.

The confirmatory holdout was selected/frozen with zero overlap before confirmatory system outputs, then executed only after the exact gold hash, source revisions, evaluator Git blobs, margins and pass rule were bound in an `EXECUTION_FROZEN` manifest. `ORION-13.C5` is therefore a replicated narrow mapping result. ORION-13-X is a separate prospectively frozen successor and is not pooled into that confirmatory verdict. Together they support the identity-authority headline while leaving C7/C8 explicitly prospective.
