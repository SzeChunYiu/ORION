# DIRECT_ROUTE_FREEZE_V1 development packet

## Scope and authority

This additive packet freezes a prospective, outcome-blind direct
`llama-server /completion` generation route for ORION P1 ScienceAgentBench. It
does not modify Runner V1, Runner V2, the analysis contract, the LUNARC
generation adapter, their registries, or any other development lane. It grants
no official execution, evaluation, outcome-opening, manuscript, or publication
authority.

The directory contains exactly eight files:

1. `DIRECT_ROUTE_FREEZE_CONTRACT_V1.json`
2. `DIRECT_ROUTE_PROMPT_BUNDLE_V1.json`
3. `direct_route_generation_driver_v1.py`
4. `validate_direct_route_freeze_v1.py`
5. `SYNTHETIC_VALIDATION_RECEIPT_V1.json`
6. `DEVELOPMENT_PACKET.md`
7. `HANDOFF_V1.md`
8. `SHA256SUMS`

## Unchanged upstream reuse

The contract exact-byte binds the merged Runner V1 and V2 contracts and
modules, the analysis contract, and the existing generation-adapter contract,
module, and attempt wrapper. The driver calls the adapter's public
`validate_plan` and `GenerationAttemptCapture` interfaces. It neither copies
nor amends adapter finalization.

The repaired PR #1159 mechanism/structured protocols and receipts are also
exact-byte bound. Their 90,575-byte prefix, 451-byte suffix, 91,026-byte
combined diagnostic prompt, and diagnostic output schema remain diagnostic
only. None is reused as an RR, OS, or NR production-shaped prompt or schema.

## Model, runtime, tokenizer, and route

- Model bytes: `18556689568`
- Model SHA-256:
  `fadc3e5f8d42bf7e894a785b05082e47daee4df26680389817e2093056f088ad`
- Model revision: `b17cb02dd882d5b6ab62fc777ad2995f19668350`
- `llama-server` SHA-256:
  `234b05b2138264f8fb263c3205e85f4c290e8afe5067e280a4f6f90cdac5696b`
- CUDA backend SHA-256:
  `fbe27c15253195c10559d98c6ba9c6d476a65d2bbf0240307b4a46d8aa17cefb`
- llama.cpp: `b10434`, commit
  `7e4c0a96880dae4fc4268ad441f8a6446bd5460a`
- Geometry: literal loopback, context 32,768, one slot, continuous batching
  off, prompt cache off, context shift off.

The inference tokenizer is bound by the GGUF bytes. The separately extracted
tokenizer source revision and file hashes are provenance inputs only;
byte-identical extracted inference-tokenizer identity and production prompt
token counts remain `CANNOT_CHECK` until prospective staging.

The only concrete client route is
`http://127.0.0.1:8080/completion`. It uses no secret, cookie, API-key header,
secret file/environment read, proxy, redirect, model pull, subprocess, tool,
or external provider call. The unchanged Runner field remains
`credential_route_status=BOUND_OWNER_CONTROLLED` because that field binds the
owner-controlled route descriptor, even though the literal loopback route
requires no secret. Kernel-level egress absence is not established by this
userspace freeze and remains `CANNOT_CHECK`.

## Prompt and state freeze

The phase-state and final-program JSON schema objects are byte-identical to the
merged production-shaped Codex bundle:

- `phase0_state`: 567 canonical bytes,
  `11299b5be0c855c1453ef99a14d1637b5c11230409efd68f50fde3394341cba1`
- `final_program`: 239 canonical bytes,
  `428e793d1f94a5b9e56731a8dd96a28b7e089aaad63d6a2be722d3ed7b266c2c`

Every request has the same exact field set, exact `json_schema` object,
`cache_prompt=false`, the paired seed, frozen sampling, and a frozen phase
output cap. Only an entire raw JSON object is parsed; prefix/suffix scanning,
duplicate members, non-finite values, and embedded-object recovery fail closed.

- RR calls `RR_PHASE0` then `RR_PHASE1`. Phase 0 must return
  `RR_TYPED_STATE`; the parsed state is canonicalized, hashed, and both the
  exact canonical state and SHA-256 are inserted into phase 1.
- OS calls only `OS_PHASE1`.
- NR calls `NR_PHASE0` then `NR_PHASE1`. Phase 0 must return
  `NR_GENERIC_PLAN`, but the phase-1 builder has no phase-0 argument. The plan,
  its bytes, and its hash cannot cross the reset boundary by construction.

Every `/completion` call passes through one existing
`GenerationAttemptCapture`. The returned receipt therefore remains
`TIMING_CAPTURED__ALLOCATION_FINALIZATION_PENDING` and requires unchanged
Runner V2 scheduler finalization before any allocation claim.

## Owner-prospective equal budget freeze

The owner selected the widest route-feasible equal acceptance envelope before
task or outcome opening. Each arm is frozen to:

```json
{
  "total_input_token_cap": 57344,
  "total_output_token_cap": 8192,
  "tool_call_cap": 0,
  "wall_time_seconds_cap": 1800.0,
  "local_execution_seconds_cap": 30.0,
  "final_candidates_per_attempt": 1
}
```

Phase output caps are RR/NR 1,024 plus 7,168 and OS 8,192. Every live call must
satisfy `timings.prompt_n + n_predict <= 32768`; cache reuse, truncation,
context shift, and post-observation budget changes are forbidden. The
two-phase input maxima are therefore 31,744 plus 25,600 = 57,344. OS retains
the same cumulative acceptance envelope even though it has one call.

This is a prospective design freeze, not observed usage or evidence that any
protected task fits. Task fit remains `CANNOT_CHECK_BEFORE_TASK_OPENING`, and
an over-limit task must fail closed rather than truncate or change caps.

### Failure and decision record

An initial owner proposal used `local_execution_seconds_cap=0`. The unchanged
Runner V1 invariant inherited by Runner V2 requires both wall-time and local
execution caps to be positive, so zero was not Runner-admissible. The final
owner decision freezes 30 seconds equally across arms to cover bounded local
serialization, validation, and state handling. The hostile validator includes
a regression that sends the 30-second plan through the unchanged adapter and
Runner V2, then confirms a zero-cap mutation is rejected.

## TDD and synthetic validation

The validator was written before the implementation. Witnessed states were:

1. Bootstrap RED: `AssertionError: False is not true : direct-route driver is not implemented`
2. Full hostile RED: `Ran 17 tests` and `FAILED (failures=17)`
3. Core implementation RED: `Ran 17 tests` and `FAILED (failures=1)` because
   the final synthetic receipt was intentionally still absent.
4. GREEN: all 17 hostile tests pass.

The suite uses invented packet objects and an injected in-memory client. It
opens zero official tasks and outcomes, invokes no model, provider, scheduler,
CI, or pytest path, and establishes no semantic-choice sensitivity.

## Claim boundary

```text
provider_seed_capability = CONFIRMED
semantic_choice_sensitivity = NOT_ESTABLISHED
candidate_semantic_diversity_gate_enabled = false
attempt_retention = ALL_ATTEMPTS_NO_SELECTION
production_admissibility = CANNOT_CHECK
scientific_authority_delta = NONE
```

Seed capability means only that the exact request field is supported by the
bound direct provider route. It does not establish useful candidate-semantic
diversity or authorize selection among attempts.

## Focused verification

Run only these bounded local checks from the repository root:

```text
rtk env PYTHONPYCACHEPREFIX=/tmp/orion-direct-route-freeze-v1-pycache python -m py_compile development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/direct_route_generation_driver_v1.py development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/validate_direct_route_freeze_v1.py
rtk rm -rf /tmp/orion-direct-route-freeze-v1-pycache
rtk env PYTHONDONTWRITEBYTECODE=1 python development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/validate_direct_route_freeze_v1.py
rtk env PYTHONDONTWRITEBYTECODE=1 python development/p1-scienceagentbench-lunarc-generation-adapter-v1-2026-08-24/validate_lunarc_generation_adapter_v1.py
rtk shasum -a 256 -c development/p1-scienceagentbench-direct-route-freeze-v1-2026-08-24/SHA256SUMS
rtk git diff --check origin/main...HEAD
```

No shell file is added, so no Bash syntax check applies.
