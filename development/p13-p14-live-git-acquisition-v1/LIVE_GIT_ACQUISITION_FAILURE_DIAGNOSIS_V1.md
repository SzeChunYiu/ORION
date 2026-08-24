# P13+P14 live-Git acquisition V1 adverse diagnosis

## Result of record

The frozen V1 runner executed once from clean `main` at
`3d8c01662e64434c736e0179c58fb30469bf42f4`. Its immutable receipt is
`LIVE_GIT_ACQUISITION_RESULT_V1.json` (SHA-256
`63bf92b65f0bc78e1b2585f36cf59d0fcb129c2d9601a54d70832d7310693c0f`).
The result retained all 45 frozen rows:

| V1 state | Count | Interpretation |
|---|---:|---|
| `OBJECTIVE_MISMATCH` / `DIGEST_MISMATCH` | 31 | Git successfully read a license blob at the pinned commit, but its raw-byte SHA-256 differed from `evidence_fetch_sha256`. |
| `EXCLUDED_LICENSE_CANNOT_CHECK` | 14 | The frozen corpus had no admissible license verification; no Git acquisition was attempted. |
| `VERIFIED_OBJECT_FACTS` | 0 | No eligible row passed the V1 digest gate. |

The exact terminal is
`P13_P14_LIVE_GIT_ACQUISITION_MINIMUM_NOT_MET__CAMPAIGN_BLOCKED`.
It is adverse evidence and is not relabelled as missingness.

## What is established

For every one of the 31 eligible rows, the command receipt records a successful
fetch of the pinned commit, a successful raw license-blob read, the observed
blob-byte SHA-256, and post-observation `HEAD` equality. Zero of those 31
observed hashes equals the corpus field named `evidence_fetch_sha256`.
Therefore the V1 corpus hash field, as frozen, is incompatible with the raw Git
blob-byte comparison implemented by the V1 runner across the entire eligible
subset.

## What is not established

The committed corpus says its hashes came from a GitHub REST "raw response",
but it does not retain those response bytes, the exact media type, the complete
request, or a construction receipt. The historical byte representation that
produced each frozen hash therefore cannot be reconstructed from committed
evidence. The precise construction error is `CANNOT_CHECK`. In particular, the
receipt does **not** establish 31 independent upstream license changes and does
not establish that the license texts are invalid.

The mismatch gate stopped each eligible row before it could be admitted as a
verified acquisition. Direct-parent and committer-time stdout remain in command
receipts, but V1 does not expose those facts as admitted result fields after a
license mismatch. They must not be silently promoted from the blocked receipt.

## Non-retroactive repair boundary

V1 must remain immutable. A successor may repair the measurement contract only
as a new, outcome-informed version. It must:

1. distinguish the hash of an API response envelope from the hash of decoded
   license bytes;
2. bind the license path, raw Git blob SHA-1, and raw blob-byte SHA-256 at the
   pinned commit;
3. retain the construction request/media type and a byte-level receipt;
4. freeze the repaired corpus and runner before another campaign execution;
5. disclose that the amendment was designed after observing the V1 all-row
   mismatch, and keep the V1 receipt in every audit trail; and
6. continue to treat missing license, acquisition failure, independent
   adjudication and protected custody as `CANNOT_CHECK`.

No issue box is closed. No lifecycle/RCS comparator campaign ran. Scientific-
authority delta: **NONE**.
