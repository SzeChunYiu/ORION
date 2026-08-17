# ORION-P5 protected hidden-cause suite freeze V1

This procedure is the host-side bridge between the design-frozen protocol and a later `EXECUTION_FROZEN` run. It does **not** publish a hidden-cause benchmark into the repository and it does **not** produce empirical evidence.

## Custody rule

The protected input is held outside challenger write authority. It contains:

- all eight protected root-cause labels;
- a unique 256-bit opening nonce per case;
- full fresh-task payloads;
- protected evaluator artifact hash;
- protected surfaces and scoring/harm rubrics;
- every declared negative/null/harmful variant payload.

Do not commit that input, its opening nonces, fresh payloads, evaluator internals, or protected rubrics to a candidate-readable branch.

## Freeze command

```bash
PYTHONPATH=src python -m orion.study.p5 \
  --protected-suite /protected/p5-suite.json \
  --candidate-packet artifacts/p5-candidate-packet.json \
  --commitment artifacts/p5-protected-commitment.json
```

The command validates the private suite and emits only:

1. a **candidate packet** with visible symptom/context, motivating/replay task identities and allowed change surfaces; and
2. a **commitment manifest** binding the full private suite, evaluator, motivating/replay split, fresh split, negative variants, protected surfaces and rubrics without publishing the protected payloads.

## Fail-closed conditions

Freeze is rejected if any of the following holds:

- one of the eight registered root-cause families is absent;
- a hidden root label has no unique nonzero 256-bit nonce;
- a declared fresh content hash does not match the evaluator-held payload;
- a fresh task changes only DATA/TOOL rather than at least one of TASK/DOMAIN/MODEL/ENVIRONMENT;
- motivating/replay task IDs overlap a fresh task ID;
- fresh or negative payloads are missing, duplicated or orphaned;
- an allowed candidate write surface is also a protected surface;
- the evaluator artifact hash is missing/invalid;
- the suite was not declared frozen before outcome access.

## Low-entropy truth commitment

A raw SHA-256 of `protected_root_cause` would be unsafe because the label has only eight possible values and can be enumerated. The manifest therefore commits to `{protected_root_cause, nonce}`. The nonce remains only in protected custody until any authorized post-study opening.

## Authority boundary

The candidate artifact declares `empirical_authority = NONE`; the commitment declares `empirical_authority = CANNOT_CHECK`. A suite commitment proves only that protected inputs were bound prospectively. It cannot establish causal-attribution accuracy, transfer benefit, integrity benefit, or permission to merge/promote a candidate.

## Transition to execution freeze

After the real hidden-cause cases, fresh payloads and protected evaluator are created under this custody rule, the host must still bind the exact final subject revision, provider/model identities, baseline config hashes, split hashes and evaluation epoch in the publication execution manifest. Only then may `PROTOCOL_V1.json` be promoted from `DESIGN_FROZEN` to a fully bound `EXECUTION_FROZEN` state. Partial binding is not valid.
