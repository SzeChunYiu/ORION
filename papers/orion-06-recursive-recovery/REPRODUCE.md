# Q2 reproduction guide

Q2 is a **methodology/case-study** paper. Its numbers are sourced from the closed ORION-Q receipts; Q1 owns the quantum theorem claim itself.

## Provenance map

Start with:

- `development/orion-q-max-r0/PROGRAMME_CLOSURE_PACKET_2026-08-21.md`
- `papers/Q-paper-02-recursive-recovery/RECEIPT_INDEX.md`
- `papers/Q-paper-02-recursive-recovery/RECEIPT_INDEX_V2.md`
- `development/orion-q-nlane-closure/REPLAY_VERIFICATION_LEDGER.md`

The original index plus V2 cover the 47 result receipts used by the final manuscript.

## Re-run the final R6 explanatory arc

The load-bearing Q2 chronology is R6N → R6O → R6P → R6Q → R6R → R6S. The corresponding runners are under `research/extensions/orion-q/`:

```bash
python research/extensions/orion-q/max_r6n_support_dominance_audit.py
python research/extensions/orion-q/max_r6o_enlarged_tag_donor_closure.py
python research/extensions/orion-q/max_r6p_weight2_frame_donor_closure.py
python research/extensions/orion-q/max_r6q_regime_predicate.py
python research/extensions/orion-q/max_r6r_prospective_fresh_subject.py
python research/extensions/orion-q/max_r6s_all_n_composition.py
```

Some runs are intentionally heavy. The committed receipt/replay ledgers remain the publication evidence when a release build elects not to rerun a heavy chemistry path.

## Re-run the N4 primary mechanism suite

```bash
python research/extensions/orion-q/nlanes/n4_a_unknown_voi.py
python research/extensions/orion-q/nlanes/n4_b_stale_receipt_reopening.py
python research/extensions/orion-q/nlanes/n4_c_interval_pareto.py
python research/extensions/orion-q/nlanes/n4_d_laundering_detection.py
python research/extensions/orion-q/nlanes/n4_e_active_experiments.py
python research/extensions/orion-q/nlanes/n4_f3_remint_transport.py
```

Additional N1/N2/N3 scripts and immutable result identities are enumerated by `.github/workflows/orion-q-nlane-closure.yml`.

## Publication synchronization

```bash
pytest tests/unit/publication/test_framework_snapshot.py \
       tests/unit/publication/test_q_series_final_spec.py \
       tests/unit/publication/test_q_series_content_binding.py
```

A green run confirms that the final Q2 paper still points to the final closure/evidence set. It does not demonstrate cross-domain superiority; that stronger question remains the separately frozen successor protocol.
