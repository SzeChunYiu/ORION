# ORION Research Harness

`orion-research-harness` makes the **canonical ORION runtime** usable from a local research folder while a tool-capable host supplies capabilities that ORION core intentionally does not own. `OrionRuntime` remains the scientific control kernel; the harness adds replayable, digest-bound host capability receipts.

The package on `main` is the canonical base. ORION-Q and other long-running programmes extend it through domain-neutral campaigns rather than separate harness engines.

## Install

```bash
python -m pip install -e '.[dev]'
python -m pip install -e 'packages/orion-research-harness[dev]'
```

## Ordinary research problems

```bash
orion-harness init .research --project-root .
orion-harness problem-add .research p1 "Research question" --criterion "Preserve frozen gates."
orion-harness solve .research p1
```

Host requests are deterministic and persisted under `.orion-harness/requests`; ingested results are digest-bound to the exact request. Web/GitHub/model capabilities are supplied by the surrounding host rather than pretended by the package.

## Local capabilities and process safety

`FILE_READ`, `FILE_WRITE`, and `FILE_LIST` are confined to `project_root`. `SHELL` and `PYTHON` are normal subprocesses, **not an OS sandbox**, and remain disabled by default. Enable them only for a workspace whose host accepts that risk:

```bash
orion-harness init .research --project-root . --allow-process-tools
```

`SHELL` never uses `shell=True`, process timeouts are capped, and receipts record the unsandboxed execution boundary.

## Persistent scientific campaigns

Campaigns add a reusable multi-cycle layer above the same workspace and host-receipt protocol:

```text
frozen campaign state
  -> production Self-ORION responsibility/revision/computation control
  -> selected registered capability
  -> digest-bound host/local result
  -> evidence admission + protected-custody checks
  -> immutable next state / cycle receipt
  -> repeat
```

Campaign code is domain-neutral. Domain-specific semantics live under `orion_research_harness/domains/`.

List built-ins and run one:

```bash
orion-harness campaign-builtins
orion-harness init .research --project-root . --allow-process-tools
orion-harness campaign-start .research orion-q:max-r6-live
orion-harness campaign-run .research orion-q:max-r6-live
orion-harness campaign-state .research orion-q:max-r6-live
```

The ORION-Q MAX-R6 adapter binds the existing N0 donor-closure, N1 interface, N2 method-language, and P10 candidate-generation stages as capabilities. The reserved stretched-N2 subject stays a protected reference until a later frozen R6 gate explicitly releases it.

## Authority boundary

A host result or campaign capability never grants scientific, revision, novelty, adoption, promotion, merge, or global-stop authority by itself. The campaign layer rejects authority-bearing capability output before evidence admission and reuses production ORION control modules for decisions.

Negative, null, blocked, and `CANNOT_CHECK` outcomes are first-class. If a campaign exposes a harness defect, repair the harness under the development protocol and replay the unchanged scientific gate; do not weaken the scientific success criterion.
