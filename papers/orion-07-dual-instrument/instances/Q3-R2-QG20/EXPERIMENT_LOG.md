# ORION-03-R2 / QG-20 experiment log

```yaml
schema: ORIONQ.Q3ProspectiveExperimentLog.v2
experiment_id: ORION-03-R2-QG20-20260822-001
paper: ORION-03-dual-instrument
status: INSTRUMENTS_FROZEN__SCIENTIFIC_OUTCOME_UNOPENED
protocol: Q3_REPLACEMENT_PROSPECTIVE_PROTOCOL_V2.md
scientific_base: c5ba39fef4f25c46de5fb69bf07f50530f4693ca
frontier_question_id: QG-20
scientific_outcome_known_before_instrument_freeze: false
contamination_check_timestamp: 2026-08-22T06:02:00Z
contamination_search_scope: GitHub branch query qg20; code query QG20
contamination_result: CLEAN
shared_packet_sha256: c047d9a9c14b219d154d1444a34bba21418a336fa11a5134b0b5d6db9a5ee9df
lane_a_receipt_sha256: 1d6e1df7901f2a247f548e8b16fae38eb64e39cfd3ef1cccba26186bfe29a08e
lane_b_manifest_sha256: d8212bbfd05aa3647d9e08e0b079956a2bedd9079cd8a228dec9afea11c500b8
lane_b_receipt_sha256: 08fa2fca2eafbebf049bae014e30aad9772f562d980c4d9625a6e6fe4ce6bb08
lane_a_frozen_before_frontier_outcome: true
lane_b_frozen_before_frontier_outcome: true
preoutcome_relation: AGREE
scientific_analyzer_present_at_instrument_freeze: false
deferred_outcome_receipt: null
independent_replay_receipt: null
final_scoring_status: NOT_SCORED
publication_authority: NONE_UNTIL_ALL_GATES_PASS
```

## Frozen instrument outputs

Lane A: `S1_P0_BOUNDARY_OBJECTIVE_SCOPED` -> `N1_COMPLETE_REWEIGHTED_CENSUS`.

Lane B: `S1_P0_BOUNDARY_OBJECTIVE_SCOPED` -> `N1_COMPLETE_REWEIGHTED_CENSUS`.

Both instruments predict that the equal-weight P0 iff boundary must be retested when SELECT is doubled, while preserving the unary incumbent and the exact SixLCU family. No QG20 analyzer/result existed when these outputs were committed.

## Deferred section

Do not edit the frozen fields above. Add outcome binding, replay and score only after an independently generated QG20 result exists.