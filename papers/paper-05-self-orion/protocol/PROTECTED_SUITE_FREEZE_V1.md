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
- a hidden root label has no 256-bit opening nonce, or its nonce is one a cheap enumeration finds (see *Low-entropy truth commitment* below);
- a declared fresh content hash does not match the evaluator-held payload;
- a fresh task changes only DATA/TOOL rather than at least one of TASK/DOMAIN/MODEL/ENVIRONMENT;
- motivating/replay task IDs overlap a fresh task ID;
- fresh or negative payloads are missing, duplicated or orphaned;
- an allowed candidate write surface is also a protected surface;
- the evaluator artifact hash is missing/invalid;
- the suite was not declared frozen before outcome access.

## Low-entropy truth commitment

A raw SHA-256 of `protected_root_cause` would be unsafe because the label has only eight possible values and can be enumerated. The manifest therefore commits to `{protected_root_cause, nonce}`. The nonce remains only in protected custody until any authorized post-study opening.

The message space cannot be enlarged: the label the candidate must produce is one of eight registered families by definition, so testing any nonce guess costs at most eight digests forever. Every bit of protection the scheme has is therefore carried by the nonce, which makes the nonce a per-case salt in everything but name. Draw it from `orion.study.p5.freeze.mint_root_cause_nonce()` — 256 bits from the OS CSPRNG, one per case, released only at opening.

Requiring the nonce to be non-zero was not that requirement, and neither is requiring it to be numerically large: `f"{2**255 + ordinal:064x}"` is 64 hex characters, non-zero, unique per case, and 2^191 times above any magnitude floor, and it opens to the same single guess an ordinal does. `validate_protected_suite` therefore rejects the *shapes a declared cheap adversary generates*, not the values that look small:

- counters and ordinals up from zero, and counters run down from 2^256;
- constant padding — a run of 32 or more identical hex characters;
- a short alphabet — fewer than twelve distinct bytes in the 32;
- a repeated block, and the fixed placeholders a generator leaves behind;
- any SHA-256, truncated SHA-512 or canonical-JSON derivation of a field the manifest publishes beside the commitment (case id, case ordinal, visible symptom, suite id);
- one salt shared across the suite, or one salt with a per-case offset — nonces that agree in their first or last 16 hex characters are rejected, because opening either case then opens both.

`orion.study.p5.hidden_cause_custody` builds its disclosure probes from the same generators, so a nonce the freeze accepts is by construction one the declared adversary cannot enumerate, and a nonce a probe can reach is one the freeze refuses. Running `PYTHONPATH=src python -m orion.study.p5.hidden_cause_custody --suite <suite>` attacks the commitments a freeze of `<suite>` would publish and exits non-zero if any opens. Do that before the manifest is published, not after.

## The shipped suite is not a protected artifact

`evidence/hidden-cause-suite/PROTECTED_SUITE_V1.json` does not satisfy the custody rule above and never did. It is a candidate-visible fixture, and the sealing of its root causes is void:

- it publishes `protected_root_cause`, `root_cause_nonce`, `success_rubric`, `harm_rubric` and `protected_surface` in plaintext, which the *Custody rule* section forbids;
- its nonces are the case ordinal, `0…01` through `0…018`, so the 24 commitments a freeze of it would publish open in 108 SHA-256 evaluations;
- its cases are emitted in eight consecutive blocks of three, so the label is the case ordinal divided by three whatever the nonce is.

The plaintext labels are the binding defect: a digest cannot withhold a value that is published beside it, so no nonce repairs this file. Redrawing its nonces now would also not repair it, for a reason that has nothing to do with entropy — the run has been scored, the answers are known, and a commitment issued by a party that already knows the answer is not a commitment. **This suite must not be re-sealed and must not be reused as a protected suite.** Re-establishing a prospective hidden-cause result requires new cases, authored under the custody rule, with CSPRNG nonces, emitted in an order independent of the family, and run before the labels are seen.

Nothing above changes the one number this suite produced. The 21/24 GLM-5.2 attribution score is reported throughout the manuscript as a descriptive diagnostic scored against locally visible gold labels (`sections/09-results-attribution.tex`, `sections/10-limitations.tex`), it is explicitly not offered as protected-evaluator evidence, and no published table or claim rests on the commitment scheme. What the defect voids is the word *protected* as applied to this file, not the diagnostic.

The failure record is `research/failures/2026-08-invertible-commitment-vacuous-custody/`.

## Authority boundary

The candidate artifact declares `empirical_authority = NONE`; the commitment declares `empirical_authority = CANNOT_CHECK`. A suite commitment proves only that protected inputs were bound prospectively. It cannot establish causal-attribution accuracy, transfer benefit, integrity benefit, or permission to merge/promote a candidate.

## Transition to execution freeze

After the real hidden-cause cases, fresh payloads and protected evaluator are created under this custody rule, the host must still bind the exact final subject revision, provider/model identities, baseline config hashes, split hashes and evaluation epoch in the publication execution manifest. Only then may `PROTOCOL_V1.json` be promoted from `DESIGN_FROZEN` to a fully bound `EXECUTION_FROZEN` state. Partial binding is not valid.
