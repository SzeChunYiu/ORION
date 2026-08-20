# P11 Query-Conditioned Compiler — Confirmatory Result Receipt V1

Terminal: `P11_QUERY_CONDITIONED_COMPILATION_GAP_SUPPORTED`

Protocol chronology:
1. exploratory feasibility pilot (non-authorizing);
2. theorem and confirmatory protocol frozen in Git history;
3. first fresh confirmatory execution;
4. post-run reproducibility-only amendment removing wall-clock values from the canonical payload, with no scientific change;
5. two full fresh-process replays compared after canonical removal of non-authoritative timing fields.

## Deterministic replay

Canonical replay SHA-256, both executions:

`8e790cf8bb8012bea8e575549730a58b21a0e1e96e51a2928d165c6fa89f3567`

Byte identity: `PASS`.

## Protected results

| d | s | fixed universal dimensions | compiled dimensions | universal/compiled dimension ratio | compiled 0.90 threshold | universal 0.90 threshold | threshold ratio |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 14 | 2 | 91 | 1 | 91x | 32 | 128 | 4x |
| 16 | 4 | 1820 | 1 | 1820x | 32 | not reached by 1024 | >32x (sentinel 33x) |
| 18 | 3 | 816 | 1 | 816x | 32 | 1024 | 32x |
| 20 | 3 | 1140 | 1 | 1140x | 32 | 1024 | 32x |

At n=1024:
- `(14,2)`: raw `0.49685`, universal `1.00000`, compiled `1.00000`;
- `(16,4)`: raw `0.49903`, universal `0.84550`, compiled `1.00000`;
- `(18,3)`: raw `0.50136`, universal `0.99152`, compiled `1.00000`;
- `(20,3)`: raw `0.50113`, universal `0.94685`, compiled `1.00000`.

Compiled accuracy is `1.0` in every frozen cell at every frozen train size from 32 through 1024. Raw linear remains near chance. All protected gates pass.

## Exact interpretation

The exact theorem establishes the fixed-representation dimension requirement for the controlled linear-readout query family. The empirical result adds a finite-sample observation: materializing every query coordinate can substantially slow learning of the active coordinate even though that exact decisive coordinate is present in both the universal and query-compiled arms.

Strongest bounded claim:

> For the frozen parity-query families and fixed linear downstream learner, allowing the current query to participate in state construction collapses a combinatorial fixed representation requirement to one active coordinate and avoids a large finite-sample nuisance burden from irrelevant universal coordinates.

This is not a universal nonlinear lower bound, not an LLM result, and not evidence that query-conditioned compilation always helps.
