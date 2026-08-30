# Epistemic Bindings for Scientific Decisions: A Matched-Information Benchmark Suite

**ORION-08 publication master — 2026-08-29**  
**Bounded target:** Transactions on Machine Learning Research (TMLR)  
**Evidence class:** exact-synthetic mechanism benchmark with donor-owned decision-sufficiency theory  

## Abstract

Scientific agents do not only store facts; they reuse failures, certificates, uncertain resource estimates, and observations whose value depends on where they apply and whether they can change a downstream decision. We study whether these **epistemic bindings** matter when visible factual information is held fixed. Six separately frozen exact-synthetic families compare typed or scoped decision mechanisms with matched-information controls and strong donor methods. Type-conditioned value-of-information reaches mean utility 3.291 versus 2.180 for the same planner with a flattened prior. Scope-bound failure reopening avoids severe over-reopening under irrelevant context changes, while its advantage over conservative never-reopen is not cleanly separated within either frozen regime. Pareto-ambiguity-targeted verification reduces mean scalarized regret from 0.2518 to 0.1096 at the same verification budget. Full-chain transport checking detects all 200 registered laundering chains with zero false positives on 200 honest chains. Decision-coupled acquisition reaches mean utility 9.266 versus 7.121 for pure information gain while spending no probes on registered entropy decoys. Typed remint/transport reaches 9.421 versus 7.157 for matched-budget re-derivation in the mixed-transport regime and ties exactly when reminting is unnecessary. An exact donor-owned fibre criterion clarifies when any readable binding can support zero regret: every positive-mass fibre must share an optimal action; refinement cannot increase Bayes risk and helps only by separating action-incompatible worlds. Its ORION-specific instantiation shows that two supported families can close very different fractions of the available decision gap (7.6% versus 98.4%). Recent stale-memory, provenance-sensitive, and budgeted-verification studies now occupy important neighboring territory, so we make no priority claim for typed memory, provenance, stale-state handling, matched verification budgets, random verification controls, or value of information. The residual contribution is a controlled cross-family benchmark of **mechanism isolation at matched information**, with exact decision-sufficiency interpretation and explicit no-value regimes. All headline evidence is synthetic; real scientific-agent effectiveness remains untested.

## 1. Scientific state is more than a bag of facts

A long-lived research workflow accumulates statements such as: a candidate failed under a particular representation; a failure receipt remains applicable only while named coordinates are unchanged; a resource is known only within an interval; a certificate has been transported through several edits; or an observation is uncertain but cannot alter the current decision. These statements contain factual content and a second layer describing **role, applicability, uncertainty, lineage, and decision relevance**.

Value-of-information methods ask which observation is worth purchasing. Database and workflow provenance records how results were derived. Modern agent-memory systems increasingly track stale state, provenance, versions, and governance. The question here is therefore not whether structured memory or provenance is useful in general. It is narrower:

> **When the visible factual payload is matched, which downstream scientific decisions depend on an explicit binding relation, and which strong baselines absorb the benefit?**

The six studies were frozen separately to isolate different decision failures. Their synthesis into one benchmark taxonomy is post-study theory building; we do not claim that a six-family universal theory was preregistered.

## 2. Common experimental contract

### 2.1 Matched visible information

Within each primary comparison, non-oracle arms receive the same serialized world facts. The treatment changes how a declared relation is represented or used, not how much hidden truth is supplied. Examples include keeping versus flattening a type-conditioned prior, retaining versus deleting a failure receipt's dependency scope, or checking a whole evidence path rather than only its final hop.

### 2.2 Donor first right of refusal

A candidate receives no special credit when a strong donor using the same information matches it. A tie or donor win is an admissible endpoint. This rule is load-bearing in the two donor-absorption studies described below.

### 2.3 Hostile and no-value regimes

Every positive mechanism has a prespecified place where a plausible shortcut should fail or where the binding should add no value. Examples include irrelevant `NOISE` changes, high-entropy decision-irrelevant decoys, deep lineage splices, and a remint-unnecessary regime. A mechanism that appeared to win everywhere would fail these controls.

### 2.4 Statistical unit and evidence class

The primary worlds are exact-synthetic stress tests under frozen generators. Generated episodes are not samples from a population of real laboratories or deployed agents. Stochastic-family uncertainty is reported with paired analyses at the generated-unit level. N4-D is an exact constructed-chain census and is reported by counts rather than a population-style p value. Replay establishes determinism, not independent scientific replication.

## 3. A donor-owned decision-sufficiency criterion

Let world state `x` carry a readable binding `B(x)` and let `A*(x)` denote the set of optimal actions. A policy that reads only `B` must choose one action for every fibre induced by the binding.

A deterministic zero-regret policy using only `B` exists **if and only if every positive-mass fibre has a common optimal action**. If `B'` refines `B`, the optimal Bayes risk under `B'` cannot be larger because every `B`-measurable policy is also `B'`-measurable. A refinement has value only when it separates worlds whose optimal-action sets are incompatible.

This is donor-owned decision-sufficiency / comparison-of-experiments theory; we do **not** claim the criterion or refinement monotonicity as an ORION invention. The ORION-specific contribution is its exact instantiation on the frozen benchmark receipts. An independent checker exhaustively verifies the criterion and monotonicity over 2,233,980 finite world/action/binding configurations and then reads the N4 receipts as data. In N4-B, scoped reopening closes 7.6% of the strongest baseline's oracle gap; in N4-F3, typed transport closes 98.4% of the naive baseline's gap and 81.9% of the strongest non-oracle baseline's gap. Thus a `SUPPORTED` direction does not imply a large or sufficient binding.

## 4. Type-conditioned priors change otherwise identical VoI decisions

N4-A uses a layered research-interface graph whose unknown edge-feasibility rates depend on a declared interface type. The typed arm and its primary control run the same myopic value-of-information planner over the same graph, known facts, costs, and action set; the control replaces type-conditioned feasibility priors with a uniform prior.

Across 300 frozen episodes, full-oracle mean utility is 4.612. Typed-prior VoI reaches 3.291, compared with 2.180 for the identical uniform-prior planner and 0.358 for exact optimization restricted to the known subgraph. The paired typed-minus-uniform mean difference is 1.111 with bootstrap 95% interval [0.833, 1.400]. The result is not a new VoI algorithm; it shows that a declared type can alter an otherwise identical acquisition calculation in this constructed world.

## 5. Applicability scope prevents over-reopening

N4-B binds a failure receipt to the context coordinates on which that failure depends. A `NOISE` coordinate changes frequently but does not affect the truth of the recorded failure. The scoped rule reopens only after a coordinate inside the recorded applicability scope changes. Controls never reopen, always reopen, or reopen after any change.

Pooled mean utility is 3.199 for scoped reopening, 2.782 for never reopen, -7.813 for unscoped change reopening, and -9.225 for always reopen. The paired regime-level analysis gives the important boundary: relative to unscoped reopening, scoped reopening improves mean round utility by 6.973 [5.740, 8.255] in `STALE_MATTERS` and 15.050 [13.624, 16.451] in `REOPEN_WASTEFUL`; relative to never reopen, however, the intervals include zero in both regimes (0.774 [-0.663, 2.254] and 0.060 [-0.540, 0.634]).

The retained claim is therefore not “scoped reopening always beats never reopening.” It is that explicit applicability scope prevents severe over-reopening driven by irrelevant changes while remaining compatible with conservative behavior in these frozen panels.

## 6. Decision-relevant uncertainty changes verification value

N4-C gives every arm the same interval-valued cost/error state and the same budget of four exact verifications. The candidate prioritizes uncertainty participating in unresolved comparisons among Pareto-surviving alternatives; the matched control verifies randomly and then uses the same midpoint estimator.

Mean scalarized regret is 0.1096 for targeted verification and 0.2518 for random verification. The paired regret reduction is 0.142 with bootstrap 95% interval [0.100, 0.187], and the candidate has zero regret in 76.5% of episodes. This is not a general active-learning theorem and, in light of recent work, not a priority claim for matched-budget verification or a random control. The bounded result is that the registered decision-boundary relation changes which uncertainty is worth resolving in this construction.

## 7. Evidence validity can be a path property

N4-D contains 200 honest and 200 hostile transport chains. Hostile classes include missing interior receipts, spoofed summary tiers, and deep splices whose final hop looks locally legal while an interior input/output identity breaks the chain.

Full-chain checking detects all 200 registered hostile chains and rejects none of the 200 honest chains. Label matching and summary-tier checking have zero recall; last-hop checking reaches 0.085 overall and zero on all 68 deep splices. This is not a cryptographic-security claim. The synthetic model assumes the declared receipt objects are available to the checker. The structural claim is only that authority to reuse or transport a result can depend on its support path rather than the final label alone.

## 8. Information gain can spend budget on facts that cannot matter

N4-E gives all probing arms the same priors and stopping rule and adds high-entropy decoys that cannot change the decision. Pure information gain spends 36.6% of probes on those decoys; the decision-coupled selector spends none.

Mean utility is 9.266 for decision-coupled selection, 7.121 for pure information gain, 8.075 for cheapest-first, 7.568 for random, and 8.989 for the declared deterministic `LLM_PROXY` heuristic. The paired difference against information gain is 2.146 [1.976, 2.299]; against the stronger proxy it is much smaller, 0.277 [0.119, 0.412]. The result isolates a distinction between uncertainty reduction and expected decision change rather than claiming novelty for value of information.

## 9. Reminting helps only when transport metadata has value

N4-F3 studies evidence reuse after representation edits under a shared certification budget. In `MIXED_TRANSPORT`, typed remint/transport reaches mean utility 9.421 versus 7.157 for matched-budget re-derivation and -7.821 for naive carry-forward. The paired utility difference is 2.264 [1.717, 2.825] against re-derivation. In the preregistered `REMINT_UNNECESSARY` regime, typed transport and re-derivation tie exactly: 0.000 [0.000, 0.000] over all 200 episodes.

This no-value regime is central. A useful binding mechanism should disappear where its metadata cannot affect the action.

## 10. Donor absorptions delimit the common story

Two neighboring studies prevent an over-broad synthesis. In N1-C, scoped failure state improves decisions relative to an unscoped state, but an ideal VoI donor given the same typed facts exactly reproduces the allocation policy. The residual is about decision state, not an ORION-specific planner. In N2-F5, a stronger model-selection donor absorbs the well-specified-world crossover-prediction advantage; candidate value survives only in a separately frozen misspecified regime.

These are not side notes. They show that the pipeline can return “donor sufficient” rather than forcing every study into a positive novelty story.

## 11. Current nearest-work boundary

The 2026 neighborhood is substantially denser than the earlier manuscript implied. **STALE** studies whether agents recognize and act on invalidated memory. **ContextNest** treats governed, versioned, provenance-bearing context as infrastructure. **MAP-Graph** represents provenance in a typed execution graph with ancestry, permission filtering, path trust, and action gating. **Provenance-sensitivity auditing** directly varies source authority as an action signal. **Governance decay** and **omission-vs-commission constraint decay** show that long-horizon state can lose or asymmetrically preserve governing constraints. Most importantly, **Nakayashiki's budgeted verification study of inherited stale constraints** holds the factual payload fixed across policy comparisons, uses the same verification budget in every arm, includes a random-record control, and scores actions deterministically.

These papers remove several claims the benchmark should not make. ORION-08 does not claim priority on typed memory, provenance-aware memory, stale-memory evaluation, versioned context, matched verification budgets, random verification controls, or provenance-sensitive action. The closest new parent is Nakayashiki because it shares the matched-payload, matched-budget, control, and deterministic-scoring design commitments.

The remaining distinction is the object being identified. Nakayashiki estimates behavioral rates in a sampled agent study and explicitly does not identify mediation. ORION-08 uses constructed finite worlds to isolate the relation that is removed or retained and combines those worlds with the exact common-optimal-action fibre criterion. The residual contribution is therefore **exact mechanism isolation and cross-family composition**, not priority on the underlying primitives or experimental controls.

## 12. Relation to provenance/context governance and ORION-23

ORION-08 assumes that relevant context can be identified, serialized, and compared under exact rules. Database and workflow provenance, ContextNest, MAP-Graph, and related governance systems own substantial infrastructure for version identity, provenance, selection, and reconstructable history. The benchmark asks a downstream question: once state is available, which distinctions are required by the next responsibility?

The paper is also narrower than ORION-23. ORION-23 develops a more general responsibility-scoped sufficiency and recovery framework. ORION-08 supplies bounded exact-synthetic mechanism evidence and an instantiation of donor-owned decision-sufficiency theory. It does not claim the general responsibility-scoped principle as its unique theoretical novelty.

## 13. Cross-study synthesis

The six primary families differ in algorithms and outputs but share one question: what relation between a fact and the current decision would be lost if state were flattened?

| Downstream responsibility | Binding used | Matched shortcut tested |
|---|---|---|
| choose which unknown to probe | interface/type-conditioned feasibility | flatten unknowns to one prior |
| decide whether an old failure still applies | dependency scope | reopen on any change / never reopen |
| spend verification budget | decision-relevant uncertainty | verify randomly at the same budget |
| accept transported evidence | full-chain support/continuity | trust summary/label/last hop |
| choose the next experiment | expected decision change | maximize entropy alone |
| reuse state after a representation edit | transport/invalidation type | rederive everything or carry everything forward |

The commonality is not a universal type system. It is a benchmark design criterion: preserve distinctions that can separate action-incompatible worlds, and require a no-value or donor regime that demonstrates when the distinction is unnecessary.

## 14. Reproducibility and statistical reporting

Each primary world is generated from a frozen protocol and deterministic code. The publication evidence includes generators, seeds, result receipts, benchmark index, paired-analysis receipt, and replay instructions. The recent literature/replay closure independently rechecked the registered publication targets; replay verifies reproducibility of the bound computations rather than external scientific replication.

The six studies are not pooled into a single p value or universal effect size. They have different outcomes and scales. N4-D is an exact finite battery rather than an IID sample from a real adversary population. The exact fibre checker uses integer arithmetic and treats `CANNOT_CHECK` as a non-pass state.

## 15. Limitations

**Exact-synthetic evidence.** No primary result is a real-agent, real-laboratory, or deployment study.

**Bindings are supplied.** The studies generally assume the relevant type/scope facts exist. They do not show that an agent can infer the right binding automatically.

**Donor-owned theory.** The common-optimal-action criterion and refinement monotonicity are not claimed as novel. Their role is to interpret the frozen ORION receipts.

**Recent neighbors absorb broad novelty.** Current agent-memory, provenance, governance, and budgeted-verification work owns important primitives and controls that earlier drafts could have described too broadly.

**Constructed hostile regimes.** Hostile controls are designed to exercise the target distinction; they are not prevalence estimates.

**No security claim.** The transport family is a synthetic provenance mechanism, not evidence of cryptographic security against real attackers.

**No universal schema.** The six families need different binding coordinates because their downstream responsibilities differ.

## 16. Conclusion

Across six separately frozen exact-synthetic studies, the same factual payload can license different decisions when applicability, uncertainty, lineage, and decision-role relations are preserved rather than flattened. Strong donors and no-value regimes show that those relations do not always help. An exact donor-owned fibre criterion provides the clean interpretation: a readable binding is sufficient only when every fibre admits a common optimal action, and refinement has value only when it separates action-incompatible worlds. On the frozen ORION receipts, supported mechanisms range from closing only 7.6% of a baseline oracle gap to closing 98.4%, reinforcing that direction and magnitude are different claims.

The paper therefore makes a bounded contribution: a matched-information mechanism benchmark and cross-family experimental contract for studying epistemic bindings. It does not establish real scientific-agent effectiveness, first invention of typed memory or provenance, cryptographic security, a universal effect size, or a minimal complete scientific-state schema. Real-domain transfer remains successor work rather than a condition for reporting the bounded benchmark honestly.

## AI assistance disclosure

General-purpose language-model tools, including OpenAI ChatGPT, were used for literature triage, code and manuscript auditing, organization, and language refinement. Scientific claims, citations, analyses, and final text were checked against the underlying evidence by the human author, who retains full responsibility. The tools are not authors and are not treated as scientific authority or independent verification.
