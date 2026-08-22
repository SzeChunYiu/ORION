# X1-B donor audit — Geroldinger--Yang p-group theorem exactly supports local scalarization

Parent: #900.
Status: **LOAD-BEARING DONOR AUDIT — committed before full C15 proof assembly.**

Source: Alfred Geroldinger and Wenkai Yang, *On a classical zero-sum invariant*, arXiv:2608.19090v1, 19 Aug 2026.

The original PDF was inspected textually and visually on the theorem/proof pages.

## Exact source statements

The paper defines, for a nontrivial finite abelian group G, `nu_p(G)` so that a zero-sum-free sequence T of sufficient length has all nonzero elements missing from `Sigma(T)` contained in a coset of a subgroup of index p.

Theorem 3.5 states:

> If G is a finite abelian p-group with `|G|>=p`, then
> `nu(G)=nu_p(G)=d(G)-1`.

The proof takes a zero-sum-free sequence T with

`|T|=d(G)-1`

and constructs a map

`lambda:G->F_p`

from the group-algebra identity

`(1-X^y) Pi(T) = lambda(y) sum_{g in G} X^g`.

It then proves explicitly that lambda is a group homomorphism.

For every

`x in G^bullet \ Sigma(T)`, 

the sequence `(-x)T` is zero-sum free. Comparing the coefficient of `X^0` in the above identity gives

`lambda(-x)=1`,

hence

> `lambda(x)=-1`.

In particular lambda is nonzero, its kernel has index p, and all missing nonzero subsequence sums lie in one affine coset.

## Specialization to `C_5^3`

For

`G=C_5^3`,

we have

`d(G)=3(5-1)=12`.

Therefore every zero-sum-free sequence T of length 11 admits a nonzero homomorphism

`lambda:C_5^3 -> F_5`

such that every nonzero missing subsequence sum x satisfies

`lambda(x)=-1`.

## Exact local-scalarization implication used by X1-B

Let

`H=h_1 ... h_12`

be any maximal zero-sum-free sequence of twelve kernel block sums in `C_5^3`, and fix i. Put

`T_i=H h_i^{-1}`.

Then `|T_i|=11` and T_i is zero-sum free.

If c is the lifted sum of any legal replacement quotient block while the other eleven blocks are fixed, then the twelve block sums

`T_i c`

must remain zero-sum free in a hypothetical upstairs counterexample. Therefore

`-c notin Sigma(T_i)`.

Likewise `T_i h_i=H` is zero-sum free, so

`-h_i notin Sigma(T_i)`.

Applying Theorem 3.5's canonical homomorphism gives

`lambda_i(-c)=lambda_i(-h_i)=-1`,

hence

> `lambda_i(c)=lambda_i(h_i)=1`.

Thus all legal twelfth replacement block sums have one common nonzero scalar image under one nonzero linear functional, exactly as required by the committed local-scalarization lemma. Rescaling the functional changes only the chosen common nonzero RHS convention.

## Audit conclusion

The p-group missing-sum/local-scalarization bridge used in the k=3 and k=4 C15 residual arguments is a valid direct specialization of Geroldinger--Yang Theorem 3.5 and its proof.

No stronger statement is imported:

- the donor theorem does not classify maximal `C_5^3` zero-sum-free sequences;
- it does not assert cross-deletion functional equality;
- it does not prove any C15 Davenport result.

Those later constraints were handled separately in the committed X1-B programme.

## Claim boundary

This audit admits one donor implication into the proof chain. It grants no C15 theorem or novelty authority by itself.