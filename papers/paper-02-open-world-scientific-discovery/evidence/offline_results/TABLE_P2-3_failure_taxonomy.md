# Table P2-3 — offline controlled-index failure taxonomy

**Authority:** `DESCRIPTIVE_ONLY`. These are terminal task classifications from the frozen 20-task offline companion after the three deterministic repeats are collapsed within task. They are not external benchmark results and carry no inferential interval.

| System | PASS | CANNOT_CHECK | premature_closure | transport_failure | budget_exhausted | other terminal failure |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `orion_full` | 19 | 1 | 0 | 0 | 0 | 0 |
| `bm25_keyword` | 0 | 0 | 20 | 0 | 0 | 0 |
| `dense_retrieval` | 0 | 0 | 20 | 0 | 0 | 0 |
| `sparse_dense_hybrid` | 0 | 0 | 20 | 0 | 0 | 0 |
| `one_pass_rag` | 0 | 0 | 20 | 0 | 0 | 0 |
| `agentic_single_route` | 0 | 0 | 20 | 0 | 0 | 0 |
| `protocol_driven_systematic_review` | 0 | 0 | 20 | 0 | 0 | 0 |
| `adaptive_multiroute_exploratory` | 0 | 1 | 16 | 3 | 0 | 0 |
| `no_route_independence_check` | 0 | 0 | 20 | 0 | 0 | 0 |
| `no_question_conditioned_read_ledger` | 19 | 1 | 0 | 0 | 0 | 0 |
| `route_stop_can_close_task` | 0 | 0 | 20 | 0 | 0 | 0 |
| `no_unavailable_route_open_state` | 19 | 0 | 1 | 0 | 0 | 0 |
| `coverage_diagnostic_controls_stopping` | 0 | 0 | 20 | 0 | 0 | 0 |
| `no_content_identity_dedup` | 14 | 1 | 0 | 0 | 5 | 0 |

## Interpretation

The evaluator has a fixed terminal-failure precedence. A task that is both route-starved and prematurely closed is classified as `premature_closure`, so a zero in a lower-precedence category does **not** prove the mechanism never occurred. In the frozen archive, the publication-bearing distinctions are:

- full ORION converts the one materially censored case into `CANNOT_CHECK` rather than a completeness claim;
- the `no_unavailable_route_open_state` ablation converts that same safety case into a premature-closure failure;
- the `no_content_identity_dedup` ablation creates five budget-exhaustion failures after duplicate work consumes the read budget;
- simple/single-pass baselines terminate with premature closure because reachable relevant material remains on unexercised routes;
- `present_but_missed`, `retrieved_but_unused`, `screening_miss`, and `route_starvation` are valid evaluator failure classes, but none is the final highest-precedence classification in this particular collapsed archive.

Source of record: `RESULTS_SUMMARY_V1.json`, itself checked by clean-CI regeneration against the frozen 840-run record digest.
