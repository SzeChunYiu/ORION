# ORION-02 C-NBR2 — certified-neighborhood revival authority correction

> **Authority status: `QUARANTINED_IMPLEMENTATION_DEVIATION`.**
>
> PR #1493 was merged as main commit `9d270935dfbbf0c2881929d93793119ed4726660`, but the merged executor does **not** implement the frozen C-NBR2 protocol. The merge does not promote the reported `VALID_WITHOUT_COVERAGE_OR_VALUE` terminal to theorem, experiment, application, or manuscript authority.
>
> Preserve the merged result JSONs as immutable receipts of the defective execution. Do not overwrite them and do not infer a corrected result from the exposed numbers.

## Blocking protocol/executor mismatch

The frozen protocol `CERTIFIED_NEIGHBORHOOD_CONFORMAL_PROTOCOL_V1.md` defines
`d1(x)` as the Euclidean distance from `x` to the **single nearest DEV-TRAIN
anchor**, and then sets

`sigma(x) = CNBR2_SIGMA_OFFSET + d1(x)`.

The merged executor `certified_neighborhood_conformal.py`, however, computes

```python
d1 = distances[:, 0]
```

which is the distance to DEV-TRAIN row 0, not the rowwise nearest-anchor
distance. `neighbour_rows` is sorted correctly, but its nearest index is not
used to obtain `d1`.

This value is scientifically load-bearing: it enters `sigma`, split-conformal
nonconformity scores, pooled and Mondrian quantiles/strata, held-out bounds,
certificate coverage, and the reported nearest-anchor geometry diagnostic.
The synthetic self-test does not detect this mismatch because calibration and
test both use the same defective `d1` implementation.

Therefore the merged numerical receipt is a reproducible
**implementation-deviation receipt**, not a protocol-faithful execution.

## Authority consequence

Until a repaired frozen rerun lands:

- `VALID_WITHOUT_COVERAGE_OR_VALUE` is **quarantined** and must not be cited as
  C-NBR2 scientific authority;
- the reported 14–17-unit nearest-anchor spacing and the resulting ~10x
  geometric-gap explanation are not admissible;
- `certification-constant stage exhausted`, `blocker geometric not
  methodological`, and `C-NBR lane closed terminal` are suspended;
- the earlier C-NBR V1 `CERTIFICATE_INVALID` result remains the last
  protocol-faithful certificate terminal for this lane;
- merging #1493 into `main` changes repository custody only, not evidence
  authority.

## Exact repair gate

The repair must be defect-only and prospective with respect to the corrected
execution:

1. Change only `d1` to the rowwise nearest-anchor distance, e.g. the distance
   at `neighbour_rows[:, 0]` (or an equivalent rowwise minimum). Do not change
   alpha, `mu=16`, the sigma offset, epsilon, representations, source bytes,
   split rules, fallback, or comparison arms.
2. Add a hostile test in which training row 0 is deliberately far while a
   different row is nearest, plus an anchor-permutation-invariance test. Both
   must fail the merged executor and pass the repair.
3. Commit the repaired executor and tests **before** reading corrected target
   outcomes.
4. Rerun the exact same frozen source and split definitions and write a new
   immutable result artifact. Preserve the #1493 result files unchanged.
5. Accept whatever corrected positive, null, adverse, or invalid terminal is
   produced. Do not retune the protocol in response to the repaired outcome.

A useful custody record for the repair should bind the defective merge commit
`9d270935dfbbf0c2881929d93793119ed4726660`, the original frozen protocol
commit `31ee8705c50d74d20828d67560bbf871fd9e96f5`, the repair commit, executor
SHA-256, result SHA-256, and rerun job/host receipt.

## Two prose corrections that remain independent of the rerun outcome

For a bound of the form

`U(x) = m(x) + q_hat * (1 + d1(x))`,

certification at threshold `eps` requires

`d1(x) <= (eps - m(x)) / q_hat - 1`.

When `m(x) >= 0`, the optimistic ceiling is therefore
`d1(x) <= eps / q_hat - 1`, not `eps / q_hat`.

Also, ordinary split-conformal finite-sample coverage relies on exchangeability
between calibration and test examples. The deliberately family-disjoint panel
is a transfer/distribution-shift audit; absent a separate non-exchangeable or
shift-valid conformal argument, its observed violation rate is empirical
fixed-panel evidence rather than an automatic distribution-free coverage
guarantee.

## Historical receipt retained for provenance

The merged #1493 files record `q_hat` around 3348–3375 PAR10/unit, zero
reported certificate coverage, and degeneration of the CNF arms to SBS. Those
numbers remain useful only for reproducing and diagnosing the defective
execution. They are not evidence for the scientific terminal until the repair
gate above is completed.
