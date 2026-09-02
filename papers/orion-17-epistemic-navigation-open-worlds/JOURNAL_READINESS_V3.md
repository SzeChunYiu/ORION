# ORION-17 journal-readiness — V3 progress record

**Status:** `ELEVEN_BOXES_DISCHARGED__ONE_REFRAMED__BASE_PLAN_UNCHANGED`
**Date:** 2026-09-02
**Scientific authority delta:** `NONE`. This records which planned items are
done and by what evidence. It promotes nothing and relaxes no criterion.

## Why this is a separate file

`JOURNAL_READINESS.md` is bound in `CONTENT_MANIFEST_V1.json` and the top-level
`SHA256SUMS`, whose identity is frozen — its checkboxes cannot be ticked in
place. This is the repository's own successor convention (ORION-16 carries
`JOURNAL_READINESS.md`, `_V2` and `_V2_1`; ORION-17 already carries a `_V2`), and
this file is bound in `CONTENT_MANIFEST_V2.json` only.

`JOURNAL_READINESS_V2.md` is **not superseded** and nothing in it is restated
here. It records the theory-closure pass against `manuscript/FINAL.md` and its
exclusions still hold — in particular "no claim that planning abstraction /
schema evolution / goal evolution are ORION-17 inventions", which the
dispositions below sharpen rather than contradict. This V3 record addresses the
later, larger `JOURNAL_READINESS.md` plan, whose §2 asks for an *atomic
per-family* layer that V2's one-line donor-completeness sentence does not
supply.

The base plans are **unchanged and still authoritative for what "done" means**.
Nothing below rewrites a criterion; each entry says only whether that criterion
is now met, and by what.

## §2 Nearest-work closure — ten of thirteen discharged

Evidence: `DONOR_MATRIX_V1.md`, which supplies the atomic per-family layer that
`NOVELTY_AND_DONOR_BOUNDARY.md` (nineteen lines, one `DONOR` token, no family
named) did not.

| base-plan item | state |
|---|---|
| graph / KG navigation families dispositioned | **DISCHARGED** |
| exploratory search / information-foraging families dispositioned | **DISCHARGED** |
| POMDP / active information acquisition families dispositioned | **DISCHARGED** |
| planning abstraction / homomorphism / representation-language families dispositioned | **DISCHARGED** |
| learned / adaptive planning representation families dispositioned | **DISCHARGED** |
| web / deep-search agent planning and stopping families dispositioned | **DISCHARGED** |
| model-revision / world-model / replanning families dispositioned | **DISCHARGED** |
| goal / objective revision and evolution families dispositioned | **DISCHARGED** |
| ontology / schema evolution and preservation-map families dispositioned | **DISCHARGED** |
| scientific-exploration breadth / concentration work dispositioned | **DISCHARGED** |
| hostile exact-composition search completed | **OPEN** |
| two no-material-change rounds | **OPEN** — a first pass cannot satisfy a stability criterion |
| `#287` novelty certificate current | **OPEN** |

All ten dispositions are `DONOR`. None yields a surviving new consequence on its
own. The subtraction narrows the paper; it does not widen it.

## §7 Manuscript — the related-work box is discharged

| base-plan item | state |
|---|---|
| full-text related-work section with atomic donor dispositions | **DISCHARGED** |

Evidence: `manuscript/FINAL_V5.md`, §"Prior work and donor attribution", carrying
family-group prose and a `### Named sources` subsection. `FINAL_V4` had none.
V5 is V4 plus that section and one correction — 186 lines added, 0 removed, every
V4 heading surviving verbatim except the title.

The remaining §7 items — claim ledger `#346` terminal, deterministic generator
replay under `#347`, immutable records/tables/figures, `#283` receipts — are
unchanged and **OPEN**.

## §3 Theory — one item reframed, not discharged

| base-plan item | state |
|---|---|
| planning-abstraction donor mappings prove conservative embedding where feasible | **REFRAMED, STILL OPEN** |

`COMPOSITION_LAW_PARENT_FINDING_V1.md` establishes that planning abstraction and
MDP homomorphism are **not** the parent of the §18 composition calculus:
homomorphism composition composes on strict object matching and supplies no
compatibility relation, so it cannot yield Theorem V4.1's `Match` side
condition. A conservative embedding into that family is therefore not the test
that would settle anything.

The test that would is named and remains undone: whether Theorem V4.3's
demand-containment condition is exactly the assume-guarantee composability
condition, and whether an existing interface framework already contains V4.1.
Both are in-house decidable. **This box is not ticked** — the work it names has
been shown to be aimed at the wrong target, which is progress but not
completion, and the replacement work has not been done.

## Net

Eleven boxes discharged, one reframed and left open, and the paper's headline
claim is smaller than it was: not a new composition law, but a decidable
registry-based compatibility test proved sound against a demand-containment
semantics with its incompleteness characterised. The base plan's remaining items
stand as written.
