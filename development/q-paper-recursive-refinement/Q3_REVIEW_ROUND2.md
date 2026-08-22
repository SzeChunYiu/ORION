# Q3 refinement round 2 — closure review on V3

**Frozen manuscript:** `papers/Q-paper-03-dual-instrument/MANUSCRIPT_V3_REFINED.md`  
**Stretch after multi-item validation:** Nature Computational Science  
**Potential fallback after multi-item validation:** npj Artificial Intelligence  
**Current honest contribution:** benchmark-definition / research-instrument systems paper

## Editorial triage

### Nature Computational Science

`EVIDENCE_BLOCKED`.

The scientific calibration question remains unmeasured at `N=1`. The registered >=20 prospective frontier series is the minimum relevant evidence object for a claim about whether agreement/disagreement/cannot-check contains information about later scientific resolution.

### npj Artificial Intelligence

For a **predictive benchmark** claim: `EVIDENCE_BLOCKED` for the same reason.

For the narrower **benchmark-definition / systems resource** claim: `CONTINUE_REFINEMENT__SCIENTIFIC_EVIDENCE_LIMIT`. V3 now defines a reusable typed measurement object and has strong systems semantics, but one live item still limits demonstrated interdisciplinary/practical value. The paper can be posted/submitted to a suitable systems or benchmark venue without overclaiming, but this internal review does not declare the npj AI bar earned solely from schema quality.

## Concern closure ledger

| Round-1 concern | V3 / branch repair | State |
|---|---|---|
| Q3-R1-V1 one item cannot answer calibration question | V3 explicitly narrows to benchmark definition + first live case | `RESOLVED_BY_CLAIM_NARROWING` for present paper; predictive claim remains evidence-blocked |
| Q3-R1-V2 architectural distinctness vague | V3 includes shared-vs-distinct instrument table and explicit shared-bias limitation | `RESOLVED_BY_CLARIFICATION` |
| Q3-R1-V3 item invalidation / typed lifecycle missing | `frontier_benchmark.py` defines content-bound item, decision and deferred-score types with `INVALIDATED_ITEM`; tests reject evidence mismatch and frozen-scorer rewrite | `RESOLVED_BY_EVIDENCE` for systems contract |
| Q3-R1-P1 relation to self-consistency/debate/evaluation | `RELATED_WORK_AND_BENCHMARK_MATRIX_V3.md` compares ground-truth timing, communication, agreement-as-score, deferred scoring and unresolved-state handling | `RESOLVED_BY_CLARIFICATION` |
| Q3-R1-P2 malformed-success repair felt appended | V3 Section 6 integrates invalid-content archival into benchmark temporal identity | `RESOLVED_BY_CLARIFICATION` |
| Q3-R1-R1 formal benchmark schema absent | V3 Sections 2–4 + executable schema now provide lifecycle; `build_typed_v0_record.py` reconstructs the historically prospective V0 into the later generic schema without rewriting chronology | `RESOLVED_BY_EVIDENCE` |
| Q3-R1-R2 avoid statistics at N=1 | retained: V0 is demonstration only | `RESOLVED_BY_CLAIM_NARROWING` |
| Q3-R1-R3 availability | V3 has normal code/benchmark availability and reproduction paths | `RESOLVED_BY_CLARIFICATION` |

## Reviewer 1 — validity

The benchmark object is now technically coherent:

1. frontier item freezes question, exact evidence digest, admissible evidence, decision coordinates and scorer rule;
2. instrument decision must bind the same item/evidence and may explicitly return cannot-check;
3. deferred score binds later evidence to the old decision and cannot rewrite the frozen scorer rule;
4. agreement is deliberately absent from the per-instrument score;
5. `INVALIDATED_ITEM` remains possible when the original measurement contract is defective.

The new `build_typed_v0_record.py` is correctly labeled as a retrospective typed view of the historically prospective V0, not a second prospective experiment.

No remaining systems-contract blocker identified.

## Reviewer 2 — positioning/significance

The strongest bounded contribution is now distinct from generic multi-agent consensus:

> a temporal scientific-evaluation object in which ground truth does not exist at freeze, heterogeneous decisions are independently recorded, disagreement/cannot-check are retained, and later scientific evidence scores each frozen decision under a scorer rule that was fixed before the outcome.

This is conceptually interesting, but the empirical value of the benchmark remains an open hypothesis. A journal that requires demonstrated predictive/calibration value should wait for the multi-item series.

## Reviewer 3 — reproducibility/boundary

Reproducibility is strong for the systems layer: benchmark schemas, V0 protocol/result, typed reconstruction, Q3 harness publication contract, invalid-content regression tests and figure lifecycle are all versioned.

The main boundary is not a reporting defect. It is the absence of enough naturally resolving prospective items.

## Round-two engineering scores

| Dimension | /10 |
|---|---:|
| problem_and_question | 9.0 |
| contribution_clarity | 8.6 |
| claim_evidence_alignment | 9.0 |
| technical_rigor | 8.8 |
| novelty_positioning | 8.1 |
| significance_or_field_advance | 7.6 |
| generality_and_boundaries | 7.2 |
| reproducibility_and_availability | 9.4 |
| figure_data_statistics_quality | 7.2 |
| writing_and_evaluability | 8.7 |
| venue_fit | 6.9 |

**Mean:** 8.23/10.

## Terminal

- **Nature Computational Science validation claim:** `EVIDENCE_BLOCKED`.
- **npj Artificial Intelligence predictive/calibration claim:** `EVIDENCE_BLOCKED`.
- **Current benchmark-definition/systems paper:** scientifically coherent and internally refined, but `CONTINUE_REFINEMENT__SCIENTIFIC_EVIDENCE_LIMIT` for an npj-level impact claim.
- **Correct next evidence:** collect the already-preregistered >=20 genuinely prospective frontier items; do not manufacture retrospective items as substitutes.
