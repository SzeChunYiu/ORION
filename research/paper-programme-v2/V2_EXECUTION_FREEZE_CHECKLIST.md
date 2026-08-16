# V2 Execution Freeze Checklist

A V2 design can move from `DESIGN_FROZEN` to `EXECUTION_FROZEN` only in a dedicated prospective PR.

## Before outcome access

- [ ] rerun the V2 nearest-work audit and record any claim contraction;
- [ ] bind exact ORION subject commit;
- [ ] bind exact V1 comparator subject/configuration;
- [ ] bind task/data/case artifacts by content hash;
- [ ] bind train/pilot/test/fresh/protected split hashes as applicable;
- [ ] bind model/provider/tool/search backend revisions;
- [ ] bind baseline and ablation configuration hashes;
- [ ] bind evaluator/adjudicator/holdout identity and custody;
- [ ] bind resource budgets, seeds and environment;
- [ ] bind search/access/contamination policy hash;
- [ ] bind the exact protocol canonical SHA-256 from `PROTOCOL_DIGESTS_V1.json`;
- [ ] create a prospective run manifest using the programme's publication run-manifest discipline;
- [ ] verify no `UNBOUND` execution identity remains;
- [ ] merge the execution-freeze PR before inspecting final outcomes.

## During execution

- [ ] preserve V1 and V2 raw records independently;
- [ ] preserve provider failures, timeouts, `CANNOT_CHECK`, nulls and harmful cases;
- [ ] do not retune the frozen margin after seeing results;
- [ ] log access to protected data/evaluators;
- [ ] retain exact per-case pairing between V1, V2, baselines and ablations.

## After outcome access

Any design change creates a new immutable protocol version. Do not edit these V2 design commitments to rescue a result.

## Incremental terminal

The V2 mechanism is paper-admissible only when the executable incremental decision rule returns `PASS` **and** the scientific/host integrity gates are satisfied. A local known-answer `PASS` is only a test of the rule itself.
