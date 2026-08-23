# P11I Wide High-Width Replication Protocol V1

**Protocol:** `ORION.P11I.WideHighWidthReplication.v1`
**Executable:** `run_p11i_wide_high_width_replication_v1.py`
**Frozen:** 2026-08-22, before executing any P11I seed.

## Why this is a successor

P11D and P11H are immutable adverse results. P11H also identifies a narrower
positive regime: its pooled strongest attack reaches the target at `r=3` and
does not reach it at any registered `r=7` rung. P11I prospectively tests that
regime on fresh seeds and a complete bank-geometry cross. It does not select a
favourable P11H cell or reuse a P11H outcome as a P11I observation.

## Frozen panel

- state width: `r ∈ {3, 7}`;
- bank geometry: `(d,s) ∈ {(14,2), (14,3), (19,3)}`;
- complete factorial: all six cells at each seed;
- execution seeds: `2026082241`, `2026082242`, `2026082243`;
- five protected queries per cell;
- train sizes: `64, 128, 256`; test size: `4096`;
- universal pool: P11H's L1 logistic, L2 logistic and 96-tree ExtraTrees
  arms, combined by maximum accuracy at each size;
- compiled defence: P11H's L2 decoder on the `r` active components;
- decoder-held-fixed control: P11H's ExtraTrees decoder on those components;
- every stochastic estimator has an explicit seed and `n_jobs=1`.

The independent unit is one `(execution seed, bank geometry)` pair. The five
queries are repeated measurements inside that unit. The primary panel therefore
has nine independent high-width units, with nine matched low-width controls.

## Frozen gates

For every high-width unit, without averaging across units:

- `compiled_by_64`: compiled mean accuracy at `n=64 >= 0.95`;
- `pooled_below_target_before_256`: pooled best accuracy at `n∈{64,128} < 0.95`;
- `delta64_ge_0_20`: compiled minus pooled accuracy at `n=64 >= 0.20`.

For every matched low-width control:

- `attack_live_at_low_width`: pooled best accuracy at `n∈{64,128} >= 0.95`.

Across every cell: zero answer-laundering events. Two complete fresh-process
scientific payloads must be byte-identical. The conjunction is
non-compensatory; one failed high-width unit fails the replication claim.

## Terminals

- `P11I_HIGH_WIDTH_ADVANTAGE_REPLICATED_WIDE_PANEL`: all scientific and
  instrument gates pass;
- `P11I_HIGH_WIDTH_ADVANTAGE_NOT_REPLICATED`: the instrument passes and at
  least one high-width scientific unit fails;
- `P11I_INSTRUMENT_PRECONDITION_NOT_MET`: laundering, a dead matched low-width
  attack, subprocess failure, or replay mismatch.

The adverse P11D and P11H terminals remain unchanged under every P11I outcome.
