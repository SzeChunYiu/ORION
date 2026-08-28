# ORION-21 NR07 — root cause of `CANNOT_CHECK_INSTRUMENT_DRIFT`

**Protocol identity:** `ORION21.TIE_ROBUST_PHASE.v1`
**Authority:** `DIAGNOSTIC_ONLY` · `scientific_authority_delta = NONE` · submission authority `false`

This document diagnoses an existing adverse terminal. It grants no law, width, mechanism,
superiority, manuscript-freeze or submission authority, and it does not alter the controlling
terminal `CANNOT_CHECK_INSTRUMENT_DRIFT`.

## 1. What failed

Registered instrument precondition P0 (authoritative LUNARC job `3550337`,
`NR07_WIDTH_LAW_FALSIFICATION_RESULT_V1.json`, sha256 `8ef964ec…e44d9e22`):

> exact replay of NR07 recorded readings at cells (14,2,3), (14,3,3), (19,3,3),
> seed 2026082201, n in {64,128,256}, to 1e-12

P0 failed at exactly one point — cell (14,3,3), n=64:

| | value |
|---|---|
| expected | `0.94912109375` = 19438/20480 |
| observed | `0.949169921875` = 19439/20480 |
| delta | `1/20480` = 4.8828125e-05 ≫ 1e-12 |

Cells (14,2,3) and (19,3,3) replayed exactly. The failure is a single localized point.

## 2. Mechanism

From the exact-anchor forensic successor (`ORION21.NR07.EXACT_ANCHOR.v2`, `RESULT.json`):

- Query 0 has a **three-way absolute-correlation tie** for the final support slot —
  features {35, 93, 263}, all at |corr| numerator 24/64.
- Queries 1–4 have `candidate_count = 1`. The equality class is therefore **exactly three
  elements**, and enumeration over it is exhaustive.
- The frozen scoring rule supplies **no deterministic secondary tie key**.

The three tie-consistent aggregate worlds, as exact rationals over 20,480 ordered decisions:

| world | fraction | decimal | selects |
|---|---|---|---|
| 0 | 19438/20480 | 0.94912109375 | feature 35 (historical expected) |
| 1 | 19439/20480 | 0.949169921875 | feature 93 (LUNARC observed) |
| 2 | 19476/20480 | 0.9509765625 | feature 263 |

## 3. Root cause

`CANNOT_CHECK_INSTRUMENT_DRIFT` is **not** caused by nondeterminism, lost data, environment
drift, or an over-tight numerical tolerance. Its root cause is that the frozen measurement
object is **under-specified**: `argsort` over tied scores is implementation-defined, and the
protocol never bound a deterministic secondary key. Two correct implementations legitimately
disagree, and the disagreement is exactly one decision in 20,480.

**Corollary — the quarantined repair used the wrong lever.** Widening the replay tolerance from
1e-12 to 1e-3 (the quarantined `V1_1` move) admits the 4.88e-05 delta and would have reported a
pass. It does not remove the under-specification; it conceals it. The quarantine is therefore
scientifically correct, and no tolerance value can repair this defect.

## 4. Why the under-specification is scientifically load-bearing

The registered primary quantity is (`prereg_criterion.primary_quantity`):

> `n_cross(p)` = smallest ladder train size whose **7-seed mean** screening accuracy reaches 0.95

So `0.95` is a registered threshold that *defines* the primary quantity, and `n_cross` is
determined by a threshold crossing. A support-selection ambiguity therefore does not stay a
rounding nuisance — it propagates through the threshold into the quantity the width law predicts.

`LADDER_TIE_EXPOSURE_V1.json` (produced by `compute_ladder_tie_exposure.py` from the
authoritative bytes) reports, over the whole ladder:

- **479 / 1050 = 45.6 %** of (cell, seed, n) points have a **non-separable support rank gap** —
  i.e. ties are pervasive, not confined to the anchor.
- **10 / 10** ladder cells have their `n_cross` crossing sitting on tied points.
- Three cells cross with a margin below 0.0011 above τ: (14,3,3) at 0.000286, (17,4,3) at
  0.000684, (14,2,3) at 0.001081 — with 43–71 % of seeds tied at the crossing size.

## 5. What is NOT established (explicit boundary)

This diagnostic establishes tie **exposure**. It does **not** establish that `n_cross` is
set-valued, for a specific reason that must not be glossed:

- The ladder readings record only the **realised** support selection, not the equality class, so
  the admissible range of the 7-seed mean is not recoverable from these bytes.
- The anchor replay (`instrument_precondition_p0`) and the ladder sweep (`readings`) are
  **different instruments** and their magnitudes must not be transferred between each other. At
  cell (14,3,3), n=64, seed 2026082201 the anchor replay reads `0.949169921875` while the ladder
  reads `0.8029296875`. Any argument that multiplies the anchor's single-seed tie swing against a
  ladder margin is invalid.

## 6. Discriminating successor hypotheses

- **H_LOCAL** — enumerating the equality class over the ladder leaves every `n_cross` value, and
  hence the C1/C2/C3 verdict, invariant. Tie exposure is incidental.
- **H_SYSTEMIC** — the admissible 7-seed mean straddles τ at one or more cells, `n_cross` is
  set-valued there, and the width-law verdict is not invariant over the admissible set.

These make opposite predictions and are separated by exhaustive equality-class enumeration on the
ladder, with the discriminator frozen before outcomes are read. No tolerance, budget or threshold
is tuned.

## 7. Tie-robustness criterion

Per `ORION21.TIE_ROBUST_PHASE.v1` (PR #1615, Priority 1), a threshold conclusion at input `x` is
tie-robust iff `max_{s∈S(x)} M(s,x) < τ` or `min_{s∈S(x)} M(s,x) ≥ τ`.

At the anchor's own measurement, `min = 0.94912109375 < 0.95 ≤ max = 0.9509765625` — the
admissible set **straddles** τ, so that measurement is **not tie-robust**. Whether the ladder's
`n_cross` values inherit this is exactly what H_LOCAL vs H_SYSTEMIC decides.

## 8. What any successor experiment must bind before reading outcomes

1. A deterministic secondary tie key, as part of the registered scientific object.
2. Raw ordered predictions and labels, retained.
3. An exact integer scorer (no floating-point aggregate).
4. Set-valued support semantics: report `[min, max]` of the primary quantity over `S(x)`.
5. A new protocol identity. The V1 lane remains history and is not reopened.

## Provenance

- Input: `NR07_WIDTH_LAW_FALSIFICATION_RESULT_V1.json`, sha256 verified equal to the
  authoritative `8ef964ecb3c02ab5988ea13ed56678a424e7d5487f64d31c2e66a149e44d9e22`.
- Analysis executed on host `billy-laptop-old`, Python 3.14.4.
- Depends on PR #1604 for the authoritative artifact; this diagnostic must land after it.
