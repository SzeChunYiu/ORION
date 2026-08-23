# X1-D finding — exact local correction criterion for one short quotient atom plus two residual indices

Date: 2026-08-22
Branch: `shadow/orion-rg-rg0-finite-regime-geometry`
Successor to superseded #909

## Setting

Let `Q=C_5^3`. Let

`B = b_1 ... b_m`, `1 <= m <= 5`,

be a **minimal nonempty zero-sum sequence** in Q (a short quotient atom), so `sigma(B)=0` and B has no nonempty proper zero-sum subsequence.

Let `r,s in Q` be two additional quotient terms not used by B.

We ask whether `B r s` contains a quotient-zero-sum subsequence C distinct from B and using at least one of the residual terms r,s.

## Exact criterion

Any such C has exactly one of three residual patterns.

### Uses r but not s

Then `C=A r` for a subsequence `A | B`, and

`sigma(A) = -r`.

### Uses s but not r

Then `C=A s`, with

`sigma(A) = -s`.

### Uses both r and s

Then `C=A r s`, with

`sigma(A) = -(r+s)`.

Conversely, any subsequence A of B satisfying one of these three equations yields the corresponding quotient-zero-sum correction.

Because B is a minimal zero-sum atom, the only zero-sum subsequences of B itself are the empty subsequence and B. Therefore every genuinely new one-block correction using the residual pair is completely determined by whether one of

`-r`, `-s`, `-(r+s)`

belongs to the subset-sum set

`Sigma(B) = { sigma(A) : A | B }`.

If the representing A is empty or all of B, the resulting correction may be a residual-only block or B plus residual terms; these are still legal and can be handled explicitly by the same equations.

## Kernel correction bookkeeping

In the split C45 representation, every source term has quotient coordinate in Q and kernel coordinate in `K=C_9^3`.

For a fixed quotient representation A of one of the three target values, the replacement block's kernel sum is the sum of the kernel coordinates of A and the selected residual terms. Hence the set of attainable **kernel** corrections is obtained by enumerating only the subset representations of the three quotient targets, not all set partitions of `B union {r,s}`.

For `|B|<=5`, there are at most `2^5=32` subsequences of B. Thus each one-block E0/E1 local correction state is exactly finite and tiny.

## Research consequence

The stronger residual-two packing reduces the first correction problem to 21 independent local atoms B_i and one residual quotient pair r,s. A quotient-level failure occurs precisely when all three target values avoid the subset-sum set of every candidate B_i (or when all corresponding kernel corrections remain trapped in the exceptional affine C9 coset).

This gives two separate obstruction coordinates:

1. **QUOTIENT_ISOLATION** — no atom B_i represents any of the three target values;
2. **KERNEL_COSET_TRAP** — quotient corrections exist but every attainable kernel correction remains inside the donor exceptional coset.

They should not be conflated in the next theorem/counterexample search.

## Claim boundary

This is elementary subset-sum bookkeeping in C5^3. It is a programme-state compression, not a novelty claim. Any new result must prove that one of the two obstruction types cannot persist globally, or classify a genuine persistent obstruction.
