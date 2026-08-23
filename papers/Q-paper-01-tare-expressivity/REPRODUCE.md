# Q1 reproduction guide

This guide reproduces the **internal evidence package**, not external novelty or journal review.

## Lightweight independent theorem sanity check

From repository root:

```bash
python papers/Q-paper-01-tare-expressivity/independent_human_proof_sanity.py
```

The output should match:

`papers/Q-paper-01-tare-expressivity/INDEPENDENT_HUMAN_PROOF_SANITY_RESULTS_2026-08-22.json`

Key checks:

- no ORION quantum/compiler import;
- local Restore bound `max_delta_f3 = 2`;
- exactly four support-2 class failures;
- zero class-lemma failures for support 3 through 8.

## Original all-n machine certificate

```bash
python research/extensions/orion-q/max_r6s_all_n_composition.py
```

Expected committed receipt:

`research/extensions/orion-q/MAX_R6S_ALL_N_COMPOSITION_RESULTS.json`

The publication proof is analytic (`HUMAN_PROOF_R6S_2026-08-22.md`); this runner is independent machine corroboration and stress testing, not the sole proof.

## Sharp support-one counterexample / D+ completeness

The support-one family definition is frozen in:

`development/orion-q-max-r0/MAX_R6O_ENLARGED_TAG_DONOR_PROTOCOL.md`

and the exact result/witness is:

`research/extensions/orion-q/MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json`

The load-bearing row is structured `n=2`, `instance_index=16`, with

`C_DP = 5 < C_D+ = 6`.

To re-execute the R6O audit:

```bash
python research/extensions/orion-q/max_r6o_enlarged_tag_donor_closure.py
```

This is substantially heavier than the standalone proof sanity check.

## Split-TARE coefficient lemma

Human proof:

`HUMAN_PROOF_R4B_MAJORISATION_2026-08-22.md`

Original deterministic runner:

```bash
python research/extensions/orion-q/max_r4b_tare_split_majorization.py
```

Committed receipt:

`research/extensions/orion-q/MAX_R4B_TARE_SPLIT_MAJORISATION_RESULTS.json`

## Publication synchronization

Run the Q-specific publication checks with the repository test environment:

```bash
pytest tests/unit/publication/test_framework_snapshot.py \
       tests/unit/publication/test_q_series_final_spec.py \
       tests/unit/publication/test_q_series_content_binding.py
```

A green run establishes internal synchronization only. It does not grant novelty, physical-resource superiority or quantum advantage.
