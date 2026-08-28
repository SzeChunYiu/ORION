# ORION-02 claim ledger V3 — fibre certifiability

**Canonical manuscript:** `MANUSCRIPT_V3.md`  
**Date:** 2026-08-28  
**scientific_authority_delta:** `NONE`  
**Submission authority:** false

This ledger defines the live submission claim surface after the independent V2 proof review. It does not rewrite the historical V2 ledger or any R18/R22/R23/R24 result.

| ID | Claim | Status | Boundary |
|---|---|---|---|
| V3-C1 | A deterministic point certificate constant on fibre `F_z` has worst-case error at least `D(z)/2`, and the midpoint attains equality. | **PROVEN** | Finite fibre, scalar target, deterministic fibre-constant certificate. |
| V3-C2 | An interval of radius `< D(z)/2` cannot cover every target value on the fibre. | **PROVEN** | Same finite-fibre setting. |
| V3-C3 | On a balanced diameter-attaining two-point conditional law, any such narrow interval has conditional miscoverage at least `1/2`. | **PROVEN** | Worst-case conditional witness; not asserted for arbitrary empirical fibre distributions. |
| V3-C4 | An `eps`-valid fibre-constant point certificate exists **iff** `D(z) <= 2 eps`; the midpoint is constructive when the condition holds. | **PROVEN** | Finite fibre, deterministic certificate. |
| V3-C5 | Minimum unconstrained refinement into parts of diameter `<=2 eps` equals the left-to-right greedy interval-cover count on sorted target values. | **PROVEN** | Refinement may use arbitrary partition of a finite fibre. |
| V3-C6 | Under separator family `S`, an `S`-measurable `eps`-valid refinement exists iff every `S`-indistinguishable pair has target gap `<=2 eps`. | **PROVEN** | `S` is declared prospectively; theorem does not learn or price `S`. |
| V3-C7 | Without refinement, maximum whole-fibre certifiable coverage equals the mass of fibres satisfying `D(z)<=2 eps`. | **PROVEN** | Population fibre masses are assumed given; no sampling estimator is supplied. |
| V3-C8 | The exhaustive floor checker found zero theorem violations on 784 registered finite configurations and its planted controls fired. | **MEASURED / CHECKER VALIDATION** | Finite checker evidence; not theorem authority. |
| V3-C9 | The refinement checker found zero R1–R5 violations on 4,704 main configurations plus separator enumeration; greedy count matched exhaustive partition minima; planted controls fired. | **MEASURED / CHECKER VALIDATION** | Finite checker evidence; not theorem authority. |
| V3-C10 | R24 reached `44/44` coverage and `20/44` strict held-out violations; the matched lexical control also reached full coverage. | **PRESERVED ADVERSE RESULT** | PMLB R24 frozen corpus/assignment; `C_R24_ARM_CONDITIONAL_CERTIFICATE_INVALID` unchanged. |
| V3-C11 | On those 44 held-out R24 decisions, `11/44` realised excesses exceed `tau`; the registered `alpha=.10`, bound `<=tau` full-coverage goal is arithmetically infeasible. | **DIAGNOSTIC ON COMMITTED DATA** | One corpus and frozen assignment; no new run. |
| V3-C12 | The available model bound has Pearson correlation `-0.1442` with realised excess, permutation `p=.3528`, Spearman `rho=-.1921`; no usable selector signal was established. | **DIAGNOSTIC ON COMMITTED DATA** | `n=44`; means no evidence of signal, not proof of zero association. |
| V3-C13 | Oracle 25% abstention exhibits a valid/useful interior point; a noise-degraded oracle suggests a selector-correlation target around `.85`. | **DIAGNOSTIC / UPPER-BOUND DESIGN STUDY** | Oracle uses realised excess and is not deployable; `.85` is not a universal constant. |
| V3-C14 | The current R24 corpus empirically establishes `D(z)>2 eps` on its accepted fibres. | **NOT ESTABLISHED / FORBIDDEN** | R24 did not directly measure fibre target diameters. |
| V3-C15 | The theory establishes broad cross-domain empirical transfer, production benefit, physical quantum advantage, or computational hardness. | **NOT CLAIMED / FORBIDDEN** | Requires separate evidence. |
| V3-C16 | Earlier `A_t/B_t` all-`t` formulas, their minimax corollaries, the conditional four-index compiler theorem, and single-block sharpness are live submission claims. | **NO — SUPERSEDED FOR SUBMISSION** | Independent V2 review found undeclared cross-gadget, dominance, single-block, padding, and integrality assumptions. Historical records remain intact. |

## Donor boundary

Generic sufficient-statistic theory, comparison of experiments, robust decision theory, interval covering, conformal prediction, and selection-conditional coverage are donor-owned. V3 claims no generic novelty for those fields. The residual is the exact joint finite-fibre certification/refinement calculus and its disciplined binding to the preserved certificate failure.

## Stop rule

The bounded theory paper does **not** wait for the multi-domain selector experiment. Any future empirical promotion must use a fresh protocol with disjoint train/calibration/test custody and may fail without reopening V3. No post-outcome change to `tau`, `alpha`, representation, or selector threshold contributes authority to the preserved R24 study.
