# ORION-08 — the finite-sample refinement law (derivation V1)

**Successor to** `real-transfer-cc18-v1` + `real-transfer-defects4j-v1` + the
addendum `ADDENDUM_OUT_OF_SAMPLE_IS_UNPREDICTED.md`.
**Status of this file:** derivation only. No outcome has been produced under it.
Additive successor study — no frozen Tier-B surface is modified.

## The gap this closes

Theorem 2 is exact on the distribution its fibres are defined on, and both real
legs confirm it in-sample. Out of sample the typed binding is negative on 3 of 5
CC18 datasets and fails on Cli/Csv in Defects4J, and the addendum proved that
**none of the four measured properties** (candidate-set size, training bugs,
fibre coverage, in-sample gain) predicts which. The findings file names the
mechanism in one sentence: *"a refinement has more fibres and fewer rows in
each, so it pays estimation error the theorem never claimed to govern."* This
study derives that estimation error as an exact, parameter-free functional of
the train-split fibre table, and tests whether its sign retrodicts the recorded
failures and predicts new ones.

## Setting (frozen from `run_real_transfer_cc18_v1.py`)

Rows are exchangeable within a fibre. A partition Π of the feature space has
fibre table {(n_f, k_f)}: train rows and train positives. A fresh held-out row
in fibre f has y ~ Bernoulli(p_f). The frozen utility is
U(1,1)=1, U(1,0)=−1, U(0,1)=U(0,0)=0, so per-fibre expected utility of action
a ∈ {0,1} is a·(2p_f − 1). The plug-in policy fit on train chooses
a_f = 1{k_f/n_f > 1/2}.

## The predictive functional

Under exchangeability with the uniform prior (the unique parameter-free
choice), p_f | k_f, n_f ~ Beta(k_f+1, n_f−k_f+1), posterior mean
p̄_f = (k_f+1)/(n_f+2). Define

  **Û(Π) = Σ_f ρ̂_f · a_f · (2 p̄_f − 1),  ρ̂_f = n_f/n.**

Û(Π) is the posterior-predictive expected utility of the plug-in policy on a
fresh row, conditional on the train fibre table. It is exact Bayesian
bookkeeping, not an approximation, and it contains no free parameter.

**Lemma (shrinkage form).** With a_f ∈ {0,1} and the threshold at 1/2,
(2p̄_f − 1) > 0 ⟺ (2k_f − n_f) > 0 ⟺ a_f = 1, so

  **Û(Π) = Σ_f ρ̂_f · max(0, (2k_f − n_f)/(n_f + 2)).**

*Proof.* (k+1)/(n+2) > 1/2 ⟺ 2k+2 > n+2 ⟺ 2k > n ⟺ k/n > 1/2. ∎

So each fibre's contribution is the MLE contribution max(0, (2k−n)/n) shrunk
by the factor n/(n+2). This is the mechanism in arithmetic form:

- the **population term** (what Theorem 2 governs) is the MLE sum
  Σρ̂·max(0,(2k−n)/n) — exactly the in-sample utility the v1 run measured;
- the **estimation cost** is the difference the n+2 denominator makes, which is
  negligible for large fibres and total for singletons (n=1: contribution 0);
- a refinement splits fibres, so it multiplies small-n fibres and shrinks its
  own value; the coarse binding keeps larger fibres and is shrunk less.

**The law to test:**
sign of the held-out Δ(policy under Π_refined − policy under Π_coarse) is
predicted by sign of Δ̂ = Û(Π_refined) − Û(Π_coarse), computed from the train
fibre tables alone.

## General thresholds (Defects4J leg)

With utility run-and-catch = b, run-and-miss = −c, skip = 0 (b=2.0, c=0.05 in
the D4J runner; optimal run iff p > c/(b+c) ≈ 0.0244), the same bookkeeping
gives Û(Π) = Σ_f ρ̂_f · a_f · (b·p̄_f − c·(1−p̄_f)) for the plug-in action a_f
fit at the MLE threshold. Lemma 1 does not extend to thresholds ≠ 1/2, so at
low thresholds the shrunk mean can disagree with the MLE action; the law keeps
a_f as fit (it predicts the out-of-sample utility **of the policy as actually
fit**, which is the quantity `OUT_OF_SAMPLE_V1.json` measured).

## Why this is not one of the four refuted predictors

The addendum refuted size, training-bugs, coverage, and in-sample gain as
single scalars. Û is a per-fibre aggregation whose value depends on **where
the in-sample gain lives**: gain concentrated in large fibres survives the
shrinkage; gain concentrated in small fibres does not. Two datasets with
identical in-sample gain and identical size (the addendum's Cli-vs-Gson pair,
0.200 vs 0.202) can differ in Δ̂. That is the discriminating prediction: the
law must put **Cli negative and Gson positive**.

## What would falsify it

1. Retrodiction: any of the 5 scored CC18 datasets where sign(Δ̂) ≠ sign of
   the recorded held-out typed Δ (credit-g −, diabetes −, spambase +,
   qsar-biodeg 0, wdbc −).
2. Retrodiction: Cli predicted ≥ 0, or Gson predicted ≤ 0, on the D4J leg.
3. Prospective: ≥ 3 sign disagreements on the pre-registered new-dataset
   cohort (gate P1 below), or any predicted-positive-but-strongly-observed-
   negative contradiction.
4. Sensitivity: primary result must survive the Jeffreys prior
   Beta(k+½, n−k+½) — a parameter-free alternative — on every sign claim.

Honest-null discipline: a dataset where Δ̂ ≈ 0 (|Δ̂| < 1e-12) is recorded as
predicted-zero and must not be counted as agreement with a nonzero observed
sign in either direction without being reported.
