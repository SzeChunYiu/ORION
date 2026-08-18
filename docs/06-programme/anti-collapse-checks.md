# Anti-collapse battery (Step 5)

Code: `src/orion/programme/hostile.py` (framework),
`checks_evidence.py` and `checks_diversity.py` (the ten checks),
`catalogue.py` (assembly). Tests: `tests/unit/programme/`.

## The fail-closed contract

Three outcomes, not two:

- `PASS` — the check ran and found nothing.
- `FAIL` — the check ran and found the collapse mode it looks for.
- `CANNOT_CHECK` — the check could not evaluate its own precondition.

`CANNOT_CHECK` blocks exactly as `FAIL` does. A boolean return type is precisely
how "could not check" becomes "checked and fine", so no check in this battery
returns one. Three further properties close the remaining gaps:

- An **empty report blocks**, so failing to run the battery cannot look like
  passing it.
- A report **missing an expected check blocks**, so a check that vanished from
  the catalogue cannot silently stop mattering.
- A check that **raises** yields `CANNOT_CHECK`, not a skipped result.

`HostileCheckReport.grants_phase4_closure` is the constant `False`. A clean
battery is a precondition for closure; it is never a grant of it.

## The ten checks

| Id | Fires when |
|---|---|
| `HC-BENCHMARK-OVERFIT` | protected score rises across epochs while independent fresh transfer falls |
| `HC-EVALUATOR-GAMING` | evaluator sits inside candidate custody, or its artifact changed with no declared `EVALUATOR_REVISION` |
| `HC-STALE-AUTHORITY` | a claim's provenance binds a source version that the live source no longer carries |
| `HC-HIDDEN-DELETION` | negative, rejected or harmful entries disappear between epochs, or a record is superseded with no successor |
| `HC-INSUFFICIENT-PROTECTED-EVIDENCE` | a conclusion is claimed from an epoch holding no protected evidence |
| `HC-UNIVERSE-COLLAPSE` | one source family exceeds the declared share ceiling, or families drop out without replacement |
| `HC-METHOD-MONOCULTURE` | one method is selected in every epoch and no challenger was ever evaluated |
| `HC-FORGOTTEN-NEGATIVE-HISTORY` | a known failure class is re-proposed with no causal-support link answering it |
| `HC-CIRCULAR-SELF-CITATION` | a settled claim's every supporting source is programme-internal |
| `HC-REPEATED-FAILURE-CLASS` | the same failure class recurs and draws the same intervention |

Each check names the precondition it needs, and returns `CANNOT_CHECK` naming
that precondition when it is absent — so a blocked report says what it could not
see, not merely that it blocked.

## Pre-registered assumptions

Written down now, before evidence exists, so they cannot later be reconciled to
whatever the first real epochs happen to look like.

- **Metric polarity.** `protected_metric`, `fresh_transfer_metric` and
  `worst_family_metric` are higher-is-better. `HC-BENCHMARK-OVERFIT` compares
  them directly, so a loss-like metric inverts the check — it would pass through
  real overfitting and fire on healthy improvement. A producer emitting a
  loss-like metric must negate it before populating `EpochSnapshot`. Encoding
  polarity as a field is a schema change, and belongs to whichever change first
  has a real producer to justify it.
- **Epoch numbering.** `HC-EVALUATOR-GAMING` treats `ReopenEvent.epoch` and
  `EpochSnapshot.sequence` as the same ordinal. No producer enforces that today.
  Both branches of the comparison are tested, so a wrong correspondence fails
  visibly rather than silently.

## Fields declared but not yet consulted

`EpochSnapshot.worst_family_metric` is declared because issue #210 Step 6
requires worst-family regressions to be reported explicitly, but no check reads
it yet. Likewise `ProgrammeState.search_universe`: the Layer-2 record is
validated by `validate_search_universe_record`, but `HC-UNIVERSE-COLLAPSE` works
purely from per-epoch source-family counts and never consults its
`unattempted_route_ids`, obligations or blind-spot tests. Wiring saturation state
into the collapse check needs the per-epoch universe versions that only executed
cycles produce.

## Every check must have failed at least once

Each `HostileCheck` declares `negative_fixture_id`: the test that shows it
rejecting something. `catalogue.validate_catalogue()` refuses duplicate ids and
shared fixtures, and `test_anti_collapse_battery.py` asserts every declared
fixture exists as a test in that module. This mirrors what
`orion.kernel.registry` enforces on discriminating checks — a check that has
never exhibited a failing case of its own is not demonstrably failable.

The no-alarm case is asserted too. `test_a_healthy_programme_raises_no_alarm`
runs the whole battery against a well-formed programme and requires all ten to
`PASS`. A battery that cries wolf on its first real run gets switched off, and a
switched-off battery detects nothing.

## Not registered into `orion.kernel.checks`

That package is auto-discovered by `pkgutil` in `orion.kernel.registry`, so
adding a module to it is a shared-registry edit in effect, and every check there
must additionally be lane-tagged and `frozen_at_round`-pinned. Registration is
queued as a follow-up for the lane that owns that wave.
