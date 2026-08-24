# P4 M6 source-provider successor V4 protocol

Frozen at `2026-08-23T15:52:09Z`, before any V4 metadata harvest. This lane
expands only the four M6 article-to-code-release source cells. It cannot alter
the V3 terminal `P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK` or any earlier
identity.

The bounded source is the first 200 unique JOSS publication DOIs returned by
one frozen Crossref query, ordered by publication date. A strict candidate is
one JOSS DOI plus one repository concept, not a search hit, paper page,
release, tag, asset, file, version, commit, fork, mirror or API response. The
JOSS page must expose its labelled GitHub repository relation; the repository
must have a non-draft latest release whose tag resolves to an immutable commit;
and the licence at that exact tag must have an accepted SPDX identifier and
blob SHA. The HTTPS release tarball is the transport identity.

Domain assignment reuses the V3 lexicon without alteration. A tie or zero match
is `CANNOT_CHECK`, and assignment is development classification rather than
scientific adjudication. JOSS/GitHub is one provider family regardless of the
number of papers, organizations, repositories or releases. It is source-family
disjoint from Figshare, but author-lineage and exact paper-to-release version
alignment remain unresolved unless explicitly asserted.

The existing per-cell quota remains 24 primary, 8 source-family-disjoint
replication and 16 reserve units (48 total), with no pooling. Metadata-qualified
candidates are not natural pairs: same-claim preservation, the single
information-coordinate intervention, author-lineage independence and material
resolvability still require outcome-blind external adjudication. No protected
case, label or system outcome may be opened.
