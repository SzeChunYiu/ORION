# Triage record — 2026-09-03 uncommitted inventory (V1)

Scope: every uncommitted/local ORION item surfaced in the 2026-09-03 repo-hygiene
inventory (7 items), each resolved to LAND / SUPERSEDED / PRESERVED-DOCUMENTED /
NEEDS-DECISION with two-way evidence. This file is the durable record; the
landed artefacts themselves travel in the PRs named below.

**Repository correction.** The inventory named `SzeChunYiu/ORION-paper` as the
PR target. That repository is the private mirror (v1-papers/v2-papers tree);
every item in this inventory lives in the public `SzeChunYiu/ORION` tree, so
all PRs in this record target `SzeChunYiu/ORION`.

## Verdict table

| # | Item | Verdict | Disposition |
|---|------|---------|-------------|
| 1 | w1-sub uncommitted relabel (8 readiness records) | SUPERSEDED-IN-PART | Cleaned relabel to 6 records landed (this PR); orion-10 and orion-13 excluded as superseded |
| 2 | mirror-complete rebind (sha c3ac6553→b8287366) | LIVE-IN-FLIGHT | Already pushed as open PR #2181; no action |
| 3 | ORION-claude Aug-23 leftovers | PRESERVED-DOCUMENTED | Every class already audited-and-rejected by the landed ADMISSION_MATRIX; nothing to land |
| 4 | tests/unit/study/test_p3_coordinate_ablations.py | NEEDS-DECISION | Orphan test; module absent everywhere; fails collection (verbatim below); not landed |
| 5 | /private/tmp/qg47wt QG47_PARTS/ (1350 receipts) | LANDED-AS-MANIFEST | Digest manifest PR'd; raw parts preserved but on volatile storage — flagged |
| 6 | ORION-wt/p2-baselines staged paper-02 figures | SUPERSEDED | Worktree removed 2026-09-03; branch ref `claude/p2-baselines` retained |
| 7 | ORION/.claude/worktrees/wf_33796e5e-18e-{1,2,3} | SUPERSEDED | 3 worktrees + 3 branch refs removed; edits target manuscript text that no longer exists on main |

## Item 1 — w1-sub uncommitted relabel

Source: `/Users/billy/Desktop/projects/ORION-wt/w1-sub`, uncommitted diff on 8
`papers/orion-*/submission/JOURNAL_READINESS_SUBMISSION_V1.md` replacing
`READY_TO_SUBMIT_SECOND_TIER` with `READY_PENDING_TEMPLATE`.

Evidence, two-way: on main at 3463d0f7, `READY_PENDING_TEMPLATE` occurs in 0
readiness records (control: `READY_TO_SUBMIT_SECOND_TIER` occurs in 28 files) —
so the relabel was genuinely absent and landable. Two of the eight records had
advanced past it and were excluded:

- **orion-10**: main has a tier-b-final-20260901 package with terminal
  `PUBLICATION_PACKAGE_COMPLETE__PORTAL_ACTIONS_ONLY` — a strictly stronger
  state; relabelling it back to a template-pending label would regress.
- **orion-13**: main's readiness record was fully rewritten (F1000Research
  brief-report filing under `submission/publication-final-20260901/`); the old
  record the diff patched no longer exists.

Correction applied while landing: the hand-edit's history sentence ("Earlier
this record said `READY_PENDING_TEMPLATE`; that label understated the template
gap") was factually wrong — the records said `READY_TO_SUBMIT_SECOND_TIER`. The
landed supersession note states the true history: the old label named the venue
tier reached but hid the venue-format conversion the same record lists as a
remaining input. ORION-12's factual "Bar note" (no section titled "Discussion";
interpretive content lives elsewhere) is kept verbatim. The label vocabulary is
defined in `WAVE1_UPGRADE_LANE_VENUE_DECISIONS_V1.md` (open PR #1692); the
records cite it as pending, not as a main path.

w1-sub worktree disposition: its 11 branch commits are fully landed or
evolved-past (of 97 files touched, 48 byte-identical to main; the 49 differing
files' main-side last-touch commits are all newer, e.g. orion-06 main.tex
ae3d79144 2026-09-03, orion-05 COVER_LETTER.md 12ce2adfe 2026-08-30 (#1887),
orion-08 03-results.tex 7196acdf1 2026-09-02). The uncommitted diff is
superseded by this PR once merged. Worktree left in place until this PR merges
(its hand-edit is the source document); removable afterwards.

## Item 2 — mirror-complete rebind

`ORION-wt/mirror-complete` was clean (no uncommitted changes); the described
work (PACKAGE_MANIFEST.json / SHA256SUMS / CLOSURE_REGISTRY.json rebind
c3ac6553→b8287366) is already pushed as **open PR #2181**
(`lane/mirror-gate-complete-20260903`), head e5ad2a14d — byte-identical to the
worktree HEAD. This is a live lane, not stranded local work: no action taken,
worktree left in place. Whether the 20260831 package is canonical vs
tier-b-final-20260901 is decided inside that lane's own review, not here.

## Item 3 — ORION-claude Aug-23 leftovers

Preserved in place (`/Users/billy/Desktop/projects/ORION-claude`), nothing
landed, nothing deleted. Each class is already adjudicated by the landed
`development/cross-session-empirical-provenance-audit-2026-08-23/ADMISSION_MATRIX.json`:

- `pilot_runs.jsonl` / `pilot_scored.jsonl`, `paper-03 evaluation/analysis`,
  `run-full`, `run-smoke`, `artifacts/` — audited and rejected as evidence in
  the matrix (run-site artefacts, superseded by certified receipts).
- `gold/annotations/` (32 annotation files) — generated by
  `generate_source_texts.py` from seeds, annotator `seed-to-gold-v1` /
  `adjudicated-v1`, i.e. placeholders, not independent annotators. Main's
  `papers/orion-13-*/evidence/CANNOT_CHECK_REMAINING_V1.md` records exactly
  this ("annotator-a/ and annotator-b/ do not exist"; promoting the adjudicated
  set to expert gold is forbidden). Landing them would contradict a landed
  CANNOT_CHECK.
- `cross-session-empirical-provenance-audit-2026-08-23/` — already on main in
  path-migrated form (the landed ADMISSION_MATRIX is that audit).
- `retry_*.log` — transient logs, no evidentiary value.
- `qg3-stage1.json` — CI workflow artefact, ephemeral by design.

## Item 4 — orphan ablation test (needs decision)

`tests/unit/study/test_p3_coordinate_ablations.py` (149 lines, untracked in
`ORION-wt/p3-100-ablations`) imports
`orion.study.p3_coordinate_ablations`, which exists nowhere: 0 hits in
`git log --all -- '*p3_coordinate_ablations*'` (control: the same log for
`p3_public_reference.py` matches) and 0 paths in `ls-tree -r` of origin/main.

Run on billy-old (per host policy), depth-1 clone of main 3463d0f7 with the
test file dropped in, `PYTHONPATH=src pytest`. Failure, verbatim:

```
ImportError while importing test module 'tests/unit/study/test_p3_coordinate_ablations.py'
tests/unit/study/test_p3_coordinate_ablations.py:16: in <module>
    from orion.study.p3_coordinate_ablations import (
E   ModuleNotFoundError: No module named 'orion.study.p3_coordinate_ablations'
Interrupted: 1 error during collection!
1 error in 0.57s
```

Not landed. Options for the owning lane: land the module it was written against
(it is not in any ref, so it must be written), or discard the test. The test
file itself remains untracked in `ORION-wt/p3-100-ablations`.

## Item 5 — QG47 parts

`/private/tmp/qg47wt/research/extensions/orion-qg/QG47_PARTS/` holds 1,350
per-task sweep receipts (schema `ORION.QG.QG47.SweepPart.v1`). Verified: not a
split document — 1,350 independent receipts, each self-contained JSON; the
aggregated results file (`QG47_N2_FULL_SWEEP_RESULTS.json`, landed, #2178)
confirms `n_parts_found=1350`, `parts_complete=true`, `parts_digest_ok=true`,
and the landed attribution doc cites the parts directory as its input, but
repo convention lands aggregates, not mass per-part files (QG48's identical
`qg48_n3_frontier_prospection.py` landed via #2184 while its parts did not).

Landed instead: `research/extensions/orion-qg/QG47_PARTS_MANIFEST_V1.json`
(schema `ORION.QG.QG47.PartsManifest.v1`) — one row per part (file,
file_sha256, task_id, part_digest, objective, prefix, witness_count), so the
attribution doc's "1350/1350 match" claim stays verifiable without landing
1,350 raw files.

**Flag:** the only surviving copy of the raw parts is
`/private/tmp/qg47wt/...` — volatile storage that macOS purges on reboot. If
the parts themselves must survive, someone must move them to durable storage
before the next reboot; the manifest preserves their digests either way.

## Item 6 — p2-baselines staged figures

Supersession was established against main's renumbered
`papers/orion-12-*` (ex-paper-02-open-world) tree: the staged figures/scripts
were the pre-renumbering versions of content main already carries. Nothing
unique. `git worktree remove --force` executed 2026-09-03; branch ref
`claude/p2-baselines` left for history. No PR (nothing to land).

## Item 7 — wf_33796e5e-18e-{1,2,3} paper-03 manuscript edits

Third state: **not landed AND superseded.** The three worktrees held
paper-03 (= orion-13) manuscript edits: main.pdf, 30-method/40-dataset/50-evaluation/06-results
.tex, gold annotations + generate_skeletons.py.

- Not landed: main's orion-13 `06-results.tex` carries the post-execution text
  (the "executed twice" phrasing); the worktree edits patched the
  pre-execution text, which exists nowhere on main.
- Superseded: main's `30-method.tex` is a 143-line ground-up rewrite; the
  `m(P_a,P_b)` formalism the edits build on occurs in 0 orion-13 files on main
  (control pattern matches in other papers). Landing the edits would graft
  removed formalism back onto a rewritten manuscript — a regression.
- The gold annotations duplicate item 3's seed-placeholder class (main's
  landed gold/adjudicated/ + CANNOT_CHECK_REMAINING supersede them).

All edits were reviewed against main before removal; none contained content
absent from main except content main deliberately removed. Three worktrees
removed (`git worktree remove --force`) and their three `worktree-wf_33796e5e-18e-{1,2,3}`
branch refs deleted, 2026-09-03.

## PRs from this triage

1. This PR: item-1 relabel (6 records) + this record.
2. QG47 parts manifest (item 5), separate branch.
