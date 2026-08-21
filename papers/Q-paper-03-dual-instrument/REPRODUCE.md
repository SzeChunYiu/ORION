# Q3 — reproducing Benchmark V0

## Frozen benchmark

Verify the protocol and outcome under:

- `development/orion-q-max-r0/DUAL_HARNESS_AGREEMENT_BENCHMARK_V0_PROTOCOL.md`;
- `development/orion-q-max-r0/dual-harness-benchmark-v0/DUAL_HARNESS_AGREEMENT_BENCHMARK_V0_RESULTS.json`;
- Lane A receipt workspace and Lane B receipt/decision artifacts in the same development tree.

The protocol must predate both lane outcomes. Divergence must remain an allowed terminal.

## Lane A

Reconstruct the host-driven answer only from its admitted receipt corpus. Verify each capability result binds to the exact request identity/digest and that the final diagnosis/move is traceable to verified evidence rather than an unbound free-text assertion.

## Lane B

Re-run the typed controller from the frozen manifest and observation transcription. The manifest digest must match the recorded value before a decision is accepted. Verify that the revision obligation remains unresolved at the decision point and that the controller therefore selects characterization rather than the unlicensed split revision.

## Scoring

Recompute the scored coordinates from the frozen protocol. V0 should produce `AGREE` on the contemporaneous coordinates and `ALIGNED` on deferred scoring after the later R6P/R6Q outcomes. Do not reinterpret the one outcome as an agreement rate.

## Repaired historical defects

Run `packages/orion-research-harness/tests/test_invalid_content_recovery.py`. Current behavior must map malformed successful reasoner content into structured `HOST_CAPABILITY_FAILED` handling and require an explicit reason before archiving invalid content to free a deterministic request identity.

## Remaining evidence gate

No reproduction procedure can create the missing benchmark series. Additional instances require new pre-outcome freezes and executions.