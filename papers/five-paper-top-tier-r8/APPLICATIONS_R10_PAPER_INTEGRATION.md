# R10 Application Integration for the Top-Tier Paper Portfolio

**Date:** 2026-08-26  
**Branch:** `chatgpt/r10-paper-applications-20260826`  
**Status:** paper-integration draft; application claims remain gated by the experiments specified below.

## 0. Publication rule

An application enters a manuscript as a scientific result only when the chain

`theorem/result -> external object -> exact bridge -> frozen experiment -> measured discriminator`

is complete. Analogy, thematic relevance, or a green internal verifier is not application evidence.

Every application subsection must distinguish:

1. **theorem authority** — what is already proved;
2. **translation authority** — why the external system instantiates the theorem's objects;
3. **experimental authority** — what was measured in that system;
4. **promotion ceiling** — the strongest sentence licensed by the evidence.

The portfolio therefore uses applications as hostile tests of the mathematics, not as marketing appendices.

---

# 1. Q1 — sharp support-two TARE normal form

## 1.1 Exact theorem-to-system bridge

Q1 proves, for the frozen shared-Tag TARE-M2 grammar and objective, that the intrinsic uniform frame-support number is exactly two. The direct application is therefore **certified restriction of an exact compiler search**, not an automatic circuit-resource reduction.

A faithful compiler may replace unrestricted frame candidates by support-0/1/2 candidates without losing the exact optimum under the frozen objective. With six frame slots, the declared raw support-two family is polynomial in system size, with per-frame candidate count `3n + 9*C(n,2)` and a six-slot raw family of order `n^12`. This is a completeness-preserving search-space theorem.

The strongest application question is whether this certified restriction changes the resource frontier of a real block-encoding workflow after gate synthesis, ancillas, and normalization are charged.

## 1.2 Application A — certified exact TARE compiler

Build an exact compiler with three modes:

- unrestricted reference;
- theorem-restricted support `<=2`;
- support `<=1` hostile control.

The support-two mode should emit a proof receipt showing that the theorem applies to the instance/grammar version and that its optimum matches the unrestricted reference on every instance where both finish.

**Primary metrics:** explored states, candidate count, compile CPU/wall time, peak RSS, cache footprint, exact frozen objective, and proof-receipt size.

**Top-tier discriminator:** a parameter regime in which unrestricted search becomes resource-limited while support-two remains exact and tractable, or a strong null result showing that the existing dynamic program already eliminates the apparent candidate explosion.

## 1.3 Application B — block-encoding resource study

Use preregistered public Hamiltonians. Compare, where semantics and conventions can be aligned:

- unrestricted TARE-M2;
- support-two exact TARE-M2;
- support-one exact TARE-M2;
- donor/original TARE construction;
- standard LCU/block encoding;
- one current structured low-gate-count block encoding.

Report Clifford, T/Rz, CNOT/two-qubit count, depth, ancillas, subnormalization factor, and any derived QSVT query/resource proxy. Normalization must remain explicit because a gate-count gain can be erased by a worse block-encoding normalization.

**Permitted paper sentence if positive:** “The support-two theorem is not only a structural normal form: on the registered Hamiltonian panel it permits an exact search restriction that reduces compiler cost by X while preserving the optimum, and produces Y resource change under the frozen block-encoding accounting model.”

**Forbidden sentence without additional evidence:** “Support two reduces the fault-tolerant cost of QSVT in general.”

## 1.4 Current application context

Nearest current work makes this experiment worthwhile rather than optional. Schillo, Sturm and Quay (arXiv:2601.05740) introduce the Pauli block-encoding construction underlying the TARE primitive and explicitly motivate circuit complexity relative to LCU. Liu et al. (arXiv:2510.08644) optimize Clifford+T, ancillas, and subnormalization for second-quantized block encoding. Yang et al. (arXiv:2608.11579, Symphony) demonstrate that global binary-symplectic Pauli compilation can materially reduce two-qubit gates and depth on HamLib. Thus the Q1 contribution must be evaluated against a modern resource-aware compiler context, not only its internal objective.

**Execution owner:** issue #1416.

---

# 2. Integrated A+B — proof-language ownership and rewrite-registry audits

## 2.1 Exact theorem-to-system bridge

The integrated paper separates three quantities that compilers and proof systems frequently conflate:

- a normalization ceiling owned by a transformation;
- a terminal lower bound owned by a named proof language;
- the intrinsic optimum under the complete production move system.

The realized XOR grammar now supplies a clean `5 -> 1` example: a restricted zero-XOR deletion language has terminal support five, while the complete frozen language with pair fusion has intrinsic support one. This result is valuable only if presented as a warning about **proof-language ownership**, not as novelty for XOR algebra.

## 2.2 Application A — equality-saturation rule-registry audit

Equality saturation is an ideal external test because the result depends explicitly on the rewrite registry. Freeze a real e-graph/MLIR pipeline and define:

- semantic state/equivalence relation;
- extraction objective;
- weak ruleset;
- full named ruleset used by the production experiment;
- independent equivalence checker.

For every benchmark, compute a weak terminal/certificate and then ask whether the full registry collapses it. Build a critical-interaction graph for rule schemas that overlap. Report e-nodes/states, rewrite firings, extraction cost, certificate size, wall time, and memory.

The scientific output is a **certificate-ownership audit**: lower certificates are attributed to the exact rule language that generated them, and any omitted global/interacting rule is recorded as a counterexample to intrinsic interpretation.

This connects directly to current compiler practice. Merckx et al. (arXiv:2602.16707) propose persistent e-graphs in MLIR, while HEC (USENIX ATC 2025) uses equality saturation for transformation equivalence checking and reports real compiler bugs. The integrated A+B paper should therefore contribute a complementary question: not merely whether a rewrite is sound, but whether a claimed lower/terminal certificate survives the complete declared production language.

## 2.3 Application B — parity/CNOT synthesis as a high-value exact case

Parity-network and exact Clifford/CNOT synthesis provide a second exact domain where XOR-like semantics are real rather than metaphorical. Current SAT-based exact synthesis already demonstrates the importance of search-language design and exact resource objectives (e.g. Shaik and van de Pol, arXiv:2504.00634; Cao et al., arXiv:2509.10070).

The application is not to claim a new CNOT optimizer. Instead:

1. freeze a parity-network state semantics and exact cost;
2. define two nested legal transformation languages;
3. compute certificate complexity under each;
4. independently verify semantic equivalence;
5. measure whether a smaller certified production budget changes exact synthesis cost.

A null result is informative: it would show that the clean XOR separation does not transfer to this production language.

## 2.4 AI application — tool/tactic language audits

A secondary discussion application is AI proof/search agents. Difficulty claims made under a restricted tactic/tool vocabulary are properties of the pair `(problem, proof language)`, not automatically of the mathematical problem. The integrated framework supplies a formal reporting discipline for agent benchmarks: name the tool/tactic language, audit omitted globally simplifying moves, and distinguish proof-language terminality from intrinsic mathematical necessity.

This should remain a conceptual application unless a Lean/SMT/tool-agent experiment is executed.

**Execution owner:** issue #1385 and draft PR #1394.

---

# 3. Paper C — FiberGuard as a representation-safety layer for AI and exact optimization

## 3.1 Exact theorem-to-system bridge

For representation `Phi` and target `T`, FiberGuard computes the target range inside each exact representation fibre. The maximum fibre diameter gives an architecture-independent information radius for any predictor that receives exactly `Phi`.

This is immediately applicable to learned optimization because many systems deliberately compress an instance into features, graph summaries, solver statistics, or learned embeddings before making a value/action/solver choice.

The representation boundary must be literal. If a model receives richer information than `Phi`, the lower bound does not apply.

## 3.2 Application A — neural solver selection

Neural solver selection is an especially clean target. Gao et al. (ICML 2025, PMLR 267) explicitly build a feature-extraction/selection pipeline to choose among complementary neural solvers. FiberGuard can audit whether the selected representation is decision-sufficient for:

- identity of the best solver;
- runtime/optimality-gap regret relative to the virtual best solver;
- a tolerance-based acceptable-solver set.

For discrete or quantized inputs, exact feature collisions with different best solvers produce an unavoidable selection error/regret certificate. For continuous learned embeddings, exact collision claims are inappropriate; use a preregistered near-collision radius together with an explicit smoothness/robustness assumption, or quantize the representation before applying an exact-fibre result.

## 3.3 Application B — selective exact optimization

Turn the audit into a decision layer:

- `ANSWER` when the current fibre target radius is below tolerance;
- `REFINE` by acquiring an additional feature or exact statistic;
- `ABSTAIN/ESCALATE` to an exact solver when uncertainty remains too large.

The experiment must price feature/inference cost. Compare always-coarse, always-full, random refinement, uncertainty-only refinement, FiberGuard, and oracle. Report target error/regret, interval width, feature cost, total decision cost, latency, memory, and collision prevalence.

This is closely aligned with recent work on decision-sufficient representations. Ye, Amin and Özdağlar (COLT 2026, PMLR 336) study compressed datasets sufficient for optimal linear-program decisions and establish hardness results for sufficiency. FiberGuard's distinct niche is exact query-specific falsification by collision plus explicit repair/abstention on finite combinatorial domains.

## 3.4 Application C — learned branch-and-bound and algorithm discovery

For learned exact solvers, replace the scalar target by a set-valued or action target:

- optimal branch variable/action;
- whether a pruning decision is safe;
- exact lower-bound interval;
- solver/heuristic choice.

If a single representation fibre contains instances with disjoint correct action sets, no deterministic representation-only policy can be correct on both. The paper should report such action collisions where an exact oracle exists.

This makes FiberGuard a **representation preflight** before training: a failed audit says “change the information supplied to the model” rather than “increase model capacity.”

## 3.5 Scalable graph theorem and atlas nontransfer

The R9 graph lane has two complementary messages:

- an all-size construction shows unbounded chromatic-number fibre diameter for the frozen `(degree multiset, triangle count)` representation;
- the seven-vertex atlas experiment shows the six-vertex C4 repair does not universally transfer, while stronger graphlet/WL refinements close the frozen atlas.

This is the correct top-tier narrative: representation repair itself must be audited for transfer.

**Execution owner:** issue #1386 and draft PR #1392.

---

# 4. Paper D — typed authority as evidence binding in agent/tool authorization

## 4.1 Exact theorem-to-system bridge

Paper D does not replace OAuth, MCP, A2A, Cedar, OPA, or an access-control language. Its external object is an **authorization-evidence integration layer** in which facts validated from tokens, proofs, approvals, tools, datasets, or requests are combined before a downstream decision.

The theorem says authority coordinates must travel through the full proof path. If facts from different records lose their origin/license coordinates, an untyped positive-rule closure can manufacture a hybrid proof. Merge safety is exactly the condition that the union of independently safe closures is already closed under every admitted merged rule.

## 4.2 Application A — MCP/A2A gateway evidence binding

The 2026-07-28 MCP specification explicitly hardens OAuth-aligned authorization and makes requests more self-describing/routable. This strengthens, rather than weakens, the paper's required boundary: do not claim MCP is broken. Test a layer *after* standards-compliant validation where authorization facts are projected into a common graph.

Bind each fact to a coordinate such as

`(issuer, token/proof id, subject, audience, request id, tool/action, delegated principal)`.

A rule may consume facts only when its cap/bridge policy licenses that coordinate combination. Compare against a deliberately coordinate-erasing integration baseline.

Use legitimate same-record fragmentation, harmless multi-record cases, expiry/retraction, issuer/audience/subject mismatch, DPoP proof/token/request binding, tool approval splicing, and out-of-model cases requiring negation/defaults.

## 4.3 Application B — Cedar/Rego/Souffle independent implementation

Cedar defines authorization requests using principal/action/resource/context and combines permit/forbid policies under default-deny and forbid-overrides-permit semantics. Paper D's positive Horn calculus is not equivalent to Cedar. That makes Cedar a useful independent execution backend for the application boundary:

- use typed evidence coordinates to construct the request/entity data;
- let Cedar/Rego make the final authorization decision;
- compare with the same policy fed coordinate-erased evidence.

The paper's contribution is upstream evidence binding and retraction, not a competing policy language.

Primary metrics: false authorization, false denial, decision latency, evidence/policy state size, retraction latency, explanation size, and independent reviewer agreement.

## 4.4 Application C — least privilege for tool agents

Current agent-security work provides an important target. The latest MCP ecosystem emphasizes authorization, and recent work on task-conditioned least privilege for terminal/MCP agents (arXiv:2608.18351) treats excess authority as a measurable failure mode. Paper D contributes a different guarantee: **authority provenance cannot be strengthened by cross-record composition unless an authorized bridge exists.**

A high-value combined experiment is therefore:

1. a model/tool agent chooses an action;
2. normal OAuth/policy enforcement checks the request;
3. Paper D tracks the provenance of facts used to justify that authorization;
4. retraction or incompatible record merge is applied;
5. verify whether the authorization remains licensed.

## 4.5 Existing discriminator

The current RFC-grounded synthetic OAuth/JWT/DPoP panel reports 14/14 typed agreement and nine false authorizations for a deliberately coordinate-erasing baseline. This is useful mechanistic evidence but remains synthetic. A top-tier broad-impact sentence requires independent policy implementation and a real integration path or domain-reviewed policy corpus.

**Execution owner:** issue #1387; draft PRs #1402 and #1413.

---

# 5. Nonquantum paper — invariant theory and proof-producing automated mathematics

## 5.1 Exact invariant-theory bridge

This is the most direct non-computational application in the portfolio.

Cziszter and Domokos define generalized Noether numbers `beta_k(G)` over a base field whose characteristic does not divide `|G|` and state that for finite abelian `G=A`,

`beta_k(A) = D_k(A)`.

The `D_k` convention in that source is the smallest length forcing the product of `k` nonempty zero-sum subsequences, matching the disjoint-subsequence convention used by the current nonquantum manuscript. Zhong's 2025 Combinatorica paper uses the same `D_k` convention and explicitly reiterates the equality with generalized Noether numbers for abelian groups.

Therefore, **after independent replay authority is obtained**, the exact zero-sum results transfer immediately in non-modular characteristic:

- `D_2(C_5^3)=20` implies `beta_2(C_5^3)=20`;
- `D_3(C_5^3)=25` implies `beta_3(C_5^3)=25`;
- `5k+10 <= D_k(C_5^3) <= 5k+11` transfers to the same corridor for `beta_k(C_5^3)` for every licensed `k`;
- any future exact `D_4` result transfers to `beta_4` under the same convention.

The field assumption must be stated explicitly: characteristic not dividing `|C_5^3|=125`, hence in particular characteristic not equal to five.

This corollary should be included in the mathematical paper because it is exact and immediate, not presented as a speculative application.

## 5.2 Factorization-theory context

The generalized Davenport constants were introduced in connection with factorization-theoretic counting functions. The 2025 Combinatorica introduction explicitly notes this historical role and the importance of `D_k` for inductive methods. The paper should therefore explain the exact constants as values of an established zero-sum invariant with consequences in both combinatorial number theory and invariant theory, rather than forcing an AI narrative onto the mathematics.

## 5.3 Application B — benchmark for certified automated mathematics

The computer-assisted proof architecture itself has value as a reproducibility benchmark:

- two structurally independent engines;
- symmetry/canonicalization manifests;
- complete partition coverage;
- positive and negative controls;
- replayable certificates/receipts;
- explicit disagreement and resource-bound terminals;
- large compute delegated to LUNARC but theorem authority granted only by replayable evidence.

Recent AI theorem-proving work increasingly emphasizes mechanically checkable research output (e.g. Tsoukalas et al., arXiv:2605.22763; LEAP, arXiv:2606.03303). The NQ package can serve as a complementary benchmark where the bottleneck is exhaustive combinatorial certification rather than Lean proof generation alone.

Metrics should include candidate/orbit counts, symmetry reduction factor, certificate bytes, solver CPU/wall time, peak RSS, checkpoint/restart overhead, partition coverage, independent replay time, and deliberate disagreement detection.

**Forbidden inference:** successful AI/solver assistance does not increase the truth status of a `D_k` value beyond the independent proof/replay contract.

**Execution owners:** issues #1383 and #1384.

---

# 6. Cross-portfolio high-value synthesis

The five papers can share one short portfolio-level perspective without blurring their claims:

| Paper | Certified object | AI/algorithmic application | Failure prevented |
|---|---|---|---|
| Q1 | exact support normal form | theorem-restricted exact quantum compiler / constrained search policy | searching provably unnecessary high-support actions |
| A+B | ownership of terminal/certificate budgets by a named move language | e-graph/rewrite/proof-agent registry audit | calling proof-language difficulty intrinsic |
| C | exact target diameter inside representation fibres | learned solver selection; selective prediction; feature acquisition | asking model capacity to recover information absent from its input |
| D | license/origin-preserving proof paths and merge safety | agent/tool authorization evidence integration | splicing valid facts from incompatible records into stronger authority |
| NQ | exact generalized zero-sum constants + replayable proof architecture | invariant-theory corollaries; certified automated-math benchmark | promoting solver output without complete proof/replay authority |

The unifying theme is **certified boundaries on what a representation, proof language, evidence graph, or search grammar is actually allowed to conclude**. This is stronger and more coherent than claiming all five papers are simply “applications of AI.”

---

# 7. Main-text promotion gates

Before submission, each application section must answer six questions in one table:

1. What exact theorem/result is used?
2. What external object instantiates its variables and assumptions?
3. What independent check establishes that mapping?
4. What frozen experiment can falsify the claimed value?
5. What negative/null result would narrow the claim?
6. What sentence is forbidden if that experiment is absent?

A top-tier application claim requires an externally meaningful discriminator, not merely a larger internal benchmark.
