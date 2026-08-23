# What the cost units mean — and what they do not

The calibration gap this programme repeatedly flagged as open is now **closed by
being resolved**, not filled. Full analysis:
`QG_COST_MODEL_CALIBRATION_FINDINGS.md`.

## The sentence

> Costs are reported in the frozen support-count objective's own units — a
> role-weighted tally of Pauli support with stipulated weights `(4, 2, 2, 1)`
> over frame, shared-Tag and factored-Restore coordinates, **rotations priced at
> zero** — and these are **not** counts of any physical resource: the
> selection-regret figure reduces exactly to `t_r x 5` factored-Restore Pauli
> letters, the frame coordinate being identically constant on the single-qubit
> probe family, and under the T-count reweighting **the programme itself
> declared**, 83.7 % of instances change regime and chemistry donor-exactness
> falls from 30/30 to 0/30.

**Scope note for whoever places it.** The ordinal invariance established here
holds *within the single-qubit probe family* and is entailed by that family having
one varying coordinate. It must **not** be quoted as general ordinal robustness —
QG-2 shows the opposite at `n >= 2`.

## Verdict: (c), sharpened

The coordinates are physically *named* and physically meaningful — frame support,
Tag checks, Restore/Pauli-frame corrections, rotations. But the **exchange rates
between them are stipulated, not measured**, and the programme has
machine-checked that a plausible alternative set of rates inverts its own
conclusions. Calibration is not achievable by further work inside this
construction; it needs an external circuit-level compilation and measurement that
does not exist here.

- **(a) direct physical reading — refuted by the programme's own declaration.**
  `O0`'s 4:2 frame ratio is contrasted *by the protocol itself* with the 7:1 a
  T-count model implies, and rotations — the T driver — carry weight **0**.
- **(b) monotone proxy — refuted by executed machine evidence.** Under `O1`
  (T-count-weighted), `QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json` records
  `GEOMETRY_OBJECTIVE_DEPENDENT`: 7752/9261 instances (83.7 %) change regime, the
  R6S support-2 sufficiency **theorem fails**, and predicate P1 retains 273 errors
  after re-induction. `O2`'s apparent robustness is a constant-shift lemma
  (`O0 + 45`), not evidence.

## A further, independent deflation of QG-39

Recomputed from the same primitives, exact on all 274,560 `(type, probe)` pairs:

- **the frame term is identically 18** at `n=1` — all six frame Paulis are
  weight-1 *by construction of the probe family* — so `-18` annihilates it under
  **every** weight vector. The frame coefficients `(4, 2)`, which are what the
  entire surrounding R6 chain is about, contribute **nothing** to QG-39;
- the Tag weight is identically 1 across all 48 accepted probes and cancels;
- therefore `K = t_tag + t_r * dF3` — an affine function of **one** structural
  count, `dF3 in [-5, 5]`.

So QG-39 is a **one-coordinate result on a probe family that structurally cannot
see the coordinate the construction is about**. Its regret of 5 is exactly
`5 * t_r`, and `t_r` is unmeasured across a declared span of `1` (stipulated in
`O0`), `3` (the programme's own T-model `O1`) and `0` (the rejected free-Pauli-frame
limit) — giving 5, 15 or 0. **Nothing in the construction fixes which.**

This is independent of, and compounds with, the null-model retraction in
`QG_RETRACTION_SELECTION_HEADLINES_V1.md`.

## What can honestly be said

> The regret is **5 single-qubit Pauli letters in the factored Restore layer, per
> column type selected.**

That is a real countable quantity. Multiplying it by a per-column count and by a
physical price per Restore Pauli is the step that has **no support**, and a
T-count or CNOT figure was **not** produced for exactly that reason — it would
have been manufactured, not estimated.

## Credit where due

No overclaim was found in the referee-facing artifacts. The programme never
claims `O0` is a physical count and says the opposite; `QG-paper-01` already
states the geometry is "a property of the (family, objective) pair" and that the
sufficiency bound is "objective-scoped, not universal".

## Residual caveat

QG-34/39 pin `centrals = (0,0,0)` and `n = 1`, whereas the referee DP optimises
over all eight central configurations.
