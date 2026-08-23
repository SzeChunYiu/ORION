# Q4 reproduction guide

Q4 is currently scoped to six **exact-synthetic matched-information mechanism studies** plus donor/negative bounds. It is not a real-agent deployment claim.

## Primary six-study suite

From repository root:

```bash
python research/extensions/orion-q/nlanes/n4_a_unknown_voi.py
python research/extensions/orion-q/nlanes/n4_b_stale_receipt_reopening.py
python research/extensions/orion-q/nlanes/n4_c_interval_pareto.py
python research/extensions/orion-q/nlanes/n4_d_laundering_detection.py
python research/extensions/orion-q/nlanes/n4_e_active_experiments.py
python research/extensions/orion-q/nlanes/n4_f3_remint_transport.py
```

Committed result artifacts:

- `N4_A_UNKNOWN_VOI_RESULTS.json`
- `N4_B_STALE_RECEIPT_REOPENING_RESULTS.json`
- `N4_C_INTERVAL_PARETO_RESULTS.json`
- `N4_D_LAUNDERING_DETECTION_RESULTS.json`
- `N4_E_ACTIVE_EXPERIMENTS_RESULTS.json`
- `N4_F3_REMINT_TRANSPORT_RESULTS.json`

all under `research/extensions/orion-q/nlanes/`.

## Donor/negative bounds

The two load-bearing bounding studies are:

```bash
python research/extensions/orion-q/nlanes/n1c_costly_verification_voi.py
python research/extensions/orion-q/nlanes/n2_f5b_donor_comparison.py
```

They prevent the final manuscript from promoting the typed-state result into a universal policy or crossover-prediction claim.

## Frozen protocols and replay

Protocols live under `development/orion-q-nlane-closure/`; deterministic replay status is recorded in `REPLAY_VERIFICATION_LEDGER.md`. `.github/workflows/orion-q-nlane-closure.yml` binds the frozen script/result/protocol identities used by the original closure.

## Publication synchronization

```bash
pytest tests/unit/publication/test_framework_snapshot.py \
       tests/unit/publication/test_q_series_final_spec.py \
       tests/unit/publication/test_q_series_content_binding.py
```

The future real-domain protocol in `TOP_TIER_UPGRADE_PROTOCOL_2026-08-22.md` is not part of the current evidence package and must not be described as executed.
