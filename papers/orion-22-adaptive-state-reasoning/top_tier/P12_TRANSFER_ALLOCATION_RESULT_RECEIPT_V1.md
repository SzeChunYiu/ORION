# ORION-22 transfer allocation result receipt V1

**Run:** GitHub Actions `32661332687` (pull_request, head `aedcaf9321aa2b9cc9acca63267eb5e8eea1ae3e`, conclusion `success`)  
**Artifact:** `p12-transfer-allocation-v1`, artifact ID `9498946866`  
**Artifact ZIP SHA-256:** `1e261db41758cafee3c8c17bbf5c3f601970273789c790750d657a3ba699afbb`  
**Primary terminal:** `P12_TRANSFER_ALLOCATION_V1_SUPPORTED`  
**Independent terminal:** `P12_TRANSFER_ALLOCATION_SECOND_INDEPENDENT_CHECKER_GREEN`  
**Agreement:** independent checker (algorithms: SAT = `full_rescan_fixpoint_up`, PATH = `bidirectional_bfs`, KNAPSACK = `exhaustive_2pow_n_enumeration`) reproduces oracle truth (`independent_truth_exact: true`), allocator selection (`independent_allocator_selection_agrees: true`), and regret (`independent_regret_agrees: true`), with `discrepancies: []`

## Exact binding

- protocol SHA-256: `e89676f852b1a45b09071ceffe7c4e92d75b4854da2e3e32d1c2877094c3ab8e`
- frozen cases SHA-256: `7694b3cffc8ff3c4f9ac93f49bf9cb0c4857921ba003199f82c463c2ef0606d4`
- primary receipt JSON SHA-256: `cf2a8ac1839b4503810b7b1150d576cd06d4f893621001bf7b8e223b3132f1f7`
- independent receipt JSON SHA-256: `8806c77d41371a2d9466bd26ffa303af90be2f8177ab392a4f736dc491f66f18`
- deterministic replay (G5): byte-identical — the artifact's replay copies (`p12_transfer_allocation_replay.json`, `p12_transfer_allocation_independent_v1.json`) hash exactly to the primary/independent receipts above (`cf2a8ac1…`, `8806c77d…`), asserted by the workflow's CI-rerun comparison step.
- allocator identity across domains (G6): one unchanged allocator (`materialize-if-q>=tau; greedy-by-desc-q; cumulative<=B; ties-by-case-order`, `tau=4`, `B=500`, signals `q_pending_multiplicity`, `c_declared_cost`, `B_budget`) — no per-domain parameterization.

## Result — unchanged allocator transfers across three charged-unit domains

Across `9` frozen cases (`3` per domain: `*_T1_BENEFICIAL`, `*_T2_NONBENEFICIAL`, `*_T3_BUDGET_RACE`), each run under `4` arms (`REASON_ONLY`, `STATE_ALWAYS`, `P12_TRANSFER_ALLOCATOR_V1`, `ORACLE_LOCATION`):

| Domain | Charged unit | REASON_ONLY regret (T1/T2/T3) | STATE_ALWAYS regret (T1/T2/T3) | Allocator regret (all) |
|---|---|---|---|---|
| `SAT_PROPAGATION` | clause_examination | 50 / 0 / 190 | 0 / 2 / 0 | **0 / 0 / 0** |
| `PATH_PLANNING` | bfs_cell_expansion | 958 / 0 / 1202 | 0 / 225 / 0 | **0 / 0 / 0** |
| `KNAPSACK` | dp_cell_fill | 514 / 0 / 1102 | 0 / 282 / 0 | **0 / 0 / 0** |

Gates: `G1_exact_outputs_all_arms: true` (all arms produce oracle-exact outputs), `G2_allocator_zero_regret_every_case: true`, `G3_restrictions_fail_somewhere: true` (both fixed policies incur positive regret in all `3` domains), `G4_resource_vector_complete_and_unlearned: true` (full `I/A/M/C/R` vectors: `I_sem`, `A_dim`, `A_transform`, `M_state`, `C_fit`, `C_infer`, `C_explicit`, `R_registered`), `G5_byte_replay: asserted_by_ci_rerun_cmp`, `G6_allocator_identity_across_domains: true`.

The allocator is never worse than either fixed policy and matches `ORACLE_LOCATION` in every case, while each fixed policy loses somewhere: `REASON_ONLY` forfeits beneficial materialization (regret up to `1202` charged ops) and `STATE_ALWAYS` pays unamortized materialization on non-beneficial structures (`2`/`225`/`282`).

## Scientific disposition

ORION-22 now has a machine-checked, replay-stable, independently corroborated result showing that a single frozen q/c/B allocation rule — unchanged across domains — attains oracle-equal location decisions under heterogeneous charged units, with complete resource-vector accounting.

This result does **not** certify ORION-16-style generality beyond the frozen 9-case set, does not establish robustness to price (`c`) miscalibration or distribution shift, and does not by itself move ORION-22 to `TOP_TIER_SUBMISSION_READY`. Robustness (price/shift stress) and hidden-parameter audit remain open per the ORION-22 gap list.

## Provenance note

The original PR head (`aedcaf93`) carried a stale pre-integration stack; this branch is a re-cut onto current `main` containing only the five files of the ORION-22 transfer suite plus this receipt. The full original stack is preserved at `archive/p12-transfer-pre-recut-aedcaf93`. The gate run above executed on the original head `aedcaf93`, whose suite files are byte-identical to the five re-cut files (verified by blob comparison: `148` of the PR's `154` added files were already on `main` unchanged; the suite files' only divergence from `main` is that they were not yet on it).
