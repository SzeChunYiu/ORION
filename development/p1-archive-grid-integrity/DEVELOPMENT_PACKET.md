# P1 archive Cartesian-grid integrity — development packet

Date frozen: 2026-08-22
Branch: `codex/p1-r7-wide-successor`
Authority: archive-integrity repair only; no scientific score or terminal is changed.

## Development question

Can the P1 table pipeline prove that every frozen system × case × seed record exists exactly once, rather than checking repeat counts only for groups that happen to remain in the archive?

## Atomic questions

1. Can the expected test systems, cases, seeds, suite fingerprint, and subject revision be bound outside the archive being checked?
2. Does loss of a complete system, case, or system×case group become archive-level `CANNOT_CHECK`?
3. Does a duplicate seed replacing another required seed fail even when the row count remains five?
4. Are unexpected identities rejected?
5. Are missing case identities blinded in publication-facing blockers?

## Negative history and saturation

The incumbent checker rejects 4/5 repeats but accepts 0/5 because absent groups never enter its count map. Replays also showed whole-system loss, whole-case loss, and seeds `[0,1,2,3,0]` all remain coherent. Exact Cartesian manifest validation is sufficient; inferring the grid from the archive is not, because the missing dimension could disappear completely.

## Frozen implementation hypothesis

Binding the immutable expected design in a sidecar and requiring each expected `(system_id, case_id, seed)` tuple exactly once will convert every structural archive hole into explicit `CANNOT_CHECK` without changing any score in the complete archive.

## Hostile tests and reopen triggers

Tests delete all five repeats for one cell, delete a whole system, delete a whole case, replace one seed with a duplicate, and introduce unexpected identities. Reopen if a valid execution legitimately has a non-Cartesian design; it must then bind an explicit tuple list rather than weakening exactness.

