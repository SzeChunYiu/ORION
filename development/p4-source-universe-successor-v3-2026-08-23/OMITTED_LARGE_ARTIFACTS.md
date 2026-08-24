# Large capture retention boundary

The isolated source lane verified its full 1,336-entry SHA-256 manifest before
integration. To avoid adding reproducible public transport payloads to the
repository, this bounded packet omits:

- `HARVEST_BUNDLE_V1.json`: 64,772,320 bytes, SHA-256
  `4ceafd8ba92b6d154aef45010856236fd824b75b31d43be802846b4f293e9af0`;
- `CANDIDATES_V1.jsonl`: 2,371 rows, SHA-256
  `612f7f00460af0f198dc5d160e979ac929c5bbdee45cf0b8ec11b5fea6ed35b5`;
- provider response bodies and the raw response index, all covered by the
  verified source-lane manifest and summarized by the retained protocol,
  provenance, transport audit, cell counts and verification receipt.

No protected case, label or system outcome is contained in the omitted files.
They are public metadata/transport captures and do not grant scientific
authority. The retained scripts and protocol specify the bounded replay, but
provider recovery and rate limits may change transport completion on a later
date.
