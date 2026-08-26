# P12 first scoring run: the floor was the harness, not the models

The first scored run returned `programs_ran: 0` across all 144 episodes, and
the gate's degeneracy guard fired:
`P12_STOPGO_FLOOR__GATE_NOT_APPLICABLE`.

## Why this is the most dangerous result the campaign could produce

Had the gate been applied to that table, it would have returned
`P12_STOPGO_BOUNDARY_NULL` — a clean, correctly-formatted failure of a
preregistered gate, with the protocol's own fail action instructing that it be
published and not iterated on.

It would also have been wrong. The arms tied at zero because **nothing
executed**, not because allocation does not matter. A null result about
complementarity and a floor produced by a broken execution environment are
indistinguishable in the aggregate table, and only one of them is about the
science.

The guard was written before the data existed, which is the only reason the
distinction survived contact with a plausible-looking number.

## Actual causes

| failure | count | cause |
|---|---|---|
| `ModuleNotFoundError` | 98 | the execution venv had no scientific stack — `pandas` alone accounted for 48 |
| `SyntaxError` | 46 | generation truncated at the 1600-token cap, mid-program |

Neither is a property of the models. The run measured the harness.

The token cap is the third time in this session that a saturated counter
nearly read as a capability limit: the ceiling probe's 420-token cap scored
1/4 parseable and looked like "the model cannot write programs", and its 1600
cap did the same at 4/6. In every case the failing episodes reported *exactly*
the cap as their completion-token count, which is the tell.

## Repair

Twelve modules installed and verified importable: pandas, matplotlib,
scikit-learn, scipy, networkx, netCDF4, geopandas, rdkit, scanpy, xarray,
rasterio, shapely. The 144 generated programs are re-scored unchanged — the
module failures need no regeneration, since the programs already exist and
only the environment was missing.

`arcpy` is proprietary ArcGIS and cannot be installed. Tasks requiring it stay
unscoreable and are recorded as excluded rather than counted as failures: an
environment that cannot run a task has not shown the task failing.

## Design note

Generation and scoring are separate processes on purpose. The eval scripts
must read `benchmark/eval_programs/gold_results/`, so a single-process design
would make the generator's deny-list guard decorative. The generator cannot
reach gold; the scorer never sees a prompt.

Crashes are recorded as `outcome: 0.0`, never dropped. Dropping them would
silently select for arms whose programs happen to run, flattering whichever
arm emits simpler code — a bias the gate cannot see.
