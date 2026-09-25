# Domain-Local Regime Geometry in Exact Quantum Compilation

## Abstract

A compact structural law can be exact on a frozen domain yet fail immediately outside it. We study this distinction in a StabPrep exact-compilation programme where the target label is whether a candidate construction attains the donor-exact optimum. The original natural feature vocabulary partitions 1,146 registered instances into cells whose irreducible majority error is 43/1,146. A prospectively frozen enlarged vocabulary changes that conclusion: its 127 coordinates induce 1,109 cells, 1,072 of them singletons, with no mixed cell and zero classification floor on the complete registered domain \(n\leq 3\). Exact separator search nevertheless shows that the zero floor is not merely memorization by the full vocabulary. Every singleton, all 8,001 pairs, and all 333,375 triples fail, whereas the four-feature set \(\{15,30,39,42\}\) yields 523 cells and zero mixed cells. Thus the minimum separator size is exactly \(k^*=4\).

The favourable finite-domain result does not transfer. On unseen \(n=4\) states, the enlarged representation makes 32 errors in 120 cases, equal to the parent cell-lookup baseline, close to a shuffle-null mean of 32.41, and substantially worse than the frozen V2 lattice donor at 3/120. The mechanism attribution is also adverse: two pre-existing feature blocks already attain zero floor, and the minimal witness uses no newly introduced STATE coordinate. We therefore do not claim that sign awareness explains the conversion or that the four-feature rule is universal.

The contribution is a bounded regime-geometry result and a reporting discipline. Exact computation can establish a genuinely compact law on a frozen domain, while held-out failure and donor absorption determine whether that law is transferable or mechanistically novel. The supported statement is that four frozen coordinates exactly determine donor-exactness for the complete \(n\leq 3\) domain; the same representation does not generalize to \(n=4\).

## 1. Introduction

Exact quantum-compilation studies often produce two different kinds of structure. One is a complete finite map: every registered instance is assigned to an exact optimum, and a sufficiently rich representation can reproduce that map. The other is a transferable law: a compact relation continues to predict exact behaviour on instances not used to construct it. These objects should not be identified merely because both can be described as a “regime boundary.”

This paper analyzes a case where the distinction is visible rather than hypothetical. An earlier StabPrep analysis used a frozen natural feature vocabulary and found mixed representation cells imposing a 43/1,146 error floor. That result correctly showed that no predicate over the original vocabulary could exactly separate donor-exact from non-donor-exact cases. A later, prospectively frozen vocabulary removes the mixed cells on the same registered domain. The appropriate scientific question therefore changes from whether the original floor is irreducible to how complex an exact separator must be in the enlarged representation and whether the separator transfers.

The answer has three parts. First, exact search proves that four coordinates are necessary and sufficient on the complete \(n\leq 3\) domain. Second, the rule fails on unseen \(n=4\) cases. Third, the favourable conversion cannot be attributed uniquely to the new sign-aware block because older blocks already contain zero-floor projections. The paper is consequently neither a universal low-order-law paper nor a mechanism-priority paper. It is an exact account of a domain-local separator and its failure boundary.

## 2. Frozen problem and evidentiary chronology

The registered dataset contains 1,146 exact instances distributed as 6 cases at \(n=1\), 60 at \(n=2\), and 1,080 at \(n=3\). Each instance carries a binary target indicating whether the donor construction is exact under the frozen compilation objective. The feature matrix used here is regenerated from committed implementations only after their hashes are checked against the frozen receipt. A hash mismatch is a `CANNOT_CHECK` terminal rather than permission to continue with an unbound representation.

The enlarged representation contains 127 frozen coordinates. It was fixed before separator outcomes were inspected. Its full partition has 1,109 cells, including 1,072 singleton cells and no mixed cell. The chronology matters because an enlarged representation chosen after reading every error could always be suspected of encoding the label directly. Here the vocabulary, regeneration route, target values, and evaluation rules are separately bound.

The original representation remains a valid negative control. Its 43/1,146 floor is reproduced exactly. The later zero floor does not rewrite that earlier result; it shows that the original impossibility was representation-relative.

## 3. Cell floors and separator complexity

For a feature subset \(S\), let two instances be equivalent when their coordinates in \(S\) agree. Each equivalence class is a feature cell. A deterministic classifier using only \(S\) must assign one label to each cell, so its minimum empirical error is the sum of minority counts across the cells. An exact separator is a subset with no mixed-label cell.

The full 127-coordinate representation has floor zero. Because the partition is nearly injective, that fact alone is not enough. A representation with one cell per instance can obtain zero floor without revealing a compact scientific relation. We therefore define the separator complexity

\[
 k^*=\min\{|S|:S\text{ induces no mixed-label cell on the frozen domain}\}.
\]

This is a finite discernibility problem. Opposite-label pairs impose separation obligations, and a feature subset is sufficient exactly when it hits every such obligation. The underlying rough-set and hitting-set mathematics is donor-owned; the ORION-specific contribution is the exact instantiation and the held-out test.

## 4. Exact four-feature law on \(n\leq 3\)

The lower bound is exhaustive. All 127 one-coordinate projections fail. All 8,001 pairs fail. All 333,375 triples fail. Consequently \(k^*\geq 4\).

The upper bound is constructive. The subset

\[
S^*=\{15,30,39,42\}
\]

induces 523 cells over all 1,146 instances and no mixed-label cell. Reprojecting the complete frozen matrix verifies every row directly, so \(k^*\leq 4\). Together,

\[
oxed{k^*=4}.
\]

The witness is substantially compressed: 523 cells for 1,146 instances. A counting bound permits an error floor as high as 623/1,146 for a partition of that size, yet the observed floor is zero. Under the exact structure-free relabelling null that preserves the cell partition and class balance, the probability of a zero floor is approximately \(1.442\times 10^{-120}\). The compact separator therefore reflects real alignment between the registered labels and the four-coordinate partition; it is not explained by cell count alone.

This result is exact for the frozen \(n\leq 3\) universe. It is not an all-size theorem.

## 5. Why the full-vocabulary zero is not merely a small-cell artifact

The complete representation is nearly injective, so a hostile review must ask how much freedom the cell structure leaves before labels are read. With \(N=1,146\) instances and \(c=1,109\) cells, the realized partition alone confines the majority error to at most

\[
(N-c)/N=37/1,146\approx0.0323.
\]

The exact relabelling probability of zero error under the observed class balance is \(7.057\times 10^{-7}\); none of 20,000 sampled relabellings reaches zero. This resolves the narrow memorization objection for the full vocabulary, but the four-feature result is scientifically more informative because it removes near-injectivity as the primary explanation.

The two analyses answer different questions. The full-vocabulary null asks whether label alignment is stronger than expected from a highly fragmented partition. The \(k^*=4\) result asks whether a small frozen projection is exactly sufficient. Both are needed for a fair account.

## 6. Mechanism attribution is not established

The enlarged vocabulary was motivated in part by sign-aware state information. A favourable zero-floor conversion might therefore be read as evidence that the new STATE block is the operative mechanism. Exact block ablations reject that interpretation.

Any two of the three L3 blocks attain zero floor. In particular, the pre-existing combination `V2 + donor-path` separates every opposite-label pair without any sign-aware coordinate. The minimum four-feature witness likewise contains no STATE-block coordinate.

A previously reported pair-level example remains correct: the STATE block resolves one pair that survives under V2 alone. What fails is the stronger causal statement that sign awareness is required for the global conversion. The fair conclusion is that the enlarged frozen information system contains several sufficient routes and does not identify a unique mechanism.

This donor absorption is not a weakness to hide. It prevents the paper from assigning novelty to whichever block happened to motivate the successor.

## 7. Held-out \(n=4\) failure

The decisive transfer test uses unseen \(n=4\) states. The enlarged representation produces 32 errors in 120 cases, identical to the parent cell-lookup baseline. A shuffle null has mean 32.41 errors and empirical \(p=0.51\). The result is therefore indistinguishable from the registered null under this evaluation.

A stronger frozen donor, the V2 lattice parent, makes only 3 errors in 120 cases. The four-feature law is not merely imperfect; it loses to an existing representation on the held-out domain.

This adverse result fixes the paper's scope. The exact \(n\leq 3\) law is a finite-domain regime geometry, not a universal compilation law. The observed failure may reflect missing interactions that appear first at larger system size, but the present evidence does not identify a replacement mechanism.

## 8. What is established

The evidence supports the following claims.

1. The original natural vocabulary has an exact irreducible floor of 43/1,146 on the registered domain.
2. The prospectively frozen enlarged vocabulary has zero floor on the complete \(n\leq 3\) domain.
3. Exactly four enlarged-vocabulary coordinates are necessary and sufficient for that zero floor.
4. The four-feature witness is non-injective and its exact separation is not explained by partition size.
5. The favourable conversion does not require the newly introduced STATE block.
6. The enlarged representation fails on unseen \(n=4\) states and is outperformed there by the V2 lattice donor.

The evidence does not support an all-size law, a unique mechanism attribution, physical-resource advantage, or superiority over the strongest donor outside the frozen domain.

## 9. Relation to prior work

Rough-set reducts, discernibility matrices, hitting-set formulations, finite sufficient representations, and cell-wise Bayes floors are established mathematical donors. Exact synthesis and structural compiler rules likewise predate this study. The paper does not claim those general constructions.

The residual is the combined scientific record: a prospectively frozen vocabulary, an exact minimum separator on a complete finite compilation domain, a structure-aware anti-memorization analysis, explicit donor subtraction, and a held-out failure that prevents the finite law from borrowing universal authority.

## 10. Reproducibility

A release package should contain the immutable instance identities and labels, the hash-bound feature generators, the regenerated 1,146-by-127 matrix, the exhaustive singleton/pair/triple lower-bound search, the four-feature witness verification, the exact cell-based null calculations, and the unseen \(n=4\) comparison including the V2 donor. The original 43/1,146 negative and the later zero-floor result must remain separately reconstructable.

The paper's numerical claims are deterministic given the bound artifacts. Internal independent replay checks implementation identity and arithmetic; it is not external scientific replication.

## 11. Limitations and next valid study

The main limitation is direct: the separator is exact only on \(n\leq 3\). Feature indices are representation-specific and do not by themselves provide a human-readable physical law. The minimality result is with respect to the frozen 127-coordinate vocabulary, not every possible scientific description.

A valid successor must use a new identity. One route is to derive a canonical interaction hypergraph from \(n\leq 4\) derivation data, freeze it, and test a deterministic \(n=5\) challenge before reading costs. Reordering the current four features or tuning against the \(n=4\) labels would not repair the present claim; it would create a post-outcome rescue.

## 12. Conclusion

Exact finite separation and transferable scientific law are different achievements. In the frozen StabPrep study, a prospectively enlarged representation admits an exact four-feature separator over all 1,146 cases at \(n\leq 3\). Exhaustive lower search proves that no smaller projection suffices, and exact null calculations show that the result is not a trivial consequence of cell fragmentation. Yet the representation fails on unseen \(n=4\) states, and the conversion cannot be credited uniquely to the new sign-aware block. The durable contribution is therefore a domain-local regime geometry together with its falsified transfer boundary.