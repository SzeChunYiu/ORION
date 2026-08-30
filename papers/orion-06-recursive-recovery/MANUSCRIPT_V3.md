# Recursive Recovery of Negative Quantum Results: An Auditable Successor Protocol for Research Programmes

**ORION-02 Manuscript V3 — publication draft**  
Scientific cut: `main@ca7df1055a43f97eaf8d142a62011c4c261af368`  
Foundation: `PUBLICATION_FOUNDATION_V2.md`  
Graph: `Q2_TRANSITION_GRAPH_V2.json`  
Declared receipt denominator: `Q2_ELIGIBLE_RECEIPT_INVENTORY_V1.json`

## Abstract

Scientific-agent systems increasingly preserve code, evidence chains and execution traces, but provenance alone does not determine what a research programme should do after a prospectively frozen hypothesis is refuted, absorbed by prior work or left `CANNOT_CHECK`. We present a bounded longitudinal case study of an executable **negative-result successor discipline** used in the ORION-Q quantum-compilation programme. Each research node retains its frozen claim, result receipt and disposition. A successor edge is admitted only when the predecessor outcome localizes a scientifically relevant responsibility, the strongest located donor receives first right of refusal, and a new protocol is frozen before its outcome. Later success never rewrites the predecessor. A complementary claim-preserving recovery theorem formalizes a necessary condition for calling an intervention a repair of the same claim identity: every failed load-bearing predicate must have at least one admissible action on a declared causal ancestor. This yields no-repair certificates, a minimum weighted causal-coverage lower bound on repair cost, and safe dominance pruning; changes to the question, population, estimand, primary metric, threshold, protected corpus or terminal semantics are classified as new successor identities rather than favorable repairs. For publication, we define a 51-receipt frozen denominator: the 40 receipts in the original ORION-02 receipt index plus 11 pre-cut receipts needed to complete the later R6O–R6S/QG lineage. Twenty-three receipts are included as graph nodes and 28 are explicitly excluded with category-level reasons. The graph contains 13 asserted successor edges; seven negative/absorbed nodes are deliberately retained without an invented successor. A fail-closed validator checks the 51-receipt partition, binds every receipt to the publication cut, rejects graph drift or invented edges, and preserves negative-result visibility. Independent replay of registered headline generators reproduces their committed outputs under a harness that also rejects perturbations and missing generators. We subtract direct prior art: ScienceAgentBench, AstaBench and SciAgentArena own substantial territory in rigorous scientific-agent evaluation; ScientistOne owns broad claim-to-evidence traceability and integrity auditing. Our narrower object is the **authorized transition from a retained scientific disposition to the next frozen question**, together with the causal-coverage boundary separating repair from successor formation. The evidence demonstrates feasibility, auditability and the formal boundary in one exact-heavy programme; it does not establish improved scientific productivity, autonomous governance or cross-domain superiority.

## 1. Introduction

Scientific agents can search literature, write code, execute analyses and draft papers. Evaluation and verification have matured accordingly. **ScienceAgentBench** evaluates executable data-driven scientific tasks sourced from peer-reviewed work. **AstaBench** and **SciAgentArena** broaden controlled scientific-agent evaluation with standardized tools, costs, environments and task families. **ScientistOne** develops a Chain-of-Evidence framework in which claims, scores, references and method descriptions are explicitly audited against source evidence and implementation. These are direct donors. ORION-02 does not claim novelty for scientific-agent benchmarking, provenance, reproducibility, evidence chains or executable outcome scoring.

A different question begins after those controls return an unfavorable scientific outcome.

Suppose a hypothesis was frozen before execution and is then refuted. The programme may discard the run, reinterpret the claim, repeat the same mechanism with a new name, or preserve the negative but fail to use it. None of those choices says which new question is scientifically licensed by the observed failure.

ORION-02 studies a bounded alternative:

`frozen question -> result -> typed disposition -> responsibility/donor analysis -> frozen successor or stop`.

The successor is a new research object, not a repair of the predecessor. A later theorem can strengthen authority for a new claim without turning a finite predecessor into a theorem. A later counterexample can refute a broad extrapolation without invalidating an earlier bounded prospective success. A donor can absorb a candidate mechanism and terminate that novelty route without making the experiment scientifically useless.

ORION-Q is a useful case because many claims have exact referees or sharply frozen finite domains. That makes invalid succession easier to detect than in noisy empirical science. We therefore treat the programme as a **mechanism case study**, not as evidence that the discipline improves research productivity generally.

## 2. Donor boundary

### 2.1 Scientific-agent benchmarks

ScienceAgentBench (ICLR 2025) evaluates 102 real data-driven research tasks from 44 peer-reviewed publications with expert validation and executable program-level scoring. AstaBench and SciAgentArena provide additional controlled scientific-research benchmarks and environments. ORION-02 gives these lines full credit for rigorous task construction, tool/cost control, executable evaluation and benchmark methodology.

### 2.2 Evidence chains

ScientistOne directly owns broad claim-to-evidence traceability, score/reference verification and method-code consistency checking. ORION-02 assumes scientific states can be bound to evidence; its candidate residual starts only **after** that evidence has produced a disposition.

### 2.3 Preregistration/provenance/negative results

Prospective freezing, provenance and publication of negative results are established scientific practices. ORION-02's candidate residual is their composition with two explicit transition constraints: responsibility-conditioned successor selection and donor first right of refusal. We make no “first” claim.

## 3. Research-state and successor model

A research node contains:

- claim/hypothesis and exact scope;
- protocol/outcome space fixed before result access;
- immutable result artifact;
- typed disposition such as `SUPPORTED`, `NEGATIVE`, `REFUTED`, `DONOR_ABSORBED`, `CANNOT_CHECK`, `MIXED` or `OPEN`;
- supported responsibility interpretation;
- donor/prior-work disposition;
- optional successor pointer.

A receipt proves identity/replay properties, not scientific truth or novelty.

An asserted successor edge requires:

1. predecessor disposition exists;
2. the predecessor identifies a residual/failure layer relevant to the successor;
3. donor/prior alternatives are considered before candidate novelty is granted;
4. successor protocol is frozen after predecessor result and before successor outcome;
5. predecessor artifact/claim boundary remains unchanged;
6. successor may fail, be donor-absorbed or remain `CANNOT_CHECK` without retroactively changing the old result.

Chronological adjacency is not sufficient to create an edge.

## 4. Frozen denominator and machine-readable graph

A case-study narrative can cherry-pick clean recovery chains unless the selection universe is declared. ORION-02 therefore freezes a publication denominator in `Q2_ELIGIBLE_RECEIPT_INVENTORY_V1.json`.

### 4.1 Declared 51-receipt universe

The universe contains:

- 40 receipts from the original `RECEIPT_INDEX.md` at the publication cut;
- 11 additional **pre-cut** receipts needed to complete the later R6O–R6S and QG5/QG7 lineage plus the N2-F5B donor-first-refusal result.

The inventory partitions these 51 artifacts exactly into:

- **23 included graph nodes**;
- **28 explicit exclusions**, grouped as pre-ladder/orthogonal programme results, R6 instrument/control states, or N-lane results not needed for the selected donor-first-refusal examples.

Exclusion means “not a ORION-02 publication transition node,” not “scientifically unimportant.” The inventory does not claim that all 51 receipts should have a successor.

### 4.2 Graph denominator

`Q2_TRANSITION_GRAPH_V2.json` contains:

- 23 result nodes;
- 13 asserted successor edges;
- the main R6M/TARE recovery chain;
- donor-absorption/robustness examples;
- seven named negative/absorbed nodes deliberately retained without an asserted successor edge.

The paper therefore reports a **declared bounded graph**, not an unbounded history of every possible research transition.

### 4.3 Fail-closed validator

`check_transition_graph.py` runs in publication CI and checks:

- the 51-receipt universe is exactly partitioned 23/28;
- every denominator receipt exists at the publication cut and remains byte-identical;
- the graph's 23 artifact paths equal the included set exactly;
- node/edge IDs are unique and endpoints exist;
- required central-chain edges remain present;
- an edge carries both relation and reason;
- standalone negatives cannot silently acquire successor edges;
- negative/partial-result visibility cannot regress.

The validator does **not** establish scientific causality. It establishes that the paper's declared causal graph and denominator are reproducible, frozen and non-cherry-picked relative to the stated publication universe.

## 5. Recovery chain I: common-anchor closure to split counterexample

A restricted shared-Tag TARE family appears plausible on early exact/chemistry checks. A support-dominance analysis explicitly retains one unresolved coupling: changing a frame can change the Tag requirement.

A frozen hostile instance returns an exact counterexample: split anchors with a spread Tag cost 8 while the common-anchor family costs 9.

The result remains:

`REFUTED: common-anchor closure`.

The exact witness localizes the residual to Tag/anchor coupling. Only after that result does the programme freeze D+, admitting arbitrary anchors with exact compatible Tag minimization.

This is the simplest successor pattern:

**exact refutation -> localized missing family coordinate -> prospectively frozen repair**.

## 6. Recovery chain II: the repair is also refuted

D+ is attacked on a registered structured domain and fails by exact frame-for-Tag borrowing. The minimal witness has cost 5 while D+ costs 6.

The failure is not relabeled as another split-anchor case. Its witness identifies a different residual: support two can be profitable on a cheap central branch because it buys a cheaper Tag. That observation licenses a D++ support-two family.

Again the original D+ refutation remains visible.

## 7. Finite positive to all-`n` theorem

D++ matches the unrestricted optimum on all then-registered finite domains. The programme records this as a bounded positive, **not** a universal theorem.

The unresolved responsibility becomes proof-level: can support three or larger ever be necessary outside the checked domains? A separate theorem protocol attacks that question. R6S later proves all-`n` support-two sufficiency for the frozen grammar/objective.

The evidence hierarchy remains explicit:

- R6P: finite family closure;
- R6S: later all-`n` theorem with stronger authority.

The theorem does not retroactively change what the finite experiment established at the time.

## 8. Prospective confirmation followed by later refutation

A compact donor/split/borrow predictor is derived on frozen panels. A previously unread public Benzene subject is selected by a precommitted rule; its predictions are digest-stamped before exact truth is opened. All 15 matchings agree.

That result remains a valid **bounded prospective confirmation**.

Later QG5 produces a different exact `n=3` row where the simple closed form predicts 11 and exact truth is 10. The correct update is:

- earlier subject-level prediction remains correct in its scope;
- universal extrapolation is refuted;
- exact witness localizes a missing borrow shape;
- separately frozen B′ tests that localization.

Later QG7 refutes B′ with another support-two configuration; B″ is then frozen and closes its registered finite panels while the all-`n` smallest-family classification remains partially open.

A positive forecast and a later negative therefore coexist without contradiction because their scopes/authority differ.

## 9. Donor absorption as a successful research terminal

Other ORION-Q lanes show a distinct succession pattern. A candidate can be matched by a stronger donor/model-selection baseline. The correct disposition is `DONOR_ABSORBED`, not a renamed candidate win.

The graph deliberately includes donor-absorbed/negative nodes even when no successor edge is asserted. Their role is to constrain future work: repeating the same mechanism under new branding is not an admissible novelty route.

## 10. What ORION-02 demonstrates

The case study establishes three bounded properties.

**Executable representation.** Dispositions and successor edges can be represented in a machine-readable graph and validated against immutable artifacts.

**Authority separation.** Exact refutation, bounded positive, theorem, donor absorption and open state remain distinct rather than collapsing into one progress score.

**Negative persistence.** A later repair cannot make a predecessor disappear from the declared denominator/graph.

ORION-02 does **not** demonstrate faster discovery, better research quality, autonomous governance, general responsibility diagnosis in noisy empirical science, or universal novelty of the transition protocol.

Those would require new controlled/cross-domain evidence and are intentionally outside the current claim.

### 10.1 Formal boundary: causal coverage of same-identity repair

The transition graph records what happened in the programme. A separate theorem asks what must be true before a successful intervention may be described as a repair of the **same** scientific claim rather than a changed successor.

Let the failed claim identity contain load-bearing predicates and let the declared action language specify which causal ancestors each admissible action can affect. A same-identity repair must select actions whose causal-effect union reaches at least one declared ancestor of every failed load-bearing predicate. This yields three consequences.

1. **No-repair certificate.** If one failed predicate has no admissible identity-preserving repair ancestor, no action set in the declared language can repair that claim identity.
2. **Repair-cost lower bound.** The minimum weighted ancestor cover is a rigorous lower bound on any identity-preserving repair cost in the action language.
3. **Dominance pruning.** If one action's causal-effect set is contained in another action's set at no lower cost, the dominated action can be removed from at least one minimum cover.

Causal coverage is necessary, not sufficient: an action on a relevant ancestor can still fail or cause a new failure. The theorem therefore constrains candidate repairs without turning them into evidence of success.

The identity rule is equally important. Changing the question, population, estimand, protocol semantics, primary metric, threshold, protected corpus or terminal semantics after failure produces a different scientific identity. Such a run can be successful research, but it is stored as a successor rather than used to rewrite the failed predecessor.

This theorem makes the graph's append-only discipline more than record keeping: it supplies a formal test for one class of post-failure relabeling that the workflow must reject.

## 11. Reproducibility and availability

The publication bundle should include:

- `Q2_ELIGIBLE_RECEIPT_INVENTORY_V1.json`;
- `Q2_TRANSITION_GRAPH_V2.json`;
- canonical validator stdout;
- reviewer-facing table mapping each main-text edge to predecessor/successor protocols/receipts;
- `papers/orion-06-recursive-recovery/theory/claim-preserving-recovery-v1/` and its independent checker;
- paper-local independent replay receipts for the cited generators;
- publication-cut git identity;
- permanent archive identifier once actually deposited;
- explicit reuse licence before any “open source” wording is used.

The repository is publicly inspectable, but public visibility is not a reuse licence. Exact replay establishes attributable reproducibility of the registered computation; it does not by itself establish the scientific validity or cross-domain effectiveness of recursive recovery.

## 12. Limitations

**One programme.** Feasibility/auditability is demonstrated in ORION-Q, not cross-domain effectiveness.

**Exact-heavy setting.** Exact referees make responsibility easier to localize than in noisy sciences.

**Declared publication universe.** The 51-receipt denominator is a bounded ORION-Q publication selection universe, not every scientific event in ORION or a sample of research generally.

**Selection rule is methodological.** Inclusion/exclusion reasons are explicit, but ORION-02 does not claim every excluded result could never inform a different successor analysis.

**Causal coverage is necessary, not sufficient.** A repair action can touch the right causal ancestor and still fail or introduce a new defect.

**No productivity outcome.** There is no controlled comparison of discovery time, paper quality or scientific yield against another governance policy.

**Human/AI composition.** Humans and multiple AI systems may participate; ORION-02 is not an autonomous-agent superiority result.

**External novelty remains empirical.** Internal donor searches/receipts cannot self-certify publication novelty.

## 13. Discussion

The successor discipline changes the meaning of “progress.” An exact counterexample can open the right family extension. A donor absorption can close an unproductive novelty route. A finite positive can justify a theorem attempt without being restated as a theorem. A prospectively confirmed case can remain valid after a different instance refutes the broad extrapolation.

The causal-coverage theorem adds a second discipline: a post-failure intervention is not a same-identity repair merely because it later succeeds. It must act on declared causal ancestors of every failed load-bearing predicate, and changing the scientific question or evaluation semantics creates a successor identity. This prevents a favorable changed question from laundering an earlier failure.

This differs from evidence-chain work in locus, not opposition. Evidence chains answer **what supports this claim?** ORION-02 asks **given the supported disposition, what research transition is now authorized?** Scientific-agent benchmarks ask whether systems solve tasks under controlled conditions. ORION-02 instead tracks how the research question itself changes after evidence arrives.

The 51-receipt denominator, fail-closed graph validator and independent replay make that case study inspectable rather than anecdotal. They still do not prove that the policy is optimal. That stronger question—whether one successor discipline improves science relative to another—is successor research rather than a hidden assumption of this paper.

## 14. Conclusion

Negative results can be represented as more than failed outputs. In the ORION-Q case study, a frozen result becomes a typed persistent state that can authorize, block or redirect later research while preserving its original claim boundary. A 51-receipt declared universe is partitioned into 23 publication graph nodes and 28 explicit exclusions; the graph carries 13 asserted successor edges and retains negative/donor nodes without invented links.

The formal recovery boundary complements the graph: every same-identity repair must cover a declared causal ancestor of every failed load-bearing predicate, uncovered predicates certify no repair within the action language, and identity-changing successes remain successors. Independent replay strengthens attribution of the registered computations without granting cross-domain effectiveness.

The candidate contribution is deliberately narrower than provenance or scientific-agent benchmarking: **an auditable successor relation from retained scientific disposition to a newly frozen question, with donor first right of refusal, append-only negative history, and a causal-coverage boundary separating repair from successor formation.**