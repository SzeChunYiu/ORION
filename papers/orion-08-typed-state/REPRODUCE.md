# ORION-08 reproduction guide

ORION-08 is scoped to six exact-synthetic matched-information mechanism studies, a corrected finite decision criterion, three bounded real-data studies, and donor/negative bounds. It is not a real-agent deployment claim.

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
print('ORION-08 publication paired analysis: MATCH')
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

## Corrected finite criterion

The publication-authority statement is in
`theory/binding-sufficiency-lattice-v1/THEOREM_CORRECTION_2026-09-01.md`.
Run the independent checker from repository root:

```bash
python papers/orion-08-typed-state/theory/binding-sufficiency-lattice-v1/independent_checker/check_binding_sufficiency.py
```

The checker imports no ORION-08 generator. It verifies the zero-regret criterion
and monotonicity over 2,233,980 configurations, the corrected refinement
strictness equivalence over 641,034 coarse/refined partition pairs, and three
negative controls, including a counterexample to the withdrawn shorthand.

## Real-data studies

The committed study directories are:

- `experiments/real-transfer-cc18-v1/`;
- `experiments/real-transfer-defects4j-v1/`;
- `experiments/real-transfer-rocrate-v1/`.

Each directory contains the protocol, runner, frozen output, findings, hashes,
and any amendments or post-hoc analyses. Verify its `SHA256SUMS` before running.
The OpenML and WorkflowHub runs may require network retrieval; use the pinned
source identities and do not replace unavailable records. Defects4J uses the
pinned upstream metadata recorded by the study. A reproduction must retain the
mixed held-out outcomes and the WorkflowHub `CANNOT_CHECK_NO_CONTRAST` terminal.

## Frozen protocols and replay

Protocols live under `development/orion-q-nlane-closure/`; deterministic replay status is recorded in `REPLAY_VERIFICATION_LEDGER.md`. `.github/workflows/orion-q-nlane-closure.yml` binds the frozen script/result/protocol identities used by the original closure.

## Publication synchronization

The current publication authority is `CLAIM_LEDGER_V4.md`, the LaTeX manuscript
tree, and the checksum-closed Tier-B package. Historical cross-paper registries
and V1--V3 manuscript/ledger files remain provenance and are not current release
authority. Run the Tier-B package verifier against the final package after any
source or metadata change.
