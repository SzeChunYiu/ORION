# P11 low-width sparse-decoder gap revival receipt V1 (NR-07)

**Lane:** NR-07 of `research/paper-programme-v1/NEGATIVE_REVIVAL_BACKLOG_V1.md`
**Executable:** `papers/paper-11-state-as-computation/run_nr07_low_width_capacity_bound_v1.py`
**Result:** `papers/paper-11-state-as-computation/NR07_LOW_WIDTH_CAPACITY_BOUND_RESULT_V1.json`
(SHA-256 `1882b2fb5938e0e88e1a2a71fcf82bb0d697d0192e271b3ee9e181076bd094de`)
**Replay:** two consecutive full runs byte-identical; all readings replay the
frozen P11H/P11I streams exactly (7 seeds: preflight 2026082201–03, execution
2026082210, replication 2026082241–43).
**Machine form:** `P11_LOW_WIDTH_GAP_REVIVAL_RECEIPT_V1.json` (this directory).

## Negative being revived

P11D's gap gates (universal-vs-compiled threshold ratio ≥ 4×, delta64 ≥ 0.20)
are unmet at `r=3` while P11.I's high-width cells pass at `r≥7`; the pooled
universal attack prevailed at the drawn `r=3` regimes
(`P11H_POOLED_UNIVERSAL_ATTACK_PREVAILED`). The backlog row asked: is the `r=3`
failure decoder capacity, decoder mechanism, or an attack-strength artifact?

## Root cause — one stage: a decoder-CAPACITY (information) limit

Not decoder mechanism and not attack strength:

- **The registered attack is already at the information boundary at `r=3`.** An
  exact hypothesis-free screening decoder — ĉ_j = mean(Y·A_j), top-|ĉ| support,
  sign of the sign-weighted sum — with **zero learned parameters and zero
  hyperparameters** matches or beats the registered L1 universal arm on every
  frozen `r=3` reading. There is no decoder-side mechanism left to upgrade on
  the attack side.
- **The defence cannot be upgraded either.** compiled@64 = 1.0 at every `r=3`
  reading, so the gap is bounded above by what the attack lacks, not by what the
  defence lacks.

**Mechanism.** Distinct parity columns are pairwise independent, so each active
column's first-order correlation with the majority-of-r label is exact and
closed-form — ρ(r) = C(r−1,(r−1)/2)/2^(r−1) (ρ₃ = 0.5, ρ₅ = 0.375,
ρ₇ = 0.3125, ρ₉ ≈ 0.2734) — while inactive columns are exactly 0. Support
recovery is therefore marginal screening whose sample cost grows as 1/ρ(r)²:

- width law (no free parameters): **n\*(r,p) = 2 ln p / ρ(r)²**
- calibrated boundary: n_screen(r,p) = (1+√(2 ln p))²/ρ(r)²

At `r=3`, n\* ∈ [36.1, 62.2] < 64 at every registered bank geometry: the
support is recoverable at the smallest registered train size. At `r=7`,
n\* ∈ [92.4, 159.2] ⊂ (64, 256): the defence window is exactly where P11I
found it.

## Lever

Capacity branch: a pre-registered **width-conditioned claim with the
impossibility argument made precise** — the proven width bound plus a
capacity-augmented attack pool (max of the registered 3 arms and the screening
decoder), which is strictly stronger than P11H's registered pool.

## Re-test results (all 21 `r=3` and all 21 `r=7` frozen readings)

| consequence | value |
|---|---|
| C1: augmented pool reaches 0.95 by n=128, every `r=3` reading | **true** (min augmented@128 = 1.0) |
| C2: `r=7` window survives the capacity-augmented attack | **true** (max below 256 = 0.9421 < 0.95) |
| C3: max attainable delta64 at `r=3` | **0.1741 < 0.20** (gate unattainable) |
| C3: max attainable threshold ratio at `r=3` | **≤ 2 < 4** (gate unattainable) |
| P2: law retrodicts the full P11H 15-rung candidate table | **held** (incl. rejected rows: `r=5` knife-edge n\* ∈ [64.2, 110.6] → "unstable") |
| P3: ρ closed form validated on frozen test sets | **held** (active within 0.004; inactive ≤ 0.022) |
| P1 as pre-registered (screen@64 ≥ 0.95 at every `r=3` rung) | **failed** (range 0.7255–1.0) — disclosed below |

**Disclosed correction.** The first draft of the certificate wrongly used the
range-1 Hoeffding form 2exp(−2nt²); for ±1-valued (range-2) statistics the
correct union bound is n_cert = (8/ρ²)ln(2p/δ) (~338 at p=969, r=3) — a loose
sufficient bound only. The load-bearing boundary is the calibrated n_screen law
plus exact empirical replay, not the certificate. The pre-registered P1 also
missed (screen@64 ≥ 0.95 predicted; observed floor 0.7255): reported as a miss,
the boundary statement corrected to (64, 128], nothing tuned.

## Before / after

- **Before:** `r=3` adverse terminal read as a bare negative (gap unmet, attack
  prevailed) with the failure stage unattributed.
- **After:** the `r=3` negative is a theorem-shaped capacity fact — both gap
  gates are unattainable at `r=3` against the strongest constructible universal
  pool; the width law explains the entire P11H ladder with no free parameters;
  and the `r=7` positive window is re-verified against a strictly stronger
  attack. No frozen byte is edited: P11H/P11I/P11D protocols, receipts and
  results stand; this receipt reclassifies the *interpretation* of the adverse
  terminal without moving any published number.

## Boundary

- Construction-synthetic only (majority-of-r on complete parity banks); bars
  0.95/0.20/4× and train grid {64,128,256} carried over unedited. No universal
  nonlinear lower bound, no real-agent claim.
- `r=5` is deliberately left open (the law predicts a knife-edge consistent
  with P11H's "unstable" rejections; a dedicated study would need its own
  frozen protocol).
- At `r=7` the 256-edge is bank-width-dependent: narrow banks (14,2)/(14,3)
  come within screening capacity by 256 (screen@256 0.9414–1.0) while (19,3)
  sits at 0.9033–1.0 — P11I's "below target before 256" wording remains the
  operative bound.
- NR-12 (query-family compile-tolerance, #996/#1016) is a separate lane; its
  files are untouched here.
