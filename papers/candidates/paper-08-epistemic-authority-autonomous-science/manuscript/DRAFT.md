# A Theory of Epistemic Authority for Autonomous Science

**Working manuscript — candidate P8 — 2026-08-17**

## Abstract

Autonomous scientific agents can retrieve evidence, revise formulations, merge representations, assert conclusions and modify their own procedures. Capability alone does not establish that any such transition is justified. Across ORION's current five-paper programme, the same distinction appears repeatedly: a system may be able to reframe without being licensed to alter the problem, able to stop without being licensed to declare closure, able to map without being licensed to merge, able to state a claim without scientific authority, or able to improve on replay without being licensed to promote a self-change. This paper investigates whether these cases admit a reusable **epistemic authority calculus**. The candidate formalism types proposed epistemic actions, required obligations, defeaters, authority sources, refusal/CANNOT_CHECK and revocation. It is explicitly non-compensatory: confidence, utility or success in one dimension cannot automatically offset a missing obligation in another. The central empirical question is whether a shared calculus prevents cross-module authority laundering better than independent capability-specific gates. The candidate is not yet a novelty claim and must survive direct comparison with P4, abstention, provenance/verification, dynamic/deontic logic and agent-governance work.

## 1. Introduction

Reliable autonomous science requires more than increasingly capable models. It requires rules governing when capabilities may be exercised.

Consider five actions:

1. rewrite the problem formulation;
2. stop searching;
3. merge two scientific representations;
4. promote a claim to verified scientific status;
5. modify and promote the agent's own mechanism.

A model can generate each action. A high confidence score can accompany each action. A local evaluator can even reward each action. None of those facts alone establishes authority.

The ORION programme currently implements authority in domain-specific ways. P1 couples responsibility to reformulation permission. P2 separates route progress from task closure. P3 preserves obstruction when mapping is not authorized. P4 explicitly studies scientific-authority promotion under protected custody. P5 denies self-promotion even after apparent local improvement.

P8 asks whether a common calculus exists above those cases.

## 2. Capability versus authority

Let `a` be a proposed epistemic action in typed domain `d`:

`d in {REFRAME, SEARCH_STOP, MAP_MERGE, ASSERT, SELF_MODIFY}`.

We distinguish:

- `Cap(a)`: the system can construct/execute `a`;
- `Supp(a)`: evidence positively supports `a`;
- `Def(a)`: active defeaters against `a`;
- `Obl(a)`: obligations that must be satisfied before authorization;
- `Auth(a)`: the action is licensed to commit;
- `Revoke(a)`: new evidence removes prior authority;
- `CC(a)`: authority cannot currently be established (`CANNOT_CHECK`).

The core thesis is that `Cap(a)`, confidence, expected utility and support are not interchangeable with `Auth(a)`.

## 3. Non-compensatory authorization

Many agent policies aggregate evidence into a scalar. This is attractive computationally but dangerous for scientific authority.

Suppose an assertion has excellent support from three sources but lacks an independent check required by the protocol. More support from the same route should not necessarily compensate for the missing check.

Likewise, a self-modification with strong replay improvement should not be admitted if fresh-transfer or evaluator-custody obligations fail.

We therefore consider an obligation family

`Obl(a) = {o1, ..., ok}`

with typed satisfaction states rather than a single score. Authorization is tentatively:

`Auth(a) iff Required(a) subset Satisfied(a) and no blocking Def(a)`.

Some obligations may be soft/resource-related; others are non-compensatory blockers. The formalism must make that distinction explicit rather than burying it in prompt text.

## 4. Authority domains

### 4.1 Reframe authority
A failure diagnosis may suggest that the formulation is wrong. The authority question is whether the available evidence licenses mutation of specific formulation/search coordinates, or whether only more diagnosis/probing is allowed.

### 4.2 Search/stop authority
A route may be exhausted or low-value. That can justify reallocating resources without authorizing global scientific closure when important routes are censored or unresolved.

### 4.3 Mapping/integration authority
Semantic similarity can suggest a cross-source mapping, but merge authority depends on referent, context, measurement, modality and preservation conditions. Obstruction is a legitimate terminal.

### 4.4 Assertion authority
P4 already demonstrates a protected, non-escalating scientific-authority transition. P8 treats this as one action domain and must not relabel the P4 contribution as new.

### 4.5 Self-modification authority
A candidate change can be generated, compiled and locally improved while still lacking authority to promote itself. Fresh transfer, regression limits, negative history and protected evaluation may be mandatory obligations.

## 5. Authority laundering

A central candidate failure class is **authority laundering**: a signal valid in one module is treated as authorization in another.

Examples include:

- a planner's confidence becoming permission to alter the scientific formulation;
- retrieval saturation becoming permission to declare the literature complete;
- semantic similarity becoming permission to merge scientific constructs;
- citation support becoming permission to claim verification;
- replay success becoming permission to self-promote.

Cross-module composition is therefore well formed only if the downstream action explicitly recognizes the upstream signal's authority type. A `PASS` token is not universal currency.

## 6. Revocation and non-monotonicity

Scientific authority must sometimes be withdrawn.

If evidence supporting an assertion is invalidated, downstream authority should be revoked or reopened. If a mapping's measurement-equivalence assumption fails, integrated conclusions may need demotion. If a self-change later causes harmful transfer, prior promotion authority should not be treated as permanently valid.

P8 therefore requires a revocation operator tied to evidence/provenance dependency rather than confidence decay alone.

## 7. Related-work boundary

The candidate sits near several mature areas. Dynamic epistemic logic models informational actions and changing knowledge. Deontic and action logics formalize permission and obligation. Belief-revision systems model non-monotonic change. Selective prediction and abstention study when a system should refuse. Recent AgentAbstain work directly evaluates when tool-using agents should not act. Provenance and scientific-verification systems track whether claims are supported and correctly attributed. Protected-evaluation and benchmark-auditing work separates candidate capability from evaluation authority.

P8 therefore cannot claim novelty for permission, abstention, provenance or non-monotonic revision in isolation.

The hostile residual is narrower: a **typed authorization layer shared across heterogeneous epistemic actions**, with non-compensatory obligations, cross-module anti-laundering and revocation, grounded in executable autonomous-science workflows.

#340 must establish whether this already exists.

## 8. Prospective experiment

#341 proposes paired adversarial cases across all five domains. Each pair contains an action that is technically feasible; the authority conditions differ.

The strongest baseline is not a scalar confidence threshold. We must compare against:

- existing P1–P5 capability-specific gates;
- provenance-only verification;
- an abstention policy;
- expected-utility authorization;
- rule-based domain-specific policies;
- the proposed shared calculus.

Primary outcomes include unauthorized-action rate, unnecessary refusal, clean authorized coverage, authority-laundering rate, correct revocation after defeaters and calibrated CANNOT_CHECK.

If the shared calculus performs no better than independent per-domain gates, P8 should be merged into programme synthesis or P4 rather than published independently.

## 9. Limitations

Authority is partly normative and task-specific. A shared calculus may become too abstract to improve real systems. Obligation design can merely relocate human judgment. Protected custody is expensive and not appropriate for every action. Excessive fail-closed behavior can reduce useful scientific autonomy. Formal authorization does not establish truth; it establishes only that a transition satisfied a defined authority contract.

## 10. Conclusion

The candidate thesis is that autonomous science needs a typed answer to a question that capability benchmarks mostly ignore: **what is this system allowed to change, close, combine, assert or promote on the basis of the evidence it actually has?** P8 remains a candidate until it demonstrates a distinct cross-capability object beyond P4 and existing logic, abstention and provenance frameworks.
