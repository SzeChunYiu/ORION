# P11H Pooled Universal-Decoder Successor Protocol V1

**Paper:** ORION-P11 — State as Computation
**Issues:** #471, #664, #667
**Protocol:** `ORION.P11H.PooledSparsityLadderAttack.v1`
**Executable:** `run_p11h_pooled_sparsity_ladder_v1.py`
**Preflight:** `orion.study.p11.successor_reach`, artifact `P11H_PREFLIGHT_ATTAINABILITY_V1.json`
**Frozen:** 2026-08-22, before the pre-run attainability preflight and before execution.

## Why P11H exists

`python -m orion.study.p11.attack_audit` exits `3` on `terminal_reach`. All four
of P11G's scientific gates hold in every world its own freeze admits, so
`all(gates.values())` was `True` before the seed was drawn and
`P11G_DETERMINISTIC_TREE_DECODER_GAP_SUPPORTED` is the only terminal that
artifact could ever have printed. That is
`UNWINNABLE_ATTACK_PREDETERMINED_SURVIVAL`, recorded under
`research/failures/2026-08-unwinnable-attack-predetermined-survival/`, and both
that record and `P11G_ARM_PLACEMENT_ADJUDICATION_V1.md` state that only a
successor protocol can retire it.

P11H is that successor. **Nothing frozen is edited.** P11C, P11D, P11E, P11F and
P11G keep their protocols, seeds, arms, thresholds, receipts and terminals
verbatim; the P11G scientific payload still digests to
`a2b0c33ce3c39e54ca1aa400a2b7d52d019fc4503f6cd5eb726c7b8bbe79a7cc`; no published
P11 number moves. P11H is a new identity with its own seed and its own claim
authority, exactly as P11G was to P11F.

P11H answers all four requirements `P11G_ARM_PLACEMENT_ADJUDICATION_V1.md` lists
under *What a successor would need to carry the claim as published*.

## The design, and the evidence for it

The adjudication's Part 3 decomposition is the measured fact the design is built
on. Holding the decoder fixed and moving only the representation attributes
**86.7%** and **55.4%** of P11G's published `n=64` gap to the change of state
rather than the change of decoder family. So the state half is the real
quantity, and a successor should vary the state and hold the decoder pool fixed
— not the other way round, and not "the same attack, bigger".

Three measurements decided the rest, all taken before this file was frozen:

1. **Capacity is not the lever.** The record already establishes that a 43×
   larger ensemble moves the tree arm's `n=64` accuracy from `0.5376` to
   `0.5356`. A successor cannot be P11G with more trees.
2. **Bank width alone is not the lever either.** Holding `r=7` and sweeping the
   complete universal bank across `C(14,2)=91`, `C(16,2)=120`, `C(14,3)=364`,
   `C(16,3)=560`, `C(19,3)=969` and `C(17,4)=2380`, the pooled attack's best
   mean accuracy below `n=256` stays inside `[0.8406, 0.9004]` — it never
   crosses `0.95` anywhere on that sweep. A bank-width-only ladder would have
   reproduced P11G's defect in a new file.
3. **The width of the compiled state is the lever.** At `(19,3)` and five
   protected queries, the pooled attack's best accuracy below `n=256` reads
   `1.0000` at `r=3`, `0.9736` at `r=5`, `0.8674` at `r=7` and `0.7810` at
   `r=9`. The statistic crosses `0.95` between `r=3` and `r=7`, and the
   `delta64` statistic crosses `0.20` over the same span. That is the axis the
   ladder is built on, and it is the paper's own quantity: `r` is how much
   query-conditioned state the compiler resolves.

The mechanism is the one the failure record already identified: the label is an
`r`-sparse linear threshold on the universal bank, so the entire sample cost is
*support discovery*, and support discovery gets cheap as `r` falls. An attack
pool that contains a decoder whose hypothesis class contains the target — a
sparse linear one — can therefore win at small `r` and lose at large `r`. P11G's
single axis-aligned tree arm could do neither.

## Frozen construction

- **preflight seed:** `2026082201` — used only to bound the reach of the
  thresholds. No gate is read at this seed.
- **execution seed:** `2026082210` — fresh, published here before execution, and
  the only seed the terminal is read at.
- **ladder:** the complete cross of two declared coordinates, a 2×3 factorial
  and not a hand-picked list —
  - state widths `r ∈ {3, 7}`;
  - bank geometries `(d, s) ∈ {(14,2), (14,3), (19,3)}`, giving complete
    universal banks of `91`, `364` and `969` parity columns;
  - so the six rungs are `(14,2,3)`, `(14,3,3)`, `(19,3,3)`, `(14,2,7)`,
    `(14,3,7)`, `(19,3,7)`.
- **protected regimes:** **two rungs, drawn from the ladder without replacement
  by the execution seed**, on a random stream disjoint from every rung's data
  stream. Every one of the 15 pairs is an admissible world.
- **five protected queries per regime** — raised from P11G's three, which is the
  power change the adjudication asks for.
- **train sizes:** `64, 128, 256`; the gates read `64` and `128`, the sizes
  strictly below the threshold gate's `256`.
- **test size:** `4096`.
- same parity-majority no-answer-laundering construction as P11C–P11G;
  vectorized parity bank; no protected hyperparameter tuning.
- each rung's data stream is keyed by its `(d, s, r)` rather than by its position
  in the ladder, so a rung's readings are a function of the regime.
- every estimator's `random_state` is derived arithmetically from the protocol
  seed, `n_jobs=1` throughout.

### Why the protected regimes are drawn rather than named

The ladder was sized at the preflight seed, so its per-rung readings were known
before this file was written. **Naming a rung after that sizing would be
post-hoc selection** — choosing the regime whose verdict one has already seen.
The executable therefore draws the protected pair from the whole ladder at the
execution seed, and the preflight publishes, in advance, how many of the 15
admissible draws clear every gate. The survival or defeat is decided by the
draw, which is the precise property P11G lacked.

### How the ladder's coordinates were admitted

A coordinate enters the ladder only if **every** rung on it gives the *same*
gate verdicts at all three preflight seeds `2026082201`, `2026082202`,
`2026082203`. This is a statement about power, not about which verdict a rung
produces: it removes knife-edge rungs in both directions, and the adjudication
asks for exactly it ("a single draw of this construction cannot decide a gate
whose boundary sits between them"). The whole candidate table, rejections
included:

| rung | bank | `pooled best < 256` at the three seeds | `delta64` | `compiled@64` | verdict |
|---|---:|---|---|---|---|
| `(14,2,3)` | 91 | 1.0000 / 1.0000 / 1.0000 | +0.000 / +0.135 / +0.103 | 1.000 / 1.000 / 1.000 | **stable, attack wins** |
| `(14,3,3)` | 364 | 1.0000 / 1.0000 / 1.0000 | +0.099 / +0.051 / +0.051 | 1.000 / 1.000 / 1.000 | **stable, attack wins** |
| `(19,3,3)` | 969 | 1.0000 / 1.0000 / 1.0000 | +0.076 / +0.122 / +0.174 | 1.000 / 1.000 / 1.000 | **stable, attack wins** |
| `(14,2,7)` | 91 | 0.8854 / 0.8576 / 0.9220 | +0.248 / +0.249 / +0.241 | 0.982 / 0.995 / 0.990 | **stable, defence survives** |
| `(14,3,7)` | 364 | 0.8808 / 0.8999 / 0.8641 | +0.237 / +0.291 / +0.338 | 0.970 / 0.995 / 0.991 | **stable, defence survives** |
| `(19,3,7)` | 969 | 0.8463 / 0.8703 / 0.8450 | +0.376 / +0.342 / +0.346 | 1.000 / 0.991 / 0.994 | **stable, defence survives** |
| `(14,2,5)` | 91 | 0.9612 / 0.9612 / 1.0000 | +0.233 / +0.234 / +0.230 | 1.000 / 1.000 / 1.000 | rejected: `r=5` incomplete |
| `(14,3,5)` | 364 | 0.9547 / 0.9564 / 0.9630 | +0.287 / +0.213 / +0.226 | 1.000 / 1.000 / 1.000 | rejected: `r=5` incomplete |
| `(19,3,5)` | 969 | 0.9245 / 0.9696 / 0.9723 | +0.202 / +0.274 / +0.278 | 1.000 / 1.000 / 1.000 | **rejected: unstable** |
| `(17,4,3)` | 2380 | 1.0000 / 1.0000 / 1.0000 | +0.139 / +0.202 / +0.048 | 1.000 / 1.000 / 1.000 | **rejected: unstable** |
| `(17,4,5)` | 2380 | 0.9269 / 0.9480 / 0.9565 | +0.327 / +0.254 / +0.269 | 1.000 / 0.993 / 1.000 | **rejected: unstable** |
| `(17,4,7)` | 2380 | 0.8564 / 0.8646 / 0.8301 | +0.392 / +0.402 / +0.358 | 0.994 / 1.000 / 0.972 | rejected: `(17,4)` incomplete |
| `(16,2,7)` | 120 | 0.8845 / 0.9245 / 0.9246 | +0.281 / +0.286 / +0.291 | 0.986 / 0.986 / 0.997 | rejected: `(16,2)` incomplete |
| `(16,3,3)` | 560 | 1.0000 / 1.0000 / 1.0000 | +0.051 / +0.051 / +0.098 | 1.000 / 1.000 / 1.000 | rejected: `(16,3)` incomplete |
| `(19,3,9)` | 969 | 0.7810 / 0.8077 / 0.8003 | +0.325 / +0.349 / +0.340 | 0.955 / 0.971 / 0.947 | **rejected: unstable** |

The rule cuts both ways, which is the point. `(19,3,5)` and `(17,4,5)` are
unstable on the gate the *attack* needs; `(17,4,3)` is unstable on the gate the
*defence* needs; `(19,3,9)` is unstable on the instrument precondition. The
`r=5` row and the `(17,4)` column cannot be completed because one of their rungs
is unstable, so neither coordinate is admitted, and the ladder is the complete
cross of what remains. `(17,4,5)` is P11G's own first cell, and its instability
here is the independently measured version of the coin flip the adjudication
already records for it (`UNIVERSAL_L1` reads `128` in 9 of 20 draws and `256` in
11).

## Decoder arms

### The universal-state attack — a **pool**, with its combination rule frozen in the gate

P11G gated on one arm and its terminal was a function of which arm that was.
P11H registers every universal-state arm its claim covers and reads the gate
through the pool, so no arm choice can change the verdict.

| arm | decoder | shown |
|---|---|---|
| `UNIVERSAL_L1` | logistic regression, `C=0.1`, `penalty="l1"`, `liblinear`, `max_iter=1000` | the complete parity bank |
| `UNIVERSAL_L2` | logistic regression, `C=1.0`, `liblinear`, `max_iter=1000` | the complete parity bank |
| `UNIVERSAL_EXTRA_TREES` | `ExtraTreesClassifier`, `n_estimators=96`, `max_features="sqrt"`, `n_jobs=1` | the complete parity bank |

**Combination rule (frozen inside this protocol's own positive gate):** the
pooled universal attack's accuracy at training size `n` is the **maximum over
the three registered arms** at `n`. Its threshold is the earliest registered `n`
at which the pooled accuracy reaches `0.95`, censored at `256`.

This rule is P11H's, defined on P11H's ladder, queries, sizes and test set. It
is not P11C's rule and does not claim to be; `rule_binding()` in
`orion.study.p11.decoder_attack_reach` records why a rule frozen for one
protocol does not travel.

### The compiled defence, and the decoder-held-fixed control

| arm | decoder | shown |
|---|---|---|
| `COMPILED_L2` | logistic regression, `C=1.0`, `liblinear`, `max_iter=1000` | the query's `r` active components only |
| `COMPILED_EXTRA_TREES` | `ExtraTreesClassifier`, `n_estimators=96`, `max_features="sqrt"`, `n_jobs=1` | the query's `r` active components only |

`COMPILED_EXTRA_TREES` is not an attack; it removes the treatment. It is the
decoder-held-fixed control the adjudication asks a successor to compute **in its
own receipt**, and P11H publishes the decomposition per rung: the published gap,
its decoder-family half (`COMPILED_L2 − COMPILED_EXTRA_TREES`), its
representation half (`COMPILED_EXTRA_TREES − UNIVERSAL_EXTRA_TREES`), and a
second representation-only reading inside the linear family
(`COMPILED_L2 − UNIVERSAL_L2`), where the decoder is literally the same
estimator and only the columns differ.

Neither arm receives the final label as an input feature.

## Pre-run attainability preflight — required before execution

P11H may not be run for a result until `orion.study.p11.successor_reach` has
recorded `P11H_PREFLIGHT_ATTAINABILITY_V1.json`, which must show:

1. every threshold inside the reach of the statistic it reads
   (`assess_threshold_panel` / `require_supported_thresholds`, no
   `THRESHOLD_UNATTAINABLE`);
2. no **hypothesis** gate satisfied by every admissible value (no
   `THRESHOLD_UNCONDITIONAL` in the `HYPOTHESIS` role — this is P11G's defect);
3. at least one hypothesis gate discriminating; and
4. `measure_terminal_reach` over all 15 admissible draws reporting
   `distinct_terminals == 2` (`require_reachable`).

Each gate statistic's support is **derived, not sampled**: the ladder is fixed
and the draw takes two rungs of six without replacement, so a statistic reducing
the drawn rungs by `max` has its infimum at the second-smallest rung reading and
its supremum at the largest, and one reducing by `min` has its infimum at the
smallest and its supremum at the second-largest. Those are order statistics of a
finite list.

The preflight bounds the bars. It never reads the outcome, and it runs at the
preflight seed, not the execution seed.

## Replay authority

The authoritative P11H executable launches **two fresh Python subprocess
executions** of the complete one-run scientific pipeline. A scientific terminal
is published only if both subprocesses exit successfully and their canonical
scientific JSON bytes and SHA-256 digests are identical; otherwise the run is
`P11H_INSTRUMENT_PRECONDITION_NOT_MET`. Replay verification is in the terminal
decision path.

## Scientific gates

Every threshold below is **P11G's own, carried over unedited**: `0.95` for the
accuracy target and `0.20` for the `n=64` gap, exactly as P14C carried P14A's
`0.05` and `0.08` onto an instrument that could move them. What P11H changes is
the support of the statistic they read, never the bar.

Gates carry a declared **role** in `orion.programme.gate_attainability`'s sense.
A `PRECONDITION` certifies the instrument and may hold in every admissible
world; a `HYPOTHESIS` carries the claim and may not.

| # | gate | role | reads | satisfied when |
|---|---|---|---|---|
| 1 | `no_answer_laundering` | PRECONDITION | active components equal to or negating the signed label on the protected test set, summed over the drawn regimes | `<= 0` |
| 2 | `attack_live_on_ladder` | PRECONDITION | the pooled attack's best mean accuracy below `n=256`, maximised over **every** rung of the frozen ladder | `>= 0.95` |
| 3 | `compiled_by_64` | PRECONDITION | the compiled arm's smallest mean accuracy at `n=64` over the drawn regimes | `>= 0.95` |
| 4 | `pooled_universal_threshold_ge_256` | HYPOTHESIS | the pooled attack's best mean accuracy below `n=256` over the drawn regimes | `<= 0.95` |
| 5 | `delta64_ge_0_20` | HYPOTHESIS | the smallest compiled-minus-pooled mean accuracy at `n=64` over the drawn regimes | `>= 0.20` |

Gate 2 is the gate P11G never wrote. It says the pooled attack registers a win
somewhere on the frozen ladder, so a defeat elsewhere is a measurement rather
than arithmetic. It is a precondition precisely because it is *meant* to hold in
every admissible world — that is a benchmark built to be measurable — and
declaring the role is what stops that from being confused with a claim.

Two further gates are properties of the executable rather than of the decoders:
`two_fresh_subprocess_payloads_byte_identical` and `subprocesses_successful`.

## Terminals

Three, so that "the attack won" is not spelled the same way as "the instrument
failed":

- `P11H_COMPILED_STATE_ADVANTAGE_SURVIVED_POOLED_ATTACK` — every gate holds.
- `P11H_POOLED_UNIVERSAL_ATTACK_PREVAILED` — every precondition holds and a
  hypothesis gate fails. **This is a first-class result, not an error**, and the
  executable exits `0` on it.
- `P11H_INSTRUMENT_PRECONDITION_NOT_MET` — a precondition or a replay gate
  fails; the run certifies nothing and the executable exits non-zero.

## Claim authority

A `P11H_COMPILED_STATE_ADVANTAGE_SURVIVED_POOLED_ATTACK` terminal supports only:

> In the two protected regimes this run's published seed drew from the frozen
> state-width ladder, query-conditioned compiled state retains a registered
> low-sample advantage over the **strongest of three registered universal-state
> decoders** operating on the complete universal parity bank — on a ladder where
> that pooled attack demonstrably reaches the same target below `n=256` in other
> admissible regimes.

A `P11H_POOLED_UNIVERSAL_ATTACK_PREVAILED` terminal supports only the
corresponding negative in the regimes drawn, and refutes the survival claim
**for those regimes** rather than universally.

Neither terminal establishes a universal nonlinear lower bound, real-agent
superiority, or that compilation dominates all possible downstream search
mechanisms. Neither overturns P11G's frozen terminal, which is retained as
evidence about the arm placed in its gate.

## Reproduce

```
python -m orion.study.p11.successor_reach                  # the pre-run preflight
python papers/paper-11-state-as-computation/run_p11h_pooled_sparsity_ladder_v1.py
python -m pytest tests/unit/study/p11
```
