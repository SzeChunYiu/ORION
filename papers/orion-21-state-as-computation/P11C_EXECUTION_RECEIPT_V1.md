# P11C Execution Receipt V1

**Protocol identity:** `ORION.P11C.StrongerDecoderAttack.v1`
**Result:** `P11C_STRONGER_DECODER_ATTACK_RESULT_V1.json`
**Canonical SHA-256:** `f65c1c5bb9cb96194fbcb20c9dbfd3a949127f9789e95cf6585d891bf939c454`
**Terminal:** `P11C_STRONGER_DECODER_GAP_SUPPORTED`

## What happened

`P11C_REPRODUCIBILITY_AMENDMENT_V1_1.md` records that the first execution
attempt exceeded the available runner wall-time before emitting a terminal or a
result artifact, and that no protected metric or gate outcome was observed. The
`P11D` audit consequently listed `P11C` as an open attack: "`P11C` remains
`CANNOT_CHECK`. It is listed as an open attack rather than inferred from
`P11D`."

The protocol, the amendment's vectorized runner and the frozen master seed were
all already on the branch. The run had never been completed, not failed. It has
now been executed to completion, twice, in fresh processes. It takes **1m47s**.

Nothing was changed to make it finish: the executed file is
`run_p11c_stronger_decoder_attack_v1_optimized.py`, which imports the frozen
runner and replaces only `parity_bank`, exactly as the amendment specifies. No
seed, cell, query count, training grid, test size, decoder identity,
hyperparameter, threshold or gate was touched.

## Gates

| # | Registered gate | Outcome |
| --- | --- | --- |
| 1 | zero answer-laundering failures | PASS — 0 |
| 2 | `COMPILED_L2` reaches 0.95 by `n=64` in both cells | PASS — 64 and 64 |
| 3 | best hostile universal threshold `>= 4x` compiled, both cells | PASS — 256 vs 64, both |
| 4 | compiled minus best universal at `n=64` `>= 0.20`, both cells | PASS — 0.294897, 0.330835 |
| 5 | two fresh-process executions byte-identical | PASS — both `f65c1c5b…f939c454` |

Per cell:

| cell | compiled dim | universal dim | `COMPILED_L2` | `UNIVERSAL_L1` | `UNIVERSAL_L2` | `UNIVERSAL_EXTRA_TREES` |
| --- | --- | --- | --- | --- | --- | --- |
| `(17,4,5)` | 5 | 2380 | 64 | 256 | `NOT_REACHED` | 2048 |
| `(19,3,7)` | 7 | 969 | 64 | 256 | `NOT_REACHED` | `NOT_REACHED` |

## The qualification that travels with this result

Gate 3 is passed at the boundary and not comfortably. The compiled threshold is
64, so the gate needs the best universal threshold to be at least 256, and the
observed value is **exactly 256** in both cells.

`P11E`, which is the same construction — the same two cells, the same compiled
and universal dimensions, the same training grid, `n=64` deltas agreeing to
three decimal places — differs from `P11C` only in its master seed, and it
observes `UNIVERSAL_L1` at **128** in cell `(17,4,5)`. That is half the boundary
value. `P11D` failed the same `>=4x` gate for the same reason, and `P11E`'s own
protocol then froze a weaker `>=2x` target "because `P11D` already ruled out the
stronger `>=4x`-in-both-cells claim".

So two runs of one construction sit on opposite sides of this gate's boundary,
and which side a run lands on is a property of its draw. This receipt does not
resolve that in either direction: `P11C`'s terminal is what its frozen gates
produce on its frozen seed and is retained as such, and it does **not** restore
the `>=4x` claim that `P11D` retired. `P11E`'s negative is not overturned by it.

`evidence/audit/P11_THRESHOLD_STABILITY_2026-08-22.json` measures how often each
side comes up across twenty seeds of the same construction. Both frozen seeds
fall inside the swept range and both reproduce exactly, which is what qualifies
the sweep to say anything about them.

| cell | `UNIVERSAL_L1` threshold across 20 seeds | gate passes |
| --- | --- | --- |
| `(17,4,5)` | `128` in 9, `256` in 11 | 11 / 20 |
| `(19,3,7)` | `256` in 20 | 20 / 20 |

The conjunction gate 3 asks for therefore holds in **11 of 20 draws, 0.55**. The
second cell never moves; the whole instability is in the first.

That is close enough to a coin flip that neither a single positive nor a single
negative is evidence about the compiler. `P11C`'s SUPPORTED and `P11D`'s
NOT\_MET are two draws from the same distribution, and reading either as
settling the `>=4x` question would be reading a coin. What the pair actually
establishes is that this construction, at five queries per cell, does not have
the power to decide the gate it was given. Raising the query count per cell, or
choosing a cell whose threshold does not sit on the boundary, is the change that
would make the question decidable; neither is a repair to any existing frozen
protocol and both need a fresh identity.

The sweep is a diagnostic and authorizes no terminal. Sweeping seeds after an
outcome is how a result gets selected rather than measured, and it may not be
used to prefer one of these runs over another — including this one. A 0.55 pass
rate says the construction cannot decide, not that the claim is false.

## Environment note

The frozen runner constructs its logistic learners with `penalty="l1"` and
`penalty` defaulted for L2. In the scikit-learn version used here that spelling
emits a `FutureWarning`: `penalty` was deprecated in 1.8 and is scheduled for
removal in 1.10, in favour of `l1_ratio`. The numbers are unaffected today and
the two executions are byte-identical, but a protocol frozen against a spelling
the library is removing will stop being executable, and re-freezing it later
under a new identity is the only repair that does not edit a protected receipt.

Neither `l1()` nor `l2()` passes an explicit `random_state` — the defect `P11D`'s
audit records for its own run. Here the two fresh-process executions were
byte-identical regardless, which is a measurement rather than a guarantee.
