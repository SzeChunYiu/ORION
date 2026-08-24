# P5 C3 native task environment V8

- Field: `runtime.task_environment`
- Status: **`BLOCKING`**
- Candidate-safe seed: `P5_C3_CANDIDATE_SAFE_SEED_V8.tar.gz`
- Seed SHA-256: `8d7197f581cad11695ae4c867ad8f941d86f7eeec8d0e8e4e7b79895d72b8f2d`
- Seed members: **69** = 55 filtered DGM source + 6 unchanged Lang-1 core + 8 control files
- Excluded: **1,595 files / 49,707,333 blob bytes** from `initial/`, `initial_polyglot/`, and `swe_bench/ref_agent_results/`
- DGM/model/benchmark/scorer/outcome executions: **0/0/0/0/0**
- Build runtime: **0.122023 s**

## Gate adjudication

- `PASS` — `exact_mutable_agent_immutable_host_split`
- `PASS` — `input_native_certificate_committed_before_self_edit`
- `PASS` — `endpoint_policy_bytes`
- `PASS` — `tool_policy_bytes`
- `PASS` — `write_policy_bytes`
- `PASS` — `excluded_outcome_prefixes_absent`
- `PASS` — `shared_core_identity_unchanged`
- `PASS` — `exact_invocation_environment_bytes`
- `FAIL` — `native_dgm_can_initialize_from_candidate_safe_seed`

## Exact residual

`UNCHANGED_DGM_REQUIRES_EXCLUDED_INITIAL_OUTCOME_METADATA_TO_INITIALIZE`

The unchanged native `DGM_outer.py` initializes the archive as `initial`, requires an `initial/` directory, and then reads prior `overall_performance` fields such as accuracy and resolved counts. Those bytes belong to the frozen 1,595-file exclusion. The new seed therefore closes every byte-materialization criterion but cannot truthfully establish a native runnable task environment.

Next discriminator: A source-native DGM release must expose an outcome-free initial-state interface, or a separately named preregistered successor adapter must do so without fabricating prior performance fields; native C3 cannot be silently patched.

No manuscript/shared packet was edited and no C4 validator, pytest, CI, Git command, DGM, model, benchmark, scorer, or outcome was executed.
