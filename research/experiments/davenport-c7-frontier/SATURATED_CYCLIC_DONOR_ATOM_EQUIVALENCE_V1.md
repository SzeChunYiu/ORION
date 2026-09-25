# Saturated cyclic donors and quotient atoms: an exact interface

Status: **proved for every finite abelian group, independently internally audited**. The threshold below is sharp. No Davenport equality is inferred from this interface alone.

## 1. Statement

Let `G` be a finite abelian group and let `g` have order `n>=2`. Let `R` be a nonempty occurrence sequence and suppose

`sigma(R)=-d g`, `0<=d<n`.

Put

`m=|R|+d`, `B=R g^(n-1)`

and let `pi:G -> G/<g>` be the quotient map. Assume `m>n`.

Then the following are equivalent:

1. `B` has no nonempty zero-sum shorter than `m`.
2. `pi(R)` is an atom.

Under either condition, every nonempty zero-sum occurrence subsequence of `B` uses every occurrence of `R` and exactly `d` donor occurrences. In particular its length is exactly `m`. The donor and `R` are treated as separately labeled occurrence bundles even if their values coincide.

The theorem has no rank, prime-order, or ambient exponent hypothesis.

## 2. Short-freeness implies a quotient atom

The projection of `R` has sum zero. Suppose a nonempty proper part `Y|R` also has zero projected sum. Both `sigma(Y)` and `sigma(R/Y)` lie in `<g>`.

If either sum is zero in `G`, that part is a nonempty zero-sum shorter than `m`: its length is at most `|R|-1<m`. Otherwise there are unique integers

`1<=alpha,beta<=n-1`

such that

`Y g^alpha`, `(R/Y) g^beta`

are zero-sum. Each is individually available in `B`; their donor occurrences need not be simultaneously disjoint. Since the two lifted sums add to `-d g`,

`alpha+beta == d (mod n)`.

If `d=0`, this forces `alpha+beta=n`. If `d>0`, the only possible sums are `d` and `n+d`, ignoring alternatives outside `[2,2n-2]`. In either case,

`|Y g^alpha|+|(R/Y) g^beta| <= |R|+n+d=m+n<2m`.

At least one of these two individually available zero-sums is shorter than `m`, contradiction. Thus the projection is an atom.

## 3. A quotient atom implies exact short-freeness

Consider any nonempty zero-sum part of `B`. It must use a nonempty occurrence part `Y` of `R`, since `g^(n-1)` is zero-sum free. The projected sum of `Y` is zero. If `pi(R)` is an atom, all occurrences of `R` are used.

Its donor count `z` then lies in `[0,n-1]` and satisfies

`-d g+z g=0`.

Therefore `z=d`, and the zero-sum has length `|R|+d=m`. Conversely `R g^d` is available and is zero-sum. This proves the equivalence and the additional exact statement. This implication itself does not need `m>n`.

## 4. The strict threshold is sharp

For any `n>=2`, take `d=0` and `R=g^n`. Then `m=n`, and

`B=g^(2n-1)`

has no nonempty zero-sum shorter than `n=m`. But `pi(R)` consists of `n` zero terms, so is reducible. Hence `m>n` cannot be weakened to `m>=n` in the equivalence.

## 5. Davenport interface

For the rank-three type-two companion, take `n=p`, `d=1`, and

`R=s^c x^r y^t`, `sigma(R)=-g`, `|R|=m-1`.

The actual shared donor supplies `g^(p-1)`, and `m=p+H>p`. Therefore `R` projects to a rank-two atom modulo `<g>`. This is precisely the first quotient used in the unsaturated budget proof.

The same theorem with `d=0` applies to a complete zero-sum companion and any actual saturated cyclic donor direction. The atom equivalence is an interface, not a sufficient condition for compatibility with additional donor values.

The coordinating researcher and a separately tasked quotient-structure researcher checked both implications, the non-disjoint completion logic, the endpoint `d=0`, uniqueness of the final donor count, and the sharp threshold example. No external theorem or computation is needed.
