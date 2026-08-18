# Governance freeze, cycle receipts, epochs (preparatory)

**Status:** `PREPARATORY_AWAITING_ACTIVATION`. Sibling to the `#276`
`docs/06-programme/` protocol index. This page documents the Step-3/4/6/7
*shapes* added after that pre-registration. It grants no authority.

## Governance freeze

`orion.programme.governance.repository_governance_freeze` emits a sealed
document covering objectives, queue policy, exploration/exploitation, budget
ceilings, stop rules, held-out refresh, evaluator custody/versioning, search
contamination, and halt/revert. Host identities stay the unbound SHA-256
sentinel. `freeze_in_force` is false.

## Cycle protocol and receipts

Nine steps (`P4-C1` … `P4-C9`) are listed by identity. Worker custody is
confined to delegation; protected evaluation stays outside candidate custody.
`CycleReceipt.decision` defaults to `CANNOT_CHECK`. `PASS` without bound
replay, fresh-transfer and assurance hashes is refused.

## Epochs, longitudinal claims, archival

Epoch manifests and programme receipts must be empty. Longitudinal assessment
returns `CANNOT_CHECK` at zero epochs and never `PASS`. The archival strategy
is a policy document with `live_archive_populated: false`.

## Activation lock

`orion.programme.activation.activation_authorized` is hardwired false. A test
fails if a `p4-programme*`, `p4-epoch-manifest*` or `p4-anti-collapse*` YAML
file reappears under `.github/workflows/`, or if `src/phase4/` is created.
