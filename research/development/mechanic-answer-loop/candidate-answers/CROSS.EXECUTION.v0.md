# Candidate answer — CROSS.EXECUTION.v0

**Target dimensions:** VERIFICATION, STATE, TRANSITION_MODEL.
**Incumbent evidence:** RAKL `publication/papers/paper-05-verified-discovery-in-mathematics/ASSURANCE_V3_BINDING_ADDENDUM_20260815.md`, `STRICT_PROMOTION_PATH_ADDENDUM_20260815.md` @ `bd4ce50f`; RAKL `publication/papers/paper-03-method-evolution-mechanics/sections/05_governed_upgrade_protocol.tex` @ `bd4ce50f` (§post-promotion attestation).

## Proposed step-specific contract

**Verification — execution is identity-bound end to end.** An execution receipt binds: the exact input source digests, the checker/tool identity digest and its manifest, the executing environment identity, and a separate attestor identity distinct from the proposer. Executor invariance is the licensed test: the same exact artifact/evidence chain must receive the same authority stage regardless of executor class (symbolic vs LLM vs human), while self-review still blocks. Dependency closure is load-bearing: the transitive dependency manifest of what was executed must *equal* the declared closure (ProofDAG-style equality, not subset).

**State.** Execution state distinguishes: candidate-passed-checks vs active-state-descends-from-candidate vs exact-active-state post-validation (the three post-promotion attestation stages) — deployment is never inferred from authorization. Every promoted execution carries an exact rollback parent.

**Transition model.** Deterministic replay is the ground transition: given identical input digests, checker identity and environment identity, re-execution must reproduce the receipt or emit a typed divergence (nondeterminism is declared, never discovered by surprise). A receipt whose inputs cannot be re-resolved at their digests transitions to CANNOT_CHECK, not to trusted history.

## Known-answer / hostile test candidates

1. Same artifact chain executed by two executor classes → same authority stage; proposer self-attestation → blocked in both.
2. Dependency manifest missing one transitive element → equality check fails, receipt refused.
3. Hostile: mark a candidate as deployed from its authorization record alone → must fail (attestation stage missing).

## Not licensed

Receipt discipline does not establish performance or capability claims for any executor; those remain benchmark obligations (CROSS.BENCHMARK).
