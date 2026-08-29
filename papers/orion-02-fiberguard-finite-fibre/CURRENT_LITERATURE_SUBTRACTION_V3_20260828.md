# ORION-02 V3 current literature subtraction — 2026-08-28

**Purpose:** submission-positioning audit for `MANUSCRIPT_V3.md`  
**scientific_authority_delta:** `NONE`

## Search question

Does the V3 finite-fibre certifiability/refinement paper collide with current work on sufficient information, robust decision making, conditional coverage, or selection-conditional conformal prediction?

## Closest donor families

### 1. Information sufficiency and experiment comparison

Blackwell-style comparison of experiments and classical sufficient-statistic theory own the general principle that the value of information is decision-relative. Current work continues to refine information orderings, including robust/prior-free variants. V3 therefore makes no novelty claim for “more informative representations support better decisions” or for fibres/partitions as an information object.

### 2. Interval covering and greedy refinement

Covering sorted scalar values with the minimum number of fixed-length intervals is a classical greedy problem. The proof pattern used in V3-C5 is donor-owned. The paper's claim is the mapping from certificate tolerance to that exact covering problem inside the fibre-certifiability calculus, not a new interval-covering algorithm.

### 3. Conformal and conditional coverage

Conformal prediction owns distribution-free marginal coverage under exchangeability. Recent work explicitly studies validity after selection and local/conditional coverage:

- Ying Jin and Zhimei Ren, **“Confidence on the Focal: Conformal Prediction with Selection-Conditional Coverage,”** arXiv:2403.03868 (2024). The paper constructs finite-sample prediction sets with coverage conditional on data-dependent selection for broad classes of selection rules.
- Yusuf Sale and Aaditya Ramdas, **“Online Selective Conformal Prediction: Errors and Solutions,”** arXiv:2503.16809 (2025). The paper identifies failures in online selective calibration strategies and gives alternatives that preserve the exchangeability needed for selection-conditional validity and FCR control.
- Zheng Zhou, Xiangfei Zhang, Chongguang Tao and Yuhong Yang, **“Conformal Prediction Assessment: A Framework for Conditional Coverage Evaluation and Selection,”** arXiv:2603.27189 (2026). The paper treats conditional coverage assessment as a supervised reliability-estimation problem and uses the resulting estimates for model selection.
- Yinjie Min, Liuhua Peng and Changliang Zou, **“A Unified Theory of Conditional Coverage in Conformal Prediction with Applications,”** arXiv:2605.11602 (2026). The paper develops non-asymptotic routes to conditional-coverage guarantees and a common framework for conditional-coverage methods.

These sources own statistical conditional-coverage methodology. V3 does not claim a new conformal method and does not use the R24 diagnostic as evidence that its real fibres satisfy a measured `D(z)` condition.

## Surviving residual

The defensible residual is narrower:

> for a deterministic certificate that is constant on a finite representation fibre, target diameter gives the exact minimax certificate radius; the same diameter threshold gives an iff certifiability criterion; minimal arbitrary refinement is an exact scalar interval-cover problem; a declared separator family is sufficient exactly when it separates every pair whose target gap exceeds the tolerance diameter; and whole-fibre abstention coverage follows exactly from the same threshold.

The value is in putting those pieces into one fail-closed certification/refinement object and binding it to a preserved empirical certificate failure without claiming the failure empirically measured fibre diameter.

## Novelty posture

- **Do not claim:** novel sufficient statistics, novel Blackwell ordering, novel interval-cover algorithm, novel conformal prediction, novel conditional-coverage theory, generic representation-learning novelty.
- **May claim, at bounded scope:** exact finite-fibre certifiability/refinement calculus for the registered certificate object; prospective discriminator that a real separator family must distinguish every target-separated pair relevant at the declared tolerance.
- **External review needed:** whether this synthesis plus the adverse application is sufficiently significant for the selected venue.

## Stop rule

A closer donor may narrow the residual further; it does not justify changing the theorem or adding a post-outcome empirical rescue. If venue reviewers judge the general calculus too elementary, route the bounded paper to a more specialist theory/methodology venue rather than reinstating the defective V2 compiler spine.
