# X1-C donor provenance repair — use the reconstructed Z3⊕Z3⊕Z3d proof, not the 2007 exposition uncritically

Parent: #901. Committed before downstream use.

## Finding

The theorem

`D(Z_3 ⊕ Z_3 ⊕ Z_(3d)) = 1 + d*(Z_3 ⊕ Z_3 ⊕ Z_(3d))`

for all positive integers d remains a valid donor input for X1-C, in particular giving

`D(C_15^3)=43`

via the homocyclic specialization `C_15^3 ≅ Z_3 ⊕ Z_3 ⊕ Z_45` under the relevant invariant-factor/isomorphism identification used in the donor family map.

However, the original Bhowmik--Schlage-Puchta 2007 exposition should not be treated as the sole proof-quality authority.

## Reconstructed source

Aleen Sheikh, *The Davenport Constant of Finite Abelian Groups*, PhD thesis, Royal Holloway, University of London, 2017, Chapter 4.

The thesis states that it reconstructs the proof of the equality for `Z_3 ⊕ Z_3 ⊕ Z_(3d)` for arbitrary positive d. It explicitly records that:

- there are places in the original proof where the details were not convincing to the author;
- the original argument appeared to explicitly cover only the coprime-to-6 case without writing out additional complications;
- at least one statement in the original proof is incorrect (the thesis points to its Remark 4.3.11);
- the chapter modifies notation/preliminaries and supplies a version intended to establish the theorem for all d.

Royal Holloway metadata identifies the thesis as Aleen Sheikh (2017), supervised by Simon Blackburn.

## Research discipline consequence

For X1-C:

1. use the **theorem** `D(C_15^3)=43` as donor-owned;
2. when a proof step depends on detailed residual combinatorics from the 2007 paper, cross-check it against the reconstructed thesis or independently verify the local statement;
3. do not infer that every intermediate lemma/formulation in the 2007 exposition is reliable merely because the final theorem is accepted;
4. preserve any discrepancy as donor-proof provenance, not as an ORION counterexample to the theorem.

## Why this matters for the current frontier

X1-C is reusing fine-grained ingredients such as the `C_3^3` residual classifications and deficiency-one block arguments. Those local objects must be independently bound rather than inherited wholesale from the final theorem citation.

The already-committed Proposition-8 / Lemma-2 specializations were separately inspected and remain the operative local donor statements unless a later audit reopens them.

## Claim boundary

This is a provenance/reliability correction only. It does not alter the current C45 target, prove a new theorem, or grant novelty authority.
