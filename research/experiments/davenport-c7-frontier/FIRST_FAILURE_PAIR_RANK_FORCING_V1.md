# Pair-product short-free depth, plane caps, and rank forcing in first failures — V1

Status: **proved prime-uniform factorization/rank reduction with donor rank-two inputs and independent arithmetic checks**. No new value of `D_k(C_p^3)` is asserted here.

Let `p>=5` be prime, `G=C_p^3`, and let

`B=U_1...U_m`

be a maximum-length atomic factorization of a first failure with overshoot `q>=1`:

`z(B)=m`, `|B|=pm+M_p+q`, `M_p=(5p-5)/2`.

Write

`e_i=|U_i|-p`.

By hereditary first-failure rigidity, every proper atom subproduct has exactly the displayed packing number. In particular

`z(U_iU_j)=2`

for every distinct pair `i,j`.

## 1. Pair-product short-free depth

Fix distinct atoms `U=U_i`, `V=U_j`, put

`E=e_i+e_j`,

and let `P=UV`. Then

`|P|=2p+E`, `sigma(P)=0`, `z(P)=2`.

Since `P|B`, the global first-failure theorem already makes `P` zero-sum-free through length

`p+q-1`.

There is a second, pair-specific threshold.

> **Pair-complement lemma.** `P` contains no nonempty zero-sum subsequence of length at most
>
> `E-p+1`
>
> whenever this number is positive.

Indeed, if `T|P` were zero-sum with

`|T|<=E-p+1`,

then its zero-sum complement would have length

`|PT^(-1)| >= 2p+E-(E-p+1)=3p-1=D(C_p^3)+1`.

A zero-sum sequence of length at least `D(G)+1` contains a proper nonempty zero-sum subsequence, so the complement splits into at least two nonempty zero-sum blocks. Together with `T` this gives a three-factorization of `P`, contradicting `z(P)=2`.

Therefore every atom pair is zero-sum-free through

> `H_ij=max(p+q-1, e_i+e_j-p+1)`.

The hereditary excess bound `e_i+e_j<=M_p` and `q<=(p-1)/2` ensure

`p<=H_ij<=2p-1`,

so the complete rank-two restricted-sum spectrum applies.

## 2. Pair-specific rank-two plane cap

Let `K<G` be any subgroup of rank at most two. The intersection subsequence

`P_K`

is also `H_ij`-short-zero-free. For `C_p^2`, the exact rank-two formula

`s_{<=h}(C_p^2)=4p-2-h`, `p<=h<=2p-1`,

therefore gives

> **Pair-plane cap**
>
> `|P_K| <= 4p-3-H_ij`.

This can be strictly stronger than the ambient first-failure plane cap because `H_ij` grows with the sum of the two atom excesses.

For a maximal p=7 atom paired with the short atom in the two hard length-19 corridors:

- `(19,10)`: `E=12+3=15`, `H=9`, hence every plane contains at most `16` terms of the 29-term pair product;
- `(19,9)`: `E=12+2=14`, `H=8`, hence every plane contains at most `17` terms of the 28-term pair product.

The ambient q=1 plane cap is only 18.

## 3. A zero-sum rank-two pair cannot attain the ambient extremal length

Suppose now that the entire pair product `P` has rank at most two. It is a zero-sum sequence over `C_p^2` and is short-zero-free through `p+q-1`.

The unrestricted rank-two threshold gives

`|P|<=3p-q-2`.

We show equality is impossible for a **zero-sum** sequence.

### q>=2

Set `k=p-q`. In the first-failure range,

`2<=k<=p-2`.

Ebert--Grynkiewicz prove that every extremal sequence of length

`3p-q-2=2p-2+k`

with no zero-sum of length at most

`p+q-1=2p-1-k`

has, after a basis choice, the form

`e_1^(p-1) e_2^(p-1) (e_1+e_2)^(p-q)`.

Its total sum is

`-(q+1)(e_1+e_2)`,

which is nonzero because `1<=q+1<p`. Hence an extremal sequence cannot be total-zero.

### q=1

Here equality would mean a total-zero, p-short-zero-free sequence of length `3p-3` over `C_p^2`.

Gao--Geroldinger--Schmid prove that every sequence of length `3p-3` with no short zero-sum contains a minimal zero-sum subsequence of length `2p-1`. Since the whole sequence is zero-sum, its complement has length `p-2` and is also zero-sum, contradicting p-short-freeness.

Thus in all cases

> **Zero-sum rank-two cap**
>
> `|P| <= 3p-q-3`.

Since `|P|=2p+e_i+e_j`, this is equivalent to

> `e_i+e_j <= p-q-3`
>
> whenever `rank <U_iU_j> <=2`.

Contrapositively:

> **Atom-pair rank forcing**
>
> `e_i+e_j > p-q-3  =>  <supp(U_iU_j)>=C_p^3`.

So the excess signature directly forces pairwise rank three.

## 4. Uniform high-overshoot consequence

Every atom excess satisfies `e_i>=q`, hence every pair satisfies

`e_i+e_j>=2q`.

Therefore, if

`3q>p-3`,

then

`2q>p-q-3`

and **every pair of atoms in every maximum first-failure factorization spans rank three**.

For p=7 this holds for both `q=2` and `q=3`. Thus every atom pair in every p=7 first failure with overshoot at least two is rank three before any projective-support enumeration.

## 5. Exact p=7 length-37 consequence

The length-37 frontier has `(p,q)=(7,1)`, so a rank-two atom pair would require

`e_i+e_j<=7-1-3=3`.

The six exact atom corridors have excess triples

- `(8,10,19)` -> `(1,3,12)`;
- `(9,9,19)` -> `(2,2,12)`;
- `(9,10,18)` -> `(2,3,11)`;
- `(9,11,17)` -> `(2,4,10)`;
- `(9,12,16)` -> `(2,5,9)`;
- `(10,10,17)` -> `(3,3,10)`.

Every pair sum is at least four. Hence:

> **Every pair of atoms in every one of the six p=7 length-37 corridors spans all of `C_7^3`.**

This includes the short-short pair in the two maximal-atom corridors, not only the pair containing the 19-atom.

## 6. Strategic use

The factorization signature now controls geometry at two scales.

1. **Whole first-failure geometry:** the overshoot `q` determines the ambient plane cap and projective deficit rules.
2. **Pair geometry:** the excess sum `e_i+e_j` determines an atom-pair short-free depth `H_ij`, a sharper pair-plane cap, and often forces that pair to span rank three.

This is a useful interface for Graver augmentation: a proposed refactor may be searched pairwise inside a rank-three subsystem whose plane concentrations are bounded explicitly by the two atom excesses.

For the hard p=7 maximal-atom corridors, the next attack can use simultaneously:

- maximal-atom projective separation;
- one- and two-term U-subsums avoiding the short atom;
- pair-plane caps 16 and 17;
- rank three of both the maximal-short pair and the short-short pair;
- the scalar line-fiber restrictions already frozen in the branch.

## Donor attribution

- John J. Ebert and David J. Grynkiewicz, *Structure of a sequence with prescribed zero-sum subsequences: Rank two p-groups*, European Journal of Combinatorics 118 (2024), 103888, DOI `10.1016/j.ejc.2023.103888`.
- W. Gao, A. Geroldinger and W. A. Schmid, *Inverse zero-sum problems*, Acta Arithmetica 128 (2007), 245--279, DOI `10.4064/aa128-3-5`.
- The exact rank-two restricted-sum formula is donor-owned classical structure recalled in Ebert--Grynkiewicz.

## Boundary

- Pairwise rank three does not by itself force a positive-gain refactor.
- The pair-plane cap applies to the pair product intersection with a fixed rank-two subgroup; it is not an ambient support bound for the third atom.
- No exact generalized Davenport value is claimed here.
