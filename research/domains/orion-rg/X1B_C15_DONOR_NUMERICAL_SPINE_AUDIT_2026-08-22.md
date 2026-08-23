# X1-B donor audit — numerical spine of the C15 candidate proof

Parent: #900.
Candidate theorem packet: `X1B_C15_DAVENPORT_43_CANDIDATE_THEOREM_2026-08-22.md`.
Status: **LOAD-BEARING DONOR AUDIT — committed before harness proof promotion.**

## Bhowmik--Schlage-Puchta quotient thresholds

Source: Gautami Bhowmik and Jan-Christoph Schlage-Puchta, *Davenport's Constant for Groups of the Form Z3 ⊕ Z3 ⊕ Z3d*, arXiv:math/0610416.

The paper defines two auxiliary quantities for a finite group G:

- `D_k(G)`: least n such that every n-term multiset contains k pairwise-disjoint nonempty zero-sum subsets;
- `D^k(G)`: least n such that every n-term multiset contains a zero-sum subset of size at most k.

(Prose/OCR renderings can visually collapse these superscript/subscript distinctions; the original PDF proposition was inspected directly.)

Proposition 1 gives for `C_3^3`:

- `D^3(C_3^3)=17`;
- `D_2(C_3^3)=11`;
- `D_k(C_3^3)=3k+6` for every `k>=3`.

Therefore in particular:

- `D_3(C_3^3)=15`.

These are exactly the greedy-residual thresholds used by the candidate C15 proof.

## Ordinary Davenport constants of the p-group factors

Geroldinger--Yang, arXiv:2608.19090, Section 2 records:

- `D(G)=d(G)+1`;
- the standard lower bound `d*(G)<=d(G)` / `D*(G)<=D(G)`;
- equality for finite abelian p-groups.

For `C_3^3`:

`d*(C_3^3)=3(3-1)=6`,

so

`d(C_3^3)=6`, `D(C_3^3)=7`.

For `C_5^3`:

`d*(C_5^3)=3(5-1)=12`,

so

`d(C_5^3)=12`, `D(C_5^3)=13`.

These are exactly the constants used to:

- produce a 13th quotient block from a residual of size at least 7;
- force a kernel zero sum from 13 quotient-block sums;
- place the 11 fixed kernel block sums at the `d(C_5^3)-1` threshold required by Geroldinger--Yang Theorem 3.5.

## Audit conclusion

The numerical donor spine used by the candidate theorem is source-consistent:

```text
D(C_3^3)     = 7
D_2(C_3^3)   = 11
D_3(C_3^3)   = 15
D^3(C_3^3)   = 17
D(C_5^3)     = 13
```

No interpolation or unverified extrapolation is used between these thresholds.

## Claim boundary

This audit verifies donor inputs only. It does not by itself establish `D(C_15^3)=43` or novelty.