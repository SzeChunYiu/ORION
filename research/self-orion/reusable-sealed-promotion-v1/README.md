# Reusable sealed promotion v1

This is the combined ORION-15/ORION-24 top-tier promotion lane proposed after the Wave-3 scoped papers were frozen.

The target is not another small attribution panel. It is a longitudinal study of adaptive method revision in which:

- candidates are generated over multiple inherited rounds;
- protected evidence can be reused only through a leakage-accounted sealed mechanism;
- promotion requires simultaneous fresh-benefit, retention, harm, resource, and authority gates;
- negative, blocked, and `CANNOT_CHECK` history remains append-only;
- candidate generation, evaluation, promotion, and independent verification have separate identities;
- real externally sourced tasks and strong fair baselines determine empirical authority.

The formal lane introduces a leakage-adjusted familywise false-promotion theorem. For an adaptively selected candidate, a fixed-candidate level-`u_j` protected test exposed through a transcript with approximate max-information budget `(kappa_j,beta_j)` has false-rejection probability at most `exp(kappa_j)u_j+beta_j`. Promotion is an intersection of fresh, retention, and harm tests, so one true component null is enough to bound a bad promotion. If the sum of effective debits over all adaptive rounds and evaluator epochs is at most `alpha`, the probability of any false promotion is at most `alpha`, even under data-dependent stopping.

The implementation uses exact rational debit accounting and a hash-chained append-only ledger. It fails closed on missing leakage inflation, duplicate conflicts, stale candidate bytes, alpha reset, missing non-compensatory gates, candidate-controlled authority, or deleted negative history.

Run the conformance and hostile controls:

```bash
python -m pytest -q tests/research/test_reusable_sealed_promotion_v1.py
python research/self-orion/reusable-sealed-promotion-v1/run_conformance_campaign.py \
  --output /tmp/reusable-sealed-conformance
python research/self-orion/reusable-sealed-promotion-v1/independent_checker/verify_campaign.py \
  --campaign /tmp/reusable-sealed-conformance \
  --output /tmp/reusable-sealed-verification.json
```

The conformance campaign grants formal/software authority only. Protected longitudinal transfer, fair-comparator superiority, negative-history benefit, frontier-agent performance, and submission authority remain false until the real external protocol is executed.
