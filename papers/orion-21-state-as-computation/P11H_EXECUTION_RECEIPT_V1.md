# P11H Execution Receipt V1

**Paper:** ORION-P11 — State as Computation
**Protocol:** `ORION.P11H.PooledSparsityLadderAttack.v1`
(`P11H_POOLED_SPARSITY_LADDER_PROTOCOL_V1.md`, frozen 2026-08-22 before the preflight)
**Executable:** `run_p11h_pooled_sparsity_ladder_v1.py`
**Result:** `P11H_POOLED_SPARSITY_LADDER_RESULT_V1.json`
**Terminal:** `P11H_POOLED_UNIVERSAL_ATTACK_PREVAILED`

## Order of operations, as executed

1. `P11H_POOLED_SPARSITY_LADDER_PROTOCOL_V1.md` frozen — ladder, pool,
   combination rule, gate roles, both thresholds, preflight seed and **execution
   seed** all written down.
2. `python -m orion.study.p11.successor_reach --write` → exit `0`,
   `P11H_PREFLIGHT_ATTAINABILITY_V1.json`. **No outcome read.**
3. `python papers/paper-11-state-as-computation/run_p11h_pooled_sparsity_ladder_v1.py`
   → exit `0`.

The draw was not computed before step 2. That ordering is the whole point: it is
the step whose absence made P11G unwinnable and P14A unmeasurable.

## Pre-run attainability preflight (step 2, before any outcome)

| gate | role | declared support | threshold | reason |
|---|---|---|---|---|
| `no_answer_laundering` | PRECONDITION | `[0.000000, 0.000000]` | `AT_MOST 0.0` | `THRESHOLD_UNCONDITIONAL` |
| `attack_live_on_ladder` | PRECONDITION | `[1.000000, 1.000000]` | `AT_LEAST 0.95` | `THRESHOLD_UNCONDITIONAL` |
| `compiled_by_64` | PRECONDITION | `[0.970117, 1.000000]` | `AT_LEAST 0.95` | `THRESHOLD_UNCONDITIONAL` |
| `pooled_universal_threshold_ge_256` | HYPOTHESIS | `[0.880811, 1.000000]` | `AT_MOST 0.95` | **`BOTH_OUTCOMES_REACHABLE`** |
| `delta64_ge_0_20` | HYPOTHESIS | `[0.000000, 0.248193]` | `AT_LEAST 0.20` | **`BOTH_OUTCOMES_REACHABLE`** |

`ThresholdPanel` outcome **`PASS`**: nothing `THRESHOLD_UNATTAINABLE`, no
hypothesis gate `THRESHOLD_UNCONDITIONAL`, and two hypothesis gates
discriminating. Both bars sit strictly inside the interval of the statistic they
read; each interval is an order statistic of the six rung readings, not a sample.

`measure_terminal_reach` over all **15** admissible draws: **`distinct_terminals`
= 2**, `PASS`. Exactly **3** of the 15 draws clear every gate — `regimes-3-4`,
`regimes-3-5`, `regimes-4-5`, the three pairs from the `r=7` rungs. That figure
was published before the seed was drawn: this protocol announced in advance that
it was 3-in-15 to print its own positive.

## Execution (step 3)

- **fresh data seed:** `2026082210`, published in the protocol before execution.
- **protected regimes drawn:** rungs `0` and `2` — cells `(14,2,3)` with a
  complete 91-column universal bank, and `(19,3,3)` with a complete 969-column
  one. `regimes-0-2` is one of the 12 draws the preflight said would not clear.
- **replay:** two fresh Python subprocesses, both exit `0`, canonical scientific
  JSON byte-identical, both digesting to
  `61ecf79f652b74447dd70caa4cf019f2e35f67559583144d68d44cd7f92dd6dd`.
- **authoritative receipt digest:**
  `8436ff99ddec0ab11a16e1ac49a924f0d7c9019998cfc42e8275f71a2db39305`.

### Gates as executed

| gate | role | statistic | bar | held |
|---|---|---:|---|---|
| `no_answer_laundering` | PRECONDITION | `0` | `AT_MOST 0.0` | **true** |
| `attack_live_on_ladder` | PRECONDITION | `1.000000` | `AT_LEAST 0.95` | **true** |
| `compiled_by_64` | PRECONDITION | `1.000000` | `AT_LEAST 0.95` | **true** |
| `pooled_universal_threshold_ge_256` | HYPOTHESIS | `1.000000` | `AT_MOST 0.95` | **false** |
| `delta64_ge_0_20` | HYPOTHESIS | `0.050586` | `AT_LEAST 0.20` | **false** |
| `two_fresh_subprocess_payloads_byte_identical` | — | — | — | **true** |
| `subprocesses_successful` | — | — | — | **true** |

Every precondition holds, so the instrument certified itself and the negative is
a measurement. Both hypothesis gates fail. **The pooled universal attack won.**

### The ladder at the execution seed

| rung | cell | universal bank | pooled 0.95 threshold | pooled best `< 256` | `delta64` | compiled @64 |
|---|---|---:|---:|---:|---:|---:|
| 0 | `(14,2,3)` | 91 | **128** | 1.0000 | +0.1482 | 1.0000 |
| 1 | `(14,3,3)` | 364 | **128** | 1.0000 | +0.0992 | 1.0000 |
| 2 | `(19,3,3)` | 969 | **128** | 1.0000 | +0.0506 | 1.0000 |
| 3 | `(14,2,7)` | 91 | `>=256` | 0.9129 | +0.2350 | 0.9840 |
| 4 | `(14,3,7)` | 364 | `>=256` | 0.8920 | +0.3172 | 0.9988 |
| 5 | `(19,3,7)` | 969 | `>=256` | 0.8876 | +0.3175 | 0.9814 |

The `r=3` / `r=7` split is identical to the one at all three preflight seeds, so
the execution seed is a fourth independent draw agreeing with the sizing. The
bank width spans 91 to 969 columns *within* each half and does not move the
verdict; `r` does.

### The drawn regimes, arm by arm, mean test accuracy over five protected queries

| arm | `(14,2,3)` @64 / @128 / @256 | `(19,3,3)` @64 / @128 / @256 |
|---|---|---|
| `COMPILED_L2` (defence) | 1.0000 / 1.0000 / 1.0000 | 1.0000 / 1.0000 / 1.0000 |
| `COMPILED_EXTRA_TREES` (control) | 1.0000 / 1.0000 / 1.0000 | 1.0000 / 1.0000 / 1.0000 |
| `UNIVERSAL_L1` | 0.8478 / **1.0000** / 1.0000 | **0.9494** / **1.0000** / 1.0000 |
| `UNIVERSAL_L2` | 0.7521 / 0.8551 / 0.9617 | 0.5898 / 0.6225 / 0.6810 |
| `UNIVERSAL_EXTRA_TREES` | 0.8518 / 0.9371 / 0.9867 | 0.5722 / 0.6990 / 0.8027 |
| **pooled** | 0.8518 / **1.0000** / 1.0000 | **0.9494** / **1.0000** / 1.0000 |

`UNIVERSAL_L1` carries the pool in both cells. This is the arm P11D and P11E
carried and P11G did not, and it is the one whose hypothesis class contains the
target: the label is an `r`-sparse linear threshold on the bank, so a sparse
linear decoder has only to find the support.

### Decoder-held-fixed control, in the receipt rather than in an audit

| drawn cell | published gap @64 | decoder-family half | state half | state share |
|---|---:|---:|---:|---:|
| `(14,2,3)` | +0.1482 | **+0.0000** | +0.1482 | **100.0%** |
| `(19,3,3)` | +0.4278 | **+0.0000** | +0.4278 | **100.0%** |

Same estimator, different columns, inside the linear family
(`COMPILED_L2 − UNIVERSAL_L2` at `n=64`): **+0.2479** and **+0.4102**.

This is the sharp part of the result, and it cuts both ways at once. The
decomposition goes P11's way *harder* than P11G's did — at `r=3` the change of
decoder family explains **none** of the gap against the tree arm, against 13.3%
and 44.6% in P11G's cells, so what gap exists is entirely the change of state.
And the defence still loses, because at `r=3` the gap is **+0.0506** against a
`0.20` bar and the pooled attack reaches the target at `n=128`. Attribution and
magnitude are different questions: the advantage is wholly a state effect and it
is too small to certify.

## What this establishes

1. **The attack could have won, and did.** P11H's hypothesis gates had both
   values reachable over its own admissible register before the seed was drawn,
   and the seed drew a losing pair. That is a measurement, not arithmetic, and
   it is the property `UNWINNABLE_ATTACK_PREDETERMINED_SURVIVAL` says P11G
   lacked.
2. **P11G's headline does not generalise across state width.** "Compiled state
   retains a low-sample advantage over a universal decoder on the complete
   parity bank" is false at `r=3` under P11G's own unedited thresholds, against a
   pool that includes the paper's own best known attack.
3. **The boundary is located and it is the width of the compiled state.** Across
   the whole ladder the pooled attack reaches `0.95` by `n=128` at every `r=3`
   rung and at no `r=7` rung, while the complete universal bank moves from 91 to
   969 columns inside each half without changing a verdict. The compiled-state
   advantage is a claim about how much query-conditioned state the compiler
   resolves, not about how large the universal representation is.

## What this does not establish

- **P11G is not overturned and nothing of it is edited.** Its protocol, seed,
  arms, thresholds, receipt and terminal are retained verbatim; its scientific
  payload still digests to
  `a2b0c33ce3c39e54ca1aa400a2b7d52d019fc4503f6cd5eb726c7b8bbe79a7cc`. P11H is a
  different protocol at different regimes and its negative is its own.
- **The `r=7` half of the ladder is not a P11H positive.** Three of the fifteen
  admissible draws would have printed
  `P11H_COMPILED_STATE_ADVANTAGE_SURVIVED_POOLED_ATTACK` and the seed did not
  draw one. The `r=7` rungs are published as ladder diagnostics; they carry no
  terminal and no claim authority, and reading them as a positive would be
  choosing a rung after seeing it, which is exactly what the draw exists to
  prevent.
- **No universal nonlinear lower bound, no real-agent superiority.** The claim
  authority section of the protocol is unchanged by the outcome.
- **The `r=5` boundary is not resolved.** It was excluded before execution for
  instability across the three preflight seeds, in both directions, and remains
  an open coordinate for a further successor with more queries or more seeds.

## Reproduce

```
python -m orion.study.p11.successor_reach            # exit 0: the preflight passes
python papers/paper-11-state-as-computation/run_p11h_pooled_sparsity_ladder_v1.py
python -m orion.study.p11.attack_audit               # exit 3: P11G still blocks, permanently
python -m pytest tests/unit/study/p11
```
