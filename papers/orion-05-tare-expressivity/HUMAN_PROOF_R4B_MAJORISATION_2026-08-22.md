# Human proof of the R4B split-TARE grouping rule — 2026-08-22

Status: analytic proof of the coefficient-coordinate statement already checked in `MAX_R4B_TARE_SPLIT_MAJORISATION_RESULTS.json`. This note **reduces**, rather than enlarges, the novelty claim: the mathematical engine is a standard majorization/Schur-concavity argument. The TARE instantiation may be useful, but the classical majorization principle itself must receive zero novelty credit.

## Setting

Let `L = g*m` nonnegative coefficient magnitudes be

\[
a_1\ge a_2\ge\cdots\ge a_L\ge0.
\]

Partition the indices into `g` unlabeled groups `G_1,...,G_g`, each of cardinality `m`. The frozen split-TARE outer normalization coordinate is

\[
\Lambda(\mathcal G)
=\sqrt m\sum_{r=1}^{g}
\sqrt{\sum_{i\in G_r}a_i^2}.
\]

The common factor `sqrt(m)` does not affect the minimizer.

Define squared magnitudes

\[
x_i=a_i^2,
\qquad x_1\ge x_2\ge\cdots\ge x_L.
\]

For a partition `G`, let

\[
s_r=\sum_{i\in G_r}x_i
\]

be the group square-mass and sort the vector `s=(s_1,...,s_g)` in descending order.

The sorted-contiguous partition is

\[
G_r^*=\{(r-1)m+1,\ldots,rm\},
\]

with group sums

\[
s_r^*=\sum_{i=(r-1)m+1}^{rm}x_i.
\]

## Theorem

The sorted-contiguous equal-size partition minimizes `Lambda` over all equal-size partitions.

## Proof

### Step 1: the contiguous group-sum vector majorizes every other partition

Take any equal-size partition and its descending group sums

\[
s_{[1]}\ge\cdots\ge s_{[g]}.
\]

For every `k=1,...,g`, the `k` groups with the largest group sums contain exactly `km` coefficients. Therefore

\[
\sum_{r=1}^{k}s_{[r]}
\le
\sum_{i=1}^{km}x_i,
\]

because no set of `km` entries can have larger total mass than the `km` largest entries of the sorted sequence.

But the right-hand side is exactly the sum of the first `k` contiguous group sums:

\[
\sum_{i=1}^{km}x_i
=
\sum_{r=1}^{k}s_r^*.
\]

At `k=g` both sides equal the total square-mass `sum_i x_i`.

Hence

\[
s^*\succ s,
\]

so the sorted-contiguous group-sum vector **majorizes** the group-sum vector of every other equal-size partition.

### Step 2: square-root summation is Schur-concave

The function

\[
\Phi(s_1,\ldots,s_g)=\sum_{r=1}^{g}\sqrt{s_r}
\]

is symmetric and concave on the nonnegative orthant, hence Schur-concave. Therefore

\[
s^*\succ s
\quad\Longrightarrow\quad
\Phi(s^*)\le\Phi(s).
\]

Multiplying by the common positive factor `sqrt(m)` gives

\[
\Lambda(\mathcal G^*)\le\Lambda(\mathcal G)
\]

for every equal-size partition `G`.

Thus the sorted-contiguous grouping is optimal. `square`

## Equality / interpretation

The minimizer need not be unique when coefficient magnitudes are repeated or when different partitions induce the same vector of group square-masses. The theorem identifies an optimal canonical grouping, not unique index identity in tied cases.

The intuition follows concavity: `sqrt` penalizes balancing the group square-masses. To minimize the sum of square roots while preserving total square-mass, the groups should be as unequal as the cardinality constraint permits. Putting the largest magnitudes together, then the next largest, realizes the group-sum vector that majorizes all competitors.

## Relation to the machine checks

The R4B runner exhaustively enumerates thousands of finite partitions across random and hostile coefficient sets and observes zero failures. Those checks remain useful for implementation binding, ties, zeros, identity remint/permutation controls and numerical regression. They are not required to establish the theorem once the majorization proof is stated.

## Publication boundary

The publication-safe statement is:

> For the equal-cardinality split-TARE normalization objective `sqrt(m) * sum_g ||c_g||_2`, sorting coefficient magnitudes and grouping contiguously is optimal by a direct majorization/Schur-concavity argument.

Do **not** claim the majorization technique itself as new. Before presenting the TARE specialization as a novelty item, perform a conventional nearest-work search in clustering/partitioning/majorization literature. ORION-01 should currently use this as supporting mathematics, not as the flagship novelty claim.
