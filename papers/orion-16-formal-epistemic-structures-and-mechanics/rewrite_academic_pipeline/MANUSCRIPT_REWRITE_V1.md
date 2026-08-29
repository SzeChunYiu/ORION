# Conservative Certificate Lifting and Selective Revalidation under Scientific Change

## Abstract

AI and scientific workflow systems increasingly rely on execution certificates, provenance records, typed effects, authorization receipts and reproducible workflow traces. These objects can remain locally valid even after the scientific question, measurement semantics or inferential obligation changes. Recomputing every lower-level certificate after each change is wasteful, but reusing them without a scientific bridge can preserve evidence whose original conclusion is no longer licensed.

We formalize **conservative certificate lifting** as a layer between native certificate validity and continued scientific standing. Lower-level certificates retain their native verdicts. A scientific conclusion is preserved only when the claim-specific lift conditions required by the new state remain satisfied. In the registered finite model, revalidating the complete affected set of scientific lift coordinates is sufficient to restore the lifted conclusion, while every proper subset is insufficient. Exhaustive checking covers 31 distinct non-laundering product countermodels and, after accounting for repeated donor loops, all 31 nonempty affected-coordinate patterns and all 211 strict-subset failures per donor-independent model. A separate implementation reconstructs the finite result, and a fresh-kernel replay verifies the paper's commutation theorem for fully separated deterministic mechanics: independent execution orders agree on the scientific projection while retaining histories that differ only by swaps of independent events.

An ideal competing product enriched with exactly the same scientific coordinates and lifting rules ties extensionally. The contribution is therefore not a proprietary architecture or a claim that provenance and execution certificates are insufficient in their native domains. It is a formal repair law for reusing valid lower-level assurance without laundering it into unchanged scientific authority after material change. Real-system performance and universal minimality of the registered coordinates remain outside the current evidence.

## 1. Introduction

A scientific workflow can preserve many correct facts while its scientific interpretation changes. A program may have executed exactly as recorded. A dataset may retain an immutable provenance chain. A theorem prover may still validate the same proof object. Yet a conclusion that depended on an old measurement protocol, evidence standard, scientific question or epoch may no longer follow.

This creates a compositional problem for AI-assisted science. If every scientific change triggers a full reset, valid execution and provenance evidence is needlessly discarded. If nothing is reopened, local validity can be mistaken for continued scientific standing.

We separate two semantic layers:

- **native validity:** whether a certificate remains valid for the object and rules it directly certifies;
- **scientific lifting:** whether that locally valid certificate still supports the scientific conclusion currently being asked.

The proposed calculus is conservative in the first layer. Existing certificate systems keep their own verdicts. The new question is which scientific bridge coordinates must be revalidated after change.

## 2. Certificate lifting

A lower-level certificate is associated with its native object, content identity and validity predicate. Scientific use additionally depends on a lift relation that binds the certificate to the claim currently being made.

The registered model represents five types of scientific continuity: exact claim and content identity, measurement semantics, evidence semantics, inferential obligation and scientific epoch. These coordinates are not claimed to be a universal minimal ontology. They provide a finite model in which the distinction between local validity and scientific standing can be tested exactly.

If none of the required scientific coordinates changes, a valid native certificate can be reused. If some coordinates change, the certificate remains valid in its own theory, but the scientific lift becomes open until the affected coordinates are revalidated.

This gives a non-laundering principle:

> accumulating more lower-level certificates cannot discharge a missing scientific lift condition unless an explicit rule connects those certificates to the changed scientific obligation.

The principle does not say that additional evidence is never useful. It says that evidence must bear on the missing obligation rather than being counted as generic support.

## 3. Necessary-and-sufficient repair in the registered model

Let the affected set contain the scientific lift coordinates changed by the transition. Assume that native certificate validity survives on unchanged premises and that unaffected lift coordinates remain valid.

The repair law has two directions.

**Sufficiency.** Revalidating every affected scientific coordinate restores the lifted conclusion.

**Necessity.** For every proper subset of the affected set, there is an admissible state in the registered model in which the unrevalidated coordinate is precisely the one that breaks the lift. Therefore no strict subset is sound for all states represented by the model.

The finite checker evaluates every nonempty affected set and every strict subset. Across the donor-independent five-coordinate model there are 31 complete affected sets and 211 strict-subset choices. In the historical implementation these rows are repeated across five donor families, yielding 155 complete-revalidation successes and 1,055 strict-subset failures. The repeated counts should not be mistaken for independent evidence. The scientifically distinct facts are the affected-set and subset relations themselves.

The result is constructive: keep valid unaffected assurance and revalidate the complete affected scientific bridge, neither rebuilding everything nor trusting an incomplete repair.

## 4. Product accumulation cannot replace a missing bridge

A second exact study constructs product states in which several lower-level certificate mechanisms are simultaneously valid. Thirty-one distinct countermodels show that product accumulation alone does not create a missing scientific lift.

These countermodels address a tempting alternative explanation. Perhaps the apparent need for a scientific layer disappears once enough provenance, execution, authorization and workflow evidence is composed. The exact product cases show that this is not true in the registered semantics: if the changed scientific obligation is not represented, the product can remain locally valid while the target scientific conclusion is unsupported.

The conclusion is deliberately conditional. A competing product that is enriched with the same scientific coordinates and lift rules should no longer fail.

## 5. Equivalence with an enriched competing product

We explicitly test that control. An ideal product is given the same scientific state variables and lifting predicate. It matches the proposed semantics on every registered finite state.

This tie is important for interpretation. The paper does not argue that scientific lifting requires a centralized framework or a particular software architecture. The formal object is portable: any system that carries equivalent scientific fields and rules should make the same decision.

The contribution is therefore a semantic interface between native certificates and scientific claims, not an expressivity advantage of one implementation.

## 6. Independent mechanics and audit history

Scientific workflows also contain multiple mechanics that may execute in different orders. A naïve commutation theorem would require the entire state, including ordered audit history, to be identical after swapping independent actions. That statement is too strong because a correct audit log should remember execution order.

The corrected theorem separates the current scientific projection from history. For deterministic admissible mechanics with disjoint writes, reciprocal read exclusions and full scientific noninterference, the scientific projection is identical under either order. The histories need only be equivalent up to swapping adjacent independent events.

A serialized kernel proof replays this theorem from primitive rules, and a separate solver check refutes the negation under the translated assumptions. Removing either cross-read exclusion admits a countermodel.

This result clarifies what concurrency can preserve: the present scientific state may commute even when chronology remains observably different and audit-relevant.

## 7. Relation to existing systems

Proof of execution, certified traces, workflow provenance, proof-carrying actions, authorization, effect typing, truth-maintenance systems and dependency-directed repair are established mechanisms. This paper treats them as donor infrastructure.

The residual problem appears one level above their native judgments. A workflow certificate can remain valid while the scientific claim that used it changes meaning. A provenance graph can correctly identify an artifact while the evidence standard for a new question has changed. Selective revalidation therefore concerns the **claim-specific scientific bridge**, not reinvention of the lower-level mechanisms.

The ideal-product tie makes this boundary explicit. If an existing system is extended with the same scientific semantics, the paper predicts equivalence rather than superiority.

## 8. What the current evidence does not establish

The finite model does not prove that the five registered scientific coordinates are universally minimal. It also does not establish deployed-agent performance or cost savings in independently maintained systems. The independent implementation and kernel replay are internal programme replications rather than external custodianship.

Real dependency graphs can also be incomplete or conservative. A broader successor studies how graph quality affects safety and extra work, but such results should enter the manuscript only after they are merged, independently bound and reviewed under the same claim discipline.

The present paper therefore remains a formal certificate-lifting and repair result.

## 9. Reproducibility and availability

The final submission should provide the formal definitions, complete finite-state generator, distinct countermodels, independent reconstruction, kernel proof and mutation controls in a versioned archive. The manuscript should report distinct scientific configurations rather than inflated loop counts and should identify the trusted computing base of the mechanized proof.

## 10. Conclusion

Scientific change should not force a choice between discarding all prior assurance and blindly carrying it forward. Conservative certificate lifting preserves native validity while reopening only the scientific bridge whose assumptions changed. In the registered model, complete affected-coordinate revalidation is sufficient and every strict subset is unsound; product accumulation cannot replace a missing bridge; and an information-equivalent enriched product ties exactly. The result is a bounded formal repair law for dynamic scientific computation, not a universal claim about certificate systems or deployed agents.