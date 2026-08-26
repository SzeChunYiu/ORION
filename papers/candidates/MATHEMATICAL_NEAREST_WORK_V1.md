# ORION-16–ORION-18 mathematical nearest-work pressure ledger V1

**Search date:** 2026-08-17  
**Status:** first formal-methods pass; not saturated  
**Rule:** entries below are pressure sources, not novelty conclusions. Full-text mechanism receipts and two no-material-change rounds remain required under #318/#334/#337/#340.

## A. ORION-16 — Formal Epistemic Structures and Mechanics

### A1. Dynamic epistemic logic

**Source:** Hans van Ditmarsch, Wiebe van der Hoek, Barteld Kooi, *Dynamic Epistemic Logic*, Springer, 2007, DOI `10.1007/978-1-4020-5839-4`.

**Already supplied:** formal informational actions, action/model update, changing epistemic models, multi-agent knowledge/belief dynamics.

**Consequence for ORION-16:** no novelty claim for modeling epistemic change as actions or state/model transformations.

**Open discriminator:** whether a mechanic contract coupling typed responsibility/evidence obligations to coordinate-scoped mutation authority, dependency-minimal reopening and recursive self-audit is already represented by an existing action-logic composition.

### A2. AGM and iterated belief revision

**Source:** Carlos Alchourrón, Peter Gärdenfors, David Makinson, “On the Logic of Theory Change: Partial Meet Contraction and Revision Functions,” *Journal of Symbolic Logic* 50 (1985), 510–530.

**Formal-proof source:** Fouillard, Taha, Boulanger, Sabouret, *Belief Revision Theory*, Archive of Formal Proofs, first released 2021; current build visible in 2026.

**Already supplied:** expansion/contraction/revision postulates and representation results; mechanized proofs of classical AGM operators and identities.

**Consequence:** ORION-16 must not present selective state change or belief revision itself as new, and should reuse formalized AGM results rather than reproving them.

### A3. Truth-maintenance and dependency-directed backtracking

**Source:** Jon Doyle, “A Truth Maintenance System,” *Artificial Intelligence* 12(3), 1979, 231–272, DOI `10.1016/0004-3702(79)90008-0`.

**Already supplied:** recorded justifications, consistency maintenance, incremental belief revision, explanation, dependency-directed backtracking and control structures over assumptions.

**Consequence:** dependency graphs, justification records and downstream invalidation are prior art. ORION-16.T1/T2 are useful structural lemmas but not automatically novel.

**Open discriminator:** authority-typed mutation and recursively composable mechanic contracts, not dependency reachability alone.

### A4. Cognitive architectures for language agents

**Source:** Sumers, Yao, Narasimhan, Griffiths, “Cognitive Architectures for Language Agents,” arXiv:`2309.02427`, TMLR-era work.

**Current pressure:** Fan and Lan, “From Cognitive Architectures to Language Agents: A Mechanism-Level Review of Lineage, Convergence, and Migration Gaps,” arXiv:`2607.23942`.

**Already supplied:** modular memory/action/decision architecture; recent mechanism-level decomposition using state, control, transition, persistence, failure, learning and resource governance.

**Consequence:** a catalog of agent modules or mechanic fields is not enough for ORION-16. The paper needs formal properties and a surviving coupled residual.

### A5. Authorization and compositional state logic

**Pressure families:** access-control authorization logic, process/separation logics, temporal/dynamic logics, design-by-contract and typed state-transition systems.

**Consequence:** ORION-16's read/write/authority typing and commutation theorem must be compared to established local-state and permission calculi. ORION-18 owns the general authority layer.

## B. ORION-17 — Epistemic Navigation in Open Worlds

### B1. Iterative graph navigation

**Source:** Sun et al., “Search-on-Graph: Iterative Informed Navigation for Large Language Model Reasoning on Knowledge Graphs,” arXiv:`2510.08825`.

**Already supplied:** observe-then-navigate graph search, schema adaptation and local informed traversal.

**Consequence:** ORION-17 cannot claim iterative graph navigation or adaptive path choice.

**Open discriminator:** representation-changing topology plus support-preserving transfer/reopening and fail-closed global stopping.

### B2. Open-world search-agent evaluation and stopping failure

**Source:** Chen et al., “Evaluating the Search Agent in a Parallel World” (Mind-ParaWorld / MPW-Bench), arXiv:`2603.04751`.

**Already supplied:** controlled interactive open-world search evaluation, evidence-collection/coverage pressure, evidence-sufficiency and when-to-stop failure analysis.

**Consequence:** evidence-coverage and stopping failures are not unique to ORION. ORION-17 must contribute a formal impossibility/authority result or a distinct evolving-topology benchmark.

### B3. Breadth, diversity and scientific-search concentration

**Source:** Tang and Yang, “AI Research Agents Narrow Scientific Exploration,” arXiv:`2605.27905`.

**Source:** Antoniades et al., “Heuresis: Search Strategies for Autonomous AI Research Agents Across Quality, Diversity and Novelty,” arXiv:`2606.25198`.

**Already supplied:** empirical evidence that scientific-agent exploration can remain concentrated; explicit quality/diversity/novelty search strategies and archives.

**Consequence:** exploration breadth/diversity is prior empirical territory. ORION-17 needs formal route/topology/stopping semantics, not merely a diversity metric.

### B4. POMDP/open-ended planning

**Pressure family:** POMDP belief-space planning, active information acquisition, value of information, open-ended hypothesis generation, replanning/model revision.

**Recent example:** Tang et al., “Tru-POMDP: Task Planning Under Uncertainty via Tree of Hypotheses and Open-Ended POMDPs,” arXiv:`2506.02860`.

**Consequence:** partial observability and open-ended hypothesis spaces are established. ORION-17.T1 must be positioned as a closure-authority indistinguishability result, and ORION-17.T2 as a limited expressivity separation rather than a claim that changing models is new.

### B5. ORION-12 ownership

ORION-12 already owns route independence, question-conditioned memory, route/task stopping, censored obligations and recall-first promotion in literature discovery.

**Mandatory discriminator:** ORION-17 must establish a general theorem or non-retrieval transfer result involving topology-changing reframes. Otherwise merge into ORION-12/ORION-11 rather than publish separately.

## C. ORION-18 — Epistemic Authority for Autonomous Science

### C1. Access-control authorization calculi

**Source:** Abadi, Burrows, Lampson, Plotkin, “A Calculus for Access Control in Distributed Systems,” *ACM Transactions on Programming Languages and Systems* 15(4), 1993.

**Already supplied:** logical treatment of principals, requests, delegation/on-behalf-of relations, access-control lists and grant decisions.

**Consequence:** typed issuers, delegation, scope and authorization derivations are established. ORION-18's possible residual is not generic access control.

### C2. Deontic and input/output logics

**Source:** Makinson and van der Torre, “What is Input/Output Logic? Input/Output Logic, Constraints, Permissions,” Dagstuhl Seminar Proceedings 07122, 2007, DOI `10.4230/DagSemProc.07122.32`.

**Recent pressure:** Giorgio Cignarale, “From Actions to Obligations: A Deontic Action Model Logic,” arXiv:`2605.26739`.

**Already supplied:** formal obligations/permissions/norm outputs; recent action-model machinery deriving context-sensitive obligations with soundness/completeness results.

**Consequence:** ORION-18 must not claim permission, obligation or dynamic deontic action reasoning in isolation.

### C3. Capability versus permission

**Source:** Zheng et al., “Separating Capability from Permission: A Governance Framework for Agentic AI Autonomy Levels,” arXiv:`2607.23438`.

**Already supplied:** explicit separation of allowed autonomy from technical capability, with risk/oversight/accountability-based governance levels.

**Consequence:** the slogan `capability != permission` is directly prior work. ORION-18 survives only through a formal cross-epistemic-action calculus, non-compensatory obligations, anti-laundering theorem and discriminating evidence.

### C4. Agent abstention

**Source:** Liu et al., “AgentAbstain: Do LLM Agents Know When Not to Act?”, arXiv:`2607.10059`.

**Already supplied:** paired should-act/should-abstain benchmark, agent-native abstention taxonomy and evidence that abstention differs from task capability.

**Consequence:** ORION-18 cannot claim abstention as new. It may use paired cases as a benchmark-design donor while distinguishing abstention from typed authority and revocation.

### C5. Provenance-based action guarding

**Source:** She, Liang, Kang, “Safeguarding LLM Agents from Misalignment through Provenance Analysis” (ProvenanceGuard), arXiv:`2607.01236`.

**Already supplied:** structured provenance support for proposed tool actions and pre-execution allow/block decisions.

**Consequence:** evidence-traceable action permission is prior work. ORION-18 needs cross-domain authority composition and laundering resistance beyond provenance support alone.

### C6. Runtime shielding and formal enforcement

**Source:** Alshiekh et al., “Safe Reinforcement Learning via Shielding,” AAAI 2018, DOI `10.1609/aaai.v32i1.11797`.

**Source:** Könighofer et al., “Shields for Safe Reinforcement Learning,” *Communications of the ACM* 68(11), 2025, DOI `10.1145/3715958`.

**Already supplied:** formally specified runtime action restriction/correction and safety guarantees under model/specification assumptions.

**Consequence:** capability filtering by formal policy is established. ORION-18's authority contracts must distinguish scientific/epistemic permission and cross-module derivation from ordinary safety shielding.

### C7. Policy composition and multivalued decisions

**Source family:** Belnap/bilattice access-control policy composition; grant/deny/conflict/unspecified semantics; defeasible and revocable policies.

**Consequence:** ORION-18's four-valued obligation status and policy composition require explicit comparison. Reusing a bilattice is not novelty.

### C8. ORION-14/ORION-15 ownership

ORION-14 already owns protected non-compensatory scientific-authority promotion. ORION-15 owns no-self-promotion and fresh/protected admission of self-change.

**Mandatory discriminator:** ORION-18 must prove and test cross-domain anti-laundering/revocation. If it merely generalizes ORION-14/ORION-15 terminology, merge it into programme synthesis.

## D. Immediate novelty contractions

The first mathematical pass already forces these contractions:

1. **ORION-16:** not “a mathematics of changing epistemic state”; candidate residual is a contract-level coupling of responsibility/obligation, mutation authority, dependency-minimal reopening and recursive mechanics.
2. **ORION-17:** not “navigation for research agents”; candidate residual is evolving-topology navigation with support-preserving transfer and open-world completion authority.
3. **ORION-18:** not “capability differs from permission”; candidate residual is typed cross-domain anti-laundering and revocation across heterogeneous epistemic actions.

## E. Open full-text and mechanism work

- formalize exact overlap with DEL action models and belief-revision operators;
- compare ORION-16 contracts against separation/process/authorization logics;
- search historical navigation under changing representations/model spaces;
- search formal impossibility/identification results for unknown-denominator completion;
- compare ORION-18 derivation rules against access-control, input/output, dynamic deontic and bilattice policy calculi;
- retrieve official code/proof artifacts where available;
- create one MechanismAssimilationReceipt per atomic donor;
- run hostile `already solved` searches for each full residual composition;
- complete two no-material-change rounds before any novelty terminal.
