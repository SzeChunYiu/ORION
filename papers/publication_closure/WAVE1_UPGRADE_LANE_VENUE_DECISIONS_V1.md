# Wave-1 upgrade lane — venue decisions

**Scope:** ORION-14, 16, 17, 19, 23.
**Decided:** 2026-08-28.
**Rule applied:** audit the earned claim first, then choose the strongest
defensible venue for that claim. Where an in-repo venue line already existed it
was treated as input to the audit, not as a constraint on it.

---

| paper | terminal | **venue** | fallback |
|---|---|---|---|
| ORION-14 | `READY_TO_SUBMIT_SECOND_TIER` | **TMLR** (fixed by operator routing) | — |
| ORION-16 | evidence `SECOND_TIER`; filing **`BLOCKED__NO_VENUE_FORMAT_MANUSCRIPT`** | **TMLR** | Empirical Software Engineering |
| ORION-17 | evidence `TOP_TIER`; filing **`BLOCKED__NO_VENUE_FORMAT_MANUSCRIPT`** | **Artificial Intelligence (AIJ)** | TMLR |
| ORION-19 | `READY_TO_SUBMIT_SECOND_TIER` | **TMLR** | Machine Learning (Springer) |
| ORION-23 | `READY_TO_SUBMIT_SECOND_TIER` | **Empirical Software Engineering** | Journal of Systems and Software |

---

## ORION-16 — TMLR, not AIJ

`JOURNAL_READINESS_V2.md` carries a selected AIJ path. It is **not followed**, for
two reasons that are about the claim rather than about preference:

1. The AIJ line predates this lane's measurements and its own next step,
   *"convert Markdown manuscript to venue template"*, is unchecked. It records an
   intention that was never executed.
2. The audited claim does not carry AIJ. `external_independent_validation`
   remains `CANNOT_CHECK`; Gene Ontology rests on four change sets and is
   corroborating; and nf-core/rnaseq returned a **null** for the method. One
   load-bearing system supports the cost claim and one bounds it.

The paper's own `Claims intentionally excluded` list rules out every superiority
narrative — no dependency-repair performance claim, no agent-performance claim.
That is precisely the shape TMLR accepts and AIJ typically does not: a
well-supported bounded claim with its negative results retained. This follows the
operator's own AIJ-with-TMLR-fallback pattern for ORION-06.

## ORION-17 — AIJ

The one paper in this lane at `READY_TO_SUBMIT_TOP_TIER`. Its mechanism claim was
converted from post-hoc attribution into a prospective prediction confirmed 5/5
on held-out packages from five organizations, with the size/density confound
resolved by a case registered in advance. The in-repo AIJ path is retained, so
the selection is not wasted; TMLR is the fallback if AIJ judges the delta narrow
against the already-owned composition theorem.

## ORION-19 — TMLR

Already audited against official TMLR sources in `TMLR_VENUE_AUDIT_V1.md`
(2026-08-19). The added result is diagnostic: an orbit-coverage analysis showing
the protected split is entirely out-of-orbit and that a representation successor
cannot reach the headroom. TMLR accepts well-supported diagnostic and negative
findings on their own terms, which is exactly what this is.

## ORION-23 — Empirical Software Engineering

No venue line existed. The spine is empirical software engineering: a repository
census and collision atlas, an event-sourced state with hard projections, a
144-state planning result and a 5,760-decision legacy-fidelity result, closing on
an external lifecycle boundary. The information-loss theorem leads, but the
weight is measurement over real repositories.

Top tier is not claimed: the organization-disjoint promotion route was closed by
a stop condition before the corpus budget was spent, because the frozen
three-class construction cannot separate the policies. EMSE fits the earned claim
— real-system measurement with a formal core and an honest negative — and JSS is
the fallback.

## ORION-14 — TMLR

Fixed by operator routing. The manuscript is already TMLR-styled and anonymous,
and the package is built.

---

## What remains human

Venue choice is recorded here; **submission itself is not automated**. Each paper's
submission manifest names the inputs only an author can supply — author identity
and order, the venue account and submission id, and confirmation of the venue
checklist.

---

## Packaging audit — what actually exists

Venue choice is only half of a submission. Building each paper's PDF exposed a
split the terminals above must reflect:

| paper | manuscript artifact | PDF | filing state |
|---|---|---|---|
| ORION-14 | venue-format, TMLR style, anonymous | **built, 23 pp, inspected** | ready |
| ORION-19 | venue-format, TMLR style, anonymous | **built, 10 pp** | ready |
| ORION-23 | full paper structure in Markdown | **built, 6 pp, inspected** | ready |
| ORION-16 | *working framework draft* only | builds, but is not a manuscript | **blocked** |
| ORION-17 | *working framework draft* only | builds, but is not a manuscript | **blocked** |

ORION-16 and ORION-17 have complete, independently verified science and no
venue-format manuscript. Their PDFs render as internal working documents over
historical base files, with no venue template, author block or anonymisation.
Reporting them as ready to submit would have been wrong, so they are reported as
blocked on manuscript preparation — writing work, not evidence work.

ORION-23's build was repaired rather than declared blocked. Its `markdown`-package
toolchain needs `texlua` and a matching cache version, and no reachable host has a
TeX distribution at all. Left alone the build silently resolved every section to
the same cached fragment and emitted a plausible but wrong six-page PDF whose
every section read as the References list. The canonical Markdown is untouched;
it is now converted ahead of the build and `\markdownInput` inputs that
conversion, so the source of truth is unchanged and the dependency is gone.

---

## The filing bar, stated once for all of Wave 1

Both lanes were using different words for what looked like the same fact — no
venue template, no author block, no anonymisation decision. That is one
condition, so it needs one bar. The bar distinguishes on **what work remains**,
not on how the artifact was described.

**`READY_PENDING_TEMPLATE`** — a complete standalone manuscript exists: an
abstract environment, an introduction, related work, methods/results, discussion,
limitations, conclusion and availability; bibliography resolved; zero undefined
references. It is not in the venue's class file and carries no author block. What
remains is **mechanical**: obtain the class, re-typeset, fill the author block.

**`BLOCKED__NO_STANDALONE_MANUSCRIPT`** — no such manuscript exists. The artifact
is a replacement or overlay document over historical versions. What remains is
**authorial**: the paper has to be written.

### Applying it, on evidence rather than description

The eight papers of the submission lane were checked against this test directly:
`orion-05`, `orion-08` and `orion-12` each carry `\begin{abstract}` and a full
introduction / methods / results / discussion / related-work / limitations /
conclusion / reproducibility sequence. They are complete manuscripts in the wrong
template — `READY_PENDING_TEMPLATE`.

ORION-16 and ORION-17 fail the same test. Both `main.tex` files lead with
`sections/01-replacement-abstract`, neither contains a `\begin{abstract}`
environment, neither has an introduction or a related-work section, and ORION-17
has no conclusion. Their front matter names historical base documents and
declares itself an overlay. A reader arriving fresh cannot read either as a
paper — `BLOCKED__NO_STANDALONE_MANUSCRIPT`.

### The lane's five under the bar

| paper | state | why |
|---|---|---|
| ORION-14 | **ready** | already in the TMLR class, anonymous, inspected |
| ORION-19 | **ready** | already in the TMLR class, anonymous |
| ORION-23 | `READY_PENDING_TEMPLATE` | complete standalone paper; needs the Springer/EMSE class |
| ORION-16 | `BLOCKED__NO_STANDALONE_MANUSCRIPT` | overlay, no abstract/introduction/related work |
| ORION-17 | `BLOCKED__NO_STANDALONE_MANUSCRIPT` | overlay, no abstract/introduction/related work/conclusion |

Neither venue class is obtainable from this toolchain — `tmlr.sty` ships from the
TMLR site rather than CTAN, and the same holds for `quantumarticle` here — so
template conversion is correctly left as a filing input in both lanes rather than
half-done.
