# Type-two top-overlap singleton row is eliminated by a maximal-atom quotient — V1

Status: **proved prime-uniform complete elimination of the rank-two row `(c,r,t)=(H,1,p-1)`**, for every prime `p==1 (mod 4)`, `p>=7`. This removes a row on which every scalar relation test is provably powerless. The proof exchanges equal-sum occurrence blocks, then applies a classical rank-two maximal-atom structure theorem in a quotient.

No full exceptional-face, first-corridor, or generalized Davenport equality is inferred.

## 1. Statement and resources

Let `p=4k+1>=7` be prime, set `H=2k`, `m=6k+1`, and use

`U=e1^(p-1)e2^(p-1)g^(p-2)s^2`,

where `e1+e2=2(s-g)` and `(e1,e2,g)` is a basis.

Suppose

`V=s^(2k) x y^(4k)`

is a zero-sum companion of rank two, with `x,y` distinct new values, and assume `UV` has no nonempty zero-sum of length less than `m`.

We derive a contradiction. The allowed prime congruence is exactly the one in which the type-two light-overlap ceiling permits `c=H`; when `p==3 (mod 4)`, that ceiling is `H-1` and this row is unavailable already.

## 2. Exchange equal-sum blocks

The companion relation gives

`x=y-2k s`,

and hence

`x+4k y=(2k+1)s`.

The actual subsequences

`W=x y^(4k) | V`,

`T=e1^k e2^k g^(2k)s | U`

have the same sum `(2k+1)s` and the same length `4k+1=p`. Every count is within the displayed resources.

Form

`U'=U T^(-1)W`, `V'=V W^(-1)T`.

These sequences are zero-sum, their product is still `UV`, and

`|U'|=3p-2`, `|V'|=m`.

Since `3p-2<2m`, short-freeness forces `U'` to be an atom: any decomposition into two nonempty zero-sums would need at least `2m` occurrences. Thus `U'` is a maximal atom in `C_p^3`.

Explicitly,

`U'=e1^(3k)e2^(3k)g^(2k-1)s x y^(p-1)`.

In particular it contains the saturated power `y^(p-1)` and retains one occurrence each of `s` and `x`.

## 3. Saturated quotient lemma

Let `A` be any atom over an elementary `p`-group and suppose `y^(p-1)|A`. Let `pi` be the quotient map by `<y>` and put

`Q=A y^(-(p-1))`.

Then `pi(Q)` is an atom in the quotient.

Indeed, its full sum is zero. If a nonempty proper occurrence subsequence `Q0|Q` had `pi(sigma(Q0))=0`, then `sigma(Q0)=a y` for some `a in F_p`. Choose the unique `j in {0,...,p-1}` with `a+j=0`. The subsequence `Q0 y^j` would be a nonempty proper zero-sum subsequence of `A`: it fits the saturated capacity and is proper because `Q0` omits an occurrence of `Q`. This contradicts atomicity.

Apply this lemma to `A=U'`. Its quotient is an atom of length

`|Q|=(3p-2)-(p-1)=2p-1`

in `C_p^3/<y>`, which is isomorphic to `C_p^2`. It is therefore a maximal atom in that rank-two group.

## 4. The verified rank-two donor theorem

The established fact used here is:

> In `C_p^2`, any two distinct support values of a maximal atom of length `2p-1` generate the whole group.

This is Proposition 2(a), printed page 2, of Gunter Lettl and Wolfgang A. Schmid, *Minimal zero-sum sequences in `C_n direct-sum C_n`*, in the [author-hosted primary paper](https://www.math.univ-paris13.fr/~schmid/personal/schmid_14.pdf). That proposition explicitly credits Gao–Geroldinger, *Zero-sum problems and coverings by proper cosets*, Corollary 6.3, together with their earlier rank-two work. The theorem is also consistent with the donor already recorded in `MAXIMAL_ATOM_PROJECTIVE_SEPARATION_V1.md`.

Both the producing agent and the independent proof auditor opened the primary author PDF and checked the exact rank-two statement. No unproved Property B classification is invoked.

## 5. The quotient contains a forbidden pair of distinct collinear values

Because `V` has rank two and its relation expresses `x` through `s,y`, the values `s,y` are linearly independent. Thus

`pi(s)!=0`.

Section 2 gives

`pi(x)=(2k+1)pi(s)`.

The scalar `2k+1` is neither zero nor one modulo `p=4k+1`. Consequently `pi(s)` and `pi(x)` are distinct nonzero collinear support values of `pi(Q)`.

This contradicts the rank-two donor theorem in Section 4. Therefore the hypothesized short-free pair does not exist.

> **Theorem.** A canonical type-two first-corridor maximal pair cannot have a rank-two light-share companion
>
> `boxed{V=s^H x y^(p-1)}`
>
> for any prime `p>=7`. In the only congruence class where `c=H` is allowed, the equal-sum exchange and saturated quotient give the contradiction above.

## 6. Why the method advances the frontier

For this row, `[n]_p<=1` allows only the original relation multiplier `n=1`, whose optimal radial completion has length exactly `m`. Thus no scalar search can prove this theorem. The exchange uses a tied representation to create a different maximal atom in which a previously new value is saturated; quotienting then exposes two forbidden collinear support values.

The saturated quotient lemma is valid independently of this row. Applying it after other occurrence exchanges offers a general structural route, but no claim is made that such an exchange always exists or preserves the needed support values in other multiplicity rows.

The proof does not enumerate primes, support coordinates, or hypothetical companions. It received independent internal mathematical review, including direct verification of the external donor statement; this is not external referee approval or a novelty claim.
