# Installation

## Requirements

- Python 3.11 or newer. Verified on 3.11.5 (Linux x86_64) and 3.13.12
  (macOS arm64).
- `git`, for the source-identity fields the environment manifest records.

Two runtime dependencies are pulled in: `cryptography` and `defusedxml`.
Both are permissive and OSI-approved; see `THIRD_PARTY_NOTICES.md`.

## Install

```bash
git clone https://github.com/SzeChunYiu/ORION.git
cd ORION
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -e .
```

## Verify the install did what you think it did

```bash
bash scripts/reproduce.sh
```

This builds a **fresh** virtualenv rather than reusing yours, installs from
source, imports the package, validates the check battery, and writes
`ENVIRONMENT_MANIFEST.json`.

Read its exit code rather than its output:

| Code | Meaning |
|---|---|
| `0` | ran and passed |
| `1` | ran and **failed** — a real defect |
| `2` | **could not run** — environment problem, verdict unknown |

The split between `1` and `2` is the point. A verification script that
cannot distinguish "this is broken" from "I never got to check" will report
health it never measured. If you wrap this in CI, treat `2` as a build
error, not as a pass.

To reuse a virtualenv instead of creating a throwaway one:

```bash
ORION_REPRO_VENV=/path/to/venv bash scripts/reproduce.sh
```

## Run the tests

```bash
python -m pip install pytest pytest-timeout
python -m pytest tests/ -q
```

The suite is substantial. Run it somewhere with real disk headroom: it
creates per-test temporary trees, and an out-of-space failure midway
produces confusing errors that look like logic defects rather than a full
filesystem.

## Regenerate the derived records

```bash
python3 scripts/build_failure_ledger.py     # FAILURE_LEDGER.md
python3 scripts/environment_manifest.py     # ENVIRONMENT_MANIFEST.json
```

Both are generated. Editing them by hand is a mistake that will be silently
overwritten on the next run — and in the ledger's case, hand-editing an
adverse record is how it starts drifting favourable.
