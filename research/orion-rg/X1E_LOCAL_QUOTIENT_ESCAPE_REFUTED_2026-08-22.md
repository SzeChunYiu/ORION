# X1-E exact counterexample — no universal local quotient escape from one atom plus two residual terms

Date: 2026-08-22
Branch: `shadow/orion-rg-rg0-finite-regime-geometry`
Parent issue: #912

## Candidate local implication refuted

False candidate:

> For every minimal short zero-sum atom B in `C_5^3` and every two residual quotient terms r,s, the union `B union {r,s}` contains a quotient-zero-sum correction distinct from B and using at least one residual term.

## Exact counterexample

Let `e_1,e_2,e_3` be the standard basis of `C_5^3`.

Choose the length-2 zero-sum atom

`B = (e_1, -e_1)`.

Its complete subset-sum set is

`Sigma(B) = {0, e_1, -e_1}`.

Choose residual quotient terms

`r=e_2`, `s=e_3`.

By the committed local correction criterion, a new correction using the residual pair exists iff one of

`-e_2`, `-e_3`, `-(e_2+e_3)`

belongs to `Sigma(B)`.

None does, by linear independence of the standard basis. Therefore `B r s` contains no quotient-zero-sum correction distinct from B which uses r and/or s.

## Consequence

The X1-E theorem cannot be proved from a universal one-atom local lemma. `QUOTIENT_ISOLATION` is a genuine local phenomenon.

Any all-sequence C45 escape theorem must use at least one additional source of structure:

- global restrictions imposed by source zero-sum-freeness;
- the existence/choice of many (21) short atoms simultaneously;
- adaptive selection of the residual pair from a larger residual;
- Property-C/D structure near the C5^3 eta boundary;
- more than one atom in the exchange; or
- a different packing/primary projection.

The frozen X1-E E1 language remains valid as a search protocol, but a positive theorem must explain why the simple local obstruction cannot persist globally in a hypothetical 133-term source counterexample.

## Claim boundary

This is an elementary exact counterexample, not a novelty claim. Its scientific value is to remove an invalid proof route before costly search.
