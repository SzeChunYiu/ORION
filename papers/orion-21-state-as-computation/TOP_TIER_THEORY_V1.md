# P11 top-tier theory expansion V1

**Programme:** #977  
**Purpose:** close the general/approximate accessibility and optionality theory obligations without claiming the still-pending real-system replications.

## T11.1 — query-family accessibility rank law

Let a finite source domain have `N` states and let a family of `m` real-valued query targets be collected as columns of

\[
F\in\mathbb R^{N\times m}.
\]

A universal representation with `d` coordinates is a matrix `Phi in R^{N x d}`. A fixed linear access family uses `W in R^{d x m}` and realizes `Phi W`.

### Exact law

If every query is represented exactly,

\[
F=\Phi W,
\]

then

\[
d\ge \operatorname{rank}(F).
\]

This follows because `rank(Phi W) <= d`. The statement is about the declared fixed linear access class, not unrestricted nonlinear or time complexity.

### Approximate law

Let `sigma_1 >= ... >= sigma_r > 0` be the singular values of `F`, and define

\[
r_\epsilon(F)=\min\left\{k:\sum_{i>k}\sigma_i^2\le \epsilon^2\right\}.
\]

If

\[
\|F-\Phi W\|_F\le\epsilon,
\]

then

\[
d\ge r_\epsilon(F).
\]

Reason: `Phi W` has rank at most `d`; by the Eckart–Young–Mirsky best-rank approximation theorem no rank-`d` matrix can beat the corresponding singular-value tail. EYM is donor mathematics; P11's object is the accessibility interpretation and its empirical placement consequences.

This extends the current exact parity/rank substrate to arbitrary finite query matrices and approximate low-rank families.

## T11.2 — relative no-answer-laundering contract

Absolute statements that a sufficient representation 'does not contain the answer' are ill-posed: a state sufficient for exact responsibility necessarily contains enough information to determine that answer under some decoder.

P11 therefore uses a **relative** no-answer-laundering contract.

For a frozen trivial decoder class `D0`, compiler `C_q` is non-laundering relative to `D0` for target `f_q` iff:

1. `C_q` is fixed without protected target labels/outcomes;
2. it may only apply the prospectively registered source-state transforms;
3. `f_q` is not realizable by any decoder in `D0` over `C_q(x)`;
4. a registered downstream class `D1` strictly above `D0` can learn/realize the target from the compiled state;
5. compiler training/inference resource is charged.

### Concrete witness family

For `z in {-1,+1}^k`, `k>=2`, let the compiler only select/permutate coordinates and let the protected target be parity `prod_i z_i`. No single-coordinate/constant decoder in `D0` realizes parity, while a registered multiplicative/compositional `D1` does. Therefore coordinate selection can expose the relevant latent subspace without itself outputting the final parity bit.

This contract does not claim that parity is novel; it supplies a falsifiable operational definition that prevents a compiler from receiving credit for directly printing the protected label.

## T11.3 — exact optionality/caching law

Consider future queries `q_i` drawn iid with probabilities `p_i`, `sum p_i=1`, over horizon `H`.

Let:

- `c` = one-time cost to compile/cache a query-specific state;
- `r_c` = per-query downstream service cost from compiled state;
- `M` = one-time universal/materialization cost;
- `r_u` = per-query service cost from universal state.

The expected number of distinct query identities observed by horizon `H` is

\[
U_H=\sum_i [1-(1-p_i)^H].
\]

Hence

\[
E[C_{cache}(H)] = c U_H + H r_c,
\]

while

\[
C_{universal}(H)=M+H r_u.
\]

The optimal policy between these two is determined exactly by the sign of

\[
\Delta(H)=cU_H-M+H(r_c-r_u).
\]

This yields a distribution-sensitive crossover law rather than the false universal statement that specialization is always cheaper.

### No-cache special case

If every query is recompiled, `C_compile(H)=H(c+r_c)`. When `c+r_c>r_u`, universal materialization becomes cheaper exactly for horizons satisfying

\[
H > \frac{M}{c+r_c-r_u}.
\]

If the denominator is non-positive, that crossover does not occur under the declared costs.

### Drift/recovery extension

If raw state is discarded and a regime change occurs with probability `rho_H`, add expected recovery cost `rho_H c_recover` to compiled-only policies. Raw+summary or universal policies may therefore dominate at long horizon even when their immediate state cost is larger.

## Scope

These results close theory obligations only. The top-tier P11 claim still requires a learned non-oracle compiler, full real resource accounting and protected real-system replication. Negative decoder attacks remain authoritative evidence about where computation moved.
