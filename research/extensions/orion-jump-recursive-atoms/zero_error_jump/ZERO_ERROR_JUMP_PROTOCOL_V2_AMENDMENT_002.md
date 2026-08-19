# Zero-error Jump V2 protocol amendment 002

Date: 2026-08-19

This amendment was made **before the V2 runner repair existed and before any V2 protected outcome was accessed**.

A systematic candidate-visible side-channel audit found three additional protected-class leaks in the initial V2 draft:

1. case IDs inherited `P` versus `C` class markers;
2. positive and control worlds exposed different old-language list lengths;
3. correspondence-obligation / validation-interface cardinalities could differ by protected class.

V2 is therefore tightened so that pre-experiment public structure is class-balanced:

- case IDs are opaque seed-derived tokens with no P/C or family index marker;
- every world exposes exactly 8 old-language public hypotheses;
- every world exposes 3 opaque objects, 2 relations, 4 public observations, 2 open discriminator IDs, 2 equal-cost `REGISTERED_PROBE` options, 2 correspondence obligations, and 2 validation interfaces;
- control probe outcomes do not include control-family identity.

The positive/control family counts, seeds, old-language full-contract status, representation moves, protected consequence semantics, strong-parent budget, parent-vs-ORION hypothesis, and candidate terminal are unchanged.
