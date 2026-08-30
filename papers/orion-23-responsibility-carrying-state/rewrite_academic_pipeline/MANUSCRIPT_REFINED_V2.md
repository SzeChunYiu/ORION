# Unresolved Premises Require a Third Outcome for Safe State Reuse

## Abstract

A compiled state can be correct when created and unsafe when reused after its premises change. We formalize reuse as a responsibility-relative decision. A retained state is sufficient only when every source world compatible with that state requires the same action for the current responsibility. A certificate records the premises, scope, evidence identity, epoch, and reopening conditions needed to preserve that sufficiency.

The central transport result concerns unresolved premises. Exhaustive enumeration of 750 registered worlds over three- and four-premise responsibilities compares three rules. A three-valued policy reuses only when all premises remain supported, reopens when any premise is contradicted, and abstains when at least one premise is unresolved and none is contradicted. It produces zero unsound reuse and zero unnecessary revocation. Treating unresolved as contradicted causes 84 unnecessary revocations. Treating unresolved as unchanged causes 212 unsound reuses. Within the registered rule class, no two-valued collapse is both sound and non-wasteful.

A 30-case authenticated-certificate panel with four corruption worlds supplies complementary conformance evidence: zero gold-scored unsafe reuse and, on valid certificates, cost equal to 0.6111 of always reopening. A separate 3,840-point safety experiment supplies no authority because its harm endpoint changes in zero cases despite 2,304 action changes.

The result is a formal and finite-panel law: unresolved support must remain a first-class state. It does not establish correctness of external witnesses, deployed safety, or general cost reduction.

## 1. Reuse is responsibility-relative

A state does not answer every future question merely because it answered one past question. Let \(\psi_r(x)\) be the retained state for responsibility \(r\), and \(a_r(x)\) the action that responsibility requires.

For retained value \(z\), define
\[
F_z^r=\{x:\psi_r(x)=z\}.
\]

State \(z\) is sufficient for \(r\) exactly when
\[
a_r(x)=a_r(x')
\quad
\text{for every }x,x'\in F_z^r.
\]

This fibre-homogeneity condition is necessary and sufficient for a deterministic policy that sees only \(z\) to be correct on every compatible source world. Confidence and computation cannot repair an inhomogeneous fibre without new information.

## 2. Responsibility-carrying certificate

A reusable state is accompanied by a certificate naming:

- the responsibility it can answer;
- the premises on which it depends;
- premise and evidence identities;
- scope and epoch;
- authority;
- invalidation and reopening conditions.

The certificate permits three decisions.

**USE.** Every required premise remains supported and the state is sufficient.

**REOPEN.** A required premise is contradicted, stale, or identity-mismatched.

**CANNOT_CHECK.** No contradiction is established, but available evidence does not determine whether every premise remains valid.

The third outcome prevents uncertainty from being converted into either acceptance or refutation.

## 3. Authenticated conformance panel

Thirty registered state–task cases are evaluated under four certificate worlds. Protected gold is separate from the certificate being checked. Corruptions cover stale, mismatched, and invalid support.

The reuse contract has zero gold-scored unsafe reuse on the complete panel. For valid certificates, its measured cost is 0.6111 times the always-reopen policy.

These are exact finite counts. Authentication establishes binding and integrity inside the model. It does not establish that an external scientific witness is substantively correct.

## 4. Why one safety experiment is non-adjudicative

A separate study contains 3,840 evaluation points. Policies choose different actions on 2,304 points, but the scored harm variable never changes.

The instrument can observe behavioral difference but not safety consequence. An invariant endpoint cannot distinguish safe from unsafe action in this design.

The study therefore carries no safety-effect authority. Reporting zero observed harm without exposing the zero-opportunity structure would be misleading.

## 5. Three-valued premise transport

Let each required premise be supported, contradicted, or unresolved after transport.

The registered rule is:
\[
\begin{cases}
\text{REOPEN}, & \text{if any premise is contradicted};\\
\text{CANNOT\_CHECK}, & \text{if none is contradicted and at least one is unresolved};\\
\text{USE}, & \text{if all are supported}.
\end{cases}
\]

Every unresolved premise is assigned both possible hidden actual states in the evaluator. This prevents uncertainty from being definitionally labeled unsafe or safe.

## 6. Exact finite law

The complete enumeration has 750 worlds.

The three-valued rule yields:
\[
\text{unsound reuse}=0,\qquad
\text{unnecessary revocation}=0,
\]
with 296 abstentions.

Two-valued alternatives expose the tradeoff.

If unresolved is collapsed to contradicted:
\[
\text{unsound reuse}=0,\qquad
\text{unnecessary revocation}=84.
\]

If unresolved is collapsed to unchanged:
\[
\text{unsound reuse}=212,\qquad
\text{unnecessary revocation}=0.
\]

Thus, within the registered rule class, preserving unresolved as a third value is necessary to avoid both error types. The abstentions are not failures of the rule. They are the cost of refusing to invent a premise status.

## 7. What the law does and does not prove

The law proves a property of the declared finite premise model. It does not say every real premise has a crisp hidden truth value or that all dependencies are conjunctive. It does not validate the authority that supplied a premise record.

Its operational implication is narrower: when the reuse decision depends on premise validity and the system cannot determine that validity, a binary keep-or-revoke interface forces either unsound reuse or unnecessary destruction in some registered worlds.

## 8. External and cost boundaries

A retrospective survey across 31 repositories, 14 organizations, and 123 facts contains 32 unresolved cases. Because the survey is retrospective and internally adjudicated, it illustrates prevalence inside the collected artifacts but does not validate external performance.

The cost ratio from the authenticated panel excludes many real expenses, including certificate creation, witness review, invalidation, and institutional coordination. It is not a deployment estimate.

## 9. Donor subtraction

Dependency tracking, cache invalidation, proof-carrying data, three-valued logic, provenance, and truth maintenance own the core primitives. The residual contribution is the responsibility-relative synthesis and the exact transport comparison under hidden resolutions of unresolved premises.

## 10. Conclusion

Safe state reuse needs more than an answer cache. It needs a responsibility, a support certificate, and a transport rule that preserves uncertainty. Exact fibre homogeneity identifies when the retained state is sufficient. The authenticated panel shows bounded fail-closed reuse. The 750-world law then shows why unresolved premises cannot be compressed into a binary status without paying in unsound reuse or unnecessary revocation. A third outcome is not indecision; it is the information-correct result.
