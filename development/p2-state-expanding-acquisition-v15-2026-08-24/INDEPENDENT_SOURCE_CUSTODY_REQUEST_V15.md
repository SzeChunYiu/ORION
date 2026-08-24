# P2 V15 independent source-custody request

This packet requests one external, outcome-blind signature. The candidate-author session cannot sign it.

## Exact source lock

- Commit/tree: `38b35218e4d0f99621cec5a8a25a0147bb88c654` / `49f437c367cc45a90867418fcef77c9ff3614456`
- Index: `index_v1.json`, blob `f4f5007156cb71e7d54e99057037fb75d44f87c4`, 22,135 bytes, SHA-256 `f34c17b3dca9d609585e5fcc9d24c5433d4ad240ef91e5c2e9a48edee1e0959a`
- Dataset manifest: 61 exact CSV blobs, canonical SHA-256 `fe93857d5566fd63c9f681939fc1bfd347d6ae9496a1a01f6edd09428ce3c30a`
- Required candidate route: `https://raw.githubusercontent.com/asreview/synergy-dataset/38b35218e4d0f99621cec5a8a25a0147bb88c654/datasets/{review}/output/{review}.csv`
- Disallowed later route: `dc2dadf...`

## Rights and independence

The exact snapshot has a root MIT license blob. Current repository metadata reports CC0 but is not bound to this historical commit. Neither substitutes for exact per-review CC-BY-4.0/CC0 adjudication. The custodian must sign the full path/blob manifest, per-review rights, no-route-switch condition, and independence from labels/outcomes.

Only then may one unchanged label-blind seven-review census run. Performance remains unauthorized until separate outcome and result custody exists.
