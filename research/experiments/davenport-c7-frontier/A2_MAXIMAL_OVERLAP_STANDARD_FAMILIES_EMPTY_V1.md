# Maximal-overlap `a=2` standard power families are empty — V1

Status: **proved prime-uniform elimination of the two standard high-multiplicity families**. In the first maximal corridor for canonical type `a=2`, the exact top light-overlap face occurs only when `p==1 (mod 4)`. If the high-multiplicity new value has saturated-coordinate sum zero and third coordinate `1` or `2`, then an explicit power of the other new value always violates the inherited depth threshold.

The difficult upper-half case is closed by an inverse-quarter rotation selector. This theorem isolates the sole remaining maximal-overlap task: prove that every high-multiplicity value is forced into one of the two standard families, apart from the already finite central exceptions.

It does not by itself close every `a=2` companion or determine a generalized Davenport constant.

## 1. Setup

Let

`p=2H+1>=13` be prime, `p==1 (mod 4)`,

so `H` is even, and put

`m=3H+1=(3p-1)/2`.

In the `(e1,e2,g)` coordinates of `A2_EXACT_DEPTH_FIBER_ENVELOPE_V1.md`,

`s=(u,u,1)`, `u=H+1=2^(-1) mod p`.

The exact light-overlap ceiling for type `a=2` is `c=H`. A boundary companion row has

`V=s^H x^r y^(p-r)`, `1<=r<=H`,

and the atom relation gives

`x=y-delta s`,

where

`delta=H r^(-1) mod p`.

Assume the high-multiplicity value belongs to one of the two standard families

`y=(A,-A,kappa)`, `kappa in {1,2}`.

For a power `x^j`, the target `-jx` has

`w=[j delta]_p`

as the sum of its first two coordinates and

`C=[w-kappa j]_p`

as its third coordinate. Therefore the exact fiber envelope gives

`rho_U(-jx)<=M_p(w,C)`.

It suffices to find `1<=j<=r` such that

`j+M_p(w,C)<m`.

## 2. The family `kappa=1`

### Noncentral rows `r<H`

Take `j=r`. Since `r delta=H`,

`w=H`, `C=H-r`.

Here `1<=C<=H-1`, so the middle-fiber formula gives

`M_p(H,C)=H+C=2H-r`.

Thus

`j+M_p(H,C)=2H=p-1<m`.

### Central row `r=H`

Now `delta=1`. Take `j=1`. Then

`w=1`, `C=0`,

and

`M_p(1,0)=p+1`.

Hence

`1+M_p(1,0)=p+2<m`

because `H>=6`.

Therefore every standard `kappa=1` row is impossible.

## 3. The lower half of `kappa=2`

Assume first `r<H/2` and again take `j=r`. Then

`w=H`, `C=H-2r>=1`.

The middle-fiber formula yields

`j+M_p(H,C)=r+H+(H-2r)=2H-r<m`.

At the exact half `r=H/2`, one has `delta=2`. Take `j=1`. Then

`w=2`, `C=0`,

so

`1+M_p(2,0)=p+3<m`.

Only

`H/2<r<H`

and the central row `r=H` remain.

## 4. Reparameterize the noncentral upper half

Put

`b=p-2r`.

Then `b` is odd and

`3<=b<=H-1`.

Moreover

`r H^(-1)==b (mod p)`,

so

> `boxed{delta^(-1)=b.}`

For any `1<=k<=b-1`, put

`w_k=ceil(kp/b)`, `j_k=b w_k-kp`.

Because `gcd(b,p)=1`,

`1<=j_k<=b-1`

and

`b w_k==j_k (mod p)`.

Thus

`w_k=[j_k delta]_p`.

These are the finite Beatty/rotation points from which the selector is built.

Write

`p=q b+a`, `q=floor(p/b)`, `1<=a<=b-1`.

There are three cases.

## 5. The two `q=2` selectors

### Case 5.1: `q=2`, `b==1 (mod 4)`

Then `a==3 (mod 4)`. Take the half-step

`k=(b+1)/2`.

A direct ceiling calculation gives

`w=H+2`, `j=(b-a)/2`,

and therefore

`C=w-2j=(3a+3)/2>=6`.

This lies in the high-fiber generic range. The exact score has margin

`m-[j+M_p(w,C)]=(3b-5)/2>0`.

Also

`r-j=a>=3`,

so the chosen power is available.

### Case 5.2: `q=2`, `b==3 (mod 4)`

Again `a==3 (mod 4)`. Take the quarter-step

`k=(b+1)/4`.

Then

`w=H/2+1`, `j=(b-a)/4`,

and

`C=(3a+3)/4>=3`.

This is a low fiber, and substitution in the exact envelope gives

`m-[j+M_p(w,C)]=j>0`.

Thus both `q=2` residue classes are eliminated.

## 6. The complemented quarter selector for `q>=3`

Set

`k=ceil(b/4)`,

`w0=ceil(kp/b)`, `j0=b w0-kp`.

Define the complemented point

`boxed{j=b-j0, w=p+1-w0.}`

The congruence calculation

`b w==b-bw0==b-j0==j (mod p)`

shows that

`w=[j delta]_p`.

We verify the three inequalities needed by the depth envelope.

### 6.1 The power is available

Since `j<=b-1`,

`r-j >= ((q-3)b+a+2)/2`.

If `q=3`, then `a` is even and at least two, so the right side is at least two. If `q>=4`, it is at least three. Hence

`boxed{1<=j<=r-2.}`

### 6.2 The selected fiber is high and has positive third coordinate

Put

`epsilon=4k-b in {1,3}`.

Using `w0<=kp/b+1`,

`w=p+1-w0 >= p(1-k/b)`

`=p(3b-epsilon)/(4b)`

`>=3p(b-1)/(4b)>=p/2`.

Since `w` is integral,

`w>=H+1`.

Furthermore, using `j0>=1`,

`C=w-2j`

`=p+1-w0-2b+2j0`

`>=p(1-k/b)-2b+2`

`>9(b-1)/4-2b+2=(b-1)/4>0`,

because `p>3b`.

Also `w0>=4`, so `w<=p-3`; since `j>=1`, one has `C<=p-5`. Thus

`boxed{H+1<=w<=p-3, 1<=C<=p-5.}`

### 6.3 The score fits below `m`

Let

`S=m-(2w-j)`.

A direct rearrangement gives

`S=2w0+j-(p+5)/2`.

Since `w0>=kp/b` and `j>=1`,

`S>=p epsilon/(2b)-3/2>0`,

because `p/b>3` and `epsilon>=1`. As `S` is an integer,

`boxed{S>=1.}`

If `C=1`, then the high-fiber endpoint formula gives

`j+M_p(w,C)=2w-j=m-S<=m-1`.

If `C=2`, the score is `2w-j-1<=m-2`. If `C>=3`, the generic high-fiber formula gives the same bound

`j+M_p(w,C)=2w-j-1<=m-2`.

Therefore every `q>=3` upper-half row is impossible.

## 7. The central `kappa=2` row

Let `r=H`, so `delta=1`. Write

`x=(B,-B-1,1)`

with `B=A-u`, and put

`R=[HB]_p`.

If `1<=R<=H`, take `j=H`. The `k=1` term in the exact depth formula realizes `-Hx` with cost `p-1`, so the score is `m-1`.

If `H+2<=R<=p-1`, the `k=2` term has cost `p-2`, so the score is `m-2`.

The two omitted residues are `R=0,H+1`, corresponding respectively to `B=0,p-1`. In either case take `j=2`. The target is `(0,2,p-2)` or `(2,0,p-2)`, represented with cost exactly `p`; hence the score is `p+2<m`.

Thus the central row is impossible as well.

## 8. Theorem

> **Maximal-overlap standard-family theorem.** Let `p>=13` be prime with `p==1 (mod 4)`. In the first maximal corridor for canonical maximal type `a=2`, no support-three boundary companion with top light overlap `c=H` can have its high-multiplicity value in either standard family
> 
> `boxed{y=(A,-A,1) or y=(A,-A,2).}`

The theorem is uniform in the free parameter `A`.

Consequently the top-overlap lane is reduced to a high-multiplicity classification problem: show that the separate power-depth inequalities force `y` into these two standard families, apart from a bounded central exception set.

## 9. Verification receipt

`check_a2_maximal_overlap_standard_families_v1.py` performs four independent layers:

- exact selector arithmetic for every prime `p==1 (mod 4)` through `1009` and every noncentral upper-half parameter `b`;
- a broader coprime odd-modulus replay for every `p==1 (mod 4)` through `5001`, without assuming primality;
- direct exact-depth evaluation for every standard-family parameter `A`, every boundary row, and every prime through `401`;
- hostile mutations that replace the half-step by the generic complement, use the primary quarter point instead of its complement, or round `b/4` down.

The checker freezes case counts, minimum structural/depth slack, mutation disagreements, and deterministic SHA-256 transcripts.

The executable is regression only. The theorem authority is the exact envelope, the inverse-quarter selector, and the central direct representations above.

## Boundary

- The theorem assumes the standard high-multiplicity forms; their prime-uniform classification remains to be proved.
- It treats only the maximal light-overlap `c=H`, which exists when `p==1 (mod 4)`.
- Lower overlap layers remain outside this statement.
- No generalized Davenport value, all-`k` formula, novelty, or priority claim is made.
