# ORION-21 NR07 width-law run: controlling disposition

The controlling output of LUNARC job `3550337` is
`authoritative-job-3550337/NR07_WIDTH_LAW_FALSIFICATION_RESULT_V1.json`, SHA-256
`8ef964ecb3c02ab5988ea13ed56678a424e7d5487f64d31c2e66a149e44d9e22`.
It terminates `CANNOT_CHECK_INSTRUMENT_DRIFT`: the preregistered exact replay
precondition failed at one anchor.

After that outcome was read, the runner widened the replay tolerance and
produced a positive `V1_1` result. Those later bytes are preserved under
`quarantine-post-outcome-readjudication/`, but they grant no authority. Any
retry requires a new protocol identity with its tolerance frozen before
outcomes are read. Exact timing, hashes, and claim boundaries are recorded in
`POST_OUTCOME_PROTOCOL_DEVIATION_DISPOSITION_V1.json`.
