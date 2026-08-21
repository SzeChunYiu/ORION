# QG-9 T1 — exact n=4 cap-3 tightness witness protocol

Issue: SzeChunYiu/ORION#793
Frozen base: `afe7994bd5e362b2e8d40482f2dde9689e6ef708`
Branch: `shadow/orion-qg-qg9-t1-support4-tightness`
Status: FROZEN BEFORE CAP3 OUTCOME.

Recompute the 36 E2/E3-uncovered anchored support-four structural slices per generator orientation directly from production R6I semantics. For each structural type choose the lowest local Tag-support realization, lexicographic tie-break. For each obstruction build a desired rank-2 block; choose the other block by exhaustive n=4 rank-2 frame search minimizing `(Uanti,total frame support,lex)` under the same ordered shared-Tag labels. Targets equal desired frame triples, so desired Restores are identity. Up to 36 candidates/orientation, canonical order, no cap3 call during generation.

For each candidate, exact cap3 is a SciPy/HiGHS MILP over the production 4,096 local R6I options for each fixed one of 54 `(B permutation,cA,cB)` configs. Local options are exactly compressed by `(10-bit parity delta, four-generator activity mask)`. Constraints: one option/qubit; exact accepting parity via six-state selector and integer parity carries; four generator-support sums <=3. Integer objective is production raw local cost minus UANTI_CONSTANT after solve. `mip_rel_gap=0`, optimal status and constraint/integrality residuals required.

Early reject candidate once any exact fixed config has `C_cap3<=U4`. A positive requires all 54 fixed configs solved optimally and global `C_cap3>U4`. Then `C_DP<=U4<C_cap3`, which is sufficient to prove support four necessary on that instance; the support-four feasible witness need not itself be globally optimal.

Generic ORION independently reconstructs the frozen candidate list and, for every negative candidate, reruns its exact rejection configuration; for a positive it reruns all 54 configs from an independent mathematical R6I option model. Native ORION-Q separates TIGHT_WITNESS / NO_WITNESS / SOLVER_CANNOT_CHECK / BINDING_FAILURE.

Terminals:
- `QG9T1_R6I_SUPPORT4_TIGHT_WITNESS_EXACT`
- `QG9T1_NO_SUPPORT4_TIGHT_WITNESS_IN_FROZEN_PANEL`
- `QG9T1_CAP3_SOLVER_CANNOT_CHECK`
- `QG9T1_CANDIDATE_BINDING_FAILURE`

No chemistry/protected subject/network. No support<=3 theorem from a finite negative scan. Novelty authority false; no physical quantum-advantage claim.
