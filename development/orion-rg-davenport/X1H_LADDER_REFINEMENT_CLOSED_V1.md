# ORION-RG X1-H — the ladder-refinement direction is closed

This programme named "a multi-threshold refinement of the `k`-wise Davenport
bound" as its next mechanic. That direction is now **closed by proof**, and the
new statistics built along the way **do not beat the published bound**.

Recording it as a negative because the alternative — writing up two new lemmas
without their scoreboard — would be advertising.

## The headline number

Across **26 evaluated rungs**, the refined bounds constructed here strictly beat
Freeze–Schmid Prop. 3.1(3) on **0**.

## Two impossibility theorems

**N1.** Let `h(n) = max{ minzs(S) : |S| = n }`. Then `h(n) <= T` iff
`n >= s_{<=T}`, and `min{ L : L - h(L) >= D_k }` equals
`min_T max(s_{<=T}, D_k + T)`. So **the sharpest possible bound of the form
"extract one minimum-length zero-sum, then apply `D_k` to the remainder" is
literally Prop. 3.1(3)**. Committing to a single threshold loses nothing.

**N2.** `j`-fold peeling with thresholds `T_1..T_j` gives

```
D_{m+j} <= max( max_i ( s_{<=T_i} + sum_{l<i} T_l ),  D_m + sum_l T_l )
```

At `j = 2` this reads `max(s_{<=T1}, s_{<=T2}+T1, D_m+T1+T2)`, while iterating
Prop. 3.1(3) twice reads `max(s_{<=T2}, s_{<=T1}+T2, D_m+T1+T2)`. The two are
exchanged by swapping `(T1, T2)`, so as the thresholds range over all values the
two families give the **same set of bounds**. **Multi-threshold peeling gains
nothing over single-threshold.**

Greedy peeling `m_1 <= m_2 <= ...` is a *lower* bound on the peel sizes and does
not constrain the adversary; the worst-case chain `n_i = n_{i-1} - h(n_{i-1})`
reproduces the iterated N1 bound exactly.

This also explains a prior-art finding: **Freeze–Schmid Prop. 3.2 *is* the
published multi-threshold recursive version** of exactly this idea.

## The new statistics, and why they do not help

Two `k`-independent statistics were constructed:

- `f_T^{!=0}(G)` — max length with `minzs(S) > T` **and** `sigma(S) != 0`;
- `D_k^{>=m}(G)` — least `L` such that every length-`L` sequence with
  `minzs >= m` has `k` disjoint zero-sums.

giving **Lemma D\***: `D_{k+1} <= min_T max( D_{k+1}^{>=T+1}, D_k + T )`, which
is `<=` Prop. 3.1(3) **termwise**, and **Lemma S**, its hand-provable relaxation.

They are never worse. They are also never strictly better on any tested rung.

Two boundary conditions were established, and both matter:

- **Lemma S can close a gap at rung `k` only if the target `L` satisfies
  `L >= kD+1`.** For `C_2^4, k=1`: `8 >= 6` ✓. For `C_5^3, k=2`: `25 < 27` ✗ —
  so **Lemma S provably cannot close `C_5^3`**, independent of whether that gap
  is real.
- **Non-circularity:** `D_{k+1}^{>=T+1}` may be used only for `T >= exp(G)`. At
  `T < exp(G)`, `D_{k+1}^{>=2} = D_{k+1}` and the bound is circular.

## What would be needed instead

Both impossibility theorems point the same way. Any strict improvement must use a
statistic that constrains **which** sequences realise `minzs > T` — not merely
how long such a sequence can be. Every quantity in the `s_{<=T}` family answers
only the second question, and N1/N2 show that family is exhausted.

## Corrections this produced

- The **`C_2^4, k=1` "gap" reported earlier in this programme was an artifact**
  of a weaker restatement of the published bound. Prop. 3.1(3) in its correct
  form already gives 8, the true value. There was never a gap there.
- `eta_l` was a loose renaming of the paper's `s_{<=l}(G)`; `eta(G)` conventionally
  means `s_{<=exp(G)}(G)` specifically. This document uses `s_{<=T}`.

## Recorded operator error

Five evaluation entries (`C_4^2 k=3`, `C_6^2 k=2`, `C_3+C_9 k=2`,
`C_2^3+C_4 k=2`, `C_5^3 k=1`) initially returned `CANNOT_CHECK` because running
child processes were killed — a `ps | grep -c` reported 0 live collectors due to
output filtering, and a `pkill` was issued on that basis. **Not a resource
limit.** They are labelled `CANNOT_CHECK_ERROR`, distinct from genuine bounds.

Genuine resource bounds, separately: `D_2(C_5^3)`, `D_3(C_5^3)` are far outside
this enumerator's budget (state `125^k` bytes at depth 20–25 over 125 symbols).
Those constants are established elsewhere in this repo by different instruments
(`X1F_D3_C5CUBED_PROTOCOL_V1.md`), not by this one.

## Authority

`mathematical_proposal: true`, `proof_authority: false` beyond N1/N2 and the
machine-checked evaluation, `novelty_claim: false`. No credit taken over
Freeze–Schmid, whose bound this analyses and fails to improve.

## Independent confirmation of the headline

The `0 of 26` scoreboard was re-checked in the main session with a separate
brute-force implementation, computing `f_T^{!=0}(C_2^4)` from scratch by
enumerating multisets and testing every subset:

```
T=1  f_T^!=0=12   eta_T^!=0=13   max(eta_T^!=0, D+T) = 13
T=2  f_T^!=0=12   eta_T^!=0=13   max(eta_T^!=0, D+T) = 13
T=3  f_T^!=0= 7   eta_T^!=0= 8   max(eta_T^!=0, D+T) =  8   <-- optimum
T=4  f_T^!=0= 4   eta_T^!=0= 5   max(eta_T^!=0, D+T) =  9
T=5  f_T^!=0= 4   eta_T^!=0= 5   max(eta_T^!=0, D+T) = 10
```

**Lemma S gives 8. Freeze–Schmid Prop. 3.1(3) gives 8. The truth is 8.**

So on the one instance where this programme previously believed it had found a
gap, the new lemma is **tight and not better** — which is the whole finding, and
it now rests on two independent implementations rather than one.
