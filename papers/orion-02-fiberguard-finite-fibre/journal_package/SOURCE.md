# When a Representation Can Certify: Sharp Fibre-Diameter Limits and Minimal Refinement

**ORION-02 — canonical submission manuscript V3**  
**Scientific cut:** fibre-diameter floor, refinement-to-certifiability theorem, and the preserved R24 certification failure  
**Status:** bounded theory/methodology manuscript; no empirical superiority claim

## Abstract

A representation can be sufficient for making a decision while remaining insufficient for certifying the value attached to that decision. We give an exact finite-fibre characterization of this gap. Let `phi` map instances to a representation, let `F_z` be a representation fibre, let `V` be the target quantity, and let `D(z)` be the range of `V` on that fibre. Any deterministic point certificate that is constant on `F_z` has worst-case error at least `D(z)/2`, and any interval of radius below `D(z)/2` must miss at least one fibre member. The bound is sharp.

The same quantity gives a constructive converse. A fibre admits an `eps`-valid constant certificate if and only if `D(z) <= 2 eps`; the midpoint of its extreme target values is then valid. For finite fibres, the minimum number of refined parts required for `eps`-valid certification is exactly the count returned by a greedy interval sweep over the sorted target values. Under a restricted separator family, certification is possible if and only if the separators distinguish every pair whose target values differ by more than `2 eps`. Without refinement, achievable coverage is exactly the mass of fibres already satisfying `D(z) <= 2 eps`. These results turn a representation-induced impossibility boundary into an exact refine-or-abstain law.

Exhaustive independent checks found no violations over the registered finite configuration families and include planted counterexamples to show that the checkers can fail. We also retain a prospective empirical failure that motivated the theory: a frozen certificate study reached `44/44` coverage but incurred `20/44` strict held-out violations, and its available selection score was not detectably correlated with realised excess (`r=-0.144`, permutation `p=0.353`, `n=44`). Those data do not establish the fibre diameters of the real corpus; they show why marginal coverage and a weak selector cannot substitute for conditional certifiability. The contribution is therefore a sharp representation-level certification criterion and exact refinement calculus, not a claim of broad empirical transfer.

## 1. Introduction

Many learned and rule-based systems compress a complex object into a representation before making a prediction, selecting an action, or issuing a certificate. The representation may be excellent for one query and inadequate for another. A state summary can identify which action to take while failing to identify how much value that action carries. A classifier can have good marginal performance while a conditional certificate fails on the subset where it is actually used. A coarse state can support a ranking but not a guarantee.

This paper asks a narrower question than general representation learning: **when can a fixed representation support a uniformly valid certificate, and what is the minimum refinement required when it cannot?** The answer is governed by one object, the target diameter of each representation fibre. If two instances are indistinguishable to the certificate but their target values are far apart, no tuning of the certificate can make that ambiguity disappear. Conversely, once refinement reduces every fibre diameter below the target tolerance, a valid certificate exists by construction.

This deterministic viewpoint complements statistical work on marginal, conditional, and selection-conditional uncertainty. Conformal prediction supplies distribution-free marginal guarantees under exchangeability, while recent selective-conformal work studies how coverage changes after data-dependent selection. Those methods address sampling validity. Our question is prior to sampling: if a representation maps two target-separated instances to the same observable state, then no fibre-constant certificate can distinguish them, regardless of calibration procedure. We therefore treat conditional coverage methods as donors for the statistical layer and isolate the representation-level obstruction underneath it.

The paper makes five claims. First, `D(z)/2` is the exact worst-case radius of any deterministic point certificate accepted on a fibre. Second, `D(z) <= 2 eps` is necessary and sufficient for an `eps`-valid fibre-constant certificate. Third, the minimum unconstrained refinement cost is exactly computable by a greedy interval sweep. Fourth, a restricted separator family can realize certification exactly when it separates every pair with target gap greater than `2 eps`. Fifth, without refinement the maximum certifiable coverage is exactly the probability mass of already-small fibres, giving a refine-or-abstain frontier.

These claims do **not** rely on the earlier `A_t/B_t` gadget family from the previous manuscript. An adversarial proof review found that those all-`t` formulas require an unstated cross-gadget separability argument under a non-additive global width term. V3 therefore removes that family, its minimax corollaries, the conditional four-index compiler theorem, and the missing single-block convention from the submission spine. They remain historical research records, not premises of the present paper.

## 2. Setting and terminology

Let `X` be a finite instance set and let

`phi : X -> Z`

be a representation. For an observed state `z`, define the fibre

`F_z = {x in X : phi(x) = z}`.

Let

`V : X -> R`

be the scalar target to be certified. Its fibre diameter is

`D_phi(z) = max_{x,x' in F_z} |V(x)-V(x')|`.

A deterministic point certificate based only on `phi` is a function `c : Z -> R`. It is accepted on a fibre when it is issued for every member of that fibre. Because all members share the same representation, the certificate must return the same value for all of them.

An interval certificate is likewise a function of `z`; write its centre as `c(z)` and radius as `r(z)`. At a fixed tolerance `eps >= 0`, a point certificate is `eps`-valid on `F_z` when

`|c(z)-V(x)| <= eps`

for every `x in F_z`.

A representation `phi'` refines `phi` when equality under `phi'` implies equality under `phi`. Equivalently, every `phi'` fibre is contained in one `phi` fibre.

The theory is deliberately finite and deterministic. It assumes no sampling model, prior, exchangeability, smoothness, learned model class, or computational hardness. Statistical estimation of `D(z)` and learning a useful refinement are separate problems.

## 3. The fibre-diameter floor

### 3.1 Point certificates

**Theorem 1 (sharp point-certificate floor).** For every fibre `F_z` and every deterministic point certificate `c(z)` accepted on it,

`max_{x in F_z} |c(z)-V(x)| >= D_phi(z)/2`.

**Proof.** Choose two fibre members with target separation `D_phi(z)`. By the triangle inequality,

`D_phi(z) <= |V(x)-c(z)| + |c(z)-V(x')|`.

At least one term is therefore at least `D_phi(z)/2`. Conversely, the midpoint

`c*(z) = (min_{x in F_z} V(x) + max_{x in F_z} V(x))/2`

has worst-case error exactly `D_phi(z)/2`. The bound is exact. ∎

This is an information statement rather than a complexity statement. Unlimited compute cannot beat the radius while the certificate sees only `z`.

### 3.2 Interval certificates

**Theorem 2 (interval floor).** An interval of radius `r < D_phi(z)/2` cannot contain `V(x)` for every `x in F_z`.

The result follows because any interval covering all target values on the fibre must span a set of diameter `D_phi(z)` and therefore have width at least `D_phi(z)`.

A probabilistic corollary follows immediately. If a conditional distribution places probability one half on each endpoint of a diameter-attaining pair, then every fibre-constant interval with radius below `D_phi(z)/2` has conditional miscoverage at least one half. This is a worst-case witness, not a statement that every real fibre has such a distribution.

## 4. From impossibility to construction

The floor becomes useful when read as an exact design criterion rather than only as a negative result.

### 4.1 Exact certifiability threshold

**Theorem 3 (certifiability equivalence).** An `eps`-valid deterministic point certificate constant on a fibre exists if and only if

`D_phi(z) <= 2 eps`.

Necessity is Theorem 1. Sufficiency is constructive: the midpoint certificate lies within half the diameter of every fibre member.

Thus a representation is not “approximately certifiable” in an informal sense. At a declared tolerance, each fibre is either already certifiable or must be split.

### 4.2 Minimum unconstrained refinement

Fix one fibre and sort its target values:

`v_1 <= v_2 <= ... <= v_n`.

A refined part is certifiable at tolerance `eps` exactly when its diameter is at most `2 eps`. The problem is therefore to cover the sorted values with the fewest intervals of length `2 eps`.

**Theorem 4 (exact minimum refinement cost).** The minimum number of certifiable parts equals the count returned by the following greedy sweep: start a part at the smallest uncovered value and include every subsequent value no more than `2 eps` above that part's minimum; then repeat on the remaining suffix.

**Proof sketch.** An optimal part containing the smallest remaining value cannot extend beyond that value plus `2 eps`. The greedy first part covers every point any feasible first part could cover. Replacing an optimal first part by the greedy one cannot increase the number of parts. Induction on the remaining suffix proves optimality. ∎

Write this minimum as `k*(z,eps)`. The number `k*-1` is the exact unconstrained number of additional representation states required to make that fibre certifiable.

### 4.3 What available separators can realize

An abstract partition may not be obtainable from the information a system can actually compute. Let `S` be a family of admissible predicates or features, and require the refined representation to be measurable with respect to `S`.

Two instances are `S`-indistinguishable when every predicate in `S` takes the same value on them.

**Theorem 5 (separator realizability).** An `S`-measurable `eps`-valid refinement exists if and only if every `S`-indistinguishable pair satisfies

`|V(x)-V(x')| <= 2 eps`.

**Proof.** If an indistinguishable pair exceeds `2 eps`, every `S`-measurable representation places it in one atom, which is uncertifiable by Theorem 3. Conversely, if no such pair exists, each atom of the joint `S`-signature has target diameter at most `2 eps`; the midpoint certificate is valid on every atom. ∎

This theorem separates two costs that are easy to conflate. `k*` is the information-theoretic minimum over arbitrary refinements. The realizable cost depends on the separator vocabulary. A weak vocabulary may require more states than `k*`, and if it merges one target-separated pair it cannot certify the fibre at any number of downstream tuning steps.

## 5. The refine-or-abstain frontier

Suppose fibres have probability mass `P(phi=z)` under a target population. Without refinement, a fibre can be certified at tolerance `eps` exactly when `D_phi(z) <= 2 eps`.

**Theorem 6 (coverage identity).** The maximum coverage achievable by a certificate that either accepts an entire original fibre or abstains on it is

`sum_z P(phi=z) * 1{D_phi(z) <= 2 eps}`.

Refining an uncertifiable fibre purchases exactly that fibre's probability mass at the representation cost required to split it into certifiable parts. Under unconstrained refinement that cost is `k*(z,eps)-1`; under a separator family, it is the corresponding measurable refinement cost.

This gives an exact frontier rather than a generic recommendation to “use more features.” For each fibre, the relevant questions are: how large is the target diameter, which target-separated pairs the available information can distinguish, and whether the purchased coverage is worth the required refinement.

## 6. Independent verification

The mathematical statements are proved above. Separate exhaustive checkers were used as hostile finite-model verification rather than as theorem authority.

For the fibre-diameter floor, the registered checker enumerated 784 finite configurations. It found zero point certificates beating `D/2`, zero intervals of radius below `D/2` covering both diameter endpoints, and zero balanced two-point examples with miscoverage below one half. Its negative controls give the certificate access to the member identity and require the checker to detect that the floor can then be beaten; planted violations fired rather than passing vacuously.

For the refinement theorem, the registered checker covered 4,704 main configurations plus nested separator enumerations. It compared the greedy part count against an exhaustive enumeration of set partitions on an independent code path. The registered claims R1-R5 had zero violations. Planted-violation controls fired for the sufficiency, necessity, separator, and coverage predicates, while the no-alarm control stayed silent.

These finite enumerations test implementation and transcription. General authority comes from the proofs, not from the absence of a small counterexample.

## 7. A preserved adverse empirical boundary

The theory was motivated by a sequence of failed certificate constructions, and those failures remain part of the scientific record rather than being overwritten by the later theorem.

The first counted revival attempt, R23, asked whether a Hamming-radius backoff could restore certified coverage on 44 held-out PMLB decisions. Against a corrected exact-cell parent at `0/44 = 0.0000`, the backoff reached `32/44 = 0.7273`. That improved coverage substantially but missed the frozen `0.95` gate. The outcome-independent lexical negative control, which ignores the geometry entirely, reached `39/44 = 0.8864` — a higher raw count than the registered Hamming geometry. That gap is not statistically established. The two arms are evaluated on the same 44 decisions under the same fold assignment, so the comparison is paired: of the 13 datasets on which the arms disagree, the control certifies 10 and the geometry 3, giving an exact McNemar two-sided `p = 0.0923` and a 20,000-replicate paired bootstrap interval on the difference of `[-0.3182, 0.0000]`, which does not exclude zero (`rounds/r23-density-backoff-revival/R23_CONTROL_PAIRED_TEST_V1.json`, recomputed from the per-dataset records by `verify_r23_control_paired_test.py`). The proposed geometry was therefore not validated by this round, but the reason is that it missed the frozen `0.95` gate at `0.7273`, not that the control outperformed it: the data do not support the stronger claim that a geometry-free baseline beats the geometry. Within the same round, the primary learned ordering minus the matched static adaptive arm had mean excess difference `-0.001218244987` with bootstrap 95% interval `[-0.011716227308, 0.008821064426]`, while acquiring more groups on average (`1.113636` versus `0.840909`); it did not establish learned-ordering value, and it carried 24 strict realized-bound violations among 42 certified commits. The R23 terminal is `C_R23_PMLB_BACKOFF_COVERAGE_IMPROVED_BELOW_GATE`.

The second counted attempt, R24, evaluated the same 44 held-out decisions. Its arm-conditional construction raised coverage from R23's `32/44` to `44/44`, meeting the registered `0.95` gate — and validity still failed: strict held-out violations were `20/44 = 0.455`, against a registered maximum of `0.10`. A matched no-geometry lexical control also reached `44/44` coverage, with fewer violations than the geometric arm (14 versus 20), so the registered geometry again supplied no measured advantage on that corpus. The R24 terminal remains `C_R24_ARM_CONDITIONAL_CERTIFICATE_INVALID`.

Across both counted attempts the same negative control outperformed the registered geometry. That repetition, rather than either round alone, is what the theory section treats as the empirical boundary worth explaining.

A subsequent diagnostic on the same committed records showed that the registered target was arithmetically infeasible at full coverage: `11/44 = 0.25` held-out excesses exceeded `tau=0.02`, whereas the gate required at most `0.10` violations with a bound no larger than `tau`. A split-conformal bound valid at `alpha=0.10` on all 44 points was `0.061381`, about `3.07 tau`.

An oracle abstention analysis showed that a useful interior point existed: removing the 25% highest realised-excess cases left 33 cases with zero violations and a conformal bound `0.016837`, below `tau`. This oracle is not an implementable method because realised excess is unknown at decision time.

The available model score did not provide a substitute. Its Pearson correlation with realised excess was `-0.1442` (`p=0.3528` under 20,000 permutations; Spearman `rho=-0.1921`, `n=44`). Abstaining on that score made the retained violation rate worse. A noise-degraded oracle simulation suggested that correlations near `0.85` would be needed on that one empirical distribution, but the value is a design target for a successor, not a general constant.

These observations are **not** used to claim that R24's real fibres have a measured diameter above `2 eps`; the study did not measure `D(z)` directly. They establish a narrower point: the empirical certificate was invalid, full coverage at the registered gate was impossible on the realised excess distribution, and the available selector did not identify the cases on which abstention would help. The theory states what must be measured or refined next.

## 8. Relation to prior work

The general mathematical ingredients are donor-owned. Sufficient-statistic and comparison-of-experiments theory establish that information is valuable relative to a decision problem rather than in the abstract. Robust decision theory likewise studies performance when observations leave sets of compatible states. Interval covering on a line and the greedy minimum-cover argument are classical algorithmic facts. We make no novelty claim for those components.

Conformal prediction provides finite-sample marginal coverage under exchangeability. Recent work on selection-conditional conformal inference makes the selection event part of the validity target; Jin and Ren (2024) give exact selection-conditional procedures for broad classes of selection rules, while Sale and Ramdas (2025) identify failures in online selective calibration and give exchangeability-preserving alternatives. Current conditional-coverage work continues to study how local reliability can be assessed and compared. Those methods operate at the statistical calibration layer.

The present paper isolates a complementary deterministic layer: **before asking whether calibration is statistically valid, ask whether the representation identifies the target finely enough for any fibre-constant certificate at the requested tolerance.** Its residual contribution is the exact joint calculus linking fibre diameter, deterministic certificate radius, minimal partition refinement, separator realizability, and abstention coverage, together with a preserved empirical failure that motivates the distinction.

## 9. Limitations

1. The core theorems concern finite fibres and a scalar target. Infinite spaces require topological or measurable extensions that are not supplied here.
2. The point-certificate results are deterministic. Randomized certificates require an explicit loss and coverage convention.
3. The theorem assumes the target values on a fibre when constructing the midpoint and computing minimal refinement. Learning or estimating those values without leakage is a separate statistical problem.
4. Separator realizability says when a declared feature family is sufficient. It does not learn the family or price feature acquisition.
5. The R24 corpus does not directly measure `D(z)` on accepted fibres. It is an adverse application record, not empirical confirmation of the diameter law.
6. The selector-correlation threshold near `0.85` comes from one 44-case realised distribution and is not a universal requirement.
7. No cross-domain transfer, production benefit, physical quantum advantage, computational-hardness result, or broad empirical superiority is claimed.
8. Earlier V2 compiler theorems depending on unstated dominance, single-block, padding, or cross-gadget assumptions are not part of the V3 submission claim. Their historical records are retained for audit.

## 10. Discussion and conclusion

A representation is not simply sufficient or insufficient. Sufficiency is relative to the question and to the tolerance at which an answer must be certified. The target diameter of a representation fibre makes that statement exact. If `D(z) > 2 eps`, no deterministic certificate that sees only `z` can meet error `eps`; if `D(z) <= 2 eps`, the midpoint certificate meets it immediately.

That equivalence turns an impossibility result into a design calculus. Minimal unconstrained refinement is an exact interval-cover problem. Realizable refinement is controlled by separator power. Abstention covers precisely the fibres that are already narrow enough. The resulting frontier separates three failure modes that are otherwise easy to mix: a certificate may be badly calibrated, the selector may fail to identify difficult cases, or the representation may merge target-separated instances so that no calibration can succeed without refinement.

The preserved R24 result illustrates why the distinction matters. Coverage reached every held-out case while conditional validity failed, and the available selector carried no detected signal about realised excess. The appropriate response is not to relax the gate after observing that failure. It is to measure the information problem prospectively: estimate fibre diameter, test separator sufficiency, or learn a selector under disjoint custody and then validate the retained set.

The bounded conclusion is therefore simple: **certifiability is governed by within-representation target variation, and the cost of repairing an insufficient representation can be characterized exactly.** The external multi-domain question—whether practical learned representations can approach that information-theoretic frontier—remains successor science rather than a condition for submitting the present theory paper.

## Selected references

- D. Blackwell, *Equivalent Comparisons of Experiments*, Annals of Mathematical Statistics 24, 265–272 (1953).
- V. Vovk, A. Gammerman and G. Shafer, *Algorithmic Learning in a Random World*, Springer (2005).
- Y. Jin and Z. Ren, *Confidence on the Focal: Conformal Prediction with Selection-Conditional Coverage*, arXiv:2403.03868 (2024).
- Y. Sale and A. Ramdas, *Online Selective Conformal Prediction: Errors and Solutions*, arXiv:2503.16809 (2025).
- Z. Zhou, X. Zhang, C. Tao and Y. Yang, *Conformal Prediction Assessment: A Framework for Conditional Coverage Evaluation and Selection*, arXiv:2603.27189 (2026).

## Publication decision record

**Canonical submission source:** this file, `MANUSCRIPT_V3.md`.  
**Supersedes for submission:** `MANUSCRIPT_V2.md`, which remains historical evidence and must not be used as the submission manuscript.  
**Primary target posture:** Transactions on Machine Learning Research (TMLR), theory/methodology paper.  
**Fallback posture:** Machine Learning, theory/methodology article.  
**Scientific terminal:** `BOUNDED_THEORY_READY__EXTERNAL_MULTI_DOMAIN_DISCRIMINATOR_OPTIONAL_SUCCESSOR`.  
**Submission authority:** not granted by this manuscript. Current source binding, independent reviewer pass, target-format build/PDF, archive/licence, and human filing metadata remain package tasks.
