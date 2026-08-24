# Campaign publication-contract binding repair

Date: 2026-08-24

Frozen base: `6b6b5390053504a4525b6857bfe3ab425034fda0`

Status: **FROZEN BEFORE IMPLEMENTATION**

Authority: harness contract/API consistency only; no scientific result.

## Atomic development question

Can the Q3 publication contract bind the campaign protocol that is actually on
current main without weakening the all-false authority checks or changing any
serialized campaign schema?

## Reproduced failure

`publication_contract` imports public campaign schema constants that were
renamed to private constants by the later paper-parity forest integration. Its
source-binding checks also look for the former helper names
`_require_authority_false` and `_authority_false`, while the current protocol
implements the same checks as `_authority_must_be_false` and `authority_false`.
Package import therefore stops at `CAMPAIGN_DECISION_SCHEMA`.

## Frozen implementation hypothesis

1. Re-export the three unchanged schema strings under their established public
   names; retain the current private names and serialized values.
2. Point publication-contract source checks at the helper names used by current
   main rather than renaming or weakening the implementation.
3. Test all six authority fields, schema values, the publication contract, and
   a fresh package-root import boundary.
4. Do not change campaign record fields, digests, transitions, decisions,
   custody, or authority values.

## Honest terminals

- `CAMPAIGN_PUBLICATION_CONTRACT_REBOUND`
- `CAMPAIGN_AUTHORITY_GUARD_REGRESSED`
- `HARNESS_PACKAGE_IMPORT_STILL_BLOCKED`
- `CAMPAIGN_BINDING_CANNOT_CHECK`

## Reopen triggers

Reopen if a serialized schema changes, any authority field can be true, the
publication contract stops inspecting the actual methods, or package import
again fails at campaign-contract binding.

## Explicit non-claims

This repair does not validate campaign science, historical campaign receipts,
the dual harness, or Q3 publication claims. It only reconnects a mechanical
contract to semantically equivalent names on current main.
