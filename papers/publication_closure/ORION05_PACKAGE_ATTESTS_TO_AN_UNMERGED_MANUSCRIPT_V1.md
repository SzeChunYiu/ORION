# ORION-05's journal package attests to a manuscript that is not in main's history

**Status:** `FINDING__DIGESTS_DESCRIBE_AN_UNMERGED_BRANCH__REPAIR_NEEDS_A_DESIGN_DECISION`
**Scientific authority delta:** `NONE`.

`check_package_sums_path_root_v1.py` established that ORION-05's package digests are
unresolvable by the repository's own checker, and that eleven are stale once resolved
correctly. "Stale" turns out to be the wrong word, and the truth is worse.

## The eleven never matched

Recomputing every entry as of `71607dca7`, the commit that wrote the file:

| | entries |
|---|---:|
| matched then and still match | 26 |
| drifted after the file was written | **0** |
| **wrong at the moment the file was written** | **11** |

Nothing drifted. The digests were never right.

All eleven are manuscript sources: `main.tex`, `bibliography.bib`, and all nine numbered
sections.

## What they describe

The recorded digest for `manuscript/main.tex` matches the version of that file at
`e7a668511` — *"paper(orion05): close the wave-1 technical revision"*, 2026-08-28.

**`e7a668511` is not an ancestor of `main`.**

`71607dca7` is *"papers: adopt 349 wave1 closeout artifacts from unmerged Codex branches"*.
It brought the package's `SHA256SUMS` across from that branch. It did not bring the
manuscript the digests describe.

So ORION-05's journal package attests to a manuscript that exists only on an unmerged
branch. A reader verifying the package against the repository would be checking the shipped
manuscript against digests for a different document.

## Two defects, and why neither was caught

Either alone would have been visible:

1. **The digests are wrong.** Eleven of forty describe files that are not in main.
2. **The path root makes them unresolvable.** The entries are repository-root-relative while
   `package_currency` resolves `paper_dir / path`, so all forty read as `missing`, and
   `missing` is not part of the staleness ratchet's failing condition.

Together they are invisible. The second hides the first, and ORION-05 is the paper where
that matters most: its committed PDF is deliberately excluded from the render-equality gate
(#1918), so this digest gate was the only remaining check on its package.

## Why regenerating is the right repair here, and normally would not be

The drift ratchet is explicit that entries leave a baseline "by reconciling the paper —
never by regenerating digests to match whatever is on disk, which would erase the evidence
that content moved and leave a manifest asserting that nothing did."

That rule protects against erasing evidence of movement. **Here there was no movement**: zero
entries drifted after the file was written, which is measured above rather than assumed. The
digests did not stop describing the files; they never described them. Recomputing therefore
erases nothing, and is the only thing that makes the record true.

That reasoning is specific to this case and does not generalise. It rests on the measured
`drifted after = 0`, and if that number were not zero the rule would apply in full.

## Why the path root is not a mechanical fix

The obvious correction — rewrite the paths as paper-relative — cannot be applied blindly.
One entry is `.github/workflows/orion05-wave1-closeout.yml`, which is outside the paper
directory and has no paper-relative form. The repo-root root may therefore be deliberate:
this package deliberately covers a repository-level workflow, and every other package does
not.

So the repair needs a decision that is not mine to make:

- **drop the out-of-paper entry** and make the remainder paper-relative, matching the other
  five packages and the checker; or
- **keep the root** and teach `package_currency` that a package may declare entries outside
  its paper, resolving each accordingly.

The first makes ORION-05 like everything else and loses a covered file. The second admits a
second convention into the checker. Both are defensible, and choosing between them is a
statement about what a journal package is allowed to contain.

## What is claimed here

That the digests describe an unmerged manuscript, measured; that nothing drifted, measured;
that the path root hides both, measured. Not that either repair is the right one.
