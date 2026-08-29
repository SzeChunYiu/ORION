# Closure-Carrying Scientific Navigation Across Regime Change

## Abstract

Scientific workflows increasingly reuse planning, abstraction, representation migration and replanning mechanisms across changes in data representation, responsibility and objective. Local validity of each transformation does not guarantee that a previously closed scientific task remains closed after the transformation. We formalize **closure-carrying navigation**: each transformation preserves its native operation while carrying an explicit contract describing the scientific obligations required at its source and guaranteed at its target.

For arbitrary finite chains of heterogeneous transformations, closure composition is sound when every intermediate hand-off is supported by an exact contract or registered equivalence bridge. Mechanization also reveals that a simple equality-of-contract rule is sufficient but not semantically necessary. The exact semantic condition is containment: the obligations demanded by the next transformation must be contained in those guaranteed by the previous one. When the decision layer is intentionally restricted to opaque contract identities and a bridge registry, registry connectivity becomes the unique maximal sound licensing rule available at that evidence boundary. This separates semantic necessity from what can be licensed using incomplete administrative information.

We complement the formal analysis with bounded non-synthetic regime changes. Witness-aware transport achieves exact finite conformance on a public RO-Crate version transition, 712 protected Wine-classification responsibility changes and ten protected breast-cancer objective/obligation cells, while value-only transport produces false closures and unconditional reopening produces unnecessary work. A separate sealed-label synthetic-grounded campaign covers 432 navigation decisions across six domains and confirms the registered law under independently implemented custody and checking, but it is not naturalistic deployment evidence.

The contribution is a compositional closure interface above existing navigation mechanisms. It does not claim universal regime transport, deployed-agent superiority or that contract equality is the exact semantic law.

## 1. Introduction

Scientific work rarely remains in one regime. A representation is migrated, a dataset is relabeled, a responsibility changes from prediction to verification, an evaluation metric changes or a previously sufficient evidence source becomes inadequate for a new objective.

Many mature mechanisms handle these transformations locally. Planning abstraction can refine a state space. Counterexample-guided methods can reopen a failed abstraction. Migration systems can translate representations. Replanning can respond to a changed world model. These operations answer whether the transformation itself is valid. They do not automatically answer whether the scientific task that was previously considered complete remains complete afterward.

We study this second question. A transformation is **closure-carrying** when it exposes the scientific obligations it requires before the change and the obligations it guarantees afterward. Navigation is licensed only when these contracts compose.

This view deliberately treats existing planning and migration methods as reusable donors. The proposed contribution is not another planning algorithm. It is a contract for transporting scientific closure through otherwise valid transformations.

## 2. Source and target obligation contracts

A scientific transformation has two layers.

The native layer describes what the transformation does: migrate a representation, refine a plan, alter an objective or change a responsibility. The closure layer describes the obligations that must hold for the scientific task to remain justified.

Each transformation therefore has a source obligation contract and a target obligation contract. The source contract states what closure information the transformation assumes. The target contract states what it preserves or establishes.

This makes a critical failure visible. Two transformations can each be locally valid while their composition is scientifically invalid because the first does not guarantee an obligation required by the second.

## 3. Arbitrary-chain composition

For two transformations, a sufficient rule is straightforward: if the first target contract exactly matches the second source contract, or if a registered equivalence bridge establishes that match, closure can compose.

The mechanized calculus extends this result to arbitrary finite chains, arbitrary numbers of transformations and obligations, and arbitrary donor-native validity predicates. Composition does not depend on one special five-step pipeline.

The theorem preserves donor validity. If a leg fails its own native predicate, the closure calculus does not repair it. The result concerns what follows when locally valid transformations are connected through scientific obligations.

This arbitrary-chain result is stronger than finite pair enumeration. The proof is over uninterpreted sorts and therefore does not rely on the identities of the specific transformation families used in the finite demonstrations.

## 4. Equality is sufficient but not the exact semantic condition

Mechanization exposes an important correction. Exact equality of intermediate contracts is sufficient for obligation-total composition, but it is not necessary.

Suppose the first transformation guarantees a set of obligations that is strictly richer than what the second transformation requires. The hand-off is semantically sound even though the contract identifiers do not match exactly.

The exact semantic condition is therefore **obligation containment**:

> every obligation demanded by the second leg must be supplied by the target contract of the first leg.

This means a strict equality rule is fail-closed but incomplete. Some refusals are conservative administrative refusals rather than genuine semantic failures.

Retaining this correction is central to the paper. A sound rule should not be promoted to an exact characterization merely because it has no observed false closures.

## 5. What can be licensed when obligations are hidden

Some systems do not expose the full semantic obligation sets. They expose only contract identities and a registry of approved bridges. At this evidence boundary, semantic containment cannot be inspected directly.

We therefore ask a different question: among rules that can use only opaque contract identities and the registered bridge table, what is the most permissive sound rule?

In the finite registered setting, the answer is connectivity in the undirected closure of the equivalence registry. Two contracts can be licensed when they lie in the same registered equivalence component. No more permissive opaque rule is sound on all states consistent with that registry.

This result should not be confused with semantic necessity. Registry connectivity is exact only relative to the information the opaque decision layer is allowed to see. If richer obligation semantics become available, containment remains the stronger scientific criterion.

The distinction separates two forms of incompleteness: genuine missing semantic evidence and administrative incompleteness in the registry.

## 6. Representation change: a public metadata transition

The first bounded real transition uses a public RO-Crate standard version change. Fourteen cases are frozen before scoring. Witness-aware closure transport classifies all cases correctly, including four where the available evidence is insufficient to license closure. A value-only rule achieves 0.429 accuracy and produces eight false closures. An always-reopen control achieves 0.286 and reopens six cases unnecessarily.

The case is finite and exact. It establishes the behavior of the transport rule on those fourteen transitions, not on arbitrary metadata standards.

## 7. Responsibility change: Wine classification

The second change class holds the representation fixed while changing the responsibility. A three-class Wine-recognition task is coarsened to a binary responsibility. Across 712 protected rows, witness-aware transport matches the registered closure law on every row and correctly leaves 238 cases unresolved by the available evidence.

The value-only comparator produces 238 false closures. Always reopening avoids false closure but unnecessarily reopens 474 rows.

This case demonstrates that preservation of a numerical value or prediction does not establish preservation of the scientific responsibility for which that value is being reused.

## 8. Objective and obligation change: breast-cancer classification

The third real change class holds the representation and responsibility fixed but changes the scientific obligation from an accuracy requirement to a malignant-class recall requirement after predictions are frozen.

Across five protected folds evaluated under two evidence states, witness-aware transport is correct in all ten cells. The value-only rule is correct in three and produces five false closures. Always reopening is correct in one and performs four unnecessary reopens.

The change is nontrivial in both directions: one fold satisfies the old accuracy obligation but fails the new recall obligation, while another fails the old obligation and satisfies the new one. A scalar summary of the old objective therefore cannot determine the new closure state.

## 9. Sealed-label stress test

A broader synthetic-grounded campaign evaluates 432 navigation decisions across six domains, nine transformation families and eight seeds. The labels are sealed before evaluation and reconstructed by separately implemented custody, evaluation and checking components.

The closure-aware navigator matches the sealed rule on all 432 cases, while donor comparators with restricted navigation envelopes fail on multiple terminal classes. Negative controls remain negative.

This campaign strengthens implementation and law-conformance evidence. It remains synthetic-grounded and does not substitute for a naturalistic multi-stage workflow. The distinction is retained explicitly because a large generated denominator is not the same as external deployment evidence.

## 10. What the combined result establishes

The paper supports a bounded compositional claim:

- local transformation validity and scientific closure are distinct;
- arbitrary finite chains can carry closure when intermediate obligations are properly connected;
- exact contract equality is a sound but incomplete rule;
- semantic obligation containment is the exact hand-off condition in the formal model;
- when only opaque registry information is available, the maximally permissive sound rule changes to registry connectivity;
- bounded real regime changes show that witness-aware transport can avoid both false closure and blanket reopening.

The ideal information-equivalent product should tie. The contribution is the closure contract, not a central architecture.

## 11. Limitations

The real-data studies are finite conformance tests, not population estimates. The sealed-label campaign is synthetic-grounded. No naturalistic multi-hop scientific pipeline has yet been evaluated under independent external custody. The formal calculus also depends on correctly specified obligation contracts; a wrong contract can transport the wrong notion of closure perfectly.

The paper does not claim universal completeness, universal minimality of its coordinates or deployed-agent superiority. It also does not claim that registry connectivity is semantically necessary when richer obligation information is available.

## 12. Reproducibility and availability

The final archive should contain the formal statements, mechanized proofs, finite countermodels, real transition manifests and independent reconstruction needed for every reported result. The anonymous submission should describe the scientific transformations and evidence contracts without exposing internal development identifiers.

## 13. Conclusion

Scientific navigation across regime change requires more than locally valid transformations. Closure must be carried through the obligations that connect one regime to the next. The formal analysis shows how this composition works for arbitrary finite chains and corrects an initially over-strict equality rule to the exact semantic containment condition. Bounded real transitions show why this distinction matters: value preservation alone can falsely close a changed task, while unconditional reopening can discard valid work. The current result is a compositional closure theory with finite real evidence, not yet a claim of general naturalistic deployment.