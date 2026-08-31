# Corpus-definition triage — where the gap can be repaired, and where it cannot

The artifact-contract audit found `CORPUS_MANIFEST` / `INCLUSION_EXCLUSION`
essentially absent across the portfolio. This says **where a repair is possible
from already-frozen data** and where it is not, so effort goes where evidence
exists.

## Correction first: the earlier denominator was wrong by 45%

The audit's original candidate detector required a results file to *begin* with
`RESULT`. ORION-03 round-2 records its results in `ROUND2_RESULTS_V2.json`, which
does not — so the one study that had just been given a corpus manifest was
being classified as **never executed**.

Matching `RESULT` anywhere in the filename instead:

| | before | after |
|---|---|---|
| candidate studies | 65 | **119** |
| executed studies | 48 | **108** |

So the previously reported figures — "0 of 65", then "1 of 65" — were computed
over a population **45% too small**. Corrected, corpus coverage is **2 of 119**.
The gap is larger than reported, not smaller.

## Triage result

| disposition | studies |
|---|---|
| already defined | 1 |
| derivable from frozen data | 69 |
| **not derivable — no population signal** | **38** |

## This tool emits no manifests, deliberately

It would be easy to auto-write 69 `CORPUS_MANIFEST.json` files from the matched
keys. That would be worthless and worse than the gap it closes.

A key called `total` matching a heuristic is **not** a corpus definition. The
ORION-03 derivation is defensible because each field was read and understood,
and because it **balances against an independent artifact**: `192 parsed = 191
usable + 1 excluded`, cross-checked against `UPSTREAM_TABLE_V2.json`'s 191 rows,
with the single exclusion's reason recorded. None of that is reachable by key
matching.

Auto-emitting would manufacture precisely the evidence the contract exists to
guarantee — a corpus definition that no one derived, asserting a population no
one checked. The 38 blocked studies are the more important half of this output:
**they cannot be repaired at all** from what they recorded, and their honest
disposition is `CANNOT_CHECK`, not a generated file.

## Scope

Triage only. `grants_authority: NONE`. Being listed as "derivable" means a
countable population signal exists, not that a correct manifest will follow —
each still needs the reading that ORION-03 got.

**Terminal:** `TRIAGE_COMPLETE__69_DERIVABLE__38_UNREPAIRABLE__DENOMINATOR_CORRECTED_65_TO_119`
