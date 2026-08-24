# Active-identification theory harness

This isolated development lane derives a finite theory connecting P3-style
partial-identification envelopes with P5-style adaptive revision
discrimination. It does not edit either manuscript.

## Artifacts

- `THEORY.md` — assumptions, four theorem candidates, two propositions,
  proof sketches, claim boundaries, and unresolved extensions.
- `NEGATIVE_RESULT_LEDGER.md` — eleven immutable failed conjectures or scope
  extensions, each with a finite counterexample, a new research identity, and
  a next discriminator. The original eight are checked here; A1--A3 are
  checked by the separate adversarial-review verifier.
- `INTEGRATION_CANDIDATES.md` — concise candidate claims for later P3/P5 or
  umbrella integration.
- `finite_active_identification_harness.py` — exact rational or explicit
  numerical checks for the eight witnesses, including an enumerated
  risk-vector Bellman frontier.
- `COUNTEREXAMPLE_RECEIPT.json` — machine-readable 8/8 receipt.
- `SHA256SUMS` — file-integrity manifest.

The same-repository adversarial review is in
`development/active-identification-theory-review-2026-08-23/`. It found no
counterexample to the finite stationary core but blocks a distinct-theorem
novelty claim: the Bellman/vector and adaptive pairwise-KL components are
donor-owned. The defensible contribution is a finite synthesis and audit
interface unless a stronger successor theorem survives a new literature and
proof audit.

## Reproduce

From the takeover checkout:

```bash
rtk python development/active-identification-theory-2026-08-23/finite_active_identification_harness.py
rtk python -m json.tool development/active-identification-theory-2026-08-23/COUNTEREXAMPLE_RECEIPT.json >/dev/null
rtk sha256sum -c development/active-identification-theory-2026-08-23/SHA256SUMS
```

The receipt is a local mathematical witness only. It is not empirical
validation, protected custody, independent review, or evidence that any real
acquisition kernel is correctly specified.
