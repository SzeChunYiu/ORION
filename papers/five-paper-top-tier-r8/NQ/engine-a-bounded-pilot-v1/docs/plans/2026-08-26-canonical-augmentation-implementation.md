# Canonical-Augmentation Implementation Plan

> **For Codex:** REQUIRED SUB-SKILL: test-driven development and verification before completion.

**Goal:** Replace raw-domain class generation with a lossless canonical construction path,
while retaining the raw generator as a small-domain reference oracle.

**Architecture:** `augmentation.py` owns invariant parent selection, intrinsic stabilizer
actions, extension orbits, level generation, hereditary constraint profiles, and fail-closed
coverage. Existing canonicalization and factorization modules remain unchanged.

**Tech stack:** Python 3.11+, pytest, jsonschema, Ruff.

### Task 1 — stabilizer extension orbits
1. Write failing brute-force small-GL orbit tests.
2. Observe the missing-module failure.
3. Implement support-basis intrinsic stabilizers plus the single outside-span orbit lemma.
4. Re-run focused tests.

### Task 2 — canonical construction path
1. Write failing canonical-parent, uniqueness, and level tests.
2. Implement one-level and bounded multi-level generation.
3. Re-run focused tests.

### Task 3 — hereditary pruning and resource terminal
1. Write failing short-subset DP, factor-prune, and resource tests.
2. Implement exact predicates and fail-closed coverage.
3. Re-run focused tests.

### Task 4 — raw equivalence panels
1. Compare every augmentation level with raw canonical filtering on complete small panels.
2. Compare pruned panels with independently filtered raw records.
3. Freeze panel sizes, record hashes, and all mismatch counts.

### Task 5 — proof and immutable closeout
1. Write the induction proof for orbit completeness and uniqueness.
2. State scaling and remaining full-execution gaps.
3. Run pytest, branch coverage, Ruff, format, compileall, schemas, manifests, and digests.
