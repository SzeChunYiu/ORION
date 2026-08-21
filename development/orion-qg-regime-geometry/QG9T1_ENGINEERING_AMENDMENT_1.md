# QG-9 T1 engineering amendment 1 — candidate-validity filtering

Date: 2026-08-21
Original frozen head: `312cf6dd320e65308315cdbc4208aa1d2224b446`
Failed workflow run: `32494677146`

The first protected execution produced **no cap-3 result artifact and opened no candidate cap-3 score**. It stopped during candidate generation because one anchored obstruction slice had a valid selected-generator label but the complete n=4 desired block had invalid ordered Tag labels. The frozen protocol already required: “retain only candidates whose desired two-block frame/Tag configuration passes the production witness semantics.” The implementation raised instead of applying that filter.

This amendment changes only execution of that pre-frozen gate:
- inspect the same first 36 obstruction slots per orientation in the same canonical order;
- build the same minimum-Tag realization and minimum-Uanti compatible second block;
- **skip** a desired candidate when the full n=4 block labels are not nonzero/distinct or any other frozen feasibility check fails;
- do not backfill beyond the first 36 obstruction slots;
- accepted panel therefore remains nonempty and <=36/orientation, <=72 total, exactly as the protocol’s “72 maximum” language permits.

Unchanged: obstruction grammar, ordering/cap, inverse-design target template, exact MILP, 54 fixed configurations, early rejection, tightness inequality, independent verifier, authority rules.

The old failed run is retained as an engineering record. It grants no scientific terminal.
