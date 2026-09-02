# Tier-B closure update — 2026-09-02 (ORION-09+10, issue #78)

Receipt for the post-package closure edits and rebind of
`submission/tier-b-final-20260901`. This file is provenance documentation of the
rebind; it is intentionally NOT a member of `SHA256SUMS` / `PACKAGE_MANIFEST.json`
payload, so the binding contract of the package is unchanged in shape.

## 1. What changed, mapped to the issue items

| Issue item | Disposition |
|---|---|
| Bare "9,547" count corrected to 9,546 distinct inputs / 9,547 comparison events | DONE — 4 sites: `sections/results.tex`, `sections/methods.tex`, `sections/discussion.tex` (in-matter), `generated_results_tables.tex`. Bound in both rebuilt `source.zip`s. |
| Induction written out fully in `supplement.tex` (base case + composition step + dead alternatives + why checked reductions license the global statement) | DONE — replaces the former 6-line summary with a 4-paragraph derivation grounded in the QG-7e / QG-7e-v2 / QG-7f receipts. Expand-only; no earlier claim weakened or widened. |
| Machine check of the composition step | DONE — `papers/orion-10-certified-static-forecasting/evidence/check_envelope_composition_v1.py` (stdlib-only). Verdict **PASS 19/19 checks, exit 0**. Receipt: `papers/orion-10-certified-static-forecasting/evidence/CHECK_ENVELOPE_COMPOSITION_RECEIPT_V1.json`. Checker + receipt + all five pinned artifacts are members of `journal/artifact.zip`, so the check re-runs from the artifact alone. |
| S-M3 significance paragraph (compilation vocabulary: theorem-warrant vs agreement-warrant vs structural-coverage-warrant; addresses `08_reviewer_2_contribution.md`) | DONE — new paragraph in `sections/discussion.tex` between the algorithm-selection and resource-estimation paragraphs. |
| Rebuild + byte-audit + rebind (PDFs, source.zips, artifact.zip, PACKAGE_MANIFEST, SHA256SUMS) | DONE — details in sections 2–4 below. |
| Submission-day literature refresh | NOT DONE (by design) — remains a separate pre-filing action; see `LITERATURE_AND_LINEAGE_REFRESH.md`. |
| Portal submission | HUMAN_FILING_ONLY — no automated filing attempted. |

Editorial verifier re-run after all edits:
`editorial/UNIFIED_PAPER_VERIFICATION.json` — 37 checks passed, 0 failed;
the refreshed JSON is included as the updated `artifact.zip` member.

## 2. Rebuild

- Host: `billy-old` (ssh), build tree `~/orion10-build-20260902/manuscript`,
  engine `tectonic` 0.15.0 at `/home/billy/.local/bin/tectonic` (not on the
  non-interactive PATH; exported per invocation).
- Commands: `tectonic main.tex`, `tectonic main-arxiv.tex`, `tectonic supplement.tex`.
- Build base: the working `manuscript/` tree with `main.tex` / `main-arxiv.tex`
  overwritten by the variants extracted from the previously bound `source.zip`s.
  Rationale: the packaged variants carry the Title Case submission title that
  every package authority (`TITLE_PAGE.md`, both `metadata.json`,
  `PACKAGE_MANIFEST.json`) records, and the arxiv variant carries
  `\date{31 August 2026}`; the working-tree mains differ only in title casing
  (and the arxiv date). Rebuilding from the packaged variants preserves the
  package's title authority instead of introducing a casing regression. The
  working-tree `.tex` mains remain as they were; the bound zips and PDFs are
  the authority.
- Page counts (zlib object-stream parse; `mdls`/`strings` cannot read these PDFs):
  journal main 9 pp (was 9), arxiv main 11 pp (was 11), supplement 11 pp
  (was 10; +1 page from the induction write-out, within the ±1 tolerance).
  `PACKAGE_MANIFEST.json` page fields (journal 9 / arxiv 11) therefore remain
  correct and were not edited.

## 3. New payload digests (all verified by `shasum -a 256 -c`, 31/31 OK, exit 0)

| File | Bytes | Pages | SHA-256 |
|---|---|---|---|
| `journal/manuscript.pdf` | 110,423 | 9 | `024dbb0cfbe74bbcfdad5813899f8d02ee1a85ef43a514403dae0ee388b8da95` |
| `arxiv/manuscript.pdf` | 109,116 | 11 | `d3ab53c229a62ec199aac5be7c079445b55606eaa12e09ca7dc307ae12df4f4a` |
| `journal/supplement.pdf` | 119,970 | 11 | `4dbf53f570e4fd1a05beee409b53b8747ed9666d825317b317c1ac24ded75fa5` |
| `arxiv/supplement.pdf` | 119,970 | 11 | `4dbf53f570e4fd1a05beee409b53b8747ed9666d825317b317c1ac24ded75fa5` |
| `journal/source.zip` | 60,805 | 18 members | `dadb003856babeff39a54d2f100f4275dc2b3573160213526fc7c5449365b599` |
| `arxiv/source.zip` | 59,279 | 17 members | `30bdf81194dc8a272eccc8b6cd8e671c195071e49d4bc225a2e23a452963427a` |
| `journal/artifact.zip` | 73,681 | 12 members | `8d10bbe46717d83d665ea82fbd77a734ef009fe0dc10feb28c3689b98908fd6d` |

`manuscript/main.pdf`, `manuscript/main-arxiv.pdf`, `manuscript/supplement.pdf`
in the paper tree carry the same bytes as their bound counterparts. Source zips
preserve the original member order and fixed `1980-01-01 00:00` timestamps.

## 4. artifact.zip member delta (7 → 12, additive)

Kept verbatim from the previous binding: all 7 existing members. Refreshed
in place: `papers/orion-10-certified-static-forecasting/editorial/UNIFIED_PAPER_VERIFICATION.json`
(37/37 verifier re-run). Added 5 members:

1. `papers/orion-10-certified-static-forecasting/evidence/check_envelope_composition_v1.py`
2. `papers/orion-10-certified-static-forecasting/evidence/CHECK_ENVELOPE_COMPOSITION_RECEIPT_V1.json`
3. `research/extensions/orion-qg/QG5_CERTIFIED_FORECAST_RESULTS.json`
4. `research/extensions/orion-qg/QG5B_EXACT_FORECASTER_RESULTS.json`
5. `research/extensions/orion-qg/QG7E_V2_PP_SINGLE_PINNER_RESULTS.json`

The checker pins the SHA-256 of all five artifacts it reads (QG-7e
`b452ac0a…`, QG-7e-v2 `c5368796…`, QG-7f `1caf27ed…`, QG-5 `f5ef5c75…`,
QG-5b `7701d4fb…`), so any drift in a supporting artifact fails the check.

`PACKAGE_MANIFEST.json` payload updated for exactly the 7 changed files above
(pre-state digests asserted before writing); `SHA256SUMS` recomputed for all 31
lines in the original order; only those 7 payload lines and the
`PACKAGE_MANIFEST.json` line changed.

## 5. Deliberate non-changes (scope discipline)

- `editorial/TIER_B_PACKAGE_VERIFICATION.json` left untouched: it is the
  historical receipt of the 2026-09-01 binding (its build tails describe the
  original latexmk builds) and its digests describe the pre-closure package
  this update supersedes.
- Abstract sentence "two alternative global proof links remain explicitly open"
  (both `metadata.json`s, packaged mains): one link is in fact refuted, not
  open. The wording is conservative (understates a negative result; no claim
  widening), and the supplement/discussion state the refutation precisely;
  editing the abstract was outside the assigned targeted edits.
- Top-level provenance docs `submission/COVER_LETTER.md` and
  `submission/DATA_AND_CODE_AVAILABILITY.md` (unbound, outside this package)
  still say "9,547 compared instances"; `submission/manuscript.pdf`
  (`cb10e5ae…`) is unbound legacy. All left as historical provenance.
- `submission/publication-ready-20260831/` (superseded package) untouched.

## 6. Still open

1. Submission-day literature refresh (separate pre-filing action, not executed).
2. Portal submission (Quantum; arXiv after acceptance per filing order) —
   HUMAN_FILING_ONLY.

## 7. Follow-up (same day, post-receipt): abstract evidence-status fix

Supersedes the first bullet of section 5 for the abstract sentence only. The
abstract's "while two alternative global proof links remain explicitly open."
misstated evidence status — the two-coordinate chain representation is REFUTED
(exact counterexample, QG-7f), only the single-pinner composition link remains
open. Fixed to "while one alternative global proof link remains explicitly
open, and a second route is refuted by an exact counterexample." in:
`manuscript/main.tex`, `manuscript/main-arxiv.tex`, and the `main.tex` members
of both `source.zip`s (packaged Title-Case variants), plus the `abstract`
field of `journal/metadata.json` and `arxiv/metadata.json` (exactly one
occurrence per file; zero occurrences of the old sentence remain). Mains
rebuilt on billy-old (tectonic, same build tree); page counts unchanged
(journal 9, arxiv 11); supplement and `artifact.zip` byte-identical
(editorial verifier re-run 37/37, output unchanged). Re-bound and re-verified:
`shasum -a 256 -c SHA256SUMS` from this directory — 31/31 OK, exit 0. New
digests: `journal/manuscript.pdf` 110,616 B
`72783f37542c383715e261deeeb5eb0fe07634037c4e6d1f52cb10082d4375cf`;
`arxiv/manuscript.pdf` 109,119 B
`06e280cc331f99179a745441e4b24a7dd8f735a6195ee7850c647305865e23cb`;
`journal/source.zip` 60,830 B
`01da53716ab9be4205d946d9231afb2bb3689b277ac64d8f87f0692bd1a05f90`;
`arxiv/source.zip` 59,303 B
`b96e9da4051b37a915ea01f79cda61bb0ab0892b783f655e326a77f58f3a640b`;
`journal/metadata.json` 2,372 B
`05c9cf7e1baa834d5345cf6c4daaa8ae0e4849999bbfb789c94ed52bf9dcda0e`;
`arxiv/metadata.json` 2,307 B
`28b66ae1d5af90f3c70ab7165bd97d8e5b6e30249ba1b1d3e5bfe429fd7ff4f8`.
Verification of the rendered PDFs is source-level plus deterministic compile
(the PDF text streams use subsetted font encodings, so raw text search is not
applicable to old or new sentence alike).
