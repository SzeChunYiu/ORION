# P14C — specification-separated primary benchmark

P14C was frozen after the P14B circularity issue was identified and does not alter P14A or P14B.

- `P14C_ADJUDICATION_CASES_V1.json` contains **28 explicit frozen cases**, four variants for each of seven semantic strata.
- `run_p14c_specification_separated_governance_v1.py` implements every policy independently from the case table.
- Before a policy call, the harness strips `gold_disposition`, `rationale`, `case_id` and `stratum`; the policy receives only factual booleans.
- Precedence variants test donor-over-interaction/history, interaction-over-history, validity failure and negative evidence.
- Six ablations separately remove evidence-integrity, freeze, identifiability, donor, interaction and negative-history checks.

The explicit specification is internal to the programme, not a human external-adjudication dataset. P14C therefore evaluates **conformance to a separately frozen specification**, not truth about open-ended science.

Terminal: `P14C_SPECIFICATION_SEPARATED_GOVERNANCE_CONFORMANCE_SUPPORTED`.

| policy | accuracy | false promotion | discovery recall |
|---|---:|---:|---:|
| **ORION_RSE_FULL** | **1.0000** | **0.0000** | **1.0000** |
| `MULTI_REVIEW` | 0.857143 | 0.142857 | 1.0000 |
| `DONOR_AWARE_REVIEW` | 0.714286 | 0.285714 | 1.0000 |
| `REFLECTION_CHECKLIST` | 0.571429 | 0.428571 | 1.0000 |
| `RAW_POSITIVE` | 0.428571 | 0.535714 | 1.0000 |

Full ORION-RSE correctly handles all retained-negative and supported-reopen cases. All six ablations lower disposition accuracy. Gold is absent from every policy input. Two independent evaluations produce identical canonical SHA-256 `74032348de7e6508b6c1827aabcf1bf9d354d30b9c6f81c8259fdb3535f01a63`.

## Could this terminal have been the other word?

The question that disqualified P14A's negative is asked of P14C's positive, over the coordinate P14C leaves free. P14A sampled the discriminator's prevalence; P14C fixes it — four cases per semantic stratum makes the `RETAIN_NEGATIVE` share exactly `4/28 = 0.142857` in every admissible table, against P14A's ceiling of `0.042326` for the same quantity. What stays free is the implementation in the graded slot, and the protocol registers seven: the full contract and its six single-component ablations.

Over that register exactly one subject clears all eight gates and six fail at least one, so the conjunction prints **two** distinct terminals. `accuracy_advantage_ge_0_10` fails for the donor, interaction and negative-history ablations, so it is refutable rather than assumed. `strongest_baseline_false_promotion_ge_0_10` is a benchmark-difficulty precondition and holds in every admissible table by construction — the property P14A's corresponding certificate lacked, where it was unsatisfiable instead.

P14A's two frozen bars, registered verbatim and read here, are both met:

- `strongest_baseline_false_promotion_ge_0_05`: reachable interval
  [0.142857, 0.142857] over admissible tables; realized 0.142857.
- `accuracy_gain_ge_0_08`: reachable interval [0.000000, 0.142857] over
  admissible subjects; realized 0.142857.

The 0.08 bar sits strictly inside its interval, so it could have gone either way. The question P14A's gates encoded is answered affirmatively at P14A's own thresholds, under P14C's protocol identity, with nothing of P14A edited.

One residual is reported rather than absorbed: `full_discovery_recall_one` is satisfied by all seven registered subjects, because an ablation removes a check and a policy reading fewer facts promotes more rather than fewer. No registered implementation abstains, so that gate carries no refutation capacity here and its pass is not evidence that the contract preserves valid discovery.

The strongest current claim is: **against an explicit adjudication specification frozen separately from policy implementation, the full ORION-RSE contract conforms to every registered governance case and strictly outperforms the registered partial-governance implementations without reducing valid promotion.** This is stronger than a self-call conformance test and weaker than external scientific validity.
