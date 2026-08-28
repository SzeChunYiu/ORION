# Anonymous review archive

This archive contains the exact anonymous manuscript source, target adapter, controlled synthetic task specification, frozen evidence summaries, exact-contract and TREC-COVID records, bounded external stress-test records, figure sources and regeneration/check scripts.

## Build

From `manuscript/`, run:

```text
SOURCE_DATE_EPOCH=1787918400 tectonic ipm_submission.tex
```

The expected PDF digest and byte count are recorded in `SUBMISSION_MANIFEST.json` outside the archive. The CAS single-column class is the public Elsevier class resolved by the TeX distribution.

## Controlled evidence

The synthetic controlled reconstruction uses the included task specification, manifest, statistics plan and scripts together with the project package named by the import statements. The frozen publication summary includes record-set and artifact-list digests. Deterministic repeats test implementation stability and do not enlarge the statistical unit.

## Exact-contract and TREC evidence

The exact-contract records preserve 400-case arm counts, independent verification, bootstrap seed and the information-equivalent tie. The TREC-COVID record preserves all 50 paired topics, the failed recall/cost gate and favorable secondary nDCG result. Third-party corpora are not redistributed.

## Authority

Successful hashes, builds and checks establish package integrity and local computational reproduction only. They do not create external scientific authority or a retrieval-superiority result.
