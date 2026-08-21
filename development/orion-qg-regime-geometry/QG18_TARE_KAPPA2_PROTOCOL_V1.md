# QG-18 TARE intrinsic support number — protected closure protocol

Status: FROZEN BEFORE QG-18A EXECUTION.
Issue: #838 (parent #835, programme #740).
Frozen base: `c5ba39fef4f25c46de5fb69bf07f50530f4693ca`.

## Question
Does the frozen unit-objective R6M/TARE grammar have intrinsic frame-support number 1 or 2?

## Exact implication under test
1. R6S already proves `C_DP = C_D++` for every n, where D++ is the complete family with every frame Pauli support <=2.
2. Production `r6p.dxx_search(..., max_weight=1)` is the complete support<=1 family: `_DxxTables` enumerates every ordered nonzero anticommuting Pauli pair whose members have `wt<=1`, and minimizes the shared Tag and Restore factoring exactly.
3. QG-7's first protected fourth-regime witness records `C_DP=C_D++=7`, `C_Dplus=8`, and `C_Dplus` is computed by the same `dxx_search(...,max_weight=1)`.
4. Therefore a fresh independent replay of that witness with `C_DP < C_cap1` proves support 1 is not universally sufficient. Together with R6S, exact intrinsic support is 2.

## Frozen witness selection
Use exactly the first row of `QG7_BPRIME_COMPLETENESS_RESULTS.json -> arm1_hostile_search.fourth_regime_candidates_verbatim`. No alternative row may be selected after outcome.

## Gates
- bind QG-7 receipt digest/terminal and require the selected row to be replay-confirmed;
- require target `n=3` and recorded values `(C_DP,C_Dxx,C_Dplus)=(7,7,8)`;
- production cap1: `dxx_search(target_pairs,3,max_weight=1,want_witness=True)` must return 8;
- independent cap1 enumerator, implemented without calling `dxx_search`, must also return 8;
- production D++ with `max_weight=2` must return 7 and witness verify;
- unrestricted production DP must return 7 with exact matching checks green;
- R6S authority/gates must bind and state all-n `C_DP=C_D++`;
- generic ORION and native ORION-Q must independently accept;
- no chemistry source or protected stretched-N2 access; novelty/R6/physical-advantage authority false.

## Terminal
Positive: `QG18_TARE_KAPPA_IS_2__SUPPORT2_NECESSITY_WITNESS_MACHINE_VERIFIED`.
Honest alternatives: parent-binding failure, cap1 disagreement, exact replay failure, generic/native disagreement, `CANNOT_CHECK`.
