# Universal Safety of Origin Erasure in Positive Authority Closures — R10

Date: 2026-08-26

Status: structural proposition for Paper D. Additive/union-preserving closure operators are established closure theory; no generic closure-theory novelty is claimed. The value here is the exact authorization interpretation, a rule-local test, and an explicit unsafe-origin witness when the test fails.

## 1. Setup

Fix one license coordinate and a finite positive Horn program `G` on claim set `Q`. Rules have nonempty bodies. Let

`C(S)=Cl_G(S)`

be the least Horn closure of seed set `S subseteq Q`.

There are no global empty-body facts in this formulation, so `C(empty)=empty`. A fixed global baseline can be handled by first closing it and quotienting/conditioning every origin closure relative to that baseline.

Suppose evidence records/origins independently provide seed sets

`S_1,...,S_r`.

Origin-preserving semantics yields

`union_i C(S_i)`.

Erasing origins before inference yields

`C(union_i S_i)`.

By monotonicity, the latter always contains the former. Universal erasure safety asks when equality holds for **every** finite family of origins.

## 2. Equivalent characterizations

### Theorem D-R10.2 — universal origin-erasure safety

The following are equivalent.

1. **Universal origin safety.** For every finite family `S_1,...,S_r`,

   `C(union_i S_i)=union_i C(S_i)`.

2. **Binary union preservation.** For all `S,T subseteq Q`,

   `C(S union T)=C(S) union C(T)`.

3. **Singleton generation.** For every `S subseteq Q`,

   `C(S)=union_{s in S} C({s})`.

4. **No genuinely conjunctive head.** For every rule `B -> h` in `G`,

   `h in union_{b in B} C({b})`.

Equivalently, for every admitted rule head, at least one body premise alone already entails that head under the full program.

### Proof

`(1)->(2)` is the two-origin special case.

`(2)->(3)` follows by finite induction over the elements of `S`, using `C(empty)=empty`.

`(3)->(4)`: seed the entire body `B`. The rule fires, so `h in C(B)`. By singleton generation,

`C(B)=union_{b in B} C({b})`,

hence some singleton body closure contains `h`.

`(4)->(3)`: prove by induction on a fair Horn derivation from `S` that every derived claim `x` belongs to `C({s})` for some original seed `s in S`.

The statement is immediate for seeds. Suppose `x=h` is newly derived by a rule `B->h`. By condition (4), choose `b_0 in B` with

`h in C({b_0})`.

By the derivation induction hypothesis, `b_0 in C({s})` for some original seed `s`. Therefore

`C({b_0}) subseteq C(C({s}))=C({s})`

by monotonicity and idempotence. Hence `h in C({s})`.

Thus every element of `C(S)` lies in the union of singleton closures. The reverse inclusion follows from monotonicity. This proves (3), which implies (1). ∎

## 3. Explicit counterexample from one violating rule

### Corollary D-R10.3 — local unsafe-merge witness

If a rule `B->h` violates condition (4), then assigning each premise `b in B` to a separate origin `S_b={b}` gives a concrete origin-erasure failure:

- no individual origin closure contains `h`;
- after pooling the origins, the body `B` is present and the rule derives `h`.

Therefore every violation of the local criterion is itself a replayable hybrid-proof certificate.

The witness need not be minimum-cardinality; the minimum witness problem is the NP-complete splicing-width problem in the companion R10 note.

## 4. Verification/search dichotomy

Paper D now has three levels of analysis.

### A. One proposed merge

Given fixed origin closures, the existing merge-safety theorem checks in linear Horn time whether their union is closed under the merged rule set.

### B. Universal erasure safety of the rule graph

Theorem D-R10.2 asks whether **every possible origin partition** is safe under coordinate erasure.

A direct algorithm:

1. compute `C({q})` for every claim `q`;
2. for each rule `B->h`, check whether `h` occurs in at least one singleton closure `C({b})`, `b in B`.

With a linear worklist closure routine of incidence size `M`, the naive bound is `O(|Q| M)` time plus rule-membership checks. Bitset/transitive optimizations may improve constants.

### C. Minimum concrete unsafe origin set

If universal safety fails, finding the smallest supplied-origin subset that creates a specified hybrid authorization can remain NP-complete by Theorem D-R10.1.

Thus:

- fixed-bundle verification is easy;
- universal policy preflight is polynomial;
- minimum attack/witness search is hard.

This three-way distinction is potentially useful for gateway and evidence-chain tooling.

## 5. Relation to unary implication systems

Condition (3) says the closure is additive/union-preserving: every multi-seed consequence is already owned by one seed's closure. In a finite Horn setting this means the **closure behavior** can be represented without genuine conjunction, even if the supplied syntax contains conjunctive rules.

This should be positioned against established work on closure operators and implicational bases. The manuscript should not claim the first characterization of additive closures or unary implicational systems.

The typed-authority contribution is the operational interpretation:

> origin erasure is universally safe exactly when the authority closure contains no genuinely cross-origin synergy.

A conjunctive rule is harmless when another path already makes its head singleton-generated; syntax alone is therefore insufficient. The test is semantic.

## 6. Authorized bridges and baselines

Real systems intentionally combine certain records. Let `B0` be an authorized baseline/bridge closure. Universal safety should then be tested **relative to** the intended bridge semantics rather than raw origin separation.

One implementation strategy is to treat `B0` as always present, compute a relative closure

`C_B(S)=Cl_G(B0 union S)`,

and compare the incremental consequences over `C_B(empty)`. The exact algebraic normalization should be frozen before the real-domain experiment because a nonempty global baseline changes the simple `C(empty)=empty` identity.

Legitimate same-request fragments, delegated identity chains, or standards-defined evidence-chain objects must be represented as authorized bridges, not mislabeled as splicing attacks.

## 7. Application as static preflight

For an evidence integration graph derived from an OAuth/MCP/A2A/Cedar/Rego/Souffle pipeline:

1. preserve standards-valid verification first;
2. identify the facts exported into the downstream integration layer;
3. bind each fact to an origin/request/token/proof coordinate;
4. compute the fixed-origin merge audit for observed bundles;
5. run the universal erasure-safety criterion on the rule graph;
6. if it fails, emit the violating rule and singleton-closure evidence as a deterministic policy-review witness;
7. use minimum-splicing search only when analysts need the smallest concrete multi-record attack bundle.

The theorem does not state that any standards-compliant protocol is unsafe. It asks whether a **particular downstream integration rule graph** remains sound after provenance coordinates are erased.

## 8. Publication boundary

The closure-theoretic union-preservation equivalence is mathematical context and should be cited rather than marketed as a standalone novelty claim.

The D manuscript's stronger composite result is the typed-authority analysis stack:

- exact coordinate nonpromotion and retraction;
- exact fixed-merge safety;
- origin-sensitive anti-splicing;
- polynomial universal origin-erasure preflight;
- NP-complete minimum hybrid-splicing search;
- independent real-domain validation.

Only the final combination, after current provenance/authorization prior-art subtraction and real-domain evidence, can support a top-tier systems/formal-methods significance claim.
