# Duplicate research-harness boundary detected during ORION-Q R6 campaign

## Observed

ORION-Q initially began implementing a dedicated research-cycle engine under `research/extensions/orion-q/harness/` after diagnosing that one-off R6 scripts were placing too much research-control responsibility on the operator.

A subsequent repository branch search found the materially stronger peer lane `shadow/orion-web-research-harness-20260820`, which already implemented a standalone `packages/orion-research-harness/` around canonical `OrionRuntime`, deterministic host capability receipts, replayable workspaces, brokered external tools, confined local tools and CLI handoff.

## Failure

The initial ORION-Q harness search was scoped too narrowly to the active branch/main tree. It identified the missing orchestration responsibility correctly but failed to search live peer branches before freezing the package location, creating a duplicate-system-boundary risk.

## Failure class

`SEARCH_UNIVERSE_PEER_BRANCH_OMISSION -> DUPLICATE_ARCHITECTURE_BOUNDARY`

## Correct response

- preserve the superseded protocol and this failure record;
- treat the peer harness as the incumbent architecture;
- do not write to the peer branch;
- absorb its package into the active ORION-Q lane with provenance;
- implement ORION-Q only as a domain/campaign adapter under the shared package;
- remove temporary duplicate engine files after useful ideas are migrated;
- strengthen future high-impact development search to include relevant live branches before package/interface freezes.

## General lesson candidate

For repository-level self-improvement, `search nearest work` includes **current peer branches**, not only main, literature, and the active lane. A correct responsibility diagnosis can still yield the wrong implementation boundary if concurrent local knowledge is omitted.
