# State as Computation: Query-Conditioned Compilation Trades Representation Rank, Accessibility Work, and Future Optionality

**ORION publication candidate P11**  
**Issue:** #471 · child tracks #664 and #667  
**Manuscript status:** complete current-evidence draft; controlled claims earned, real-system promotion gate open  
**Evidence date:** 2026-08-20

## Abstract

Intelligent systems are usually evaluated as if the state presented to a learner or reasoner were a fixed observation. We study a different regime in which **constructing state is itself a computational action**. For a query family `F`, a fixed query-agnostic representation must expose enough coordinates to support many possible downstream queries, whereas a query-conditioned compiler can construct only the state needed by the current query. In a controlled linear-readout setting we prove that any fixed representation supporting exact readout of a query family requires dimension at least the rank of that family. For all size-`s` parity queries on `d` Boolean coordinates this gives a requirement of `binom(d,s)` dimensions, while direct query-conditioned compilation needs one active coordinate. A separate no-answer-laundering construction exposes 5–7 relevant latent components but leaves the final decision to the same downstream learner. Frozen confirmatory experiments show universal/compiled representation ratios of 91×–1820× and observed sample-threshold reductions of 4× to more than 32×; the no-answer-laundering study reduces the 0.95-accuracy threshold by 32× or more in high-dimensional cells. Deterministic replays are byte-identical. We then distinguish current accessibility from future optionality: under exact workload models, compiled-only state may minimize current state while creating predictable future-query option debt, whereas retaining raw state buys recoverability and universal materialization buys immediate multi-query coverage at memory and upfront-compute cost. These results establish a controlled resource picture, not a universal advantage of compilation. Learned compilers, stronger nonlinear decoders, full compiler-cost accounting and real-system replications remain required before a broad state-as-computation claim is promoted.

## 1. Introduction

A representation can contain the information needed for a task and still make that information expensive for a bounded learner or reasoner to use. This observation is not new. Predictive V-information formalizes information usable by a restricted predictive family; partial evaluation specializes computation to known inputs; knowledge compilation and materialized views move work upstream; task-conditioned retrieval and modern context-management systems restructure what an agent sees. Recent state-design studies likewise show that changing state structure can materially alter reasoning while holding model parameters fixed. These donors rule out a weak novelty claim that “representation matters” or that “computation can make information easier to use.”

The unresolved systems question is narrower and more quantitative: **when should state itself be constructed for the current task, what downstream resources does this construction substitute for, what does the construction cost, and what future tasks become harder because universal information was not materialized or retained?**

We call this view *state as computation*. It treats a state transformation `C(R,q)` not as free preprocessing but as one place where an inference system can spend resources. The downstream system then operates on the constructed state under its own model, sample, search, verifier and tool budget. This creates a resource-allocation boundary linking four quantities that are often studied separately:

1. current-task accessibility;
2. construction/preprocessing work;
3. state memory and downstream model/search burden;
4. future optionality and recoverability.

The present paper earns three controlled components of that programme. First, an elementary rank theorem makes explicit the dimension cost of supporting a query family through a fixed linear-accessible representation. Second, frozen controlled experiments demonstrate large finite-sample nuisance effects when a universal representation materializes many irrelevant query coordinates. A hostile no-answer-laundering study shows that the effect survives when the compiler does not output the final answer. Third, exact workload equations separate query-specific accessibility from future optionality and identify compile/cache/materialize crossovers under frozen workload assumptions.

The claim is intentionally bounded. We do not prove a nonlinear lower bound, an algorithmic-time lower bound, a universal benefit of query conditioning, or an LLM/agent result. The strongest current statement is that **for controlled query families and bounded downstream learners, task-conditioned state construction can trade upstream construction work for large reductions in accessible representation rank and sample burden, while future-query uncertainty determines whether compilation, caching, raw retention or universal materialization is preferable**.

## 2. Donor boundary and research residual

### 2.1 Prior-owned primitives

The current ORION nearest-work ledger assigns prior ownership to the following primitives:

- **computationally usable information:** Xu et al., *A Theory of Usable Information under Computational Constraints* (ICLR 2020), including the fact that computation can transform inaccessible information into usable information;
- **program specialization / partial evaluation:** classical work specializes a program when some inputs are known;
- **knowledge compilation, materialized views and multi-query optimization:** moving work upstream and reusing compiled structure is longstanding;
- **task/query-conditioned retrieval and memory:** conditioning a representation on the current request is not new;
- **agent context compression and reversible context management:** active compression, raw-history retention and dynamic context selection are crowded primitives;
- **state-design effects on reasoning:** changing state structure can improve or degrade downstream reasoning;
- **rate-distortion, feature acquisition and information bottleneck:** task-oriented compression and cost-sensitive feature selection own nearby abstractions.

### 2.2 Residual claim-space

What remains scientifically live is the joint resource account:

> State construction is an allocatable inference resource whose cost, accessible dimension, downstream burden, cache/recovery cost and future optionality can be measured on a common Pareto boundary.

The theory and controlled experiments in this manuscript are foundations for that residual, not ownership of the donor primitives.

## 3. Formal setup

Let `X` be a domain with probability measure `mu`, and let `F={f_1,...,f_N}` be real-valued query functions in `L2(mu)`. A fixed query-agnostic representation is a map

`phi: X -> R^m`.

It supports exact linear query answering if for every query `q` there exists `w_q in R^m` such that

`f_q(x) = <w_q, phi(x)>`

almost surely.

A query-conditioned compiler instead receives `(x,q)` and constructs

`c = C(x,q)`

before the downstream learner or reasoner acts. The key accounting rule is that `C` is not free: its operations, latency, learned-compiler training cost, output state size and cache/recovery consequences belong to the resource receipt.

### 3.1 Theorem 1: query-family rank lower bound

If `span(F)` has dimension `r`, every fixed representation that supports exact linear readout of every query has `m >= r`.

The proof is direct: all `f_q` must lie in the span of the `m` coordinate functions of `phi`; that span has dimension at most `m` and must contain an `r`-dimensional function family.

This is elementary linear algebra and is not claimed as novel mathematics.

### 3.2 Approximate orthonormal frontier

If `f_1,...,f_N` are orthonormal and `U` is any `m`-dimensional linearly accessible subspace, Bessel’s inequality gives

`(1/N) sum_q ||f_q - P_U f_q||_2^2 >= 1 - m/N`.

The statement is useful because it makes an approximation tradeoff explicit without pretending that the same bound applies to unrestricted nonlinear decoders.

### 3.3 Parity corollary

For `X={-1,+1}^d` under the uniform measure and all size-`s` subsets `S`, define

`f_S(x)=product_{i in S} x_i`.

Distinct parity characters are orthogonal, so a fixed exact linear representation supporting all size-`s` queries requires

`m >= binom(d,s)`.

A direct query-conditioned compiler can compute the requested parity in one output coordinate. This establishes an exact **representation-dimension** gap, not a total-time lower bound.

### 3.4 No-answer-laundering condition

A direct compiler `C(x,q)=f_q(x)` is an intentionally strong specialization baseline but can be criticized for returning the answer. We therefore require a second regime in which the query selects multiple latent components, none of which is identically equal to or the negation of the final label. The final target is computed only after representation construction and must still be learned by the same downstream learner.

## 4. Controlled experiments

### 4.1 P11 confirmatory design

The confirmatory study was frozen after exploratory feasibility and theorem registration. It compares:

- raw input with a linear downstream learner;
- a fixed universal feature bank containing all relevant query coordinates;
- query-conditioned compiled state;
- frozen train sizes from 32 through 1024.

The scientific payload excludes nondeterministic wall-clock timing so exact replay can be byte-identical. No seed, learner, threshold or scientific metric was changed by that reproducibility amendment.

### 4.2 P11 confirmatory results

Terminal: `P11_QUERY_CONDITIONED_COMPILATION_GAP_SUPPORTED`.

| d | s | universal dims | compiled dims | dimension ratio | compiled n at 0.90 | universal n at 0.90 |
|---:|---:|---:|---:|---:|---:|---:|
| 14 | 2 | 91 | 1 | 91× | 32 | 128 |
| 16 | 4 | 1820 | 1 | 1820× | 32 | not reached by 1024 |
| 18 | 3 | 816 | 1 | 816× | 32 | 1024 |
| 20 | 3 | 1140 | 1 | 1140× | 32 | 1024 |

At `n=1024`, raw/universal/compiled accuracies were respectively:

- `(14,2)`: `0.49685 / 1.00000 / 1.00000`;
- `(16,4)`: `0.49903 / 0.84550 / 1.00000`;
- `(18,3)`: `0.50136 / 0.99152 / 1.00000`;
- `(20,3)`: `0.50113 / 0.94685 / 1.00000`.

Compiled accuracy was `1.0` in every frozen cell at every frozen train size. The canonical replay SHA-256 was identical across two fresh-process executions:

`8e790cf8bb8012bea8e575549730a58b21a0e1e96e51a2928d165c6fa89f3567`.

These data support a finite-sample nuisance interpretation: the decisive coordinate exists in the universal bank, but a bounded learner must identify it among many irrelevant coordinates.

### 4.3 P11B no-answer-laundering design

The second frozen construction exposes only the `r` active parity components needed by a query, with `r` equal to 5 or 7. The downstream logistic learner still computes a nontrivial odd-cardinality majority target. Every compiled component is checked against the final signed label and its negation over protected queries.

### 4.4 P11B results

Terminal: `P11B_QUERY_COMPONENT_COMPILATION_SUPPORTED`.

| d | s | r | universal dims | compiled dims | universal n at 0.95 | compiled n at 0.95 |
|---:|---:|---:|---:|---:|---:|---:|
| 15 | 3 | 5 | 455 | 5 | 2048 | 64 |
| 17 | 3 | 5 | 680 | 5 | 2048 | 64 |
| 17 | 4 | 5 | 2380 | 5 | not reached by 2048 | 64 |
| 19 | 3 | 7 | 969 | 7 | not reached by 2048 | 64 |

At `n=2048`, raw/universal/compiled accuracies were:

- `(15,3,5)`: `0.50493 / 0.99716 / 1.0`;
- `(17,3,5)`: `0.50205 / 0.96549 / 1.0`;
- `(17,4,5)`: `0.49985 / 0.76221 / 1.0`;
- `(19,3,7)`: `0.50024 / 0.87140 / 1.0`.

No component was answer-equivalent or answer-negating; laundering failures were `0`. The canonical two-replay SHA-256 was

`6f0260d84c5aba236c247960feef837428f2aa7806782c0698bb49073243abf6`.

The high-dimensional cells therefore show an observed 0.95-threshold improvement of 32× or more while leaving a downstream decision to be learned.

## 5. Future optionality and state economics

Current-task accessibility and future-task optionality are separate coordinates. Let a universal query family contain `N` independent components and a compiled state retain `r` of them.

If raw state is lost, uniform one-step future-query coverage of compiled-only state is exactly

`r/N`.

If `K` independently chosen random compilations of size `r` are cached, expected coverage is

`1 - (1-r/N)^K`.

Under uniform query demand, the expected number of distinct requested components after `K` requests is

`N[1-(1-1/N)^K]`.

These equations yield an interpretable policy tradeoff:

- **task compile:** minimal current state, future option debt if source is lost;
- **compile + cache:** grows state with encountered demand;
- **retain raw + compile:** recoverable coverage remains 1, but misses require recompilation;
- **universal materialization:** immediate coverage 1 at `N`-component memory and larger upfront work.

### 5.1 Frozen workload result

The deterministic P15 workload evaluation, now absorbed as P11’s optionality track, established the following first grid crossovers at which universal bulk compile work becomes lower than expected cache compile work under uniform demand:

| batch-efficiency beta | first frozen crossover horizon |
|---:|---:|
| 0.25 | 0.50N |
| 0.50 | 1.00N |
| 0.75 | 2.00N |

At `K=N`, expected distinct-demand fractions fall substantially under concentrated Zipf-like workloads, delaying the regime in which universal materialization is attractive. At `N=2048`, for example, the expected fraction is `0.63221` under uniform demand, `0.25735` for Zipf 1.1 and `0.09506` for Zipf 1.5.

These are exact controlled workload results, not universal agent-memory laws.

## 6. Accessibility-work accounting

The scientific comparison is invalid if compilation is treated as free. P11 therefore uses the shared `ORION.P11P14.ResourceReceipt.v1` schema with separate coordinates for:

- compiler/preprocessing operations and latency;
- state bytes/tokens and memory traffic;
- model identity/capacity;
- generated tokens/recurrent steps;
- search nodes, verifier calls and tools;
- cache memory and reuse;
- raw recovery/reconstruction/recompilation;
- end-to-end latency and reproducible energy where available.

Learned-compiler training cost is reported separately and amortized only under prospectively stated reuse horizons. Results are shown as quality–resource Pareto surfaces rather than a post-hoc scalar.

## 7. Experiments required for external promotion

The manuscript story is complete, but the stronger empirical claim is not.

### E1 — fresh generalized query families

Use prospectively regenerated orthogonal and approximately low-rank families, task-family holdouts, fixed train-size grids and both linear and one frozen nonlinear decoder sweep. Preserve `NOT_REACHED` without extrapolation.

### E2 — learned compiler

Train only on development tasks/query descriptions and source state. Test unseen query identities/families. Compare against oracle compiler, universal state, random selector, donor feature-selection baseline and stronger matched decoder. Report compiler quality separately from downstream quality.

### E3 — multi-query union rank

Freeze query batches, vary overlap/rank at fixed batch size, and compare per-query recompilation, union-rank compilation, universal materialization and compile+cache.

### E4 — shifted optionality workloads

Evaluate uniform, concentrated, bursty, drifted and rare-critical future queries. Report future-service probability and rare-critical coverage separately from current accuracy.

### E5 — real-system replication

At least one same-information LLM/procedural setting and one formal/search or long-horizon memory setting are required for the broadest paper terminal. If stronger decoders or real systems erase the effect, retain that negative and narrow the claim to the controlled regime.

## 8. Statistical analysis and reporting

The exact theorems and workload equations require no statistical inference. Frozen controlled learner results are reported exactly as receipted; this manuscript does not invent confidence intervals absent from the result receipts.

For future learned-compiler and real-system studies:

- select policies/hyperparameters on development families only;
- hold out entire query/task families for primary evaluation;
- use paired item comparisons inside family;
- use family/domain-block uncertainty for headline generalization claims;
- report all prespecified cells/regimes, including null and harmful compilation regimes;
- retain `NOT_REACHED` thresholds rather than extrapolating;
- keep deterministic scientific payloads separate from nondeterministic timing fields.

## 9. Discussion

The controlled results show why “the information is already there” can be an incomplete systems statement. A universal representation can contain the decisive component and still impose a substantial identification burden on a bounded learner. Task-conditioned compilation can reduce that nuisance burden by moving work upstream.

But compilation is not a free lunch. Direct specialization may simply compute the answer; P11B addresses that criticism only in a controlled multi-component family. A learned compiler can fail, its training cost can dominate, a strong decoder can erase the benefit, and aggressive compression can destroy future optionality. The correct scientific object is therefore not a declaration that compiled state is better. It is the **frontier** connecting construction work, accessible state, downstream reasoning, cache/recovery and future query distribution.

This perspective also predicts when universal state should win. As future query diversity or horizon grows, or when bulk materialization is sufficiently efficient, universal state can reduce repeated compile work. Concentrated workloads and cheap raw recovery favor on-demand compilation; rare critical queries can reverse average-optimal choices. The phase diagram is therefore workload- and responsibility-dependent.

## 10. Limitations

1. Current dimension theorems apply to fixed linear-accessible function spaces, not unrestricted nonlinear decoders.
2. Parity/Walsh worlds are deliberately transparent controlled constructions, not models of all realistic state.
3. P11B removes a simple answer-laundering failure mode but does not prove that every learned compiler is non-laundering.
4. Current sample-threshold results are controlled and do not establish an LLM/agent law.
5. Compiler training/inference cost is not yet fully measured in a learned real system.
6. Optionality phase results depend on frozen workload assumptions and should not be universalized.
7. The 2026 literature landscape is changing rapidly; final submission requires a fresh external literature/archival-version check.

## 11. Reproducibility and evidence identity

Authoritative project evidence currently lives on the Frontier V2 research branch associated with PR #631:

- `THEOREM_QUERY_CONDITIONED_COMPILATION_GAP_V1.md`;
- `THEOREM_GENERAL_QUERY_REPRESENTATION_RANK_V1.md`;
- `P11_QUERY_CONDITIONED_COMPILER_PROTOCOL_V1.md`;
- `P11_CONFIRMATORY_RESULT_RECEIPT_V1.md`;
- `P11B_NO_ANSWER_LAUNDERING_PROTOCOL_V1.md`;
- `P11B_CONFIRMATORY_RESULT_RECEIPT_V1.md`;
- `THEOREM_STATE_OPTIONALITY_COVERAGE_V1.md`;
- `P15_STATE_OPTIONALITY_RESULT_RECEIPT_V1.md`.

Two fresh-process replays are byte-identical for both P11 and P11B. Real-system promotion remains blocked until the specified external experiments execute.

## 12. Data and code availability

Controlled generators, protocols, runners and result receipts are repository artifacts under `research/extensions/orion-frontier-v2/` on the Frontier V2 branch/PR. No external dataset is claimed by this manuscript. Future real-system datasets/splits must be versioned and released or identified with enough source information to reproduce the protected evaluation.

## 13. Claim ledger

| Claim | Current status | Evidence | Forbidden widening |
|---|---|---|---|
| fixed exact linear support needs dimension at least query-family rank | EARNED CONTROLLED THEOREM | rank theorem | arbitrary nonlinear lower bound |
| parity universal vs query-compiled dimension gap | EARNED CONTROLLED THEOREM | parity corollary | total-time lower bound |
| large finite-sample accessibility gap in frozen cells | EARNED CONTROLLED RESULT | P11 receipt | universal sample-complexity law |
| compact benefit without direct answer field | EARNED CONTROLLED RESULT | P11B receipt | all compilers are non-laundering |
| compile/cache/materialize policy changes with workload | EARNED CONTROLLED WORKLOAD RESULT | optionality receipt | universal memory theorem |
| learned compiler yields matched-resource advantage | OPEN | E2 | may not be stated as result |
| stronger decoder does not erase effect | OPEN | E1/E2 | may not be assumed |
| real-system state compilation improves frontier | OPEN | E5 | no LLM/Lean/agent claim yet |

## 14. Publication decision

**Current decision:** strong controlled/theoretical manuscript, not yet externally promotable as the full P11 paper.

Promotion requires: learned/non-oracle compiler; stronger-decoder attack; reproducible full resource accounting; at least one real-system replication; and a final donor/literature delta leaving a coherent residual.

## References and donor notes

1. Xu, Y. et al. **A Theory of Usable Information under Computational Constraints.** ICLR 2020. [Exact author metadata should be re-verified at submission.]
2. Jones, N. D., Gomard, C. K. & Sestoft, P. **Partial Evaluation and Automatic Program Generation.** Prentice Hall, 1993.
3. Darwiche, A. & Marquis, P. **A Knowledge Compilation Map.** *Journal of Artificial Intelligence Research* 17, 229–264 (2002). [DOI/issue metadata to be verified in final citation pass.]
4. ORION Frontier V2 Nearest-Work Ledger (2026-08-20), which additionally tracks current state-design, context-compression, query-conditioned memory and adaptive-state donors whose archival metadata must be refreshed before submission.

### Citation integrity note

The live external literature search service was unavailable during this drafting pass. Contemporary 2025–2026 donor names in the ORION nearest-work ledger are therefore treated as donor pointers, not silently normalized into fabricated bibliography entries. A final academic-search + reference-verification pass is mandatory before submission.
