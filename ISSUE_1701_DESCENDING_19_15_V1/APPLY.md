# Application contract

This packet is intended as the second commit on `shadow/issue1701-descending-closure-20260829`.

- expected live-main ancestor: `b8fd5d2ca8eb1f6547592893591ba3aa93bf96c8`
- expected parent commit: `7974125ff7c36b3827170f81f121d60fc07467eb`
- expected parent tree: `b20fd7d14356f57e0d561f73ea95429258089966`
- changes: additive directory `ISSUE_1701_DESCENDING_19_15_V1` only

The delivery bundle contains an exact object pack and a two-step patch reproducer. A target
repository must already contain the live-main ancestor. The installer refuses a base/tree
mismatch and does not update `main`.
