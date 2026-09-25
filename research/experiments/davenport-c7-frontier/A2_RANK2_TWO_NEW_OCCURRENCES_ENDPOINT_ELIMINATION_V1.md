# The type-two endpoint with two low-multiplicity new occurrences is empty — V1

Status: **proved prime-uniform elimination of the entire rank-two endpoint row `(c,r,t)=(H-1,2,p-1)`** for every prime `p>=7`. Three prime congruence classes are handled by a proper companion subsum, a short radial lift, and an equal-sum exchange followed by a published rank-two multiplicity theorem.

This statement closes an endpoint row, not the full exceptional face or any generalized Davenport value.

## 1. Setup

Let `p=2H+1>=7` be prime, `m=3H+1`, and

`U=e1^(p-1)e2^(p-1)g^(p-2)s^2`,

where `e1+e2=2(s-g)` and `(e1,e2,g)` is a basis.

Suppose a rank-two zero-sum companion has

`V=s^(H-1)x^2y^(p-1)`

with distinct new values `x,y`, and assume `UV` contains no nonempty zero-sum of length less than `m`. This also forces `V` to be an atom, since its length is exactly `m`.

## 2. Primes p==3 (mod 4): the companion is already non-atomic

Write `p=4q+3`, so `H=2q+1`, `c=H-1=2q`. Multiply the companion relation by

`n=(p+1)/2=2q+2`.

Its least positive residues on `(s,x,y)` are

`(D,A,B)=(q,1,2q+1)`.

All three counts fit strictly inside the companion. Thus this is a nonempty proper zero-sum subsequence of `V`, a contradiction.

## 3. Primes p==5 (mod 8): the inverse-two scalar is short after lifting

Write `p=4q+1` with `q` odd. Then `H=2q`, `c=2q-1`, and `n=(p+1)/2=2q+1` gives

`(D,A,B)=(3q,1,2q)`.

The new-value counts fit. The enlarged radial donor contains `c+2=2q+1` copies of `s`; its exact type-two surcharge is

`2ceil(max(D-c-2,0)/2)=2ceil((q-1)/2)=q-1`.

The lifted length is consequently

`3q+1+2q+(q-1)=6q=m-1`,

again a contradiction. This also covers the formal small endpoint `q=1`; the present theorem itself starts at `p>=7`.

## 4. Primes p==1 (mod 8): saturate y by exchanging an equal-sum block

Let `p=8k+1`. Since this number is prime and `p>=7`, one has `k>=2`.

Here `H=4k`, `c=4k-1`, and the companion relation gives

`2x-y=-(4k-1)s=(4k+2)s`.

The actual subsequences

`W=x^2y^(8k) | V`,

`T=e1^(2k)e2^(2k)g^(4k)s^2 | U`

both sum to `(4k+2)s` and have the same length `8k+2=p+1`.

The exchange `U'=U T^(-1)W` is zero-sum of length `3p-2`. Since the pair is short-free below `m` and `3p-2<2m`, it is an atom, just as in `A2_RANK2_TOP_SINGLETON_QUOTIENT_ELIMINATION_V1.md`.

Explicitly,

`U'=e1^(6k)e2^(6k)g^(4k-1)x^2y^(p-1)`.

Apply the saturated quotient lemma from that note to quotient by `<y>`. Removing `y^(p-1)` leaves a maximal atom `Q` of length `2p-1` in `C_p^2`.

Delete one occurrence of the projected `x` from `Q`. The result `S` is zero-sumfree of length `2p-2`, with displayed occurrence counts

`pi(e1)^(6k) pi(e2)^(6k) pi(g)^(4k-1) pi(x)`.

## 5. Projection collisions cannot invalidate the multiplicity bounds

Every projected value is nonzero, since a zero value would already be a proper zero-sum in `Q`.

The three values `pi(e1),pi(e2),pi(g)` are pairwise distinct. If the first two coincided, `Q` would contain `12k>=p` equal occurrences. If either coincided with `pi(g)`, it would contain `10k-1>=p` equal occurrences. Both contradict atomicity of `Q`.

The value `pi(x)` is allowed to coincide with one of those three. Even in that case, the two largest multiplicities `m1>=m2` in `S` obey

`m1<=6k+1<=8k-2=p-3`,

`m2>=6k>=2(8k+1)/3=2p/3`.

The inequalities use only `k>=2`. Thus no assumption of four distinct projected support values is needed.

## 6. Verified external multiplicity theorem

Bhowmik, Halupczok and Schlage-Puchta, *The structure of maximal zero-sum free sequences*, Acta Arithmetica 143 (2010), 21–50, Theorem 1(3), proves that a sequence in `C_p^2` of length `2p-2` with largest multiplicity at most `p-3` and second largest multiplicity at least `2p/3` contains a nonempty zero-sum. See the [primary author-hosted paper, Theorem 1 on printed page 2](https://pro.univ-lille.fr/fileadmin/user_upload/pages_pros/gautami_bhowmik/Publications/Bmult-acta.pdf) and the [publisher record](https://www.impan.pl/pl/wydawnictwa/czasopisma-i-serie-wydawnicze/acta-arithmetica/all/143/1/83134/the-structure-of-maximal-zero-sum-free-sequences).

Applying that theorem to `S` contradicts its zero-sumfreeness. This closes the last prime congruence class.

The external theorem is a published prime-uniform result. Its authors explicitly describe bounded computer-assisted inputs in their proof architecture, including Theorem 3 and their dependency diagram on printed page 4. Those inputs remain donor-owned. The present argument runs no brute-force search and does not claim an independent fully elementary reproving of that donor theorem.

## 7. Conclusion and proof boundary

The three congruence classes exhaust all odd primes. Therefore

`boxed{V=s^(H-1)x^2y^(p-1)}`

cannot occur in a type-two first-corridor rank-two maximal pair for any prime `p>=7`.

For primes `p==1 (mod 8)`, this is precisely the `R=2` family in `A2_RANK2_EXACT_SCALAR_BARRIER_V1.md`: every admissible optimized radial scalar score is at least `m`. The new proof crosses that barrier by changing the maximal atom and exploiting its saturated quotient.

The producing agent and a separately tasked proof auditor independently opened the primary donor paper and checked its exact multiplicity hypotheses. Both the auditor and root checked the full written argument, including the exchange, quotient, congruence cases, and possible projection collisions. Internal mathematical review is GREEN. No full first-corridor or Davenport equality is asserted.
