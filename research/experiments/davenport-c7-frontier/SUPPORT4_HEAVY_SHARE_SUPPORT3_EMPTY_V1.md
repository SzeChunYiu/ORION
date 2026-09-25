# Heavy-share support-three equality branch is empty in the first corridor — V1

Status: **proved prime-uniform structural elimination**. For every prime `p>=7` and every canonical support-four maximal-atom type, the exact-support-six first-corridor support-three branch that shares the heavy unsaturated maximal-atom value is impossible. This removes the entire heavy-share rank-two equality mechanism, not merely its interior or its first few overlap layers.

No generalized Davenport value or novelty/priority claim is made here.

## 1. Setup

Write

`p=2H+1`, `m=(3p-1)/2=3H+1`,

and put the support-four maximal atom in canonical form

`U=e1^(p-1)e2^(p-1)s^a g^(p-a)`,

where

`g=s-a^(-1)(e1+e2)`, `1<=a<=H`.

Assume the first-corridor maximal pair attains total support six and lies in the support-three rank-two branch sharing only the heavy value `g`:

`V=g^c x^r y^t`,

with `c,r,t>0`, `c+r+t=m`.

Pair `p`-short-freeness gives the heavy actual-value capacity

`boxed{1<=c<=a-1.}`

Let `K=<g,x,y>`. By the first-corridor equality normal form, `K` is a rank-two plane and

`K cap supp(U)={g}`.

The pair is `(m-1)`-short-zero-free and the exact representation-depth criterion applies to every nonempty proper subsequence of `V`.

## 2. The new values are off the heavy projective line

Every projective line of a `p`-short-zero-free sequence contains at most `p-1` terms: `p` terms in one cyclic subgroup `C_p` would contain a nonempty zero-sum of length at most `p`.

The heavy line already contains

`p-a+c`

copies of the actual value `g` in `UV`.

If, say, `x in <g>`, then its multiplicity satisfies

`r>=H+1-c`

from `t<=p-1`. Hence the heavy line would contain at least

`p-a+c+H+1-c=p+H+1-a>=p+1`

terms, because `a<=H`. Contradiction.

Thus

`boxed{x,y notin <g>.}`

Their images in the cyclic quotient

`pi:K -> K/<g> ~= C_p`

are both nonzero.

## 3. The projected new-value sequence has at least two atom factors

Since `V` is zero-sum and `g` vanishes in the quotient,

`S=pi(x)^r pi(y)^t`

is a zero-sum sequence over `C_p` of length

`|S|=r+t=m-c`.

Using `c<=a-1<=H-1`,

`|S|>=m-(H-1)=2H+2=p+1.`

Every atom over `C_p` has length at most `p`. Therefore `S` factors into at least two nonempty cyclic atoms:

`S=Q_1 ... Q_k`, `k>=2`.

Lift each `Q_i` back to the corresponding subsequence of the `x,y` terms of `V`. Since its quotient sum is zero,

`sigma(Q_i)=q_i g`

for a unique residue `q_i in {0,...,p-1}`.

The factor is a proper subsequence of `V`, because at least one other quotient atom remains.

## 4. Each quotient atom has a tiny positive heavy-line sum

First, `q_i!=0`: otherwise `Q_i` itself would be a proper zero-sum subsequence of the atom `V`.

The antipodal-shell theorem forbids every proper companion subsum on

`{qg:a<=q<=p-a}`.

So `q_i` cannot lie in that interval.

It also cannot lie in the upper interval `p-a+1,...,p-1`. Indeed, if

`q'=p-q_i`,

then `1<=q'<=a-1`. The complement `V/Q_i` is proper and has sum `q'g`. Since `|Q_i|<=p`,

`|V/Q_i|>=m-p=H`,

whereas the exact heavy-line depth for `q'<a` is

`rho_U(q'g)=q'<=a-1<=H-1`.

This contradicts the graded inequality

`rho_U(sigma(V/Q_i))>=|V/Q_i|`.

Hence

`boxed{1<=q_i<=a-1.}`

For these residues the exact depth is simply

`rho_U(q_i g)=q_i`.

To see this directly, any U-representation of `q_i g` has counts `z` on `s` and `u` on `g` with `z+u==q_i (mod p)` and `0<=z<=a`, `0<=u<=p-a`; since `z+u<=p` and `1<=q_i<p`, one has `z+u=q_i`, and the saturated-axis correction only adds nonnegative cost. The literal `g^{q_i}` representation attains `q_i`.

Applying the graded depth inequality to `Q_i` gives

`boxed{|Q_i|<=q_i.}`

Now suppose `q_i>=a-c`. The pair contains `p-a+c` actual copies of `g`, so it contains the `p-q_i` copies needed to cancel `Q_i`, because

`p-q_i<=p-a+c`.

Then

`Q_i g^(p-q_i)`

is an actual nonempty zero-sum subsequence of `UV` of length

`|Q_i|+p-q_i<=p<m`,

contradicting pair short-freeness.

Therefore every quotient atom satisfies the stronger bound

`boxed{1<=|Q_i|<=q_i<=a-c-1.}`

In particular, if `c=a-1`, the branch is already impossible.

## 5. Partial-sum crossing contradiction

Assume now `a-c>=2`.

Let

`Q=sum_i q_i`

as an ordinary positive integer. Since the lifted quotient factors partition the `x,y` terms,

`sum_i sigma(Q_i)=sigma(x^r y^t)=-c g`.

Thus

`Q==p-c (mod p)`.

Also

`Q>=sum_i |Q_i|=|S|=m-c>p-c`.

Hence `Q` is not the first positive representative `p-c`; in particular

`boxed{Q>p.}`

Order the factors arbitrarily and take the shortest initial block whose ordinary `q`-sum `R` satisfies

`R>=a-c`.

The preceding partial sum is below `a-c`, and the new summand is at most `a-c-1`, so

`a-c<=R<=2(a-c)-2`.

Since `c>=1` and `a<=H`,

`R<=2a-4<=p-5<p`.

Because the total ordinary sum is `>p`, this initial block is a proper subcollection of the quotient factors.

Let `W` be the union of its lifted subsequences. Then

`sigma(W)=R g`,

and

`|W|<=R`.

Again `R>=a-c` implies that the pair contains enough actual heavy terms to supply `p-R` copies of `g`:

`p-R<=p-a+c`.

Therefore

`W g^(p-R)`

is an actual zero-sum subsequence of `UV`, of length

`|W|+p-R<=p<m`.

This is the final contradiction.

## 6. Theorem

> **Heavy-share rank-two elimination theorem.** For every prime `p>=7` and every canonical support-four maximal-atom type
>
> `1<=a<=(p-1)/2`,
>
> the first maximal corridor has no exact-support-six support-three rank-two companion sharing only the heavy unsaturated maximal-atom value.

Thus the support-three equality face, if it survives at all, must be on the **light-share** side.

This strictly strengthens the previous results:

- the all-type heavy interior elimination;
- the `a=2` heavy one-share theorem;
- every finite heavy-overlap control.

Those remain useful as independent regression and historical evidence, but they are no longer the frontier.

## 7. Why the argument is structurally useful

The proof does not classify the two new values and does not choose scalar multiples of the full three-support relation. It uses three invariant ingredients instead:

1. project the companion plane modulo the shared heavy direction;
2. factor the long projected zero-sum sequence into cyclic atoms;
3. convert the pair-depth inequalities into a bound on the ambient heavy-line sum of every quotient atom, then force a partial-sum crossing.

This quotient-factorization mechanism is a candidate template for other equality faces where a long companion collapses to a lower-rank zero-sum sequence after modding out a shared support direction.

## Verification receipt

`check_support4_heavy_share_support3_empty_v1.py` checks the arithmetic inequalities in the proof for every prime through `1009`, every canonical type and every admissible heavy overlap. As an independent control, it also enumerates every coefficient-compatible boundary row through prime `101` and verifies that the exact heavy radial multiplier oracle leaves zero residual multiplicity rows.

The checker is regression only; theorem authority is the quotient-factorization and partial-sum proof above.

## Boundary

- The light-share support-three branch remains open on its boundary strips and in the exceptional high-overlap `a=1` interior.
- The rank-three support-four companion remains open.
- The theorem assumes the first maximal corridor and a support-four maximal atom.
- No `D_3(C_p^3)` value, all-`k` formula, or novelty/priority claim is made.
