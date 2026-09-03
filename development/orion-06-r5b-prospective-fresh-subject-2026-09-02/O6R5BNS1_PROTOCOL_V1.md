# O6R5BNS1 — prospective fresh-subject confirmation of the R1-revived R5B mechanism (protocol V1)

Status: FROZEN 2026-09-02, BEFORE any coefficient of any non-committed DUCC
library file was fetched, parsed, or read, and BEFORE any parent envelope or
controlled-aware frontier value was computed on any fresh subject.

Study id: `O6R5BNS1`. Lane: `development/orion-06-r5b-prospective-fresh-subject-2026-09-02/`.
Driver: `research/extensions/orion-q/max_o6_r5b_prospective_fresh_subject.py`.
Targeted blocker: `ORION06_NEGATIVE_REVIVAL_R1_SUCCESSOR.json` →
`paper_freeze.remaining_gates[0]` = "protected prospective new-subject
confirmation for the R4C/R5B mechanism claims" (R5B half). This study attacks
exactly that gate for the R5B mechanism on ONE fresh source file. It grants no
freeze, no novelty, no R6, no end-to-end authority.

## 1. Scientific question

The R1 revival (`development/orion-05-06-negative-revival-r1-2026-08-27/`,
result `ORION06_NEW_RESOURCE_REVIVAL.json`) executed the frozen
controlled-select-aware exact-representation-and-rematching mechanism
(`CONTROLLED_SELECT_AWARE_EXACT_REPRESENTATION_AND_REMATCHING`) on the H4
six-term batch and obtained `IMPROVED` (two strict parent-dominating points
inside the 1 percent Lambda budget). Its frozen residual reads: "H4 was already
open; protected new-subject confirmation remains unearned". The original R5B
negative was on equilibrium N2, also already open.

O6R5BNS1 asks: does the SAME frozen mechanism, with the SAME frozen decision
rule, applied to the frozen six-term window-champion batch of a deterministically
selected, never-previously-read DUCC library source file, (a) admit such a
subject, and (b) produce strict parent-dominating points within the frozen
1 percent Lambda budget? Either direction is a first-class result: strict
dominance on a never-read file is the prospective confirmation the freeze gate
names; parent-envelope retention on a never-read file is a prospective
refutation of the mechanism claim's generalization beyond already-open
subjects, with the failure localized to the fresh subject.

## 2. Pre-freeze disclosure (mirrors the MAX-R6R discipline)

To design the deterministic selection rule, ONLY git tree metadata of the public
library at the pinned commit was inspected (file paths and git blob ids via the
committed `max_r6r_prospective_fresh_subject.pinned_tree_listing` blob-filtered
clone; `git ls-tree -r`). No `*.ducc.results.txt` content of any path outside
the already-committed subject set was fetched or read before this freeze.
Path/blob metadata contains no Hamiltonian coefficient. One timing calibration
was run on ALREADY-OPEN data only: `try_admit` on the R6R-committed benzene
DUCC2 cc-pVDZ 6Elec_6Orbs blob (admitted in 24.2 s, 390 terms) to establish
that the n_qubits <= 12 window-replay stage is budgetable; no R5B-mechanism
quantity (no canonical pair witness, no controlled frontier, no Pareto point)
was computed on any benzene file before this freeze.

## 3. Frozen fresh-subject selection rule

Library: npbauman/DUCC-Hamiltonian-Library at pinned commit
`be306f5830549304176365750d712093950bbdde` (the commit every committed
ORION-Q chemistry receipt pins), enumerated by the committed R6R tree-listing
machinery; the listing digest is recorded in the receipt.

- Excluded molecule directories (verbatim R6R set, which also protects the
  stretched-N2 discriminator): {H2, H2O, H4, LiH, N2}.
- Additionally excluded git blob ids (subjects already read by committed
  receipts): `b98792b1055dbac0ebf2a7576f72412e3e4ac6c5` (H4 cc-pVDZ 2.0au
  DUCC3), `15369e8e886efbb3d32f3b2dfe2cfbb96ddebeba` (N2 equilibrium DUCC2),
  `5f157e7bd05aac26b30b10dcea44b7650b7f8648` (H2O Eq cc-pVTZ),
  `5c02c72b88e12b391ea1d8f77eb6b3e04fc2a915` (benzene cc-pVDZ 6Elec_6Orbs
  DUCC2 — the R6R fresh subject).
- Eligibility (verbatim R6R `parse_candidate` path grammar): path ends with
  `.ducc.results.txt`; some path segment is `DUCC2` or `DUCC3`; top-level
  directory not excluded; some path segment matches
  `^(FrozenCoreCCSD_)?(\d+)Elec_(\d+)Orbs$` with even electron count 2k and
  orbital count m satisfying 1 <= k < m; then n_occ = k, n_orb = m,
  n_virt = m - k, n_qubits = 2m.
- Compute cap (declared a priori, justification identical to R6R's recorded
  rationale): eligible candidates must satisfy n_qubits <= 12; the P10 window
  replay above 12 qubits is not budgetable under the 3600 s run cap.
- Candidate order (verbatim R6R): (n_qubits ascending, path ascending,
  bytewise).
- Admission per candidate (verbatim R6R `try_admit` on the frozen
  `r6f._frozen_batch` machinery): blob-verified fetch (observed git blob SHA-1
  equals the ls-tree blob id); frozen parse + Jordan-Wigner with identity term
  dropped and terms sorted by (-|coeff|, x, z); at least two improving R6B
  window champions; the frozen batch is the first two champions with six
  unique source indices from distinct windows; the six batch targets are
  pairwise commuting. At most the first 6 candidates are tried; every failure
  is recorded verbatim (path, blob, reason).

Pre-freeze expectation from metadata inspection only (not binding on the run):
the first candidate in the frozen order is
`Benzene/cc-pVDZ/FrozenCoreCCSD_6Elec_6Orbs/DUCC3/benzene.cc-pvdz_files/restricted/ducc/benzene.cc-pvdz.ducc.results.txt`
(blob `cd32e1e77cc3...`, 12 qubits) — a never-read file at a different DUCC
level than every committed subject. The run computes the selection itself; if
the deterministic rule admits a different file, that file is the subject.

Honest scope note (frozen): the fresh subject is a never-read SOURCE FILE
(new blob, new coefficients, new active-space Hamiltonian), not a new molecule
family — the benzene family was admitted by R6R at DUCC2. The claim boundary
in Section 8 says exactly this.

## 4. Frozen machinery (imported only, never copied)

- `research/extensions/orion-q/max_r6r_prospective_fresh_subject.py`:
  `pinned_tree_listing`, `parse_candidate`, `eligible_candidates`, `try_admit`,
  `PINNED_COMMIT`.
- `research/extensions/orion-q/max_r6f_donor_clifford_preconditioned_tare3.py`
  (via `try_admit` → `r6f._frozen_batch`): source fetch + blob verification +
  parse + Jordan-Wigner + R6B window-champion replay.
- `papers/orion-06-recursive-recovery/revival/orion06_negative_revival_r1.py`
  (the committed R1 revival runner): `perfect_matchings`,
  `canonical_pair_witness`, `controlled_pair_frontier`, `_aggregate_matching`,
  `_pareto_points`, `_point_dominates`, `_point_equal`, `POINT_COORDS`.
- No mathematical constant, cost model, threshold, or aggregation rule is
  redefined locally; every number in the receipt comes from these modules or
  from integer/float arithmetic on their outputs.

## 5. Frozen staged procedure (parent envelope before candidates)

Stage 1 (no `controlled_pair_frontier` call happens before stage-1 output is
printed; enforced by a module flag asserted inside stage 2):
1. enumerate the pinned tree, record the listing digest;
2. apply the Section-3 rule in order, admit the subject, record the batch
   (six source indices, champion windows, term count, max_imag, observed blob);
3. compute the PARENT envelope exactly as R1 `run_r5b` did: for each of the 15
   pair edges `canonical_pair_witness` (canonical internal-G TARE-M2 witness,
   direct-anti representation when the pair anticommutes), aggregate all 15
   perfect matchings with `_aggregate_matching`, Pareto-prune with
   `_pareto_points`, and record `minimum_Lambda` and the 1.01 budget;
4. print `ORION06_R5B_NS1_STAGE1_PARENT=<canonical sorted JSON>` and
   `ORION06_R5B_NS1_STAGE1_PARENT_DIGEST=<sha256 of that JSON>`, then flush.

Stage 2 (only after stage 1 is printed):
5. compute `controlled_pair_frontier` for each of the 15 pair edges; record
   per-edge frontier sizes;
6. enumerate every candidate point = every matching crossed with every product
   of per-edge frontier choices (exactly R1 `run_r5b`); Pareto-prune;
7. apply the frozen R1 R5B decision rule verbatim (Section 6).

## 6. Frozen decision rule (verbatim from the R1 protocol R5B attempt)

- Budget: `1.01 * minimum parent Lambda` (+ 1e-12 tolerance).
- A candidate inside the budget is STRICT if it is dominated by no parent
  Pareto point and strictly Pareto-dominates at least one parent point
  (`_point_dominates` on the seven frozen POINT_COORDS coordinates).
- A candidate inside the budget is an EXPANSION if it is dominated by no
  parent point and equals no parent point.
- IMPROVED iff at least one strict candidate exists.
- PARETO_TRADEOFF_ONLY iff no strict candidate but at least one expansion.
- RETAINED_NEGATIVE iff the parent envelope contains or dominates every
  candidate point.

## 7. Frozen verdict space (terminals; no post-hoc weakening)

- `ORION06_R5B_NS1_PROSPECTIVE_STRICT_PARENT_DOMINANCE_CONFIRMED__ONE_FRESH_FILE_ONLY`
- `ORION06_R5B_NS1_PROSPECTIVE_FRONTIER_EXPANDED_NO_STRICT_DOMINANCE__ONE_FRESH_FILE_ONLY`
- `ORION06_R5B_NS1_PROSPECTIVE_PARENT_ENVELOPE_RETAINED__GENERALIZATION_REFUTED_ON_THIS_FILE`
- `ORION06_R5B_NS1_FRESH_SUBJECT_UNAVAILABLE` (the 6-candidate admission loop
  exhausted; failures recorded verbatim; no mechanism computation)
- `ORION06_R5B_NS1_CANNOT_CHECK__CANDIDATE_PRODUCT_OVER_CAP` (integrity gates
  pass but the candidate product exceeds the registered 2,000,000-point cap;
  counts recorded)

Any binding-gate failure (blob mismatch, witness check failure, matching-count
drift, staging violation, non-determinism) raises and fails the run; it is a
defect, not a terminal.

## 8. Frozen claim boundary

A strict-dominance confirmation claims ONLY: the frozen R1-revived
controlled-select-aware exact-representation-and-rematching mechanism, with its
frozen decision rule, produced at least one strict parent-dominating point
inside the frozen 1 percent Lambda budget on the frozen six-term
window-champion batch of ONE deterministically selected, never-previously-read
DUCC library source file, before which no R5B-mechanism quantity on that file
had been computed anywhere. This advances (does not close) freeze gate
`remaining_gates[0]` for the R5B half on one fresh file. It is NOT a new
molecule family, NOT a theorem for all n or all subjects, NOT end-to-end QSVT
superiority, NOT hardware independence, NOT novelty, NOT R6, and authorizes no
final freeze or submission. A retention terminal claims exactly: the mechanism
failed to beat its parent envelope on this one fresh file, localizing the
boundary of the R1 IMPROVED result to already-open subjects.

## 9. Integrity gates (hard assertions, recorded in the receipt)

- Protocol file SHA-256 recorded; driver run at the registration commit
  (base_revision recorded).
- Anti-instrument import gate (AST inspection of the driver's actual imports):
  no qiskit / openfermion / cirq / pyscf dependency; stdlib + numpy + frozen
  repo modules only.
- Pinned provenance: selected subject's observed git blob SHA-1 equals the
  ls-tree blob id (r6f machinery assertion) and the tree-listing digest is
  recorded.
- Fresh subject truly fresh: molecule directory outside the frozen exclusion
  set; blob equals none of the four committed subject blobs; the run fetches
  no path other than evaluated candidates' paths (all recorded).
- Six batch targets pairwise commuting; exactly 15 matchings; parent point
  count exactly 15; every witness check passes on every parent and candidate
  point (asserted inside the frozen machinery).
- Staging: stage-1 digest printed before any `controlled_pair_frontier` call
  (module flag; gate recorded).
- Candidate product cap 2,000,000 (honest CANNOT_CHECK terminal above it).
- Determinism: the registered run is executed twice; the two result JSONs must
  be byte-identical (runtime fields excluded from the receipt).
- No committed file modified; only this protocol, the driver, and the result
  JSON are added.

## 10. Runtime and outputs

Single run well under 3600 s (calibrated: admission ~25 s at n=12 on the open
benzene DUCC2 file; the pair-witness/frontier stage at n_qubits <= 12 is
bounded by the H4 precedent of 341 candidate points and the 2,000,000 cap).
Outputs: stdout stage-1 lines + `ORION06_R5BNS1_RESULT_JSON=<path>`;
`development/orion-06-r5b-prospective-fresh-subject-2026-09-02/O6R5BNS1_RESULTS.json`
(canonical sorted JSON, schema `ORION.ORION06.R5BProspectiveFreshSubject.v1`).
