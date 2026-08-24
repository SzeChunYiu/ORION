# P3 cross-construct OAEI public-development successor

**Identity:** `P3.PUBLIC.OAEI.CROSS_CONSTRUCT.IDENTIFICATION_ENVELOPE.DEV.V3`  
**Exact terminal:** `PUBLIC_V3_MAXIMAL_BINARY_ENVELOPE_COVERAGE_PASS__PUBLIC_V3_NO_HARM_SUPERIORITY__PUBLIC_NONPROTECTED_ONE_SEED_FAMILY_ONLY`  
**Protected/source-disjoint multi-family authority:** `CANNOT_CHECK`

## What was repaired

- The predecessor remains unchanged: 68,187 same-construct cases, candidate-universe recall 0.930962, envelope coverage 0.995542, and terminal `PUBLIC_CANDIDATE_UNIVERSE_INVALID`.
- V3 enumerated 193,305 input-only cases without construct blocking: 68,043 same-construct and 125,262 cross-construct cases.
- The public evaluator restricted closed-world scoring to the declared reference domain. It marked missing panels, out-of-domain cases, and non-binary relations `CANNOT_CHECK` rather than silently treating them as obstruction.
- All 1,399 binary equivalence pairs mapped into the V3 universe. All 35 `<`/`>` pairs mapped to `CANNOT_CHECK`.

## Exact public-development result

- Full input universe: `193,305` cases.
- Scorable public-reference census: `117,914` cases (`1,399` GLUE; `116,515` OBSTRUCTION).
- `CANNOT_CHECK`: `75,391` cases: `2,415` no reference member, `72,941` outside the licensed reference domain, and `35` non-binary reference relations.
- Binary candidate-universe recall: `1.000000` (`1399/1399`).
- Maximal binary envelope coverage: `1.000000`.
- Information-equivalent ideal exact tie: `True`.
- Mechanics terminal: `PUBLIC_V3_MAXIMAL_BINARY_ENVELOPE_COVERAGE_PASS`.
- Comparative terminal: `PUBLIC_V3_NO_HARM_SUPERIORITY`.

## Scorable-census metrics

| System | Precision | Recall | F1 | Exact | Unresolved | Envelope coverage | Harm R1 | Harm R2 | Harm R3 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `AML_V3_2_AUTO_SOURCE_NATIVE` | 0.994845 | 0.275911 | 0.432009 | 0.922706 | 0.069457 | 0.992164 | 0.025201 | 0.025268 | 0.056478 |
| `FLAT_LABEL_EQUALITY_V1` | 0.831615 | 0.691923 | 0.755365 | 0.994683 | 0.000000 | 0.994683 | 0.005317 | 0.011966 | 0.019938 |
| `TOKEN_JACCARD_FORCED_V1` | 0.804956 | 0.719800 | 0.760000 | 0.994606 | 0.000000 | 0.994606 | 0.005394 | 0.013671 | 0.018692 |
| `P3_CONFLICT_PRESERVING_WRAPPER_V2_CROSS_CONSTRUCT` | 1.000000 | 0.258041 | 0.410227 | 0.920883 | 0.076293 | 0.997176 | 0.021897 | 0.021897 | 0.033194 |
| `P3_MAXIMAL_BINARY_IDENTIFICATION_ENVELOPE_V3` | NA | 0.000000 | NA | 0.000000 | 1.000000 | 1.000000 | 0.250000 | 0.250000 | 0.250000 |
| `P3_INFORMATION_EQUIVALENT_IDEAL_V3` | NA | 0.000000 | NA | 0.000000 | 1.000000 | 1.000000 | 0.250000 | 0.250000 | 0.250000 |

## Coverage–harm frontier

The V3 candidate is the full binary identification envelope. Its coverage-one result is real but follows from retaining both licensed binary truths for every scorable case. It is not a point-prediction success.

- Candidate-minus-AML harm: `[+0.224799430093, +0.224731584036, +0.193522397680]`.
- Candidate-minus-AML exact rate: `-0.922706379226`.
- Candidate-minus-AML unresolved rate: `+0.930542598843`.
- Thus V3 achieves the required coverage mechanics but is strictly worse than AML in all three action-harm regimes.

## Recursive failure diagnosis

V2's 304 envelope failures comprised 285 double-negative agreements that missed GLUE and 19 double-positive agreements that asserted GLUE on V2-imputed obstruction. Under V3's corrected licensed-domain replay, the same wrapper has zero false-positive GLUE but still has `333` failures, all double-negative point obstructions on public GLUE pairs. Thus the 19 V2 failures do not survive the corrected scoring contract, whereas the shared-negative evidence failure does.

Failure targets on the wider census: `201:82`, `202:91`, `204:16`, `205:61`, `221:1`, `223:4`, `225:5`, `230:3`, `301:37`, `302:24`, `303:4`, `304:5`.

The cross-construct repair recovered 64 public GLUE pairs that the V2 type block could not express. This validates removal of the block, not a causal construct claim.

## Coordinate audit

- Joint operational contrast counts: `{'REFERENT_1__CONSTRUCT_0': 42402, 'REFERENT_1__CONSTRUCT_1': 75512}`.
- Same-construct scorable cases: `42,402`; cross-construct scorable cases: `75,512`.
- Every scorable pair has a different document-aware IRI key; there is no `REFERENT_0` control stratum.
- IRI inequality is an input identity contrast, not independent proof of the epistemic referent coordinate.
- Construct and referent identity are not causally separated, and no independent outcome-blind coordinate evaluator was used.
- Coordinate terminal: `DESCRIPTIVE_REFERENT_OPPORTUNITY_ONLY__NO_CAUSAL_COORDINATE_SEPARABILITY_OR_INDEPENDENT_EVALUATOR`.

## Comparator audit

- AgreementMakerLight v3.2 is a reproducibly bound source-native development comparator: tag commit `d54a6650818d3474fe36090c2bc7dfe5bf4dfcb6`, jar SHA-256 `a5b831a6c000e49aa4702b16486dabdf38e40bb68203a16a8019414fecc2ecf3`, and no reference argument.
- Nineteen successful outputs replayed byte-identically; test 206 remained unparsable.
- On the licensed scorable domain AML precision/recall/F1 were `0.994845` / `0.275911` / `0.432009`.
- It is not a current-SOTA certificate: execution used OpenJDK 17 rather than the README-named Java 8 runtime, auto mode is not certified as the strongest configuration, and no second current ontology matcher is bound.

## Claim boundary and next research discriminator

V3 supports one bounded statement: **a full binary identification envelope attains coverage one on a wider, correctly licensed public-development universe, while exposing a large action-harm cost.** It does not support comparative superiority, a nontrivial selective-envelope claim, causal coordinate value, protected confirmation, or multi-family transport.

The next result must be source-disjoint: freeze a structure-aware proper subenvelope on multiple untouched ontology families, bind current strong matchers, and require all of (i) binary coverage 1.0, (ii) harm noninferiority in every frozen regime, (iii) exact information-equivalent-ideal tie, and (iv) cluster-level replication.
