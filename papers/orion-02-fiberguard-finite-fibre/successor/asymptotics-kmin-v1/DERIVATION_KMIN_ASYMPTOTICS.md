# DERIVATION — profile-Kmin asymptotics (asymptotics-kmin-v1)

Registered BEFORE the outcome run. All quantities refer to the frozen,
certified closed form in `../verify_c2c10_profile.py` (C2–C10), `L = 1`,
`N = 2^(m-2)`, `q = m-1`, `b(s) = ceil(lg s)` with `b(1) = 0`.

## 1. Exact decomposition (basis of the integer DP)

For a profile Π (multiset of block sizes, `k = |Π| ≥ 2`) with anchor class
`a` (the first block of size `a` in iteration order; costs are
permutation-symmetric, so "one designated block of size `a` + a multiset of
variable blocks covering `m - a`" covers every (profile, anchor-class) pair
exactly):

```
C(Π) = 2m + k - 3 + T_a(a) + df(a) + Σ_var (T_v(s) + df(s)) + max_b(Π)
T_a(s) = 2f + (b(s)+2)(w - s f),  w = N + (s-1)N/2,  f = N/2^(s-1)
T_v(s) = 2f + (b(s)+2)(w - s f),  w = sN/2,          f = N/2^s
```

with two exceptions mirrored from the frozen `block_term`: a variable block
of size `q = m-1` (only possible in the profile `(1, q)`) has `f = eps·L ∈
{0,1}`; a block of size `s ≤ m-2` has all-integer `w, f` (denominators
divide `2^(m-2)`). Hence with Python integers the DP computes Kmin exactly
where the frozen float harness loses precision (`G > 2^53`, roughly `m ≥ 51`)
and where its partition enumeration is infeasible (`p(m)` growth, `m ≥ 66`;
`m = 66` exceeded a 10-minute timeout on this machine).

`Kmin = max over eps ∈ {0,1}, anchor classes, k ≥ 2 of floor(G/(2k-1)) + 1`
for `G = C_one - C(Π) > 0`, `C_one = (b(m)+1)W + m - 1 + df(m) + b(m) -
(m(b(m)+1) - 1)·eps`, `W = N(m+1)/2`.

## 2. Rates and the family envelope

Per-unit variable-block rate (`s ≤ m-2`):

```
ρ(s) = T_v(s) / (sN) = 2^(1-s)/s + (b(s)+2)(1/2 - 2^-s)
     = (b(s)+2)/2 · (1 + O(2^-s))
```

`ρ(s)/s`-structure: within a dyadic band `s ∈ [2^j, 2^(j+1))` the leading
term is the constant `(j+2)/2`; at powers of two it jumps by `1/2`.

Uniform family `j` (all variable blocks of size `2^j`, `k ≈ m/2^j`):

```
γ_j = G/(N(2k-1)) ≈ [(B+1)/2 - (j+2)/2] · 2^(j-1) = (B - j - 1) · 2^(j-2),
B = b(m)
```

`f(j) = (B-1-j)·2^(j-2)`: `f(j)/f(j-1) = 2(B-j)/(B+1-j) ≥ 1 ⇔ j ≤ B-1`;
`f(B-2) = f(B-3) = 2^(B-4)`, `f(B-4) = (3/4)·2^(B-4)`. So the family
envelope is maximized at block sizes `2^(b(m)-3)` and `2^(b(m)-2)`, both
giving leading value `2^(B-4)` — matching the empirical argmax (16-blocks
dominate band `b = 6` (m = 33..64); the m = 65 winner mixes 32 and 25).

## 3. Registered law and discriminating prediction

**Conjecture (to be tested exactly, not fitted):**

```
γ*(m) = Kmin(m,1)/N = 2^(b(m)-4) · (1 + ε(m)),   ε(m) = O(b(m)/2^(b(m)))
```

equivalently `Kmin(m,1) = 2^(m + b(m) - 6)·(1 + ε(m))`.

Observed so far (all values certified exact by the frozen harness or the
validated DP): `ε ∈ [0.057, 0.23]` for `m ∈ {41..48, 63, 64, 65}` with the
low end at the band start `m = 65` (ε = 0.057).

**Discriminator at m = 129.** A linear-in-`b` reading of the same data
(`4·b(m) - 20`) agrees with `2^(b-4)` at `b = 6, 7` (4, 8) by coincidence and
predicts `γ*(129) ≈ 12`; the exponential law predicts `≈ 16`. The exact DP
table decides.

## 4. Rigorous two-sided pinch (proof sketch for the findings note)

- *Lower bound (construction):* the uniform family `j = b(m) - 3` plus a
  bounded anchor/filler correction gives `γ* ≥ 2^(B-4) - c·B` for an explicit
  absolute `c` (filler waste and anchor excess are `O(B)` per unit).
- *Upper bound (all profiles):* `b(s) + 2 ≥ lg s + 1` and Jensen on the
  convex `s lg s` give, for any `k` variable blocks covering `S = m - a`,
  `Σ s_i (b(s_i)+2) ≥ S(lg(S/k) + 1)`; combined with the divisor `2k-1` this
  caps `γ` by the family envelope `max_j (B-j-1)2^(j-2) + O(B) = 2^(B-4) +
  O(B)`. The DP table certifies that the `O(B)` fuzz stays in `[0.05, 0.23]·
  2^(B-4)` through `m = 140`.

Net: `Kmin(m,1) = Θ(2^(m + b(m)))` with leading constant `2^(b(m)-6)/(1)`
per band; the band boundaries `m = 2^B + 1` are where `γ*` (not `Kmin` itself)
jumps by factor ≈ 2.
