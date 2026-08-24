# Cross-session P1--P5 update ingestion

**Observed remote main:** `7f7f91931323cb891c323c898888fa81b86a2ac1`  
**Local dirty-wave head:** `1b27b32b7d1dda3793d8247689f81e6c2f78d83d`  
**Policy:** no merge, rebase, reset, commit or push. Import only exact reviewed
blobs or a minimal independently confirmed fix.

## Imported

| Source | Disposition |
|---|---|
| PR 997, merge `6e230946...` | Imported exact P1 `source_frame.py` and its rebound R7A amendment. |
| PR 1005, merge `f3521f6b...` | Imported exact P1 receipt-semantic binding implementation and its regression file. The test file is retained; pytest was not run. |
| PR 1010, merge `877d5060...` | Imported exact P5 V2-default preflight update and its regression file. The test file is retained; pytest was not run. |
| PR 1011, merge `c2535e1a...` | Local 47-item recursive ledger was byte-identical to the repaired remote blob; no rewrite was needed. |
| PR 984, merge `be99f4c9...` | Imported exact P1 floor-effect diagnosis as adverse instrument evidence. It does not replace the new owner-algebra/naturalistic successors. |
| PR 1015, merge `7f7f9193...` | Imported the exact Markdown/JSON negative-revival backlog as a research queue, not as scientific authority. |
| Issue 1003 | Independently confirmed and fixed `_rate_block` so applicability is checked before the denominator. The local inventory already parses with one footer pair, so no inventory regeneration was performed. |

## Not imported

- PRs 1007 and 1013 repair Q/P6--P15 or framework snapshot paths and do not
  supply a new P1--P5 scientific result.
- Claude head `6c4a98d4...` last changed Q-paper paths only. Its untracked P1,
  P3 and P5 material remains outside the provenance contract.
- No old worktree, branch name, ChatGPT narrative or CI status is accepted as
  a result without exact source bytes and claim-boundary review.

## Coordination

Ownership/status messages were sent to ChatGPT tasks `Help Finish Orion Work`
and `Orion Paper Refinement`. They were asked to report exact PR/SHA/path
updates and avoid overwriting this dirty local P1--P5 wave. Future compatible
updates should be appended here before manuscript integration.
