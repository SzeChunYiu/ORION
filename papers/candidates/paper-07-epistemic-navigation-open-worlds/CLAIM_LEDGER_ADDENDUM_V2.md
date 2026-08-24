# P7 claim-ledger addendum V2

**Date:** 2026-08-17  
**Rule:** additive rows only; existing V1 formal/nonclaim boundaries remain unchanged.

| ID | Claim | Status | Authority | Boundary / reopen trigger |
|---|---|---|---|---|
| P7.C-V2.1 | Eight prospective benchmark contracts covering required/negative/non-retrieval families exist in machine-readable form. | `ARTIFACT_FACT` | `benchmark/instances_v1.jsonl` | Reopen on case/schema change. |
| P7.C-V2.2 | Every frozen row is executed against the reference terminal oracle and suite-level family/control constraints. | `LOCAL_DETERMINISTIC` | `formal/check_benchmark_contracts_v2.py`; aggregate V2 receipt | The oracle checks contract consistency only. |
| P7.C-V2.3 | The case set includes a harmful-reframe negative control and a non-retrieval experimental-design topology-change case. | `ARTIFACT_FACT` | manifest + aggregate runner | Does not establish that the cases are ecologically valid or difficult. |
| P7.C-V2.4 | A P7 system improves navigation or scientific outcomes over fixed-topology/P1/P2/replanning baselines. | `CANNOT_CHECK` | no candidate-agent run | Requires protected matched prospective evaluation. |
| P7.C-V2.5 | The atlas residual is novel and warrants a separate paper. | `CANNOT_CHECK` | no novelty certificate | Requires #337/#343/#287 and positive non-retrieval discriminator. |

### Prohibited inference

`manifest PASS` does not imply `P7 empirical PASS`. It means the frozen rows, terminals and coverage invariants are internally consistent.
