# ORION-02 anonymity audit V4

## Review surfaces checked

- TMLR PDF;
- hand-written LaTeX source and bibliography;
- anonymous supplementary ZIP and all enclosed text/code/result projections;
- retained TMLR source ZIP and every decoded archive member;
- release manifests, integrity ledger, budget and manuscript-excellence records;
- PDF metadata and extracted text.

## Controls

- no author names, affiliations, emails, local paths or named repository links;
- no macOS, Linux, or Windows home-directory path in any package file or decoded ZIP payload;
- TMLR review mode retained;
- review PDF identifies only anonymous authors;
- no named project or owner token in the anonymous source/supplement;
- repository, commit, environment and implementation-digest fields removed from result projections;
- no link from the review package to a named preprint or repository;
- full provenance-bearing objects withheld until deanonymization;
- camera-ready placeholders are not treated as completed metadata.

The deterministic package builder enforces forbidden-token and local-path scans, including decoded ZIP payloads. ZIP contents are enumerated and bound by manifests. Anonymity is a review-package property, not a claim that public search could never infer project lineage from scientific content.

The identified arXiv PDF and source archive are public-route artifacts, not members of the TMLR anonymous upload set. TMLR permits an identified public preprint but requires the review submission itself to remain anonymous and not link to that version. The package builder verifies these route roles separately.
