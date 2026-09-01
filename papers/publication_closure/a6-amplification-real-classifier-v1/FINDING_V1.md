# The amplification attack lands on ORION-16's shipped classifier, and one guard closes it

**Status:** `MACHINE_CHECKED_AGAINST_THE_REAL_SUBJECT__REPAIR_HOLDS_UNDER_A_CONTROLLED_METRIC`
**Scientific authority delta:** `NONE`. Nothing here is a theorem about the world. It is an
exhaustive property check of one classifier plus a proposed guard.

## What was checked, and against what

`IMPLEMENTATION_GAP_V1.md` recorded the fair objection to the first amplification check:
it ran against a model I wrote for the occasion, which is the weakest possible target. This
run imports ORION-16's shipped
`check_real_transition_audit_independent_v1.py` by path, pins it at sha256
`698f49ca…c4db`, and fails closed if it differs. Nothing is copied.

Both protocols and every prediction were committed **before** their runs
(`696fc4ae5` and the two that follow), so no prediction could be adjusted to its outcome.

## Result 1 — the attack lands

`RESULT_V1.json`, verdict `ATTACK_LANDS_ON_INNER_LAYER_ONLY`.

Over all 256 states, `classify()` returns `ADMISSIBLE` for exactly one — the all-true state.
It is a full conjunction and by that measure maximally conservative. The amplification does
not come from a loose disjunct. It comes from two conjuncts a derivation can satisfy **by
absence**: a route that transports no evidence makes `evidence_transport_known` and
`evidence_transport_valid` trivially true.

- **4** amplifying edges: `CANNOT_CHECK -> ADMISSIBLE` by vacuity-only flips.
- **228** legitimate promotion edges, which require a coordinate naming real evidence.
- **0** amplifying edges start from the outer unknown layer. `execution_support`,
  `provenance_binding` and `source_current` are already amplification-resistant. The
  exposure is entirely in the inner layer, and that bound is a result in its own right.

All five pre-declared controls held, including `C-LEGIT`: a genuine repair applies the
**identical coordinate delta** as the attack and lands identically on `ADMISSIBLE`. So the
finding is not that the classifier decides wrongly. It is that **the state space has no
coordinate recording why a flag became true**, and an attack and a legitimate repair are
therefore indistinguishable to it.

## Result 2 — a prediction I got wrong, and it made the finding stronger

Prediction 4 in `PROTOCOL_V1.md` was that no pair among the 24 real cases would realize an
amplifying edge, since the case set was built to exercise families rather than adjacency.

**That was wrong.** Five realized pairs exist, all from `RC-ALIAS-MISSING` — a real case
whose gold verdict is `CANNOT_CHECK` — reaching every one of the five `ADMISSIBLE` real
cases by flipping only the two transport coordinates. Its source is the RO-Crate 1.2→1.3
alias document and its required token is *"RDF consumers to handle previous URIs"*: the
standard did not supply the alias mapping, which is exactly why transport is unknown.

The attack is not a synthetic corner of the state space. It is realized inside ORION-16's
own shipped case set.

## Result 3 — the repair, and the prediction it failed first

The proposed guard adds one coordinate, `transport_vacuous`, true when the route transports
nothing, and returns `CANNOT_CHECK` when it is set.

`REPAIR_RESULT_V1.json` records `REPAIR_FAILS__P1_zero_amplifying_edges_survive`. Four of
five predictions held; four amplifying edges survived. **That receipt stands unedited.**

The diagnosis (`REPAIR_DIAGNOSIS_V1.md`) is that all four survivors sit at
`transport_vacuous = False` on both ends — the route genuinely transported evidence — so
they are the legitimate case, convicted by a metric that could not see the distinction. The
`VACUOUS` list was a constant written before the repair's coordinate existed; once that
coordinate exists, vacuity is a property of the **state**, not of the coordinate. My
protocol-design error, not a defect in the repair.

### A note on two edge counts that look inconsistent and are not

`RESULT_V1.json` reports **4** amplifying edges; `REPAIR_RESULT_V1.json` reports **8**
before the repair. These are the same finding counted over different domains.

The first enumerates the original eight-coordinate space, 256 states. The second enumerates
the nine-coordinate space the repair introduces, 512 states, in which every original state
appears twice — once with `transport_vacuous` false and once true. Each of the four edges is
therefore counted twice. Nothing about the attack changed between the two receipts.

## Result 4 — corrected metric, with the control that matters

`REPAIR_RESULT_V2.json`, verdict `REPAIR_HOLDS_UNDER_CORRECTED_METRIC_WITH_CONTROL`. The
corrected metric was frozen before running, and run against **both** classifiers:

| prediction | outcome |
|---|---|
| metric still detects the attack on the **unrepaired** classifier | **4 edges**, all via the vacuous transport route |
| zero amplifying edges after the repair | **0** |
| all sixteen real gold verdicts preserved | **preserved** |
| no edge amplifies by `obligations_clear` alone | **none**, under either classifier |

The first row is the load-bearing control. Without it a metric that reports zero after a
repair proves nothing, because it may simply have defined the problem away.

## What this does not establish

- ORION-16 nowhere claims non-amplification. It has no authority vocabulary at all. This is
  a gap on the seam between it and ORION-18, not an error either paper committed.
- The repair **relocates** trust rather than removing it. An adversary who misreports
  `transport_vacuous` defeats it exactly as before. What changes is that the defeat becomes
  a fabrication about the derivation rather than a true statement about a vacuously
  satisfied condition. That is an improvement and it is not a proof.
- The repair is checked over this eight-coordinate audit classifier, not over ORION-16's
  full formal core.
- The mapping of "re-grounding" onto these coordinates is argued from the papers'
  definitions in `../A6_AMPLIFICATION_COUNTEREXAMPLE_V1.md`. It is the load-bearing
  assumption of everything above, and it is not proved.

## Why this is the A6 result rather than a bug report

`A6_COMPOSITION_ROUTE_V1.md` argued the top-tier shape is *a mechanism and a normative
constraint, composed, with a proof that the mechanism cannot violate the constraint*. What
exists now is the falsifiable version of that: a mechanism (ORION-16's repair-driven
transition audit), a normative constraint (non-amplification, borrowed from ORION-18's
half of the programme), an exhibited violation realized in the mechanism's own case set,
and a guard that closes it under a metric with a control proving the metric still bites.

Neither donor field produces this. Truth maintenance never asks by what authority a
re-derivation licenses anything; deontic logic never models a mechanism that manufactures
candidate effects. The composition is owned by neither, which was the whole argument for
attempting it.

The honest ceiling: this is a checked property of one classifier and its case set, not a
theorem over the formal cores. Turning it into one is the next piece of work, and it is
now a well-posed piece of work rather than an open question.
