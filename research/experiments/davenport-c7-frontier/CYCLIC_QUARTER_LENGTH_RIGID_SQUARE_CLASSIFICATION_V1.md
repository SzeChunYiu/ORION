# Exact rigid-square classification at quarter length

Status: **proved prime-uniform arithmetic classification, independently internally audited**. Applied to the exceptional rank-three first unsaturated face, it leaves two infinite edge families and five explicit primitive pairs. This is a strict inverse reduction, not a complete elimination of that face.

## 1. Exact cyclic statement

Let `a,b` be positive integers, let

`p=4(a+b)-1`

be prime, and let `h` generate `C_p`. Define

`Q=(b h)^a (-a h)^b`.

The two displayed values are nonzero and distinct. Then `Q` is the only atomic divisor of `Q^2` if and only if, after interchanging `a,b`, both of the following hold:

- `gcd(a,b)=1` and `a<=b`;
- either `a<=2`, or `(a,b)` is one of

`(3,5), (3,8), (4,7), (4,11), (5,7)`.

The corresponding primes for these five pairs are respectively `31,43,43,59,47`. These are exact surviving cyclic configurations; their occurrence as full rank-three companions is not asserted.

## 2. Primitive pairs and the occurrence rectangle

If `gcd(a,b)>1`, dividing the count vector by that common divisor gives a proper zero-sum part of `Q`. Therefore rigidity forces `gcd(a,b)=1`.

An occurrence part with `A` copies of `b h` and `B` copies of `-a h` has zero sum precisely when

`bA-aB == 0 (mod p)`, `0<=A<=2a`, `0<=B<=2b`.          (1)

When the ordinary determinant is zero, coprimality makes the count vector an ordinary multiple of `(a,b)`. The nonempty possibilities in the rectangle are exactly `Q` and `Q^2`.

Thus any solution of

`bA-aB=p`                                                   (2)

in the rectangle contradicts rigidity: factor the resulting zero-sum part into atoms; not all can be `Q`, since its count vector is not proportional to `(a,b)`. Conversely, if no nonzero multiple of `p` occurs as the determinant in (1), then `Q` is an atom and the only atomic divisor of its square.

Swapping `a,b` exchanges the two roles up to changing the generator's sign, so assume `a<=b` from now on.

## 3. Seven or more copies in each value are impossible

Suppose `a>=7`. There is a unique integer `A` in `[a+1,2a]` with

`bA==p (mod a)`,

because `gcd(a,b)=1`. Set `B=(bA-p)/a`. The numerator obeys

`bA-p >= b(a+1)-4(a+b)+1`

`=b(a-3)-4a+1 >= a(a-7)+1 >0`.

Also `A<=2a` and `p>0` give `B<2b`. Therefore (2) is an occurrence-valid positive solution. This contradicts rigidity and proves `a<=6`.

## 4. The remaining constant residue classes

This is a finite arithmetic case distinction in the bounded integer `a`, with formulas valid for every `b` in each class. It is not a computation over primes or support values.

### 4.1. `a=6`

Here `p=4b+23`. Coprimality gives `b=1` or `5` modulo six. The first class would make `p` divisible by three, impossible. Thus `b=5 (mod 6)`, and `b>=a` gives `b>=11`. Take

`A=11`, `B=(7b-23)/6`.

These satisfy (2), with `0<A<=12` and `0<B<2b`. Hence no pair with `a=6` survives.

### 4.2. `a=5`

Now `p=4b+19`. Coprimality excludes `b=0 (mod 5)`, while `b=4 (mod 5)` would make `p` divisible by five. The other classes give:

| Residue of `b` modulo 5 | `A` | `B` |
|---|---:|---|
| 1 | 8 | `(4b-19)/5` |
| 2 | 6 | `(2b-19)/5` |
| 3 | 7 | `(3b-19)/5` |

Each row solves (2), and `A<=10`, `B<2b`. In the first class `b>=6` makes `B>0`. In the third class `b>=8` does the same. In the second class, `B>0` for every allowed `b>=12`; its sole smaller allowed value is `b=7`. Thus only `(5,7)` remains.

### 4.3. `a=4`

Here `p=4b+15`, and coprimality makes `b` odd.

For `b=1 (mod 4)`, use

`A=7`, `B=(3b-15)/4`.

The first possible value `b=5` makes `p=35`, not prime; every remaining allowed `b>=9` gives `B>0`. For `b=3 (mod 4)`, use

`A=5`, `B=(b-15)/4`.

This gives `B>0` for every allowed `b>=19`. The smaller values are `b=7,11,15`, and `b=15` gives composite `p=75`. In all positive cases the counts fit (2). Therefore only `(4,7)` and `(4,11)` remain.

### 4.4. `a=3`

Here `p=4b+11`. Coprimality excludes `b=0 (mod 3)`, and primality excludes `b=1 (mod 3)`. Thus `b=2 (mod 3)`. Use

`A=5`, `B=(b-11)/3`.

This solves (2) with positive fitting counts for every allowed `b>=14`. The smaller allowed values are `5,8,11`; the last gives composite `p=55`. Therefore only `(3,5)` and `(3,8)` remain.

Together these arguments prove necessity of the stated list, leaving `a=1,2` as the two possible infinite families.

## 5. Every listed primitive pair really is rigid

For `a=1` or `2`,

`|bA-aB|<=2ab<p`

throughout the occurrence rectangle. The same strict inequality holds for `(a,b)=(3,5)`, since `2ab=30<p=31`. Therefore the only zero-sum count vectors in these cases are ordinary multiples of `(a,b)`, proving rigidity whenever the pair is primitive.

For the other four pairs, `2ab<2p`, so the only possible nonzero multiples in (1) are `p` and `-p`. The congruence `bA==p (mod a)` and the upper bound `A<=2a` give the following maximal possible `A`:

| `(a,b)` | `p` | Largest possible `A` | `bA` |
|---|---:|---:|---:|
| `(3,8)` | 43 | 5 | 40 |
| `(4,7)` | 43 | 5 | 35 |
| `(4,11)` | 59 | 5 | 55 |
| `(5,7)` | 47 | 6 | 42 |

In every case `bA<p`, so (2) would require a negative `B`. Thus determinant `p` is impossible. The complement map

`(A,B) -> (2a-A,2b-B)`

preserves the rectangle and changes the determinant's sign, so determinant `-p` is equally impossible. This proves the converse and completes the exact classification.

The displayed constants are direct arithmetic witnesses in a classification already reduced to four pairs; no sequence or support enumeration supplies theorem authority.

## 6. Application to the rank-three type-two first face

In the rigid-square alternative of `A2_RANK3_UNSATURATED_QUOTIENT_BUDGET_V1.md`, write

`p=4q-1`, `H=2q-1`, `c=2a`, `r=2b`, `a+b=q`.

The actual full companion relation is

`y=a s+b x+(1/2)g`.

In the twice-quotiented cyclic group, the atom is

`Q=pi(s)^a pi(x)^b`,

and it is the only atomic divisor of its square. Since `a pi(s)+b pi(x)=0`, choosing `h=pi(s)/b` makes its two values exactly `b h` and `-a h`. The theorem applies without changing any actual multiplicities.

Consequently, after possibly exchanging the numbers `a,b` for the arithmetic statement, the entire rigid branch is forced into

- `min(c,r)=2`;
- `min(c,r)=4`, with the other half-count odd;
- or the doubled exceptional pairs `(c,r)=(6,10),(6,16),(8,14),(8,22),(10,14)` and their reversals, at the five primes stated above.

In overlap notation, the two infinite possibilities are `c=2` or `r=2`, and `c=4` or `r=4`. The original donor distinguishes `c` from `r`; this arithmetic interchange does not assert a symmetry of the full geometric problem. The primitive condition in the four-count family forces `p=3 (mod 8)`.

This proves strict additional rigidity of the first unsaturated face. It does not eliminate the listed full-companion possibilities, and it does not assume that their surviving cyclic models can be realized with the original donor.

The coordinating researcher and a separately tasked quotient-structure researcher checked the determinant construction, the coprimality step, all bounded residue classes, all prime exclusions, and the converse rectangle argument. No external structural theorem is used in this classification.
