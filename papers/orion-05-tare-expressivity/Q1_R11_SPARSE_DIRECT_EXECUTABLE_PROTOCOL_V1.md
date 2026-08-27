# Q1 R11 sparse-direct executable gate — prospective protocol V1

Date frozen: 2026-08-27  
Owners: #1518 / #1511  
Authority at freeze: theorem candidate only; `Q1_R11_EXACT_O_N9_DIRECT_SOLVER_THEOREM` is **not** yet earned.

## Question

Does the R11 theorem candidate admit an executable exact optimizer for the frozen R6M six-slot grammar whose own source contains no import/call of the historical 512-state R6M DP, no full `4^n` Tag sweep, and no `4^(2n)` pattern table, while reproducing exact optima on a frozen hostile battery?

## Frozen implementation contract

The new solver must:

1. represent every support-`<=2` frame sparsely as at most two `(qubit, local-letter)` entries;
2. generate ordered anticommuting pairs constructively from the overlap cases in the theorem candidate and reproduce `B(n)=54n^3-108n^2+60n`;
3. preprocess the six target-local letter arrays and four B/C-permutation identity-frame Restore baselines in `O(n)`;
4. evaluate one frame triple by corrections on the union of the six frame supports only (`|U|<=9`);
5. solve the six shared-Tag equations with a 64-state syndrome DP over `U` only;
6. enumerate the three frame pairs directly; pruning may use only lower bounds plus a cost of an actually found feasible witness;
7. never call an unrestricted solver/oracle from inside candidate evaluation.

Central choice may be minimized analytically per pair because it changes only the direct frame multiplier and not Tag or Restore semantics. B/C target permutations remain explicitly enumerated.

## Frozen verification denominator

### A. Structural checks

- independent no-ORION-import pair/count/Tag/active-union checker from #1524;
- source scan forbidding R6M/R6P optimizer imports, global Tag enumeration, and exponential pattern-table construction;
- generated pair count for `n=1..6` must equal `[6,120,666,1968,4350,8136]`;
- every generated pair is nonzero, support `<=2`, anticommuting, duplicate-free, and has union size `<=3`.

### B. Complete one-qubit universe

All `3^6 = 729` six-target instances whose six target letters are independently chosen from `X,Z,Y`, grouped by the fixed matching `((0,1),(2,3),(4,5))`.

For every one of the 729 instances:

- sparse-direct optimum must equal an independent exhaustive local `4^7` grammar enumeration;
- returned witness must independently recompute to the optimum;
- max frame support must be `<=2`.

This universe is fixed by the protocol, not sampled after outcome access.

### C. Frozen R6M-DP hostile equality

Compare sparse-direct cost and a self-verified sparse witness against the frozen R6M DP on:

- the three existing n=1 hostile panels: `n1_identical`, `n1_swapped`, `n1_mixed`;
- the two existing n=2 hostile panels: `n2_a`, `n2_b`;
- QG7 `H1_n3` local-index `2` (recorded `C_DP=7`, support-two witness);
- QG7 `H1_n3` local-index `5` (recorded `C_DP=7`, a second support-two-needed row).

The QG7 rows are identified by their already committed target-pair bytes; they may not be replaced if slow or adverse.

## Hostile controls

- pair generator count is checked both formulaically and by duplicate-free emitted identities;
- a deliberately full support-product count is rejected as the registered pair object;
- Tag solver reports the maximum active-union size actually encountered and must never exceed 9;
- the executable gate rejects any source-level dependency on the historical R6M DP or D++ solver;
- support-one-only initialization is retained only as a feasible incumbent; the final support-two search must be able to improve it on the QG7 rows;
- every reported best witness is rescored from sparse frames, Tag and target letters rather than trusted from the search accumulator.

## Resource accounting

Report, per verification case where material:

- ordered pair count;
- support-one incumbent cost;
- support-two optimum cost;
- frame triples visited;
- frame triples pruned by the direct-cost lower bound;
- candidates reaching the bounded Tag DP;
- maximum active-union size;
- wall time.

These are implementation/replay resources only. They are not physical quantum resources and do not establish production value.

## Terminals

- `Q1_R11_EXACT_O_N9_DIRECT_SOLVER_THEOREM` — every frozen structural and equality gate passes;
- `Q1_R11_PAIR_COUNT_ONLY__RUNTIME_HIDDEN_DEPENDENCY` — pair theorem survives but executable source needs an n-growing hidden dependency;
- `Q1_R11_RUNTIME_THEOREM_COUNTEREXAMPLE` — sparse solver disagrees with an exact frozen oracle/brute result;
- `CANNOT_CHECK_FROZEN_GRAMMAR_EVALUATION_COST` — exact identity cannot be established in the frozen environment.

A positive Round-1 terminal closes only the algorithmic theorem gate. It does **not** establish material production/resource significance; Round 2 remains separately governed by #1511.
