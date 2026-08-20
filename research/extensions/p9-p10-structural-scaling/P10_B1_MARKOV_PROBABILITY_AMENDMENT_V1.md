# P10 B1 Markov Probability Amendment V1

Status: **FROZEN BEFORE NATIVE-STATE OUTCOMES**

Frozen: 2026-08-20

The V2.1 B1 Markov comparator originally required only an argmax next-action prediction. The native-state protocol additionally compares multiclass log loss, which requires a probability assigned to the true action. This amendment freezes that probability adapter without changing any B1 accuracy prediction.

## Accuracy prediction

For every leave-top-module-out fold, reconstruct the exact V2.1 source trajectories in original frozen manifest/source order. B1 is trained on the **full frozen V2.1 source-transition training population**, including transitions that may lack a new native-state receipt. For each previous tactic family, predict the most-common following family exactly as V2.1; unseen previous families back off to the global most-common following family.

The primary B1/B4 accuracy comparison is evaluated only on the identical native receipt-eligible held-out transition rows. Giving B1 all source-training transitions is conservative when native-state coverage is below 100%.

## Probability adapter

For log loss only, use add-one/Laplace smoothing over the fixed 16 P10 tactic families:

`P(y | h) = (count(h,y)+1) / (sum_y count(h,y)+16)`.

For a previous family unseen in training, use add-one-smoothed global following-family counts:

`P(y) = (global_count(y)+1) / (sum_y global_count(y)+16)`.

The B1 argmax used for accuracy is still the unsmoothed exact V2.1 most-common prediction, so this probability adapter cannot alter the historical accuracy baseline.

No smoothing constant may be tuned from native-state outcomes.
