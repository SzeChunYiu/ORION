# Integration instructions

## Preconditions

1. Integrate only into an isolated child branch of the authorized R8 branch after verifying
   the exact target SHA. Do not edit another session's checkout.
2. Preserve `DISCLOSURE.md`, both exposure markers, and independence terminal `CANNOT_CHECK`.
3. Do not label the directory `clean-room`, `blinded`, or `independent`, and do not count it as
   one side of the two-engine pass.
4. Treat `DONOR_NORMALIZATION_CONTRACT.json` as the frozen mathematical binding. Verify its
   source blob identities before comparing any census.

## Suggested destination

Copy this directory as an engineering module, for example:

`papers/five-paper-top-tier-r8/NQ/engineering/nq-engine-a-exposed/`

Do not import donor implementations into it. Keep the source manifest and complete-tree digest
with the copy. Rebuild all manifests after the destination path is fixed.

## Required integration gates

- install `requirements-test.txt` in a fresh Python 3.11+ environment;
- run all pytest controls, Ruff lint/format, compileall, and branch coverage;
- validate every JSON object against the included Draft 2020-12 schemas;
- recompute `SOURCE_MANIFEST.json` and verify it before execution;
- bind each run's input, result, stdout, stderr, environment, and scheduler receipt digests;
- require full raw-range/orbit coverage before any global negative;
- on partial traversal or a resource stop, emit only `CANNOT_CHECK_RESOURCE_BOUND`;
- preserve every disagreement, adverse result, duplicate anomaly, and normalization mismatch.

## Work still required before a runnable frozen full job

1. Generate a complete, duplicate-free local GL-class archive, then expand each class with
   `declared_donor_images`; retain every `NormalizationWitness` in a range-addressed manifest.
2. Use the proved `generate_canonical_classes` grammar and preserve its complete-level coverage
   receipts. Before a full job, establish bounded target-resource estimates and a deterministic
   checkpoint/range merge grammar; resource feasibility is not yet verified.
3. Implement separately proved short-spectrum and D3 structural extension generators.
4. Freeze partition ranges, checkpoint/resume grammar, memory estimates, and merge rules.
5. Only then prepare the smallest adequate CPU SLURM job. Resource failure remains
   `CANNOT_CHECK_RESOURCE_BOUND`; widening the scientific grammar is forbidden.
6. Have a proof auditor check the mathematical reduction and an artifact auditor check the
   immutable archive. This exposed staging cannot satisfy independent-engine separation.
