# Low-Order Decision Certificates and Value-Estimation Limits in Structured Quantum Compilation

## Abstract

Low-order statistics can decide whether optimization is needed while failing
to determine an optimum's value or structure. We prove this hierarchy for a
Pauli partition compiler with a fixed structural SELECT-PREPARE-width
objective. For every \(m\ge5\), the unary compiler is globally optimal exactly
when every pair gain is nonpositive and the sum of any two disjoint pair gains
plus one is nonpositive. The largest clause touches four term indices, and an
explicit \(m=4\) instance proves the threshold sharp.

For every \(t\ge1\), two explicit \(5t\)-term families have identical ordered
weights and complete labeled pair-gain matrices, yet their exact improvements
are \(12t-2\) and \(10t-1\). Pair-only estimators therefore incur real additive
error at least \((2t-1)/2\), integer error at least \(t\), and symmetric factor
at least \(\sqrt{(12t-2)/(10t-1)}\); no uniform factor below \(\sqrt{6/5}\) is
possible. One family forces a triple block, while the other uses only pairs and
singletons.

For every \(m\ge5\) and \(L\ge1\), a second pair of instances agrees on every
labeled common-factor count through order \(m-2\) but has value gap
\([m(\lceil\log_2m\rceil+1)-1]L\). Moebius inversion proves that the parity
trade is the unique nonzero integer direction invisible to all proper labeled
marginals. These are representation limits, not computational-hardness claims.

**Keywords:** quantum compilation; low-order certificates; information lower
bounds; minimax estimation; Markov bases; Möbius inversion

## 1. Introduction

Global combinatorial optimization supports several distinct downstream
questions: whether a baseline is optimal, how much improvement is available,
what structure an optimizer must contain, and whether a feature representation
approximates the optimum uniformly. A representation can be complete for one
question and incomplete for another.

We give an exact scalable example in structured quantum compilation. The
compiler partitions \(m\) Pauli terms into arbitrary blocks, extracts common
Pauli factors, and pays a structural cost. Although its candidate space contains
every set partition, unary optimality is decided by inequalities involving at
most four indices. This makes pair information appear unusually powerful. Our
remaining theorems locate its exact limits.

The contributions are:

1. a four-index decision theorem for every \(m\ge5\), with an exact four-term
   counterexample;
2. two pair-indistinguishable product families with unbounded additive value
   gap and forced triple-versus-pair optimizer structure;
3. exact real, integer, symmetric multiplicative, and one-sided minimax lower
   bounds;
4. a construction showing that interactions through order \(m-2\) do not
   determine exact value; and
5. a primitive-kernel theorem showing that the corresponding invisible
   difference trade must be the dense parity direction.

## 2. Compiler and objective

An instance is an ordered tuple of nonidentity Pauli strings
\(p_1, \ldots, p_m\). Let \(w_i\) be the weight of term \(i\), let
\(W=\sum_iw_i\), and let \(f(S)\) count the columns on which every term in a
nonempty block \(S\) has the same nonidentity Pauli.

The compiler chooses a set partition \(\Pi\) and factor/ancilla options. Under
the fixed equal-weight structural objective, factoring and shared width dominate
their alternatives. For \(|\Pi|\ge2\), the reduced cost is

\[
\begin{aligned}
C(\Pi)={}&2m+|\Pi|-3+\sum_{S\in\Pi}d(|S|)
+\max_{S\in\Pi}b(|S|)\\
&+\sum_{S\in\Pi}\left[2f(S)+(b(|S|)+2)
\bigl(w(S)-|S|f(S)\bigr)\right],
\end{aligned}
\]

where \(b(s)=\lceil\log_2s\rceil\), \(b(1)=0\), and

\[
d(1)=0, \qquad
d(s)=d(\lceil s/2\rceil)+d(\lfloor s/2\rfloor)+s-2.
\]

The unary incumbent has cost \(C_U=2W+3m-3\). The one-block flag convention is
evaluated separately. These are structural compiler costs, not physical T
counts, depth, runtime, qubits, or fault-tolerant overhead.

## 3. A four-index decision certificate

For every pair, define

\[
g_{ij}=4f(\{i, j\})-(w_i+w_j).
\]

Let \(\mathcal P_4(m)\) require

\[
g_{ij}\le0
\]

for every pair and

\[
g_{ij}+g_{k\ell}+1\le0
\]

for every two disjoint pairs.

**Theorem 1.** For every \(m\ge5\),

\[
\min_\Pi C(\Pi)=C_U
\quad\Longleftrightarrow\quad
\mathcal P_4(m).
\]

**Proof.** First suppose \(|\Pi|\ge2\). For a block \(S\) of size \(s\), set

\[
T_s(S)=[s(b(s)+2)-2]f(S)-b(s)w(S),
\qquad h_s=s-1-d(s).
\]

Direct expansion of the cost gives

\[
C_U-C(\Pi)=\sum_{S\in\Pi}\bigl(T_{|S|}(S)+h_{|S|}\bigr)
-\max_{S\in\Pi}b(|S|).
\]

The depth recurrence yields \(h_s=1\) for \(s=2,3,4\), \(h_5=0\), and
\(h_s\le0\) for \(s\ge5\). For a block of size \(s\ge3\), take a perfect
matching if \(s\) is even and an \(s\)-cycle if \(s\) is odd. Summing the pair
clauses counts every term once or twice and uses
\(f(\{i,j\})\ge f(S)\), giving \(w(S)\ge2s f(S)\). Therefore

\[
T_s(S)\le[s(2-b(s))-2]f(S)\le-2;
\]

when \(f(S)=0\), the stronger bound
\(T_s(S)=-b(s)w(S)\le-b(s)s\) applies. Thus every block of size at least three
has total credit \(T_s+h_s\le-1\).

For a pair, \(T_2+h_2=g_{ij}+1\). Pair blocks in one partition are disjoint.
Their gains are integers, every \(g_{ij}\le0\), and the two-pair clause prevents
two of them from being zero. Hence any collection of pair blocks has total
credit at most one. If the partition contains only pairs and singletons, the
final width term is one and the total gain is nonpositive. If it contains a
larger block, that block cancels the possible unit of pair credit and the width
term is at least two, again making the gain nonpositive.

For the exceptional one-block partition, write \(b=b(m)\),
\(F=f([m])\), and \(d=d(m)\). Direct calculation gives

\[
C_U-C_{\mathrm{one}}
=(1-b)W+[m(b+1)-1]F+2m-2-d-b.
\]

The same matching/cycle sum gives \(W\ge2mF\). If \(F=0\), then \(W\ge m\)
and the gain is negative. If \(F\ge1\), the recurrence closes
\(5\le m\le8\) with \(b=3,d=2m-6\), closes \(9\le m\le16\) with
\(b=4,d\ge m-1\), and \(b\ge5\) makes the remaining coefficient negative for
\(m\ge17\). Thus no partition improves on unary when \(\mathcal P_4(m)\)
holds.

Conversely, a failed pair clause is witnessed by that pair and all remaining
singletons; a failed disjoint-pair clause is witnessed by those two pairs and
the remaining singletons. Their gains are respectively \(g_{ij}\) and
\(g_{ij}+g_{k\ell}+1\). ∎

The four-term instance

\[
XXII, \quad XYII, \quad XZII, \quad XIXX
\]

satisfies both clause families, yet has \(C_U=27\) and one-block cost \(23\).
The term-count threshold is therefore sharp.

## 4. Complete pair information, different values and optimizers

The local five-term gadgets act on six qubits. Written with the first qubit on
the left, they are

\[
\begin{aligned}
A_1={}&(\mathrm{XXXXII},\mathrm{XXXIXI},\mathrm{XXXIIX},
        \mathrm{XXIIII},\mathrm{XXIIII}),\\
B_1={}&(\mathrm{XXXXII},\mathrm{XXXIXI},\mathrm{XXIXXI},
        \mathrm{XXIIII},\mathrm{XXIIII}).
\end{aligned}
\]

Both have ordered weights \((4,4,4,2,2)\), and direct intersection of their
supports gives the same common-factor count for every labeled pair. For
\(t\ge1\), let \(A_t\) and \(B_t\) be \(t\) copies on disjoint six-qubit
coordinate sets.

To determine their optima, use the block credit
\(U(S)=T_{|S|}(S)+h_{|S|}\) from the proof of Theorem 1. Enumerating the 31
nonempty subsets and 52 partitions of one five-term gadget gives a unique
maximum \(\sum U=12\) for \(A_1\), at the triple-plus-pair partition
\(\{\{1,2,3\},\{4,5\}\}\). For \(B_1\), the maximum is 10 and is attained only
by pair-and-singleton partitions. A block meeting two gadgets has
\(f(S)=0\) and strictly negative credit; splitting it by gadget increases
\(\sum U\) without increasing the maximum index width. The global optimum
therefore decomposes by gadgets. Accounting once for the shared maximum-width
term yields

\[
\Delta_A(t)=12t-2,
\qquad
\Delta_B(t)=10t-1.
\]

Their value gap is \(2t-1\). Every optimum in \(A_t\) contains the distinguished
triple block and one pair in each gadget. Every optimum in \(B_t\) uses only
pairs and singletons. Thus complete pair information determines neither the
exact improvement nor the presence of a triple block in an optimizer. The
ancillary verifier reproduces every local subset/partition row and performs
direct full-partition checks for \(t=1,2\); the scalable formulas follow from
the displayed decomposition.

## 5. Exact minimax consequences

Let \(\Phi\) be any deterministic real-valued estimator whose input is exactly
the term count, ordered weights, and complete labeled pair-gain matrix. The two
fiber members have identical inputs, so \(\Phi\) returns one value \(y_t\) for
both.

**Theorem 2 (additive minimax radius).** For every \(t\ge1\),

\[
\max\{|y_t-\Delta_A|,|y_t-\Delta_B|\}
\ge \frac{2t-1}{2}.
\]

The midpoint attains equality. If the estimator must return an integer, the
minimum worst-case error is exactly \(t\).

**Proof.** Two real values at distance \(2t-1\) cannot both lie within a smaller
radius of one estimate. The integer radius is the ceiling of half the distance.
∎

### 5.1 Symmetric multiplicative estimation

For positive improvements, use the convention

\[
\Delta/\rho\le y\le\rho\Delta,
\qquad \rho\ge1.
\]

**Theorem 3.** A common estimate valid for both fiber members requires

\[
\rho\ge
\sqrt{\frac{\Delta_A}{\Delta_B}}
=\sqrt{\frac{12t-2}{10t-1}}.
\]

The geometric mean attains equality. The bound increases with \(t\) and tends
to \(\sqrt{6/5}\). Hence no estimator using only the stated pair information
has a uniform symmetric factor strictly below \(\sqrt{6/5}\) on this family.

For one-sided certificates, a common upper estimate must be at least
\(\Delta_A\) but at most \(\alpha\Delta_B\) to approximate \(B_t\); the same
ratio applies to a common lower estimate. Thus the asymptotic one-sided factor
is at least \(6/5\). These are information lower bounds, not computational
hardness results.

## 6. Proper interactions still miss exact value

Fix \(m\ge5\), set \(q=m-1\), \(b=\lceil\log_2m\rceil\), and distinguish one
anchor from \(q\) variable terms. For every subset \(S\subseteq[q]\) of one
parity, place \(L\) columns supported on the anchor together with the variables
in \(S\); use the opposite parity in the second instance. Each side therefore
has \(N=2^{m-2}L\) trade columns. Add to both instances

\[
K=Nm(b+1)+m-1+d(m)+b+1
\]

columns supported on all \(m\) terms.

The resulting pair agrees on ordered weights and on every labeled common-factor
count for subsets of size at most \(m-2\), yet

\[
\Delta(A)-\Delta(B)
=\left[m(\lceil\log_2m\rceil+1)-1\right]L.
\]

**Proof.** For every proper labeled subset of terms, the two parity classes
contain the same number of supersets, so all common-factor counts through order
\(m-2\) agree. The common padding also makes the one-block partition uniquely
optimal: for any proper partition, the exact cost difference from the full
block is bounded below by

\[
3K-Nm(b+1)-[m-1+d(m)+b]>0.
\]

Only the full common-factor count differs. Its coefficient in the one-block
improvement is \(1-m(b+1)\), while the parity imbalance is \(L\), giving the
displayed absolute gap. Thus, for fixed \(m\), the ambiguity is unbounded in
\(L\). ∎

## 7. The unique invisible direction

Represent a trade column by a subset of \([q]\). Let
\(\delta:2^{[q]}\to\mathbb Z\) be the signed multiplicity difference, and
define its upper marginal by

\[
M(T)=\sum_{S\supseteq T}\delta(S).
\]

Equality of all proper labeled marginals is \(M(T)=0\) for every proper
\(T\subsetneq[q]\).

**Theorem 4 (proper-marginal kernel).** If every proper upper marginal vanishes,
then

\[
\delta(S)=(-1)^{q-|S|}c,
\qquad c=\delta([q]).
\]

**Proof.** Möbius inversion on the Boolean lattice expresses \(\delta(S)\) as
the alternating sum of upper marginals over supersets of \(S\). Only the top
marginal can remain. ∎

If \(c\ne0\), every Boolean cell is used and exactly half occur on each signed
side. A primitive integer trade therefore has mass at least
\(2^{q-1}=2^{m-2}\) on each side. The parity construction with \(L=1\) attains
this bound. The statement proves minimality of the *difference trade*; it does
not prove that the common padding is minimal.

## 8. Relation to prior work

Markov-basis and hierarchical-model theory [1-5] owns the generic language of
fibers, marginal-preserving moves, toric ideals, and higher-order interactions
invisible to lower marginals. Boolean-lattice Möbius inversion is classical.

The residual result is the exact conjunction for the fixed compiler objective:
a four-index certificate decides global unary optimality for all \(m\ge5\), the
same pair representation has exact unbounded and multiplicative value limits,
optimizer block structure is not identifiable, and even order-\(m-2\)
information misses exact value through the primitive parity direction.

## 9. Reproducibility and limitations

The four-term witness, pair-indistinguishable gadgets, product formulas,
minimax optima, and Boolean-lattice kernel have been checked with independent
exact implementations; the analytic arguments provide all-parameter authority.

The results apply to the stated structural objective. The decision theorem
does not reconstruct an optimizer. The minimax bounds apply to estimators
restricted to the exact declared representation. The high-order construction
uses conservative common padding whose minimality is open. The work proves
information nonidentifiability, not a complexity-class lower bound. Transfer to
other compiler grammars or physical resource models remains open.

## 10. Conclusion

Information sufficiency is query-dependent. Complete pair information decides
whether the unary compiler is optimal, yet it cannot recover the improvement
value within arbitrarily small additive or fixed multiplicative error and
cannot determine optimizer block structure. Even all labeled interactions
below the top two orders fail to determine exact value, and the invisible
integer direction is necessarily dense.

A perfect decision statistic is therefore not automatically a useful value
statistic. In this compiler, the distinction is exact, scalable, and
independent of computational assumptions.

## Data and code availability

Exact implementations reproducing the four-term witness, paired gadget
families, product formulas, minimax calculations, and Boolean-lattice kernel
accompany the submission source. They are verification aids; the displayed
arguments carry the all-parameter claims. A permanent archival identifier must
be inserted before final upload.

## References

1. P. Diaconis and B. Sturmfels, “Algebraic Algorithms for Sampling from
   Conditional Distributions,” *The Annals of Statistics* **26**, 363-397
   (1998). DOI: 10.1214/aos/1030563990
2. A. Dobra, “Markov Bases for Decomposable Graphical Models,” *Bernoulli*
   **9**, 1093-1108 (2003). DOI: 10.3150/bj/1072215202
3. S. Hosten and S. Sullivant, “A Finiteness Theorem for Markov Bases of
   Hierarchical Models,” *Journal of Combinatorial Theory, Series A* **114**,
   311-321 (2007). DOI: 10.1016/j.jcta.2006.06.001
4. M. Develin and S. Sullivant, “Markov Bases of Binary Graph Models,”
   *Annals of Combinatorics* **7**, 441-466 (2003).
   arXiv: math/0308280
5. D. Král', S. Norine, and O. Pangrác, “Markov Bases of Binary Graph Models
   of \(K_4\)-Minor-Free Graphs,” *Journal of Combinatorial Theory, Series A*
   **117**, 759-765 (2010). DOI: 10.1016/j.jcta.2009.07.007
