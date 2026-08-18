# Mathlib v2 corpus source record

This directory contains an exact, unmodified, outcome-blind sample of active
Mathlib source files plus the upstream build identity files:

- repository: <https://github.com/leanprover-community/mathlib4>
- commit: `e72c1e277f31441626621f7d0c7207862fc25569`
- commit time: 2026-08-18T08:09:40Z
- Lean toolchain: `leanprover/lean4:v4.34.0-rc1`
- upstream license: Apache-2.0; the full upstream `LICENSE` is retained here
- materialized: 2026-08-18

`../../MATHLIB_CORPUS_V2_MANIFEST.json` records the path, byte count and SHA-256
digest of every selected source and support file. The deterministic selection
code and policy are in `../../prepare_mathlib_corpus_v2.py`; no tactic sequence,
proof outcome or parser result was used for selection. Reproduction must stop
on any source, revision, toolchain or manifest mismatch.
