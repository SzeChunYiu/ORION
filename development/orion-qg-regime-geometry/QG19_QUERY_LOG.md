# QG-19 query log — every retrieval attempt, verbatim, with result counts

Date: 2026-08-22. Branch: `claude/orion-harness-verification-b17qdj`.
Protocol: `QG19_HOSTILE_NOVELTY_PROTOCOL_V1.md` (frozen at `aaf0987a`, unmodified).
Authority: NOT_R6. `novelty_authority: false`. This log grants nothing.

## 0. Retrieval channel and its limits (G6 / G7 disclosure)

Two retrieval mechanisms were available in principle: `WebSearch` (server-side, returns
result links plus tool-rendered passage text) and `WebFetch` / `curl` (direct document
retrieval). **Direct document retrieval was blocked by the session's egress policy on
every domain attempted.** Nine `WebFetch` calls and two `curl` calls were made; all
eleven were refused:

| attempt | target | outcome |
|---|---|---|
| WebFetch | `en.wikipedia.org/wiki/Generalized_distributive_law` | EGRESS_BLOCKED |
| WebFetch | `arxiv.org/html/2602.13494v1` | EGRESS_BLOCKED |
| WebFetch | `en.wikipedia.org/wiki/Courcelle%27s_theorem` | EGRESS_BLOCKED |
| WebFetch | `handwiki.org/wiki/Generalized_distributive_law` | EGRESS_BLOCKED |
| WebFetch | `www.semanticscholar.org/search?q=algebraic+dynamic+programming` | EGRESS_BLOCKED |
| WebFetch | `www.mimuw.edu.pl/~kw305874/thesis.pdf` | EGRESS_BLOCKED |
| WebFetch | `dl.acm.org/doi/10.1109/18.825794` | EGRESS_BLOCKED |
| WebFetch | `link.springer.com/rwe/10.1007/978-1-4614-6624-6_86-1` | EGRESS_BLOCKED |
| WebFetch | `scispace.com/papers/efficient-maximum-likelihood-decoding-…` | EGRESS_BLOCKED |
| curl | `https://arxiv.org/abs/2107.01752` | CONNECT tunnel failed, 403 |
| curl | `https://en.wikipedia.org/wiki/Courcelle%27s_theorem` | CONNECT tunnel failed, 403 |

The proxy status endpoint reports `enabled: true`, so this is an organization egress
policy, not a tooling fault, and per `/root/.ccr/README.md` it was not routed around.

**Consequence, stated plainly:** every passage quoted in this lane is *the text returned
by the search tool*, not text read off the primary document. No source in this run was
verified at document level. Passages are marked `passage_provenance:
websearch_result_text` in the results file. This is a real weakening of G2 and is the
reason no verdict in this lane is recorded as document-confirmed.

## 1. Cap disclosure

* Search-call cap: 90. **Spent: 52.**
* Four of those calls (Q27, Q42, Q43 and their fan-outs) were expanded by the search
  backend into multiple sub-searches; link counts below give the total across sub-searches
  where that happened.
* Direct-fetch attempts: 11. Successful: 0.
* Runtime: within the < 60 min cap.

## 2. The log

Format: `Qn` | family — (i) own vocabulary, (ii) donor-field translation, (iii)
inverted/survey | verbatim query | links returned | bearing?

### C-A — the structural criterion (QG-22 Q3)

| # | family | verbatim query | links | bearing |
|---|---|---|---|---|
| Q1 | (i) | `min-plus dynamic programming over a conserved syndrome linear time exact optimum compilation` | 7 | no direct hit; surfaced min-plus/knapsack equivalence |
| Q2 | (i) | `algebraic dynamic programming semiring framework exact optimization linear time local terms` | 9 | **yes** — semiring/ADP framework |
| Q3 | (i) | `dynamic programming over group homomorphism invariant fixed finite abelian group polynomial time` | 10 | partial — abelian-group algorithmics, not DP |
| Q4 | (ii) | `Gomory group relaxation integer programming dynamic programming over finite abelian group shortest path` | 10 | **yes** |
| Q5 | (ii) | `Aji McEliece generalized distributive law semiring Viterbi transfer matrix junction tree linear time chain` | 9 | **yes** |
| Q6 | (ii)/(iii) | `Courcelle theorem bounded treewidth linear time optimization monadic second order extended` | 10 | **yes** |
| Q7 | (ii) | `"shortest route problem over a finite abelian group" integer programming Gomory abstract` | 10 | **yes** |
| Q8 | (ii) | `Shapiro "Dynamic programming algorithms for the integer programming problem" group knapsack abstract` | 9 | bibliographic only |
| Q9 | (ii) | `transfer matrix method one-dimensional lattice model exact partition function linear in chain length constant state space` | 10 | **yes** |
| Q10 | (ii) | `weighted constraint satisfaction bounded treewidth solved in time O(n d^{w+1}) bucket elimination Dechter` | 9 | **yes** |
| Q11 | (ii) | `Giegerich Meyer "Algebraic Dynamic Programming" yield grammar evaluation algebra Bellman's principle formal framework` | 9 | **yes** |
| Q12 | (iii) | `Bellman principle of optimality state is a sufficient statistic dynamic programming applies when objective additive over stages survey` | 9 | **yes** |
| Q13 | (ii) | `Wolf 1978 efficient maximum likelihood decoding linear block codes using a trellis 2^{n-k} states syndrome Viterbi` | 10 | **yes — decisive** |
| Q14 | (ii) | `syndrome trellis states partial syndrome dynamic programming decoding complexity linear in blocklength exponential in number of parity checks` | 8 | **yes** |
| Q15 | (ii) | `Valiant holographic algorithms homomorphism into finite group polynomial time counting problems` | 10 | adjacent, not bearing on C-A |
| Q16 | (ii) | `"applied to a trellis with no more than" "states" Wolf linear block code Viterbi abstract quote` | 10 | **yes — passage recovered** |
| Q44 | (ii) | `dynamic programming over symplectic invariant Pauli syndrome Clifford circuit optimization linear time exact optimum block structure` | 9 | **yes — in-domain instance** |
| Q46 | (iii) | `"Optimising quantum circuits is generally hard" NP-hard circuit optimization contradicts polynomial time claim` | 10 | **yes — G5 hostile context** |

### C-B — intrinsic support number κ

| # | family | verbatim query | links | bearing |
|---|---|---|---|---|
| Q17 | (i) | `"intrinsic support number" family invariant optimum realized at support bound with matching lower bound` | 10 | **none bearing** — the exact term returned nothing in this sense |
| Q18 | (ii) | `sparsity of optimal solutions integer programming support size bound tight lower bound Aliev De Loera Eisenbrand` | 10 | **yes — decisive** |
| Q19 | (ii) | `Caratheodory rank integer cone minimal support optimal solution survey sparse solutions of linear programs` | 9 | **yes** |
| Q20 | (ii) | `"On the Smallest Support Size of Integer Solutions to Linear Equations" abstract exact smallest support tight` | 5 | **yes** |
| Q21 | (ii) | `survey named invariants minimum number of nonzero components optimal solution sparsity measure combinatorial optimization junta essential variables` | 9 | partial — ℓ0/sparse-optimization vocabulary |
| Q41 | (iii) | `is the support bound tight survey sparse solutions lattices semigroups matching lower bound exact smallest support attained` | 10 | **yes** |

### C-C — regime geometry as a five-component template

| # | family | verbatim query | links | bearing |
|---|---|---|---|---|
| Q22 | (ii) | `superoptimization survey characterizing when a compiler heuristic is already optimal structural predicate regime` | 8 | partial |
| Q23 | (ii) | `equality saturation egg extraction cost model proving optimality of extracted term compiler optimization landscape` | 10 | **yes** |
| Q24 | (i) | `"regime" characterization where a canonical construction attains the optimum quantum circuit compilation donor-optimal region trades witnesses` | 10 | **yes** |
| Q25 | (iii) | `survey methodology characterizing optimality regions of an optimization heuristic phase diagram of solution structure reusable template` | 9 | nothing bearing |
| Q26 | (iii) | `"Phase transitions in quantum-circuit compilation" arXiv 2608.00189 abstract regimes near-optimal configurations` | 9 | **yes** |
| Q39 | (iii) | `survey quantum circuit compilation optimality gap between heuristic and optimal exhaustive characterization when heuristic matches optimum` | 10 | partial |
| Q47 | (ii) | `dominance rules certifying a construction is optimal structural characterization of optimal solutions branch and bound preprocessing framework` | 8 | **yes** |

### C-D — κ ≠ syndrome rank; the rewrite-alignment failure

| # | family | verbatim query | links | bearing |
|---|---|---|---|---|
| Q27 | (ii) | `ZX-calculus rewrite dependent lower bound stabilizer rank not tight invariant depends on chosen normal form T-count` | 40 (4 sub-searches) | **no bearing hit** — backend itself reported no matching result |
| Q28 | (i) | `invariant computed under one rewriting system fails under another confluence presentation dependence rewriting theory complexity measure mismatch` | 9 | partial — confluence/presentation dependence |
| Q29 | (iii) | `limitations of rank-based lower bound methods gap between rank bound and true complexity log-rank conjecture survey` | 10 | **yes** |
| Q42 | (ii) | `minimum weight generating set stabilizer code NP-hard rank does not determine minimum support generators equivalent presentations` | 25 (3 sub-searches) | **yes** |
| Q45 | (iii) | `strength of a lower bound depends on the formulation reformulation integer programming extended formulations bound not invariant` | 10 | **yes** |

### C-E — the negative-history typology

| # | family | verbatim query | links | bearing |
|---|---|---|---|---|
| Q30 | (i) | `typology of negative results categories failed definition null ablation false positive taxonomy first-class record of what failed` | 10 | **yes** |
| Q31 | (ii) | `PROV-O provenance ontology experiment tracking metadata schema recording failed experiments negative results machine learning` | 10 | **yes** |
| Q32 | (iii) | `taxonomy of failure modes in scientific research reproducibility why studies fail categories registered reports null results classification survey` | 8 | partial |
| Q40 | (ii) | `ontology of negative findings scientific claims typed categories abandoned hypothesis subsumed by prior work provenance record` | 6 | **yes** |
| Q43 | (ii) | `ablation study taxonomy component does not help component hurts performance categories reporting negative ablation results standard terminology` | 39 (4 sub-searches) | partial — informal ablation outcome categories |
| Q48 | (iii) | `"Dead Science Walking" publication bias AI scientist pipeline negative results recording abstract` | 9 | **yes** |
| Q50 | (iii) | `null result database infrastructure typed categories of negative outcome recorded as first-class scientific record why an experiment failed` | 9 | **yes** |
| Q51 | (iii) | `"negative and null results in eScience" workshop taxonomy categories of negative results Maheshwari 2017 classification` | 5 | **yes — decisive** |

### C-F — digest custody is not correctness

| # | family | verbatim query | links | bearing |
|---|---|---|---|---|
| Q33 | (ii) | `SLSA provenance attestation "does not" guarantee correctness only integrity of build supply chain security limitations` | 9 | **yes** |
| Q34 | (i) | `reproducible builds bit-for-bit determinism does not imply the software is correct or free of bugs deterministic bug reproduces` | 10 | **yes** |
| Q35 | (i) | `Leek Peng "Reproducible research can still be wrong" PNAS 2015 abstract quote` | 10 | **yes** |
| Q36 | (ii) | `slsa.dev "SLSA does not" cover code quality vulnerabilities "provenance" what SLSA is not scope limitations documentation` | 10 | **yes** |
| Q37 | (ii) | `in-toto attestation integrity of the supply chain not correctness of the artifact proof-carrying code correctness requires a proof` | 9 | **yes** |
| Q38 | (iii) | `ACM artifact review badging levels "Results Reproduced" "Results Replicated" typed badges prevent overclaiming evidence strength` | 7 | **yes** |
| Q49 | (iii) | `"replication laundering" definition governance failure mode reproducing a result does not validate it AI scientist` | 6 | **yes — decisive** |
| Q52 | (iii) | `"Governance Laundering" Meyman taxonomy failure modes attestations treated as evidence cannot support independent verification abstract` | 8 | **yes — decisive** |

## 3. Queries that returned nothing bearing, restated for G1

These are the searches whose emptiness a reader is entitled to inspect:

* **Q17** — `"intrinsic support number" family invariant optimum realized at support bound with matching lower bound`. 10 links, none about a support-budget invariant of an optimization family; results were compressive sensing, LOCAL-model lower bounds, capacity support points.
* **Q25** — `survey methodology characterizing optimality regions of an optimization heuristic phase diagram of solution structure reusable template`. 9 links, all topology optimization / heuristic overviews; no methodological template of the kind C-C states.
* **Q27** — `ZX-calculus rewrite dependent lower bound stabilizer rank not tight invariant depends on chosen normal form T-count`. 40 links across four sub-searches; the backend explicitly reported that the combination "doesn't correspond to a single well-known published result" in its results.
* **Q1** — `min-plus dynamic programming over a conserved syndrome linear time exact optimum compilation`. 7 links; the phrase as such matched nothing. C-A was nevertheless subsumed from Q13/Q16 under different vocabulary, which is the entire reason family (ii) is mandatory.
* **Q8** — `Shapiro "Dynamic programming algorithms for the integer programming problem" group knapsack abstract`. 9 links, bibliographic reference recovered but no abstract text; recorded `CANNOT_ASSESS` at source level.
