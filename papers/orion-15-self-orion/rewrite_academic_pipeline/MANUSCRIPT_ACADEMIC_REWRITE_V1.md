# Protected Recursive Scientific Improvement: Fallible Self-Diagnosis without Self-Promotion

## Abstract

Autonomous research systems increasingly diagnose their own failures, propose repairs, modify code and choose subsequent experiments. A central governance problem follows: the same internal process that proposes a modification may also be tempted to treat its own diagnosis or apparent improvement as authority to adopt that modification. We study a narrower and already auditable question than end-to-end self-improvement superiority: **how can a scientific system use fallible self-diagnosis and self-generated proposals without making those internal judgments self-authorizing?**

ORION-15 separates diagnosis, proposal, evidence, assurance and adoption into typed status transitions. Internally generated objects may guide what to investigate or propose next, but adoption remains a separately licensed transition. The formal core characterizes when exact revision decisions factor through an evidence interface, gives the optimal interface-only risk when they do not, and proves a protected-promotion impossibility: if two situations that require different promotion decisions are internally indistinguishable, no internal rule can be both sound and complete. Finite discriminator-panel and adaptive-testing results then characterize when additional tests can separate revision decisions and what cost is required.

The architecture is evaluated in a deliberately non-vacuous error setting. A retained hidden-cause diagnostic archive is correct on 21 of 24 constructed cases and preserves three wrong attributions. Those errors are not repaired away. They show why proposal origin cannot itself be an adoption certificate. A local Defects4J development factorial and subsequent archival replay provide bounded engineering evidence, while the planned comparative self-improvement campaign remains unexecuted. Its frozen design contains 2,228 cases, eight arms, three seeds and 53,472 planned run cells, but zero cells were eligible because required benchmark rights and protected fresh-adoption custody were unavailable. Zero eligible cells are treated as `CANNOT_CHECK`, not as zero improvement.

The contribution is therefore a theory and architecture of **protected recursive scientific improvement without self-promotion**. The paper does not claim superior repair rate, causal self-improvement, safer transfer or lower false-adoption rate than strong self-improving-agent baselines. Those empirical claims require a separately authorized campaign.

## 1. Introduction

A system that can inspect its own failures and modify its own method creates a useful feedback loop. It also creates a circularity problem. The evidence that a proposed change is good may itself be generated, selected or interpreted by the process that wants the change adopted.

This issue is not specific to one family of self-improving agents. It appears whenever proposal generation, evaluation and promotion are colocated. Automated program repair can generate patches. Search systems can mutate their own heuristics. agents can rewrite tools or prompts. Scientific assistants can update experiment policies in response to failure. In every case, a proposal may be informative without being authoritative.

We therefore separate two questions that are often conflated.

1. **Can the system generate a useful diagnosis or proposal?**
2. **What evidence licenses that proposal to become the adopted scientific method?**

The first question concerns capability. The second concerns scientific status transition. ORION-15 is built around the claim that these transitions should be distinct even when the system is highly autonomous.

This paper does not attempt to establish that ORION-15 improves itself better than strong self-editing or evolutionary baselines. A frozen comparative campaign exists, but its protected execution prerequisites are not satisfied. Instead, we study the scientific object that is already implemented and auditable: a protected revision architecture in which fallible internal judgments can guide search without acquiring adoption authority.

### 1.1 Contributions

The paper contributes five layers.

1. **Evidence-interface factorization.** Exact revision through a restricted evidence interface is possible exactly when the required minimal revision front is constant on every interface fibre.
2. **Risk under information loss.** When revision labels cannot be recovered exactly, the best interface-only decision has the expected conditional Bayes risk; under the appropriate zero-one special case this becomes fibre impurity.
3. **Protected-promotion impossibility.** If internally indistinguishable states require different promotion decisions, no internal policy can be simultaneously sound and complete.
4. **Discriminator design.** For finite candidate tests, exact revision is possible exactly when the selected panel separates every pair of latent states requiring different revisions; minimum additive cost reduces to a weighted set-cover problem. Adaptive policies are exact precisely when every reachable terminal leaf is decision-pure.
5. **Non-self-authorizing architecture.** Diagnosis and proposal can remain useful even when wrong because adoption requires a separate protected transition. The 21/24 diagnostic archive supplies a concrete error setting; the unexecuted 53,472-cell performance campaign supplies an explicit boundary on what is not yet known.

The central result is architectural and epistemic, not a performance leaderboard.

## 2. Scientific state and protected revision

Let a scientific workflow maintain a state that includes at least:

- the current method or policy;
- evidence supporting or defeating candidate changes;
- negative history and rejected alternatives;
- the origin of a diagnosis or proposal;
- the evaluator and assurance identities;
- the authority permitted to change the adopted method.

A **diagnosis** is an internal judgment about why the current method failed. A **proposal** is a candidate action, computation, repair or method modification. An **adoption** is the status transition that changes the active scientific method.

These objects are intentionally typed differently. A high-confidence diagnosis can be wrong. A generated patch can pass an incomplete evaluator. A proposal can be useful for directing the next experiment while still lacking authority to change the method.

The protected architecture therefore exposes no rule of the form
\[
\text{proposal generated} \Rightarrow \text{proposal adopted}.
\]
Instead, adoption consumes a separate evidence and assurance object under host-owned authority.

This distinction makes self-improvement recursive without making it reflexively self-certifying. A new method may later generate another diagnosis and proposal, but every adoption event must again satisfy the protected transition contract.

## 3. When can revision factor through an evidence interface?

Suppose the latent scientific situation is \(w\), the full-information revision decision is \(r(w)\), and the internal decision layer observes only an evidence interface \(E(w)\).

### Theorem 1 — exact factorization

An exact revision rule \(\rho\) satisfying
\[
r(w)=\rho(E(w))
\]
for every world exists if and only if \(r\) is constant on each fibre of \(E\).

The statement is set-theoretic. Measurable or computable factorization requires the additional regularity conditions recorded in the theory ledger. The theorem does not claim a new general statistical principle; it identifies the exact information boundary for this revision problem.

The consequence is direct. If two worlds look identical through the permitted evidence interface but require different revisions, then no internal decoder can recover the correct revision in both.

### Theorem 2 — optimal interface-only risk

On the registered standard-Borel setting with finite nonempty action/decision alphabets and finite loss, the optimal interface-only risk equals the expected conditional Bayes risk. When every target label is an admissible action under zero-one loss, the residual becomes fibre impurity.

This separates two failure modes. A poor revision decision can result from a weak algorithm, or from an interface that has already collapsed scientifically relevant distinctions. More internal search cannot repair the second failure without acquiring new information.

## 4. Why self-promotion can be impossible

The factorization theorem yields a protected-promotion corollary.

### Corollary 1 — indistinguishability blocks sound-and-complete self-promotion

If two situations are internally indistinguishable but require different protected promotion decisions, no internal rule based only on that interface can be both sound and complete.

Always refusing promotion may be sound but incomplete. Always promoting may be complete on some positive states but unsafe elsewhere. The theorem does not imply that an external evaluator is infallible; it shows that some distinction outside the internal interface is logically required if the required decisions differ.

This is the formal reason proposal origin is not adoption authority. A system may be excellent at generating candidates and still be unable to distinguish a genuine improvement from a candidate that exploits its own evaluator.

The protected architecture therefore treats evaluator identity, fresh evidence, hidden transfer, assurance, negative history and external adoption authority as possible parts of the promotion interface. Which subset is required depends on the declared workflow class. The general principle is that the information needed to distinguish promotion decisions must not be erased by the interface controlled by the candidate.

## 5. Designing discriminators rather than trusting confidence

When the current evidence interface is insufficient, the next question is which additional tests should be acquired.

For a finite set of latent states and candidate tests, define a pair of states as **revision-conflicting** when they require different revisions.

### Theorem 3 — finite discriminator panels

A fixed panel of tests permits exact revision selection if and only if it separates every revision-conflicting pair. With additive test costs, the minimum-cost exact panel is the corresponding weighted set-cover optimum.

This result turns “run more experiments” into a precise design problem. A test is useful when it separates a currently mixed revision fibre. A large but redundant benchmark may add no decision information at all.

### Proposition 1 — adaptive testing

A terminating deterministic adaptive test policy is exact if and only if every reachable terminal leaf is revision-decision-pure.

The stochastic extension in the theory ledger states the analogous criterion in terms of separating transcript laws. It also records the boundary: identical one-test marginals do not by themselves prove impossibility, and unrestricted policy optimization may attain only an infimum without additional assumptions.

These caveats matter for self-improvement experiments, where adaptive testing can otherwise create a false impression that every extra probe is independent evidence.

## 6. State-indexed active identification

The theory extends to finite observable laboratory state with state-dependent legal interventions, costs and known outcome/next-state kernels. The exact frontier enumerates legal deterministic discriminator-tree risk vectors at a finite horizon. Under fixed ex-ante credal ambiguity, licensed deterministic and world-independent randomized minimax values are support-function minima over that frontier and its convex hull.

These results are finite controlled-state specializations. They do not claim general robust-POMDP novelty. The negative ledger is equally important: destructive/unavailable actions, informative state transitions, nonclosed priors, rectangularization, zero-cost closure, infinite horizon and state-sufficiency failures remain explicit boundary cases.

The paper uses this theory as a design discipline: recursion does not remove the need to record which interventions were legal, what state was observed, what uncertainty model was licensed and who owned the decision to adopt.

## 7. A non-vacuous error setting: 21 of 24 diagnoses

A governance architecture that never sees a wrong internal judgment would demonstrate little about self-promotion risk. ORION-15 therefore retains an archived hidden-cause attribution exercise with 24 fixed constructed cases.

The diagnostic is correct on 21 cases and wrong on three. The three errors remain in the record. They are not relabeled as partial successes and are not excluded from the denominator.

This archive supports one narrow observation:

> the architecture does not require perfect self-knowledge in order to keep diagnosis and adoption distinct.

It does **not** show that a 21/24 diagnostic is good enough for autonomous self-improvement. The 24 cases are not a probability sample of deployment failures, and a nominal confidence interval would not be a justified population statement. There is no matched external baseline and no protected transfer result in this archive.

The value of the errors is conceptual. A wrong diagnosis can still generate a plausible proposal. If proposal origin automatically carried adoption authority, the architecture would convert diagnostic error directly into method change. The protected transition prevents that logical shortcut.

## 8. Local development evidence and retained defects

ORION-15 also contains a bounded public-development factorial around one Defects4J Lang-1 known-fix cluster. The scientific unit is one source/bug/fix cluster; Java distributions and phase streams are within-cluster measurements rather than independent replicates.

The first result retained a harmful/adverse terminal because JDK-17 cells violated the benchmark's Java-11 contract and the raw-tree identity model rejected benchmark-prepared checkout trees. A preregistered V2 successor over the same public known fix observed an implementation main effect and no environment effect in that local pattern. A subsequent audit discovered a path construction defect that collapsed declared checkout/test paths. A post-outcome V3 archival replay repaired the archival streams and reached an archival-complete terminal.

The sequence is deliberately not compressed into a success story. V3 was frozen after V2 outcomes were known, cannot recreate overwritten V2 checkout bytes and is not an independent scientific replication. The public known fix and local evaluator do not grant generality, protected freshness or comparative self-improvement authority.

This negative history illustrates the architecture's intended behavior: failures and superseded receipts remain part of the scientific state instead of disappearing when a later run looks cleaner.

## 9. Comparator preflight is not comparator performance

The planned wider campaign identifies six comparator roles and freezes source identities, revisions, licences and entry points. Synthetic adapters and outcome-blind preflight checks test interface contracts. They do not establish comparative performance.

The current ledger records that zero of the six comparator families is confirmatory-ready under the full protected contract. Some adapters can map a subset of synthetic terminal cases to typed proposed actions; many remain `UNRESOLVED`. Source locks, benchmark payload rights, protected scorers and full native execution bindings are incomplete in different ways across the panel.

This distinction matters because a paper can accidentally convert engineering preparation into scientific evidence. A parser that preserves native status is not evidence that its system solves the benchmark. A synthetic conformance row is not an independent task. A source-identity ledger is not a performance table.

ORION-15 therefore uses the preflight only to establish what would have to be true before the planned comparison could be executed faithfully.

## 10. The frozen performance campaign and why zero is not a result

The maximum performance successor is prospectively specified at 2,228 cases, eight arms and three seeds, yielding 53,472 planned run cells. Its endpoints include resolved-rate gain, PASS_TO_PASS regressions, evaluator-gaming detection, held-out transfer, causal credit, resource cost and false adoption.

The authoritative execution disposition is not a null effect. It is:

`SWE_BENCH_RIGHTS_AND_PROTECTED_FRESH_ADOPTION_CUSTODY_UNAVAILABLE`.

Zero run cells were eligible and all case rows remain `CANNOT_CHECK` for the performance claims.

This is scientifically important because “zero executed” and “zero improvement” are completely different propositions. The former is an acquisition/custody outcome. Treating it as the latter would fabricate an effect estimate from missing eligibility.

The following claims therefore remain unestablished:

- resolved-rate superiority;
- reduction in PASS_TO_PASS regressions;
- evaluator-gaming detection advantage;
- held-out transfer superiority;
- causal candidate effect;
- resource advantage;
- lower false-adoption rate.

These endpoints can move only after benchmark rights and protected fresh-adoption custody are validly acquired and the frozen comparison is executed.

## 11. What the bounded paper establishes

The current evidence supports a theory/architecture claim rather than a performance claim.

1. Exact revision through an evidence interface requires decision purity on every interface fibre.
2. When that condition fails, the residual risk is determined by the information retained at the interface, not by internal confidence alone.
3. If protected promotion differs across internally indistinguishable states, internal self-promotion cannot be both sound and complete.
4. Additional tests should be selected for their ability to separate revision-conflicting states, not for raw benchmark volume.
5. The implemented ORION-15 control path keeps diagnosis/proposal distinct from adoption authority.
6. The 21/24 diagnostic archive demonstrates that this distinction is non-vacuous in the presence of retained internal mistakes.
7. Negative and superseded development outcomes remain part of the state rather than being erased by later repair.

This supports the paper's central proposition:

> Fallible self-diagnosis and self-generated method proposals can guide recursive scientific search without becoming self-authorizing, provided that adoption is a distinct protected transition whose decisive evidence is not collapsed into the candidate-controlled interface.

## 12. Relation to adjacent work

The paper is intentionally downstream of several mature areas: automated program repair, evolutionary and self-editing agents, adaptive experimentation, causal intervention evaluation, robust decision-making and constitutional/evaluator-governance mechanisms.

ORION-15 does not claim to invent self-improving agents, mutation/search, failure attribution, evaluator integrity or negative-history memory. Its residual contribution is the status-transition problem: how these capabilities can be composed so that generating a candidate, diagnosing a failure and authorizing adoption remain different scientific acts.

The immediate pre-submission version should include a venue-specific nearest-work review and explicit donor subtraction against the final comparator set. That literature task can sharpen novelty wording but cannot grant performance authority absent the frozen execution.

## 13. Limitations

1. The strongest comparative campaign has zero eligible execution cells because rights and protected adoption custody are unavailable.
2. The 21/24 diagnostic archive is a fixed constructed case set, not deployment-level accuracy evidence.
3. The Defects4J development result concerns one source/bug/fix cluster and retains known archival and preregistration limitations.
4. Synthetic adapter conformance and source preflight do not establish comparator correctness or performance.
5. Protected evaluators may themselves be wrong; separation of authority does not imply infallibility.
6. The formal results are exact under their declared interfaces and finite/stochastic conditions, not universal sample-complexity or robust-control theorems.
7. No claim of superior self-improvement, safer transfer or causal recursive improvement is made.

## 14. Reproducibility and governance

The submission package should bind the theory ledger, diagnostic archive, negative-result history, local development receipts, comparator identity/preflight ledger and the authoritative zero-eligibility disposition. Reproduction must preserve the difference between public-development replays, same-lane checks and genuinely external protected evaluation.

The frozen performance design should remain separate from the bounded paper's empirical results. If rights and custody later become available, its outcomes—positive, null, adverse or `CANNOT_CHECK`—should be added without retroactively changing the theory manuscript's historical claims.

## 15. Conclusion

Recursive scientific improvement is not the same as recursive self-authorization. A system may diagnose its failures, propose repairs and choose informative tests while remaining unable to promote its own proposal into the adopted method. ORION-15 formalizes the information conditions behind that separation and implements an authority path in which diagnosis and proposal are scientifically useful but status-limited.

The retained 21/24 diagnostic errors make the point concrete: fallible internal judgments are precisely why adoption needs a distinct evidence and authority boundary. The unexecuted 53,472-cell campaign sets the complementary boundary: the architecture has not yet earned a comparative performance claim.

The present paper is therefore complete at a scoped theory/architecture level. Its strongest future extension is empirical, but that extension begins with rights and protected custody—not with stronger prose or another internal replay.

## Submission posture

**Bounded paper:** complete manuscript candidate for a theory/methods/governance venue after final bibliography, proof review, production render and venue-specific literature closure.

**Performance/top-tier successor:** not earned. Execute the frozen comparison only after benchmark rights and protected fresh-adoption custody are validly established.