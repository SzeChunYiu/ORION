# Typed and Scoped Partial-Knowledge State for Research Decisions

**Manuscript V2 — publication-synthesis draft**  
Publication cut: `main@ca7df1055a43f97eaf8d142a62011c4c261af368`  
Claim authority: `CLAIM_LEDGER.md` + `PUBLICATION_FOUNDATION_V2.md`

## Abstract

Research agents do not act only on facts about the world. They also act on partial knowledge about which facts are unresolved, which failure records remain valid, which certificates survive representation changes, and which uncertainties matter for the next decision. We test whether attaching explicit **type and scope** to such state changes decision quality when competing methods receive the same underlying information. Across six prospectively frozen exact-synthetic studies, we isolate six downstream responsibilities: probing unknown feasibility, reopening stale failures, allocating verification under interval uncertainty, transporting evidence across remints, selecting decision-relevant experiments, and reusing state after representation edits. Each study includes matched-information controls and a hostile regime designed to punish the obvious untyped shortcut. Typed-prior value-of-information probing reaches mean utility 3.291 versus 2.180 for the identical planner with uniform priors; scope-bound reopening reaches 3.199 pooled utility while unscoped change reopening falls to -7.813; dominance-targeted verification reduces scalarized regret to 0.1096 versus 0.2518 for random verification at the same budget; full-chain typed transport detects all 200 registered laundering chains at zero false positives, whereas last-hop checking reaches 0.085 recall overall and zero on deep splices; decision-coupled probing reaches utility 9.266 versus 7.121 for pure information gain while avoiding max-entropy decoys; and typed remint/transport reaches 9.421 in the mixed-transport regime versus 7.157 for matched re-derivation and -7.821 for naive carry-forward, while tying all controls exactly when reminting is unnecessary. Two first-right-of-refusal negatives bound the interpretation: an ideal value-of-information donor exactly closes the allocation-policy residual in a separate typed-failure-state study, and a model-selection donor ties the candidate on the original crossover-prediction world. These results establish a bounded mechanism claim: in constructed worlds where downstream responsibilities require distinctions not represented by untyped state, explicit type/scope can be load-bearing even at matched information. They do not establish performance on real agents, real scientific pipelines, or adversarial deployment.

## 1. Introduction

A long-running research process accumulates more than observations. It accumulates **epistemic state** about its own knowledge: an interface is feasible with some prior probability; a previous attempt failed under a particular representation and access contract; a cost is bounded by an interval rather than measured; a certificate was minted through a sequence of transformations; a representation changed after the certificate was issued. Downstream decisions consume this state to decide what to probe, what to trust, what to reopen, what to verify, and when to rebuild.

Many of the underlying ingredients are mature. Value-of-information and active-learning methods allocate measurements; provenance systems track where information came from; memory systems detect and revise stale state; interval and robust optimization reason under uncertainty; context-governance systems track versions and eligibility. Recent agent-memory work makes the staleness problem especially explicit. STALE (Chao et al., 2026; arXiv:2605.06527) studies implicit invalidation of stored memories, while later stale-dependency repair work tests whether updated evidence propagates into downstream behaviour. ContextNest (Sulpovar et al., 2026; arXiv:2607.02116) develops versioned, provenance-aware governance for agent-consumable context. We therefore do not claim any of those primitives as new.

The narrower question here is different. **When the same information is available to every method, can its type and scope change what a research process is licensed to do with it?** A failure receipt may be true and well-provenanced yet cease to apply after one representation coordinate changes. A certificate may remain individually valid at each hop yet become invalid as a chain if an interior artifact was substituted. A high-entropy unknown may be informative but irrelevant to the decision. A verification budget may be wasted on uncertainty that cannot change the choice. These are not failures of retrieval; they are failures to represent which distinctions matter for the downstream responsibility.

We isolate that question through six exact-synthetic worlds. Each world is frozen before outcome, gives non-oracle arms the same serialized facts, registers a strongest donor or matched-information control, and contains a hostile regime whose purpose is to make the obvious shortcut fail. The hostile regime is not post-hoc explanation: if the trap does not bite, the protocol declares the world invalid and the positive result cannot be used. This design makes the paper a mechanism study rather than a benchmark of natural agent performance.

Our contribution is threefold. First, we provide a common experimental contract for studying typed/scoped state under matched information. Second, across six distinct downstream responsibilities, the registered type/scope distinction is load-bearing exactly where the hostile construction requires it. Third, two negative results demonstrate first right of refusal: when an ideal donor already receives the same decision-relevant structure, the candidate advantage disappears rather than being reframed as novelty.

The scope is deliberately narrow. Every primary result is exact-synthetic and frozen-seeded. Deterministic `LLM_PROXY_HEURISTIC` arms are heuristics, not measurements of any LLM. Hash-like identifiers in the transport world are model artifacts, not cryptographic security. No result demonstrates real-agent safety, real scientific productivity, or quantum-system performance.

## 2. Common experimental contract

All primary studies are stored under `research/extensions/orion-q/nlanes/`, with prospectively frozen protocols under `development/orion-q-nlane-closure/`. The companion `CLAIM_LEDGER.md` binds every number and limitation.

### 2.1 Matched information

For each study, all non-oracle arms receive the same serialized world state. The comparison changes **how the state is represented or consumed**, not which underlying facts are visible. A typed prior and a uniform prior, for example, operate on the same unknown edges and known observations; a scoped failure receipt and an unscoped failure memory refer to the same historical failure; full-chain and last-hop transport checkers receive the same serialized chain.

This parity is essential to the interpretation. We do not ask whether extra information helps. We ask whether an explicitly represented distinction—type, scope, chain position, decision relevance, or invalidation class—changes the decision made from the same information.

### 2.2 First right of refusal

Each world registers a strong alternative before result access. These include exact optimization on the known subgraph, the identical VOI planner with different state typing, random verification under the same budget, matched-budget re-derivation, an ideal VOI policy, and a parametric model-selection donor. A donor tie or win is an admissible endpoint. It is not repaired after the fact.

### 2.3 Hostile validity gates

Each primary world also contains a construction that should defeat a particular shortcut. Blind optimism must be punished in N4-A; always-reopen must fail in a regime where failures remain valid in N4-B; deep chain splices must defeat local/last-hop checking in N4-D; max-entropy decoys must attract pure information gain in N4-E; and the typed remint mechanism must reduce exactly to the controls when reminting is unnecessary in N4-F3. If these traps fail, the world is not considered evidence for the intended mechanism.

### 2.4 Determinism and authority

The N-lane studies use frozen generators and deterministic execution paths. The replay ledger records re-execution of the cited results. A deterministic replay establishes that the recorded computation can be regenerated; it does not establish external validity or novelty. Each receipt therefore carries an explicit bounded authority string.

## 3. Typed priors change what is worth probing

N4-A studies a layered interface graph in which unknown edge feasibility depends on an exposed interface type. Every non-oracle method receives the same graph, edge types, known outcomes, costs, and type-conditioned generator rates. The decision is whether to probe unknown edges before committing to a path.

`ORION_TYPED_VOI` uses the declared type-conditioned rates as priors inside a myopic value-of-information calculation. `PURE_VOI_UNIFORM` uses the **same VOI planner** but replaces the typed rates with a uniform 0.5 prior. Thus the isolation is not VOI versus no VOI; it is whether the state encodes which type of unknown is being considered.

Across the frozen 300 paired episodes, full oracle mean utility is 4.612. Typed VOI reaches 3.291 with 1.39 probes per episode, versus 2.180 for the identical uniform-prior planner and 0.358 for exact optimization restricted to the known subgraph. The latter abstains in 93.3% of episodes. Blind optimistic commitment reaches -13.619 with success rate 0.19, while the declared deterministic LLM-proxy heuristic reaches -12.306. The hostile optimism gate therefore bites in the direction required by the protocol.

The result does not show that typed priors are universally preferable, nor that an agent can learn the correct type. It shows that in this frozen world, the type label carries decision-relevant information that a matched planner loses when the same unknowns are flattened to one prior.

## 4. Scope determines when a failure should be reopened

N4-B turns from unknown feasibility to historical failure. An edge can carry a failure receipt bound to context coordinates such as representation version or access contract. The world also contains an irrelevant `NOISE` coordinate that changes frequently. A failure can become stale only when a coordinate in its recorded scope changes.

The four main policies are `ORION_SCOPED_REOPEN`, `NEVER_REOPEN`, `ALWAYS_REOPEN`, and `UNSCOPED_CHANGE_REOPEN`. The last policy has the same change observations but treats any changed coordinate, including `NOISE`, as a reason to reopen every failure.

Pooled mean utility is 3.199 for scope-bound reopening, 2.782 for never reopen, -7.813 for unscoped change reopening, and -9.225 for always reopen. The paired regimes explain the effect. When staleness matters, scope-bound reopening reaches 2.870 versus 2.096 for never reopen. In the hostile `REOPEN_WASTEFUL` regime, scope-bound reopening retains 3.528 versus 3.468 for never reopen, whereas always reopen falls to -13.406 and unscoped change reopening to -11.522 with failure-attempt rate 0.838.

The broad problem of stale memory is not novel to this paper; current agent-memory work studies implicit invalidation directly. The bounded point here is narrower: **a change event is not by itself a revocation event**. The state must say which dimensions the earlier failure depended on. Without that scope, the same evidence either remains stale too long or is discarded too aggressively.

## 5. Verification value depends on the decision boundary

N4-C studies path selection when edge cost and error are represented by intervals and only a fixed number of edges can be verified exactly. The baseline question is not whether verification helps—it does—but which uncertain edges should consume the budget.

`ORION_INTERVAL_PARETO` first identifies paths that survive interval-dominance filtering, then targets edges whose uncertainty participates in unresolved comparisons among those surviving paths. `RANDOM_VERIFY_MIDPOINT` spends the identical budget on random edges. Other controls optimize midpoints, worst cases, or best cases without targeted verification.

At budget `B=4`, mean scalarized regret is 0.1096 for the targeted method, with 76.5% zero-regret episodes. Random verification reaches 0.2518, midpoint optimization 0.2621, robust worst case 0.7755, and optimistic best case 1.2679. The mean dominance-survivor count is 23.12, satisfying the registered non-degeneracy gate.

We do not interpret these episodes as a population sample of real scientific domains. They are deterministic stress cases showing that an uncertainty representation becomes useful when tied to the **decision comparisons it can change**, rather than to uncertainty magnitude alone.

## 6. Transport authority is a chain property

N4-D asks whether evidence/certificates transported through a sequence of edits can be checked locally. The frozen dataset contains 200 honest chains and 200 laundering chains across three classes: missing interior receipt, spoofed summary of tier usage, and deep splice where individual hops appear legal but an interior input/output identity breaks the chain.

All checkers receive the same serialized chain. `ORION_CHAIN_TRANSPORT` validates every hop, recomputes the chain continuity and verifies that the maximum tier used remains within the allowed bound. It detects all 200 laundering chains and rejects none of the 200 honest chains: recall 1.000 and false-positive rate 0.000 in the exact synthetic model. Label matching and summary-tier checks have recall 0.000. Last-hop checking reaches 0.085 overall and 0.000 on all 68 deep splices.

This is not a cryptographic result. The synthetic model assumes that the per-hop receipt objects available to the checker are not themselves forged end to end. The result instead isolates a structural point: **a certificate that is locally valid at the final hop can be globally unsupported because the authority to transport it is path-dependent.**

## 7. Information can be high-entropy and decision-irrelevant

N4-E studies the choice of the next experiment under a shared stopping rule. The world contains deliberately high-entropy decoy facts whose outcomes do not affect the decision. Pure information gain is therefore offered an attractive but irrelevant target.

The decision-coupled selector reaches mean utility 9.266 with 2.71 probes per episode. Pure information gain reaches 7.121; cheapest-first 8.075; random 7.568; the declared deterministic LLM proxy 8.989. All arms have commit accuracy 1.0, so the comparison is about experiment selection, not whether a final answer can eventually be found.

The hostile decoy behaves as designed: pure information gain spends 36.6% of its probes on decoys, while the decision-coupled method spends none. This does not establish a new theory of active learning. It establishes that in this world, the state must distinguish **uncertainty that can change the decision** from uncertainty that merely has high entropy.

## 8. Typed invalidation decides whether to remint or reuse

N4-F3 studies representation edits. A receipt may transport soundly, require reminting, or become invalid. `ORION_TYPED_REMINT` uses the registered typed invalidation rule to decide which state can be carried forward. Controls either re-derive within the same budget or carry state forward naively.

In `MIXED_TRANSPORT`, typed remint/transport reaches mean utility 9.421 versus 7.157 for matched-budget re-derivation and -7.821 for naive carry-forward. Pooled values are 7.286, 6.439 and -3.976 respectively. Across 14,400 receipts, the registered rule records zero invalidation mismatches and zero infeasible commits.

The hostile first-right-of-refusal regime is equally important. In `REMINT_UNNECESSARY`, all four arms tie **exactly** at 11.809659685355605 and ORION performs zero remints. The mechanism therefore earns no artificial benefit when the typed state says that nothing needs to change.

## 9. Two donor absorptions bound the thesis

A mechanism programme needs cases where the candidate does **not** survive first right of refusal.

### 9.1 Typed failure state without policy novelty

N1-C asks whether typed scoped failure state helps under a binding verifier budget. The typed state has a paired solve-rate delta of +0.0271 over an unscoped ablation, with bootstrap 95% interval `[0.0248, 0.02955]`; false escalation is 0.0 versus 0.6959. But the allocation policy itself is exactly matched by an ideal VOI donor given the same typed facts: paired delta 0.0, identical solve rate 0.9866. The permitted interpretation is therefore about **state as decision information**, not a novel verification-allocation policy.

### 9.2 Crossover prediction absorbed on its original world

N2-F5B compares a candidate crossover predictor to a stronger model-selection donor. On the original world, both reach 0.9948 and the candidate residual is absorbed. A bounded difference survives only in the frozen misspecified world: 0.9844 versus 0.9531, with crossover relative error 0.084 versus 0.441. We retain the donor tie as the primary boundary; the misspecification result is not evidence that the original novelty claim survived.

These negatives are consequential. They show that the paper's rule is not “typed state wins.” It is “give the strongest alternative the same information; if it closes the mechanism, give it the credit.”

## 10. Synthesis: responsibility determines the required state distinction

The six positive studies look heterogeneous if described by their algorithms: VOI, reopening, Pareto verification, provenance checking, active selection, reminting. Their shared object is easier to see from the downstream responsibility.

| Responsibility | Missing distinction in the hostile control | Consequence |
|---|---|---|
| choose what unknown to probe | type-conditioned feasibility | probes allocated to the wrong unknowns |
| decide whether a failure still applies | dependency scope of the receipt | stale failures persist or valid failures are reopened |
| spend a verification budget | whether uncertainty can change the choice | verification is spent away from the decision boundary |
| accept transported evidence | chain-level support/continuity | local validity launders a broken interior dependency |
| choose next experiment | decision relevance of uncertainty | entropy attracts decoys |
| reuse state after an edit | typed invalidation / transportability | either stale carry-forward or wasteful re-derivation |

Thus the paper does not propose one universal type system. It identifies a recurring pattern: **state is sufficient only relative to the responsibility that consumes it.** The exact type/scope fields differ because the downstream responsibility differs.

This interpretation also explains why broad neighboring work is donor-owned rather than contradicted. STALE asks whether a memory is still current; context governance asks which versioned artifacts are eligible and attributable; VOI asks which observation is worth purchasing. Q4 uses these ideas as building blocks and asks whether their relevant distinctions remain necessary under matched-information controls across different responsibilities.

## 11. Reproducibility and reporting

All result-bearing families are tied to frozen protocol and result receipts under the repository paths named in `CLAIM_LEDGER.md`. The primary N-lane studies use seed `20260821` and deterministic runners. `development/orion-q-nlane-closure/REPLAY_VERIFICATION_LEDGER.md` records replay status; the N4-F3 result was separately replayed during manuscript assembly according to the claim ledger.

A final submission package should expose:

- the exact repository commit corresponding to the manuscript;
- protocol files and generator/runner code;
- committed result receipts;
- a one-command or explicitly enumerated replay path;
- a generated-data statement distinguishing synthetic worlds from any external source;
- code/data availability statements that do not invent a DOI or archive identifier before an actual deposit exists.

Figures and tables must be regenerated from receipt values rather than copied from prose. A publication archive, if created, is a submission operation and does not change the scientific authority of the underlying result.

## 12. Limitations

**Constructed worlds.** The studies are authored to isolate specific distinctions. Their strength is causal/mechanistic clarity, not ecological validity. We do not know how frequently the same distinctions dominate natural research workflows.

**No real LLM evaluation.** `LLM_PROXY_HEURISTIC` arms are deterministic baselines. They cannot support claims about frontier model capabilities or failures.

**Typed information is supplied.** The experiments ask whether a distinction is useful once represented; they generally do not solve the harder problem of learning the correct type/scope from raw unstructured evidence.

**Security boundary.** N4-D is not a cryptographic or hostile-system security study. Receipt forgery and compromised roots of trust are outside the model.

**Rule soundness.** Some transport/invalidation rules are constructed to be sound in their synthetic world. The experiment tests the value of exposing/using the rule, not whether the rule would be sound in every domain.

**Episode independence.** Large episode counts should not be read as thousands of independent scientific domains. Where inferential statistics are reported, they apply only under the registered experimental unit and procedure; otherwise results are descriptive properties of the frozen generated worlds.

**Scope-specific omissions.** N4-B excludes within-episode accumulation of new failure receipts. N4-C reports scalarized regret rather than full-front hypervolume. N4-F3 uses the registered remint cost model. These restrictions remain part of the claim.

## 13. Related-work boundary

Three neighboring areas are particularly important.

**Agent memory and state revision.** STALE (Chao et al., 2026, arXiv:2605.06527) makes implicit stale-memory invalidation a direct benchmark problem. Sun and He (2026, arXiv:2608.01619) study repairing implicit stale dependencies by auditing from updated state into drafted behavior. Q4 therefore claims neither stale-memory detection nor belief retirement as a primitive.

**Context governance and provenance.** ContextNest (Sulpovar et al., 2026, arXiv:2607.02116) formalizes governed, versioned, attributable context selection for autonomous agents. Provenance and version identity are donors here. Q4's bounded residual concerns which scoped distinctions are required by *different downstream responsibilities*, including but not limited to retrieval eligibility.

**Decision-theoretic information acquisition.** VOI, active learning, robust decision making and Pareto/interval methods are established machinery. Our experiments intentionally give these donors first right of refusal; N1-C demonstrates an exact case where an ideal VOI donor eliminates policy novelty.

The final novelty sentence should be frozen only after a submission-date primary-source search over these families. This manuscript therefore avoids “first” or field-wide uniqueness claims.

## 14. Conclusion

Across six prospectively frozen exact-synthetic worlds, explicit type and scope are load-bearing when a downstream research responsibility requires distinctions that matched-information controls discard. The same pattern appears in what to probe, which failure remains applicable, what to verify, whether evidence can be transported, which uncertainty matters to an experiment, and when state should be reminted. Crucially, the programme also contains cases where a stronger donor closes the purported novelty or every arm ties exactly.

The durable conclusion is consequently modest but useful: **partial knowledge is not interchangeable merely because its factual content is the same; what a research process may safely or efficiently do with that knowledge can depend on type, scope, dependency and responsibility.** Whether that mechanism improves real research agents remains a separate empirical question.
