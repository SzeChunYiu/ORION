# ChatGPT-branch sweep — what is unabsorbed, and what only looks unabsorbed

**Date:** 2026-08-29 · **Scope:** every `origin/chatgpt/*` branch · **Verdict:** no bulk adoption

Answers the standing question "is there work on the ChatGPT branches we are wasting?"
The short answer is no, and the interesting part is why the raw numbers say otherwise.

## Method, and why the obvious method is wrong

A file is only genuinely unabsorbed if the branch *authored* it and `main` lacks
that content. Two cheaper tests both give false positives, and both have already
produced a wrong call in this programme:

- `git diff main..branch` conflates what the branch changed with what `main` gained
  afterwards. On PR #1728 this reported 65 changed files including deleted ORION-02
  evidence; the merge-base diff shows the branch changes exactly 6, all PDFs.
- "absent at this path" is not "absent". The R0 namespace unification renamed 2,734
  files, so a path missing from `main` is as likely to be a rename as a loss.

So each file is classified three ways: blob at the merge base, blob on the branch,
blob on `main`. Only `branch != main` counts, and anything absent at its path is
then re-checked **by basename across the whole of `main`** before being called new.

Scope is stated rather than assumed: 98 of 98 `origin/chatgpt/*` branches processed,
confirmed by a completion marker and a per-branch progress log. An earlier run of
this same sweep was read mid-write and reported 10 rows when it had found 834 — the
counts below come from a single clean run.

## Results

| Measure | Count |
|---|---:|
| Branches swept | 98 |
| Branches holding content `main` lacks | 83 |
| Distinct files differing from `main` | 891 |
| — absent at their path on `main` | 840 |
| — basename also absent anywhere on `main` | 470 |
| — basename present elsewhere (relocation/rename) | 226 |

Raw rows: `CHATGPT_BRANCH_SWEEP_2026-08-29.tsv` (branch, path, `main` blob or `ABSENT_ON_MAIN`).

## The one large finding, and why it is not adopted

271 of the truly-new files are a single directory, `papers/five-paper-top-tier-r8/`,
carried by dozens of branches across rounds r8–r19. It is a real five-paper top-tier
programme — `AB/`, `C/` (FiberGuard), `D/` (typed merge safety), `NQ/` — with
manuscripts, claim ledgers, benchmark artifacts and a harness. `main` has no
directory of that name, and its own five-paper trail (`development/five-paper-hardening-r3-2026-08-28`)
is a checksum manifest over R2 documents that never references the packet.

On those facts it reads as 271 lost files. It is not, and the test that settles it is
lineage rather than filename. Paper `C/` is FiberGuard, which is ORION-02. The packet
holds 7 files for it — `MANUSCRIPT_R8_FIBERGUARD.md`, `fiberguard_r8.py`,
`FIBERGUARD_R8_RESULTS.json`, `verify_refinement_bellman_r9.py` and their ledgers, none
of which exist on `main` under any name. But `main`'s ORION-02 holds **252** files on a
later and independent experiment lineage — `experiments/fibre-diameter-floor-v1/`,
`experiments/refinement-to-certifiability-v1/`, the conformal-recovery V1 and V2 result
and custody sets, and the R23 density-backoff revival. `verify_refinement_bellman_r9.py`
and `check_refinement_to_certifiability.py` are the same question with different code.

The science was carried forward and then taken further; the R8/R9 files are a
superseded parallel lineage. Adopting them would import an older answer alongside a
newer one, which is the failure mode that put eight stale PDFs on `main` in #1719 and
nearly deleted a retraction in the ORION-11 adoption. **No bulk adoption.**

## What is worth taking

`papers/five-paper-top-tier-r8/BLOCKER_REGISTRY.json` has no equivalent on `main` and
is lineage-independent: a 16-entry structured statement of what stands between five
manuscripts and a top-tier venue, explicitly recording
`grants_journal_readiness: false`. Its value is the taxonomy of *why* each item is
open, which survives the renumbering:

| Status | Blockers | Who can close it |
|---|---|---|
| `CLOSED_INTERNAL_R8` / `CLOSED_MATHEMATICALLY_R8` / `CLOSED_DRAFT_R8` | PORT-01, AB-01, AB-02, C-01, C-02, D-01 | closed |
| `OPEN_LUNARC` | NQ-01, NQ-02 | compute — runnable now |
| `OPEN_MATHEMATICS` | NQ-03 | proof work |
| `OPEN_LITERATURE` | C-03, D-03, ALL-01 | primary-source subtraction |
| `OPEN_EXTERNAL` | AB-03, D-02 | outside authority, cannot self-close |
| `OPEN_HUMAN` / `OPEN_RELEASE` | ALL-02, ALL-03 | operator |

Two of the sixteen are compute jobs that need no external authority. Under the current
paper identities those are the concrete gap items; the remainder are gated on
literature, external authority, or the operator, and no amount of internal work closes
them. That distinction — operational versus structural — is the part of this packet
worth carrying into the ORION-01..25 boards.

## Not claimed

That every one of the 470 truly-new files is superseded. The lineage test was run on
paper `C/` and generalised to the packet on the strength of its shared round numbering
and shared base commit. The remaining 225 truly-new files outside
`five-paper-top-tier-r8/` — chiefly 77 `.github` workflow files and 48 under
`publication_closure/` — are recorded in the TSV and have not been individually
adjudicated.
