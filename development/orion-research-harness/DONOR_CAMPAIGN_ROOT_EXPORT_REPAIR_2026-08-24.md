# Donor-campaign package-root export repair

Date: 2026-08-24

Frozen base: `284f8a6926a91287c9311812d637d02fd607c565`

Status: **FROZEN BEFORE IMPLEMENTATION**

Authority: Python public API/export consistency only; no scientific result.

## Atomic development question

Can the implemented `build_donor_campaign_manifest` function be exposed through
the package root promised by its tests without changing manifest construction,
campaign execution, or donor authority?

## Reproduced failure

`test_paper_parity_campaign.py` imports the builder from
`orion_research_harness`, but `__init__.py` neither imports nor lists it. Test
collection fails before any donor campaign executes. The implementation already
exists in `donor_campaign.py` and is used internally by `research_lane.py`.

## Frozen implementation hypothesis

1. Import the existing function into the package root and add it to `__all__`.
2. Assert root and module imports are the same function object.
3. Execute the three paper-parity campaign tests to expose, not hide, any next
   runtime failure.
4. Do not alter donor selection, manifests, campaign decisions, receipts, or
   authority fields.

## Honest terminals

- `DONOR_CAMPAIGN_ROOT_EXPORT_REPAIRED`
- `DONOR_CAMPAIGN_EXECUTION_REGRESSED`
- `DONOR_CAMPAIGN_NEXT_BLOCKER_EXPOSED`
- `DONOR_EXPORT_CANNOT_CHECK`

## Reopen triggers

Reopen if root and module identities diverge, the builder signature changes, or
the export repair changes a generated manifest.

## Explicit non-claims

This repair does not validate campaign runtime, execute external donors, grant
scientific authority, or revalidate historical donor receipts.
