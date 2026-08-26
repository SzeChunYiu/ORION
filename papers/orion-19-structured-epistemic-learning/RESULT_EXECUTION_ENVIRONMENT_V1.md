# ORION-19 result-execution environment V1

Date bound: 2026-08-19

Purpose: record the environment in which the official result-bearing M1, D1 and corrected A2/A4 workflows executed. This is distinct from the later TMLR manuscript/PDF build environment.

## Common execution contract

- GitHub Actions hosted runner: `ubuntu-24.04`;
- runner image observed on official result executions: Ubuntu 24.04.4 LTS, image release `20260810.271.1` where logged;
- Python: CPython `3.12.13` on the official D1 execution and matching Python 3.12 setup on M1/A2-A4;
- install command: `python -m pip install -e '.[dev,candidates]'`;
- candidate dependency closure is declared in repository `pyproject.toml` / lock rather than patched into result scripts;
- result scripts are deterministic under the frozen seeds and emit content digests over the result objects.

Observed candidate/scientific dependency versions on the official Ubuntu/Python-3.12 result lane included:

- `numpy 2.5.2`;
- `scikit-learn 1.9.0`;
- `scipy 1.18.0`;
- `joblib 1.5.3`;
- `threadpoolctl 3.6.0`.

The surrounding development/test environment also installed:

- `pytest 9.1.1`;
- `pytest-split 0.11.0`;
- `pytest-xdist 3.8.0`;
- `execnet 2.1.2`;
- `cryptography 50.0.0`;
- `cffi 2.1.1`;
- `defusedxml 0.7.1`.

These auxiliary packages are not described as scientific model components.

## M1

Scientific protocol: `ORION-19.M1Protocol.v1.3`.

Official result run: `32263768718`, job `96103106194`.

Pre-outcome execution/test history is preserved:

- v1.3 runtime amendment converted `DictVectorizer` output to dense arrays after scikit-learn 1.9 rejected int64 CSR index metadata before protected execution; feature/model/test semantics were unchanged;
- v1.5 changed only the small smoke-test fixture from 6 to 8 train pairs/family because the frozen kNN grid contains `k=15`; official 64/24/48 train/dev/test corpus sizes were unchanged.

Result digest: `sha256:01e1b62da27b424d453c63b798a5cbb13a915a4546b8ced68fcf84c32d04d97e`.

## D1

Scientific protocol: `ORION-19.D1MethodTransferProtocol.v1.2`.

Original official result run: `32235110762`.

Original official result subject identity: PR merge ref `e69606d5ee7e5e035ab6374202f9e62c154579ae`.

Result digest: `sha256:34003fb8ffcecec6ed01654e40c644ff05b7640be56b398a45efc1e52a30141a`.

Dataset digest: `sha256:2775298457b7bdee815b207733507cd27d55719df314ef6352bb601bd709c19c`.

A later archive-only replay initially produced a different result digest solely because `run_d1.py` defaults `subject_sha` to `GITHUB_SHA`; rerunning unchanged scientific code with the original official subject identity reproduced the exact original result and dataset digests. This provenance-only episode is retained in the D1 execution/verification receipts.

## A2/A4

Corrected official focused replay: run `32253419104`, job `96069463554`.

Result digest: `sha256:f775c6046520d10c346657fd13f24b51cd776b7436a2a99afc93e4c1ce9bb7f3`.

The corrected runner explicitly measured candidate-order, evaluator-gold, weak-relation and hidden-history hostile controls rather than accepting the earlier attestation-only archive.

## Reproduction rule

The publication package should reproduce from the merged scientific source/results and the repository lock/current declared candidate dependencies. If a later environment changes numerical behavior, that is a new reproduction discrepancy to investigate; the historical result environment is not silently rewritten to match a new dependency release.
