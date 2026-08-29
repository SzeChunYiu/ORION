# Checker notes — check_global_obstruction_basis_v1.py

Design date 2026-08-28. Checks output of the frozen campaign
`ORION05.GLOBAL_OBSTRUCTION_BASIS.v1` (branch `science/o05-obstruction-basis-v1`,
freeze commit `1404c56cd`). Validated locally: `py_compile` clean; `--self-test`
(synthetic rows only, zero solver calls) passes all five scenarios —
clean→0, corrupted row outcome→2, mis-graded terminal→2, corrupted control
block→2, malformed input→3.

## Independence boundary: re-derived vs shared

**Re-derived from the frozen texts (no runner import, no solver import):**
- Pauli letter algebra: `lsy`, `lmul` from the production convention
  `I=0,X=1,Y=2,Z=3` with symplectic coordinates `((0,0),(1,0),(1,1),(0,1))` —
  a frozen mathematical definition restated in the solver header and THEORY §1.
- `F_3` Restore rule, frame multipliers `(2,4)` by central choice
  (`m0,m1 = (2,4) if central==0 else (4,2)`, cost `m*(w-1)` per member),
  Tag cost `2·w(S)` — from the manuscript objective and THEORY §1.
- Census enumeration + input hashing (THEORY D1 / PROTOCOL instance_family).
- Slot mapping for Restore recomputation: matching pairs in canonical order →
  blocks A,B,C; permutations swap within B and C only, A never swapped; slot
  order `a0,a1,b0,b1,c0,c1`; branch 0 = slots 0,2,4, branch 1 = 1,3,5. Read
  off the PAPER solver's `_ordered_variants`/`restore_cost_full_scan` source
  (frozen paper artifact — this is the definition of the recorded fields, not
  runner judgment).
- Branch roles f0/f1 by Tag label (THEORY D4), coordinate classes (α,β)
  (THEORY §1/R6S), Lemma-E reduction with per-deletion feasibility and exact
  cost-equality audit (THEORY D5), the three shape predicates and failure
  taxonomy (THEORY D6), membership (D7), outcome derivation, and the campaign
  decision order (PROTOCOL `decision_rule_order`) — all re-implemented from
  the frozen text.
- Extra independent checks the runner does not perform this way: exact
  minimum-Tag-weight verification at n=2 by brute force over all 16 dense
  tags, and Tag-constraint-rank recomputation by my own GF(2) elimination.

**Shared, and why it does not launder the runner's judgment:**
- Result-row FIELD NAMES and the CONTROL_GATE.json shape are taken from the
  frozen runner file. That is schema (where numbers live), not judgment
  (what the numbers should be); every value is recomputed or compared here.
- The control-id naming convention `control:r6o-16` mirrors the frozen
  runner's `CONTROLS_POS` keys (a synthetic protocol may override via
  `control_id`).

**Deliberately NOT checked (not checkable without re-solving; no tolerance
granted, just scope):**
- Optimality of `c_d2` (=C_DP) and the value of `c_d1` (=C_D+). The checker
  verifies witness validity and all internal cost identities, and `gap`
  arithmetic/outcome consistency — the same witness-vs-optimality boundary the
  R11 equivalence receipt draws. A future cluster-side extension could add an
  independent D+ referee at n=2 (12³ pair triples, brute-force tags); left out
  to keep this checker within its mandate.
- Byte-identity of the recorded Tag among equal-weight minimum tags (see A3).
- The solver-side `verify_witness`/phase-certificate booleans are taken as
  recorded flags; the checker re-verifies its own feasibility set instead.

## Ambiguities found in the frozen text (flagged now, BEFORE outcomes; not
resolved here)

- **A0 (most material). THEORY D5 deletion order is unspecified.** "repeatedly
  delete any coordinate … with class (0,0)" fixes neither the scan order nor
  confluence. The frozen runner deletes in pair/member/coordinate order with
  restart; the checker uses its own order. If two legal orders can yield
  different reduced witnesses with different membership verdicts, checker
  vs runner would disagree without either being wrong. Prospective
  clarification candidates (choice belongs to the freeze owner, not me):
  declare the runner's order normative, or claim/prove order-independence of
  the membership verdict. Until clarified, any such disagreement is reported
  as exit-2 (never arbitrated), per instructions.
- **A1. `base_commit` placeholder survives in the frozen PROTOCOL.json**
  (`TO_BE_FILLED_AT_FREEZE_COMMIT`). The freeze commit is 1404c56cd (a file
  cannot contain its own hash); the design-base commit was never back-filled.
  Binding is currently by branch/commit only.
- **A2. THEORY.md header contradiction.** First line still reads "(DESIGN,
  NOT FROZEN, NOT EXECUTED)" while the status line says
  FROZEN_BEFORE_ANY_CENSUS_OUTPUT. Cosmetic, but a hostile reviewer will
  notice.
- **A3. Tag tie-break identity.** D3 freezes the solver's witness tie-break,
  but among equal-weight minimum Tags the recorded Tag identity is
  solver-internal. Checker verifies feasibility + exact minimum weight only.
- **A4. `occ` domain undefined in THEORY D6.** The occupancy count's
  coordinate range is only implicit (M1's block-local domain). Checker adopts
  union(supp f0, supp f1), matching the frozen runner; THEORY.md should state
  it.
- **A5. T2's "replay-verified" is not operationalized.** The runner emits
  GAP_NOT_IN_BASIS without a replay step; PROTOCOL's decision text says
  "verified". The checker treats any GAP_NOT_IN_BASIS row as T2-triggering;
  what constitutes replay verification for the aggregate needs prospective
  definition.
- **A6. Requeue-pass provenance is not recorded in rows.** CANNOT_CHECK_
  INCOMPLETE_CENSUS applies "after the frozen long-timeout requeue pass", but
  a TIMEOUT row does not say which pass produced it. Checker treats any
  residual TIMEOUT/ERROR at check time as incomplete-census.
- **A7. gap<0 rows** are emitted as terminal=ERROR by the runner; PROTOCOL's
  outcome list does not name this case (covered by ERROR; minor).
- **A8. Aggregate RESULT.json format is not frozen.** The runner writes no
  aggregate; the planned aggregation job's output schema (COMPUTE_PLAN step 4)
  is unfrozen. Checker compares only a `terminal` field if a RESULT.json
  exists, else prints its recomputed terminal.
- **A9. Adverse-row field set.** "TIMEOUT/ERROR rows preserved verbatim" is
  enforced here as: such rows must not carry an `outcome`. Whether extra
  fields on adverse rows are conforming is unstated.

## Usage

```
# production (on the cluster, after the census lands):
python3 check_global_obstruction_basis_v1.py \
  --out-dir <RESULT_DIR> \
  --protocol papers/orion-05-tare-expressivity/experiments/global-obstruction-basis-v1/PROTOCOL.json
# exit 0 agree | 2 disagreement (CANNOT_CHECK__CHECKER_DISAGREEMENT) | 3 cannot-check

# self-test (anywhere, no solver, no repo access):
python3 check_global_obstruction_basis_v1.py --self-test
```
