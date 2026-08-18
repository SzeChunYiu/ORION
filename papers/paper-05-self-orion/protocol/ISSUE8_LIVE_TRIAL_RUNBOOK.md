# Issue #8 live-trial runbook

This runbook is process evidence for `SzeChunYiu/ORION#8`. It does not grant
empirical trial credit, Phase-2 closure, or Self-ORION authority.

Current typed status: `CANNOT_CHECK`.
Failure class: `FROZEN_ARTIFACT_NOT_CONSULTED_BY_EXECUTION`.
Receipt: `papers/paper-05-self-orion/evidence/ISSUE8_PACKET_EXECUTION_BINDING_RECEIPT.json`.

## Do not launch

Do not edit `papers/paper-05-self-orion/phase2/LIVE_EXECUTION_TRIGGER.txt`.
Do not push a change to `.github/workflows/p5_phase2_live_execution.yml` for the
purpose of starting a run. The merged workflow still rebuilds a packet from
`phase2_preflight.build_frozen_live_trial_packet` and does not pass
`frozen_packet`. After #277 / PR #289, that construction blocks at
`BIND_FROZEN_PACKET` rather than executing a bound #8 trial. Editing the
workflow YAML to attach the packet would itself launch a live run; do not
do that from this lane. A run that executed the preflight registry instead of
the published packet would be `UNBOUND_EXECUTION_REPORT`, the class already
quarantined via #212.

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

## Fail-closed wiring (merged via #277 / PR #289)

`assess_phase2_preflight` now fail-closes on binding identity and reports
`CANNOT_CHECK` when the in-source registry and the published packet disagree,
without electing either side. Merge commits: `8aaa9e64becefbdf6efc39fe24c05abdc1c52f7b`
and `86e8f15f2406ae32ef271364e10f9cc40e03a3b2`.

This lane still does not fork `phase2_preflight.py` and still does not elect a
canonical registry. The remaining execution-path gap is that
`p5_phase2_live_execution.yml` constructs `Phase2ClosurePreflight` without
`frozen_packet`, so the published packet is not consulted by the workflow.
Attaching `FrozenPacketBinding.from_packet_document(...)` belongs in a change
that does not launch the live workflow as a side effect.

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
