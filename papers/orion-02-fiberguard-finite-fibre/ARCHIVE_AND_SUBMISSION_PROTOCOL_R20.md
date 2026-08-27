# ORION-02 R20 archive and submission protocol

Status:

`ARCHIVE_AND_SUBMISSION_NOT_AUTHORIZED`

## Permanent archive object

The archive release must be built from the clean current-main R20 branch after the strict internal release receipt and any externally requested claim narrowing. The release tree must include manuscript source/PDF, bibliography, claim/evidence/rights ledgers, exact theorem verifiers, all durable result receipts, reproduction instructions, external reports, software/data licences, and a machine-readable tree manifest.

The release builder must:

1. reject a dirty working tree;
2. record the exact Git commit and every Git blob;
3. construct the archive twice and require byte identity;
4. verify every manifest digest after unpacking into a fresh directory;
5. render and inspect every manuscript page;
6. preserve withdrawn and adverse terminals;
7. exclude credentials, private data, transient scheduler secrets, and unsupported positive prose;
8. publish under author-approved licences;
9. obtain a permanent DOI or equivalent content-addressed identifier;
10. write the DOI back only in a successor commit, avoiding self-reference.

## Exact submission object

The upload subject is a frozen successor of the permanent archive. It must bind:

- venue and article type;
- author order, affiliations, ORCID and corresponding author;
- title, abstract, keywords and subject classifications;
- manuscript PDF/source;
- supplementary source/result bundle;
- cover letter and significance statement where required;
- funding, contributions and conflicts;
- code/data availability and rights language;
- suggested/excluded reviewers if required;
- exact byte digests for every uploaded object.

## Portal execution

Before final submission, the author must approve the compiled portal preview, not merely local source. The portal receipt must record submission identifier, timestamp, venue, article type, uploaded filenames, byte sizes, digests where available, and preview approval. Any portal conversion that changes equations, references, figures, page order or supplement boundaries is a disagreement terminal.

## Allowed terminals

- `ORION02_R20_ARCHIVE_PASS__SUBMISSION_OPEN`;
- `ORION02_R20_PORTAL_PREVIEW_PASS__FINAL_AUTHOR_APPROVAL_OPEN`;
- `ORION02_R20_SUBMISSION_RECEIPT_BOUND`;
- `CANNOT_CHECK_DATA_RIGHTS`;
- `CANNOT_CHECK_AUTHOR_METADATA`;
- `PORTAL_PREVIEW_DISAGREEMENT`;
- `SUBMISSION_NOT_AUTHORIZED`.

No automation may convert an open author or legal field into a positive terminal.
