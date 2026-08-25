# Changelog

Versions follow [semantic versioning](https://semver.org/). This project is
pre-1.0: the public interface may change between minor versions, and nothing
here promises API stability yet.

## 0.1.0

First versioned release. It marks the point at which the repository became
installable, reproducible and legally redistributable by someone other than
its author — not the point at which its scientific claims became settled.

### Added

- **Licensing.** Apache-2.0 for code, CC BY 4.0 for manuscripts and derived
  data. Third-party terms in `THIRD_PARTY_NOTICES.md`, read from installed
  package metadata rather than from documentation.
- **`scripts/reproduce.sh`** — one-command clean-environment reproduction
  with three distinct exit codes: `0` passed, `1` failed, `2` could not run.
- **`scripts/import_sweep.py`** — walks every module and separates core
  import failures (a defect) from optional-extra failures (expected on a
  base install).
- **`scripts/environment_manifest.py`** — records source commit, interpreter,
  platform and package versions, emitting unreadable fields as null *with a
  reason* rather than omitting or guessing them.
- **`scripts/build_failure_ledger.py`** and `FAILURE_LEDGER.md` — the adverse
  record, generated from execution receipts.
- **`THREAT_MODEL.md`**, **`INSTALL.md`**.

### Fixed

- `scipy` was imported by five source files and declared in no dependency
  list at all. Added to the `candidates` extra.
- The `dev` extra pulled in neither numpy nor scikit-learn, so the documented
  test install could not collect the suite. Collection went from 22 errors to
  7,090 tests collected once `dev` was made to depend on `candidates`.
- `scripts/import_sweep.py` aborted on `orion.benchmarks.__main__`, which
  raises `SystemExit` at import — a `BaseException` that escaped the
  `Exception` handler and took every later module with it.

### Scientific status at this tag

Twenty execution jobs carry frozen terminals: **9 positive, 3 adverse,
8 blocked** on an external party. Every receipt reads
`external_validation: CANNOT_CHECK`, which is accurate rather than pending —
two implementations inside one programme are not independent adjudication.

Two of this programme's own tests were found to be vacuous and are recorded
rather than quietly repaired: the P15 key-compromise arm, and the T19
structural core, whose encoding made both worlds' transcripts identical by
construction so it could only ever report agreement.

`FAILURE_LEDGER.md` carries the full adverse record. It is generated, because
a hand-maintained one drifts favourable.
