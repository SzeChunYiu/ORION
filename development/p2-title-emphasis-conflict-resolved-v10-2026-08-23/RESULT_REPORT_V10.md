# P2 V10 provider-native conflict-resolved title-emphasis diagnostic

## Terminal

`P2_V10_PROVIDER_NATIVE_CONFLICT_RESOLVED_TITLE_EMPHASIS_FAILS_ONE_OR_MORE_FROZEN_GATES__RESIDUAL_DISCARDED__EXACT_U4_FALLBACK`

## Exact one-shot result

The only V9 population blocker was repaired through source-native identity semantics, not label choice. Provider record IDs `1003` and `1018` have the same normalized title--abstract content identity but distinct author and DOI hashes, and both have blank provider `duplicate_record_id`. The pinned provider notebook defines duplicate grouping by cleaned title plus authors. V10 therefore retained both exact nonduplicate source rows and changed nothing else.

All source, population, V9, V8/u4, protocol, implementation and runner bindings passed. The frozen three arms executed once on **21,897** rows across all seven source-disjoint reviews in **357.789818416989874 seconds**.

| Frozen controller estimand | Value | Gate |
|---|---:|---|
| mean delta CRE20 | +0.000779992745 | fail (`>= +0.010858985821`) |
| mean delta R@10 | -0.005382681125 | fail (`>= +0.010858985821`) |
| mean delta WSS95 | +0.001765466550 | pass (`>= 0`) |
| positive CRE20 reviews | 4/7 | fail (`>= 6/7`) |
| positive R@10 reviews | 1/7 | fail (`>= 6/7`) |
| worst-review delta R@10 | -0.044444444444 | pass (`>= -0.05`) |
| controller WSS95 positive in every review | yes | pass |

The residual is not admitted. Exact u4 remains the fallback. The positive mean WSS95 and passing harm/absolute-work-saving gates do not overwrite failure of both coprimary magnitude gates and both sign gates. No threshold was relaxed and no review was deleted.

## Execution boundary

- execution attempts: **1**
- grid/tuning/retry: **none**
- pytest/repository CI/git/manuscript/shared-file operations: **none**
- public same-workspace development: **yes**
- independent/protected confirmation: **no**

This result does not reverse the adverse KIFMS finding and does not authorize source-general, domain-general, workflow-general, application-exact, or ORION-specific superiority.

## Hash

- `RESULT_V10.json`: `c69e5634b8d0e82a1fa393dbae276d728e9a2f7ba4c9db81a27c0329e2e66742`
- compact receipt and all other packet hashes: `SHA256SUMS`
