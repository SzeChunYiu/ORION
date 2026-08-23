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

---

# OUTCOME (appended after execution; nothing above was edited)

Terminal reached: `QG34_EXACT_MINIMAX_ADAPTIVE_DEPTH_ESTABLISHED`.

```
D_* = 3
```

The exact minimax adaptive probe depth above the joint bulk+spectrum summaries
is **3**. Depth distribution over the 92 initial joint classes:

| `D(S)` | 0 | 1 | 2 | 3 |
|--------|---|---|---|---|
| classes | 7 | 30 | 39 | **16** |

The 7 depth-0 classes are the singleton joint classes; 16 classes attain `D_*`,
with sizes 6, 12, 24 and 48.

## The four things the freeze required

1. **Bellman over the reachable state set.** 4,441 distinct states were valued;
   the number comes from the recursion, not from a hand-built tree.
2. **Infeasibility certificate at `d - 1 = 2`.** No depth-2 adaptive tree
   resolves *any* of the 16 worst classes. Checked on all 16, not a sample.
   So 3 is minimal, not merely achieved.
3. **Per-state arity lower bounds.** `ceil(log_a |S|)` with `a` the largest
   number of distinct `K_p` values a single probe takes on `S`, reported for
   every class. It is **tight on 80 of the 92** — so on twelve classes the
   information bound alone does not explain the depth and the Bellman value is
   doing real work.
4. **Independent re-derivation.** A second solver with a different state
   encoding (integer bitmasks over the 715 orbit ids, exact value recursion with
   arity branch-and-bound) against the first (sorted tuples, iterative-deepening
   feasibility). **Per-class agreement on all 92.**

An explicit optimal tree was extracted for the largest worst class (48 types):
depth 3, every leaf a singleton, covering all 48.

## Q4 (secondary, computed only after the minimax value was sealed)

Expected probe depth under the uniform prior over the 715 orbit types:
**2.3748**. It was not used to select the minimax tree.

## Q5 — what this does and does not say about fixed-versus-adaptive

Adaptivity never needs more than **3** probes on any input, against QG-32's
certified fixed set of **5**.

It does **not** follow that adaptive beats the fixed *minimum*. QG-32 `#911`
certifies 5 as an upper bound and QG-32b `#918` asks whether 4 suffice; the true
fixed minimum is their result to establish, and per the freeze this atom does not
adjudicate it. If that minimum turns out to be 4 or 5 there is a strict
separation; if it is 3 there is none. The number established here is the
adaptive side only.

## Relation to the symmetry ceiling in this branch

The companion result shows `bulk + spectrum` is exactly the symmetry-complete
summary (Theorem C1), so all 715/92 residual separation is position-asymmetric
information. `D_* = 3` says three position-indexed queries suffice to extract
all of it, worst case, from any of the 92 starting states.
