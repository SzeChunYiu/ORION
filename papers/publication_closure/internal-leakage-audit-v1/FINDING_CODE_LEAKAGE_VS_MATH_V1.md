# Internal codes in rendered PDFs: what is leakage and what is mathematics

A scan of every rendered PDF for `P<n>` / `Q<n>` / `E<n>` tokens flags **17 papers**, with counts up to 57 (ORION-15) and 27 (ORION-12, ORION-14). Treating that scan as a leakage list would be wrong, and acting on it with a blanket substitution would corrupt published mathematics.

## The collision

ORION-14 renders:

> `TV(P0, P1) = sup_{B in F_O} |P0(B) - P1(B)|`

`P0` and `P1` here are **probability measures**, and this is the definition of total variation distance. The same paper separately renders `The P4-X exact-contract successor`, where `P4` is the paper's own internal identifier. One token pattern, two meanings, in one document.

A regex that strips `P<n>` fixes the second and destroys the first.

## Classification actually applied

Only prose that refers to the paper *as a programme item* is leakage:

| pattern | verdict |
|---|---|
| `not a P5 novelty` | leakage — self-reference |
| `is not a P5 dossier/eight-class task adapter` | leakage — self-reference |
| `TV(P0, P1)`, `measure P1 - P0` | **mathematics — keep** |
| `Case P5-HC002` | data label — keep; renaming would break traceability to the case record |

Repaired in ORION-15: `not a P5 novelty` to `not a contribution of this paper`, and the dossier sentence likewise. Verified in the re-rendered PDF: 0 occurrences.

## What is deliberately left

The remaining flagged tokens across ORION-12/14/17/18 and others did not resolve to prose self-references on inspection. They are section labels, case identifiers, table keys and mathematics. Each needs reading in context; the scan is a candidate generator, not a verdict.

## Rule this establishes

A corpus-wide token scan is a **candidate generator**. Before any substitution, the token must be read in its rendered context and classified. The cost of getting this wrong is asymmetric: a missed internal code is an embarrassment, while a corrupted probability measure is a retraction.
