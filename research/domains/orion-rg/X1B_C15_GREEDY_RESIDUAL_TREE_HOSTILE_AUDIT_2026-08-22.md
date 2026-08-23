# X1-B hostile audit — correction to the C15 greedy residual tree

Parent: #900.
Status: **PROOF-ASSEMBLY CORRECTION — committed before any full C15 theorem claim.**

## Problem found by hostile donor audit

The earlier reduction packet `X1B_C15_RESIDUAL_REDUCTION_TO_13_AND_10_2026-08-22.md` organized the hard cases by greedily removing quotient zero-sums of length 3 and retained only residual sizes 16, 13, and 10.

For the full proof, however, the natural safe greedy procedure removes quotient zero sums of **length at most 3**, because a quotient zero sum of length 1 or 2 is also a valid block. A length-2 removal changes the residual-size congruence and creates one additional hard case.

Therefore the statement that only 13-point and 10-point interfaces remain was too strong as a complete end-to-end reduction. The already proved 13-point and 10-point closure packets remain valid for those interfaces, but they do not exhaust the full greedy tree.

## Correct block-count analysis

Start with 43 projected positions in `C_3^3`. Greedily remove pairwise-disjoint nonempty quotient zero-sum blocks of size at most 3 until the residual R contains no quotient zero sum of size at most 3.

Let m be the number of removed blocks. Since the short-zero-sum constant is 17, the terminal residual has `|R|<=16`. Since every removed block has size at most 3,

`43-3m <= |R| <= 16`,

so `m>=9`.

If `m>=13`, the 13 removed quotient blocks already force a kernel zero sum by `D(C_5^3)=13`, so a counterexample must have `m<=12`.

Thus `m in {9,10,11,12}`. To reach 13 quotient blocks total, R would need `13-m` disjoint quotient zero sums.

### m=12

Need one residual zero sum. Since `|R|>=43-36=7` and `D(C_3^3)=7`, this closes.

### m=11

Need two residual zero sums. Since `D_2(C_3^3)=11`, every case with `|R|>=11` closes. The only survivor is

`|R|=10`,

which forces total removed size 33, hence all eleven removed blocks have size 3. This is exactly the separately closed k=3 / 10-point branch.

### m=10

Need three residual zero sums. Since `D_3(C_3^3)=15`, all cases with `|R|>=15` close.

Two sizes can survive the generic threshold:

- `|R|=13`: total removed size 30, hence all ten blocks have size 3. This is the separately closed k=4 / 13-point branch.
- **`|R|=14`: total removed size 29, hence exactly nine removed blocks have size 3 and one removed block has size 2. This branch was omitted previously.**

### m=9

Since `|R|<=16` but also `|R|>=43-27=16`, necessarily `|R|=16`, and all nine removed blocks have size 3. Four residual blocks are needed.

The donor `C_3^3` extremal argument closes this 16-point branch quotient-only, as recorded in the earlier reduction packet.

## Donor classification of the missing 14-point branch

Bhowmik--Schlage-Puchta Proposition 8 states that for `k>=3`, every multiset of size `3k+5` failing to contain k disjoint zero-sum subsets has the specified seven-point extremal construction.

For `k=3`, this is exactly size 14. Thus every 14-point residual with packing number below 3 lies in the donor-classified `D_3(C_3^3)=15` extremal layer.

The paper's Lemma 2 supplies the corresponding 14-point double-seven configuration and its uniqueness up to linear equivalence under the relevant no-short-zero-sum extremal conditions.

Hence the missing branch is a **small donor-classified quotient interface**, not an unbounded new family.

## Correct live residual tree

Before a full `D(C_15^3)=43` proof can be claimed, the hard interfaces are now:

1. 10-point residual, 11 fixed triples — independently closed;
2. 13-point residual, 10 fixed triples — independently closed;
3. **14-point residual, 9 fixed triples + 1 fixed quotient-zero-sum pair — OPEN at this checkpoint;**
4. 16-point residual — donor/quotient-only closed.

## Authority correction

- The committed k=3 / 10-point theorem remains valid for that branch.
- The committed k=4 / 13-point theorem remains valid for that branch.
- Neither should be described as exhausting the whole C15 proof until the 14-point branch is closed.
- No full C15 theorem or breakthrough claim is authorized at this checkpoint.

This correction supersedes only the *exhaustiveness* statement of the earlier residual-reduction packet; historical files remain unchanged for auditability.