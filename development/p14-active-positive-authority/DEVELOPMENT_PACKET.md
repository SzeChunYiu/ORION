# P14 active positive authority — development packet

Base: `claude/papers-1-10-issues-uqrj2o@fd9892fdafd7734b07c8b24a4384c9e9561b1349`
Status: `ADDITIVE_LIFECYCLE_ADJUDICATION`

## Defect

P14C is the current, replay-authoritative positive controlled result and answers
P14A's question at P14A's unchanged thresholds. P14A remains an immutable
historical receipt whose bars were outside its own sampling support. A raw
terminal scan nevertheless surfaces P14A as if it were the current paper result.

## Repair

- add one machine-readable active-authority record;
- bind it to the P14C result, replay adjudication and gate-attainability audit;
- record P14A only as immutable adjudicated history, not active claim authority;
- pin every referenced artifact by SHA-256;
- leave every historical artifact byte-identical.

## Acceptance

The active P14 scientific terminal is positive and replay-authoritative; the
P14A file remains present with its original digest; P14C's unchanged-threshold
resolution remains present; and hostile P14 tests stay green.
