# Literature entailment and novelty audit

Search date: 2026-08-28

## Method

Queries combined exact quantum compilation, algorithm selection, instance-space analysis, compiler-option prediction, verified optimization, exact synthesis, Pauli compilation, stabilizer preparation, circuit benchmarks and connectivity overhead. Crossref and OpenAlex were used for discovery, then DOI records and available primary abstracts were checked. Metadata-only rows are never used for a scientific claim beyond bibliographic identification. No search result is treated as a novelty certificate.

## Nearest-work entailment

| Work | Evidence basis read | Entailed scope used here | Novelty subtraction |
|---|---|---|---|
| Rice, *The Algorithm Selection Problem*, <https://doi.org/10.1016/S0065-2458(08)60520-3> | primary metadata; chapter title; abstract unavailable in Crossref | historical attribution to the algorithm-selection problem only | selecting an algorithm from instance information is not new |
| Smith-Miles, *Cross-disciplinary perspectives on meta-learning for algorithm selection*, <https://doi.org/10.1145/1456650.1456656> | primary DOI metadata and abstract | algorithm selection is related to meta-learning and instance characteristics | broad feature-to-algorithm selection is donor work |
| Smith-Miles and Muñoz, *Instance Space Analysis for Algorithm Testing*, <https://doi.org/10.1145/3572895> | primary DOI metadata and abstract | instance-space analysis maps problem features and algorithm performance for testing and insight | interpretable performance footprints and algorithm regions are donor work |
| Katial et al., QAOA instance dependence, <https://doi.org/10.1287/ijoc.2024.0564> | primary DOI metadata and abstract | instance-space analysis is applied to quantum-optimization parameter initialization | quantum instance-space use is already established |
| Moussa et al., *To quantum or not to quantum*, <https://doi.org/10.1088/2058-9565/abb8e5> | primary DOI metadata and abstract | algorithm selection is applied to quantum versus classical optimization | quantum/classical selection is donor work |
| Quetschlich et al., compilation-option prediction, <https://doi.org/10.1109/QSW59989.2023.00015> | primary metadata; abstract unavailable in Crossref | title-level identification of quantum compilation-option prediction | compilation-option prediction is not claimed as new |
| Quetschlich et al., *MQT Predictor*, <https://doi.org/10.1145/3673241> | primary DOI metadata and abstract | automatic device selection and device-specific compiler composition are evaluated across circuits and devices | automated device/compiler choice and feature-conditioned performance are donor work |
| Hietala et al., verified optimizer, <https://doi.org/10.1145/3434318> | primary DOI metadata and abstract | a quantum-circuit optimizer with machine-checked correctness exists | verified circuit optimization is donor work |
| Iten et al., exact pattern matching, <https://doi.org/10.1145/3498325> | primary DOI metadata and abstract | exact and practical pattern matching is used for circuit optimization | exact local optimizer patterns are donor work |
| Duncan et al., ZX simplification, <https://doi.org/10.22331/q-2020-06-04-279> | primary DOI metadata and abstract | graph-theoretic ZX-calculus simplification reduces circuits | global algebraic circuit simplification is donor work |
| Quetschlich et al., *MQT Bench*, <https://doi.org/10.22331/q-2023-07-20-1062> | primary DOI metadata and abstract | a scalable benchmark suite supports evaluation of quantum software and design-automation tools | compiler benchmarking and heterogeneous test sets are donor work |
| Li et al., *QASMBench*, <https://doi.org/10.1145/3550488> | primary DOI metadata and abstract | a low-level quantum benchmark suite supports evaluation and simulation | low-level circuit benchmarking is donor work |
| Bravyi et al., optimal Clifford circuits, <https://doi.org/10.1038/s41534-022-00583-7> | primary DOI metadata and abstract | optimal Clifford circuits are computed for bounded qubit counts and used to study synthesis | bounded exact Clifford synthesis is donor work |
| Yuan and Zhang, connectivity overhead, <https://doi.org/10.22331/q-2025-05-28-1757> | primary DOI metadata and abstract | depth overhead from arbitrary connectivity constraints is characterized | hardware-connectivity overhead is donor work and absent from the present structural costs |
| Peres and Galvão, Pauli-based compilation, <https://doi.org/10.22331/q-2023-10-03-1126> | primary DOI metadata and abstract | Pauli-based computation is used for compilation and hybrid computation | Pauli-based compilation is donor work |
| van den Berg and Temme, simultaneous diagonalization, <https://doi.org/10.22331/q-2020-09-12-322> | primary DOI metadata and abstract | Pauli clusters are simultaneously diagonalized to reduce Hamiltonian-simulation circuits | Pauli-cluster optimization is donor work |
| Paykin et al., PCOAST, <https://doi.org/10.1109/QCE57702.2023.00087> | primary metadata; abstract unavailable in Crossref | title-level identification of a Pauli-based circuit-optimization framework | Pauli optimization frameworks are donor work |

The manuscript also cites Izmaylov et al., <https://doi.org/10.1021/acs.jctc.9b00791>, for unitary partitioning. Its contribution is treated as a parent construction, not a novelty comparator.

## Hostile alternative

The strongest alternative is that this paper is instance-space analysis with four quantum examples. That alternative absorbs the general feature-performance map, algorithm footprints, option prediction, and benchmark logic.

The residual survives only in the exact typed objects that the cited performance-mapping work does not by itself establish:

1. a constructive feasible witness explaining a strict compiler gap;
2. an all-size normal form separated from a named mechanism taxonomy;
3. an intrinsic support number separated from a safe proof-derived ceiling;
4. an exact objective region where one normalization proof applies, with silence outside;
5. a representation-level impossibility certificate from mixed feature cells;
6. a near-injective in-domain conversion that is rejected by prospective transfer.

This residual is a combination and reporting discipline, not a claim that each component is individually unprecedented.

## Claim-language decision

- Remove or avoid: `first`, `novel`, `general compiler law`, `universal phase diagram`, `superior compiler`, `physical advantage`, `compact predictor`.
- Retain: `we define` for the manuscript's record structure, `we prove` for the two exact normalization statements and six-term equivalence, and `we observe` for the two-model slack relation.
- State explicitly that algorithm selection, instance-space analysis, compiler-option prediction, verified optimization, exact synthesis, benchmarking, Pauli compilation and connectivity analysis are donor work.

## Freshness and limitation

This is a bounded submission-date search, not an exhaustive priority proof. Crossref abstracts were unavailable for three conference/chapter records; those rows support identification only. A venue editor or external domain reviewer may identify a closer collision, which would require claim contraction or retargeting rather than weakening the evidence standard.
