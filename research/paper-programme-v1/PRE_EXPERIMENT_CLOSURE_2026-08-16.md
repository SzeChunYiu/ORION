# Five-paper pre-experiment closure — 2026-08-16

**Subject at start of wave:** `9f54e776d4bc2e663e93e51e74d71e49eee664b7`  
**Purpose:** record what can truthfully be completed before external outcomes, expert gold, protected evaluation and final execution identities exist.

This document is a state ledger, not a publication verdict. `DESIGN_FROZEN` means the scientific design is registered before final outcomes. It does **not** mean Gate 3 is fully PASS: Gate 3 requires exact execution bindings and becomes `EXECUTION_FROZEN` only when subject/dataset/split/model/provider/baseline/evaluator identities are bound before outcome access.

## Programme gate matrix

| Gate | State after this wave | What is complete | What still blocks PASS |
|---|---|---|---|
| 0 — claim coherence | PARTIAL / strong | stable P1–P5 identities; one primary hypothesis per paper; ownership boundaries; protocol IDs | final term-definition/claim-ledger audit after empirical results |
| 1 — nearest-work closure | PARTIAL / current | fresh 2026 audit and claim contraction; public reference repos pinned where useful | mandatory rerun within 14 days of submission; any new nearest work may reopen claims |
| 2 — complete manuscript | PARTIAL / strong | canonical working manuscript for all five; keywords; methods/evaluation design; nearest work/limitations | external Results/Discussion/statistics; final data/code statements; venue-complete author/submission metadata |
| 3 — prospective freeze | DESIGN_FROZEN | machine-readable V1 protocol for every paper; hypotheses/baselines/ablations/metrics/statistics/plots/access rules frozen; `outcome_accessed=false` | final subject, data/split, provider/model, baseline config, evaluator and epoch hashes |
| 4 — empirical adequacy | CANNOT_CHECK | external study designs and denominators defined | actual matched external runs, expert/official gold, uncertainty/effects |
| 5 — mechanism identification | DESIGNED | per-paper ablation families and resource parity rules frozen | actual ablation runs/equivalence decisions |
| 6 — figures/tables | SPEC_FROZEN | named paper-specific figures/tables; normalized result schema; dependency-free bar/scatter/heatmap SVG utility | actual result data, uncertainty-bearing final plots/tables, caption/N audit |
| 7 — reproducible artifact | PARTIAL | common protocol/result schemas, analysis standard, stats utilities, plot utility, CI tests | frozen raw external artifacts, environment/resource manifests, clean independent reproduction, archival DOI |
| 8 — integrity/authority | PARTIAL / strong | fail-closed external evidence machinery already exists; P4 threat/custody policy; P5 fresh-transfer policy; hidden-label/access rules frozen | independent protected execution and external verifier/host evidence |
| 9 — submission package | DEFERRED | journal-agnostic high-bar standard defined | target journal, final template, author/funding/conflicts, cover letter, final PDF after science freezes |

## Shared assets completed in this wave

- `research/paper-programme-v1/protocols/PUBLICATION_PROTOCOL_SCHEMA_V1.json`
- `research/paper-programme-v1/protocols/RESULT_RECORD_SCHEMA_V1.json`
- `research/paper-programme-v1/protocols/ANALYSIS_STANDARD_V1.md`
- `research/paper-programme-v1/protocols/publication_stats.py`
- `research/paper-programme-v1/protocols/publication_svg.py`
- CI coverage in `tests/test_journal_protocol_assets.py`

The analysis layer is intentionally dependency-light. It supports Wilson intervals, prospective proportion-precision planning, deterministic paired/bootstrap summaries and dependency-free SVG bar/scatter/heatmap rendering from frozen data summaries. It refuses to substitute missing observations for `CANNOT_CHECK`.

## P1 — Recursive Epistemic Reconstruction

### Completed before external run

- `P1.hidden-formulation.v1` frozen with H1 primary and H2–H4 secondary.
- Hidden-shift families fixed: parent-domain, representation, decomposition/interface, measurement/operationalization, evidence-only negative control, execution-only negative control.
- Required current baseline families fixed, including AREX-like, SCION-like and Iris-like comparators.
- ORION ablations, resource/exclusion rules, statistical rules, practical margins and P1-1..P1-6/T1..T3 outputs fixed.
- Hidden-shift case schema added; gold cause/reframe/reopen labels protected.
- SciAgentArena code reference pinned to `HelloWorldLTY/SciAgentArena@9865bb0c261bd9a59ef23576805b268b458b59d2`.
- manuscript evaluation now points to the V1 protocol and distinguishes design freeze from execution freeze.

### Remaining irreducible blockers

- construct/freeze final fresh hidden-shift case set and adjudication gold;
- bind final subject/model/provider/baseline/evaluator identities;
- run matched baselines and ablations;
- compute external uncertainty/effects and populate results/failure analysis.

## P2 — Open-World Scientific Knowledge Discovery

### Completed before external run

- `P2.open-world-discovery.v1` frozen with benchmark-family official metrics plus premature-closure guard.
- Deep/Wide/SAGE/MetaSyn/offline-complete-gold families, BM25/dense/hybrid/RAG/agentic/protocol-review baselines and route-governance ablations fixed.
- route trial schema records backend/query/content identity, transport failure, earned independence and route/task decisions.
- AutoResearchBench code reference pinned to `CherYou/AutoResearchBench@a46c9bfb8968786f73f0a6a5b365b5384cd0f96d`.
- AutoResearchBench released dataset is confirmed as a separately distributed Apache-2.0 artifact; the actual downloaded/decrypted bundle must be content-hashed at execution freeze rather than inferred from repo identity.
- manuscript is protocol-bound and explicitly preserves live-provider mutability/contamination as measured conditions.

### Remaining irreducible blockers

- download/license-check/content-hash final benchmark data and any SAGE/MetaSyn assets;
- freeze provider/model/query/resource identities;
- execute official/offline matched campaigns;
- populate recall/stopping/cost figures and failure taxonomy from raw traces.

## P3 — Global Knowledge Portrait

### Completed before external run

- `P3.cross-domain-atlas.v1` frozen with safe-integration primary hypothesis and valid-integration guard.
- real-case families, structured-integration baselines, coordinate/obstruction/recoverability ablations, statistics and P3-1..P3-7/T1..T3 outputs fixed.
- `ANNOTATION_SCHEMA_V1.json` covers source identity, referent, construct, measurement, context, polarity, modality, attribution, discourse, mapping, preservation, contradiction, integration and recoverability.
- `ANNOTATION_HANDBOOK_V1.md` and `ADJUDICATION_POLICY_V1.md` frozen before final gold/model outputs.
- unresolved scientific cases remain valid gold; adjudication cannot manufacture certainty.
- MUSE reference pinned to `cohentsofia/MUSE@f7a40317db46145d0c90b221311d8324db5da1b9`.
- manuscript now binds the annotation and external study protocol.

### Remaining irreducible blockers

- sample/freeze the at-least-three-discipline source corpus;
- recruit/execute independent and domain-expert annotation under the frozen handbook;
- freeze adjudicated gold before final system output inspection;
- execute matched integration baselines/ablations and downstream evaluation.

## P4 — Verified Scientific Discovery

### Completed before protected run

- `P4.protected-authority.v1` freezes false-authority promotion as primary with clean-coverage guard.
- attack families, source-aware baselines, authority ablations, safety margins and P4-1..P4-6/T1..T3 outputs fixed.
- `THREAT_MODEL_V1.md` freezes attribution/content/conflation/influence/checker/contamination/evaluator/holdout/refusal threats.
- `ATTACK_CASE_SCHEMA_V1.json` separates candidate-visible inputs from protected gold and exact evidence content/provenance identity.
- `CUSTODY_POLICY_V1.md` separates candidate, protected evaluator/holdout and independent host verifier; post-hoc evaluator changes version the evaluation.
- manuscript now binds the protected V1 design and clean-positive guard.

### Remaining irreducible blockers

- independent host must generate/freeze part of the final hostile set after method freeze;
- bind evaluator/holdout/source/split/subject/baseline hashes;
- execute #59/#101 protected campaign with access telemetry;
- obtain independent verification of headline false-promotion/coverage evidence.

## P5 — Self-ORION

### Completed before protected self-improvement run

- `P5.hidden-cause-fresh-transfer.v1` freezes protected fresh improvement as primary with harmful-transfer guard.
- eight hidden-cause families, current self-improvement/failure-attribution baseline families, governance ablations, longitudinal/tail reporting and P5-1..P5-7/T1..T3 outputs fixed.
- `HIDDEN_CAUSE_CASE_SCHEMA_V1.json` separates visible symptom/context from protected cause and replay/fresh identities.
- `FRESH_TRANSFER_POLICY_V1.md` freezes motivating/replay/fresh evidence roles, freshness consumption, harmful-tail accounting and host-only promotion boundary.
- PAST-Bench reference pinned to `Gen-Verse/PAST-Bench@f8223517ae7491e776b69793d9f11e9d074ab42e`.
- manuscript evaluation now names the V1 protocol and forbids replay-only/internal-readiness promotion.

### Remaining irreducible blockers

- construct/freeze hidden-cause and genuinely fresh transfer sets;
- bind protected evaluator and final subject/provider/baseline identities;
- complete live/protected dependencies #8/#76 on the exact subject;
- execute current self-improvement baselines/ablations and preserve every harmful/null candidate;
- obtain external host verification/attestation for any promotion recommendation.

## What a future AI session should do next

Do not add another architecture layer merely because empirical evidence is absent. Pick one paper issue, bind the missing execution identities without inspecting final outcomes, change the protocol state to `EXECUTION_FROZEN` in a dedicated PR, then run exactly that protocol. If the experiment falsifies the claim, preserve it and shrink/reconstruct the paper. If the scientific design itself must change after outcomes are seen, create V2 and retain V1 unchanged.
