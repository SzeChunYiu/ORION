# Q4 claim ledger V2

| ID | Claim | Evidence | Boundary |
|---|---|---|---|
| Q4V2-C1 | Typed type-conditioned VOI outperforms the identical uniform-prior VOI planner in N4-A and recovers 71% of oracle utility on the frozen world. | N4-A receipt | Exact-synthetic, 300 paired episodes; not a real-agent claim. |
| Q4V2-C2 | Scope-bound reopening outperforms unscoped/always reopening and does not give back meaningful utility in the wasteful-reopening regime. | N4-B receipt | Two frozen 200-episode regimes. |
| Q4V2-C3 | Dominance-targeted verification yields 0.1096 mean regret vs 0.2518 for random verification at equal budget. | N4-C receipt | Scalarized synthetic regret, 400 episodes. |
| Q4V2-C4 | Full-chain transport verification detects all 200 laundering cases with recall 1.000 and FPR 0.000, including all 68 deep splices. | N4-D receipt | Constructed chains; not cryptographic-security evidence. |
| Q4V2-C5 | Decision-coupled active experiments outperform pure information gain on the decoy world; pure information gain spends 36.6% of probes on decision-irrelevant decoys. | N4-E receipt | Frozen exact-synthetic world. |
| Q4V2-C6 | Typed remint/transport beats matched-budget re-derivation when transport is available and ties exactly in the no-value regime. | N4-F3 receipt | Frozen construction; transport rules sound by construction. |
| Q4V2-C7 | N1-C closes the allocation-policy claim: ideal VOI ties the typed policy exactly despite a typed-state advantage over the scoping ablation. | N1-C receipt | Honest donor closure. |
| Q4V2-C8 | N2-F5B is donor-absorbed on the original world and survives only as a misspecification-robustness result on the frozen misspecified world. | N2-F5B receipt | Mixed bounded result. |
| Q4V2-C9 | The suite is deterministic/replayable under its frozen seeds/protocols. | replay ledger + receipts | Reproducibility claim, not external-validity claim. |

## Forbidden promotions

No real research-pipeline, LLM-capability, cryptographic-security, lower-bound, impossibility, P10, or physical-quantum claim follows. Do not turn the six positive families into a universal statement that typing always helps; N4-F3's exact tie is part of the result.