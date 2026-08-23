# P9-U GPT-R1 academic-paper-skills and framework audit

Date: 2026-08-20
Parent: #662
Negative-recovery parent: #586
Base: `main@8dd32366b92540b0e401ec9c8910c77af535f1fa`

## Academic-paper-skills scope

This pass applies current literature search, reference verification, three separately frozen reviewer lenses, statistics/independent-unit review, and a whole-manuscript claim/evidence/boundary consistency pass.

## Donor subtraction

The 2026 frontier makes structured reasoning itself direct prior art:

- **Graph Reasoning Paradigm** (ACL 2026, doi:10.18653/v1/2026.acl-long.1660) uses graph-structured symbolic reasoning and structured evaluation with topology-aware RL across mathematics and code.
- **StrucSum** (Findings EACL 2026, doi:10.18653/v1/2026.findings-eacl.192) injects sentence-level graph structure into long-document reasoning and reports quality/factuality gains.
- **BRIEF-Pro** (Findings ACL 2026, doi:10.18653/v1/2026.findings-acl.696) makes context compression a strong multi-hop reasoning donor and reminds us that representation construction has latency/cost consequences.
- graph/relational architectures, structured prompting, query-matched interfaces, exact symbolic engines, test-time scaling and representation compilers are donor-owned mechanisms.

P9 novelty cannot be “structure helps.” The scientific residual is a cross-regime **accessibility frontier law**: under matched semantic information and charged preprocessing, when and by how much does representation change the model scale, sample budget or inference compute required to reach a fixed verified target?

## Reviewer 1 — validity/methods, frozen

**P9-R1-01 — Information equivalence must be checked, not asserted. Blocking: Yes.**
Flat and structured arms require exact/reversible round-trip or a formally justified information-equivalence relation. If the structured arm receives additional task answer information, the frontier comparison is invalid.

**P9-R1-02 — Compiler/preprocessing cannot be free. Blocking: Yes.**
Representation construction, retrieval, indexing, query compilation and memory all enter the same resource accounting. A frontier shift caused entirely by an external solver/compiler is not an LLM accessibility result.

**P9-R1-03 — Thresholds are more defensible than post-hoc exponents. Blocking: Yes.**
Primary analysis should estimate predeclared critical/crossover frontiers on the frozen grid. Power-law exponents are secondary unless the functional form is frozen and diagnostics justify it.

## Reviewer 2 — prior work/contribution, frozen

**P9-R2-01 — graph/structured reasoning is saturated donor space. Blocking: Yes for novelty wording.**
GRP and StrucSum make explicit structure a current reasoning mechanism. P9 must compare against structured prompting/training/architectures rather than against flat text alone.

**P9-R2-02 — compression and query interfaces are donor mechanisms. Blocking: Yes.**
BRIEF-Pro and exact/task-sufficient interfaces mean that smaller state can improve reasoning. ORION's contribution must be the law/regime selection, not the mere existence of compression.

**P9-R2-03 — architecture prior can substitute for input structure. Blocking: Yes.**
The design must include graph/relational architecture and adaptive-compute controls to determine whether the accessibility advantage is input representation, architecture, compute, or their interaction.

## Reviewer 3 — reproducibility/generalization, frozen

**P9-R3-01 — task instance or predeclared task cluster is the independent unit. Blocking: Yes.**
Repeated decoding samples, remints and scale checkpoints do not independently multiply scientific n.

**P9-R3-02 — second model family and held-out domain are mandatory. Blocking: Yes for the general law.**
A frontier found on one model family may be a tokenizer/training-prior artifact.

**P9-R3-03 — no-crossing cells remain first-class results. Blocking: Yes.**
If a larger flat model erases the gap, or an exact query engine dominates both, that cell remains in the scaling surface rather than being deleted.

## Editor synthesis

The largest P9-U claim survives donor subtraction if it is stated as a representation-accessibility scaling law over matched semantic information and total resource cost. The paper should answer which access geometry is useful in which regime, whether its advantage survives stronger models/compute, and whether failed cells can yield a transferable new access coordinate or query interface.

## Framework consistency

Current ORION provides representation/access research substrate through:

- `EpistemicContextCompiler.rakl-v1`;
- `SimilarityWitness.rakl-v1` and `MeasurementRelation.rakl-v1`;
- `GeneratorTransport.rakl-v1` for correspondence/transport;
- `RetrievalBenchmark.rakl-v1` and `BackwardMultiseedBenchmark.rakl-v1`;
- `RaklTransferProfile.v1` / `RaklAnswerTransfer.v1`;
- K/W/M state and explicit source/representation semantics.

The later P11/P12 programme owns learned state construction economics and joint dynamic state-versus-reasoning allocation. P9 should consume those only as donor/control mechanisms and remain focused on the accessibility scaling law.

No canonical runtime object currently asserts a universal learned accessibility frontier or automatically discovers an optimal representation for arbitrary tasks. The broad P9 claim is therefore prospective.

Verdict: `CONSISTENT_AS_PROSPECTIVE_EXTENSION`.

## Negative-to-positive successor — Adaptive Access Geometry Discovery (AAGD)

The existing #586 programme supplies the causal taxonomy: unknown operator/transformation, unknown failure applicability, wrong access geometry/serialization, and wrong hypothesis/model class.

AAGD applies that taxonomy to every retained failed/tied frontier cell. The discriminator first checks information mismatch/leakage, compiler answer-computation, token/length confound, architecture substitution, more-compute closure and exact donor solution. Only after those are ruled out may the programme propose a new access coordinate/query interface/local operator.

Generic graph prompting, graph architecture, compression and structured CoT are donor-owned. A proposed access mechanic is promoted only if it changes a predeclared frontier on fresh tasks, transfers to another task/model-family cell, and remains beneficial after its construction cost is charged.

## Broad positive terminal

`GENERAL_REPRESENTATION_ACCESSIBILITY_SCALING_LAW` requires:

1. prospectively frozen matched-information resource frontiers;
2. representation-induced shift in model/data/inference thresholds under charged preprocessing;
3. hostile controls against length, answer-computing preprocessing, architecture and extra-compute explanations;
4. replication across at least two open-weight model families and heterogeneous held-out domains;
5. complete reporting of no-crossing/negative cells;
6. at least one failure-derived access coordinate/operator with fresh transfer.
