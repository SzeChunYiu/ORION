# Q1-C1 GitHub resource-closure protocol

Status: frozen before remote execution; `EXECUTION_STATUS=NOT_STARTED`

## Scope

This is a fresh Q1-C1 execution cycle on GitHub-hosted Linux. It inherits the
fixed candidate, theorem, fixtures, proof certificate, mutation registry,
result schema, two-lane separation, and two-phase comparison rules. It inherits
no PASS terminal from a local run and does not reinterpret any prior result.

## Environment contract

The runner commit must be a strict descendant of this protocol. The remote job
must use:

- Ubuntu 24.04 on x86-64;
- CPython exactly 3.12.13;
- `uv==0.11.33`;
- `uv sync --frozen --all-extras --python 3.12.13` from the committed lock;
- NumPy exactly 2.3.5;
- cryptography exactly 50.0.0; and
- `/usr/bin/strace -f -qq -e trace=network` successfully launching every
  traced negative control and scientific child.

The resolved interpreter path is host-specific. Its path and executable
SHA-256 must be recorded, and the coordinator and every child must use that one
resolved interpreter. Dependency, Python, interpreter-identity, audit-hook, or
strace failure blocks or invalidates the run under the frozen Q1-C1 terminal
rules; it cannot be silently repaired within a result commit.

## Commit chronology

The remote automation must create two new commits on a new evidence branch:

1. **Lane-result commit.** From a clean runner checkout, execute `prepare` and
   commit the complete Lane A and Lane B terminals, raw captures, audit logs,
   and traces. The coordinator directory must not exist.
2. **Coordinator-result commit.** In a separate job, check out the exact
   lane-result commit, recreate the lock-exact environment, verify every lane
   byte against git, execute `compare`, and commit only the coordinator output.

The second job must not edit any lane terminal. The source branch and evidence
branch are distinct. A workflow log or uploaded artifact without both commits
is diagnostic only.

## Release condition

The coordinator must serialize all of the following before this cycle can
close Q1-C1:

- terminal `PASS`;
- all sixteen obligations `PASS`;
- 23 of 23 mutations `KILLED`;
- exact historical replay with no semantic diff;
- exact 4,161-row Lane A/Lane B fieldwise comparison with no diff;
- dependency lock closed; and
- syscall-trace gates true for Lane A replay, Lane A adapter, Lane B, and the
  coordinator.

Any scientific counterexample remains a counterexample. Any custody or schema
failure remains invalid. A resource failure remains blocked. No retry may drop
an unfavorable fixture, mutation, field, or lane.

## Authority limits

Even a valid PASS grants only the stated Q1-C1 mathematical theorem, Lane B's
algorithm binding, and finite production agreement on the declared 4,161-row
corpus. It grants no novelty, arbitrary-n production implementation
equivalence, physical-resource claim, runtime superiority, manuscript quality,
submission readiness, merge authority, or publication authority.
