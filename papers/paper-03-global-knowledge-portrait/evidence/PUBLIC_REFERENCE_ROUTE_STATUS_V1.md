# ORION-P3 public-reference Step-3 rescue status V1

**Date:** 2026-08-17  
**Issue:** #100  
**Route:** `P3.public-reference-mapping.v1`

## Implemented on main

Merged PR #255 already provides the resource-constrained public-reference route:

- prospective non-mutating protocol;
- public-authority policy;
- pinned MUSE, SciSchema and SciFact sources, with SciER retained subject to exact dataset binding;
- machine-readable case schema;
- deterministic import/build layer;
- deterministic ORION mapping evaluation and conservative controls;
- statistical/ablation analysis;
- Makefile build/evaluate/analyze/test targets;
- claim ledger and pilot correction;
- isolated unit tests.

Issue #100's reuse box is therefore complete: public MUSE/SciSchema/SciER-style annotations are reused where authority/license fit instead of being recreated.

## What remains scientific rather than infrastructural

The route still needs a frozen case artifact produced from the pinned upstream data and then replayed independently. It must not fill missing coordinates with model guesses merely to reach the original end-to-end checklist.

The original stronger `P3.cross-domain-atlas.v1` raw-text/expert-gold study remains a separate `CANNOT_CHECK` target. The public-reference route is a narrower primary experiment that the owner can actually execute without paid annotators, provider credentials, or GPU resources.

## Next gate

Use the credential-free GitHub Actions lane to:

1. fetch the exact pinned public authorities;
2. build the 32-case public-reference atlas;
3. run deterministic evaluation and analysis;
4. emit checksums and a build report;
5. archive the generated cases/results as a workflow artifact.

Only after the build report says `READY_FOR_FREEZE` should execution identities be bound and empirical issue boxes be promoted.
