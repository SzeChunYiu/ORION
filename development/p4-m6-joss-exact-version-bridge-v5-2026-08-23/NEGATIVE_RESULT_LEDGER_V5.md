# P4 JOSS exact-version bridge V5 negative-result ledger

**Preserved programme terminal:** `P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK`

Every failure retains cause, observed result, residual and next discriminator. No null, CANNOT_CHECK or failed V4 identity is overwritten.

## 1. `V3_M6_OMITTED_IDENTITY_PAYLOAD`

**Cause.** The bounded integrated V3 packet omitted the 2,371-row candidate payload, so V4 could not compare nine M6 concepts across providers.

**Observed.** The original handoff still held the candidate JSONL under the recorded SHA-256; 9/9 exact reported M6 rows were recovered (Earth 2, Software 6, Physical 1), and all nine concept/publication pairs are unique. No V3/V5 publication, version DOI or concept DOI overlap was observed.

**Residual.** Recovery licenses only exact identity deduplication; V3 author-lineage and natural-pair status remain CANNOT_CHECK.

**Next discriminator.** Use the recovered bounded nine-row identity packet for future source-frame dedup; never treat an omitted payload as zero overlap again.

## 2. `JOSS_ARCHIVE_TO_REPOSITORY_TAG_RELATION`

**Cause.** An exact JOSS archive DOI does not automatically state a repository tag or commit. Only archive metadata with an explicit GitHub tree/release/commit URL was accepted.

**Observed.** 103/200 had one archive-explicit tag/commit identity matching the JOSS repository; among the 80 V4 provider-qualified rows, 48 did.

**Residual.** Rows without an explicit archive-to-tag/commit relation remain CANNOT_CHECK; matching version strings or dates were not substituted.

**Next discriminator.** For the same failed DOI identities only, pre-freeze a source-native archive provenance or Software Heritage origin/revision route; add no replacement papers.

## 3. `ARCHIVE_TAG_TO_IMMUTABLE_COMMIT`

**Cause.** Two archive-explicit tag candidates returned GitHub ref HTTP 404; one lies inside the V4-qualified frame.

**Observed.** 101/103 selected identities resolved to 40-hex commits; 47/48 selected V4-qualified identities resolved.

**Residual.** A named but unresolved tag is not an immutable version relation and contributes zero bridge candidates.

**Next discriminator.** Resolve the same tag identity through source-native release metadata or an immutable Software Heritage revision, preserving the HTTP-404 evidence.

## 4. `ARCHIVE_VERSION_CONCEPT_IDENTITY`

**Cause.** Some DOI registrations omit, self-reference or ambiguously encode the distinct concept DOI for the archived version.

**Observed.** 165/200 expose exactly one distinct DOI IsVersionOf relation; 68/80 V4-qualified rows pass this gate.

**Residual.** A labelled archive DOI without a distinct version-to-concept relation remains insufficient for cross-version concept control.

**Next discriminator.** Query only the same archive identity at its source-native version endpoint under a new freeze; do not infer concept identity from DOI prefix or filename.

## 5. `EXACT_ARCHIVE_AND_COMMIT_RIGHTS`

**Cause.** Generic copyright, missing rights, nonaccepted licences and NOASSERTION are not hand-mapped to accepted software rights.

**Observed.** 179/200 have at least one accepted DOI-registered SPDX licence; 83/101 resolved commits have an accepted SPDX licence after syntax-only canonicalization. All 39 exact bridge passes satisfy both gates.

**Residual.** Failed rights rows contribute zero exact bridge candidates; one exact candidate has no Zenodo-native licence field but has matching exact DataCite BSD-3-Clause registration and commit licence.

**Next discriminator.** For failed identities, bind exact source-native version rights plus immutable-commit rights; do not infer from the default branch or repository description.

## 6. `V4_FAILED_IDENTITIES_NOT_REPLACED`

**Cause.** Nine V4 JOSS relation failures and later repository changes cannot be converted into new V4 units by re-reading mutable pages.

**Observed.** V5 retains all 200 DOI identities but requires the V4 provider-qualified predecessor and unchanged V4 repository/domain identity; exactly 39/80 pass the complete bridge and no V4-failed identity is promoted.

**Residual.** 41 V4-qualified rows remain exact-version bridge failures; the other 120 remain under their original V4 failures.

**Next discriminator.** Repair only under same-identity frozen provenance routes; never replace a failed DOI with a new page or count a changed repository as continuity.

## 7. `M6_EXACT_CELL_FRAME_SHORTFALL`

**Cause.** Exact version bridging reduces the V4 80 provider-qualified concepts to 39, while V3 contributes only nine predecessor-strict Figshare metadata concepts.

**Observed.** Deduplicated V3-strict plus V5-exact public-source candidate totals are Earth 5/48, Life 4/48, Software 36/48 and Physical 3/48. V3 disjoint replication counts are 2/8, 0/8, 6/8 and 1/8.

**Residual.** No M6 domain passes total, primary and source-disjoint replication gates; surplus in Software or another cell cannot compensate.

**Next discriminator.** After same-identity bridge repair, freeze non-GitHub domain-specific publication-linked release providers; Software still needs at least two additional disjoint-provider concepts even if its V4 bridge expands.

## 8. `PROVIDER_FAMILY_VS_AUTHOR_LINEAGE`

**Cause.** Different repositories/archive hosts establish a transport-source distinction, not independent authors, independent scientific claims or independent statistical units.

**Observed.** All 39 exact bridges use JOSS+GitHub+Zenodo and are structurally provider-family disjoint from the nine V3 Figshare identities; externally adjudicated author-lineage independence remains 0.

**Residual.** Provider-family disjointness cannot license lineage independence, same-claim preservation or natural-pair eligibility.

**Next discriminator.** Freeze an outcome-blind external lineage and natural-pair adjudication packet before any case label or system outcome.

## 9. `NATURAL_PAIR_ADJUDICATION`

**Cause.** Public metadata does not adjudicate same target claim, one-coordinate information-state change, material resolvability or outcome protection.

**Observed.** 0 author-lineage decisions, 0 natural-pair adjudications and 0 eligible natural pairs.

**Residual.** All 39 exact bridges remain transport candidates only. P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK is preserved.

**Next discriminator.** Commission the frozen outcome-blind external panel only after the source cells pass identity, relation, rights, dedup, lineage and quota gates.

## 10. `SOURCE_NATIVE_ARCHIVE_TRANSPORT`

**Cause.** The first Zenodo wave hit HTTP 429 for 46 identities and HTTP 410 for one.

**Observed.** A same-identity sequential resume recovered all 46 rate-limited records; DOI 10.5281/zenodo.20816805 remains HTTP 410. Original failures are retained, and no DOI was added or replaced.

**Residual.** The one withdrawn/gone source-native archive remains CANNOT_CHECK and is not among the 39 exact bridge passes.

**Next discriminator.** Preserve the 410 and use only an immutable source-native tombstone or Software Heritage identity for that same DOI under a new freeze.

