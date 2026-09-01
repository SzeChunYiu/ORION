# NQ Engine A Engineering-Staging Implementation Plan

> **For Codex:** REQUIRED SUB-SKILL: Use test-driven development task-by-task.

**Goal:** Build an exact, fail-closed engineering staging engine for canonical multiset
generation and multi-bin zero-sum factorization on `C_p^d`, without claiming independent
replay authority.

**Architecture:** A small dependency-light Python package separates finite-group
primitives, GL canonicalization/orderly generation, exact DP, certificate validation,
receipt semantics, and deterministic manifests. JSON Schema artifacts bind the external
contract.

**Tech Stack:** Python 3.11+, pytest, jsonschema, Ruff.

---

### Task 1: Primitive group and canonicalization
- Write failing tests for strict vector validation, modular addition/rank, orbit invariance,
  and canonical idempotence.
- Run the focused tests and record the expected missing-module failure.
- Implement `group.py` and `canonical.py` minimally.
- Re-run focused and full tests.

### Task 2: Canonical orderly generation and coverage
- Write failing tests for deterministic ordering, duplicate rejection, rank slices, complete
  coverage counters, and explicit resource termination.
- Observe failure; implement `orderly.py`; re-run.

### Task 3: Exact multi-bin factorization DP
- Write failing tests comparing against a separate brute-force oracle on `C_2`, `C_3`, and
  `C_2^2`, plus positive, negative, permutation, duplicate-heavy, and empty cases.
- Observe failure; implement `factorization.py`; re-run.

### Task 4: Certificate, schemas, and hostile mutation
- Write failing tests for disjointness, nonempty bins, index bounds, recomputed sums, malformed
  vectors, wrong schema versions, and mutated certificates.
- Observe failure; implement certificate validation and JSON schemas; re-run.

### Task 5: Fail-closed receipts and deterministic manifests
- Write failing tests ensuring partial/resource runs never become negative proofs and exposure
  markers are mandatory; test stable manifest bytes and tamper detection.
- Observe failure; implement `receipt.py` and `manifest.py`; re-run.

### Task 6: Completeness and quality gates
- Document the DP and orbit-completeness arguments and full-census gaps.
- Run pytest with branch coverage, Ruff, format check, compileall, schema checks, manifest
  verification, and forbidden-token/diff hygiene checks.
- Generate immutable engineering receipts and a complete-tree digest.
