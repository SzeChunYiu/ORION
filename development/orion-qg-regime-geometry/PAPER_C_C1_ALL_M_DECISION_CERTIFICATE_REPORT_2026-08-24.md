# Paper C / C1 — all-`m` decision-certificate result

Date: 2026-08-24  
Primary owner: `PAPER_C`  
Status: dual-harness accepted under the frozen structural grammar.

## Result

For every number of terms `m>=5`, every Pauli-string length `n`, and every admitted nonidentity Pauli tuple in the frozen partition compiler,

`C_F=C_U`

if and only if both of the following hold:

1. every pair gain is nonpositive;
2. every sum of two disjoint pair gains plus one is nonpositive.

Thus an optimizer over all set partitions has an exact decision certificate whose largest clause touches only four term indices, independent of `m`.

The proof is formulaic rather than enumerative. It derives the exact partition gain, uses matching/cycle sums to control every block of size at least three, uses integrality to collapse arbitrarily many disjoint pair blocks to the two-pair clauses, handles the exceptional single-block formula separately, and gives explicit witness partitions for the converse.

## Sharp lower boundary retained

The same certificate is false at `m=4`. The registered instance

`XXII, XYII, XZII, XIXX`

satisfies every one-pair and two-disjoint-pair clause, but the unary cost is 27 while the single-block optimum is 23. The positive result is therefore stated with the sharp threshold `m>=5`; this adverse instance is part of the result and is not excluded from any denominator.

## Independent corroboration

- Production and generic implementations independently enumerated all 11,628 reorder-quotiented `m=5,n=2` instances. Both found 75 certificate-positive instances, exactly the same 75 unary-optimal instances, with zero mismatches.
- Complete `m=5,n=1` (21 rows) and `m=6,n=1` (28 rows) quotients also had zero mismatches.
- The prior complete `m=6,n=2` parent (38,760 rows) was digest-bound as a regression only, not used as the all-`m` proof premise.
- Native ORION-Q and generic ORION both returned `ACCEPT_EXACT_FROZEN_ALL_M_DECISION_THEOREM`.
- Repeating the complete dual harness produced byte-identical source, generic, and dual receipts.

## Immutable identities

- Protocol SHA-256: `0d7adc323e6addc8018fbb6556d280a8a122f4a1644e2f1bc9a59fc973ecb5f0`
- Source result digest: `455883f266c0294e10e451346c123ed27e1a807ff72312142c7c43bb4c5e3a53`
- Generic verification digest: `a5060a42897d29ce6db722e0be911c158f78a465d1793a8466dca54512a6d00e`
- Native campaign manifest digest: `57f622e23ad4dba219350ab907186e89978f91dfb499307d75f7a3f4770ceec6`
- Dual receipt digest: `e88a137789cd304769450a0486d53072aa9331b28f99e485f3e6ea1f1491796a`
- QG-12 parent file SHA-256: `6b829cf0fa19629522df3c5907fa3c14ac4e49f6c32b4ed1227e486b202a9329`

Positive terminal:

`PAPER_C_C1_ALL_M_GE_5_FOUR_INDEX_DECISION_THEOREM_MACHINE_CORROBORATED__M4_SHARP_COUNTEREXAMPLE`

## Engineering adverse history

The first native attempt stopped before admission because the campaign runner and local executor disagreed on state/decision provenance keys. After that mismatch was repaired, the first rerun exposed two campaign-state persistence roots. Both engineering failures were recorded as `CANNOT_CHECK`, repaired separately in PR #1098, and never interpreted as scientific evidence.

## Remaining authority boundary

This result establishes decision equality only for the equal-weight structural `SELECT+PREP+WIDTH` grammar. It does not determine the exact improvement value or the optimizer witness, does not transfer to other objectives or compiler grammars, and makes no T-count, depth, runtime, qubit, fault-tolerance, physical-advantage, novelty, or venue-readiness claim. Primary-source donor subtraction remains a submission blocker.
