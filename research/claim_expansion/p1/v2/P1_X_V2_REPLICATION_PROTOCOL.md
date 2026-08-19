# P1-X V2 disjoint replication protocol — comparator fairness repair

Date: 2026-08-19  
Parent: #529  
Predecessor result: `results/P1_X_PROTECTED_RESULT_V1.json`  
Status: `V2_FROZEN_BEFORE_V2_OUTCOME_ACCESS`

## Reason for V2

V1 is immutable and records a material post-access comparator implementation defect `P1X-V1-D001`: B1/B2 iterate status-map keys rather than values in one clean `NO_CHANGE` guard. V2 does not rewrite V1. It prospectively repairs that implementation defect and executes on a new disjoint protected identity set.

## Scientific invariants retained from V1

Unchanged:

- research question and novelty boundary;
- five domain families;
- eight responsibility archetypes;
- 400 protected cases (`5 x 8 x 10`);
- candidate/protected field separation;
- P1-X decision semantics;
- B3 ideal-product equivalence semantics;
- ESRD primary outcome;
- P1-X minus B1 `+0.10` practical margin;
- 95% domain-stratified bootstrap lower-bound requirement `> 0`;
- lower-level `-0.02`, false-reframe `+0.02`, zero-invariant-violation, and per-domain `>-0.05` non-regression gates;
- exact McNemar and Holm secondary analyses;
- no inherent-expressivity claim.

## Only controller repair

B1 and B2 replace the V1 predicate

`all(status == "UNTESTED" for status in statuses)`

with

`all(status == "UNTESTED" for status in statuses.values())`.

No other B1/B2 policy is changed. P1-X/B3 code is reused byte-for-byte from V1.

## Disjoint protected replication

Namespace: `P1_X_PROTECTED_V2_REPLICATION_2026-08-19`.

Case IDs use `P1X-V2-PROTECTED-{DOMAIN}-{ARCHETYPE}-R{01..10}` and therefore do not overlap V1.

To avoid reproducing V1 proposal ordering verbatim, V2 deterministically rotates each case's candidate proposal order by a SHA-bound offset derived from the precommitted case seed. Replicates 9--10 retain the protected unauthorized-success decoy family, but the candidate order is seed-permuted rather than simply reversed.

The scientific gold rules remain the frozen eight archetypes; order/identity perturbations must not change the correct decision.

## Stop rule

V2 is the final comparator-fair replication for #529 unless an independent verifier finds a new material implementation/scoring defect. If V2 passes the primary/non-regression gates and independent verification, the wider P1 claim may be promoted only at the bounded exact heterogeneous-contract scope. If it fails, #529 narrows/ends at the corresponding V2 terminal.

Terminal: `P1_X_V2_REPLICATION_FROZEN__NO_V2_OUTCOMES_ACCESSED`.
