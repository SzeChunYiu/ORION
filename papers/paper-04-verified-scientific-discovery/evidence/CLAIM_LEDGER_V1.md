# ORION-P4 Claim Ledger — protected V2

| # | Manuscript claim | Evidence | Status |
|---|---|---|---|
| 1 | Citation correctness, support, attribution, influence, and scientific authority are distinct coordinates. | Related-work audit; authority gate implementation. | Bounded conceptual/implementation claim |
| 2 | The repaired subject uses a non-compensatory authority transition whose failed prerequisites cannot be averaged away. | Subject `f6e51b5c...`; `protocol/PROTECTED_RUN_BINDINGS_V2.json`. | Tested mechanism claim |
| 3 | On the frozen V2 battery, ORION reduces false scientific-authority promotion versus the strongest frozen mechanism proxy. | `evidence/protected_v2/PUBLICATION_METRICS_V2.json`; `RESULT_ATTESTATION_V2.md`. | **SUPPORTED — H1 PASS** |
| 4 | H1 effect is `-0.50`, paired 95% CI `[-0.553,-0.447]`. | Campaign `31976589735`; independent reproduction receipt. | **SUPPORTED** |
| 5 | Safety gain does not arise from blanket refusal: both systems promote 60/60 clean positives. | Publication metrics + independent receipt. | **SUPPORTED — H2 PASS** |
| 6 | ORION is superior on correct `CANNOT_CHECK` selection. | Publication metrics. | **NOT SUPPORTED — H3 null** |
| 7 | All eight registered ablations worsen false-promotion rate without clean-coverage loss. | V2 ablation summary in publication metrics. | **SUPPORTED on this battery** |
| 8 | The soft-confidence terminal is especially unsafe on this battery (330/360 false promotions). | V2 ablation summary. | **SUPPORTED on this battery** |
| 9 | Scored candidate/comparator processes did not access protected identifiers or external IPs. | `P4ActualAccessTelemetry.v2`; protected raw `strace` retained. | **SUPPORTED for retained telemetry surface** |
| 10 | Independent code reproduced the headline counts. | Artifact `9271232325`; reproduction lineage hash `26f4cf9e...`. | **SUPPORTED** |
| 11 | Comparator results concern protocol-matched mechanism proxies, not original external implementations. | `host/BASELINE_CONFIGS_V2.json`; manuscript disclosure. | Scope boundary |
| 12 | The result generalizes to arbitrary scientific claims/evaluators. | No admissible evidence. | **NOT CLAIMED** |

## Evidence paths

- Final safe aggregates: `evidence/protected_v2/PUBLICATION_METRICS_V2.json`
- Attack-family contrast: `evidence/protected_v2/FAMILY_CONTRAST_V2.json`
- Result/custody attestation: `evidence/protected_v2/RESULT_ATTESTATION_V2.md`
- Execution bindings: `protocol/PROTECTED_RUN_BINDINGS_V2.json`
- Comparator/ablation disclosure: `host/BASELINE_CONFIGS_V2.json`
- Protected campaign: GitHub Actions run `31976589735`
- Safe bundle: artifact `9271234622`, SHA-256 `51ac14bc3a6b4b570aaca6d4a41c91f53d9bf2887e66f0620c412f78566a3b44`
- Independent reproduction: artifact `9271232325`

## Negative claims retained

Paper IV does not claim provenance tracking, attribution evaluation, iterative verification, evidence escalation, contamination detection, evaluator tamper detection, or auditability as standalone novelties. It does not claim H3 superiority, universal evaluator security, performance of the external authors' original systems, or naturalistic scientific fact-checking accuracy.
