# Hostile independent audit of the `a=1`, two-share support-three elimination — V1

Status: **independent verification of the theorem in `A1_LIGHT_SUPPORT3_TWO_SHARE_ELIMINATION_V1.md`; no additional theorem or novelty authority**.

Audited base commit:

`8afb8405ba3e4d5f16c7477d499d0a79003d9925`.

## 1. Audit target

The audited theorem eliminates, for every prime `p>=7`, an exact-support-six first-corridor companion

`V=s^2 x^r y^t`

when the support-four maximal atom has type `a=1`.

The primary proof is symbolic except for the isolated arithmetic row

`(p,c,r,t)=(13,2,6,11)`,

which it discharges by a radial-depth enumeration.

The hostile audit changes both load-bearing computational mechanisms rather than translating the primary checker line by line.

## 2. Independent multiplicity audit

The independent verifier does not use the primary `p mod 4` case formulas. For every prime through `1009`, it:

1. enumerates every ordered multiplicity row `2+r+t=(3p-1)/2` with `r<=t<=p-1`;
2. tests three-support atomicity by searching every nontrivial scalar multiple of the coefficient relation;
3. searches every scalar multiplier again for a lifted short zero-sum, using the saturated-atom cost

`lambda_2(C)=C` for `C<=3`, and `lambda_2(C)=3C-6` for `C>=4`.

Exactly one atom-compatible row survives this independent scalar search:

`boxed{(13,2,6,11).}`

This reproduces the arithmetic resonance without using the symbolic branch split.

## 3. Independent `p=13` depth engine

For the resonance, write the saturated maximal atom as

`U=f1^12 f2^12 f3^12 s`, `s=(1,1,1)`.

The verifier constructs the complete depth table `rho_U` by occurrence-level dynamic programming over the actual 37 terms of `U`. It does not call the closed formula

`rho(z)=S(z)-2` off the coordinate hyperplanes.

The relation is parameterized as

`y=s+3x`.

The companion plane avoids all three saturated axes exactly when the three coordinates of `x` are pairwise distinct. Thus the independent structural universe has

`13*12*11=1716`

ordered parameters.

For each parameter, a second occurrence-level dynamic program processes the 19 actual terms of

`V=s^2 x^6 y^11`

and records, for every group element, every attainable subsequence cardinality. The verifier then checks the exact graded inequality

`|W|+rho_U(-sigma(W))>=19`

for every nonempty proper `W|V`.

Frozen result:

- structural parameters: **1716**;
- parameters passing both singleton inequalities: **312**;
- parameters passing the full exact graded inequality: **0**.

Hence the independently generated maximal-atom depth table and the independently generated companion cardinality table reproduce the empty `p=13` base.

## 4. Score distribution and mutation control

For each structural parameter define

`mu(x)=min_{nonempty proper W|V} (|W|+rho_U(-sigma(W)))`.

The complete independent distribution is

| `mu` | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| count | 12 | 42 | 108 | 210 | 318 | 390 | 330 | 132 | 36 | 42 | 78 | 18 |

No parameter has `mu>=19`, as required by the theorem.

As a hostile mutation, lower the artificial acceptance threshold from `19` to `15`. Exactly **18** parameters then survive. This positive control prevents an implementation that always reports incompatibility from passing the audit.

## 5. Sanitizer replay

The live Davenport workflow compiles and runs the independent verifier in two modes:

- optimized C++17;
- C++17 with AddressSanitizer and UndefinedBehaviorSanitizer.

Both modes must reproduce the same resonance, counts, score histogram, zero theorem survivors, and 18-state mutation control.

## 6. Audit conclusion

The hostile replay supports the repository theorem:

> for every prime `p>=7`, the `a=1` exact-support-six support-three face has no companion with shared multiplicity two.

The audit grants no novelty credit and does not advance the frontier beyond the later `c>=4` reduction. Its role is to make the finite `p=13` authority and the arithmetic-resonance isolation independently reproducible on the consolidated live branch.
