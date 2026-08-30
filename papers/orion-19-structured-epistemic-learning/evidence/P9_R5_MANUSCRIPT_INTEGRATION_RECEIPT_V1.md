# ORION-19 — R5 evidence integration receipt

**Date:** 2026-08-29
**Authority:** issue #1701 board, P0 line — *"ORION-19: integrate V3 causal-diagnostic
positive + orbit-coverage gate + custody-only UT3 record"*, and the ORION-19 section
of §C.
**Scientific authority delta:** `NONE`. No threshold, target, cell, corpus, comparator,
arm, cost, seed, outcome definition or success gate was changed.

## Sources, recovered path-by-path (no branch merged)

| artifact | source branch |
|---|---|
| `evidence/P9_CAUSAL_DIAGNOSTIC_TRANSPORT_V3_{RECEIPT.md,RUN.json}` | `claude/r5-revival-orion19-18-20260828` |
| `evidence/P9_PROTECTED_CELL_EXECUTION_RECEIPT_V1_2026-08-28.json` | same |
| `evidence/P9_QWEN_618_RECOVERY_EXECUTION_RECEIPT_V1_2026-08-28.json` | same |
| `evidence/R5_REVIVAL_LEDGER_V1.json` | same |
| `top_tier/P9_CAUSAL_DIAGNOSTIC_TRANSPORT_PROTOCOL_V3.md`, `top_tier/run_causal_diagnostic_transport_v3.py` | same |
| `build_evidence_summary.py`, `evidence/OFFICIAL_EVIDENCE_SUMMARY_V1.json` | same (additive R5 block only) |
| `theory/orbit-coverage-gate-v1/` | `claude/w1-final-submission-20260828` |
| `experiments/ut3-checkpoint-custody-v1/` | `codex/all25-bounded-freeze-v2-20260828` |

**Integrity:** all nine files recovered from `claude/r5-revival-orion19-18-20260828`
were re-hashed in this tree and match that branch's own `SHA256SUMS` entries byte for
byte (9/9 MATCH). No file was edited in transit.

## What the manuscript now states (`manuscript/sections/05-results.tex`)

Three subsections were added. Nothing was removed or rewritten; the registered V1
instrument and its `4/5 (0.8)` headline table are untouched.

1. **Decision-rule refinement.** V2 raised accuracy to 1.0 but its terminal was
   `P9_CAUSAL_DIAGNOSTIC_TRANSPORT_V2_GATE_NOT_MET` — half-draw stability failed on
   D-A. That failure is stated as a failure. V3 applies LCB95 target satisfaction with
   every other element frozen and reaches
   `P9_CAUSAL_DIAGNOSTIC_TRANSPORT_V3_SUPPORTED`, no failing clauses.
2. **Orbit-coverage gate**, terminal
   `GATE_EVALUATED__REPRESENTATION_SUCCESSOR_NOT_INDICATED`.
3. **U-T3 custody-only record**, still blocked.

## Negatives, nulls and CANNOT_CHECKs preserved — none softened

- **D-A protected cell is NOT converted to a pass.** Probe and protected LCBs both sit
  below the unchanged 0.965 target; all four half decisions return `CANNOT_CHECK`.
  Under the frozen V1 gold rule D-A remains `CANNOT_CHECK`. V3 makes the abstention
  decision-stable; it does not make it a pass. The manuscript says this explicitly.
- **No target was relaxed.** D-A 0.965, D-I 0.95, executable 1.0 all unchanged, as are
  cells, arms, costs (8.0/2.0/12.0), R=24 and draw seeds.
- **V2 gate failure retained** in the record and in the manuscript.
- **Qwen scaling negative untouched**: authoritative negative, and on recovery
  `UNSOLVABLE within the frozen family` — 1.5B and 3B collapse to a constant label in
  both arms, only 0.5B is non-degenerate and its primary-budget delta is negative
  (-0.141). No monotone scale benefit is claimed anywhere.
- **U-T3 remains BLOCKED.** 4 of 6 declared ladder points in custody; the two
  Llama-3.2 points are `CANNOT_CHECK` (gated repo, HTTP 401), which the receipt itself
  marks as *not* evidence the points are unnecessary. **Zero grid cells executed**;
  `produces_scientific_result: false`. The missing piece is a cell executor, declared
  but not built.
- The Wine null cell and the `T4_ATTACK_SUCCEEDED` reminting verdict are unchanged.

## Binding artifacts

`SHA256SUMS` regenerated over the previous 114 paths (all still present; none dropped)
plus the 19 newly bound paths = 133 entries. `CONTENT_MANIFEST_V1.json` extended
additively by the same 19 paths.

**Open:** `CONTENT_MANIFEST_V1.json.subject_commit` is deliberately left at
`81473e5ee0c75977bdb059954ea52c90045c66a2` rather than being pointed at a branch commit
that is not this tree's HEAD. It must be rebound at freeze time. This is recorded as
open, not silently patched.

## Not done here

The V3 runner was not re-executed and the orbit checker was not re-run; both are
compute. See the ORION-19 `NEEDS_COMPUTE` entries in the accompanying worker report
for exact commands. Every number quoted in the manuscript additions is copied from a
committed artifact.

## Skills-protocol compliance

`skills-applied: NONE` for the `manuscript/sections/05-results.tex` additions recorded
above. Under `papers/PAPER_WRITING_SKILLS_PROTOCOL_V1.md` §1 section edits are "writing a
paper" and the `nature-*` package should have been loaded first; in this session it was
loaded later, for the ORION-17 manuscript. Disclosed rather than back-filled. The
additions are not re-derived: every quoted value is copied from a committed artifact, the
registered V1 instrument and its 4/5 headline table are untouched, and every negative
listed above is carried unsoftened.

## Cross-lane note — the UT3 packet path is shared with the orchestration branch

**Amendment, 2026-08-29.** `work/issue1701-orchestration` independently recovered part of
`experiments/ut3-checkpoint-custody-v1/`. Compared here:

- `run_ut3_checkpoint_custody_lunarc.sbatch` is **byte-identical** on both branches
  (sha256 `076cc3fd7b44e5da09cb1f166adcab07111d21defd5a4b60846b1021df91644a`, 7,424 bytes),
  so it merges without conflict.
- `P9_UT3_CHECKPOINT_CUSTODY_RECEIPT_V1.json` is also byte-identical (sha256
  `d1334f0edd16ab64e113a11be016511a6cf422339dc18fb0684bc5aa0d0d5d70`) but sits at a
  **different path**: `ut3-checkpoint-custody-v1/` on that branch, `job-3550343/` here.
  A merge lands **two copies**. The `job-3550343/` path is the one the packet's own
  `SHA256SUMS` attests — that manifest was recovered byte-exact from
  `codex/all25-bounded-freeze-v2-20260828` and lists
  `job-3550343/P9_UT3_CHECKPOINT_CUSTODY_RECEIPT_V1.json`. The top-level copy is not
  covered by it. Recommended resolution: drop the top-level duplicate and keep the
  manifest-attested path.

This branch carries the complete eight-file packet (manifest, README, authority
disposition, both jobs' stdout/stderr, both job dirs); the orchestration branch carries
two of those files. Nothing here was edited in transit.

## UT3 carries no scientific authority in the manuscript — verified

The manuscript states UT3 as custody-only. `manuscript/sections/05-results.tex` §"U-T3
frontier grid: custody only, no scientific result" is its only appearance anywhere in the
manuscript (grep for `u-t3|ut3|u_t3` returns three lines, all inside that subsection). It
reads, in full:

> The U-T3 frontier evaluation grid remains blocked and is reported as such. A custody run
> placed 4 of 6 declared ladder points in local custody (Qwen2.5 at 0.5B, 1.5B, 3B and
> 7B); the two Llama-3.2 points are gated and recorded as CANNOT-CHECK for those ladder
> points --- which is not evidence that they are unnecessary or that the grid is sound.
> **Zero grid cells were executed.** The receipt carries
> `produces_scientific_result: false` and licenses no statement about any crossing; the
> missing component is a cell executor, which is declared but not built. U-T3 stays
> blocked until cells carry outcomes.

No scientific claim is stated or implied. No correction was required.
