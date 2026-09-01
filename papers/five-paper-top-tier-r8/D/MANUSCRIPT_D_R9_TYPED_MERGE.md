# Typed Authority under Evidence Retraction and Graph Merge

**R9 research manuscript — 2026-08-26**

## Abstract

Reachability in a dependency graph does not identify the authority under which a surviving conclusion may be used. We study finite positive conjunctive rule graphs in which independent seeds carry declared evidence licenses and every rule has a license cap. Directly refuted claims receive the empty label. The induced monotone operator has a least fixed point on a finite powerset lattice.

A license reaches a claim exactly when a finite, seed-founded, unrefuted proof tree carries that license through every leaf and rule cap. Unsupported cycles create no authority; additional refutations can only remove licenses; and post-outcome, bounded-computation, jurisdictional, or other restricted evidence cannot promote itself to a stronger coordinate absent an authorized seed-and-cap path. Projecting onto one license yields an ordinary positive Horn program, giving linear-time worklist evaluation in the explicit incidence size, strong noninterference between license coordinates, a syntactic license quotient, and a policy dominance preorder.

The main extension concerns **graph merge**. Two evidence records may be individually safe while their union creates a hybrid proof whose premises come from different records. For one license, let `C` be the union of the two component closures. The merge introduces no new authority exactly when `C` is closed under every rule admitted by the merged license projection. This fixed-point criterion is both necessary and sufficient and is checked by one Horn replay initialized at `C`. When authorized bridges are declared, the same theorem applies after computing the intended bridge closure. Origin-sensitive licenses can prevent unauthorized evidence splicing by requiring every rule path to carry an allowed provenance coordinate rather than an untyped conclusion alone.

A deterministic evaluator, JSON schema, proof-tree extractor, retraction ledger, merge-safety checker, and hostile corpus accompany the theory. The registered finite audit evaluates approximately 16.8 million graph-pair merges and exercises unsupported cycles, cap confusion, alternative derivations, direct refutation, and cross-record evidence splicing. This exhaustive bounded audit corroborates the implementation but does not establish real policy validity.

The remaining broad-impact gate is external: an independently maintained permission or evidence policy must be encoded and adjudicated by domain reviewers, and the typed system must prevent a consequential authority error made by an untyped baseline. The calculus tracks declared authority, not factual truth, legal compliance, probability, inconsistency, defaults, or arbitrary negation.

## 1. From derivability to licensed use

Scientific and operational records mix claims supported by different kinds of evidence. An analytic proof, finite exhaustive computation, prospective prediction, post-outcome repair, data-use consent, and jurisdictional approval may all support the same untyped sentence while licensing different downstream actions.

An untyped graph answers whether a conclusion remains reachable. It cannot answer:

- whether the surviving path is theorem-grade or bounded computation;
- whether a repaired forecast remains prospective;
- whether evidence is authorized for a jurisdiction or data-use purpose;
- whether two records can be combined without manufacturing a hybrid permission; or
- which claim-license pairs lose every valid proof after a refutation.

We attach licenses to a positive least-fixed-point semantics. The model is intentionally small. It is not a general theory of scientific truth or legal interpretation. Its value is that nonpromotion and retraction are explicit, executable, and auditable.

### Contributions

1. finite powerset-license least-fixed-point semantics;
2. a finite seed-founded proof-tree characterization;
3. canonical typed retraction and refutation monotonicity;
4. coordinatewise Horn reduction and linear-time evaluation;
5. strong license noninterference, syntactic compression, and policy dominance;
6. an exact graph-merge safety criterion;
7. an origin-sensitive defense against cross-record evidence splicing;
8. deterministic evaluator, schema, hostile corpus, and exhaustive bounded merge audit; and
9. a frozen real-domain validation protocol separating formal correctness from policy usefulness.

Generic fixed points, Horn evaluation, provenance annotations, minimal supports, hitting sets, causality, resilience, and deletion robustness are established work and are not claimed as generic novelty.

## 2. Typed positive rule graphs

Let `Q` be a finite claim set and `Lambda` a finite license set. Each claim `q` has an independent seed label

`sigma(q) subseteq Lambda`.

A rule is

`r=(B_r -> h_r, K_r)`,

where `B_r` is a nonempty finite body, `h_r` is the head, and `K_r subseteq Lambda` is the cap. A license crosses the rule only if every premise carries it and the cap permits it:

`tau_r((L_p)_{p in B_r}) = K_r intersection intersection_{p in B_r} L_p`.

Let `R subseteq Q` be directly refuted claims. Define the operator

`F_R(L)(q)=empty` for `q in R`,

and otherwise

`F_R(L)(q)=sigma(q) union union_{r:h_r=q}[K_r intersection intersection_{p in B_r}L(p)]`.

The intended authority assignment is

`Lic_R = lfp(F_R)`.

Rules with empty bodies are represented as seeds. Direct refutation removes a claim both as a conclusion and as a premise source.

## 3. Fixed point and proof trees

### Theorem 1 — finite convergence and schedule independence

Synchronous iteration from all-empty labels stabilizes after at most `|Q||Lambda|` label additions plus a final check. Every fair accumulating asynchronous schedule reaches the same least fixed point.

### Theorem 2 — typed proof-tree equivalence

A license `lambda` belongs to `Lic_R(q)` if and only if there exists a finite proof tree rooted at `q` such that:

1. no node is directly refuted;
2. every leaf `a` has `lambda in sigma(a)`; and
3. every internal node applies a declared rule whose cap contains `lambda`, with one child proof for every antecedent.

The proof is induction on fixed-point iteration and tree height.

### Corollary 3 — unsupported cycles remain empty

A positive cycle without a licensed seed has no finite seed-founded proof tree and therefore creates no authority. A seeded cycle can propagate only licenses permitted by every traversed cap.

### Corollary 4 — license conservation

Every derived license occurs in every leaf seed and every rule cap along at least one valid proof tree. A theorem-shaped head does not create a theorem license.

## 4. Retraction under direct refutation

### Theorem 5 — refutation monotonicity

If `R subseteq R'`, then

`Lic_{R'}(q) subseteq Lic_R(q)`

for every claim.

### Definition 6 — typed retraction

Let `L_pre=Lic_empty` and `L_post=Lic_R`. Define

`Ret(R)={(q,lambda): lambda in L_pre(q) minus L_post(q)}`.

### Theorem 7 — canonical semantic retraction

Relative to the declared seeds, rules, caps, and refutations, `L_post` is the unique assignment containing exactly the claim-license pairs with a finite untainted proof tree. The retraction removes every and only pair that loses all such trees.

This is semantic canonicity relative to the input policy. It is not a claim that the policy encoding is uniquely correct.

## 5. Coordinatewise Horn evaluation

Fix a license `lambda`. Retain:

- every unrefuted seed claim carrying `lambda`; and
- every unrefuted rule whose cap contains `lambda` and whose body contains no directly refuted claim.

Let `Reach_{R,lambda}` be the least Boolean Horn closure.

### Theorem 8 — coordinatewise reduction

`lambda in Lic_R(q)` if and only if `q in Reach_{R,lambda}`.

Thus licenses do not interact semantically in the positive calculus. The set-valued evaluator is a parallel family of Boolean Horn programs.

### Theorem 9 — worklist complexity

Let

`M=|Q|+sum_r(|B_r|+1)`.

For fixed `R` and `lambda`, all reachable claims are computed in `O(M)` time and `O(M)` space. All licenses are evaluated in `O(|Lambda|M)` time, with bitset implementations improving constants where appropriate.

## 6. License noninterference and policy order

For a license `lambda`, define its projection by the seed set

`S_lambda={q:lambda in sigma(q)}`

and retained rule set

`P_lambda={r:lambda in K_r}`.

### Theorem 10 — strong license noninterference

Two typed systems with the same claim/rule shapes, refutations, `lambda` seed projection, and `lambda` rule projection derive `lambda` at exactly the same claims, regardless of all other license coordinates.

### Corollary 11 — license compression

Licenses with identical seed-and-cap signatures have identical derived claim sets under every refutation set. They may be evaluated once and expanded afterward.

### Theorem 12 — projection dominance

Write `lambda preceq mu` when `S_lambda subseteq S_mu` and `P_lambda subseteq P_mu`. Then, under every direct-refutation set,

`Reach_{R,lambda} subseteq Reach_{R,mu}`.

The preorder is a property of the declared policy encoding, not an inherent philosophical order among evidence types.

### Corollary 13 — formal nonpromotion

If a target is outside the Horn closure of `S_lambda` under `P_lambda`, evidence on foreign license coordinates cannot give the target `lambda`. In particular, a post-outcome repair cannot regain prospective authority without a prospective seed-and-cap path.

## 7. Merge-induced authority

Independent evidence records are often combined. Even when each record is internally valid, their union can create a proof that neither record contained.

Fix one license `lambda`. Let programs `G_1` and `G_2` share a declared claim vocabulary or a content-bound alignment. Let their seed closures be

`C_1=Cl_{G_1}(S_1)` and `C_2=Cl_{G_2}(S_2)`.

The naive expected merged authority is

`C=C_1 union C_2`.

A **hybrid proof** is a proof in the union program whose leaves or rules draw essentially from both records and whose conclusion is outside `C`.

### Theorem 14 — exact merge-safety criterion

For the union program `G=G_1 union G_2`, the merge introduces no new `lambda` authority beyond the component closures if and only if `C` is closed under every rule of `G`. Equivalently,

`Cl_G(S_1 union S_2)=C`

if and only if, for every rule `B->h` in `G`,

`B subseteq C` implies `h in C`.

**Proof.** If the union closure equals `C`, fixed-point closure is necessary. Conversely, if `C` contains the seeds and is closed under every union rule, it is a fixed point above the seed set. The least union fixed point is contained in `C`; it also contains both component closures, so equality follows. ∎

The criterion is checked by initializing a worklist at `C`; any newly added claim is a merge-induced authority witness. The first firing can be serialized with its cross-record premises.

### Authorized bridges

Let `B` be a declared bridge program. Compute the intended closure

`C_B=Cl_{G_1 union G_2 union B}(C_1 union C_2)`

under only authorized bridge and component rules. A broader runtime merge is safe relative to that policy exactly when `C_B` is closed under the runtime rule set. This separates intended composition from accidental splicing.

## 8. Origin-sensitive defense against evidence splicing

License type alone may be too coarse. Two claims can both carry `THEOREM` while their conjunction is unauthorized because they come from incompatible models, jurisdictions, datasets, or versions.

Let an authority coordinate be a pair `(lambda,o)` where `o` belongs to a finite origin or compatibility policy. Rule caps list the origin combinations permitted to cross. The same least-fixed-point semantics applies on the expanded coordinate set.

### Theorem 15 — origin-coordinate nonpromotion

No conclusion receives `(lambda,o)` unless a finite proof tree carries that exact coordinate from every leaf through every rule cap. Combining two foreign origins cannot manufacture a compatible origin coordinate absent an authorized bridge.

This is a direct instance of license conservation, but it changes the operational merge result. The price is policy granularity and possible state growth; the origin vocabulary must be curated rather than inferred as truth.

## 9. Proof footprints and intervention

For a fixed license, the inclusion-minimal proof footprints form a finite antichain. A direct-refutation set removes the license from a target exactly when it intersects every minimal footprint. Seed-only intervention is the analogous hitting-set problem on minimal leaf supports.

This connection is useful for audit and incident response but is not claimed as generic novelty. Current recursive-Datalog causality and resilience work, together with earlier provenance research, already develops minimal supports, responsibility, robustness, and deletion reasoning. The residual here is typed cap-preserving authority and merge/nonpromotion policy.

## 10. Executable semantics and bounded audit

The package includes:

1. JSON schema for claims, licenses, seeds, rules, caps, refutations, origins, and authorized bridges;
2. deterministic fixed-point evaluator;
3. proof-tree and first-new-merge-witness extraction;
4. typed retraction ledger;
5. license-signature quotient and dominance audit;
6. merge-safety checker implementing Theorem 14; and
7. hostile fixtures.

The registered finite generator exhausts approximately 16.8 million graph-pair merges in its declared bounded universe. It checks component closure, merged closure, first hybrid proof, unsupported cycles, cap blocking, alternative derivations, direct refutation, coordinate noninterference, and origin splicing. A second implementation is required by the R9 harness before the bounded audit is treated as independently reproduced.

The exhaustive finite result validates the implementation on its declared universe. The analytic theorems carry all-size authority.

## 11. Real-domain validation protocol

Formal correctness does not establish that the license vocabulary or rule conjunctions match a consequential policy. The R9 experiment therefore freezes:

- one permission-bearing domain;
- an independently maintained source corpus;
- a traceable rule-extraction protocol;
- at least two domain encoders or adjudicators;
- one operational authorization query;
- an untyped reachability baseline;
- typed licenses and caps;
- clean, refuted, spliced, cycle, and cap-confusion cases; and
- promotion and cannot-check terminals.

The desired discriminator is a case where untyped reachability authorizes an action that the curated policy forbids, while the typed system blocks it for a reviewable license or origin reason. Null regimes must also remain visible. If the domain requires negation, defaults, inconsistency handling, or probability, the current model must reject the encoding rather than silently reuse positive semantics.

## 12. Applications

### 12.1 Scientific evidence graphs

After evidence withdrawal, typed replay reports which claims remain citeable, reproducible, operational, or theorem-grade. The system tracks declared authority, not factual truth.

### 12.2 Multi-agent and tool pipelines

Seed-founded proof trees prevent agents or tools from manufacturing provenance by recursively citing one another. Origin coordinates can prevent two individually authenticated but incompatible results from being spliced into a stronger permission.

### 12.3 Data-use and jurisdictional policy

Licenses can represent consent, purpose, jurisdiction, or review scope. Domain experts must validate the encoding; the calculus alone is not legal compliance.

### 12.4 Incident response

Known compromised claims are evaluated in linear time. Choosing the smallest proactive intervention can remain combinatorially difficult; a proposed blocker can nevertheless be verified exactly.

### 12.5 Model and dataset governance

A downstream model claim may remain reachable while losing the license needed for deployment, reproduction, or cross-dataset transfer. Merge safety exposes hybrid derivations created only after registries are combined.

## 13. Prior-art boundary

The paper claims no generic novelty for:

- least fixed points or positive Datalog;
- proof trees and Horn worklists;
- semiring/annotated provenance;
- trust annotations;
- minimal supports, causes, responsibility, hitting sets, resilience, or deletion robustness; or
- access-control and policy logics in general.

The residual contribution is a compact typed evidence-policy component: powerset licenses, cap-preserving nonpromotion, exact typed retraction, coordinate noninterference, projection dominance, graph-merge safety, origin-sensitive anti-splicing, and executable scientific cases.

A current primary-source overlap matrix is a submission gate.

## 14. Limitations

- Positive conjunctive rules only.
- No arbitrary negation, defaults, probability, inconsistency, or nonmonotonic belief revision.
- License and origin sets are policy inputs, not inferred truth.
- Direct refutation is one update model; belief contraction with defeasible assumptions is different.
- Proof-footprint families can be exponentially large.
- Exhaustive bounded testing is not a proof of policy validity.
- Real-domain usability and reviewer agreement remain open evidence gates.

## 15. Conclusion

Reachability is not authority, and graph union is not automatically safe composition. Typed least-fixed-point semantics makes evidence coordinates travel with their proof paths; direct refutation removes exactly the coordinates that lose all valid trees; and the merge-safety criterion identifies when combining records creates a new hybrid proof.

The mathematics is complete for finite positive rule graphs. The publication frontier is deliberately external: demonstrate that the distinction prevents an independently recognized policy error, or retain the paper as a scoped formal component rather than claiming broad scientific-governance impact.

## Tool-use disclosure

A generative language model assisted organization, language revision, theorem exploration, hostile-test design, and preparation of the real-domain protocol. The author is responsible for the formal semantics, proofs, policy encoding, code, data, citations, and final claims.
