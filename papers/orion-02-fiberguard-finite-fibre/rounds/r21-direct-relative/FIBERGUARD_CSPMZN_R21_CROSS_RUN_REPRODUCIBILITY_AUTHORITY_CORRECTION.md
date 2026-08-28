# FiberGuard CSP-MZN R21 cross-run reproducibility authority correction

Date: 2026-08-27
Owner: #1550 / #1512
Status: **ADVERSE SCIENCE PRESERVED; CROSS-RUN CUSTODY CANNOT CHECK UNTIL REPAIRED SEPARATE-RUNNER PASS**

## Preserved executions

Dedicated run `33082103451` at head `d1ea1ce0...` executed the frozen round
twice and matched the committed result:

```text
C_R21_CSPMZN_DIRECT_RELATIVE_ADVERSE
result SHA-256 9606f30d1c0c503935c1612b1d352f8b7bef835aeda96478e2e1fdcdb489cbde
```

Relocation-only run `33084807980` at head `800ba6f6...` also executed twice
byte-identically within its runner, but produced:

```text
C_R21_CSPMZN_DIRECT_RELATIVE_ADVERSE
result SHA-256 00d67a629b4967ed0518e242016d458ca197a53f378560b45bb71742500ca558
```

It then failed the comparison with the committed object.  Both complete raw
action artifacts are archived unchanged as `R21_ACTION_ARTIFACT_9650559083.zip`
and `R21_ACTION_ARTIFACT_9651706165.zip`.  The original custody V1 and committed
`9606f30d...` result are not overwritten or relabelled.

## Exact divergence

There are 53 scalar differences only:

- fold 1 `test_row_digest`;
- the global out-of-fold `row_digest`;
- `relative_prediction`, `interval_lower`, and `interval_upper` for the last
  17 fold-1 rows (global row indices 439--455).

Every affected prediction moved by `0.15/9 = 1/60`.  There are zero changes to
selected pairs, route choices, losses, timeouts, acquisition, conformal radius,
aggregate metrics, terminal, hostile controls, or authority fields.  The
Round-2 adverse scientific disposition therefore remains intact.

## Root cause

Those 17 query rows have a bitwise-identical 288-dimensional transformed
static vector.  Thirty route-fit rows have that same vector and compete for
the registered nine-neighbour route regressor.  Their mathematical squared
distances are all exactly zero, so the frozen protocol requires the first nine
lexical instance identities.

The executor evaluated distance as
`||q||^2 + ||x||^2 - 2 q.x`.  With norms around `1.13e9`, hosted BLAS kernels
can accumulate the identical columns differently by a few floating-point bits
before the stable sort.  Stable sorting then preserves lexical order only
inside each *computed* bitwise tie.  Executing twice on one host did not expose
that cross-host residual.

The move from historical `extensions/` to canonical
`rounds/r21-direct-relative/` did not change the executor bytes and did not
cause the divergence.  Reverting the move would not repair it.

## Frozen defect-only repair

The only admissible implementation change is to set a distance to exact zero
when, and only when, the transformed query and training rows are bitwise
identical.  The existing stable sort then implements the already-frozen lexical
tie rule.  No epsilon, rounding, k, source, fold, representation, pair grammar,
conformal level, route threshold, loss, gate, or terminal may change.

A hostile 30-duplicate/17-query test failed before the repair with duplicate
distances `7.62939453125e-06` and passes after the repair with exact zero.  Two
local full replays reproduce the committed `9606f30d...` bytes, but local
replay is not cross-runner authority.

## Current authority and successor rule

Until two separate hosted runners reproduce one another and the committed
object byte-for-byte, the custody status is:

```text
ORION02_R21_ADVERSE_PRESERVED__CROSS_RUN_REPRODUCIBILITY_CANNOT_CHECK
```

A later green record may supersede that string **for reproducibility custody
only**.  It must preserve both archived receipts and this failure.  It does not
replace the `9606f30d...` object, consume another science round, create external
independence, or upgrade production, novelty, journal, or submission authority.
