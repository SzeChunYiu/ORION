# ORION-P4 Claim Ledger — protected V2

> **Record of the pre-rewrite manuscript, 2026-08-22.** The manuscript was
> subsequently rewritten so that its claims are about the mechanism rather than
> about a named system, so that internal status tokens do not appear in its
> prose, and so that repository paths sit in Data Availability instead of the
> narrative. The claim wording below is the wording of the manuscript as it stood
> when this ledger was cut. **No number, evidence path, artifact, authority or
> status in this table changed in that rewrite**, and none has been edited here:
> a ledger is a record of what was allowed and on what evidence, so it is
> annotated rather than restated. Two rows read differently in the rewritten
> prose without their evidence moving: row 3's subject is now "the governed
> pipeline" rather than the implementation name, and row 6's `CANNOT_CHECK`
> selection is now written as leaving a claim "undetermined". Row 6 is still
> **NOT SUPPORTED**, and the rewritten Results and Limitations sections state
> more explicitly than the original why — the eligible family is saturated by
> construction, so the comparison had no resolving power and its null is an
> inability to discriminate rather than evidence that no difference exists.

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

## Addendum, 2026-08-22 — row 6 and the H3 negative

Annotated, not restated: row 6 and the last sentence of "Negative claims
retained" are the record of what was allowed on the V2 evidence, and they stay
as written.

Row 6's **NOT SUPPORTED — H3 null** is correct about the battery it was allowed
on and was never a comparative finding. `evidence/audit/P4_PANEL_RESOLUTION_2026-08-22.json`
puts a number on that: for the V2 panel, `correct_cannot_check_rate` is 1.0 for
all eleven systems, `metric_resolution` is `SATURATED`, `declared_ci95` is
`[0.0, 0.0]` and `verdict_could_have_differed` is `false`. A guard no system in
the panel can fail has not been passed, and a negative decided on it records the
instrument.

A battery on which the axis moves now exists and has been run once, under a
protocol frozen before the construction was repaired:
`evidence/protected_v3/` (`FREEZE.md`, `IDENTIFIABILITY_V3.json`, `PANEL_V3.json`,
`RESULT.md`). On it H3 is **SUPPORTED** at 1.0, CI95 `[1.0, 1.0]`: ORION selects
the correct `CANNOT_CHECK` terminal on 30/30 gold cases with 0/360 false
promotions, and the H1-selected comparator `provenai-citation-fidelity-influence`
scores 0/30. **`deepsciverify-abstract-to-full-escalation` scores 15/30, so
against it the margin is 0.5, not 1.0**; both numbers belong in any sentence
about H3. Reportable because the exact V3/`CANNOT_CHECK` claim axis clears at
informedness 0.0 over fourteen probes and thirteen seeds against a declared
ceiling of 0.0 — the same register recovers the V1 and V2 `CANNOT_CHECK` label at
1.0. Four registered digest-prefix noise-control residuals on `BLOCK`/`PROMOTE`
remain disclosed; no whole-register clearance is asserted.

What this does and does not change in the negatives above. `P4.H3` in
`journal_package/MANIFEST.json` is now SUPPORTED on the V3 artifacts, and the V2
entry is retained beside it as `P4.H3.V2`. What is claimed is **terminal
expressiveness under a non-compensatory gate lattice — the ability to report an
inability** — pre-registered in `FREEZE.md` §5 before the panel ran, and not a
finer-grained scientific judgement: nine of the ten comparators score 0 because
they cannot emit `CANNOT_CHECK` at all. So the retained negative "does not claim
H3 superiority" narrows rather than lifts. **General abstention superiority is
still not claimed**, and a panel of eleven systems in which ten are two-valued
cannot separate "better at knowing when it cannot check" from "the only one that
can say so". No number, evidence path or status on the V2 rows has been edited.
