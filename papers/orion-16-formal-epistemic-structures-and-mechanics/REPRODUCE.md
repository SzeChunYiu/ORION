# Reproduce ORION-16 candidate formal results

**Candidate:** Formal Epistemic Structures and Mechanics  
**Status:** deterministic formal-support path; no novelty/empirical-superiority authority  
**Python dependency:** standard library only for current checkers

## 1. Reproduction subject

Reproduce from an immutable commit containing:

- `manuscript/FORMAL_CORE_V1.md`;
- `formal/check_finite_models.py`;
- `../checkers/p6_finite_falsifiers_v1.py` via the candidate-root shared checker directory;
- `../../CHECK_RESULTS_V2.md`;
- `CLAIM_LEDGER_V1.md`.

The working synchronization branch is `shadow/p6-p8-wide-sync-2026-08-17`. Before any publication claim, replace the branch reference in an archival manifest with the exact immutable commit SHA.

## 2. Environment

Current V2 local environment:

```text
CPython 3.13.5
Linux 6.18.35 x86_64
```

The scripts use no third-party Python package and make no network/model/provider/judge/LLM API calls.

Record at reproduction time:

```bash
python --version
uname -a
printf 'PYTHONHASHSEED=%s\n' "${PYTHONHASHSEED:-unset}"
```

No checker currently depends on hash iteration order, but a clean run may set:

```bash
export PYTHONHASHSEED=0
```

## 3. Primary deterministic checker

From repository root:

```bash
python papers/orion-16-formal-epistemic-structures-and-mechanics/formal/check_finite_models.py
```

Expected V2 structural signature:

```text
ORION-16 finite-model checks: PASS
  DAGs enumerated: 543
  reopening cases: 130320
  scientific-projection separated-commutation cases: 1536
  ordered-history distinction / independent trace equivalence: confirmed
  non-escalation compositions: 8192
  residual-obligation preservation fixture: confirmed
  recursive self-loop countermodel: detected
  candidate-controlled authorization countermodel: detected
```

Whitespace/label formatting can change in later versions; the numeric counts and semantic case identities must be versioned if the generator changes.

## 4. Small theorem-boundary falsifier

```bash
python papers/candidates/checkers/p6_finite_falsifiers_v1.py
```

The small checker is intentionally redundant with selected large-checker cases. It exists as an easy-to-audit theorem-boundary fixture and currently covers reopening, state-vs-history commutation, non-escalation, residual obligation retention and recursive/self-authorization countermodels.

## 5. Capture an immutable run

Suggested current capture procedure:

```bash
mkdir -p /tmp/orion-p6-repro
python papers/orion-16-formal-epistemic-structures-and-mechanics/formal/check_finite_models.py \
  | tee /tmp/orion-p6-repro/check_finite_models.stdout.txt
python papers/candidates/checkers/p6_finite_falsifiers_v1.py \
  | tee /tmp/orion-p6-repro/p6_finite_falsifiers_v1.stdout.txt
sha256sum /tmp/orion-p6-repro/*.txt
```

A release/archive gate should copy the stdout files and hash manifest into an immutable results directory or archival artifact rather than relying on `/tmp`.

## 6. What the current checks establish

They support bounded implementation correspondence for:

- dependency-descendant reopening and unaffected-state preservation;
- current-scientific-state commutation under a finite separated mechanic class;
- the fact that ordered audit history need not be literally equal across independent execution orders;
- two-step authority non-escalation in the bounded token model;
- residual-obligation persistence fixture;
- recursive self-loop and candidate-controlled admission countermodels.

They do **not** establish:

- completeness of real dependency graphs;
- unrestricted proof correctness;
- donor-faithful embedding of DEL/AGM/TMS/ETAS/FAVA/repair systems;
- exact ORION-11 registry/protocol correspondence;
- empirical advantage;
- novelty or publication readiness.

## 7. Next reproducibility layers

### A. Exact ORION-11 embedding
Freeze current ORION-11 mechanic/reframe/reopening decision fixtures and test decision equivalence under the ORION-16 encoding.

### B. Donor-native fixtures
Where formal specifications/code permit, construct fixtures reproducing native decisions for effect/authorization/rollback donors before adding ORION-16-only dimensions.

### C. Exhaustive trace semantics
Replace the two-event history fixture with a bounded event-structure/trace enumerator that distinguishes state projection equality from trace equivalence and chronology-sensitive policies.

### D. Proof assistant
After semantics freeze, select at least one nontrivial theorem—preferably history-aware composition or residual-obligation preservation—for mechanization. Record proof-assistant version and exact proof hash.

### E. Cross-domain benchmark
#353 requires an exact-ground-truth non-ORION-11 transfer family plus a negative control and strongest donor-specific baselines.

## 8. Claim authority

Current status remains governed by `CLAIM_LEDGER_V1.md`. A deterministic PASS is `FORMAL/LOCALLY_TESTED` support only and cannot be converted into `novel`, `better`, `verified`, or `peer-review ready` language without the external gates.