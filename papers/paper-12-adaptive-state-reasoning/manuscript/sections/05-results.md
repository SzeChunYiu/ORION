# Results

The historical protected terminal is
`P12A_JOINT_ALLOCATION_SUPERIORITY_SUPPORTED`. Current claim authority is
`P12A_SUPERIORITY_AUTHORITY_WITHHELD` under
`P12A_COMPARISON_VALIDITY_ADJUDICATION_V1.json`.

| policy | mean verified success |
|---|---:|
| `JOINT_FROZEN` | **0.858154** |
| `FIXED_11` | 0.515503 |
| `ADAPTIVE_STATE_ONLY` | 0.463135 |
| `ADAPTIVE_REASON_ONLY` | 0.452759 |

The joint policy improves over the better one-axis adaptive policy by **mean `+0.334717`**, family-block 95% bootstrap CI **`[0.286008, 0.382693]`**.

The **worst held-out family gain is `+0.158203`**. Joint versus fixed `(1,1)` gain is **`+0.342651`** on average. Every allocation respects the two-unit budget, the oracle ceiling holds in every family, and two fresh executions produce the identical SHA-256

`0194bc094f5696583533af5baae41e7c339902603d3706c8a1d2a78493f98947`.

## Why the historical contrast is not a signal-count result

Both one-axis policies use pre-outcome signals, but they may emit only two
allocations while `JOINT_FROZEN` may emit four. `ADAPTIVE_STATE_ONLY` has a
perfect-signal ceiling of 0.475464 and `ADAPTIVE_REASON_ONLY` a ceiling of
0.463623, both below the winner's achieved 0.858154. The comparison therefore
does not isolate the value of a second signal.

## Regime interpretation

The large gain arises primarily because a one-axis policy's restricted action set
cannot serve the opposite-axis and jointly limited regimes at any signal value.

Giving one-signal policies the same four allocations yields mean gain 0.040771,
family-block interval [0.031006, 0.050659], and worst-family gain 0.001953. The
original positive gate then returns
`P12A_JOINT_ALLOCATION_SUPERIORITY_GATE_NOT_MET`. A new frozen P12B, not a
post-hoc threshold change, is required for positive authority.
