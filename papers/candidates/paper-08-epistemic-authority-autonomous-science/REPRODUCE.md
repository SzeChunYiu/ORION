# Reproduce ORION-18 candidate formal results

**Candidate:** A Theory of Epistemic Authority for Autonomous Science  
**Status:** deterministic formal-support path; no cross-domain superiority/novelty authority  
**Python dependency:** standard library only for current checkers

## 1. Reproduction subject

Reproduce from an immutable commit containing:

- `manuscript/FORMAL_CORE_V1.md`;
- `formal/check_authority_calculus.py`;
- shared `papers/candidates/checkers/p8_finite_falsifiers_v1.py`;
- `papers/candidates/CHECK_RESULTS_V2.md`;
- `CLAIM_LEDGER_V1.md`.

The current working synchronization branch is `shadow/p6-p8-wide-sync-2026-08-17`. Replace this moving reference with an exact commit SHA in any archived result manifest.

## 2. Environment

Current V2 local environment:

```text
CPython 3.13.5
Linux 6.18.35 x86_64
```

The current checker uses no third-party package, network request, model/provider, judge or LLM API.

Suggested clean setup:

```bash
export PYTHONHASHSEED=0
python --version
uname -a
```

## 3. Primary deterministic checker

From repository root:

```bash
python papers/candidates/paper-08-epistemic-authority-autonomous-science/formal/check_authority_calculus.py
```

Expected V2 semantic signature:

```text
ORION-18 authority-calculus checks: PASS
  cross-domain no-coercion cases: 36
  scope narrowing/widening fixtures: confirmed
  stale-epoch replay rejection: confirmed
  finite-penalty additive counterexamples: 101
  dependency revocation + independent re-derivation fixture: confirmed
  post-hoc refusal non-prevention fixture: confirmed
  self-authorization countermodel: confirmed
  clean authorized coverage control: confirmed
  ORION-11-ORION-15 toy embedding fixtures: confirmed
```

The 36 domain-pair cases use six toy domains. Without explicit coercions, only same-domain authorization is accepted. This is a finite implementation fixture for the typed derivation rule, not evidence that real coercions are semantically sound.

## 4. Small theorem-boundary falsifier

```bash
python papers/candidates/checkers/p8_finite_falsifiers_v1.py
```

The smaller checker supplies an independently readable toy version of anti-laundering, scope monotonicity, additive-blocker, revocation, epoch/post-hoc timing, self-promotion and clean authorized controls.

## 5. Capture an immutable run

```bash
mkdir -p /tmp/orion-p8-repro
python papers/candidates/paper-08-epistemic-authority-autonomous-science/formal/check_authority_calculus.py \
  | tee /tmp/orion-p8-repro/check_authority_calculus.stdout.txt
python papers/candidates/checkers/p8_finite_falsifiers_v1.py \
  | tee /tmp/orion-p8-repro/p8_finite_falsifiers_v1.stdout.txt
sha256sum /tmp/orion-p8-repro/*.txt
```

A release/protected-evaluation gate should store stdout and hash manifests as immutable artifacts with custody metadata.

## 6. What the current checks establish

Bounded support exists for:

- domain-preserving authorization unless an explicit coercion path exists;
- scope narrowing versus scope widening;
- stale epoch rejection;
- the finite-penalty counterexample under extensible positive evidence;
- targeted dependency revocation with an alternate trusted derivation positive control;
- post-hoc refusal being non-preventive after irreversible commit;
- candidate-controlled self-admission countermodel;
- clean authorized coverage positive control;
- toy representability of five ORION-11–ORION-15 hard-obligation gate shapes.

They do **not** establish:

- semantic soundness of any real cross-domain coercion;
- exact ORION-11–ORION-15 decision-equivalent embedding;
- faithful ETAS/FAVA/SecPAL/Delegation-Logic embeddings;
- that cross-domain typing beats independent correct local gates;
- reduced real unauthorized action without excessive refusal;
- novelty or publication readiness.

## 7. Next reproducibility layers

### A. Exact ORION-11–ORION-15 embeddings
Freeze current native gate fixtures with protocol/registry identities and require decision equivalence under the ORION-18 representation.

### B. Authorization-donor fixtures
Encode representative native policy decisions from trust-management/effect/permission systems where specifications/code permit. ORION-18 must preserve those decisions before claiming generalization.

### C. Cross-domain attack generator
Create versioned paired cases for:

- valid local judgment + invalid foreign-domain use;
- valid registered coercion positive control;
- stale epoch replay;
- scope widening;
- revoked ancestor;
- post-hoc refusal;
- `CANNOT_CHECK` versus `DENY`;
- clean authorized cases.

Each case needs exact hidden label, effect identity, domain/scope, evidence/grant lineage, obligations, coercion registry and expected terminal.

### D. Protected custody
#341 requires labels/evaluator rules not writable by the candidate under test. Freeze evaluator chronology, access telemetry and result hashes prospectively.

### E. Strong baselines
Compare against independent ORION-11–ORION-15 gates and strongest feasible effect/permission/authorization donor formulations, not only confidence/scalar/no-policy baselines.

## 8. Claim authority

`CLAIM_LEDGER_V1.md` is the current maximum claim boundary. ORION-18's decisive paper-level result remains `CANNOT_CHECK`: cross-domain composition must add anti-laundering/revocation value beyond already-correct independent gates and mature authorization systems without causing excessive refusal.