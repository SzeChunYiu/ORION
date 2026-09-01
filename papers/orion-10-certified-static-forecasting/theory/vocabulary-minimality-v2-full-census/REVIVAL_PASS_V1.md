# ORION-10 fibre criterion — revival pass on `FIBRE_CONSTANCY_REFUTED`

**Terminal: `VOCABULARY_ENRICHMENT_INADMISSIBLE__ONE_SIDED_ENVELOPE_OBSERVED`.**
**Scientific authority delta: `NONE`.** No new instance was generated and no number in
`FULL_CENSUS_RESULTS_V2.json` was recomputed; this is re-analysis of the frozen 740-row
census, and it does not soften the V2 refutation.

## Why this pass exists

A filed negative is an intermediate state, not a stopping point: it owes an attribution
and an attempted improvement before it is left alone. `FINDINGS_V2.md` recorded
`FIBRE_CONSTANCY_REFUTED` with no such path, so this document supplies one — and the
result is that the most obvious path is closed, which is worth more than leaving the
question open.

## Pre-declared success condition

The refutation says cost is not constant on `f_Bprime`-fibres. The standard repair is
vocabulary enrichment: find one additional **Psi-side** feature such that cost *is*
constant on the enriched fibres. That would recover an exact explanation at the price of
a slightly larger vocabulary, which is a positive result about what vocabulary suffices.

A feature qualifies only if it is not computed from cost. Restoring constancy with a
cost-derived key explains cost with cost, which is circular and would be tuning the
outcome positive.

## Enrichment: every candidate in the census is inadmissible

| key | fibres | cost-mixed | admissible? |
|---|---|---|---|
| `f_Bprime` (the refuted criterion) | 7 | 6 | — baseline |
| `f_Bprime + regime` | 23 | 4 | **no** — cost-derived |
| `f_Bprime + gap4` | 11 | 6 | **no** — `gap4 = C_Dxx − min(C_Dplus, f_Bprime)` |
| `f_Bprime + C_Dplus` | 31 | 4 | **no** — a cost |
| `f_Bprime + C_DP` | 21 | **0** | **no** — a cost |
| `f_Bprime + panel` | 54 | 34 | **no** — the instance-family label |

`f_Bprime + C_DP` drives cost-mixed fibres to zero, and that is exactly the trap. `C_DP`
equals `C_Dxx` on all 740 rows, so this key contains the answer. It is reported here so
that the zero is on the record as circular rather than discovered later and mistaken for
a rescue.

`regime` deserves the same explicit treatment, because it is the one candidate that
looks structural. It is not. `run_full_census_v2.py` assigns it from cost relations
alone — `fourth` when `gap4 < 0`, `tie` when `C_Dxx == C_Dplus == f_Bprime`, `split`
when `C_Dxx == C_Dplus`, `borrow` otherwise — and the offset breakdown is correspondingly
degenerate:

```
borrow  offsets {0: 249}
tie     offsets {0: 140}
fourth  offsets {1: 64}
split   offsets {1: 261, 2: 13, 3: 13}
```

Every instance whose offset is 2 or 3 is `split`. That is a restatement of a cost
relation, **not** a structural localization, and it must not be reported as one.

**The refutation therefore strengthens.** It is not an artifact of an under-recorded
vocabulary: among everything the census measured, no admissible feature can rescue
constancy.

## What does survive, stated at its real strength

```
offsets f_Bprime − C_Dxx : {0: 389, 1: 325, 2: 13, 3: 13}
714 of 740 (96.49%) lie in {0, 1}
```

| `f_Bprime` | `C_Dxx` range | width | n |
|---|---|---|---|
| 4 | [4, 4] | 0 | 10 |
| 5 | [4, 5] | 1 | 54 |
| 6 | [3, 6] | 3 | 145 |
| 7 | [4, 7] | 3 | 219 |
| 8 | [5, 8] | 3 | 211 |
| 9 | [6, 9] | 3 | 87 |
| 10 | [9, 10] | 1 | 14 |

`f_Bprime` alone confines `C_Dxx` to at most four values, and the two extreme fibres are
much tighter than that.

**The two sides of this envelope are not equally earned, and collapsing them would
overstate the result.** The upper side, `C_Dxx ≤ f_Bprime`, is the B'-soundness property
the census already checks (`bprime_soundness`, zero hard-assertion failures across 740
rows) — it is theorem-backed, not a discovery here. The lower side,
`C_Dxx ≥ f_Bprime − 3`, has **no proof**: it is an observed envelope over one frozen
census, and nothing in this pass establishes it holds beyond these instances.

## Falsifier, declared before any successor runs

Any admitted instance with `f_Bprime − C_Dxx > 3` refutes the lower envelope. It is a
one-line check against a new census and needs no new machinery.

## Improvement path

1. **Prove or refute the lower envelope.** A bound of `3` on a vocabulary-to-cost offset
   is either a theorem about B' or an accident of this instance space. Deciding which is
   the highest-value next question this lane owns, and it is decidable.
2. **Look for a Psi-side feature outside the recorded set.** The census records only
   `f_Bprime`, three costs, `gap4`, `regime` and `panel`. An admissible enrichment, if
   one exists, is a structural invariant nobody has serialised yet — so the next census
   should record candidate Psi-side invariants *before* outcomes are computed, which
   this one did not.
3. **Do not re-run the census to change this answer.** The 740 rows are frozen, the
   control reproduces QG-7's 64 fourth-regime entries verbatim, and re-tuning the
   criterion against the same instances is exactly the rescue the protocol forbids.
