# Responsibility-Carrying State: Exact Sufficiency, Authenticated Reuse, and Three-Valued Transport

## Abstract

State reuse is unsafe when a compiled representation retains an answer but loses the premises that made the answer valid. We study responsibility-carrying state, a reuse contract that binds a derived state to its required premises, scope, evidence identity, epoch, and reopening conditions.

The formal core defines responsibility-relative sufficiency by equivalence-class homogeneity: a state is sufficient for a responsibility only when every source world compatible with the retained state has the same required action. A certificate can then authorize reuse, require reopening, or return `CANNOT_CHECK`. In a 30-case controlled panel with authenticated certificates and four corruption worlds, the contract produces zero gold-scored unsafe reuse. For valid certificates, its measured cost is 0.6111 times the always-reopen comparator. The panel proves finite conformance, not correctness of externally supplied witnesses.

A separate safety-cost experiment is withheld. Across 3,840 registered points, policy action changes occur in 2,304, but the self-scored harm endpoint changes in zero. The instrument has no opportunity to observe a safety difference and cannot support its intended claim.

We then establish a three-valued transport law by exhaustive enumeration of 750 premise-status worlds. Reuse only when every required premise remains supported, revoke when a contradiction is established, and abstain when no contradiction is known but at least one premise is unresolved. This rule has zero unsound reuse and zero unnecessary revocation. Mapping unresolved to contradiction causes 84 over-revocations; mapping it to unchanged causes 212 unsound reuses. Within the registered rule class, no two-valued transport is both sound and non-wasteful.

The contribution is a bounded formal and controlled account of safe state reuse. It does not establish external deployment safety or the correctness of real-world premise certificates.

## 1. Introduction

Compiled state can make repeated reasoning cheap. It can also conceal why a previous answer was valid. If a premise changes, a cached conclusion may remain syntactically available even though its scientific responsibility is no longer discharged.

Ordinary cache invalidation tracks object identity or version. Scientific reuse needs a richer question:

> Which premises, scopes, and authority records must remain valid before this state can answer the current responsibility?

Responsibility-carrying state attaches that dependency information to the reusable object. The contract is deliberately fail-closed. A state may be reused, reopened, or left unresolved. The third outcome matters when the status of a premise is unknown.

## 2. Responsibility-relative sufficiency

Let \(x\) be a source world, \(r\) a responsibility, and \(\psi_r(x)\) the state retained for answering \(r\). Let \(a_r(x)\) be the gold action required by the responsibility.

Define the fibre
\[
F_z^r=\{x:\psi_r(x)=z\}.
\]

**Definition 1.** State \(z\) is sufficient for responsibility \(r\) when
\[
a_r(x)=a_r(x')
\quad\text{for all }x,x'\in F_z^r.
\]

This is an exact information criterion. A state can be sufficient for one responsibility and insufficient for another. Global “state sufficiency” without a responsibility is therefore ill-posed.

**Theorem 1.** A deterministic reuse policy depending only on \(z\) is correct for every compatible source world if and only if each admitted fibre is homogeneous under \(a_r\).

The result separates state reuse from model confidence. A confident answer cannot overcome a fibre that contains incompatible required actions.

## 3. Responsibility certificate

A certificate binds the retained state to:

- the responsibility;
- required premise identities;
- premise statuses;
- content and scope;
- epoch or version;
- evidence digests;
- authority and reopening conditions.

The decision vocabulary is:

- `USE_COMPILED` when the state is sufficient and every required premise remains supported;
- `REOPEN_REQUIRED` when a required premise is contradicted or a material identity has changed;
- `CANNOT_CHECK` when the available evidence cannot determine whether reuse is sound.

The certificate does not make a witness true. It makes the reliance explicit and testable.

## 4. Authenticated finite-panel conformance

A controlled panel contains 30 state–task cases and four certificate worlds, including valid, corrupted, stale, and mismatched evidence conditions. Protected gold is stored outside the certificate evaluated by the reuse policy.

The contract produces zero gold-scored unsafe reuse on the complete registered panel. When certificates are valid, its cost is 0.6111 times the always-reopen comparator.

The result establishes exact conformance in the declared finite model. It does not show that a real scientific witness is correct, that an external authority would issue the same certificate, or that authentication alone guarantees semantic truth.

## 5. The safety endpoint that could not measure safety

An earlier policy study contains 3,840 registered evaluation points. The candidate action changes on 2,304 points, so the policies are behaviorally distinct. The scored harm variable changes on zero points.

A safety comparison needs cases in which a policy decision can alter the harm outcome. Here, the endpoint is invariant over the tested interventions. The observed absence of harm is therefore definitionally uninformative.

The correct disposition is `CANNOT_CHECK` for the intended safety mechanism. The result is not repaired by reporting the large number of rows or the number of action changes.

## 6. Transporting premise status

Reused state often depends on premises whose statuses change across contexts. For each required premise, consider three transport states:

- supported;
- contradicted;
- unresolved.

A transport policy must decide whether the compiled state remains reusable.

The registered three-valued rule is:

1. if any required premise is contradicted, reopen;
2. if no premise is contradicted but at least one is unresolved, return `CANNOT_CHECK`;
3. otherwise reuse.

This is a non-compensatory conjunction. Strong support for one premise cannot offset a blocker in another.

## 7. Exhaustive transport law

The transport experiment enumerates 750 worlds covering all registered assignments for three and four premises, together with both possible hidden resolutions of every unresolved premise.

The three-valued rule has:

- unsound reuse: 0;
- unnecessary revocation: 0;
- abstentions: 296.

Two two-valued collapses fail in opposite directions.

**Pessimistic collapse.** Mapping unresolved to contradicted has zero unsound reuse but 84 unnecessary revocations.

**Optimistic collapse.** Mapping unresolved to unchanged has zero unnecessary revocation but 212 unsound reuses.

**Theorem 2 (registered transport law).** Within the declared premise model and rule class, the three-valued rule is the unique transport policy with zero unsound reuse and zero unnecessary revocation. No two-valued collapse satisfies both properties.

The hidden-resolution construction is essential. An earlier instrument defined unresolved as already unsafe and therefore made the result circular. The corrected model gives unresolved premises a hidden actual value and evaluates both resolutions.

## 8. Cost and responsibility

Responsibility metadata creates overhead, but reopening everything also has a cost. The finite authenticated panel shows one setting in which valid certificates preserve reuse at lower cost than always rebuilding, while corruption causes fail-closed reopening.

This is not a universal economic result. Certificate construction, witness checking, storage, invalidation, and authority coordination all need to be counted in a real deployment.

## 9. Retrospective external boundary

A retrospective survey contains 31 repositories from 14 organizations, 123 extracted facts, and 32 `CANNOT_CHECK` dispositions. It was read after outcomes and has no prospectively frozen external test.

The survey can illustrate that incomplete support occurs in real artifacts. It cannot validate the transport law, estimate deployment safety, or serve as independent scientific authority.

## 10. Donor boundary

Cache invalidation, proof-carrying data, dependency tracking, truth maintenance, provenance, three-valued logic, and selective prediction supply neighboring concepts. The paper does not claim those primitives.

The residual contribution is their responsibility-relative integration: exact fibre sufficiency, authenticated reuse with explicit reopening, preservation of unresolved status, and an exhaustive finite transport law.

## 11. Limitations

The formal model assumes premise identities and hidden truth values are well defined. Real scientific premises can be contested, partially applicable, or dependent. The authenticated panel is internally constructed. The retrospective external material is not a prospective validation set.

No claim is made about deployed safety, independent witness correctness, institutional agreement, or general cost savings.

## 12. Conclusion

Reusable state should carry the responsibilities and premises that authorize its use. Exact fibre homogeneity identifies when a retained state is information-sufficient. Authenticated certificates can then support reuse or force reopening, but a safety endpoint with no harm variation cannot validate the policy. When premise status is transported, unresolved must remain a third outcome: treating it as false wastes valid work, while treating it as unchanged permits unsound reuse. The result is a bounded fail-closed law for state reuse, not a substitute for external scientific authority.
