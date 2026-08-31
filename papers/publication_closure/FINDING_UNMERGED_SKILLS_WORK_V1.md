# Substantial requested work is sitting in unmerged pull requests

Seven pull requests are open, and together they contain more paper work than this session produced. They were not discovered by looking at papers; they were found by listing open PRs.

| PR | branch | size | subject |
|---|---|---|---|
| #1815 | `academic-rewrite-batch-06-07-08-10-12-14-16-20260829` | **+7374** | applies `academic-paper-skills` across 23 bounded paper objects |
| #1853 | `academic-top-tier-refinement-20260830` | **+6988** | top-tier refinement across ORION-01–2x |
| #1798 | `chatgpt/all25-top-tier-readiness-20260829` | +2186/-397 | all-25 readiness and manuscript gaps |
| #1764 | `codex/all25-top-tier-gap-closure-20260829-pro` | +2010 | cross-paper theory, design and inference closure |
| #1821 | `recover/orion17-density-prospective` | +918 | ORION-17 density-prospective packet |
| #1885 | `pub/orion14-tmlr-hardening` | +65 | ORION-14 double-blind fix |
| #1854 | `fix/orion01-workflow-pin-refresh` | +2 | workflow pin |

## #1815 is the skills application that was asked for

It produces `rewrite_academic_pipeline/MANUSCRIPT_REWRITE_FINAL.md` per paper and covers papers that have no LaTeX source at all, including **ORION-02 and ORION-03** --- both recorded elsewhere as unbuildable. If those rewrites are usable, the "no manuscript" bucket is smaller than recorded.

## Why it does not merge as-is

Measured, not assumed:

- 57 commits ahead of main, **143 behind**
- `git merge-tree` reports **zero conflict markers**; the merge is textually clean
- merging it and running the suite gives **10 failures**, all binding-coverage: the new files are added to papers whose content is hash-bound, and the manifests predate them

The failures name P6, P7 and P8 --- ORION-16, -17 and -18. **ORION-16's bindings are under the V1 freeze**, so reconciling them is the same blocked operation recorded previously. A full merge is gated on that freeze decision; a partial merge covering only unbound papers would deliver most of the value and requires splitting a 57-commit branch.

## What this says about the session's method

Every audit in this session read the working tree. None of them read the open pull requests. Two consequences followed: work already done was not counted, and effort went into papers whose rewrites already existed on a branch. The tree is not the whole repository.

A smaller instance of the same error: **#1904 was created, tested, and reported as recorded, but never merged.** Its file was absent from `main` until an explicit audit of every recorded finding caught it. Creating a pull request is not landing it.
