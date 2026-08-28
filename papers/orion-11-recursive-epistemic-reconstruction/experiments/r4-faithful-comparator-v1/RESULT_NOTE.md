# ORION-11 R4 — faithful-comparator result (LUNARC job 3550342, 2026-08-28)

**Verdict (primary frozen world set): `H_R4_FALSIFIED__FAITHFUL_COMPARATOR_MATCHES_ORION`.**
Anchor reproduction gate **PASSED**, so the comparative reading is admissible.

## Anchor gate (unchanged arms must reproduce committed v2.2.4 rates)

| arm | hidden-shift success | committed | forbidden | reproduced |
|---|---|---|---|---|
| `orion_mutation_necessity` | 1.0 | 1.0 | 0.0 | yes |
| `active_voi_repair_parent` | 0.49375 | 0.49375 | 0.0 | yes |
| `darc_r2act_dependency_parent` | 0.49375 | 0.49375 | 0.2376821651630812 | yes |
| `causalflow_minimal_counterfactual_parent` | 0.49375 | 0.49375 | 0.8213046495489243 | yes |

n_worlds 2882, hidden_shift 480, intervention budget 4.0 — all unchanged.

## Repaired parents (one change each: single top-confidence pick -> ordered search)

| arm | hidden-shift success | forbidden rate | joint | McNemar b/c vs ORION | matches ORION |
|---|---|---|---|---|---|
| `darc_search_admitted_parent` | 1.00000 | 0.23768 | 1.00000 | 0 / 0 | no (forbidden) |
| `activevoi_search_admitted_parent` | 1.00000 | **0.00000** | 1.00000 | 0 / 0 | **YES** |
| `causalflow_sibling_admitted_parent` | 1.00000 | 0.41083 | 1.00000 | 0 / 0 | no (forbidden) |

## What this establishes

1. The frozen +0.50625 hidden-shift margin over the three named parents is **fully
   recovered by ordered search alone**. All three repaired parents go from 0.49375
   to 1.00000 on protected_root_task_success. Search is not an ORION mechanic.
2. `activevoi_search_admitted_parent` matches ORION on **both** components —
   success 1.0 and forbidden-mutation rate 0.0 — with **zero discordant pairs**
   across all 480 hidden-shift worlds. It is indistinguishable from ORION on the
   pre-registered joint criterion. The pre-registered falsification fires.
3. Constraint-compliance is nevertheless **not free**: the darc and causalflow
   repairs recover task success but retain their parents' forbidden-mutation
   rates (0.238, 0.411). Two of three arms did not falsify. **Which component
   supplies activevoi's 0.000 is NOT isolated by this run** — note that
   `active_voi_repair_parent` already had forbidden 0.000 before the repair, so
   the zero may be inherited from its admission structure rather than from its
   probe ladder. Separating those requires an ablation this experiment did not
   run.

## Consequence (per protocol)

ORION-11 must **withdraw the comparative reading** of the v2.2.4 margin. The
committed v2.2.4 terminal is NOT retracted — it remains a valid internal
necessity result — but "beats three strong parents by 50 points" is an artefact
of comparators that never iterate. The defensible residual is level-ordering
economy (ORION mean cost 1.834 vs parent budget ceiling 4), not necessity.

## Honest limitation

The replication world set returned
`INSTRUMENT_FAULT__ANCHOR_REPRODUCTION_FAILED__NO_CLAIM_READ`: this runner
hardcodes the *primary* committed rates in its gate, and the replication set has
its own. That arm is **CANNOT_CHECK**, not a pass and not a failure. A follow-up
should parameterise the gate per world set and re-run.
