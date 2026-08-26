# ORION-16–ORION-18 assumption and benchmark regression results V2

**Authority:** `LOCAL_DETERMINISTIC_SUPPORT_ONLY`  
**Artifact-set SHA-256:** `bbf26697db10993486c3620c8571b6231de7eef997d966cdda8f87761e569a04`

This focused additive suite complements the larger V1 finite enumerators. It executes theorem-assumption countermodels for ORION-16 and outcome-bearing benchmark contracts for ORION-17/ORION-18. It uses only the Python standard library and makes no network, model, judge, or LLM API call.

## Executed result

- unit tests: **28**;
- named structural checks: **29**;
- machine-readable hostile/negative-control cases: **37**;
- aggregate terminal: **PASS**.

| Suite | Unit tests | Structural checks | Frozen cases | Terminal |
|---|---:|---:|---:|---|
| ORION-16 | 10 | 10 | 12 | `PASS` |
| ORION-17 | 7 | 10 | 8 | `PASS` |
| ORION-18 | 11 | 9 | 17 | `PASS` |

## What V2 adds

- **ORION-16:** positive and negative controls for path-realizable reopening minimality, declared write footprints, separation, authority escalation, recursive cycles, self-authorization, and history-aware commutation.
- **ORION-17:** eight frozen cases spanning hidden branches, unknown/censored coverage, deceptive route diversity, dead-end revisit, required and harmful topology change, and a non-retrieval experimental-design transfer case.
- **ORION-18:** paired clean/blocked cases across all five domains, five explicit laundering attacks, `CANNOT_CHECK`, and a clean authorized cross-domain coercion control so deny-all policies cannot pass.

## Reproduction

```bash
python papers/candidates/run_assumption_regressions_v2.py \
  --json-output papers/candidates/ASSUMPTION_REGRESSION_RESULTS_V2.json \
  --markdown-output papers/candidates/ASSUMPTION_REGRESSION_RESULTS_V2.md
```

## Claim boundary

- Finite checks do not prove unrestricted theorems.
- Reference-policy oracles do not establish live-agent efficacy.
- No result authorizes novelty, empirical superiority, flagship promotion, or peer-review readiness.
