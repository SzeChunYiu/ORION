# Paper-parity import-boundary repair

Date: 2026-08-24

Frozen base: `a46fe8237225f3f72232d6f3ee68109dfbd06be3`

Status: **FROZEN BEFORE IMPLEMENTATION**

Authority: Python import and harness availability only; no scientific result.

## Atomic development question

Can the public paper-parity runtime remain the default export of
`orion.runtime` without making imports of `orion.runtime.runtime` recurse back
through `paper_runtime` and the partially initialized navigation module?

## Reproduced failure

On the frozen base, this command fails during module collection:

```text
PYTHONPATH=packages/orion-research-harness/src:src python -c "import orion_research_harness"
```

The cycle is:

```text
orion.engine.navigation
-> orion.self_orion package initialization
-> orion.self_orion.live_trial
-> orion.runtime.runtime
-> orion.runtime package initialization
-> orion.runtime.paper_runtime
-> orion.engine.navigation (partially initialized)
```

## Incumbent and donor ceiling

The paper-parity integration intentionally makes `orion.runtime.OrionRuntime`
the public default while retaining `KernelOrionRuntime`. The cycle begins
earlier: navigation imports the completion programme at module scope, which
forces the large `self_orion` package initializer before navigation has defined
its public class. The donor ceiling is an ordinary deferred implementation
import at the point the default navigator is constructed; no public API change
is required.

## Saturation assessment

- **Knowledge:** the full exception trace identifies the repeated module and
  the eager `src/orion/runtime/__init__.py` boundary.
- **Search universe:** direct kernel-runtime import, public runtime import,
  navigation-first construction, top-level `orion` import, and the original
  harness-package trace cover the affected cycle.
- **Formulation:** the public types must retain their identities after the lazy
  boundary; an import that merely stops raising is insufficient.

## Challenge to the saturation basis

Tests executed in an already populated interpreter can hide import cycles.
Each hostile import check must run in a fresh subprocess. Type-checker-only
imports must not become runtime imports.

## Why prior checks missed it

The paper-parity files were recovered through a forest integration after their
original commits. No fresh-interpreter harness import smoke test was bound to
that union, so two individually reasonable eager package exports composed into
a cycle.

## Frozen implementation hypothesis

1. Move the completion-programme import from navigation module scope into
   `PaperParityNavigator.__init__`, only when default cells are requested.
2. Preserve public names and identities: `OrionRuntime` is the paper-parity
   runtime; `KernelOrionRuntime` is the kernel runtime; `RuntimeResult` is the
   shared result type.
3. Add fresh-subprocess tests for kernel, public, navigation-first, top-level,
   and harness import roots.
4. Do not alter solver/runtime behavior or paper-parity selection.

## Honest terminals

- `PAPER_PARITY_RUNTIME_IMPORT_BOUNDARY_REPAIRED`
- `PAPER_PARITY_PUBLIC_EXPORT_IDENTITY_REGRESSED`
- `HARNESS_IMPORT_CYCLE_PERSISTS`
- `IMPORT_REPAIR_CANNOT_CHECK`

## Reopen triggers

Reopen if any fresh import root fails, if the public runtime ceases to be the
paper-parity runtime, if the kernel alias changes identity, or if resolving one
public attribute again executes a partial-module cycle.

## Explicit non-claims

This repair does not validate the paper-parity solver, the dual harness, or any
scientific receipt. It removes one partial-module cycle and preserves named
export identity. A later independent import failure remains a separate blocker,
not evidence against this boundary repair.
