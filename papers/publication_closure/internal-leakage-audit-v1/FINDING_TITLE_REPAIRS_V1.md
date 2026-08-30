# Title leakage: repaired for 21..24, blocked by a frozen record for 16/17/18

## Repaired and landed

`AUTHOR_CODE` is now **0** across all 25 papers. ORION-21/22/23/24 carried an
internal paper identifier in `\author{}` (`ORION-P11`..`P14`) and ORION-24 led
its title with the project code `ORION-RSE:`. All repaired, PDFs re-rendered and
re-bound through the render path added this session (#1891, #1892).

## Blocked, and why the block is legitimate

Three title version suffixes remain:

| paper | title still carries |
|---|---|
| ORION-16 | `--- V5` |
| ORION-17 | `--- V4` |
| ORION-18 | `--- V3 science update` |

The repairs themselves are trivial and were written. They cannot land because
each paper's **`CONTENT_MANIFEST_V1.json` is a frozen record** whose
`subject_commit` (`87e2bcb33…`) binds `manuscript/main.tex`. Editing the title
makes the file differ from that commit, and the checker correctly reports:

```
P6: subject_commit_status claims BOUND but these differ from 87e2bcb33…:
    papers/orion-16-.../manuscript/main.tex
```

Everything downstream of V1 was reconciled successfully: the V2 manifests, the
paper `SHA256SUMS`, the subject commit/tree and each manifest's own digest. The
render path works and produced all three PDFs with **zero overfull boxes**. Only
the V1 frozen claim blocks it, and it blocks it correctly.

## What must not be done

Rewriting V1's `subject_commit` to the new tree. V1 asserts what was bound at a
specific commit. Repointing it so a later edit passes would convert a historical
record into a moving one, which is the precise failure the frozen-manifest test
exists to prevent. The same applies to regenerating its digests.

## What would resolve it

A release-authority decision, not a repair:

1. **Supersede V1 for P6/P7/P8** — record a successor manifest and mark V1
   historical, the way `SUPERSEDED` packages already work elsewhere in this
   repository. V1 keeps asserting what was true at `87e2bcb33`.
2. **Or accept the suffixes** in these three titles until their next scheduled
   re-freeze.

Option 1 is almost certainly right, because a version suffix in a submitted
paper's title is a real defect and the frozen record is not the artifact being
submitted. But superseding a frozen manifest is an authority act, and this
session should not perform it silently inside a typography fix.

`grants_authority: NONE`

**Terminal:** `TITLE_REPAIR_BLOCKED_BY_FROZEN_V1_MANIFEST__SUPERSESSION_REQUIRED`
