# ORION V3 Execution Takeover Implementation Plan

> **For Codex:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Convert the competing ORION V3 execution descriptions into one fail-closed, machine-checkable queue and execute every dependency-ready study on LUNARC without duplicate submission, post-outcome retuning, or paper-authority laundering.

**Architecture:** Add an execution-control layer beside the existing V3 theory package rather than editing the active theory branch in place. The layer separates source identity, protocol freeze, scheduler submission, raw terminal capture, result-bundle validation, scientific disposition, and paper synchronization. Queue conflicts stop scientific submission, while an explicitly labelled engineering reference check may still verify the pinned code and cluster environment.

**Tech Stack:** Python 3.11, pytest, JSON, SHA-256 manifests, Git/GitHub source identities, SLURM on LUNARC, existing `orion.discovery.frontier_dominance` reference implementation.

---

### Task 1: Freeze takeover source identities

**Files:**
- Create: `development/orion-v3-execution-takeover-2026-08-25/SOURCE_IDENTITY.json`
- Create: `development/orion-v3-execution-takeover-2026-08-25/DEVELOPMENT_PACKET.md`

**Steps:**
1. Record the exact V3 head, live `main`, issues #1325/#1329, PR #1326, and retrieval timestamps.
2. Hash the source issue bodies and branch execution backlog.
3. Verify that the takeover branch still points to the recorded V3 head.
4. Commit the packet before implementation.

### Task 2: Reproduce and classify the baseline

**Files:**
- Create: `development/orion-v3-execution-takeover-2026-08-25/BASELINE_RECEIPT.json`
- Create: `development/orion-v3-execution-takeover-2026-08-25/FAILURE_LEDGER.md`

**Steps:**
1. Install the pinned repository in a private environment.
2. Run `scripts/check_orion_discovery_v3.py`, the focused hostile suite, the finite census, and compilation.
3. Run the failing PR checks locally where reproducible.
4. Record each failure with command, exit code, failing boundary, and whether it is V3-local or inherited from `main`.
5. Do not fix any failure until a minimal reproduction identifies its root cause.

### Task 3: Canonical execution-manifest reconciliation

**Files:**
- Test: `tests/unit/discovery/test_execution_takeover.py`
- Create: `src/orion/discovery/execution_takeover.py`
- Create: `research/orion-discovery-v3/EXECUTION_TAKEOVER_MANIFEST_V1.json`
- Create: `scripts/check_orion_execution_takeover.py`

**Steps:**
1. Write a failing test that rejects duplicate job IDs, ambiguous aliases, missing dependencies, and conflicts between #1329 and the branch backlog.
2. Run the test and confirm it fails because the takeover module is absent.
3. Implement immutable source records and fail-closed queue reconciliation.
4. Add the latest 13-job order while retaining all 11 branch job identities as explicit aliases or unresolved predecessors.
5. Require every executable job to have exact inputs, resource class, dependencies, required outputs, terminals, and authority ceiling.
6. Verify the focused tests and structural checker pass.
7. Commit the reconciled manifest and checker.

### Task 4: Protocol-freeze and SLURM packaging

**Files:**
- Test: `tests/unit/discovery/test_execution_takeover.py`
- Modify: `src/orion/discovery/execution_takeover.py`
- Create: `scripts/freeze_orion_execution_job.py`
- Create: `scripts/package_orion_slurm_job.py`

**Steps:**
1. Write failing tests for outcome-bearing protocol inputs, stale source SHA, missing donor-product definitions, hidden scalarization, and duplicate scheduler submission.
2. Implement canonical JSON hashing and a protocol state machine: `DRAFT -> FROZEN -> SUBMITTED -> TERMINAL -> VALIDATED`.
3. Make scientific submission refuse while a job is ambiguous or under-specified.
4. Generate SLURM bundles containing the exact Git object, input hashes, environment description, command, resource request, and output manifest.
5. Add deduplication against both a local submission ledger and live `squeue`/`sacct` identities.
6. Verify red-green tests and commit.

### Task 5: LUNARC engineering reference check

**Files:**
- Create remotely: one content-addressed engineering-check bundle under the user's ORION scratch area.
- Create locally after completion: `development/orion-v3-execution-takeover-2026-08-25/LUNARC_REFERENCE_RECEIPT.json`

**Steps:**
1. Package the pinned V3 object without scientific outcome inputs.
2. Check for an existing identical job before submission.
3. Submit a small CPU job running the structural checker, hostile suite, finite census, and compilation.
4. Capture job ID, scheduler record, stdout/stderr hashes, environment identity, exit code, and generated finite receipt hash.
5. Label the terminal `ENGINEERING_REFERENCE_CHECK_ONLY`; do not count it as a V3 scientific job.

### Task 6: Execute dependency-ready scientific jobs

**Files:**
- One immutable result directory per canonical job under `research/orion-discovery-v3/executions/<job-id>/<protocol-hash>/`.

**Steps for each job:**
1. Confirm the job is unambiguous, frozen, dependency-ready, and not already submitted or terminal.
2. Validate matched donor information, tools, evaluators, vector resources, and authority contracts.
3. Submit the smallest adequate SLURM resource class.
4. Monitor to a scheduler terminal and preserve stdout, stderr, raw data, and environment identity.
5. Produce every required bundle file from `AI_EXECUTOR_PROMPT_V1.md`.
6. Run an independent checker implementation where possible; otherwise emit `EXTERNAL_AUTHORITY_BLOCKER.json`.
7. Record positive, adverse, donor-tie, resource-incomparable, or `CANNOT_CHECK` terminals without retuning.
8. Commit one bounded result per job.

### Task 7: Root-cause and successor loop

**Files:**
- Create per failure: `research/failures/<dated-failure>/README.md`
- Create per justified successor: a separately identified development packet and protocol.

**Steps:**
1. Reproduce each framework or execution failure.
2. Trace the failure to the earliest broken boundary.
3. Write a failing regression test before implementation.
4. Implement the minimal fix on the takeover branch.
5. Rerun the original job only when the frozen protocol permits infrastructure retry; otherwise create a new successor identity.
6. Preserve the predecessor terminal permanently.

### Task 8: Paper synchronization and submission gates

**Files:**
- Modify only paper artifacts whose exact atomic authority transition is accepted.
- Create: `papers/P1_P15_EXECUTION_TAKEOVER_STATUS_V1.json`

**Steps:**
1. Resolve paper identity through `papers/README.md`, `papers/PAPER_ALIASES.md`, and the paper registry.
2. Map validated job atoms to P1-P15 without cross-paper double counting.
3. Keep specialist-submission and top-tier/external-authority gates separate.
4. Reproduce source, tables, figures, PDF, package, rights, and reviewer-access artifacts.
5. Preserve all adverse/null/harmful/`CANNOT_CHECK` results in manuscripts and claim ledgers.
6. Bind exact submission bytes only after independent scientific and visual/package audits.
7. Leave final authorship, declarations, and journal upload to the owner.

