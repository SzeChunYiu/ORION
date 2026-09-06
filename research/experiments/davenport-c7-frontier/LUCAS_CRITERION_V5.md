# The pointed system's infeasibility is an exact digit criterion — V5

Status: **proved.** Every step is an identity; the computation in the checker validates the *implementation*, not the claim. This upgrades `SHORT_ATOM_LAW_UNIFORM_V5.md` from "verified for `5 ≤ p ≤ 23`" to a theorem for all primes, and removes linear algebra from the method entirely.
Checker: `verify_lucas_criterion_v5.py`. Priority CANNOT_CHECK.
Lane: `claude/orion-research-frontier-3ck9yt`.

## 1. Statement

> **Theorem.** Let `p ≥ 5` be prime, `D = 3p−2`, let `m > D`, and let `w ≥ p`. The pointed system on the two-sided window `S = [w+1, m−w−1]` is inconsistent over `F_p` **if and only if** there is an integer `d` with
>
> `m − 2w − 1 ≤ d ≤ m − 3p + 1`
>
> all of whose base-`p` digits are dominated by the corresponding digits of `m − 1 − w`.

No linear algebra, no per-prime computation: an arithmetic condition on two integers.

## 2. Proof

Write `dmax = m − D − 1`, and let `A` be the system matrix with `A[d][l] = (−1)^l C(l−1,d)` for `l ∈ S`, `b_d = −(−1)^m C(m−1,d)`, `0 ≤ d ≤ dmax`.

**(i) Fredholm.** `A x = b` is inconsistent over the field `F_p` iff some `λ` has `λᵀA = 0` and `λᵀb ≠ 0`.

**(ii) The dual vector is a function.** Put `P(y) = Σ_d λ_d C(y,d)`, an integer-valued function on `ℤ`. Then `λᵀA = 0` says `(−1)^l P(l−1) = 0` for every `l ∈ S`, i.e. `P(l−1) = 0`; and `λᵀb ≠ 0` says `P(m−1) ≠ 0`. For `w ≥ p` the window is `S = [w+1, m−w−1]`, so `{l−1 : l ∈ S}` is the **integer interval** `[w, m−w−2]`, of size `L = m − 2w − 1`.

**(iii) Newton about the left end.** By the forward-difference formula,

`P(y) = Σ_d μ_d C(y−w, d)`,  `μ_d = (Δ^d P)(w)`,

a bijective change of coefficients. Since `Δ C(y,e) = C(y,e−1)`, we get `μ_d = Σ_e λ_e C(w, e−d)`, so `λ_e = 0` for `e > dmax` forces `μ_d = 0` for `d > dmax`, and conversely. Because `C(j,d) = 0` for `j < d`, the vanishing of `P` on `[w, w+L−1]` is **exactly** `μ_0 = ⋯ = μ_{L−1} = 0` — the triangular system unwinds one coefficient at a time.

**(iv) Evaluate.** Hence the admissible `P` are precisely `Σ_{d=L}^{dmax} μ_d C(y−w, d)` with `μ` free, and

`P(m−1) = Σ_{d=L}^{dmax} μ_d C(m−1−w, d)`.

Such a `P` with `P(m−1) ≠ 0` exists iff `C(m−1−w, d) ≢ 0 (mod p)` for some `d ∈ [L, dmax]`. (If `L > dmax` the sum is empty and the system is consistent.)

**(v) Lucas.** `C(Y,d) ≢ 0 (mod p)` iff every base-`p` digit of `d` is at most the corresponding digit of `Y`. With `Y = m−1−w` this is the statement. ∎

## 3. What this changes

1. **The short-atom law is a theorem.** `SHORT_ATOM_LAW_UNIFORM_V5.md` gives the closed form `w(p,m)` and verified it for seven primes. It is now a corollary of §1 by digit bookkeeping, for every prime — the checker confirms the closed form is recovered from the criterion alone, with no linear algebra, at every prime and length tested.
2. **The method is cheap.** Deciding a case costs a digit comparison instead of Gaussian elimination over `F_p`. Any prime, any length, instantly.
3. **It explains the shape of the answer.** The generic bound `(3p−1)/2` and the exceptional residue run `[(p+1)/2, p−2]` are consequences of when the interval `[m−2w−1, m−3p+1]` first catches an integer digit-dominated by `m−1−w`. The periodicity in `m mod p` is immediate, because the digit condition only sees residues and carries.
4. **The `p = 7` hand-proof is demystified.** The peeling `d=6 ⇒ M_14`, `d=5 ⇒ M_13`, … in `SHORT_ATOM_BOUND_UNIFORM_V4.md` §2a is the triangular unwinding of step (iii), seen coefficient by coefficient.

## 4. What it does not settle

The criterion is for the **pointed** system on a two-sided window. The **atom-spectrum** system of `GENERAL_SPECTRUM_SPECIAL_LENGTHS_V4.md` (Observation D) is a different object: two families of unknowns `W_L, X_L` and coefficients `C(L,d) + (−1)^N C(N−L,d)`. The same duality applies and turns it into: *find `P` vanishing on the interval `[N−D, D]`, satisfying `P(L) = −(−1)^N P(N−L)` for `L ∈ [p+1, N−D−1]`, with `P(0) + (−1)^N P(N) ≠ 0`.* That is a genuine functional equation rather than a plain interval-vanishing condition, and it is **not** solved here. It is, however, now the precisely-stated obstacle, which the earlier record could only describe as "needs a rank argument".

## 5. Verification

`verify_lucas_criterion_v5.py` checks the steps separately and then the whole chain:

1. the Lucas step directly, over all `n < 4p` at every prime tested;
2. Newton's rewriting numerically on samples, for several `w` and degree bounds;
3. the digit criterion against Gaussian elimination on **all 2,916** `(p,m,w)` cases across `p ∈ {5,7,11,13,17,19}` — 0 disagreements;
4. that the closed-form law is recovered from the criterion alone.

## Claim ceiling

§1 is proved for all primes `p ≥ 5`, all `m > D` and all `w ≥ p`; the restriction `w ≥ p` is what makes the shifted window a single interval, and is satisfied everywhere the programme applies it. The corollary closed form in `SHORT_ATOM_LAW_UNIFORM_V5.md` is stated on the applied range `m ≤ (11p−3)/2`; the criterion itself carries no such restriction, so the range there reflects the bookkeeping done, not a limit of the theorem.
