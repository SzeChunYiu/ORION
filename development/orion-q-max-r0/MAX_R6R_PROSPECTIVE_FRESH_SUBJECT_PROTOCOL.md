# MAX-R6R Prospective Fresh-Subject Prediction Protocol (frozen before any fresh coefficient is read)

Status: FROZEN 2026-08-21, BEFORE any coefficient of any non-committed DUCC
library file was fetched, parsed, or read, and BEFORE any DP, donor-family, or
predicate value was computed on any fresh subject.
Author lane: ORION-Q max-r0 harness drive (branch claude/orion-harness-verification-b17qdj).
Not R6. No novelty credit. The protected stretched-N2 discriminator is never read.

Pre-freeze disclosure: to design the deterministic selection rule, ONLY the git
tree metadata of the public library at the pinned commit was inspected (file
paths and git blob ids via a blob-filtered clone; `git ls-tree -r`). No
`*.ducc.results.txt` content of any path outside the already-committed subject
set was fetched or read before this freeze. Path/blob metadata contains no
Hamiltonian coefficient.

## 1. Scientific question

R6Q induced an exact regime-membership predicate

    P(t) := [C_R6L(t) == C_Dplus(t)] AND [f_B(t) >= C_R6L(t)]

(committed receipt MAX_R6Q_REGIME_PREDICATE_RESULTS.json, selected candidate
P1) with zero classification error on every verified finite domain: the
9261-instance structured-n2 training panel, two 240-instance seeded random
panels (n = 2..3), and all 30 recorded chemistry matchings (H4, equilibrium
N2). On every one of those instances the sharper two-trade completeness
identity C_DP == min(C_R6L, C_Dplus, f_B) also held.

R6R is the capstone prospective test — prediction before computation, the
framework's strongest evidence form: on a molecule/geometry NEVER seen by any
committed ORION-Q receipt, stage 1 evaluates the predicate and records the
predicted regime and predicted DP cost for all 15 matchings of the frozen
six-term batch, prints them with a digest, and ONLY THEN does stage 2 run the
unrestricted R6M DP referee. Either outcome is a first-class result: a
confirmation extends the predicate's verified domain to prospectively unseen
chemistry; a refutation localizes exactly where its verified domain ends.

## 2. Frozen fresh-subject selection rule

Library: the public GitHub repository npbauman/DUCC-Hamiltonian-Library at the
pinned commit be306f5830549304176365750d712093950bbdde (the same commit every
committed ORION-Q chemistry receipt pins). The run enumerates the tree at that
commit via a blob-filtered git clone and `git ls-tree -r` (paths + git blob
ids; the listing's SHA-256 is recorded in the receipt).

Exclusion list (molecules appearing in any committed ORION-Q receipt, verified
by grepping the committed receipts and scripts before this freeze):
- H4 (H4/cc-pVDZ/2.0au/DUCC3/..., blob b98792b1...),
- N2 (cc-pVTZ 6Elec_6Orbs equilibrium DUCC2, blob 15369e8e...; and the
  PROTECTED stretched geometry 1.5_Eq-3.1020au, which is never read),
- H2O (H2O/Eq/..., blob 5f157e7b...),
- LiH and H2 (used via SNIPRS/hamiltonian notebook receipts R4B/R4C).
Frozen excluded top-level molecule directories: {H2, H2O, H4, LiH, N2}.

Eligibility of a tree entry (path string tests only):
1. path ends with `.ducc.results.txt`;
2. path contains a `/DUCC2/` or `/DUCC3/` segment (post-DUCC transformed
   Hamiltonians, the same family as every committed chemistry subject; `Bare`
   and unlabeled lanes are out of scope);
3. the top-level directory is NOT in the excluded molecule set;
4. some path segment matches `^(FrozenCoreCCSD_)?(\d+)Elec_(\d+)Orbs$` with an
   even electron count 2k and orbital count m satisfying 1 <= k < m. The
   frozen active-space config is then n_occ = k, n_orb = m, n_virt = m - k,
   n_qubits = 2m — exactly the convention of the committed N2 subject
   (6Elec_6Orbs -> n_occ 3, n_virt 3, n_qubits 12). Entries without an
   explicit machine-readable active space are ineligible (the frozen parser
   cannot be configured for them without human judgment).

Candidate order (frozen, deterministic): eligible entries sorted by
(n_qubits ascending, path ascending, bytewise). Rationale, recorded a priori:
the frozen referee stack (R6B window-champion replay, R6M exact DP, R6L/D+
family minima, R6Q borrow family) has committed chemistry precedent at
n_qubits <= 12 and a 25-minute runtime budget; smallest-first is the only
compute-honest deterministic order. Alphabetical-first-overall would select a
20-qubit/10-orbital subject whose P10 window replay alone is not budgetable.

Subject admission (the same six-term batch-construction rules used by R6B and
enforced by the committed R6M chemistry lane, applied in candidate order to at
most the first 6 candidates):
1. blob-verified fetch of the pinned raw file (git blob SHA-1 must equal the
   ls-tree blob id — the frozen r6f._frozen_batch machinery's own check);
2. frozen parse + Jordan-Wigner (r4d machinery via p10/r6f, unmodified),
   identity term dropped, terms sorted by (-|coeff|, x, z);
3. R6B window-champion replay (r6b.window_champions, unmodified): at least 2
   improving window champions; the frozen batch is the first two champions;
   six unique source indices; champions from distinct windows (these are
   r6f._frozen_batch's own assertions);
4. the six batch targets are pairwise commuting (the committed R6M chemistry
   lane's hard assertion).
The first candidate passing all four is THE fresh subject. A candidate failing
any check is recorded verbatim (path, blob, reason) and the next is tried. If
none of the first 6 eligible candidates passes, the run terminates with the
honest outcome FRESH_SUBJECT_UNAVAILABLE — the rule is not weakened post hoc.

## 3. Frozen batch, families, and predicate (all machinery imported unmodified)

- Matchings: the 15 canonical unordered perfect matchings of the six batch
  indices (r6m.perfect_matchings).
- C_R6L: r6m.donor_r6l_matching on the fetched terms (weight-one donor family).
- C_Dplus: r6o.dplus_pairs on the matched target pairs (anchor-split family).
- f_B: r6q.borrow_family_min (frozen R6Q borrow family; None -> INF sentinel
  10^9, exactly as R6Q).
- Predicate: P := (C_Dplus == C_R6L) AND (f_B >= C_R6L) — the committed R6Q
  selected predicate P1, evaluated verbatim.
- Features s1,s2,s3,a3,a2max: r6q.simple_features (recorded for diagnosis).

## 4. Frozen staged prediction procedure (prediction BEFORE computation)

Stage 1 (no DP call on the subject happens before stage 1 output is printed):
for each of the 15 matchings compute C_R6L, C_Dplus, f_B and record
- predicted_C_DP := min(C_R6L, C_Dplus, f_B)   [two-trade completeness]
- predicted_donor_exact := P  (equivalently predicted_C_DP == C_R6L; the
  equivalence is asserted per matching)
- predicted_regime := "donor_exact" if predicted_C_DP == C_R6L else
  ("split" if predicted_C_DP == C_Dplus else "borrow").
Print to stdout, then flush, BEFORE any ground-truth computation:
- ORIONQ_MAX_R6R_STAGE1_PREDICTION=<canonical sorted JSON of the stage-1 block>
- ORIONQ_MAX_R6R_STAGE1_DIGEST=<sha256 of that canonical JSON>
The code enforces staging: the referee refuses to run unless the stage-1
receipt has been emitted (module flag asserted inside the stage-2 loop).

Stage 2 (ground truth, only after stage 1 is printed): for each matching run
the unrestricted frozen R6M DP referee r6m.exact_r6m_matching (which
internally verifies its own witness and raises on any check failure) giving
C_DP, and record
- truth_donor_exact := (C_DP == C_R6L); truth_regime := "donor_exact" /
  "split" (C_DP == C_Dplus < C_R6L) / "borrow" (C_DP < C_Dplus);
- hard assertions per matching: sandwich C_DP <= C_Dplus <= C_R6L; borrow
  soundness C_DP <= f_B; witness checks all true;
- D++ containment pinch exactly as the committed R6P chemistry lane: the
  direct D++ sweep is infeasible at chemistry n, so C_Dxx is recorded as
  pinched equal to C_DP when C_DP == C_Dplus (then C_DP <= C_Dxx <= C_Dplus
  forces equality) and as unpinched (null) otherwise; the pinch is
  informational, not a verdict gate.

## 5. Frozen verdict space

- PREDICTION_CONFIRMED: for ALL 15 matchings, predicted_regime ==
  truth_regime AND predicted_C_DP == C_DP (exact), and every integrity gate
  holds. (Regime match is implied by cost match; both are still recorded.)
- PREDICTION_REFUTED: at least one matching mismatches (regime or exact cost).
  Every mismatching matching is reported verbatim (matching, predicted vs
  truth costs and regimes, features) — this localizes the boundary of the
  predicate's verified domain. Integrity gates must still hold; a refutation
  is a first-class result, not a failure of the run.
- FRESH_SUBJECT_UNAVAILABLE: the Section-2 admission loop exhausted its 6
  candidates without an admissible subject; candidate failures are reported
  verbatim. No prediction, no DP.

## 6. Integrity gates (hard assertions, recorded in the receipt)

- Protocol frozen first: the receipt records this file's SHA-256.
- Pinned provenance: commit == be306f58...; the selected subject's observed
  git blob SHA-1 equals the ls-tree blob id (r6f machinery assertion) and the
  full eligible-tree listing digest is recorded.
- Fresh subject truly fresh: its top-level molecule directory is outside the
  frozen exclusion set; its blob equals none of the committed subject blobs.
- Reserved stretched-N2 never read: the N2 molecule directory is excluded
  from candidacy entirely, and the run fetches no path other than evaluated
  candidates' paths (all recorded); asserted false in the receipt.
- Staging: stage-1 digest printed before any exact_r6m_matching call on the
  subject (enforced in code, gate recorded).
- Sandwich + borrow soundness + DP witness checks on every matching.
- F3-table binding of the imported R6Q module against r6m._F3 (as in R6Q).
- No committed file modified; only the three declared new files are added.
- Authority string contains NOT_R6; no novelty/donor credit; deterministic
  double run: byte-identical RESULTS JSON and stdout receipt lines across two
  runs (runtime is reported on stderr only and is the sole run-varying output;
  a clone/cache directory outside the repository may be reused between runs).

## 7. Runtime and outputs

Single run under 25 minutes with the session venv python; exit 0 on every
honest terminal (CONFIRMED / REFUTED / UNAVAILABLE).
Outputs:
- stdout: the two stage-1 lines above, then
  ORIONQ_MAX_R6R_PROSPECTIVE_FRESH_SUBJECT=<canonical sorted JSON receipt>.
- research/extensions/orion-q/MAX_R6R_PROSPECTIVE_FRESH_SUBJECT_RESULTS.json
  (pretty, sorted keys) — written from the real run.
- No existing file is modified; the only additions are this protocol, the
  runner max_r6r_prospective_fresh_subject.py, and the RESULTS json.

## 8. Claim boundary (frozen)

A confirmation claims ONLY: the committed R6Q predicate and the two-trade
completeness identity, evaluated by the frozen structural family minima,
correctly predicted the unrestricted frozen-grammar DP optimum on all 15
matchings of the frozen six-term batch of one prospectively selected, never
previously read chemistry subject, before that optimum was computed. It is not
a theorem for all n or all targets, grants no R6 authority and no novelty or
donor credit, and says nothing about other grammars, objectives, or batches.
A refutation claims exactly the mismatches it reports.
