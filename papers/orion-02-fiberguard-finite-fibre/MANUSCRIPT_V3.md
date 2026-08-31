# When a Representation Can Certify: Sharp Fibre-Diameter Limits and Minimal Refinement

## Abstract

Compressed representations are often reused both to choose actions and to certify the value of those actions, although the two tasks need not require the same information. We characterize this gap exactly for deterministic certificates on finite representation fibres. If a fibre has target diameter $D$, every fibre-constant point certificate has worst-case error at least $D/2$, and the midpoint of the extreme target values attains the bound. A certificate with tolerance $\varepsilon$ therefore exists if and only if $D\leq 2\varepsilon$. When this condition fails, a greedy interval cover of the sorted targets gives the minimum unconstrained refinement. With a restricted separator family, certification is possible exactly when no indistinguishable pair differs by more than $2\varepsilon$; without refinement, the maximum coverage is the mass of fibres that already satisfy this condition. Preserved application studies failed at decision value, useful coverage, or held-out validity, while an analytic joint-profile repair corrected a specification defect without establishing transfer value. They motivate the formal question but do not measure empirical fibre diameters. The contribution is therefore an exact finite representation-level certification and refinement calculus, not a broad empirical-transfer result.

**Keywords:** representation sufficiency; deterministic certification; fibre diameter; selective prediction; abstention; algorithm selection

## 1. Introduction

Learned and rule-based systems routinely compress complex instances before selecting an action. The same compressed state is then often used to issue a bound, confidence statement, or safety certificate. A representation may contain enough information to choose an action while omitting information needed to certify the value attached to that action. Marginal predictive validity does not by itself resolve this problem, because the certificate may be used only on a selected subset or may be constant over instances with different target values.

Statistical work addresses complementary parts of this difficulty. Conformal prediction provides finite-sample marginal guarantees under exchangeability, while conditional and selection-conditional methods study reliability for local or selected cases [5,8–12]. Selective classification studies the trade-off between coverage and risk when a system may abstain [6,7]. These methods govern sampling, calibration, and selection. A logically prior question remains: does the representation distinguish every pair of instances that must receive different certified values?

We answer that question in a finite deterministic setting. Let a representation partition the instance space into fibres, and let a scalar target be attached to each instance. The target diameter of a fibre is the largest target difference hidden by the representation. This single quantity gives both the exact minimax radius of a fibre-constant certificate and the precise tolerance at which certification becomes possible.

The same characterization yields a constructive repair calculus. For arbitrary refinement, the fewest certifiable parts are obtained by a greedy cover of sorted target values. When only a declared family of separators is available, the joint separator signature is sufficient exactly when it distinguishes every target-separated pair. If refinement is not allowed, the maximum whole-fibre coverage is the probability mass of fibres whose diameters already satisfy the tolerance.

The formal results are accompanied by adverse evidence rather than a successful application claim. Frozen algorithm-selection and classification studies exhibited three distinct failures: certificates that were too loose to act, certificates that acted but violated their risk criterion, and a selection score that did not identify the difficult cases. A later analytic repair corrected the joint learned/fallback policy language but did not turn those null results into unseen-instance value. We retain these outcomes because they delimit what the theorem explains and what remains unmeasured.

The paper establishes an exact finite-fibre calculus for deterministic scalar certification. It does not establish statistical estimation of fibre diameter, learned separator quality, randomized-certificate guarantees, production benefit, computational hardness, or cross-domain transfer.

## 2. Formal setting

Let $X$ be a finite instance set, and let

$$
\phi:X\rightarrow Z
$$

be a representation. For every attained state $z\in\phi(X)$, define the non-empty fibre

$$
F_z=\{x\in X : \phi(x)=z\}.
$$

Let $V:X\rightarrow\mathbb{R}$ be the scalar target to be certified. The target diameter hidden by state $z$ is

$$
D_\phi(z)=\max_{x, x'\in F_z}|V(x)-V(x')|.
$$

A deterministic point certificate based only on the representation is a function $c:Z\rightarrow\mathbb{R}$. If the certificate is issued at state $z$, it returns the same value $c(z)$ for every member of $F_z$. At tolerance $\varepsilon\geq 0$, it is valid on $F_z$ when

$$
|c(z)-V(x)|\leq\varepsilon\qquad\text{for every }x\in F_z.
$$

An interval certificate has centre $c(z)$ and radius $r(z)$. A refinement $\phi'$ of $\phi$ may split an original fibre but may not merge points from different original fibres. Thus $\phi'(x)=\phi'(x')$ implies $\phi(x)=\phi(x')$.

For a family $\mathcal{S}$ of available predicates, write $x\sim_{\mathcal{S}}x'$ when every predicate in $\mathcal{S}$ takes the same value on $x$ and $x'$. An $\mathcal{S}$-measurable refinement retains the original state $\phi(x)$ and, within each original fibre, may use only the joint $\mathcal{S}$-signature. It therefore neither merges original fibres nor splits an equivalence class of $\sim_{\mathcal{S}}$ within one fibre.

The results below make no sampling, exchangeability, smoothness, computational, or model-class assumption. They concern the information retained by a fixed finite representation when the target values are treated as given.

## 3. Sharp certificate limits

### 3.1 Point certificates

**Theorem 1 (sharp point-certificate floor).** For every attained fibre $F_z$ and every deterministic point certificate $c(z)$,

$$
\max_{x\in F_z}|c(z)-V(x)|\geq \frac{D_\phi(z)}{2}.
$$

Equality is attained by the midpoint certificate

$$
c^*(z)=\frac{\min_{x\in F_z}V(x)+\max_{x\in F_z}V(x)}{2}.
$$

**Proof.** Choose $x_-, x_+\in F_z$ with $V(x_+)-V(x_-)=D_\phi(z)$. The triangle inequality gives

$$
D_\phi(z)\leq |V(x_-)-c(z)|+|c(z)-V(x_+)|.
$$

At least one term is at least $D_\phi(z)/2$. The midpoint $c^*(z)$ is at distance at most half the range from every target value in the fibre, so it attains the lower bound. $\square$

The floor is informational. Additional computation cannot improve it while the certificate observes only $z$.

### 3.2 Interval certificates

**Corollary 1 (interval floor).** An interval centred at $c(z)$ and having radius $r<D_\phi(z)/2$ cannot contain $V(x)$ for every $x\in F_z$.

**Proof.** An interval covering the minimum and maximum target values must have width at least $D_\phi(z)$ and therefore radius at least $D_\phi(z)/2$. $\square$

If a conditional distribution places probability one half on each endpoint of a diameter-attaining pair, every narrower fibre-constant interval has conditional miscoverage at least one half. This is a worst-case witness, not a distributional claim about an observed corpus.

## 4. Exact refinement to certifiability

### 4.1 The certifiability threshold

**Theorem 2 (certifiability equivalence).** A deterministic point certificate with error at most $\varepsilon$ on every member of $F_z$ exists if and only if

$$
D_\phi(z)\leq 2\varepsilon.
$$

**Proof.** Necessity follows from Theorem 1. If the condition holds, the midpoint certificate has maximum error $D_\phi(z)/2\leq\varepsilon$, proving sufficiency. $\square$

At a declared tolerance, an original fibre is therefore either certifiable as it stands or must be refined or rejected.

### 4.2 Minimum unconstrained refinement

Fix one fibre and sort its target values, with multiplicity, as $v_1\leq\cdots\leq v_n$. A refined part is certifiable at tolerance $\varepsilon$ exactly when its target diameter is at most $2\varepsilon$.

**Theorem 3 (exact minimum refinement).** The minimum number of certifiable parts is returned by the following greedy sweep. Start a part at the smallest uncovered value $v_i$, include every remaining value no larger than $v_i+2\varepsilon$, and repeat on the uncovered suffix.

**Proof.** Consider the smallest value that remains uncovered. Any feasible part containing it can contain only values at most $2\varepsilon$ above it. The greedy part contains every remaining value that any feasible part anchored at that minimum could contain. Replacing the corresponding part of an optimal partition by the greedy part leaves a suffix no larger than the suffix left by the optimum, and cannot increase the number of parts needed. Induction on the number of uncovered values proves optimality. $\square$

Let $k^*(z,\varepsilon)$ denote this count. Then $k^*(z,\varepsilon)-1$ is the minimum number of additional states required within the fibre when arbitrary partitions are allowed. The greedy interval-cover primitive is classical; the result here identifies it as the exact refinement cost for the certificate problem.

### 4.3 Restricted separator families

An arbitrary partition may use distinctions that a real system cannot compute. The available separator family therefore changes the realizable frontier.

**Theorem 4 (separator realizability).** An $\mathcal{S}$-measurable refinement supporting an $\varepsilon$-valid deterministic certificate exists if and only if

$$
x\sim_{\mathcal{S}}x'\quad\Longrightarrow\quad |V(x)-V(x')|\leq 2\varepsilon
$$

for every pair $x, x'$ in the original fibre.

**Proof.** If an indistinguishable pair differs by more than $2\varepsilon$, every $\mathcal{S}$-measurable refinement places it in one refined fibre, which is uncertifiable by Theorem 2. Conversely, if every indistinguishable pair satisfies the bound, each joint-signature class within the original fibre has target diameter at most $2\varepsilon$. The representation given by the pair of the original state and the joint signature, together with midpoint certificates on its fibres, is therefore valid. $\square$

This theorem separates information-theoretic and implementable refinement. The unconstrained count $k^*$ may be unattainable under a weak separator vocabulary, and downstream calibration cannot repair a separator family that merges a target-separated pair.

## 5. The refine-or-abstain frontier

Suppose the original fibres have masses $P(\phi(X)=z)$ under a declared target population. A certificate that observes only $z$ must accept or reject the whole original fibre.

**Theorem 5 (whole-fibre coverage identity).** Without refinement, the maximum coverage of an $\varepsilon$-valid deterministic certificate is

$$
\sum_{z\in\phi(X)}P(\phi(X)=z)\,\mathbf{1}\{D_\phi(z)\leq 2\varepsilon\}.
$$

**Proof.** Theorem 2 makes every small-diameter fibre certifiable and every large-diameter fibre uncertifiable. Accepting all and only the certifiable fibres attains the stated mass, and no other whole-fibre acceptance rule can add mass without accepting an invalid fibre. $\square$

Refining an uncertifiable fibre can purchase its probability mass at a representation cost. Under arbitrary refinement, that cost is $k^*(z,\varepsilon)-1$ additional states. Under a separator restriction, it is the cost of a measurable partition whose signature classes satisfy Theorem 4. This is an exact accounting identity, not a claim that target diameters, separator costs, or population masses are easy to learn.

## 6. Finite model checks

The proofs carry the general authority. Separate exhaustive programs were used only to test transcription and implementation on finite instances.

The first program enumerated 784 configurations. It found no point certificate beating $D/2$, no interval of radius below $D/2$ covering both endpoints, and no balanced two-point witness with miscoverage below one half. A negative control gave the certificate the hidden member identity and confirmed that the checker then detected a violation of the fibre-constant floor.

The refinement program examined 4,704 main configurations, together with nested separator enumerations. It compared the greedy count with an exhaustive enumeration of set partitions on a separate code path. All registered sufficiency, necessity, separator, and coverage predicates agreed, and planted violations fired. These enumerations do not convert finite checks into proof or external replication.

## 7. Preserved adverse and repair boundaries

The application records below use different corpora and loss scales. They are not pooled, and none directly measures $D_\phi(z)$. Their role is to show the practical failure modes that a representation-level certificate must distinguish.

| Study object | Preserved observation | Supported interpretation |
|---|---|---|
| Paired learned/fallback routing on three public algorithm-selection scenarios | None of 99 frozen development candidates was feasible, and the selected certificate changed no route decision. | Outcome-exposed corroborating null; an earlier positive interpretation remains retracted. |
| Exact joint learned/fallback profile repair | A diagonal pairing shortcut changed one exact randomized minimax value from 35 to 70; identical marginal profile sets admitted joint values 0 and 50 under different compatibility relations. | The legal joint profile and acquisition timing are required certificate inputs; this analytic repair establishes no unseen-instance value. |
| Initial certified-neighbourhood envelope | The certificate was invalid on both registered splits. On the official split, full-space and reduced-space coverage were 0.210 and 0.331, with violation rates 0.169 and 0.182; family-disjoint coverage was zero. | Limited coverage did not carry valid action authority. |
| Corrected split-conformal neighbourhood envelope | The marginal violation criterion was met on both splits only with zero held-out coverage and no improvement over the single-best fallback. | Validity without coverage or value is an operational null, not a recovered application claim. |
| Held-out density-backoff study | Coverage was 32/44, below the frozen 0.95 threshold. A lexical control reached 39/44, but the paired difference was not established (exact McNemar $p=0.092$; bootstrap interval included zero). | The registered geometry was not validated, and the control comparison is descriptive rather than decisive. |
| Held-out arm-conditional study | Coverage reached 44/44, but 20/44 strict violations exceeded the frozen 0.10 maximum. The control had 14 aggregate violations, but per-instance policy-arm flags were not retained, so the paired difference remains undetermined. | The primary certificate is invalid on its own criterion; no comparative superiority follows from the untestable aggregate difference. |

The paired-route null is preserved exactly because its later analytic repair addresses a specification defect rather than the failed application endpoint. Correct joint profiles prevent an invalid compression of learned and fallback actions, but they do not supply conditional validity, family-shift validity, or production value.

The neighbourhood sequence shows the opposite sides of the validity-utility trade-off. The initial envelope acted on some cases but violated its registered criterion. The corrected conformal envelope satisfied a marginal criterion only by abstaining everywhere. A later full-coverage construction acted on every held-out case but failed conditional validity. These are distinct scientific outcomes, not stages of a successful certificate.

The arm-conditional study also retained a selector diagnostic. The available score had Pearson correlation $r=-0.144$ with realised excess under 20,000 permutations ($p=0.353$, $n=44$). This result does not prove zero association; it shows that a useful association was not established on the frozen sample. The adverse application records therefore motivate prospective measurement of fibre diameter and selector quality, but they do not verify the finite-fibre theorem on those corpora.

## 8. Relation to prior work

The decision value of information is classical. Blackwell comparison orders experiments by their usefulness across decision problems [1], and the algorithm-selection formulation makes the instance-to-algorithm decision problem explicit [2]. The present result does not claim a new general information order. It fixes one representation and one scalar certificate target, then computes the exact ambiguity that this representation leaves.

Selective classification formalizes coverage-risk trade-offs when a predictor may reject cases [6,7]. Theorem 5 is narrower: it gives the exact deterministic whole-fibre coverage when acceptance cannot distinguish members of one representation state. It does not learn a rejection function or provide a population risk bound.

Conformal prediction supplies distribution-free marginal coverage under exchangeability [5,8]. Exact conditional validity cannot generally be obtained distribution-free without restrictions [9]. Recent work develops selection-conditional procedures [10,11] and local or structured conditional-coverage assessment [12,13]. Those papers address calibration, selection, and conditional reliability. The finite-fibre floor instead asks whether a fixed observable state identifies the target at the requested tolerance before any calibration method is chosen.

The greedy cover of sorted values and the midpoint of an interval are standard ingredients. The residual contribution is their joint use in a fail-closed certificate object: exact radius, tolerance equivalence, minimal refinement, separator realizability, and whole-fibre abstention all follow from the same target diameter. The adverse records make clear that this deterministic calculus is not a statistical or empirical transfer guarantee.

## 9. Discussion

Representations are sufficient only relative to a question. A state can support action selection while remaining inadequate for a value certificate. The target diameter makes this mismatch explicit. If $D_\phi(z)>2\varepsilon$, no deterministic certificate observing only $z$ can attain error $\varepsilon$ on the whole fibre. If $D_\phi(z)\leq2\varepsilon$, the midpoint certificate attains it immediately.

This equivalence distinguishes three repair routes. A calibration problem calls for a statistical repair; a weak selector calls for better information about which cases should be accepted; and a large fibre diameter requires refinement of the representation itself. Treating these failures as interchangeable encourages post-outcome retuning of a certificate whose observable state may never have contained the required information.

The adverse studies illustrate all three boundaries. One certificate was too conservative to change any route, another obtained nominal marginal validity only through universal abstention, and another attained full coverage while violating its own held-out criterion. The correct response is not to reinterpret these outcomes as near successes. They delimit successor questions about learning diameters, separators, or selectors under disjoint evaluation.

The bounded conclusion is that deterministic certifiability is governed exactly by within-representation target variation, and that the minimum abstract repair can be characterized. Whether practical learned representations approach this frontier remains an empirical question outside the present claim.

## 10. Limitations

1. The theorems concern finite fibres and a scalar target. Infinite spaces and vector-valued certificates require additional topological, measurable, or geometric assumptions.
2. The certificates are deterministic. Randomized procedures require a declared loss and coverage convention.
3. The constructions use the target values within a fibre. Estimating those values without leakage is a separate statistical problem.
4. Separator realizability evaluates a declared feature family. It neither learns the family nor prices feature acquisition.
5. The coverage identity assumes known target-population fibre masses and whole-fibre acceptance.
6. The preserved studies do not measure target diameters on their empirical fibres. They cannot confirm the theorem's mechanism on those corpora.
7. No broad transfer, production advantage, computational-hardness result, or comparative superiority claim is made.

## 11. Data and code availability

During double-blind review, an anonymous supplementary archive provides the standard-library theorem checkers, frozen expected outputs, anonymized scientific projections of the exact result objects underlying the adverse summaries, and the paired-comparison and selector-diagnostic scripts. The archive includes a machine-readable manifest with SHA-256 digests and distinguishes checks on enclosed results from full upstream-data reruns. The third-party benchmark data originate from the public Algorithm Selection Benchmark Library (ASlib) and Penn Machine Learning Benchmarks (PMLB) resources [3,4] and remain subject to their original licences. Full provenance-bearing result objects and a permanent archival identifier will accompany the non-anonymous record.

## 12. Generative AI disclosure

A generative language model assisted with manuscript organization, language revision, adversarial review, and package preparation. The author remains responsible for the scientific claims, citations, code, and final submission.

## References

1. D. Blackwell. Equivalent comparisons of experiments. *The Annals of Mathematical Statistics* **24**, 265–272 (1953). doi:10.1214/aoms/1177729032
2. J. R. Rice. The algorithm selection problem. *Advances in Computers* **15**, 65–118 (1976). doi:10.1016/S0065-2458(08)60520-3
3. B. Bischl et al. ASlib: A benchmark library for algorithm selection. *Artificial Intelligence* **237**, 41–58 (2016). doi:10.1016/j.artint.2016.04.003
4. R. S. Olson, W. La Cava, P. Orzechowski, R. J. Urbanowicz and J. H. Moore. PMLB: a large benchmark suite for machine learning evaluation and comparison. *BioData Mining* **10**, 36 (2017). doi:10.1186/s13040-017-0154-4
5. V. Vovk, A. Gammerman and G. Shafer. *Algorithmic Learning in a Random World*. Springer (2005).
6. R. El-Yaniv and Y. Wiener. On the foundations of noise-free selective classification. *Journal of Machine Learning Research* **11**, 1605–1641 (2010).
7. Y. Geifman and R. El-Yaniv. Selective classification for deep neural networks. *Advances in Neural Information Processing Systems* **30** (2017). arXiv:1705.08500.
8. A. N. Angelopoulos and S. Bates. Conformal prediction: a gentle introduction. *Foundations and Trends in Machine Learning* **16**, 494–591 (2023). doi:10.1561/2200000101
9. R. F. Barber, E. J. Candes, A. Ramdas and R. J. Tibshirani. The limits of distribution-free conditional predictive inference. *Information and Inference* **10**, 455–482 (2021). doi:10.1093/imaiai/iaaa017
10. Y. Jin and Z. Ren. Confidence on the focal: conformal prediction with selection-conditional coverage. *Journal of the Royal Statistical Society Series B* **87**, 1239–1259 (2025). doi:10.1093/jrsssb/qkaf016
11. Y. Sale and A. Ramdas. Online selective conformal prediction: errors and solutions. arXiv:2503.16809 (2025).
12. Z. Zhou, X. Zhang, C. Tao and Y. Yang. Conformal prediction assessment: a framework for conditional coverage evaluation and selection. arXiv:2603.27189 (2026).
13. Y. Min, L. Peng and C. Zou. A unified theory of conditional coverage in conformal prediction with applications. arXiv:2605.11602 (2026).
