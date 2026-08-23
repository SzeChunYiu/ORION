# P14A Controlled Sufficiency-Debt Protocol V1

Status: **FROZEN BEFORE OUTCOME**  
Date: 2026-08-20  
Parent atom: `F0.P14`

## Question

Can nested representations be equally sufficient for a lower responsibility while having sharply different value for a later responsibility, and can that lost responsibility be recovered only by reopening a richer state?

The logical fact that prediction/control/intervention/repair can require different state is prior-owned by decision theory, causal/RL abstraction, predictive-state and debugging literatures. This experiment is a controlled benchmark object for ORION's later cross-domain sufficiency-debt claim.

## Latent world

Independent balanced signs `x,m,r in {-1,+1}`.

Responsibilities:

1. `PREDICT`: output `y0 = x`.
2. `DECIDE`: choose current action `a0 = x`.
3. `INTERVENE`: after a blinded intervention flag, output `y1 = x*m`.
4. `VERIFY`: verify a proposed interventional outcome using `x,m`.
5. `REPAIR`: conditional on a verified failure, choose repair owner `r`.

Representations:

- `Z1 = (x)`;
- `Z2 = (x,m)`;
- `Z3 = (x,m,r)`.

The hierarchy is nested and deterministic. No representation contains a protected answer field; responsibilities are computed by an external evaluator.

## Exact predictions

- all Z1/Z2/Z3 are exactly sufficient for PREDICT and DECIDE;
- Z1 is insufficient for INTERVENE/VERIFY because `m` remains balanced conditional on Z1;
- Z2/Z3 are exact for INTERVENE/VERIFY;
- Z2 is insufficient for REPAIR because `r` remains balanced conditional on Z2;
- Z3 is exact for REPAIR.

## Execution

Enumerate the full 8-state latent support exactly; also execute 100 fresh finite samples of n=1024 as a sampling sanity check with seed family rooted at `914421`.

Report Bayes-optimal accuracy for each representation x responsibility and the **sufficiency debt** when a lower-rung-minimal representation is reused one or more rungs upward.

## Positive terminal

`P14_CONTROLLED_SUFFICIENCY_DEBT_LADDER_SUPPORTED` only if:

- full enumeration matches every exact prediction above;
- Z1/Z2/Z3 all score 1.0 on PREDICT and DECIDE;
- Z1 scores exactly 0.5 Bayes accuracy on INTERVENE and VERIFY;
- Z2/Z3 score 1.0 on INTERVENE and VERIFY;
- Z2 scores exactly 0.5 on REPAIR;
- Z3 scores 1.0 on REPAIR;
- finite-sample sanity deviations are within 0.05 of the exact Bayes values;
- no representation contains a responsibility label field.

## Boundary

A positive result is an exact **controlled ladder construction**, not a novel theorem about sufficiency and not evidence that real LLM or Lean states exhibit the same ladder. P14's larger claim still requires materially different real-system domains.
