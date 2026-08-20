# P1-U GPT-R3 pre-acquisition freeze V2

Parent: #649  
Campaign: #716  
Base: `main@8c6a2d56b0ddcea24667da97df4445df5c714dae`

Final scientific pre-acquisition commit: `9d139caedf48a9c72f771d861394f31df291e7db`.

No 2022 acquisition query had been executed before this commit.

## Why V2 supersedes V1

The first dedicated workflow exposed a hostile-test expectation error before acquisition: one `NO_QUALIFYING_SOURCE` still leaves 39 cases and four remaining cases in that class, so it correctly satisfies the frozen corpus quotas. The test had incorrectly expected automatic `CANNOT_CHECK` after any single no-source query.

Before any 2022 search:
- the Python literal typo `false` was corrected to `False` in the new evaluator;
- the hostile test was corrected to require two missing cases from the same class, which actually violates the frozen minimum of four;
- an explicit test now confirms one no-source disposition is admissible when all quotas remain satisfied.

No query text, scan limit, source qualification, corpus quota, R2 policy byte, decision margin, endpoint, or comparator changed.

## Final frozen files

- `development/p1-u-gpt-r3-source-universe/DEVELOPMENT_PACKET.md`;
- `research/claim_expansion/p1/gpt_r3/SOURCE_UNIVERSE_PLAN_V1.json`;
- `research/claim_expansion/p1/gpt_r3/evaluate.py`;
- `tests/unit/p1/test_p1_u_r3_source_universe.py`.

Acquisition remains locked until the dedicated `p1-u-r3-source-universe` workflow is green on a head containing these bytes. After that green gate, these files and the merged R2 policy/protocol are immutable for R3.
