# P2 eager-import containment

Date: 2026-08-24

Frozen base: `96f6082f492da96e31edfd6a5ece5bfdea753f73`

Status: **FROZEN BEFORE IMPLEMENTATION**

Authority: Python import containment only; no P2 repair and no scientific result.

## Atomic development question

Can `orion_research_harness` remain importable for independent research domains
without eagerly importing the known-incomplete P2 runner, while keeping direct
P2 runner import visibly adverse?

## Reproduced failure

On the frozen base, importing the package root loads
`paper_programme_conformance`, which imports `orion.study.p2.runner`. The runner
expects `ReadClassification`, `ReadEvent`, and `RouteEvent`, while the systems
module landed by PR #1078 exposes the newer `ReadEncounter` and `RouteTrial`
schema. Collection stops at the first missing symbol.

This is not a one-name defect. The interleaved runner and systems modules also
disagree on resource, read, route, stop, and trace field names. Adding an alias
would hide the first exception without restoring a coherent P2 evaluator.

## Frozen implementation hypothesis

1. Move P2-only imports in `paper_programme_conformance` to the P2 fixture and
   execution paths that use them.
2. Require a fresh subprocess to import `orion_research_harness` successfully.
3. Require a separate fresh subprocess importing `orion.study.p2.runner` to
   retain the exact `ReadClassification` adverse signature.
4. Do not edit P2 systems, runner, gold, manuscripts, ledgers, evidence, or
   scoring semantics in this iteration.

## Honest terminals

- `P2_EAGER_IMPORT_CONTAINED`
- `P2_RUNNER_SCHEMA_INTERLEAVING_PRESERVED`
- `HARNESS_PACKAGE_IMPORT_STILL_BLOCKED`
- `P2_CONTAINMENT_CANNOT_CHECK`

## Reopen triggers

Reopen if package import again executes the P2 runner, if direct P2 runner
import no longer exposes its adverse state without a separately validated
schema repair, or if any non-P2 package-root export changes identity.

## Explicit non-claims

This iteration does not make the P2 programme conformance check executable. It
does not validate P2 results or choose between the old and new event schemas.
It only prevents that incomplete, independently owned subsystem from blocking
unrelated harness domains at import time.
