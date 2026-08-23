# ORION-RG X1-F4 — the extremal witnesses for `D_2(C_5^3) = 20`, classified

Issue `SzeChunYiu/ORION#915`, phase X1-F4. Prior art: Zhong 2025
(*Combinatorica*) solves the inverse problem for `k`-th Davenport constants at
**rank 2**; rank 3 is not covered.

## Result

```
Exactly 1405 GL(3,5)-classes,
comprising 2,015,744,000 length-19 sequences over C_5^3 with no two disjoint
nonempty zero-sum subsequences.
```

The 98,622 sequences enumerated for `#916` are exactly those normalized to
contain `e1,e2,e3` with `m(e1) <= m(e2) <= m(e3)`.

## X1-F4 as stated is refuted, and now quantitatively

`#915` proposes that every maximal length-19 failure is `GL`-equivalent to the
Freeze–Schmid obstruction type. There are **1405** classes, and only **714** of
them contain three independent elements of multiplicity 4 at all. So
"`e1^4 e2^4 e3^4` plus junk" is not merely non-unique — it is not even the
general *shape*. The maximising independent triple has multiplicity sum `>= 10`
in exactly four patterns: `(4,4,4)` 714 classes, `(3,4,4)` 596, `(3,3,4)` 84,
`(2,4,4)` 11.

## What is proved, versus what is census

**Proved.**

- **P1** every zero-sum has length `>= 7` — the complement of a zero-sum of
  length `L` must be zero-sum-free, so `19 - L <= D(C_5^3) - 1 = 12`.
- **P2** every zero-sum has length `<= 13 = D(C_5^3)` — a zero-sum of length
  `>= 14` contains a zero-sum inside any 13 of its elements, leaving a second
  disjoint one.
- **P3** the total sum is nonzero, immediate from P2 since `19 > 13`.
- **P4** maximum multiplicity `<= 4`.

**Verified by exhaustion over all 1405 classes — census facts, not proofs.**

- **T1** min zero-sum length is exactly **7** and max exactly **13** in *every*
  class: both bounds of P1/P2 are attained by every single witness.
- **T2** max multiplicity is exactly 4 in every class (P4 is always tight).
- **T3** the support injects into `PG(2,5)` — no two support elements are scalar
  multiples. This is **not forced locally**: `u^2 (2u)^1` has no short zero-sum,
  yet it never occurs. An unexplained regularity, and a good target for a proof.
- **T4** the projective support never contains a full line of `PG(2,5)`; it meets
  a line in at most 5 points.
- **T5** support size lies in `{5,...,10}`.

## Structure theorem

P1 together with T1 gives, for every witness `S`:

> `S = A * B` with `A` a **minimal zero-sum of length exactly 7** and `B` a
> **maximal zero-sum-free sequence of length 12 = D(C_5^3) - 1`.

So the classification of extremal `D_2` witnesses reduces to understanding how a
length-7 minimal zero-sum can be glued to a *maximal* zero-sum-free sequence —
which ties X1-F4 directly to the inverse problem for `D(C_5^3)` itself. Across
the 7,239 `(class, length-7 zero-sum)` pairs the complements realise **1,238**
distinct `GL`-classes, and `e1^4 e2^4 e3^4` is **not** the typical one.

Not computed: what fraction of all maximal zero-sum-free classes over `C_5^3`
those 1,238 represent. Recorded as open, not as "checked and fine".

## Why the class count is believable

The canonical form is `C(S) = ` lex-min over ordered independent triples `T` from
`supp(S)` of `A_T(S)`, with `A_T` the unique `g in GL(3,5)` sending `T` to
`(e1,e2,e3)`. Invariance and completeness are both proved in the receipt.

The decisive check is the **orbit–stabilizer identity**, which is independent of
the canonicalizer being right: for every one of the 1405 classes,
`N(C)/|Stab(C)|` equals its observed multiplicity in the enumeration, with
**0 mismatches** and a total of **exactly 98,622**. Separately,
`|Stab| * |orbit| = |GL(3,5)| = 1,488,000` holds for all 1405.

The failure mode a classification must rule out is *collapsing* — a
canonicalizer that maps everything together reports "1 class" and looks like a
beautiful theorem. Controls run: 103 sequences inside one multiplicity profile,
provably inequivalent by distinct zero-sum length distributions, received **103
distinct** canonical forms; 400/400 random-`GL` round trips agree, with all 400
images lacking `{e1,e2,e3}` so the canonicalizer was exercised
support-generically; idempotence 400/400; and all 1405 representatives pass the
independent C `k`-disjoint checker.

## Authority

`mathematical_proposal: true`, `mathematical_result_credit: false`,
`proof_authority: false` beyond the machine-checked census, `novelty_claim:
false`.
