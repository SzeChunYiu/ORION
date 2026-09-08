# Research tree

This directory looks like fifty live programmes. It is not.

Most top-level folders are **V1 freeze evidence**. Their Git paths are digest-bound in [`orion-v1-freeze/V1_COMPONENT_BINDING_V1.json`](orion-v1-freeze/V1_COMPONENT_BINDING_V1.json). Moving them would orphan the freeze, tests, and workflows. They stay here and are **archived in place**.

The machine catalog is [`archive/LAYOUT_V1.json`](archive/LAYOUT_V1.json). Policy and a sparse-checkout recipe live in [`archive/`](archive/).

| Class | Top-level folders | What to do |
|---|---:|---|
| Live | 12 | Work here |
| Control plane | 1 | `orion-v1-freeze/` — do not move |
| Frozen in place | 37 | Historical evidence; do not `git mv` |

## Start here (live)

| Path | What it is |
|---|---|
| [`extensions/orion-q/`](extensions/orion-q/) | Quantum compilation (ORION-Q) |
| [`extensions/orion-qg/`](extensions/orion-qg/) | Quantum regime geometry |
| [`extensions/orion-qn/`](extensions/orion-qn/) | Quantum successor notes |
| [`experiments/davenport-c7-frontier/`](experiments/davenport-c7-frontier/) | C7 / Davenport frontier (last touched 2026-09-06) |
| [`extensions/orion-math-c7-davenport/`](extensions/orion-math-c7-davenport/) | Davenport registration |
| [`extensions/p6-higher-order-epistemic-mechanics/`](extensions/p6-higher-order-epistemic-mechanics/) | Typed epistemic mechanics |
| [`extensions/p7-method-space/`](extensions/p7-method-space/) · [`p8-method-authority/`](extensions/p8-method-authority/) | Method space / authority |
| [`extensions/p9-structured-neural/`](extensions/p9-structured-neural/) · [`p10-structured-reasoning/`](extensions/p10-structured-reasoning/) | Structured reasoning |
| [`extensions/meta-orion-recursive-scientific-evolution/`](extensions/meta-orion-recursive-scientific-evolution/) | Meta-ORION / RSE |
| [`novelty/`](novelty/) | Novelty vs donor recomposition |
| [`cross-domain-mechanic-transfer-v1/`](cross-domain-mechanic-transfer-v1/) | Cross-domain transfer |
| [`flagships/`](flagships/) | Sealed self-improvement flagship |
| [`orion-rg/`](orion-rg/) | ORION-04 reasoning-geometry |
| [`p3-matched-polarity-necessity-v2/`](p3-matched-polarity-necessity-v2/) | Post-freeze P3 successor |
| [`self-orion-v4/`](self-orion-v4/) | Current self-ORION confirmatory packet |
| [`paper-programme-v1/`](paper-programme-v1/) · [`paper-programme-v2/`](paper-programme-v2/) | Paper-programme control |
| [`orion-01-05-convergence-v1/`](orion-01-05-convergence-v1/) | ORION-01…05 evidence convergence |
| [`orion-v1-freeze/`](orion-v1-freeze/) | V1 freeze control plane |

Post-freeze one-file registrations also sit under `extensions/`: `orion01`, `orion-03-typed-merge`, `orion-10-vocabulary`, `p1-p3-structure`.

## Frozen in place (do not move)

These folders are closed or superseded programmes whose **path is the archive**. GitHub still lists them next to live work because the freeze pins the path, not because they are active.

Largest: `orion-epistemic-state-v1/` (~221 MB census JSON). Treat it as a frozen dump, not a working directory.

Full table: [`archive/FROZEN_IN_PLACE.md`](archive/FROZEN_IN_PLACE.md).

## Why not `git mv` into `archive/`?

`papers/archive/` holds **pre-unification aliases** that were rebound to canonical `papers/orion-NN-*` paths. Research freeze identity is the opposite: the canonical path *is* `research/<programme>/`, hashed as a Git tree OID.

A symlink at the old path is also unsafe: freeze bindings are `kind: tree`, not blobs.

To hide frozen trees in a local clone without rewriting history, use [`archive/SPARSE_CHECKOUT`](archive/SPARSE_CHECKOUT).
