# Canonical protocol checker

The canonical pre-execution checker for this successor identity is:

- `registry_protocol_checker_v1.py`
- `test_registry_protocol_checker_v1.py`

It validates only the prospectively frozen protocol and deliberately emits `PROTOCOL_FREEZE_VALIDATED__NO_SOURCE_OUTCOME`. It does not resolve the upstream commit or test the pinned source instance.

The earlier unversioned `registry_protocol_checker.py` is a noncanonical draft retained in branch history and must not be used as a release or scientific receipt. Workflows and manifests for this identity must invoke the versioned checker explicitly.
