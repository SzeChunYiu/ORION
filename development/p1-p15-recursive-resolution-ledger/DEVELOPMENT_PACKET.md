# P1–P15 recursive resolution ledger

## Scope

Add one machine-readable programme ledger that classifies every paper's current
claim/evidence state without changing any scientific result.  The ledger is an
audit and routing artifact, not a promotion instrument.

## Base and branch

- base revision: `fd9892fdafd7734b07c8b24a4384c9e9561b1349`
- branch: `codex/p1-p15-recursive-resolution-ledger`
- publication: local commit only; no push or pull request in this task

## Required distinctions

Every ledger item uses exactly one of:

1. `FIXED_BY_EXISTING_PR`
2. `ACTIVE_POSITIVE_AUTHORITY`
3. `HISTORICAL_ADVERSE_RESULT`
4. `PROSPECTIVE_SUCCESSOR_REQUIRED`
5. `EXTERNAL_EVIDENCE_BLOCKER`

Historical adverse evidence is append-only.  It may be superseded for a new,
prospectively frozen claim identity, but it may never be deleted, overwritten,
or relabelled positive.  A successor failure remains a result; it is not a
license to tune the gate or endpoint after outcomes are visible.

## Deliverables

- `research/paper-programme-v1/P1_P15_RECURSIVE_RESOLUTION_LEDGER_2026-08-23.json`
- `src/orion/publication/recursive_resolution_ledger.py`
- `tests/unit/publication/test_recursive_resolution_ledger.py`

## Acceptance checks

- all and only `P1` through `P15` are represented in order;
- every item has a stable identity, a category, sources, and an executable next
  step with success and failure terminals;
- historical items are immutable;
- prospective and external items cannot grant positive authority;
- existing-PR fixes include a PR number, URL, head branch, and verification
  command;
- positive authority has an explicit bounded scope and authority artifact;
- the validator rejects post-hoc relabelling, missing papers, missing sources,
  and authority granted from blockers.

## Out of scope

- rerunning protected or external experiments;
- changing claim terminals or manuscript prose;
- merging, publishing, or representing an open repair branch as landed;
- guaranteeing that any prospective successor will pass.
