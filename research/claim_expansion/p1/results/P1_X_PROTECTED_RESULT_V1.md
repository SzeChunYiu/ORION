# P1-X protected execution V1 — immutable result and post-access discrepancy

Date: 2026-08-19  
Parent: #529  
Outcome-access receipt: `3805823aff202bda6014af578d68b3329f0f5e2a`

## Frozen V1 result

All 400 precommitted protected identities were generated once and analyzed with the frozen V1 controller/analysis subject.

- P1-X: **400/400 ESRD = 1.000**.
- B1 donor-complete greedy: **255/400 = 0.6375**.
- B2 success-authorizes-reframe: **175/400 = 0.4375**.
- B3 ideal typed product: **400/400 = 1.000**, with zero decision mismatches to P1-X.
- Frozen V1 paired P1-X minus B1 difference: **+0.3625**; domain-stratified bootstrap 95% CI **[0.315, 0.410]**; McNemar `b=145, c=0`, two-sided `p=4.484155085839415e-44`.
- P1-X records zero false high-level reframes and zero protected-invariant violations.
- Every domain has 80 cases; P1-X is 1.000 and B1 is 0.6375 in each domain.

The predeclared statistical/non-regression gates pass on the literal frozen V1 execution.

## Mandatory post-access discrepancy P1X-V1-D001

A fresh independent reconstruction after outcome access found that B1 and B2 contain a baseline implementation defect in their `NO_CHANGE` guard: the code tests `all(... for status in statuses)` where `statuses` is a dictionary, so it iterates revision-class keys instead of status values. As a result, each comparator incorrectly misses **25 clean no-change controls**.

This defect was frozen before outcome access. It is therefore **not patched inside V1** and the V1 result above remains immutable.

The bug does not affect P1-X or B3, and it does not create P1-X/B3 expressivity separation. However, it materially weakens the primary comparator and therefore prevents V1 alone from authorizing the wider publication claim.

Required repair: a **new disjoint V2 replication**, frozen before its outcomes, changing only the comparator bug plus disjoint case identities/templates. V1 remains visible as positive-but-comparator-compromised evidence.

## Scientific interpretation that remains valid

V1 establishes that the frozen P1-X decision contract is internally coherent on the protected exact battery and that an information-equivalent ideal product ties it exactly. Therefore **no inherent expressivity or centralization advantage is supported**.

V1 does **not yet** authorize the wider empirical architecture claim against the realistic donor-complete product because comparator fairness is reopened by P1X-V1-D001.

Terminal: `P1_X_V1_PROTOCOL_POSITIVE__COMPARATOR_FAIRNESS_REOPENED`.
