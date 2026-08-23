# Results

The protected terminal is `P12A_JOINT_ALLOCATION_SUPERIORITY_SUPPORTED`.

| policy | mean verified success |
|---|---:|
| `JOINT_FROZEN` | **0.858154** |
| `FIXED_11` | 0.515503 |
| `ADAPTIVE_STATE_ONLY` | 0.463135 |
| `ADAPTIVE_REASON_ONLY` | 0.452759 |

The joint policy improves over the better one-axis adaptive policy by **mean `+0.334717`**, family-block 95% bootstrap CI **`[0.286008, 0.382693]`**.

The **worst held-out family gain is `+0.158203`**. Joint versus fixed `(1,1)` gain is **`+0.342651`** on average. Every allocation respects the two-unit budget, the oracle ceiling holds in every family, and two fresh executions produce the identical SHA-256

`0194bc094f5696583533af5baae41e7c339902603d3706c8a1d2a78493f98947`.

## Why the result is stronger than a fixed-baseline win

The scientific comparator is not the fixed `(1,1)` policy. Both one-axis policies already use pre-outcome signals adaptively. The protected result therefore isolates the value of **having both resource coordinates available to the policy**, rather than the generic value of adaptation.

## Regime interpretation

The gain arises because families contain different mixtures of access-limited, reasoning-limited and jointly limited examples. A one-axis policy has a structural blind spot: it cannot move resource to the other locus even when its signal identifies that need. The joint policy can.

The experiment therefore tests the proposition's key mechanism without giving the joint arm extra computation.