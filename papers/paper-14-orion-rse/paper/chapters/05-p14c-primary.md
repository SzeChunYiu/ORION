# P14C — specification-separated primary benchmark

P14C was frozen after the P14B circularity issue was identified and does not alter P14A or P14B.

- `P14C_ADJUDICATION_CASES_V1.json` contains **28 explicit frozen cases**, four variants for each of seven semantic strata.
- `run_p14c_specification_separated_governance_v1.py` implements every policy independently from the case table.
- Before a policy call, the harness strips `gold_disposition`, `rationale`, `case_id` and `stratum`; the policy receives only factual booleans.
- Precedence variants test donor-over-interaction/history, interaction-over-history, validity failure and negative evidence.
- Six ablations separately remove evidence-integrity, freeze, identifiability, donor, interaction and negative-history checks.

The explicit specification is internal to the programme, not a human external-adjudication dataset. P14C therefore evaluates **conformance to a separately frozen specification**, not truth about open-ended science.

Terminal: `P14C_SPECIFICATION_SEPARATED_GOVERNANCE_CONFORMANCE_SUPPORTED`.

| policy | disposition accuracy | false promotion | useful-discovery recall |
|---|---:|---:|---:|
| **ORION_RSE_FULL** | **1.0000** | **0.0000** | **1.0000** |
| `MULTI_REVIEW` | 0.857143 | 0.142857 | 1.0000 |
| `DONOR_AWARE_REVIEW` | 0.714286 | 0.285714 | 1.0000 |
| `REFLECTION_CHECKLIST` | 0.571429 | 0.428571 | 1.0000 |
| `RAW_POSITIVE` | 0.428571 | 0.535714 | 1.0000 |

Full ORION-RSE correctly handles all retained-negative and supported-reopen cases. All six ablations lower disposition accuracy. Gold is absent from every policy input. Two independent evaluations produce identical canonical SHA-256 `74032348de7e6508b6c1827aabcf1bf9d354d30b9c6f81c8259fdb3535f01a63`.

The strongest current claim is: **against an explicit adjudication specification frozen separately from policy implementation, the full ORION-RSE contract conforms to every registered governance case and strictly outperforms the registered partial-governance implementations without reducing valid promotion.** This is stronger than a self-call conformance test and weaker than external scientific validity.