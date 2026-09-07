# First-corridor Davenport generalization checkpoint — 2026-09-04 V1

Status: **live theorem-development checkpoint; no novelty authority and no `D_3` closure claim**.

## 1. Prime-uniform critical corridor

For prime `p>=5`, a critical `k=3` obstruction containing a maximal atom of length `3p-2` has one of

`C_j(p)=(p+j, p+(p+1)/2-j, 3p-2)`, `1<=j<=floor((p+1)/4)`.

For the maximal pair `P=UV` using the longer companion, hereditary factorization rigidity gives `z(P)=2` and pair short-free depth equal to one less than the companion length.

The all-corridor scalar-complement theorem now gives

`|supp(P)|>=6`

for every corridor index `j`.

## 2. Support-four maximal atom reduction

If the maximal atom has support four, then, up to automorphism,

`U=e1^(p-1)e2^(p-1)e3^a g4^(p-a)`,

`g4=e3-a^{-1}(e1+e2)`, `1<=a<=(p-1)/2`.

At exact pair support six the longer companion has exactly two genuinely new actual values. It has either

- support three and rank two, sharing exactly one unsaturated maximal-atom value; or
- support four and rank three, sharing both unsaturated values.

It cannot use the two saturated actual values `e1,e2`.

## 3. Exact depth formulation

For `x in C_p^3`, let

`rho_U(x)=min{|T|:T|U, sigma(T)=x}`.

The support-four circuit gives a closed one-parameter formula for `rho_U`. Pair short-freeness is equivalent to the graded condition

`|W|+rho_U(-sigma(W)) >= |V|`

for every nonempty proper `W|V`.

This replaces maximal-atom subset enumeration by a depth oracle. At `p=7` it independently reproduces the frozen `(19,10)` pair counts

`538,24,0`

for `a=1,2,3`.

The antipodal depth satisfies `rho_U(x)+rho_U(-x)>=p`. Its exact equality shell forces every proper companion subsum away from both saturated maximal-atom projective lines and makes the companion an atom, at unchanged length, in both rank-two quotients modulo those lines.

## 4. Exact C7 improvement: pair support six is empty

Two independent exact stage-one replays now classify the already frozen `538,24,0` compatible `(19,10)` pair companions by pair support.

The support-six face is

`boxed{0,0,0}`.

Therefore, before the length-8 third atom is introduced,

> **C7 pair theorem.** A support-four length-19 maximal atom paired with a compatible length-10 atom in the `(8,10,19)` corridor satisfies
>
> `|supp(UV)|>=7`.

This is stronger and earlier than the old full-triple statement that all 2796 support-four completions four-pack.

## 5. First prime-uniform equality-face elimination

In the first corridor `j=1`, specialize to maximal type `a=2` and the support-three rank-two branch sharing the heavy value `g4`.

Pair capacity forces the companion shared multiplicity to one. Writing the new multiplicities as `r<=t`,

`r+t=3(p-1)/2`.

There are two cases.

- If `r,t>=(p+1)/2`, doubling the companion relation produces a mixed zero-sum subsequence of `UV` of length exactly `p-1`.
- If `r=(p-1)/2`, then `t=p-1`, and tripling the relation produces a mixed zero-sum of length exactly `|V|-1`.

Both violate the inherited short-free window. Hence:

> **Uniform branch theorem.** The `a=2` heavy-share three-support equality branch is impossible for every odd prime `p>=5`.

This theorem is symbolic; finite regression through prime 1009 is only a control.

## 6. Genuine small-prime boundary

The broader first-corridor support-seven statement cannot start naively at `p=5`. Exact depth-oracle discovery found genuine support-six pair examples at `p=5`, maximal type `a=2`, in the **light-share** rank-two branch. A representative multiplicity shape is

`V=e3^2 x^2 (x+e3)^3`.

The pair is 6-short-zero-free and has packing number two.

Thus the natural generalization target is

`p>=7`.

## 7. Finite discovery controls beyond C7

Targeted exact equality-face searches at `p=11,13,17` also return zero support-six first-corridor candidates for every support-four maximal type tested. These are **discovery controls only** and are not theorem authority.

The current evidence therefore supports the theorem target

> `p>=7`, first maximal corridor, support-four maximal atom `=> |supp(UV)|>=7`.

## 8. What is still genuinely missing

The existing all-prime proof does **not** yet eliminate every support-six normal-form branch. The main hard mechanism is the symmetric `a=1` light-share rank-two family: the three other maximal-atom directions are saturated, and the obstruction uses the geometry of the two new support values rather than only their multiplicities.

A second difficult family is the `a=2` rank-three four-support companion face.

Pure scalar-multiple tests are insufficient in these families. Exact replay shows that mixed subsets of the two new support values are essential. This is an important negative boundary: any proof claiming that multiplicity arithmetic alone closes support six is incomplete.

## 9. Donor gate

Ebert--Grynkiewicz determine the exact rank-two restricted-sum extremal sequence, but the present heavy-pair route naturally lands one term below that extremal length. No published deficiency-one stability theorem has been imported or assumed. The near-extremal step remains a branch-local proof problem unless a verified donor is found.

## 10. Next proof target

The next atomic target is:

> prove that in the `a=1` first-corridor support-three normal form, the rectangle of mixed new-value subsums must meet a low `rho_U` shell, producing a zero-sum of length at most `|V|-1`.

For `a=1`, after changing to the three saturated basis directions, the depth has the symmetric form

`rho_U(z)=min(sum [z_i]_p, 1+sum [z_i-1]_p)`.

This turns the residual into a two-dimensional lattice/box-intersection problem inside the companion plane, rather than a search over arbitrary rank-three sequences.

## Claim ceiling

No line in this checkpoint claims that `D_3(C_7^3)` is determined, that the candidate all-prime formula is proved, or that any donor theorem is novel to ORION.
