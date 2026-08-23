# ORION-QG QG-39 — what the impossibility costs

QG-35 proves a summary-only compiler **cannot** select the optimal frame. This
atom asks the only question a practitioner cares about next: **so what does that
cost?**

The answer is exactly computable, because the cost model is finite and held.

## The regret curve

A summary-only compiler sees the joint class, not the type, and must commit to a
frame. Worst-case **regret** with a probe budget `k`:

```
regret of committing to p on state S = max_{o in S} [ K_p(o) - min_q K_q(o) ]
R_0(S) = min_p  (that)
R_k(S) = min( commit ,  min_p max_v R_{k-1}(S_v) )
R_k*   = max over the 92 initial joint classes
```

| probe budget | worst-case regret | classes with nonzero regret |
|---|---|---|
| **0** (summary only) | **5** | 76 / 92 |
| 1 | 3 | 45 / 92 |
| 2 | 2 | 7 / 92 |
| **3** | **0** | 0 / 92 |

Budget-0 regret histogram over the 92 classes:
`{0: 16, 1: 19, 2: 41, 3: 10, 4: 5, 5: 1}` — only 16 classes are free.

## Why 5 is large

Scale reference from the same data: `K` ranges over `[-3, 7]`, and the optimal
values `min_p K_p(o)` range over `[-3, 4]` — a total spread of **7**.

So a compiler selecting frames from the cheap summary alone can be wrong by
**5 on a scale whose entire spread of optima is 7**. This is not a marginal
penalty; it is comparable to the whole dynamic range of the objective.

## The witness, brute-force verified

Worst class: size 24, regret 5. **All 384 frames** achieve regret `>= 5` on it —
0 do better. Under the best committable frame `p = 0`:

```
type IXIXYI      own optimum = 0      cost under p = 5      excess = 5
```

And that class contains **24 distinct optimal-frame sets across 24 types** — every
single type wants a different frame.

## What this adds to QG-35

QG-35 is an impossibility theorem: the information is absent. On its own that
leaves open whether the absence matters — a compiler might lose nothing in
practice. It loses 5.

It also gives the **exchange rate**: `5 -> 3 -> 2 -> 0` for budgets `0 -> 3`.
Three probes buy exact optimality; the first probe buys the largest single
reduction. That is a directly actionable curve for anyone building on this
construction, and it is consistent with QG-35b's `D_act* = 3` — reaching regret 0
is precisely the actionable target reaching depth 0.

## Boundaries — stated, not buried

- **Units are the frozen cost model's own** (`config_cost - baseline`). This is
  **NOT** a claim about T-count, ancilla, depth, or any physical resource, and
  carries `NOT_R6`. Calibrating these units to a hardware resource is exactly the
  gap this programme has not closed.
- Worst-case regret over the class. Mean-case is reported separately (worst-class
  mean regret at budget 0 is 3.0).
- Column-type level. The instance-level analogue under QG-36's shared-frame model
  is not computed here.

## Authority

`mathematical_proposal: true`, `NOT_R6`, no compiled-resource or physical-
advantage claim, `novelty_claim: false`.
