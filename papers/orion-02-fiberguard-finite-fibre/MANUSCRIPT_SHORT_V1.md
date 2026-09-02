<!-- ORION-02 derived filing surface provenance (2026-09-02), not manuscript text.
     Decision (a) of SzeChunYiu/ORION-paper#78: compress to a short, honestly-scoped
     theory note; file to TMLR as a short paper. This file is MANUSCRIPT_SHORT_V1.md,
     a NEW derived surface from the canonical MANUSCRIPT_V3.md + CLAIM_LEDGER_V3.md,
     which remain untouched and canonical. Compression: contribution stated as the
     joint fail-closed calculus; the seven preserved adverse/null records of the
     canonical section 7 reduced to one table with evidence pointers.
     skills-applied: nature-writing, nature-polishing, nature-publication-closure -->

# When a Representation Can Certify: A Fail-Closed Calculus for Finite Representation Fibres

## Abstract

Compressed representations are often reused both to choose actions and to certify the value of those actions, although the two tasks need not require the same information. This note states a joint fail-closed calculus for deterministic certificates on finite representation fibres, governed by one quantity: the target diameter $D$ hidden by a representation state. Half that diameter is the exact worst-case error floor of any fibre-constant point certificate, and the midpoint of the extreme target values attains it. A certificate with tolerance $\varepsilon$ exists if and only if $D\leq 2\varepsilon$. When the condition fails, a greedy interval cover of the sorted targets gives the minimum unconstrained refinement; with a restricted separator family, certification is possible exactly when no indistinguishable pair differs by more than $2\varepsilon$; and without refinement, the maximum coverage is the mass of fibres that already satisfy the condition. The calculus is fail-closed: a fibre that cannot be certified at the declared tolerance is refined or rejected, never re-calibrated around absent information. Seven preserved adverse and null application records, none favourable and none pooled, form the measured boundary of what the calculus has been shown to do in practice. The contribution is the calculus together with that boundary, not an empirical-transfer or comparative-superiority result.

**Keywords:** representation sufficiency; deterministic certification; fibre diameter; selective prediction; abstention

## 1. Introduction

Learned and rule-based systems routinely compress complex instances before selecting an action, and the same compressed state is then used to issue a bound, confidence statement, or safety certificate. A representation may contain enough information to choose an action while omitting information needed to certify the value attached to that action. Marginal predictive validity does not by itself resolve this problem, because the certificate may be used only on a selected subset or may be constant over instances with different target values.

Statistical work addresses complementary parts of the difficulty: conformal prediction provides finite-sample marginal guarantees under exchangeability, conditional and selection-conditional methods study reliability for local or selected cases, and selective classification studies coverage-risk trade-offs when a system may abstain [5–12]. These methods govern sampling, calibration, and selection. A logically prior question remains: does the representation distinguish every pair of instances that must receive different certified values?

We answer that question in a finite deterministic setting, and we state the answer as one calculus. Let a representation partition the instance space into fibres and let a scalar target be attached to each instance. The target diameter of a fibre is the largest target difference hidden by the representation. From this single quantity we derive five linked results: the sharp minimax radius of a fibre-constant certificate; the exact tolerance at which certification becomes possible; the minimum unconstrained refinement, given by a greedy cover of sorted target values; the exact characterization of refinement restricted to a declared separator family; and the maximum whole-fibre coverage available without refinement. Each result converts the same diameter into a distinct repair-or-refuse decision, which is why we present them jointly.

The formal results are accompanied by adverse evidence rather than a successful application claim. Seven frozen algorithm-selection and classification studies failed at decision value, useful coverage, or held-out validity. We retain these outcomes, compressed to one table, because they delimit what the theorem explains and what remains unmeasured; they are the paper's measured identity, not decorative caveats. This note establishes an exact finite-fibre calculus for deterministic scalar certification. It does not establish statistical estimation of fibre diameter, learned separator quality, randomized-certificate guarantees, production benefit, computational hardness, cross-domain transfer, or superiority of any tested selection rule.

## 2. Formal setting

Let $X$ be a finite instance set, let $\phi:X\rightarrow Z$ be a representation, and for every attained state $z\in\phi(X)$ define the non-empty fibre $F_z=\{x\in X : \phi(x)=z\}$. Let $V:X\rightarrow\mathbb{R}$ be the scalar target to be certified. The target diameter hidden by state $z$ is

$$
D_\phi(z)=\max_{x, x'\in F_z}|V(x)-V(x')|.
$$

A deterministic point certificate based only on the representation is a function $c:Z\rightarrow\mathbb{R}$; if issued at state $z$, it returns the same value for every member of $F_z$. At tolerance $\varepsilon\geq 0$ it is valid on $F_z$ when $|c(z)-V(x)|\leq\varepsilon$ for every $x\in F_z$. An interval certificate has centre $c(z)$ and radius $r(z)$. A refinement $\phi'$ of $\phi$ may split an original fibre but may not merge points from different original fibres. For a family $\mathcal{S}$ of available predicates, write $x\sim_{\mathcal{S}}x'$ when every predicate in $\mathcal{S}$ takes the same value on $x$ and $x'$. An $\mathcal{S}$-measurable refinement retains the original state and, within each original fibre, may use only the joint $\mathcal{S}$-signature.

The results make no sampling, exchangeability, smoothness, computational, or model-class assumption. They concern the information retained by a fixed finite representation when the target values are treated as given.

## 3. The joint fail-closed calculus

### 3.1 Sharp certificate floor

**Theorem 1 (sharp point-certificate floor).** For every attained fibre $F_z$ and every deterministic point certificate $c(z)$,

$$
\max_{x\in F_z}|c(z)-V(x)|\geq \frac{D_\phi(z)}{2},
$$

with equality attained by the midpoint certificate $c^*(z)=\tfrac{1}{2}\left(\min_{x\in F_z}V(x)+\max_{x\in F_z}V(x)\right)$.

**Proof.** Choose $x_-, x_+\in F_z$ with $V(x_+)-V(x_-)=D_\phi(z)$. The triangle inequality gives $D_\phi(z)\leq |V(x_-)-c(z)|+|c(z)-V(x_+)|$, so at least one term is at least $D_\phi(z)/2$. The midpoint is at distance at most half the range from every target value in the fibre. $\square$

The floor is informational: additional computation cannot improve it while the certificate observes only $z$.

**Corollary 1 (interval floor).** An interval centred at $c(z)$ with radius $r<D_\phi(z)/2$ cannot contain $V(x)$ for every $x\in F_z$. If a conditional distribution places probability one half on each endpoint of a diameter-attaining pair, every narrower fibre-constant interval has conditional miscoverage at least one half; this is a worst-case witness, not a distributional claim about an observed corpus.

### 3.2 The certifiability threshold

**Theorem 2 (certifiability equivalence).** A deterministic point certificate with error at most $\varepsilon$ on every member of $F_z$ exists if and only if $D_\phi(z)\leq 2\varepsilon$.

**Proof.** Necessity follows from Theorem 1; sufficiency holds because the midpoint certificate has maximum error $D_\phi(z)/2\leq\varepsilon$. $\square$

At a declared tolerance, an original fibre is therefore either certifiable as it stands or must be refined or rejected.

### 3.3 Minimum unconstrained refinement

Sort the target values of one fibre, with multiplicity, as $v_1\leq\cdots\leq v_n$. A refined part is certifiable at tolerance $\varepsilon$ exactly when its target diameter is at most $2\varepsilon$.

**Theorem 3 (exact minimum refinement).** The minimum number of certifiable parts is returned by the greedy sweep that starts a part at the smallest uncovered value $v_i$, includes every remaining value no larger than $v_i+2\varepsilon$, and repeats on the uncovered suffix. The count $k^*(z,\varepsilon)-1$ is the minimum number of additional states required within the fibre under arbitrary partitions.

**Proof.** Any feasible part containing the smallest uncovered value can contain only values at most $2\varepsilon$ above it, so the greedy part contains every remaining value that any feasible part anchored at that minimum could contain; replacing the corresponding part of an optimal partition by the greedy part cannot increase the number of parts needed. Induction on the number of uncovered values proves optimality. $\square$

The greedy interval-cover primitive is classical; the result identifies it as the exact refinement cost for the certificate problem.

### 3.4 Restricted separator families

An arbitrary partition may use distinctions that a real system cannot compute.

**Theorem 4 (separator realizability).** An $\mathcal{S}$-measurable refinement supporting an $\varepsilon$-valid deterministic certificate exists if and only if

$$
x\sim_{\mathcal{S}}x'\quad\Longrightarrow\quad |V(x)-V(x')|\leq 2\varepsilon
$$

for every pair $x, x'$ in the original fibre.

**Proof.** If an indistinguishable pair differs by more than $2\varepsilon$, every $\mathcal{S}$-measurable refinement places it in one refined fibre, which is uncertifiable by Theorem 2. Conversely, if every indistinguishable pair satisfies the bound, each joint-signature class within the original fibre has target diameter at most $2\varepsilon$, and the representation given by the original state and the joint signature, with midpoint certificates, is valid. $\square$

This separates information-theoretic from implementable refinement: the unconstrained count $k^*$ may be unattainable under a weak separator vocabulary, and downstream calibration cannot repair a separator family that merges a target-separated pair.

### 3.5 Whole-fibre coverage without refinement

Suppose the original fibres have masses $P(\phi(X)=z)$ under a declared target population. A certificate that observes only $z$ must accept or reject the whole original fibre.

**Theorem 5 (whole-fibre coverage identity).** Without refinement, the maximum coverage of an $\varepsilon$-valid deterministic certificate is

$$
\sum_{z\in\phi(X)}P(\phi(X)=z)\,\mathbf{1}\{D_\phi(z)\leq 2\varepsilon\}.
$$

**Proof.** Theorem 2 makes every small-diameter fibre certifiable and every large-diameter fibre uncertifiable; accepting all and only the certifiable fibres attains the stated mass, and no other whole-fibre rule can add mass without accepting an invalid fibre. $\square$

Refining an uncertifiable fibre purchases its probability mass at a representation cost: $k^*(z,\varepsilon)-1$ additional states under arbitrary refinement, or the cost of a measurable partition satisfying Theorem 4 under a separator restriction. This is an exact accounting identity, not a claim that diameters, separator costs, or masses are easy to learn.

The five statements form one calculus. Given a declared tolerance, the diameter decides whether a fibre is certifiable (Theorem 2), what any certificate must pay in worst-case error (Theorem 1), what refinement costs in states (Theorem 3), whether a restricted system can pay it at all (Theorem 4), and what abstention costs in coverage (Theorem 5). The decision is closed in the failing direction: an uncertifiable fibre is refined or refused.

## 4. Finite model checks

The proofs carry the general authority. Separate exhaustive programs were used only to test transcription and implementation on finite instances: a floor checker over 784 registered configurations found no point certificate beating $D/2$, no interval of radius below $D/2$ covering both endpoints, and no balanced two-point witness with miscoverage below one half, with a negative control confirming the checker fires; a refinement checker over 4,704 main configurations matched greedy counts to exhaustive partition minima on a separate code path, with all separator and coverage predicates agreeing and planted violations firing. These enumerations do not convert finite checks into proof or external replication.

## 5. Measured application boundary

The application records below use different corpora and loss scales. They are not pooled, and none directly measures $D_\phi(z)$. Their role is to show the practical failure modes that a representation-level certificate must distinguish. Each row cites the committed evidence record for detail.

| Record | Preserved result | Disposition | Evidence |
|---|---|---|---|
| V3-E1 | Paired learned/fallback routing on three public algorithm-selection scenarios: none of 99 frozen development candidates was feasible, and the selected certificate changed no route decision. | Corroborating null; an earlier positive interpretation remains retracted. | `extensions/r18/R18_RECOVERY_DISPOSITION_V2.md` |
| V3-E2 | Exact joint learned/fallback profile repair: a diagonal pairing shortcut changed one exact randomized minimax value from 35 to 70; identical marginal profile sets admitted joint values 0 and 50. | Analytic specification repair; no unseen-instance value. | `extensions/r19/FIBERGUARD_JOINT_ROUTE_R19_REPLACEMENT.md` |
| V3-E3 | Initial certified-neighbourhood envelope: invalid on both registered splits; on the official split, full-space and reduced-space coverage were 0.210 and 0.331 with held-out violation rates 0.169 and 0.182, and family-disjoint coverage was zero. | Adverse; limited coverage did not carry valid action authority. | `experiments/results/CERTIFIED_NEIGHBORHOOD_RESULT_V1.md` |
| V3-E4 | Corrected split-conformal neighbourhood envelope: the marginal violation criterion was met on both splits only with zero held-out coverage and no improvement over the single-best fallback. | Operational null; validity without coverage or value. | `experiments/results/CERTIFIED_NEIGHBORHOOD_CONFORMAL_RECOVERY_RESULT_V2.md` |
| V3-E5 | Held-out density-backoff study: coverage 32/44, below the frozen 0.95 threshold; a lexical control reached 39/44; the paired difference was not established (exact McNemar $p=0.0923$; bootstrap interval included zero). | Adverse; the control comparison is descriptive rather than decisive. | `rounds/r23-density-backoff-revival/FIBERGUARD_PMLB_PROPOSAL_ORDERING_R23_RESULT.md` |
| V3-E6 | Held-out arm-conditional study: coverage reached 44/44, but the geometry primary incurred 20/44 strict violations against the frozen 0.10 maximum. | Primary adverse; invalid by its own frozen criterion. | `rounds/r24-arm-conditional-fibres-revival/FIBERGUARD_PMLB_ARM_CONDITIONAL_R24_RESULT.md` |
| V3-E7 | R24 paired comparator, matched lexical control: 14/44 strict violations; the paired flags give (both, geometry only, control only, neither) = (14, 6, 0, 24). | Both arms fail the 0.10 validity gate; no superiority in either direction. | `rounds/r24-arm-conditional-fibres-revival/R24_STRICT_VIOLATION_COMPARATOR_V1.json` |

One entry requires exact wording. The V3-E7 paired comparison has $n=44$ with six discordant pairs, all in one direction, giving exact two-sided McNemar $p=0.03125$. We report this value only to characterize the one-sidedness of the discordance on this frozen endpoint. Both arms fail the frozen 0.10 validity gate, both certificates are invalid, and the value supports no usable-certificate or superiority claim for either selection rule.

The arm-conditional study also retained a selector diagnostic: the available score had Pearson correlation $r=-0.144$ with realised excess under 20,000 permutations ($p=0.353$, $n=44$; `SELECTOR_LIMITED_CERTIFICATION_V1.md`). This does not prove zero association; it shows that a useful association was not established on the frozen sample. The adverse records therefore motivate prospective measurement of fibre diameter and selector quality, but they do not verify the finite-fibre theorem on those corpora.

## 6. Relation to prior work

The decision value of information is classical: Blackwell comparison orders experiments by their usefulness across decision problems [1], and the algorithm-selection formulation makes the instance-to-algorithm decision explicit [2]. The present result does not claim a new general information order; it fixes one representation and one scalar certificate target, then computes the exact ambiguity that this representation leaves. Selective classification formalizes coverage-risk trade-offs when a predictor may reject cases [6,7]; Theorem 5 is narrower, giving the exact deterministic whole-fibre coverage when acceptance cannot distinguish members of one representation state, without learning a rejection function.

Conformal prediction supplies distribution-free marginal coverage under exchangeability [5,8]; exact conditional validity cannot generally be obtained distribution-free without restrictions [9]; and recent work develops selection-conditional procedures and conditional-coverage assessment [10–13]. Those papers address calibration, selection, and conditional reliability. The finite-fibre floor instead asks whether a fixed observable state identifies the target at the requested tolerance before any calibration method is chosen. The greedy cover of sorted values and the midpoint of an interval are standard ingredients; the residual contribution is their joint use in a fail-closed certificate object — exact radius, tolerance equivalence, minimum refinement, separator realizability, and whole-fibre abstention all following from the same target diameter — together with an explicitly adverse application boundary.

## 7. Discussion and limitations

Representations are sufficient only relative to a question. A state can support action selection while remaining inadequate for a value certificate, and the target diameter makes this mismatch explicit. The equivalence of Theorem 2 distinguishes three repair routes: a calibration problem calls for a statistical repair, a weak selector calls for better information about which cases to accept, and a large fibre diameter requires refinement of the representation itself. Treating these failures as interchangeable encourages post-outcome retuning of a certificate whose observable state may never have contained the required information. The adverse studies illustrate all three boundaries: one certificate was too conservative to change any route, another obtained nominal marginal validity only through universal abstention, and another attained full coverage while violating its own held-out criterion. The correct response is not to reinterpret these outcomes as near successes; they delimit successor questions about learning diameters, separators, or selectors under disjoint evaluation.

The boundaries are as follows. The theorems concern finite fibres and a scalar target; infinite spaces and vector-valued certificates require additional topological, measurable, or geometric assumptions. The certificates are deterministic, so randomized procedures require a separately declared loss and coverage convention. The constructions use the target values within a fibre; estimating those values without leakage is a distinct statistical problem. Separator realizability evaluates a declared feature family but neither learns that family nor prices feature acquisition, and the coverage identity assumes known fibre masses and whole-fibre acceptance. The preserved studies do not measure target diameters on their empirical fibres and cannot confirm the theorem's mechanism on those corpora. We make no broad transfer, production-advantage, computational-hardness, or comparative-superiority claim.

## 8. Data and code availability

During double-blind review, an anonymous supplementary archive provides the standard-library theorem checkers, frozen expected outputs, anonymized scientific projections of the exact result objects underlying the boundary table, and the paired-comparison and selector-diagnostic scripts; the archive mirrors the evidence paths cited in the table and includes a machine-readable manifest with SHA-256 digests, distinguishing checks on enclosed results from full upstream-data reruns. The third-party benchmark data originate from the public Algorithm Selection Benchmark Library (ASlib) and Penn Machine Learning Benchmarks (PMLB) resources [3,4] and remain subject to their original licences. Full provenance-bearing result objects and a permanent archival identifier will accompany the non-anonymous record.

## 9. Generative AI disclosure

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
