# Campaign provenance-key binding — engineering amendment 1

Date: 2026-08-24  
Parent protocol: `CAMPAIGN_PROVENANCE_KEY_BINDING_REPAIR_2026-08-24.md`  
Status: frozen after the first focused repair run and before store rebinding.

## Reopen trigger hit

After admitting the two missing provenance digests, the toy campaign reached the controller's `TERMINAL` outcome. The protocol's required terminal-state load check then failed: `ResearchWorkspace.load_latest_campaign_state(...)` returned `None`.

Inspection found two concurrent persistence roots:

- `CampaignStore`, used by `campaign_runner`, writes manifests/states/cycles under `.orion-harness/campaign-control/`;
- the public `ResearchWorkspace` campaign methods read and write `.orion-harness/campaigns`, `.orion-harness/campaign-states`, and `.orion-harness/campaign-cycles`.

Both implementations use the same SHA-256 campaign keying, immutable create semantics, cycle indexing, and content-digest cycle names. The split is path identity, not a serialization difference.

## Amended minimal hypothesis

Keep `CampaignStore` as the campaign runner's hardened interface, but bind its three paths to the existing public workspace directories. Do not dual-write and do not add a fallback search order: either would create two candidate latest states and make replay identity ambiguous.

## Required checks

1. the campaign runner reaches `TERMINAL`;
2. `CampaignStore.latest_state` and `ResearchWorkspace.load_latest_campaign_state` return byte-equivalent terminal state objects;
3. immutable state/cycle publication tests still pass;
4. no result is relabelled scientific evidence.

## Authority boundary

This amendment repairs one persistence identity boundary. It adds no authority beyond the parent protocol.
