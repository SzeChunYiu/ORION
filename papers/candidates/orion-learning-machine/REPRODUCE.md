# Reproduce the P9/P10 learning-machine lane

**Papers:** `../paper-09-executable-research-core/`, `../paper-10-content-bound-math-evaluation/`
**Status:** deterministic local reproduction; no external superiority or novelty authority

## 1. Reproduction subject

Everything in this directory. `SCRIPT_MANIFEST_SHA256.txt` binds the 36 delivered source files and verifies 36/36 as committed. Committed outputs live in `results/` and are not covered by that manifest, because it was generated before they existed.

## 2. Environment

```text
CPython 3.13
numpy 2.4.4
sympy 1.14.0
scikit-learn 1.8.0
```

Phase 0 and phase 1 require numpy, sympy and scikit-learn. **Phase 2A also requires numpy and scikit-learn**, though nothing in its own logic uses it: `run_phase2a.py` imports `orion_learning_machine.runtime`, the package `__init__` re-exports `.competence`, and `competence.py` imports both at module level (`import numpy as np` and `from sklearn.preprocessing import StandardScaler`). It is the only module in the framework importing either; an AST scan of every file under `framework/` finds no other third-party import besides pytest in the framework's own tests. An earlier draft of this file called phase 2A standard-library-only; that was wrong, and CI caught it by running phase 2A in an environment without numpy. The import is left as delivered rather than made lazy, because every framework file is byte-bound by `SCRIPT_MANIFEST_SHA256.txt`.

No network access, no model provider, no LLM API, no judge.

Suggested clean setup:

```bash
export PYTHONHASHSEED=0
python --version
```

## 3. Framework tests

```bash
cd framework && python -m pytest -q
```

Expected: `25 passed`. Recorded in `results/FRAMEWORK_TESTS.txt`.

## 4. Deterministic experiments

Every command below is byte-reproducible on re-run — verified, not asserted.

```bash
PYTHONPATH=framework python experiments/phase0_solver_ecology/run.py      # -> results/PHASE0_SOLVER_ECOLOGY.txt
PYTHONPATH=framework python experiments/phase1_mechanic_composition/run_v1.py  # -> results/PHASE1_MECHANIC_COMPOSITION.txt
PYTHONPATH=framework python experiments/phase2_real_source/run_phase2a.py      # -> results/PHASE2A_RESULTS.json
```

All three seed on `SEED=20260818`. Phase 0 and phase 2A were each run twice and compared byte-for-byte; both are identical. Phase 1 is the slow one (minutes, CPU-bound).

Phase 2A writes `experiments/phase2_real_source/RESULTS_PHASE2A.json` next to the script; the committed copy is `results/PHASE2A_RESULTS.json`. Compare rather than overwrite.

## 5. What cannot be run

```bash
PYTHONPATH=framework python experiments/phase2_real_source/run_phase2b_goal_effect.py
```

Fails with `FileNotFoundError: HF_MATHLIB_TACTICS_SAMPLE.json`. That input is **not in the bundle**, so the goal-effect question is `CANNOT_CHECK` and no result is claimed for it.

```bash
./VERIFY_LOCAL_CLOSURE.sh
```

Cannot run. It requires `closure_logs/FROZEN_SHA256SUMS.txt` and `CLOSURE_MANIFEST.json`, neither of which is in the bundle. It asserts an authority of `LOCAL_CORE_COMPLETE`; that assertion is **not verifiable from what was delivered**. `REPRODUCE_LOCAL_CLOSURE.sh` also calls `sha256sum`, which is absent on macOS — use `shasum -a 256`.

Both scripts are retained as delivered rather than repaired, so the gap stays visible.

## 6. What these runs establish

- A learned competence map routes solvers to the best fixed solver's success at ~1/3 its effort, and holds under distribution shift (P9, phase 0).
- Failure-aware composition matches the oracle by **abstaining on opaque tasks at zero effort**, where imitation spends effort. It does *not* solve more than imitation — both reach the ceiling (P9, phase 1).
- Macros mined from a 7-file Lean corpus are **not distinguishable from shuffled tactic order**, p = 0.83 at bigram order against a 1000-rep shuffle null (P10, phase 2A).

## 7. What they do not establish

- No comparison against any independent, externally-implemented baseline. Every arm is defined inside this harness.
- No real verifier has been bound; `bind_verifier_receipt` is exercised only with synthetic receipts.
- Phase 0 and phase 1 task distributions are synthetic and self-generated.
- The Lean corpus is 7 files from 2 repositories — adequate for the null reported, not for any general claim.
- No literature pass has been run for either paper, so novelty is `CANNOT_CHECK` for both.

## 8. Claim authority

Neither paper has a claim ledger or a readiness file. The maximum supported statement is the three bullets in §6, each bounded to its own synthetic or 7-file setting. Nothing here supports a superiority, generality or novelty claim.
