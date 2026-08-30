# The equal-Psi, unequal-cost witness search reproduces

#1701 asks, for ORION-10's successor: *freeze primitive vocabulary `Psi` before
fresh labels/costs*, then *search for an equal-`Psi`, unequal-cost witness; if
found, conclude no `Psi`-only explanation of any size exists*.

Both are already discharged by this packet, and both were re-run rather than cited.

## Re-run on current `main`

| script | exit | terminal |
|---|---|---|
| `enumerate_scoped_vocabularies_v1.py` | 0 | `VOCABULARY_MINIMALITY_IS_DISCRETE`, `crosscheck_passed=True` |
| `check_bprime_fibre_criterion_v1.py` | 0 | `CANNOT_CHECK_FIBRE_CONSTANCY_ON_SELECTED_WITNESSES` |

```
n=5: partitions=  52  universal=1  only_discrete=True  refuted=  51  crosscheck=True
n=6: partitions= 203  universal=1  only_discrete=True  refuted= 202  crosscheck=True
```

## Why this answers the witness question

Theorem 2 of `theory/certificate-explanation-gap-v1/THEORY.md` gives the fibre
criterion: the `Psi`-measurable functions are exactly the assignments of one value
per fibre, so a formula over `Psi` — whatever its operators, interaction order or
length — computes only a function of `Psi`. An exact `Psi`-only explanation
therefore exists **iff cost is constant on every `Psi`-fibre**.

The enumeration finds, for every partition coarser than the discrete one, an
explicit pair of instances in the same fibre with different cost — an equal-`Psi`,
unequal-cost witness. At n=6 that is **202 of 203 partitions refuted**, the single
survivor being the discrete partition itself. The witnesses are constructed and
independently agreed with brute-force enumeration over every cost function.

Because the criterion quantifies over formulas of every size, exhibiting one
witness pair for a vocabulary rules out a `Psi`-only explanation **of any size**,
which is exactly the conclusion #1701 asks to be drawn.

## Scope, unchanged

The packet's own limit stands: this is the universal statement over the frozen
abstract space and claims nothing about any particular named ORION-10 vocabulary
such as `B'` or `B''`. The `B'` fibre-criterion check remains
`CANNOT_CHECK_FIBRE_CONSTANCY_ON_SELECTED_WITNESSES` and is preserved, not
upgraded.
