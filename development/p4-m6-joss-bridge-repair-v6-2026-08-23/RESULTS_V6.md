# P4 M6 JOSS same-identity provenance-bridge repair V6

**Terminal:** `P4_M6_JOSS_SAME_IDENTITY_CONTENT_ADDRESSED_BRIDGE_REPAIR_PARTIAL_17_OF_41__FINAL_EXACT_56_OF_80__AUTHOR_LINEAGE_AND_NATURAL_PAIR_CANNOT_CHECK`

**Preserved programme terminal:** `P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK`

The V6 development repair re-used exactly the 41 failed members of the frozen same-200 DOI frame. It added or replaced **zero** publication identities. Exact source-native archive bytes or qualified Software Heritage directory identities were required to equal an immutable Git commit snapshot, and accepted rights were required at both the exact archive and commit.

## Exact result

- Repaired: **17/41**; unresolved: **24/41**.
- Final exact JOSS bridges: **56/80** (V5 39 + V6 17).
- Repair methods: **12** exact normalized source-archive/GitHub-commit manifest equalities and **5** qualified-SWHID-path/Git-tree equalities.
- Content identities bound among the 41: **20**; three still fail another exact gate.
- New/replacement DOI identities: **0**; files, tags, commits, versions and requests counted as units: **0**.

## Domain accounting

| Domain | Frozen V4 qualified | V5 exact | V6 repair | Final exact | Remaining | V3 strict | Dedup union /48 | Replication /8 | Full cell |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| EARTH_ENVIRONMENT | 5 | 3 | 1 | 4 | 1 | 2 | 6/48 | 2/8 | FAIL |
| LIFE_BIOMEDICAL | 7 | 4 | 0 | 4 | 3 | 0 | 4/48 | 0/8 | FAIL |
| SCIENTIFIC_SOFTWARE | 62 | 30 | 15 | 45 | 17 | 6 | 51/48 | 6/8 | FAIL |
| PHYSICAL_ENGINEERING | 6 | 2 | 1 | 3 | 3 | 1 | 4/48 | 1/8 | FAIL |

Scientific Software now exceeds 48 total and 24 JOSS-primary candidates, but its unchanged Figshare replication arm is **6/8**, so its full cell still fails. Earth, Life and Physical remain below 48 and 8. Surplus never transfers across domains or gates.

## Remaining primary cause (mutually exclusive)

- `EXACT_ARCHIVE_SOFTWARE_RIGHTS_CANNOT_CHECK_OR_NOT_ACCEPTED`: **2**
- `FROZEN_ARCHIVE_DOI_IS_CONCEPT_OR_MUTABLE_LATEST_REDIRECT__EXACT_PUBLICATION_VERSION_CANNOT_CHECK`: **12**
- `SOURCE_ARCHIVE_TO_IMMUTABLE_REPOSITORY_COMMIT_CONTENT_IDENTITY_CANNOT_CHECK`: **10**

These primary counts sum to 24. Overlapping gate counts and every unresolved DOI are retained in `NEGATIVE_RESULT_LEDGER_V6.json`.

## Claim boundary

- Development transport evidence only; the disclosed pre-freeze feasibility probe forbids a confirmatory characterization.
- No global transport, provider-generality, natural-pair-readiness, author-lineage-independence, performance or superiority claim.
- Author-lineage adjudications, natural-pair adjudications and eligible natural pairs all remain **0**.
- No protected data, case labels or system outcomes were accessed.

## Next discriminator

For the same 24 frozen unresolved identities only, require a source-native exact version DOI rather than a mutable concept/latest redirect, an authenticated source-archive-to-immutable-commit content identity, and accepted exact archive and commit software rights. Separately, close the unchanged source-disjoint replication quotas with already-frozen nonreplacement provider identities before any external outcome-blind lineage/natural-pair adjudication; do not widen to global transport.
