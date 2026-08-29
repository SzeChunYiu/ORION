# ORION-08 — fresh literature closure for the typed/scoped-state composition claim

Submission gate from `JOURNAL_READINESS.md`. Prior closure: `NOVELTY_RESEARCH_2026-08-22.md`
and `NEAREST_WORK_MATRIX_V3.md`. This pass searched for work published **after** that date.

**Result: the neighbourhood moved.** A dense 2026 literature on agent-memory
staleness, provenance-sensitive action, and budgeted verification now exists, and several
entries postdate the V3 matrix. None of it sinks the paper, and the closest one is a
strong parent worth absorbing rather than fencing off — but **the V3 matrix is no longer
current and the manuscript's Related Work must be updated before submission.**

## The nearest new parent

**Nakayashiki, *When Stale Constraints Go Unchecked: Budgeted Verification Failures in
Inherited Agent Memory*, arXiv:2608.25553v2 (2026-08-27).**

It shares four design commitments with ORION-08, which is why it matters:

| shared commitment | how it appears there |
|---|---|
| factual payload held fixed, epistemic relation varied | turn-1 prompts are **byte-identical** across world × policy cells; world state invisible at allocation |
| matched budget across arms | verification budget is exactly 2 records **in every arm** |
| hostile / no-value control | source-agreement arm: record confirms memory → near-ceiling, +0.7 to +2.0 points |
| exact deterministic scoring | outcome `Y` on action id alone; "no model judges anything" |

Headline: with a constraint stated, agents inspected its provenance path in ~20% of
episodes; when that constraint was superseded, native allocation produced stale-consistent
decisions in **77.3% / 74.7% / 74.7%**, and re-assigning one of two slots to the critical
path moved current-record-consistent decisions by **+74.0 / +72.7 / +61.3** points, 6/6
models. 5,400 confirmatory episodes, OpenTimestamps-anchored pre-registration.

It also names further neighbours ORION-08 does not currently cite: STALE
(arXiv:2605.06527), governance decay under compaction (arXiv:2606.22528), omission-vs-
commission constraint decay (arXiv:2604.20911), selection integrity for graph memory
(arXiv:2606.12290), and budget-aware agent work (BAGEN, arXiv:2606.00198).

## Impact on each V3 matrix row

| V3 row | status after this pass |
|---|---|
| typed / provenance-aware agent memory | **superseded as stated** — MAP-Graph (2608.10509) and provenance-sensitivity auditing (2607.20827) are closer than the cited parents |
| stale-memory / state-revision benchmarks | **directly contested** — STALE and 2608.25553 occupy this row |
| value of information | holds; no new exact-VoI parent found |
| provenance / lineage tracking | **narrowed** — full-path vs last-hop transport remains distinct, but must now be positioned against supersession semantics |
| uncertainty-aware / Pareto decision-making | **most affected** — ORION-08 claims "matched-budget verification … with paired regret against random verification"; 2608.25553 runs matched-budget verification **with a random-record control**. The delta must be re-stated |
| governed / versioned memory | holds; the no-value remint regime has no found analogue |

## What survives — the unique fibre

Absorbing the parent sharpens rather than dissolves the contribution. Three things remain
ORION-08's alone across everything found:

1. **Exact exhaustive verification, not sampled measurement.** ORION-08's
   binding-sufficiency lattice checks **2,233,980 world-action configurations in exact
   rational arithmetic** and returns a proved biconditional — sufficiency **iff** common
   optimal action, refinement never increases risk. 2608.25553 is an empirical study over
   6 models and 5,400 episodes with bootstrap intervals. These are different epistemic
   objects: one proves a condition, the other estimates a rate.
2. **Mechanism identification, which the parent explicitly disclaims.** It states plainly:
   *"It does not identify why native allocation selects what it selects, it does not
   establish mediation"*, and lists "Mechanism of native under-verification not isolated"
   as limitation 9. ORION-08's whole design is mechanism isolation under matched
   information. The parent measures a consequence; ORION-08 isolates a cause.
3. **Cross-family composition.** ORION-08's object is the family-level contract across six
   preregistered studies. Every parent found is single-family.

## Required before submission — not optional

1. Rewrite `NEAREST_WORK_MATRIX_V3.md` → V4 with the rows above, and cite arXiv:2608.25553,
   2605.06527, 2608.10509, 2607.20827, 2606.22528, 2604.20911.
2. Re-state the Pareto/matched-budget delta so it does not read as claiming priority on
   matched-budget verification with a random control.
3. Add the distinction explicitly to `05-related-work-boundary.tex`: **exact exhaustive
   biconditional vs sampled empirical rate**, and **mechanism isolation vs disclaimed
   mediation**. This is the paper's strongest positioning and it is currently unstated.
4. The matrix file is headed **"ORION-04 nearest-work matrix"** while living under
   ORION-08 — legacy numbering that a reviewer will notice. Same defect as ORION-06's
   readiness record.

## Gate disposition

`LITERATURE_CLOSURE_INCOMPLETE__MATRIX_SUPERSEDED`. The gate is **not** closed by this
pass; it is now precisely specified. Nothing found refutes ORION-08's results, and the
exhaustive-exact and mechanism-isolation deltas look durable — but submitting against a
Related Work that predates arXiv:2608.25553 would hand a reviewer the objection.
