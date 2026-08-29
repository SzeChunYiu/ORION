# Path-by-path recovery: `codex/issue-1701-orion01-closeout-20260829`

Issue #1701 lists this branch under **ADOPT FIRST** for ORION-01. The adoption-safety
sweep flagged it as carrying an evidence loss, so it was recovered file by file rather
than merged.

## Classification

| | files |
|---|---:|
| already identical to `main` | 5 |
| genuinely diverged | 2 |
| **unique contributions** | **0** |

## `proof_checker_v3.py` — do not adopt, `main` is a superset

`main` 11,206 B / 320 lines against the branch's 10,194 B / 282 lines. Both define the
same **15** functions and the branch defines **none** that `main` lacks. Taking the branch
version would delete 38 lines of checker for nothing.

## `theory-B-MANUSCRIPT_V3.md` — adopt one line

The whole difference is 4 bytes on line 164, and it is a real correctness fix:

```
main    beta_{P1 x P2}(F1 x F2;C) = beta_P1(F1;C1)+beta_P2(F2;C2)
branch  beta_{P1 x P2}(F1 x F2;C) = beta_{P1}(F1;C1)+beta_{P2}(F2;C2)
```

Unbraced `beta_P1` subscripts only the `P` and renders the `1` as an ordinary character,
so the product formula displays inconsistently against the correctly-braced
`beta_{P1 x P2}` on the same line. Adopted.

## Disposition

`RECOVERED_PATHWISE__ONE_LINE_ADOPTED`. The branch is otherwise fully superseded and must
not be merged: it contributes nothing else and would remove checker code.

Worth stating plainly — **being listed as ADOPT FIRST is not the same as being
safe to adopt.** This branch is named that way on the board and is, in fact, 99%
superseded with one four-byte fix worth keeping.
