# P4 V3 claim-axis authority — development packet

Base: `claude/papers-1-10-issues-uqrj2o@fd9892fdafd7734b07c8b24a4384c9e9561b1349`
Status: `ADDITIVE_ADJUDICATION`

## Defect

The immutable V3 identifiability register contains four failed seed-invariance
cells on the `BLOCK` and `PROMOTE` axes. All four are the registered
`digest-prefix` noise control. The V3 H3 claim is computed only on the
`CANNOT_CHECK` axis, which clears all fourteen probes on all thirteen seeds.

The manifest states that boundary correctly, but the P4 ledgers and promotion
notes shorten it to “the register clears”. That wording can be read as a
whole-register assertion and conflicts with the artifact.

## Repair

1. Preserve the frozen protocol, register, panel and V2 negative result byte for
   byte.
2. Compute claim authority on an explicit `(construction, terminal)` coordinate.
3. Require the construction-level audit and every seed-invariance cell for that
   terminal to pass at the declared ceiling, with no unscored probe result.
4. Report off-axis residuals, but never allow them to authorize or defeat a
   claim on another axis.
5. Correct every unqualified “register clears” statement to the exact
   `V3/CANNOT_CHECK` claim scope.

## Hostile tests

- the committed V3 register authorizes only the `V3/CANNOT_CHECK` scope;
- changing any `CANNOT_CHECK` seed to failure withholds authority;
- an unscored registered probe withholds authority;
- an off-axis residual remains disclosed and cannot be averaged away;
- the committed adjudication is content-bound to the immutable register.

## Scientific boundary

This is an authority and reporting repair, not a new experiment. It does not
turn the historical V2 H3 result positive, change any observed result, or claim
that the entire V3 identifiability register passes.
