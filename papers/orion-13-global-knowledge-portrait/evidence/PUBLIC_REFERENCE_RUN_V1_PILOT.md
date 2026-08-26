# ORION-P3 public-reference run V1 — development pilot record

**Authority:** `DEVELOPMENT_PILOT_ONLY`  
**Protocol:** `P3.public-reference-mapping.v1`  
**GitHub Actions run:** `32034567843`  
**ORION revision:** `fce08f7792cb0db41ad14942e33170bbb9406e43`

## What the run established

The zero-budget route is operational. GitHub-hosted execution fetched pinned public authorities, bound input identities before outcome access, built 32 cases, ran deterministic ORION/baseline/ablation analysis, bound result hashes, and uploaded the evidence bundle without a provider key, GPU, or new annotation team.

The pilot produced:

- 32 cases;
- ORION mapping accuracy `1.000` on that pilot set;
- flat-predicate canonicalization accuracy `0.875` and false-merge rate `0.125`;
- exact-coordinate conservative accuracy `0.875` with abstention `0.125`;
- paired ORION-minus-flat false-merge difference `-0.125`, bootstrap 95% CI `[-0.25, -0.03125]`;
- no false-split difference against the conservative baseline;
- a `+0.125` false-merge penalty when polarity/modality/attribution/discourse information or obstruction handling was removed.

These values are retained as development history, not promoted to final manuscript evidence.

## Why this run is not publication-final

### 1. Unstable locators

The generated `cases.jsonl` embedded GitHub-runner paths such as `/tmp/muse/...` and `/tmp/scifact/...`. Content hashes were bound correctly, but those path strings are not independently replayable source locators.

### 2. Incomplete coordinate pressure

The pilot selected only `COMPATIBLE` and `CONTRADICTORY` expected relations. Consequently the referent, construct, measurement and temporal-context ablations had zero measured effect. The run therefore cannot support a general semantic-coordinate necessity claim.

## Frozen pilot identities

- SciFact `claims_dev.jsonl` SHA-256: `86f0435d08fdb65d1aa41d1472684f57e6e71930626497bdf4d7a9ec1a632217`
- pilot case artifact SHA-256: `d7f65287500ddd2dffa1d15aa0619d1f9ca6e4d2d1dcb9c5770cad5f3e785d7a`
- `BUILD_REPORT.json`: `b95ce19bc4887fe65ee53b57c07878dda610eb3c38e251c2303af711960ef959`
- `SUMMARY.json`: `fc6636de6718acb87ffdd645bb4049644cda641bb7b30319537ba4cb2aca7759`
- `ANALYSIS.json`: `20ca95361e293df0dffa4687b3fffcd6882ccf6d62205fae879f4289c8b5d5e0`
- pre-bindings hash: `4d045b5178b716470ab2a9ca6dee91eb67a8b8a0ca44098d499fcd2e4c025af0`

## Prospective correction

The next study is separately frozen as `P3.public-reference-mapping.v1.1`. It requires stable upstream-relative locators and explicit authoritative cases for `DISTINCT_REFERENT`, `DISTINCT_CONSTRUCT`, and `DISTINCT_MEASUREMENT` in addition to compatibility and contradiction controls.

No v1 outcome is used to select individual v1.1 cases; only the predeclared structural coverage defects above motivate the new protocol version.
