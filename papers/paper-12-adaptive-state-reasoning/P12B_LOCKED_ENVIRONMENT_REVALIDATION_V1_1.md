# P12B locked-environment revalidation v1.1

**Frozen before the locked-environment re-execution.** The V1 result remains an
immutable historical receipt. A strict reconstruction under the repository's
locked Python 3.12 environment reproduced the scientific counts and estimates,
but correctly rejected full-core equality because V1 records NumPy 2.3.5 while
the lock resolves NumPy 2.5.2 for Python 3.12. This is an environment-identity
mismatch, not evidence that the scientific gates failed.

## Fixed environment identity

- launcher contract: `uv run --frozen --extra candidates`;
- implementation: CPython;
- Python: `3.12.13`;
- NumPy: `2.5.2`;
- lockfile: repository-root `uv.lock`;
- `uv.lock` SHA-256:
  `4e0f595c568cf7cfdf15bb88518ad2fc5951a1cf9f03bb3c4b307471f852dade`.

The cache directory is operational and is not part of the scientific identity.

## Frozen revalidation rule

The V1.1 supervisor must execute two fresh Python subprocesses in the fixed
environment. Authority requires all original P12B scientific and replay gates,
plus exact equality of the five environment fields above. The family panel,
actions, policies, seeds, estimand, thresholds, multiplicity family and
bootstrap procedure are unchanged. The committed V1 receipt must not be edited.

Success retains
`P12B_EQUAL_ACTION_SIGNAL_COMPLEMENTARITY_SUPPORTED`. Any scientific, replay,
lockfile, Python or NumPy mismatch reaches
`P12B_EQUAL_ACTION_SIGNAL_COMPLEMENTARITY_GATE_NOT_MET`.

