# Mathematical Extensions R4 — Product Certificates, Realization Gates, and Search Budgets

Date: 2026-08-25

Canonical predecessor: `MANUSCRIPT_V3_PIPELINE.md`

Status: theorem addendum for integration into the next manuscript version. It preserves the V3 distinction between an abstract zero-sum deletion language and the separately defined dependent-triple Pauli compiler.

## 1. Purpose

Paper B is about ownership of a support number. A terminal budget can be exact for a proof language without being an intrinsic lower bound for a compiler. The V3 manuscript makes that distinction correctly but treats the product example in one homogeneous form. This addendum supplies a general heterogeneous product theorem, an exact realization criterion, and the corresponding direct-enumeration law.

The new statements are deliberately conditional where production realization is not established. They strengthen the paper by turning a cautionary comparison into a reusable theorem framework.

## 2. Abstract deletion systems

An abstract shortening system `P` consists of a set of finite states, a nonnegative integer size `|x|`, and legal moves that strictly decrease size. A state is terminal when it has no legal move. Define

`beta(P) = sup{|x| : x terminal}`,

assuming the supremum is finite and attained in the systems considered below.

For the zero-sum deletion language of the V3 manuscript, states are nonzero-total words, size is word length, and legal moves delete nonempty proper zero-sum subsequences. Its exact terminal complexity is `zsf(H;A)`.

## 3. Heterogeneous product exactness

Let `P_1,...,P_t` be shortening systems. Their independent product has tuple states `(x_1,...,x_t)`, total size `sum_i |x_i|`, and moves that act in exactly one component.

**Theorem B1 (abstract product terminal complexity).**

`beta(product_i P_i) = sum_i beta(P_i)`.

**Proof.** A product state is terminal exactly when every component is terminal. Hence every terminal tuple has size at most the sum of the component maxima. Conversely, choosing a maximum terminal state in every component gives a terminal tuple attaining that sum. ∎

For axis-separated zero-sum alphabets this is also a direct consequence of Paper A's direct-sum theorem, but Theorem B1 applies to any independent shortening systems.

## 4. Intrinsic support in independent compiler products

Let compiler family `F_i` have objective `C_i`, support functional `k_i(x_i)`, and intrinsic support `kappa_i`. Define the independent product by Cartesian-product feasibility, additive objective, and total support

`k(x_1,...,x_t)=sum_i k_i(x_i)`.

Assume there are no cross-component compiler moves or constraints.

**Theorem B2 (intrinsic product support).** If every component has an all-instance support-`kappa_i` normalization and an instance for which every optimum has support at least `kappa_i`, then

`kappa(product_i F_i) = sum_i kappa_i`.

**Proof.** Apply each component normalization independently to obtain the upper bound. For the lower bound, take the product of the component lower-witness instances. Additivity and independence imply that every product optimum restricts to an optimum in each component; therefore its total support is at least the sum of the component lower bounds. ∎

The lower-witness premise is essential. Componentwise upper bounds alone do not establish intrinsic equality.

## 5. The production-realization gate

Let a compiler family `F` have a representation map

`psi : production states -> abstract states of P`.

A proof system on production states is *faithfully represented by P* when:

1. every production move in the proof system maps to a legal move of `P`;
2. every legal `P` move used for an upper theorem has a sound admissible lift from the relevant production state; and
3. size in `P` equals the support quantity claimed for the proof system.

**Theorem B3 (exact production certificate criterion).** Suppose:

1. every production state has a represented `P`-normal form of size at most `beta(P)`;
2. a production state realizes a terminal abstract state `w` of size `beta(P)`;
3. every production move allowed by the named proof system maps to a legal `P` move; and
4. no additional rule in that proof system reduces the realizing production state.

Then the production certificate complexity of that proof system is exactly `beta(P)`.

**Proof.** The represented normal-form theorem gives the upper bound. The realizing state is terminal under every represented proof move and has size `beta(P)`, giving the matching lower bound. ∎

This theorem isolates the precise gap left open in the V3 dependent-triple comparison. The abstract standard-basis word in `F_2^5` proves exact terminal complexity five for the declared abstract language. It does not become a production certificate lower bound until a production state satisfying items 2–4 is exhibited.

### Failure modes caught by the criterion

- An abstract terminal word may have no feasible production preimage.
- A preimage may exist but an additional compiler rule may reduce it.
- An abstract deletion may not lift to a semantics-preserving production edit.
- The represented word length may not equal the compiler support functional.

Any one of these failures invalidates an intrinsic or production-certificate interpretation while leaving the abstract theorem correct.

## 6. Proof-language dominance

For two sound production proof systems `P` and `Q` on the same compiler family, write `P <= Q` when every legal `P` move is also a legal `Q` move.

**Proposition B4 (monotonicity under stronger proof systems).**

`beta_Q(F) <= beta_P(F)`.

**Proof.** Every state terminal under `Q` is terminal under `P`, because `Q` has at least the moves of `P`. Taking maximum terminal support gives the inequality. ∎

Strict inequality requires a witness: a state terminal at the larger `P` budget that `Q` can reduce. This formulation clarifies what a stronger global transformation must demonstrate. It is not enough to produce a smaller support on selected examples.

## 7. Direct-enumeration law

Let a direct support enumerator on `n` coordinates visit every labeled support of size at most fixed budget `B`, with a fixed finite number `q>=1` of local nonidentity labels per selected coordinate. Its search volume is

`V_B(n)=sum_{j=0}^B binom(n,j) q^j`.

**Theorem B5 (fixed-budget enumeration growth).** For fixed `B` and `q`,

`V_B(n)=Theta(n^B)`.

If two valid budgets satisfy `B>K`, then

`V_B(n)/V_K(n)=Theta(n^(B-K))`.

**Proof.** The leading term is `binom(n,B)q^B`, which is `Theta(n^B)`; all lower terms have smaller degree. Dividing the two polynomial asymptotics gives the ratio. ∎

For heterogeneous independent components with coordinate counts `n_i`, separate direct enumerators have ratio

`Theta(product_i n_i^(beta_i-kappa_i))`

when both the certificate and intrinsic product equalities have been established under Theorems B1 and B2. With a common coordinate scale `n`, this becomes

`Theta(n^(sum_i(beta_i-kappa_i)))`.

This remains a statement about a declared enumeration architecture. It is not an algorithm-independent time lower bound.

## 8. Conditional amplification theorem

Combining the preceding results gives a reusable statement.

**Theorem B6 (realized certificate-gap amplification).** For independent compiler components `F_i`, suppose:

1. a production proof language `P_i` satisfies the exact realization criterion with complexity `beta_i`;
2. intrinsic support is exactly `kappa_i`; and
3. `beta_i>=kappa_i`.

Then the product has exact certificate complexity `sum_i beta_i`, exact intrinsic support `sum_i kappa_i`, additive gap

`sum_i(beta_i-kappa_i)`,

and direct-enumeration ratio

`Theta(n^(sum_i(beta_i-kappa_i)))`

under the common-scale model.

The theorem is exact only after the realization conditions are verified componentwise. Without them, the same formulas compare an abstract budget with an intrinsic compiler budget and must be labeled as such, as in the V3 manuscript.

## 9. Applications

### 9.1 Proof-carrying exact optimization

A solver can publish both its search result and the proof language that justifies its support cap. The realization criterion prevents a certificate computed in an abstract quotient from being silently promoted to a compiler lower bound.

### 9.2 Certificate-aware branch and bound

If a stronger sound proof system lowers the verified budget from `B` to `K`, Theorem B5 quantifies the exponent removed from a direct support enumerator. This provides a mathematical objective for proof-system engineering: add transformations that eliminate terminal obstructions, not merely heuristics that work on an average panel.

### 9.3 Solver comparison

Two exact solvers can be compared by the largest support terminal under their declared rule sets. Proposition B4 gives a monotone ordering when one rule set contains another. A strict separation requires an explicit state and a verified reduction.

### 9.4 Verification architecture

The product theorems permit modular certification. Each component can carry its own terminal witness, normalization, and intrinsic obstruction, after which composition is theorem-driven rather than inferred from repeated homogeneous examples.

These are potential uses of the formalism. No deployed compiler benchmark or proof-carrying solver is claimed in this addendum.

## 10. Integration into the manuscript

1. Insert Theorem B3 immediately after the abstract certificate theorem; it should govern every later production interpretation.
2. Replace the homogeneous product section by Theorems B1, B2, and B6, then specialize to the declared five-versus-one comparison only at the level actually established.
3. Add Proposition B4 to formalize proof-language strength.
4. Use Theorem B5 to derive enumeration consequences instead of relying on informal leading-exponent language.
5. Keep the V3 statement that the production factor-five lower bound remains open unless a realizing production state is proved.

## 11. Atomic claim status

- Abstract product exactness: `VERIFIED`.
- Intrinsic product equality: `VERIFIED` under explicit component lower-witness and independence premises.
- Exact production realization criterion: `VERIFIED`.
- Proof-language monotonicity: `VERIFIED`.
- Direct-enumeration asymptotics: `VERIFIED` for fixed budgets and local alphabet.
- Product amplification: `VERIFIED` under the listed realization premises.
- Factor-five production certificate for the current dependent-triple compiler: `UNRESOLVED` and not asserted.
- Algorithm-independent complexity lower bound: `NOT_CLAIMED`.

## 12. Editorial effect

The addendum makes Paper B a theorem about when certificate numbers transfer across abstraction boundaries. Its strongest standalone contribution is the realization gate, because it turns a recurrent reporting error into a checkable mathematical condition. The remaining high-selectivity blocker is a concrete production realization or a broader family with several independently verified tight and loose controls. Without that evidence, the manuscript should retain its calibrated abstract-versus-production framing rather than claim an intrinsic factor-five separation.