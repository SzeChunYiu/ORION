# X1-C finding — forced C45 kernel sequences have at least 39/42 full-order terms

Parent: #901. Committed before downstream use.

## Setup

Let

`K=C_15^3 ≅ C_3^3 ⊕ C_5^3`

and let `U` be a maximal zero-sum-free sequence of length 42 arising from the committed X1-C maximal-kernel completion reduction for a hypothetical length-133 zero-sum-free sequence over `C_45^3`.

The committed primary-projection constraints give

`pack_0(pi_3(U))=12`

and

`pack_0(pi_5(U))<=6`.

Every nonzero element of K has order 3, 5, or 15. Write

- `a` = number of order-3 terms of U;
- `b` = number of order-5 terms of U;
- `c` = number of order-15 terms of U.

Then `a+b+c=42`.

Under the CRT decomposition:

- an order-5 term projects to 0 in `C_3^3`;
- an order-3 term projects to 0 in `C_5^3`;
- an order-15 term projects nontrivially to both primary factors.

## Bound on order-5 terms: b <= 1

The projection `pi_3(U)` contains exactly b zero terms. Each zero term itself is a zero-sum block.

Since `pack_0(pi_3(U))=12`, after deleting the b zero terms the remaining nonzero projected sequence of length `42-b` must fail to contain `13-b` pairwise disjoint zero-sum subsequences; otherwise those blocks together with the b singleton zero blocks would give 13 disjoint zero-sums in `pi_3(U)`.

For `b<=10`, we have `13-b>=3`, and the exact donor formula

`D_k(C_3^3)=3k+6` for k>=3

implies that a sequence failing k disjoint zero sums has length at most

`D_k-1 = 3k+5`.

Thus, with `k=13-b`,

`42-b <= 3(13-b)+5 = 44-3b`.

Hence

`2b <= 2`,

so `b<=1`.

The remaining large-b cases are independently impossible:

- if `b=11`, the nonzero remainder has length 31; `D_2(C_3^3)=11` forces two disjoint zero-sums, which with 11 zero singletons gives 13;
- if `b=12`, the nonzero remainder has length 30; `D(C_3^3)=7` forces one zero-sum, which with 12 zero singletons gives 13.

Therefore in all cases

`b<=1`.

## Bound on order-3 terms: a <= 2

The projection `pi_5(U)` contains a zero terms. If its nonzero remainder contained `7-a` disjoint zero sums, then together with the a zero singletons `pi_5(U)` would have 7 disjoint zero-sum blocks, contradicting the committed bound `pack_0(pi_5(U))<=6`.

We use the following donor bounds for `C_5^3`:

- `D_3(C_5^3)<=33`;
- `eta(C_5^3)=33`, so every length-33 sequence contains a nonempty zero-sum of length at most 5.

The standard extraction argument therefore gives

- `D_4(C_5^3)<=38`: extract one short zero-sum (length <=5), leaving at least 33 terms and hence 3 further disjoint zero-sums;
- iteratively `D_5(C_5^3)<=43` and `D_6(C_5^3)<=48`.

Now suppose `a>=3`.

- If `a=3`, the nonzero remainder has length 39, which is >=`D_4<=38`, so it contains 4 disjoint zero-sums; with the 3 zero singletons this gives 7, contradiction.
- If `a=4`, the nonzero remainder has length 38 >=`D_3<=33`, so it contains at least 3 disjoint zero-sums; with four zero singletons this gives 7.
- For `a>=5`, the contradiction is only easier: the required number `7-a` of additional nonzero blocks is <=2 while the nonzero remainder remains far above the classical Davenport threshold. In particular, a=5 needs two blocks and a=6 needs one.

Therefore

`a<=2`.

## Full-order consequence

Since

`c = 42-a-b`,

with `a<=2` and `b<=1`, we obtain

`c>=39`.

Thus every maximal kernel sequence U compatible with a hypothetical C45 counterexample contains at least

`39 of 42`

terms of full order 15.

Equivalently, at most three terms have deficient primary order, with the sharper split

- at most two order-3 terms;
- at most one order-5 term.

## Significance

This is substantially stronger than the generic mixed-rank inverse information currently available for arbitrary maximal zero-sum-free sequences in `C_15^3`. It is not asserted as a theorem about all maximal C15^3 sequences; it is a theorem about the restricted class forced by the C45 quotient-block realization and primary packing constraints.

It sharply narrows the remaining inverse compatibility problem:

> a hypothetical C45 counterexample can only realize a maximal C15^3 kernel sequence that is almost entirely supported on full-order elements.

The next hostile questions are:

1. can the remaining 0--3 low-order defects be eliminated using block-exchange/lift compatibility?
2. does the fresh `nu_3/nu_5` maximal-atom machinery force all 42 terms to have order 15 under this packing signature?
3. can the 39 full-order terms alone force a zero-sum or a forbidden primary-factor packing pattern?

## Claim boundary

This result uses admitted donor `D_k/eta` constants and the previously committed C45 compatibility reductions. It does not prove `D(C_45^3)=133`, classify all maximal zero-sum-free sequences in C15^3, or establish novelty authority.
