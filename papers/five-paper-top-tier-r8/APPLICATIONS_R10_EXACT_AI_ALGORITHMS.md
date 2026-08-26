# Exact AI, Algorithms, and High-Value Application Programme R10

Date: 2026-08-26

Status: application architecture for manuscript integration. Every lane below is theorem-to-system-to-experiment. No application is promoted from analogy alone.

## 0. Expert-cell conclusion

The strongest portfolio narrative is **certified action under compression**.

Modern exact and AI-assisted systems compress a problem before acting: a compiler compresses semantics into signatures, a learned optimizer consumes a feature representation, an agent compresses evidence into a provenance/authorization graph, and a computer-assisted proof search quotients a large symmetry space. The scientific question is not whether compression is useful; it is what conclusions remain licensed after compression.

The papers supply different certificates:

- **Q1 / integrated AB:** a *search-space certificate* — which support bound belongs to the actual move system rather than a weaker proof language;
- **C / FiberGuard:** an *information certificate* — whether the representation determines the target to the requested radius;
- **D / typed authority:** an *authorization certificate* — whether the action is supported by a seed-founded proof carrying the required license and origin;
- **NQ:** a *computer-assisted proof certificate* — whether symmetry reduction and finite search cover the full mathematical source problem.

The application programme therefore prioritizes four executable systems and one cross-paper controller.

---

# 1. Q1 + integrated AB: certificate-constrained exact and AI-guided quantum compilation

## 1.1 Target problem

Exact circuit resynthesis and Pauli/parity-network compilation often combine aggressive heuristic search with a smaller exact kernel. Current work shows that parity-network optimization materially affects two-qubit gate counts and that exact synthesis kernels can improve real compilation workflows, while exact search remains memory- and combinatorics-limited.

The ORION opportunity is to separate two questions that are usually conflated:

1. what support ceiling is actually guaranteed by the semantics-preserving production grammar; and
2. how much search is wasted when an optimizer uses a weaker certificate language than the complete move system.

## 1.2 System: CertCap compiler kernel

Input:

- a frozen production grammar;
- complete local/global/shared-auxiliary move registry;
- semantics map;
- support/objective functional;
- exact or heuristic search policy.

Output:

- certified production support cap `K_prod`;
- weaker-language cap `K_cert` where applicable;
- realizing/terminal witness or an explicit no-realization terminal;
- exact candidate-volume prediction for the declared enumerator;
- proof object replayable independently.

AI is allowed to propose rewrite orders, parity-term orderings, branching choices, or candidate circuits, but the formal kernel owns admissibility and the support cap. The learned/LLM policy therefore cannot silently convert a heuristic observation into an exact certificate.

## 1.3 Exact experiment

Use a fixed public circuit/Pauli benchmark panel and compare:

- exact search with no support certificate;
- exact search with the weak-language cap;
- exact search with the complete production cap;
- heuristic/ML-guided search constrained by the complete cap;
- heuristic/ML-guided search without the cap.

Report:

- enumerated states/candidate supports;
- wall time and peak memory;
- proof-verification time;
- final two-qubit/CNOT count when that objective is truly modeled;
- regimes in which the cap is irrelevant because another bottleneck dominates;
- every instance where a presumed product/additive cap is invalidated by a cross move.

The strongest result would be a theorem predicting a measured search exponent reduction together with a production-realized strict certificate gap.

## 1.4 Manuscript claim boundary

Allowed:

> A complete move audit can turn proof-language support waste into a formally certified reduction of an exact compilation search space.

Not allowed without hardware/physical measurement:

> The support theorem improves quantum fidelity, hardware success probability, or quantum advantage.

## 1.5 Current external anchors

- Campbell and Dahl, *Enhancing Quantum Optimization with Parity Network Synthesis*, 2024, arXiv:2402.11099.
- Li et al., *Parallelizable Exact Synthesis of Quantum Circuits via Semi-Tensor Product*, 2026, arXiv:2607.24195; reports integration into a real circuit-optimization workflow and exposes the current scalability pressure on exact synthesis.
- Wang, Tan, Cong, and De Micheli, *Quantum State Preparation Using an Exact CNOT Synthesis Formulation*, 2024, arXiv:2401.01009.

These works motivate the application but do not grant ORION novelty. The residual ORION question is certificate ownership and production-realized search reduction.

---

# 2. Paper C / FiberGuard: adaptive representation control for learned exact optimization

## 2.1 Target problem

Learned combinatorial optimization increasingly uses learned features for branching, solver selection, objective prediction, and heuristic guidance. Recent work coordinates neural solvers at the instance level and studies what LLM representations contain about combinatorial instances. These systems can fail before learning begins: two instances may have identical model input but require different exact decisions.

FiberGuard should therefore become a **pre-deployment representation firewall**, not only a finite collision benchmark.

## 2.2 System: FiberGuard Controller

For each representation fibre `F` and target `T`, maintain an exact or certified target interval and a menu of refinements with acquisition costs.

At runtime the controller chooses:

- `ANSWER`: current information already satisfies the target radius;
- `REFINE`: buy the feature/refinement minimizing worst-case residual decision cost;
- `ABSTAIN/DEFER`: route to the exact solver/full representation when information remains insufficient.

The R9 Bellman recursion provides the exact finite-state policy when child fibres and feature costs are known. The R9 graph theorem further shows that one natural low-order graph representation has **unbounded** chromatic-number fibre diameter, so the failure is not a six- or seven-vertex artifact.

## 2.3 Highest-value concrete applications

### A. Learned branch-and-bound

Freeze the exact representation consumed by a branching model at a B&B node. Define the target as full strong-branching score or the exact best branch under a fixed solver state. Search for representation collisions with different oracle branch decisions.

A collision is stronger than an average accuracy failure: no model receiving only that representation can be correct on both states.

Evaluate FiberGuard as a router:

- cheap learned branch if the fibre is safe;
- acquire richer solver features if refinement is cost-effective;
- otherwise invoke strong branching.

Primary metrics: exact branch-choice regret, B&B node count, wall time, feature acquisition cost, strong-branching calls, and proof-of-optimality preservation.

### B. Neural solver / algorithm selection

Recent neural solver-selection work explicitly relies on feature extraction. Freeze a solver portfolio, solver versions, deterministic resource budget, and representation. Target either a deterministic best-solver label under the frozen protocol or a robust solver set.

FiberGuard identifies feature collisions where the selected solver must differ and prices the minimum repair. This converts representation auditing into a certified adaptive algorithm-selection layer.

### C. LLM feature extraction for optimization

A 2026 *Computers & Operations Research* paper studies feature extraction and algorithm selection in open-weight LLMs. FiberGuard can test a complementary question: whether the *explicit recovered representation* is sufficient for the target before asking how well an LLM decodes it.

This separates latent/model failure from information failure.

## 2.4 Required benchmark protocol

For at least one production-derived or public learned-optimization domain:

1. freeze instances before feature-selection outcome review;
2. hash the exact model input representation;
3. compute an exact/registered target or independent high-authority oracle;
4. enumerate exact collisions when feasible and certified lower bounds otherwise;
5. estimate collision prevalence only on the frozen corpus, never from the synthetic family;
6. price feature acquisition;
7. compare against `always coarse`, `always full`, random refinement, uncertainty-only refinement, and oracle routing;
8. measure total decision cost, not only prediction error.

## 2.5 Manuscript claim boundary

Allowed:

> Exact representation collisions induce architecture-independent decision floors; a certificate-aware refinement/defer policy can remove those floors at a measured acquisition cost.

Not allowed:

> A collision in a frozen feature map is a lower bound for a richer GNN/Transformer/LLM representation.

## 2.6 Current external anchors

- Gao et al., *Neural Solver Selection for Combinatorial Optimization*, ICML 2025.
- Wenkel et al., *Towards a General Recipe for Combinatorial Optimization With Multi-Filter GNNs*, LoG 2025.
- *Behavior and representation in open-weight Large Language Models for combinatorial optimization: From feature extraction to algorithm selection*, *Computers & Operations Research*, available online 19 August 2026.
- Antoniadis et al., *Approximation algorithms for combinatorial optimization with predictions*, ICLR 2025.
- Cappart et al., *Combinatorial Optimization and Reasoning with GNNs*, JMLR 2023, for the exact-solver/learned-component paradigm.

---

# 3. Paper D: typed-authority firewall for tool-using and multi-agent AI

## 3.1 Target problem

Agentic AI security is moving from text filtering to provenance, identity, tool authorization, and stateful execution. Current systems and standards explicitly emphasize tool permissions, authorization context, execution telemetry, and provenance. Recent research such as ProvenanceGuard, AuthGraph, Agent-Sentry, and AttriGuard shows that provenance-aware action control is an active high-value problem.

Paper D should not compete by claiming generic provenance. Its distinct role is a **small exact authorization calculus after facts have been authenticated/extracted**.

## 3.2 System: AuthorityGuard

Each fact entering an agent/tool workflow carries one or more authority coordinates, for example:

- authenticated user intent;
- policy approval;
- token/request binding;
- tenant/session origin;
- reviewed internal evidence;
- retrieved/untrusted evidence;
- tool output;
- prospective vs post-outcome evidence;
- data-use/jurisdiction scope.

Rules specify which coordinates are allowed to cross. A high-impact action such as `send`, `execute`, `publish`, `transfer`, or `reuse_data` is enabled only when the required license has a finite seed-founded proof tree.

The graph-merge theorem detects hybrid authorization created only after two individually safe evidence records are combined. Origin-sensitive coordinates prevent cross-session or cross-token splicing. Typed retraction removes authority after evidence or credentials are invalidated.

## 3.3 Integration point with agent platforms

The system is deliberately downstream of authentication/OAuth/MCP checks. MCP's 2026 authorization work hardens issuer/resource binding and enterprise-managed access; Paper D addresses a different layer: whether separately valid facts are safe to compose into a stronger downstream permission.

OpenAI's 2026 Codex security guidance likewise emphasizes technical boundaries, approvals, and agent-native telemetry. AuthorityGuard can consume such authenticated events and produce a replayable logical authorization certificate.

## 3.4 Exact benchmark programme

### A. Agent tool authorization

Use an agent-security benchmark or frozen tool workflow containing clean and adversarial traces. Compare:

- untyped reachability/provenance union;
- typed AuthorityGuard;
- a conventional policy engine encoding where feasible;
- a current provenance defense if its implementation and threat model permit a fair comparison.

Cases must include:

- benign multi-source merges;
- indirect-prompt-injection-derived facts;
- stale/retracted evidence;
- unsupported cycles;
- cross-session/token/tenant splicing;
- foreign-license promotion;
- legitimate authorized bridges.

Metrics:

- false authorization / attack success;
- false denial / benign task completion;
- first forbidden proof witness;
- proof footprint size;
- retraction propagation latency;
- merge-induced authority frequency;
- policy compression size and evaluation time.

### B. MCP / OAuth evidence integration

The existing RFC-grounded OAuth/JWT/DPoP discriminator is a strong synthetic starting point. The next step is a real gateway or provenance integration path in which validated token/proof facts can be accidentally mixed after validation. The paper should demonstrate the error in the integration layer, not suggest that OAuth itself permits arbitrary claim mixing.

### C. Multi-agent research or coding workflow

Give each agent/tool output a content-bound origin and authority class. The experiment asks whether several individually plausible agent outputs can recursively or cross-contextually manufacture a permission to execute/publish that no authorized seed granted.

This is especially suitable for long-running coding/research agents because tool traces, approvals, repository writes, and external-compute receipts already form explicit evidence graphs.

## 3.5 Manuscript claim boundary

Allowed:

> Typed seed-founded authority and origin-preserving merge checks prevent a reviewed class of cross-record authorization errors while retaining explicit benign bridges.

Not allowed:

> The calculus establishes factual truth, legal compliance, general prompt-injection immunity, or general AI alignment.

## 3.6 Current external anchors

- She, Liang, and Kang, *Safeguarding LLM Agents from Misalignment through Provenance Analysis*, 2026, arXiv:2607.01236 (ProvenanceGuard).
- Wang, Li, and Tian, *Aligning Provenance with Authorization: A Dual-Graph Defense for LLM Agents*, 2026, arXiv:2605.26497 (AuthGraph).
- Sequeira et al., *Agent-Sentry: Bounding LLM Agents via Execution Provenance*, 2026, arXiv:2603.22868.
- He et al., *AttriGuard: Defeating Indirect Prompt Injection in LLM Agents via Causal Attribution of Tool Invocations*, 2026, arXiv:2603.10749.
- Model Context Protocol 2026-07-28 specification release and authorization hardening.
- OpenAI, *Running Codex safely at OpenAI*, 8 May 2026.

The prior-art section must explicitly explain that AuthorityGuard is a typed fixed-point authorization/verifier layer, not a new provenance-extraction or intent-inference method.

---

# 4. Nonquantum paper: proof-producing symmetry-aware computational mathematics

## 4.1 Direct mathematical application

The strongest direct application remains nonunique factorization / block-monoid theory, where generalized Davenport constants already have established arithmetic meaning. The paper should lead with the exact `C_5^3` mathematics rather than force an AI application.

The 2025 rank-two inverse `D_k` work and the 2026 generalized Davenport-constant literature confirm that generalized and inverse zero-sum invariants remain active mathematical objects.

## 4.2 Algorithmic system: ZeroSumProof

The reusable algorithmic contribution should be a proof-producing finite-classification architecture:

1. mathematical compression to quotient/rank/multiplicity strata;
2. exact source-level grammar rather than relaxation-level inference;
3. full stabilizer canonicalization;
4. lazy short-zero-sum cuts;
5. exact disjoint-zero-sum packing adversary;
6. independently generated forbidden-set and orbit manifests;
7. clean-room replay by a structurally different engine;
8. machine-readable SAT survivor or UNSAT/census certificate.

This architecture is valuable beyond one constant because it separates discovery search from proof authority.

## 4.3 Coding-theoretic translation

A sequence in `F_5^3` can be viewed as a multiset of parity-check columns. A zero-sum subsequence is an all-one linear dependency on a selected column multiset; `k` pairwise-disjoint zero sums correspond to `k` disjoint all-one dependencies.

The manuscript may define the corresponding restricted column-multiset problem and state exact equivalences. It must not claim a new coding bound unless a coding parameter and theorem are genuinely transferred.

Potential experiment:

- take small parity-check column multisets;
- compare generic SAT/ILP with the ORION symmetry/source-aware solver;
- measure orbit reduction, lazy-cut counts, certificate size, and independent replay time.

## 4.4 AI application — use as a certifiable reasoning benchmark, not a headline claim

The frozen zero-sum instances can serve as a benchmark for theorem-proving/search agents because every proposed result has an exact external verifier and hostile source/quotient traps. This is useful for evaluating whether an AI system distinguishes discovery evidence from proof authority.

This should be a secondary application only unless a real agent benchmark is executed.

## 4.5 Current external anchors

- Freeze and Schmid, *Remarks on a generalization of the Davenport constant*, 2010: eventual arithmetic progression and factorization connections.
- Zhong, *On the Inverse Problem of the k-th Davenport Constants for Groups of Rank 2*, *Combinatorica* 2025.
- Godinho, Lemos, and Neumann, *A generalization of the Davenport constant over abelian groups*, *Discrete Mathematics* 2026.
- Current coding-theoretic work continues to connect weighted Davenport constants and intersecting codes; this connection is donor-owned unless ORION proves a new exact transfer.

---

# 5. Cross-paper system: Dual-Certificate Safe Action Controller

## 5.1 Motivation

A learned/agentic system can be wrong for two fundamentally different reasons:

- **information failure:** the representation does not determine the requested target/action;
- **authority failure:** the evidence graph does not license the action even if the action is inferentially attractive.

Paper C detects the first. Paper D detects the second.

## 5.2 Controller

For hidden instance/world state `x`, observed representation `Phi(x)`, target/action query `T`, and required authority license `lambda`:

1. compute/certify the target range on the current information fibre;
2. if the range exceeds the permitted radius or contains opposite action labels, refine the representation or defer;
3. independently compute typed authority for the proposed action;
4. execute only if the information certificate and authority certificate both pass;
5. emit both certificates with the action receipt.

For exact scalar decisions, the information certificate can be the fibre endpoint interval. For discrete actions it can be target constancy across the fibre. The authority certificate is a finite seed-founded proof tree carrying the required license/origin.

## 5.3 Safety theorem

Under the declared finite-domain/fibre certificate and positive typed-authority semantics, an action released by the controller is simultaneously:

- within the certified target radius for every state compatible with the current representation; and
- supported by a valid typed proof carrying the required license.

This theorem does **not** establish that the representation domain contains the real world, that the target is the correct objective, or that the policy encoding is morally/legal correct. It cleanly composes two independently checkable guarantees.

## 5.4 Best application

Agentic optimization or scientific agents:

- an ML/LLM component proposes a solver/action from compressed features;
- FiberGuard decides whether the representation supports that decision or must request richer information;
- AuthorityGuard checks whether the evidence/user/tool context licenses executing the action;
- an exact solver or human review is the fallback.

This creates a strong portfolio-level narrative without merging the scientific claims of Papers C and D.

---

# 6. Submission-grade application evidence matrix

| Paper | Application headline | Minimum evidence required before strong claim | Best metrics |
|---|---|---|---|
| Q1 + AB | Certificate-constrained exact/AI quantum compilation | complete production move map + realized cap gap + public compiler benchmark | candidate states, runtime, memory, verification time, 2Q count if modeled |
| C | Adaptive representation firewall for learned optimization | public/production feature map + exact/certified collisions + priced refine/defer experiment | target error/regret, interval width, feature cost, total decision cost, B&B nodes/runtime |
| D | Typed-authority firewall for agent/tool pipelines | independent policy encoding + real or standards-grounded integration + benign/adversarial controls | false authorization, false denial, task success, proof size, retraction latency |
| NQ | Proof-producing symmetry-aware exact classification | independent replay + complete source-level coverage + machine-verifiable receipts | orbit count, cut count, runtime/RSS, certificate size, replay agreement |

A manuscript should not use the phrase “application” for a lane that has only an analogy. Until the corresponding evidence gate closes, label it “application programme” or “transfer hypothesis.”

---

# 7. Immediate execution queue

## Codex/LUNARC

- finish CR-B and full independent NQ replay (#1383);
- prepare source-level lift RED controls and canonical-prefix run (#1384);
- independently replay the AB XOR grammar and bind one genuine production-derived rewrite/Pauli grammar (#1385);
- audit/cherry-pick the unbounded FiberGuard graph theorem, then execute a production-derived learned-optimization/refinement-cost study (#1386);
- independently replay typed authority in a different policy engine and execute an agent/tool provenance case (#1387).

## ChatGPT research lane

- maintain current-literature overlap matrices for each application;
- derive application-specific theorems before experiments where possible;
- design exact baselines and null/hostile regimes;
- integrate only evidence-backed application language into manuscript abstracts, introductions, experiments, and discussion.

## Promotion rule

A top-tier application claim requires all three:

1. **mathematical bridge:** the application metric follows from a theorem or exact registered contract;
2. **operational realization:** the bridge is implemented in a real or public-domain system/benchmark;
3. **comparative discriminator:** the proposed method wins or exposes a failure against a strong matched baseline, with null regimes retained.

Anything missing one of these remains a transfer hypothesis rather than a paper headline.
