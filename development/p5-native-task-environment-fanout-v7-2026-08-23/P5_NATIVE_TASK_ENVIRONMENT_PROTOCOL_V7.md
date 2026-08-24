# P5 native task-environment fan-out protocol — V7

**Frozen:** `2026-08-23T20:21:29Z`  
**Authority:** outcome-blind byte-level task-environment acceptance only

## Scope

Adjudicate and, where complete evidence exists, bind only the six V6 runtime.task_environment field instances.

Only `runtime.task_environment` may change. All other 120 field instances remain exactly at the V6 state. No arm, model, benchmark, protected scorer, pytest suite, repository CI, or manuscript is run or edited.

## Fail-closed acceptance rule

- Every arm-specific criterion is represented by existing bytes or an exact canonical manifest value.
- Every referenced local byte artifact exists at validation and matches its recorded SHA-256.
- Every included task/content component has an explicit rights disposition consistent with the V6 rights manifest.
- No schema, plan, future input, source default, native bundled task, prior outcome, protected score, reference answer, or unexecuted promise is treated as evidence.
- The manifest binds one reproducible candidate-visible task environment without claiming runtime image, provider, custody, execution, performance, or superiority closure.

Any missing criterion leaves that arm `BLOCKING`; a schema, plan, source default, excluded native bundle, or future promise is never promoted to evidence.

## Per-arm criteria

### C1
- exact shared source archive/repository identity
- byte-frozen setup specification
- byte-frozen effective default-agent configuration
- retry agent disabled
- action sampler disabled
- review disabled
- open-PR behavior disabled
- native tool/write policy

### C2
- authored/licensed session bytes
- host-issued minimal-class certificate
- evaluator definition bytes
- write-root declaration
- shared core identity

### C3
- exact mutable-agent versus immutable-host tree split
- input-native certificate committed before self-edit
- endpoint policy
- tool policy
- write policy
- excluded outcome prefixes absent from candidate seed
- shared core identity

### C4
- exactly one ADIAS domain/adaptor identity
- visible task id and deterministic seed
- turn, step, and evaluation-sample limits
- environment implementation and data bytes
- bundled ADIAS task data excluded
- shared core identity

### C5
- fixed train membership
- fixed eval-dev membership
- fixed development-only locked-surrogate membership
- frozen solver outputs for every development item
- frozen solver.py bytes
- frozen prompts.py bytes
- development soft anchors
- external input-native certificate
- generated-output rights disposition
- protected final panel absent

### C6
- topic bytes
- allowed source corpus manifest
- allowed skills and exact tool parameters
- filtered source seed bytes
- source-bundled prior-outcome prefixes excluded
- exact profile and reset policy
- no reference answers or protected scores
- shared core identity

## Arithmetic

If `k` arms pass, V7 must report `54+k` bound, `72-k` blocking, `6-k` R2 blockers, and still `0/6` ready arms.
