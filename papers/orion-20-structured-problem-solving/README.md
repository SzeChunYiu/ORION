# P10 — Structured problem solving

P10 is currently a prospective maximum-claim manuscript, not a completed
empirical paper. `P10_ACTIVE_CLAIM_AUTHORITY_V1.json` is the machine-readable
active record and `CLAIM_EVIDENCE_LEDGER.md` states the evidence required for
each hypothesis.

H1–H6 are `PROSPECTIVE_NOT_EXECUTED`. Their outcome-free protocol is frozen,
but its protected donor, evaluator, custody, and attainability inputs are absent,
so execution is not authorized. This is not a negative result and does not
authorize a positive one. The shared ORION learning-machine lane remains bounded
to `LOCAL_REPRODUCIBLE_CORE_ONLY` and cannot discharge a P10 hypothesis.

The four execution domains (Lean via LeanDojo/miniF2F, SyGuS via cvc5, IPC
planning via Fast Downward/VAL, code generation via EvalPlus), their public
sources and their licence statuses are frozen in
`protocol/P10_DOMAIN_SOURCE_FREEZE_V1.json` (checker:
`protocol/check_p10_domain_source_freeze_v1.py`; tests:
`tests/unit/p10/test_p10_domain_source_freeze.py`). That freeze populates the
H1-H6 design at the domain/source/licence layer only: 100 tasks per domain and
80 known-method controls are committed minimums, not selected or executed
counts, and the per-task enumeration is NOT_POPULATED. Baseline-implementation,
H1-H6 execution and candidate-edit machine-checking boxes carry CANNOT_CHECK
verdicts with reasons in the same artifact.
