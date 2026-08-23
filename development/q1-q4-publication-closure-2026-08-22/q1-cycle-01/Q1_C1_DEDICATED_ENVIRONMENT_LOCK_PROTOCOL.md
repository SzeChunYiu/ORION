# Q1-C1 dedicated environment-lock amendment

Status: frozen after CI run 32610336116 and before its successor

## Trigger and preserved failure

The first GitHub resource-closure attempt stopped before scientific execution.
Its root-level `uv sync --frozen --all-extras` correctly installed
`cryptography==50.0.0` but installed `numpy==2.5.2`. The frozen candidate and
author-stack adapter require `numpy==2.3.5`. This is a contract counterexample,
not a theorem result and not permission to relax the NumPy requirement.

No lane terminal or result commit was produced by the failed attempt.

## Replacement environment contract

The successor uses the dedicated hash-locked file
`harness/q1_c1_ci_requirements.lock`. It contains exactly the four binary or
transitive distributions required by Q1-C1 execution:

- NumPy 2.3.5;
- cryptography 50.0.0;
- cffi 2.1.1; and
- pycparser 3.0.

Every entry is a direct PyPI wheel URL plus its SHA-256 fragment. The target is
CPython 3.12.13 on Ubuntu 24.04 x86-64. The job creates a fresh virtual
environment and installs with `uv pip install --require-hashes`. It then checks
all four installed versions before starting either lane.

The repository and research-harness sources are executed from the committed
checkout; candidate scientific modules are executed from the fixed candidate
archive. Installing unrelated root extras is prohibited in this child cycle.

## Chronology and outcomes

This amendment and lock must be strict ancestors of the new workflow/runner
commit and every result commit. The earlier failed workflow remains failed. A
new run number and new evidence branch are required.

An install, version, hash, Python, architecture, audit, or strace mismatch
blocks or invalidates the new run before scientific authority. The original
two-repeat, immutable-terminal, post-commit comparison, mutation, and authority
rules remain unchanged.
