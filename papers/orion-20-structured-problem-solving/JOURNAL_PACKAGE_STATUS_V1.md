# ORION-20 journal fit and package status V1

```text
scientific_authority_delta = NONE
assessed_at                = 2026-08-28
lane                       = FORMAL_OCME_THEORY_AND_MEASUREMENT_CONTRACT
overall                    = NOT_SUBMISSION_READY
```

Nothing here is marked DONE on the strength of a plan. No PDF was built, no
venue invented, no licence or cover letter authored. Where an action is
required, the exact command is recorded rather than run.

The repository's own record already agrees with this verdict:
`papers/publication_closure/receipts/remaining11/ORION-20_SCIENCE_FREEZE_V1.json`
carries `"journal_authority": false` and `"submission_authority": false`,
with terminal `ORION_20_BOUNDED_OCME_SCIENCE_FROZEN__NATIVE_PROMOTION_PENDING`.

---

## 1. Status board

| # | Item | Status | Artifact / evidence |
|---|---|---|---|
| 1 | Exactly one canonical manuscript source | **OPEN** | Four in-directory surfaces plus one divergent out-of-directory copy — §2 |
| 2 | Current PDF exists | **DONE (exists)** | `manuscript/main.pdf`, `successor/P10_U_MANUSCRIPT.pdf` |
| 3 | PDF current relative to its source | **OPEN** | Renders none of the five formal objects; now also behind sources — §3 |
| 4 | Defensible primary venue | **OPEN** | No venue named in any committed artifact — §4 |
| 5 | Fallback venue | **OPEN** | §4 |
| 6 | Submission manifest with exact hashes | **PARTIAL → OPEN** | `SHA256SUMS` exists and verified 50/50 before this pass; now invalidated — §5 |
| 7 | Cover letter | **OPEN** | Absent; `find` over the paper directory for `*COVER*` returns 0 |
| 8 | Data / code availability statement | **OPEN** | Absent; no availability statement in any manuscript surface — §6 |
| 9 | Licence | **PARTIAL** | Repo-level `LICENSE-PAPERS-CC-BY-4.0.txt` (CC BY 4.0) exists; not referenced from the paper or its manuscript — §6 |
| 10 | Permanent archive / DOI | **OPEN** | No DOI, Zenodo record, or archive artifact anywhere in the paper directory |
| 11 | Bibliography fit for a formal venue | **OPEN** | 4 entries, all `@misc` arXiv preprints, 0 DOIs — §6 |
| 12 | Author / affiliation block | **OPEN** | `\author{ORION Paper X Ultimate-Successor Working Manuscript}` is a placeholder, not an author |

---

## 2. Canonical manuscript source — OPEN

There is **not** exactly one. Four surfaces inside the paper directory each
carry manuscript-level content:

| Surface | Role | Notes |
|---|---|---|
| `manuscript/main.tex` + `manuscript/sections/*.tex` (18 files) | LaTeX build target | Treated as canonical by this pass; the only surface edited |
| `successor/P10_U_MANUSCRIPT.tex` | Monolithic LaTeX | Renders the same document; `diff` against the concatenated section files reports **331** differing lines |
| `TOP_TIER_DYNAMIC_EPISTEMIC_MANUSCRIPT_V1.md` | Markdown manuscript | **Sole carrier** of `ORION-20-T1..T5` and of the `P10_FULL_FROZEN_DONOR_EVALUATOR_INPUTS_ABSENT` terminal |
| `top_tier/P10_OCME_MANUSCRIPT_ADDENDUM_V1.md` | Markdown addendum | Declares it "supersedes only the outcome/status layer of `successor/P10_U_MANUSCRIPT.tex`" |

Plus one **divergent copy outside the paper directory**:
`papers/candidates/paper-10-structured-problem-solving/successor/P10_U_MANUSCRIPT.tex`
— `diff -rq` reports it **differs** from the in-directory copy of the same
filename. It is out of this pass's write scope and was not touched.

**Consequence.** A submission cannot be assembled until one source is
declared canonical and the others are either deleted, redirected, or
explicitly reclassified as records rather than manuscripts. The formal
content the disposition assigns to this paper currently lives in a Markdown
file that no PDF renders.

## 3. PDF currency — OPEN

Both PDFs exist and both hash-verified against `SHA256SUMS` before this
pass. Currency was assessed by content, which is decisive and avoids the
git-timestamp ambiguity (`manuscript/main.pdf` was last touched by a CI
rebind commit *after* the sources' last commit, so timestamps alone prove
nothing).

*[verified]* Extracted text of `manuscript/main.pdf` (16,651 characters)
contains the following occurrence counts:

| Term | `affine` | `AND2` | `SQUARE` | `decidab` | `minimality` | `donor frontier` | `T1` |
|---|---|---|---|---|---|---|---|
| Count | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

`successor/P10_U_MANUSCRIPT.pdf` renders the same title and abstract.

The PDF is not empty of OCME language: `OCME` is present and `closure`
occurs **15** times, because it renders the Stage-C gate *specification*
prose. What it does not contain is the technical content. **Relative to the
Wave-2 definition of the paper — "the finite closure, exhaustive-search
dominance, certified expansion, primitive-minimality definitions, and exact
input contract form the current paper" — the built PDF carries none of the
theorem statements, neither finite study, and none of the five objects'
technical vocabulary.** It renders the prospective empirical programme
instead. This is corroborated by
`TOP_TIER_PROMOTION_V1.md`, whose gate box "manuscript/result binding
updated to include generated OCME and all surviving negatives" is
**unchecked**.

Additionally, after this pass's edits (see
[`MANUSCRIPT_SCOPE_AUDIT_V1.md`](MANUSCRIPT_SCOPE_AUDIT_V1.md) §5), the PDF
is behind its sources: title, abstract, and three sections changed, and one
new section file was added.

**Build command — recorded, NOT run.** `main.tex` uses `\bibliography`, so a
single pass is insufficient:

```sh
cd papers/orion-20-structured-problem-solving/manuscript
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

## 4. Venue — OPEN

**No venue is named in any committed artifact.** The disposition's
`publication_lane` field is a lane label, not a venue; the science freeze
sets `journal_authority: false`.

*The following is this auditor's reasoning, not a decision, and not DONE.*
A paper whose established content is a closure formalism, a definition of
certified expansion with a macro-rejection lemma, a minimality definition,
and an exact measurement contract — with **no** empirical result — fits the
formal-methods / knowledge-representation literature rather than an
empirical ML venue, since every empirical endpoint is `CANNOT_CHECK`. The
choice cannot be made responsibly until item 1 (canonical source) and the
audit's F-1 (theorem statements that do not match their proofs) are
resolved, because the set of theorems the paper actually claims is not
currently well defined.

## 5. Submission manifest — PARTIAL, now invalidated

`SHA256SUMS` covers **50** of the **52** files that were present in the directory before this pass. The two
uncovered files are `SHA256SUMS` itself and `CONTENT_MANIFEST_V1.json`
(which binds file paths and roles, not hashes). Before any edit in this
work window, `shasum -a 256 -c SHA256SUMS` reported **50 OK, 0 failures**.

This pass's edits invalidate these entries:

- `manuscript/main.tex`
- `manuscript/sections/02-nearest-work-pressure.tex`
- `manuscript/sections/11-primary-hypotheses.tex`
- `manuscript/sections/16-claim-ladder-and-status.tex`

and add one file that is not covered at all:

- `manuscript/sections/00-scope-and-status.tex`

Nine new audit-surface files are likewise uncovered:
`THEOREM_PROOF_AUDIT_V1.md`, `MANUSCRIPT_SCOPE_AUDIT_V1.md`,
`JOURNAL_PACKAGE_STATUS_V1.md`, and the whole new **`audit/`** directory
(`AUDIT_A1_FINITE_CLOSURE_V1.md` through `AUDIT_A6_COVERAGE_AND_LIMITS_V1.md`,
six files). The `audit/` directory must not be missed at regeneration.

**Deliberately not regenerated.** Silently rewriting an integrity manifest
after editing the files it protects would destroy the only signal that the
files changed. Regeneration is a decision for the claim authority.

**Regeneration command — recorded, NOT run** (from the repository root, and
only after the PDF is rebuilt so its hash is captured too):

The committed manifest is sorted by **hash**, not by path, and ends with a
trailing newline. A path-sorted regeneration would reformat all 50 lines and
destroy the diff. The command below preserves the existing format:

```sh
cd /path/to/ORION
find papers/orion-20-structured-problem-solving -type f \
  ! -name SHA256SUMS ! -name CONTENT_MANIFEST_V1.json -print0 \
  | xargs -0 shasum -a 256 | sort \
  > papers/orion-20-structured-problem-solving/SHA256SUMS
```

*[verified]* Run against the current tree this command reproduces **46 of
the 50** committed lines byte-identically; the four that differ are exactly
the four files this pass modified.

`CONTENT_MANIFEST_V1.json` also needs its `bound_files` list extended with
the new audit and section files, and its `subject_commit` refreshed.

## 6. Licence, availability, bibliography

**Licence — PARTIAL.** `LICENSE-PAPERS-CC-BY-4.0.txt` (Creative Commons
Attribution 4.0 International, 396 lines) and `LICENSE` (202 lines) exist at
the repository root. Neither is referenced from the paper directory, the
manuscript, or `README.md`. A manuscript-level licence statement is OPEN. No
licence was authored by this pass.

**Data/code availability — OPEN.** No availability statement exists in any
manuscript surface (`grep -rn 'availability'` over the paper directory
returns only the native-Lean coverage fractions, not a statement). The
material a statement would have to point at does exist and is unusually
well specified: `protocol/P10_DOMAIN_SOURCE_FREEZE_V1.json` with checker,
the `top_tier/` runners and independent checkers, the frozen case files, and
`research/orion-epistemic-state-v1/results/P10-DES-01/`. Writing the
statement is a separate authored artifact and was not invented here.

**Bibliography — OPEN.** `manuscript/bibliography.bib` holds **4** entries
(`alphaevolve2025`, `codeevolve2025`, `lamp2026`, `grind2026`), all
`@misc` arXiv preprints with `howpublished` fields and **zero** DOIs. All
four are cited; no uncited entries and no undefined citations. Four
preprint references is thin for a formal paper at any venue, and the
project's own external-novelty record is
`INACCESSIBLE_WORK_MAY_ABSORB_CLAIM` with 75/75 atoms `CANNOT_CHECK`, so a
literature-saturation pass is a genuine prerequisite rather than a
formality. `TOP_TIER_PROMOTION_V1.md` lists "immediate pre-submission
theorem-proving/synthesis/evolutionary literature saturation" as an
unchecked gate box.

---

## 7. Blocking order

1. Declare one canonical manuscript source and resolve the divergent copy at
   `papers/candidates/paper-10-structured-problem-solving/` (item 1).
2. Resolve audit finding **F-1** — decide which theorem set the paper
   claims, since three of the five headline statements have no proof
   ([`THEOREM_PROOF_AUDIT_V1.md`](THEOREM_PROOF_AUDIT_V1.md)).
3. Bring the formal content into the canonical source (items 1, 3).
4. Rebuild the PDF; then regenerate `SHA256SUMS` and
   `CONTENT_MANIFEST_V1.json` (items 3, 6).
5. Only then: venue, cover letter, availability statement, licence
   statement, archive DOI (items 4, 5, 7, 8, 9, 10).
