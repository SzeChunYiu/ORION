# ORION-11 Prospective Power / Precision Analysis V1

**Provenance.** This document is bound to protocol `ORION-11.hidden-formulation.v1.1`
(DESIGN_FROZEN, `outcome_accessed: false`). All case counts are derived from the
frozen suite at the hashes below. No outcome data has been inspected.

| Field | Value |
|-------|-------|
| Analysis id | `ORION-11.prospective-power.v1` |
| Status | `FROZEN_ANALYSIS` |
| Suite PILOT | `7a50a2d5025beb7dea4835911fa7dbf4a191431447397c73939c276b71dc49b5` (18 cases) |
| Suite TEST | `21b461d89280631b93b766d6fb000c7f9f5fbeccee7cb6664f238c2c5c8e6420` (48 cases) |
| Total frozen cases | 66 |
| Protocol margin H1 | superiority: at least +0.05 absolute root-success difference |
| Protocol margin H2 | non-inferiority: unnecessary-reframe rate may not worsen by more than +0.02 absolute |
| Confidence | 95% (Wilson score; paired percentile bootstrap, 10000 resamples) |
| Stochastic repeats | 5 per (case, system), reduced to one observation per case before any rate |
| Subject model | `glm-5.2` |

---

## 1. Analysis scope

The final test is the **48-case TEST split** (21b461d8...). The 18-case PILOT
split is held aside for variance estimation, system debugging, and pilot-only
analysis; it may be pooled with TEST only if the power analysis below shows
inadequate precision on TEST alone *and* the pooling is predeclared before
outcome access.

**TEST split composition:**

| Family | Count | Role |
|--------|-------|------|
| hidden_parent_domain | 8 | H1 superiority target |
| hidden_representation_or_coordinate_system | 8 | H1 superiority target |
| hidden_decomposition_or_interface | 8 | H1 superiority target |
| hidden_measurement_or_operationalization | 8 | H1 superiority target |
| evidence_only_negative_control | 8 | H2 non-inferiority guard |
| execution_only_negative_control | 8 | H2 non-inferiority guard |
| **Hidden-shift subtotal** | **32** | H1 analysis |
| **Control subtotal** | **16** | H2 analysis |

**Unit of analysis.** The frozen case, after the 5 stochastic repeats are
reduced to one observation per case (majority for performance, mode-severity for
control outcomes). The Wilson interval `n` is therefore 32 (hidden-shift) or 16
(controls), never 160 or 80.

---

## 2. H1 — superiority at +0.05 margin (32 hidden-shift test cases)

### 2.1 Precision of the matched difference

The paired bootstrap interval width depends on the standard deviation of the
within-case difference between systems. For binary outcomes on 32 cases, the
95% percentile interval half-width is:

| sigma_diff | 95% CI half-width | Interpretable power example |
|------------|-------------------|-----------------------------|
| 0.35 | 0.121 | High-effect study |
| 0.40 | 0.139 | Moderate-effect study |
| 0.45 | 0.156 | Low-effect study |
| 0.50 | 0.173 | Minimal-effect study |

**sigma_diff estimate.** For binary `root_success` with two systems, the
paired-difference standard deviation is:

    sigma_diff = sqrt(p1(1-p1) + p2(1-p2) - 2*rho*sqrt(p1(1-p1)*p2(1-p2)))

where `rho` is the within-case correlation. With `p1 ~ 0.60` (ORION, hypothesised)
and `p2 ~ 0.40` (best baseline), and `rho ~ 0.3` (moderate paired correlation on
same-case outcomes), sigma_diff ≈ 0.42. The conservative range is 0.35–0.50.

### 2.2 Power sensitivity grid

Power to detect that the `lower bound of the 95% CI exceeds +0.05`:

| True effect | sigma=0.35 | sigma=0.40 | sigma=0.45 | sigma=0.50 |
|-------------|------------|------------|------------|------------|
| +0.10 | 0.201 | 0.174 | 0.155 | 0.140 |
| +0.12 | 0.304 | 0.256 | 0.222 | 0.197 |
| +0.15 | 0.489 | 0.409 | 0.349 | 0.304 |
| +0.18 | 0.676 | 0.577 | 0.496 | 0.431 |
| **+0.20** | **0.782** | **0.683** | **0.595** | **0.521** |
| +0.25 | 0.944 | 0.882 | 0.808 | 0.732 |
| +0.30 | 0.992 | 0.971 | 0.933 | 0.882 |

**Operating point.** At the central estimate (sigma_diff=0.42, effect=+0.20)
power is approximately 0.65. At effect=+0.25 power is approximately 0.82.
A modest absolute effect of +0.20 to +0.25 is the minimum the study can
detect with adequate power on 32 hidden-shift test cases.

### 2.3 Decision: 32 TEST cases are adequate for H1

The frozen 32-case hidden-shift TEST set provides:

- **80%+ power** for effects of +0.25 or larger (the plausible range given
  mechanical-system upper bounds of ~0.60 root success and the hypothesised
  ORION advantage from targeted reframing);
- **~60-65% power** for a +0.20 effect, which is acceptable for a first
  evaluation — the negative finding is itself informative, and the study design
  includes 5 stochastic repeats per cell to reduce the variance of the
  per-case estimate.

The 18 PILOT cases are NOT pooled. They are reserved for variance debugging
and pilot-only analysis as declared in the protocol. Pooling would increase
N to 50 hidden-shift cases, but the PILOT cases have been used for mechanical
solvability auditing and pilot debugging, violating the independence required
for a final test.

---

## 3. H2 — non-inferiority at +0.02 margin (16 control test cases)

### 3.1 The +0.02 margin is not certifiable with 16 controls

The non-inferiority test requires the **upper bound** of the bootstrap CI for
the difference `(ORION_unnecessary_reframe_rate - baseline_unnecessary_reframe_rate)`
to lie strictly below +0.02.

Even with **zero unnecessary reframes in both systems** (difference = 0), the
95% CI upper bound at n=16 is:

| sigma_diff | CI upper bound at diff=0 | Certifiable margin |
|------------|------------------------|---------------------|
| 0.15 | 0.074 | +0.074 |
| 0.20 | 0.098 | +0.098 |
| 0.25 | 0.123 | +0.123 |
| 0.30 | 0.147 | +0.147 |

**The +0.02 margin is approximately 5-7x narrower than the narrowest achievable
upper bound.** A non-inferiority test at +0.02 with 16 controls has near-zero
power under any realistic sigma_diff: the CI upper bound cannot shrink below
approximately +0.07 even with perfectly identical systems.

### 3.2 Power to detect non-inferiority at larger margins (n=16)

| Margin | sigma=0.15 | sigma=0.20 | sigma=0.25 |
|--------|-----------|-----------|-----------|
| +0.05 | 0.265 | 0.169 | 0.123 |
| +0.08 | 0.569 | 0.359 | 0.248 |
| +0.10 | 0.760 | 0.516 | 0.359 |
| +0.12 | 0.893 | 0.670 | 0.484 |
| +0.15 | 0.979 | 0.851 | 0.670 |

At margin +0.10 and sigma 0.20 (moderate), power is 0.516 — marginal.
At margin +0.12 and sigma 0.20, power is 0.670 — acceptable for a safety
guard. At margin +0.15, power is 0.851 — adequate.

### 3.3 Decision: H2 at +0.02 is a design target, not a certifiable gate

The +0.02 margin is retained as the **declared design aspiration** in the
protocol. The `assess_hypothesis` procedure in `statistics.py` (lines 463-464)
will correctly return `NOT_SUPPORTED` when the CI upper bound exceeds +0.02,
and the `UNDERPOWERED` verdict (line 472-480) will fire when `min_units` is
declared above the prospective N. The study will report the observed difference
with its CI and let the reader judge whether the non-inferiority claim is
supported.

**Recommendation for future revision:** A non-inferiority margin of +0.10
to +0.12 would be certifiable with 16 controls at adequate power. The
protocol's H2 margin should be revised to +0.10 in a future amendment, or
the control set should be expanded to 30+ cases.

---

## 4. Sensitivity across the effect-size continuum

### 4.1 Wilson interval precision on standalone rates

| n | p | 95% Wilson interval | Half-width |
|---|----|--------------------|------------|
| 32 | 0.50 | [0.336, 0.664] | 0.164 |
| 32 | 0.70 | [0.527, 0.830] | 0.152 |
| 32 | 0.80 | [0.633, 0.903] | 0.135 |
| 32 | 0.85 | [0.690, 0.935] | 0.123 |
| 32 | 0.90 | [0.750, 0.964] | 0.107 |
| 32 | 0.95 | [0.816, 0.988] | 0.086 |
| 16 | 0.00 | [0.000, 0.194] | 0.097 |
| 16 | 0.05 | [0.008, 0.267] | 0.130 |
| 16 | 0.10 | [0.024, 0.331] | 0.153 |
| 16 | 0.20 | [0.073, 0.443] | 0.185 |

On 32 hidden-shift cases, a standalone rate of 0.80 has a Wilson interval
spanning roughly 0.63 to 0.90 — adequate to distinguish ORION from the
mechanical baselines (~0.50–0.60 expected). On 16 controls, the interval
is wide: a 0.05 unnecessary-reframe rate is consistent with anywhere from
0.008 to 0.267.

### 4.2 Can the PILOT split be pooled?

Pooling PILOT + TEST would give 44 hidden-shift cases (48 at n=32, 50 if
pooled to 44). The power gain is modest:

| Effect | sigma=0.45, n=32 | sigma=0.45, n=44 | sigma=0.45, n=48 |
|--------|------------------|------------------|------------------|
| +0.15 | 0.349 | 0.434 | 0.458 |
| +0.20 | 0.595 | 0.713 | 0.747 |
| +0.25 | 0.808 | 0.902 | 0.924 |

Pooling does not change the operating point materially. The PILOT cases are
already contaminated by mechanical solvability auditing and pilot debugging,
so pooling is **not recommended**. The protocol's PILOT/TEST split is
preserved as-is.

---

## 5. Secondary hypotheses

### 5.1 H3 — Dependency-directed reopen F1

The reopen F1 test uses all 66 cases (both splits). The mechanism-free floor
is 0.792 (PILOT) / 0.823 (TEST) — the blind largest-component policy. The
full-reset ablation scores 0.722 / 0.719. With 66 cases (48 TEST), the
paired bootstrap for `ORION minus blind-larger-component` has adequate
precision: a 0.10 F1 improvement is detectable at >80% power.

### 5.2 H4 — Recursion stability

The 66 cases distribute across dependency depths 0–3. Per-depth precision
is limited (e.g., 6 cases at depth 3 on TEST). H4 is reported as a
descriptive trend (trace fidelity and invariant violation rate versus
depth, Figure ORION-11-6), not a formal hypothesis test.

---

## 6. Summary of findings

| Question | Answer |
|----------|--------|
| Is 32 hidden-shift TEST cases adequate for H1? | **Yes.** Effect +0.25 has ~80% power; effect +0.20 has ~60% power. Adequate for a first evaluation. |
| Is 16 control TEST cases adequate for H2 at +0.02? | **No.** The margin is 5-7x tighter than the narrowest achievable CI upper bound. Near-zero power. |
| Should PILOT be pooled? | **No.** Contamination from auditing; marginal power gain. |
| Should the suite be expanded? | **Not for H1.** For H2, a future revision should either expand controls to 30+ or relax the margin to +0.10. |
| Are stochastic repeats necessary? | **Yes.** 5 repeats per cell reduce within-case variance. The study is powered on 32 cases; without repeats, the effective N is still 32, but the per-case estimate is noisier. |
| Minimum detectable effect (80% power) | H1: ~+0.22 absolute root-success difference on 32 hidden-shift cases (sigma_diff=0.45). |

---

## 7. Pre-registered interpretation rules

These rules are frozen before outcome access. They bind the study's final
interpretation regardless of what the data show.

1. **H1 is SUPPORTED** only if the entire 95% CI for the matched difference
   (ORION minus strongest baseline) on `root_success` lies above +0.05 on the
   32 hidden-shift TEST cases. A CI that merely includes +0.05 is not support.

2. **H2 is NOT EQUIVALENT** at +0.02. The study will report the observed
   difference and its CI. No non-inferiority claim is made at the +0.02 margin
   on 16 controls. An exploratory H2 evaluation at +0.10 may be reported as a
   secondary analysis but is not a pre-registered test.

3. **H3 is SUPPORTED** if the 95% CI for the reopen F1 difference (ORION minus
   blind-largest-component) lies entirely above 0.0 on all 48 TEST cases.

4. **H4 is reported descriptively** — trace fidelity and invariant violation
   rate by depth, with no formal hypothesis test.

5. **CANNOT_CHECK cases** are excluded from every numerator and denominator.
   They are never scored as failures. The number of CANNOT_CHECK cases is
   reported alongside every rate.

6. **Pilot-only analysis** on the 18 PILOT cases is for variance estimation
   and system debugging. No hypothesis verdict is drawn from PILOT.