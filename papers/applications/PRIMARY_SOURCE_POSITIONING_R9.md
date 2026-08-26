# Current Primary-Source Positioning R9

**Search freeze:** 2026-08-26  
**Status:** seed matrix for specialist audit, not a novelty certificate

This matrix records the closest primary sources found for the application programme and the residual claim that ORION would need to establish. Absence from this list or a failed search is never novelty authority.

| Lane | Closest primary source | Established content relevant here | Residual ORION application claim | Disqualifying overlap / language ceiling |
|---|---|---|---|---|
| APP-C | Z. Chen, J. Liu, X. Wang, J. Lu, W. Yin, **On Representing Mixed-Integer Linear Programs by Graph Neural Networks**, arXiv:2210.10759 | Shows fundamental GNN representation limitations for MILPs and conditions under which richer/random features can recover feasibility, value, and solutions. | Exact query-specific fibre certificates, content-bound endpoint witnesses, minimum-cost/sequential repair, and enrich/abstain/route integration on the actual optimizer representation. | ORION cannot claim generic discovery that GNNs fail to distinguish optimization instances. |
| APP-C | Z. Chen et al., **Expressive Power of Graph Neural Networks for (Mixed-Integer) Quadratic Programs**, arXiv:2406.05938 | Studies representability of feasibility, objective values, and solutions for QP/MIQP graph encodings. | Exact negative fibres and costed repair for a frozen architecture/query where the representation is insufficient. | Positive representability and general GNN expressivity are donor-owned. |
| APP-C | B. Zhang et al., **A Complete Expressiveness Hierarchy for Subgraph GNNs via Subgraph Weisfeiler–Lehman Tests**, ICML 2023 | Gives a hierarchy for subgraph GNN expressivity. | Use hierarchy levels as candidate refinements and solve the exact cost/diameter trade-off for optimization queries. | ORION cannot claim the hierarchy or higher-order expressivity itself. |
| APP-C | C. Zhou, X. Wang, M. Zhang, **From Relational Pooling to Subgraph GNNs**, ICML 2023 | Builds more expressive graph representations through labels/subgraphs and WL relations. | Empirically and exactly identify the cheapest refinement that closes registered optimization fibres. | “Richer GNNs distinguish more graphs” is not residual novelty. |
| APP-C | C. Graziani et al., **The Expressive Power of Path-Based Graph Neural Networks**, ICML 2024 | Establishes path-based expressivity and cycle-counting advantages. | Evaluate path/cycle features as registered FiberGuard repairs under acquisition and solver costs. | Cycle/path expressivity is donor-owned. |
| APP-C | U. Johansson, C. Sönströd, H. Boström, **Conformal Regression with Reject Option**, PMLR 230, 2024 | Combines conformal regression with rejection to trade coverage for interval informativeness. | Compare exact fibre intervals/abstention with statistical rejection, especially on high-confidence exact collisions. | ORION cannot claim generic reject-option or conformal validity. |
| APP-C | A. Gangrade, A. Kag, V. Saligrama, **Selective Classification via One-Sided Prediction**, AISTATS 2021 | Develops selective classification with accuracy–coverage guarantees. | Exact action-disagreement certificates for combinatorial decisions and matched-cost routing. | Selective classification is donor-owned. |
| APP-C | S. Tayebati et al., **Learning Conformal Abstention Policies for Adaptive Risk Management**, arXiv:2502.06884 | Learns adaptive abstention policies for LLM/VLM risk management. | Exact representation-diameter state and exact feature acquisition within combinatorial optimization. | Adaptive abstention/RL is not ORION novelty. |
| APP-AB | B. Bogaerts et al., **Certified Symmetry and Dominance Breaking for Combinatorial Optimisation**, arXiv:2203.12275 | Provides machine-verifiable certification for symmetry and dominance reasoning in SAT and optimization. | Certificate ownership for finite-signature normal forms, realization gates, and interaction-aware support budgets. | Generic proof logging and certified symmetry/dominance breaking are donor-owned. |
| APP-AB | A. Hoen, A. Oertel, A. Gleixner, J. Nordström, **Certifying MIP-based Presolve Reductions for 0–1 Integer Linear Programs**, arXiv:2401.09277 | Certifies MIP presolve transformations using pseudo-Boolean proof logging. | Verify a support cap and complete move-interaction registry whose theorem changes the finite search universe. | “Certified presolve” alone is not residual novelty. |
| APP-AB | M. Anders et al., **Faster Certified Symmetry Breaking Using Orders With Auxiliary Variables**, arXiv:2511.16637 | Improves practical proof logging/checking for SAT symmetry breaking. | Measure whether ORION normal-form certificates add a distinct cap/interaction benefit beyond mature certifying symmetry tools. | Speeding proof logging for symmetry is donor-owned. |
| APP-AB | S. Shoja, D. Arnström, D. Axehill, **A Unifying Complexity-Certification Framework for Branch-and-Bound Algorithms for MILP/MIQP**, arXiv:2503.16235 | Certifies worst-case B&B computational measures for parametric optimization and solver strategies. | Architecture-specific search-volume consequences from exact normal forms and complete move interactions. | ORION cannot claim generic B&B complexity certification. |
| APP-AB | S. Dold et al., **Pseudo-Boolean Proof Logging for Optimal Classical Planning**, arXiv:2504.18443 | Produces independently checkable lower-bound/optimality certificates for planning. | Test transfer of support-normal-form certificates to a non-Pauli exact domain and compare certificate burden. | Generic proof-producing optimal planning is donor-owned. |
| APP-D | R. B. Thapa, S. Staab, **Causality and Minimal Supports in Recursive Datalog**, arXiv:2607.16443 | Develops minimal supports, causes, responsibility, and deletion robustness for recursive Datalog. | Typed cap-preserving authority, fixed-point merge safety, and origin-sensitive anti-splicing. | Minimal supports, hitting sets, causality, and deletion robustness are donor-owned. |
| APP-D | M. Calautti et al., **The Complexity of Why-Provenance for Datalog Queries**, arXiv:2303.12773 | Studies why-provenance complexity for recursive Datalog and practical SAT-based computation. | Exact typed nonpromotion and merge authorization, not generic why-provenance. | Provenance witness computation is donor-owned. |
| APP-D | Y. Wang et al., **MAP-Graph: Provenance-Aware Shared Memory for Multi-Agent Workflows**, arXiv:2608.10509 | Uses typed execution graphs, lineage, permission eligibility, trust, and risk-sensitive gates for multi-agent memory. | Demonstrate a reviewed hybrid-proof/merge error specifically prevented by exact typed closure and origin coordinates beyond lineage filtering. | Provenance-aware agent memory and permission filtering are current competing systems. |
| APP-D | Z. Wang, **Proof-Carrying Agent Actions**, arXiv:2606.04104 | Defines portable action certificates and runtime governance across heterogeneous agent systems. | Provide theorem-backed authority nonpromotion and graph-merge safety as a complementary decision semantics. | Portable action envelopes and runtime receipts are donor-owned. |
| APP-D | A. Dalugoda, **HDP: Human Delegation Provenance in Agentic AI Systems**, arXiv:2604.04522 | Cryptographically records multi-hop human delegation provenance. | Handle logical evidence conjunction, refutation, typed caps, and incompatible-origin merge beyond signed delegation chains. | Human delegation token chains are donor-owned. |
| APP-D | N. Gallo, **Proof-of-Continuity**, arXiv:2607.08906 | Requires non-expansive authority propagation along causal execution chains and prevents merged authority sources. | Compare ORION’s positive-rule merge criterion and proof-tree explanations against continuity-based authority propagation. | Non-expansive authority propagation is not an unoccupied claim. |
| APP-NQ | S. Cichacz, **Disjoint zero-sum subsets in Abelian groups and its application — survey**, arXiv:2410.22245 | Surveys disjoint zero-sum subsets and applications to orthomorphisms and graph labeling. | Exact `C_5^3` thresholds as proof-producing solver oracles and disjoint binary-kernel packing benchmarks. | General applications of disjoint zero sums to graph labeling/orthomorphisms are donor-owned. |
| APP-NQ | S. Elledge, G. Hurlbert, **An application of graph pebbling to zero-sum sequences in abelian groups**, arXiv:math/0409588 | Uses graph pebbling to prove zero-sum results with number-theoretic/group applications. | Search-to-proof methodology and exact kernel-packing translation for the frozen constants. | Generic cross-applications of zero-sum theory are established. |
| APP-NQ | Y. Fan et al., **On short zero-sum subsequences of zero-sum sequences**, arXiv:1108.2866 | Studies short zero-sum thresholds and `C_0(G)`-type phenomena for finite abelian groups. | Exact early constants/spectrum and source-level proof-producing computation for `C_5^3`. | Short-zero-sum concepts and broad group families are donor-owned. |
| APP-Q1 / D | B. R. C. A. de Lima et al., **Towards Datalog on Quantum Annealers**, arXiv:2608.04645 | Compiles recursive Datalog to Ising models with correctness lemmas verified in Lean. | Not a direct application target, but a warning that quantum/Datalog bridges already exist; Q1 and D must retain distinct compiler and authority claims. | Do not market a generic “Datalog plus quantum” connection as novel. |

# Residual positioning by paper

## Q1

The application residual is a faithful map from the sharp frozen-grammar support theorem to one maintained compiler/runtime resource, including complete production moves and material exact benefit. The theorem alone does not supply production impact.

## Integrated A+B

The residual is not proof logging or Davenport theory. It is the exact conjunction of finite-signature normal forms, proof-language ownership, production realization, cross-move interaction, and a verified search cap.

## Paper C

The residual is not generic GNN expressivity or abstention. It is an exact, query-specific representation audit with endpoint witnesses, proof-carrying intervals/action sets, and exact cost-aware repair integrated into learned optimization.

## Paper D

The residual is not generic provenance, causality, agent memory, or action receipts. It is typed cap-preserving nonpromotion, exact merge closure, and origin-sensitive anti-splicing demonstrated on a reviewed policy error.

## Nonquantum paper

The residual application is proof-producing exact computation and disjoint binary-kernel packing. Classical zero-sum applications remain donor-owned unless a new exact bridge and external discriminator are proved.

# Submission gate

Before any top-tier submission, a human specialist must review the full source set, verify exact statement overlap, add missing primary literature, and sign a claim-by-claim residual matrix. The current file is a research seed, not a novelty or venue certificate.

`PRIMARY_SOURCE_POSITIONING_R9_SEEDED__HUMAN_SPECIALIST_AUDIT_OPEN`
