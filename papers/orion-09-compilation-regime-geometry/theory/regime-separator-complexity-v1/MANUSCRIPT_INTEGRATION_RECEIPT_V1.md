# ORION-09 — Manuscript integration receipt for `ORION09.REGIME_SEPARATOR_COMPLEXITY.v1`

**Date:** 2026-08-29
**Action:** discharge of the blocker `MANUSCRIPT_INCOMPLETENESS__SUBMISSION_BLOCKED`
raised in `CLAIM_DISPOSITION.md` §6 / `THEORY.md` §8 and referred there rather than taken.
**Authority:** issue #1701 board, P0 line — *"ORION-09: integrate four-feature separator
result and correct the stale abstract"*, which classifies this as a correctness/package
action, not new science.

## Scientific authority delta

`NONE`. No threshold, corpus, comparator, vocabulary, outcome definition or success gate
was changed. No receipt, protocol, addendum or ledger byte was modified. No recorded
terminal was altered:

- `H_A_N2 = POSITIVE_CONVERSION` — unchanged.
- `H_B_N4_residual = NOT_IMPROVED` — unchanged and now stated in the abstract.
- `NOT_R6` authority ceiling — unchanged.
- No `CANNOT_CHECK` was converted to a pass.

## Files edited

| file | change |
|---|---|
| `manuscript/main.tex` | abstract rescoped to the wording proposed in `CLAIM_DISPOSITION.md` §6, extended with `k*=4` and the `n=4` shuffle-null `p=0.51` |
| `manuscript/sections/03-results.tex` | previous refutation scoped to "within that vocabulary"; new subsection reporting floor 0 under the enlarged vocabulary, both structure-free nulls, `k*=4` with witness, and **both** adverse findings |
| `manuscript/sections/06-limitations.tex` | non-separability scope corrected: recovered law is domain-local, not universal |
| `MANUSCRIPT_V3.md` | abstract rescoped; §9.3's "Enlarging the representation remains an open successor question" replaced by §9.4 answering it, carrying both adverse findings |
| `rewrite_academic_pipeline/MANUSCRIPT_REWRITE_V1.md` | abstract rescoped in the same direction |

`MANUSCRIPT_V2.md` is deliberately **not** edited: `MANUSCRIPT_V3.md` records it as the
prior draft, and it is retained unmodified as history.

## Negative and adverse results preserved verbatim in the manuscript

Both adverse findings from `RESULT.json` are now in the manuscript body, not only in the
evidence tree:

1. `MECHANISM_ATTRIBUTION_NOT_SUPPORTED` — any two of L3's three blocks attain floor 0;
   V2 + donor-path attains it with no sign-aware feature; the minimal witness contains
   zero sign-aware coordinates. The conversion did not require the new block.
2. The `n=4` non-transfer — 32/120 CV errors equal to the parent cell-lookup baseline,
   shuffle-null mean 32.41, empirical `p=0.51`.

Per `THEORY.md` §3.7 the positive is never stated without the `n=4` negative attached.
The originally frozen-vocabulary 43/1146 floor is retained in every rewritten abstract;
it is scoped, not deleted.

## Not done here

Re-running the three independent checkers is compute and was not performed in this
session. See the ORION-09 `NEEDS_COMPUTE` entry in the accompanying worker report for the
exact commands. All numbers quoted above are copied from the committed checker outputs
(`RESULT.json`, `ANALYSIS.json`, `MINIMALITY_VERIFICATION.json`, `REPLAY_REPORT.json`),
none is hand-derived.

## Skills-protocol compliance

`skills-applied: NONE` for the manuscript edits recorded above. Under
`papers/PAPER_WRITING_SKILLS_PROTOCOL_V1.md` §1 an abstract rewrite and section edits are
"writing a paper" and the `nature-*` package should have been loaded first; in this
session it was loaded later, for the ORION-17 manuscript. Disclosed rather than
back-filled. The edits are not re-derived: every quoted value is copied from
`RESULT.json`, `ANALYSIS.json`, `MINIMALITY_VERIFICATION.json` or `REPLAY_REPORT.json`,
and both adverse findings are carried with the positive.

## #1649 governance, preserved not spent

`theory/size-transfer-derivation-v1/DERIVATION_NOTE.md` — recovered byte-exact in the
same commit — carries ORION-09's #1649 Tier B record:
`DERIVATION_ONLY__PROMOTION_BUDGET_NOT_SPENT`, stating that the one promotion attempt is
unspent and that the note is deliberately not an attempt at it. Nothing here spends it.
The abstract rescope is the correctness action the board classifies as "not new science",
and this lane's own `PROTOCOL.json` stop rule reads: "This lane is complete. It generates
no successor experiment. The one open item it creates is a manuscript rescope."

## Deferral to PR #1702 — READ THIS BEFORE FILING ORION-09

**Amendment, 2026-08-29 (after the edits recorded above).**

A parallel lane, `shadow/issue1701-middle-papers-recovery-20260829` (PR **#1702**), was
found to have made the same abstract and results-section rescope independently. Its
version was audited here and is **correct**: it retains the 43/1,146 floor, states floor
0 and the four-feature minimum separator, and preserves **both** adverse findings — the
`n=4` non-transfer with its shuffle null `p=0.51`, and the unsupported state-sign
mechanism attribution ("requires no hypothesized state-sign feature, so transfer and
mechanism attribution remain unsupported"). No negative and no `CANNOT_CHECK` was
softened by it.

`git merge-tree` showed my versions of two files conflicting with #1702's:

```
CONFLICT (content): manuscript/main.tex
CONFLICT (content): manuscript/sections/03-results.tex
```

Both files have therefore been **reverted to `origin/main`** on this branch, so #1702's
wording applies cleanly. The recovered theory packets are byte-identical between the two
branches (`git diff --quiet` exit 0 for `size-transfer-derivation-v1`; the only delta in
`regime-separator-complexity-v1` is this receipt), so the recovery halves merge without
conflict.

### Consequence — a live dependency, not a closed item

**ORION-09's abstract and results-section correctness now depends on PR #1702 merging.**
If #1702 is closed unmerged, `manuscript/main.tex` and
`manuscript/sections/03-results.tex` revert to carrying the stale claim, and the blocker
`MANUSCRIPT_INCOMPLETENESS__SUBMISSION_BLOCKED` is **not** discharged. The rescope must
then be re-applied — the wording proposed in `CLAIM_DISPOSITION.md` §6 is still the
reference text.

### What this branch still contributes to ORION-09, which #1702 does not

#1702 edits only `main.tex` and `03-results.tex`. Three stale surfaces are left untouched
by it and are corrected here:

| file | stale text #1702 leaves in place |
|---|---|
| `manuscript/sections/06-limitations.tex` | "richer path/schedule-aware features **may** recover exact determination" — they demonstrably did, on `n<=3` |
| `MANUSCRIPT_V3.md` | abstract carries the superseded scoped claim, and §9.3 ends "Enlarging the representation remains an **open successor question**" |
| `rewrite_academic_pipeline/MANUSCRIPT_REWRITE_V1.md` | the newest wave-1 rewrite abstract, still carrying the unscoped refutation |

Both lanes are needed for the paper to be internally consistent.
