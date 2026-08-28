# Permanent negative history

The historical experiment constructed independent binary latent variables `(x,m,r)` and responsibilities `PREDICT=x`, `DECIDE=x`, `INTERVENE=x*m`, `VERIFY=x*m`, and `REPAIR=r`. Representations were `Z1=(x)`, `Z2=(x,m)` and `Z3=(x,m,r)`.

Exact enumeration produced the intended responsibility ladder: all representations were perfect for prediction/decision; `Z1` was exactly 0.5 on intervene/verify while `Z2/Z3` were 1.0; `Z2` was 0.5 on repair while `Z3` was 1.0. Exact upward debts were therefore +0.50.

However, the frozen protocol also required the maximum deviation among 100 finite-sample sanity replicates of `n=1024` to be ≤0.05. The observed maximum was `0.0556640625` at replicate 92. The controlled sufficiency-debt gate is therefore permanently not met.

## Root cause

The harness grouped a finite sample by compact state, selected the majority target value from that same sample and credited that majority on the same observations, then maximized deviation over 100 replicates. The statistic combines within-sample majority optimism with an extreme-value operation. The correct response is not to change `0.05` after observing `0.0556640625`. The old terminal stays negative. The successor changes the estimand: exact support is evaluated by exhaustive equivalence classes, while efficacy is evaluated on a fresh safety–cost benchmark.