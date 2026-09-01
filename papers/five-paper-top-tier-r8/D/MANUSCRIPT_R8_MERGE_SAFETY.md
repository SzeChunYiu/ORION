# Typed Authority Without License Splicing: Least-Fixed-Point Semantics and Exact Merge Safety

## Abstract

Positive rule graphs can track whether a conclusion is reachable, but an operational system often needs a stronger question: **under which declared evidence or permission class is the conclusion authorized?** We attach finite sets of authority licenses to claims, give every rule an explicit license cap, and evaluate the resulting positive conjunctive program by its least fixed point. A license reaches a claim exactly when a finite seed-founded proof tree carries the license through every premise and cap. Unsupported cycles create no authority, direct refutation can only remove licenses, and post-outcome or bounded-computation paths cannot acquire a stronger license absent an admissible seed path.

Typing creates a new composition hazard. Two license coordinates that are safe when evaluated separately can become unsafe when their seeds and rules are merged: one coordinate may supply a seed while another supplies a rule, or separate coordinates may supply different premises of a conjunction. We prove an exact merge-safety criterion. Let `C_1` and `C_2` be the separate Horn closures and `U=C_1 union C_2`. The closure after merging the coordinates equals `U` if and only if `U` is closed under every rule admitted by the merged policy. Otherwise the difference is precisely the license-splicing set created by the merge.

A deterministic checker replays seed/rule, conjunctive-premise, and recursive-bridge attacks, together with dominance and disconnected controls. An exhaustive audit over 4,096 license signatures on three claims and a nine-rule pool evaluates all 16,777,216 ordered pairs. It finds 878,592 unsafe merges, with zero disagreements between direct merged evaluation and the closure criterion. The generic least-fixed-point, provenance, minimal-support, and deletion-causality machinery is established prior work; the residual contribution is typed nonpromotion and exact coordinate merge safety. A real domain-policy validation remains required before an operational compliance or scientific-governance claim.

## 1. Introduction

Scientific, regulatory, and agentic systems routinely distinguish forms of support. A conclusion may be analytically proved, reproduced by an external group, supported only by bounded computation, available for prospective use, or licensed only after an outcome is known. A Boolean dependency graph erases these distinctions.

Typed labels solve only part of the problem. If a policy engine later coalesces two labels, aliases two roles, or combines two independently curated rule projections, the merged graph may create a path that existed in neither coordinate. This is not ordinary propagation. It is **license splicing**.

Examples include:

- one coordinate supplies an authorized seed and another supplies the rule from that seed to an action;
- two coordinates separately authorize different premises of a conjunctive rule;
- separate partial bridges combine into a recursive derivation; and
- a supposedly weaker and stronger permission are merged without checking whether their rule sets are compatible.

This paper formalizes both the typed positive semantics and the merge hazard. It deliberately excludes negation, probability, inconsistent rules, and broad claims about human scientific judgment.

### Contributions

1. Finite powerset labels with capped positive conjunctive transfer.
2. Least-fixed-point, schedule-independence, proof-tree, nonpromotion, and retraction theorems.
3. Coordinatewise Horn reduction and static license-signature compression.
4. An exact necessary-and-sufficient safe-merge criterion.
5. A deterministic hostile checker and exhaustive 16.8-million-pair audit.
6. A deployment contract that separates internal mathematical validity from domain-policy validation.

## 2. Typed positive rule systems

Let `Q` be a finite claim set and `Lambda` a finite license set. Each claim `q` has an independent seed label `sigma(q) subseteq Lambda`.

A positive rule is

`r=(B_r -> h_r, K_r)`,

where `B_r` is a nonempty finite body, `h_r` a head, and `K_r subseteq Lambda` the license cap. Given current labels `A(q)`, the rule transfers

`K_r intersect intersection_{p in B_r} A(p)`.

Let `R subseteq Q` be directly refuted claims. Refuted claims receive the empty label and cannot support rules. Define `F_R` by seed union and all capped rule transfers at unrefuted heads. The semantics is

`Lic_R=lfp(F_R)`.

### Theorem 1 — finite convergence

Bottom-up iteration reaches the least fixed point after at most `|Q||Lambda|` label additions. Every fair accumulating rule schedule reaches the same assignment.

### Theorem 2 — typed proof trees

`lambda in Lic_R(q)` if and only if there is a finite unrefuted proof tree rooted at `q` whose leaves are seeds carrying `lambda` and whose every rule cap admits `lambda`.

The proof is the standard induction between first-entry iteration rank and tree height.

### Consequences

- unsupported positive cycles stay empty;
- a license at a conclusion occurs on every seed and rule cap along at least one proof tree;
- if `R subseteq R'`, then `Lic_{R'}(q) subseteq Lic_R(q)`;
- typed retraction removes exactly the claim-license pairs that lose all untainted proof trees; and
- evidence on another license coordinate cannot manufacture `lambda` authority.

## 3. Per-license projections

Fix `lambda`. Retain exactly:

- unrefuted seeds whose seed label contains `lambda`; and
- unrefuted rules whose cap contains `lambda` and whose body contains no refuted claim.

### Theorem 3 — coordinatewise Horn reduction

A claim carries `lambda` in the typed least fixed point exactly when it is reachable in this ordinary positive Horn program.

Thus licenses are semantically independent coordinates until an external policy operation changes their projections.

### Static quotient and dominance

Define the syntactic signature of a license by its seed-membership and rule-cap-membership bit vectors. Identical signatures have identical derived claim sets under every refutation and may be evaluated once.

If the seed and rule projection of `lambda` is contained in that of `mu`, then every `lambda`-licensed claim is also `mu`-licensed. This is a policy-defined preorder, not an intrinsic hierarchy of evidence.

## 4. The license-splicing problem

Consider two coordinates over the same claim and rule shapes. Coordinate `i` has seed set `S_i` and retained-rule set `P_i`. Let

`C_i=Cl(S_i,P_i)`

be its least Horn closure. A naive alias or merge forms

`S=S_1 union S_2`, `P=P_1 union P_2`

and computes `C=Cl(S,P)`.

Monotonicity always gives `C_1 union C_2 subseteq C`. The inclusion can be strict.

### Attack A — seed/rule splice

Coordinate one licenses seed `a` but not rule `a->target`. Coordinate two admits the rule but has no seed. Both separate target closures are empty; the merge derives the target.

### Attack B — conjunctive-premise splice

One coordinate derives `a`, the other derives `b`, and the merged rule pool contains `{a,b}->target`. Neither separate coordinate supplies all premises; the merge does.

### Attack C — recursive bridge splice

One coordinate supplies a seed and one edge of a cycle/chain; another supplies the remaining bridge and target rule. The merged closure creates several intermediate claims and the target.

These attacks do not require unsupported greatest-fixed-point cycles. They occur under the ordinary seed-founded least fixed point.

## 5. Exact safe-merge theorem

Let `U=C_1 union C_2`.

### Theorem 4 — safe merge iff closed union

`Cl(S_1 union S_2, P_1 union P_2)=U`

if and only if `U` is closed under every rule in `P_1 union P_2`.

**Proof.** If the merged closure equals `U`, every merged rule whose body lies in `U` has its head in the closure and therefore in `U`; so `U` is closed.

Conversely, `U` contains both seed sets. If it is closed under every merged rule, it is a model of the merged Horn program. The least merged closure is therefore contained in `U`. Monotonicity supplies the reverse inclusion because each separate program is a subprogram of the merge. ∎

Define the **splicing set** as

`Splice=(merged closure) minus U`.

The theorem gives a linear-time checker after the separate closures are known: scan each merged rule and test whether its body is contained in `U` while its head is not. If no violation exists, the merge is safe. If one exists, bottom-up merged evaluation enumerates the full splicing set.

### Corollary — dominance-safe merge

If one complete coordinate projection contains the other, the merge equals the stronger projection and is safe.

### Corollary — disconnected safe merge

If no merged rule has semantic support crossing the claim regions reached by the two coordinates, the union is closed and the merge is safe.

## 6. Executable hostile audit

The R8 checker implements:

1. ordinary Horn closure;
2. separate coordinate closures;
3. merged closure;
4. the closed-union criterion; and
5. attack/control serialization.

The explicit suite contains three unsafe and two safe cases. Every expected disposition is reproduced.

### Exhaustive census

For three claims, the frozen rule pool contains six unary and three binary-conjunctive rules. A coordinate signature chooses any seed subset and any rule subset, yielding 4,096 signatures. The audit evaluates every ordered pair:

- ordered pairs: 16,777,216;
- safe: 15,898,624;
- unsafe: 878,592;
- maximum new claims from splicing: two; and
- criterion mismatches: zero.

This is a complete finite test of the implementation on the declared pool. The theorem carries the general authority.

## 7. Retraction, intervention, and donor boundary

Minimal proof supports and their hitting sets describe which direct refutations block a positive target. Current recursive-Datalog work develops minimal supports, causality, responsibility, and robustness in considerably greater generality than this paper's application. Those generic results are not claimed here.

The typed system contributes a different coordinate: a claim may remain reachable but lose one authority license, and a policy merge may create authority through cross-coordinate splicing. Retraction is computed per coordinate; merge safety is checked before aliases or policy unions are admitted.

Optimal intervention may still be hard, but generic hitting-set hardness is context rather than the headline.

## 8. Applications

### 8.1 Scientific evidence records

Keep theorem, finite-exact, prospective, post-outcome, and external-replay authority separate. A repaired claim can remain reachable while prospective authority stays retracted. Merging evidence classes requires the safe-merge check.

### 8.2 Multi-agent and tool pipelines

Agents, tools, memories, or sources can carry different action licenses. Unsupported mutual citation creates no license. More subtly, aliasing two role labels can splice a source path and a tool permission into an unauthorized action. The safe-merge theorem detects that exact structural hazard.

### 8.3 Regulatory and data-use policy

Jurisdiction, consent, purpose, and review-scope coordinates can be evaluated separately. Before a policy engine coalesces roles or permissions, it can prove that the union of separate closures is closed under all newly shared rules.

These are model routes, not validated deployments. Domain experts must confirm that positive conjunction, direct refutation, and caps match the source policy.

## 9. Relation to prior work

Positive Datalog, least-fixed-point semantics, provenance semirings and annotations, trust-aware reasoning, truth maintenance, minimal supports, causal responsibility, and deletion robustness are established. Recent recursive and stratified Datalog work makes the generic support/hitting-set overlap especially explicit.

The residual contribution is deliberately narrow:

- a finite evidence-license policy with cap-preserving nonpromotion;
- coordinate signatures and dominance;
- exact unsafe-merge semantics for license projections;
- a necessary-and-sufficient closed-union test; and
- executable hostile attacks that change the reportable authority while ordinary untyped reachability can appear acceptable.

A final submission must include a full primary-source comparison and a real domain-reviewed case.

## 10. Limitations

The calculus is finite, positive, and conjunctive. It does not model negation, defaults, probabilities, inconsistent evidence, defeasible priorities, or legal interpretation. Direct refutation is a hard node removal. Caps and license vocabulary are curated inputs. A well-founded authority graph does not make its claims true.

The 16.8-million-pair census verifies a small implementation universe, not policy adequacy. No compliance, safety, or human-science usability claim is made without the external case gate.

## 11. Conclusion

Typed reachability prevents obvious authority promotion, but types themselves must be composed safely. Two harmless coordinates can become harmful when their seeds, rules, or conjunctive premises are pooled. The exact boundary is simple: the merge is safe precisely when the union of the separate closures is already closed under every merged rule.

That criterion is cheap to check, exposes concrete splicing witnesses, and complements rather than replaces existing provenance and causality theory. Its operational value now depends on a real policy encoding whose semantics are validated outside the authors' own system.

## Tool-use disclosure

A generative language model assisted manuscript organization, code generation, and language revision. The author remains responsible for every theorem, implementation, source, and claim.
