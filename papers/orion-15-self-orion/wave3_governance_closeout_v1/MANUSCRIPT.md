# Fail-Closed Promotion for Adaptive Method Revision

**Canonical Wave-3 governance manuscript, ORION-15**  
**Scientific terminal:** `SELF_ORION_PROTECTED_TRANSFER_NOT_ESTABLISHED__GOVERNANCE_THEORY_RETAINED`  
**Subject repository state:** `235e62c1a275be260798ab1596282fff7594a924`

## Abstract

Adaptive method revision is often described as a search problem: diagnose a failure, generate a change, evaluate it, and retain the best candidate. That description omits the hardest boundary. A reviser may not possess the information or authority needed to decide which change is licensed, and repeated evaluation with optional stopping can manufacture false confidence unless error spending, retention, harm, and custody are explicit.

We formulate method revision as a decision problem over latent development situations, minimal admissible revision fronts, observable evidence interfaces, controlled interventions, and typed promotion authority. Exact revision is possible through an interface if and only if every interface fibre requires the same decision. When fibres mix decisions, the irreducible risk is the conditional Bayes risk; no stronger proposer can recover a distinction erased by its interface. For finite ambiguity sets, exact non-adaptive discriminator design is weighted set cover, deterministic adaptive design is characterized by decision-pure leaves, and stochastic adaptive design requires mutually singular decision-class transcript laws. A finite state-indexed frontier enumerates legal revision trees under destructive actions and state-dependent costs. For adaptive promotion, predictable alpha spending with conditionally valid tests controls the probability of any false promotion even under data-dependent stopping. Promotion is additionally gated by fresh-task benefit, retention, harm, resource and authority constraints; missing or conflicting receipts block rather than default to success.

The repository contains bounded diagnostic evidence—21/24 on one constructed attribution archive and, in a later bounded harvest, 22/24 control versus 23/24 treatment, with an earlier perfect treatment ceiling not reproduced. These audits motivate the framework but do not establish protected longitudinal transfer. The preregistered six-arm, 768-cluster campaign remains unexecuted and zero of six comparator arms is confirmatory-ready. We therefore withdraw empirical general self-improvement and retain a formal governance contribution: conditions under which adaptive revision can be identified, evaluated and promoted without laundering replay gains, optional stopping, retention loss or candidate self-certification into scientific authority.

## 1. From self-editing to authorized revision

A method reviser operates in a partially observed scientific process. The latent situation may include the actual cause of a failure, the reliability of an evaluator, the effect of a candidate on earlier capabilities, and whether protected evidence licenses promotion. Its visible interface may include logs, issue history, replay cases, model-generated diagnoses, local tests, and summaries of prior experiments.

Three separations are fundamental:

1. **proposal is not diagnosis**: generating a plausible edit does not identify the failure mechanism;
2. **evaluation is not authority**: a score computed by a candidate-writable evaluator cannot authorize its own promotion;
3. **replay is not transfer**: improvement on already observed cases does not establish fresh-task benefit or retention.

The paper's unit is therefore not “an agent that improves itself.” It is an authorized revision decision with explicit information, loss, experimental actions, custody and error budget.

## 2. Minimal revision fronts

Let \(\Theta\) be a set of latent development situations and let \((\mathcal R,\prec)\) be a well-founded strict partial order of candidate revisions. The relation \(r'\prec r\) means that \(r'\) changes strictly less of the method than \(r\). Representation repair and evaluator repair can be incomparable, so a total ladder is neither required nor desirable.

For \(\theta\in\Theta\), let \(\mathcal A(\theta)\subseteq\mathcal R\) contain revisions admissible after causal responsibility, task recovery, preservation, fresh transfer, harm and authority constraints are applied. When nonempty, define the minimal front
\[
\mathcal M(\theta)=\min_{\prec}\mathcal A(\theta).
\]
Let \(Q(\theta)\) indicate a material residual. The required decision is
\[
G(\theta)=
\begin{cases}
\mathsf{NO\_REVISION}, & \neg Q(\theta),\\
\mathsf{UNRESOLVED}, & Q(\theta)\ \text{and}\ \mathcal A(\theta)=\varnothing,\\
\mathcal M(\theta), & Q(\theta)\ \text{and}\ \mathcal A(\theta)\ne\varnothing.
\end{cases}
\]
Returning an antichain is deliberate: if several incomparable minimal revisions remain licensed, silently selecting one fabricates preference or evidence.

A reviser observes an interface \(\phi:\Theta\to\mathcal Z\), not \(\theta\) itself.

### Theorem 1 — revision factorization

There exists an exact rule \(g:\phi(\Theta)\to\operatorname{im}(G)\) satisfying \(G=g\circ\phi\) if and only if
\[
\phi(\theta)=\phi(\theta')\Longrightarrow G(\theta)=G(\theta')
\]
for all \(\theta,\theta'\in\Theta\).

The proof is the quotient argument: an exact factor is necessarily constant on fibres; fibre constancy makes the induced definition independent of representative. Measurable or computable factorization requires the corresponding quotient regularity and is not implied by the set-theoretic statement alone.

The theorem shifts attention from latent-cause recovery to **decision sufficiency**. An interface may omit many latent details and still be sufficient if it separates every pair requiring different revision fronts. Conversely, arbitrarily rich logs are insufficient if one cross-decision pair remains observationally equivalent.

## 3. Irreducible risk on mixed fibres

Assume standard-Borel \(\Theta,\mathcal Z\), measurable \(\phi,G\), a finite nonempty decision alphabet \(\mathcal Y\), finite nonempty action set \(\mathcal D\), and loss \(L:\mathcal D\times\mathcal Y\to[0,\infty)\). Let \(H\sim\mu\), \(Z=\phi(H)\), \(Y=G(H)\), and \(p_y(z)=\Pr\{Y=y\mid Z=z\}\).

### Theorem 2 — mixed-fibre Bayes bound

Every measurable deterministic or randomized rule using only \(Z\) has risk at least
\[
R^*(\phi,L)=\mathbb E_Z\left[\min_{a\in\mathcal D}\sum_y L(a,y)p_y(Z)\right],
\]
and a measurable fibrewise Bayes action attains the bound. Under zero-one loss with \(\mathcal D=\mathcal Y\),
\[
R^*(\phi)=1-\mathbb E_Z\left[\max_y p_y(Z)\right].
\]

Conditioned on \(Z=z\), a randomized rule is a convex combination of action risks, so it cannot improve on the smallest constituent. The expression exposes asymmetric costs: broad revision may reduce under-revision while increasing harmful transfer; abstention may be optimal without making the fibre identifiable.

### Corollary 1 — candidate self-certification is incomplete or unsound

If two situations have the same complete candidate-visible transcript but protected evidence authorizes promotion in one and forbids it in the other, no internally computed promotion rule is both sound and complete. Always abstaining may remain sound but is incomplete.

External custody is therefore an information-and-authority requirement, not a claim that an external evaluator is infallible.

## 4. Discriminator design

Fix a visible value \(z\) and a finite ambiguous fibre \(F_z\). Let \(\mathcal T\) be a finite family of tests or interventions with deterministic protected outcomes \(o_t(\theta)\). Define the cross-decision pairs
\[
U_z=\{\{\theta,\theta'\}\subseteq F_z:G(\theta)\ne G(\theta')\}
\]
and the pairs distinguished by test \(t\),
\[
D_t=\{\{\theta,\theta'\}\in U_z:o_t(\theta)\ne o_t(\theta')\}.
\]

### Theorem 3 — discriminator cover

A non-adaptive panel \(S\subseteq\mathcal T\) permits exact revision selection on \(F_z\) if and only if
\[
\bigcup_{t\in S}D_t=U_z.
\]
With nonnegative additive costs, the minimum-cost exact finite panel is the induced weighted set-cover optimum. If a cross-decision pair belongs to no \(D_t\), the declared test family cannot resolve the decision.

### Proposition 1 — deterministic adaptive purity

A terminating deterministic adaptive policy permits exact revision selection if and only if every reachable terminal leaf contains situations sharing one common \(G\)-value.

### Theorem 4 — stochastic transcript separation

For a fixed terminating adaptive policy \(\pi\), let \(P_\theta^\pi\) be the law of its complete transcript. Exact measurable decoding exists if and only if the decision classes admit measurable transcript regions that have probability one under their own class and zero under the others. On a finite fibre, this is equivalent to pairwise mutual singularity of the decision-class mixture laws.

Identical one-test marginals do not establish impossibility because dependence across a transcript can carry information. A stronger policy-uniform sufficient condition is equality of every history-conditional outcome kernel for every legal intervention; then every candidate-independent policy induces identical complete transcript laws.

## 5. Legal laboratory state and robust revision trees

Real interventions change what can be done next. A destructive test, exhausted budget, changed evaluator or consumed protected case must be represented as a state transition rather than a prose warning.

For finite latent world set \(W\), observable laboratory state \(s\), state-indexed terminal actions \(\mathcal D(s)\), legal interventions \(\mathcal E(s)\), costs \(c(s,e)\), and known outcome/next-state kernels \(K_{s,e}\), define the finite-horizon risk-vector frontier recursively from terminal losses and legal branches.

### Theorem 5 — finite state-indexed frontier

The recursion exactly enumerates the world-risk vectors of all legal deterministic discriminator trees up to the horizon. For any fixed ex-ante credal set, deterministic minimax value is the minimum support function over the frontier; licensed world-independent randomization uses its convex hull.

This is a finite controlled-state decision result and a specialization of donor POMDP/robust-decision machinery. It does not claim general robust-POMDP novelty. Fixed-prior and posterior-rectangular ambiguity are different games: they coincide for a fixed policy on all bounded path losses exactly under the appropriate path-law pasting stability. A local worst-case recursion must not be presented as solving an arbitrary fixed-prior problem.

## 6. Anytime-safe promotion

Suppose candidate \(j\) is evaluated after filtration \(\mathcal F_{j-1}\). Let \(\alpha_j\ge0\) be predictable, with the pathwise budget
\[
\sum_{j\ge1}\alpha_j\le\alpha.
\]
For every null candidate, assume its protected-test \(p\)-value is conditionally super-uniform:
\[
\Pr\{p_j\le u\mid\mathcal F_{j-1}\}\le u,\qquad u\in[0,1].
\]

### Theorem 6 — adaptive false-promotion bound

If candidate \(j\) can be promoted only when \(p_j\le\alpha_j\), then under arbitrary adaptive candidate generation and stopping,
\[
\Pr\{\text{at least one null candidate is promoted}\}\le\alpha.
\]

For each null candidate, conditional error is at most \(\alpha_j\). Summing conditional probabilities and applying the tower property gives the bound. The theorem does not make an invalid test anytime-valid; the conditional validity assumption must come from a prospectively registered confidence sequence, e-process, masked procedure, or other licensed construction.

A valid receipt records candidate bytes, subject state, split identity, evaluator identity, test family, \(\alpha_j\), cumulative spend and decision. Replaying, retrying or resuming cannot decrease cumulative spend. Duplicate receipt identities are idempotent; conflicting receipts block. A missing, malformed, stale or unbound receipt produces `UNRESOLVED`, not promotion.

## 7. Non-compensatory acceptance

Statistical significance is only one gate. For a candidate \(r\), define prospectively frozen endpoints:

- fresh-task value difference \(\Delta_{\mathrm{fresh}}(r)\);
- retention difference \(\Delta_{\mathrm{retain}}(r)\);
- harmful-transfer rate/severity \(H(r)\);
- resource cost \(C(r)\);
- authority and custody violations \(A(r)\).

A promotion policy may require, for example,
\[
\operatorname{LCB}(\Delta_{\mathrm{fresh}})>\delta,\qquad
\operatorname{LCB}(\Delta_{\mathrm{retain}})>-\varepsilon,\qquad
\operatorname{UCB}(H)<h,
\]
together with \(C(r)\) inside its registered envelope, \(A(r)=0\), complete receipts, and an unspent error budget.

These gates are non-compensatory. A large aggregate fresh gain cannot cancel a protected subgroup harm, retention collapse, holdout access, evaluator mutation, or missing receipt. Replay-only improvement cannot satisfy the fresh gate. Candidate-generated evidence may propose promotion but cannot supply the protected authority needed by Corollary 1.

## 8. Negative history and longitudinal state

A longitudinal reviser inherits the actual retained state after every round:

- accepted and rejected candidates;
- adverse and null outcomes;
- used protected cases and error-budget spend;
- costs, failures, retries and `CANNOT_CHECK` episodes;
- authority violations and evaluator changes.

Deleting a negative result changes the information set and can repeat a failed intervention or launder optional stopping. History may be compressed only by a prospectively specified, content-bound map whose effect is evaluated against full immutable history. Positive-only history is not an ablation of negative-history retention; it changes the intervention.

## 9. Bounded repository evidence

The repository contains several useful but limited audits.

### 9.1 Diagnostic attribution archive

One fixed constructed archive contains 24 cases. A recorded model run classified 21 correctly and retained three named errors. This is descriptive debugging evidence, not a probability sample, matched campaign, transfer estimate, or population confidence statement.

### 9.2 Bounded GLM-5.3 harvest

A later bounded attribution harvest records control \(22/24\) and treatment \(23/24\). An earlier perfect \(24/24\) treatment ceiling was not reproduced. Its authority disposition permits only bounded descriptive direction. It does not establish generation-invariant performance, external independence, broad superiority, submission authority, or protected longitudinal transfer.

### 9.3 Public development factorial and interface work

A public Defects4J known-fix replay isolates an implementation main effect inside one source/bug/fix cluster and later repairs archival path binding. Synthetic adapter suites and outcome-blind comparator bindings test contracts and expose blockers. They are engineering evidence, not independent scientific units or protected outcomes.

### 9.4 The unexecuted wide campaign

The registered wide successor specifies 768 source-disjoint clusters across eight domains and eight revision classes, six comparator families, protected freshness, retention and harm gates. At the current terminal, zero of six comparator arms is confirmatory-ready: complete adapters, matched resource/configuration bindings, protected scorer and independent custody are missing. No protected longitudinal outcome table exists.

## 10. Scientific disposition

The evidence does not support claims that Self-ORION:

- improves protected fresh-task performance across revision rounds;
- outperforms fair self-refinement comparators;
- preserves prior capabilities under repeated promotion;
- reduces harmful transfer;
- achieves better resource-adjusted value;
- establishes autonomous or general self-improvement.

Those claims remain `CANNOT_CHECK`, not negative performance estimates. The positive contribution is the formal governance layer: informational limits, revision-front factorization, active discriminator design, legal-state control, anytime error spending, non-compensatory harm/retention gates, typed authority, and append-only negative-history custody.

The scientific terminal is therefore
`SELF_ORION_PROTECTED_TRANSFER_NOT_ESTABLISHED__GOVERNANCE_THEORY_RETAINED`.

## 11. Relation to prior work

The factorization and mixed-fibre results are decision-specific uses of statistical experiment comparison and Bayes decision theory. The discriminator results sit in active diagnosis, minimum test-set and sequential experimental-design traditions. The finite state recursion specializes controlled-state and robust-decision machinery. Anytime-valid inference and familywise error control supply the statistical tools needed for optional stopping and adaptive candidate families.

The residual contribution is the integration of these donors into a fail-closed method-revision contract with minimal revision fronts, protected promotion authority, retention/harm vetoes, immutable negative history and executable receipt boundaries. No donor theorem is relabelled as a new general statistical principle.

## 12. Limitations

1. No protected six-round campaign has been executed.
2. No fair six-arm comparator outcome table exists.
3. The bounded case archives are constructed and small.
4. The formal results require their stated finite, measurability, kernel and validity assumptions.
5. A sequential error theorem cannot repair invalid, leaked or candidate-controlled evaluation.
6. External custody reduces writable conflicts but does not make an evaluator infallible.
7. The paper does not establish broad, autonomous or generation-invariant self-improvement.
8. No journal submission is represented as having occurred.

## 13. Conclusion

Adaptive method revision is safe only when the decision is identifiable from the licensed interface and promotion remains valid under the actual adaptive process. When protected promotion varies inside a candidate-visible fibre, self-certification is impossible. When candidate tests are adaptively selected, error budget, retention, harm, resource and authority gates must be immutable and fail closed. Negative history is part of the state, not editorial debris.

The repository's empirical programme has not established protected longitudinal transfer. Rather than converting incomplete execution into a performance claim, this paper closes at the formal governance terminal and leaves the protected campaign as future empirical work.

## References

- D. Blackwell, “Equivalent Comparisons of Experiments,” *Annals of Mathematical Statistics* 24 (1953), 265–272.
- H. Chernoff, “Sequential Design of Experiments,” *Annals of Mathematical Statistics* 30 (1959), 755–770.
- R. Reiter, “A Theory of Diagnosis from First Principles,” *Artificial Intelligence* 32 (1987), 57–95.
- J. de Kleer and B. C. Williams, “Diagnosing Multiple Faults,” *Artificial Intelligence* 32 (1987), 97–130.
- A. Ramdas, J. Ruf, M. Larsson, and W. Koolen, “Admissible Anytime-Valid Sequential Inference Must Rely on Nonnegative Martingales,” arXiv:2009.03167.
- B. Duan, A. Ramdas, and L. Wasserman, “Familywise Error Rate Control by Interactive Unmasking,” ICML 2020.
- A. K. Kuchibhotla and Q. Zheng, “Near-Optimal Confidence Sequences for Bounded Random Variables,” ICML 2021.

## Data and code availability

The theorem ledger, manuscript sources, bounded evidence archives, protocol identities, comparator preflight records and deterministic checkers are contained in the public ORION repository. Protected cases and outcomes do not exist at this terminal; the package does not imply that an unavailable campaign was run.
