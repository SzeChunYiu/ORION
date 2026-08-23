# P1 mutation-necessity primary rerun — instrumentation packet V2

**Date:** 2026-08-18  
**Paper:** P1 — Recursive Epistemic Reconstruction  
**Parents:** #98, #278, #316  
**Prerequisite:** PR #363 / `PRIMARY_EXECUTION_FREEZE_V2.json`.

## Why this packet exists

The powered P1 successor is already prospectively frozen. It has 2,882 confirmatory worlds: 480 hidden shifts and 2,402 negative controls, three strong H1 parents, nine runnable arms, five direct ablations, a four-unit intervention budget, independent scoring/statistics, and a pre-bound replication seed.

The first observable primary attempt did **not** execute a candidate arm. It aborted because the original execution receipt bound an ephemeral regenerated `WORLD_FREEZE.json` envelope while the campaign runner correctly restored the committed immutable `PRIMARY_WORLD_FREEZE.json`. PR #363 preserves that negative instrumentation history and adds `PRIMARY_EXECUTION_FREEZE_V2.json`, whose only scientific-neutral correction is the immutable world-receipt envelope hash.

A previous outcome-workflow draft (#360) also contained two execution defects:

1. one version regenerated worlds without explicitly naming the v2.2.4 protocol tip;
2. it invoked `PRIMARY_EXECUTION_FREEZE.json` instead of the corrected V2 receipt.

This lane fixes only those execution defects and runs the already-frozen campaign read-only.

## Frozen scientific identity — MUST NOT CHANGE

The rerun must preserve exactly:

- protocol version `P1.epistemic-mutation-necessity.v2.2.4`;
- confirmatory seed `202608172211`;
- replication seed `202608172212`;
- N = 2,882;
- hidden-shift N = 480;
- negative-control N = 2,402;
- all public/protected world hashes;
- all three H1 parents;
- all nine runnable arms;
- all five ablations;
- H1 margin / H2 safety rules / Holm/bootstrap parameters;
- independent scorer/statistics/source hashes;
- four-unit intervention budget.

No post-outcome parent removal, margin change, world regeneration rule change, exclusion, scorer change, or generator change is allowed.

## Correct replay procedure

1. Check out the exact PR head that contains the corrected V2 execution receipt.
2. Assert both immutable receipts still record `arms_executed=false` and `outcome_accessed=false`.
3. Regenerate worlds into temporary storage **with explicit protocol path** `research/revival/p1/protocol/P1.epistemic-mutation-necessity.v2.2.4.json`.
4. Compare regenerated scientific identity fields and public/protected bytes against committed `PRIMARY_WORLD_FREEZE.json`. The regenerated envelope's `subject_git_sha` may differ because this rerun adds workflow files; that field is not a new scientific world.
5. Replace only `/tmp/.../WORLD_FREEZE.json` with the committed immutable `PRIMARY_WORLD_FREEZE.json` after the exact-byte/hash comparisons pass.
6. Assert the SHA-256 of that immutable world receipt equals `PRIMARY_EXECUTION_FREEZE_V2.json.world_freeze_sha256`.
7. Invoke `run_mutation_necessity_campaign.py` using the corrected V2 execution receipt.
8. Accept either frozen scientific terminal (`SUPPORTED` or `NOT_SUPPORTED`) as a valid outcome; upload all result bytes read-only.

## Path/watch completeness

The rerun workflow watches every bound source family, including:

- `absorbed_mechanics.py`;
- world freezer and protocol chain;
- necessity cases/engine/policies/scoring/statistics;
- campaign runner;
- primary world and V2 execution receipts;
- the workflow itself.

A source drift should trigger the workflow and then fail the execution receipt rather than silently skip validation.

## Authority boundary

This primary result, even if positive, does not by itself make P1 peer-review ready. The already-bound disjoint replication seed must still be executed and the resulting claim must survive independent #283 verification and final claim-ledger/manuscript integration.

The powered successor is evidence for the **wide P1 programme**: it directly tests when high-level formulation/search-universe mutation is scientifically necessary after lower-level repairs are ruled out, under protected sibling/dependency constraints. It must not be used as an excuse to delete P1's broader reconstruction, repair-selectivity, scoped-invalidation, or recursion-stability claims where those are supported by their own registered evidence.
