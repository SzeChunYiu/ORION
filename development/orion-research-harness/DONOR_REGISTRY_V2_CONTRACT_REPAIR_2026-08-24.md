# Donor registry v2 campaign-contract repair

Date: 2026-08-24

Frozen base: `9805f309b923e17a68905e004e7898733197c7b6`

Status: **FROZEN BEFORE IMPLEMENTATION**

Authority: test-to-current-registry identity consistency only; no scientific result.

## Atomic development question

Do the donor-campaign tests bind the full registries actually selected by
`PaperParityNavigator`, rather than the superseded base-registry v1 identities?

## Reproduced failure

The donor-campaign builder delegates to `PaperParityNavigator`, whose normal and
ORION-Q full registries are `orion:donors:normal:v2` and
`orion:donors:orion-q:v2`. Navigation and runtime tests already bind those exact
identities. Two campaign tests alone still assert v1 and stop before campaign
execution.

## Frozen implementation hypothesis

1. Change only the two expected registry IDs from v1 to v2.
2. Leave registry selection, contents, digests, manifests, capability counts,
   campaign execution, and authority fields unchanged.
3. Run the complete paper-parity campaign test file and record any next failure
   without adjusting its expected outcome post hoc.

## Honest terminals

- `DONOR_REGISTRY_V2_CONTRACT_REPAIRED`
- `DONOR_CAMPAIGN_NEXT_BLOCKER_EXPOSED`
- `DONOR_REGISTRY_IDENTITY_REGRESSED`
- `DONOR_REGISTRY_CONTRACT_CANNOT_CHECK`

## Reopen triggers

Reopen if `PaperParityNavigator` changes registry identity, if manifest registry
IDs diverge from its plan, or if a registry version is changed without a donor
surface change and independent test update.

## Explicit non-claims

This repair does not establish donor completeness, execute an external donor,
validate campaign runtime, or grant scientific/publication authority.
