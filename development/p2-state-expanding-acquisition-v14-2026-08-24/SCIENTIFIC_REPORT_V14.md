# P2 state-expanding acquisition successor V14

## Question and boundary

V14 asks whether the exact repository commit/path frozen by V13 actually owns the separately frozen index identity. The mismatch was discovered before this packet was frozen, so the official gate is an explicitly post-discovery content-addressed reproduction and causal lineage diagnosis. It is not prospective, independent or performance evidence.

The gate made six online requests: commit metadata, exact root tree and raw index bytes for each of two commits. It parsed only GitHub commit/tree metadata. Each raw index body was hashed in memory, was never JSON-decoded and was not retained. There were zero review CSV requests, zero population censuses and zero label, class-count, model, ranking or metric operations.

## Exact causal result

The V13-frozen commit `38b35218...` resolves to root tree `49f437c...`. That tree binds `index_v1.json` to blob `f4f5007...`, 22,135 bytes. The raw path independently reproduces Git blob SHA-1 `f4f5007...` and SHA-256 `f34c17b...`.

V13 separately expected blob `ada2668...`, 23,118 bytes and SHA-256 `5d829c6...`. Those bytes are also real and reproducible, but their owner route is commit `dc2dadf...`, root tree `2173535...`. They do not belong to the frozen `38b35218...` commit/path.

Therefore the exact causal code is:

`FROZEN_INDEX_SHA_DOES_NOT_MATCH_PINNED_COMMIT_PATH`

The historical owner was not substituted. V14 stopped before index parsing, the seven-review census and every performance action.

## Widest defensible positive result

The negative acquisition result has been converted into a precise source-version theorem for this route: two individually valid Git lineages were incorrectly combined into one frozen tuple. The commit/path lineage and the expected-byte lineage are now separately content-addressed down to commit, root tree, Git blob SHA-1, byte count and SHA-256. This is sufficient to specify one minimal repair without changing the scientific selection or performance contract.

It does not establish that seven eligible reviews exist and does not support a claim that keywords improve screening.

## Efficient V15 repair

V15 preserves the source authority originally frozen by V13: repository `asreview/synergy-dataset`, commit `38b35218...`, its exact candidate-dataset template and root tree `49f437c...`. In a new protocol it binds the actually owned index tuple: blob `f4f5007...`, 22,135 bytes, SHA-256 `f34c17b...`. This changes no selection rule, u4 component, learner, balancer, fallback, cost accounting or V10 gate.

An independent source custodian must sign that coherent tuple and same-snapshot rights before the label-blind seven-review census. The later `dc2dadf...` index is provenance evidence only; no route switch is permitted after census begins. Outcome and result custody remain separately required before performance.

## Exact terminal

`P2_V14_FROZEN_INDEX_IDENTITY_MISMATCH__PINNED_COMMIT_PATH_RESOLVES_F4F5007_BLOB_SHA256_F34C17B3__EXPECTED_ADA2668_BLOB_SHA256_5D829C66_BELONGS_TO_DC2DADF__STOP_BEFORE_CENSUS_AND_PERFORMANCE`
