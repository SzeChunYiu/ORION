# When a Representation Can Certify: Sharp Fibre-Diameter Limits and Minimal Refinement

## Abstract

A representation can be sufficient for choosing an action while remaining insufficient for certifying the value attached to that action. We give an exact finite-fibre characterization of this gap. Let \(\phi:X\to Z\) be a representation, let \(F_z=\{x:\phi(x)=z\}\) be a representation fibre, and let \(V:X\to\mathbb R\) be the quantity to be certified. Write \(D(z)\) for the range of \(V\) on \(F_z\). Any deterministic point certificate that depends only on \(z\) has worst-case error at least \(D(z)/2\), and no interval of radius below \(D(z)/2\) can cover every fibre member. Both bounds are sharp.

The same diameter yields a constructive converse. A fibre admits an \(\varepsilon\)-valid constant certificate if and only if \(D(z)\le2\varepsilon\); the midpoint of its extreme values is then valid. For finite fibres, the minimum number of refined parts required for \(\varepsilon\)-valid certification is exactly the count produced by a greedy interval sweep over sorted target values. Under a restricted separator family, certification is possible if and only if the available separators distinguish every pair whose target values differ by more than \(2\varepsilon\). Without refinement, maximum certifiable coverage is exactly the population mass of fibres already satisfying the diameter condition.

We preserve an adverse prospective empirical study that motivated the theory. A frozen certificate construction reached 44/44 held-out coverage but incurred 20/44 strict violations, and the available selection score was not detectably associated with realised excess. These observations do not identify the real fibre diameters; they show why marginal coverage and a weak selector cannot substitute for conditional certifiability. The contribution is a sharp information-level certification criterion and refine-or-abstain calculus, not an empirical superiority claim.

## 1. Introduction

Modern decision systems routinely compress a complex instance before acting. The resulting representation may preserve the information needed to rank alternatives, classify an object, or choose a control action. Certification is a stronger task. To issue a reliable numerical guarantee, the representation must also distinguish instances whose target values differ by more than the declared tolerance.

This distinction is easy to miss because decision quality and certificate quality are often evaluated on the same held-out examples. A representation can support accurate choices in aggregate while merging cases that require materially different certificates. No downstream optimizer can recover a distinction that the representation has erased.

We ask a deterministic question underneath statistical calibration: **when can a fixed representation support a uniformly valid certificate, and how much refinement is minimally necessary when it cannot?** The answer is the target diameter of each representation fibre.

The paper contributes an exact fibre-level lower bound, a necessary-and-sufficient certifiability criterion, an optimal unconstrained refinement algorithm, a realizability theorem for restricted separator vocabularies, and a coverage identity that makes the trade between abstention and representation refinement explicit.

## 2. Setting

Let \(X\) be a finite instance space and \(\phi:X\to Z\) a representation. For an observed representation state \(z\in Z\), define

\[
F_z=\{x\in X:\phi(x)=z\}.
\]

Let \(V:X\to\mathbb R\) be the scalar quantity to be certified, and define the fibre diameter

\[
D_\phi(z)=\max_{x,x'\in F_z}|V(x)-V(x')|.
\]

A deterministic point certificate based only on the representation is a function \(c:Z\to\mathbb R\). An interval certificate may likewise choose a centre \(c(z)\) and radius \(r(z)\). At tolerance \(\varepsilon\ge0\), a point certificate is \(\varepsilon\)-valid on \(F_z\) if

\[
|c(z)-V(x)|\le\varepsilon\quad\text{for every }x\in F_z.
\]

A representation \(\phi'\) refines \(\phi\) when every \(\phi'\)-fibre lies inside one \(\phi\)-fibre. The theory is finite and deterministic: it assumes no distributional form, exchangeability, smoothness, learned model class, or computational hardness.

## 3. The sharp fibre-diameter floor

**Theorem 1 (point-certificate floor).** For every fibre and every point certificate constant on that fibre,

\[
\max_{x\in F_z}|c(z)-V(x)|\ge D_\phi(z)/2.
\]

Choose two fibre members whose targets achieve the diameter. By the triangle inequality, their separation is at most the sum of their distances to the common certificate; at least one distance is therefore at least half the diameter. The midpoint of the minimum and maximum target values attains exactly that radius, so the bound is sharp.

**Theorem 2 (interval floor).** No interval of radius less than \(D_\phi(z)/2\) can cover every target value in the fibre. The result follows because such an interval has width smaller than the diameter of the target set.

These statements are information bounds, not complexity bounds. Unlimited downstream computation cannot beat them while the observable representation remains \(z\).

## 4. Exact certifiability criterion

The lower bound immediately becomes a constructive decision rule.

**Theorem 3 (certifiability equivalence).** An \(\varepsilon\)-valid fibre-constant point certificate exists if and only if

\[
D_\phi(z)\le2\varepsilon.
\]

Necessity follows from Theorem 1. For sufficiency, issue the midpoint certificate

\[
c^*(z)=\frac{\min_{x\in F_z}V(x)+\max_{x\in F_z}V(x)}{2}.
\]

Every fibre member is within half the diameter of that midpoint.

This theorem turns “the representation seems too coarse” into an exact test. At a declared tolerance, a fibre is either already certifiable or must be refined or abstained upon.

## 5. Minimum unconstrained refinement

Consider one fibre and sort its target values:

\[
v_1\le v_2\le\cdots\le v_n.
\]

A refined part is certifiable at tolerance \(\varepsilon\) exactly when its target diameter is at most \(2\varepsilon\). The minimum-refinement problem is therefore equivalent to covering the sorted values with the fewest intervals of length \(2\varepsilon\).

**Theorem 4 (greedy optimal refinement).** Start a part at the smallest uncovered target value and include every subsequent value no more than \(2\varepsilon\) above that part's minimum. Repeating this procedure produces the minimum possible number of certifiable parts.

The exchange argument is standard but decisive: no feasible first part containing the smallest remaining point can extend farther than the greedy part. Replacing the first part of any optimum by the greedy choice cannot increase the number of remaining parts. Induction completes the proof.

Let \(k^*(z,\varepsilon)\) denote this minimum. Then \(k^*-1\) is the exact number of additional representation states required under unconstrained refinement.

## 6. What an available separator vocabulary can realize

An abstract partition may not be implementable from the information available to the system. Let \(\mathcal S\) be a family of admissible predicates or features. Call two instances \(\mathcal S\)-indistinguishable when every separator in \(\mathcal S\) assigns them the same value.

**Theorem 5 (separator realizability).** An \(\mathcal S\)-measurable \(\varepsilon\)-valid refinement exists if and only if every \(\mathcal S\)-indistinguishable pair satisfies

\[
|V(x)-V(x')|\le2\varepsilon.
\]

If an indistinguishable pair exceeds the tolerance diameter, every representation computable from \(\mathcal S\) must place the pair in the same atom, which is uncertifiable. Conversely, if all indistinguishable pairs satisfy the bound, each complete separator-signature atom has target diameter at most \(2\varepsilon\), and the midpoint certificate is valid on every atom.

This theorem separates information-theoretic refinement from realizable refinement. A richer optimizer cannot compensate for a separator vocabulary that merges a target-separated pair.

## 7. The refine-or-abstain frontier

Suppose representation fibres have population mass \(P(\phi=z)\). Without adding information, a fibre is certifiable exactly when its diameter is no larger than \(2\varepsilon\).

**Theorem 6 (coverage identity).** The maximum coverage achievable by a rule that either certifies an entire original fibre or abstains on it is

\[
\sum_z P(\phi=z)\,\mathbf 1\{D_\phi(z)\le2\varepsilon\}.
\]

Refinement purchases the mass of otherwise uncertifiable fibres at a representation cost. Under unconstrained refinement, the cost is \(k^*(z,\varepsilon)-1\); under a restricted separator family, it is the corresponding measurable refinement cost. The resulting design question is therefore fibre-specific: how large is the target diameter, what target-separated pairs can the available information distinguish, and whether the additional certifiable mass justifies the refinement.

## 8. Verification and hostile controls

The mathematical authority of the general statements comes from the proofs. Exhaustive finite checkers provide an independent defect-detection layer. The registered verification enumerates finite fibre configurations, checks that no fibre-constant point or interval certificate beats the diameter floor, compares greedy refinement against exhaustive set partitions, and verifies the separator and coverage identities. Planted violations are included so that a silent or vacuous checker cannot be mistaken for support.

This division of authority matters. Finite enumeration is useful for finding transcription and implementation defects; it does not turn a bounded absence of counterexamples into an all-size theorem.

## 9. Preserved adverse empirical boundary

The theoretical work was motivated by failed certification attempts, and the failures remain part of the evidence rather than being rewritten after the theorem was developed.

A first held-out revival improved coverage but missed its registered coverage threshold and was outperformed by an outcome-independent lexical negative control. A later arm-conditional construction reached full held-out coverage on 44 decisions but produced 20 strict violations, far above the registered maximum. A matched no-geometry control also reached full coverage with fewer violations. The available model score had weak, non-significant association with realised excess and did not provide a useful abstention rule.

An oracle analysis showed that a safe interior point existed if the worst realised-excess cases were removed, but realised excess is unavailable at decision time and the oracle is not an implementable method. These observations support only a bounded conclusion: full marginal coverage did not imply valid conditional certification, and the available selector did not identify the cases on which abstention should occur.

We do **not** infer the real fibre diameters from these data. The empirical study did not directly observe \(D_\phi(z)\). The theory instead states what a future system must measure or refine before claiming conditional certifiability.

## 10. Relation to statistical uncertainty and representation theory

Conformal prediction and selective or conditional coverage methods address sampling validity under explicit probabilistic assumptions. Sufficient-statistic, Blackwell-comparison, and robust-decision traditions likewise formalize that information is valuable relative to a decision problem. Interval covering and greedy covering on the real line are classical algorithmic objects.

The present contribution is narrower than those donor areas. It isolates a representation-level obstruction that exists *before* calibration: if the representation maps two target-separated instances to the same observable state, no certificate that depends only on that state can distinguish them. Statistical methods can then be layered on top of a representation that is sufficiently informative for the certificate being requested.

## 11. Limitations

The theory is finite and deterministic. Estimating fibre diameters from samples, learning a useful separator family, and controlling statistical error when the population is only partially observed are separate problems. The target is scalar; vector or structured certificates require an appropriate geometry. The greedy refinement theorem assumes arbitrary partitioning by target order and therefore represents an information-theoretic lower bound when the available features impose additional constraints.

The adverse empirical study is deliberately not promoted into evidence of broad transfer. It motivates the information boundary but does not establish the fibre structure of a general real-world population.

## 12. Conclusion

Certification is a stronger information requirement than decision. A fixed representation can support a useful action while merging instances that require incompatible guarantees. The fibre diameter measures that incompatibility exactly: half the diameter is the sharp worst-case certificate radius, \(D\le2\varepsilon\) is the exact certifiability condition, greedy interval covering gives minimum unconstrained refinement, and separator indistinguishability characterizes what a restricted feature vocabulary can realize. The resulting refine-or-abstain law identifies when additional calibration is meaningful and when new information is mathematically unavoidable.
