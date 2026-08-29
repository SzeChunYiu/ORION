# ORION-11 Execution Manifest V1

**Provenance.** This manifest binds the frozen protocol `ORION-11.hidden-formulation.v1.1`
(DESIGN_FROZEN, `outcome_accessed: false`) to concrete execution bindings.
Every hash was computed from the repository state at the time of manifest creation.

| Field | Value |
|-------|-------|
| Manifest id | `ORION-11.execution-manifest.v1` |
| Status | `FROZEN_MANIFEST` |
| Repository fingerprint | `aae1f6826096469a5108469dc00ed424f105674b` (HEAD at manifest creation) |
| Created | 2026-08-16 |
| Outcome access | `false` — must remain `false` until this manifest is frozen and archived |

---

## 1. Study parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| Subject model | `glm-5.2` | `PROTOCOL_V1.json` → `execution_bindings.subject_model` |
| Model provider | Anthropic-compatible gateway | `ANTHROPIC_BASE_URL` env var; `provider.py` |
| Credential | `ANTHROPIC_API_KEY` env var | `provider.py` → `CREDENTIAL_ENV_VAR` |
| Stochastic repeats | 5 | `PROTOCOL_V1.json` → `statistics.stochastic_repeats` |
| Seeds | 0, 1, 2, 3, 4 | `harness.py` → `default_seeds()` |
| Confidence | 0.95 | `statistics.py` → `PROTOCOL_CONFIDENCE` |
| Bootstrap resamples | 10000 | `statistics.py` → `PROTOCOL_RESAMPLES` |
| H1 superiority margin | +0.05 | `statistics.py` → `H1_SUPERIORITY_MARGIN` |
| H2 non-inferiority margin | +0.02 | `statistics.py` → `H2_NON_INFERIORITY_MARGIN` |

---

## 2. Suite hashes

| Suite | Hash | Cases | Role |
|-------|------|-------|------|
| PILOT | `7a50a2d5025beb7dea4835911fa7dbf4a191431447397c73939c276b71dc49b5` | 18 | Debugging, variance estimation, pilot-only analysis |
| TEST | `21b461d89280631b93b766d6fb000c7f9f5fbeccee7cb6664f238c2c5c8e6420` | 48 | Final hypothesis testing |

**Hash computation method.** `suite_fingerprint()` in `src/orion/study/p1/cases.py`
SHA-256 hashes every case's `case_id`, `task_family`, `public_prompt`,
`observable_resources`, and `protected_gold` fields, sorted by case_id. The
hash covers gold as well as public fields — a result bound to a suite fingerprint
is verifiably bound to the exact gold labels used.

---

## 3. Case family / split distribution

| Family | PILOT | TEST | Total |
|--------|-------|------|-------|
| hidden_parent_domain | 3 | 8 | 11 |
| hidden_representation_or_coordinate_system | 3 | 8 | 11 |
| hidden_decomposition_or_interface | 3 | 8 | 11 |
| hidden_measurement_or_operationalization | 3 | 8 | 11 |
| evidence_only_negative_control | 3 | 8 | 11 |
| execution_only_negative_control | 3 | 8 | 11 |
| **Total** | **18** | **48** | **66** |

---

## 4. System suite

### 4.1 Subject (1)

| System ID | Source | Role |
|-----------|--------|------|
| `orion_full` | `orion_system.py` | SUBJECT |

### 4.2 Baselines (5)

| System ID | Implementation | Role |
|-----------|---------------|------|
| `static_react_tool_workflow` | `baselines.py` → `StaticReActBaseline` | BASELINE |
| `tree_search_iterative_research` | `baselines.py` → `TreeSearchBaseline` | BASELINE |
| `arex_like_recursive_audit_followup` | `baselines.py` → `AREXLikeBaseline` | BASELINE |
| `scion_like_dependency_execution_plan` | `baselines.py` → `SCIONLikeBaseline` | BASELINE |
| `iris_like_information_state_revision` | `baselines.py` → `IrisLikeBaseline` | BASELINE |

### 4.3 Ablations (5)

| System ID | Implementation | Ablation target |
|-----------|---------------|-----------------|
| `orion_no_explicit_W` | `orion_system.py` | Without explicit W state |
| `orion_no_explicit_M` | `orion_system.py` | Without explicit M state |
| `orion_generic_retry` | `orion_system.py` | Generic retry instead of typed reframe |
| `orion_full_reset` | `orion_system.py` | Full reset instead of dependency reopen |
| `orion_no_self_audit` | `orion_system.py` | Without mechanic-cell self-audit |

### 4.4 Live provider arm (optional)

| System ID | Source | Notes |
|-----------|--------|-------|
| `orion_live_provider` | `provider.py` → `ProviderBackedSystem` | Requires `ANTHROPIC_API_KEY`; runs only with `--live` flag |

---

## 5. Baseline config hashes

The baseline config is the code in `baselines.py` at the repository HEAD:

```
e4ab2add3ecb6c1dc98600935269067b86126a05a640fb3f271e714f1f3f7bc3
```

*Computed as SHA-256 of `src/orion/study/p1/baselines.py`.*

---

## 6. Evaluator / adjudication identities

### 6.1 Scoring pipeline

| Component | Path | Hash |
|-----------|------|------|
| Metrics | `src/orion/study/p1/metrics.py` | `ea12b98e066b111f9440db472f17802ace4b08ef40839d7c2b292f0539e44080` |
| Statistics | `src/orion/study/p1/statistics.py` | `ea12b98e066b111f9440db472f17802ace4b08ef40839d7c2b292f0539e44080` (combined with metrics) |
| Tables | `src/orion/study/p1/tables.py` | `7d0ecfc71bf2962cf2d9b1ad4fe9c918dbc1895f445b848806b1b06e6f11675d` |
| Arm validity | `src/orion/study/p1/arm_validity.py` | `b903bbba9390d5fea2036d51ac0bcd3e4a4a67e37cad86ab5bd2cbde78c80299` |

### 6.2 Adjudication

| Component | Path | Hash |
|-----------|------|------|
| Adjudication | `src/orion/study/p1/adjudication.py` | `71dc50464d3d9550d0eecef739f306bf26f99506da866bfed0504397bb96bef8` |
| Rubric | `protocol/ADJUDICATION_RUBRIC_V1.md` | (covered by SHA-256 in `adjudication.py`; rubric body hash: `dce9f3612f50cc39a22d7761de80a40683f38ebbdf548a7df7b009e7bad941be`) |

### 6.3 Conductor (harness + run entrypoint)

| Component | Path | Hash |
|-----------|------|------|
| Conductor | `src/orion/study/p1/harness.py` + `run_trial.py` + `systems.py` | `dbb9f0b948f2fd66bf80a794595fc7403716d4e280fa12251aaf3a412dc459be` |

---

## 7. Subject model bindings

| Field | Value | Status |
|-------|-------|--------|
| Subject model | `glm-5.2` | `BOUND` (in `PROTOCOL_V1.json`) |
| Model provider | `ANTHROPIC_BASE_URL` env var | `UNBOUND` — set at run time |
| Subject revision | `aae1f6826096469a5108469dc00ed424f105674b` | `BOUND` (HEAD at manifest creation) |
| Baseline config hashes | `e4ab2add3...` | `BOUND` |
| Suite PILOT hash | `7a50a2d5...` | `BOUND` |
| Suite TEST hash | `21b461d8...` | `BOUND` |
| Split hashes | (per-case individual hashes) | `BOUND` — see `src/orion/study/p1/cases.py` → `case_from_dict` |
| Evaluator hash | `ea12b98e...` | `BOUND` |
| Evaluation epoch | (timestamp of run) | `UNBOUND` — set at run time |

---

## 8. Seeds

| Parameter | Value |
|-----------|-------|
| Seed set | `{0, 1, 2, 3, 4}` |
| Generator | `random.Random(seed)` in `statistics.py` (CPython Mersenne Twister) |
| Determinism | Same seed + same inputs → same interval |

---

## 9. Resource ceilings

Per `baselines.py` → `budget_for()`, keyed on `budget_class`:

| Budget class | Tool calls | Search queries | Model tokens |
|-------------|-----------|----------------|-------------|
| `p1_standard_v1` | 1000 | 500 | 2000000 |

All 66 cases use `budget_class: p1_standard_v1`.

---

## 10. Access policy

| Policy | Enforcement |
|--------|-------------|
| Gold labels never reach SUT | Type signature: `SystemUnderTest.run(view: PublicView, ...)`. `PublicView` has no `protected_gold` attribute. |
| Evaluator custody | Gold/adjudication artifact is host-owned and versioned before final candidate runs. |
| Search contamination | Public benchmark use is declared; web-search access to benchmark solutions is audited. |
| Access logging | Tool/search requests and accesses to benchmark/evaluator paths are retained. |
| Adjudication | Model panel: at least 2 structurally independent judges; distinct judge/lineage/context ids; Cohen/Fleiss kappa reported; floor 0.6. |
| Human adjudication | Not required (`amendment A1`). |

---

## 11. Execution checklist

### Pre-flight checks (before any system runs)

- [ ] **PROTOCOL_V1.json has `outcome_accessed: false`.** Verify by reading the file. If `true`, this manifest is void and the study is contaminated.
- [ ] **Suite hashes match.** Compute `suite_fingerprint()` for PILOT and TEST. They must equal `7a50a2d5...` and `21b461d8...`.
- [ ] **Repository is clean.** `git status --porcelain` returns empty (except for specified untracked files).
- [ ] **HEAD matches the manifest.** `git rev-parse HEAD` equals `aae1f682...`.
- [ ] **All 11 system IDs are registered.** Baseline + ablation + ORION subject = 11.
- [ ] **Live arm credential is present.** `ANTHROPIC_API_KEY` is set (if `--live` is used).
- [ ] **Live arm endpoint is correct.** `ANTHROPIC_BASE_URL` points to the intended Anthropic-compatible gateway.
- [ ] **Model is `glm-5.2`.** Verify `PROTOCOL_V1.json` → `execution_bindings.subject_model`.
- [ ] **Resource ceilings are enforced.** `budget_for()` returns the correct `p1_standard_v1` caps.
- [ ] **Output directory is empty.** `papers/orion-11-recursive-epistemic-reconstruction/results/raw/` contains no prior run records.

### Run execution

- [ ] **Run PILOT first.** `python -m orion.study.p1.run_trial --split pilot --live` (if live arm is needed).
- [ ] **Inspect PILOT output.** Verify no CANNOT_CHECK records from mechanical systems. Verify arm validity passes.
- [ ] **Set outcome_accessed flag.** After PILOT but before TEST, verify outcome_accessed is still `false`.
- [ ] **Run TEST.** `python -m orion.study.p1.run_trial --split test --live` (if live arm is needed).
- [ ] **Archive raw records.** Both `pilot_runs.jsonl` and `test_runs.jsonl` are non-empty and contain exactly the expected number of records.
- [ ] **Verify scoring completed.** Both `pilot_scored.jsonl` and `test_scored.jsonl` are non-empty.

### Post-run verification

- [ ] **Suite fingerprint on every record.** Every record in the archive carries the suite fingerprint. Verify alignment.
- [ ] **Subject revision on every record.** Every record carries the git revision. Verify alignment with manifest.
- [ ] **No CANNOT_CHECK records from mechanical systems.** All 10 mechanical systems (5 baseline + 5 ablation) must produce OK records on all 66 cases x 5 seeds. CANNOT_CHECK on the live arm is expected if no credential.
- [ ] **Seeds are complete.** Every (case, system) pair has exactly 5 records, one per seed.
- [ ] **No excluded records.** The `excluded` field is `false` on every record.
- [ ] **Arm validity check.** `assess_arm_discrimination` returns `permits_system_comparison: true`.
- [ ] **Tables generated.** `papers/orion-11-recursive-epistemic-reconstruction/results/tables/` contains all expected tables.

---

## 12. Machine-checkable freeze verification

The following can be verified programmatically before any system runs:

```python
# Suite integrity
from orion.study.p1.cases import load_cases, Split, suite_fingerprint
pilot = load_cases(CASES_ROOT, split=Split.PILOT)
test = load_cases(CASES_ROOT, split=Split.TEST)
assert suite_fingerprint(pilot) == "7a50a2d5..."
assert suite_fingerprint(test) == "21b461d8..."

# Outcome not accessed
import json
proto = json.loads(PROTOCOL_PATH.read_text())
assert proto["outcome_accessed"] == False

# Protocol status frozen
assert proto["protocol_status"] == "DESIGN_FROZEN"

# All systems present
from orion.study.p1.baselines import baseline_systems
from orion.study.p1.orion_system import orion_systems
assert len(baseline_systems()) == 5
assert len(orion_systems()) == 5

# Resource ceilings correct
from orion.study.p1.baselines import budget_for
from orion.study.p1.cases import PublicView
budget = budget_for(PublicView("x", "x", (), "p1_standard_v1"))
assert budget.tool_calls == 1000, f"got {budget.tool_calls}"
assert budget.search_queries == 500, f"got {budget.search_queries}"
```

---

## 13. Confidentiality contract

**`EXECUTION_FROZEN` must not be set before outcome access.** The protocol's
`outcome_accessed` flag transitions from `false` to `true` at the moment any
protected label is read for scoring. The following sequence is enforced:

1. **Manifest is frozen** (this document) — no outcome has been accessed.
2. **Suite is run** — systems produce traces, which are archived raw.
3. **Scoring runs** — `score_archive()` reads `ProtectedGold` from the cases.
   At this point `outcome_accessed` becomes logically `true`, even if the
   flag file is updated after.
4. **`EXECUTION_FROZEN` is set** — only after the scored archive exists and
   the manifest is complete.

This order is machine-checkable: the `outcome_accessed` flag in `PROTOCOL_V1.json`
must be `false` before step 2, and the manifest's `status` must be `FROZEN_MANIFEST`
before step 3. A manifest created after outcome access is void.

---

## 14. Amendment log

| Amendment | Date | Change |
|-----------|------|--------|
| — | — | Initial manifest creation |

---

*This manifest is created before any outcome is accessed. The `outcome_accessed`
flag in `PROTOCOL_V1.json` is `false` at the time of writing, and the suite
hashes were verified against the frozen case files.*