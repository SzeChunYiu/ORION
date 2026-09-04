# Prime-uniform maximal-atom corridor and support-six barrier — V1

Status: **proved analytic reduction with arithmetic regression**. Donor inputs are named below. This file does not determine `D_3(C_p^3)` and grants no novelty or priority authority.

## 1. Critical `k=3` setup

Let `p>=5` be prime and let

`G=C_p^3`.

Use the block-monoid convention of this lane: `D_k(G)` is the largest length of a zero-sum sequence whose zero-sum packing number is at most `k`. The donor-derived rank-three formula gives

`D_2(G)=(9p-5)/2`,

and Olson's p-group formula gives

`D(G)=3p-2`.

Put

`N_3(p)=(11p-3)/2`.

This is one above the Freeze--Schmid candidate lower-line value for `D_3`.

Let `B` be zero-sum with

- `|B|=N_3(p)`, and
- `z(B)<=3`.

Since `N_3(p)>D_2(G)`, one has `z(B)>=3`, hence

`boxed{z(B)=3}`.

Moreover `B` is `p`-short-zero-free. Indeed, if `A|B` were a nonempty zero-sum subsequence with `|A|<=p`, then the zero-sum complement would have length at least

`N_3(p)-p=(9p-3)/2=D_2(G)+1`.

It would therefore have packing number at least three; adjoining `A` would give four disjoint nonempty zero-sums in `B`, contradiction.

Thus every atom in a three-atom factorization of `B` has length at least `p+1`.

## 2. Exact maximal-atom corridor enumeration

Suppose a three-atom factorization of `B` contains a maximal atom `U`, so

`|U|=D(G)=3p-2`.

Write the other two atom lengths in increasing order as

`|A|=p+j`,

`|V|=p+b`,

with `1<=j<=b`.

The total length identity gives

`(p+j)+(p+b)+(3p-2)=(11p-3)/2`,

hence

`boxed{j+b=(p+1)/2}`.

The order `j<=b` is equivalent to

`1<=j<=floor((p+1)/4)`.

Therefore every maximal-atom factorization at the critical `k=3` length has exactly one of the prime-uniform profiles

`boxed{C_j(p)=(p+j, p+(p+1)/2-j, 3p-2)}`

for

`boxed{1<=j<=floor((p+1)/4)}`.

There are exactly `floor((p+1)/4)` such corridors.

Examples:

- `p=5`: `(6,7,13)`;
- `p=7`: `(8,10,19)`, `(9,9,19)`;
- `p=11`: `(12,16,31)`, `(13,15,31)`, `(14,14,31)`;
- `p=13`: `(14,19,37)`, `(15,18,37)`, `(16,17,37)`.

Thus the two p=7 maximal corridors are not isolated accidents: they are the first two members of the same all-prime arithmetic family.

## 3. Hereditary depth of the maximal pair

Keep the notation above and let

`P=UV`,

where `V` is the longer companion of length `p+b`.

Because `A` is already a disjoint zero-sum atom, `z(P)>=3` would imply `z(B)>=4`. Since `U` and `V` themselves give two disjoint zero-sums,

`boxed{z(P)=2}`.

Now suppose `X|P` is a nonempty zero-sum subsequence with

`|X|<=p+b-1`.

Then its zero-sum complement in `P` has length at least

`|P|-(p+b-1)`

`=(4p+b-2)-(p+b-1)`

`=3p-1=D(G)+1`.

A zero-sum sequence longer than `D(G)` cannot be an atom, so that complement factors into at least two nonempty zero-sum blocks. Together with `X`, this gives `z(P)>=3`, contradiction.

Hence

`boxed{P is (p+b-1)-short-zero-free}`.

In particular `P` is `p`-short-zero-free. This is the prime-uniform version of the p=7 depths `9` for the `19+10` pair and `8` for the `19+9` pair.

## 4. Uniform support-six barrier for the first two corridors

We now combine the hereditary pair depth with `SHORTFREE_COMPLEMENT_SUPPORT_BARRIER_V1.md`.

Since

`|P|=4p+b-2>4(p-1)`,

capacity alone gives `|supp(P)|>=5`.

Assume for contradiction that

`|supp(P)|=5`.

For the support-complement lemma, the capacity deficit is

`Delta=5(p-1)-|P|`

`=p-b-3`

`=(p+2j-7)/2`,

where `b=(p+1)/2-j`.

For `j=1` or `j=2` whenever that corridor exists, the three hypotheses of the support-complement lemma hold:

1. `Delta>=0`;
2. `5+Delta=(p+2j+3)/2<=p`;
3. `2Delta=p+2j-7<=p-2`.

The last inequality is exactly `j<=2`.

Since `P` is already `p`-short-zero-free, the lemma forbids support five. Therefore:

> **Support-six theorem.** In either of the first two maximal corridors `C_1(p)` or `C_2(p)`,
>
> `boxed{|supp(UV)|>=6}`,
>
> where `U` is the maximal atom and `V` is the longer companion.

For `p=7`, this simultaneously recovers the pair-support-six conclusions for `(8,10,19)` and `(9,9,19)`.

### Exact method boundary at `j=3`

For the third corridor one obtains

`2Delta=p-1`,

while the complement lemma requires `2Delta<=p-2`.

Thus the present mechanism misses `j=3` by exactly one unit. This is a useful structural frontier: any all-corridor theorem must add one unit of information beyond the coordinatewise embedding used by the basic support-complement argument.

## 5. Corollary for support-four maximal atoms

Suppose additionally that the maximal atom `U` has support exactly four. By `SUPPORT4_MAXIMAL_ATOM_WEIGHTS_V1.md`, it is, up to automorphism and reordering, one of the canonical atoms

`U_c=e1^(p-1)e2^(p-1)e3^c(e3-c^(-1)(e1+e2))^(p-c)`,

`1<=c<=(p-1)/2`.

If `j<=2`, the support-six theorem gives

`|supp(U union V)|>=6`.

Since `|supp(U)|=4`, the longer companion must contribute at least two actual support values outside the maximal-atom support:

`boxed{|supp(V) \ supp(U)|>=2}`.

This reduces the all-prime support-four extreme-corridor attack to a finite canonical parameter `c` together with at least two genuinely new companion values.

## 6. Computational receipt

`check_maximal_atom_corridor_prime_uniform_v1.py` independently checks the corridor count, all length identities, the hereditary complement threshold, the three support-complement inequalities for `j<=2`, and the exact one-unit failure at `j=3` for every prime `5<=p<=401`.

The computation is regression only; the all-prime authority is the symbolic proof above.

## 7. Boundary

- No value of `D_3(C_p^3)` is claimed.
- The theorem is conditional only on the existence of a critical length-`N_3(p)` packing obstruction containing a maximal atom in a three-atom factorization.
- The support-six conclusion is proved for corridor indices `j=1,2`; the present support-complement method does not cover `j>=3`.
- The support-four corollary does not classify the longer companion or close any all-prime corridor by itself.
- `D_2(C_p^3)`, `D(C_p^3)`, and the underlying lower-line context are donor-owned; priority/novelty remains `CANNOT_CHECK`.
