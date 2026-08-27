# ORION-05 R11 sparse direct-solver development packet

Date: 2026-08-27
Base: `main@63c36a20c8120fcd45469bbe5708b9e9aadfe923`
Parent issues: #1511, #1518, #1523
Donor draft: #1524 (theorem candidate only)

## Atomic development questions

1. Is the number of ordered anticommuting phase-ignored Pauli pairs whose two
   members each have support at most two exactly
   `54*n^3 - 108*n^2 + 60*n`?
2. Can those pairs be generated directly, without scanning the quadratic
   cross-product of all support-two Paulis?
3. Do three such pairs contain every growing frame choice in the frozen R6M
   six-slot grammar?
4. Can a minimum compatible shared Tag be confined to the six-frame active
   union, and can that Tag be solved without any `n`-dependent oracle?
5. Can target-dependent Restore cost be reduced to an `O(n)` identity-frame
   baseline plus a constant-size correction?
6. Does a new implementation using only those facts reproduce the exact
   optimum and a valid optimum witness of the frozen 512-state referee on a
   complete feasible small-`n` domain and the registered support-one boundary?

## Recovered incumbent and adverse history

- The frozen 512-state R6M XOR dynamic program remains the unrestricted exact
  referee. This work does not change or optimize that implementation.
- The R6S theorem establishes that an optimum exists with every frame support
  at most two for the frozen grammar/objective.
- The R6O/R6P sharpness witness must remain adverse to a support-one claim:
  unrestricted/support-two cost `5` is strictly below complete support-one
  cost `6` on the registered two-qubit instance.
- The original raw six-frame count was `O(n^12)`. Generic bounded-locality
  anticommuting-pair counting receives no novelty credit.
- Convergence V1 remains immutable. The Round-1 status file in this packet is
  an explicit, source-bound additive delta that takes precedence only after
  the packet is reachable from `main` and the merged-main workflow passes.
- PR #1498 remains open adverse custody for the old direct D++ implementation:
  372/372 sampled `n<=5` cells completed exactly, while 12/12 sampled `n=6`
  cells timed out at 600 seconds. Its P6/wrapper authority is defective, the
  raw receipt is unchanged, and it neither refutes this sparse solver nor
  establishes production acceleration.

## Bounded saturation assessment

### Knowledge

The relevant frozen sources are the R6M protocol and implementation, the R6S
exchange theorem, the R6O support-one refutation, and the R6P finite D++
closure. They expose all objective terms and all nine parity constraints.

### Search universe

The implementation search is limited to exact direct enumeration of the
R6S-certified support-two normal form. It includes constructive pair
generation, active-union Tag solution, baseline/correction scoring, constant
matching/permutation/central choices, and final witness reconstruction. It
excludes heuristic pruning, production-runtime benchmarking, hardware costs,
generic TARE, and protected Task-3 paths.

### Formulation

The claimed algorithmic object is exact optimum cost plus one separately
verifiable sparse witness for the frozen six-slot R6M grammar under its frozen
support-count objective. Equality of serialized tie-break bytes with the
historical referee is not part of the mathematical object; two optimum
witnesses are equivalent when each is feasible and separately recomputes
the same exact optimum.

## Challenge to the saturation basis

The candidate is false if any target-, Tag-, Restore-, phase-, matching-, or
central-choice dependency requires scanning an unbounded set inside a frame
triple. The verifier therefore checks source independence, complete `n=1`
configuration/orientation equality, hostile `n=2` witnesses, full-versus-
restricted Tag minima, and full-scan-versus-baseline Restore equality.

## Why an earlier search could have missed this route

The historical D++ enumerator materializes `4^(2n)` pattern tables and sweeps
all `n`-qubit Tags. Those implementation choices hide the fact that
anticommutation forces pair overlap and that Tag constraints read only the
constant-size frame union.

## Frozen implementation hypothesis

After linear target preprocessing, three directly generated ordered
anticommuting support-two frame pairs, a 64-state Tag-syndrome solve over at
most nine active coordinates, and active-coordinate Restore corrections form
an exact `O(n^9)` optimizer for the frozen grammar. The implementation must not
import or call the 512-state production DP.

## Reopen triggers and honest terminals

- Pair count or generator mismatch:
  `ORION05_R11_PAIR_GENERATOR_COUNTEREXAMPLE`.
- Exact-cost or witness mismatch:
  `ORION05_R11_RUNTIME_THEOREM_COUNTEREXAMPLE`.
- Hidden `n`-dependent work inside candidate evaluation:
  `ORION05_R11_PAIR_COUNT_ONLY__RUNTIME_HIDDEN_DEPENDENCY`.
- Frozen source or authority cannot be reconstructed:
  `CANNOT_CHECK_FROZEN_R6M_EQUIVALENCE`.
- All obligations close:
  `ORION05_R11_EXACT_O_N9_DIRECT_SOLVER_THEOREM__FROZEN_R6M_ONLY`.

No terminal authorizes generic TARE, production-DP acceleration, hardware or
physical-resource advantage, novelty, venue, or submission claims.
