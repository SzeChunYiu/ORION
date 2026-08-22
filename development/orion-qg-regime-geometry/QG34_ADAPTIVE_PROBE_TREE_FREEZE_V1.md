# ORION-QG QG-34 — exact adaptive probe tree: PRE-OUTCOME FREEZE

Issue `SzeChunYiu/ORION#924`. Written and committed **before** the minimax
solver is run. No adaptive depth is predicted here.

## Why this atom is reachable now

`#924` names QG-31 `#904` and QG-32 `#911` as parents, both still on open PRs.
This lane does not consume them. The companion work in this branch
(`QG_POSITION_SYMMETRY_CEILING_PROTOCOL_V1.md`) recomputed every primitive
`#924` needs directly from `main`:

| primitive | reproduced | reported |
|-----------|-----------|----------|
| local-Clifford orbit types | 715 | 715 |
| indexed probe coordinates `K_p` | 384 | 384 |
| bulk signature classes | 45 | 45 |
| unlabeled defect-spectrum classes | 54 | 54 |
| joint `(bulk, spectrum)` classes | 92 | 92 |

Joint class size histogram (computed, not predicted):
`{1:7, 2:22, 3:6, 4:6, 6:25, 8:2, 12:14, 24:8, 48:2}`, summing to 715, largest
class 48.

## Frozen definitions

For a non-singleton state `S` of orbit types,

```
D(S)        = 1 + min_p max_v D({ o in S : K_p(o) = v })
D(singleton)= 0
```

where the minimum is over the 384 indexed probes, and probes that do not split
`S` are ignored. The primary target is

```
D_* = max over the 92 initial joint classes S of D(S).
```

Two probes inducing the same partition of `S` are the same move and are
deduplicated; this changes no value and is stated so the search is reproducible.

## Frozen result branches

Registered before execution, all four admissible:

- `QG34_EXACT_MINIMAX_ADAPTIVE_DEPTH_ESTABLISHED`
- `QG34_ADAPTIVE_EQUALS_FIXED_NO_SEPARATION`
- `QG34_ADAPTIVE_STRICTLY_CHEAPER_THAN_FIXED`
- `CANNOT_CHECK_RESOURCE_BOUND`

The last is a real outcome, not a failure: the largest joint class has 48
members and the move set has 384 probes, so exhaustion is not guaranteed in
advance.

## What must accompany any depth number

1. **A Bellman proof over the reachable state set** — the value must come from
   the recursion, not from a constructed tree that merely happens to work.
2. **A matching infeasibility certificate at `d - 1`** for the worst class, so
   the number is proved minimal and not just achieved.
3. **A per-state arity information lower bound** `ceil(log_a |S|)` where `a` is
   the largest number of distinct `K_p` values any single probe takes on `S`,
   reported alongside `D(S)` so it is visible where the bound is tight and where
   it is not.
4. **An independent re-derivation** with a different implementation and state
   encoding, per `#924` Q2.

## Explicitly not claimed by this atom

- No dependence on, and no adjudication of, QG-32b `#918` (fixed `<= 4`
  feasibility). `#924` states this atom does not depend on that outcome, and it
  does not.
- No R6 / compiled-resource claim. `NOT_R6`.
- The fixed-probe comparator (`5` fixed probes suffice) is QG-32's result, taken
  as a **cited comparator only**. If a separation is reported it is reported as
  "adaptive depth versus QG-32's reported fixed bound", not as an independent
  re-derivation of that bound.
- Q4 expected depth under priors is secondary and will only be computed after
  the minimax value is sealed, and never used to select the minimax tree.

## Authority

`mathematical_proposal: true`, `mathematical_result_credit: false`,
`proof_authority: false` beyond the machine-checked recursion, `novelty_claim:
false`. No credit over decision-tree minimization, adaptive testing,
identification trees, or DP on partitions.
