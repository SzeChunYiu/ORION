# V5 result — fibre constancy is refuted, and the uniformity was selection

**Status:** `FIBRE_CONSTANCY_REFUTED_ON_UNSELECTED_POPULATION`
**Scientific authority delta:** `NONE`. `promotes_no_claim` continues to hold, as in V1.

V1 terminated `CANNOT_CHECK_FIBRE_CONSTANCY_ON_SELECTED_WITNESSES` and named its own
remedy: serialise `f_B'` and `C_D++` for the unselected instances and re-run the grouping.
The V4 run's committed receipt carries 13,458 such rows, so no new computation was needed.

## The answer

Nine `f_B'` fibres. **Seven carry more than one cost.**

| `f_B'` | costs `C_Dxx` observed, with counts |
|---|---|
| 5 | 4 ×32, 5 ×255 |
| 6 | 3 ×7, 4 ×11, 5 ×229, 6 ×1008 |
| 7 | 2 ×1, 3 ×5, 4 ×40, 5 ×77, 6 ×783, 7 ×2099 |
| 8 | 4 ×3, 5 ×55, 6 ×101, 7 ×1275, 8 ×2591 |
| 9 | 6 ×70, 7 ×82, 8 ×1314, 9 ×1773 |
| 10 | 7 ×27, 8 ×21, 9 ×726, 10 ×612 |
| 11 | 8 ×5, 10 ×138, 11 ×80 |

Cost is not constant on the Ψ-fibres. By the criterion V1 quotes — an exact Ψ-only
explanation exists **iff** cost is constant on every Ψ-fibre — no exact Ψ-only explanation
exists over this population.

## The uniformity was the selection, demonstrated rather than asserted

V1 saw `f_B' − C_Dxx = 1` in all 64 of its witnesses and could not tell whether that was a
fact about the population or about the predicate that chose them.

Applying V1's own predicate, `C_Dxx < min(C_D+, f_B')`, to the full census selects **583**
rows. Within those 583:

- every fibre carries exactly one cost — **zero** inconstant fibres;
- `f_B' − C_Dxx = 1` in **all 583**;
- `C_D+ − C_Dxx = 1` in **all 583**.

Which is V1's result exactly, reproduced at nine times the sample size. Among the 12,875
unselected rows, all seven inconstant fibres appear. The predicate manufactures the
uniformity, and it does so perfectly.

Over the whole census the same offsets spread out:

| offset | distribution over 13,458 rows |
|---|---|
| `f_B' − C_Dxx` | 0 ×8444, 1 ×4509, 2 ×292, 3 ×204, 4 ×8, 5 ×1 |
| `C_D+ − C_Dxx` | 0 ×8152, 1 ×4785, 2 ×521 |

## One of V1's three observations survives, and it is worth separating

`C_DP − C_Dxx = 0` holds in **13,458 of 13,458** rows, not merely in the selected ones.
`C_DP = C_Dxx` is a population fact and not an artefact.

So V1's three observations do not stand or fall together: two were produced by the
selection, one was not. Reporting them as a single "exact and uniform relationship", as V1
does, blurs that, and the distinction is the useful part of this result.

## The prediction, and what it was

`PROTOCOL_V5.md` was committed before the computation and predicted
`FIBRE_CONSTANCY_REFUTED_ON_UNSELECTED_POPULATION`, with a secondary prediction that the
violations would sit in the unselected rows while the selected ones continued to look
uniform. Both hold. The primary prediction was the one that could have been wrong: had the
full census also shown constancy, the selection would have been harmless and the criterion
met.

## What this does and does not settle

It settles V1's `CANNOT_CHECK` in the direction V1 suspected, over the frozen unit-cost R6M
grammar and the ten registered panels. It says nothing about all `n`, promotes no claim,
and moves no other terminal.

It does not answer the separate V3 question about the offset-3 envelope and the prefix
control, which `PROTOCOL_V4.md` declared and the V4 runner does not report. That remains
open and is recorded as open in `../vocabulary-minimality-v4-per-panel-dedupe/RESULT_V4_2026-09-01.md`.
