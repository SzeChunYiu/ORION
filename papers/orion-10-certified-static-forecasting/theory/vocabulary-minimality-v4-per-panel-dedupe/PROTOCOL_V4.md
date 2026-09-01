# ORION-10 B' fibre criterion V4 — per-panel dedupe

**Committed before the run, with no outcome in hand.**
**Scientific authority delta: `NONE`.** V2's `FIBRE_CONSTANCY_REFUTED` is untouched, and
V3's `CANNOT_CHECK_PREFIX_CONTROL_FAILED` stands as filed.

## The defect V4 repairs

V3 lifted every cap twentyfold and returned `CANNOT_CHECK_PREFIX_CONTROL_FAILED`: five of
ten panels did not reproduce V2's rows as their prefix, so no envelope claim could be made
in either direction.

The cause is in the generator, at `run_full_census_v2.py:1060`. One `dedupe: set = set()`
is created and passed into every `run_panel` call, with instances skipped on
`canonical_key(tp, n)` membership. A cap is therefore not only a stopping point: raising
`H1_n3` from 120 to 2400 inserts roughly 2,280 extra keys before `H2_n3` runs, and
`H2_n3` then skips instances it would otherwise have evaluated. **Every panel's
enumeration depends on the caps of the panels before it in `PANEL_ORDER`.**

`H1_n3` runs first and matched. The `n=3` panels after it did not.

## The single change

Each panel gets its own dedupe set, reset at the top of the `PANEL_ORDER` loop. The diff
against `run_cap_lift_v3.py` is 15 insertions and 2 deletions, of which 13 are the comment
recording why. Caps, grammar, routes, skeletons, enumeration order within a panel, regime
rule and terminal selection are otherwise byte-identical.

Dedupe still removes duplicates **within** a panel, which is the only place a
`canonical_key` collision was ever scientifically meaningful — two identical instances in
one panel are one instance. Cross-panel suppression was never intended; it was an
artefact of sharing the container.

## Why this restores the control

With per-panel state, a panel's enumeration depends only on its own cap. V2's rows are
then a prefix of V4's **by construction** rather than by hope, and the prefix control
becomes a genuine check on determinism instead of a check on cap coupling.

## Falsifier, unchanged since `REVIVAL_PASS_V1.md`

**Any admitted instance with `f_Bprime − C_Dxx > 3` refutes the lower envelope.**

Declared before V3 ran, unchanged for V4, and not restated in the light of V3's nine
candidate violations.

## Terminals, frozen here

- `ENVELOPE_REFUTED_AT_LIFTED_COVERAGE` — the prefix control passes and at least one
  instance exceeds offset 3. `REVIVAL_PASS_V1.md`'s one-sided bound must then be
  withdrawn, and V3's nine candidates are confirmed rather than assumed.
- `ENVELOPE_SURVIVES_20X_COVERAGE` — the prefix control passes and no instance exceeds
  offset 3. V3's nine were then a cross-panel skipping artefact. **This is not a proof**;
  it raises the coverage at which the envelope has been tested and no more.
- `CANNOT_CHECK_PREFIX_CONTROL_FAILED` — the prefix control fails again. The cause is then
  not the shared dedupe set, and no envelope claim may be made in either direction.
- `CANNOT_CHECK_WALL_CLOCK` — the run does not complete in its SLURM budget. Partial
  coverage is reported as partial.

## Prediction, recorded before the run

V3's nine violations all lie **beyond** V2's prefix, in `H2_n3` (5) and `H4_n3` (4), both
panels whose enumeration V3 contaminated. If cross-panel skipping produced them, they
should not survive. If they are genuine members of the frozen space, they should reappear.

Writing this down first is the point: either outcome is informative, and neither can be
retrofitted afterwards.
