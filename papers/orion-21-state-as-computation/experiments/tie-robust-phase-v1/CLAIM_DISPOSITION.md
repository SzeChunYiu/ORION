# ORION-21 — claim disposition for the phase-boundary claim

**Protocol identity:** `ORION21.TIE_ROBUST_PHASE.v1`
**Authority:** `DIAGNOSTIC_AND_DISPOSITION_ONLY` · `scientific_authority_delta = NONE`
**Controlling terminal of the V1 lane:** `CANNOT_CHECK_INSTRUMENT_DRIFT` — unchanged.

## The tracker's closing condition

> **CLOSE WHEN:** phase-boundary claim has an exact valid run or is removed from the paper.

This document closes it via the **second** branch, and says exactly why the first is unavailable.

## Why "an exact valid run" is not reachable for the V1 ladder

A faithful replay of the registered ladder is impossible. The custody terminal is
`NR07_LUNARC_EXECUTABLE_BYTES_ABSENT`: the original width-law runner bytes are not
committed. Only the **post-outcome-modified** variant survives, in quarantine, and it
differs from the original precisely in the adjudication tolerance that makes it
non-authoritative.

Reconstructing the ladder from the committed P11H generator semantics is possible in
principle, but the result would be a **new prospective measurement**, not a replay — it
could not retroactively validate the registered run. `PROTOCOL.json` in this directory
preregisters exactly that measurement (`ORION21.TIE_ROBUST_PHASE.v1`) for anyone who
wants to establish the phase behaviour afresh.

## Why the point phase-boundary claim is removed

From committed bytes alone (see `DIAGNOSIS.md` and `LADDER_TIE_EXPOSURE_V1.json`):

1. The registered primary quantity is a threshold crossing —
   `n_cross(p)` = smallest ladder train size whose 7-seed mean screening accuracy
   reaches `τ = 0.95`.
2. The frozen scoring rule is **under-specified at ties**: it binds no deterministic
   secondary key, so at an equality boundary it names a *set* of supports, not one.
3. At the anchor measurement the admissible set gives accuracies
   `19438/20480 = 0.94912109375`, `19439/20480 = 0.949169921875` and
   `19476/20480 = 0.9509765625`. Since
   `min = 0.94912109375 < 0.95 ≤ max = 0.9509765625`, the admissible set **straddles τ**.
   By the tie-robustness criterion the conclusion is **not tie-robust**: no
   implementation-specific tie ordering establishes it.
4. Ties are not incidental. Across the ladder, **479 / 1050 = 45.6 %** of (cell, seed, n)
   points have a non-separable support rank gap, and **10 / 10** cells have their
   `n_cross` crossing sitting on tied points.

A point phase label that depends on an arbitrary `argsort` tie-break is not a scientific
result. It is therefore **withdrawn** and replaced by the ambiguity statement below.

## What replaces it

> Under the registered NR07 protocol the phase-boundary label at the measured anchor is
> **not identified**. The admissible accuracies consistent with the frozen scoring rule
> span `[19438/20480, 19476/20480]`, which straddles the registered `τ = 0.95`. The
> protocol does not determine which side of the boundary the cell falls on.

This is a **determinate** statement — stronger than the indeterminate `CANNOT_CHECK` it
replaces, and it is falsifiable: exhibiting a deterministic secondary key that was part of
the registered object, or showing the equality class is a singleton, would overturn it.

## Explicit limits

- This does **not** re-adjudicate the registered width-law study, establish or refute the
  width law, or license any pooled-attack, compiled-defence or P11-gate statement.
- It does **not** claim the phase boundary is *wrong* — only that the frozen protocol does
  not determine it.
- The quarantined post-outcome positive readjudication remains non-authoritative. Widening
  the replay tolerance from `1e-12` to `1e-3` admits the observed `4.88e-05` delta but acts
  on the replay comparison, not the support selection, so it conceals the
  under-specification rather than repairing it.
- It establishes tie **exposure** across the ladder, not that `n_cross` is set-valued
  there. The ladder readings record only the realised selection. The anchor replay and the
  ladder sweep are different instruments and their magnitudes must not be transferred.

## Rescue path

`ORION21.TIE_ROBUST_PHASE.v1` is preregistered in this directory with four terminals
frozen before outcomes. `T1_TIE_ROBUST` would show the crossing is well defined and would
justify reinstating a point claim under the new identity;
`T3_TIE_AMBIGUOUS_VERDICT_CHANGING` would confirm the withdrawal. Both are reachable and
neither is favoured.

## Executed outcome (2026-08-29)

The rescue path has been run, exactly once, under the frozen protocol.

**Terminal: `T3_TIE_AMBIGUOUS_VERDICT_CHANGING`** — the branch that confirms the
withdrawal. LUNARC job `3552796`, `ORION_SOURCE_COMMIT b8fd5d2ca8eb1f6547592893591ba3aa93bf96c8`,
runner exit `0`, independent checker exit `0` with `status: PASS` and exact agreement on the
runner terminal. Raw outputs are preserved verbatim under `result/run-3552796/` and were
verified byte-for-byte against the digests written on the compute node.

T3 fired because two admissible selections yield different verdicts:

| Endpoint | Verdict | `nondecreasing_in_p` | Spearman `n_cross` vs `ln p` |
|---|---|---|---:|
| lo | `C1_LAW_CONFIRMED_REGIME_EXTENDED` | true | `0.9847319278346618` |
| hi | `C4_INDETERMINATE` | false | `0.9509918346667657` |

Coverage: 7,536 candidate prediction streams, 4,351 separable query points, 899 tied query
points, `all_n_cross_point_identified: false`.

Two consequences follow, and only these two.

First, the withdrawal recorded above is no longer resting on an instrument we could not
run. The registered study cannot adjudicate its own hypothesis under its frozen protocol,
and that is now an executed, independently checked finding rather than an absence.

Second, the fourth limit under "Explicit limits" is superseded on its narrow point: the
sweep now does establish that `n_cross` is set-valued on the reconstructed ladder, because
the admissible set was enumerated rather than inferred from a single realised selection.
Every other limit in that section stands unchanged.

Nothing is promoted. `C1_LAW_CONFIRMED_REGIME_EXTENDED` appears at the lo endpoint and is
on the protocol's own `forbidden_promotions` list; the disagreement between the endpoints
is precisely why that endpoint cannot be read as confirmation of the width law. The V1
lane's controlling terminal `CANNOT_CHECK_INSTRUMENT_DRIFT` is unchanged, the quarantined
post-outcome positive stays non-authoritative, and `scientific_authority_delta` remains
`NONE`.

## Requirements on any successor

1. A deterministic secondary tie key, registered as part of the scientific object.
2. Raw ordered predictions and labels retained.
3. An exact integer scorer; no float aggregate.
4. Set-valued reporting: `[min, max]` of the primary quantity over the admissible set.
5. A new protocol identity. The V1 lane remains history and is not reopened.
