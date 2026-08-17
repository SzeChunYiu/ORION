# Table P2-3 — offline controlled-index failure taxonomy

**Authority:** `DESCRIPTIVE_ONLY`. These are terminal task classifications from the frozen 20-task offline companion after the three deterministic repeats are collapsed within task. They are not external benchmark results and carry no inferential interval.

| System | PASS | CANNOT_CHECK | present-but-missed | retrieved-but-unused | screening miss | route starvation | transport failure | premature closure | budget exhausted |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `orion_full` | 19 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `bm25_keyword` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | 0 |
| `dense_retrieval` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | 0 |
| `sparse_dense_hybrid` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | 0 |
| `one_pass_rag` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | 0 |
| `agentic_single_route` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | 0 |
| `protocol_driven_systematic_review` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | 0 |
| `adaptive_multiroute_exploratory` | 0 | 1 | 0 | 0 | 0 | 0 | 3 | 16 | 0 |
| `no_route_independence_check` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | 0 |
| `no_question_conditioned_read_ledger` | 19 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `route_stop_can_close_task` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | 0 |
| `no_unavailable_route_open_state` | 19 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| `coverage_diagnostic_controls_stopping` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 | 0 |
| `no_content_identity_dedup` | 14 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |

## Interpretation

The evaluator has a fixed terminal-failure precedence. A task that is both route-starved and prematurely closed is classified as `premature_closure`, so a zero in a lower-precedence category does **not** prove the mechanism never occurred. The zero columns above mean only that those classes never became the **terminal highest-precedence label** in this collapsed archive.

The publication-bearing distinctions are:

- full ORION converts the one materially censored case into `CANNOT_CHECK` rather than a completeness claim;
- the `no_unavailable_route_open_state` ablation converts that same safety case into a premature-closure failure;
- the `no_content_identity_dedup` ablation creates five budget-exhaustion failures after duplicate work consumes the read budget;
- simple/single-pass baselines terminate with premature closure because reachable relevant material remains on unexercised routes;
- the exploratory adaptive comparator exposes three terminal `transport_failure` cases in addition to its premature closures.

Source of record: `RESULTS_SUMMARY_V1.json`, itself checked by clean-CI regeneration against the frozen 840-run record digest.
