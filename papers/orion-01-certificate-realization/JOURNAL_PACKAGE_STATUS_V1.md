# ORION-01 — Final journal package status V1

**Schema:** `ORION.PaperClosure.JournalPackageStatus.v1`
**Date:** 2026-08-28
**Publication lane:** `SPLIT_TWO_THEORY_PAPERS` (per `papers/publication_closure/wave2/WAVE2_DISPOSITION_V1.json`)
**scientific_authority_delta:** `NONE`

Nothing was built, compiled, or generated for this audit. No venue, licence, or cover letter
was invented. Every DONE below names an existing committed artifact; everything else is OPEN.

---

## 1. Status matrix

| Item | Paper A | Paper B |
|---|---|---|
| Exactly one canonical manuscript source | **DONE** | **DONE** |
| Current PDF exists | **OPEN** | **OPEN** |
| PDF current relative to source | **N/A** — no PDF | **N/A** — no PDF |
| Exact build command recorded | **OPEN** — no build path exists | **OPEN** — no build path exists |
| Primary venue | **DONE (recorded intent only)** | **DONE (recorded intent only)** |
| Fallback venue | **DONE (recorded intent only)** | **DONE (recorded intent only)** |
| Submission manifest with exact hashes | **PARTIAL** | **PARTIAL** |
| Cover letter | **OPEN** | **OPEN** |
| Data / code availability statement | **PARTIAL** | **PARTIAL** |
| Licence | **PARTIAL** | **PARTIAL** |

Overall: **NOT PACKAGE-READY.** Two of eleven rows per paper are unqualified DONE.

---

## 2. Row detail

### 2.1 Canonical manuscript source — DONE

| Paper | Path | Bytes | sha256 |
|---|---|---|---|
| A | `papers/orion-01-certificate-realization/theory-A-MANUSCRIPT_V2.md` | 12792 | `596217cfcf623b77ab77ecbd2ae0abbffdaf7ef2392cb2f8915ed790eec68365` |
| B | `papers/orion-01-certificate-realization/theory-B-MANUSCRIPT_V2.md` | 11400 | `66654d730332917bc5b8210bfd8610b8ad6f709cf87a746325c5a5a5a551ea04` |

Exactly one `_V2` manuscript per paper in the paper directory; no competing V1/V3. Both
on-disk hashes were recomputed for this audit and match the freeze receipt exactly.

Superseded copies exist under `papers/archive/2026-08-pre-unification/theory-A-multitag-constraint-rank/`
and `.../theory-B-certificate-complexity/`. They are archived, not competing sources, but a
submission manifest should name the canonical path explicitly so the distinction survives
outside this repository.

### 2.2 PDF — OPEN

No PDF exists for either paper. Verified by `find papers -iname "*.pdf"`, which returns PDFs
for ORION-12, -13, -15, -17, -18, -20, -21 and -25 (typically `manuscript/main.pdf`) and
**none** under `papers/orion-01-certificate-realization`. Scoped absence claim: the search
covered the whole `papers/` tree by extension, not by path guess.

The "PDF current relative to source" row is therefore not merely unverified — it is vacuous.

### 2.3 Build command — OPEN, and there is nothing to record

**There is no LaTeX source anywhere in ORION-01.** `find papers -iname "*.tex"` returns
section files for other papers only. The canonical sources are Markdown, and no
Markdown-to-PDF path (Pandoc template, Makefile, `COMPILE.md`, workflow) exists for this
paper.

So the honest entry is: **no build command exists to record.** Writing a plausible
`pandoc`/`pdflatex` invocation here would fabricate a path that has never been exercised.

For reference, the comparable in-repo pattern is `papers/orion-13-global-knowledge-portrait/`,
which carries `manuscript/sections/*.tex` plus a `journal_package/COMPILE.md`. Replicating
that structure is the work item; it has not been done.

### 2.4 Venue — DONE as recorded intent, with an authority caveat

Both manuscripts carry a Publication decision record:

| Paper | Primary | Fallback / stretch |
|---|---|---|
| A | `Quantum` | `PRX Quantum`, "only if independent editors view the alphabet-zero-sum/compiler connection as an exceptional cross-area insight" |
| B | `Quantum` | `PRX Quantum`, "only under an independently endorsed exceptional-connection case" |

Both stretch targets are explicitly conditioned on an external judgement that has not been
obtained. Both records also list external-only gates that remain open (donor PDF audit,
independent proof replay, figures, formatting, archive deposition).

**This is recorded intent, not submission readiness.** The freeze receipt records
`journal_authority: false`, `submission_authority: false`, `top_tier_ready: false`, and
`external_peer_review_claimed: false`. `WAVE2_DISPOSITION_V1.json` likewise carries
`submission_authority: false` and `top_tier_authority: false`. Do not let a filled venue row
read as clearance.

### 2.5 Submission manifest with exact hashes — PARTIAL

Exact sha256 + byte counts for all four canonical ORION-01 files exist in **two** committed
places:

1. `development/five-paper-hardening-r2-2026-08-25/R2_FILE_MANIFEST.json` — the five-paper R2
   hardening wave manifest (ORION-01 through ORION-04 plus siblings); contains `path`,
   `bytes`, `sha256` per file.
2. `papers/publication_closure/receipts/remaining11/ORION-01_SCIENCE_CONTENT_FREEZE_V1.json` —
   `manuscript_cuts[]` and `claim_ledgers[]`, same hashes.

What does **not** exist is a submission manifest scoped to ORION-01 covering the artifacts a
journal package needs: figures, verifier code, environment lock, expected result hashes,
evidence map, and the A1/B1 parent artifacts. The comparable in-repo target is
`papers/orion-13-global-knowledge-portrait/journal_package/MANIFEST.json` + `SHA256SUMS`.

### 2.6 Cover letter — OPEN

None exists for either paper. Verified by repository-wide `find` for `*COVER_LETTER*`, which
returns drafts under ORION-06, -12, -13, -14, -16, -17, -18 and several `papers/candidates/`
entries, and **nothing** for ORION-01.

### 2.7 Data / code availability — PARTIAL

`papers/FIVE_PAPER_DATA_CODE_AVAILABILITY_R2_2026-08-25.md` covers the R2 five-paper wave, and
`R2_FILE_MANIFEST.json` confirms ORION-01 is in that wave. It contains drafted Code
availability and Data availability paragraphs.

But it is explicitly headed **"Proposed manuscript statements"**, it names no paper
individually, and its own FAIR audit records "Findable: pending DOI/release metadata" and
"Accessible: final immutable archive pending". It lists a nine-item **"Archive inventory
required before submission"** — immutable source archive and commit id, environment lock,
one-command execution per verifier, expected result hashes, generated instances and figure
source data, machine-readable claim ledger and evidence map, licence statement, README
separating analytic authority from finite corroboration, and external replay instructions.
None of those nine is recorded as done for ORION-01.

Neither manuscript contains an availability statement in its own text.

### 2.8 Licence — PARTIAL

Repository root carries `LICENSE` and `LICENSE-PAPERS-CC-BY-4.0.txt`. Neither ORION-01
manuscript declares a licence, and the paper directory has no `LICENSE.md` (compare
`papers/orion-13-global-knowledge-portrait/journal_package/LICENSE.md`). Whether the
repository papers licence is intended to govern these two manuscripts is **not recorded
anywhere I could verify**, so this is not marked DONE.

---

## 3. Version currency — CANNOT_CHECK, with the reason

Path-scoped history for both manuscripts returns a single commit:

```
3a1a83178  papers(R0): ORION-01…25 namespace unification — 2734 renames, 1706 rebinds …
```

Re-run with `git log --follow` it returns two:

```
3a1a83178  papers(R0): … namespace unification …
3f363fb4b  docs(theory): harden five-paper publication wave R2
```

The mass-rename commit truncates history at the rename boundary, and `--follow` recovers only
one further step. **This is not sufficient to establish that any derived artifact is current
relative to source** — but the question is moot here, because §2.2 establishes there is no
derived artifact. Recording the limitation so a future pass does not mistake the short log for
a complete one.

---

## 4. Contingencies outside the package

Two package rows depend on artifacts outside this paper directory, and neither was executed in
this pass:

- **A1 parent** — `research/extensions/orion-qg/paper_a_a1_multitag_tare.py` and
  `PAPER_A_A1_MULTITAG_TARE_RESULTS_2026-08-24.json`. Carries `kappa_R6M = 2` (Paper A §8,
  Paper B §4).
- **B1 parent** — `research/extensions/orion-qg/paper_b_b1_rank_only_proof_gap.py` and
  `PAPER_B_B1_RANK_ONLY_PROOF_GAP_RESULTS_2026-08-24.json`, with
  `QG16_R6I_SUPPORT1_PHASE_RESULTS.json` as the apparent `kappa_R6I = 1` record.

Path existence was verified. **Sufficiency was not**: no parent was replayed, and no check was
made that these artifacts contain the complete upper theorem and necessity witness their
manuscripts attribute to them. Any submission manifest must bind these by hash, and the
independent-proof-replay gate both manuscripts already list as external-only remains open.

---

## 5. Blocking constraint on closing these rows

Rows 2.4, 2.7 and 2.8 would normally be closed by editing the manuscripts (adding an
availability statement, a licence line, a venue block). **The manuscripts are under a
committed content freeze** (`paper_content_frozen: true`) and are hash-pinned by
`ORION-01_SCIENCE_CONTENT_FREEZE_V1.json` and `WAVE2_DISPOSITION_V1.json`, both under
`papers/publication_closure/`. See `SIBLING_DECOUPLING_AUDIT_V1.md` §4 for the full pin list
and the governance conflict.

Rows that can be closed **without** touching frozen files, by adding new artifacts to this
directory: submission manifest (2.5), cover letter (2.6), paper-local licence file (2.8), and
a paper-local availability statement (2.7) — the last three as standalone package files rather
than manuscript text.

Rows that **cannot** be closed without resolving the freeze: any in-manuscript statement, and
the PDF/build path (2.2, 2.3), which additionally requires creating a manuscript source
pipeline that does not exist.
