# ORION-10 fibre criterion V2 — full-census witness serialization

**Protocol id:** `ORION10.BPRIME_FIBRE_CRITERION_FULL_CENSUS.v2`
**Status:** `DESIGN_FROZEN` — committed before any V2 output was computed.
**Parent terminal:** `CANNOT_CHECK_FIBRE_CONSTANCY_ON_SELECTED_WITNESSES`.

## The gap is serialization, not knowledge

`check_bprime_fibre_criterion_v1.py` reports:

```
witnesses=64 of 740 evaluated (676 not serialised)
cost-mixed fibres keyed on f_Bprime: 0
offset f_Bprime - C_Dxx uniformly 1: True
terminal: CANNOT_CHECK_FIBRE_CONSTANCY_ON_SELECTED_WITNESSES
```

The V1 packet states the reason precisely, and it is a selection-effect argument, not
a measurement failure:

> the 64 are SELECTED on `C_D++ < min(C_D+, f_B')`, so conditioning on a gap is what
> produces the uniformity. A selection-conditioned sample cannot establish
> fibre-constancy over the space; the 676 unselected instances are the ones that would
> test it.

Zero cost-mixed fibres across 64 selection-conditioned witnesses is **not** evidence
that the vocabulary determines cost. The criterion (certificate-explanation-gap-v1,
Theorem 2) is that an exact Psi-only explanation exists **iff** cost is constant on
every Psi-fibre — a statement over the whole space.

QG-7's `arm1_hostile_search` serialises only `fourth_regime_candidates_verbatim`. The
other 676 instances were evaluated and discarded. **The data needed to decide this
already existed at run time and was not written down.**

## What V2 does

Re-run the QG-7 panel census under a **new identity**, serializing every evaluated
instance's fibre-relevant fields — `f_Bprime`, `C_Dxx`, and the cost keyed on them —
for all 740, not only the selected 64.

**QG-7's frozen result is not modified.** `research/extensions/orion-qg/QG7_BPRIME_COMPLETENESS_RESULTS.json`
is read-only input; V2 writes to this directory under its own schema.

Carried over unchanged from V1: the panel order, `n` values, the dedupe rule, the
replay-confirmation step, and the fibre criterion itself. The only change is **what is
written out**, not what is computed or how.

## Reproduction control, run before any V2 claim

The successor must reproduce QG-7's published aggregates from its own re-run:

- `evaluated` total = **740**
- fourth-regime census total = **64**
- the 64 selected candidates identical to `fourth_regime_candidates_verbatim`

**If those do not reproduce, report `CANNOT_CHECK_CENSUS_DOES_NOT_REPRODUCE_QG7` and
make no fibre claim.** A census that cannot reproduce its parent's counts cannot
adjudicate its parent's open question.

## Terminals

- `FIBRE_CONSTANCY_SUPPORTED_ON_FULL_CENSUS` — no cost-mixed fibre keyed on `f_Bprime`
  across all 740. The Psi-only explanation stands on the real instance space.
- `FIBRE_CONSTANCY_REFUTED` — at least one cost-mixed fibre appears among the 676
  previously unserialised instances. **This would show the V1 uniformity was a
  selection artifact**, which is the outcome the V1 packet explicitly anticipated and
  is a real result, not a failure.
- `CANNOT_CHECK_CENSUS_DOES_NOT_REPRODUCE_QG7` — control fails.

The refutation branch is the one to expect on the V1 packet's own reasoning. It is
declared here so it cannot later be presented as a disappointment.

## Authority

`scientific_authority_delta: NONE` until executed. Grants no claim, alters no ORION-10
terminal, touches no `journal_package/`. A V2 result is successor evidence under a new
identity.
