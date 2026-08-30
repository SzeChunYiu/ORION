# Adoption disposition — `chatgpt/wave1-publication-closeout-20260828`

Issue #1701 lists this branch under **ADOPT FIRST** for ORION-14. This record is the
result of actually checking it before adopting.

**Disposition: DO NOT ADOPT WHOLESALE.** The branch carries real manuscript improvement
*and* removes two recorded `CANNOT_CHECK` authority terminals that `main` currently
carries. The improvements are adoptable; the removals are not.

## What was compared

Branch `81d10573c` against `main` `344c1225c`, merge-base `f5e015f87`. Three-way blob
test per file, so "differs" is never confused with "is newer":

| direction | files |
|---|---:|
| identical to main already | 9 |
| **branch ahead** (main untouched since base) | **13** |
| **both diverged** (real reconcile needed) | **6** |

## The blocking finding

Diff totals are 1,453 added / 573 removed lines, with 13 removed lines carrying
negative-evidence vocabulary. Removed lines can be rewrites rather than deletions, so
each identifier was checked against the branch's **final content**, not the diff:

| identifier | merge-base | branch | main | verdict |
|---|---:|---:|---:|---|
| `P4_NATURALISTIC_V2_IDENTITY_COMPLETE__…_CANNOT_CHECK` | 2 | 1 | 2 | survives (reduced) |
| `P4_EXTERNAL_TERMINAL_CANNOT_CHECK` | 1 | **0** | 1 | **LOST** |
| `CANNOT_CHECK_FULL_COMPARATOR_FREEZE` | 1 | **0** | 1 | **LOST** |
| `P4_NATURAL_PAIR_SOURCE_TRANSPORT_CANNOT_CHECK` | 8 | 7 | 8 | survives (reduced) |

Control: the branch contains 1,629 `CANNOT_CHECK` occurrences under ORION-14, so the
search finds what is there. The two zeros are absences, not search failures.

### What replaced them

`08-data-and-code-availability.tex:183` previously read, in substance, that the bounded
probes establish at most repository or entrypoint facts, that no audited external system
supplies the native three-terminal map the naturalistic endpoint requires, and that the
audit terminal therefore **remains** `CANNOT_CHECK_FULL_COMPARATOR_FREEZE`. The branch
replaces this with a statement that the naturalistic source-expansion programme *is not
part of the evidence supporting the present performance claims*.

`06-threat-model-limitations-and-interpretation.tex:196` previously recorded that no
audited neighbour natively separates `ResolvedTrue` / `ResolvedFalse` / `CannotCheck`,
and named both terminals as current. The branch drops the naming.

### The scale of the rewrite

The two dropped identifiers are not isolated line edits. Measured against `main`, the
branch compresses three sections substantially:

| section | words on `main` | words on branch | removed |
|---|---:|---:|---:|
| `06-threat-model-limitations-and-interpretation.tex` | 2,288 | 758 | **67%** |
| `08-data-and-code-availability.tex` | 1,288 | 253 | **80%** |
| `09-conclusion.tex` | 766 | 295 | **61%** |

These are real cuts, not reflow — byte counts fall in the same proportion (17,325→5,812;
13,820→1,870; 6,001→2,311). All three are classified branch-ahead, meaning `main` still
sits at the merge-base for them: the branch shortened this text, `main` did not lengthen it.

A compression pass may well be wanted for a page limit. The objection is not its
existence but what it takes with it: the limitation section loses 3 of its 3
negative-evidence lines and the conclusion loses its 1, which is how the two terminals
disappeared.

Both edits convert a **recorded authority limit** into a **scope disclaimer**. Nothing in
the branch supplies a receipt resolving either limit — the limits are not answered, they
stop being stated. For a submission, a dropped authority limit is a non-disclosure a
reviewer is entitled to find, and #1701's own ORION-14 line asks the opposite:
*"Preserve source/provider edge blockers as authority limits."*

## Adoption rule that follows

1. The 13 branch-ahead files may be adopted **only** with both identifiers and their
   surrounding limitation text restored. Adopting the section rewrites as-is is a
   regression regardless of their other merit.
2. The 6 diverged files need per-file reconciliation and must be re-checked for the same
   pattern before any of them lands.
3. Adopting any `manuscript/` `.tex` change moves the ORION-14 render epoch and therefore
   invalidates `manuscript/main.pdf`, which exists on `main`. Any adoption must be
   followed by a CI rebuild and a post-merge PDF re-import — a branch-side PDF cannot
   satisfy this, because its own squash-merge moves the epoch again.

No claim is promoted or retracted by this record; it gates an adoption.
