# ORION-05 Round 2: production-faithful exact-search benchmark

**Status:** `FROZEN_BEFORE_OUTCOME`  
**Base:** `main@27ea5e1b04dbed853b7ddba60c8bf736ef087bf5`  
**Round:** 2 of at most 3

## Question

Does the support-at-most-two solver established in Round 1 provide measured
production exact-search value against the existing unrestricted 512-state R6M
referee when both optimize the identical frozen structural objective?

This is deliberately not a comparison to the defective old D++ wrapper in
PR #1498. Its 372 exact cells and twelve n=6 timeouts remain adverse custody;
they neither support nor refute this prospective comparison.

## Frozen subject and panel

The production subjects are the already source-bound H4 (8 qubits) and
equilibrium N2 (12 qubits) R6M six-term batches. The committed R6M receipt is
the target source; target identities are reconstructed consistently across all
15 committed matching witnesses before measurement.

For each subject, canonical matching indices 0, 7 and 14 are fixed. Each is run
at least-significant-coordinate projections 1, 2, 3 and the full subject.
Projections 1 and 2 form the correctness panel. Projection 3 and the full
subject form the scale panel. No matching or projection may be selected after
seeing performance.

Every completed cell has three fresh measured repetitions. A timed-out cell has
one censored attempt. The per-attempt wall limit is 120 seconds.

## Matched semantics

Both algorithms optimize exactly `C_R6M`: three anticommuting frame pairs, one
common Tag, four relative B/C target orders, eight central choices and the
frozen Restore factor rule. Each cell fixes one matching. The support-two lane
completely enumerates its constructive ordered-pair cube; the unrestricted lane
uses the complete arbitrary-frame/Tag 512-state XOR DP. Coefficients are absent
from both structural objectives.

## Predeclared measurements

- exact objective and independent witness validity;
- exact planned states/nodes;
- wall time and CPU time;
- peak resident set size;
- separate witness-verification time;
- completion versus timeout.

Measured attempts are fresh single-process children pinned to one logical CPU.
Raw JSONL and the deterministic aggregate are both retained. Timed-out or
adverse rows are never rewritten.

## Decision

`ORION05_R12_PRODUCTION_EXACT_SEARCH_VALUE_PASS` requires all source and
correctness gates, completion of all six full-subject support-two cells, and at
least a 25% median improvement in wall time, CPU time or peak RSS over the
unrestricted referee. No other resource median, including witness verification,
may regress by more than 10%.

`ORION05_R12_EXACT_BUT_NO_PRODUCTION_VALUE` is emitted when all validity
preconditions hold but that positive rule fails, including any support-two
full-subject timeout.

`ORION05_R12_CANNOT_CHECK_MATCHED_PRODUCTION_VALUE` is emitted for binding
failure, unrestricted-referee timeout, unresolved exact-objective disagreement,
or independent-witness failure.

Any valid terminal consumes Round 2. A null opens only the predeclared distinct
Round-3 safe-ordering/parallelism mechanism; it does not permit parameter
retuning of this benchmark.

## Authority ceiling

No result here establishes generic TARE complexity, physical or fault-tolerant
resource value, production advantage outside frozen R6M, novelty, external
independence, journal authority or submission readiness. Protected Task-3/P9 is
outside scope and unchanged.

The machine-readable JSON beside this file controls exact hashes, panel fields,
thresholds and terminals.
