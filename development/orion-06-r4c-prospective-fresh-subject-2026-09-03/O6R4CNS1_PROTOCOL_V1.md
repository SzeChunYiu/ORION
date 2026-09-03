# O6R4CNS1 — prospective fresh-subject confirmation of the R1-revived R4C mechanism (protocol V1)

Status: FROZEN 2026-09-03, BEFORE the content of any non-committed
SNIPRS/hamiltonian notebook was fetched, parsed, or read, and BEFORE any
pair witness, lambda, frontier, or Pareto quantity was computed on any
fresh subject.

Study id: `O6R4CNS1`. Lane: `development/orion-06-r4c-prospective-fresh-subject-2026-09-03/`.
Driver: `research/extensions/orion-q/max_o6_r4c_prospective_fresh_subject.py`.
Targeted blocker: `ORION06_NEGATIVE_REVIVAL_R1_SUCCESSOR.json` →
`paper_freeze.remaining_gates[0]` = "protected prospective new-subject
confirmation for the R4C/R5B mechanism claims" (R4C half; the R5B half was
discharged by O6R5BNS1). This study attacks exactly that gate for the R4C
mechanism on ONE fresh notebook. It grants no freeze, no novelty, no R6, no
end-to-end authority.

## 1. Scientific question

The R1 revival (`development/orion-05-06-negative-revival-r1-2026-08-27/`,
lever `R4C_ACTUAL_RESTORE_OUTER_SELECT_PARETO_REPLAY`) executed the frozen
actual-resource pair accounting on the ALREADY-OPEN H2 notebook subject
(14 non-identity terms, 135,135 perfect matchings, exact) and obtained
`IMPROVED` — strict parent-dominating points inside the 1 percent legacy
budget — with residual "open-subject mechanism evidence only".

O6R4CNS1 asks: does the SAME frozen mechanism, with the SAME frozen
decision rule, applied to the full non-identity Pauli list printed by a
deterministically selected, never-previously-read notebook of the SAME
subject repository, (a) admit such a subject at exact-enumerable scale, and
(b) produce strict parent-dominating points within the frozen 1 percent
legacy budget? Either direction is a first-class result: strict dominance
on a never-read subject is the prospective confirmation the freeze gate
names; parent-envelope retention on a never-read subject is a prospective
refutation of the mechanism claim's generalization beyond already-open
subjects, with the failure localized to the fresh subject.

## 2. Pre-freeze disclosure (mirrors the O6R5BNS1 discipline)

To design the deterministic selection rule, ONLY the git tree metadata of
`SNIPRS/hamiltonian` at the pinned commit was inspected (file paths and git
blob ids via the GitHub trees API; canonical listing digest of all 79 blobs
= `ae1734455d7bfbf8b1805e13d3f4e2609dd4d90da33700b7bbcd578a31e4169d`).
No notebook content outside the already-committed H2 subject was fetched or
read before this freeze. Paths and blob ids contain no Hamiltonian
coefficient. No R4C-mechanism quantity (no pair witness, no legacy or
actual lambda, no frontier, no Pareto point) was computed on any fresh
candidate before this freeze. The pinned commit equals the repository HEAD
at freeze time (`c628c05430e9409f3c637f2f65f05c40438d1c29`), so every
candidate blob is immutable.

## 3. Frozen fresh-subject selection rule (candidate ladder)

Repository: `SNIPRS/hamiltonian` at pinned commit
`c628c05430e9409f3c637f2f65f05c40438d1c29`.

Excluded by path (metadata-only exclusions, frozen):
- `simulation-H2.ipynb` and `.ipynb_checkpoints/simulation-H2-checkpoint.ipynb`
  — the committed R4C subject family (blob `bb8ded60…` and its checkpoint
  variant; the committed receipt and the R1 replay bind to this family).
- `simulation-LiH.ipynb` and `.ipynb_checkpoints/simulation-LiH-checkpoint.ipynb`
  — the R4C development-evidence family (protocol V1 of the confirmatory
  study: "No LiH outcome may authorize this confirmation").
- Every non-`.ipynb` path (`*.py`, `__pycache__/`, `out/`, `save/`,
  `iterate.sh`) — not notebooks.

Candidate order (frozen): all remaining TOP-LEVEL `*.ipynb` paths in
bytewise lexicographic order FIRST, then all remaining
`.ipynb_checkpoints/*-checkpoint.ipynb` paths in bytewise lexicographic
order:

1. `QDrift.ipynb` (`dad3ebb6802290ad0026564415c3df3383590770`)
2. `commute.ipynb` (`65bec82f9b55a0482261e3949939eeb137cd1244`)
3. `diagonalize.ipynb` (`617c2432ad269903a1fb81ba2021a920a9ddb4ea`)
4. `hamiltonian.ipynb` (`7fdabdc148f10b2db28c3d3973e3f20fddc92d39`)
5. `phase.ipynb` (`f26c06aadb14ce6d736a6fa59b1dede560ccda50`)
6. `plots.ipynb` (`fe7aa34cf45eb2f7cf13d29fcf2a8257cab926c7`)
7. `script.ipynb` (`dd8fd9df59c3a8d9540806b0cd7a6552725b1273`)
8. `simulation.ipynb` (`546398ee586db47c979f410d754cd32a312e25cf`)
9. `.ipynb_checkpoints/QDrift-checkpoint.ipynb` (`dad3ebb6802290ad0026564415c3df3383590770`)
10. `.ipynb_checkpoints/commute-checkpoint.ipynb` (`47e88be5465e34b85c954e153cbc74c2ddf2c649`)
11. `.ipynb_checkpoints/diagonalize-checkpoint.ipynb` (`617c2432ad269903a1fb81ba2021a920a9ddb4ea`)
12. `.ipynb_checkpoints/hamiltonian-checkpoint.ipynb` (`7fdabdc148f10b2db28c3d3973e3f20fddc92d39`)
13. `.ipynb_checkpoints/phase-checkpoint.ipynb` (`f26c06aadb14ce6d736a6fa59b1dede560ccda50`)
14. `.ipynb_checkpoints/plots-checkpoint.ipynb` (`85b3808dfa267319519575c1c201a1fd300547a9`)
15. `.ipynb_checkpoints/script-checkpoint.ipynb` (`2fd64429bf421126b7000c94ce0f6fd186fbd01f`)
16. `.ipynb_checkpoints/simulation-checkpoint.ipynb` (`f8355ce72300d164bc2c344ce41be56908b3d218`)

Per-candidate admission, in the frozen order, until the FIRST admission:

- Fetch the raw file at the pinned commit; verify the git blob sha-1
  (sha1 of `blob <len>\0<bytes>`) equals the pinned blob id above.
- Extract per cell, with the R4C notebook regex VERBATIM
  (`^\s*(\d+) \[([+\-0-9.eE]+) '(-?)([IXYZ]+)'\]\s*$`, identity index 0
  dropped, sign applied), deduplicated by printed index (first occurrence
  wins within a cell).
- Subject cell = the cell with the LARGEST extracted non-identity count;
  ties resolved to the LOWEST cell index.
- Structural admission conditions (outcome-blind): extracted count `L` in
  the subject cell satisfies `L >= 6`, `L` even, `L <= 14`. The cap 14 is
  the committed H2 subject's exact scale (135,135 matchings, the proven
  exact-enumeration budget of the R1 replay).
- Every rejection is recorded (path, blob, per-cell counts, reason:
  `no_matching_lines` / `odd_L` / `L_below_minimum` / `L_over_cap` /
  `inconsistent_pauli_length` / `blob_mismatch`). Pauli-word length
  consistency across the subject cell's extracted rows is a structural
  precondition (the pair-witness machinery takes one register width `n`);
  it is computable without any mechanism quantity.

Deviation note, frozen here: the original confirmatory protocol treats an
odd `L` as the terminal `CANNOT_CHECK_PAIR_PROTOCOL_ODD_L` for ITS single
pinned subject. This study pre-registers a MULTI-candidate ladder
(structural admission conditions only — parity, minimum, cap — all
computable without any mechanism quantity), exactly as the R6R/O6R5BNS1
admission ladders reject candidates on n-qubit and budget caps. Parity and
scale are structural preconditions, not outcomes; skipping on them cannot
select for or against the mechanism claim.

If no candidate admits: terminal `ORION06_R4C_NS1_FRESH_SUBJECT_UNAVAILABLE`.

## 4. Frozen mechanism and decision rule (R1 replay, verbatim)

Imported frozen machinery only (no math copied):
`papers/orion-06-recursive-recovery/revival/orion06_negative_revival_r1.py`
(`perfect_matchings`, `canonical_pair_witness`, `pauli_word_key`,
`_legacy_pair_lambda`, `_pair_lambda`, `_sum_witness_vectors`,
`_pareto_points`, `_point_dominates`, `_point_equal`, `sha256_value`,
`POINT_COORDS`, `run_r4c`).

On the admitted fresh subject (terms, `n` = Pauli-word length):

1. All `L(L-1)/2` pair witnesses via `canonical_pair_witness`; every
   witness check must pass (assert). `direct` = type
   `DIRECT_ANTI_UNITARY`; per-pair `legacy_lambda = sqrt(2) hypot(|a|,|b|)`
   and `actual_lambda = hypot(|a|,|b|)` if direct else legacy.
2. Enumerate ALL perfect matchings (exact; `(L-1)!!` total). Per matching:
   `legacy_Lambda` (sum of legacy), `Lambda_joint` (sum of actual),
   `direct_unitary_blocks`, summed witness vector
   (`parity_CNOT`, `controlled_Rz`, `controlled_H`,
   `controlled_Pauli_support`, `AND2_compute_uncompute_pairs`,
   `max_extra_conjunction_scratch`), serialized matching over printed
   source indices, matching and witness sha256s.
3. Parent (`strongest parent`) = the minimum-`legacy_Lambda` point, ties
   broken by serialized matching (bytewise), exactly as `run_r4c`.
4. Pareto = `_pareto_points` over ALL points (POINT_COORDS coordinates).
5. Decision rule, verbatim: budget `1.01 * parent["Lambda_joint"]`;
   in-budget Pareto points = those with `Lambda_joint <= budget + 1e-12`;
   `strict` = in-budget Pareto points with `_point_dominates(point,
   parent)` (dominance is antisymmetric — all coordinates `<=` and the
   coordinate tuples unequal — so a point that dominates the parent is
   never dominated by it); `tradeoffs` = Pareto points with
   `not _point_equal(point, parent)`.
   - strict nonempty → `IMPROVED` /
     `ORION06_R4C_NS1_PROSPECTIVE_STRICT_PARENT_DOMINANCE_CONFIRMED__ONE_FRESH_NOTEBOOK_ONLY`
   - else tradeoffs nonempty → `PARETO_TRADEOFF_ONLY` /
     `ORION06_R4C_NS1_FRONTIER_TRADEOFF_ONLY__ONE_FRESH_NOTEBOOK_ONLY`
   - else → `RETAINED_NEGATIVE` /
     `ORION06_R4C_NS1_PARENT_ENVELOPE_RETAINED__GENERALIZATION_REFUTED_ON_THIS_NOTEBOOK`

## 5. Committed-machinery control (runs BEFORE the fresh verdict)

Before any fresh mechanism quantity, the driver executes the COMMITTED H2
replay `r1.run_r4c(r1._protocol())` end-to-end (network fetch of the
committed notebook, subject sha verification, all-matchings enumeration,
and the committed `MAX_R4C_FRESH_H2_HETEROGENEOUS_PAIR_RESULTS.json`
frontier binding) and asserts: `matching_count == 135135`, every
`legacy_frontier_binding` row passes, `revival_outcome == "IMPROVED"`,
`original_negative_preserved is True`. A control failure aborts with
terminal `ORION06_R4C_NS1_CONTROL_FAILURE` (exit 3, no claims). The
control touches only the already-open committed subject.

## 6. Staging and digests

Stage 1 (printed and flushed BEFORE any fresh witness/lambda computation):
selection record + admitted subject (path, blob, cell index, full extracted
term list) + canonical stage-1 digest. Stage 2: the frozen replay and
verdict of Section 4. The receipt records `stage1_digest` and a
`stage1_before_frontier` gate.

## 7. Gates (hard)

- Anti-instrument import gate (AST scan of the driver; forbidden
  substrings `qiskit`, `openfermion`, `cirq`, `pyscf`) — pass required.
- Every candidate's observed git blob sha-1 equals its pinned tree id;
  the run fetches no path other than the evaluated candidates' paths (all
  recorded in the receipt).
- Subject family exclusions hold by path (no `simulation-H2*`, no
  `simulation-LiH*`).
- Subject cell rule as frozen (max count, lowest index on ties).
- `L` even, `6 <= L <= 14`; enumerated matchings equal `(L-1)!!`.
- Every pair witness check passes; control assertions of Section 5 pass.
- Stage-1 digest emitted before any frontier computation (module flag).
- Determinism: the registered run is executed twice; the two result JSONs
  must be byte-identical (no runtime fields in the receipt).
- No committed file modified; only this protocol, the driver, the run log,
  and the result JSON are added.

## 8. Terminals and authority

`ORION06_R4C_NS1_PROSPECTIVE_STRICT_PARENT_DOMINANCE_CONFIRMED__ONE_FRESH_NOTEBOOK_ONLY`
/ `ORION06_R4C_NS1_FRONTIER_TRADEOFF_ONLY__ONE_FRESH_NOTEBOOK_ONLY` /
`ORION06_R4C_NS1_PARENT_ENVELOPE_RETAINED__GENERALIZATION_REFUTED_ON_THIS_NOTEBOOK`
/ `ORION06_R4C_NS1_FRESH_SUBJECT_UNAVAILABLE` /
`ORION06_R4C_NS1_CONTROL_FAILURE`.

Authority: PROSPECTIVE ONE-FRESH-NOTEBOOK MECHANISM CONFIRMATION ONLY —
no novelty, no freeze, not R6, not end-to-end, no new-molecule-family
claim (the notebook's molecule may coincide with a known family; that is
recorded, not claimed). Either confirmatory or refutational direction is a
first-class outcome.

## 9. Runtime and outputs

Single run well under 3600 s (the committed H2 control enumerates 135,135
matchings — the R1 precedent; a fresh subject admits only at `L <= 14`,
the same bound). Outputs: stdout stage-1 lines +
`ORION06_R4CNS1_RESULT_JSON=<path>`;
`development/orion-06-r4c-prospective-fresh-subject-2026-09-03/O6R4CNS1_RESULTS.json`
(canonical sorted JSON, schema `ORION.ORION06.R4CProspectiveFreshSubject.v1`).
