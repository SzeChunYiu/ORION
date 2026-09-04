# First-corridor Davenport generalization checkpoint — 2026-09-04 V7

Status: **Paper-2 theorem-development checkpoint after complete type-three rank-two closure and exact overlap-plane reduction of the rank-three face. No `D_3` closure, all-prime `D_k` formula, or novelty/priority claim.**

## 1. Local theorem target

For every prime `p>=7`, prove in the first maximal corridor

`C_1(p)=(p+1,(3p-1)/2,3p-2)`

that a maximal pair whose maximal atom has support four satisfies

`|supp(UV)|>=7`.

At exact support six, the companion is either

1. support three/rank two, sharing exactly one maximal-atom overlap value; or
2. support four/rank three, sharing both overlap values.

The present checkpoint sharpens both branches.

## 2. Rank-two equality face: current classification

The heavy-share support-three branch is now empty for **every** canonical support-four maximal type.

On the light-share side:

- every type `a>=4` is empty prime-uniformly;
- type `a=3` is now empty prime-uniformly;
- only types `a=1,2` remain.

Thus:

> `boxed{every rank-two support-three equality survivor has light type a in {1,2}.}`

This is a qualitative reduction from an unbounded family of maximal types to two exceptional types.

### Type `a=3` closure

The type-three proof now has a complete architecture:

- exact `a=3` depth/radial formula;
- exact half-overlap bound `c<=floor(H/2)`;
- all interiors removed by the all-type doubling theorem;
- right-half boundary `e<=f` removed by one floor/ceiling scalar;
- left-half boundary `e>f` removed by two explicit scalar regimes depending on `r>=2e-1` or `r<2e-1`.

The complete type-three CI replay is green on the Paper-2 integration branch.

### Types `a=1,2`

Both exceptional lanes already eliminate light overlap multiplicities

`c=1,2,3,4`

for every prime `p>=7`.

Hence any remaining rank-two survivor in either exceptional type has

`c>=5`.

Type `a=2` now additionally has exact closed arithmetic:

`c_light=2 floor((p-1)/4)`,

and

`lambda_{2,c}(D)-D=2 ceil(max(D-c-2,0)/2)`.

This identifies the genuine difficulty: type two can reach high overlap `c=H` when `p==1 (mod 4)`, so the half-overlap scalar method that closes type three cannot simply be copied.

## 3. Exact overlap-plane lifting theorem

For the canonical maximal atom

`U=e1^(p-1)e2^(p-1)s^a g^(p-a)`, `g=s-a^(-1)(e1+e2)`,

the shortest `U`-representation of an arbitrary target

`C s+D g`

in the overlap plane is

`nu_a(C,D)=min (z+q+2[a^(-1)(q-D)]_p)`

over

`0<=z<=a`, `0<=q<=p-a`, `z+q==C+D (mod p)`.

This is exact by saturated-coordinate forcing and requires at most `a+1` trials.

## 4. Rank-three scalar-plane certificate

For a rank-three support-four companion

`V=s^c g^d x^r y^t`,

and nonzero scalar n, put

`C=[nc]_p`, `D=[nd]_p`, `R=[nr]_p`, `T=[nt]_p`.

The new-value subsequence

`x^R y^T`

has sum

`-C s-D g`.

Therefore a rank-three box is impossible whenever

`R<=r`, `T<=t`,

and

`R+T+nu_a(C,D)<=m-1`.

This removes the actual geometry of `x,y` from the first rank-three obstruction test.

## 5. Rank-three discovery frontier

A bounded exact arithmetic scan through prime `79` gives:

- multiplicity boxes after basic support/capacity restrictions: `28135`;
- coefficient-atom boxes: `27104`;
- killed by the exact scalar-plane certificate: `26631`;
- arithmetic residuals: `473`.

The residual types are

- `471` boxes of maximal type `a=2`;
- `2` boxes of maximal type `a=3`;
- `0` boxes of type `a>=4`.

This distribution is **discovery only**. No all-prime rank-three `a>=4` theorem is claimed yet.

The first type-three residual is

`(p,a,c,d,r,t)=(13,3,3,2,2,12)`,

and the second bounded residual occurs at `p=17`.

Type `a=1` has no rank-three support-four equality branch: the `g` value already has multiplicity `p-1` in the maximal atom, so pair `p`-short-freeness forbids the companion from sharing it, while the rank-three support-four normal form requires both overlap values.

## 6. Current theorem gaps

The prime-uniform first-corridor support-seven theorem is now concentrated in three mechanisms:

1. **type `a=1` light-share rank two with `c>=5`;**
2. **type `a=2` light-share rank two with `c>=5`, especially the high-overlap regime;**
3. **rank-three support-four companions,** where the exact scalar-plane certificate should first be promoted to an all-prime `a>=4` elimination and the exceptional `a=2,3` residual boxes then attacked with simultaneous quotient atomicity / mixed depth.

This is substantially narrower than V6: type `a=3` rank two is no longer a gap, and the rank-three search no longer begins with arbitrary new support values.

## 7. Paper-2 architecture

The emerging paper spine is now coherent enough to organize before the final headline theorem:

1. support-four maximal-atom classification;
2. exact representation depth and antipodal shell;
3. simultaneous quotient atomicity;
4. exact light/heavy radial lifting costs;
5. all-type interior elimination and full heavy-share elimination;
6. complete `a>=3` light rank-two elimination;
7. exact overlap-plane lifting and rank-three scalar reduction;
8. final exceptional-type closure.

The desired submission headline remains the prime-uniform first-corridor support-seven theorem. An exact generalized Davenport value would strengthen the paper further but is not required for the structural paper to have an independent identity.

## 8. Next attack

The highest-value next steps are:

- prove symbolically that the rank-three scalar-plane certificate kills every type `a>=4`, matching the bounded zero-residual discovery;
- derive a two-parameter/power-depth normal form for the exceptional `a=2` high-overlap rank-two face, using the exact parity staircase rather than generic radial search;
- retain the `a=1` high-overlap face as a separate symmetric-depth problem rather than mixing it into the type-two arithmetic.

## Claim ceiling

No line here claims:

- `D_3(C_7^3)` is determined;
- the all-prime generalized Davenport formula is proved;
- rank-three `a>=4` is closed beyond bounded discovery;
- novelty or priority is certified by the repository alone.
