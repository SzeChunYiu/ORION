# Epistemic Bindings for Scientific Decisions: A Matched-Information Benchmark Suite

**Recursively refined V3 — 2026-08-22**  
**Stretch after real-domain transfer:** Nature Machine Intelligence  
**Current target:** npj Artificial Intelligence / AI-for-science methods venue

## Abstract

Scientific agents do not only store facts; they reuse failures, certificates, uncertain resource estimates and observations whose value depends on where they apply and whether they can change a downstream decision. We study whether that **epistemic binding** matters when visible factual information is held fixed. Six prospectively frozen exact-synthetic families compare typed/scoped decision mechanisms with matched-information controls and strong donor methods. We organize these separately preregistered studies into a post-study benchmark taxonomy spanning type-conditioned priors, applicability scope, decision-relevant uncertainty, transformation lineage, decision-coupled acquisition and remint obligations.

The frozen families exhibit complementary effects and null regimes. Type-conditioned value-of-information (VoI) achieves mean utility 3.291 versus 2.180 for the same VoI planner with a uniform prior. Scope-bound reopening remains robust when irrelevant context changes trap unscoped reopening. Pareto-ambiguity-targeted verification reduces mean scalarized regret from 0.252 for matched-budget random verification to 0.110. Full-chain transport catches all 200 registered laundering chains, including 68 deep splices, with zero false positives on 200 honest chains, whereas last-hop checks miss the deep attacks. Decision-coupled acquisition spends no probes on decision-irrelevant high-entropy decoys, compared with 36.6% for pure information gain. Typed remint/transport improves utility in a mixed-transport regime, while all correct methods tie exactly in the preregistered regime where reminting is unnecessary. Two additional donor comparisons prevent broader policy claims.

The contribution is not a priority claim for typed memory, provenance, stale-state handling or VoI. It is a controlled benchmark hypothesis: **the same scientific facts can license different decisions when applicability, uncertainty, lineage and decision-role relations are explicit rather than flattened**. The six families remain heterogeneous and are not pooled into one universal effect size. A secondary publication analysis reruns the original frozen seeds to report paired episode-level contrasts and bootstrap uncertainty without changing any primary terminal. All headline evidence is synthetic; real scientific-agent transfer remains an explicit evidence gap governed by a separately frozen protocol.

---

## 1. Scientific state is more than a bag of facts

A long-lived research workflow accumulates statements such as:

- a candidate failed under representation version 3;
- a certificate is valid only while two assumptions remain unchanged;
- a resource coordinate is known only within an interval;
- a previous negative applies to one method grammar but not a later representation edit;
- an observation is uncertain but cannot alter the current scientific choice;
- evidence can cross one transformation only if a remint obligation is discharged.

These statements contain factual content and a second layer describing **role, applicability, uncertainty, lineage and decision relevance**. Modern agent-memory systems increasingly represent provenance, temporal supersession and typed content explicitly, and VoI is already a well-established decision principle. The open question in this paper is therefore not whether agents should have structured memory.

We ask instead:

> **When visible facts are matched, which scientific decisions actually depend on explicit epistemic bindings, and which strong baselines can absorb the benefit?**

The six frozen studies were developed separately to isolate different decision failures. V3 organizes them into one benchmark taxonomy after the fact. This synthesis is theory-building, not a claim that one six-family theorem was preregistered.

---

## 2. A common benchmark contract

`BENCHMARK_INDEX_V1.json` records each family using the same publication-level fields:

- binding axis;
- downstream scientific decision;
- treatment arm;
- strongest primary comparator;
- oracle where applicable;
- hostile or no-value control;
- primary metric;
- frozen seed/generator/result;
- exact claim boundary.

### 2.1 Matched information

Within each family, non-oracle primary arms receive the same frozen factual world. The treatment changes the declared metadata used by the decision rule, not the amount of hidden truth supplied to it.

### 2.2 Donor first right of refusal

A typed mechanism receives no special credit when a strong planner using the same information matches it. This rule is visible in the positive and negative results: for example, N1-C supports the value of typed failure state while an ideal VoI donor absorbs the allocation policy itself.

### 2.3 Hostile and no-value regimes

Every mechanism has a prespecified place where a plausible shortcut should fail or the typed coordinate should add no value. Examples include irrelevant `NOISE` changes, high-entropy decision-irrelevant decoys, deep lineage splices and a remint-unnecessary regime. A mechanism that “wins everywhere” would fail these controls.

### 2.4 Statistical reporting

The frozen result receipts remain the primary scientific record. For stochastic episode generators, `publication_analysis.py` deterministically rebuilds the original seeded episodes and computes paired treatment-comparator differences plus percentile-bootstrap intervals. This is secondary reporting only: it changes no seed, generator, arm, metric, gate or terminal. N4-D is an exact constructed-chain census and is reported by counts rather than Monte-Carlo uncertainty.

---

## 3. Six epistemic-binding axes

| Axis | Decision problem | Frozen family | Key control |
|---|---|---|---|
| type prior | what prior should an unknown scientific interface receive? | N4-A | identical VoI with uniform prior |
| applicability scope | does an old failure still license closure? | N4-B | irrelevant context changes |
| decision-relevant uncertainty | which unknown should consume verification budget? | N4-C | matched-budget random verification |
| transport lineage | does evidence survive a transformation chain? | N4-D | deep splice vs last-hop check |
| decision coupling | which observation can change the action? | N4-E | high-entropy decoys |
| remint obligation | reuse, remint or rederive after an edit? | N4-F3 | remint-unnecessary exact tie |

The axes are related by a common question: **what relation between a fact and the current decision would be lost if the state were flattened?**

---

## 4. Type-conditioned priors change otherwise identical VoI decisions

N4-A uses a layered research-interface graph whose unknown edge-feasibility rates depend on declared interface type. The typed arm and the primary control run the same myopic VoI algorithm over the same graph, known facts, costs and action set. The control replaces type-conditioned feasibility priors with a uniform 0.5 prior.

Across 300 frozen episodes:

- full oracle mean utility: 4.612;
- typed-prior VoI: 3.291;
- uniform-prior VoI: 2.180;
- known-graph-only: 0.358.

The result does not establish a new VoI algorithm. It demonstrates that declared type information changes the value of an otherwise identical acquisition calculation in this world.

---

## 5. Applicability scope prevents both stale reuse and pointless reopening

N4-B binds a failure receipt to context coordinates such as representation and access contract. A `NOISE` coordinate changes frequently but does not affect the truth of the recorded failure.

The scoped rule reopens only if a coordinate inside the recorded applicability scope changes. Controls never reopen, always reopen or reopen on any change.

Pooled mean utility is 3.199 for scoped reopening versus 2.782 for never reopening, -7.813 for unscoped change reopening and -9.225 for always reopening. The `REOPEN_WASTEFUL` hostile regime is essential: relevant coordinates almost never change while `NOISE` changes frequently, so unscoped and always-reopen rules incur large unnecessary costs.

The mechanism is narrower than stale-memory detection. The scientific question is which state change was actually part of the old failure's validity conditions.

---

## 6. Uncertainty matters when it blocks the decision

N4-C assigns interval-valued cost/error coordinates to candidate paths and gives each arm a verification budget of four edges. The treatment targets edges contributing to unresolved Pareto ambiguity; the primary comparator verifies four random edges and then uses the same midpoint estimator.

Mean scalarized regret is 0.1096 for the targeted method versus 0.2518 for random verification, with 76.5% zero-regret outcomes for the targeted arm. The publication analysis reports the corresponding paired regret reduction and interval over the same 400 seeded episodes.

The result is not a general active-verification theorem and the scalarized regret does not replace full Pareto analysis. It isolates one decision-specific use of uncertainty: verify what can change the ranking, not merely what is wide.

---

## 7. Evidence validity is a path property

N4-D constructs honest and laundering transformation chains. Some invalid evidence is spliced deeper in the chain while the final hop remains superficially consistent.

Full-chain typed transport detects 200/200 laundering chains, including all 68 deep splices, with 0/200 false positives on honest chains. The last-hop rule detects only 8.5% of the registered laundering set and none of the deep splices.

This is an exact synthetic lineage result, not a cryptographic-security claim. Hashes and transformation identities are controlled by the world generator. The mechanism claim is simply that validity after a sequence of representation edits cannot generally be inferred from the final label alone.

---

## 8. Information gain can spend budget on facts that cannot matter

N4-E gives all probing arms the same priors and the same stopping rule: continue while at least one unknown fact has positive myopic net VoI. Only the **next fact selection** changes.

Two facts are deliberately constructed as high-entropy but decision-irrelevant decoys. Pure information gain spends 36.6% of probes on them; the decision-coupled selector spends zero. Mean utility is 9.266 for decision-coupled selection versus 7.121 for information gain and 8.989 for the deterministic `LLM_PROXY` heuristic.

Again the claim is not that VoI or active learning is new. The experiment isolates a distinction between uncertainty reduction and expected decision change.

---

## 9. Reminting should help only when transport metadata has value

N4-F3 studies evidence reuse after two representation edits under a shared certification budget.

In `MIXED_TRANSPORT`, typed remint/transport achieves mean utility 9.421 versus 7.157 for matched-budget re-derivation and -7.821 for naive carry-forward. In `STALE_HOSTILE`, naive carry-forward is deliberately punished. The crucial first-right-of-refusal condition is `REMINT_UNNECESSARY`: every correct method ties exactly in the frozen output and the typed method spends zero remints.

The exact result receipt retains full precision; the manuscript reports rounded values because the extra decimals carry no scientific meaning.

---

## 10. Donor absorptions delimit the common story

Two neighboring studies are included because they prevent an over-broad synthesis.

**Typed failure state versus verification policy.** N1-C finds that scoped failure state improves decisions relative to an unscoped state, but an ideal VoI donor given the same typed facts reproduces the allocation policy. The residual is about decision state, not an ORION-specific planner.

**Crossover prediction under model misspecification.** N2-F5 appears positive against its first baselines; a stronger model-selection donor later closes the well-specified-world advantage. Candidate value survives only in a deliberately misspecified regime.

These absorptions are not side notes. They define where “epistemic structure matters” stops being “this policy is new.”

---

## 11. A theory-building synthesis

The six studies suggest the following bounded design principle:

> Scientific state should preserve relations that determine whether a fact is applicable, transportable, decision-relevant or worth resolving; flattening those relations can change the decision even when the visible factual payload is unchanged.

This is a hypothesis generated by the suite, not a proved minimal schema. The experiments do not establish that all six axes are independent, necessary or sufficient. They provide controlled failure modes for a future real-domain benchmark.

A practical implication is that agent-memory evaluation should not be limited to recall. A system can remember the right sentence and still use it incorrectly because the validity scope, transformation history or decision role has been lost.

---

## 12. Relation to prior work

Typed/provenance-aware memory, stale-memory revision and governed persistent memory are active topics; VoI is classical and has also been applied directly to agent communication/planning. Q4 therefore makes no priority claim for those primitives.

The narrower experimental delta is the **matched-information scientific-decision design**: hold the factual world fixed, perturb whether a declared epistemic relation is represented/used, require a hostile or no-value control, and give a strong donor first right of refusal.

The benchmark index makes that contract reusable across the six families rather than treating the manuscript as a collection of unrelated synthetic wins.

---

## 13. Real-domain transfer is the remaining evidence gate

All headline primary studies are synthetic by design. That provides exact truth and clean mechanism isolation but creates a simulation-to-reality gap. The registered successor therefore freezes a matched-information study over real research decisions: reopen a negative, verify an uncertain resource, transport evidence, choose a Pareto-relevant measurement, or select a decision-relevant experiment.

Until that study exists, the paper does not claim real scientific-agent effectiveness. This blocks the Nature Machine Intelligence stretch target but does not invalidate the current mechanism/benchmark contribution.

---

## 14. Code, data and benchmark availability

The six frozen generators, result receipts, protocols, machine-readable `BENCHMARK_INDEX_V1.json`, publication analysis script and reproduction instructions are committed in the ORION repository. Before journal publication, a tagged release should be deposited in a DOI-minting repository and the permanent identifier inserted here. The minimum dataset consists of the frozen result JSON files plus the benchmark index; the generators reproduce the stochastic synthetic worlds from fixed seeds.

## AI-assisted research and writing disclosure

ORION and language-model tooling were used to execute/audit research and recursively refine this manuscript. They are not authors and grant no scientific or novelty authority. Human authors remain responsible for research design, claims, interpretation, references and submitted text. Final disclosure wording should follow the target journal's current policy.

---

## Current evidence boundary

This manuscript may claim a six-family **exact-synthetic matched-information mechanism benchmark** and the post-study epistemic-binding taxonomy above. It may not claim real-agent transfer, first invention of typed memory/provenance/VoI, cryptographic security, a universal effect size, or a minimal/complete scientific-state schema.
