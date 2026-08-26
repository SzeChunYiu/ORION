# A Theory of Epistemic Authority for Autonomous Science

**Working manuscript — candidate ORION-18 — 2026-08-17**

## Abstract

Autonomous scientific agents can reframe problems, search and stop, align representations, assert claims and modify their own procedures. Capability to construct such actions does not establish authority to commit them. This distinction is increasingly explicit in agent security and programming-language research: ETAS provides typed effects, persistent action traces, residual obligations and policy safety; FAVA builds evidence-backed permission graphs and uses deterministic SMT authorization before effectful actions; AgentAbstain evaluates whether tool-using agents know when not to act; ProvenanceGuard treats source attribution as an independent verification dimension; execution-provenance work moves agent evaluation from final outputs toward process accountability. ORION must absorb these mechanisms rather than claim permissions, abstention or provenance as new. ORION-18 therefore studies a narrower cross-domain problem: can heterogeneous *epistemic* effect domains share a typed authorization calculus that preserves domain-specific gates while preventing one domain's valid signal from being laundered into another domain's authority? We define typed effects, hard obligations, grants, explicit cross-domain coercions, `CANNOT_CHECK`, dependency-grounded revocation and protected authority roots. We prove a syntactic anti-laundering theorem, show why extensible additive evidence cannot encode absolute blockers with finite penalties, and give countermodels for post-hoc refusal and candidate-controlled self-promotion. ORION-18 remains a candidate until it embeds ORION-11–ORION-15 conservatively and demonstrates cross-domain failures or transfer advantages beyond strong effect/permission and independent-gate baselines.

## 1. Introduction

Reliable autonomous science requires more than capable models and successful tool use. It requires rules governing when epistemically consequential actions may be committed.

Consider five action families:

1. change the problem formulation or search universe;
2. stop searching or declare a task closed;
3. merge scientific representations;
4. promote a claim to verified scientific authority;
5. modify and promote the agent's own mechanism.

A model can generate each action. It can assign high confidence to each. A local evaluator can reward each. A system may even execute each successfully in a narrow operational sense. None of those facts alone determines whether the transition is authorized.

ORION already implements this distinction in five domain-specific ways. ORION-11 governs formulation/search mutation through responsibility. ORION-12 separates route progress from task closure. ORION-13 preserves obstruction when mapping is not authorized. ORION-14 protects scientific-authority promotion with content-bound evidence and independent checks. ORION-15 denies self-promotion and requires replay, fresh transfer and protected assurance.

ORION-18 cannot claim those mechanisms. Its question is whether there is a **typed composition theory above them** that explains when authority may and may not cross domain boundaries.

## 2. Why current permission work raises the bar

The contemporary nearest-work landscape already contains strong formal and systems mechanisms.

### ETAS
ETAS (arXiv:2607.17780) treats agent actions, tools, typed memory, human approvals, policies and traces as semantic program elements. Its static semantics tracks effects and potential action traces; policies express allow/deny/temporal constraints; residual obligations remain when static proof is insufficient; dynamic semantics distinguish requested, handled, denied and committed events. ORION-18 therefore cannot claim typed effects, residual obligations or trace-visible policy enforcement.

### FAVA
FAVA (arXiv:2607.27267) translates ambiguous tasks into a structured Permission IR, lowers that into an evidence-backed permission graph tracking dependencies/context, and uses an SMT authorizer before effectful execution. ORION-18 therefore cannot claim evidence-backed permission graphs or deterministic pre-action authorization.

### AgentAbstain
AgentAbstain (arXiv:2607.10059) uses paired should-act/should-abstain tasks and reports that abstention competence is substantially distinct from ordinary task-solving capability. It also identifies post-hoc abstention, where irreversible action occurs before refusal. ORION-18 therefore cannot claim that agents need to know when not to act.

### ProvenanceGuard and execution provenance
ProvenanceGuard (arXiv:2606.18037) shows that a claim can be supported somewhere yet attributed to the wrong source; source ownership is an independent verification axis. A 2026 execution-provenance survey (arXiv:2606.04990) unifies evidence tracing, tool-use lineage, memory provenance, guardrails, debugging, audit and recovery. ORION-18 therefore cannot claim provenance as authority by itself.

### Runtime governance and permission systems
Agent-Sentry, Policy Cards and the 2026 user-permission-systems survey provide additional pressure from behavioral bounds, machine-readable obligations and runtime enforcement. Classical deontic/action and authorization logics are broader historical parents.

The ORION opportunity, if any, begins after these are absorbed.

## 3. Epistemic effects and authority domains

Let `D` be a set of effect domains. The initial ORION embedding uses

\[
D_0=\{REFRAME,SEARCH\_STOP,MAP\_MERGE,ASSERT,SELF\_MODIFY\}.
\]

An effect request is

\[
e=(id,d,op,S,p,epoch),
\]

with identity, domain, operation, target scope, payload/state delta and epoch.

A typed judgment records at least a kind, domain, scope, content/provenance identity and epoch. Kinds include support, blocker, obligation satisfaction, grant, revocation, capability, utility and closure.

A bare `PASS`, `SUCCESS`, `VERIFIED`, high confidence score or positive replay delta is not sufficient authority currency because it omits the domain and scope in which the judgment is valid.

## 4. Requested versus committed effects

ORION-18 adopts a request/commit semantics:

\[
REQUEST(e),\;ALLOW(e),\;DENY(e),\;CANNOT\_CHECK(e),\;COMMIT(e).
\]

An effect may commit only when the authorization derivation matches the exact effect identity, scope, content identity and current epoch.

This is deliberately compatible with effect/permission systems rather than presented as a competitor. ORION-18's scientific question concerns *which epistemic judgments may be reused across effect domains*.

## 5. Hard obligations and non-compensation

For effect `e`, let `O_h(e)` be hard obligations and `O_s(e)` soft/resource considerations. Authorization requires every hard obligation to be satisfied and every blocking defeater absent. Soft utility can rank already-admissible options but does not discharge a hard obligation.

A simple algebraic result clarifies why this distinction must be represented explicitly. Suppose an authorization score is

\[
S(e)=\sum_i w_i x_i-Mb
\]

with a finite blocker penalty `M`, fixed threshold and an extensible/unbounded stream of positive evidence. For any finite `M`, sufficiently much positive evidence eventually crosses the threshold while the blocker remains active. Therefore an *absolute* blocker requires a conjunctive, veto, lexicographic or otherwise explicitly non-compensatory layer unless the positive evidence space is externally bounded.

This is a limited theorem. A fixed-dimensional bounded score can simulate a veto with a sufficiently large finite weight; ORION-18 does not claim every scalar decision rule is invalid.

## 6. Cross-domain coercions

The core ORION-18 object is an explicit coercion

\[
c:d\Rightarrow d'
\]

that specifies when a judgment rooted in domain `d` may contribute to authority in `d'`. A coercion includes premises, scope transformation, evidence-preservation conditions and an authorized issuer/root.

Without such a rule:

- planner confidence does not imply reframe authority;
- route exhaustion does not imply global task closure;
- semantic similarity does not imply merge authority;
- citation support does not imply verified scientific authority;
- replay improvement does not imply self-promotion authority.

### Authority laundering

**Authority laundering** occurs when an authority-bearing signal valid in `d` is used to authorize an effect in `d'` without a valid registered coercion path.

This is intentionally broader than a single failure pattern. ORION-14 already has an internal authority-laundering falsifier in the assertion/verification lane. ORION-18's candidate contribution is only **cross-domain** laundering.

## 7. Anti-laundering theorem

Assume every judgment is domain-typed and every ordinary inference rule preserves the authority domain. The only rules allowed to change domain are registered coercions.

Then no derivation can conclude `Auth_{d'}(e)` from authority-bearing premises rooted exclusively in `d != d'` unless a valid coercion path from `d` to `d'` occurs.

The proof is by induction on derivation height. Base axioms preserve their domain. Ordinary inference preserves domain by assumption. Therefore any domain change in a derivation must be introduced by a coercion rule.

The theorem is syntactic. It does not prove that registered coercions are semantically correct. Soundness of each coercion is a separate obligation.

## 8. Dependency-grounded revocation

Authority is non-monotonic. Evidence can be invalidated, a source can lose admissibility, an evaluator can be compromised, a scope can expire, or a mapping assumption can fail.

ORION-18 records a dependency graph over evidence judgments, grants, coercion applications and authorization certificates. If an ancestor is revoked, every certificate that necessarily depends on it becomes invalid. A certificate with an independent complete trusted derivation may survive.

This yields a targeted revocation property: revoke affected descendants without globally destroying unrelated authorization state.

The mechanism is closely related to dependency repair/provenance work and is not claimed in isolation. Its role in ORION-18 is to make cross-domain authority composition reversible and auditable.

## 9. `CANNOT_CHECK` is not refusal

`CANNOT_CHECK(e)` means a mandatory authorization premise cannot currently be established or refuted. It differs from:

- `DENY`, where a blocker/violation is established;
- `UNAUTHORIZED`, where no valid authority derivation exists;
- `REVOKED`, where prior authorization lost a premise;
- `DEFER`, where scheduling/resources postpone an action;
- ordinary abstention, which may not explain which authorization premise is unresolved.

This distinction matters because a system can be correct to avoid an action for several epistemically different reasons. A benchmark that collapses all of them into “refused” loses information about authority calibration.

## 10. Pre-effect authorization and post-hoc abstention

For irreversible/effectful actions, an authorization decision must precede the commit if it is to be preventive.

If the effect is already committed and the system later emits `DENY` or `CANNOT_CHECK`, that later refusal cannot retroactively satisfy pre-effect authorization. AgentAbstain already identifies this empirically as post-hoc abstention; ORION-18 adopts it as a timing invariant.

## 11. Protected roots and self-promotion

If a self-modifying candidate can rewrite both its admission predicate and every evidence value read by that predicate, it can construct an accepting policy regardless of any external target property. Internal acceptance therefore cannot imply external promotion soundness without at least one protected root or invariant outside candidate write control.

ORION-15 already owns this operational mechanism. ORION-18 uses it as one instance of a more general root/delegation boundary and must not relabel it.

## 12. Conservative embeddings of ORION-11–ORION-15

A valid general calculus must reproduce existing domain gates when instantiated on their native cases.

**ORION-11 / `REFRAME`.** Responsibility and evidence determine which formulation/search coordinates may be mutated; dependent closure reopens.

**ORION-12 / `SEARCH_STOP`.** Route stop is not task stop; mandatory censored/open coverage obligations block global closure.

**ORION-13 / `MAP_MERGE`.** Similarity alone cannot discharge referent, context, measurement and obstruction obligations.

**ORION-14 / `ASSERT`.** Content-bound evidence, source ownership/support, independent/hostile checking and protected evaluator identity determine scientific-authority promotion.

**ORION-15 / `SELF_MODIFY`.** Replay, fresh transfer, protected assurance, negative history and host-only promotion govern self-change admission.

ORION-18 gains no novelty from these within-domain instances. The required theorem/checker target is **conservative gate embedding**: the general calculus reproduces their frozen native decisions exactly.

## 13. Why cross-domain composition might still matter

Independent local gates can all be correct while their composition is wrong.

Imagine ORION-12 emits a valid `ROUTE_STOP` judgment. A downstream component sees the generic token `PASS` and interprets it as permission to assert “the scientific literature is complete.” Nothing is wrong with the ORION-12 route judgment. The error lies in the untyped transport from search-route authority to assertion/closure authority.

Likewise, a ORION-13 mapping similarity score can be valid evidence while being insufficient merge authority; a ORION-14 citation-supported claim can be validly sourced while lacking a stronger verification obligation; a ORION-15 replay improvement can be real while lacking self-promotion authority.

ORION-18 therefore predicts a distinct failure family: **composition can introduce authority violations even when every producing module emits a locally valid judgment**.

This is the key discriminator against a programme consisting only of five independent correct gates.

## 14. Donor-faithful embedding

ORION-18 must also embed strong external donors conservatively.

- ETAS-style typed effects/traces should retain their native policy behavior when scientific-domain coercions are inactive.
- FAVA-style permission graphs and deterministic authorization should remain valid specializations.
- AgentAbstain paired act/abstain cases should retain their act/abstain truth while ORION-18 adds a more typed explanation of why.
- ProvenanceGuard's source-specific support/attribution judgments should remain non-fungible evidence dimensions.

A generalization that changes donor-native verdicts merely to look more comprehensive is rejected.

## 15. Deterministic hostile checks

The first checker is committed at `papers/candidates/checkers/p8_finite_falsifiers_v1.py`. The current local run is 7/7 PASS on bounded fixtures covering:

1. blocked cross-domain authorization without a coercion and allowed transport with an explicit path;
2. scope narrowing versus widening;
3. the finite-penalty additive-blocker counterexample;
4. dependency revocation that preserves an independent authorization path;
5. stale epoch replay plus post-hoc-refusal timing;
6. candidate-controlled constant-accept self-promotion countermodel;
7. a clean authorized control preventing total-refusal behavior.

The protected benchmark must expand this to paired cases across all five domains, cross-module laundering attacks, revocation timing, scope/epoch replay and valid-coercion positive controls.

## 16. Prospective evaluation

The strongest baseline is not a confidence threshold. ORION-18 must compare against:

- the existing independent ORION-11–ORION-15 gates;
- FAVA/ETAS-style typed-policy implementations where feasible;
- provenance-only verification;
- an abstention policy;
- expected-utility authorization;
- rule-based domain-specific authorization;
- untyped/global `PASS` tokens;
- no-revocation and no-hard-obligation ablations.

Primary outcomes include unauthorized-action rate, authority-laundering rate, unnecessary refusal, clean authorized coverage, correct revocation, stale-certificate acceptance, calibrated `CANNOT_CHECK`, and cost/latency.

The decisive ORION-18 result would be a case where independent gates are locally correct but fail under composition, while typed cross-domain coercion blocks the invalid transport without reducing valid action coverage.

If that does not occur, ORION-18 should merge into ORION-14/programme synthesis.

## 17. Exact ownership boundary

The V1 ORION-11–ORION-15 ownership matrix marks all five within-domain authority transitions `MERGE_EXISTING`. Generic permissions/effect typing, provenance and abstention are `ADOPT / DO NOT CLAIM` because strong external donors own them.

The only ORION-18 rows allowed to remain paper-level candidates are cross-domain coercion/anti-laundering and related dependency revocation—each still `CANNOT_CHECK` pending external saturation and prospective evaluation.

## 18. Limitations

Authority contracts are normative and task-specific. A typed calculus can merely move human judgment into the coercion registry. Protected roots can be compromised. Conservative embeddings can be technically correct yet scientifically uninteresting. Excessive fail-closed behavior can reduce useful autonomy. Formal authorization establishes contract compliance, not truth. Cross-domain boundaries themselves may be disputed or fluid.

There is also a serious novelty risk: authorization and effect systems are mature, and current agent-security work is moving rapidly. ORION-18 should be terminated if its cross-domain object is already standard policy composition with renamed domains.

## 19. Conclusion

ORION-18 treats autonomous science as a system of effectful epistemic actions whose authority is typed, scoped, evidence-bound, revocable and compositional. The programme's strategy is assimilation-first: absorb the strongest permission, effect, abstention and provenance mechanisms, embed the existing ORION gates without stealing them, then test whether cross-domain scientific authority has failure modes that those components do not resolve individually. Until that test succeeds, ORION-18 remains a candidate rather than a flagship.