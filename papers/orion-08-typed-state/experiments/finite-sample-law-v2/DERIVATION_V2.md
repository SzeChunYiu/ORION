# ORION-08 — distributional finite-sample law (derivation V2)

**Successor to** `finite-sample-law-v1` (terminal `LAW_FAILS_RETRO`, documented
in its `FINDINGS_V1.md`). Registration discipline: this file and
`PROTOCOL_V2.md` are committed before any V2 outcome is produced.

## Why V2 (failure attribution, one sentence)

V1 extracted only the posterior-predictive **mean** (Δ̂) and tested its sign;
the refutation (credit-g: mean +0.0115 prior-robust, observed −0.010) lives in
the predictive **variance**, which V1 never used. The predictive model already
contains the full distribution of the held-out Δ; V2 registers exactly that
functional.

## The generative predictive model

Same setting as V1 (frozen utility, binning, split, seed; see
`finite-sample-law-v1/DERIVATION_V1.md`). Fix the **common refinement**
partition S (the typed refined partition; every arm's utility is measurable
with respect to it — the coarse and infogain actions are constant on S-fibres
by construction, since their partitions are coarsenings or side-refinements on
the same binned columns).

For each refined fibre s with train count (n_s, k_s) and train mass
q̂_s = n_s/n:

1. p_s ~ Beta(k_s + 1, n_s − k_s + 1)   (uniform prior; Jeffreys sensitivity
   Beta(k_s + ½, n_s − k_s + ½) registered alongside),
2. test-half occupancy N_s ~ Multinomial(n_te, q̂),
3. test positives K_s ~ Binomial(N_s, p_s).

The held-out utility of any fibre-measurable policy a(·) is
Û_te(a) = (1/n) Σ_s a(s)·(2K_s − N_s). Drawing **one** (p, N, K) realization
and evaluating all arms on it preserves the arms' correlation structure (they
share rows). Δ_typed, Δ_infogain, and the arm-winner are functionals of the
same draw. 10,000 draws per dataset (seeded, fixed in the protocol; MC error
reported).

This is the posterior predictive of the plug-in policy under exchangeability
within fibres and iid row sampling — the same assumptions V1's mean used, with
nothing added. No parameter is fitted.

## The registered quantities

Per dataset:

- **P(Δ_typed < 0)** — the law's headline: the probability that the typed
  refinement hurts out of sample.
- **σ̂** — MC standard deviation of Δ_typed; **confident set** = datasets with
  |Δ̂| > 2σ̂.
- **80% central predictive interval** of Δ_typed.
- **P(typed beats infogain)** (joint, shared draws) — reported, not gated.

## Defects4J (general threshold)

Same construction with run/skip utility: per-fibre contribution
a·(b·K/N-scaled form), a = run iff MLE p > c/(b+c) (b=2.0, c=0.05 frozen in
the V1 D4J runner). All quantities identical in form.

## Falsifiers

- G1: any confident-set dataset (|Δ̂| > 2σ̂) whose observed sign disagrees.
- G2: predictive 80% intervals failing their binomial coverage test at the
  17-dataset level (exact two-sided binomial test, α = 0.05).
- G3 (D4J, conditional on data): Cli not in the top 2 of P(fail), or Gson at
  or above the cohort median.
- G4: a predicted-zero dataset whose observed Δ = 0 falls outside its
  predictive interval.

## What V2 may not do

Rescue V1's refuted claim. The mean-sign law stays refuted regardless of V2's
outcome; V2's claim, if it passes, is a different one — *the predictive
distribution of out-of-sample refinement value, computed from the train fibre
table alone*. A V2 pass earns that sentence in an additive successor ledger;
nothing edits the frozen Tier-B surfaces or V1's verdict.
