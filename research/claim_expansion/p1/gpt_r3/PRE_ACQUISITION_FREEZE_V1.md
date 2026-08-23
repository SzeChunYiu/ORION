# P1-U GPT-R3 pre-acquisition freeze V1

Parent: #649  
Campaign: #716  
Base: `main@8c6a2d56b0ddcea24667da97df4445df5c714dae`

Scientific freeze commit: `ffc1e03e30deaa38dcfe682a8d52e7cb6d44728a`.

Frozen before any 2022 acquisition query was executed:
- `development/p1-u-gpt-r3-source-universe/DEVELOPMENT_PACKET.md`;
- `research/claim_expansion/p1/gpt_r3/SOURCE_UNIVERSE_PLAN_V1.json`;
- `research/claim_expansion/p1/gpt_r3/evaluate.py`;
- `tests/unit/p1/test_p1_u_r3_source_universe.py`.

Candidate/comparator policy remains byte-owned by merged R2 under `research/claim_expansion/p1/gpt_r2/` and is not modified by R3.

## Freshness/contamination ledger

R3 primary sources must be published in calendar year 2022. Replication, if reached, uses 2021.

Ineligible development material includes:
- every source opened or used during R2;
- every result surfaced by the single exploratory pre-freeze 2024 R3 development query `2024 scientific model misspecification corrected mechanism experiment`.

No 2022 R3 query had been executed when the scientific freeze commit was created.

## Mutation rule after dedicated workflow passes

Once 2022 acquisition begins, the frozen files above and the merged R2 policy/protocol may not change in this campaign. A defect discovered afterward invalidates/terminates R3 and requires a successor; it cannot be repaired after outcome-bearing acquisition begins.

All forty query dispositions must freeze before any ORION/B3 execution. Failed/no-source queries remain visible. Corpus quota failure returns `P1_R3_CANNOT_CHECK_SOURCE_UNIVERSE` without candidate scoring.
