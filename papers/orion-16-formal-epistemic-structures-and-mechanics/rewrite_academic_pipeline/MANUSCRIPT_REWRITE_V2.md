# Conservative Certificate Lifting under Scientific Change

## Abstract

Scientific and AI workflows increasingly reuse execution certificates, provenance records, typed effects, authorization receipts, and reproducible traces across multiple stages of reasoning. A lower-level certificate can remain valid even when the scientific question, measurement semantics, or inferential obligation changes. Recomputing every certificate after every change discards valid assurance; reusing all certificates unchanged can preserve a scientific conclusion whose original support no longer applies.

We formalize **conservative certificate lifting** as a semantic layer between native certificate validity and continued scientific standing. Native certificates keep their own verdicts. A scientific conclusion is carried forward only when the claim-specific lift conditions required by the new scientific state remain satisfied. In a registered five-coordinate finite model, revalidating the complete affected set of scientific lift coordinates is sufficient to restore the lifted conclusion, while every proper subset is unsound for at least one admissible state. The checker covers all 31 nonempty affected-coordinate patterns and all 211 strict-subset failures in the donor-independent model. Historical loops repeat these patterns across five donor families; those repetitions are not treated as independent evidence. A separate implementation reconstructs the finite result.

We also prove a commutation result for fully separated deterministic mechanics. Under disjoint writes, reciprocal read exclusions, and scientific noninterference, independent execution orders yield the same current scientific projection while their audit histories may differ by swaps of independent events. A fresh-kernel replay verifies the theorem and mutation controls show that removing either cross-read exclusion admits a countermodel.

An ideal competing system enriched with exactly the same scientific coordinates and lift rules ties extensionally. The contribution is therefore a portable repair law for reusing valid lower-level assurance without laundering it into unchanged scientific authority after material change. The registered coordinates are not claimed to be universally minimal, and deployed-system cost savings or external validation remain open.

## 1. Introduction

Scientific workflows preserve many locally valid objects across time. A program can still have executed exactly as recorded. A theorem prover can still accept the same proof object. A data artifact can retain its provenance. An authorization receipt can still describe a valid past action. Yet the scientific conclusion that once depended on those objects may cease to follow after the question, measurement meaning, evidence standard, or inferential obligation changes.

This creates a selective-revalidation problem. Two extreme policies are both unsatisfactory:

- **reset everything:** recompute or discard all prior assurance after any material scientific change;
- **reuse everything:** carry forward every locally valid certificate without checking whether the scientific bridge from certificate to current claim still holds.

We separate the problem into two semantic layers. **Native validity** asks whether a certificate remains valid in the theory or system that issued it. **Scientific lifting** asks whether that native verdict still supports the scientific conclusion currently under consideration.

The paper's central result is a repair law: preserve unaffected native assurance, identify which claim-specific lift coordinates changed, and revalidate the complete affected scientific bridge. In the registered finite model, that repair is sufficient and no strict subset is uniformly sound.

## 2. Native validity and scientific lifting

A lower-level certificate is associated with its own object identity, premises, and validity predicate. Scientific use adds another relation: the certificate is being used to support a particular claim under a particular scientific interpretation.

The registered model represents five forms of continuity relevant to this bridge: exact claim/content identity, measurement semantics, evidence semantics, inferential obligation, and scientific epoch. These coordinates are a finite study model, not a proposed universal ontology.

If none of the required scientific coordinates changes, a valid native certificate can remain lifted. If some coordinates change, the native certificate need not be revoked. Instead, the scientific lift becomes open on exactly the affected bridge coordinates.

This yields a non-laundering principle:

> Additional lower-level certificates cannot discharge a missing scientific lift condition unless an explicit rule connects their native judgments to the changed scientific obligation.

The principle is conservative toward existing assurance systems. It does not weaken what they certify; it prevents their verdicts from silently acquiring a broader scientific meaning.

## 3. Selective repair law in the registered finite model

Let \(A\) be the set of scientific lift coordinates changed by a transition. Assume that native validity survives on unchanged premises and unaffected lift coordinates remain valid.

The repair law has two directions.

### Sufficiency

Revalidating every coordinate in \(A\) restores the lifted scientific conclusion.

### Necessity within the registered model

For every proper subset \(B\subset A\), there exists an admissible model state in which a coordinate in \(A\setminus B\) is precisely the missing condition that breaks the lift. Therefore no strict subset of the affected set is sound for every registered state.

With five coordinates, there are 31 nonempty affected sets. Enumerating every strict subset gives 211 incomplete repair choices. The donor-independent checker verifies all 31 complete repairs and rejects all 211 strict-subset alternatives through explicit countermodels.

A historical implementation evaluates the same patterns inside five donor families, yielding 155 complete successes and 1,055 strict-subset failures. These counts are repeated realizations of the same scientific configurations and are not presented as 1,210 independent observations.

## 4. Product accumulation does not create a missing scientific bridge

A natural alternative is that the apparent need for a scientific lifting layer disappears once enough lower-level assurance mechanisms are combined. We therefore construct product states in which provenance, execution, authorization, and related native certificates are simultaneously valid.

Thirty-one distinct non-laundering countermodels show that product accumulation alone does not restore a scientific bridge whose changed obligation is absent from the representation. The lower-level product can remain fully valid in its native semantics while the current scientific conclusion is unsupported.

This is not a claim that product assurance is weak. The missing object is different: a relation from locally valid evidence to the present claim.

## 5. Information-equivalent implementations tie

To test whether the result depends on a particular architecture, an ideal competing product is enriched with the same scientific coordinates and the same lift predicate. It agrees with the proposed semantics on every registered finite state.

This tie is a required control. It shows that conservative lifting is not an expressivity advantage of a centralized system. Any implementation that preserves equivalent scientific state and applies equivalent repair rules should make the same lifting decision.

The contribution is therefore semantic and portable: a boundary between native certificate validity and current claim standing.

## 6. Commutation of independent scientific mechanics

Scientific systems also execute multiple mechanics whose order can vary. A naïve commutation theorem might require the entire state, including ordered audit history, to be identical after swapping independent actions. That is too strong because a correct audit log should preserve chronology.

We instead distinguish the current scientific projection from history. For deterministic admissible mechanics with disjoint writes, reciprocal read exclusions, and full scientific noninterference, executing the mechanics in either order produces the same current scientific projection. Histories are equivalent only up to swaps of adjacent independent events.

A serialized kernel derivation replays this theorem from primitive rules. A separate solver check refutes the negation under the translated assumptions. Mutation controls are informative: removing either cross-read exclusion admits a countermodel, showing that the theorem depends on genuine separation rather than on notation.

This result clarifies what can commute in an auditable scientific system. Current scientific meaning may be order-invariant even when the execution record correctly remains order-sensitive.

## 7. Why the repair is selective rather than global

The practical appeal of certificate lifting is not that it guarantees a performance gain. No such deployed-system claim is made. Its conceptual advantage is more basic: it distinguishes unaffected assurance from the scientific assumptions invalidated by a change.

A full reset is always safe only if discarding valid prior evidence is acceptable. Blind reuse is efficient only by ignoring the possibility that the target claim changed. Selective repair occupies the middle ground: keep what remains valid, reopen what the scientific transition actually made uncertain, and require an explicit bridge before a prior certificate supports the new claim.

The finite necessity result prevents the selective policy from becoming arbitrary. Within the registered model, every affected coordinate matters in at least one admissible state.

## 8. Relation to prior assurance and dependency mechanisms

Proof-carrying actions, certified execution, workflow provenance, authorization, effect systems, truth-maintenance systems, dependency-directed recomputation, and selective invalidation are established mechanisms. They solve important native problems and are treated as donor infrastructure here.

The residual question arises when a certificate remains locally valid but the scientific interpretation of what it is being used to support has changed. Conservative lifting adds a claim-specific scientific bridge above native verdicts; it does not replace the mechanisms that generated those verdicts.

## 9. Limitations

The five-coordinate model is finite and deliberately explicit. The current evidence does not prove that those coordinates are universally necessary, sufficient, independent, or minimal. Real systems may require different scientific state or may conservatively reopen more than the finite model predicts.

The independent implementation and fresh-kernel replay are same-programme replications, not external custodianship. The manuscript also does not establish wall-clock savings, reduced scientific error, or superior deployed-agent performance. A broader successor can test those consequences only with independently maintained systems and version-bound release evidence.

The commutation theorem applies to fully separated deterministic mechanics under its stated noninterference assumptions. It should not be generalized to shared-state, stochastic, or partially observed actions without new proof obligations.

## 10. Reproducibility and availability

The release package should include the formal definitions, finite-state generator, all 31 distinct affected-set cases, strict-subset countermodels, independent reconstruction, kernel proof, solver check, and mutation controls. Repeated donor loops should be documented as implementation coverage while the manuscript reports the distinct scientific configurations.

The trusted computing base of the mechanized checks should be identified explicitly. For the AIJ submission, reviewer-facing prose should describe the scientific semantics rather than repository-internal module or test names.

## 11. Conclusion

Scientific change should not force a choice between discarding every prior certificate and carrying every certificate forward unchanged. Conservative certificate lifting preserves native validity while reopening the claim-specific scientific bridge affected by change. In the registered finite model, revalidating the complete affected set is sufficient and every strict subset is unsound; accumulating unrelated native assurance cannot replace the missing bridge; and an information-equivalent implementation ties exactly. The result is a bounded formal repair law for dynamic scientific computation, not a universal ontology or a deployed performance claim.