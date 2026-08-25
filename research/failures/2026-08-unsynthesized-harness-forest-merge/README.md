# Harness forest merge retained mutually incompatible contract fragments

**Observed:** 2026-08-25 in the `engineering-conformance` job for the ORION
execution-takeover lane: 16 failures with 431 passes.

## Failure

The merged harness contained individually motivated but unsynthesized contract
fragments from different development lanes:

- strict campaign tests survived while strict manifest validation,
  `shadow_control`, and typed contract-failure handling had been overwritten;
- the runner retained three consecutive timeout clamps from three different
  designs, so the final 900-second assignment silently overrode both the
  120-second compatibility helper and the committed 7,200-second bound;
- a shell-safety test contained the same setup and execution body twice;
- a terminal campaign cycle carried its terminal and state, while the enclosing
  run projection dropped both;
- the X1-A test named a field that had never existed in the incumbent revision
  report;
- the C15 audit bound the correct Git blob but searched for a token not present
  in those exact bytes;
- the X1-B K4 result exceeded the default bounded output capture, truncating its
  JSON token into an unparsable receipt.

No single scientific outcome caused this family.  The failures occurred at
serialization, validation, resource, and test-integration boundaries.

## Failure class

`UNSYNTHESIZED_CONTRACT_FOREST_MERGE`

Passing fragments from multiple branches were concatenated or overwritten
without an end-to-end contract reconciliation.  Later assignment order and
stale projections silently selected which fragment was live.

## Correct response

1. Reproduce every failure against the isolated merged checkout.
2. Restore strict, non-mutating campaign contract failures and the shadow
   decision projection.
3. Keep one timeout authority, bounded at 7,200 seconds, with compatibility for
   the legacy environment name.
4. Keep default process output bounded and permit an explicit, bounded larger
   capture only for campaigns whose valid receipt is larger.
5. Project terminal/state/error fields from the final cycle to the enclosing
   campaign run.
6. Repair stale tests and token checks only where live source/blobs prove the
   asserted interface or token never existed.
7. Re-run the complete harness, not only each branch's original focused tests.

## General lesson candidate

A branch forest cannot be integrated by file presence or green source-branch
tests alone.  Where multiple lanes touch one contract, integration must enumerate
the live authority for each field, environment variable, clamp, projection, and
terminal, then execute an end-to-end hostile suite over the synthesized result.
This is engineering conformance only and creates no scientific or publication
authority.
