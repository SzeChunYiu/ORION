# ORION-Q / ORION-QG manuscript consistency sweep V1

Date: 2026-08-21
Method: `nature-polishing` consistency-before-language pass + reference/authority cross-check.

This sweep audits scientific terminology, claim strength, evidence classes, donor ownership and cross-paper boundaries before sentence-level polish. A finding marked `MUST_EDIT_FINAL` is not considered closed merely because a sidecar audit exists.

## Portfolio-wide controlled vocabulary

### Evidence authority
Use these words consistently:
- **theorem / all-n theorem** — only when proof authority exists for the exact grammar/objective;
- **exhaustive on the stated finite domain** — complete finite enumeration, not universal theorem;
- **exact counterexample** — one verified witness is logically sufficient to refute the stated universal/restricted claim;
- **machine-evidenced / frozen panel** — deterministic finite evidence without universal authority;
- **prospective confirmation/refutation** — prediction/diagnosis frozen before outcome, scoped to the registered case(s);
- **replay** — determinism/provenance evidence, never an independent efficacy replicate;
- **CANNOT_CHECK** — unavailable authority/evidence, not failure and not success.

### Support terminology
- **support ceiling** = proven upper bound when tightness is not established;
- **intrinsic support number `kappa`** = smallest proven sufficient support with lower-bound/infeasibility tightness evidence;
- R6M ORION-01: all-n support ceiling <=2; do not silently call it intrinsic `kappa=2` unless an independent support1 impossibility result is authorized for the same grammar/objective;
- R6I ORION-09 V3: exact `kappa_R6I=1` because support1 sufficiency + support0 infeasibility are both committed.

### Objective-phase terminology
- **certificate/proof-validity cone** for QG16;
- outside the cone = `THIS_PROOF_CERTIFICATE_DOES_NOT_APPLY`, not “support2 required”;
- **global phase boundary** only if sharpness/necessity is actually proved. Current QG16 sharpness is OPEN.

### Representation terminology
- StabPrep: **unidentifiable / not a function of the frozen 13-feature vocabulary on the registered domain**;
- do not say globally `information-theoretically impossible/unknowable` without the vocabulary/domain qualifier.

### Source/licence terminology
- until an authorized licence is selected, use **publicly inspectable source/repository**, not “ORION is open source.”
- third-party DUCC data are referenced by source repository/commit/blob; do not imply redistribution rights.

## ORION-01 final-manuscript sweep

Final target draft: `MANUSCRIPT_V3.md`.

### Closed corrections
- `C_DP=C_D++` all n is visible as the load-bearing theorem.
- support-three necessity is explicitly false for the frozen R6M/raw-support objective.
- R6R is bounded prospective one-subject/15-matching evidence.
- later QG closed-form counterexamples are inside D++ and do not refute R6S.
- TARE full text now receives explicit credit for user-selectable `R_k`, ancilla/control choices and non-unique optimizable Tag strings.
- numerical donor study correctly described as fixing a canonical `R_k` family while minimizing Tag weights rather than as proving global joint optimality.

### `MUST_EDIT_FINAL` at LaTeX/bibliography stage
- insert current TARE v4 citation key and exact title;
- cite anticommuting/unitary-partitioning donors without implying TARE authors invented that primitive;
- label every large finite checker count as a complete domain rather than `n` samples;
- add Data/Code Availability text from portfolio audit;
- include theorem/referee map as table or supplementary manifest.

## ORION-02 final-manuscript sweep

Current draft: `MANUSCRIPT_V2.md`; publication V3 recommended after graph-validation/benchmark-reference insertion.

### Closed corrections
- broad provenance/Chain-of-Evidence novelty ceded to ScientistOne.
- broad scientific-agent benchmarking ceded to ScienceAgentBench, AstaBench and SciAgentArena.
- paper states one-programme feasibility/research-hygiene evidence rather than productivity improvement.
- receipts explicitly not truth.

### `MUST_EDIT_FINAL`
- add ScienceAgentBench archival ICLR 2025 citation alongside AstaBench/SciAgentArena; do not merge names;
- make `Q2_TRANSITION_GRAPH_V2.json` and its validator the Methods/Results backbone, not an optional supplement;
- report declared graph denominator: 23 nodes / 13 asserted successor edges / standalone no-edge negatives as publication scope, while making clear this is a bounded ORION-Q programme graph rather than all possible scientific transitions;
- if claiming *complete* eligible-transition coverage, add a machine-generated inventory that maps the programme receipt index to inclusion/exclusion reasons; otherwise use “declared publication graph,” not “complete graph”;
- do not claim the method improves research quality/speed without a controlled policy comparison.

## ORION-03 final-manuscript sweep

Current manuscript remains V1 plus V2 foundation/prospective protocol; **no final V2/V3 results manuscript is authorized yet**.

### Closed corrections
- benchmark parents separated: ScienceAgentBench, AstaBench, SciAgentArena, MLGym.
- ORION-03 object stated as pre-outcome inter-instrument diagnosis/agreement on unresolved frontier questions with deferred scoring, not generic task benchmarking.
- two additional prospective questions are frozen without fabricated Lane A/B results.

### `BLOCKING`
- execute 2–3 additional prospective frontier instances under the pre-frozen protocol;
- each frontier question is the independent unit; do not inflate `n` with coordinates/messages/calls;
- independent replay of included receipts;
- D2/D3 instrument-defect disposition;
- fresh novelty search at actual submission date.

No language polish can close these scientific gates.

## ORION-04 final-manuscript sweep

Current draft: `MANUSCRIPT_V2.md`; publication V3 recommended for current-donor terminology.

### Closed corrections
- exact-synthetic scope appears in title/abstract/discussion boundary;
- first-right-of-refusal ties/absorptions are main evidence rather than hidden negatives;
- information-parity artifact defines matched visible serialized facts.

### `MUST_EDIT_FINAL`
- distinguish **STALE-style memory invalidation** (later evidence conflicts with remembered state) from ORION-04 N4-B **scope invalidation** (a previously valid failure receipt's dependency coordinates changed);
- credit ContextNest/provenance/version governance as donor infrastructure; ORION-04 asks how typed/scoped facts change decisions, not how to build the context store;
- explicitly separate ORION-04 bounded experiment from ORION-23's general responsibility-scoped sufficiency theory;
- do not pool six worlds into one effect/p value;
- use `2.3x` N4-C ratio only beside absolute regrets;
- N4-D 200 hostile/200 honest chains are a constructed finite battery, not a population security estimate;
- call LLM proxy arms deterministic heuristics, never real LLM measurements.

## ORION-09 final-manuscript sweep

Final target draft: `MANUSCRIPT_V3.md` on refresh cut `c5ba39f...`.

### Closed corrections
- Instance Space Analysis/Rice treated as primary conceptual parents.
- generic feature→performance/footprint novelty removed.
- R6I exact `kappa=1` integrated.
- QG6 syndrome rank 5 explicitly presented as a safe but loose proof-derived ceiling, not intrinsic support.
- QG16 cone has correct outside semantics and sharpness OPEN.
- StabPrep mixed-cell result vocabulary-bounded.
- QG17 result excluded because refresh cut has protocol/no committed result.

### `MUST_EDIT_FINAL`
- update figure contract to include R6I proof-bound hierarchy and QG16 cone as main displays;
- PRX Quantum version needs a broad-reader/nontechnical value argument; if this requires overclaiming universality, transfer to Quantum;
- add exact citations to ISA/Rice and donor compiler families;
- preserve different authority types in the cross-family table; no pooled family success rate.

## ORION-10 final-manuscript sweep

Current draft: `MANUSCRIPT_V2.md`; publication V3 recommended to foreground current static-analysis donor language.

### Closed corrections
- exact 10<11 row is central refutation, not hidden in 9,545/9,546 aggregate;
- proved upper bound/support theorem separated from conjectural closed-form equality;
- B′/F2 repair is separately frozen.

### `MUST_EDIT_FINAL`
- cite Qet/Qualtran/resource-estimation work and explicitly cede generic static quantum cost analysis/upper-bound estimation;
- define `ForecastCertificate` as reporting schema/authority decomposition, not a claim to invent static analysis;
- benchmark instances are deterministic registered panels, not IID statistical samples;
- chemistry subject, not individual matching, is the external scientific unit for transfer language;
- timing is descriptive: add environment, cold/warm definition and raw/quantile availability; no theorem authority from speedup;
- do not headline 99.99% accuracy.

## Cross-paper ownership sweep

| Object | Owner paper | Neighbor nonclaim |
|---|---|---|
| R6M all-n support2 expressivity | ORION-01 | ORION-09 cites as one regime-geometry case |
| negative-result successor governance | ORION-02 | ORION-03 is measurement benchmark, not governance method |
| frontier dual-instrument agreement | ORION-03 | ORION-02/QG outcomes supply deferred cases only |
| matched-information typed/scoped state experiments | ORION-04 | ORION-23 owns general responsibility-scoped sufficiency theory |
| cross-family regime-geometry framework | ORION-09 | ORION-01/ORION-10 own detailed theorem/forecast objects |
| layered static forecast certificate + refutation/repair | ORION-10 | ORION-09 may use as regime-geometry example only |

## Submission-language cleanup pass

After the `MUST_EDIT_FINAL` scientific/content changes above, then apply sentence-level polish:
- remove repeated “we therefore”/“crucially” scaffolding;
- replace long authority strings in prose with stable short labels, keeping exact strings in tables/SI;
- reduce internal ORION issue/branch language in main text; preserve it in reproducibility supplement;
- define all abbreviations once;
- use consistent `all-n`, `support-two`, `Tag`, `Restore`, `D++`, `B′`, `B″` typography;
- keep claim strength equal or weaker after compression—especially in titles/abstracts.

## Sweep status

- ORION-01 V3: content-consistency pass complete; target package/citations/figures remain.
- ORION-02 V2: requires graph-denominator wording + benchmark citations before final polish.
- ORION-03: scientific BLOCK remains.
- ORION-04 V2: current-donor terminology update required before final polish.
- ORION-09 V3: freshness/content consistency complete; updated figures + target-aware review remain.
- ORION-10 V2: static-analysis donor integration required before final polish.
