# P1-X Protected Outcome Access Receipt V1

Date: 2026-08-19  
Parent issue: #529  
Execution branch base: `main@ae6ee89faa4ba5de8d03509753b406ef32eb5c7d`

## Pre-access frozen identities

- merged protocol: `40efb8478ffc164ef844fd5c3f17e8d2ed8f49aa`;
- protected identity freeze: commit `e19b6a5978fcfd9d6c77e581627fa139a943e1b1`;
- contamination exclusions: commit `2a1b81e26209b892a6611f5d4e2b79eb77b266c5`;
- controller/scoring implementation: commit `0953e0d17f610aceb4d9fc885eb792d0d231b813`;
- protected generator: commit `2c2cb761fc8e321e1af3e8bfec8b7130c6e4d727`;
- dev-only controller tests: commit `c1b5114aa50bb4a62e2b99ddb8d656dec24b0101`;
- protected analysis implementation: commit `60938ac18e0070f1d673b000d0a51ce9c342dea7`;
- dev preflight: commit `194a58202cd246f0bc980fd71fb8ef44a0fabda3`.

## Pre-access state

- protected case identities committed: **YES**;
- protected gold generated/accessed by candidate/controller development before this receipt: **NO**;
- protected aggregate results known before this receipt: **NO**;
- controller semantics frozen: **YES**;
- primary `+0.10` margin frozen: **YES**;
- non-regression margins frozen: **YES**;
- analysis/statistics frozen: **YES**;
- B3 equivalence boundary frozen: **YES**.

## Authorized next operation

Generate the complete 400-case protected bundle once from the frozen generator, execute all four frozen arms on exactly the same bundle, and run the frozen analysis without deleting or changing cases.

From this receipt onward, any change to controller semantics, protected generator mechanics, ESRD, margins, comparator definitions, or analysis rules requires a new V2 protocol and leaves V1 results immutable.

Terminal: `PROTECTED_OUTCOME_ACCESS_AUTHORIZED_V1`.
