# ORION-12 claim ledger describes an abstract that no longer exists

`check_claim_ledger.py` and `check_claim_ledger_v1.py` both report eight
`LEDGER_SENTENCE_MISSING` violations. They are correct, and the drift runs in
the *safe* direction, which is why it is worth stating carefully rather than
quietly repairing.

## What the ledger still asserts

Five claims bound to `abstract` (`ORION-12-C01`, `ORION-12-C02`, `ORION-12-C03`, `ORION-12-C12`,
`ORION-12-X20`) and three to `conclusion` (`ORION-12-C04`, `ORION-12-C05`, `ORION-12-X21`).

`ORION-12-C01` reads:

> In a frozen 390-task complete-gold controlled index, full ORION reaches mean
> recall 0.979487 versus 0.666667 for the strongest protocol-frozen
> confirmatory comparator and makes no premature task closure…

## What the manuscript now says

The live abstract is 1,077 characters and shares no close match with any
stored sentence — best similarity below the 0.3 cutoff for all three abstract
claims tested. It was replaced, not reworded. It now reads, in part:

> A 390-task controlled index is descriptive; external screening does not
> establish superiority. In V7, six locked gates fail and the full candidate
> loses to its frozen u4 donor. V8 admits no residual, and V10 fails four
> gates. V13 validates a provider-native fibre-separating coordinate, but only
> 4/7 reviews support it.

## The direction of the drift

The old ledger records a **superiority** claim: 0.979 recall against 0.667 for
the comparator. The current abstract records the opposite posture — the index
is *descriptive*, screening does *not* establish superiority, six gates fail,
and the candidate *loses* to its donor.

So the manuscript became more conservative and the ledger did not follow. The
stale entries are the residue of a stronger claim the paper has already
retracted in its own prose.

That matters for how this is repaired. A checker reporting eight missing
sentences looks like decay; here it is the guard noticing that the paper
withdrew a claim without withdrawing its ledger entry.

## Why this was not repaired here

The abstract's region spec sets `hard_fail_unledgered: true`, so every claim
the *new* abstract makes must be ledgered too. Repairing this means deriving
the current claim set from the current prose, binding each to evidence, and
deciding for each retired claim whether it is withdrawn or relocated.

That is the paper's claim structure, not a synchronisation task. Rewriting
ledger sentences to match whatever the manuscript now says would make both
checkers green while removing the only mechanism that noticed the paper's
claims had changed.

## Provenance

| artifact | last changed |
|---|---|
| `manuscript/main.tex` | `6474c521` 2026-08-24 — "Integrate unified ORION-11-ORION-15 scientific fronts" |
| `protocol/CLAIM_LEDGER_V1.json` | `7f05258c` 2026-08-24 — "coordinated ledger regen; drop stale abstract duplicate (#1045)" |

The ledger regeneration and the manuscript integration landed the same day,
in that order. The integration moved the abstract afterwards.
