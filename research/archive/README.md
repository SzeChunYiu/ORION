# Research archive (in place)

This is the archive index for `research/`, not a dumping ground for moved trees.

## Policy

1. **Do not `git mv` freeze-bound directories.** `V1_COMPONENT_BINDING_V1.json` records Git tree OIDs at exact `research/<dir>/` paths. Relocating those trees orphans freeze identity.
2. **Do not add files inside freeze-bound trees** just to mark them archived. That changes the tree OID.
3. **Do not replace a bound tree with a symlink.** Bindings are trees, not blobs.
4. Programmes that are closed or superseded stay at their freeze path and are listed here as **frozen in place**.
5. Live work is the short list in [`../README.md`](../README.md).

The machine catalog is [`LAYOUT_V1.json`](LAYOUT_V1.json). Every top-level `research/` directory except this `archive/` folder has a row. A unit test fails if a new folder appears uncatalogued or if a freeze-bound flag drifts.

## What “archived” means here

| Style | Used for | Example |
|---|---|---|
| In-place freeze path | V1-bound programmes | `research/orion-discovery-v1/` |
| Physical move under `papers/archive/` | Pre-unification paper aliases | `papers/archive/2026-08-pre-unification/` |
| Physical move under repo `archive/` | Root clutter (logs, receipts) | `archive/housekeeping/` |

Research freeze evidence uses the first style on purpose.

## Local working tree

Frozen census dumps are optional for day-to-day work. From a fresh clone:

```bash
git sparse-checkout init --no-cone
git sparse-checkout set --no-cone $(grep -v '^#' research/archive/SPARSE_CHECKOUT | tr '\n' ' ')
```

That keeps live programmes, the freeze control plane, and this index, and omits `orion-epistemic-state-v1` and the other frozen-in-place trees.

## Catalog

- [`LAYOUT_V1.json`](LAYOUT_V1.json) — classes, freeze flags, last commit, sizes
- [`FROZEN_IN_PLACE.md`](FROZEN_IN_PLACE.md) — human table of the 37 frozen top-level folders
- [`SPARSE_CHECKOUT`](SPARSE_CHECKOUT) — live-only sparse patterns
