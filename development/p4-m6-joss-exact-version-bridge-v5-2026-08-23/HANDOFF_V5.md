# P4 JOSS exact-version bridge V5 handoff

Write scope only: `/Users/billy/Documents/Codex/2026-08-23/can-x20/work/lane-handoffs/p4-joss-exact-version-bridge-v5`

No main checkout or manuscript file was edited. No pytest, repository CI, Git commit, merge, rebase or push was run.

## Terminals

- V5: `P4_M6_JOSS_ARCHIVE_EXACT_VERSION_BRIDGE_PARTIAL_39_OF_80__M6_CELL_FRAME_AUTHOR_LINEAGE_AND_NATURAL_PAIR_CANNOT_CHECK`
- Preserved programme terminal: `P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK`
- Recovered-dedup terminal: `P4_V3_M6_EXACT_CONCEPT_PUBLICATION_IDENTITIES_RECOVERED__V3_V5_CROSS_PROVIDER_DEDUP_COMPLETE_NO_OVERLAP_OBSERVED`

All V3/V4 terminals, provider subterminals and negative identities are retained in `RESULT_V5.json`.

## Exact counts

- Same frozen JOSS DOI identities: **200**; added/replacement DOI identities: **0**.
- Hash-recovered V3 M6 concept/publication pairs: **9/9** (Earth 2, Life 0, Software 6, Physical 1).
- V3/V5 DOI-key overlap: **0 publication, 0 archive-version, 0 archive-concept**.
- Labelled JOSS archive/repository relations: **200/200**; DataCite DOI records: **200/200**.
- One archive-explicit tag/commit for the same JOSS repository: **103/200**; immutable commits: **101/103**.
- Accepted archive SPDX rights: **179/200**; accepted licence at immutable commit: **83/101**.
- V4 provider-qualified concepts: **80**; complete exact bridge: **39/80**, each a unique DOI/repository concept.
- Exact bridge domains: Earth **3**, Life **4**, Software **30**, Physical **2**.
- Deduplicated V3-strict plus V5-exact cell totals: Earth **5/48**, Life **4/48**, Software **36/48**, Physical **3/48**.
- V3 provider-disjoint replication arms: **2/8, 0/8, 6/8, 1/8**. All four cells fail.
- Author-lineage independence adjudicated: **0**; natural pairs adjudicated/eligible: **0/0**.

## Principal blockers

1. **41/80** V4-qualified concepts still lack the complete exact archive/version/repository/tag/commit/rights chain.
2. **32/80** V4-qualified rows lack an archive-explicit tag/commit relation; one selected V4-qualified tag returned GitHub HTTP 404.
3. **12/80** lack one distinct archive-version/concept DOI relation; **3/80** lack accepted exact archive rights (overlapping failures).
4. Cell quotas remain far short; even exact Scientific Software is 36/48 and its Figshare replication side is 6/8.
5. Provider-family disjointness is not author-lineage independence; external outcome-blind lineage and natural-pair adjudication remain absent.
6. One same frozen Zenodo archive identity remains HTTP 410; the original 46 rate-limited identities were recovered by same-identity resume without replacing them.

## Integration candidates

Bounded artifacts suitable for review/copy are under 1 MB each. Start with:

- `RESULT_V5.json`
- `RESULTS_V5.md`
- `V3_M6_IDENTITY_RECOVERY_V5.json`
- `V3_V5_CROSS_PROVIDER_DEDUP_AUDIT_V5.json`
- `PROVIDER_FAMILY_AND_LINEAGE_AUDIT_V5.json`
- `CELL_COUNTS_V5.json`
- `NEGATIVE_RESULT_LEDGER_V5.{json,md}`
- `PROTOCOL_V5.json`, `PROTOCOL_FREEZE_RECEIPT_V5.json`
- `VERIFY_RECEIPT_V5.json`, `SHA256SUMS`

Row-level evidence is in `BRIDGE_ROWS_V5.jsonl`; releases, tags, commits, archive files and API responses remain evidence fields and never become additional n.
