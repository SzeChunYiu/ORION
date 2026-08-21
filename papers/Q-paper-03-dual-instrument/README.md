# Q3 — Controller–host agreement benchmark

**Stable ID:** ORION-Q3  
**Canonical manuscript:** `manuscript/main.tex`  
**Status:** `MANUSCRIPT_REVIEW_PASS / EVIDENCE_GATE_BLOCKED`

## One job

Q3 is now the benchmark paper, not the systems-harness paper. It defines a receipted controller–host agreement measurement for live research-frontier decisions and reports the frozen V0 instance. The two lanes receive the same admissible evidence but use architecturally distinct decision procedures: an LLM-host-driven research lane and a typed non-LLM campaign controller.

P15 (`papers/paper-15-orion-research-harness/`) owns the broader systems-harness guarantee surface. Q3 includes only enough receipt/custody architecture to make the benchmark interpretable.

## Current result

Benchmark V0 was frozen before either lane outcome. The lanes agree on the responsible layer and primary next move: representation-regime characterization. The typed controller independently withholds the unlicensed representation split because its predicate obligation is unresolved. Deferred scoring is `ALIGNED` after the subsequently executed characterization/closure lanes.

This is **one instance**. It supports the benchmark definition and first measurement only. The publication plan requires at least 2–3 additional frozen question instances before standalone submission; no such series exists on current main, so the evidence gate remains blocking.

## Current defect status

The V1 manuscript's D2/D3 defects are stale. Current `test_invalid_content_recovery.py` verifies structured failure for malformed successful receipts and explicit audit-preserving recovery. The rewrite reports them as repaired historical defects rather than open failures.

See `JOURNAL_READINESS.md`, `REPRODUCE.md`, and `CLAIM_LEDGER_V2.md`.