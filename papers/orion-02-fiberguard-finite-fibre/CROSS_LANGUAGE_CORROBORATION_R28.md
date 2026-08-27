# ORION-02 R28 — structurally independent Rust corroboration

Date: 2026-08-27

Terminal:

`ORION02_R20_RUST_CROSS_LANGUAGE_CHECKER_PASS`

## Independence boundary

`verify_r20_cross_language.rs` is a standard-library-only Rust implementation. It does not import an ORION Python module, does not use a Python-generated parser, and does not depend on an external Rust crate. It parses the durable R18 recovery result and current-main R19 result directly, rechecks their authority ceilings, and independently recomputes theorem-critical finite controls.

This is structural code independence and language independence under the same research owner and repository custody. It is not external independence.

## Recomputed controls

The checker verifies:

- the R18 null terminal, 99-candidate denominator, zero feasible development candidates, zero route coverage on all three panels, equality of routed and full learned means, and full learned improvement over the no-feature fallback;
- the R19 `35 -> 70` invalid-shortcut counterexample;
- identical learned/fallback marginals with full-pair randomized value 0 and diagonal-only value 50;
- route-observation ranking reversal;
- acquisition-timing route reversal;
- 1,000 deterministic witness-compression systems;
- 700 no-free-extension constructions;
- 33,824 exact fallback-alignment identities;
- 696 finite lower-boundary families, 484,416 ordered comparisons, and 15 nonnegative linear monotone objectives.

The Rust result is deterministic under one source subject and is executed twice byte-identically before any durable receipt is published.

## Authority

The Rust checker increases confidence that the Python theorem and result machinery has not shared one parser or implementation bug. It does not supply peer review, a new empirical subject, independent institutional custody, a novelty opinion, production evidence, or journal authority.

Current authority:

- cross-language implementation corroboration: true;
- same-owner structural independence: true;
- external independence: false;
- novelty: not established;
- journal authority: false.
