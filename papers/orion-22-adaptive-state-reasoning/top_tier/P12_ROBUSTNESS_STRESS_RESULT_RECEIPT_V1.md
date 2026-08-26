# P12 robustness stress V1 — result receipt

**Study:** `P12_ROBUSTNESS_STRESS_V1` (protocol `P12_ROBUSTNESS_PROTOCOL_V2.md`, frozen at `9f7a34ca`; expanded 27-case file frozen at `766414f6`)
**Terminal:** `P12_ROBUSTNESS_STRESS_V1_EXECUTED`
**CI run:** `32672856998` (GitHub Actions, `p12-robustness-stress-v1` workflow, head `16834fe35`) — conclusion **success**
**Artifact:** `9501847244` (`p12-robustness-stress-v1`, 30,610 bytes)

## Artifact-member SHA-256 digests (each output byte-identical to its in-run replay)

| member | SHA-256 |
|---|---|
| `p12_robustness_stress_v1.json` (runner) | `591077a27741261666926b116cbe5e64f62cde7ad350922d8635997d9a1e48a1` |
| `p12_robustness_replay.json` (runner replay) | `591077a27741261666926b116cbe5e64f62cde7ad350922d8635997d9a1e48a1` |
| `p12_robustness_independent_v1.json` (checker) | `25c763f165a02c344a999d556ef77089409cef24f838c62d9fc7817e1c78a3a4` |
| `p12_robustness_independent_replay.json` (checker replay) | `25c763f165a02c344a999d556ef77089409cef24f838c62d9fc7817e1c78a3a4` |
| `p12_hidden_parameterization_audit_v1.json` (audit) | `fa099848a3dee29d1da9b50f326407695d56c69755c2670be8a17903bdf60fa9` |
| `p12_audit_replay.json` (audit replay) | `fa099848a3dee29d1da9b50f326407695d56c69755c2670be8a17903bdf60fa9` |

## Executed coverage (all gates green)

- RG1 exactness: every arm's outputs equal V1 ground truth in every domain, regime and mix — **true**.
- RG3 coverage: 5 price regimes (`FLAT, MEM2X, CMP2X, MEM4X, CMP4X`); 45 V1 case-regime cells; 135 expanded case-regime cells; 4 B1 case mixes; 3 B2 joint shared-budget mixes — complete.
- RG4 two implementations: independent checker (deliberately different algorithm classes: full-rescan fixpoint SAT-UP, bidirectional-BFS PATH, exhaustive 2^n KNAP) — `P12_ROBUSTNESS_SECOND_CHECKER_GREEN`, **36 cases checked, 0 discrepancies**.
- RG5 hidden-parameterization audit: `P12_HIDDEN_PARAMETERIZATION_AUDIT_GREEN`, self-validation valid, static axis clean, dynamic stripped-input replay clean.
- V1 FLAT replication: the original V1 zero-regret claim at FLAT prices **replicates** on the runner's own numbers and on the checker's independent numbers.

## Verdicts (data-bound, recorded exactly as the runs produced them)

| axis | verdict |
|---|---|
| `price_axis` | **BROKEN** — `price_axis_zero_regret_regimes: []` (no regime yields zero allocator regret across all 36 case records) |
| `distribution_shift_axis` | **BROKEN** — `shift_case_mixes_zero_regret: false`, `shift_joint_mixes_zero_regret_regimes: []` |
| `hidden_parameterization_axis` | bound by the separate audit artifact — GREEN |

**Scientific reading (bounded):** the unchanged-allocator V1 transfer result (zero regret under FLAT unit prices) does **not** survive price skew (`MEM*`/`CMP*` regimes) or task-distribution shift (B1 mixes, B2 joint mixes). The FLAT zero-regret claim itself replicates exactly. The hidden-parameterization audit certifies the breakage is a property of the frozen allocator under stress, not of undisclosed tuning.

## Provenance of the checker fix (run history)

Runs 1–5 (through `ea79c064`) were implementation-debug iterations of harness code (audit AST handling, cache priming, report shape). Run `32667527161` failed only the final coverage assert: the checker keyed its case records by `(domain, case_id)`, and because the expanded set carries the nine V1 case_ids verbatim, the count collapsed to 27 distinct keys instead of 36 checked records. Fixed at `16834fe35` by keying `(tag, domain, case_id)`; this also makes the checker's price-axis scope exactly mirror the runner's registered `[v1_report, exp_report]` scope and makes the V1-FLAT replication check read its own pass's cells.

**Frozen-surface integrity:** `git diff 766414f6..16834fe35` over `P12_ROBUSTNESS_PROTOCOL_V2.md`, `p12_transfer_cases_v1.json`, `p12_transfer_cases_expanded_v1.json` is **empty** — protocol and case files were never modified after the freeze; all post-freeze commits touch harness code only (workflow, audit, runner, checker).

## Non-claims

- This receipt does **not** claim the allocator is price-robust or shift-robust; both axes are BROKEN as produced.
- It does not claim anything about allocators other than the frozen `P12_TRANSFER_ALLOCATOR_V1` (tau=4, greedy-by-q, cumulative<=B=500).
- It does not upgrade, widen or retract the landed P12B equal-action complementarity authority; it stress-tests the V1 transfer allocation layer only.
- The BROKEN verdicts are negatives with an open revival lane (selectivity/regime-conditioned allocation), recorded in the negative-revival backlog.
