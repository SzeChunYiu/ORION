# ORION-04 reproduction guide

ORION-04 is currently scoped to six **exact-synthetic matched-information mechanism studies** plus donor/negative bounds. It is not a real-agent deployment claim.

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

## Secondary paired uncertainty analysis

The publication analysis does **not** change any frozen protocol, seed, generator, arm, primary metric, gate or terminal. It rebuilds the original stochastic episodes and reports paired treatment/comparator differences with deterministic percentile-bootstrap intervals.

```bash
python papers/orion-08-typed-state/publication_analysis.py > /tmp/q4-publication-analysis.json
python - <<'PY'
import json
from pathlib import Path
expected = json.loads(Path('papers/orion-08-typed-state/PUBLICATION_PAIRED_ANALYSIS_V1.json').read_text())
actual = json.loads(Path('/tmp/q4-publication-analysis.json').read_text())
assert actual == expected
print('ORION-04 publication paired analysis: MATCH')
PY
```

`N4_D` is an exact constructed-chain census and is intentionally reported by exact counts rather than bootstrap uncertainty.

## Benchmark taxonomy

`BENCHMARK_INDEX_V1.json` maps the six separately frozen families into a common publication schema: binding axis, downstream decision, treatment, strongest comparator, hostile/no-value control, primary metric, generator/result/protocol and exact claim boundary. The taxonomy is a post-study synthesis; it does not retroactively make the six studies one preregistered experiment.

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
