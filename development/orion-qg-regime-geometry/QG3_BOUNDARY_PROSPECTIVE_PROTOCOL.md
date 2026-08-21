# QG-3 Boundary-Engineered Prospective Forecast Protocol (frozen BEFORE any prediction subject was generated or selected)

Status: FROZEN 2026-08-21, BEFORE any Track-A candidate file outside the committed
subject set was fetched, parsed, or read, BEFORE any Track-B synthetic instance was
generated, and BEFORE any predicate, family-minimum, or DP value was computed on any
prediction subject of this lane.
Programme: ORION-QG (charter PROGRAMME_CHARTER_V1.md, lane QG-3), parent ORION-Q MAX.
Branch: claude/orion-harness-verification-b17qdj. Not R6. No novelty credit. No donor
credit. The protected stretched-N2 discriminator is never read.

## 0. Pre-freeze disclosure (everything touched before this freeze)

Only committed material was used to design this protocol:

1. The committed R6Q/R6R/R6M/R6O/R6N receipts and runners were read. The committed
   R6R receipt's pinned-tree candidate listing (paths, blobs, n_qubits — metadata
   only, no coefficients) was used to design the Track-A rule.
2. Runtime calibration on COMMITTED subjects only: `r6f._frozen_batch` was replayed
   once on the committed equilibrium-N2 subject (614 terms, 66 s), and the committed
   R6R/R6Q runtime logs were read.
3. One hand-built synthetic timing instance was run through ALL machinery including
   the DP referee, pre-freeze, purely to measure n=14 runtime:
   `A=((1,0),(1,0)), B=((8,0),(8,0)), C=(((96,0)),((96,96)))` at n=14
   (gave C_R6L=11, C_Dplus=10, f_B=10, C_DP=10). This instance is NOT a subject of
   this lane; every Track-B instance uses n <= 5, so no collision is possible; the
   runner nevertheless hard-asserts that no staged instance equals it.
4. A pre-freeze census of the COMMITTED structured-n2 domain (the 9261-instance
   panel whose exact ground truth is fully bound in the committed R6O/R6Q receipts,
   predicate error zero) was computed with the closed-form family minima only (no DP
   call): exactly 231 of the 9261 instances have all six targets pairwise commuting,
   and ALL 231 are donor-exact by the family minima (hence by committed ground
   truth). Structural consequence recorded a priori: within weight-one-pair batches
   at two qubits, pairwise commutation excludes both trade regimes; engineered
   commuting trade instances therefore need weight-2 block structure. The Track-B
   families below were designed from this observation plus HAND-derived closed-form
   costs (Section 4); the predicate/family minima were NOT evaluated by code on any
   instance of the Track-B families (any n, any letters) before this freeze.

## 1. Scientific question (the R6R escalation)

The committed R6R capstone confirmed the R6Q predicate P1 and the two-trade
completeness identity C_DP == min(C_R6L, C_Dplus, f_B) prospectively on a fresh
chemistry subject — but every one of its 15 matchings was predicted AND confirmed
donor-exact, so the split and borrow branches of the predicate were exercised only
as exclusions. QG-3 escalates to POSITIVE trade-regime forecasts: predict, before
any DP call, that specific instances sit in the split regime (C_DP == C_Dplus <
C_R6L) or the borrow regime (C_DP < C_Dplus), with the exact DP cost, and only then
let the unrestricted committed R6M DP referee decide. A confirmed positive forecast
extends the predicate's verified domain into the trade regimes prospectively; a
refutation localizes the predicate's boundary and is a first-class discovery.

## 2. Frozen machinery (all imported unmodified from research/extensions/orion-q)

- Ground truth referee: `r6m.exact_r6m_matching` (unrestricted frozen R6M DP with
  self-verifying witness).
- Family minima: `r6m.donor_r6l_matching` (C_R6L), `r6o.dplus_pairs` (C_Dplus),
  `r6q.borrow_family_min` (f_B; None -> INF sentinel 10^9).
- Predicate: committed R6Q P1(t) := [C_R6L == C_Dplus] AND [f_B >= C_R6L], verbatim.
- Predicted cost: predicted_C_DP := min(C_R6L, C_Dplus, f_B); predicted regime :=
  donor_exact if predicted_C_DP == C_R6L, else split if predicted_C_DP == C_Dplus,
  else borrow (identical tie-break to the committed R6R lane; truth regime uses the
  same rule on C_DP).
- Features `r6q.simple_features` recorded per row for diagnosis.
- Library machinery: the committed R6R runner's `pinned_tree_listing`,
  `eligible_candidates`, `try_admit`, and `stage1_predict` are imported and reused
  verbatim (module import only; its `main()` is never called).
- F3-table binding: `r6q.F3` must equal `r6m._F3` exactly (hard assert).

## 3. Track A — frozen library-scan rule (real Hamiltonian batches)

Library: npbauman/DUCC-Hamiltonian-Library at pinned commit
`be306f5830549304176365750d712093950bbdde` (the commit every committed chemistry
receipt pins), enumerated by blob-filtered clone + `git ls-tree -r` exactly as the
committed R6R lane (cache directory outside the repository, reusable between runs,
honoring `ORIONQ_R6R_CACHE`).

Eligibility: identical to the committed R6R rule (path ends `.ducc.results.txt`;
has a `/DUCC2/` or `/DUCC3/` segment; top-level molecule NOT in {H2, H2O, H4, LiH,
N2}; an explicit `^(FrozenCoreCCSD_)?(\d+)Elec_(\d+)Orbs$` segment with even
electron count 2k, 1 <= k < m), MINUS every batch already in a committed receipt:
any candidate whose git blob is in the committed-subject blob set
{b98792b1055dbac0ebf2a7576f72412e3e4ac6c5 (H4),
 15369e8e886efbb3d32f3b2dfe2cfbb96ddebeba (equilibrium N2),
 5f157e7bd05aac26b30b10dcea44b7650b7f8648 (H2O),
 5c02c72b88e12b391ea1d8f77eb6b3e04fc2a915 (Benzene DUCC2 cc-pVDZ 6E6O — the
 committed R6R subject)} is excluded.

Order: (n_qubits ascending, path ascending, bytewise) — the committed R6R
compute-honest order. Scan cap: the FIRST 6 eligible candidates (a priori estimate:
two 12-qubit and four 14-qubit Benzene active spaces). Term budget: after the
blob-verified fetch + frozen parse (`r6f._load_terms_verified`), a candidate whose
term list exceeds 1200 terms is recorded verbatim as SKIPPED_TERM_BUDGET and its
window replay is not run (deterministic, content-derived; protects the 25-minute
budget). Admission: otherwise exactly the committed R6R `try_admit` (blob equality,
frozen R6B six-term batch with >= 2 improving window champions from distinct
windows, six unique indices, pairwise-commuting six targets); failures recorded
verbatim, scan continues to the cap (no early stop: EVERY candidate up to the cap
is attempted, so the census is complete over the scanned prefix).

For every ADMITTED batch: stage predictions for ALL 15 canonical matchings via the
committed R6R `stage1_predict` (family minima + predicate only; provably no DP
call). If any real matching is predicted split or borrow, Track A becomes a
positive prospective test on real chemistry; if every scanned real matching is
predicted donor-exact, that census (batches scanned / skipped / failed, all
donor-exact) is itself the structural finding and is reported as such.

## 4. Track B — frozen engineered synthetic generator (seed 20260824)

Deterministic generator `numpy.random.default_rng(20260824)`, single stream, draw
index i = 0, 1, 2, ...; sub-family cycles with i mod 3: F1, F2, F3. All Pauli keys
are (x, z) bit-mask pairs; letter l at qubit q is `r6o._letter_key(l, q)`; products
via `p10.mul`. `distinct_pair(rng)`: perm = rng.permutation(3); return
(int(perm[0])+1, int(perm[1])+1). Every instance is three ordered target pairs
(blocks) evaluated at the canonical matching ((0,1),(2,3),(4,5)) over
`r6m._synthetic_terms`; all six targets must be pairwise commuting (hard assert).

- F1 (borrow-engineered), n = 3 when (i div 3) is even else 4:
  qperm = rng.permutation(n); q0, qh, qk = qperm[0..2]; u = rng.integers(1,4);
  (p1, r1) = distinct_pair; (p2, r2) = distinct_pair;
  heavy block C = (p1@qh * p2@qk, r1@qh * r2@qk); two tag blocks = (u@q0, u@q0);
  slot = rng.integers(0,3) places the heavy block; tag blocks fill the rest.
  Hand-derived a priori (Section 0.4 disclosure; letter/qubit-permutation
  invariance): C_R6L = 8, C_Dplus = 8, f_B = 7 -> predicted borrow, predicted
  C_DP = 7, for every F1 instance.
- F2 (split-engineered), n = 5:
  qperm = rng.permutation(5); q0 = qperm[0]; (a,b) = qperm[1..2]; (c,d) =
  qperm[3..4]; u = rng.integers(1,4); heavy1 = (p1@a * p2@b, r1@a * r2@b) and
  heavy2 = (s1@c * s2@d, t1@c * t2@d) with two distinct_pair draws each (order:
  (p1,r1), (p2,r2), (s1,t1), (s2,t2)); light block = (u@q0, u@q0); slotperm =
  rng.permutation(3) assigns [light, heavy1, heavy2] to block slots.
  Hand-derived a priori: C_R6L = 13, C_Dplus = 11, f_B = 11 -> predicted split,
  predicted C_DP = 11, for every F2 instance.
- F3 (random commuting, unbiased coverage), n = 3: six targets drawn in order; per
  target up to 200 attempts of x = rng.integers(0,8), z = rng.integers(0,8),
  accepting the first with (x,z) != (0,0), weight <= 2, and symplectic product 0
  with every previously accepted target of the instance; if any target exhausts its
  200 attempts the draw yields no instance and the stream continues.

Frozen selection (BEFORE any predicate value of any generated instance is seen —
the rule is fixed here): stream draws are processed in order; each completed
instance's staged prediction is computed; the instance is INCLUDED in the staged
set iff the quota for its predicted regime is not yet full — quotas: split 4,
borrow 4, donor_exact 4 (staged cap 12). The stream stops when all three quotas
are full or at draw cap 400. Excluded instances are counted per predicted regime
(census) but not staged, not refereed. Gate (hard): staged total >= 10 with >= 3
predicted-split and >= 3 predicted-borrow; if unmet at the cap, the run reports
outcome TRACKB_QUOTA_UNMET honestly (predictions still refereed).

Freshness: no Track-B instance may equal the Section-0.3 timing instance (hard
assert) nor any instance with recorded targets in the committed R6O receipt's
verbatim violation lists (hard assert).

## 5. Frozen staged procedure (prediction BEFORE computation)

Stage 1: compute ALL Track-A staged rows (every admitted real batch, all 15
matchings) and ALL Track-B staged rows (each staged instance, canonical matching):
C_R6L, C_Dplus, f_B, predicate P1, predicted_C_DP, predicted_regime, features. No
`exact_r6m_matching` call happens before stage-1 output. Print to stdout, then
flush:
- `ORIONQ_QG3_STAGE1_PREDICTION=<canonical sorted JSON of the full stage-1 block>`
- `ORIONQ_QG3_STAGE1_DIGEST=<sha256 of that canonical JSON>`
The referee refuses to run unless the stage-1 receipt has been emitted (module
flag asserted inside every referee loop — staging enforced in code).

Stage 2 (ground truth): for every staged row run the unrestricted frozen R6M DP
referee `r6m.exact_r6m_matching` (self-verifying witness; raises on any internal
check failure), record C_DP, truth_regime, cost_match, regime_match; hard
assertions per row: sandwich C_DP <= C_Dplus <= C_R6L, borrow soundness C_DP <=
f_B, witness checks all true. D++ containment pinch exactly as the committed
R6P/R6R lanes: C_Dxx recorded equal to C_DP when C_DP == C_Dplus, null otherwise
(informational, never a verdict gate).

## 6. Frozen verdict space

Precedence order:
1. POSITIVE_REGIME_PREDICTIONS_REFUTED: at least one staged row (either track)
   mismatches in regime or exact cost. Every mismatching row is reported verbatim
   (targets, predicted vs truth costs and regimes, features) — it localizes a
   predicate/completeness failure and is a discovery-grade result.
2. TRACKB_QUOTA_UNMET: no mismatch, but the Section-4 quota gate failed at the
   draw cap. All comparisons still reported.
3. POSITIVE_REGIME_PREDICTIONS_CONFIRMED: every staged row matches (n/n reported),
   quota gate met. The Track-A finding is reported alongside as one of
   REAL_TRADE_REGIME_BATCH_FOUND / LIBRARY_SCAN_ALL_DONOR_EXACT /
   NO_ADMITTED_REAL_BATCH; when it is not REAL_TRADE_REGIME_BATCH_FOUND, the
   positive trade-regime confirmation claim is explicitly synthetic-only and the
   claim boundary states it.

## 7. Integrity gates (hard assertions, recorded in the receipt)

- Protocol frozen first; this file's SHA-256 recorded.
- F3-table binding `r6q.F3 == r6m._F3` exact.
- Pinned provenance: commit be306f58...; every fetched candidate blob-verified;
  the ducc listing digest recorded; no fetched path has a top-level molecule in
  the excluded set; the protected stretched-N2 path is never fetched (asserted
  false in the receipt).
- All Track-A candidate blobs outside the committed-subject blob set.
- Six-target pairwise commutation for every admitted real batch (R6R admission)
  and every Track-B instance.
- Staging: stage-1 digest printed before any DP call (enforced in code).
- Sandwich + borrow soundness + DP witness checks on every refereed row.
- Track-B freshness asserts (Section 4).
- Deterministic double run: byte-identical stdout receipt lines and RESULTS JSON
  (runtime on stderr only); single run under 25 minutes with the session venv.
- Authority string contains NOT_R6; donor_novelty_credit = novelty_credit =
  r6_authority = false; no committed file modified; only the three declared QG-3
  files are added.

## 8. Outputs

- stdout: the two stage-1 lines, then
  `ORIONQ_QG3_BOUNDARY_PROSPECTIVE=<canonical sorted JSON receipt>`.
- research/extensions/orion-qg/QG3_BOUNDARY_PROSPECTIVE_RESULTS.json (pretty,
  sorted keys) — written from the real run.
- Runner: research/extensions/orion-qg/qg3_boundary_prospective.py. Exit 0 on
  every honest terminal (CONFIRMED / REFUTED / QUOTA_UNMET).

## 9. Claim boundary (frozen)

A confirmation claims ONLY: the committed R6Q predicate P1 and the two-trade
completeness identity, evaluated by the frozen structural family minima, correctly
predicted the unrestricted frozen-grammar R6M DP optimum — including strictly
positive split- and borrow-regime membership and the exact DP cost — on the staged
rows of this run (the scanned real-library matchings and the staged engineered
synthetic instances), before any of those optima were computed. If the library
scan finds no trade-regime real batch, the positive-regime claim is synthetic-only
and the library census (all scanned real matchings donor-exact) is the Track-A
finding. It is not a theorem for all n or all targets, grants no R6 authority and
no novelty or donor credit, and says nothing about other grammars, objectives, or
batches. A refutation claims exactly the mismatches it reports.
