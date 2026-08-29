# Top-tier identification closure wave 4 — 2026-08-29

**Base main:** `467133ddd55a415c6d305a5f7b908dc30e72ee20`  
**Scientific authority delta:** `NONE`

## Expert lenses

- **External construct validity — ORION-13.** Convert the known polarity confound into a prospectively anti-confounded witness design rather than rerunning the same reduct analysis.
- **Partial identification / transport — ORION-24.** Bound what a controlled source result can say about a mixed target population before external strata are measured.

## ORION-13

The existing exact result is preserved: on the two frozen 32-case corpora, polarity alone is the unique semantic reduct, so those corpora do not test necessity of the other six coordinates.

The new design-only successor targets **exclusive witnesses**. For each non-polarity coordinate, a valid witness pair must have opposite independently adjudicated verdicts, identical agreement bits on every other coordinate, a different agreement bit on the target coordinate, and fixed polarity agreement. Omitting that coordinate then makes the pair observationally identical, proving the coordinate cannot be dropped from a universally correct rule on any class containing the witness.

The protocol freezes at least 10 candidate witness pairs per non-polarity coordinate before adjudication, targets >=5 valid witnesses across >=3 source families, forbids closed-world negatives, forbids post-label candidate replacement, and requires external adjudication where the source does not explicitly encode the relation.

This is a stress-test necessity claim, not a prevalence claim.

## ORION-24

For target stratum weights `pi_s` and bounded score advantages `delta_s in [-1,1]`, if measured strata contribute `A` and unmeasured target strata have total mass `W`, the sharp target-average interval is

`[A-W, A+W]`.

The sign is positively identified only when `A-W>0`. With one measured stratum of effect `d` and target prevalence `p`, the exact interval is `[pd-(1-p), pd+(1-p)]`; even `d=1` cannot guarantee a positive mixed-population average unless `p>1/2` without further constraints.

P14C's controlled specification-separated conformance remains fully intact. The theorem states why P14D must report external stratum-specific effects and target-weight provenance rather than only a pooled score.

## Stop rule

No external labels are opened or invented. ORION-13's external witness outcomes and ORION-24's external stratum effects/weights remain prospective. These packets close identification/design gaps so future empirical work has a non-post-hoc decision rule.