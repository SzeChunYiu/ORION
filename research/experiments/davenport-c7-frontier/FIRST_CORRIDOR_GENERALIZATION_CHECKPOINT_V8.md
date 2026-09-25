# First-corridor Davenport generalization checkpoint — 2026-09-04 V8

Status: **Paper-2 theorem-development checkpoint after simultaneous-overlap control and rank-three `a>=4` boundary reduction. No `D_3` closure, all-prime `D_k` formula, or novelty/priority claim.**

## 1. Target

For every prime `p>=7`, prove in the first maximal corridor

`C_1(p)=(p+1,(3p-1)/2,3p-2)`

that a maximal pair with support-four maximal atom satisfies

`|supp(UV)|>=7`.

The exact-support-six equality face has only two mechanisms:

1. support-three/rank-two companion sharing one unsaturated value;
2. support-four/rank-three companion sharing both unsaturated values.

## 2. Rank two

The rank-two face is now reduced to the two exceptional light types

`boxed{a in {1,2}.}`

All heavy-share support-three companions are empty. All light types `a>=3` are empty. Types `a=1,2` have overlap layers `c=1,2,3,4` eliminated for every prime `p>=7`, so every remaining rank-two survivor has `c>=5`.

Type `a=2` has exact arithmetic

`c_light=2 floor((p-1)/4)`

and

`lambda_{2,c}(D)-D=2 ceil(max(D-c-2,0)/2)`.

The genuine rank-two residue is therefore the high-overlap arithmetic of types `a=1,2`, not a general support-four classification problem.

## 3. Exact rank-three overlap-plane interface

For

`U=e1^(p-1)e2^(p-1)s^a g^(p-a)`,

`g=s-a^(-1)(e1+e2)`,

the exact `U`-cost of an arbitrary overlap-plane target `C s+D g` is

`nu_a(C,D)=min (z+q+2[a^(-1)(q-D)]_p)`

over

`0<=z<=a`, `0<=q<=p-a`, `z+q==C+D (mod p)`.

For a rank-three companion

`V=s^c g^d x^r y^t`,

a scalar n gives new-value residues `R=[nr]_p`, `T=[nt]_p` and overlap target residues `C=[nc]_p`, `D=[nd]_p`. If

`R<=r`, `T<=t`,

and

`R+T+nu_a(C,D)<=m-1`,

the box is impossible.

This exact certificate removes the geometry of x,y from the first rank-three attack.

## 4. Simultaneous-overlap theorem for `a>=4`

Let `c_light,c_heavy` be the exact first-corridor reuse ceilings. For every canonical type

`a>=4`,

if both overlap directions are available, then

`boxed{c_light+c_heavy<=a-2.}`

The proof uses the exact rotation intervals. Writing

`a u=1+ell p`,

every block of a consecutive integers contains one k for which

`[u k]_p=p-(p-k)/a`.

Such a residue is already in the forbidden top block for `a>=5`; the endpoint `a=4` is handled by its unique borderline congruence.

Therefore every rank-three box of type `a>=4` satisfies

`boxed{c+d<=a-2.}`

and hence

`r+t>=p+2`.

## 5. Exact doubling reduction in rank three

Put

`S=c+d`.

If the smaller new-value multiplicity has

`r>H=(p-1)/2`,

then doubling gives residues

`R=2r-p`, `T=2t-p`.

The pair contains enough literal overlap copies to cancel `2c s+2d g`, and the resulting zero-sum has length exactly

`boxed{p-1.}`

Thus every `a>=4` survivor lies on the thin boundary

`boxed{r=H-k, t=p-S+k, 0<=k<=S-1.}`

The boundary width is at most `S<=a-2`.

## 6. Scalar-three central-boundary theorem

On the thin boundary, scalar three kills every box satisfying

`3k<=H-2`,

`3(S-k)<=2H`,

`2c<=a`,

`2d<=p-a`.

Indeed the new-value residues are

`R=H-3k-1`,

`T=p-3(S-k)`,

and the pair has enough literal overlap terms to cancel `3c s+3d g`. The resulting zero-sum has length exactly

`boxed{m-1.}`

Therefore every remaining `a>=4` rank-three box lies in one of four explicit edge regimes:

1. `3k>H-2`;
2. `3(S-k)>2H`;
3. `2c>a`;
4. `2d>p-a`.

No theorem currently asserts that all four edge regimes are realizable or independent. The next proof target is to remove redundant edge regimes using mixed overlap depth, then close the remaining scalar cases.

## 7. Discovery context, kept non-authoritative

The earlier bounded exact scalar-plane census through prime `79` found no rank-three arithmetic residual of type `a>=4` at all. Its only residual types were `a=2,3`.

A broader coefficient-atom boundary diagnostic after the new doubling reduction shows that scalar three removes more than 99% of tested `a>=4` boundary boxes; the observed residuals fall only into the light-imbalance and right-new-value-edge modes.

These percentages and residual classifications are **discovery only**. The all-prime theorem currently stops at the four explicit edge regimes of Section 6.

## 8. Current theorem gaps

The prime-uniform first-corridor support-seven theorem is now concentrated in:

1. rank-two light type `a=1`, overlap `c>=5`;
2. rank-two light type `a=2`, overlap `c>=5`, including its genuine high-overlap regime;
3. rank-three `a>=4` edge regimes after the V8 boundary reductions;
4. exceptional rank-three types `a=2,3`, to be attacked after the generic `a>=4` mechanism is closed.

Type `a=1` cannot occur in the rank-three support-four equality branch because its heavy overlap value is already saturated in U.

## 9. Paper-2 spine

The paper now has a coherent theorem sequence independent of any final exact Davenport value:

- support-four maximal-atom classification;
- exact depth and antipodal shell;
- simultaneous quotient atomicity;
- exact radial and overlap-plane lifting costs;
- all-type rank-two interior and heavy-share elimination;
- complete light rank-two elimination for `a>=3`;
- simultaneous-overlap sum bound;
- rank-three doubling and central-boundary reductions;
- final exceptional/edge closure.

The desired submission headline remains the prime-uniform first-corridor support-seven theorem.

## Claim ceiling

No line here claims:

- `D_3(C_7^3)` is known;
- the generalized all-prime `D_k` formula is proved;
- all rank-three `a>=4` boxes are yet eliminated;
- novelty or priority is certified.
