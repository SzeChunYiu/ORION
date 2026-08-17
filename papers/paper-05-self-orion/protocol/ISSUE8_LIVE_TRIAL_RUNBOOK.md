# Issue #8 live-trial runbook

This runbook is process evidence for `SzeChunYiu/ORION#8`. It does not grant
empirical trial credit, Phase-2 closure, or Self-ORION authority.

Current typed status: `CANNOT_CHECK`.
Failure class: `FROZEN_ARTIFACT_NOT_CONSULTED_BY_EXECUTION`.
Receipt: `papers/paper-05-self-orion/evidence/ISSUE8_PACKET_EXECUTION_BINDING_RECEIPT.json`.

## Do not launch

Do not edit `papers/paper-05-self-orion/phase2/LIVE_EXECUTION_TRIGGER.txt`.
Do not push a change to `.github/workflows/p5_phase2_live_execution.yml` for the
purpose of starting a run. The merged workflow rebuilds a packet from
`phase2_preflight.build_frozen_live_trial_packet` instead of loading
`protocol/LIVE_TRIAL_PACKET_V1.json`. A run on that path would be
`UNBOUND_EXECUTION_REPORT`, the class already quarantined via #212.

The packet's own command, `python -m orion.self_orion.live_packet --live`, is
the sound preflight: it refuses on missing credentials, on `corpus_revision:
UNBOUND`, and on an epoch that differs from the freeze, and it records
immutable `CANNOT_CHECK` episodes. It is not what the merged workflow calls.

## Two registries, neither elected here

| Binding | Frozen packet | Merged workflow registry |
|---|---|---|
| Wide task | `P5.LIVE.WIDE.stopping-rule-source-families` | `phase2:wide:microglia-complement-cross-disease` |
| Deep task | `P5.LIVE.DEEP.flat-round-without-lineage` | `phase2:deep:mos2-screening-exciton` |
| Epoch | `P5.shadow-live-research.epoch-1` | env, or `github-actions-<run_id>-attempt-<n>` |
| Budget | `24.0` | workflow default `32` |
| Reasoner env | `ORION_P5_REASONER_MODEL` | `ORION_PHASE2_REASONER_MODEL` |
| Baseline id | `simple_llm_retrieval_baseline.v1` | `simple-llm-retrieval-baseline-v1` |

These are different research problems. This lane does not choose which registry
is canonical. That is a governance decision, not a coding convenience.

## Fail-closed wiring (owned by #277)

Issue #277 / PR #289 owns making `assess_phase2_preflight` fail closed on
binding identity. This lane does not fork `phase2_preflight.py`.

Bind the published packet to the merged workflow **only after** that fail-closed
gate is on `origin/main`. Until then, keep this `CANNOT_CHECK` receipt.

After the gate merges, the binding must:

1. load `LIVE_TRIAL_PACKET_V1.json`;
2. recompute and verify `packet_fingerprint`;
3. identity-check task ids, epoch, baseline id, resource budget, provider
   manifest hash, and evaluator artifact hash against the freeze;
4. fail closed on any divergence, reporting both registries, without silently
   adopting one of them;
5. refuse `corpus_revision: UNBOUND`;
6. leave protected gold outside candidate custody.

## Operator blockers that remain after code binding

- `OPENAI_API_KEY` (or another frozen explicit reasoner identity that the
  packet's provider manifest actually names);
- reachable protected verifier (`ORION_PROTECTED_VERIFIER_URL` /
  `_TOKEN` / `_ARTIFACT_HASH`) holding held-out gold outside the answering lane;
- `ORION_PHASE2_EVALUATION_EPOCH_ID` equal to the frozen epoch, or a new
  pre-outcome packet with a recomputed fingerprint;
- an exact Phase-2 closure subject, with `corpus_revision` no longer `UNBOUND`.

No secret value belongs in this repository, in this runbook, or in a receipt.

## What would close #8

A result-bearing wide + deep run **and** the matched baseline, on the exact
closure subject, through the bound packet, with immutable raw traces, protected
evaluator bindings, and preserved failure/null evidence, merged to `main`.
Repository tests, this receipt, and Copilot entitlement probes are not that run.
