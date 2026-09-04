# Hostile independent audit of the `a=1`, four-share support-three elimination — V1

Status: **independent verification of `A1_LIGHT_SUPPORT3_FOUR_SHARE_ELIMINATION_V1.md`; no additional theorem or novelty authority**.

Audited parent commit:

`b726ec44473b3de6dabba35972354389d7ee1aeb`.

## Arithmetic audit

The primary proof uses explicit multiplier families depending on `p mod 3` and `p mod 5`. The independent C++ verifier ignores those formulas. For every prime through `5000`, it enumerates every multiplicity row

`4+r+t=(3p-1)/2`, `r<=t<=p-1`,

and every nonzero scalar multiplier of the coefficient relation.

Frozen totals:

- multiplicity rows: **388365**;
- rows passing the independent three-support atomicity test: **184929**;
- rows with no lifted relation-multiple certificate: exactly

`(7,1,5),(13,3,12),(17,8,13)`.

The audit therefore reproduces the three arithmetic resonances without using the symbolic case split.

## Exact-base audit

For each resonance, the verifier builds `rho_U` by a 0/1 occurrence dynamic program over

`U=f1^(p-1)f2^(p-1)f3^(p-1)s`.

For every nonzero `y`, it solves

`x=-r^(-1)(4s+t y)`

and checks every proper count-vector subsequence of

`V=s^4 x^r y^t`.

The audited universe is intentionally larger than the theorem's structural universe: no plane-intersection, support-distinctness, or projective filters are used.

Define

`mu=min_{nonempty proper W|V} (|W|+rho_U(-sigma(W)))`.

The exact histograms are:

- `p=7`: `2:8,3:26,4:52,5:75,6:93,7:81,8:6`;
- `p=13`: `2:8,3:32,4:71,5:148,6:192,7:328,8:375,9:483,10:366,11:120,12:72`;
- `p=17`: `2:8,3:33,4:67,5:152,6:222,7:379,8:423,9:630,10:663,11:750,12:561,13:486,14:174,15:132,16:30,17:69,18:114,19:12,20:6`.

The theorem thresholds are `10`, `19`, and `25`, so all three bases are empty.

## Mutation controls

Lowering the artificial acceptance threshold to the largest observed score admits:

- 6 parameters at `p=7`;
- 72 parameters at `p=13`;
- 6 parameters at `p=17`.

The multiplier stage also has a load-bearing negative control: it must leave exactly three residual rows, not zero. These controls prevent always-negative implementations from validating the theorem.

## Audit conclusion

The independent scalar sweep, occurrence-level depth construction, full graded subsequence test, score histograms, and sanitizer replay support the repository theorem that the `a=1` exact-support-six support-three face has no companion with shared multiplicity four.
