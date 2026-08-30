# Scientific Authorization Beyond Action Authorization

## Abstract

AI systems can be authorized to execute an action without possessing the evidence needed to justify the scientific conclusion that motivates that action. We formalize this distinction through a typed scientific-authorization calculus that composes local permission, provenance and evidence records without allowing them to amplify into unsupported scientific authority. The calculus enforces domain, scope and epoch confinement; preserves unresolved hard obligations; supports explicit protected coercions; and models revocation through alternative support families rather than treating one revoked source as automatic global falsification.

The general composition laws are mechanized over uninterpreted domains and interpreted for finite donor chains. This interpretation corrects an earlier breadth claim: a historical enumeration of 169 successful donor-pair compositions repeats one reflexive composition across donor names and is not evidence of 169 heterogeneous scientific chains. A stronger exact study reduces 3,072 states to 192 verdict classes and checks 36,864 representative pairs corresponding to 9,437,184 state pairs. No unsound composed pair is found, every widening hop blocks, and deliberately incorrect composition operators change the soundness count.

A separate bounded evidence study contains 20 frozen cases spanning empirical, formal, multiple-support and systems settings. The scientific-discharge rule matches the registered gold on all 20 cases, produces no false scientific promotions, distinguishes 12 cases in which action permission and scientific authorization diverge, and preserves conclusions supported by an independent derivation after partial revocation. The gold and calculus are nevertheless produced within the same research programme, so this result is specification-conformance evidence rather than independent external adjudication.

The contribution is a higher scientific-discharge layer above donor-owned authorization and provenance mechanisms. External scientific authority and comparison with a real integrated authorization/evidence system remain necessary for a broader empirical claim.

## 1. Introduction

Modern AI agents operate under increasingly sophisticated authorization systems. Permissions can depend on user identity, tool scope, provenance, delegation, context freshness, policy and evidence. These controls answer whether an action may be taken.

Scientific work adds a different question: **does the available evidence authorize the scientific commitment implied by that action?**

An agent may be permitted to publish a file, run an experiment, update a database or execute a remediation while still lacking evidence that a scientific claim is established. Conversely, a scientific claim may remain supported even after one source or execution path is revoked if an independent derivation survives.

Conflating these layers creates authority laundering. Local permission, successful execution or high confidence can be transformed into a stronger scientific conclusion without an explicit rule that justifies the transformation.

We therefore model action authorization and scientific discharge as distinct relations. Generic authorization systems remain intact. The scientific layer consumes their outputs but cannot rewrite them.

## 2. Scientific discharge as a typed relation

A scientific commitment is associated with an object, content identity, scope, epoch and set of evidence obligations. Evidence and local authorization records may discharge some of these obligations. A commitment is authorized only when at least one complete support family satisfies the required type and authority conditions.

This model has three important consequences.

First, action permission is neither necessary nor sufficient by itself for scientific discharge. Second, missing type information can leave a scientific decision unresolved rather than forcing automatic denial or promotion. Third, revocation operates on support families: removing one premise eliminates only the derivations that depend on it.

These properties are not intended to replace authorization logics, provenance standards or evidence ledgers. They specify how those lower-level objects can be used to support a higher scientific decision.

## 3. Non-amplifying composition

Consider a chain of locally authorized evidence or delegation steps. A scientific composition is sound only when each step remains within the domain, scope and epoch allowed by the root authority or passes through an explicit protected coercion.

The mechanized calculus proves non-amplification and confinement over arbitrary finite chains. Composition cannot mint a wider scientific scope merely because each local hop is individually permitted.

The formal interpretation is important because a locally meaningful donor record may use a different type system from the scientific layer. The bridge theorem shows when the donor hop entails the hypotheses required by the general calculus rather than assuming that all authorization objects already share one ontology.

## 4. Correcting a misleading multiplicity count

An earlier finite artifact reports 169 successful ordered donor-pair compositions and 169 widening countermodels. That number initially appeared to suggest broad heterogeneous composition evidence.

Mechanized re-analysis shows otherwise. The enumeration iterates over thirteen donor names, but the composition body does not depend on those names. All 169 successful rows therefore reduce to one distinct clean reflexive state under the shipped interpretation. Several intentionally wrong composition operators reproduce the same 169 success count.

This correction changes the evidentiary role of the old result. The rows remain part of the historical record, but the pair count is not used as breadth evidence.

A stronger exact composition test is therefore required.

## 5. Exact composition stress test

The revised study constructs an exact reduced state space. A total of 3,072 states collapse to 192 verdict classes under the equivalences relevant to the composition decision. The checker evaluates 36,864 representative pairs, which stand for 9,437,184 state pairs.

No unsound composition is observed. Every scope-widening hop blocks. Both successful discharge and refusal states are exercised. Nine discharging representatives produce 81 discharging composed pairs.

The key hostile control is mutation sensitivity. Deliberately wrong composition operators change the soundness count, unlike the historical multiplicity statistic. This shows that the new endpoint measures the composition law itself rather than the number of donor labels in an outer loop.

The result is still formal and finite. It is not evidence of deployed-agent behavior.

## 6. Action permission and scientific authorization can diverge

The bounded real-evidence study freezes 20 cases across empirical, formal, multiple-support and systems settings. Twelve cases are constructed so that the local action-authorization facts are compatible with an action while the scientific-discharge decision differs because the scientific evidence obligations differ.

The discharge rule matches the registered target on all 20 cases and produces no false scientific promotions. Cases with missing scientific typing remain unresolved rather than being silently converted into a positive or negative scientific conclusion.

The result demonstrates the intended separation in heterogeneous finite cases. It does not show that the target labels are independently correct, because the labels were produced within the same research programme as the calculus.

## 7. Revocation should remove derivations, not facts by association

Scientific evidence can have multiple independent support paths. If a source is revoked, only support families containing that source should be removed. A conclusion remains supported while at least one complete independent family survives.

The bounded study includes both partial and complete revocation. Revoking one source preserves a conclusion supported by an independent derivation; revoking all registered supporting sources blocks the conclusion.

This prevents two opposite errors. One source revocation should not erase unrelated evidence, and surviving confidence should not rescue a conclusion after every registered support family has been broken.

## 8. Protected coercion and indeterminate cases

Scientific domains often require translation across types: a local verifier output may need to be interpreted as evidence for a broader scientific obligation. Such a coercion is not assumed merely because the values look compatible.

The calculus requires the full intermediate type to match or an explicitly protected coercion to establish the bridge. Missing or ambiguous coercion leaves the decision unresolved. High confidence does not repair a hard type mismatch.

This rule makes uncertainty semantically different from denial. New evidence or a valid bridge can later resolve the case.

## 9. Relation to authorization, provenance and governance systems

Capability control, delegation, revocation, provenance, evidence-backed permission, effect typing and freshness checks are mature mechanisms. The paper does not claim them as new.

The residual scientific object lies above them. It asks which typed evidence authorizes a scientific commitment, how that authority narrows across composition, and how support survives or disappears under revocation.

A sufficiently enriched competing authorization product should tie the calculus. If the same scientific obligations and coercion rules are represented natively in another system, the contribution becomes a formal interpretation or equivalence result rather than empirical superiority.

## 10. Evidence boundary

The strongest current limitation is independence of scientific gold. The 20-case study is implemented with a separate checker, but the target labels and the calculus belong to the same research programme. Agreement is therefore internal specification consistency, not external scientific adjudication.

A broader empirical claim requires at least three real scientific-decision domains with independently governed outcome authority, along with a strong integrated authorization/evidence baseline receiving the same information. The evaluation must report both false scientific promotion and over-abstention so that a system cannot appear safe by refusing every uncertain claim.

## 11. Reproducibility and availability

The final submission should archive the formal calculus, interpretation proof, reduced composition state space, mutation controls and the 20-case study with its independent implementation. The manuscript should state explicitly that the historical donor-pair count is multiplicity rather than breadth evidence. Development identifiers and repository chronology should remain outside the reader-facing narrative.

## 12. Conclusion

Permission to act and authority to make a scientific commitment are different decisions. The proposed calculus preserves local authorization while requiring typed scientific obligations to be discharged explicitly, prevents scope amplification across composition and handles revocation through alternative support families. Mechanized and exact finite results support the formal semantics, and a 20-case study demonstrates the intended action/science separation. The current evidence is bounded by same-programme gold; independent external adjudication is the decisive next step for a broader claim.