# Phase-2 protected service contracts V1

ORION's Phase-2 clients are executable without custom Python adapters, but the protected services must remain separately controlled from the candidate/reasoner process. This document freezes their wire contracts at a human-readable level. The Python clients remain the canonical machine checks.

## Protected runtime source verifier

Environment:

```text
ORION_PROTECTED_VERIFIER_URL
ORION_PROTECTED_VERIFIER_TOKEN
ORION_PROTECTED_VERIFIER_ARTIFACT_HASH
ORION_PHASE2_EVALUATION_EPOCH_ID
```

The request binds the exact interpreted contribution, retrieved item content/source identity, evaluator artifact and epoch, plus a canonical `request_hash`. A successful response must echo the exact request/evaluator/epoch identities, set `passed=true`, and provide at least one protected certificate ID. A bare boolean is rejected.

## Protected candidate sandbox

Environment:

```text
ORION_PROTECTED_SANDBOX_URL
ORION_PROTECTED_SANDBOX_TOKEN
ORION_PROTECTED_SANDBOX_ARTIFACT_HASH
```

The sandbox request contains the exact base revision, SHA-256 patch identity, base64 patch bytes, touched paths and test plan. The sandbox response must echo the request hash, sandbox artifact identity, base revision and patch hash and return:

- SHA-256 `candidate_revision_hash`;
- `passed_required_tests` boolean;
- test result IDs;
- failure signatures;
- resource units;
- output artifact IDs.

Patch bytes are sourced from `FileSystemDevelopmentArtifactStore`, which verifies content hashes on every read. The sandbox never receives authority to promote the candidate.

## Protected development assurance

Environment:

```text
ORION_PROTECTED_DEVELOPMENT_EVALUATOR_URL
ORION_PROTECTED_DEVELOPMENT_EVALUATOR_TOKEN
```

The evaluator artifact/epoch are inherited from the frozen Phase-2 provider stack. The assurance request binds the complete development request, proposal and sandbox execution receipt plus its canonical request hash. The response must bind the exact request/proposal/candidate/evaluator/epoch and return:

- development delta;
- fresh-assurance delta;
- blocking-invariant result;
- evaluator-frozen-before-candidate flag;
- fresh-split flag;
- resource-matched flag;
- reason list.

The `SelfOrionChangeController` remains non-compensatory: protected-path/binding/invariant failures reject; visible-development gains with nonpositive fresh assurance become META_OVERFIT; only a clean result may become `RECOMMEND_HOST_PROMOTION`. It never self-merges.

Compose the consequential Shadow development stack with:

```python
from orion.self_orion.live_shadow_development import (
    build_live_shadow_development_stack_from_env,
    write_shadow_development_service_manifest,
)

dev = build_live_shadow_development_stack_from_env(
    provider_stack=stack,
    artifact_root="/protected/development-artifacts",
    base_revision="<exact git commit oid from subject attestation>",
)
write_shadow_development_service_manifest(
    dev,
    "/protected/shadow-development-services.json",
)
```

## Frozen hostile attack executor

Environment:

```text
ORION_AUTHORITY_ATTACK_EXECUTOR_URL
ORION_AUTHORITY_ATTACK_EXECUTOR_TOKEN
ORION_AUTHORITY_ATTACK_EXECUTOR_ARTIFACT_HASH
```

The service receives one exact frozen attack spec and the exact authority trial binding. The response must bind the canonical request hash, executor artifact, attack, subject and execution artifact. It must report observed authority outcome, whether candidate authority increased, resources and an evidence artifact identity/hash.

## Protected hostile evaluator

Environment:

```text
ORION_AUTHORITY_EVALUATOR_URL
ORION_AUTHORITY_EVALUATOR_TOKEN
```

The evaluator artifact/epoch come from `AuthorityTrialBinding`; its process lineage must differ from the producer/executor lineage. Each request contains the frozen attack, exact execution artifact and complete binding. The response must bind request/attack/execution/evaluator/epoch and report PASS/FAIL/CANNOT_CHECK, expected-outcome observation, false-promotion observation, tamper/leakage signal and protected evidence IDs.

Compose the ten-attack runner with:

```python
from orion.self_orion.authority_live import (
    build_live_authority_trial_runner_from_env,
)

runner = build_live_authority_trial_runner_from_env(binding=binding)
report = runner.run(binding)
```

## Boundary

All service tokens are transport secrets and are absent from public/content-addressed manifests. Service artifact identities, evaluator identities, epochs, request hashes and returned artifact hashes are evidence bindings. A response from any service that does not reproduce its exact bindings fails closed.

These clients make the campaign executable; they do not make the services independent. External custody/process lineage must still be established operationally and recorded in the Phase-2 evidence artifacts.
