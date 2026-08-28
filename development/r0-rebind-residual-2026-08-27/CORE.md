# CI red since Wave R0 — measured diagnosis

**Status:** diagnosis only. No repair claimed, no suite run (Mac is metadata-only;
verification belongs on laptop billy / CI).
**Scope:** why `fast (all but p2)` has been red on `main` since 2026-08-26, and why
the two open byte-restore PRs move it the wrong way.

## Trajectory

| commit | what | FAILED |
|---|---|---|
| `926c7529e` | last green main | 0 |
| `3a1a83178` | **Wave R0 namespace unification (#1474)** | **142** |
| `0deff0ad4` | wave 1 — collapse `ORION-ORION-NN` (#1494) | 131 |
| `6d2d1699b` | wave 3a — rebind publication packages (#1496) | 126 |
| `b1e65d444` | current tip | 124 |

Counts are `grep -c 'FAILED tests/'` on each run's `fast (all but p2)` job log.

## R0 is not corruption

`papers/PAPER_RENAME_RECEIPT_V1.json` records R0 as a deliberate, operator-directed
migration — "operator naming-unification directive 2026-08-26 (one flat ORION-NN
series)" — with 2734 git renames, `content_edits_in_moves_commit: 0`, a separate
rebind pass over 11162 text files, regenerated digest pins for `orion-16..25`
(384 hashes, `926/926 OK`), a machine-readable alias registry
(`papers/PAPER_ALIASES.md`: 26 id, 31 dir, 13 file aliases), and `freeze_checker`
exit 0.

The pre-R0 freeze was self-consistent, checked independently rather than assumed:
verifying `R2_FILE_MANIFEST.json` against git blobs gives `ok=20 mismatch=0` at
`9291bc6a7` (pre-R0), `mismatch=2` at R0, and `ok=20 mismatch=0` at current main.

**Therefore reverting R0 would undo an explicit operator directive, and is not the
repair.** The residual damage is that R0's rebind pass reached manuscript prose but
not the harness registries, test expectations and several manifests.

## The two byte-restore PRs move the wrong way

Set-differencing the failing-test names between `main` and each PR's own
`fast` job:

| PR | title | fixes | **newly breaks** |
|---|---|---|---|
| #1540 | batch byte-restore 99 frozen/terminal artifacts | 1 | **8** |
| #1538 | byte-restore five R0-corrupted frozen manifests | 0 | **1** |

They restore indiscriminately, including files R0 was *directed* to rewrite. Both
should be closed rather than merged.

Corroborating: of R0's 3658 touched files, **3654 are still diverged** from their
pre-R0 bytes on main (`git diff --name-only 3a1a83178^ origin/main`). The four
merged repair waves did not restore bytes — they rebound expectations forward.
Byte-restore and forward-rebind are pushing in opposite directions, which is why
every PR sits at 124–131 regardless of what it changes.

## What the 124 failures actually are

Normalising assertion payloads (hashes, ids and counts masked) gives **68 distinct
shapes over 119 messages**; the top 5 cover 45 (38%). The dominant shapes are
digest/content bindings — 16 `Regex pattern did not match`, 15 `<HASH> == <HASH>`,
8 `assert N == N` — i.e. artifacts R0 rewrote whose recorded digests were never
re-pinned. R0 regenerated pins only for `orion-16..25`.

Surviving old names are a **minor** contributor, and this was measured rather than
assumed: `scripts/enumerate_r0_rebind_residual.py` flags 178 files, which overlap
the 61 failing test files in only **4**. An earlier bare-id sweep flagged 2099
files and was discarded as noise — `P1`/`Q1` collide with study-lane and workflow
names.

## Next

1. Close #1538 and #1540 with the set-difference evidence.
2. Rebase the wave PRs. #1498/#1501/#1502 each carry exactly one extra failure,
   `test_r2_manifest_binds_every_declared_file`, because `e28d2c072` changed
   `R2_FILE_MANIFEST.json` after they branched. This is merge skew, not a fragile
   test: the manifest binds an explicit 20-file list, not a glob.
3. Re-pin the digests R0 rewrote outside `orion-16..25`, driven by the residual
   file list, and re-measure the count. Verification runs on laptop billy / CI.

## Reproduce

```bash
python3 scripts/enumerate_r0_rebind_residual.py --report   # naming residual only
git diff --name-only 3a1a83178^ origin/main | wc -l        # R0 residual divergence
```
