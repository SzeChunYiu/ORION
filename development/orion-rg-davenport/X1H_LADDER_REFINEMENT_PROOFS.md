# Refinements of the eta-ladder (Lemma B)

## Notation
G finite abelian (additive). A *sequence* = finite multiset S over G; |S| length; sum(S) the sum.
A *zero-sum* of S = nonempty sub-multiset A with sum(A)=0.  minzs(S)=min{|A| : A zero-sum}, = INF if none.
D(G) Davenport constant = least d with every length-d sequence having a zero-sum
     = 1 + (max length of a zero-sum-free sequence).
Standard fact (F1): every zero-sum minimal under inclusion has length <= D(G).
D_k(G) = least L such that every length-L sequence has k pairwise disjoint zero-sums; D_0=0, D_1=D.
f_T(G) = max length of a sequence with no zero-sum of length <= T (INF if unbounded); eta_T = f_T+1.
Facts: f_T = INF iff T < exp(G);  f_T = D-1 and eta_T = D for T >= D.

Lemma B (given):  D_{k+1} <= min_T max(eta_T, D_k + T).

===============================================================================
NEGATIVE RESULTS: single-threshold Lemma B is already optimal given only {eta_T}
===============================================================================

## Theorem N1 (h-form equivalence)
Define h(n) = max{ minzs(S) : |S| = n }.  Then
 (i)  h is non-increasing;
 (ii) h(n) <= T  <=>  n >= eta_T;
 (iii) min{ L : L - h(L) >= D_k }  =  min_T max(eta_T, D_k + T).

Proof.
(i) If |S|=n+1 with minzs(S)=m, delete one element: S' has |S'|=n and every zero-sum of S'
    is a zero-sum of S, so minzs(S') >= m. Hence h(n) >= h(n+1).
(ii) h(n) > T  <=>  some length-n S has no zero-sum of length <= T  <=>  n <= f_T  <=>  n < eta_T.
(iii) (<=) Let L = max(eta_T, D_k+T) for an optimal T. By (ii) h(L) <= T, and
      L >= D_k+T >= D_k+h(L), so L - h(L) >= D_k.
      (>=) Let L satisfy L - h(L) >= D_k and set T := h(L). By (ii) L >= eta_T; also L >= D_k+T.  []

So the sharpest possible "extract ONE minimum-length zero-sum, then apply D_k" bound
is *literally* Lemma B. Nothing is lost by committing to a single threshold.

## Theorem N2 (multi-threshold peeling collapses)
Peeling with thresholds T_1,...,T_j and then applying D_m gives
   D_{m+j} <= max( max_{i<=j} ( eta_{T_i} + sum_{l<i} T_l ),  D_m + sum_{l<=j} T_l ).
For j=2 this family, minimized over (T_1,T_2), equals the family from applying Lemma B twice.

Proof. The display follows by induction: peel i needs current length >= eta_{T_i}, and the
current length is >= L - sum_{l<i} T_l.  For j=2 it reads
        max( eta_{T1}, eta_{T2}+T1, D_m+T1+T2 ),
while iterating Lemma B (bound D_{m+1} with T_1, then D_{m+2} with T_2) reads
        max( eta_{T2}, eta_{T1}+T2, D_m+T1+T2 ).
These are exchanged by the transposition (T1 T2); as T_1,T_2 range over all thresholds the
two families are the same set of numbers.  []

Remark. The *greedy* peel (always remove a minimum-length zero-sum) satisfies m_1<=m_2<=...
because minzs is monotone under passing to sub-multisets. But that is a LOWER bound on each
m_i, so it does not constrain the adversary, who maximises each m_i. The worst-case greedy
chain n_i = n_{i-1} - h(n_{i-1}) reproduces exactly the iterated N1 bound.

CONSEQUENCE. Any strict improvement of Lemma B must use a statistic strictly finer than
{eta_T}: it must say something about WHICH sequences realise minzs > T, not merely how long
such sequences can be.

===============================================================================
POSITIVE RESULTS
===============================================================================

## Lemma Z (sum-zero splitting)
If sum(S)=0 then S partitions into zero-sums each of length <= D(G); hence S contains at
least ceil(|S| / D(G)) pairwise disjoint zero-sums.

Proof. If S is nonempty with sum(S)=0 then S is itself a zero-sum, so it contains an
inclusion-minimal zero-sum A, and |A| <= D(G) by (F1). Since sum(S\A) = 0 - 0 = 0, recurse
on S\A. This partitions S into A_1,...,A_t with sum |A_i| = |S| and each |A_i| <= D(G),
so t >= |S|/D(G).  []

## New statistics
f_T^{!=0}(G) := max length of a sequence S with minzs(S) > T AND sum(S) != 0;
                eta_T^{!=0} := f_T^{!=0} + 1.        (Always <= f_T, eta_T.)
D_k^{>=m}(G) := least L such that every sequence S with |S|=L and minzs(S) >= m has k
                pairwise disjoint zero-sums.
                (Monotone in L, so well defined; vacuously D_k^{>=m} <= f_{m-1}+1 = eta_{m-1}.)

## Lemma D*  (sharp threshold-conditioned ladder)   -- the main refinement
For every k >= 0 and every T >= 1:
        D_{k+1}(G) <= max( D_{k+1}^{>=T+1}(G),  D_k(G) + T ),
hence   D_{k+1}(G) <= min_{T>=1} max( D_{k+1}^{>=T+1}(G),  D_k(G) + T ).

Proof. Put L = max(D_{k+1}^{>=T+1}, D_k+T) and take any S with |S| = L.
 * If minzs(S) <= T: pick a zero-sum A of MINIMUM length, so |A| <= T. Then
   |S\A| >= L - T >= D_k, so S\A carries k pairwise disjoint zero-sums; with A that is k+1.
 * If minzs(S) >= T+1: then L >= D_{k+1}^{>=T+1} yields k+1 pairwise disjoint zero-sums
   directly.  []

### Proposition D*-dominance:  D_{k+1}^{>=T+1} <= eta_T, so Lemma D* <= Lemma B, termwise in T.
Proof. At L = eta_T = f_T+1 there is NO sequence of length L with minzs >= T+1 at all
(such a sequence has no zero-sum of length <= T, so has length <= f_T < L). The defining
condition is vacuously true, so D_{k+1}^{>=T+1} <= eta_T.  []
Hence Lemma D* can never be weaker than Lemma B anywhere. It is the sharpest bound of the
shape "condition on minzs(S) vs T".

## Lemma S  (computable relaxation of D*, provable by hand)
For every k >= 0 and T >= 1:
        D_{k+1}^{>=T+1}(G) <= max( eta_T^{!=0}(G),  k*D(G) + 1 ),
and therefore
        D_{k+1}(G) <= min_{T>=1} max( eta_T^{!=0}(G),  D_k(G) + T,  k*D(G) + 1 ).

Proof. Let L = max(eta_T^{!=0}, kD+1) and |S| = L with minzs(S) >= T+1. If sum(S) != 0 then
S witnesses f_T^{!=0} >= L, i.e. L <= f_T^{!=0} < L, absurd. So sum(S) = 0. By Lemma Z, S has
at least ceil(L/D) >= ceil((kD+1)/D) = k+1 pairwise disjoint zero-sums. Feed into Lemma D*. []

### Corollary (first rung, unconditional improvement)
For k = 1 the term k*D+1 = D+1 <= D_1 + T (T >= 1) is absorbed, so
        D_2(G) <= min_{T>=1} max( eta_T^{!=0}(G), D(G)+T )  <=  min_{T>=1} max( eta_T(G), D(G)+T ).
So at the first rung Lemma S is an unconditional refinement of Lemma B.

### Boundary of Lemma S
Lemma S differs from Lemma B only on the window   f_T^{!=0} < L <= f_T,
i.e. exactly when every extremal "no zero-sum of length <= T" sequence of length L is forced
to have total sum 0. Outside that window it degenerates to Lemma B.
For k >= 2 the term k*D+1 can dominate, so Lemma S is NOT uniformly <= Lemma B; we therefore
always report min(Lemma B, Lemma S, Lemma D*), which by construction is never worse than
Lemma B on any instance.
