# Modular-inverse selector for shared support in maximal corridors — V1

Status: **proved prime-uniform depth filter**. This uses the exact representation-depth formula to decide when the longer companion can reuse either of the two unsaturated support values of a support-four maximal atom. It strengthens the support-six normal form but does not eliminate all equality cases.

## 1. Setup

Let

`U=e1^(p-1)e2^(p-1)e3^a g4^(p-a)`

be a support-four maximal atom over `C_p^3`, with

`g4=e3-a^{-1}(e1+e2)`, `1<=a<=(p-1)/2`.

Write

`u=[a^{-1}]_p in {1,...,p-1}`.

In the prime-uniform maximal corridor `C_j(p)`, let the longer companion have

`|V|=m=p+b`,

where

`b=(p+1)/2-j`, `1<=j<=floor((p+1)/4)`.

The maximal pair `UV` is `(m-1)`-short-zero-free. Hence every term `v|V` satisfies the singleton depth constraint

`rho_U(-v)>=m-1`.

We evaluate this exactly for the two unsaturated actual support values `e3` and `g4`.

## 2. Exact depth of `-e3`

Use the one-parameter depth formula for target

`-e3=(0,0,p-1)`.

The condition

`[p-1-t]_p<=a`

with `0<=t<=p-a` leaves exactly

`t=p-a-1` or `t=p-a`.

At `t=p-a`, the length is `3p-3`.

At `t=p-a-1`, one has

`c1=c2=p-1-u`, `c3=a`,

so the length is

`3p-3-2u`.

Therefore

> `boxed{rho_U(-e3)=3p-3-2u.}`

For `e3` to occur in `V`, singleton compatibility requires

`3p-3-2u >= p+b-1`.

Equivalently,

> **light-share condition**
>
> `boxed{u <= (3p+2j-5)/4.}`

If this inequality fails, the companion contains no copy of the actual value `e3`.

## 3. Exact depth of `-g4`

Now

`-g4=(u,u,p-1)`.

The same two values of `t` are admissible.

At `t=p-a-1`, the length is `3p-3`.

At `t=p-a`,

`c1=c2=u-1`, `c3=a-1`,

and the length is

`p+2u-3`.

Since `u<=p-1`, the latter is always smaller. Thus

> `boxed{rho_U(-g4)=p+2u-3.}`

For `g4` to occur in `V`, singleton compatibility requires

`p+2u-3 >= p+b-1`.

Equivalently,

> **heavy-share condition**
>
> `boxed{u >= (p+5-2j)/4.}`

If this inequality fails, the companion contains no copy of the actual value `g4`.

The special type `a=1` has `g4` multiplicity `p-1` already, so pair p-short-freeness independently sets its companion capacity to zero. The depth condition is consistent with that exclusion.

## 4. Three inverse regimes

Put

`L_j=(p+5-2j)/4`,

`R_j=(3p+2j-5)/4`.

The corridor range always has `L_j<=R_j`. The inverse residue `u` therefore falls into three structural regimes.

### Low inverse: `u<L_j`

The heavy value `g4` is forbidden to the companion. If an exact support-six maximal pair exists, the companion must share `e3` and cannot share both unsaturated values. By the support-six normal form it therefore has support three and rank at most two.

### Middle inverse: `L_j<=u<=R_j`

Both unsaturated actual values pass the singleton depth test. The support-six equality face may use either the support-three rank-two branch or the support-four branch.

### High inverse: `u>R_j`

The light value `e3` is forbidden. Any exact support-six maximal pair must share `g4` only and hence again has support three and rank at most two.

Thus:

> **Inverse-selector theorem.** Outside the middle inverse interval `[L_j,R_j]`, exact support six with a support-four maximal atom is automatically forced into the three-support rank-two companion branch.

This converts the nonlinear support-sharing question into a single modular inverse test on the maximal-atom type.

## 5. First-corridor specialization

For `j=1`,

`L_1=(p+3)/4`,

`R_1=3(p-1)/4`.

Together with the sharp first-corridor plane theorem:

- if `u<L_1`, any exact support-six companion is a rank-two three-support atom sharing only `e3`, and its plane meets `supp(U)` exactly at `e3`;
- if `u>R_1`, it is a rank-two three-support atom sharing only `g4`, and its plane meets `supp(U)` exactly at `g4`;
- only `L_1<=u<=R_1` can contain the rank-three four-support equality branch.

At `p=7` the three canonical support-four types have inverse residues

- `a=1 -> u=1`: light only;
- `a=2 -> u=4`: middle, either allowed;
- `a=3 -> u=5`: heavy only.

This is exactly the structural split to use before any `(8,10,19)` companion enumeration.

## 6. Strategic consequence

The equality face now has two layers of exact preprocessing:

1. support six forces only two new actual values and support three/four for the companion;
2. the inverse residue of the support-four maximal-atom type often decides which shared value is even possible, forcing rank two outside a narrow middle interval.

The remaining rank-two branch is a three-support circuit in a plane with a prescribed single intersection with the maximal-atom support in the first corridor. Its next natural treatment is therefore a one-dimensional kernel/residue analysis rather than a six-point search.

## Verification receipt

`check_support4_shared_value_depth_filter_v1.py` evaluates the exact depth formula at `-e3` and `-g4` and verifies both closed formulas, both corridor threshold equivalences, and the p=7 split for every prime through 401 and every support-four type/corridor index.

The checker is regression only; theorem authority is the calculation above.

## Boundary

- Passing a singleton depth test does not prove that a compatible companion exists.
- The middle inverse interval is not eliminated.
- The theorem assumes a support-four maximal atom.
- No `D_3(C_p^3)` value or novelty/priority claim is made.
