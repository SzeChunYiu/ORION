# Mathematical Extensions R5 — Exact Certificate Waste and the Necessity of Product Independence

Date: 2026-08-25

Canonical predecessors: `MANUSCRIPT_V3_PIPELINE.md` and `MATHEMATICAL_EXTENSIONS_R4.md`

Status: rigorous theorem addendum. It keeps the distinction between abstract terminal complexity, production certificate complexity, normalization ceilings, and intrinsic compiler support.

## 1. Purpose

R4 established heterogeneous product equalities, the production-realization gate, proof-language monotonicity, and polynomial search exponents. This pass makes the product budget explicit for heterogeneous cyclic signature factors, identifies the exact leading constant of the direct-enumeration penalty, and proves by counterexample that the no-cross-component-move premise is mathematically necessary.

## 2. Exact cyclic-axis certificate budgets

For component `i`, let its abstract deletion language use the standard-generator alphabet of

`H_i=direct_sum_{j=1}^{r_i} C_{n_{ij}}`.

By Paper A Theorem A8, its exact abstract terminal complexity is

`beta_i=sum_j (n_{ij}-1)`.

**Theorem B7 (heterogeneous cyclic-axis product).** Under the independent-product move semantics of R4 Theorem B1,

`beta_total=sum_i sum_j (n_{ij}-1)`.

**Proof.** Apply Theorem A8 in each component and then R4 Theorem B1. ∎

The formula is exact for the named abstract product language. It transfers to a production certificate only after every component passes the R4 production-realization gate.

## 3. Certificate-waste vector

Suppose component `i` has exact production-certificate budget `beta_i` and exact intrinsic support `kappa_i`. Define

`w_i=beta_i-kappa_i>=0`

and call `w=(w_1,...,w_t)` the *certificate-waste vector*. Its sum is not merely a difference of reported support numbers: under a direct support enumerator it is the exponent lost by using the proof-language ceiling instead of the intrinsic ceiling.

For `q_i>=1` local labels, define

`V_B(n;q)=sum_{j=0}^B binom(n,j)q^j`.

**Theorem B8 (sharp fixed-budget asymptotic).** For fixed `B` and `q`,

`V_B(n;q)=(q^B/B!)n^B+O(n^(B-1))`.

Consequently, for independent component enumerators with `beta_i>=kappa_i`,

`product_i V_{beta_i}(n_i;q_i) / product_i V_{kappa_i}(n_i;q_i)`

`= [product_i q_i^(w_i) kappa_i!/beta_i!] product_i n_i^(w_i) (1+o(1))`.

Under a common scale `n_i=n`, the exact polynomial exponent is `sum_i w_i`.

**Proof.** The degree-`B` term of `V_B` is `q^B binom(n,B)=(q^B/B!)n^B+O(n^(B-1))`; all other terms have degree at most `B-1`. Divide the component asymptotics and multiply. ∎

This theorem sharpens the R4 `Theta` statement. It remains architecture-specific: an algorithm that does not enumerate every labeled support is outside the model.

## 4. Independence is necessary

R4 product exactness assumes every move acts in one component. The next proposition shows that this is not a technical convenience.

**Proposition B9 (cross-component collapse).** There are shortening systems `P_1,P_2` with

`beta(P_1)=beta(P_2)=1`

such that their independent product has terminal complexity two, while an extended product with one legal cross-component move has terminal complexity one.

**Proof.** Let each component have an empty state of size zero and a terminal state `x_i` of size one, with no component move reducing `x_i`. The independent product has terminal state `(x_1,x_2)` of size two, so its terminal complexity is two.

Now add the cross-component move

`(x_1,x_2)->(empty,empty)`.

The size-two tuple is no longer terminal. The tuples `(x_1,empty)` and `(empty,x_2)` remain terminal and have size one. Hence the extended product terminal complexity is one. ∎

Therefore a componentwise terminal witness does not amplify automatically in a production system with global reconstruction, shared auxiliaries, or cross-component cancellations. Those operations must be frozen or analyzed explicitly.

## 5. Realization theorem with a cross-move audit

**Corollary B10 (safe product realization).** The R4 realized-certificate amplification theorem is valid when, in addition to the component realization conditions, every allowed production proof move either acts within one component or is proved unable to reduce the product of the component terminal witnesses.

The second alternative is important in compiler models with shared Tags or global frame changes. Merely saying that benchmark instances were assembled on disjoint qubits does not exclude a global proof move.

## 6. Application to the current five-versus-one example

For the declared abstract standard-basis language in `F_2^5`, `beta=5`. For the separately defined dependent-triple compiler, intrinsic support is one. The direct-enumeration comparison has exponent four per independent component only if the production proof language has exact certificate complexity five and cross-component production moves do not collapse terminal witnesses.

Those premises remain unproved for the current production interpretation. The mathematically correct claim is therefore:

- exact abstract terminal budget: five;
- exact intrinsic compiler support: one;
- numerical difference between separately defined budgets: four;
- production certificate gap and its amplified enumeration exponent: unresolved.

## 7. Verification

The R5 verifier checks a heterogeneous three-component budget, the certificate-waste vector, and convergence of the normalized search-volume ratio to the leading-constant law of Theorem B8.

## 8. Atomic status

- Heterogeneous cyclic-axis budget: `VERIFIED`.
- Sharp enumeration constant: `VERIFIED`.
- Cross-component collapse counterexample: `VERIFIED` constructively.
- Safe product-realization corollary: `VERIFIED`.
- Factor-five production certificate: `UNRESOLVED`.
- Architecture-independent runtime lower bound: `NOT_CLAIMED`.

## 9. Remaining scientific frontier

Paper B has reached a clean theoretical boundary. The next meaningful advance is empirical-mathematical rather than another abstraction: realize a longest abstract terminal word in a production state, enumerate every named production rule on that state, and independently verify irreducibility. A failed realization would also be informative because it would identify which abstraction step creates the certificate waste. Until that experiment exists, further amplification claims should remain conditional.
