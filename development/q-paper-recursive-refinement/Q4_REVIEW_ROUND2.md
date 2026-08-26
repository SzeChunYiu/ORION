# Q4 refinement round 2 — closure review on V3

**Frozen manuscript:** `papers/orion-08-typed-state/MANUSCRIPT_V3_REFINED.md`  
**Stretch after real-domain transfer:** Nature Machine Intelligence  
**Current target:** npj Artificial Intelligence / AI-for-science methods venue

## Editorial triage

### Nature Machine Intelligence

`EVIDENCE_BLOCKED` for a real scientific-agent claim.

The manuscript now has a coherent benchmark theory and stronger uncertainty reporting, but all headline primary evidence remains exact-synthetic. The preregistered real-decision study is the correct closure. No additional synthetic family or language polish can substitute for transfer evidence.

### npj Artificial Intelligence

**Posture:** `READY_FOR_SCOPED_TARGET__POSITIONING_RISK`.

V3 now presents one reusable matched-information benchmark contract rather than six disconnected wins. It contains strong comparators, prespecified hostile/no-value regimes, exact-synthetic reproducibility, paired uncertainty for stochastic generators, donor absorptions and explicit simulation-to-reality limits. The paper is still specialized and theory-building, but its current scope is now commensurate with its evidence.

## Concern closure ledger

| Round-1 concern | V3 closure | State |
|---|---|---|
| Q4-R1-V1 post-hoc six-family synthesis | V3 repeatedly labels the epistemic-binding taxonomy as post-study theory building; family-specific preregistered claims remain primary | `RESOLVED_BY_CLAIM_NARROWING` |
| Q4-R1-V2 point estimates without paired uncertainty | `publication_analysis.py` reruns frozen seeded episodes and `PUBLICATION_PAIRED_ANALYSIS_V1.json` records paired differences + deterministic 95% bootstrap intervals | `RESOLVED_BY_ANALYSIS` |
| Q4-R1-V3 heterogeneous metrics pooled | V3 never computes a universal effect size; figures contract requires separate scales/panels | `RESOLVED_BY_CLARIFICATION` |
| Q4-R1-P1 generic typed-memory novelty | `NEAREST_WORK_MATRIX_V3.md` gives zero priority credit to typed memory, provenance, stale-state revision and VoI primitives | `RESOLVED_BY_CLARIFICATION` |
| Q4-R1-P2 reusable benchmark object absent | `BENCHMARK_INDEX_V1.json` provides common machine-readable fields across six families | `RESOLVED_BY_EVIDENCE` |
| Q4-R1-R1 figure architecture | `FIGURE_CONTRACT_V3.md` freezes taxonomy, control/effect matrix, paired-uncertainty and boundary figures | `RESOLVED_BY_CLARIFICATION`; final rendering remains production |
| Q4-R1-R2 deterministic publication analysis availability | `REPRODUCE.md` now reruns and byte-compares the paired-analysis JSON | `RESOLVED_BY_EVIDENCE` |
| Q4-R1-R3 excessive decimal precision | V3 rounds manuscript values while keeping exact receipts | `RESOLVED_BY_CLARIFICATION` |

## Reviewer 1 — validity/statistics

The paired publication analysis improves the paper because it exposes heterogeneity rather than merely adding intervals.

- N4-A typed vs uniform VoI: mean utility difference 1.111, 95% bootstrap interval [0.833, 1.400].
- N4-C targeted vs random verification: paired regret reduction 0.142 [0.100, 0.187].
- N4-E decision-VoI vs information gain: utility difference 2.146 [1.976, 2.299].
- N4-F3 mixed typed vs rederive: 2.264 [1.717, 2.825], while the no-value regime is exactly 0 [0,0].
- N4-B scoped vs never-reopen intervals cross zero in both registered regimes; V3 now correctly narrows the result to strong protection against **unscoped over-reopening** without claiming a clear advantage over conservative never-reopen.

That last correction materially increases claim-evidence integrity.

No scoped statistical blocker identified. These are deterministic bootstrap summaries over one frozen seed family and are not independent replications; the manuscript states that boundary.

## Reviewer 2 — positioning/significance

The residual contribution is now specific:

> a six-family matched-information benchmark suite testing whether explicit relations between scientific facts and applicability/uncertainty/lineage/decision role alter downstream decisions, with strong donor and no-value controls.

The paper no longer claims that any single memory primitive is new. Its generality is benchmark-theoretic rather than deployment-level.

The real-domain transfer gate remains the obvious next scientific test and is already preregistered.

## Reviewer 3 — reproducibility/readability

Reproducibility is strong: generators, seeds, frozen outputs, benchmark index, paired-analysis code/result, donor controls and one-command reproduction instructions are committed. The figure contract makes negative/no-value regimes visible rather than relegating them to limitations.

A permanent DOI-tagged release remains journal-production work.

## Round-two engineering scores

| Dimension | /10 |
|---|---:|
| problem_and_question | 9.0 |
| contribution_clarity | 8.8 |
| claim_evidence_alignment | 9.2 |
| technical_rigor | 8.7 |
| novelty_positioning | 8.3 |
| significance_or_field_advance | 8.0 |
| generality_and_boundaries | 7.8 |
| reproducibility_and_availability | 9.5 |
| figure_data_statistics_quality | 8.5 |
| writing_and_evaluability | 8.8 |
| venue_fit | 7.9 |

**Mean:** 8.59/10.

## Terminal

- **Nature Machine Intelligence real-agent/scientific-discovery claim:** `EVIDENCE_BLOCKED`.
- **npj Artificial Intelligence exact-synthetic mechanism/benchmark claim:** `READY_FOR_SCOPED_TARGET__POSITIONING_RISK`.
- **New synthetic benchmark family needed:** `NO`.
- **Correct next scientific upgrade:** execute the frozen real-domain matched-information study if the broader transfer claim is desired.
