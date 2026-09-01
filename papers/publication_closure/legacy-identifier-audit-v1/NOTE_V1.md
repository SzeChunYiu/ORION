# Legacy paper identifiers in front matter

Closes the `immediate_safe_actions` item recorded for ORION-07 in
`TOP_TIER_ATOMIC_GAP_LEDGER_V2` — *"add an aliasing note explaining the legacy ORION-03
identifiers without editing frozen files"* — and generalises it, because the same defect
appears in two other papers.

## The finding

Three front-matter documents announce themselves as a different paper:

| document | declares | actually belongs to |
|---|---|---|
| `orion-06-recursive-recovery/NEAREST_WORK_MATRIX_V3.md` | **ORION-02** | ORION-06 |
| `orion-07-dual-instrument/README.md` | **ORION-03** | ORION-07 |
| `orion-08-typed-state/NEAREST_WORK_MATRIX_V3.md` | **ORION-04** | ORION-08 |

45 front-matter documents were checked; these three disagree.

## Why these are not explained by the alias registry

`papers/PAPER_ALIASES.md` is the declared single source of truth for historical paper ids.
It carries **39 alias entries, and not one maps an `ORION-NN` id to a different
`ORION-NN`**. Its old ids are P-series and letter-series names (`P6`, `theory-A`, `NQ`),
which is exactly right for the R0 unification it records.

So a header reading "ORION-02" inside `orion-06-` is **not** a sanctioned historical
alias. A reviewer encountering it has no registry entry to resolve it against, and no way
to tell whether they are reading the wrong paper's matrix. That is the whole defect: not
that the id is old, but that it is **unresolvable**.

## Why this note rather than an edit

None of the three files is content-bound or covered by a `SHA256SUMS`, so editing them is
permitted. It is still the wrong first move:

- The headers are evidence of the renaming history. Silently rewriting them removes the
  trace without recording that it happened.
- The durable fix is a **guard**, not three edits — otherwise the next document
  reintroduces it.

`check_legacy_paper_identifiers_v1.py` is that guard. It inspects the first three lines of
each paper's front matter, consults the alias registry before reporting, and exits `1` on
an unsanctioned mismatch and `3` if the registry is missing — so "could not check" is never
confused with "checked and clean".

Validated in both directions: with the tree as-is it reports **3** findings; correcting one
header drops it to **2**; restoring returns **3**. It reads the files rather than
asserting a fixed answer.

## Recommended resolution

Either correct the three headers to their own paper id **and** add the old id to
`PAPER_ALIASES.md` so the history survives, or leave the headers and add explicit
registry entries sanctioning them. Both are defensible. What is not defensible is leaving
an identifier that the declared source of truth cannot resolve — and this checker will
keep failing until one of the two is done.

`grants_authority: NONE`. This reports identifiers only and says nothing about content.
