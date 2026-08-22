# X1-B theorem — complete closure of the C15 k=3 / 10-point residual

Parent: #900.
Status: **CANDIDATE FINITE-COMPUTATIONAL THEOREM CHAIN — committed before use in the full C15 proof assembly.**

## 1. Residual setup

Assume for contradiction that a zero-sum-free sequence S of length 43 exists in

`C_15^3 ≅ C_3^3 direct-sum C_5^3`.

In the k=3 branch of the committed greedy quotient reduction, eleven disjoint quotient-zero-sum triples have already been removed from the `C_3^3` projection, leaving a 10-position residual A with no quotient zero sum of length at most 3.

The generic quotient block-count guarantee supplies at least one nonempty quotient-zero-sum subset of A. If A contained two disjoint quotient zero sums, the eleven removed triples plus those two blocks would yield 13 quotient blocks, whose kernel block sums force a zero sum by `D(C_5^3)=13`. Therefore a surviving k=3 residual has **no two disjoint nonempty quotient zero sums**.

## 2. Local scalarization applies to every residual zero sum

Fix the eleven removed triple blocks. Choose any one residual quotient-zero-sum subset B. The eleven fixed triples plus B form twelve disjoint quotient-zero-sum blocks.

In a hypothetical globally zero-sum-free S, the twelve lifted block sums form a maximal zero-sum-free sequence in `C_5^3`, of length `d(C_5^3)=12`.

The committed p-group local-scalarization lemma applies after fixing those same eleven blocks: there is a nonzero linear functional

`lambda:C_5^3 -> F_5`

such that the lifted sum of **every legal twelfth replacement block** has one common nonzero scalar image.

Because the other eleven blocks are the removed triples, every nonempty quotient-zero-sum subset of the 10-position residual A is a legal twelfth replacement block.

After rescaling lambda, every residual quotient-zero-sum subset C therefore satisfies

`sum_{j in C} f_j = 1`

over `F_5`, where `f_j=lambda(y_j)` and `y_j` is the kernel coordinate of residual position j.

Thus every genuine k=3 C15 counterexample induces a common-RHS scalar assignment on its 10-position quotient residual.

## 3. Independent raw finite elimination

The committed independent verifier does **not** quotient by `GL(3,3)`. It enumerates every raw 10-position multiset satisfying the short-zero-sum conditions.

Completeness gates:

- zero is excluded from the support;
- multiplicity is at most 2, since three equal nonzero `F_3^3` elements sum to zero;
- no opposite support pair;
- no three distinct support elements summing to zero;
- a separate exhaustive support audit proves no admissible support of size 9 exists;
- hence support sizes 5 through 8 cover every 10-position multiset under the frozen short-zero-sum gate.

For every generated candidate the verifier independently enumerates all nonempty position subsets, rejects candidates having two disjoint quotient zero sums, then row-reduces the common-RHS system over `F_5`.

Exact result:

```text
raw_candidates 1190124
no_disjoint 400608
inconsistent 400608
consistent 0
max_masks 43
```

Therefore:

> **No raw 10-position residual satisfying the k=3 quotient gates admits the scalar assignment forced by local scalarization.**

This conclusion has no symmetry-quotient dependency.

## 4. Agreement with the separately developed orbit verifier

A separately committed algorithmically independent Python verifier uses full multiplicity-vector augmentation and the complete `GL(3,3)` action. It reduces the same residual family to 43 canonical no-disjoint orbits and finds zero common-RHS-consistent orbit.

The raw replay above strengthens that result by checking all 400,608 admitted raw candidates directly.

The canonical research-harness campaign for this finite verifier remains non-authorizing by design and supplies provenance/governance rather than mathematical promotion authority.

## 5. Closure conclusion

A genuine k=3 residual would necessarily produce a common-RHS scalar assignment by the p-group local-scalarization theorem. Exact exhaustive raw enumeration proves no quotient residual admitting such an assignment exists.

Hence:

> **The k=3 / 10-point residual of a hypothetical length-43 zero-sum-free sequence over `C_15^3` is impossible.**

The k=3 residual branch is closed, subject to the correctness of the admitted p-group local-scalarization bridge and the overall C15 proof audit.

## Authority boundary

This packet closes the finite k=3 interface for proof assembly. It does not by itself prove `D(C_15^3)=43`. The full theorem still requires:

- donor verification of the greedy quotient reduction and p-group inputs;
- the separately committed k=4 closure;
- a hostile end-to-end logical audit;
- current-literature novelty subtraction;
- independent mathematical review beyond the ORION harness.