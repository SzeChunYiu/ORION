# Q/QG publication CI receipt V1

Date: 2026-08-21
Workflow: `q-qg-publication`
Run: `32531610273`
Job: `96924573112`
Publication branch head audited: `21a643bf53f5909ccc11e8459a2a8f1d00ca1fbd`

This receipt records package-integrity checks only. It grants no scientific novelty, submission, peer-review or acceptance authority.

## 1. Portfolio publication checker

Canonical stdout:

```text
Q_QG_PUBLICATION_CHECK=PASS
ORIGINAL_CUT=ca7df1055a43f97eaf8d142a62011c4c261af368
QG1_REFRESH_CUT=c5ba39fef4f25c46de5fb69bf07f50530f4693ca
PUBLICATION_HEAD=origin/codex/q-qg-nature-skills-publication-closure-20260821
PUBLICATION_BRANCH_CHANGED_FILES=79
FINAL_MANUSCRIPTS=Q1V3,Q2V3,Q4V3,QG1V3,QG2V3
SCIENTIFIC_RECEIPT_MUTATIONS_BY_PUBLICATION_BRANCH=0
Q3_PUBLICATION_AUTHORITY=SCIENTIFIC_SERIES_INCOMPLETE__CANNOT_CHECK_PEER_REVIEW_READY
SUBMISSION_AUTHORITY=NOT_GRANTED_BY_THIS_CHECK
```

Interpretation:
- the publication branch modified no frozen scientific receipt/protocol path;
- final scientific manuscripts are the five V3 drafts named above;
- QG1 alone uses the separately adjudicated current-main refresh cut;
- Q3 remains intentionally scientifically blocked.

## 2. Q2 declared-denominator / successor-graph validator

Canonical stdout:

```text
Q2_TRANSITION_GRAPH_CHECK=PASS
PUBLICATION_CUT=ca7df1055a43f97eaf8d142a62011c4c261af368
DECLARED_RECEIPT_UNIVERSE=51
INCLUDED_GRAPH_NODES=23
EXCLUDED_WITH_REASON=28
ASSERTED_SUCCESSOR_EDGES=13
NEGATIVE_OR_PARTIAL_NODES=13
STANDALONE_WITHOUT_INVENTED_SUCCESSOR=7
CUT_BOUND_DENOMINATOR_RECEIPTS=51
SCIENTIFIC_CAUSALITY_AUTHORITY=NOT_GRANTED_BY_VALIDATOR
```

Interpretation:
- Q2's 51-receipt declared publication universe is fully partitioned 23/28;
- all 51 receipts are bound to the frozen Q2 publication cut;
- the graph has 13 asserted successor edges and retains 7 named negative/absorbed nodes without an invented successor;
- validator explicitly does not self-certify scientific causality.

## 3. Paper-specific science manifest validator

Canonical summary:

```text
Q_QG_SCIENCE_MANIFEST_CHECK=PASS
BOUND_SCIENCE_ARTIFACTS=34
Q1_ARTIFACTS=10
Q4_ARTIFACTS=8
QG1_ARTIFACTS=11
QG2_ARTIFACTS=5
SCIENTIFIC_AUTHORITY=UNCHANGED_BY_MANIFEST
```

All 34 load-bearing science artifacts resolved to a 40-character git blob ID at the paper's declared scientific cut.

### Q1 — 10 bound science artifacts

- R6N support-dominance/counterexample history — blob `09d50f810a19d42b161311db85fc3d59ea1a69cf`
- R6O enlarged-Tag donor/counterexample — `ac4f3f677b632d6162eb0da3e89514f73ad684ce`
- R6P finite support-two closure — `ce2c0aec22090d266688f01cd0b6c25f503209d5`
- R6Q finite regime predicate — `09678307e379f0221376021e50b12c26ed5d3c8a`
- R6R prospective fresh subject — `234b4ca1964ab4573d0dc25a550f7f5ea73982e4`
- R6S all-n theorem — `e7949b35e7010ae9b24d9f69a35f210fa7f55c13`
- QG5 exact companion counterexample — `36fc6b6b032eff3321e0befa8a5c809733242e16`
- QG7 B-prime counterexample — `88b2477dcea656c108c7190023581e458716fdea`
- QG7b finite hybrid-family repair — `c5c84c0b0c4c16e99925c41c3eed94263a4eba93`
- QG7c partial classification proof — `235ed02a7d19e749cf75623ac6b7ccce5887518a`

### Q4 — 8 bound science artifacts

- N4-A typed VOI — `beedee22e5e2ad8c5899339816223fd28e8efdf2`
- N4-B scoped reopening — `2e1680896019aeb77306e4c6d334d7b73becaa1c`
- N4-C interval Pareto — `9b4875f82f335467142b601563e32402de1f4e92`
- N4-D laundering battery — `3a35d920f48259a8c548794a515637026a605d7a`
- N4-E decision-coupled experiments — `309e17f4f85e3296d81bfe31ce49a09d81db35d2`
- N4-F3 typed remint/transport — `eb9c4fdb8fe72ac9277807b928894bf576fd7dfd`
- N1-C typed-failure-state donor control — `f3e2e1a3e562a44f81c01f8ef0a32dc657b7e081`
- N2-F5B donor absorption — `570208578d9af41f28e39bd9a4b62ee7fe6d059c`

### QG1 — 11 bound science artifacts

- R6S all-n R6M support theorem — `e7949b35e7010ae9b24d9f69a35f210fa7f55c13`
- QG5 exact counterexample — `36fc6b6b032eff3321e0befa8a5c809733242e16`
- QG7 exact fourth-regime counterexample — `88b2477dcea656c108c7190023581e458716fdea`
- QG7b finite hybrid-family repair — `c5c84c0b0c4c16e99925c41c3eed94263a4eba93`
- QG7c partial proof — `235ed02a7d19e749cf75623ac6b7ccce5887518a`
- QG12 SixLCU theorem — `a06d2b69d9a2711b27f7f2045919517d891b42e5`
- QG15 StabPrep transfer/prospective refutation — `b31035063e9f35fece50f22f4a6cbdd6d3534185`
- QG15b predicate-language result — `18b4209914254f380433590535315473a6dcc81b`
- QG9 V6 R6I all-n support-one / `kappa=1` theorem — `be16675462ef956507489d60ae6e27a50cc05791`
- QG16 R6I objective support-one certificate cone — `bda3b7cbda2a1a992d6e2ebba01f1f429dbf688e`
- QG6 syndrome-dimension safe ceiling — `ec181174662a501ab1aef9a2c54c14e022035cbf`

### QG2 — 5 bound science artifacts

- QG5 original forecast + exact counterexample — `36fc6b6b032eff3321e0befa8a5c809733242e16`
- QG5b separately frozen repair / theorem-backed forecaster — `10717f4f84d79297d2f60f1250f3b81a16a75741`
- R6S all-n support-two theorem — `e7949b35e7010ae9b24d9f69a35f210fa7f55c13`
- QG7 later B-prime counterexample — `88b2477dcea656c108c7190023581e458716fdea`
- QG7b finite companion repair — `c5c84c0b0c4c16e99925c41c3eed94263a4eba93`

## 4. What this receipt closes

- publication-branch science-mutation concern: **closed for this audited head**;
- Q2 selection-denominator/cherry-picking reproducibility concern: **closed for declared 51-receipt universe**;
- paper-specific load-bearing artifact identity: **closed for 34 science artifacts**;
- Q1/Q2/Q4/QG1/QG2 content-ready claim remains consistent with V3 readiness ledger.

## 5. What remains open

- ordinary repository CI for the same head was still queued at the time this receipt was written;
- target LaTeX/build packages;
- citation insertion and final reference audit;
- deterministic figure/source-data generation and visual QA;
- archive DOI/permanent identifier;
- explicit repository/code/data licence(s);
- author/funding/competing-interest metadata;
- Q3 prospective scientific executions.

Any later edit to a final manuscript/package requires re-running the same fail-closed workflow before package authority can advance.
