# P12B protocol amendment v1.1: preserve the fixed sigma mixture

**Frozen before runner implementation and before protected outcome access.**

This amendment supersedes only the bootstrap resampling sentence and gate 6 in
`P12B_EQUAL_ACTION_SIGNAL_COMPLEMENTARITY_PROTOCOL_V1.md`, whose frozen SHA-256
is `a44870bea56ea0c94c1b0dec15f3f11961e9371c1f3fedbda3048c654210cb09`.
Every arm, action, budget, seed, family, episode count, sigma stratum, estimand,
threshold and terminal remains unchanged.

Because the panel fixes eight family RNG blocks in each of four sigma strata,
the primary 20,000-resample family-block bootstrap preserves that mixture:
within every replicate it samples eight families with replacement separately
from each sigma stratum, then averages all 32 selected family deltas.  The random
seed remains `2026083303`.

Gate 6 therefore reads:

> the **stratified** family-block bootstrap 95% lower bound is at least `0.12`.

An additional unstratified 32-family block bootstrap is reported as a sensitivity
analysis, using seed `2026083304`.  It is not a promotion gate because it
randomizes a panel composition that the protocol fixed in advance.

The independent unit remains one family RNG block (`n=32`); episodes and fixed
sigma labels are not independent replicates.
