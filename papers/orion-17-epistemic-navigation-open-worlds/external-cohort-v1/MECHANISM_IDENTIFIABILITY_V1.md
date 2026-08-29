# ORION17.MECHANISM_IDENTIFIABILITY.v1 — why the disagreement study cannot identify density

**Parent study:** `ORION17.RULE_DISAGREEMENT.v1.study`  
**Parent terminal:** `NO_DISCRIMINATION`  
**Status:** `STRUCTURAL_DIAGNOSIS_PROVED_FROM_FROZEN_RESULT`  
**Scientific authority delta:** `NONE`

This note does not rescue the density rule and does not fit a replacement threshold. It
explains why the completed prospective disagreement study is non-identifying even though
all 20 requested repositories were measured.

## 1. Constant-outcome theorem

Let `I` be the set of informative, nondegenerate cases, let the binary outcome be
`Y in {sound, unsound}`, and let `R` be any binary prediction rule. If `Y` is constant on
`I`, then

`accuracy_I(R) = fraction of cases on which R predicts that constant label`.

**Proof.** With `Y=y0` for every case, the indicator of correctness is exactly
`1{R=y0}`. Averaging gives the identity. ∎

Therefore accuracy differences among rules on a constant-outcome panel measure only how
often the rules emit the constant label. They cannot establish that one rule tracks
variation in the outcome, because there is no outcome variation to track.

The parent result has exactly this form: all **16/16 nondegenerate repositories are
UNSOUND**. On that subset, density accuracy `10/16` means only that density predicts
`unsound` on ten cases; the module and edge rules score `6/16` because they predict
`unsound` on six. No mechanism is identified by those accuracies.

## 2. Disagreement-stratum corollary

The cohort was selected into two strata in which density and both absolute-size rivals
make opposite predictions by construction.

- `small_fewedge_dense`: density predicts UNSOUND; both rivals predict SOUND.
- `large_manyedge_sparse`: density predicts SOUND; both rivals predict UNSOUND.

If every informative outcome is UNSOUND, every informative case in the first stratum is a
density win and every informative case in the second is a rival win. The paired score is
therefore determined by **how many informative cases remain in each stratum**, not by a
relationship between the rules and a varying outcome.

That is exactly the frozen result: after removing mechanical degeneracies, the first
stratum contributes **10 density wins / 0 rival wins** and the second contributes
**0 density wins / 6 rival wins**. The resulting 10–6 split is a census of retained stratum
sizes under a constant outcome.

## 3. Degeneracy-confounding theorem

Suppose a measurement defect `D` forces the observed outcome to SOUND regardless of the
latent mechanism being compared. Such a case is uninformative for every rule. If it is
nevertheless scored as an ordinary outcome, it awards a correctness point exactly to rules
that predict SOUND on that case.

The parent study proves this defect for the donor-coarse instrument on four `src/`-layout
repositories: the bucket expression collapses all modules to the package name, the policy
reopens everything, and false-closure retention is mechanically zero. All four degenerate
cases occur in the large/sparse stratum, where density predicts SOUND and both size rivals
predict UNSOUND. Consequently those four cases add **four density wins by construction**.

Thus the all-20 14–6 density score decomposes exactly as

`10 informative small/dense wins + 4 degenerate sound credits` versus
`6 informative large/sparse rival wins`.

The four added wins are not mechanism evidence.

## 4. Why the frozen gate correctly returns NO_DISCRIMINATION

The preregistered density gate requires at least 15/20 wins and at least 7/10 in each
stratum. Density obtains 14/20 and 4/10 in the large/sparse stratum, so it fails. Neither
absolute-size rival passes the same gate. `NO_DISCRIMINATION` is therefore the correct
frozen terminal.

The stronger diagnosis here is that the failure is not simply "sample size too small".
The informative subset has no outcome variation, and the observed sound cases are
measurement-degenerate. Increasing N under the same measurement/selection mechanism can
still fail to identify the competing rules.

## 5. A separate protocol-authority limitation

`STUDY_V1.json` records another important boundary: the original
`ORION17_RULE_DISAGREEMENT_PROTOCOL_V1.json` froze terminals and thresholds but did **not**
freeze an exact outcome-measurement definition. The executed study recovered
`false_closure_retention > 0` from the campaign's pre-existing instrument.

That is preferable to inventing a new outcome, but it is not the same as a prospectively
frozen operationalization. A future decisive study must bind the exact instrument,
parameters, repository-layout normalization, degeneracy conditions, and terminal semantics
before outcomes are accessed.

## 6. What a valid successor must change — without rescuing this result

A new identity may proceed only if it fixes the measurement design rather than changing a
threshold after seeing outcomes. Minimum requirements:

1. **Freeze outcome operationalization first.** Exact script/version, history depth,
   `n_changes`, definition of false retention, and failure/CANNOT_CHECK semantics.
2. **Eliminate layout degeneracy prospectively.** Either normalize package roots in a
   separately validated instrument or exclude a mechanically proven degenerate layout by a
   pre-outcome rule. Do not decide exclusion from observed SOUND/UNSOUND labels.
3. **Use untouched repositories.** None of the 8 historical campaign projects or the 20
   V1 disagreement repositories may count as fresh confirmation.
4. **Keep the three rules frozen.** Density 1.5 and rivals 49/216 remain historical
   hypotheses; no fitted replacement threshold under the same question.
5. **Add an identifiability terminal.** If the nondegenerate protected cohort contains no
   outcome variation, terminate `CANNOT_CHECK_MECHANISM__OUTCOME_CONSTANT`; do not rank
   rules by accuracy.
6. **Retain symmetric scoring.** Density and each rival receive exactly the same outcome,
   exclusions, missing-data handling, and inferential gate.

A new rule based on layout, package structure, or any other feature observed after V1
outcomes is a **new hypothesis** requiring its own derivation/protected cohort. It cannot be
reported as the explanation validated by V1.

## 7. Claim ceiling

Earned: the completed study rejects unique mechanism identification and exposes a
measurement degeneracy plus constant-outcome non-identifiability.

Not earned: density is true, density is false, absolute size is true, `src/` layout is the
scientific mechanism, or a new threshold/rule. The earlier 5/5 prospective density
observation remains historical evidence at its original scope; V1 does not promote it to a
unique mechanism.

**Terminal:** `MECHANISM_NOT_IDENTIFIABLE__CONSTANT_INFORMATIVE_OUTCOME_PLUS_LAYOUT_DEGENERACY`.
