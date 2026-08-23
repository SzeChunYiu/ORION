# ORION-RG X1-G — the inverse Davenport problem for `C_5^3`

Classify, up to `GL(3,5)`, the maximal zero-sum-free sequences over `C_5^3`
(length `d = 12`) and the minimal zero-sum sequences of maximal length
(`D = 13`). Follow-on from X1-F4, whose structure theorem reduced the extremal
`D_2` witnesses to exactly this object.

## Prior art — checked first, and rank 3 is open

- **Rank 2 is classical.** Property B (Gao–Geroldinger; proved for prime `n` by
  Reiher), with the Bhowmik–Schlage-Puchta / Gao–Geroldinger description of
  maximal zero-sum-free sequences over `C_n^2`.
- **Rank 3 is not known.** Complete inverse results exist only for special
  families — Schmid, *EJC* 18 (2011) #P33 for `C_2^2 + C_2n`;
  Bhowmik–Schlage-Puchta 2007 for `C_3 + C_3 + C_3d`. The literature explicitly
  motivates the rank-2 structure by the fact that the rank-3 Davenport constant
  is unresolved in general.

No source gave a structural classification for `C_p^3`.

## Result

```
maximal zero-sum-free sequences, length 12 :  26,369 GL(3,5)-classes
                                              39,147,296,000 sequences

minimal zero-sum sequences, length 13 = D  :   3,325 GL(3,5)-classes
                                               4,897,256,000 sequences
```

The second is the inverse Davenport problem proper for `C_5^3`.

## A correction to the anchor this atom was given

The task brief stated the rank-2 form as
`e^{p-1} * prod_{i=1}^{p-1}(a_i e + f)` (shape A). **That is incomplete.** The
full statement needs a second shape,
`e^{p-2} * prod_{i=1}^{p}(a_i e + f)` with `sum a_i = 1` (shape B). Over
`C_5^2` there are 18 classes, and 4 of them have max multiplicity 3 — so shape A,
which requires multiplicity 4, cannot hold for them. Brute force over all 480
ordered bases: 0 classes fit neither shape. The pipeline reproduces the *correct*
rank-2 theorem before being pointed at rank 3.

## Proved

- **P1** `sigma(S) != 0` for every zero-sum-free `S`, so `U = S*(-sigma(S))` has
  length 13 and is a **minimal** zero-sum sequence.
- **P2 — inductive reduction.** If `g in supp(S)` has multiplicity 4 then
  `S = g^4 * T`, and the image of `T` in `G/<g> = C_5^2` is a **maximal**
  zero-sum-free sequence of length 8, hence of shape A or B by the rank-2
  theorem.

  *Proof.* If a sub-multiset `T'` of `T` sums to 0 in `G/<g>` then
  `sigma(T') = j g` for some `j` in `0..4`. `j = 0` makes `T'` a zero-sum in `S`;
  `j > 0` makes `T' * g^{5-j}` a zero-sum in `S`, since `m(g) = 4 >= 5-j`. Both
  contradict zero-sum-freeness. ∎

  **Coverage: 17,153 of 26,369 classes (65.0%)**, 25.47 billion sequences. The
  argument **fails at multiplicity 3**, where `j = 1,2` are unblocked — that
  boundary is exactly where a rank-3 structure theorem would have to do new work.

## The conjecture this produced

**T1 — projective squarefreeness.** In every one of the 26,369 classes,
`supp(S)` injects into `PG(2,5)`: no two support elements are scalar multiples.

This is **not forced elementwise**. `u^2 (2u)^1` is itself zero-sum-free, and the
only local constraint is `m(u) <= 2`, `m(2u) <= 1`. Yet it never occurs. The same
regularity held across all **1,405** extremal `D_2` witness classes from X1-F4 —
two independent complete censuses, roughly **41 billion sequences**, no exception.

> **Conjecture.** Every maximal zero-sum-free sequence over `C_p^3` is
> projectively squarefree.

This is the one regularity found here that looks like a theorem waiting for a
proof, and it is stated as a conjecture rather than reported as a fact.

## Validation

- **The bit primitive is proved, not sampled.** The `u128` translation is
  OR-linear, so checking all 125 singleton masks under all 125 translations is a
  *complete* proof. 15,625/15,625.
- **Two independently structured enumerators** — position-recursive versus
  code-recursive, different pruning — both give 3,275,411 normalized sequences.
- **Slice completeness.** Independent Python brute force over the `|supp| <= 5`
  slice produced 7,302 sequences; the C enumerator produced an **identical set**.
- **Orbit–stabilizer.** `N(C)/|Stab(C)|` matches the observed multiplicity for
  every one of the 26,369 classes, 0 mismatches, with
  `|Stab| * |orbit| = |GL(3,5)|` throughout.
- **Anti-collapse.** Inside one multiplicity profile, 129 sequences with distinct
  subsequence-sum signatures received **129 distinct** canonical forms.
- **Rank-2 anchor.** All 8,400 zero-sum-free length-8 sequences over `C_5^2`
  enumerated with **no** normalization give 18 classes summing to 8,400, all
  fitting shape A or B.
- **Cross-classification identity.** Every minimal zero-sum `U` of length 13
  equals `S*(-sigma(S))` for exactly the `|supp(U)|` choices `S = U` minus one
  element. Hence `#(zero-sum-free length 12) = sum_U |supp(U)|`:

  ```
  39,147,296,000  =  39,147,296,000       exact
  ```

  This links the two classifications and would fail loudly if either were wrong.

## The two headline numbers do not rest on equal evidence

- **26,369** is validated the strong way — the predicted count `N(C)/|Stab(C)|`
  matches the observed normalized enumeration exactly for every class.
- **3,325** is **not** validated that way. It rests on the surjection argument,
  the sum-over-support identity, and an anti-collapse control. Weaker evidence,
  recorded as such rather than presented alongside the first as equivalent.

## Authority

`mathematical_proposal: true`, `mathematical_result_credit: false`,
`proof_authority: false` beyond P1/P2 and the machine-checked census,
`novelty_claim: false`.
