# Codex branch sweep — all 105 unmerged branches classified

Issue #1701 instructs every session to check unmerged branches for work in flight and to
**never merge a large stale/diverged branch wholesale**. This is that check, run
exhaustively rather than by sampling.

Method: `check_branch_adoption_safety_v1.py`, a three-way blob classification of every
changed file against `origin/main` — so "differs from the merge-base" is never mistaken for
"is newer" — followed by an evidence-loss test asking whether `main` holds negative-evidence
lines or `.jsonl` records **by key** that the branch does not.

## Result

| | branches |
|---|---:|
| swept | **105** |
| clean, with unique contributions | **40** |
| **carry evidence losses — do not adopt wholesale** | **53** |
| nothing unique (already absorbed) | 12 |

**More than half the unmerged codex lane would destroy evidence if merged wholesale.**
That is the single most useful number here, and it is why the "recover path-by-path" rule
in section A of the board exists.

Worst offenders by records lost:

| branch | evidence losses | files |
|---|---:|---:|
| `p1-p15-takeover-20260823` | **86** | — |
| `p1-p5-successor-execution` | **70** | — |
| `p6-p10-evidence-closure-20260823` | **70** | — |
| `p11-p15-confirmatory-execution` | **69** | — |
| `p1-diagnostic-ontology-active-base` | **55** | — |
| `all25-bounded-freeze-v2-20260828` | 10 | 293 |

Note `issue-1701-orion01-closeout-20260829` carries **1** loss despite being named in the
board as an ORION-01 **ADOPT FIRST** source. Listed-as-adopt-first is not
safe-to-adopt-wholesale, and that is exactly the trap this sweep exists to catch.

Largest clean candidates, ranked by unique contribution:

| branch | unique files |
|---|---:|
| `orion-04-crb-replay-exec-20260827` | **250** |
| `crb-full-manifest-1383-20260826` | **233** |
| `r9-nq-full-manifest-unblocker-20260826` | **218** |
| `r9-nq-cleanroom-engine-b-20260826` | **210** |
| `r9-p2-baseline-repair-20260826` | 116 |

## How to use this

- The 40 clean branches can be merged after a normal CI regression check; each was
  classified `rc=0` with zero evidence losses.
- The 53 lossy branches must be recovered **path-by-path**. `CODEX_BRANCH_SWEEP_V1.json`
  carries the per-branch loss count; the checker re-run on any one of them prints the
  specific paths and, for `.jsonl` ledgers, the specific record keys that would be lost.
- The 12 empty branches need no action.

## Scope

This classifies **adoption safety**, not scientific merit. A clean branch may still contain
work that is wrong; a lossy branch may contain work that is excellent and merely needs
per-file recovery. `grants_authority: NONE`.
