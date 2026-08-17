# Table P2-3 — offline controlled-index failure taxonomy

**Authority:** `TIER_B_committed`. These are terminal task classifications from the frozen 390-task offline companion after the three deterministic repeats are collapsed within task. They are not external benchmark results; the achieved precision for this family is recorded in `RESULTS_SUMMARY_V1.json` under `achieved_precision`, and no primary is promoted here.

| System | PASS | CANNOT_CHECK | present-but-missed | retrieved-but-unused | screening miss | route starvation | transport failure | premature closure | budget exhausted |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `orion_full` | 319 | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 59 |
| `bm25_keyword` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 390 | 0 |
| `dense_retrieval` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 390 | 0 |
| `sparse_dense_hybrid` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 390 | 0 |
| `one_pass_rag` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 390 | 0 |
| `agentic_single_route` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 390 | 0 |
| `protocol_driven_systematic_review` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 390 | 0 |
| `adaptive_multiroute_exploratory` | 0 | 13 | 16 | 0 | 0 | 0 | 65 | 296 | 0 |
| `no_route_independence_check` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 390 | 0 |
| `no_question_conditioned_read_ledger` | 319 | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 59 |
| `route_stop_can_close_task` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 390 | 0 |
| `no_unavailable_route_open_state` | 319 | 0 | 0 | 0 | 0 | 0 | 0 | 12 | 59 |
| `coverage_diagnostic_controls_stopping` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 390 | 0 |
| `no_content_identity_dedup` | 236 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 145 |

## Interpretation

The evaluator has a fixed terminal-failure precedence. A task that is both route-starved and prematurely closed is classified as `premature_closure`, so a zero in a lower-precedence category does **not** prove the mechanism never occurred. The zero columns above mean only that those classes never became the **terminal highest-precedence label** in this collapsed archive.

The publication-bearing distinctions are:

- full ORION converts 12 materially censored cases into `CANNOT_CHECK` rather than a completeness claim;
- the `no_unavailable_route_open_state` ablation converts those same safety cases into 12 premature-closure failures;
- the `no_content_identity_dedup` ablation creates 145 budget-exhaustion failures after duplicate work consumes the read budget;
- simple/single-pass baselines terminate with premature closure because reachable relevant material remains on unexercised routes;
- the exploratory adaptive comparator exposes 65 terminal `transport_failure` cases in addition to its premature closures.

Source of record: `RESULTS_SUMMARY_V1.json`, itself checked by clean-CI regeneration against the frozen 16380-run record digest.
