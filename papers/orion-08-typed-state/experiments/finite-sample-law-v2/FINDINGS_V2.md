# ORION-08 distributional law — findings V2

**Terminal: `LAW_V2_PARTIAL_G1_G2`** (exit 1). Registered gates G1 and G2
fail; G4 passes; Jeffreys sensitivity clean; both structural cross-checks
exact. Protocol `PROTOCOL_V2.md` + amendment A1 committed (db7c2c2a6,
f3b050021) before this outcome. Pass 1 (aborted pre-verdict by its own
cross-check — a Beta(k+1, n−k+2) coding error caught at ~50 MC-SE) is retained
as `RESULTS_V2_pass1_aborted.json`; the result of record is the single clean
post-A1 pass.

## Cross-checks (both exact)

- Observed arm utilities reproduce `finite-sample-law-v1/RESULTS_V1.json` at
  max |Δ| = 0.0 (15 arm comparisons, 5 retro datasets).
- MC mean of Δ matches the closed-form mean of the same R-fibre predictive on
  all 16 datasets (max diff 4.0e-04 ≈ MC-SE; 13 prior violations gone).

## Phase R2 (retro 5)

| dataset | mean | sd | P(Δ<0) | confident | obs sign |
|---|---|---|---|---|---|
| credit-g | +0.0111 | 0.0161 | 0.226 | no | − |
| diabetes | +0.0108 | 0.0223 | 0.288 | no | − |
| spambase | +0.0942 | 0.0153 | 0.000 | **yes** | + |
| qsar-biodeg | 0 | 0 | — | — | 0 |
| wdbc | +0.0061 | 0.0171 | 0.320 | no | − |

**V1's refuter is now correctly unconfident.** credit-g (V1's mean-sign
failure, Δ̂=+0.0115) sits at P(Δ<0)=0.226 — the predictive variance that V1
discarded straddles zero exactly where V1 missed. V1's failure attribution
(mean extracted, variance unused) is thereby *confirmed* by V2's own numbers.

## Phase P2 (prospective; registry exhausted at 11)

The pre-registered scan past openml-1480 yields exactly 11 qualifying
datasets (40927 fails fetch and is 10-class regardless; 40996/41027 are
10-class) — pooled cohort 16, per amendment A1.

## Gate outcomes

- **G1 FAILS — one violation: openml-6332.** mean +0.0768, sd 0.0352
  (confident positive, P(Δ<0)=0.013), observed Δ negative (z = −3.76).
  6332 is the cohort's most fragmented table: 25.6% of its test rows fall in
  R-fibres **never occupied in train** — mass the predictive cannot see and
  the observed scoring sends to action 0.
- **G2 FAILS — 8/16 inside the 80% central intervals** (expected 12.8; exact
  two-sided binomial p = 0.007). The predictive is anti-conservative.
- **G4 PASSES — predicted-zero stratum 3/3** (qsar-biodeg, openml-1487,
  openml-40701 all observed exactly 0). Running record across V1+V2:
  **9/9**.
- **Sensitivity: Jeffreys flips no headline sign.**

## Failure attribution (one stage, diagnosed not assumed)

Per-dataset standardized residuals (observed − predictive mean)/σ̂ are **11/13
negative among nonzero-sd datasets** (sign test p = 0.0112); every interval
miss is a miss on the LOW side. Two mechanisms, cleanly separated:

1. **Systematic optimism (all datasets): the winner's curse of fibre-action
   selection.** Each fibre's action is argmax over the *same* train counts the
   posterior conditions on; a conjugate posterior that ignores the selection
   overstates selected value. (k+1)/(n+2) shrinkage corrects sampling noise,
   not selection — hence a one-sided bias the interval width cannot absorb.
2. **Unseen-fibre mass (the extreme offenders):** unseen-R-fibre test mass is
   0.256 (6332), 0.063 (40994), 0.053 (wdbc) — the three largest |z| — but
   ≈0 for 23517/1590/4134, which still miss low. Mechanism 1 is necessary
   for the pattern; mechanism 2 amplifies it where the table is most
   fragmented.

The surviving structure sharpens into one sentence: **a train fibre table
upper-bounds out-of-sample refinement value in expectation; it does not
estimate it.** The zero stratum (no value anywhere) is perfectly predictable
(9/9); any nonzero value is overstated by every naive posterior tested (V1
mean-sign; V2 full conjugate predictive).

## What this licenses

Nothing in the frozen Tier-B package changes; the successor ledger records:
the distributional form of the finite-sample law is REFUTED on 16 pooled CC18
datasets (one confident-set contradiction + significant interval
under-coverage, one-sided low); the zero stratum is 9/9 across both studies;
the attribution (selection-induced optimism + unseen-fibre mass) is measured,
not asserted. A V3, if attempted, must model the selection (e.g. actions
chosen on a disjoint half) — a different law, registered before its outcome;
neither V1 nor V2 is revived by it.

## Phase D2 — Defects4J

`D4J_SKIPPED_DATA_UNAVAILABLE` (host lacks `~/d4j_data.json`). Not checked is
not passed; carried forward unchanged.
