# ORION-01 journal package status V2

**Date:** 2026-08-31

This status supersedes `JOURNAL_PACKAGE_STATUS_V1.md` for current filing operations without rewriting the historical record.

- Paper A package: `journal_package_A/`, bound to `theory-A-MANUSCRIPT_V3.md` and `theory-A-CLAIM_LEDGER_V3.md`.
- Paper B package: `journal_package_B/`, bound to `theory-B-MANUSCRIPT_V3.md` and `theory-B-CLAIM_LEDGER_V3.md`.
- Scientific authority: `CANONICAL_JOURNAL_SCIENCE_V3.md` plus the two V3 claim ledgers.
- Closure rule: no package source edit may exceed its ledger; scientific edits belong in a new canonical manuscript/ledger review cycle.
- Rendering is valid only with a fresh `main.pdf` and `BUILD_SHA256SUMS` produced by `build.sh` and accepted by `verify_package.py --require-render`.

The publication package is scientifically bounded and reproducible. Human filing metadata and target-journal formatting remain external administrative inputs.
