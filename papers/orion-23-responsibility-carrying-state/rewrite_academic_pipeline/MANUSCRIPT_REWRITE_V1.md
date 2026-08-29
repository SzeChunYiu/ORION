# Responsibility-Relative State Reuse and Three-Valued Certificate Transport

## Abstract

A state representation that is sufficient for one scientific responsibility can be unsafe to reuse for another. Provenance and freshness do not resolve this problem: a record can be current and correctly sourced while omitting information required by the new responsibility. We study **responsibility-relative reuse** through formal transport rules and bounded real/verifier-backed experiments.

On 17,970 handwritten-digit episodes, a compact state learned for a parity responsibility preserves the accuracy of an always-raw baseline when the responsibility alternates between parity and exact-digit decisions while reading 48.44% fewer raw features. Confidence-only and provenance-only reuse fail when the stronger responsibility is unsupported. In a disjoint verifier-backed CNF study, responsibility-aware reuse is correct on all 24 old/new-responsibility episodes and reduces raw literal reads by 44.44% relative to always reading the full state, while confidence-only and provenance-only rules are correct on 12 of 24. A stronger provenance-tiered donor comparison over 48 frozen CNF episodes is correct on 36 of 48 and makes 12 unsupported reuses after responsibility change; the responsibility-aware rule is correct on all 48 with no unsupported reuse. In a separate 60-case drift study, conditional certificate transport is correct in all cases with no unsound transport or needless re-issue, whereas unconditional transport is unsound in 40 cases and signature-only transport performs 20 needless re-issues.

We further prove a three-valued premise-support law for certificate transport. Each load-bearing premise is classified as established, contradicted or unknown. Reuse is licensed only when every premise remains established; contradiction invalidates the old certificate; unknown evidence must remain unresolved. Exhaustive verification over 750 premise-status cases shows the trade-off exactly: treating unknown as established causes 212 unsound reuses, while treating unknown as contradiction causes 84 unnecessary revocations. The three-valued rule is the only tested rule with neither error, at the cost of leaving 296 decisions unresolved.

The contribution is a bounded theory and evaluation of responsibility-relative state reuse, not a universal guarantee for arbitrary semantic drift or deployed research agents.

## 1. Introduction

State is often evaluated by asking whether it retains enough information to perform a task. Scientific workflows pose a more specific question: enough information **for which responsibility?**

A compact representation may be sufficient to classify parity but not an exact digit. A proof certificate may remain valid for the formula against which it was issued but not after the formula or claim changes. A provenance record may be fully current while the question asked of the record becomes stronger.

These examples motivate a responsibility-relative view of sufficiency. A state is not simply sufficient or insufficient. It supports a set of scientific responsibilities under a particular evidence and epoch contract.

This paper studies two linked problems:

1. when can a compact state be reused without reopening raw information after the responsibility changes?
2. when can a certificate be transported after its load-bearing premises become established, contradicted or unknown in the new state?

The first problem is empirical and resource-sensitive. The second yields a sharp three-valued transport law.

## 2. Responsibility-relative support

Let a state be associated with a scientific responsibility such as prediction, exact identification, verification or repair. Reuse is licensed only when the state contains the information required by the current responsibility and the supporting evidence remains applicable.

This distinction is stronger than provenance. Provenance answers whether a state came from the expected source or version. Responsibility support asks whether that state is adequate for the decision now being made.

The two coordinates can diverge. A compact state can be perfectly current for yesterday's question and structurally insufficient for today's.

A responsibility-carrying state therefore records not only its content but also the responsibilities it supports, the conditions under which support is revoked and whether raw recovery is available.

## 3. Real-data responsibility shift

The first study uses handwritten digits. A compact state is constructed for a parity responsibility and is later confronted with a stronger exact-digit responsibility.

Across 17,970 episodes, the responsibility-aware method matches the always-raw accuracy on both responsibilities while reading 33 features per episode instead of 64, a 48.44% reduction in raw-state access. The method reopens raw state when the compact representation does not support the stronger responsibility and never reuses that unsupported state for exact-digit decisions.

The primary controls show why ordinary confidence and provenance are insufficient. A confidence-only rule reuses unsupported compact state frequently and obtains exact-digit accuracy of approximately 0.396. Provenance-only and unqualified reuse remain current but structurally inadequate for the stronger question, with exact-digit accuracy of approximately 0.238.

The result does not imply that compact state is always preferable. It shows that a representation can be adequate for one responsibility and inadequate for a stronger one despite high confidence and current provenance.

## 4. Verifier-backed semantic and epoch shift

A second study uses CNF formulas with exact mechanical verification. Each base formula has two satisfying models. A previously verified model is valid for the original responsibility. A new clause changes the formula and leaves exactly one alternate satisfying model, making the old certificate stale for the changed responsibility.

Across 24 old/new-responsibility episodes, responsibility-aware reuse and always-raw evaluation are both verifier-correct on all 24. The responsibility-aware method reads 60 raw literals compared with 108 for always raw, a 44.44% reduction. Confidence-only and provenance-only rules are correct on 12 of 24 and reuse the old certificate in the 12 changed cases where it is no longer supported.

This study gives the reuse contract an exact semantic anchor. The old certificate is demonstrably valid before the clause change and demonstrably invalid afterward.

## 5. A strong provenance-tiered donor is still not responsibility support

To test whether the result disappears once provenance is made substantially stronger, a donor family is given graded provenance and freshness information over 48 frozen CNF episodes.

The two strongest donor variants are correct on 36 of 48 cases. Each makes 12 unsupported reuses when the responsibility changes despite the record remaining current. Responsibility-aware reuse is correct on all 48 with no unsupported reuse. A composed responsibility-aware variant also remains exact and reduces mean literal reads to 5.0 compared with 6.25 for the strongest donor.

The result is not that provenance is unhelpful. Provenance and responsibility answer different questions. A record can be authentic and current while failing to support the new scientific obligation.

## 6. Certificate transport under drift

State reuse also requires a rule for deciding whether an old certificate survives a change. The 60-case drift study separates redundant, conflicting and mixed changes.

A conditional transport rule is correct on all 60 cases, with no unsound transport and no unnecessary re-issue. Unconditional transport is unsound in 40 cases because it carries certificates across conflicting drift. A signature-only rule performs 20 unnecessary re-issues on redundant changes. Always re-issuing is safe but more expensive in the redundant stratum.

This result demonstrates that certificate preservation should depend on what changed, not merely on the presence of a new signature or epoch label.

## 7. Load-bearing premises require three-valued transport

We next formalize transport directly. A certificate depends on a finite set of load-bearing premises. After change, each premise can be in one of three scientific states:

- **established:** the premise is unchanged or entailed in the new state;
- **contradicted:** the premise is false in the new state;
- **unknown:** the available evidence establishes neither truth nor falsity.

These states license different actions.

If every premise remains established, the old derivation can be replayed and the certificate may be reused. If any load-bearing premise is contradicted, the old certificate cannot be reused. Checking unrelated premises cannot repair a derivation whose hypothesis is false. If no premise is contradicted but at least one is unknown, neither reuse nor revocation is licensed by the available evidence. The correct scientific disposition is unresolved pending further evidence.

The third case is essential. Unknown is not a bias that can be collapsed safely into true or false.

## 8. No two-valued collapse is both sound and non-wasteful

The theorem is tested exhaustively over 750 cases covering every status assignment on three- and four-premise certificates, with hidden actual values supplied for unknown premises so that unnecessary revocation is meaningfully testable.

The three-valued rule produces no unsound reuse and no unnecessary revocation, leaving 296 cases unresolved because the target is not determined by the visible evidence.

An optimistic two-valued collapse treats unknown as established. It never over-revokes but performs 212 unsound reuses. A pessimistic collapse treats unknown as contradiction. It is sound but performs 84 unnecessary revocations.

The trade-off is exact in the tested domain:

> optimistic collapse is cheaper but unsafe; pessimistic collapse is safe but wasteful; explicit unknown preserves both soundness and non-waste at the cost of abstaining where the evidence is insufficient.

An initial implementation of this test incorrectly defined unknown to be unsound by construction, which would have made pessimistic revocation vacuously correct. A planted control exposed that defect before the result was accepted. The corrected evaluation resolves each unknown premise both ways behind the decision boundary, preserving the intended scientific meaning of uncertainty.

## 9. What the combined evidence establishes

The real-data and verifier studies show that state sufficiency is responsibility-relative in two qualitatively distinct domains. The donor comparison shows that provenance currency does not imply responsibility support. The drift study shows that certificate reuse can be selective rather than unconditional or blanket-conservative. The premise-support theorem explains the shared mechanism: scientific reuse depends on whether every load-bearing premise remains established, contradicted or unresolved.

The evidence does not support a universal ladder of scientific responsibilities or arbitrary semantic transport. Responsibilities can be partially ordered or incomparable. The current experiments cover specific classification and verifier-backed obligations rather than open-ended research-agent workflows.

## 10. External lifecycle boundary

A broader public-repository lifecycle corpus exists, but its outcomes were accessed before the present transport theorem was finalized. It is therefore not used as prospective confirmation of the theorem. Moreover, some facts required by the frozen contract remain unavailable because the exact runtime observation specified by the contract does not exist for those repositories.

Those cases illustrate the unknown state of the theorem but do not cross the external-evidence boundary. A future external study must be prospectively frozen on new, disjoint authority before it can promote the claim.

## 11. Relation to state, provenance and certified reuse

Persistent memory, provenance, proof-carrying state and stale-state handling are established areas. The paper does not claim those primitives as new. Its residual object is the responsibility relation: which question a state supports, when support must be reopened and how certificate transport should behave when a load-bearing premise is established, contradicted or unknown.

An information-equivalent competing product that represents the same responsibility support should tie.

## 12. Limitations

The studies are bounded and task-specific. The digits experiment shares a public dataset with other analyses, although the episodes and endpoints here are separately defined. The CNF worlds provide exact verification but are not a proxy for arbitrary scientific reasoning. The three-valued theorem assumes that the load-bearing premise set is correctly specified; omitted premises can invalidate transport even if the rule is applied perfectly.

No deployed safety-critical authority or universal research-agent performance is claimed.

## 13. Reproducibility and availability

The anonymous submission should archive the frozen episode definitions, verifier-backed cases, donor contracts, drift study, transport-law checker and independent reconstruction. The adverse instrument defect and its correction should remain in the audit record because it demonstrates why non-vacuous hostile controls matter.

## 14. Conclusion

Scientific state reuse depends on the responsibility being asked of the state, not only on whether the state is current or well provenanced. Across real digits and exact CNF settings, responsibility-aware reuse preserves correctness while avoiding unnecessary raw recovery. The three-valued transport law provides the corresponding certificate rule: reuse when every load-bearing premise is established, revoke when one is contradicted, and remain unresolved when the evidence leaves a premise unknown. Collapsing that third state is either unsafe or wasteful.