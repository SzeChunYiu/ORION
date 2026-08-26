# ORION-01 submission package

**Primary target:** PRX Quantum (stretch)  
**Fallbacks:** npj Quantum Information; Quantum; another strong quantum-information/quantum-algorithms venue according to editor fit.

This package is editorial material. The scientific claim boundary remains `CLAIM_LEDGER_V2.md`.

## Proposed title

**Sharp Support-Two Normal Forms for Shared-Tag TARE Quantum Compilation**

Alternative, slightly broader:

**Exact Support Complexity and Coupling Regimes in Shared-Tag TARE Quantum Compilation**

The first title is preferred because it states the theorem rather than the research history.

## One-sentence result

For a declared three-block shared-Tag TARE-M2 compiler under its support-count objective, arbitrary-support auxiliary Pauli frames are unnecessary: every exact optimum admits frame support at most two for every system size, while an exact two-qubit counterexample proves support one insufficient.

## Significance statement

Block-encoding constructions can expose large auxiliary representation spaces even when the target operator is fixed. This work gives an exact normal-form theorem for one nontrivial TARE compiler family: the optimal auxiliary-frame coupling scale is **exactly two qubits, independent of system size**. The proof is analytic and identifies the same weight-two parity obstruction realized by the optimizer's sharp counterexample, connecting the normal-form boundary to an explicit compiler trade rather than merely observing sparsity. The result also separates normal-form complexity from the richer finite-domain taxonomy inside that normal form.

## Why the result may interest a broad QIST editor

1. **Exact, all-size statement.** The main result is not a benchmark trend: `kappa_R6M=2` holds for arbitrary `n` within the declared grammar/objective.
2. **Sharpness.** The paper gives both the all-`n` upper bound and an exact support-one impossibility witness.
3. **Mechanistic proof boundary.** The combinatorial exchange fails exactly at weight two, matching the observed optimal frame-for-Tag coupling mechanism.
4. **Compiler normal-form consequence.** A representation family that superficially permits support growing with `n` collapses to an `O(n^12)` raw frame-candidate family for the fixed six-slot grammar.
5. **Honest external boundary.** TARE and generic Pauli-frame/symplectic optimization receive zero novelty credit; finite trade classifiers and chemistry results are supporting evidence, not promoted into universal claims.

## Draft editor cover letter

Dear Editors,

We submit **“Sharp Support-Two Normal Forms for Shared-Tag TARE Quantum Compilation.”**

Tag-and-Restore Encoding (TARE) introduces substantial freedom in the auxiliary Pauli frames, shared Tag operator, target assignment and Restore structure used to block-encode Pauli combinations. We ask a structural question distinct from heuristic circuit optimization: *how complicated must an exact optimum actually be?*

For a precisely defined three-block shared-one-bit-Tag TARE-M2 family, we prove that the intrinsic uniform frame-support number is exactly two. Every unrestricted optimum, for arbitrary system size and target instance within the grammar, has an equally good representative whose frame Paulis act on at most two qubits. The proof uses a two-bit symplectic/Tag parity class and a proper zero-sum subset exchange, together with an analytic local bound on the three-way Restore penalty. The bound is sharp: a completely enumerated two-qubit support-one family has optimum 6 while the unrestricted optimum is 5.

The sharpness is mechanistically informative. The exchange theorem fails precisely on the weight-two parity patterns realized by the optimal frame-for-Tag coupling witness. Thus the mathematical obstruction and the compiler mechanism identify the same boundary. Supporting exact finite-domain work prospectively predicts donor-exact behavior on a previously unread public DUCC Hamiltonian, while later adversarial work is disclosed to show that the finite trade taxonomy should not be generalized beyond its registered domains.

We make no claim to have introduced TARE, anticommuting unitary partitioning, Pauli-frame optimization or binary-symplectic circuit simplification. Our claimed contribution is the sharp grammar-specific support theorem and its coupling boundary. Two bounded literature searches, including one after the exact theorem statement was fixed, did not locate a prior equivalent; we record that only as a search result rather than a novelty certificate.

All theorem evidence, exact counterexamples, protocols and deterministic reproduction artifacts are public in the accompanying repository. The manuscript explicitly distinguishes analytic proof, machine corroboration, finite-domain evidence and later follow-up limitations.

Sincerely,

[Authors]

## Data and code availability statement

All code and data used for the reported results are contained in the public ORION repository. The main theorem's analytic proof is provided in `HUMAN_PROOF_R6S_2026-08-22.md`; the original machine certificate is `MAX_R6S_ALL_N_COMPOSITION_RESULTS.json`; the exact support-one counterexample is in `MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json`; and a standalone checker that imports no ORION quantum/compiler module is provided as `independent_human_proof_sanity.py`. Public Hamiltonian inputs are source/blob pinned in the corresponding receipts. Reproduction commands are listed in `REPRODUCE.md`.

## Reproducibility statement

The publication-facing theorem is analytic. Machine enumeration is used as independent corroboration/stress testing rather than as an extrapolation from finite size to arbitrary `n`. The sharp lower-bound witness is exact under a support-one enumerator whose completeness is specified prospectively in the frozen R6O protocol. Canonical manuscript/proof/claim-ledger bytes are content-bound by `papers/Q_SERIES_CONTENT_BINDING_V1.json`, and framework/paper consistency is checked by the Q-series publication tests.

## Claim-language guide

Preferred:

- “We prove a sharp support-two normal form for the declared TARE-M2 grammar/objective.”
- “The intrinsic uniform frame-support number is two.”
- “A bounded literature search did not locate a prior equivalent.”

Avoid:

- “TARE only needs two-qubit frames.”
- “All block encodings reduce to support two.”
- “We prove quantum advantage.”
- “First ever” / “nobody has studied this.”
- “The two discovered trades are universally complete.”

## Submission checklist

Internal items completed:

- [x] final all-`n` theorem incorporated;
- [x] sharp support-one lower-bound witness incorporated;
- [x] human analytic proof;
- [x] standalone independent-implementation sanity check;
- [x] donor subtraction / bounded novelty map;
- [x] final exact-statement novelty refresh;
- [x] later QG limitation disclosed;
- [x] claim ledger synchronized;
- [x] figures plan updated;
- [x] reproduction guide;
- [x] framework/paper/harness sync specification and content binding;
- [x] external quantum-expert pre-review explicitly skipped by owner without converting it to PASS.

At upload time:

- [ ] insert author names/affiliations;
- [ ] render journal-format PDF and figures;
- [ ] normalize bibliography to venue style;
- [ ] rerun the exact-statement literature refresh if materially later than 2026-08-22;
- [ ] run repository publication/harness test suite on the exact submission commit;
- [ ] archive the submission commit SHA/DOI/preprint identifier after upload.
