# FiberGuard R21 CSP-MZN direct-relative joint-route result

> **Reproducibility-custody correction (2026-08-27):** a later separate hosted
> run preserved this adverse terminal and every decision/loss, but
> exposed a cross-run exact-tie byte divergence.  The two raw receipts and the
> defect-only repair boundary are preserved in
> `FIBERGUARD_CSPMZN_R21_CROSS_RUN_REPRODUCIBILITY_AUTHORITY_CORRECTION.md`.
> Cross-run custody remains `CANNOT_CHECK` until two separate repaired runners
> match; the adverse Round-2 science below is not retracted or upgraded.

## Terminal

```text
C_R21_CSPMZN_DIRECT_RELATIVE_ADVERSE
```

This is a completed adverse Round-2 result, not `CANNOT_CHECK`, null, or a
failed positive. ORION-02 is now **OPEN, 2/3 distinct rounds consumed**: BNSL
Round 1 is null; CSP-MZN direct-relative/joint-route Round 2 is adverse. The
TSP-LION2015 cost-prerequisite `CANNOT_CHECK` is preserved but did not
adjudicate or consume a distinct mechanism.

## Bound subject and execution

- subject: GPLv3 `coseal/aslib_data@551b22beef8df17de59286b4822ef720e0aa4d6f`;
- scenario: `CSP-MZN-2013`, 4,642 instances, 11 solvers, 155 features;
- protocol/executor freeze before outcome access:
  `ec5f757e8747449e40bbfe6fde6e1fa227656f49`;
- reporting-only correction:
  `a3100c5c9278c6d8ab862680c8aea315273b7b93`;
- corrected result SHA-256:
  `9606f30d1c0c503935c1612b1d352f8b7bef835aeda96478e2e1fdcdb489cbde`;
- two corrected executions were byte-identical;
- all ten outer folds and `44 * 10 = 440` legal joint-pair selection profiles
  were executed.

The first complete frozen result remains recorded at SHA-256
`e9be34bd50b5f0a825c3c1b08ae05ed1d19a1b5937af791435283ffeb0e3736b`.
Its only defect was an omitted post-acquisition `choices` field; all scientific
vectors and the adverse terminal were already the same.

## Decisive outcome

| Arm | Learned rows | Timeouts | Mean total excess | p95 | Maximum |
|---|---:|---:|---:|---:|---:|
| always learned | 4,642 | 1,101 | 696.399 | 688.430 | 18,756.750 |
| point relative (primary comparator) | 3,852 | 1,110 | 732.374 | 713.600 | 18,754.080 |
| **certified direct relative** | **1,414** | **1,847** | **3,582.851** | **18,003.300** | **18,754.080** |
| post-acquisition same route | 1,414 | 1,847 | 3,584.359 | 18,005.390 | 18,756.750 |
| uncertainty only | 2,312 | 1,907 | 3,794.489 | 18,003.560 | 18,754.080 |
| random rate matched | 1,414 | 2,407 | 5,738.110 | 18,007.260 | 18,754.080 |
| always fallback | 0 | 3,073 | 8,304.387 | 18,028.200 | 18,754.080 |
| oracle route (descriptive only) | 2,759 | 1,066 | 562.295 | 660.750 | 18,754.080 |

The certified router's mean minus the same-information point router is
`+2,850.477`, with predeclared paired-bootstrap 95% interval
`[+2,659.641, +3,045.890]`. Its timeout count also rises by 737. The result is
therefore decisively adverse under the prospectively disjoint terminal rules.

The interval mechanism itself did not simply collapse:

- empirical paired-interval coverage: `0.910599` at nominal `0.90`;
- certified learned coverage: `1,414 / 4,642 = 0.304610`;
- sign-error rate on certified learned rows: `0.094059`.

The adverse mechanism is instead the safe-default alignment boundary. The
relative interval conservatively sends 3,228 uncertain/fallback-favoured rows
to a fallback solver. On this subject the selected learned selector is much
stronger than that fallback on average, so this conservatism converts relative
sign caution into large total decision harm. Marginal sign coverage is not
operational route value.

## Hostile controls

All registered controls passed:

- complete Cartesian and independent nested legal-pair enumerations agree;
- diagonal-only pairing has no authority;
- decisions are measurable from pre-optional-acquisition `static` information;
- the pre/post loss difference equals exactly the avoided `dynamic` charge on
  fallback paths;
- common-oracle subtraction preserves every pair sign;
- every instance has exactly one out-of-fold choice/loss/timeout/acquisition
  record for every arm;
- shuffled relative labels remain unauthorized;
- R19 hostile values remain `full=0`, `diagonal-only=50`, and timing
  `pre=5`, `post=10`.

## Authority and next gate

This is bounded historical out-of-fold evidence on one pinned MiniZinc/CSP
scenario. It does not grant deterministic/pathwise safety, unseen-domain or
production value, generic learned-selector superiority, external independence,
novelty, journal authority, or submission readiness.

Round 2 must not be repaired by widening the relative interval, preferring the
always-learned arm after seeing test outcomes, changing the fallback, or
retuning BNSL/CSP-MZN. The next permissible experiment is the already-declared
scientifically distinct **Round 3 safe learned proposal ordering**: learning
may propose refinement/order choices only behind the exact certificate shield
and may not change admissibility or conditional authority. If Round 3 is also
null/adverse, trigger the specialist boundary-paper fallback without weakening
evidence standards.
