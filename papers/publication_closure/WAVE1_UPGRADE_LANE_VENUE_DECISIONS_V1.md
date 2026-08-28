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
| ORION-16 | `READY_TO_SUBMIT_SECOND_TIER` | **TMLR** | Empirical Software Engineering |
| ORION-17 | `READY_TO_SUBMIT_TOP_TIER` | **Artificial Intelligence (AIJ)** | TMLR |
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
