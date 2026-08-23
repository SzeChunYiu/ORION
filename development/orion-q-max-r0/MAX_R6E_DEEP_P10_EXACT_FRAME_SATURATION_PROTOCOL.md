# ORION-Q MAX-R6E deep P10 exact-frame saturation diagnostic protocol

Date: 2026-08-21
Parent programme: #679
Authority: open-subject search-responsibility diagnosis only; not R6 and no novelty authority.
Predecessors:
- exact TARE-3 top-four development: exact joint beats canonical TARE but ties `B_FRAME_ONLY_STRONG` on every frozen top-four row;
- verified R6B TARE transformation-reuse donor negative;
- verified R6C canonical-ORION / ORION-Q residual agreement authorizing a new method protocol;
- R6D six-term partition/representation co-optimization remains non-authorizing and cannot weaken this diagnostic.

## Why this diagnostic is required

The exact TARE-3 top-four panel was selected by the earlier candidate-blind P10 ranking, which ranks improvement against the canonical TARE frame. That ranking was frozen before the later exact `B_FRAME_ONLY_STRONG` comparator existed.

Therefore the top-four frame-only collapse does **not** by itself prove that the exact-joint method language is saturated. A deeper P10 row could be less impressive against canonical TARE but strictly improve over the exact frame-only donor.

Before inventing another method-language operation, MAX-R6E tests this search-policy alternative exhaustively on the already-open subjects.

## Frozen subjects

Use only:

- H4 / cc-pVDZ / 2.0au / DUCC3, blob `b98792b1055dbac0ebf2a7576f72412e3e4ac6c5`;
- equilibrium N2 / cc-pVTZ / 6e6o / DUCC2, blob `15369e8e886efbb3d32f3b2dfe2cfbb96ddebeba`.

The stretched-N2 prospective discriminator blob `6ab53f2a83c1f8ab5cc3bf4309525fb1ec7421dd` remains unread.

## Frozen search universe

Replay the unchanged candidate-blind P10 scan exactly:

1. source terms sorted by `(-abs(coefficient), x, z)`;
2. non-overlapping `WINDOW=12` chunks;
3. every three-term combination inside each window;
4. skip direct pairwise-anticommuting triples;
5. compute the strengthened canonical TARE comparator and candidate-blind rank-2 P10 construction;
6. retain a row iff P10 has positive support reduction against that canonical comparator.

No row may be excluded because it is expensive for the exact verifier. The complete P10-improving universe is the diagnostic population.

The expected population sizes from the already-generated P10 receipt are pinned as a consistency check, not a scientific gate target:

- H4: 452 P10-improving rows from 4,812 eligible non-direct triples;
- equilibrium N2: 671 P10-improving rows from 11,132 eligible non-direct triples.

A mismatch aborts the diagnostic as an implementation/state error.

## Exact comparison for every retained row

For every P10-improving triple compute:

- `C_joint` from the frozen hostile-verified exact joint TARE-3 DP;
- `C_frame` from the complete exact `B_FRAME_ONLY_STRONG` donor comparator;
- `delta_exact_vs_frame = C_frame - C_joint`.

Both operate on the identical target triple. The coefficient vector, TARE normalization, block cardinality, five Uanti rotations and two-bit TARE label width are unchanged; this is the same fixed-block comparison as the earlier exact-TARE3 protocol.

Every exact-joint witness and exact frame-only witness used for a strict row must pass reconstruction/cost checks.

## Search-policy ordering and receipts

Serialize, per subject:

- total eligible P10 population;
- all strict exact-vs-frame rows (`delta_exact_vs_frame > 0`), not only a top subset;
- count and fraction of strict rows;
- the first strict row's rank under the original P10 ordering
  `(-p10_fraction, -p10_delta, term_indices)`;
- maximum exact-vs-frame support reduction;
- deterministic best strict rows ordered by
  `(-delta_exact_vs_frame, -p10_fraction, -p10_delta, term_indices)`;
- whether any strict row occurs outside the old top-four and old top-eight panels;
- a SHA-256 digest of the complete retained exact-vs-frame outcome table so negative/equal rows are preserved without truncating the receipt.

The complete table may be emitted as a separate JSON file/artifact; the summary receipt must bind its digest and row count.

## Hostile verification

Before a search-responsibility conclusion may be emitted:

1. reuse the frozen exact-joint hostile exactness panel and require all exact;
2. require the complete P10 population counts to match the pinned prior P10 receipt;
3. deterministically re-evaluate a fixed boundary panel consisting of P10 ranks `0,1,2,3,4,7,8,15,31,last` for each subject and require exact equality to the corresponding full-table rows;
4. recompute every strict row's candidate and frame-only cost from its serialized witnesses;
5. verify full-table SHA-256 from canonical JSON serialization;
6. require the protected stretched-N2 subject to remain unread.

## Responsibility outcomes

This is a diagnosis, not an R6 promotion.

### `MAX_R6E_CURRENT_SEARCH_INCOMPLETE`

Emit only if **both** H4 and equilibrium N2 contain at least one row with

`C_joint < C_frame`.

This falsifies the stronger claim that the exact-joint method language itself was saturated. The next responsibility becomes search-policy / candidate-selection incompleteness. The exact-joint capability remains the incumbent method; no novelty credit is created by finding a better selector.

### `MAX_R6E_PARTIAL_SEARCH_REOPEN`

Emit if exactly one subject contains a strict row. Preserve both paths: search-policy incompleteness on the positive subject and method-language saturation on the flat subject. No prospective access is allowed.

### `MAX_R6E_EXACT_FRAME_SATURATION_SUPPORTED`

Emit only if **neither** open subject contains any strict row across the complete P10-improving universe. This materially strengthens `RESP:METHOD_LANGUAGE_INADEQUATE_AFTER_DONOR_CLOSURE` by ruling out the obvious deeper-search explanation under the frozen P10 alphabet.

All three outcomes keep R6 closed and preserve the entire negative/equal table. No threshold, donor comparator or subject may be changed to obtain a positive sign.
