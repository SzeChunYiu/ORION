# Negative-to-positive conversion ledger

Live scoring of the reopen adjudication's derived moves. A prediction that fails is
recorded as failed. Authority: development record; converts nothing by itself.

| # | negative | predicted move | lane | outcome |
|---|---|---|---|---|
| N1 | comm-s2 pinned sector open (QG-7c/7d) | FAILED_DECOMPOSITION → change the decomposition, not the menu | QG-7e | **CONVERTED — theorem complete.** But the *prediction was wrong*: E1's decomposition attack was refuted by exact enumeration (10 of 12 states admit no Δ≤0 alternative at all, so it was a local-optimality failure, not a descent failure), and what closed it was a **menu enlargement** — admitting all eight per-block target-permutation subsets where QG-7d realized only the global mirror. Scored against the adjudication. |
| N2 | StabPrep boundary unseparable at any budget | FAILED_DEFINITION → redefine the vocabulary | QG-15c | running |
| N3 | no support-2 phase witness; exact tie on 4,896 at O_nc_out | INACTIVE_NO_ATOM_CONDITION → solve for the tie locus | QG-17b | running |
| N4 | prospective forecast refuted at n=4 | FAILED_DEFINITION → make n-dependence explicit | — | not yet chartered |
| N5 | syndrome rank 5 vs κ_R6I = 1 (sound but loose) | UNRESOLVED → measure rank − κ across families | QG-20 | running |
| N6 | novelty freezes authored without literature access | DONOR_SUBSUMPTION RISK → hostile external-novelty lane | QG-19 | not yet chartered |
| W5 | no real-chemistry trade regime found | — | R7 | **EXECUTED — honest negative that confirms prospectively.** Census extended to 180 matchings at 12/14/16 qubits, all donor-exact; six genuinely unread 16q batches admitted. Successor is an O1-style re-freeze, not a harder hunt. |
| W8 | R6B batch selection taken on the receipt's word | — | — | registered by the QG-3 verifier's stated limit |

## What N1 costs the method finding

The adjudication's method finding — "all six prior conversions identified the wrong
OBJECT, never merely an insufficient search; enlarging move menus failed repeatedly while
redefinition succeeded repeatedly" — predicted N1 would need a decomposition change. It
did not. A menu enlargement closed it, and the decomposition attack was exactly refuted.

So the finding is a **heuristic with a counterexample**, not a law. The honest refinement:
a negative can be an insufficient search when the search fails to realize a degree of
freedom its own protocol already declares. That is what happened here — `dxx_search`
enumerates the per-block permutation independently per block, QG-7d's protocol says so,
and its menu implemented only 2 of the 8 subsets. Worth checking for in every lane that
stalls: *does our menu realize everything our own protocol claims as free?*
