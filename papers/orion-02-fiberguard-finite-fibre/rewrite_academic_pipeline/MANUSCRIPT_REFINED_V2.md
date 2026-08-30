# Fibre Diameter Is the Exact Information Limit for Deterministic Certification

## Abstract

A representation may preserve enough information to choose an action while merging instances that require incompatible numerical guarantees. We characterize this certification gap exactly for finite deterministic representations. For a representation \(\phi:X\to Z\), target \(V:X\to\mathbb R\), and fibre \(F_z=\{x:\phi(x)=z\}\), let
\[
D_\phi(z)=\max_{x,x'\in F_z}|V(x)-V(x')|.
\]
Every point certificate depending only on \(z\) has worst-case error at least \(D_\phi(z)/2\), and no interval of smaller radius can cover the whole fibre. Both bounds are attained by the midpoint of the fibre extremes. Thus a fibre admits an \(\varepsilon\)-valid constant certificate if and only if \(D_\phi(z)\le2\varepsilon\).

The same object determines what must change when certification fails. For a finite fibre, greedy covering of sorted target values by intervals of length \(2\varepsilon\) gives the minimum unconstrained refinement. Under a restricted separator vocabulary, a certifiable refinement exists exactly when every separator-indistinguishable pair differs in target value by at most \(2\varepsilon\). Without refinement, maximum certifiable coverage is the mass of fibres that already satisfy the diameter condition.

A preserved prospective study shows why these distinctions matter. A frozen construction covered 44 of 44 held-out decisions but violated its strict certificate on 20 of 44, while a no-geometry control produced fewer violations and the available selection score did not yield a useful abstention rule. These data do not identify population fibre diameters. They show that marginal coverage and a weak selector cannot substitute for conditional certifiability. The contribution is an exact information-level refine-or-abstain law, not empirical superiority.

## 1. Introduction

Compression is usually judged by whether a downstream system can make a useful decision. Certification asks for more. A certificate must remain valid for every instance that the observable representation treats as the same.

Suppose two instances share representation state \(z\), but their target values differ by more than the allowed tolerance. A downstream optimizer may be arbitrarily powerful, yet any deterministic certificate that sees only \(z\) must issue the same answer for both. The failure is therefore informational before it is statistical or computational.

This paper asks three linked questions:

1. What is the smallest uniformly valid certificate radius available from a fixed representation?
2. How much refinement is minimally necessary when that radius exceeds a declared tolerance?
3. Which refinements can be realized from a restricted family of observable separators?

The answer to all three is organized by fibre diameter. The resulting theory distinguishes three remedies that are often conflated: calibrate within an already certifiable fibre, add information by refining the representation, or abstain where neither route is available.

## 2. Setting

Let \(X\) be a finite instance space, \(\phi:X\to Z\) a representation, and \(V:X\to\mathbb R\) the scalar quantity to be certified. For \(z\in Z\), define
\[
F_z=\{x\in X:\phi(x)=z\}
\]
and
\[
D_\phi(z)=\max_{x,x'\in F_z}|V(x)-V(x')|.
\]

A point certificate is a function \(c:Z\to\mathbb R\). It is \(\varepsilon\)-valid on \(F_z\) when
\[
|c(z)-V(x)|\le\varepsilon
\quad\text{for every }x\in F_z.
\]
An interval certificate chooses a centre and radius using only \(z\). A refinement \(\phi'\) is admissible when every \(\phi'\)-fibre lies inside one original \(\phi\)-fibre.

The theory is deterministic. It does not assume exchangeability, smoothness, a sampling distribution, a learned model class, or asymptotic consistency.

## 3. Sharp certification floor

**Theorem 1 (point-certificate floor).** For every fibre and every point certificate constant on that fibre,
\[
\max_{x\in F_z}|c(z)-V(x)|\ge \frac{D_\phi(z)}{2}.
\]

Choose \(x_-\) and \(x_+\) attaining the minimum and maximum target values. Their separation is at most the sum of their distances from the common certificate. At least one distance is therefore at least half the diameter.

The midpoint
\[
c^*(z)=\frac{\min_{x\in F_z}V(x)+\max_{x\in F_z}V(x)}{2}
\]
attains exactly \(D_\phi(z)/2\), so the bound is sharp.

**Corollary 2 (interval floor).** No interval of radius below \(D_\phi(z)/2\) can cover all targets in \(F_z\), and the midpoint interval of radius \(D_\phi(z)/2\) does.

The result is an information bound. More downstream computation cannot improve it while the observable state remains \(z\).

## 4. Exact certifiability

**Theorem 3 (certifiability equivalence).** An \(\varepsilon\)-valid fibre-constant certificate exists if and only if
\[
D_\phi(z)\le2\varepsilon.
\]

Necessity follows from Theorem 1. Sufficiency follows because the midpoint is within half the diameter of every fibre member.

This equivalence gives a complete local decision rule. If the diameter condition holds, calibration may choose among valid certificates. If it fails, no calibration procedure restricted to the same representation can create uniform validity. The system must refine the representation or abstain.

## 5. Minimum unconstrained refinement

Fix one fibre and sort its target values:
\[
v_1\le v_2\le\cdots\le v_n.
\]
A refined part is certifiable exactly when its target diameter is at most \(2\varepsilon\). The problem becomes covering the sorted values with the fewest intervals of length \(2\varepsilon\).

**Theorem 4 (greedy optimality).** Start at the smallest uncovered value and include every subsequent value no more than \(2\varepsilon\) above it. Repeating this rule uses the minimum possible number of certifiable parts.

No feasible first interval containing the smallest remaining point can extend farther than the greedy interval. Replacing the first part of any optimum by the greedy choice cannot increase the number of remaining parts; induction completes the argument.

If \(k^*(z,\varepsilon)\) parts are required, then \(k^*-1\) is the exact number of additional representation states needed under unconstrained refinement. This is an information-theoretic construction. It does not imply that the required partition is computable from the features available to a deployed system.

## 6. Restricted separator vocabularies

Let \(\mathcal S\) be a family of admissible predicates. Two instances are \(\mathcal S\)-indistinguishable when every predicate in \(\mathcal S\) assigns them the same value.

**Theorem 5 (separator realizability).** An \(\mathcal S\)-measurable \(\varepsilon\)-valid refinement exists if and only if every \(\mathcal S\)-indistinguishable pair satisfies
\[
|V(x)-V(x')|\le2\varepsilon.
\]

If an indistinguishable pair exceeds the bound, every representation built from \(\mathcal S\) must leave the pair together and is therefore uncertifiable. Conversely, each complete separator-signature atom has diameter at most \(2\varepsilon\) when the pairwise condition holds, so its midpoint certificate is valid.

This theorem exposes the difference between an abstract partition and an implementable one. Refinement requires information that actually distinguishes the target-separated cases.

## 7. Refine-or-abstain coverage

Suppose fibres have population mass \(P(\phi=z)\). A rule that must certify or abstain on each whole original fibre can cover exactly the already certifiable mass.

**Theorem 6 (coverage identity).**
\[
\operatorname{coverage}_{\max}(\varepsilon)
=
\sum_z P(\phi=z)\,
\mathbf 1\{D_\phi(z)\le2\varepsilon\}.
\]

Refinement can recover otherwise uncertifiable mass, but it has a representation cost. Under unconstrained refinement that cost is \(k^*(z,\varepsilon)-1\). Under a restricted separator family, it is the cost of a measurable partition satisfying Theorem 5.

The resulting design problem is fibre-specific. A valid system must know which fibres exceed the tolerance, whether available observations distinguish the offending pairs, and whether the gain in certifiable mass justifies the additional state.

## 8. Adverse empirical history

The theory was motivated by prospective certificate experiments, and their adverse outcomes remain visible.

A frozen held-out construction reached coverage on all 44 decisions but produced 20 strict certificate violations. A matched control without the proposed geometry also reached full coverage and produced fewer violations. The available score had weak, non-decisive association with realized excess and did not supply a reliable abstention boundary.

An oracle could obtain a safe interior by removing the worst realized-excess cases, but realized excess is available only after the outcome and therefore cannot define a prospective selector.

These findings support a narrow conclusion: full marginal coverage did not establish conditional validity, and the available score did not identify the cases on which the system should abstain. They do not reveal the true population fibres or estimate their diameters. The empirical study is a failure analysis, not validation of the theoretical model.

## 9. Relation to neighboring theories

Sufficient representations, Blackwell comparisons, robust decision theory, interval covering, conformal prediction, and selective prediction all supply neighboring concepts. The present result does not replace their probabilistic or decision-theoretic guarantees.

Its role is earlier in the chain. Before asking whether a certificate is statistically calibrated, one must ask whether the representation distinguishes cases whose requested guarantees are incompatible. If it does not, no representation-constant calibration can be uniformly valid.

## 10. Verification and scope

The all-instance statements are analytic. Finite enumeration can independently check small fibre configurations, greedy partitions, separator atoms, and planted counterexamples, but it does not replace the proofs.

The scalar, finite setting is deliberate. Structured targets require a chosen metric or partial order. Sample-based estimation of unknown diameters introduces statistical error. Learning a useful separator vocabulary introduces a model-selection problem. Those extensions are not established here.

## 11. Conclusion

Fibre diameter is the exact deterministic information limit for certification. Half the diameter is the sharp certificate radius, \(D\le2\varepsilon\) is the exact certifiability criterion, greedy interval covering gives the minimum unconstrained refinement, and separator indistinguishability determines which refinements are realizable. The preserved empirical failure shows why these distinctions are operationally necessary: coverage can be complete while conditional certificates remain wrong. A trustworthy system must therefore calibrate only after the representation is certifiable, refine where target-separated cases can be distinguished, and abstain where they cannot.
