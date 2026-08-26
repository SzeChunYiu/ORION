# Mathematical Extensions R6 — Proof-Tree Intersection Semantics and a Bound QG5 Retraction Record

Date: 2026-08-26

Canonical predecessors: `MANUSCRIPT_V3_PIPELINE.md`, `MATHEMATICAL_EXTENSIONS_R4.md`, `MATHEMATICAL_EXTENSIONS_R5.md`, and `research/extensions/orion-qg/PAPER_D_D1_AUTHORITY_CALCULUS_RESULTS_2026-08-24.json`

Status: rigorous theorem-and-application addendum for finite acyclic registered certificate hypergraphs. Generic provenance and reachability results receive no novelty credit.

## 1. Contribution

R5 proved license-coordinate noninterference, syntactic compression, dominance, and nonpromotion. This addendum adds a normal form that makes the difference between reachability and authority explicit: every authorized license is witnessed by one proof tree whose seed labels and rule caps share that license.

The theorem yields an exact failure mode for untyped systems. A conclusion may remain reachable through a proof assembled from individually valid premises while carrying no license at all, because no single license survives the intersection along that proof. It also binds the formal calculus to the existing QG5 record in which one counterexample retracts exactly two claims while independent theorem and repaired claims survive.

## 2. Registered acyclic typed systems

Let `Q` be a finite set of claims and `Lambda` a finite license set. Each seed claim `q` carries an initial label set `sigma(q) subseteq Lambda`. Each registered positive rule

`r: B_r -> h_r`

has a cap `K_r subseteq Lambda`. A derivation through `r` propagates

`K_r intersection (intersection_{q in B_r} Lic(q))`.

Alternative derivations are combined by union. Directly refuted claims are unavailable as seeds, premises, or heads. Assume the registered dependency hypergraph is acyclic.

A *proof tree* for a claim is a finite rooted tree whose leaves are non-refuted seeds and whose internal nodes are registered rules. Define the authority of a proof tree by

`Auth(T)=intersection of all leaf seed labels and all internal rule caps in T`.

## 3. Proof-tree formula

**Theorem D10 (proof-tree intersection semantics).** For every claim `q`,

`Lic(q)=union_{T in PT(q)} Auth(T)`,

where `PT(q)` is the set of non-refuted proof trees for `q`.

**Proof.** Order claims topologically. A seed tree contributes exactly its seed label set. For a rule tree with root rule `r`, choose one proof tree for every premise. The license set carried by that composite tree is the intersection of the selected premise authorities with `K_r`, exactly matching the rule update. Taking every combination of premise trees and then the union over alternative root rules reproduces the monotone fixed-point update. Induction along the topological order proves equality at every claim. ∎

The formula is not merely explanatory. It gives a finite witness for every retained license: one proof tree whose complete authority intersection contains that license.

## 4. Reachability is strictly weaker than authority

Erase all label sets and caps but retain the same seeds and rule shapes. Call the resulting Boolean conclusion relation *untyped reachability*.

**Corollary D11 (typed–untyped separation).** A claim is untyped-reachable exactly when it has at least one proof tree. A license `lambda` is authorized for that claim exactly when at least one proof tree has `lambda in Auth(T)`.

Consequently, untyped reachability can hold while `Lic(q)` is empty.

**Example.** Let seed `p` carry only license `A`, seed `q` carry only license `B`, and let a rule `{p,q}->r` have cap `{A,B}`. The untyped rule fires. Typed propagation yields

`{A} intersection {B} intersection {A,B}=emptyset`.

Thus `r` is reachable but has no reportable authority. This is the precise error made by systems that treat existence of a proof as permission to reuse its conclusion under every premise's authority.

## 5. Refutation as proof-tree deletion

**Corollary D12 (exact refutation update).** After directly refuting a set `R subseteq Q`, delete every proof tree that contains a refuted claim as a leaf, internal premise, or root. The post-refutation authority is the union of the intersections on the remaining trees.

A license retracts exactly when every proof tree carrying that license is deleted. A conclusion can remain reachable or retain other licenses through an alternative tree. This is stronger than deleting the conclusion wholesale and more precise than preserving its entire pre-refutation label.

R5 license noninterference is immediate from this formula: changing coordinates other than `lambda` cannot create or destroy a `lambda`-carrying proof tree unless the `lambda` projection itself changes.

## 6. Bound QG5 application

The registered QG5 authority record supplies a concrete application rather than a synthetic policy toy. Its frozen benchmark contains 9,546 rows. The original closed-form forecast is exact on 9,545 and has one counterexample. The record checks 254,253 finite acyclic models and registers a symbolic topological-induction proof.

For the counterexample, the exact retraction is

- `ORIGINAL_CLOSED_FORM_EXACTNESS`;
- `ORIGINAL_REGIME_LABEL`.

The following independent or repaired claims remain authorized under their own proof trees:

- `F2_EXACTNESS`;
- `FEASIBLE_UPPER_BOUND`;
- `SUPPORT_TWO_SUFFICIENCY`;
- `REPAIRED_REGIME_LABEL`.

The QG5B repair is explicitly post-outcome. It is not promoted to prospective confirmation. In proof-tree language, the failed forecast trees are deleted, while theorem-supported and post-outcome repair trees survive with their own intersections. Untyped reachability alone cannot express this distinction.

This application remains bound to the registered ORION record and is not generalized to unregistered scientific systems.

## 7. Algorithmic consequence

For an acyclic registered graph, the theorem can be evaluated without materializing all proof trees: the least-fixed-point dynamic program already unions the same intersections. Proof trees are explanatory and auditable witnesses, while the fixed point is the compact evaluator.

When many licenses share one syntactic projection, R5 signature compression evaluates that projection once. When a reviewer asks why one license survived, a single tree extracted during dynamic programming is a complete positive certificate. When a license retracts, the remaining task is a blocker statement over its license-specific proof trees; generic hitting-set complexity is donor material and is not a novelty claim here.

## 8. Verification

`papers/verify_five_math_extensions_r6.py` implements two independent semantics on finite acyclic fixtures:

1. least-fixed-point propagation of typed labels; and
2. explicit enumeration of proof-tree authority intersections.

They agree before and after direct refutation. The verifier also checks an untyped-reachable but authority-empty mixed-coordinate example and binds the QG5 application constants: 9,546 total rows, 9,545 exact rows, one error, two exact retractions, and 254,253 formally checked finite models.

## 9. Prior-art and novelty calibration

Proof trees, positive provenance, Horn closure, alternative derivations, and support/blocker reasoning are established subjects. The generic union-of-intersections formula is presented as the semantic normal form of the paper's typed cap calculus, not as a blanket novelty claim. The residual contribution is the no-promotion policy interpretation, license-coordinate retraction semantics, executable authority layer, and bound QG5 demonstration that post-outcome repair cannot restore prospective authority.

## 10. Atomic status

- Proof-tree intersection formula for finite acyclic registered systems: `VERIFIED`.
- Typed–untyped separation: `VERIFIED` constructively.
- Exact refutation by proof-tree deletion: `VERIFIED`.
- QG5 one-row counterexample and two-claim retraction: `BOUND` to the frozen authority record.
- QG5B prospective confirmation: `FALSE`; it remains post-outcome repair.
- Generic novelty of provenance, proof trees, hitting sets, or Horn evaluation: `NOT_CLAIMED`.
- Transfer to unregistered external systems or jurisdictions: `NOT_CLAIMED`.

## 11. Remaining scientific frontier

The formal core and one nontrivial ORION application are now integrated. The next valuable step is external validity: encode one independently governed evidence policy—such as preregistered versus post-outcome evidence or jurisdiction-specific data-use authority—and test whether an untyped system produces a decision that the policy rejects. Additional generic Horn lemmas would add less value than that bound external case.
