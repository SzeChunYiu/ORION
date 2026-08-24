# P2 V15 handoff

- Positive: GitHub-valid signed commit `38b35218...` -> tree `49f437c...` -> exact index blob `f4f5007...`; provider tag `metadata-v1-final` targets the commit.
- State expansion: complete non-truncated tree exposes 61 exact dataset CSV blobs; manifest SHA-256 `fe93857d5566fd63c9f681939fc1bfd347d6ae9496a1a01f6edd09428ce3c30a`.
- Preserved adverse: V14 mismatch/terminal unchanged; later `dc2dadf...` never substituted.
- Implementation correction: V15 froze the candidate template incorrectly; it was never executed. V15B preserves the error and restores immutable V14's `/output/{review}.csv` template for successor use only.
- Custody/rights: exact root license is MIT; current metadata CC0 is not snapshot-bound; per-review CC-BY/CC0 remains unsigned. Index attestation 404. Independent source custody false.
- Stop: 0 index parses, 0 CSV requests/censuses, 0 labels/models/metrics, no pytest/CI.
- Next: external outcome-blind custodian signs `INDEPENDENT_SOURCE_CUSTODY_REQUEST_V15.json`; only then run one unchanged label-blind census.
