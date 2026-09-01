# Correction: `GOVERNANCE_ADJUDICATION_V1.md` §4 asserts additions that were never made

**Written:** 2026-09-01, against `origin/main` at `fe39f297e`.
**Scientific authority delta:** `NONE`.
**Status:** three assertions in §4 are **unsupported**; §6's `SHA256SUMS` count is wrong.
The adjudication in §2 is unaffected and stands.

`GOVERNANCE_ADJUDICATION_V1.md` is left byte-unchanged. A receipt that turns out to be
wrong is corrected beside itself, not silently rewritten — rewriting it would erase the
evidence that the error occurred, which is the thing a later reader most needs.

## What §4 claims, and what is actually on `main`

§4 is headed *"What was added to the paper"*. Each claim was checked against
`origin/main` with a control pattern that must match, so a zero result means absent
rather than a search that failed.

| §4 claim | on `main` | control |
|---|---|---|
| `submission/density_prospective/main.tex` added | **0 path hits** tree-wide for `density_prospective` | `orion17` → 15 hits |
| `CLAIM_LEDGER_V4.md` row `ORION-17.V4.12` added | **0 hits** for `V4.12` | `V4.11` → 3 hits |
| `CLAIM_LEDGER_V4.md` boundary addendum, *"14 insertions, 0 deletions"* | not present | as above |

§6 states the paper-root `SHA256SUMS` was *"extended 73 → 89"*. On `main` that file is
**exactly 73 lines**.

## This is not relocation damage

The packet was moved from `papers/orion-17-.../theory/density-prospective-v1/` to
`papers/publication_closure/orion17-density-prospective-v1/` in #1821, and the obvious
hypothesis is that the move dropped the paper-tree edits. **It did not.** The same three
checks run against `backup/pr1821-remote-20260901`, the branch head *before* any
relocation, return the same zeros — `density_prospective` 0 with control `orion17` at 4,
`V4.12` 0, `SHA256SUMS` 73 lines. The relocation was ten renames at 100% similarity.

The claimed edits were never on the branch. §4 describes work that was not performed.

## Why this one matters more than a bookkeeping slip

§4 does not merely list files. It states that `submission/density_prospective/main.tex`
*"discharges filing terminal `BLOCKED__NO_STANDALONE_MANUSCRIPT`"*.

So the packet contradicts itself. `RESULT.md` §9 records the filing terminal as
**`BLOCKED__NO_STANDALONE_MANUSCRIPT`** and explains why — the only manuscript artifact
is a working framework draft, `main.tex` leads with `sections/01-replacement-abstract`
and carries no `\begin{abstract}`, no introduction, no related-work section. §4 asserts
that blocker discharged by a file that does not exist.

**`RESULT.md` is the one to believe.** Its terminal is corroborated by the tree; §4's is
contradicted by it. ORION-17's filing terminal remains
`BLOCKED__NO_STANDALONE_MANUSCRIPT`, and
`ORION17_MANUSCRIPT_BLOCKER_ROUTE_V1.md` — which treats that blocker as open and records
what clearing it would require — is correct as written.

## What survives untouched

The adjudication proper, §2, does not depend on any of this. It rules the prospective
density result admissible rather than a forbidden rescue, on the ground that #1649's stop
fired on a different object — the arbitrary-chain theorem owned by V4.5 — and yields
`TOP_TIER_SUCCESSOR_NOT_SUPPORTED__BOUNDED_RETAINED`. That reasoning is about the
relationship between two studies, not about files, and it stands.

§5's preserved items stand: the #1649 stop, all five `NEGATIVE_HISTORY.jsonl` entries
including the `ARBITRARY_CHAIN_THEOREM_ALREADY_EXISTED` control, `donor-coarse`'s 77,630
combined false retentions, `always-reopen`'s 382,044 unnecessary reopenings, the
naturalistic multi-hop blocker, and ORION-16's boundary labelled convergent
same-programme evidence rather than independent corroboration.

The scientific result is likewise untouched: the packet's independent checker returns
`PASS`, `correct: 5/5`, with all four negative controls firing, re-run from the packet's
current location.

## Consequence for `PUBLICATION_DISPOSITION_MATRIX_V1.md` row 17

Row 17 names three conditions: *land packet path-by-path, adjudicate governance, write
standalone manuscript.* The first two are discharged — the packet is on `main` and §2 is
a genuine adjudication. **The third is not**, and no artifact on `main` discharges it.
ORION-17 stays `NO_BOX_EARNED_ON_MAIN` at two of three.

## Why the paper tree could not have received those edits anyway

ORION-17 is one of `DIRECT_BOUND_PAPERS`. All 123 files named in
`CONTENT_MANIFEST_V2.json` — including every file under `manuscript/` — are byte-bound
against `subject_commit 2b4cde64`, and `bound_paths` enumerates the paper directory with
`rglob("*")`. Adding `submission/density_prospective/main.tex` or editing
`CLAIM_LEDGER_V4.md` would have broken the binding and turned CI red. Whatever produced
§4's text, the edits it describes could not have landed in that tree by that route.
