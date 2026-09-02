# O3CS1 — bounded exhaustive certificate for the ORION-03 rung-1 Construction B (cap-to-seed simulation) (protocol V1)

Status: FROZEN 2026-09-03, BEFORE any registered-grid document pair was evaluated.

Study id: `O3CS1`. Lane: `development/orion-03-cap-seed-simulation-2026-09-03/`.
Driver: `research/extensions/orion-03-typed-merge/o3cs1_cap_seed_simulation.py`.
Schema: `ORION.ORION03.CapSeedSimulationBoundedExhaustive.v1`.

## 1. Aim and residual addressed

The ORION-03 Tier-B JAR closure (PR #2128, commit df0b0007b) left the rung-1
formal-separation attempt as `ATTEMPTED__NOT_AIRTIGHT`
(`papers/orion-03-typed-merge-falsification/FORMAL_SEPARATION_ATTEMPT_20260902.md`).
Its Step B ("Construction B") is retained as internal documentation in prose only:

> every capped rule `(A_r → h_r, K_r)` is simulated exactly by adding a fresh
> seed claim `c_r` with `σ(c_r) = K_r` and replacing the rule by
> `(A_r ∪ {c_r} → h_r, Λ)`; ... simultaneous induction on the synchronous
> iterates from bottom gives equality of the `Q`-coordinates of the two least
> fixed points.

The prose induction is not machine-checked anywhere, and it does not explicitly
treat the interaction with the manuscript's refutation clamp (refuted claims are
clamped to the empty label against re-derivation; the prose only requires
`c_r ∉ R`). The named successor V2 (second live corpus: RustSec/GHSA
advisory–licence joins, `SCIENCE_ITEM_DISPOSITION_20260902.md` rung 2) requires
external multi-gigabyte corpus snapshots (pinned crates.io crate/version
snapshot, OSV export) that are not acquirable on this host in this window; per
the lane instructions the next-best EXACT rung is taken instead, and the PR
states this substitution.

O3CS1 asks: does Construction B, executed verbatim by the paper's own frozen
reference evaluator, preserve — on EVERY canonical document of the registered
bounded grid — (RQ1) the `Q`-coordinate least fixed points in the baseline
regime, (RQ2) the `Q`-coordinate least fixed points in the final
(refutation-clamp) regime, and (RQ3) the retracted (claim, license) pairs
restricted to `Q`? Either direction is a first-class outcome: universal
preservation upgrades the retained negative's Step B from prose to a bounded
exhaustive machine certificate; any counterexample refutes the construction as
retained and is recorded verbatim.

## 2. Pre-freeze disclosure (calibration and mechanics only; no verdict data)

Before this freeze, using the driver module's helper functions:

- Mechanics were exercised ONLY on cells OUTSIDE the registered grid —
  `(L=4, n=1, m=1)` (512 documents) and `(L=1, n=4, m=1)` (30,720 documents) —
  asserting only that both evaluations complete and return well-formed output.
  No equality verdict was computed or recorded on any document of any
  registered cell.
- Timing calibration ONLY (no comparisons, results discarded) on 3,000
  documents of the largest registered cell `(L=2, n=3, m=2)`:
  0.038 ms/document-pair, projecting ≈ 2 minutes for the full grid.
- Enumeration-completeness counts (pure counting, no evaluation) verified
  against the closed-form planned counts on full cells `(2,2,1)`, `(1,3,2)`,
  `(3,2,0)`.

## 3. Frozen machinery (imported only, never copied)

- `papers/orion-03-typed-merge-falsification/evidence_license_evaluator.py`
  (the frozen public reference evaluator of the manuscript's "Finite typed
  authority system"): `validate_document`, `evaluate_document` (which computes
  the baseline and refuted least fixed points and the retracted pairs),
  `ValidationError`. Pinned at registration: SHA-256
  `82ecb77dcdbce97d3980152d5053a166227d6a0403d11f021a6f478108b1b86a`
  (origin/main `4f2a223ae...`); the driver hard-asserts this digest at runtime.
- No transfer, fixed-point, clamping, or retraction semantics are redefined
  locally; every label, iteration, and retraction in the receipt comes from the
  frozen evaluator's outputs.

## 4. Frozen definition space and registered grid

Documents are exactly the evaluator's public schema contract (version "1.0";
nonempty license list `Λ`; nonempty claim list with seed subsets of `Λ`; rules
with nonempty body, head a claim, cap subset of `Λ`; refutation subset of
claims). The grid is parameterized by `L = |Λ|`, `n = |claims|`, `m = |rules|`;
within a cell, EVERY assignment of seeds, rule multiset, and refutation set is
enumerated exactly once (rule multisets via combinations-with-replacement over
the sorted rule space, so rule-order permutations are not revisited).

Registered grid (26 cells; the single corner cut is registered here, not chosen
at runtime): all `(L, n, m)` with `L ∈ {1,2,3}`, `n ∈ {1,2,3}`, `m ∈ {0,1,2}`,
EXCEPT `(L=3, n=3, m=2)`, which projects to 58,094,592 canonical documents and
exceeds the registered enumeration cap. Planned canonical documents per cell:

| L | n | m | planned docs |
|---|---|---|---|
| 1 | 1 | 0–2 | 4, 8, 12 |
| 1 | 2 | 0–2 | 16, 192, 1248 |
| 1 | 3 | 0–2 | 64, 2688, 57792 |
| 2 | 1 | 0–2 | 8, 32, 80 |
| 2 | 2 | 0–2 | 64, 1536, 19200 |
| 2 | 3 | 0–2 | 512, 43008, 1827840 |
| 3 | 1 | 0–2 | 16, 128, 576 |
| 3 | 2 | 0–2 | 256, 12288, 301056 |
| 3 | 3 | 0–1 | 4096, 688128 |

Planned total: 2,960,848 canonical documents. Enumeration cap: 4,000,000
(hard-asserted; breach at planning time yields the registered CANNOT_CHECK
terminal, breach at runtime is a defect and raises).

## 5. Frozen construction (verbatim Step B)

For each document `D` with rules `r = (body A_r, head h_r, cap K_r)`, the
simulated document `S(D)` adds, PER RULE INDEX, a fresh claim
`cs1_seed_r<k>` with `seeds = K_r`; replaces rule `r` by
`(body = A_r ∪ {cs1_seed_r<k>}, head = h_r, cap = Λ)`; keeps all original
claims, seeds, other rules, and the refutation set unchanged; `cs1_seed_r<k>`
is never refuted. `S(D)` is passed through the frozen evaluator's own
validation. Both `D` and `S(D)` are evaluated by `evaluate_document` (baseline
regime and final refutation regime in one call).

## 6. Registered questions and comparison rule

Restricted to the original claim set `Q` (the fresh seeds are dropped from all
comparisons):

- RQ1: `baseline_labels` of `evaluate_document(D)` equals `baseline_labels` of
  `evaluate_document(S(D))` on `Q`.
- RQ2: same for `final_labels` (refutation clamp active).
- RQ3: the `retracted` (claim, license) pair lists, restricted to `Q`, are
  equal.

Registered adversarial control (a control that could have failed; probe only,
no claim either way): on cells `(1,2,1)` and `(2,2,1)` (1,728 documents), the
variant `S'(D)` with the FIRST seed claim added to the refutation set
(violating the construction's `c_r ∉ R` boundary condition) is evaluated and
the same RQ1–RQ3 comparison recorded as breaks/held. The construction makes no
claim for `S'`; the tally is recorded as data.

## 7. Frozen verdict space (terminals; no post-hoc weakening)

- `O3_CS1_CAP_SEED_SIMULATION_VERIFIED__BOUNDED_EXHAUSTIVE_ALL_QUESTIONS`
  (every registered document passes RQ1–RQ3)
- `O3_CS1_SIMULATION_REFUTED__COUNTEREXAMPLE_RECORDED`
  (first counterexample recorded verbatim: document, simulated document, both
  evaluations, failed question id; enumeration stops at the counterexample)
- `O3_CS1_CANNOT_CHECK__GRID_OVER_ENUMERATION_CAP`
  (planned total exceeds the registered cap at runtime)

Any binding-gate failure (import gate, evaluator digest drift, machinery
control probes, per-cell enumeration drift without a counterexample, runtime
cap breach) raises and fails the run; it is a defect, not a terminal.

## 8. Frozen claim boundary

A VERIFIED terminal claims ONLY: Construction B as written in
`FORMAL_SEPARATION_ATTEMPT_20260902.md` Step B, executed through the frozen
reference evaluator, preserves the `Q`-coordinate least fixed points (both
regimes) and the `Q`-restricted retractions on every one of the 2,960,848
canonical documents of the registered bounded grid. It is a
documentation-level certificate of a RETAINED NEGATIVE's internal construction.
It is NOT an expressiveness theorem, NOT a separation of any kind, NOT a
manuscript or ledger status change (D3-C1..C15 untouched), NOT a widening of
the frozen V3 surface, NOT novelty authority, and NOT the successor-scope
second-corpus study. A REFUTED terminal claims exactly: the construction as
retained fails on the recorded document; the prose note requires correction
before any future reliance on Step B (manuscript edits are out of this study's
scope and are left to the paper lane).

## 9. Integrity gates (hard assertions, recorded in the receipt)

- Anti-instrument import gate: AST inspection of the driver's actual imports;
  forbidden substrings numpy/scipy/pandas/requests/urllib/socket/http/
  qiskit/openfermion/cirq/pyscf; stdlib + the frozen evaluator only.
- Frozen-machinery digest: the evaluator file's SHA-256 equals the
  registration-time digest hardcoded in the driver.
- Machinery controls that could have failed: `validate_document` rejects a
  duplicate-claim-id document and an unknown-rule-head document.
- Enumeration exactness: per-cell actual count equals the closed-form planned
  count whenever the cell completed without a counterexample.
- Registration pinning: receipt records `base_revision` (git HEAD at run),
  `protocol_sha256`, and the canonical-JSON `result_digest`.
- Determinism: the registered run is executed twice at the registration SHA;
  the two result JSONs must be byte-identical (no timestamps or runtime fields
  in the receipt; wall-clock lives only in the run log).

## 10. Runtime and outputs

Calibrated ≈ 2 minutes (0.038 ms/document-pair on the largest cell); run cap
3600 s. Outputs: `O3CS1_TERMINAL=`, `O3CS1_RESULT_JSON=`,
`O3CS1_RESULT_DIGEST=` on stdout (captured in `RUN_O3CS1.log`), canonical
sorted JSON at `development/orion-03-cap-seed-simulation-2026-09-03/O3CS1_RESULTS.json`
(and `O3CS1_RESULTS.run2.json` for the determinism gate).
