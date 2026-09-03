# A5 Access Log and Exact Source/Rights Receipts — V1

Date: 2026-09-03. Scope: every network access executed for the P4/A5 external-evidence
programme is logged with purpose, rights basis, and byte-level binding. This file indexes
the receipt packages; the JSON/JSONL artifacts carry the evidence.

Interpretation boundary (all routes): harvests and byte bindings are PROSPECTIVE and
NON-AUTHORITATIVE. No route accesses external gold labels, protected ORION predictions,
or adjudicates case eligibility. Mechanism counts are harvest counts, not eligible-pair
counts. Nothing here grants scientific authority; adjudication happens later under the
governed pipeline.

## Route R1 — arXiv CC BY exact-version pool (V1, complete)

- Pool: `ARXIV_CC_BY_SOURCE_POOL_V1.jsonl` — 1536 CC BY 4.0 candidates, 384 per domain,
  sha256 `47dd24…d895`; binding record `ARXIV_CC_BY_SOURCE_POOL_BINDING_V1.json`
  (P4.NAT.AXIS.768.ARXIV_CC_BY_POOL_1536.V1, case_eligibility UNADJUDICATED_SOURCE_CANDIDATES_ONLY).
- Rights basis: exact-version CC BY 4.0 filter on `arXivRaw` license; attribution required;
  CC0 metadata per arXiv policy; CC BY does not clear third-party figures/publisher
  versions — case construction is text-only unless separately cleared. Official policy
  snapshots + receipt: `policy_snapshots/`, `OFFICIAL_ARXIV_POLICY_SNAPSHOT_RECEIPT_V1.json`.
- Immutability: bind only exact latest `vN` from the harvested OAI record; unversioned
  URLs forbidden (arXiv versions are permanent and citable).
- Access log: `ARXIV_CC_BY_POOL_HARVEST_LOG_V1.json` (OAI harvest), sample verification
  `ARXIV_CC_BY_LIVE_SAMPLE_RECEIPT_V1.json` (8/8 license+version verified live),
  preflight `ARXIV_CC_BY_FULLTEXT_LIVE_PREFLIGHT_V1.json` + script dir.

## Route R1 — arXiv full-text byte binding (V2, terminal)

- Executor: `arxiv-cc-by-fulltext-pool-binding-v2/bind_arxiv_cc_by_fulltext_pool_v2.py`
  (script sha256 `447cd7…8feb1`), LUNARC sbatch: probe 3569325; binding 3569822 (FAILED
  at 387 rows — `/home/scyiu` home quota exceeded, `Errno 122`); resubmitted 3570516
  after moving the byte store to
  `/projects/hep/fs9/users/scyiu/orion-a5-sources/arxiv-fulltext/pdf` (home `pdf` is a
  symlink to it; home tree freed 1.3 GB).
- Terminal state (run 2026-09-03T12:57:19Z→13:58:26Z, host lunarc-scyiu-sbatch):
  **bound_n 1531/1536** (EARTH_ENVIRONMENT 384, LIFE_BIOMEDICAL 382,
  PHYSICAL_ENGINEERING 382, SCIENTIFIC_SOFTWARE 383); resumed 387 previously-bound rows,
  newly bound 1144. Terminal marker:
  `…POOL_BINDING_INCOMPLETE__RESUME_REQUIRED` (bound_n != pool rows).
- `cannot_check_n = 5` — exact-version PDF URLs return HTTP 404 after 3 retries each:
  `1805.00393v4`, `1908.00285v3`, `2003.10750v3`, `1811.00003v2`, `1907.08612v2`.
  Spot-verified live 2026-09-03: two of the five return 404 while a prior version of
  the same paper returns 200 — genuine upstream absence, not a URL-construction defect.
  Resume cannot help these; they stay unbound and recorded.
- Preflight cross-check vs the durable preflight receipt (workflow artifact 9814382058):
  6/8 matched; 2 ids (`1801.00636v1`, `2103.11013v1`) fetched byte-different PDFs from
  the same exact-version URLs (pdf_sha256 drift at one character position each —
  verified char-level, not a display artifact). Provenance caveat: arXiv's permanence
  guarantee is identifier-level, not byte-level, for some PDFs; receipts keep the
  run-time sha and flag the drift.
- Append-only artifacts (sha256 in `BINDING_V2_SHA256SUMS`, transfer-verified):
  `BINDING_V2_RECEIPTS.jsonl` `cb3902…930`, `ACCESS_LOG_V2.jsonl` `c1c49f…e24`
  (a few marker rows appended after result-write, so it supersedes the in-JSON
  provenance hash `65fd13…b6`), `BINDING_V2_RESULT.json` `8378e2…7bae`,
  `RUN_STDOUT.log` `4d2778…1198`. 1159 access-log attempts, 6.5 GB PDF bytes on fs9,
  NOT committed. Network policy: concurrency 1, 3.1 s min interval, hosts
  arxiv.org/export.arxiv.org only, 64 MiB per-PDF cap, 3 retries.

## Route R2 — PMC OA linked records harvest (V1, complete)

- Executor `pmc-oa-linked-harvest-v1/harvest_pmc_oa_linked_v1.py`, run host
  billy-laptop-old, 2026-09-03T07:50:46Z→08:15:27Z, 906 HTTP requests, script sha256
  `337e26…e9ea`. Status PROSPECTIVE_HARVEST_EXECUTED.
- Mechanisms (harvest counts, NOT eligible-pair counts):
  - M3 protocol→results: 250 discovered/harvested; both-sides-with-licence 6, CC BY 4.0
    both sides 3.
  - M4 article→correction: 300 discovered/harvested; both-sides-with-licence 258,
    CC BY 4.0 both sides 203.
  - M8 article→licensed supplement: 26 scanned (from 2026-08-28), 14 articles with
    supplementary material, 20 supplement files hashed.
- Rights basis: per-record `ali:license_ref` from OAI-PMH; supplement files hashed
  individually; no content rights inferred from metadata alone. Policy snapshots
  (OAI Identify, ListSets head, NCBI eutils docs, PMC OA tool page; one upstream 404
  noted) verified by sha256 in `RESULT_V1.json` → `policy_snapshots/SNAPSHOT_MANIFEST.json`.
- Access log: `ACCESS_LOG_V1.jsonl` (completed run) + `ACCESS_LOG_V1.jsonl.attempt1`
  (first attempt, network-interrupted after snapshot fetch; snapshots retained from it).
- Network policy: concurrency 1, min interval 1.5 s, providers eutils/pmc.ncbi only.

## Route R3 — Zenodo related-data byte binding (V1, complete)

- Executor `zenodo-bytes-binding-v1/bind_zenodo_candidate_bytes_v1.py`, run host
  billy-laptop-old, 2026-09-03T07:44:03Z→08:04:14Z, 105 HTTP requests. Status
  PROSPECTIVE_BYTE_BINDING_EXECUTED.
- Input: `P4_ZENODO_RELATED_OBJECT_CANDIDATES_V2.jsonl` (173 rows, sha256
  `d6f767…1247`). Output: 44 records receipted, 58 files byte-bound (sha256 + provider
  MD5 cross-check, 58/58 match). Per-file byte cap 256 MiB; bytes stored outside the
  repository at `--bytes-dir` — NOT committed.
- Rights basis: Zenodo per-record license terms recorded per file; open-access records
  only; policy snapshot `zenodo_developers_api_2026-09-03.html` sha256-verified in
  `RESULT_V1.json`. Access log: `ACCESS_LOG_V1.jsonl`; receipts `BINDING_V1_RECEIPTS.jsonl`.
- Network policy: concurrency 1, min interval 2.5 s, hosts zenodo.org only.

## Commit policy

Only JSON/JSONL/MD/script artifacts and their `SHA256SUMS` are committed. No fetched
content bytes (PDFs, supplement files, Zenodo files) enter the repository; they remain
on the harvest hosts, referenced by sha256. Each subdirectory carries its own
`SHA256SUMS` binding every committed file.
