# P1: the V1 preflight `require_mapped` check cannot pass on LUNARC

**Status:** `BODY_FREE_OBSERVATION_ONLY__NO_PROTECTED_EXECUTION_NO_SCIENTIFIC_AUTHORITY`

The successor V4 design packet states the actual runtime defect as a
hypothesis:

> The V1 check requires the pathname rendered in `/proc/<pid>/maps` to equal
> the frozen logical `/sw/...` path. On LUNARC, the same file may be rendered
> under canonical `/lunarc/sw/...`, with matching device and inode identity.

Measured on LUNARC, that "may" is "always".

## Observations

Probe: a body-free Python process on the LUNARC login node. No protected
packet, no model, no tokenize, no completion, no generation, no job, no
scheduler allocation, no network.

| check | result |
|---|---|
| `/sw/…/Python/3.11.5-GCCcore-13.2.0` exists | yes, **not a symlink** |
| `/lunarc/sw/…/Python/3.11.5-GCCcore-13.2.0` exists | yes, **not a symlink** |
| device / inode, logical | `66` / `15577490566` |
| device / inode, canonical | `66` / `15577490566` |
| same file identity | **yes** |
| `resolve(strict=True)` of the logical path | returns the **canonical** path |
| distinct mapped pathnames under the sw trees | 8 |
| any row rendered as `/sw/…` | **no — zero of 8** |
| any row rendered as `/lunarc/sw/…` | **yes — all 8** |

## What this establishes

A check comparing the maps pathname to the frozen logical `/sw/...` string
fails on every row, every time, on this host. It is not flaky and not
node-dependent: the kernel renders the mount's canonical path, and the
logical path is a second name for the same device and inode rather than a
symlink to it.

This is a **string comparison where an identity comparison was required**.

## What it does not establish

- It does not prove this caused the V3 protected failure on job `3537893`.
  It shows the check cannot pass here, which is necessary for that failure
  and not sufficient to attribute it.
- It says nothing about GPU visibility, model execution, protected success,
  task success, production admissibility, or ORION superiority.
- The probe ran on the login node. A compute node could in principle render
  differently, though the same mount topology is expected.

## Consequence for the evidence chain

The GPU-visibility line of investigation — jobs `3537910`, `3537915`,
`3537988`, `3538042`, and the cg14 node exclusion — tested a different
variable. Job `3538042` legitimately established `VISIBLE_A40_IDENTITY_BOUND`
on `cg15`, and that result stands on its own. But a visible GPU does not
make the V1 maps check pass, because that check never consults the GPU.

The design's own required mapping rule already encodes the fix: bind logical
**and** `resolve(strict=True)` canonical paths, require them to share device
and inode, and admit maps rows only under that exact two-element set. These
measurements confirm the rule is necessary rather than defensive — on this
host the canonical branch is the only one that ever matches.

## Reproducing

```python
import os, pathlib
L = "/sw/easybuild_milan/software/Python/3.11.5-GCCcore-13.2.0"
C = "/lunarc" + L
a, b = os.stat(L), os.stat(C)
assert (a.st_dev, a.st_ino) == (b.st_dev, b.st_ino)
assert str(pathlib.Path(L).resolve(strict=True)) == C
rows = [l.split()[-1] for l in open("/proc/self/maps") if "/sw/" in l]
assert not any(p.startswith("/sw/") for p in rows)
```
