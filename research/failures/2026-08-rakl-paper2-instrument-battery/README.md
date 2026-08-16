# RAKL Paper II instrument-falsifiability battery: four self-refutations

**Observed:** RAKL Structural Mechanics programme (preserved at `SzeChunYiu/RAKL@bd4ce50f`, `publication/papers/paper-02-structural-mechanics/sections/05_instrument_falsifiability.tex`, with artifacts under `research/paper2_six_family_audit_v1/`, `research/paper2_controlled_witness_extraction_v1/`, `research/paper2_prose_transfer_v1/`). Imported as negative history per `provenance/rakl/PAPER_SALVAGE_LEDGER.md`; companion exemplar to `2026-08-rakl-paper4-instrument-negative/`.

## Failure(s)

Four instruments of one programme, refuted in sequence — every negative preserved verbatim:

1. **A gate that passed everything and was non-falsifiable.** A confirmatory extension passed every registered gate (6/6 families, p=0.03125, large paired gain) — then the audit showed one comparison arm *was* the gold function (zero variance), no seed could fail the gate, two thirds of the headline gain was constructed (control arm zeroed by stratum design), and destroying every task text changed nothing: the benchmark contained no extraction problem at all.
2. **A perfect 1.0 that measured serialization fidelity.** The renderer emitted the structural record verbatim and the "extractor" parsed it back — render/extract was the identity map. What survives is deliberately narrower: a valid test of fail-closed parser behavior, preserved as such.
3. **A falsifiable instrument that failed honestly — template inversion.** Built to the repair spec (text-destruction collapses performance; every coordinate a sole discriminator somewhere; two-sided gates frozen pre-outcome), it passed six of seven gates — and failed error-diversity: all 55 errors in the single held-out lexicon class, zero in the other six. Terminal preserved verbatim: `INSTRUMENT_NOT_PROBATIVE__TEMPLATE_INVERSION`. The registered revival spec explicitly rejects the "repair" that would widen cue lists (it would move *further into* template inversion while looking like improvement).
4. **The battery refuted one of its own probes.** The shuffled-gold null, under a proper score over a decision space with abstention, provably measures *differential abstention* (expected advantage = 0.2304·Δr), not label binding — derived arithmetically after two epochs had already been read through it. Repair: restrict to jointly decisive items; validated two-sided with a structurally-independent sha256 arm (no-alarm case first: the original probe false-alarms at abstention 0.4/0.6; the repaired probe clears it at every rate, and still fires on planted leaks including abstention-masked ones). One prior terminal's *reading* withdrawn — the receipt not edited, the governed arms not promoted, re-reading requires a new versioned epoch.

## Failure class

`INSTRUMENT_NOT_PROBATIVE` (three species: gold-arm identity / serialization identity / template inversion) and `PROBE_MEASURES_WRONG_QUANTITY` for case 4.

## Correct response (as executed by the incumbent)

Audit instruments with an executable battery; preserve refuted terminals verbatim; scope surviving claims down rather than deleting runs; when a probe itself is refuted, repair it under two-sided known-answer validation and withdraw only the *readings* that turned on it, in a new versioned epoch.

## General lesson candidates (the battery's design requirements, each traceable to a measured failure)

- No comparison arm may be the gold function; the gate must be failable (exhibit a failing seed).
- Discriminating coordinates sampled, never assigned per stratum; each coordinate the sole discriminator in some stratum.
- Destroying the task surface must destroy performance, comparing the pair (decision, structure signature), never the decision alone.
- False-accept always reported paired with valid-transfer retention (a trivial always-reject arm attains zero false-accepts).
- Error attribution must separate structural difficulty from surface coverage (matched pairs; class-diverse held-out realizations).
- A negative control on a proper score over a decision space with abstention must be restricted to jointly decisive items.
- Turn the battery on itself; a probe validated only by alarms is not validated — assert the no-alarm case first.

These are the incumbent grounding for ORION's host battery + check-admissibility design (`orion.kernel.battery`, `gate.run_discriminating_check`) and the natural source for its next hardening wave (seed-failability and trivial-arm analogues are not yet in the host battery).
