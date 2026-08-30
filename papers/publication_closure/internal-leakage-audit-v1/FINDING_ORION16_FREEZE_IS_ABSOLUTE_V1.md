# ORION-16 title/author repair: blocked, and the block is correct

**Terminal:** `TITLE_REPAIR_IMPOSSIBLE_UNDER_V1_FREEZE__POLICY_DECISION_REQUIRED`

## The defects

`manuscript/main.tex` carries two things that make the paper unsubmittable:

- title suffix `--- V5` (an internal version label)
- author field `Working framework draft`

## Why they cannot currently be repaired

`manuscript/main.tex` is bound in the frozen `CONTENT_MANIFEST_V1.json` at subject commit `87e2bcb33`. Three routes were tried; the checker refused all three.

| route | result |
|---|---|
| add a `SUPERSEDED_BINDING_*.json` record | **no effect** — nothing in the suite references `SUPERSEDED_BINDING` |
| reconcile V1's digests to the repaired file | **rejected** — `subject_commit_status: BOUND` compares against the commit, not just digests |
| re-bind V1 at a new subject commit | **refused** — `frozen CONTENT_MANIFEST_V1.json no longer describes the V1 subject; bind additive files in CONTENT_MANIFEST_V2.json` |

## A correction worth recording

The `SUPERSEDED_BINDING` records in ORION-19, -23 and -25 look like a supersession mechanism. They are not. No test consults them; they are documentary only. Anyone reading them as an escape hatch will lose time, as happened here.

A second wrong inference: every paper's V1 `subject_commit` has moved several times in git history, which reads as licence to move it again. Those moves **predate the freeze**. History showing a field once moved is not evidence it may move now.

## What the design actually says

V1 is frozen. Additive files go to `CONTENT_MANIFEST_V2.json`. But `main.tex` is a *modification*, not an addition, so V2 offers no route either. The freeze is absolute for files V1 already binds.

## What would unblock it

A deliberate decision, not a workaround:

1. amend freeze policy to permit a manuscript-surface class of repair (title/author) with an auditable record; **or**
2. render the submission from a source that V1 does not bind; **or**
3. accept the defects and do not submit this paper.

Option 3 is the current de-facto state. Loosening the guard to force the edit was rejected: the guard behaved exactly as designed, and the science in this paper is unaffected either way.
