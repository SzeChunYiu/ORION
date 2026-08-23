# P9 unified I/A/C/M resource-ledger result receipt V2

**Programme:** #977
**State:** `BOUND_TO_RUN` (filled from the actual workflow run; no local execution)
**Protocol:** `P9_UNIFIED_RESOURCE_LEDGER_PROTOCOL_V2.md` (SHA-256 `13309b302fc3d218cc60433545ce16360c632a9ccc809feeb0fdd764fb8158d7`, including the pre-execution `R_registered` erratum)

## Run binding

- Workflow: `.github/workflows/p9-unified-resource-ledger-v2.yml`
- Run: `32664198718` (`https://github.com/SzeChunYiu/ORION/actions/runs/32664198718`), head `c3f2709a5b029b58246d2435cdfdec7ddb454acf`, conclusion `success`
- Artifact: `p9-unified-resource-ledger-v2`, id `9499807171`, ZIP SHA-256 `67e768a7b9d607c7cd8b6c8e9b4eb52fb4bfdbbff4221225919f8173d1b4bf92` (committed evidence JSON file SHA-256 `efae315e7269c5f3b4ab8ce32402f443f80eb774ecec6aab0f1e879bb09d97a9`, byte-identical to the artifact member)
- Evidence committed at: `papers/paper-09-structured-epistemic-learning/evidence/P9_UNIFIED_RESOURCE_LEDGER_V2.json` (ledger `receipt_sha256` `364b84665f00888527202723164778048c84e1c94f5413f8348dbb87e4668b0a`)

## Terminal

`P9_UNIFIED_RESOURCE_LEDGER_V2_GREEN` — second checker `P9_UNIFIED_RESOURCE_LEDGER_SECOND_CHECKER_V2_GREEN`, deterministic byte replay verified, frozen causal diagnostic re-executed in-run to `P9_CAUSAL_DIAGNOSTIC_V1_SUPPORTED` with identical five-cell decisions.

## Survival of the causal-diagnostic conclusion under matched full accounting

**Verdict: `SURVIVES_FULL_ACCOUNTING`.** Every endpoint held:

- all five frozen decisions reproduced by re-derivation under corrected accounting (probe predictions and protected golds);
- diagnostic accuracy `4/5`, generic `UNCERTAINTY_ESCALATE_COMPUTE` accuracy `1/5`;
- the `D-A` protected cell remains `CANNOT_CHECK` (quality-transport failure below the 0.965 target; no accounting rule can move it);
- diagnostic false compute-escalations `0`, generic `4`.

## Per-cell matched resource vectors (corrected V2 accounting)

`R9 = (I_sem, A_dim, A_transform, M_state, C_fit, C_infer, C_explicit | R_registered)`. "Hidden total" = `A_transform + M_state + C_fit + C_infer + C_explicit`, the compute the abstract registered cost conceals.

| Cell | Arm (selector) | I_sem | A_dim | A_transform | M_state | C_fit | C_infer | C_explicit | R_reg | Hidden total |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| D-A (gold `CANNOT_CHECK`) | diagnostic `ACCESSIBILITY` | 64 | 64 | 64 | 778 | 68992 | 64 | 0 | 2 | 69898 |
| D-A | generic `COMPUTATION` | 64 | 64 | 0 | 68928 | 68992 | 68800 | 0 | 12 | 206720 |
| D-I | diagnostic `INFORMATION` | 64 | 64 | 0 | 778 | 68992 | 64 | 0 | 8 | 69834 |
| D-I | generic `COMPUTATION` | 1 | 1 | 0 | 1077 | 1078 | 1075 | 0 | 12 | 3230 |
| B-I | diagnostic `INFORMATION` | 4 | 4 | 0 | 0 | 0 | 1 | 4 | 8 | 5 |
| B-I | generic `COMPUTATION` | 3 | 3 | 0 | 0 | 0 | 1 | 8 | 12 | 9 |
| B-A | diagnostic `ACCESSIBILITY` | 2 | 2 | 1 | 0 | 0 | 1 | 0 | 2 | 2 |
| B-A | generic `COMPUTATION` | 2 | 2 | 0 | 0 | 0 | 1 | 1 | 12 | 2 |
| B-C | diagnostic = generic `COMPUTATION` | 7 | 7 | 0 | 0 | 0 | 1 | 7 | 12 | 8 |

Digits split: 1078 train / 359 probe / 360 protected (frozen seeds 20260901/20260902). `M_state` for the `COMPUTATION` arms is support-vector-coordinate count plus the shared scaler (68800+128 for `D-A`; 1075+2 for `D-I`). The registered-cost ordering and the physical-hidden-compute ordering disagree in direction in `D-I` (registered 8 < 12, hidden 69834 > 3230, because restoring the 64-pixel information requires the full re-fit); per the frozen protocol no scalar exchange rate may be derived from this, and the disagreement is disclosed rather than resolved. In `D-A` the generic escalation conceals ~3x the hidden compute of the diagnostic arm (206720 vs 69898) while registering 12 vs 2.

## Vector-dominance disclosure

Zero dominance findings across all ten split-level checks (5 cells x probe/protected). No selected arm is strictly dominated on the seven physical coordinates by another target-reaching arm of its cell; the `D-I` registered-versus-hidden disagreement above is a cross-arm cost-ordering disclosure, not a dominance violation (`COMPUTATION` exceeds `M_state` 1077 > 778).

## Audit corrections executed (V1 → V2)

1. fitted scaler coordinates now counted in `M_state` (+128 on every `D-A` arm and `D-I` `INFORMATION`; +2 on the remaining `D-I` arms);
2. exact-domain readout touch counted (`C_infer = 1` on every `B-*` arm);
3. `B-C` `ACCESSIBILITY` serialization work counted (`A_transform = 7`);
4. hardcoded decisions replaced by re-derivation from re-executed frozen qualities.

No quality value, target, registered cost, prediction, protected gold, or protected negative was altered.

## Authority boundary

Post-outcome accounting for the bounded P9 causal-diagnostic headline only. This receipt does not establish a universal resource exchange rate, does not repair the `D-A` `CANNOT_CHECK` cell, does not convert the wine null into evidence for or against universality, and does not touch the protected Qwen scaling negative (`LLM_STRUCTURE_SCALING_FRONTIER_NOT_SUPPORTED`, which must not be repaired or re-run).
