# Recursive Recovery of Negative Quantum Results: An Auditable Successor Protocol for Research Programmes

**ORION-Q2 Manuscript V3 — publication draft**  
Scientific cut: `main@ca7df1055a43f97eaf8d142a62011c4c261af368`  
Foundation: `PUBLICATION_FOUNDATION_V2.md`  
Machine-readable case object: `Q2_TRANSITION_GRAPH_V2.json`

## Abstract

Scientific-agent systems increasingly preserve code, evidence chains and execution traces, but provenance alone does not determine what a research programme should do after a prospectively frozen hypothesis is refuted, absorbed by prior work or left `CANNOT_CHECK`. We present a bounded longitudinal case study of an executable **negative-result successor discipline** used in the ORION-Q quantum-compilation programme. Each research node retains its frozen claim, result receipt and disposition. A successor edge is admitted only when the predecessor outcome localizes a scientifically relevant responsibility, the strongest located donor receives first right of refusal, and a new protocol is frozen before its outcome. Later success never rewrites the predecessor. The current publication graph contains 23 declared result nodes and 13 asserted successor edges; seven negative/absorbed nodes are deliberately retained without an invented causal successor. A fail-closed validator binds every graph node to the original publication cut and rejects missing artifacts, duplicate/invented edges, drifted predecessor bytes, or loss of negative-result visibility. Representative chains show qualitatively different legitimate transitions: restricted-family refutation to targeted family repair, second refutation to a stronger support family, finite positive to all-`n` theorem, bounded prospective confirmation followed by later closed-form refutation, and candidate residual to donor absorption. We explicitly subtract current prior art: ScienceAgentBench, AstaBench and SciAgentArena own substantial territory in rigorous scientific-agent evaluation; ScientistOne owns broad claim-to-evidence traceability and integrity auditing. Our narrower object is the **authorized transition from a retained scientific disposition to the next frozen question**. The evidence demonstrates feasibility and auditability in one exact-heavy research programme; it does not establish improved scientific productivity, general autonomy or cross-domain superiority.

## 1. Introduction

Recent scientific-agent systems can search literature, write code, execute analyses and draft research artifacts. Alongside that capability has come a rapid maturation of evaluation and verification. ScienceAgentBench evaluates executable data-driven scientific tasks extracted from peer-reviewed work. AstaBench and SciAgentArena broaden controlled scientific-agent testing with standardized tools, costs, environments and task families. ScientistOne's Chain-of-Evidence makes claim/source, score, reference and method-code consistency first-class audit targets. These are direct donors. Q2 does not claim that scientific agents need provenance, that scientific tasks should be benchmarked rigorously, or that evidence should be traceable to code and sources.

A different question begins **after** those controls return an unfavorable scientific outcome.

Suppose a hypothesis was frozen before execution and the exact result is negative. The programme may discard the run, reinterpret the original claim, repeat the same search with a new name, or preserve the negative but fail to use it. None of those choices tells us which new question is scientifically licensed by the observed failure.

Q2 studies a bounded alternative:

`frozen question -> result -> typed disposition -> responsibility/donor analysis -> frozen successor or stop`.

The successor is not an edit to the predecessor. It is a new research object whose admissibility depends on the old result remaining visible. A later theorem can strengthen authority for a new claim without turning the finite predecessor into a theorem. A later counterexample can refute a broad extrapolation without invalidating an earlier bounded prospective success. A donor can absorb a candidate mechanism and thereby terminate that novelty branch without making the experiment worthless.

The ORION-Q programme is a useful case because many claims have exact referees or sharply frozen finite domains. This makes invalid succession easier to detect than in a noisy empirical science. We therefore treat the programme as a **mechanism case study**, not as evidence that the discipline improves scientific productivity generally.

## 2. Related work and donor subtraction

### 2.1 Scientific-agent evaluation

**ScienceAgentBench** (ICLR 2025) evaluates 102 real data-driven scientific tasks sourced from 44 peer-reviewed papers, with expert validation and executable program-level scoring. **AstaBench** provides a broad, controlled scientific-research suite with standardized tools and strong baselines. **SciAgentArena** evaluates interactive real-world scientific scenarios with stepwise verification. Q2 therefore claims no novelty for authentic scientific-task construction, executable outcome scoring, controlled tools/costs, or broad scientific-agent benchmarking.

### 2.2 Chain-of-Evidence and research integrity

**ScientistOne** directly addresses claim-level verifiability through Chain-of-Evidence and audits for score, reference and method-code consistency. Q2 depends on the same general principle that scientific states must be bound to evidence, but it does not claim that principle as new. Its candidate residual starts only once a result has an evidentiary identity and a disposition.

### 2.3 Automated research systems

The AI Scientist and later end-to-end systems already span ideation, experiments and manuscript production. Q2 is not an autonomy result. Humans and multiple AI tools may participate in the ORION-Q case study. The contribution is the transition contract between research states.

### 2.4 Preregistration, provenance and negative results

Prospective freezing, provenance and publication of negative results are established practices. Q2 combines them with two additional constraints: **responsibility-conditioned successor selection** and **donor first right of refusal**. The paper makes no “first” claim; a submission-date literature search remains mandatory.

## 3. Research-state and successor model

A Q2 research node contains:

- claim/hypothesis and exact scope;
- protocol/outcome space fixed before result access;
- immutable result artifact;
- typed disposition such as `SUPPORTED`, `NEGATIVE`, `REFUTED`, `DONOR_ABSORBED`, `CANNOT_CHECK`, `MIXED`, `OPEN`;
- supported responsibility interpretation;
- donor/prior-work disposition;
- optional successor pointer.

A receipt proves identity/replay properties, not truth or novelty.

An asserted successor edge requires all of:

1. the predecessor disposition exists;
2. the predecessor identifies a residual or failure layer relevant to the successor;
3. donor/prior alternatives are considered before candidate novelty is granted;
4. the successor protocol is frozen after the predecessor result but before successor outcome access;
5. the predecessor artifact/claim boundary remains unchanged;
6. the successor may fail, be donor-absorbed or remain `CANNOT_CHECK` without retroactively changing the old result.

Chronological adjacency alone is not an edge.

## 4. Publication graph and denominator

Q2 makes its narrative graph machine-readable in `Q2_TRANSITION_GRAPH_V2.json`. On the frozen publication cut, the declared graph contains:

- **23 result nodes**;
- **13 asserted successor edges**;
- a central R6M/TARE recovery chain;
- donor-absorption/robustness examples;
- **seven named negative/absorbed nodes deliberately retained without an asserted successor edge** rather than linked by narrative convenience.

The graph is bounded to the ORION-Q publication scope. We call it a **declared publication graph**, not a universal graph of all scientific transitions and not yet a proof that every historical receipt was transition-eligible.

`check_transition_graph.py` fails closed if:

- a graph artifact is missing from the frozen cut;
- a node artifact has drifted relative to that cut;
- node/edge IDs duplicate;
- an edge points to an absent node or lacks a relation/reason;
- a required central-chain edge disappears;
- a standalone negative is silently given a successor;
- negative/partial visibility drops below the registered floor.

This validator does **not** decide scientific causality. It verifies that the paper's declared causal graph is internally reproducible and frozen-artifact bound.

A stronger future package may add a generated inventory mapping every programme receipt to inclusion/exclusion rationale. Until then, the manuscript avoids claiming complete coverage of all possible eligible transitions.

## 5. Recovery chain: common-anchor closure to split counterexample

A restricted shared-Tag TARE family appears plausible on early exact/chemistry checks. An explanatory support-dominance analysis explicitly retains one unresolved coupling: changing a frame can change the Tag requirement.

A frozen hostile instance then returns an exact counterexample: split anchors with a spread Tag cost 8 while the common-anchor donor family costs 9.

The disposition remains:

`REFUTED: common-anchor closure`.

The successor is not “try harder.” The exact witness localizes the residual to Tag/anchor coupling, which licenses a separately frozen D+ family admitting arbitrary anchors with exact compatible Tag minimization.

This is the simplest successor pattern in the graph:

**exact refutation -> localized missing family coordinate -> prospectively frozen repair**.

## 6. Recovery chain: the repair is also refuted

D+ itself is attacked on a registered structured domain and is refuted by exact frame-for-Tag borrowing. The minimal witness has cost 5 while D+ costs 6.

The second failure is not relabeled as the same split mechanism. Its witness localizes a different coordinate: support two can be profitable on a cheap central branch because it buys a cheaper Tag. That observation licenses a D++ support-two family.

Again the original D+ refutation is retained; the successor does not overwrite it.

## 7. Finite positive to theorem

D++ matches the unrestricted exact optimum on all then-registered finite domains. The programme records that as a bounded positive, **not** a universal theorem.

The unresolved responsibility is now proof-level: can support three or larger ever be necessary beyond the checked domains? A separate theorem protocol attacks exactly that question. R6S later proves all-`n` support-two sufficiency for the frozen grammar/objective.

The evidence ladder therefore remains explicit:

- finite family closure: bounded authority;
- later all-`n` theorem: stronger authority for the new universal claim.

The theorem does not retroactively change what the finite experiment established at the time.

## 8. Prospective confirmation followed by later refutation

A compact donor/split/borrow predicate is derived on frozen panels. A previously unread public Benzene subject is selected under a precommitted rule; its prediction is digest-stamped before exact truth is opened. All 15 matchings agree.

That result remains a valid **bounded prospective confirmation**.

Later QG5 produces a different fresh exact row where the broader simple closed form predicts 11 and exact truth is 10. The correct update is not “the Benzene result was wrong.” It is:

- the earlier subject-level prediction remains correct in its scope;
- the universal extrapolation is refuted;
- the exact witness localizes a missing borrow shape;
- a separately frozen B′ successor tests that localization.

This pair demonstrates the central succession principle: later evidence can narrow a generalization without erasing prior bounded evidence.

## 9. Repeated repair and open end states

B′ repairs the QG5 row and its registered successor panels. QG7 then freezes a stronger completeness attack and finds 64 exact fourth-regime witnesses outside B′. B″ is frozen separately and closes its registered finite panels. QG7c later closes most but not all all-`n` classification obligations; one pinned proof sector remains open on the publication cut.

The succession graph therefore permits a chain to end at `PARTIAL/OPEN` rather than manufacturing a final positive.

This is important for an automated research setting: **a loop must be allowed to stop because authority is insufficient**, not only because a target score has been reached.

## 10. Donor absorption is an informative terminal

Other ORION-Q lanes show a different recovery mode. A candidate residual can appear useful and then be matched by a stronger donor or model-selection baseline. The correct terminal is `DONOR_ABSORBED`, not a renamed candidate win.

The publication graph includes such nodes even when no successor edge is asserted. Their scientific role is to constrain future work: repeating the same mechanism under new branding is no longer an admissible novelty route.

## 11. What the method does—and does not—demonstrate

Q2 demonstrates three bounded properties.

**Executable representation.** Scientific dispositions and successor edges can be represented in a machine-readable graph and checked against immutable artifacts.

**Chronology/authority separation.** Bounded positive, theorem, exact refutation, donor absorption and open state remain distinct rather than collapsing into one progress score.

**Negative persistence.** A later repair cannot make the predecessor disappear from the publication graph.

Q2 does **not** demonstrate:

- faster discovery;
- higher-quality science;
- autonomous governance without human input;
- general causal responsibility diagnosis in noisy empirical domains;
- universal novelty of the successor protocol.

Those would require separate controlled or cross-domain evidence.

## 12. Reproducibility and availability

The machine-readable graph names each result artifact explicitly. The transition validator binds graph nodes to the frozen publication cut and runs in the dedicated Q/QG publication CI.

The final package should additionally provide:

- the complete graph JSON;
- validator output;
- reviewer-facing table mapping each main-text edge to predecessor/successor protocols and receipts;
- a permanent archive identifier;
- an explicit reuse licence before any “open source” wording is used.

The repository is currently publicly inspectable, but public visibility alone is not a reuse licence.

## 13. Limitations

**One programme.** The case study establishes feasibility/auditability in ORION-Q, not cross-domain effectiveness.

**Exact-heavy setting.** Many nodes have exact referees, making responsibility easier to localize than in noisy science.

**Declared graph, not universal denominator.** The 23-node/13-edge graph is the bounded publication object. It does not claim that every historical ORION receipt was eligible for a successor transition unless an explicit inclusion/exclusion inventory is generated.

**No productivity outcome.** We do not compare discovery time, publication quality or scientific yield against an alternative research-governance policy.

**Human/AI composition.** The case study may involve both humans and multiple AI tools; Q2 is not an autonomous-agent superiority result.

**External novelty remains empirical.** The donor cards and current search narrow the claim, but no internal receipt can self-certify novelty.

## 14. Discussion

The most useful consequence of the successor discipline is that “progress” stops being synonymous with “positive result.” An exact counterexample can be the event that opens the right family extension. A donor absorption can close an unproductive novelty route. A finite positive can justify a stronger theorem attempt without being restated as a theorem. A prospectively confirmed case can remain valid when a later instance refutes the broad extrapolation.

This differs from evidence-chain work in locus rather than in opposition. Evidence chains answer **what supports this claim?** Q2 asks **given the supported disposition, what research transition is now authorized?** Scientific-agent benchmarks ask whether systems solve tasks under controlled conditions. Q2's graph instead tracks how the task/hypothesis itself changes after scientific evidence arrives.

The current case study is intentionally modest. Its value is a reproducible research object that future work can test under stronger conditions: blinded noisy domains, competing successor policies, or agent systems whose claimed autonomy can be evaluated independently.

## 15. Conclusion

Negative scientific results can be stored as more than failed outputs. In the ORION-Q case study, a frozen result becomes a typed persistent state that can authorize, block or redirect later research while preserving its original claim boundary. The declared publication graph records exact refutations, bounded positives, a later all-`n` theorem, donor absorptions, prospective confirmation followed by broader refutation, and an open proof link without flattening them into one success metric.

The candidate contribution is therefore deliberately narrower than provenance or scientific-agent benchmarking: **an auditable successor relation from retained disposition to a newly frozen scientific question, with donor first right of refusal and append-only negative history.**
