# Operator filing runbook V1 — Tier-B board execution (SzeChunYiu/ORION-paper#78)

**Generated:** 2026-09-03 · **Repo main:** f509ff91c · **Audit base:** b2d875855
(byte-audit: all 11 terminal packages verify clean, 281/281 SHA256SUMS rows OK;
b2d875855→f509ff91c changed only P12 campaign code under `papers/top_tier/`, no
package bytes touched).

Every unticked actionable board box terminates in an operator-side portal
action — no submission-portal credentials exist on any repo machine. This
runbook makes the whole board executable in one short operator session: per
action, the exact package directory, the upload files, and the receipt to file.

## Universal pre-flight (before every upload)

```sh
cd papers/<paper>/submission/<package-dir> && shasum -a 256 -c SHA256SUMS
# require: every line OK; any FAIL/missing = stop, do not upload
```

**Author identity (recorded, `papers/AUTHOR_IDENTITY_V1.json` + orion-08
`HUMAN_INPUTS_REQUIRED.md` [x] rows):** Sze Chun Yiu · Stockholm University ·
sze-chun.yiu@fysik.su.se · no funding to declare · no competing interests ·
acknowledgements omitted unless mandatory.

## Filing actions (ordered: arXiv first where boxed so)

| # | Box | Paper | Route → portal | Upload (within package) | Primary SHA-256 |
|---|-----|-------|----------------|--------------------------|-----------------|
| 1 | 109 | orion-01 | arXiv quant-ph → arxiv.org/submit | `submission/tier-b-final-20260901/arxiv/manuscript.pdf` + `arxiv/source.zip` | pdf `48021079…bab0bf` |
| 2 | 109 | orion-05 | arXiv quant-ph → arxiv.org/submit | `submission/final-20260831/manuscript.pdf` + `arxiv-source.zip` | pdf `caf6d46a…6614f` |
| 3 | 123 | orion-02 | TMLR (OpenReview, double-blind) → openreview.net | `submission/tier-b-final-20260901/journal/manuscript.pdf` + `journal/source.zip` (7pp anonymous; per `VENUE_RESOLUTION.md` 2026-09-01) | pdf `f176ffc2…c7240` |
| 4 | 41 | orion-08 | TMLR (OpenReview) — see its own `submission/FILING_SURFACE.md` | `submission/tier-b-final-20260901/journal/` | pdf `eb966292…a17f4` |
| 5 | (V2) | orion-06 | TMLR: `submission_tmlr/` anonymous lane (`main.pdf` + `anonymous-source.zip` + `anonymous-review-supplement.zip`); arXiv route separately: `submission/publication-ready-20260831/arxiv/` (both current at #2179) | — | tmlr pdf `1affe0d3…38c04a` |
| 6 | (V1 addendum) | orion-07 | TMLR double-blind: `submission/publication-ready-20260831/journal/manuscript.pdf` + `journal/source.zip` (canonical identity, official tmlr assets in-zip); arXiv: `arxiv/` | — | journal pdf `d752ac98…fbe5a` |
| 7 | 53 | orion-09 | arXiv quant-ph first, then Quantum (IOP) — journal lane: `submission/publication-ready-20260831/journal/` (`QUANTUM_ARXIV_FILING.md`, `SUBMISSION_CHECKLIST.md`, review-materials.zip) | — | pdf `3d6cf7b6…de7ab` |
| 8 | 94 | orion-03 | JAR — current dual-route package `submission/tier-b-final-20260901/` (pipeline-closed 2026-09-01, #2128): `journal/manuscript.pdf` + `journal/source.zip` + `artifact.zip` + `COVER_LETTER.md`; not the older `journal_package_final/submission/` or `submission/README.md` lanes (hazard table) | pdf `ed34801f…31da1` |
| 9 | 63 | orion-12 | IP&M (Elsevier EM, via journal site) — `submission/publication-final-20260901/journal/`: `manuscript_anonymous.pdf` + `source_anonymous.zip` + `COVER_LETTER.md` + `ELSEVIER_AI_DECLARATION.txt` etc. | — | (verify against package sums) |
| 10 | 76 | orion-13 | F1000R brief report — `submission/publication-final-20260901/journal/`: `manuscript.docx` (+ `manuscript.pdf` reference) | — | (verify against package sums) |
| 11 | 75 | orion-13 | **BLOCKER:** mint archive DOI for instance data first — requires an archive account (Zenodo) the repo cannot create; `.zenodo.json` absent, no API creds | — | — |

orion-10 (box set complete) needs no portal action this session: terminal
`PUBLICATION_PACKAGE_COMPLETE__PORTAL_ACTIONS_ONLY` at
`submission/tier-b-final-20260901/` (31 rows verified).

## Do-not-file hazards (bytes preserved, marked in-tree)

| Path | Why |
|------|-----|
| `papers/orion-02-…/submission/superseded-paperc-quantum-package/` | a *different* manuscript (Paper C pipeline) |
| `papers/orion-07-…/submission_tmlr/` | superseded 2026-08-29 wrapper generation, three-question title — README in dir (2026-09-03) |
| `papers/orion-08-…/submission/superseded-tmlr-pandoc-lane/` | superseded pandoc lane (#2185) |
| `papers/orion-06-…/submission/publication-ready-20260831/journal/` | superseded for the TMLR route by `submission_tmlr/` (V2); `arxiv/` subpackage remains the arXiv surface |
| `papers/orion-03-…/journal_package_final/submission/` + `papers/orion-03-…/submission/README.md` lane | older JAR generations; current surface is `submission/tier-b-final-20260901/` (2026-09-02, #2128) |
| any `publication-ready-20260831/` of orion-02 | superseded snapshot (its own submission README table) |

## Per-portal human inputs (beyond identity block)

- **TMLR/OpenReview (02, 06, 07, 08):** OpenReview profile completeness,
  conflict declarations, action-editor suggestions, public-discussion opt-in;
  double-blind anonymity preserved (upload the anonymous lanes only).
- **arXiv (01, 05, 06, 07, 09):** category selection (quant-ph per boxes;
  orion-02 cs.AI + cs.LG cross-list; 07 cs.AI+cs.LG per manifest), licence
  choice (default arXiv non-exclusive), author-verified metadata.json per route.
- **Quantum (09):** referee suggestions per journal lane checklist.
- **JAR (03):** per `submission_checklist.md` in the package.
- **Elsevier IP&M (12):** CREDIT statement, AI-use declaration (file present),
  highlights, ORCID at profile level.
- **F1000R (13):** data-availability DOI (action 11 gates this), CC licence
  election, approved-screening status.

## Receipt protocol (box 133)

After each portal action lands: append `FILING_RECEIPT_<venue>_<yyyymmdd>.md`
to that paper's `submission/` tree (portal, UTC timestamp, portal submission
ID, uploaded file list with SHA-256s, operator confirmation line), then tick
the matching box on ORION-paper#78 with a one-line comment mirroring the
receipt path + submission ID. PR the receipt into SzeChunYiu/ORION (poll CI to
`conclusion=success` before squash-merge; no branch protection).
