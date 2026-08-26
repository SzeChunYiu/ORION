# Typed Authority R9 Addendum: Minimum Safe License Bases

## 1. Operational compression is not full semantic compression

Corollary 11 of the main manuscript gives an exact polynomial quotient for licenses with identical seed-and-cap signatures. That quotient preserves the complete typed label map under every refutation set.

A different problem arises when a deployment exposes only a declared portfolio of operational authorizations. The designer may wish to retain the smallest subset of candidate license coordinates that still covers every required authorization while exposing none of a declared forbidden portfolio. This is **portfolio compression**, not equivalence-class compression of the full semantics.

The distinction matters. Exact full-map quotienting is syntactic and polynomial. Portfolio compression is combinatorial even though every individual license projection is evaluated in linear time.

## 2. Minimum Safe License Basis

Fix a finite positive typed authority program `G`, a direct-refutation set `R`, candidate licenses `Lambda_c`, required operational claims `T+`, forbidden operational claims `T-`, and an integer budget `k`.

For a license `lambda`, let

`A_lambda = Reach_{R,lambda}`

be its coordinatewise Horn closure. A subset `B subseteq Lambda_c` is a **safe license basis** when

1. every required claim is carried by at least one selected license:

   `T+ subseteq union_{lambda in B} A_lambda`;

2. no forbidden claim is carried by any selected license:

   `T- intersection union_{lambda in B} A_lambda = empty`.

The decision problem **MINIMUM SAFE LICENSE BASIS** asks whether such a basis exists with `|B| <= k`.

The operational view is existential over retained typed coordinates. It does not erase coordinates and then rerun Horn rules. Cross-coordinate premise splicing therefore remains forbidden.

## 3. Exact reduction to safe set cover

### Theorem 16 — projection reduction

For each candidate license, compute `A_lambda` by the coordinatewise worklist. Discard every license satisfying

`A_lambda intersection T- != empty`.

For every remaining license, define its required-claim coverage set

`C_lambda = A_lambda intersection T+`.

Then `B` is a safe license basis if and only if the family `{C_lambda : lambda in B}` covers `T+`.

**Proof.** A selected license reaching a forbidden claim violates safety independently of every other coordinate, so every unsafe license must be absent. Once unsafe coordinates are removed, strong license noninterference implies that selecting or omitting one coordinate cannot change another coordinate's closure. The positive requirement is therefore exactly that the selected required-claim coverage sets have union `T+`. ∎

This theorem is useful beyond hardness. It converts typed portfolio compression into an ordinary, auditable set-cover instance after one linear Horn evaluation per license. The reduction preserves the identity of every selected authority coordinate and every covered operational claim.

## 4. Complexity boundary

### Theorem 17 — NP-completeness under severe restrictions

MINIMUM SAFE LICENSE BASIS is NP-complete. Hardness holds even when:

- there are no direct refutations;
- there are no forbidden claims;
- the rule graph is acyclic;
- every rule is unary and has depth one; and
- every cap is a singleton license.

**Proof.** Membership in NP follows from a selected-license certificate. Run the linear Horn worklist for every selected coordinate and verify required coverage and forbidden exclusion.

For hardness, reduce SET COVER. Given universe `U`, family `S_1,...,S_n`, and budget `k`, create one license `lambda_i` and one seed claim `s_i` carrying only `lambda_i`. For every element `u in S_i`, add the unary rule

`s_i -> q_u`

with cap `{lambda_i}`. Let the required portfolio be `{q_u : u in U}` and let the forbidden portfolio be empty. License `lambda_i` reaches exactly the claims corresponding to `S_i`; hence a safe basis of size at most `k` exists exactly when the original family has a set cover of size at most `k`. The construction has the stated restrictions. ∎

The theorem does not claim generic novelty for SET COVER hardness. The contribution is the exact identification of a typed operational-policy problem with safe set cover after coordinatewise authority evaluation.

## 5. Algorithms and certificates

Let `m=|T+|` and let

`M=|Q|+sum_r(|B_r|+1)`

be the explicit Horn incidence size.

### Corollary 18 — exact fixed-portfolio algorithm

After computing all candidate projections in `O(|Lambda_c| M)` time, bitmask dynamic programming finds an optimal safe basis in

`O(|Lambda_c| 2^m)` time and `O(2^m)` memory.

Thus the problem is fixed-parameter tractable in the size of the required operational portfolio, even though it is NP-complete in general.

### Corollary 19 — greedy certificate

After unsafe coordinates are removed, the standard greedy rule that repeatedly selects the license covering the largest number of currently uncovered required claims returns an `H_m`-approximate basis, where `H_m` is the `m`th harmonic number. Each step can emit:

- the selected license identifier;
- newly covered required claims;
- its coordinatewise proof trees; and
- the invariant that no selected license reaches a forbidden claim.

The approximation guarantee is inherited from classical set cover; it is not a new approximation theorem.

### Corollary 20 — fail-closed infeasibility

If a required claim is uncovered by every license surviving the forbidden-claim filter, no safe basis exists. The uncovered claim and the per-license forbidden/reachability reasons form a short infeasibility certificate.

Weighted license-retention costs give weighted set cover after the same projection reduction.

## 6. Why forbidden filtering cannot be postponed

A four-license control illustrates the safety constraint. One license covers required targets 0 and 1 but also reaches a forbidden claim. Two separate safe licenses cover targets 0 and 1, and a fourth covers targets 2 and 3.

Ignoring the forbidden claim yields a two-license cover. The safe optimum is three. In a second control, the only license covering a required target is unsafe, so the correct result is infeasible rather than a smaller but unauthorized basis.

This is not an interaction effect between licenses. It is a coordinate-local exclusion made exact by noninterference.

## 7. Executable audit

The verifier constructs the depth-one typed program used in the reduction and independently compares:

1. reachability-derived license coverage;
2. direct SET COVER coverage;
3. exhaustive basis enumeration;
4. bitmask dynamic programming; and
5. the harmonic greedy bound.

The registered audit checks 10,087 set systems exhaustively:

- every family on universes of sizes one through three; and
- every family of at most six distinct nonempty subsets on a four-element universe.

It additionally checks 4,000 deterministic generated systems on universes of sizes five through nine. Across the registered panels there are zero reduction mismatches, zero dynamic-programming versus brute-force mismatches, and zero greedy-bound violations. The forbidden-claim controls reproduce the safe optimum increase from two to three and the fail-closed infeasible case.

These finite checks corroborate the implementation. The analytic reduction and proofs carry all-size authority.

## 8. Prior-art and authority boundary

SET COVER NP-completeness, harmonic greedy approximation, and logarithmic approximation limits are established results. They are included to calibrate the policy-compression boundary, not as new complexity theory.

The residual paper contribution is narrower:

- strong license noninterference makes each candidate authority coordinate independently evaluable;
- the operational portfolio problem therefore reduces exactly, not heuristically, to safe set cover;
- forbidden authority is filtered before optimization;
- selected licenses retain typed proof certificates; and
- the result separates easy full-semantic quotienting from hard query-portfolio compression.

No real-policy utility, deployed performance, or external complexity review is established by the local artifact. The OAuth corpus and independent domain-review gate remain separate.
