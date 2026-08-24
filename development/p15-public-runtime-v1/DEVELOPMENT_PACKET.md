# P15+Q3 public runtime campaign — no-results freeze

## Outcome

This increment resolves the public acquisition manifest without claiming a run:
30 workload identities, 20 objective buggy/fixed revision pairs, and three
source-bound runtime definitions are frozen. The exact terminal is:

`P15_PUBLIC_RUNTIME_V1_CANNOT_CHECK__NO_CONTAINER_RUNTIME__NO_BUILT_IMAGES__NO_RESULTS`

The checker binds exact canonical digests for every source record, workload row,
failure pair, runtime definition, gate, authority object and non-bypass
statement. Counts alone are not treated as identity evidence.

## Public inputs

- CORE-Bench: ten public training capsule identities from the first ten frozen
  manifest rows. The benchmark code is MIT; capsule terms remain
  `CANNOT_CHECK`, so only identifiers and receipts may be redistributed.
- PaperBench: ten alphabetically first paper IDs and exact config hashes at the
  frozen frontier-evals commit. Code is MIT; third-party paper/asset terms remain
  `CANNOT_CHECK` and payloads are not copied here.
- ScienceAgentBench: ten first eligible verified task IDs after excluding the six
  documented upstream-license exceptions. The Dataset Viewer reports 102 rows;
  the selected tasks are under the benchmark's CC-BY-4.0 default. Dataset task
  identities were verified through the read-only Hugging Face Dataset Viewer.
- Defects4J: first four active bug/fix pairs in each of Chart, Closure, Lang,
  Math and Time. Defects4J infrastructure is MIT. Upstream project terms remain
  `CANNOT_CHECK`; only IDs, revisions, report URLs and later receipts may be
  retained.

## Why execution is blocked

This session has neither Docker nor Podman. The three source definitions are
hashed, but no OCI image was built and no image digest exists. Therefore zero of
30 workloads and zero of 20 failure cases were executed. A Dockerfile hash is
not an image, and a source manifest is not a result.

## Authority boundary

Scientific-authority delta is `NONE`; the issue execution box remains open.
Independent replication, protected custody, external adoption, CODECHECK/ACM
replay, hardware/site independence and population inference remain
`CANNOT_CHECK`. Online public data cannot bypass any of them.

## Reopen route

1. audit each selected upstream payload's own license before acquisition;
2. build all three frozen definitions and retain immutable OCI digests;
3. execute the Cartesian runtime/workload/failure matrix under matched arms;
4. retain every install, failure, timeout, null, recovery, integrity escape,
   overhead and mutation receipt;
5. run the unchanged gate; do not tune thresholds or drop failing workloads;
6. seek external replay/adoption separately from this same-owner portability run.
