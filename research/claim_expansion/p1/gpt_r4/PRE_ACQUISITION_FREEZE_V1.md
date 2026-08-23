# P1-U GPT-R4 pre-acquisition freeze V1

Parent: #649  
Campaign: #719  
Base: `main@2d6065755084588737274102aa7c140f2f1d8b7c`

Final scientific pre-acquisition commit: `248269836e039ca0851f7804bf2a91fd2b8b5730`.

No 2020 R4 acquisition query had been executed before this commit.

Frozen scientific files:
- `development/p1-u-gpt-r4-matched-pairs/DEVELOPMENT_PACKET.md`;
- `research/claim_expansion/p1/gpt_r4/MATCHED_PAIR_PLAN_V1.json`;
- `research/claim_expansion/p1/gpt_r4/evaluate.py`;
- `tests/unit/p1/test_p1_u_r4_matched_pairs.py`.

Candidate/comparator policy remains byte-owned by merged R2 (`research/claim_expansion/p1/gpt_r2/policy.py` and `PROTOCOL_V1.json`) and is not changed by R4.

## Lock rule

Acquisition begins only after the dedicated R4 workflow is green on a head containing the frozen scientific files above. After the first 2020 query executes:
- query text/order/scan limit cannot change;
- pair matching rules cannot change;
- R2 policy/protocol cannot change;
- R4 evaluator, margins and endpoints cannot change;
- source/pair cases cannot be dropped based on policy outcomes;
- policies cannot run until all 28 source dispositions and all pair/unresolved objects are sealed.

Any post-acquisition defect invalidates R4 and requires a successor; it cannot be patched after outcome-bearing evidence access.
