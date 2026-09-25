# Exact `a=2` light-overlap ceiling and radial staircase — V1

Status: **proved prime-uniform arithmetic theorem**. For canonical support-four maximal type `a=2`, the first-corridor light-overlap ceiling and every light-direction radial lifting cost admit closed formulas. This is the `a=2` arithmetic base for the remaining high-overlap rank-two problem.

No support-seven theorem, generalized Davenport value, or novelty/priority claim is made here.

## 1. Setup

Let

`p=2H+1>=7`

be prime and use the canonical support-four maximal atom of type `a=2`

`U=e1^(p-1)e2^(p-1)s^2 g^(p-2)`,

where

`g=s-u(e1+e2)`, `u=2^(-1)=(p+1)/2` in `F_p`.

In the first maximal corridor the longer companion has length

`m=3H+1`.

If it reuses the light value `s` exactly `c` times, the pair contains radial resources

`e1^(p-1)e2^(p-1)s^(c+2)g^(p-2)`.

Let `lambda_{2,c}(D)` be the minimum number of these terms summing to `D s`.

## 2. Exact light-overlap ceiling

The general multi-copy sharing theorem says that light reuse through multiplicity `c` is possible only while

`[u k]_p<=p-h`

for every integer

`k=2,3,...,2+c`,

where

`h=ceil(H/2)`.

For even `k=2q`,

`[u k]_p=q`.

For odd `k=2q+1` in the relevant interval,

`[u k]_p=H+1+q`.

Every even residue automatically lies below `p-h`. The odd condition is

`H+1+q<=2H+1-h`,

or

`q<=H-h=floor(H/2)`.

Thus the first forbidden odd integer is

`2 floor(H/2)+3`.

Since the tested interval ends at `2+c`, the exact reusable light multiplicity is

> `boxed{c_light=2 floor(H/2)=2 floor((p-1)/4).}`

Equivalently,

- if `p==1 (mod 4)`, then `c_light=H`;
- if `p==3 (mod 4)`, then `c_light=H-1`.

This explains why type `a=2` has a genuinely high-overlap regime: unlike `a=3`, the overlap may reach half the group order minus one term.

## 3. Exact radial staircase

The general exact light-radial theorem gives

`lambda_{2,c}(D)`

as the minimum of

`z+q+2[uq]_p`

over

`0<=q<=p-2`, `0<=z<=c+2`, `z+q==D (mod p)`.

Put

`L=max(D-c-2,0)`.

Let

`q0=2 ceil(L/2)`,

the smallest even integer at least `L`.

Then `q0<=D`, `q0<=p-2`, and

`z0=D-q0`

satisfies `0<=z0<=c+2`. Because `q0` is even,

`[u q0]_p=q0/2`,

so this representation has length

`D+q0`.

We now show it is optimal.

### Even q, no wrap

If `q` is even and `z+q=D`, then

`2[uq]_p=q`

and the cost is

`D+q`.

Feasibility requires `q>=L`, so the smallest possible even q is exactly `q0`.

### Odd q

If `q` is odd, then

`[u q]_p=(p+q)/2`,

hence

`2[uq]_p=p+q`.

With no wrap the cost is

`D+p+q`,

and with one wrap it is even larger. Both exceed the feasible even-q cost `D+q0`.

### Even q with wrap

If `z+q=D+p`, an even q has cost

`D+p+q`,

again larger than `D+q0`.

Therefore:

> **Exact `a=2` radial staircase.** For every `1<=D<=p-1`,
>
> `boxed{lambda_{2,c}(D)=D+2 ceil(max(D-c-2,0)/2).}`

Equivalently, the radial surcharge is the smallest even integer not below `D-c-2`:

`boxed{lambda_{2,c}(D)-D=2 ceil(max(D-c-2,0)/2).}`

In particular the whole literal range

`D<=c+2`

has zero surcharge.

## 4. Exact boundary-certificate interface

For a light-share support-three boundary relation

`c s+r x+t y=0`,

let a scalar multiplier n produce least residues

`D=[nc]_p`, `A=[nr]_p`, `B=[nt]_p`.

Whenever

`A<=r`, `B<=t`,

the exact lifted zero-sum length is at most

`D+A+B+2 ceil(max(D-c-2,0)/2)`.

Thus the row is impossible as soon as

> `boxed{D+A+B+2 ceil(max(D-c-2,0)/2)<=3H.}`

This is an exact arithmetic discriminator; no radial dynamic program remains in the `a=2` boundary problem.

## 5. Strategic consequence

The remaining type-two rank-two problem has a different shape from type three:

- the radial cost is simpler than for `a=3`;
- but the overlap can be much larger, reaching `c=H` when `p==1 (mod 4)`;
- the high-overlap rows are therefore not covered by the `H>=2c` constructions that closed `a=3`.

The correct next split is between

1. **moderate overlap**, where one scalar certificate can still exploit a positive `H-2c` margin; and
2. **high overlap**, where the multiplicity relation itself becomes nearly symmetric and should be attacked through the two-parameter plane/depth normal form rather than by copying the `a=3` scalar argument.

## Verification receipt

`check_a2_exact_overlap_and_radial_staircase_v1.py` compares the closed radial formula with the general one-dimensional exact radial oracle for every prime through `401`, every allowed light overlap, and every target `D`. It also verifies the exact overlap ceiling through prime `1009` directly from the multi-copy interval criterion.

The checker is regression only; theorem authority is the parity proof above.

## Boundary

- The theorem does not eliminate the remaining `a=2` boundary rows by itself.
- The already proved `c=1,2,3,4` eliminations remain valid and independent.
- Rank-three support-four companions are separate.
- No `D_3(C_p^3)` value or all-k formula is claimed.
