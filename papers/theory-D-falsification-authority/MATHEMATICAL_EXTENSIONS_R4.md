# Mathematical Extensions R4 — Per-License Evaluation and Minimal Refutation

Date: 2026-08-25

Canonical predecessor: `MANUSCRIPT_V3_PIPELINE.md`

Status: theorem addendum for integration into the next manuscript version. It uses the least-fixed-point semantics of V3 and does not restore the invalid greatest-fixed-point claim removed there.

## 1. Purpose

The V3 manuscript defines authority propagation correctly as a least fixed point and proves support, retraction, and evaluator-schema theorems. This addendum develops a second mathematical layer: coordinatewise Horn evaluation is linear-time for a fixed license, whereas selecting a smallest direct refutation that blocks a target is already NP-complete on acyclic depth-two graphs.

The result distinguishes two tasks that are often conflated:

1. evaluating what authority currently propagates; and
2. choosing the smallest intervention that stops a target authority claim.

## 2. Frozen model

Let `Q` be a finite claim set and `Lambda` a finite license set. Every claim `q` has seed authority `sigma(q) subseteq Lambda`. A positive rule is

`r=(B_r -> h_r, K_r)`,

where `B_r subseteq Q` is a finite body, `h_r in Q` is the head, and `K_r subseteq Lambda` is the rule cap.

For a direct-refutation set `R subseteq Q`, refuted claims have no authority and cannot support rules. The V3 operator is

`F_R(A)(q)=empty` for `q in R`,

and otherwise

`F_R(A)(q)=sigma(q) union union_{r:h_r=q, B_r cap R=empty}(K_r cap intersection_{p in B_r} A(p))`.

The intended semantics is the least fixed point

`Lic_R = lfp(F_R)`.

## 3. Per-license Horn reduction

Fix a license `lambda in Lambda`. Define a Boolean positive rule system `G_{R,lambda}` as follows.

- A claim `q notin R` is a Boolean seed when `lambda in sigma(q)`.
- A rule `B_r -> h_r` is retained when `lambda in K_r`, `h_r notin R`, and `B_r cap R=empty`.
- A retained rule fires when all body claims are reachable.

Let `Reach_{R,lambda}` be the least Horn closure of these Boolean seeds and rules.

**Theorem D1 (coordinatewise reduction).** For every claim `q`,

`lambda in Lic_R(q)` if and only if `q in Reach_{R,lambda}`.

**Proof.** Project every set-valued approximant of the V3 Kleene iteration onto the Boolean coordinate “contains `lambda`.” Seed union becomes Boolean seed membership. For a rule, `lambda` belongs to

`K_r cap intersection_{p in B_r} A(p)`

exactly when the rule cap contains `lambda` and every body claim contains `lambda`. Direct refutation removes the same claims and rules on both sides. The Boolean projections therefore have identical initial states and identical monotone update steps. Their least fixed points coincide. ∎

This theorem shows that licenses do not interact semantically in the positive model. The set-valued evaluator is a parallel family of ordinary Horn closures.

## 4. Worklist complexity

Let

`M = |Q| + sum_r (|B_r|+1)`

measure claims, rule heads, and body incidences. Assume constant-time membership in the frozen seed and cap sets after preprocessing.

**Theorem D2 (evaluation complexity).** For fixed `R` and `lambda`, membership of `lambda` in every `Lic_R(q)` can be computed in `O(M)` time and `O(M)` space. All licenses can be evaluated in `O(|Lambda| M)` time.

**Proof.** Use the standard Horn worklist. For every retained rule store a counter equal to its body size. Seed-reachable claims enter a queue. When a claim is popped, process each incident rule once and decrement its counter. A rule whose counter reaches zero marks its head reachable and enqueues it if new. Every claim is enqueued at most once and every body incidence is processed at most once. The all-license bound repeats the algorithm for each coordinate. ∎

Bitset implementations may improve constants or word-level parallelism. The theorem states a representation-independent linear bound in the explicit incidence size.

## 5. Proof footprints

A finite `lambda`-proof tree for target `q` is the V3 proof tree specialized to one license. Its leaves are unrefuted seed claims carrying `lambda`; each internal node is justified by a retained rule whose cap contains `lambda`.

The *footprint* of a proof tree is the set of all claim labels occurring in it. Let

`P_lambda(q)`

be the family of inclusion-minimal footprints of finite `lambda`-proof trees for `q` in the unrefuted graph.

Because `Q` is finite, there are finitely many possible footprints even if recursive rules admit infinitely many syntactic trees.

**Theorem D3 (minimal-refutation hitting-set law).** A direct-refutation set `R` removes `lambda` from target `q` if and only if

`R cap P != empty`

for every `P in P_lambda(q)`.

**Proof.** By the V3 proof-tree theorem, `lambda` survives at `q` exactly when at least one finite proof tree remains valid. A tree remains valid exactly when its footprint is disjoint from `R`. If any footprint is disjoint from `R`, an inclusion-minimal subfootprint realized by a proof tree is also disjoint, so `lambda` survives. Conversely, if `R` intersects every minimal footprint, it intersects every proof footprint and no proof tree survives. ∎

Thus minimal direct refutations are precisely minimal hitting sets of the antichain `P_lambda(q)`.

### Seed-only interventions

When only seed claims may be directly refuted, replace footprints by inclusion-minimal leaf-support sets. The same proof shows that a seed intervention blocks the target exactly when it hits every minimal leaf support.

## 6. Evaluation is easy; minimum intervention is hard

Define `SEED-BLOCKER`:

- input: an acyclic positive rule graph with one license, a target `q`, a designated set `B` of refutable seed claims, and integer `k`;
- question: is there `R subseteq B` with `|R|<=k` such that the target loses the license?

**Theorem D4 (NP-completeness of minimum seed refutation).** `SEED-BLOCKER` is NP-complete even when the rule graph has depth two beyond the seeds.

**Proof.** Membership in NP follows because a candidate `R` can be checked by the linear evaluator of Theorem D2.

For hardness, reduce HITTING SET. Let the universe be `U` and the nonempty family be `E_1,...,E_m`. Create one seed claim `s_u` carrying the sole license for each `u in U`. For every set `E_j`, create an intermediate claim `p_j` and the rule

`{s_u : u in E_j} -> p_j`.

For every `j`, add the singleton rule

`{p_j} -> q`.

All rule caps contain the license. In the unrefuted graph, `p_j` is licensed exactly when every seed indexed by `E_j` survives, and the target is licensed exactly when at least one `p_j` survives. Refuting seed set `R` removes the target exactly when every `E_j` contains a refuted element. Hence `R` blocks the target exactly when the corresponding universe elements form a hitting set. The construction is polynomial and has seed-to-intermediate-to-target depth two. ∎

**Corollary D5 (weighted intervention).** Assigning nonnegative refutation costs yields the weighted hitting-set problem on minimal seed supports. Exact optimization remains NP-hard, while any proposed intervention is still verified in linear time.

The generic hitting-set connection is donor-owned mathematics. The paper-local contribution is its exact derivation from the frozen license semantics, together with the evaluation/intervention boundary and the explicit depth-two reduction.

## 7. Cycles and fixed-point discipline

Theorems D1–D5 depend on the least fixed point. Replacing it by the greatest fixed point changes both evaluation and intervention semantics.

For example, two unsupported claims with rules `a->b` and `b->a` have empty least authority but may carry arbitrary authority at a greatest fixed point. Such a cycle would create spurious proof supports with no seed leaves and would invalidate the proof-footprint characterization.

The next manuscript version should therefore keep the following distinctions visible:

- positive cycles can propagate seeded authority;
- unsupported cycles do not create least-fixed-point authority;
- direct refutation removes nodes from both conclusions and support; and
- proof trees are finite and seed-founded.

## 8. Applications

### 8.1 Evidence and scientific-claim graphs

A license can represent permission to cite, reproduce, or operationalize a claim. Theorem D2 supports rapid recomputation after a retraction. Theorem D3 identifies minimal sets of claims whose withdrawal blocks a downstream conclusion.

### 8.2 Regulatory and policy provenance

Rule caps can encode jurisdiction, data-use permission, or review scope. Coordinatewise evaluation permits separate auditing of each license. Minimum intervention then asks for the least costly evidence withdrawal that prevents a regulated conclusion from remaining authorized.

### 8.3 Trustworthy AI pipelines

Claims may represent model outputs, data assertions, or tool results, while licenses record provenance classes. The least-fixed-point semantics prevents unsupported recursive agreement among agents from manufacturing authority. Minimal blockers expose which evidence nodes must be challenged to invalidate a downstream answer.

### 8.4 Incident response

When a source is compromised, the linear evaluator computes all downstream authority losses. For proactive hardening, minimal proof footprints identify alternate evidence paths; a target with many disjoint supports is harder to disable by a small intervention.

### 8.5 Audit planning

The evaluation/intervention dichotomy explains why checking a proposed refutation is cheap while choosing the best one can be difficult. This supports certified heuristics: an optimizer proposes a blocker, and the exact evaluator verifies its effect.

These are potential application models. The addendum does not claim a deployed regulatory, scientific, or AI system.

## 9. Further mathematical directions

### 9.1 Parameterized algorithms

The hitting-set form suggests fixed-parameter algorithms in blocker size, proof-width, or number of minimal supports. Such results require a separate complexity analysis and are not asserted here.

### 9.2 Counting and robustness

Counting minimal proof supports would quantify redundancy. A target with `r` pairwise claim-disjoint proof footprints requires at least `r` direct refutations. This lower bound follows immediately because a single refuted claim can hit at most one member of a disjoint family.

### 9.3 Negative premises

The coordinatewise Horn reduction relies on positivity. Adding negation or default assumptions changes monotonicity and may destroy least-fixed-point retraction behavior. Such extensions need a new semantics rather than an informal reuse of the current theorems.

## 10. Integration into the manuscript

1. Insert Theorems D1 and D2 after the least-fixed-point and proof-tree sections.
2. Add proof footprints and Theorem D3 as the mathematical bridge from evaluation to intervention.
3. Present Theorem D4 as a separate complexity result, with an explicit donor boundary to classical hitting set and Horn provenance.
4. Use the application cases in Section 8 to replace generic provenance motivation.
5. Keep the unsupported-cycle counterexample in the main text or a visible boxed warning.

## 11. Atomic claim status

- Per-license Horn reduction: `VERIFIED`.
- Linear worklist evaluation: `VERIFIED` in explicit incidence size.
- Minimal-refutation hitting-set law: `VERIFIED` from the finite proof-tree theorem.
- NP-completeness of seed blocker: `VERIFIED` by the displayed HITTING SET reduction.
- Weighted extension: `VERIFIED` as the weighted hitting-set specialization.
- Generic novelty of hitting-set provenance: `NOT_CLAIMED`.
- External deployment impact: `NOT_CLAIMED`.

## 12. Editorial effect

Paper D now has a sharper mathematical spine: monotone authority evaluation is tractable, but optimal falsification intervention is combinatorially hard. This is substantially stronger than a semantics-only research note. The remaining high-selectivity gates are a primary-source overlap audit against database provenance and a fully worked application instance whose rule graph and intervention question are independently meaningful.