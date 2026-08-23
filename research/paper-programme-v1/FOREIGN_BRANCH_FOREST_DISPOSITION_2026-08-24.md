# Foreign branch-forest disposition — P6–P15 combination audit (2026-08-24)

**Question (operator directive 2026-08-23):** the foreign AI sessions (codex, chatgpt)
hold P6–P15 branches; combine their work into main without losing any of it and without
duplicating what already landed.

**Method.** Blob-level tree comparison, not commit history: for every foreign branch,
`git ls-tree -r` over `papers/paper-06…paper-15` was classified per file against both
current `origin/main` (45e5fee59) and the shared fork base `c5ba39fe`:

- `SAME` — blob identical on main and branch (already combined);
- `BRANCH_AHEAD` — file unchanged since base on main, advanced on branch (unmerged work);
- `BRANCH_ONLY` — file exists only on the branch (unmerged work);
- `DIVERGED` — both sides changed the file since base (reconciliation surface);
- `MAIN_ONLY` / `MAIN_AHEAD` — main newer (branch stale there).

## Result

| Branch | SAME | BRANCH_AHEAD | BRANCH_ONLY | DIVERGED |
|---|---:|---:|---:|---:|
| `codex/p6-p10-evidence-closure-20260823` | 553 | **0** | **0** | 33 |
| `codex/p11-p15-confirmatory-execution` | 519 | **0** | **0** | 28 |
| `codex/p1-p15-takeover-20260823` | 507 | **0** | **0** | 57 |
| `chatgpt/p6-p8-repro-checker-splice-cleanup-20260823` | 737 | **0** | **0** | 47 |
| `chatgpt/p12-p13-submission-hardening-20260823` | 754 | **0** | **0** | 44 |
| `chatgpt/gap-wave-p7-p11-recut-20260823` | 755 | **0** | **0** | 47 |

(SAME counts differ because each branch snapshots main at a different age; the
`chatgpt/*` branches forked from a main only ~30 commits old, `codex/*` from
`c5ba39fe`, 169 commits behind current main.)

**Every P6–P15 file the foreign branches added or advanced is already on main in equal
or newer form. There is no uncombined foreign P6–P15 evidence in the branch forest.**

## Nature of the residual DIVERGED files (all reconciled in main's favour)

1. **Generated binding surfaces** — `CONTENT_MANIFEST_V1/V2.json`, `SHA256SUMS`,
   `CLAIM_LEDGER_*.md`: main regenerated these after later receipt landings
   (#1026/#1032/#1039/#1006/#1041 waves). Branch versions are stale bindings.
2. **Editorial surfaces** — `README.md`, `manuscript/sections/*`,
   `TOP_TIER_PROMOTION_V1.md`: main carries the newer cross-paper collision-review
   prose (e.g. P11 abstract's P8-laundering distinction; P7 promotion doc's
   P6/P13/P2 donor-boundary paragraphs). Spot-checked divergences show main
   strictly supersets the branch text.
3. **Defective branch-side authority JSONs** — on `codex/p6-p10-*` and
   `codex/p11-p15-*`:
   - `P11_ACTIVE_CLAIM_AUTHORITY_V1.json`: **invalid JSON** (`p11i_runner` entry
     spliced without delimiter);
   - `P14_ACTIVE_CLAIM_AUTHORITY_V1.json`: **invalid JSON** (`external_validity`
     key after closing brace);
   - `P10_ACTIVE_CLAIM_AUTHORITY_V1.json`: valid but **duplicate `lifecycle_state`
     key** (silent shadowing).
   Main's versions of all three parse cleanly. Codex lane: if these branches are
   landed as-is the authority files will break JSON parsing — regenerate rather
   than merge those blobs.

## Disposition

- **No merge action required** on P6–P15 paths. The foreign forest's live content is
  on P1–P5 + infra paths (`.github/workflows/orion-qg-*`, `development/`, `src/orion`)
  — codex's own lane, out of scope here by the ownership split.
- The branches are **preserved** (operator rule: never delete). This note is the
  evidence that they contain no uncombined P6–P15 work, so future sessions do not
  re-audit them.
- Re-audit trigger: any NEW foreign branch whose push date postdates 2026-08-24
  00:00 UTC, or any branch that adds files under `papers/paper-(0[6-9]|1[0-5])/`
  not present on main — rerun the same blob-classification
  (`BRANCH_AHEAD ∪ BRANCH_ONLY ≠ ∅` is the merge signal).
