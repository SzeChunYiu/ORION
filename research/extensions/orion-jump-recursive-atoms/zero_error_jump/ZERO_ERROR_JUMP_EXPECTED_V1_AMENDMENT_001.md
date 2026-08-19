# Zero-error Jump expected-count amendment 001

Date: 2026-08-19

This amendment was made **before any benchmark runner or scoring implementation existed and before any protected outcome was accessed**.

The initially frozen expected table set `OVERJUMP_ALWAYS.unresolved_or_rejected = 14`. A consistency audit of the already frozen family counts showed this was arithmetically incompatible with the declared arm semantics:

- 24 positive cases total;
- `OVERJUMP_ALWAYS` always proposes `BRIDGE_CORRESPONDENCE`;
- only the four A-family positive cases have that gold move;
- therefore 20 positive proposals are structurally invalid and must be rejected/unresolved.

The corrected expected value is **20**. No seed, world family, comparator, move library, success gate, terminal, parent-vs-ORION hypothesis, or any other metric changed.

This note is preserved as pre-outcome design history; the runner must bind the corrected JSON and may not silently reinterpret either version after outcomes.
