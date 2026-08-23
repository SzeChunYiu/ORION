# QG-7e — single-pinner PP hidden-home closure protocol V1

Date: 2026-08-22
Issue: #872
Parent programme: #740
Direct parent: QG-7d information closure #836 / PR #860
State parent: QG-22 #868 / PR #869
Sibling PA theorem: QG-7d J7 PR #870
Branch: `codex/orion-qg-qg7e-pp-single-pinner-20260822`
Status: **FROZEN BEFORE OFFICIAL QG-7e DUAL-HARNESS OUTCOME.**
Authority ceiling: single non-comm-s2 pinner PP normalization only; chain/global B'' completeness remain OPEN; novelty/R6/physical advantage false.

## 1. Target

Close the QG-7c **PP single-pinner** residual over the complete hidden phantom-home environment.

The parent QG-7c visible quotient has 32,556 PP failures. QG-7d information closure proved that each visible row has an omitted six-letter hidden environment, so the complete theorem domain is

`32,556 * 4^6 = 133,349,376`

full environments.

V1 may use only:
1. the already-earned QG-7c G1-G4 moves;
2. a frozen all-support-one whole-system relocation library;
3. exact D+ (all frame generators support <=1);
4. unchanged committed QG-5b B'.

No B'', B''' or new family may be introduced after outcome.

## 2. Disclosed exploratory fingerprints

This is confirmatory. The official run must reproduce exactly:

- PP visible failures: `32,556`;
- visible failure histogram: `32116 x +1`, `440 x +2`;
- exact per-cell failure counts, in frozen `(ja,R_b,R_a,p)` lexicographic order:
  `4057,3678,4057,3678,3678,4057,3678,4057,217,187,217,187,187,217,187,217`;
- hidden domain: `4096` states in tuple order `(a0,b0,c0,a1,b1,c1)`;
- full product domain: `133,349,376`;
- 576-relocation + parent screen residual: `6,488`, every residual delta `+1`;
- exact D+ template count under canonical label orientation: `61,056`;
- D+ delta histogram on the 6,488 residuals: `{-2:136,-1:3676,0:2652,+1:24}`;
- exact D+ residual count: `24`;
- exact B' delta on those 24: `-1` for every row;
- final residual: `0`.

Two earlier exploratory implementations were rejected before freeze: one used an incorrect hidden-tuple indexing, and one allowed visible/hidden target permutations to differ. Their provisional counts have no authority.

## 3. Exact hidden mapping

Hidden state order is frozen as:

`(a0,b0,c0,a1,b1,c1)`.

At the home coordinate:
- block A targets are `(a0,a1)`;
- block B targets are `(b0,b1)`;
- block C targets are `(c0,c1)`.

The reference PP pinner has local frame letters `Z` on branch 0 and `X` on branch 1 at home. Thus reference hidden F3 is

`F3(a0,b0*Z,c0) + F3(a1,b1*X,c1)`.

Any target permutation tuple is **global** across b, a and home. A factorized calculation may condition on one common `(sigma_A,sigma_B,sigma_C)` but may never minimize each coordinate under different permutations.

## 4. Reference structural cost

For the frozen PP reference shape:
- our comm-s2 block: central support-two frame -> extra 2;
- non-comm-s2 pinner: central support-two frame -> extra 2;
- third block support-one -> extra 0;
- shared Tag support two -> cost 4.

Reference structural cost is exactly `8`.

The complete reference cost for a full environment is therefore

`C_ref = 8 + F3_visible_ref + F3_hidden_ref`.

The production analyzer must verify sampled/reference members through primitive R6S labels/cost, not only use this formula.

## 5. Parent G1-G4 screen

Rebuild QG-7c T4b PP G1-G4 on the complete visible domain from local Pauli/F3 semantics. These moves leave the hidden-home letters unchanged, so their exact delta can be lifted to every hidden environment.

A visible row with parent best `<=0` is already closed for every hidden environment and does not enter the 32,556 residual product.

## 6. Frozen 576 whole-system relocation library

For each full environment, enumerate exactly:

- relocation coordinate `q in {b,a,home}`;
- shared support-one Tag letter `s in {X,Y,Z}` at q;
- for each of three blocks, label-1 frame letter is one of the two letters anticommuting with s;
- one target permutation bit per block, shared globally across all coordinates.

Count: `3 * 3 * 2^3 * 2^3 = 576`.

Every resulting member has support-one frames and Tag weight one, hence structural cost exactly 2.

A factorized implementation is allowed:
- for fixed global sigma, minimize local frame-letter choices at the relocation coordinate;
- add target-only F3 on the other coordinates under that same sigma.

Expected combined parent/relocation residual: exactly 6,488 full environments, all `+1` relative to C_ref.

## 7. Exact full D+ family

On only the 6,488 residuals, enumerate the exact support<=1 family.

For a nonzero Tag string S over the three coordinates:
- a support-one rank-2 block must place both anticommuting frames at one coordinate q with S(q) nonidentity;
- under canonical shared labels `(0,1)`, frame0 local letter is S(q), frame1 is one of the two letters anticommuting with S(q);
- each block independently chooses q, the anticommuting frame1 letter, and target permutation;
- Tag cost is `2*wt(S)`;
- frame-extra cost is zero;
- Restore/F3 is exact over all three coordinates.

The analyzer must either prove/cite the exact label-orientation symmetry reducing to canonical `(0,1)` or explicitly enumerate both orientations. Expected canonical template count: 61,056.

Expected exact D+ delta histogram on the 6,488 rows:
`{-2:136,-1:3676,0:2652,+1:24}`.

A deterministic subset of the 24 positive rows plus at least one row in each nonpositive histogram class must be cross-checked against production `r6p.dxx_search(..., max_weight=1)`.

## 8. Exact B' handoff

On exactly the 24 D+ residuals, evaluate committed QG-5b `bprime_family_min` on the full n=3 target pairs, including home.

For every row:
- production B' value must equal `C_ref-1`;
- selected B' witness must pass `verify_bprime_witness`;
- generic ORION independently computes the same B' minimum from the frozen B' grammar without importing the production helper.

Expected final residual: zero.

## 9. Composition theorem and remaining boundary

A positive terminal proves the PP single-pinner local normalization statement needed by the QG-7c all-n composition argument: every such local environment has a non-increasing rewrite into an already-earned family.

Together with J7 PA closure, all **single non-comm-s2 pinner** cases close.

Still OPEN and explicitly false in every V1 receipt:
- `CHAIN_ALL_N`: two pinning blocks / comm-s2 pinner / mutually pinned comm-s2 chains;
- `GLOBAL_BDOUBLEPRIME_COMPLETENESS`;
- whole QG-7d final all-n identity until chain composition closes.

## 10. Dual harness

Generic ORION independently rebuilds Pauli multiplication/symplectic/F3, PP G1-G4, hidden mapping, 576 relocation, exact D+, and exact B' on the 24 residuals.

Native ORION-Q requires exact analyzer/generic agreement and keeps:
- `PP_SINGLE_PINNER_ALL_N=true` only on positive;
- `CHAIN_ALL_N=false`;
- `GLOBAL_BDOUBLEPRIME_COMPLETENESS=false`;
- novelty/R6/physical advantage false.

Deterministic analyzer replay must be byte-identical.

## 11. Honest terminals

- `QG7E_PP_SINGLE_PINNER_CLOSED_ALL_HIDDEN_ENVIRONMENTS__CHAIN_OPEN`
- `QG7E_RELOCATION_FINGERPRINT_MISMATCH`
- `QG7E_DPLUS_RESIDUAL_MISMATCH`
- `QG7E_BPRIME_HANDOFF_REFUTED__RESIDUAL_REMAINS`
- `QG7E_GENERIC_NATIVE_DISAGREEMENT`
- `QG7E_PARENT_BINDING_GAP`
- `QG7E_CANNOT_CHECK`
