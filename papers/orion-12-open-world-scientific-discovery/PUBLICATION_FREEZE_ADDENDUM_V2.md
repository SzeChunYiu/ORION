# ORION-12 publication-freeze addendum V2

**Freeze date:** 2026-09-01  
**Status:** `CURRENT_BOUNDED_CONTROL_METHOD__EXTERNAL_SUPERIORITY_NOT_SUPPORTED__ESTIMATOR_SIGNAL_INERT`

This successor retains the V1 filing scope and incorporates the landed BEIR
route-aware stopping diagnostics. It grants no broader authority.

## Current ceiling

The paper supports a fail-closed acquisition-control method that separates
route stopping from task closure, derives route independence from provenance,
and retains unavailable material routes as open obligations. The controlled
index and 400-case exact-contract battery support the declared mechanism.

The external superiority claim is not supported. The registered TREC-COVID
comparison has recall@100 delta `-0.01769` with 95% bootstrap interval
`[-0.02729,-0.00906]` and 175.7% more candidate reads. The favorable nDCG@10
result is secondary and cannot rescue the failed recall-and-cost gate.

## New negative mechanism localization

Two prospectively separated BEIR successors test explanations for the
route-aware stopping failure:

- V2 changes threshold scale by density normalization. On ArguAna, all five
  stopping decisions remain identical to V1.
- V3 makes the estimator query-conditional and scales by each query's unseen
  fraction. ArguAna again remains identical to V1 at all five depths; SciFact
  is also unchanged, while NFCorpus changes slightly without approaching the
  fusion baseline.

The V3 falsifier therefore fires with terminal `CONDITIONAL_ESTIMATOR_INERT`.
On ArguAna, the rank-overlap marginal predicts near-zero contribution from
every unread route for every query and prefix. Threshold scale and query
conditioning cannot act on a signal that contains no discriminating
information. This is a sharper negative: the observed defect lies in the
measurement, not merely the rule reading it.

The no-rescue clause remains binding. No fourth estimator is introduced under
this identity. A successor must change the statistic under a new frozen
protocol.

## Retained undetermined boundaries

OpenAIRE remains `CANNOT_CHECK` after provider invalidity. The fresh 48-task
campaign was not accessed. Complete-gold and exact-contract results remain
controlled diagnostics and do not establish open-world completeness. The V2/V3
successors have `scientific_authority_delta: NONE`; they narrow mechanism
interpretation without converting the earlier negative into a pending success.
