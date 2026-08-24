# P1 V2 negative-result ledger

Every item remains visible; no absence is converted into a negative.

## N01_HEADER_SCHEMA_DRIFT — REPAIRED_WITH_ADVERSE_PRESERVED

- **Result:** The 20 documented header names were followed by one unnamed terminal field, so the original exact-header gate failed.
- **Cause:** Pinned CSV serialization contains an undocumented trailing column.
- **Residual:** All 71,944 data rows had width 21 and the frozen Amendment B gateway required the terminal cell to be empty; zero nonempty terminal cells occurred.
- **Next discriminator:** On every future blob, refreeze and repeat the exact header plus uniformly-empty check before row semantics.

## N02_INVALID_RECORD_ID — EXCLUDED

- **Result:** 246 rows lacked a usable Record ID.
- **Cause:** Source identifier missing under frozen normalization.
- **Residual:** Never imputed from DOI, title or ordering.
- **Next discriminator:** Provider-issued corrected identifiers in a later pinned release.

## N03_MISSING_ENDPOINTS — CANNOT_CHECK

- **Result:** 2,683 rows lacked both endpoints; 2,504 lacked an original endpoint; 1,151 lacked a notice endpoint.
- **Cause:** The seven-field source metadata did not supply both source-native endpoints.
- **Residual:** No title, author, date or fuzzy relation inference was used.
- **Next discriminator:** An official provider-native endpoint relation or rights-owner attestation.

## N04_SELF_RELATIONS — CANNOT_CHECK

- **Result:** 14,144 explicit-both-endpoint row occurrences collapsed original and notice to the same source-declared identity.
- **Cause:** The endpoint fields do not identify two distinct artifacts after exact aliasing.
- **Residual:** They cannot support an original-notice pair.
- **Next discriminator:** A provider correction binding a distinct notice identifier.

## N05_DUPLICATE_RELATIONS — DEDUPLICATED

- **Result:** 198 later row occurrences repeated an already frozen relation key.
- **Cause:** Multiple source rows encode one exact directed identifier relation.
- **Residual:** Only one relation was counted; row multiplicity is not sample size.
- **Next discriminator:** None for census; retain component-level family grouping in any study.

## N06_IDENTIFIER_ALIAS_AMBIGUITY — CANNOT_CHECK

- **Result:** 302 unique relations and 406 connected components failed DOI-PMID alias consistency.
- **Cause:** A DOI co-occurred with multiple PMIDs or a PMID with multiple DOIs.
- **Residual:** No equivalence direction was guessed.
- **Next discriminator:** Official identifier resolution with immutable response receipts.

## N07_ORIGINAL_NOTICE_ROLE_COLLISION — CANNOT_CHECK

- **Result:** 838 unique relations were in role-collision components; 13,451 source components contained an identity used as both original and notice, including self/update chains.
- **Cause:** The same identifier occupies both endpoint roles somewhere in the visible relation graph.
- **Residual:** Connected families were not split to manufacture independence.
- **Next discriminator:** Provider-native version-chain semantics prospectively frozen before reclassification.

## N08_NO_BOTH_PMID — CANNOT_CHECK_BOUNDED_ROUTE

- **Result:** 20,110 otherwise admitted RW relations lacked PMIDs on both endpoints for the frozen batch reducer.
- **Cause:** The bounded Europe PMC idlist/core reducer was PMID-addressable only.
- **Residual:** DOI presence is preserved in the RW census; this is not absence from Europe PMC or a rights failure.
- **Next discriminator:** Prospectively freeze an official DOI-to-PMCID resolver and rerun only this residual.

## N09_EPMC_ALLOWLIST_SEARCH_ABSENCE — CANNOT_CHECK

- **Result:** 17,730 both-PMID relations lacked an allowlist search match on one or both endpoints.
- **Cause:** At least one endpoint was not returned under the frozen Europe PMC OA/PMC/license search predicate.
- **Residual:** No incompatible license or missing article was inferred.
- **Next discriminator:** Exact endpoint resolution plus article-specific rights metadata or permission.

## N10_TYPE_OTHER_OR_AMBIGUOUS — CANNOT_CHECK_TYPED_CELL

- **Result:** 11 exact-rights relations were outside the three frozen provider strata and 1 matched multiple strata.
- **Cause:** Provider publication-type metadata was absent/outside-band or nonunique.
- **Residual:** No nearest action or scientific terminal was imputed.
- **Next discriminator:** Owner-separated source-native type adjudication under a frozen mapping.

## N11_SCIENTIFIC_TERMINAL_GOLD — CANNOT_CHECK

- **Result:** 0 scientific terminal cells were assigned; 0 cases were adjudicated.
- **Cause:** Publication type and retraction metadata are not minimal scientific responsibility-to-authority gold.
- **Residual:** No case text, causal responsibility, author intent or action column was opened.
- **Next discriminator:** Rights-cleared case dossiers and sealed, owner-separated minimal-transition adjudication.

## N12_CONSTRUCT_AND_EFFECT — CANNOT_CHECK

- **Result:** 0 anti-leak candidate views, donor-complete arms, information-equivalent arms, model outputs, protected scores or effect estimates exist.
- **Cause:** This lane stops at source-universe feasibility.
- **Residual:** The V1 overall construct-validity terminal remains active.
- **Next discriminator:** Freeze and execute owner-separated construct validation on the three width-pass strata.

