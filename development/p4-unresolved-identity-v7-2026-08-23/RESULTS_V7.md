# P4 V7 Targeted Unresolved-Identity Result

## Outcome

- Frozen unresolved identities revisited: **24/24**
- New same-identity repairs: **14**
- Exact JOSS bridges after V7: **70/80**
- Remaining unresolved: **10**
- Replacement publications: **0**
- Files, versions, tags, commits, or requests counted as units: **0**
- Author-lineage adjudications: **0**
- Natural-pair adjudications / eligible pairs: **0 / 0**

## Scientific discriminator

V7 adds the exact Crossref-to-JOSS-review relation and uses the frozen JOSS version to select a unique publication-time child from provider version history. A positive row also requires an exact source-native tag resolved to a 40-hex commit, archive-authenticated content/origin identity (provider related identifier, SWH tree identity, normalized manifest equality, exact embedded revision, or exact release-asset byte equality), provider-bound checksums, and accepted rights at both archive and commit. Editorial assertion alone never closes the identity gate.

## Primary unresolved causes

- `ARCHIVE_TO_COMMIT_AUTHENTICATED_IDENTITY_CANNOT_CHECK`: **3**
- `EXACT_ARCHIVE_SOFTWARE_RIGHTS_CANNOT_CHECK_OR_NOT_ACCEPTED`: **2**
- `EXACT_ARCHIVE_VERSION_DOI_RELATION_CANNOT_CHECK`: **2**
- `EXACT_TAG_TO_IMMUTABLE_COMMIT_CANNOT_CHECK`: **3**

## Boundary

The packet is development transport evidence, not natural-pair or author-lineage adjudication. The programme terminal remains `P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK`.
