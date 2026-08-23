# ORION-RG X1-K — when the extremal `D_2` decomposition holds, and when it does not

X1-F4 proved, for `C_5^3`, that every extremal `D_2` witness splits as

> `S = A · B` with `A` a **minimal zero-sum of length exactly 7** and `B` a
> **maximal zero-sum-free sequence** of length 12.

Read naively that invites a general structure theorem. **It is not general.** This
atom gives the criterion that governs it and an explicit counterexample family.

## Setting

`G` finite abelian, `D = D(G)`, `D_2 = D_2(G)`, and

```
m := D_2(G) - D(G)
```

An **extremal `D_2` witness** is a sequence of length `D_2 - 1` with no two
disjoint nonempty zero-sum subsequences.

Lemma A (X1-F0) already gives `min zero-sum >= m` for every such witness. The
whole question is whether `<= m` also holds.

## Criterion

> If `f_m(G) <= D_2(G) - 2` then every extremal `D_2` witness has minimum
> zero-sum length **exactly** `m`, and therefore splits as
> `A · B` with `A` a minimal zero-sum of length `m` and `B` a **maximal**
> zero-sum-free sequence of length `d(G) = D - 1`.

*Proof.* A witness has length `D_2 - 1 > f_m(G)`, so it carries a zero-sum of
length `<= m`; Lemma A gives `>= m`. Removing a minimal such `A` leaves
`D_2 - 1 - m = D - 1` elements which must be zero-sum-free, hence maximal. ∎

The criterion is **sufficient, not necessary a priori** — but it turns out to
predict the truth exactly on every group tested, including the failure.

## The table — complete, and the criterion is right every time

| group | `D` | `D_2` | `m` | `f_m` | `D_2-2` | criterion | direct test on the witnesses |
|-------|-----|-------|-----|-------|---------|-----------|------------------------------|
| `C_2^2` | 3 | 5 | 2 | 3 | 3 | ✓ tight | **holds** — 9 witnesses, all min ZS 2 |
| `C_2^3` | 4 | 7 | 3 | 4 | 5 | ✓ slack 1 | **holds** — 7, all 3 |
| `C_2^4` | 5 | 8 | 3 | **8** | 6 | **✗ by 2** | **FAILS** — 3,480, histogram `{3: 3360, 4: 120}` |
| `C_2^5` | 6 | 10 | 4 | 6 | 8 | ✓ slack 2 | **holds** — 138,880, all 4 |
| `C_3^2` | 5 | 8 | 3 | 6 | 6 | ✓ tight | **holds** — 408, all 3 |
| `C_3^3` | 7 | 11 | 4 | 9 | 9 | ✓ tight | **holds** — 400,608, all 4 |
| `C_5^2` | 9 | 14 | 5 | 12 | 12 | ✓ tight | **holds** — 96,720, all 5 |
| `C_5^3` | 13 | 20 | 7 | 18 | 18 | ✓ tight | **holds** — all 1,405 classes (X1-F4 T1) |

**The criterion predicts the direct test in 8 of 8 groups, including the one
negative.** Every row is a complete enumeration, not a sample.

Two patterns worth someone's attention:

- `f_m = D_2 - 2` **exactly** — the criterion is *tight* — for `C_2^2`, `C_3^2`,
  `C_5^2`, `C_3^3`, `C_5^3`: every rank-`<=2` group tested, and both odd-`p`
  rank-3 groups.
- The elementary 2-groups of rank `>= 3` behave irregularly: slack 1 at
  `C_2^3`, **fails by 2** at `C_2^4`, slack 2 at `C_2^5`. Non-monotone in rank,
  and `C_2^4` is the sole failure in the table.

### Instrument validation, done before the new rows were trusted

`research/orion-rg/x1k_extremal_d2_witness_enumerator.c` was written after the
Python enumeration, and was checked against every case Python had already
settled **before** being used on `C_2^5`, `C_3^3` and `C_5^2`:

| case | Python | C enumerator |
|---|---|---|
| `C_2^2` | 9, all min ZS 2 | 9, `{2: 9}` |
| `C_2^3` | 7, all min ZS 3 | 7, `{3: 7}` |
| `C_3^2` | 408, all min ZS 3 | 408, `{3: 408}` |
| `C_2^4` | 3,480, `{3: 3360, 4: 120}` | 3,480, `{3: 3360, 4: 120}` |

4 of 4, including the counterexample histogram.

## The counterexample, explicitly

`C_2^4`: `D = 5`, `D_2 = 8`, `m = 3`, witnesses of length 7. Here
`f_3(C_2^4) = 8 > 6 = D_2 - 2`, so the criterion's hypothesis fails — and so does
its conclusion.

Exhaustive over all 116,280 multisets of length 7:

- **3,480** extremal `D_2` witnesses;
- minimum-zero-sum histogram **`{3: 3360, 4: 120}`**;
- so **120 witnesses have minimum zero-sum 4 > m = 3** and admit **no**
  decomposition into a length-`m` minimal zero-sum plus a maximal zero-sum-free
  sequence.

Sharply: there are exactly **120** length-7 multisets over `C_2^4` with minimum
zero-sum `> 3`, and **all 120 are extremal `D_2` witnesses**. The failure of the
criterion is realised in full, not partially.

## Prior art, checked before writing this up

The inverse problem for `D_k` is an established, active area, and **rank two is
solved**: Zhong, *On the inverse problem of k-th Davenport constants for groups of
rank 2*, Combinatorica (2025) (arXiv:2503.21231). Related: Schmid, *Inverse
zero-sum problems II*; Schmid, *The inverse problem associated to the Davenport
constant for `C_2 + C_2 + C_2n`*, Electron. J. Comb. 18(1) (2011).

Note also that the standard framing of that literature is slightly different from
this one: it studies **zero-sum** sequences of length `D_k(G)` that cannot be
partitioned into `k+1` nontrivial zero-sum subsequences, whereas the object here
is an **arbitrary** sequence of length `D_2 - 1` with no two disjoint zero-sums.
The two are related through the Freeze–Schmid characterisation but are not the
same object, and this document does not claim they are.

**No novelty is claimed.** The rank-2 rows above are within Zhong's scope. The
contribution here is bounded: a computable criterion, a table where it predicts
correctly including a negative, and an explicit counterexample family that shows
the X1-F4 decomposition does **not** generalise.

## Standing correction to X1-F4

X1-F4's structure theorem is an instance, not a general law. Anyone extending it
should check `f_m(G) <= D_2(G) - 2` first.

## Authority

`mathematical_proposal: true`, `novelty_claim: false`, `proof_authority: false`
beyond the stated criterion proof and the exhaustive enumerations.
