# X1-C finding — nested exact one-block structure inside maximal C_15^3 kernel sequences

Date: 2026-08-22
Branch: `shadow/orion-rg-rg0-finite-regime-geometry`
Parent issue: #901

## Setting

In the live P3 route for `C_45^3 -> C_3^3`, a hypothetical length-133 zero-sum-free source sequence yields a 42-block quotient packing whose lifted block sums form a maximal zero-sum-free sequence

`H = h_1 ... h_42`

over the kernel

`K = C_15^3`.

Here `|H|=42=d(C_15^3)` because `D(C_15^3)=43` is donor-known.

By CRT,

`C_15^3 ≅ C_3^3 ⊕ C_5^3`.

Project H to the `C_3^3` factor.

## Exact nested block count

Freeze--Schmid / Bhowmik--Schlage-Puchta give

`D_12(C_3^3)=42`.

Therefore the 42 projected terms admit at least 12 pairwise-disjoint nonempty zero-sum blocks.

They cannot admit 13 such blocks. Indeed, if there were 13 quotient-zero-sum blocks, take their lifted block sums in the complementary `C_5^3` factor. Since

`D(C_5^3)=13`,

some nonempty subcollection of those 13 lifted sums would add to zero in `C_5^3`. The same subcollection is already zero in the `C_3^3` projection, hence yields a nonempty zero-sum subsequence of H in `C_15^3`, contradicting zero-sum-freeness of H.

Thus the maximum number of disjoint `C_3^3` quotient-zero-sum blocks inside any maximal zero-sum-free H is **exactly 12**.

## Maximal second-stage lift sequence

Fix any 12-block packing of the projected H and let

`g_1,...,g_12 in C_5^3`

be the corresponding second-stage lifted block sums.

The sequence `G=g_1...g_12` must be zero-sum-free: any nonempty zero-sum subcollection in `C_5^3`, combined with the quotient-zero-sum property of the selected blocks in `C_3^3`, would give a zero-sum subsequence of H.

Since `d(C_5^3)=12`, G is a **maximal zero-sum-free sequence** in `C_5^3`.

Consequently its nonempty subsequence-sum set equals every nonzero element of `C_5^3`: for any nonzero `x` not representable by G, appending `-x` would create a zero-sum-free sequence of length 13, contradicting `D(C_5^3)=13`.

## Hierarchical state reduction

Every maximal 42-term zero-sum-free kernel sequence `H` arising in the P3 C45 route therefore admits an exact two-level block hierarchy:

`H (42 terms in C15^3)`
` -> 12 disjoint zero-sum blocks in C3^3`
` -> 12 maximal zero-sum-free lift sums in C5^3`.

The first level has an exact one-block deficit (`12` available versus `13` needed by ordinary Davenport induction); the second-level lift sequence has complete nonzero subsequence-sum coverage.

This does not by itself prove any missing-sum-coset theorem for `C_15^3`, because a desired correction may have a nontrivial `C_3^3` component and block exchanges may change the nested packing. But it gives a rigorous, finite hierarchical state that every maximal kernel sequence must carry.

## Research consequence

The live mixed-kernel question can be reframed from arbitrary 42-term `C_15^3` zero-sum-free sequences to a hierarchical obstruction:

1. an exact 12-block packing of the `C_3^3` projection;
2. a maximal `C_5^3` lift-sum sequence with complete nonzero subsequence-sum coverage;
3. the compatibility constraints between top-level C45 quotient-block exchanges and this nested packing.

A possible breakthrough lemma would show that the nested hierarchy always supplies a lift-compatible correction for the missing top-level block, or else classify the exact obstruction preventing such a correction.

## Donor / claim boundary

CRT decomposition, `D_12(C_3^3)=42`, `D(C_5^3)=13`, and the standard maximal-zero-sum-free subsequence-sum coverage argument are donor mathematics. This note records their exact composition in the live C45 proof state. No novelty or theorem authority is claimed.
