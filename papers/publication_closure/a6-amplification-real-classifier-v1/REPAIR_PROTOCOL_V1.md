# Proposed repair, and the protocol for testing it

**Status at time of writing:** `REPAIR_PROTOCOL_FROZEN__NOT_YET_RUN`
**Scientific authority delta:** `NONE`.

The attack landed. `RESULT_V1.json` records four amplifying edges in the abstract state
space and five realized pairs inside ORION-16's own shipped case set. A finding that stops
there names a hole and leaves it open. This protocol tests a specific repair.

## Where the hole actually is

`classify()` returns `ADMISSIBLE` for exactly one of 256 states — the all-true state. It is
a full conjunction, and by that measure maximally conservative. The amplification does not
come from a loose disjunct. It comes from **two conjuncts that a derivation can satisfy by
absence**: `evidence_transport_known` and `evidence_transport_valid` are both trivially
true of a route that transports nothing.

That is why `C-LEGIT` held. An attack and a genuine repair apply the identical coordinate
delta, and the classifier separates them nowhere, because the state space has no coordinate
recording *why* a flag became true.

## The repair

Add one coordinate, `transport_vacuous`, true when the derivation route transports no
evidence at all. Then require, before `evidence_transport_known` may discharge anything:

```
if transport_vacuous: return "CANNOT_CHECK"
```

placed with the outer unknown layer, which `C-OUTER` already showed to be
amplification-resistant.

`transport_vacuous` belongs to the non-vacuously-satisfiable class. It is a fact about the
derivation route, in the same way `provenance_binding` and `source_current` are facts about
the artifact. A re-grounding cannot set it favourably by choosing a different domain; a
route that transports nothing *is* the vacuous route.

## Predictions, recorded before running

1. Zero amplifying edges survive in the extended space.
2. All sixteen real-case gold verdicts are preserved exactly, because every real case has a
   genuine transport and so defaults `transport_vacuous=False`.
3. The count of legitimate promotion edges is unchanged in kind — the repair removes the
   vacuity route without removing any route that supplies evidence.
4. A discriminating control holds: with `transport_vacuous=True` forced, no state anywhere
   in the extended space classifies `ADMISSIBLE`.

If (2) fails the repair is not adoptable as stated, whatever (1) says.

## The limitation, stated before the result rather than after

The repair does not eliminate trust. It **relocates** it, onto a coordinate that must be
reported faithfully. An adversary who can misreport `transport_vacuous` defeats it exactly
as before. What changes is that the misreport becomes a lie about a fact of the derivation,
rather than a true statement about a vacuously satisfied condition — a fabrication rather
than a loophole. That is a real improvement and it is not a proof of non-amplification, and
the manuscript must say so in those words.

The second limitation is inherited: the mapping of "re-grounding" onto these coordinates is
argued from the papers' definitions in `../A6_AMPLIFICATION_COUNTEREXAMPLE_V1.md`, not
proved. Everything here is downstream of that assumption.
