# ORION-P3 public-reference Step-3 rescue status V1

**Date:** 2026-08-17  
**Issue:** #100  
**Route:** `P3.public-reference-mapping.v1`

## Resource-constrained route

Merged PR #255 provides the prospective public-reference protocol, authority policy, pinned MUSE/SciSchema/SciFact inputs, deterministic builder/evaluator/analysis, claim ledger and tests. Merged PR #260 adds portable freezing, independent replay, credential-free execution, and the frozen evidence archive.

No paid annotator commission, provider credential, or GPU is required. Unsupported coordinates are not guessed; they remain outside the narrower public-reference claim.

## Executed evidence

GitHub Actions run `32046403537` reached the complete gate on 2026-08-17:

- isolated public-reference tests: GREEN;
- exact pinned MUSE / SciSchema / SciFact retrieval: GREEN;
- authoritative candidate pools: MUSE 258, SciFact 957, SciSchema 16;
- deterministic selected atlas: 32 cases;
- represented strata: biology, imaging, materials, MUSE cross-domain, scientific claim verification;
- represented case families: different-name/same-referent, polarity/modality/attribution/context, valid/invalid representation mapping;
- build status: `READY_FOR_FREEZE`, no blockers;
- portable gold status: `PUBLIC_REFERENCE_GOLD_FROZEN`;
- portable gold SHA-256: `35f9e39b75ff53b7f0ec82cd03ebcaaa82509ee0aea3f5b96aac3fd62c854ed8`;
- independent second freeze: byte-for-byte identical / replay PASS;
- deterministic evaluation and publication analysis: GREEN.

The pointer/hash-only gold and evidence are archived on `main` under:

- `gold/adjudicated/public-reference-v1/`;
- `evidence/public-reference-v1/`.

No upstream MUSE paragraph text is vendored into the gold artifact.

## Narrow empirical result

On the frozen 32-case public-reference mapping atlas:

- ORION mapping semantics: accuracy `1.000`, false-merge `0.000`, false-split `0.000`;
- flat predicate canonicalization: accuracy `0.875`, false-merge `0.125`, false-split `0.000`;
- paired ORION-minus-flat false-merge difference: `-0.125`, 95% paired bootstrap CI `[-0.250, -0.03125]`;
- forcing compatibility without obstruction produces `+0.125` false-merge delta, 95% CI `[+0.03125, +0.250]`;
- removing modality/polarity/attribution/discourse produces the same `+0.125` false-merge delta on the covered cases.

These results apply only to the public-reference mapping route and must not be promoted to raw-text extraction, retrieval, provider, downstream-answering, or universal cross-domain adequacy.

## Remaining scientific boundary

The original stronger `P3.cross-domain-atlas.v1` end-to-end study still requires evidence for its broader eight-family construct-validity/recoverability claim. That remains `CANNOT_CHECK`; the public-reference route is not a semantic shortcut around missing authority.
