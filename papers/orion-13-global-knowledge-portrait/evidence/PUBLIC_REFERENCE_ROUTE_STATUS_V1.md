# ORION-13 public-reference Step-3 rescue status V1

**Date:** 2026-08-17  
**Issue:** #100  
**Route:** `ORION-13.public-reference-mapping.v1` + disjoint confirmatory `v1.1`

## Resource-constrained route

Merged PRs #255/#260 established the zero-paid-resource public-reference route using pinned MUSE, SciFact and SciSchema authority, portable gold freezing, deterministic evaluation and archived evidence. Merged PR #262 moved only the immutable narrow result into the manuscript and claim ledger.

No paid annotator commission, provider credential, or GPU is required. Unsupported coordinates are not guessed; they remain outside the narrower public-reference claim.

## Initial executed evidence

The first 32-case public-reference atlas is archived under `public-reference-v1/` with portable gold SHA-256 `35f9e39b75ff53b7f0ec82cd03ebcaaa82509ee0aea3f5b96aac3fd62c854ed8`. It produced ORION false-merge 0.000 versus 0.125 for flat predicate canonicalization, paired delta -0.125 with 95% CI [-0.250,-0.03125].

Because that first run's execution identities were not fully bound prospectively, it is treated as an initial narrow result rather than the final confirmatory authority.

## Execution-frozen disjoint confirmation

A second 32-case holdout was selected/frozen before any confirmatory system output in freeze-only workflow run `32047464810`:

- deterministic selection offset 32 from the same pinned authority pools;
- zero case overlap with the first atlas;
- five represented strata: materials, MUSE cross-domain, physics, psychology, scientific claim verification;
- three represented case families: different-name/same-referent, polarity/modality/attribution/context, valid/invalid representation mapping;
- raw holdout SHA-256 `79316a561c96ac968bf2598501850bd90deaf1b78501346b0c703663ef794f2b`;
- portable holdout SHA-256 `13a76c68c149c2552f3543babeca6e1ad5afe23c45ea9c0dc365c1445cf2782b`;
- portable freeze independently replayed before execution.

`protocol/PUBLIC_REFERENCE_CONFIRMATORY_EXECUTION_V1.json` then froze the exact holdout hash, source revisions, evaluator Git blobs, bootstrap seed, margins and pass rule while `confirmatory_outcome_accessed_at_freeze=false`.

Confirmatory workflow run `32048125743` is GREEN and verified every bound identity before evaluation. On the disjoint holdout:

- ORION: accuracy 1.000, false-merge 0.000, false-split 0.000;
- flat predicate canonicalization: accuracy 0.8125, false-merge 0.1875, false-split 0.000;
- paired ORION-minus-flat false-merge delta: -0.1875, 95% CI [-0.34375,-0.0625];
- ORION-minus-exact false-split delta: 0.000, 95% CI [0.000,0.000];
- predeclared false-merge superiority: PASS;
- predeclared false-split non-inferiority: PASS;
- combined confirmatory primary verdict: **PASS**.

The discriminating effect is concentrated in the 13 polarity/modality/attribution/context cases: flat canonicalization false-merged 6/13 while ORION false-merged none. The other covered families were correct under all compared rules.

Covered ablations reproduce the structural signal: forcing compatibility without obstruction and removing modality/polarity/attribution/discourse each add +0.1875 false merges, 95% CI [+0.0625,+0.34375]. Other zero-effect ablations remain coverage-limited/descriptive.

Frozen confirmatory gold, execution manifest, summary, analysis, provenance and checksums are archived under `public-reference-v1.1-confirmatory/`.

## Remaining scientific boundary

This is now a prospectively replicated result for the already-structured mapping calculus. It still does **not** establish the original `ORION-13.cross-domain-atlas.v1` end-to-end claims about raw-text extraction, strongest model/RAG/schema baselines, full eight-family construct validity, recoverability of generated portraits, downstream scientific utility, or W-expansion. Those remain `CANNOT_CHECK` until separately frozen evidence exists.
