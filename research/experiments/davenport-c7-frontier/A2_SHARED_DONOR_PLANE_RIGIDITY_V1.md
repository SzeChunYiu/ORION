# Shared-donor plane rigidity for maximal type a=2 — V1

Status: **proved exact plane-fiber envelope and sharp one-value extension theorem**. These are symbolic results; the accompanying finite checks are regression, not proof. No complete support-seven theorem or generalized Davenport constant is claimed.

## 1. Source interface and the change of donor

The starting checkpoint was `9229d28be5a643ff7bf30ea6213aba717c48e309` (V8). Before commit, the live branch was re-read at `6be5e754005317f9389d677065572a0ce26743e9`; this additive result is based on that head, preserving the parallel work. The parallel lane read at `6be5e754005317f9389d677065572a0ce26743e9` supplies `A2_EXACT_DEPTH_FIBER_ENVELOPE_V1.md` and `A2_MAXIMAL_OVERLAP_STANDARD_FAMILIES_EMPTY_V1.md`. The latter eliminates two standard top-overlap families using the other new value and an inverse-quarter selector.

The change here is to use **all already available shared copies as part of the donor**. If `V=s^c R`, then `UV=(U s^c)R`. A short zero-sum may freely use both the original and shared copies of s. They are separate occurrences; none is used twice. Consequently, for every nonempty `W|R`, short-freeness requires

`|W| + rho_(U s^c)(-sigma(W)) >= m`.

This is the original graded-depth principle applied to a different occurrence partition. The donor need not be an atom. Its own nonempty zero-sums must be checked separately.

Use the basis `(e1,e2,g)`, with

`p=2H+1 >= 7`, `u=(p+1)/2`, `s=(u,u,1)`,

`U=e1^(p-1)e2^(p-1)g^(p-2)s^2`.

For `1<=c<=H`, set `K=c+2` and

`B_K=U s^c=e1^(p-1)e2^(p-1)g^(p-2)s^K`.

Write `[v]_p` for the least nonnegative residue. The coordinate plane studied below is

`Pi={(A,-A,C): A,C in F_p}`.

It is NOT the whole group and NOT the overlap plane spanned by s and g.

## 2. Exact enlarged-donor plane-fiber envelope

Define

`E_K(C)=max_A rho_(B_K)(A,-A,C)`.

**Theorem 1.** For every odd prime `p=2H+1>=7`, `3<=K<=H+2`, and `0<=C<=p-1`,

```
E_K(C) = p                         if C=0,1,2;
         p+1                      if 3<=C<=K;
         p+C-K+1                  if K+1<=C<=p-1.
```

Empty ranges are ignored. These are exact maxima, not just upper bounds.

### Proof

Selecting k copies of s forces the other resource counts, so a candidate representation has length

`S_k(A)+[C-k]_p+k`,

where

`S_k(A)=[A-ku]_p+[-A-ku]_p`, `0<=k<=K`,

and it is available precisely when `[C-k]_p<=p-2`.

For `A!=0`, put `d=min([A]_p,[-A]_p)`; thus `1<=d<=H`. Direct residue arithmetic gives

```
S_k(A) = p-k   if k is even and k<=2d,
                 or k is odd and k<=2(H-d)+1;
         2p-k otherwise.
```

For every `3<=N<=H+2`, at least one of N and N-1 is in its low case. Indeed, simultaneous failure of their respective inequalities would require `N>H+2`. Hence

`min_(0<=k<=N) S_k(A) <= p-N+1`.

This upper bound is attained. If `N=2l` is even, choose `d=l-1`; N is high and N-1 low. If `N=2l+1` is odd, choose `d=H-l+1`; again N is high and N-1 low. These d are in `[1,H]` because `3<=N<=H+2`. No earlier low term is smaller, and every high term exceeds the claimed minimum. For N=1 and N=2 the minima are respectively p-1 and p-2 for every nonzero A.

If `C<=p-2`, available k split into `0<=k<=min(C,K)`, with third-coordinate cost C, and `C+2<=k<=K`, with third-coordinate cost C+p. The missing k=C+1 would require p-1 copies of g and is unavailable.

For C=0, nonzero A has S_0=p and every wrapped candidate costs at least p, so the maximum is p. For C=1,2 the nonwrapped minima just calculated give depth p, and wrapped candidates cannot improve it. For `3<=C<=K`, take N=C; the maximum nonwrapped depth is p+1, while wrapped candidates cost at least p+C>p+1. For `K<C<=p-2`, take N=K; there is no wrapped candidate and the maximum is `C+p-K+1`.

At C=p-1, k=0 is unavailable, and k=1,...,K all have third-coordinate cost C. Removing k=0 changes none of the preceding minima or sharp witnesses: k=1 already has value p-1, below S_0=p. This gives the final endpoint.

The omitted value A=0 cannot increase any upper bound. For `C<=p-2`, k=0 gives depth C. At C=p-1 choose the largest odd k<=K, which is at least K-1; its pair cost is p-k. This finishes the proof.

## 3. A singleton restriction for every overlap layer

Put `m=(3p-1)/2=3H+1`. Suppose `B_K y` has no nonempty zero-sum of length at most m-1, where `y=(A,-A,kappa)` lies in Pi. Then

`1+rho_(B_K)(-y)>=m`.

**Corollary 2.** For `K=c+2`, `1<=c<=H`, the least residue kappa must satisfy

`1 <= kappa <= H+1-c`.

Indeed, if `C=[-kappa]_p<=K`, Theorem 1 bounds the score by p+2<m. Otherwise the score is at most `p+C-K+2`; reaching m requires `C>=H+c`, equivalently the displayed restriction. This includes exclusion of the zero vector.

This is a uniform restriction across all c, not just c=H. It concerns only values in Pi; it does not show that an arbitrary value lies in Pi.

## 4. Sharp classification at maximal overlap

Now let `p=4q+1>=13` be prime. Thus H=2q, m=6q+1, and the top light overlap c=H gives

`B=e1^(4q)e2^(4q)g^(4q-1)s^(2q+2)`.

**Theorem 3 (exact one-value extension classification).** For `y=(A,-A,kappa)` and `1<=t<=p-1`, the sequence `B y^t` has no nonempty zero-sum of length at most m-1 if and only if exactly one of the following applies:

1. `A=0`, `kappa=1`, and `t=1`;
2. `A!=0`, `kappa=1`, and `t*alpha<=q`, where `alpha=min([A]_p,[-A]_p)`.

In particular, every such extension has `t<=q=(p-1)/4`, and this uniform bound is attained by `y=(1,-1,1)`, `t=q`.

### Step 1: The donor's own shortest zero-sum is m

Every coordinate count in B is below p. The four support vectors form a circuit with relation `(-1,-1,2,-2)`. Thus every nonempty zero-sum count vector is the least-residue vector of a scalar n times this relation, and has length `3p-2n`.

For `1<=n<=2q`, its s-count is 2n, so feasibility gives `n<=q+1`. For `2q+1<=n<=4q`, its s-count is `2n-p`, an odd number. The s-cap 2q+2 therefore gives `n<=3q+1`. The g-cap can only remove candidates, not admit larger n. The endpoint n=3q+1 is feasible, with counts

`(q,q,2q+1,2q)` in the order `(e1,e2,s,g)`.

It has length m, and no larger n is feasible. Therefore B's minimum nonempty zero-sum length is exactly m.

### Step 2: Only kappa=1 can occur

Corollary 2 at c=H gives kappa=1 from the presence of just one y. If A=0, then y=g. Two copies of y together with the p-2 copies of g in B give g^p, so t>=2 is forbidden. Adding just one g preserves the scalar upper bound n<=3q+1 from Step 1, and still has no coordinate multiplicity p, so t=1 is allowed.

### Step 3: An explicit first-exit certificate for A nonzero

Put `alpha=min([A]_p,[-A]_p)` and

```
j = 1                       if alpha>q;
    floor(q/alpha)+1         if 1<=alpha<=q.
```

Then `1<=j<=q+1` and `q < j*alpha <= 2q`. In the second case there is no modular wrap; in the first the inequality follows from alpha<=2q. Hence, for `P=[-jA]_p`,

`q+1 <= P <= 3q`.

If j<=t, use j copies of y and the following donor counts:

```
e1: P-(q+1),
e2: (p-P)-(q+1),
s:  2q+2,
g:  2q-j-1.
```

All counts are nonnegative and within B. In particular, `2q-j-1>=q-2>=1` because q>=3. The s-contribution to either first coordinate is q+1 modulo p, so these donor terms sum to `(-jA,jA,-j)=-jy`. Their total length after adjoining y^j is

`j + (2q-1) + (p-j) = 6q = m-1`.

This is an occurrence-valid zero-sum certificate. If `t*alpha>q`, the selected j is at most t, proving necessity.

### Step 4: Sufficiency and sharpness

Suppose `t*alpha<=q`. Then t<=q and, for every `1<=j<=t`, the centered residue of jA is `d=j*alpha<=q`. At target `-jy=(P,-P,p-j)`, the third coordinate is at least `p-q=3q+1>=2q+2`, so all donor s-counts k=0,...,2q+2 are in the nonwrapped range (apart from the irrelevant k=0 omission when j=1).

In the residue formula of Theorem 1, k=2q+1 is low and has pair cost 2q; k=2q+2 is high because d<=q; all earlier k have cost at least 2q. Thus

`rho_B(-jy)=(p-j)+2q=m-j`.

Every zero-sum using j copies of y therefore has length at least m. Every zero-sum entirely inside B has length at least m by Step 1. These exhaust the possibilities, proving sufficiency. Taking alpha=1 and t=q proves sharpness.

## 5. Consequence for the live maximal-pair problem

For a first-corridor rank-two top-overlap row

`V=s^H x^r y^(p-r)`, `r<=H`,

the high-multiplicity value has `p-r>=H+1>q`. Theorem 3 therefore forces

`y_1+y_2 != 0`.

This excludes **every** high-multiplicity value in Pi, without assuming its third coordinate is 1 or 2, without the relation `x=y-delta*s`, and without any case split in r. It strictly strengthens the local one-value obstruction used to handle the parallel standard families.

It does **not** prove that y is forced into Pi. That classification step, or a separate treatment of nonzero first-coordinate sum, is still needed for complete top-overlap closure. Lower overlaps, rank-two type a=1, and the unresolved rank-three edges are not closed here.

## 6. A proved barrier: one-value tests cannot settle lower overlap

**Theorem 4 (capacity lower bound).** Let p be an odd prime, `2<=K<=p-1`, `A!=0`, `y=(A,-A,1)`, and `1<=t<=p-1`. Every nonempty zero-sum in `B_K y^t` has length at least `2p-K`.

For a zero-sum using j copies of y, `1<=j<=t`, and k copies of s, the first two donor counts have sum `S_k([-jA]_p)>=p-k`, by the same residue calculation (valid for all `0<=k<=p-1`). The third-coordinate equation makes `g_count+k+j` a positive multiple of p. The total length is therefore at least `p+(p-k)>=2p-K`.

For a zero-sum using no y, all four counts are below p and the circuit argument applies. If the s-count is z, the zero-sum length is either `3p-z` or `2p-z`, according to which half contains the relation scalar. As z<=K, it is again at least `2p-K`.

Consequently, for `K<=H+1` (equivalently `c<=H-1`), all these extensions are `(m-1)`-short-free, even for t=p-1. For primes `p==3 (mod 4)`, the legitimate top light overlap is already c=H-1, so this obstruction is directly relevant.

This is an infinite family of **partial donor extensions**, not full zero-sum companions V and not counterexamples to the support-seven target. It proves that the enlarged-donor one-value method cannot by itself close lower overlap. More pure-power enumeration cannot change that. Mixed subsequences involving both x and y, or a genuinely additional structural condition, are necessary on this family.

The sharp jump at `p==1 (mod 4)`, from K=H+1 to K=H+2, is explained by `2p-K` crossing from m to m-1. At the latter value Theorem 3 constructs the first forbidden zero-sum and classifies exactly when it occurs.

## 7. Verification and review boundary

Local replay: `python check_a2_shared_donor_plane_rigidity_v1.py` passed with 1,585 exact fiber maxima (39,335 plane points) across all primes 7 through 31; 30,200 one-value extension rows for p=13,17,29; 36,236 capacity-bound rows; and 37,552 explicit certificates at 80 primes through 1009. All three sharp positive/one-extra-copy controls and the resource, rounding, and envelope mutations passed. The default transcript is frozen in the checker and `A2_SHARED_DONOR_PLANE_RIGIDITY_RESULT_V1.json`.

The checker constructs bounded-occurrence minimum-depth tables by ordinary group addition; it does not use the displayed residue formula to build them. It compares Theorem 1 with every plane fiber in its bounded domain, verifies Theorem 3 in both directions, and checks the explicit certificate's group sum, length and each donor capacity. Controls deliberately use too few s-copies, one extra y-copy, and an incorrect first-exit rounding rule.

Three review roles were applied within this single-model analysis, not by separate external experts: additive-combinatorics review of the occurrence partition and theorem scope; modular-arithmetic review of parity, wraps and endpoints; verification review via a separately structured bounded-occurrence DP and mutation controls. External independent review remains outstanding.

Public literature check: Savchev--Chen, *Long zero-free sequences in finite cyclic groups*, arXiv:math/0602568, is a relevant inverse-theory neighbor. No result from it is needed for these elementary proofs, and the search is not a novelty certificate. No priority or journal-readiness assertion is made.
