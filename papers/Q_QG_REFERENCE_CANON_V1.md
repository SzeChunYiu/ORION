# ORION-Q / ORION-QG verified reference canon V1

Date checked: 2026-08-21
Method: `nature-academic-search` discovery + `nature-ref-verifier` field-level metadata check.
Purpose: provide a small verified donor/parent bibliography that every V2 manuscript must cite before any broader venue-specific bibliography is rendered.

This is not a complete related-work review. It is the **minimum mandatory canon** whose omission would make the novelty/positioning claims misleading. Preprints must be rechecked for title/version/publication changes immediately before submission.

## Metadata status vocabulary

- `VERIFIED_PRIMARY` — publisher/DOI/arXiv primary record checked.
- `VERIFIED_SECONDARY` — reliable bibliographic source checked, primary page may be inaccessible.
- `ARXIV_CURRENT` — current arXiv record checked; publication status may change.
- `RECHECK_AT_SUBMISSION` — time-sensitive metadata or title/version.

## Quantum-compilation core

| ID | Verified reference | Identifier | Status | Required in |
|---|---|---|---|---|
| QC-1 | Niclas Schillo, Andreas Sturm, Rüdiger Quay. **TARE: Block Encoding Linear Combinations of Pauli Strings Without Ancilla State Preparation.** 2026. | arXiv:2601.05740v4; DOI `10.48550/arXiv.2601.05740` | `ARXIV_CURRENT` + `RECHECK_AT_SUBMISSION` | Q1, QG1, QG2 |
| QC-2 | Artur F. Izmaylov, Tzu-Ching Yen, Robert A. Lang, Vladyslav Verteletskyi. **Unitary Partitioning Approach to the Measurement Problem in the Variational Quantum Eigensolver Method.** *J. Chem. Theory Comput.* 16(1), 190–195 (2020). | DOI `10.1021/acs.jctc.9b00791` | `VERIFIED_PRIMARY` | Q1 donor background; QG1 when anticommuting partitioning is discussed |
| QC-3 | Matthew P. Harrigan et al. **Expressing and Analyzing Quantum Algorithms with Qualtran.** 2024. | arXiv:2409.04643 | `ARXIV_CURRENT` | QG2 resource-analysis donor; optional Q1/QG1 context |
| QC-4 | Georg Moser, Michael Schaper. **Automated Expected Cost Analysis for Quantum Programs.** 2026. | arXiv:2604.03971 | `ARXIV_CURRENT` | QG2 mandatory static-analysis donor |
| QC-5 | Tyler LeBlond, Christopher Dean, George Watkins, Ryan S. Bennink. **Realistic Cost to Execute Practical Quantum Circuits using Direct Clifford+T Lattice Surgery Compilation.** | arXiv:2311.10686 | `ARXIV_CURRENT` / publication status recheck | QG2 representative compilation/resource-estimation donor |

### QC-1 title-drift warning

Earlier repository prose sometimes uses **“Block Encoding Linear Combinations of Pauli Strings Using the Stabilizer Formalism.”** The current arXiv v4 title located on 2026-08-21 is **“TARE: Block Encoding Linear Combinations of Pauli Strings Without Ancilla State Preparation.”** Final BibTeX must use the metadata current at submission, not a cached earlier title.

## Algorithm-selection / regime-map ancestry

| ID | Verified reference | Identifier | Status | Required in |
|---|---|---|---|---|
| AS-1 | John R. Rice. **The Algorithm Selection Problem.** *Advances in Computers* 15, 65–118 (1976). | DOI `10.1016/S0065-2458(08)60520-3` | `VERIFIED_PRIMARY/DBLP` | QG1 mandatory conceptual ancestor |
| AS-2 | David H. Wolpert, William G. Macready. **No Free Lunch Theorems for Optimization.** *IEEE Trans. Evol. Comput.* 1(1), 67–82 (1997). | DOI `10.1109/4235.585893` | `VERIFIED_PRIMARY/IBM+DOI` | QG1 optional conceptual boundary; do not use as a novelty substitute |
| AS-3 | Kate Smith-Miles, Mario Andrés Muñoz. **Instance Space Analysis for Algorithm Testing: Methodology and Software Tools.** *ACM Computing Surveys* 55(12), Article 255, 1–31 (2023). | DOI `10.1145/3572895` | `VERIFIED_PRIMARY` | QG1 **mandatory primary parent** |
| AS-4 | Mario Andrés Muñoz et al. **instancespace: A Python package for insightful algorithm testing through Instance Space Analysis.** *SoftwareX* 31, 102246 (2025). | DOI `10.1016/j.softx.2025.102246` | `VERIFIED_PRIMARY` | QG1 current-tooling context, optional |

### QG1 positioning rule

QG1 may **not** claim novelty for:
- mapping regions in feature/instance space where algorithms behave differently;
- selecting algorithms from instance features;
- discovering that performance depends on problem structure.

Its candidate residual must be stated more narrowly: exact/witness-carrying compiler trade mechanisms, theorem/counterexample authority, objective-indexed phase boundaries, and tests of whether the chosen structural vocabulary determines regime membership.

## Autonomous-research / scientific-agent canon

| ID | Verified reference | Identifier | Status | Required in |
|---|---|---|---|---|
| AR-1 | Chris Lu et al. **The AI Scientist: Towards Fully Automated Open-Ended Scientific Discovery.** 2024. | arXiv:2408.06292 | `ARXIV_CURRENT` | Q2 broad autonomous-research donor; Q3 context |
| AR-2 | Deepak Nathani et al. **MLGym: A New Framework and Benchmark for Advancing AI Research Agents.** 2025. | arXiv:2502.14499 | `ARXIV_CURRENT` | Q3 benchmark parent |
| AR-3 | Jonathan Bragg et al. **AstaBench: Rigorous Benchmarking of AI Agents with a Scientific Research Suite.** 2025. | arXiv:2510.21652 | `ARXIV_CURRENT` | Q2/Q3 mandatory benchmark donor |
| AR-4 | Rui Meng et al. **ScientistOne: Towards Human-Level Autonomous Research via Chain-of-Evidence.** 2026. | arXiv:2605.26340 | `ARXIV_CURRENT` | Q2 **mandatory provenance/verifiability donor**; Q3 context |
| AR-5 | Tianyu Liu et al. **Benchmarking AI Agents for Addressing Scientific Challenges Across Scales** (SciAgentArena). 2026. | arXiv:2606.12736 | `ARXIV_CURRENT` | Q3 mandatory current benchmark context; Q2 optional |
| AR-6 | Yutaro Yamada et al. **Towards End-to-End Automation of AI Research.** 2026. | arXiv:2606.15497 | `ARXIV_CURRENT` | Q2 current end-to-end automation context, optional |

### Q2/Q3 donor-subtraction rule

- ScientistOne/Chain-of-Evidence owns the broad claim that research-agent outputs should be claim-to-evidence traceable and audited for references, scores and method-code alignment.
- AstaBench, MLGym and SciAgentArena own substantial territory in controlled scientific-agent evaluation and benchmark design.
- Q2 must therefore headline **negative-result successor discipline**, not evidence provenance or scientific-agent benchmarking generally.
- Q3 must headline **inter-instrument diagnosis/agreement on unresolved frontier questions with deferred scoring**, not generic research-agent benchmarking.

## Typed/scoped state and memory canon

| ID | Verified reference | Identifier | Status | Required in |
|---|---|---|---|---|
| TS-1 | Hanxiang Chao, Yihan Bai, Rui Sheng, Tianle Li, Yushi Sun. **STALE: Can LLM Agents Know When Their Memories Are No Longer Valid?** 2026. | arXiv:2605.06527 | `ARXIV_CURRENT` | Q4 mandatory current stale-memory donor |
| TS-2 | Misha Sulpovar, Benn R. Konsynski, Qaish Kanchwala, Gabe Goodhart. **ContextNest: Verifiable Context Governance for Autonomous AI Agent.** 2026. | arXiv:2607.02116 | `ARXIV_CURRENT` | Q4 mandatory current provenance/version-governance donor |

### Q4 donor-subtraction rule

Q4 may not claim novelty for:
- detecting or revising stale memories generally;
- provenance/version tracking generally;
- deterministic retrieval/context governance generally;
- value-of-information as a general decision principle.

The retained manuscript object is bounded matched-information mechanism isolation: whether typed/scoped state is load-bearing for specific downstream decisions under frozen exact-synthetic worlds, including first-right-of-refusal negatives.

## Mandatory citation insertion map

### Q1
- Introduction first TARE mention → QC-1.
- Anticommuting/unitary-partitioning donor discussion → QC-2.
- Related-work/resource-estimation paragraph if retained → representative QC-3/QC-5, without implying direct equivalence.

### Q2
- autonomous research systems → AR-1 and/or AR-6;
- rigorous scientific-agent evaluation → AR-3;
- claim/evidence verifiability → AR-4;
- any statement about current science-agent limits → AR-3/AR-5, with exact scope.

### Q3
- research-agent benchmark landscape → AR-2, AR-3, AR-5;
- end-to-end scientific agents → AR-1/AR-6;
- explicitly state that these score task/system outputs, whereas Q3 proposes a different frontier inter-instrument object.

### Q4
- stale-memory revision → TS-1;
- governed/versioned/provenanced agent context → TS-2;
- add classic VOI/provenance references only after exact metadata verification; do not rely on uncited textbook memory.

### QG1
- TARE family → QC-1;
- algorithm-selection ancestry → AS-1;
- primary instance-space parent → AS-3;
- optional no-free-lunch context → AS-2;
- current InstanceSpace tooling only if discussed → AS-4.

### QG2
- TARE family → QC-1;
- compositional resource analysis → QC-3;
- automated static quantum cost analysis → QC-4;
- realistic compilation/resource-estimation pipelines → QC-5.

## References still requiring a second verification round

Before submission, run a complete manuscript-to-bibliography audit and add/verify:
- the exact upstream DUCC Hamiltonian Library citation/metadata/licence;
- any Clifford/stabilizer synthesis references named in Q1/QG1;
- any SixLCU/StabPrep donor references if those families rely on external published methods rather than repository-defined comparison families;
- classic value-of-information and provenance references used in Q4;
- venue-specific references introduced during analogue-paper calibration.

## Reference-integrity hard gates

1. Every factual field-history statement must have a citation.
2. Every citation in the bibliography must be cited in the manuscript.
3. Every cited DOI/arXiv identifier must resolve and match title/authors.
4. Preprint title/version drift must be refreshed within 14 days of submission.
5. A metadata-only search hit is not support for a scientific claim; the abstract/full primary record must be read for claim fit.
6. No paper is cited merely because it is prestigious or likely to supply a reviewer.
