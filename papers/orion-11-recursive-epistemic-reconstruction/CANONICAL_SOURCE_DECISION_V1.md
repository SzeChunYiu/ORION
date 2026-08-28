# ORION-11 — canonical manuscript source decision V1

`scientific_authority_delta: NONE`

Records which manuscript source is canonical and which packages are superseded, so
that the historical package cannot be submitted by accident after the 2026-08-28
comparative-necessity retraction.

**No LaTeX or PDF build was run.** Disk headroom on this host is ~1.3 GiB and a TeX
build plus its sidecars is not a safe use of it. The exact build command is recorded
in §5 instead.

---

## 1. Decision

> **The single canonical manuscript source is `manuscript/main.tex`.**

Authority for this, not asserted but cited:

- `README.md` (§Manuscript): *"`manuscript/main.tex` is the canonical Paper-I working
  manuscript."*
- `journal_package/MANIFEST.json` → `required_files`: `manuscript/main.tex` carries
  `role: "manuscript-source"`. It is the only file in the manifest with that role.

`main.tex` `\input`s, in order: `generated/suite_facts`, `sections/01-foundations`,
`02-recursive-engine`, `02a-minimal-escalation-theory`, `03-reframe-reopen`,
`04-self-audit`, `05b-necessity-successor`, `05c-revision-responsibility-successor`,
`05a-methods`, `05-evaluation`, `06-related-work-boundary`,
`06b-successor-discovery-failure-interface`, `07-limitations`, `09-reproducibility`,
`10-ethics-safety-resources`, `08-conclusion`. Anything not reachable from that list
is not part of the canonical manuscript.

Two section files exist in the tree but are **not** `\input` by `main.tex` and are
therefore not canonical content: `sections/06-limitations.tex` and
`sections/06a-post-saturation-novelty-refresh.tex`.

## 2. Superseded and non-canonical packages — complete list

| # | Path | What it is | Status |
|---|---|---|---|
| 1 | `journal_package/manuscript.pdf` | 33-page independently inspected historical render. `sha256 06a60f0f6ec69bc142952b4fc9dc1030fcd0f80de41f941958debe375e6ea99e`, 468,355 bytes. MANIFEST role `historical-compiled-and-visually-reviewed-manuscript`. | **SUPERSEDED — must not be submitted.** `journal_package/MANIFEST.json`: `package_status: SUPERSEDED`, `current_submission_authorized: false`, `render_binding.binding_status: HISTORICAL_SUPERSEDED`, `current_revision_binding: false`. |
| 2 | `manuscript/main.pdf` | Working build of the canonical source. `sha256 f3c42ebe8085c85ef9d48d8380da5f6f4abedf93b5fa9d21a7a3cd92414d03e5`, 511,288 bytes. Tracked; last touched by commit `6d2d1699b` (2026-08-27). | **STALE as of 2026-08-28.** Predates the retraction edits to `main.tex`, `05b`, `07-limitations`, `08-conclusion`, `01-foundations` and `P1-T4`. It still shows the retracted comparative margin and must be rebuilt before any use. |
| 3 | `journal_package/RENDER_INPUT_CLOSURE.json` | The 31 pinned TeX inputs of the historical V3 render. | **HISTORICAL.** Pins a source state that no longer exists. |
| 4 | `journal_package/RENDER_CLOSURE_STATE.json` | Generator-derived current state; `state: SUPERSEDED`, 20 `drifted_inputs`. MANIFEST role `generator-derived-current-render-closure-state`. | **AUTHORITATIVE for render currency; needs regeneration.** All six files edited on 2026-08-28 were already in its `drifted_inputs` list, so the drift *set* is unchanged, but the input hashes are not. Regenerate; do not hand-edit. |
| 5 | `journal_package/SHA256SUMS` | Checksum inventory for the historical package. | **HISTORICAL.** Refresh only when a new package is actually built. |
| 6 | `successor/P1_U_MANUSCRIPT.tex` | *Not a version of this paper.* A distinct prospective successor manuscript, title "General Scientific Problem Reformulation Superiority", for an **unexecuted** study. Its own §"Current status" says it does not alter the predecessor result and does not assert that P1-U superiority has been observed. | **NOT A SUBMISSION CANDIDATE.** Prospective design document. Never build or submit as ORION-11. |
| 7 | `TOP_TIER_DYNAMIC_EPISTEMIC_MANUSCRIPT_V1.md` | 51-line positioning/abstract sketch. | **NOT A MANUSCRIPT SOURCE.** |
| 8 | `JAAMAS_INFORMATION_SHEET_V1.md` | Venue information sheet. | **COMPANION, not a manuscript.** Retraction applied 2026-08-28. |
| 9 | `results/figures/*.pdf` vs `manuscript/figures/*.pdf` | Two figure directories, both on `\graphicspath{{figures/}{../results/figures/}}`. | **`manuscript/figures/` wins** — it is searched first. `results/figures/` is the generator output directory and is the fallback. `P1-7_necessity_replication.pdf` exists only under `manuscript/figures/`. |

Also present and explicitly historical, listed so nothing is missed:
`evidence/CLAIM_LEDGER_V1.md` (`immutable-historical-v1-claim-ledger`),
`protocol/PROTOCOL_V1.json` (`historical-v1-frozen-protocol`),
`results/P1-T2_baseline_ablation_results.json` (`historical-v1-headline-table`),
`results/P1-T3_failure_taxonomy.json` (`historical-v1-failure-taxonomy`),
`results/campaign.stale-run.log`.

## 3. How a reader tells them apart

Four checks, in order of speed:

1. **Package status field.** Open `journal_package/MANIFEST.json`. If
   `package_status` is `SUPERSEDED` or `package_authority.current_submission_authorized`
   is `false`, nothing in `journal_package/` may be submitted. Both currently hold.
2. **Render currency.** Open `journal_package/RENDER_CLOSURE_STATE.json`. If
   `state` is `SUPERSEDED` or `drifted_inputs` is non-empty, the historical PDF is a
   render of inputs that have since changed. Currently `SUPERSEDED` with 20 drifted
   inputs.
3. **The abstract test — decisive after 2026-08-28.** The current source abstract
   states hidden-shift success `1.0000` and then explicitly withdraws the comparative
   margin. Any PDF whose abstract reads *"1.0000 versus 0.4938 and 0.4833 for the
   strongest assimilated parents"* is a **pre-retraction render** and is not
   submittable, whatever its filename. This is the single fastest discriminator and
   it works on a printed copy.
4. **Page count and hash.** The historical package PDF is 33 pages,
   `sha256 06a60f0f…`. `manuscript/main.pdf` is `sha256 f3c42ebe…`. Neither hash may
   appear on a submitted artefact until a fresh build replaces it.

## 3a. Working-tree hazard recorded on 2026-08-28

The R4 evidence package `experiments/r4-faithful-comparator-v1/` is **tracked at
`wave2/integration` HEAD** and its content there is byte-identical to PR #1603
(`git diff refs/rev/pr1603 HEAD -- <dir>` returns 0 lines). It is nevertheless
**absent from the working tree**: all seven files show as unstaged deletions and only
a stale `__pycache__/` directory remains on disk. The deletion predates this
retraction work.

Consequence: a blanket `git add -A` or `git commit -a` from this working tree would
commit the removal of the falsification evidence that the entire retraction rests on.
Stage the retraction paths explicitly, or restore the seven files first. This document
does not restore them — that is a git operation outside its remit.

## 4. What still blocks a current submission

Carried forward from `README.md` and `journal_package/README.md`, unchanged by this
document except where noted:

1. No fresh content-bound PDF build of the current source, and no visual audit of it.
   **Now also required by the 2026-08-28 retraction edits.**
2. No immutable public archive/DOI binding this exact release.
3. No repository-level redistribution terms (see `ARCHIVE_LICENCE_AUDIT_V1.md`).
4. No clean-checkout access to the externally held 47-entry source-native adapter
   handoff or its independent checksum receipt.
5. No target venue selected, so no cover letter.

`ORION-11.CURRENT_PACKAGE` remains `OPEN`.

## 5. Exact build command — recorded, not executed

Transcribed verbatim from `journal_package/COMPILE.md`. Run from
`papers/orion-11-recursive-epistemic-reconstruction/manuscript/`:

```bash
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Requires a TeX distribution with `amsmath`, `graphicx`, `booktabs`, `longtable`,
`hyperref`, `underscore`. `main.tex` additionally loads `amssymb`, `geometry`,
`xurl`, `tabularx`, `caption`, `array`, `ragged2e`.

`bibtex main` resolves two databases, `bibliography` and `novelty_refresh_2026`, via
the `\pOneBibDatabases` catcode trick in `main.tex` lines 18–21. That trick exists
because `underscore[strings]` otherwise mangles the underscore in the second database
name; do not "simplify" it.

Before any rebuilt PDF replaces `journal_package/manuscript.pdf`, `COMPILE.md`
requires: all citations and cross-references resolve; every page rendered with
Poppler and inspected (title/abstract, both figures, all result tables, the
multi-page nearest-work matrix, section transitions, bibliography, margins, page
numbering); then refresh `journal_package/SHA256SUMS` and run its check.

**Two additions required by this retraction, to be checked in that visual audit:**

- Table `tab:P1-T4`'s caption is now materially longer and carries a bold withdrawal
  sentence. Confirm it does not overflow its float or push the table across a page
  break.
- `sections/05b-necessity-successor.tex` gained a `\paragraph{Withdrawn comparative
  reading.}` block and two `\idt{}` calls on long snake_case arm identifiers
  (`activevoi_search_admitted_parent`). Confirm they break legally and do not
  overfull the line. `\idt` is defined in `main.tex` line 28 as `\path{#1}`.

**Do not run this build on this host.** Run it on `laptop billy` or in the
publication-package CI job.
