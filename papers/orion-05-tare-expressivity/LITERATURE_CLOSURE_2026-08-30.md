# ORION-05 submission-date literature closure — 2026-08-30

## Scope

This is the submission-date refresh required by `JOURNAL_READINESS.md` and the manuscript's hostile-search boundary. It is deliberately targeted to the bounded residual claimed by the paper: the all-`n` support-two normal form, exact counterexamples delimiting narrower families, and the associated regime map for the Schillo–Sturm–Quay stabilizer-formalism block-encoding construction. It is not an assertion that every quantum-compilation paper has been exhaustively searched.

## Search date and queries

Search date: **2026-08-30**.

Targeted searches covered combinations of:

- `TARE`, `Tag`, `Restore`, Pauli, block encoding, stabilizer;
- support-two / weight-two normal form with anticommuting Pauli auxiliary families;
- pairwise anticommuting Pauli block encoding and ancilla structure;
- current 2026 binary-symplectic / Pauli compilation and block-encoding work.

## Nearest/current works checked

1. **Niclas Schillo, Andreas Sturm, Rüdiger Quay, “Block Encoding Linear Combinations of Pauli Strings Using the Stabilizer Formalism,” arXiv:2601.05740 (2026).**
   - Direct donor and origin of the transform-to-pairwise-anticommuting plus stabilizer correction/Restore construction.
   - The current abstract describes the construction, logarithmic ancilla scaling, larger-ancilla trade-offs, four examples and numerical LCU comparisons.
   - It does **not** state the ORION-05 all-`n` support-two structural characterization or its regime boundary.
   - Already cited as `schillo2026blockencoding`.

2. **Zhaohui Yang et al., “Efficient Compilation for Hamiltonian Simulation via Global Binary Symplectic Form Simplification,” arXiv:2608.11579 (2026).**
   - Current global Pauli/BSF compilation work using controlled-Pauli Clifford transformations over a global tableau.
   - Its contribution is holistic Hamiltonian-simulation compilation and gate/depth reduction, not the TARE support-two exactness theorem.
   - Already cited as `yang2026symphony`.

3. **Hantao Nie, Zhijian Lai, Dong An, “Pauli-structured preconditioning for quantum linear system solvers,” arXiv:2606.01733 (2026).**
   - Studies Pauli-structured regrouping and block-encoding normalization in quantum linear solvers.
   - Relevant to structure-aware block-encoding cost, but not a donor for the claimed support-two normal form or TARE regime classification.

4. **Taehee Ko, “Exact and Efficient Circuit Construction for Block Encoding Matrix Polynomials,” arXiv:2608.15161 (2026).**
   - Gives exact compiling of block encodings for matrix polynomials and a distinct interpolation/QSP construction.
   - Does not address the TARE auxiliary-family support classification.

## Decision

**No closer donor was found in this targeted 2026 refresh that collapses the bounded ORION-05 residual.** The manuscript must continue to give the TARE primitive, Tag/Restore identity, generic anticommuting-unitary machinery, Clifford/symplectic compilation and block-encoding optimization **zero novelty credit**. The residual remains only the exact structural result already earned by the frozen evidence: the all-`n` support-two normal form, exact counterexamples delimiting narrower families, and the resulting regime map with its stated unresolved proof boundary.

This closure does not widen the claim, does not establish hardware advantage, and does not convert downstream QG stress tests into independent empirical authority.
