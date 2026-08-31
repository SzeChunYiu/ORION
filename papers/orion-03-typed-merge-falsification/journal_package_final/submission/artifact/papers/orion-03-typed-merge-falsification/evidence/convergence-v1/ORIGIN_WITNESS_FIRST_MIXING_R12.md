# Paper D R12 — exact origin-witness propagation and first-mixing certificates

Date: 2026-08-26

Exact parent: `f6b21c94b9cd372700d7a13ccc229e27637acef9`

Status: analytic extension of the typed-authority merge calculus, with a source-bound `agentgateway` authentication-to-authorization bridge control. Generic Horn closure, Datalog provenance, lineage semirings, truth maintenance and set-intersection propagation are donor-owned.

## 1. Problem sharpened by the real SAFE control

R11 proved that the pinned `agentgateway` `RuleSets` merge is origin-witness preserving: a merged authorization cannot erase a constituent deny or failed require, and any merged allow is already allowed by at least one constituent authorization origin.

That result rules out a broad claim that native same-field policy merge is generically unsafe. The remaining Paper-D question is narrower: when independently valid evidence origins feed a positive authorization pipeline through explicit bridges, can a pooled derivation be localized to the first rule that requires facts no single origin owns together?

The answer is exact for finite acyclic positive Horn programs.

## 2. Fine-origin and pooled semantics

Let `Lambda` be a finite nonempty origin set and let `A` be a finite set of atoms equipped with a topological order. Each origin `lambda` supplies a seed set `S_lambda subseteq A`.

A rule has the form

`h <- b_1,...,b_k`,

where `k>=1` and every body atom precedes `h`. Rules are positive and acyclic.

For each origin, let `C_lambda` be the ordinary Horn closure of `S_lambda`. Let `C_pool` be the Horn closure of the pooled seeds `union_lambda S_lambda`.

Define the **singleton-origin witness set**

`W(a) = {lambda in Lambda : a in C_lambda}`.

An atom `a` is a **hybrid authorization** exactly when

`a in C_pool` and `W(a)=empty`.

This definition does not reject every proof that happens to mix origins. It rejects only a pooled authorization for which no selected origin independently supplies a complete proof. If one origin supplies an alternative complete proof, the atom is not hybrid even if a mixed proof also exists.

## 3. Exact witness-set recurrence

For a seed atom, record every origin containing that seed. For a rule `r: h <- B`, define its singleton-origin contribution as

`I_r = intersection_{b in B} W(b)`.

### Theorem D-R12.1 — exact witness propagation

For every atom `h`,

`W(h) = SeedOrigins(h) union union_{r: head(r)=h} I_r`.

Because the program is acyclic, this recurrence is evaluated in one topological pass.

### Proof

If `lambda` belongs to the right-hand side, either `h` is a seed of `lambda`, or one rule for `h` has every premise in `C_lambda`; in either case `h in C_lambda`.

Conversely, if `h in C_lambda`, then either it is a seed or the last step of some origin-local Horn proof is a rule whose every premise lies in `C_lambda`. Thus `lambda` belongs to the corresponding body-witness intersection. ∎

The pooled Boolean recurrence is obtained by replacing seed-origin sets by existence and set intersection by conjunction. The two recurrences must not be conflated: pooled truth records whether some multi-origin proof exists, while `W` records whether some one-origin proof exists.

## 4. First-mixing localization

A pooled-enabled rule `r: h <- B` is a **first-mixing rule** when:

1. every body atom is pooled derivable;
2. every body atom has a nonempty singleton-origin witness set; and
3. `intersection_{b in B} W(b)=empty`.

Thus every premise is independently supported somewhere, but no origin supports all premises together.

### Theorem D-R12.2 — every hybrid authorization has a first-mixing ancestor

If `q` is hybrid, then every pooled proof tree for `q` contains a first-mixing rule. A certificate may choose the lowest hybrid atom in that tree; its selected deriving rule is first-mixing.

### Proof

A hybrid atom cannot be a pooled seed, since every pooled seed belongs to at least one `S_lambda` and therefore has a witness. Choose a pooled proof tree for `q` and a hybrid node `h` with no hybrid descendant. Its deriving rule is pooled enabled. Every body atom is nonhybrid and pooled, hence has a nonempty witness set. If their witness-set intersection contained `lambda`, Theorem D-R12.1 would put `lambda` in `W(h)`, contradicting hybridness. Therefore the intersection is empty. ∎

The certificate is local: the rule, each premise's nonempty witness set, their empty intersection, the pooled proof from that rule to `q`, and the independently recomputed fact `W(q)=empty`.

### Corollary D-R12.3 — alternative proofs prevent false alarms

If any origin independently derives `q`, then `W(q)` is nonempty and `q` is not hybrid, even when another pooled proof contains a first-mixing rule.

A detector based on “there exists a mixed proof” is therefore unsound for Paper D's authorization question. The correct predicate is pooled derivability plus empty singleton-origin witness set.

## 5. Exact audit algorithm

Represent each `W(a)` as a bitset over origins. In topological order:

1. initialize seed-origin bits;
2. for every rule, intersect its body bitsets;
3. union the result into the head bitset;
4. separately compute pooled Boolean reachability;
5. flag atoms that are pooled true and have the zero bitset;
6. for each flagged target, descend through a pooled proof until the first-mixing rule is reached.

### Theorem D-R12.4 — audit complexity

Let `L=|Lambda|` and let `B` be the total number of body-atom occurrences. With machine-word bitsets, all witness sets and pooled values are computed in

`O((|A| + B) ceil(L/w))`

time and `O(|A| ceil(L/w))` space, where `w` is the word size. Certificate extraction is linear in the chosen proof DAG.

This is the complexity of auditing one fixed pooled state. It does not solve the NP-complete minimum-dangerous-origin-subset problem proved in R10.

## 6. Compositional safety

Call a module **origin-witness preserving** on an interface when every pooled-derived interface atom has a nonempty witness set.

Call a bridge instance **overlap safe** when every pooled-enabled bridge rule has a nonempty intersection of its body witness sets.

### Theorem D-R12.5 — safe composition

If an upstream module is origin-witness preserving on its output interface, every enabled bridge rule is overlap safe, and the downstream module is origin-witness preserving relative to its input witnesses, then the composed pipeline is origin-witness preserving.

### Proof

Every pooled bridge conclusion receives a nonempty singleton-origin contribution from an enabled rule. These conclusions therefore enter the downstream module with nonempty witnesses. By downstream witness preservation, every pooled output retains a witness. ∎

### Corollary D-R12.6 — a hybrid output localizes a failed premise

Under the same finite acyclic contract, if the composed output is hybrid, then at least one of the following has a content-bound counterexample:

- the upstream module's witness-preservation claim;
- bridge overlap safety; or
- the downstream module's witness-preservation claim.

The first-mixing certificate identifies the earliest failed rule on a pooled proof.

This is a verification decomposition, not a claim that arbitrary systems expose enough provenance to instantiate it.

## 7. Source-bound `agentgateway` bridge control

Pinned repository: `agentgateway/agentgateway`

Pinned commit: `e136c7458b0fe0f51378dd31ffd60ab2b6939fc2`

Load-bearing blobs beyond R11:

- `crates/agentgateway/src/http/jwt.rs`: `32bd2c61741a3b65971d4b1831965c7e2e98071f`;
- `crates/agentgateway/src/cel/types.rs`: `29680dc3793fd51f1bb20af12ebd4d52a4587fa8`;
- R11 authorization and bind blobs remain `30e65076749448cb7b35d47ccf4303add7e6fec8` and `203227d5d19ee29848821d72b06a373908ddb3bf`.

The source establishes this exact bridge shape:

1. `Jwt::apply` validates one token into one `Claims` value;
2. the value is inserted into request extensions by its Rust type;
3. the CEL executor exposes one typed field `jwt: ExtensionOrDirect<jwt::Claims>`;
4. HTTP authorization creates one request executor and evaluates authorization expressions against that field;
5. authorization rule sets compose by the R11 deny/require/allow semantics.

Therefore the authorization evaluator does **not** consume a coordinatewise union of several JWT claim maps at this bridge. At evaluation time, claim predicates read one active typed `Claims` object. If the claim origin is the validated token, all JWT premises read from that slot share the same singleton origin witness. A conjunction of those JWT premises cannot be a cross-token first-mixing rule.

This is a SAFE result for the bound single-slot bridge, not a whole-gateway security certification. It does not cover facts copied into headers or metadata, external authorization responses, transformations, multiple request phases, policy-selection mistakes, or a different implementation that explicitly unions claim maps.

## 8. Hostile and null controls

### Cross-token erasure

Origin `A` supplies `subject=alice`; origin `B` supplies `scope=admin`; the authorization rule requires both. The pooled erased map derives authorization, while witness sets `{A}` and `{B}` have empty intersection. The rule is a first-mixing certificate.

A single-slot bridge selecting either token does not authorize.

### Alternative complete token

Add origin `C` containing both claims. The authorization witness set becomes `{C}`. A mixed `A+B` proof still exists, but the authorization is not hybrid.

### Explicit bridge license

If a registered bridge license deliberately authorizes a cross-origin tuple, that license must itself be represented as an authority origin or typed rule premise. Erasing it from the model and then calling the result splicing is invalid.

### Native authorization merge

The R11 source-bound `RuleSets` result remains a real null control: merged authorization has an individually authorizing origin and preserves every deny/require. R12 does not overwrite that result.

## 9. Prior-art boundary

Donor-owned material includes:

- positive Horn least fixed points;
- why/where provenance and lineage;
- provenance semirings and provenance polynomials;
- truth-maintenance dependency tracing;
- Datalog explanation and witness computation;
- set and bitset data-flow analysis.

Paper D cannot claim witness-set propagation or first-cause localization as generic database novelty. The residual candidate contribution is the exact singleton-origin authorization predicate, its distinction from merely mixed proofs, the first-mixing certificate tied to typed authority merge safety, and the source-bound discrimination between a real single-slot/safe-merge pipeline and a hostile coordinate-erased bridge.

## 10. Publication boundary and next experiment

The analytic theorem and finite verifier are manuscript-grade finite mathematics once independently reviewed. The real application evidence remains asymmetric:

- synthetic OAuth coordinate erasure: unsafe positive control;
- real `agentgateway` native authorization merge: safe control;
- real `agentgateway` JWT-to-CEL single-slot bridge: safe source-bound control.

A top-tier systems/security claim still requires an independently maintained integration in which multiple evidence records actually reach one authorization decision, with the origin-preserving and coordinate-erased implementations receiving identical information. A real SAFE result remains publishable specificity but does not demonstrate a deployed vulnerability.

No external domain adjudication, production exploit, novelty certificate, venue judgment or journal authority follows from this tranche.
