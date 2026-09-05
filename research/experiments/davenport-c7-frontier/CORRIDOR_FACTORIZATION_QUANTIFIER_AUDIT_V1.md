# Corridor factorization quantifier audit — V1

Status: **corrected proof scope**. The six-pattern argument for a hypothetical length-37 obstruction in `C_7^3` establishes the existence of a selected factorization. It does not establish the same length restriction for every factorization.

## 1. The gap

`ATOM_LENGTH_CORRIDOR_V1.md` originally said that every three-atom factorization belongs to its six-pattern list. Its proof instead chooses a shortest atom `A` in the full sequence and uses short-zero donor theorems to choose a shortest atom `U` in the complement. The third atom is the remaining complement. These choices prove an existential conclusion.

For example, knowing that a total-zero complement of length 29 contains an atom of length at most ten does not show that both atoms in an arbitrarily preselected factorization have lengths ten and nineteen. The short atom might belong to another factorization. This identifies a logical gap; it does not construct a length-37 obstruction or assert that any excluded triple is actually realizable.

## 2. The proved replacement

Under exactly the stated donor hypotheses, a hypothetical zero-sum sequence `B` of length 37 and packing number at most three has a factorization obtained by:

1. choosing a shortest atom `A` in `B`;
2. choosing a shortest atom `U` in `BA^{-1}`;
3. taking the remaining zero-sum complement as `V`.

The packing bound makes the last complement an atom. The displayed proof then puts the sorted lengths of this selected factorization in the six-pattern list. Both the theorem statement and the choice in its proof now say this explicitly. The older cross-context checkpoint has the same correction.

This existence statement is enough for a covering strategy: eliminating every candidate pattern for the selected factorization would eliminate the obstruction. It is insufficient for rejecting an arbitrary alternate factorization merely because its lengths are absent from the list.

## 3. Consequences and scope

The prime-uniform arithmetic list for factorizations that contain a maximal atom is unaffected: its length identity is derived directly from the total length and the maximal length. The local short-free pair theorems are also unaffected; their statements include the pair hypotheses they use.

The audit was performed while testing a new relation certificate of length `m+1`. That certificate cannot be rejected solely because a resulting alternate factorization lies outside the selected six-pattern list. The failed inference is preserved here to prevent its reuse.

This correction neither proves nor disproves the full first corridor or `D_3(C_7^3)`. It reduces the recorded authority to what the existing proof establishes.
