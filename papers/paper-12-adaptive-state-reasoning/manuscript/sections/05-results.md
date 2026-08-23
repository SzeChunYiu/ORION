# Results

The historical runner printed its preregistered superiority terminal. The later
comparison-validity adjudication withholds that claim authority. The current
bounded authority comes from the prospectively frozen P12B equal-action result.

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
original positive gate is not met. This failure motivated a new frozen P12B
rather than a post-hoc threshold change.

## Prospectively frozen P12B

P12B gives all three arms the same four actions and budget two, and scores the
exact required allocation. The independent unit is one family RNG block
(`n=32`); 1,024 episodes within each block are technical observations. Mean
two-signal gain over the stronger one-signal arm is 0.253906. The stratified
family-block 95% bootstrap interval is [0.251221, 0.256653], minimum family gain
is 0.196289, and every fixed sigma stratum exceeds 0.21. Two fresh subprocess
payloads are byte-identical, supporting the controlled equal-action
signal-complementarity claim. An append-only V1.1 revalidation reproduces the
same values under the repository lock's CPython 3.12.13 and NumPy 2.5.2
environment; the original environment receipt remains unchanged.
