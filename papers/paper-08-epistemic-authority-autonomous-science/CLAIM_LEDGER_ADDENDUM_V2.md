# P8 claim-ledger addendum V2

**Date:** 2026-08-17  
**Rule:** additive rows only; existing V1 formal/nonclaim boundaries remain unchanged.

| ID | Claim | Status | Authority | Boundary / reopen trigger |
|---|---|---|---|---|
| P8.C-V2.1 | Seventeen machine-readable authority cases cover five domains, four verdicts, paired native controls, laundering, unresolved authority and an allowed coercion. | `ARTIFACT_FACT` | `benchmark/authority_cases_v1.jsonl` | Reopen on case/schema change. |
| P8.C-V2.2 | Every case is executed against the typed non-compensatory reference verdict semantics. | `LOCAL_DETERMINISTIC` | `formal/check_benchmark_contracts_v2.py`; aggregate V2 receipt | Reference semantics, not a protected evaluator. |
| P8.C-V2.3 | The suite prevents trivial deny-all success by requiring clean same-domain authorization in all five domains and one clean cross-domain coercion. | `LOCAL_DETERMINISTIC` | aggregate suite-level constraints | Does not establish appropriate authorization rates in real tasks. |
| P8.C-V2.4 | The shared calculus detects failures missed by exact independent P1–P5 gates. | `CANNOT_CHECK` | no composed-gate experiment | Requires exact embeddings and protected cross-domain attacks. |
| P8.C-V2.5 | P8 reduces laundering without unacceptable unnecessary refusal. | `CANNOT_CHECK` | no empirical outcome | Requires paired protected evaluation and confidence intervals. |
| P8.C-V2.6 | P8 is novel and warrants a separate paper. | `CANNOT_CHECK` | no novelty certificate | Failure sends material to P4/programme synthesis. |

### Prohibited inference

`case-suite PASS` does not mean that a candidate agent, coercion registry, provenance system or protected gate is correct. It establishes only internal consistency of the frozen contracts.
