# FiberGuard / ORION-02 R20 — exact closed-world certificates and the limits of inductive deployment

Date: 2026-08-27

Status: current evidence-integrated scientific story. This document narrows the paper to claims supported by exact theorems, prospectively frozen experiments, and preserved adverse outcomes. It does not grant external review, novelty, venue, or submission authority.

## Working title

**Finite-Fibre Decision Certificates Do Not Extrapolate: Exact Closed-World Guarantees, Prospective Deployment Failures, and Joint Route Repair**

## Abstract

A representation is operationally insufficient when states that it identifies require materially different actions. For a finite state space and action portfolio, FiberGuard computes exact representation-fibre regret, certified safe action sets, randomized minimax value, compressed worst-fibre witnesses, minimum-cost static repair, and exact adaptive acquisition policies under state-dependent feature cost. These are closed-world theorems: their authority is over the declared finite fibre.

We test whether that authority survives algorithm-selection deployment. On the complete SAT12-ALL corpus, exhaustive evaluation of all 513 dependency-closed feature-step representations identifies `{Pre,lobjois}` with robust total excess 1712, compared with 12000 for no features and 16906.55 for all features. The same exact-equality object fails prospectively under official and family-held-out splits because continuous signatures rarely recur. A one-sided calibrated learned-action certificate can also worsen deployed decision cost when rejected states are sent to a harmful fallback. A prospectively frozen paired marginal route then yields no feasible development candidate among 99 choices and changes zero routes on MAXSAT12, MAXSAT19, and QBF. Finally, a separately frozen neighborhood/Lipschitz escape is invalid: held-out violations exceed ten percent under official folds and family-held-out coverage is zero at the registered tolerance.

The negative sequence is explained by an exact repair theorem. A deployed route is determined not by separate learned and fallback marginals, but by the legal joint profile language, the route observation, compatibility, acquisition timing, and one common statewise oracle. Randomized route compression is exact precisely when it preserves the lower image of the convex hull of legal joint profiles. Thus exact finite-fibre certificates remain valid and useful, but no inductive certificate follows without an independently justified structural law. The paper contributes a theorem-to-deployment authority calculus and a prospectively preserved failure atlas, not a universal claim that feature acquisition or abstention improves solver selection.

## 1. Exact closed-world theory

Let `F` be one complete finite representation fibre, `A` a finite action set, and

`R(a,x)=C(a,x)-C*(x)`

with the same statewise oracle `C*(x)=min_b C(b,x)` for every action, feature charge, defer leaf, and route leaf.

The supported theorem package is:

1. **Deterministic fibre regret**

   `rho_det(F)=min_a max_{x in F} R(a,x)`.

2. **Safe action sets**

   `Safe_epsilon(F)={a:max_x R(a,x)<=epsilon}`, nonempty exactly when `rho_det(F)<=epsilon`.

3. **Randomized minimax regret**

   `rho_rand(F)=min_{p in Delta(A)} max_x sum_a p_a R(a,x)`, with an exact finite LP and an optimal support of at most `|F|` deterministic policies.

4. **Refinement monotonicity**

   Splitting a complete fibre cannot increase deterministic or randomized action regret before acquisition cost.

5. **Compressed witnesses**

   Deterministic worst-fibre value is witnessed by at most `|A|` states. Randomized value has a small primal mixture and a dual adversarial-state certificate.

6. **Static repair**

   Minimum-cost deterministic representation repair is exact weighted set cover on minimal action-conflict hyperedges. Pairwise conflicts are insufficient for three or more actions.

7. **State-dependent acquisition**

   Exact adaptive refinement requires statewise loss profiles, or an equivalent sunk-cost offset state. A scalar Bellman state is universally exact exactly when acquisition charge is constant on each reached observation cell.

8. **Adaptive and randomized separations**

   Static versus adaptive and deterministic versus randomized expected-loss gaps are unbounded. These generic mechanisms are donor-owned; the FiberGuard residual is their exact complete-fibre/common-oracle certificate realization.

9. **Joint route theorem**

   Learned and fallback marginal profile sets do not determine deployed route value. The exact object is the legal joint learned/fallback profile set together with route observation, compatibility, and acquisition timing. Randomized compression preserves every monotone convex route objective exactly iff it preserves

   `conv(P_joint)+R_+^F`.

All statements above are finite analytic theorems. Bounded programs corroborate implementations but do not create external proof authority.

## 2. Complete-corpus operational result

The pinned ASlib SAT12-ALL audit evaluates every dependency-closed feature-step subset under one runtime/PAR10 oracle baseline. It contains 1614 instances, 31 solvers, 115 raw features, ten feature steps, and 513 dependency-closed representations.

- no features: robust total excess `12000`;
- all features: action-only ambiguity nearly vanishes, but robust total excess is `16906.55` because one acquisition path is extremely expensive;
- exact optimum static representation `{Pre,lobjois}`: robust total excess `1712`, mean total excess `23.0143`, 1595 fibres, maximum fibre size 20;
- its worst fibre is certified by three instances.

This is an exact transductive result on the complete pinned corpus. It is not evidence of unseen-signature generalization.

## 3. Prospectively preserved deployment failures

### 3.1 Exact equality does not transfer inductively

Under the official held-out protocol, the training-selected exact-equality policy covers only about 3.22% of held-out instances, has mean total excess about 5380.23, and a catastrophic wrong-action rate about 44.55%. A same-information 16-nearest-neighbor comparator obtains mean excess about 1465.09 and catastrophic rate about 11.96%.

Under zero-family-overlap shift, exact-equality coverage is about 5.08%, mean excess about 5341.59, and catastrophic rate about 44.24%; the 16-nearest-neighbor comparator obtains about 1982.36 and 16.23% respectively.

The failure is not a contradiction of the finite theorem. The training fibre is incomplete for an unseen state, so the theorem's subject is absent.

### 3.2 Calibration does not imply decision value

A later prospective certificate configuration controls marginal false-certificate frequency on SAT16, SAT18, and SAT20, yet selective routing worsens cost on SAT16 and SAT18 because the registered fallback is worse than the learned action on rejected states. Therefore learned-arm calibration alone cannot certify the deployed route.

### 3.3 Paired marginal routing produces no action

The R18 protocol freezes MAXSAT12 development, MAXSAT19 no-retuning validation, QBF-2016 untouched testing, official nested folds, eleven models, three alpha values, and three paired route modes. Zero of 99 development candidates is feasible. The least-bad row changes zero routes on every panel:

| Panel | Routed mean | Full learned mean | No-feature fallback mean | Route coverage | Certificate failure |
|---|---:|---:|---:|---:|---:|
| MAXSAT12-PMS | 3292.7431 | 3292.7431 | 7652.9374 | 0.0000 | 0.0491 |
| MAXSAT19-UCMS | 10392.3040 | 10392.3040 | 12392.3775 | 0.0000 | 0.0297 |
| QBF-2016 | 1964.8780 | 1964.8780 | 4860.6993 | 0.0000 | 0.0364 |

Terminal: `FIBERGUARD_R18_NO_PAIRED_ROUTE_VALUE`.

This is outcome-exposed recovery corroboration under a protocol frozen before the unsupported former positive prose. The positive prose remains retracted.

### 3.4 A naive structural neighborhood law is invalid

The prospectively frozen SAT11-HAND-ALGO experiment asks whether a development-fitted representation-space distance yields an unseen-state regret certificate.

Under official folds:

- full-neighborhood coverage is about 0.2095 and held-out violation is about 0.1688;
- PCA10-neighborhood coverage is about 0.3311 and held-out violation is about 0.1818.

Under the family-disjoint split, coverage is zero for both registered representations at epsilon 5000, while held-out violation remains about 0.1515 and 0.1682.

Terminal: `CERTIFICATE_INVALID`.

This refutes the proposed Lipschitz/neighborhood bridge on its frozen subject. It does not refute statistical nearest-neighbor prediction; rather, it prevents a statistical neighborhood from being mislabeled as an exact unseen-state certificate.

## 4. Explanation by exact joint-route structure

The deployment failures share one formal cause: the deployed policy is not determined by a certificate for one marginal arm.

For each state, a legal deterministic route profile must encode:

- the learned action and its total excess;
- the fallback action and its total excess;
- whether feature cost is already sunk;
- the observation available when routing occurs;
- the compatibility relation between learned and fallback profiles;
- the route decision induced by that observation.

Separate learned/fallback envelopes can permit diagonal pairings that no legal policy realizes. The original R19 diagonal shortcut is therefore false: one hostile profile system has true randomized value 35 and shortcut value 70. The replacement theorem enumerates legal joint profiles and gives exact deterministic, randomized, and dual certificates.

This explains why neither one-sided calibration nor paired marginal calibration is sufficient. A useful route certificate must be a certificate of the deployed joint policy.

## 4.1 Cross-language implementation control

A standard-library-only Rust checker now parses the durable R18 and R19 JSON subjects directly and recomputes the no-free-extension, fallback-alignment, witness-compression, lower-image, joint-marginal, route-coarsening, and acquisition-timing controls. It shares repository ownership but not language, parser, or ORION Python implementation. Its authority is same-owner structural corroboration, not external independence.

## 5. What the paper claims

The strongest defensible claim is:

> Exact finite representation fibres support small, model-independent decision certificates under one common statewise oracle. Those certificates are closed-world objects. In prospectively frozen solver-selection studies, exact equality, one-sided rejection, paired marginal routing, and a naive neighborhood transfer law all fail to produce a valid inductive certificate. The failures are predicted by an exact joint-route theorem that identifies the missing policy language, observation, compatibility, and acquisition-timing structure.

The paper does **not** claim:

- generic novelty for minimax regret, set cover, active feature acquisition, abstention, conformal prediction, nearest neighbors, nested CV, or Pareto pruning;
- universal failure of learned algorithm selection;
- production prevalence outside the pinned corpora;
- deterministic safety from marginal conformal coverage;
- that a statistical selector is an exact unseen-state certificate;
- external review, novelty adjudication, journal readiness, or acceptance from internal receipts.

## 6. Publication architecture

The manuscript should be organized around one contrast rather than a sequence of extensions:

1. exact finite-fibre decision theory;
2. complete-corpus positive operational example;
3. prospective inductive and routing refutations;
4. exact joint-route repair theorem;
5. authority calculus distinguishing complete-fibre proof, marginal statistical validity, conditional routed-case validity, and empirical selector performance;
6. reproducible failure atlas and reviewer-verifiable certificates.

The negative outcomes are load-bearing results, not limitations to hide. The resulting paper is suitable for specialist review as a theory-plus-falsification paper once the current evidence objects, independent replay status, source/rights manifest, and submission package are frozen.
