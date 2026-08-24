# P1--P5 adversarial theory harness

Internal mathematical audit only; not external or independent peer review.

## Artifacts

- `THEOREM_AUDIT_LEDGER.md` — one row for every new P1--P5 theorem,
  proposition, labelled corollary, and every clause of the umbrella theorem;
  includes explicit counterexample attempts, repairs, and a post-repair audit.
- `ADVERSARIAL_REVIEWER_REPORT.md` — corrected theorem suite with proofs,
  publication-gap diagnosis, recursive research problems, and four scientific
  harness lanes.
- `finite_counterexample_harness.py` — standalone exact finite-witness
  generator; it is not pytest or CI.
- `COUNTEREXAMPLE_RECEIPT.json` — generated receipt. All eight witness checks
  pass. SHA-256:
  `b88c0c6b4f03594235daa0bd07e905d648e941157c99fa1b39bccb8039add39a`.
- `SHA256SUMS` — file-level integrity manifest for the complete audit lane.

## Reproduce the local mathematical receipt

```bash
rtk python development/adversarial-theory-harness-2026-08-23/finite_counterexample_harness.py
```

The receipt has authority `LOCAL_EXACT_MATHEMATICAL_WITNESSES_ONLY`. It does
not alter or supersede any empirical terminal.
