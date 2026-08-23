# ORION-RG X1-S — `C_2^5` is a *single* orbit: the three-orbit structure is an `r = 4` phenomenon

## The question

X1-R found the `C_2^4` extremal `D_2` witness set decomposes into **three** `GL(4,2)`-orbits
(2520 + 840 + 120). The obvious follow-up is whether that is the start of a pattern or an
accident of `r = 4`. `C_2^5` settles it, and the answer is *accident*.

## Result

| group | `D_2` | witness length | witnesses | min-ZS histogram | `GL(r,2)`-orbits |
|---|---|---|---|---|---|
| `C_2^4` | 8 | 7 | 3,480 | `{3: 3360, 4: 120}` | **3** — 2520 + 840 + 120 |
| `C_2^5` | 10 | 9 | 138,880 | `{4: 138880}` | **1** — 138,880 |

For `C_2^5`, every sampled witness has stabiliser order **72**, so its orbit has size
`|GL(5,2)| / 72 = 9,999,360 / 72 = 138,880` — the entire witness set. One witness suffices
for the conclusion: if a single orbit already has the size of the whole set, there are no
others. **The `C_2^5` witness set is `GL(5,2)`-homogeneous.**

## Why the two groups differ — and how far that explanation reaches

The stratification is explained; the orbit count is not.

`C_2^5` has `m = 4`, so Lemma A forces minimum zero-sum `>= 4`, and the X1-K criterion
(`f_4 = 6 <= D_2 - 2 = 8`) forces it to be **exactly** 4. Hence a single min-zero-sum
stratum — which is what the histogram shows. At `C_2^4` the criterion **fails** (X1-M: it is
the unique group where it does), producing two strata, 3 and 4.

So: *the criterion holding implies a single stratum* — that much is proved. But **a single
stratum does not imply a single orbit**, and the `C_2^4` data shows the gap directly: its
min-zero-sum-3 stratum of 3,360 is not one orbit, it splits `2520 + 840`. The minimum
zero-sum statistic is therefore strictly coarser than the orbit decomposition at `r = 4`,
and the two happen to coincide at `r = 5` only because both are trivial there.

This is a coherent picture across X1-M/R/S: `C_2^4` is the unique group where the
decomposition fails **and** the only one found with a heterogeneous witness set. On two data
points that is an alignment, not a law, and it is recorded as such.

## `C_2^6`: not reached

`D_2(C_2^6) = 11` is known, so the same question is posable at witness length 10 over 63
non-zero elements. The enumerator (which does `C_2^4` instantly and `C_2^5` in 2.3 s) did not
complete in 600 s and produced no output. Recorded as **`CANNOT_CHECK_RESOURCE_BOUND`** for
this method, not as a negative result.

*Method note:* the run was wrapped as `timeout … | tail || echo TIMEOUT`, in which the `||`
is dead code — piping makes `$?` the exit status of `tail`, so the guard can never fire. The
absence of output is what indicates non-completion here, not the absent warning. Recorded
because this is the same class of error as reading swallowed output as emptiness.

## Validation

- The enumerator was validated on `C_2^4` **before** use on `C_2^5`, reproducing 3,480 with
  histogram `{3: 3360, 4: 120}` exactly — matching both X1-K and the independent enumeration
  run by the prior-art gate.
- `C_2^5` returned 138,880 witnesses, matching the count in the X1-K table, which was
  produced by a different program.
- Orbit–stabiliser holds exactly: `138,880 × 72 = 9,999,360 = |GL(5,2)| = 31·30·28·24·16`.

## Prior-art status

Unchanged from X1-R and not re-gated: the gate reported **not found**, with scope stated, for
any classification of the `C_2^r` extremal `D_2` witness sets, having read Freeze–Schmid
Section 7 in full and confirmed its `r = 4` content is pure *value*. Its stated coverage gaps
(no MathSciNet/zbMATH; Davydov–Tombak not read directly) carry over. No novelty is claimed
beyond that scope.

## Open

1. `C_2^6` — needs a better method than direct enumeration.
2. The geometric identity of the `C_2^4` 2520 and 840 orbits (carried from X1-R, untouched).
3. Whether `GL`-homogeneity holds for all `r >= 5`, or fails again somewhere. Two points do
   not distinguish "`r = 4` is exceptional" from "small `r` is exceptional".
