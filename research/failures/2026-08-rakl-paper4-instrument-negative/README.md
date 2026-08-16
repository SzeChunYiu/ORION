# RAKL Paper IV v1: the canonical instrument-negative exemplar

**Observed:** RAKL Structural Learning Mechanics programme, v1 Phase-0/1 execution (preserved at `SzeChunYiu/RAKL@bd4ce50f`, `publication/papers/paper-04-structural-learning-mechanics/`, esp. `GENERATOR_DEFECT_CORRECTION.md`, `STRICT_CLOSURE_ADDENDUM_20260814.md`). Registered here per `provenance/rakl/PAPER_SALVAGE_LEDGER.md` obligation 2 — imported as negative history, not as ORION's own episode.

## Failure

The executed v1 Phase-0/1 diagnostic was invalidated by a **generator defect**: the instrument that produced the training/evaluation cases was itself broken, so the run cannot support the mechanism inference it was designed for — in either direction.

## Failure class

`INSTRUMENT_NEGATIVE` — the run refutes the *instrument*, not the *mechanism*. RAKL's own governance froze the packet as immutable negative instrument history with an explicit rule: it "cannot be reinterpreted as a mechanism negative" (`publication/PUBLICATION_SERIES_V2.md`), and the paper's status is `DESIGN_PROTOCOL_WITH_INVALIDATED_V1_DIAGNOSTIC` — the preregistration stays useful, the executed evidence does not.

## Why this is the canonical exemplar

It exercises, on a real programme, three contracts ORION now carries:

1. **Instrument-vs-mechanism attribution** (`DIAGNOSE.ATTRIBUTION.v0` answer record): infrastructure/instrument causes must be excluded before any mechanism-level attribution; here the attribution correctly stopped at the instrument.
2. **Monotone negative history**: the invalidated packet is preserved immutable, addressable, and scope-bound — neither deleted nor averaged into later results.
3. **No silent status inflation**: the conditional paper does not fall back to weaker claims; repaired-instrument execution (`#462`-gated in RAKL) is required before any residual/capability conclusion, and if rejected, supported fragments migrate under a *versioned* migration rather than a fabricated result.

## General lesson (already load-bearing in ORION)

A negative result inherits the weakest link of its measurement chain. Before a failed run may update beliefs about a mechanism, the instrument must be independently validated on known-answer cases — and when it fails validation, the honest verdict class is `INSTRUMENT_ATTRIBUTED` with the target question reopened, never `REFUTED`. This is the incumbent grounding for the kernel's distinction between a check that is `NOT_SOUND` (rejects its own positive fixture) and a check that `FAILED` on its target.
