# ORION-02 figure contract — V3

## Figure 1 — Negative-result recovery state machine

**Reader question:** What is the method independent of ORION-Q lane names?

Show one claim episode as:

`frozen question -> execute/verify -> typed terminal -> unresolved obligation -> separately frozen successor`

Terminal branches must include `POSITIVE`, `NEGATIVE`, `ABSORBED`, `MIXED`, `SATURATED`, `LOWER_BOUND_CLOSED`, and `CANNOT_CHECK`. The visual must make clear that the parent terminal is immutable after a successor is created.

**Do not imply:** every negative must have a successor or that the controller chooses the scientifically optimal successor.

## Figure 2 — The R6 recovery DAG as a worked trace

**Reader question:** Did the abstract recovery rule actually generate a nontrivial scientific trajectory?

Use nodes rather than a chronological prose timeline:

`exact donor saturation`
→ unresolved explanation obligation
→ `R6N local explanation + global closure refuted`
→ frozen repair
→ `R6O second exact refutation`
→ support-two successor
→ `R6P finite closure`
→ prediction obligation
→ `R6R prospective confirmation`
→ composition obligation
→ `R6S all-n theorem`.

Color/shape semantics should distinguish refutation, finite-domain closure, prospective evidence and theorem. Every arrow must be annotated with the unresolved obligation that licensed the successor.

## Figure 3 — Donor subtraction and honest terminals

A compact matrix showing representative Q outcomes:

- apparent proxy win → implementation-aware negative;
- specialized policy → donor absorption;
- internal resource gain → projection-dependent mixed result;
- full-knowledge negative → partial-knowledge reopening.

The figure's role is to show that the protocol does not force all lanes toward a positive terminal.

## Table 1 — Recovery contract and evidence boundary

Columns:

`terminal | operational meaning | what evidence earns it | licensed next move | forbidden promotion`.

This table should appear in main text even if Figure 3 is supplementary.

## Main-text discipline

- Detailed R0–R5 chronology belongs in Supplementary Information or the receipt-index dataset.
- ORION-01 owns the mathematical proof details of R6S; ORION-02 should show only the result needed to demonstrate the recovery endpoint.
- Receipt filenames should be in Methods/Data Availability/SI, not inside the visual argument.
