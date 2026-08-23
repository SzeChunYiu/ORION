# ORION research harness — nonzero local process recorded as success

## Observed

Hostile review of the canonical `packages/orion-research-harness/` campaign path found that `execute_local()` intentionally used `subprocess.run(..., check=False)` and returned the process `returncode`, but `service_local_request()` then persisted every normally-returned `SHELL`/`PYTHON` invocation with `success=true` regardless of that return code.

A process that exited nonzero after emitting partial or malformed evidence could therefore become an immutable successful host receipt. The campaign runner would pass the receipt to the scientific result-contract parser instead of returning `CAPABILITY_FAILED`.

## Failure

This is a host-execution receipt defect. It grants no scientific, novelty, or R6 evidence. Any campaign result produced through a nonzero process exit must remain failed even if stdout contains a syntactically plausible result token.

## Failure class

`HARNESS_EXECUTION_RECEIPT -> NONZERO_PROCESS_EXIT_LAUNDERED_AS_SUCCESS`

## Correct response

- preserve stdout, stderr, argv, cwd, and return code in the failed receipt;
- persist `success=false` for every nonzero local `SHELL`/`PYTHON` exit;
- leave the campaign state unchanged and return `CAPABILITY_FAILED`;
- make the failed receipt immutable so replay cannot launder it into success;
- do not change any scientific result contract or gate.

## Authority

`HARNESS_ERRATUM_ONLY__NO_SCIENTIFIC_AUTHORITY`
