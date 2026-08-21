# ORION-QN S2/S3 donor absorption — structured search and oracle-resource frontier

Status: **RESEARCH ABSORPTION / PRE-PROTOCOL — NO S2/S3 POSITIVE CLAIM**  
Programme: `SzeChunYiu/ORION#734`  
Date / literature cutoff for this packet: **2026-08-21**  
Parent: `VS1_P6_P2_P4_LOCAL_SIMULATION_PROTOCOL_V1.md`

## 1. Active frontier question

After S1A establishes whether ORION-QN can execute and verify a genuine unstructured Grover kernel under a bounded query-model claim, what scientific residual remains for structured discovery and expensive oracle construction?

The hostile reading is:

> A square-root query theorem is not a research contribution, hybrid quantum/classical benchmarking is not a research contribution, and an implementation that compares against a weak classical loop is not evidence of quantum value.

The surviving ORION-QN question is narrower:

> Can an evidence-governed research system bind a theorem-valid quantum search route, its coherent access/oracle construction, a structure-exploiting classical incumbent, and a non-self-authorizing verification/authority receipt into one reproducible eligibility decision that correctly returns `QUANTUM_QUERY_ADVANTAGE_ONLY`, `QUANTUM_PROJECTED_FT_ADVANTAGE`, `CLASSICAL_PARENT_SUFFICIENT`, or `CANNOT_CHECK` as the regime changes?

## 2. Donor D1 — Brehm & Weggemans 2026 structured k-SAT hybrid benchmarking

Primary paper:

- Martijn Brehm and Jordi Weggemans, **Assessing fault-tolerant quantum advantage for k-SAT with structure**, *Quantum* 10, 1975 (2026), DOI `10.22331/q-2026-01-20-1975`.

Observed public code repository:

- `martijnmartijnmartijnmartijn/Quantum-advantage-k-SAT-with-structure`
- observed `main` commit: `05ac0ddabc37ef237b7aa35e8a2dccab6ccc8d42`

### Mechanisms absorbed

The paper/code already owns the broad idea of **hybrid benchmarking** quantum search/backtracking against materially stronger classical solving under realistic structure and fault-tolerant resource coordinates.

The public repository explicitly combines:

- a basic backtracking solver whose tree data supports quantum-backtracking complexity calculation;
- modern classical SAT solving;
- SBVA preprocessing + CaDiCaL, described by the repository as the winner of the 2023 SAT competition;
- separate quantum query, `T`-depth and `T`-count coordinates;
- exponential fits to median observed complexity;
- crossover analysis under assumed `T`-gate times.

The 2026 result is a mandatory hostile boundary: almost all apparent speedups vanish when even modest instance structure or `T`-count is considered, with only a limited Grover regime remaining under `T`-depth assumptions.

### ORION-QN disposition

`ADOPT AS STRONG PARENT / NOVELTY STRIKE`.

ORION-QN may **not** claim novelty for:

- comparing quantum backtracking/Grover against a strong classical solver;
- using structured SAT distributions;
- reporting `T`-depth / `T`-count rather than query counts alone;
- estimating quantum/classical crossover regimes;
- discovering that structure can erase a theoretical quantum speedup.

### New S2 obligation derived from D1

S2 needs **two distinct classical comparators**, because theorem validity and practical advantage answer different questions:

1. `C_TREE_MATCHED` — the exact deterministic classical backtracking tree/test model required to instantiate the selected quantum-backtracking theorem. This is the semantic/theorem comparator.
2. `C_STRUCTURE_STRONG` — the strongest reproducible structure-aware classical solver available under the registered benchmark information/budget. This is the advantage comparator.

A quantum route may be theorem-valid relative to `C_TREE_MATCHED` while still terminating `CLASSICAL_PARENT_SUFFICIENT` relative to `C_STRUCTURE_STRONG`.

That distinction becomes a first-class ORION-QN receipt coordinate rather than an informal caveat.

## 3. Donor D2 — quantum-oracle resource modelling and synthesis

Primary current preprint:

- Zhihang Li et al., **Modeling and Resource Optimization for Quantum Oracles**, arXiv:`2605.21380` (2026).

The work introduces an explicit hierarchical oracle-description/evaluation model and a space-depth optimization method. Its existence is sufficient to strike the idea that "ORION-QN counts oracle construction" is novel by itself.

### ORION-QN disposition

`ADOPT / STRONGER-ORACLE HOSTILE PARENT`.

ORION-QN may not claim novelty for explicit quantum-oracle gate/depth accounting or oracle circuit optimization.

### New S3 obligation derived from D2

`QOracleContract` must distinguish at least:

```text
semantic predicate/oracle relation
construction algorithm identity
construction input/access
one-time construction resources
per-call resources
inverse/uncompute resources
controlled form resources when required
workspace/ancilla trade-off
reuse horizon
precision/error coordinates
```

A unit-cost query comparison cannot set an end-to-end terminal while any load-bearing coordinate above is unresolved.

## 4. Donor D3 — concrete Grover-oracle resource accounting

Mandatory prior:

- David Prokop, Petros Wallden, and David Joseph, **Resource analysis of a Grover-search quantum algorithm for the shortest vector problem**, arXiv:`2402.13895`.

This line of work concretely decomposes Grover-search oracle costs into qubits, gates/depth and fault-tolerant resources for a real problem family.

### ORION-QN disposition

`ADOPT AS APPLICATION-LEVEL RESOURCE PARENT`.

The residual cannot be "we wrote down a detailed Grover oracle resource receipt."

## 5. Donor D4 — tree-size-aware quantum backtracking

Relevant algorithmic parent:

- Andris Ambainis and Martins Kokainis, **Quantum algorithm for tree size estimation, with applications to backtracking and 2-player games**, arXiv:`1704.06774`.

The algorithm explicitly works with local exploration of an unknown search tree and gives a quantum tree-size estimator plus a backtracking speedup related to the actually explored tree size.

### ORION-QN disposition

`ADOPT / THEOREM-MODEL PARENT`.

S2 must not reduce quantum backtracking to an unexplained square-root of a post-hoc classical runtime. The registered tree/local-access model and theorem assumptions must be checkable from the `QProblemContract` and `QAccessContract`.

## 6. Expert-cell synthesis

### Q1 — algorithms / complexity

A valid theorem-level speedup must identify the exact search-tree/oracle model. Strong classical structure exploitation can dominate without contradicting the theorem. Therefore theorem validity and practical route preference are separate coordinates.

### Q2 — quantum PL / reversible implementation

The coherent child/predicate/check operations needed by quantum backtracking are not free simply because their classical counterparts exist. Reversible realization, garbage and uncomputation remain explicit.

### Q3 — verification / statistics

Fitted asymptotic exponents, median runtime fits and crossover estimates need their own provenance/uncertainty receipts. A fitted crossover is projected evidence, not direct hardware evidence.

### Q4 — FTQC / resources

`T`-depth and `T`-count can reverse conclusions. No scalar resource proxy is constitutional. Both must remain visible before any chosen hardware model maps them to runtime.

### Q5 — ORION architecture

The useful ORION residual is the typed integration:

```text
research problem
-> theorem eligibility
-> access/oracle derivability
-> classical-incumbent selection
-> quantum resource construction
-> measurement/verification
-> bounded authority terminal
```

P8 remains outside the quantum executor.

### Q6 — hostile no-hidden-speedup review

The easiest false positive is to compare a theorem-matched quantum backtracking route only to the primitive backtracking algorithm from which the tree is derived. S2 must give a strong structure-aware classical solver first right of refusal for the advantage claim.

## 7. Candidate scientific residual after donor absorption

The current prospective residual is **not a new quantum algorithm**.

Candidate residual:

> **Proof-carrying quantum eligibility under heterogeneous incumbents:** a typed scientific execution contract that can certify that a quantum route is mathematically eligible under one exact access/tree model while separately adjudicating whether it is useful relative to the strongest same-information structure-aware classical route, without laundering theorem validity into resource/authority superiority.

This remains a candidate residual, not a novelty claim. It must survive broader novelty search and experimental discrimination.

## 8. Frozen design consequences for S2

Before S2 outcomes, the protocol must bind:

```text
QProblemContract
QTreeAccessContract
QTheoremEligibilityReceipt
QOracleContract
C_TREE_MATCHED identity/resources
C_STRUCTURE_STRONG identity/resources
QBacktrackingKernel identity/resources
QMeasurementContract
QVerificationReceipt
QResourceReceipt
QAdvantageReceipt
```

Required terminal distinctions:

```text
THEOREM_ASSUMPTIONS_NOT_MET -> CANNOT_CHECK_ACCESS_MODEL
THEOREM_VALID_QUERY_GAIN_BUT_STRONG_CLASSICAL_WINS -> CLASSICAL_PARENT_SUFFICIENT
THEOREM_VALID_QUERY_GAIN_ONLY -> QUANTUM_QUERY_ADVANTAGE_ONLY
PROJECTED_FT_REGIME_SURVIVES_STRONG_CLASSICAL -> at most QUANTUM_PROJECTED_FT_ADVANTAGE
```

No S2 simulator execution can issue physical end-to-end advantage.

## 9. Frozen design consequences for S3

S3 is no longer a toy `oracle cost multiplier` alone. It must produce an **oracle-cost phase diagram** over at least:

- one-time coherent construction;
- quantum per-call + inverse cost;
- ancilla/workspace budget;
- classical predicate/preprocessing cost;
- allowed reuse horizon;
- Grover/backtracking query count;
- measurement/repetition cost.

The numeric grid will be frozen in a separate packet before S3 result aggregation.

Primary scientific discriminator:

> Does ORION-QN correctly downgrade an otherwise valid query-level quantum result as the oracle construction/access regime crosses the point where the strongest classical route is no longer dominated?

This is a **routing/adjudication** result unless a genuinely new algorithmic/resource law emerges.

## 10. Saturation / next search

This packet is not novelty closure. Before promoting the candidate residual, search at minimum:

- quantum algorithm selection / portfolio routing;
- resource-aware quantum compilation and full-stack optimizers;
- algorithm configuration / selection with performance models;
- proof-carrying/verified quantum compilation;
- access-model-aware dequantization and quantum advantage certification;
- hybrid quantum/classical workflow selection.

If a donor already combines theorem eligibility + same-information access derivability + strong-classical first refusal + independent evidence/authority receipt semantics, ORION-QN must absorb it and narrow again.

## 11. Current terminal

`S2_S3_DONOR_ABSORPTION_COMPLETE__HYBRID_BENCHMARKING_AND_ORACLE_RESOURCE_ACCOUNTING_DONOR_OWNED__PROOF_CARRYING_ELIGIBILITY_RESIDUAL_OPEN`

This terminal authorizes a prospective S2/S3 protocol design. It does not authorize implementation-result claims or novelty.
