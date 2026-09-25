# The `p=7`, `a=2` rank-three support-four equality face is empty — V1

Status: **exact finite theorem with an explicit exception-and-certificate table**. In the first maximal corridor over `C_7^3`, the only support-six rank-three companion face left by the prime-uniform reductions is impossible. The proof does not rely on the earlier full equality-face search returning a zero count: it reduces the face to six multiplicity rows, classifies the 14 ordered parameter pairs surviving all separate power tests, and gives a concrete mixed zero-sum certificate of length at most eight for every survivor.

Together with the already-proved support-three eliminations, this establishes that a first-corridor maximal pair whose length-19 atom has support four must have total support at least seven.

No exact value of `D_3(C_7^3)`, novelty, or venue authority is claimed here.

## 1. Canonical maximal atom

Work in coordinates over `F_7` with

`e1=(1,0,0)`, `e2=(0,1,0)`, `s=(0,0,1)`.

For maximal type `a=2`, `2^(-1)=4 mod 7`, so put

`g=s-4(e1+e2)=(3,3,1)`.

The canonical length-19 atom is

`U=e1^6 e2^6 s^2 g^5`.

The first maximal corridor is

`(8,10,19)`,

and the length-10 companion `V` must pair with `U` to remain 9-short-zero-free.

Assume the pair has total support exactly six and that `V` lies in the rank-three support-four branch. Then

`V=s^c g^d x^r y^t`,

where `x,y` are genuinely new values and `<s,g,x,y>=C_7^3`.

## 2. The multiplicity face has only six rows

The exact multi-copy criterion gives

`1<=c<=2`, `1<=d<=1`.

Thus `d=1`. Pair 7-short-freeness gives `r,t<=6`, and after ordering the new values we may take `r<=t`. Since

`c+d+r+t=10`,

the complete multiplicity list is

`(c,d,r,t)` in

`{(1,1,2,6),(1,1,3,5),(1,1,4,4),`

`  (2,1,1,6),(2,1,2,5),(2,1,3,4)}`.

Every displayed coefficient vector is primitive in its multiplicity box; no other row satisfies the support-four branch capacities.

## 3. Exact occurrence-level depth

For `z in C_7^3`, let

`rho_U(z)=min{|T|:T|U, sigma(T)=z}`.

The verification program computes this table by a bounded occurrence-level dynamic program over the actual 19 terms of `U`; all `7^3=343` group elements are reached. The result is independently cross-checked against the closed support-four depth formula, but the enumeration below consumes the occurrence table.

For every proper companion subsequence `W|V`, pair short-freeness requires

`|W|+rho_U(-sigma(W))>=10`.

In particular each power of a new value must satisfy

`rho_U(jx)>=j`, `rho_U(-jx)>=10-j`, `1<=j<=r`,

and the analogous inequalities for `y` through multiplicity `t`.

## 4. Exhaustive parameter reduction

Fix one of the six rows. Since the support has rank three, choose `x` outside the plane `<s,g>`. The zero-sum relation

`c s+g+r x+t y=0`

then determines `y` uniquely:

`y=-t^(-1)(c s+g+r x)`.

The exhaustive classification does not quotient by symmetry. It checks all 343 choices of `x`, rejects zero, old-support, repeated-support, and rank-defective cases, and leaves exactly 290 structural candidates in each multiplicity row.

Applying only the separate `x`- and `y`-power inequalities leaves respectively

`2,0,4,4,4,0`

ordered candidates in the six rows, for a total of 14.

Let `iota` exchange the first two coordinates. When `r=t`, also allow exchanging `x` and `y`. The 14 candidates form the following six displayed orbits.

## 5. Explicit mixed certificates

In each line, `W` is a subsequence of `V`, `T` a subsequence of `U`, and

`sigma(WT)=0`, `|WT|<=8<10`.

Thus each line contradicts pair short-freeness. Applying the stated symmetries supplies every ordered candidate in the orbit.

| row `(c,d,r,t)` | representative `(x,y)` | orbit | `W` | `T` | `|WT|` |
|---|---|---:|---|---|---:|
| `(1,1,2,6)` | `((1,2,0),(5,0,2))` | `iota` | `x^2 y^3` | `e1 g` | 7 |
| `(1,1,4,4)` | `((0,4,1),(1,4,2))` | `iota`, `x<->y` | `x y` | `s^2 g^2` | 6 |
| `(2,1,1,6)` | `((1,5,6),(4,1,2))` | `iota` | `x y^3` | `e1^2 g^2` | 8 |
| `(2,1,1,6)` | `((2,5,5),(5,1,1))` | `iota` | `x y` | `e2 s` | 4 |
| `(2,1,2,5)` | `((0,2,4),(5,0,2))` | `iota` | `x^2 y^2` | `e1 s g` | 7 |
| `(2,1,2,5)` | `((4,6,3),(2,4,1))` | `iota` | `x y^2` | `e2 g^2` | 6 |

For example, in the first line

`sigma(x^2y^3)=(3,4,6)`

and

`sigma(e1g)=(4,3,1)`,

so their sum is zero modulo seven. The checker verifies the corresponding identity and all resource capacities separately for every one of the 14 ordered entries, not merely for the orbit representatives.

The two rows with zero power survivors require no mixed table entry.

## 6. Theorem and corridor consequence

> **Rank-three equality-face theorem at `p=7`.** No length-10 atom `V` can form an exact-support-six first-corridor maximal pair with the canonical type-`a=2` support-four length-19 atom `U` in the rank-three support-four branch.

The other canonical support-four types cannot enter this branch at `p=7`:

- type `a=1` has zero heavy overlap capacity;
- type `a=3` has zero light overlap capacity.

The support-three rank-two branch is already empty for all three types: the `a=1` overlap ceiling is four and its layers `c=1,2,3,4` are proved impossible; type `a=2` has overlap ceiling two and its layers are proved impossible; type `a=3` is completely closed.

Therefore:

> **C7 support-seven corollary.** If a first-corridor `(10,19)` maximal pair over `C_7^3` contains a support-four length-19 atom, then
> 
> `boxed{|supp(UV)|>=7.}`

This is a theorem about the maximal pair before the length-8 third atom is introduced.

## 7. Verification receipt

`check_p7_a2_rank3_support4_exception_table_v1.py` freezes:

- all six primitive multiplicity rows;
- 290 structural candidates per row;
- power-survivor counts `(2,0,4,4,4,0)`;
- the exact 14 ordered `(row,x,y)` entries;
- a deterministic transcript digest over all 1740 structural candidates;
- all 14 explicit `W,T` resource identities and their lengths;
- a hostile control showing that power tests alone leave exactly 14 unresolved candidates;
- a mutation control showing that deleting any one certificate leaves an unresolved entry.

The depth table is built from occurrences, while the certificate verification uses direct vector sums. The earlier all-face C++ sweep is not imported as an oracle.

## Boundary

- This theorem is specific to `p=7`, the first maximal corridor, a support-four maximal atom, and exact total support six.
- It does not close maximal atoms of support at least five.
- It does not close the unresolved support-eight Type-A length-37 face.
- It does not establish `D_3(C_7^3)=36`.
