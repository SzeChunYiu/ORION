# ORION Frontier Research Programme V1

Status: **FROZEN RESEARCH PROGRAMME — NO OUTCOME CLAIMS**

Frozen: 2026-08-20

Base: `main@6460410595a14cf9894c9acd450ab2b649a3b858`

This programme is deliberately separate from the already-frozen P9/P10 structural-scaling branch. It may cite merged P9/P10 as prior ORION evidence, but it may not reinterpret, retune, or contaminate those results.

## 1. Programme thesis

The next ORION question is not merely whether representation matters. It is:

> **Where can task-relevant structure live in a reasoning system, and what resource must be paid when it is not exposed at the right locus?**

A modern reasoning system contains more than model weights. Useful structure can be placed in:

- model parameters / architecture;
- the external input representation;
- a compiled task state or memory object;
- a retrieval index and query representation;
- an exact tool or verifier;
- a search policy;
- a persistent state/cache reused across branches;
- additional inference-time computation.

The programme asks whether these loci form a measurable substitution frontier under fixed task information.

The strongest prospective claim is therefore not `better prompts beat worse prompts`. It is:

> **For a fixed task distribution, capability is a property of the model-plus-support system. Equivalent task structure can sometimes be externalized from generic model capacity into representation, state, retrieval, tools, memory, or search, shifting the resources required to attain a fixed quality.**

This is a hypothesis. It becomes evidence only through the frozen tests below.

## 2. Why this programme exists after P9/P10

Merged P9 supports a bounded representation/accessibility result and separates information, learning, and exact-computation residuals. Merged P10 supports broad source-level Mathlib action recurrence and freezes stronger native-state/search escalations.

The current structural-scaling branch extends those papers toward model-scale and native-Lean tests. This new programme occupies adjacent territory that branch does not own:

1. **support placement** — move structure between representation, architecture, retrieval, tools, memory, and search;
2. **certified state compaction** — replace long histories with machine-verifiably task-sufficient state, not heuristic summaries;
3. **compile-once / reason-many amortization** — pay once to construct a reusable state object and quantify the crossover against repeated large-model reasoning;
4. **observation-time scaling** — spend test-time budget on acquiring/refining the right state rather than only generating more reasoning tokens;
5. **representation–retrieval duality** — ask whether better task coordinates reduce reranker strength, candidate depth, or premise-search cost;
6. **persistence–reconstruction tax** — quantify the compute lost when sufficient state is repeatedly reconstructed from history instead of persisted.

## 3. Research group and veto roles

The ChatGPT-led programme operates as four independent reviewer roles. Any role may block promotion.

### T — Theory / learning complexity
Owns definitions, restricted-class theorems, lower/upper bounds, sufficiency claims, and proof obligations. Rejects empirical quantities presented as universal lower bounds.

### S — Systems / LLM / agents
Owns compute accounting, tokenizer/context accounting, model/runtime identity, externalized tools/memory/retrieval, and real-agent execution. Rejects model-capability claims that actually belong to the harness.

### F — Formal methods / Lean
Owns exact state identity, compiler/verifier semantics, premise/search receipts, source revision, and proof-search claims. Rejects theorem-prover claims inferred from one-step prediction alone.

### H — Hostile novelty / reproducibility
Owns nearest-work subtraction, semantic-equivalence attackers, contamination, post-hoc drift, outcome-independent thresholds, negative-result retention, and receipt integrity.

## 4. Core mathematical objects

Let latent task state be `X`, target decision/action be `Y`, representation be `R`, model family be `M`, retrieval support be `K`, tool/verifier support be `T`, persistent state support be `P`, and inference/search budget be `C`.

### 4.1 Support vector

Define a declared system-support vector

`B = (S_model, C_inference, K_retrieval, T_tool, P_persistence, L_context)`.

The coordinates must be measured in native units first (parameters, generated tokens/FLOPs where possible, retrieved candidates, tool/verifier calls, persisted bytes/state objects, input tokens). No scalar conversion is allowed until a cost model is frozen.

### 4.2 Structural Support Frontier

For target quality `q`, define

`F_q = ParetoMin { B : Perf(B, R) >= q }`.

The primary scientific question is whether moving the same task-relevant structure between loci shifts `F_q`.

A single scalar score is not required. A non-dominated frontier is preferable to an arbitrary weighted sum.

### 4.3 Externalization Substitution Ratio

For one resource coordinate `a` and two support placements `u,v`, define

`ESR_a(q;u,v) = log( a*_u(q) / a*_v(q) )`

when all other frozen resources are matched and both thresholds are observed. Positive values mean placement `v` requires less of resource `a` to attain `q`.

### 4.4 Certified task-sufficient state

A compaction `Z = g(H)` of history `H` is **task-sufficient** for a bounded environment if, for every allowed future action sequence `A` in the declared horizon/class, the future outcome distribution relevant to the task is unchanged conditional on `Z`:

`P(O_future | H, A) = P(O_future | Z, A)`.

For finite deterministic environments this may be verified exhaustively or by a formal equivalence/bisimulation argument. For open environments it may only be an empirical approximation and must be labeled accordingly.

### 4.5 Replay tax

Let `C_replay(h,b)` be the cost of reconstructing state from history prefix length `h` for `b` branches, and `C_persist(h,b)` the cost when a sufficient state snapshot is reused. Define

`ReplayTax = C_replay / C_persist`.

Report wall time, model tokens, verifier/compiler calls, and state bytes separately.

### 4.6 Amortized state-compiler cost

If a compiler constructs reusable state at cost `C_compile` and `m` downstream queries cost `C_solve` each, define

`A_m = C_compile/m + C_solve`.

Compare with repeated direct reasoning cost `C_direct`. A prospective crossover exists at the smallest frozen `m` for which `A_m < C_direct` while quality is non-inferior.

### 4.7 Observation-time scaling

Let an agent acquire state coordinates/evidence through actions `o_1,...,o_k`, each with declared cost. Define the minimum observation budget needed to reach quality `q` as `O*(q)`.

The programme explicitly distinguishes:

- **thinking-time scaling**: more generation/search on a fixed observation;
- **observation-time scaling**: acquire/refine more task state;
- **model scaling**: larger parameterized solver.

The high-value result is a substitution curve among all three.

## 5. Frontier F1 — Structural Support Frontier

### Question
Can the same task-relevant computation be supplied through different system loci, and do those placements trade off with generic model/search capacity?

### Primary arms
1. `WEIGHTS/GENERIC`: no external structure; generic model must recover it.
2. `REPRESENTATION`: structure supplied explicitly in input coordinates.
3. `ARCHITECTURE`: frozen model architecture contains the correct interaction prior.
4. `TOOL`: exact preregistered operation externalizes the difficult subcomputation.
5. `MEMORY/STATE`: previously compiled task state is supplied.
6. `RETRIEVAL`: relevant relational object/premise is exposed by a structured index/query.
7. `SEARCH`: verifier/search policy supplies structure through constrained exploration.

Not every domain must instantiate every arm. Each claimed pair requires an exact semantic/resource accounting contract.

### Primary outputs
- quality at matched resources;
- threshold resources for target qualities;
- Pareto frontier;
- `ESR` values where thresholds are observed;
- worst-domain / worst-module behavior.

### Promotion gate
A support-substitution claim requires at least two qualitatively different domains and at least three support placements, with no hidden information addition in any same-information comparison.

## 6. Frontier F2 — Certified Sufficient-State Compaction

### Question
Can long reasoning/interaction histories be replaced by compact states with an explicit certificate that no task-relevant future information was lost?

### Controlled phase
Use finite deterministic procedural environments where history-to-state equivalence is mechanically checkable. Construct:

- raw full transcript;
- ordinary heuristic summary;
- full current Markov state;
- exact task-specific quotient state;
- deliberately over-compressed invalid state.

The quotient-state certificate must be verified **before** model evaluation.

### Real-system phase
1. P9-like workflows: canonical current relation/history object versus transcript.
2. Lean: native proof state/dependency object versus reconstructed tactic transcript.
3. Optional coding-agent environment: test/repository state with lossless pointers to full history.

### Primary endpoints
- downstream task success;
- token/context size;
- sample efficiency where learning is involved;
- replay/search cost;
- semantic-orbit stability;
- certificate violation count (must be zero for a `CERTIFIED` claim).

### Strong claim if earned
> Task-sufficient context can be compacted without predictive loss in bounded environments, converting long-horizon reasoning from history replay into state-based computation.

Do not claim losslessness for open-world summaries unless formal/complete environment semantics justify it.

## 7. Frontier F3 — Compile Once, Reason Many

### Question
Can a stronger model/tool compile a complex world into a reusable verified state so that smaller solvers answer many subsequent queries more efficiently than repeated direct reasoning?

### Arms
- repeated large-model direct reasoning;
- repeated small-model direct reasoning;
- large compiler -> free-form summary -> small solver;
- large compiler -> typed state -> small solver;
- exact/symbolic compiler -> typed state -> small solver where available.

The compiler output is frozen once per world/session and reused without hidden refresh.

### Key design
Each compiled world must support multiple downstream questions/actions not shown when the state was compiled. Otherwise the compiler could simply solve the question itself.

### Metrics
- per-world compile cost;
- per-query solve cost;
- accuracy as a function of number of downstream queries `m`;
- amortized cost `A_m`;
- crossover `m*`;
- state reuse degradation under domain/revision changes;
- compiler leakage: whether answer-specific information entered the state.

### Strong claim if earned
> Part of reasoning capacity can be amortized into a reusable task representation: compile once, then answer many queries with a smaller solver at lower total cost.

This is not ordinary CoT distillation: no student weight update is required for the primary claim, and reuse across unseen downstream queries is load-bearing.

## 8. Frontier F4 — Observation-Time Scaling / Progressive State Refinement

### Question
When a model is uncertain, is it better to spend the next unit of budget on more internal reasoning or on acquiring the next most useful piece of state?

### Controlled phase
Construct tasks with a frozen latent state and exact coordinate-relevance graph. At each step the agent may:

- `THINK`: spend inference budget without new information;
- `OBSERVE`: reveal one allowed coordinate/bundle;
- `TOOL`: execute one exact operation;
- `STOP`: answer.

Compare fixed-full-state, random observation, uncertainty-driven observation, oracle relevance (upper bound), fixed-thinking, and joint adaptive policies.

### Primary curves
- quality vs thinking tokens;
- quality vs observations;
- quality vs combined cost;
- fraction of budget spent on state acquisition;
- calibration of remaining difficulty.

### Strong claim if earned
> Test-time scaling has an observation axis: acquiring/refining task state can dominate additional serial reasoning when failure is representation/observation limited.

## 9. Frontier F5 — Representation–Retrieval Duality

### Question
Can better task coordinates substitute for stronger retrieval/reranking or larger candidate pools?

### Formal-math target
Use a fixed Lean theorem/proof state and a frozen Mathlib index. Compare queries built from:

- theorem text only;
- raw proof-state text;
- canonical typed state;
- typed state + dependency coordinates.

Retrieval systems are held fixed. Candidate depth `k`, reranker scale, and iterative retrieval steps are varied prospectively.

### Agent/code target
Use a fixed repository/search corpus and exact answer-bearing files. Compare raw task text with a compiled structural query/state under identical retrievers.

### Metrics
- recall/nDCG of ground-truth evidence;
- `k*(q)` candidate depth;
- reranker/model scale threshold;
- downstream solve rate under fixed search/verifier loop;
- retrieval calls/tokens.

### Strong claim if earned
> Some reasoning-intensive retrieval cost is a representation tax: exposing task structure reduces the retrieval depth or reranker capacity required to recover the same evidence.

## 10. Frontier F6 — Persistence–Reconstruction Tax

### Question
How much reasoning compute is wasted because agents reconstruct sufficient state from history at every branch/turn instead of persisting it as a first-class object?

### Controlled test
Generate branch-heavy deterministic tasks with identical branch semantics. Compare:

- replay transcript to reconstruct state per branch;
- persistent full state;
- persistent certified quotient state.

### Formal test
If the current native-Lean programme succeeds, compare proof-state reconstruction versus snapshot reuse under identical search branching and verifier budgets. Nearest work already establishes large systems speedups for Lean snapshotting; ORION novelty must come from the state-sufficiency/resource-frontier analysis, not from claiming first proof-state snapshotting.

### Outputs
- wall-time and token ReplayTax;
- state bytes;
- branch count scaling;
- error propagation from reconstructed/summary state;
- quality at matched wall-time/Lean-call budgets.

## 11. Cross-domain programme claim ladder

### R0 — conceptual decomposition
No empirical promotion. The system-support vector and frontier are only definitions.

### R1 — controlled support substitution
At least one finite task family shows a prospectively frozen support-placement tradeoff with exact task information accounting.

### R2 — certified-state advantage
At least one bounded environment demonstrates certified task-sufficient compaction with zero certificate violations and improved resource use at non-inferior quality.

### R3 — amortized compiler advantage
`Compile Once, Reason Many` crosses over repeated direct reasoning on unseen downstream queries under matched quality.

### R4 — real-domain replication
At least two real domains from different classes (e.g. formal proving + coding/search, or procedural + formal proving) show the same qualitative support/resource tradeoff.

### R5 — system-level structural support law
Only if multiple resource coordinates and domains produce stable frontier shifts under hostile controls may the programme claim a general empirical principle. No universal theorem is implied.

## 12. Hostile controls common to all lanes

1. Information accounting: state/retrieval/tool arms cannot silently receive extra answer-bearing facts.
2. Answer leakage: compilers run before downstream query identity where the protocol claims reusable state.
3. Cost accounting: input tokens, output tokens, model calls, retrieval depth, verifier/tool calls, persistent bytes, and wall time are reported separately.
4. Model identity: exact checkpoint/revision/quantization/runtime receipts.
5. Transformation invariance: order/symbol/alpha-renaming controls where semantics permit.
6. Domain identity attacker: verify gains are not domain-label shortcuts.
7. Negative arm retention: lossy summaries, failed compilers, and regressions remain visible.
8. No post-outcome cost weights: any scalar cost conversion is frozen before comparing arms.
9. No cross-paper contamination: merged P9/P10 remain immutable donor evidence, not tuning targets unless a new protocol explicitly permits it.
10. Nearest-work refresh immediately before any paper-level novelty claim.

## 13. Immediate execution order

1. Freeze nearest-work ledger and hostile matrix.
2. Implement a finite certified-state benchmark with exhaustive equivalence checking.
3. Implement a controlled observation-time scaling benchmark with separate THINK/OBSERVE budgets.
4. Implement a compile-once multi-query benchmark with answer-blind compilation.
5. Only then add LLM execution adapters; controlled results must not be retuned to resemble LLM outcomes.
6. If P10 native-state data becomes available, instantiate retrieval and persistence tests on Lean without changing their gates.
7. Add a third-domain agent/code experiment only after a public benchmark/runtime is fixed.
8. Promote the highest surviving rung; preserve all nulls.

## 14. Publication strategy

Do not assign historical P11 identity to this programme. Use `Frontier-F1...F6` until an earned standalone residual exists.

Potential papers if supported:

- **Where Intelligence Lives: The Structural Support Frontier of Reasoning Systems**
- **Certified State Compaction for Long-Horizon Reasoning**
- **Compile Once, Reason Many: Amortizing Reasoning into Reusable Task State**
- **Observation-Time Scaling: When Better State Beats More Thinking**
- **Representation Is Retrieval: Structured State Reduces Evidence-Search Cost**

The titles are prospective. No title is an achieved claim.
