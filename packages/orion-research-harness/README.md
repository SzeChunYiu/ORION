# ORION Research Harness

`orion-research-harness` makes the **canonical ORION runtime and mechanics programme** usable from a local research folder while a tool-capable host supplies capabilities that ORION core intentionally does not own. `OrionRuntime` remains the scientific control kernel; the harness adds replayable, digest-bound host capability receipts plus discoverable bridges to ORION's canonical mechanics, fibres, saturation, and Self-ORION research surfaces.

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

The ordinary solve path invokes canonical `OrionRuntime` / `OrionSolver`, whose governed root cycle is `ORION_SOLVE -> FRAME -> SEARCH -> ABSORB -> RECONSTRUCT -> DETECT -> DIAGNOSE -> REFRAME -> REOPEN -> SATURATE_BOUNDED` as applicable. The saved run includes the immutable mechanic receipts and can be inspected with:

```bash
orion-harness runs .research
orion-harness run-mechanics .research <run-id>
```

Host requests are deterministic and persisted under `.orion-harness/requests`; ingested results are digest-bound to the exact request. Web/GitHub/model capabilities are supplied by the surrounding host rather than pretended by the package.

## Find the mechanic instead of knowing its module

ORION's paper/runtime surface is larger than the root solve loop. The canonical mechanics programme contains a recursively audited **59-cell graph** including decomposition, search/absorption/reconstruction, diagnosis/reframing, fibre reopening, bounded saturation, authority, experience, review, benchmarking, experiment selection, execution, and context policy. The harness reads that graph from canonical ORION; it does not maintain a second hand-written mechanics ontology.

```bash
orion-harness mechanics-coverage
orion-harness mechanics
orion-harness navigate 'fibre problem solver'
orion-harness navigate 'atomization of a problem'
orion-harness navigate 'saturation of knowledge'
orion-harness mechanic FRAME.DECOMPOSE.v0
orion-harness mechanic REOPEN.FIBRE.v0
```

`mechanics-coverage` is a release/integration check: it requires the canonical 59-cell graph, the runtime root mechanics, and key paper-bound anchors such as `FRAME.DECOMPOSE`, `REOPEN.FIBRE`, and the bounded-saturation children. It establishes **structural discoverability only**. It does not manufacture empirical validity or scientific authority for a mechanic.

### Problem atomization and recursive atoms

Problem decomposition is represented by `FRAME.DECOMPOSE.v0`, with supported decomposition changes routed through `REFRAME.DECOMPOSITION.v0` and affected fibres reopened by `REOPEN.FIBRE.v0`. The model-free `MechanicalControlRuntime` / `MechanicalFirstPlanner` is also exposed by navigation as `RUNTIME.MECHANICAL_CONTROL.v1`; it generates required evidence, parent-discipline, search-coverage, failure-diagnosis, verification, and saturation-challenge questions from typed problem state.

The separate recursive atom calculus is a **study/governance calculus**, not a magic atomizer or novelty oracle. Inspect its exact dispositions, recursion-stop reasons, negative-history categories, and post-map challenge surface with:

```bash
orion-harness atom-calculus
```

It may support decisions such as decompose, subsume, interaction-only, no incremental value, non-identifiable, or cannot-check. It grants no novelty or self-promotion authority.

### Development fibre versus method fibre

ORION has two different fibre concepts and the harness keeps them separate.

A **Self-ORION `DevelopmentFibre`** is the canonical successor of RAKL `ProblemFibre`: a target-conditioned working view for one mechanic containing its cell, open questions, empirical frontier, related/failure episodes, transfer receipt, warnings, and snapshot identity. Compile or rank them directly from a workspace:

```bash
orion-harness fibre .research FRAME.DECOMPOSE.v0
orion-harness fibres .research --limit 12
```

A **P6 `MethodFibre`** is claim-relative formal structure: structural reduction/signature, evidence-bound membership, substitution/composition, and lineage preservation. It is not the same as a research problem fibre and cannot authorize scientific transfer merely from structural equivalence:

```bash
orion-harness method-fibre-surface
orion-harness navigate 'method fibre'
```

### Knowledge and development saturation

The runtime solver uses bounded saturation under a frozen basis. Flatness is not universal completeness, and resource exhaustion does not become closure. The broader Self-ORION development surface is non-compensatory across knowledge, search universe, formulation, operator, experience pattern, obstruction, relation, path, and meta-method axes.

```bash
orion-harness saturation-surface
orion-harness navigate 'knowledge saturation'
```

The harness exposes both surfaces and their source modules. It does not collapse route stopping into task saturation or claim recall from repeated flatness.

## Paper mechanics versus proposed research gaps

The repository's executable-embedding audits distinguish mechanics that are already live, mechanics whose semantics are distributed/partial, and research objects that remain proposed. The harness follows the same rule:

- implemented canonical mechanics are discoverable and, where there is a canonical runtime/control API, routed to that implementation;
- distributed mechanics expose their actual owning modules/contracts rather than a fabricated unified implementation;
- paper-only or proposed gaps remain visibly proposed/open and must not be represented as executable authority.

This is intentional. “All mechanics are in the harness” means no implemented canonical mechanic is silently hidden or bypassed; it does **not** mean prose proposals are falsely promoted to runtime capability.

## Local capabilities and process safety

`FILE_READ`, `FILE_WRITE`, and `FILE_LIST` are confined to `project_root`. `SHELL` and `PYTHON` are normal subprocesses, **not an OS sandbox**, and remain disabled by default. Enable them only for a workspace whose host accepts that risk:

```bash
orion-harness init .research --project-root . --allow-process-tools
```

`SHELL` never uses `shell=True`, process output is bounded and drained continuously, POSIX process groups are killed on timeout, and nonzero process exits are persisted as failed capability receipts rather than successful scientific evidence.

A failed receipt binds to its deterministic request identity, so an orchestration failure (missing interpreter, absent module, dead network) would otherwise pin the workspace to that failure forever. `retry-failed` frees the identity without erasing history:

```bash
orion-harness retry-failed .research               # archive every failed result
orion-harness retry-failed .research hostreq:...   # archive one failed result
```

Only **failed** results can be archived; successful receipts stay immutable. The failed receipt moves, bytes unchanged, to `results/archived/<request>.failed-<n>.json`, the request becomes pending again, and the same deterministic request can then be serviced after the host repairs the environment.

One narrow exception exists for a *successful* receipt whose content violates the task schema (which the recursive solver surfaces as `HOST_CAPABILITY_FAILED` rather than a traceback): `retry-failed <ws> <request_id> --invalid-content --reason "..."` archives it to `results/archived/<request>.invalid-<n>.json` with a sidecar recording the stated reason, freeing the identity for a corrected receipt. The reason is mandatory and the original bytes are preserved.

## Persistent scientific campaigns

Campaigns add a reusable multi-cycle layer above the same workspace and host-receipt protocol:

```text
frozen campaign state
  -> production Self-ORION responsibility/revision/computation control
  -> selected registered capability
  -> digest-bound host/local result
  -> strict result-contract validation
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

Campaign state and contracts are strict and non-coercing. A malformed `success=true` result is `CAPABILITY_CONTRACT_FAILED` and cannot change scientific observations or advance the campaign. Protected-reference `released` is a real boolean; a string such as `"false"` is rejected rather than truthily interpreted.

## Authority boundary

A host result, mechanic navigation result, fibre working view, atom-calculus disposition, saturation report, or campaign capability never grants scientific, revision, novelty, adoption, promotion, merge, or global-stop authority by itself. The campaign layer rejects authority-bearing capability output before evidence admission and reuses production ORION control modules for decisions.

Negative, null, blocked, and `CANNOT_CHECK` outcomes are first-class. If a campaign exposes a harness defect, repair the harness under the development protocol and replay the unchanged scientific gate; do not weaken the scientific success criterion.
