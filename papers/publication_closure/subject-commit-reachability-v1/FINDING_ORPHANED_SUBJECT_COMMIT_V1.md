# A bound subject commit had no ref left, and a rename-blind history walk

Two of the ten CI failures remaining on `main` after #1819 had a single cause, and
a third had a second cause hiding behind it. Both are fixed here; neither was
fixed by re-pinning anything.

## 1. The subject commit no ref reached

ORION-16 and ORION-17 both bind
`subject_commit c0aa940413f39357f4944c7433786f8eee8735a6` in their
`CONTENT_MANIFEST_V2.json`. The reproducibility checker reported
`exact_subject_commit_identities: PARTIAL — V2 subject tree is unavailable`.

Verified, in order:

- the commit is **not an ancestor of `main`**;
- the only ref that reached it was `origin/external/cohorts-v1`, present on one
  machine as a **stale remote-tracking ref**;
- `gh api .../branches/external/cohorts-v1` → **404**, and
  `git ls-remote --heads origin 'external/*'` returns nothing. The branch was
  deleted;
- GitHub still served the object by SHA, because unreferenced objects survive
  until garbage collection;
- the object is intact: its tree carries 106 files for ORION-16 and 120 for
  ORION-17.

So two papers bound their subject to a commit that **no reference reached**, kept
alive only by GitHub not yet having collected it. A fresh clone could not reach it,
which is what the checker was correctly reporting, and a garbage collection would
have made it permanent.

**Fixed by restoring a reference, not by re-pinning a manifest.** The commit is now
reachable from `archive/subject-c0aa9404-orion16-orion17`. The bindings were
correct all along; the reference under them had been deleted.

Of the six distinct `subject_commit` values bound across all `CONTENT_MANIFEST`
files, this was the only unreachable one — the other five are reachable from
branches that still exist on the remote, checked individually.

## 2. The history walk could not see across two renames

`check_negative_null_history_v1.py` accepts a negative-history row when its source
has the recorded bytes **now or at some point in git history**, so that an honest
later extension of a claim ledger does not invalidate an immutable adverse record.
The walk was `git log --format=%H -- <current path>`.

`git log -- <path>` stops at a rename. ORION-16's `CLAIM_LEDGER_V4.md` moved
**twice**, and the recorded bytes `5bc5185d…` live at a third path entirely:

| walk | commits seen | contains the recorded digest |
|---|---|---|
| `git log -- <current path>` | 1 | no |
| `git log --follow -- <current path>` | 2 | no |
| the bytes' actual home, `papers/paper-06-formal-epistemic-structures-and-mechanics/CLAIM_LEDGER_V4.md` | — | **yes** |

The bytes were never lost: blob `903beb4059a56c3bf7e798fb6d5bbaf752c6560e` is in
the object store and is reachable from a ref. `--follow` does not rescue this —
it does not survive a restructuring that moves thousands of files at once, which
is exactly what R0 was.

The walk now falls back to **every historical path sharing the same basename**.
That keeps the claim "this named artifact had these bytes" while surviving
directory renames, and is strictly narrower than accepting any blob anywhere in
the object store, which would drop the path from the binding entirely.

## Validation

- **Causal, isolated:** `test_negative_history_is_content_bound` **fails on `main`**
  and **passes with the fix**, same tree, same command.
- **Falsification:** replacing the recorded digest with 64 zeros still raises
  `stale or missing source binding`. The fix widens where the bytes may be found,
  not whether they must be found.
- **A caveat worth recording:** the subject-identity checks resolve against the
  working tree, so *any* uncommitted file under `papers/` makes them report
  `PARTIAL`. While diagnosing this, a staged file from an unrelated probe produced
  three failures that looked like regressions from this fix and were not. Run these
  checks on a clean tree.

## Why the rename-blind walk is diagnosed here but not fixed here

The fix is one function: fall back to every historical path sharing the source's
basename. It was written, and it works — `test_negative_history_is_content_bound`
fails on `main` and passes with it, same tree and command, while a 64-zero digest
is still rejected.

It is **not shipped in this change**, because the file it edits,
`papers/candidates/checkers/check_negative_null_history_v1.py`, is itself a
**bound file** in ORION-16's and ORION-17's `CONTENT_MANIFEST_V2.json`, pinned by
SHA-256. Editing it breaks those bindings by construction, and on CI it traded one
failure for five: three subject-identity checks, a diagnostic-count check, and a
P6 certificate check.

Re-deriving those manifests is a legitimate operation — a content binding records
what the tree contains, unlike a frozen protocol — and `check_content_binding_v1.py`
has a `--write` mode for exactly this. But `--write` regenerates
`CONTENT_MANIFEST_V1.json`, not the V2 manifests these tests read, and it rewrites
118 lines of two papers' `SHA256SUMS`. That is a papers-lane operation on two
papers' content bindings, and it is not taken here while that lane is active.

**What a fixer needs:** the one-function change above, plus a V2 content re-binding
for ORION-16 and ORION-17 that repins this checker's digest. The bug, the fix and
its validation are recorded so that work does not have to be rediscovered.
