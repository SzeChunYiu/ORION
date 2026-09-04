# Exact `a=2` light radial excess — V1

Status: **proved prime-uniform exact formula**. For the canonical support-four maximal type `a=2`, the exact shortest realization of every multiple of the shared light value is a parity staircase. This removes the remaining radial minimization from the `a=2` support-three lane. It is a radial theorem only; it does not by itself eliminate the companion geometry or determine a generalized Davenport constant.

## 1. Setup

Let `p>=5` be an odd prime and put

`u=2^(-1) mod p=(p+1)/2`.

For the canonical type `a=2`, write

`U=e1^(p-1)e2^(p-1)s^2 g^(p-2)`,

where

`g=s-u(e1+e2)`.

Suppose a compatible companion contributes `c>=0` additional copies of the light value `s`. The available radial resources are therefore

`e1^(p-1)e2^(p-1)s^(c+2)g^(p-2)`.

For `0<=D<=p-1`, let `lambda_{2,c}(D)` be the minimum number of terms in a subsequence of these resources whose sum is `D s`.

The general exact radial theorem gives

`lambda_{2,c}(D)=min (z+q+2[uq]_p)`

over

`0<=z<=c+2`, `0<=q<=p-2`, `z+q==D (mod p)`.

Throughout the pair-capacity range one has `c<=p-3`, so `z+q<2p` and the congruence has only the nonwrapped value `D` or the wrapped value `D+p`.

## 2. Wrapped representations are never optimal

Any wrapped representation has

`z+q=D+p`,

so its term count is at least `D+p`.

Set

`L=max(D-c-2,0)`

and let `q0` be the first even integer at or above `L`:

`q0=2 ceil(L/2)`.

If `L=0`, then `q0=0`. If `L>0`, then

`q0<=L+1=D-c-1<=D`.

Also `q0<=p-2` throughout `0<=D<=p-1`, `0<=c<=p-3`. Hence

`z0=D-q0`

satisfies `0<=z0<=c+2`, and `(z0,q0)` is a nonwrapped admissible representation.

Its cost will be `D+q0<=D+p-2`, strictly below every wrapped cost. Thus every minimizer is nonwrapped:

`boxed{z+q=D.}`

## 3. The inverse-of-two parity split

Write `p=2H+1`, so `u=H+1`.

For an even number of `g` terms, `q=2j` with `0<=j<=H-1`,

`[u q]_p=[(H+1)2j]_p=j`.

Therefore every admissible even `q` has cost

`z+q+2[uq]_p=D+q`.

For an odd number, `q=2j+1` with `0<=j<=H-1`,

`[u q]_p=H+1+j`.

No wrap occurs in this range, and the cost is

`z+q+2[uq]_p`

`=D+2(H+1+j)`

`=D+p+q`.

Thus every nonwrapped odd representation costs more than `D+p`, while the admissible even representation from Section 2 costs less than `D+p`. Odd `q` is never optimal.

Among admissible even values, the cost `D+q` is increasing in `q`. The smallest admissible value is exactly `q0`.

## 4. Exact formula

Combining the preceding sections gives:

> **Exact `a=2` radial-excess theorem.** For every odd prime `p>=5`, every `0<=c<=p-3`, and every `0<=D<=p-1`,
> 
> `boxed{lambda_{2,c}(D)=D+2 ceil(max(D-c-2,0)/2).}`

Equivalently,

`boxed{lambda_{2,c}(D)-D=2 ceil(max(D-c-2,0)/2).}`

The excess is the smallest even integer not below `max(D-c-2,0)`.

In particular:

- `lambda_{2,c}(D)=D` for `0<=D<=c+2`;
- the excess staircase thereafter is `2,2,4,4,6,6,...`;
- every optimizer uses an even number of `g` terms;
- the first optimal resource pair is

`q=2 ceil(max(D-c-2,0)/2)`, `z=D-q`.

## 5. Consequences for the first corridor

In the first maximal corridor the exact light-overlap ceiling is

`c<=2 floor((p-1)/4)`.

Every scalar-multiplier certificate in the `a=2` light-share support-three face can now be checked without any minimization: once the light residue `D` is known, its exact radial surcharge is the displayed parity staircase.

At the doubled target `D=2c`, the formula recovers the previously proved costs:

- `c=1`: `lambda_{2,1}(2)=2`;
- even `c>=2`: `lambda_{2,c}(2c)=3c-2`;
- odd `c>=3`: `lambda_{2,c}(2c)=3c-1`.

So the radial synthesis used in the interior theorem is not merely feasible; it is optimal.

## Verification receipt

`check_a2_exact_radial_excess_v1.py` compares the closed formula with the general exact radial oracle for every prime through `101`, every full capacity value `0<=c<=p-3`, and every target `0<=D<=p-1`. It separately verifies all symbolic feasibility and parity identities through prime `1009`, freezes the optimizer census and a deterministic SHA-256 transcript, and includes a floor-staircase mutation that must disagree.

The checker is regression only. The theorem authority is the wrapped-cost and parity proof above.

## Boundary

- This theorem computes radial lifting cost only.
- It does not establish a compatible scalar multiplier or a forbidden mixed subsequence.
- It does not close the surviving `a=2` boundary geometry.
- No `D_3(C_p^3)` value, all-`k` formula, novelty, or priority claim is made.
