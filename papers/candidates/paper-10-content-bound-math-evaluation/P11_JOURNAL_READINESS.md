# ORION-21 peer-review readiness

**Programme identity:** ORION-21 — Content-Bound Mathematical Evaluation (#471)  
**Submission title:** *Bytes, Builds, and Meaning: Content-Bound Evaluation for Evolving Lean Repositories*  
**Target venue family:** Journal of Automated Reasoning / peer-reviewed automated-reasoning venue; final portal metadata remains author-controlled.  
**Scientific terminal:** `P11_BOUNDED_EVALUATION_METHODS_PAPER`  
**Package terminal:** `PEER_REVIEW_READY` when the exact PR head passes repository CI and `check_p11_peer_review_ready.py`.

This terminal does **not** reopen the unsupported broad V3 empirical claim. It turns the existing immutable ORION-21 evidence into a complete, bounded methods/experience paper.

## Scientific closure

- [x] Exact 457-file / 31-module / 5,655,364-byte subject bound to a Mathlib revision and Lean toolchain.
- [x] Original positive-looking V2 retained and explicitly invalidated.
- [x] Parser contamination quantified: 1,289/4,861 trajectories (26.52%), 3,903 leaked top-level boundaries.
- [x] V2.1 separately frozen before repaired outcome.
- [x] Corrected blocked recurrence result reported with bootstrap interval and frozen null distributions.
- [x] Source recurrence kept distinct from native proof-state/dependency structure and downstream proof utility.
- [x] Eight prospectively selected native Lean audit subjects accepted; planted invalid proof rejected.
- [x] Two complete native replays byte-identical.
- [x] Source/revision/statement/attempt substitution controls fail content-bound matching.
- [x] Task-id-only stale-success control preserved.
- [x] Artifact identity, extraction validity, native acceptance, semantic faithfulness and scientific authority separated in prose and claim ledger.
- [x] Historical invalid/null/missing evidence retained rather than reconstructed.
- [x] Constructive nearest-work saturation keeps pinned/versioned benchmarks, native traces, tactic mining and semantic-faithfulness mechanisms outside standalone novelty.

## Submission closure

- [x] Full editable LaTeX manuscript.
- [x] Abstract, keywords, tables, threats to validity, reproducibility, data/code availability and generative-AI disclosure.
- [x] Submission-specific bibliography including 2026 benchmark-integrity and version-robustness pressure.
- [x] Submission-specific claim ledger mapping every numerical/headline claim to committed evidence.
- [x] Reproduction guide distinguishes source-only checks from native Lean replay requirements.
- [x] Cover-letter draft.
- [x] Declarations interface that does not invent funding, ORCID, institutional or competing-interest attestations.
- [x] Deterministic package linter.
- [x] Prospective ORION-21 V3 protocol kept as future work, not mixed into current results.

## Explicit nonclaims

ORION-21 does not claim:

- reusable tactic discovery;
- downstream proof-search improvement;
- statement faithfulness from compilation;
- theorem correctness beyond the exact native judgment;
- native replay of all 457 files;
- cross-revision or cross-repository mechanism transfer;
- novelty of content hashing, pinned revisions, native verification, proof-state tracing, tactic mining, or version-aware proof refactoring;
- acceptance by any journal or completion of independent external peer review.

## Exact-head gate

The package is `PEER_REVIEW_READY` only on an exact PR head for which:

1. repository `ci` is successful;
2. any candidate-paper workflow triggered by the changed path is successful or demonstrably not applicable;
3. `python3 papers/candidates/paper-10-content-bound-math-evaluation/check_p11_peer_review_ready.py` exits zero on the same tree;
4. no later manuscript/source edit has occurred without re-running the gate.

External submission portal attestations (affiliation, funding, competing interests, ORCID, preferred reviewers) remain author-controlled metadata and are not inferred by ORION.
