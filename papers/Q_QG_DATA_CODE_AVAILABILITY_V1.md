# ORION-Q / ORION-QG data and code availability V1

Date: 2026-08-21
Evidence cut: `main@ca7df1055a43f97eaf8d142a62011c4c261af368`
Method: `nature-data` inventory + FAIR/reproducibility preflight.

This file supplies publication wording and unresolved author decisions. It does not create a DOI, licence, repository release, or external archive by itself.

## Portfolio-level audit

### What is already available

The repository already contains, at stable paths:
- result-bearing JSON receipts;
- pre-outcome protocols and closure packets;
- analyzer/checker code;
- independent/generic verifiers for major QG lanes;
- replay-verification ledgers for the N-lanes;
- manuscript claim ledgers and proof/evidence maps;
- pinned external-source commit/blob identities for public DUCC Hamiltonian material used by Q1/QG2.

### What is not yet publication-complete

1. **No root repository licence was located on the publication branch.** Therefore the manuscripts must not call ORION “open source” until an explicit licence is selected and committed. Source is publicly inspectable on GitHub, but public visibility is not a reuse licence.
2. No archival DOI/Zenodo record is yet bound to the exact publication code/data cut.
3. No paper-specific machine-readable manifest currently lists every load-bearing result/protocol/code path and its content digest for all six papers.
4. Protected or deliberately unread material must remain excluded; the stretched-N2 discriminator may not be packaged merely for completeness.
5. External DUCC source files should be cited to their source repository/commit rather than redistributed unless reuse permission is explicitly established.

## Recommended release object

Before first submission of any Q/QG paper, create one immutable archive release of the publication evidence cut containing only publication-authorized material and record:

- git commit SHA;
- archive DOI or permanent identifier;
- exact licence(s) for code and original data/receipts;
- machine-readable `MANIFEST.json` with path, role, SHA-256 and paper ownership;
- environment/dependency lock or tested interpreter/package versions;
- one-command or minimal reproduction entry points per paper;
- explicit exclusions/protected-data note.

Do not invent the DOI or licence in manuscripts before that release exists.

## Q1 — Exact Support Ceiling in Shared-Tag TARE Compilation

### Data availability — ready-to-paste draft

> All ORION-generated numerical results supporting this study are stored as deterministic, content-addressable result receipts in the accompanying research repository. The load-bearing receipts include the support-dominance checks, exact counterexample searches, finite support-two closure, the all-n composition theorem, the finite regime-predicate evaluation, and the prospectively frozen fresh-subject test. The public Hamiltonian subjects are referenced by repository commit and source-blob identity; the study does not redistribute protected or deliberately withheld subject material. A permanent archival identifier for the exact publication release will be inserted after deposit.

### Code availability — ready-to-paste draft

> The exact dynamic-programming referees, theorem/checker scripts, protocol files and independent verification code used in this study are available in the accompanying repository at the publication commit identified in the reproducibility statement. The repository is publicly inspectable. An explicit reuse licence and permanent archival identifier will be reported in the final submitted version once the publication release is deposited.

### Q1 FAIR/reproducibility blockers
- [ ] choose and record project/code licence;
- [ ] archive exact publication cut and insert DOI/permalink;
- [ ] paper-specific manifest covering R6N/R6O/R6P/R6Q/R6R/R6S plus cited QG boundary receipts;
- [ ] exact replay commands from clean environment;
- [ ] cite public DUCC source repository/commit without implying redistribution rights.

## Q2 — Recursive Recovery of Negative Quantum Research Results

### Data availability — ready-to-paste draft

> This methods/case-study paper uses repository-native research records rather than a newly collected external dataset. The supporting data are the prospectively frozen protocols, result receipts, negative/donor/positive dispositions, closure packets and the machine-readable successor graph that links eligible predecessor states to their authorized successors. These artifacts are available with the paper's publication release; protected materials not required for the reported case study remain excluded.

### Code availability — ready-to-paste draft

> Code implementing the relevant research harness, typed campaign controller, receipt validation and the quantum-programme analyzers is available in the accompanying repository at the stated publication commit. The final version will cite a permanent archive and explicit reuse licence once deposited.

### Q2 blockers
- [ ] release a complete eligible-chain manifest so the successor graph cannot be read as a selected anecdotal subset;
- [ ] add a schema/checker that validates transition-graph edges against source receipts;
- [ ] choose project licence and archive DOI;
- [ ] distinguish instrument code used to produce the case study from post-hoc publication-synthesis code.

## Q3 — Dual-Instrument Frontier Research Benchmark

### Data availability — draft, **not yet final**

> The benchmark protocol, immutable instrument inputs, Lane-A and Lane-B receipts, and deferred outcome-scoring records will be released for every included frontier question. Each benchmark instance will expose the frozen question and pre-outcome instrument outputs while preserving any independent protected material required by the underlying research lane. The final availability statement will list all completed instances and their digests after the prospectively frozen multi-instance gate has been discharged.

### Code availability — draft

> The research harness and typed non-LLM campaign-controller implementations used by the benchmark are publicly inspectable in the accompanying repository. The final release will bind the exact implementations and replay commands used for every benchmark instance, together with a permanent archive and reuse licence.

### Q3 blockers
- [ ] execute the already frozen additional prospective instances before publication;
- [ ] bind exact Lane A/Lane B implementation digests for each instance;
- [ ] independent replay of every included receipt;
- [ ] final disposition of instrument defects D2/D3;
- [ ] project licence and archive DOI.

## Q4 — Typed and Scoped Partial Knowledge

### Data availability — ready-to-paste draft

> All study worlds are synthetic and generated deterministically from the frozen protocols and seed recorded in the repository. Result receipts for the six primary studies and two negative/donor-absorption controls are provided with the publication release. No human, clinical or private dataset is used. The final manuscript will cite the permanent archive of the exact publication release.

### Code availability — ready-to-paste draft

> The deterministic world generators, candidate and baseline policies, evaluation gates and replay-verification scripts are available in the accompanying repository. Each study can be regenerated from its frozen protocol and source code. The final release will specify the exact reuse licence and permanent archive identifier.

### Q4 blockers
- [ ] one-command aggregate reproduction entry point over N4-A/B/C/D/E/F3 plus N1-C/N2-F5B;
- [ ] machine-readable parity manifest stating which serialized information is identical across compared arms;
- [ ] project licence and archive DOI.

## QG1 — Compilation Regime Geometry

### Data availability — ready-to-paste draft

> All reported regime maps, exact witnesses, theorem/counterexample receipts and prospective-forecast outcomes are generated from deterministic compiler-family analyzers and stored in the accompanying repository. The publication release will include the TARE, SixLCU and StabPrep result receipts, independent-verification records and the cross-family evidence matrix. No protected chemistry discriminator is required for the cross-family claims.

### Code availability — ready-to-paste draft

> Analyzer and independent-verifier implementations for the reported compiler families are available in the accompanying repository at the publication commit. The final article will cite a permanent archival snapshot and explicit reuse licence.

### QG1 blockers
- [ ] paper-specific cross-family manifest with exact path/digest per theorem, finite-domain result and prospective refutation;
- [ ] deterministic figure/table regeneration scripts;
- [ ] licence and archive DOI;
- [ ] do not package unmerged successor outcomes into the frozen publication release unless the paper is formally reopened and re-adjudicated.

## QG2 — Certified Static Resource Forecasting

### Data availability — ready-to-paste draft

> The benchmark instances, forecast outputs, unrestricted-referee comparisons and exact counterexample are stored as deterministic result receipts in the accompanying repository. The publication package will identify the theorem-backed support-two receipt, the original refuted forecast receipt, the corrected/enlarged-family receipt, and the exact source rows used for each benchmark panel. Public Hamiltonian source data are referenced by their original repository commit and blob identity.

### Code availability — ready-to-paste draft

> The static forecaster, exact support-two family evaluator, unrestricted referee bindings and independent witness-verification code are available in the accompanying repository. The final article will cite the exact publication commit, permanent archive and explicit reuse licence.

### QG2 blockers
- [ ] executable `ForecastCertificate` serialization/checker bound to the manuscript schema;
- [ ] clean benchmark regeneration that separates theorem authority from empirical timing;
- [ ] licence and archive DOI;
- [ ] source-data citation/permission audit for public DUCC rows.

## Licence decision — `AUTHOR_INPUT_NEEDED`

No licence choice is inferred. Before calling code/data “open source” or granting reuse rights, an authorized repository owner must choose the licence(s) appropriate to:
- original ORION source code;
- original synthetic result receipts/data;
- manuscript/figure text if separately licensed;
- third-party/public input data, which retain their upstream terms.

Until then, use **publicly inspectable source** rather than **open-source code** in manuscripts.

## FAIR status summary

| Dimension | Current | Publication closure |
|---|---|---|
| Findable | GitHub paths and digests exist | archival DOI + paper-specific manifests |
| Accessible | public repository for current materials | permanent archive; explicit protected/excluded-material note |
| Interoperable | JSON/Markdown receipts and protocols largely structured | schema versions + machine-readable paper manifest |
| Reusable | reproducible evidence is strong | explicit licence + dependency/environment record + citation of third-party data terms |

The licence/archive gap is a publication blocker for strong “open/reusable” wording, not a blocker to the underlying scientific results.
