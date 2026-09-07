# First-corridor `a=1` one-share support-three face is impossible — V1

Status: **proved prime-uniform branch elimination for `p>=7`**. This closes the exact-support-six `a=1` rank-two subfamily in which the companion reuses the light maximal-atom value exactly once. It does not close the whole `a=1` face and does not determine a generalized Davenport constant by itself.

## 1. Setup and saturated coordinates

Let `p>=7` be prime and consider the first maximal corridor

`C_1(p)=(p+1,(3p-1)/2,3p-2)`.

For the support-four maximal atom of type `a=1`, change basis to the three saturated directions

`f1=e1`, `f2=e2`, `f3=g4`.

Then, with

`s=e3=f1+f2+f3`,

we have

`U=f1^(p-1) f2^(p-1) f3^(p-1) s`.

Write a vector `z` in this basis as `(z1,z2,z3)` with least residues in `{0,...,p-1}`, and put

`S(z)=[z1]_p+[z2]_p+[z3]_p`.

The support-four depth formula becomes

`rho_U(z)=min(S(z),1+sum_i [z_i-1]_p)`.

If no coordinate of `z` is zero, the second term is `S(z)-2`. If exactly `k>=1` coordinates are zero, the second term is `S(z)-2+kp>=S(z)`. Hence the exact collapse

`boxed{rho_U(z)=S(z)-2 if z1 z2 z3 !=0, and rho_U(z)=S(z) otherwise.}`

Now assume an exact-support-six first-corridor pair in the support-three branch shares `s` exactly once:

`V=s x^r y^t`,

with `r<=t`, two genuinely new values `x,y`, and

`m=|V|=(3p-1)/2`.

The first-corridor plane theorem gives

`span(V) cap supp(U)={s}`,

so the companion plane contains none of the saturated axes `<f1>,<f2>,<f3>`.

The pair is `(m-1)`-short-zero-free.

## 2. Pair short-freeness in depth form

For every nonempty proper subsequence `Y|V`, complementing inside the atom `V` gives the equivalent inequality

`rho_U(sigma(Y))>=|Y|`.

Applying the original pair inequality to the same subsequence also gives

`rho_U(-sigma(Y))>=m-|Y|`.

We use both sides below.

## 3. The multiplicity split

Since the shared multiplicity is one,

`r+t=m-1=3(p-1)/2`.

Every actual value occurs at most `p-1` times in the `p`-short-free pair, hence `t<=p-1`. Therefore

`r>= (p-1)/2`.

Put `q=(p-1)/2`. There are exactly two cases.

### Interior: `r,t>=q+1`

The atom relation is

`s+r x+t y=0`.

Doubling gives

`2s+[2r]_p x+[2t]_p y=0`.

Because `r,t>p/2`,

`[2r]_p=2r-p<=r`, `[2t]_p=2t-p<=t`.

The pair `UV` contains two copies of `s`, one from `U` and one from `V`, so this is an actual mixed zero-sum subsequence. Its length is

`2+(2r-p)+(2t-p)=p-1<m`,

contradicting short-freeness.

Thus only the boundary can remain:

`boxed{r=q, t=p-1.}`

## 4. Boundary relation

At the boundary the atom relation is

`s+q x+(p-1)y=0`.

Since `q=-2^(-1)` in `F_p`,

`y=s-2^(-1)x`, equivalently `boxed{x=2(s-y).}`

The value `y` occurs `p-1` times. Hence for every `1<=j<=p-1`, applying the two depth inequalities to `Y=y^j` gives

`rho_U(jy)>=j`,

`rho_U(-jy)>=m-j`.

We first classify the possible saturated-coordinate residue pattern of such a value `y`.

## 5. Radial rigidity lemma

> **Lemma.** Let `p>=7` be prime and let `y` lie in the companion plane, which contains no saturated axis. If
>
> `rho_U(jy)>=j` and `rho_U(-jy)>=m-j`
>
> for every `1<=j<=p-1`, then, after permuting the saturated coordinates,
>
> `boxed{y=(1,a,p-a)}`
>
> for some `1<=a<=p-1`.

### Step 1: no coordinate of `y` is zero

The plane condition excludes two zero coordinates, because that would put `y` on a saturated axis. Suppose exactly one coordinate is zero. Let `R_j` be the sum of the two nonzero residues of `jy`. Then the depth collapse gives

`j<=R_j<=j+(p+1)/2`.

Applying the same upper bound to `(p-j)y=-jy` yields the sharper lower bound

`(p-1)/2+j<=R_j`.

Therefore

`R_j-j in {(p-1)/2,(p+1)/2}`

for every `j`.

But modulo `p`,

`R_j-j == j(T-1)`,

where `T` is the sum of the two nonzero coordinates of `y`. If `T!=1 mod p`, the right side runs through every nonzero residue as `j=1,...,p-1`, impossible for a two-element residue set. If `T=1 mod p`, the right side is always zero, also impossible because neither displayed value is zero modulo `p`. Hence all three coordinates of `y` are nonzero.

### Step 2: exact residue-sum identity

Let

`S_j=sum_i [j y_i]_p`.

Now the depth collapse gives

`j+2<=S_j<=j+3(p-1)/2`.

Applying the upper bound to `(p-j)y=-jy` sharpens the lower side to

`j+(p+3)/2<=S_j`.

Thus

`d_j=S_j-j`

lies in the integer interval

`[(p+3)/2, 3(p-1)/2]`,

which has width `p-3<p` and contains exactly `p-2` integers.

Modulo `p`,

`d_j == j(T-1)`,

where now `T=y1+y2+y3`. If `T!=1 mod p`, these residues run through all `p-1` nonzero classes, impossible inside an interval of width less than `p` containing only `p-2` representatives. Hence `T=1 mod p`.

The interval contains exactly one multiple of `p`, namely `p`, so

`boxed{S_j=p+j}`

for every `1<=j<=p-1`. In particular `y1+y2+y3=p+1` as ordinary integers.

### Step 3: second-moment jump-set obstruction

Write the three positive residues as `a,b,c`, so

`a+b+c=p+1`,

and from `S_j=p+j`,

`floor(ja/p)+floor(jb/p)+floor(jc/p)=j-1`

for every `1<=j<=p-1`.

At `j=2`, exactly one of `a,b,c` exceeds `p/2`; relabel so `c>p/2`. Put

`d=p-c=a+b-1`,

so `1<=d<p/2`.

Because `jd/p` is never integral for `1<=j<=p-1`,

`floor(jc/p)=j-1-floor(jd/p)`.

Therefore

`floor(ja/p)+floor(jb/p)=floor(jd/p)`

for every `j`.

Take first differences in `j`. For `1<=w<p`, let

`J_w={j: floor(jw/p)-floor((j-1)w/p)=1}`.

Then

`J_a disjoint-union J_b = J_d`.

Moreover

`J_w=w^(-1){1,...,w-1}`

inside `F_p`, because a floor jump occurs exactly when `[jw]_p<w`.

Multiplying the set identity by `d` gives

`d a^(-1){1,...,a-1} disjoint-union d b^(-1){1,...,b-1}={1,...,d-1}`.

Take sums of squares modulo `p`. Using

`sum_{k=1}^{n-1} k^2=n(n-1)(2n-1)/6`

and substituting `d=a+b-1`, the difference between the two sides simplifies to

`- d(a-1)(a+b)(b-1)/(6ab) ==0 mod p`.

Here `p>=7`, `a,b,d` are nonzero modulo `p`, and `a+b=d+1<p`. Hence if both `a,b>1`, every factor is nonzero modulo `p`, contradiction. Thus one of `a,b` equals one.

Since `a+b+c=p+1`, after a coordinate permutation

`y=(1,a,p-a)`.

This proves the lemma.

## 6. The rigid boundary still fails

By the lemma, permute coordinates so

`y=(1,a,p-a)`.

Then

`x=2(s-y)`.

If `a=1` or `a=p-1`, the vector `x` lies on a saturated coordinate axis, contradicting the first-corridor plane condition.

Otherwise swap the last two coordinates if necessary and assume

`2<=a<=q`.

If `a<q`, then

`x=(0,p+2-2a,2a+2)`,

whose two nonzero residues sum to `p+4`. Hence

`rho_U(-x)=2p-(p+4)=p-4`.

But the pair inequality for the singleton `x` requires

`rho_U(-x)>=m-1=(3p-3)/2`,

impossible.

It remains only `a=q`. Then

`x=(0,3,1)`

up to swapping the last two coordinates.

Choose

`j0=ceil((q+2)/3)=ceil((p+3)/6)`.

For every `p>=7`,

`1<=j0<=q`, `3j0>=q+2`, and `3j0<p`.

Thus

`j0 x=(0,3j0,j0)`

without wrap in the second coordinate, and

`rho_U(-j0 x)=2p-4j0`.

The pair inequality for `x^j0` would require

`2p-4j0>=m-j0`,

equivalently

`3j0<=2p-m=(p+1)/2=q+1`,

contradicting `3j0>=q+2`.

Therefore the boundary is impossible.

## 7. Theorem

> **Theorem.** For every prime `p>=7`, an exact-support-six first-corridor maximal pair with support-four maximal atom of type `a=1` cannot have a support-three rank-two companion that reuses the light value `e3` exactly once.
>
> Equivalently, every hypothetical `a=1` support-three equality companion must satisfy
>
> `boxed{v_e3(V)>=2.}`

This is a symbolic all-prime branch elimination. It uses the exact depth formula, the first-corridor plane condition, a second-moment jump-set argument, and no finite classification theorem.

## Verification receipt

`check_a1_light_support3_one_share_elimination_v1.py` performs two controls:

- exhaustive finite verification through prime `101` that the radial residue identity admits only sorted patterns `(1,a,p-a)`;
- arithmetic regression through prime `1009` for the interior doubling and terminal `(0,3,1)` contradiction.

The checker is regression only. The theorem authority is the proof above.

## Boundary

- This does **not** eliminate the `a=1` support-three face with shared multiplicity at least two.
- It does not eliminate the `a=2` light-share support-three face.
- It does not eliminate rank-three four-support companions.
- It assumes the support-four maximal-atom normal form and the first maximal corridor.
- No `D_3(C_p^3)` value, all-`k` formula, or novelty/priority claim is made.
