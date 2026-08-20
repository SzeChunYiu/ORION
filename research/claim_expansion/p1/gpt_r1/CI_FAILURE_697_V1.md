# P1-U GPT-R1 CI failure receipt — PR #697

Date observed: 2026-08-20
PR: #697
Workflow run: `32367574494`
Head under test: `fb153b7d5d6f7e6e1911c997dd66e93bd193b38f`
Overall CI conclusion: `FAILURE`

## P1-specific failure

The four ARD tests did not reach the frozen scientific assertions. Import of `run_ard_exact_pilot.py` failed on Python 3.12 while `@dataclass` processed postponed string annotations. The test loader used `importlib.util.module_from_spec()` followed by `exec_module()` without first inserting the module into `sys.modules`; Python 3.12 dataclasses consult `sys.modules[cls.__module__]` during annotation processing and received `None`.

This is an execution-harness/test-loader defect. It is not evidence for or against the frozen ARD numerical receipt because `build_report()` was never executed by those failed tests.

The repair on the R2 branch changes only the loader to register `sys.modules[spec.name] = module` before `exec_module()`, matching normal Python import semantics. The ARD protocol, implementation, expected result, margins, templates, baselines and scientific gates are unchanged.

## Other failures in the same full-repository job

The same run also reported repository-wide package/binding drift outside the P1 ARD tranche, including:

- P6/P7/P8 candidate-content binding and SHA256SUMS drift;
- P9/P10 learning-machine publication-manifest drift;
- P1-P4 journal-package digest mismatches.

These failures are not scored as ARD scientific failures. They remain repository synchronization work and are not hidden.

## Authority

This receipt grants no P1-U superiority, runtime registration, adoption or merge authority. The failed #697 run remains immutable history. A targeted exact-head ARD workflow on the fresh R2 branch must execute the frozen implementation and reproduce `ARD_EXPECTED_EXACT_RESULT_V1.json` before the finite mechanistic positive is called repository-reproduced.
