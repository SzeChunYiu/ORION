# P13 D2 donor-complete baseline result receipt V1

**Programme:** #977 · **PR:** #992 · **State:** `EXECUTED_BOUND_ON_GREEN`

## Execution binding (exact)

| item | value |
|---|---|
| protocol (pre-outcome freeze) | `papers/paper-13-responsibility-carrying-state/top_tier/P13_D2_DONOR_BASELINE_PROTOCOL_V1.md` @ `f1d0a2ba` |
| cases (pre-outcome freeze, gold dispositions frozen) | `p13_d2_donor_cases_v1.json` @ `fafee495` (58131 bytes, 48 cases) |
| runner / checker | @ `4f212b05` / @ `1cf27558` |
| CI run | `32661218631` (`p13-d2-donor-baseline-v1`), **conclusion=success** |
| artifact | id `9498827505`, size 3348 B, ZIP SHA-256 `d7eba7e1d2403647dc809ce1511f05abfc36b04028be0a0380805b536798c124` |
| primary terminal | `P13_D2_DONOR_BASELINE_V1_SUPPORTED` (receipt_sha256 `5a2478ef…`) |
| independent terminal | `P13_D2_DONOR_BASELINE_SECOND_INDEPENDENT_CHECKER_GREEN` (receipt_sha256 `b52abfbe…`), 0 invariant failures |
| agreement | `P13_D2_DONOR_BASELINE_TWO_IMPLEMENTATIONS_AGREE` asserted in-workflow; artifact JSONs byte-identical to local execution |

## Outcomes (48 episodes; 4 cells × 12)

| arm | verifier-correct | unsupported reuse | mean literal reads | solver calls |
|---|---|---|---|---|
| D2_CORE | 36/48 | 12 | 6.25 | 12 |
| D2_PLUS | 36/48 | 12 | 6.25 | 12 |
| RCS | 48/48 | 0 | 5.0 | 24 |
| COMPOSED | 48/48 | 0 | 5.0 | 24 |
| ALWAYS_RAW | 48/48 | 0 | 5.5 | 24 |

All four frozen gates hold: (1) both donor arms commit 12 unsupported reuses on `B_CHANGED_CURRENT`; (2) RCS and COMPOSED are perfect; (3) COMPOSED 5.0 <= donor 6.25 on both comparisons; (4) ALWAYS_RAW ceiling 48/48. Degenerate control: forcing D2 raw at every episode reproduces ALWAYS_RAW's total reads (300).

## What this earns

At bounded verifier-backed CNF scope (5 vars, frozen episode family, seed 20261307): the donor-complete provenance-tiered memory in its strongest demand-graded form (D2_PLUS) performs unsupported reuse under responsibility change with provenance continuity, and the responsibility-registration axis is not reducible to the provenance/grounding axis; the composition dominates both donor arms on correctness and literal-read cost.

## What this does NOT earn (authority boundary)

- Research-agent-scope external authority gate; real workflow deployment.
- Transport under arbitrary semantic-change classes beyond the frozen grid.
- Real-data (digits) replication of the D2 arm — open strengthening.
- `COMPOSED` is decision-equivalent to `RCS` on this grid by construction (all records G=MAX ⇒ demand grading adds no information); the earned claim is cost/correctness dominance over the DONOR arms, not separation from RCS.
- The `B_CHANGED_CURRENT` regime (semantic change without announced checkpoint bump) is the donor-faithful between-checkpoints regime, frozen in the protocol before execution; it is a modeling assumption about the donor's trust window, not an observed property of any deployed donor.
