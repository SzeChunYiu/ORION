# LUNARC private-environment dependency leak

## Observed

SLURM job `3539804`, frozen as `V3-ENGINEERING-REFERENCE-01`, passed three pre-outcome engineering checks and then failed while collecting the focused hostile tests with `ModuleNotFoundError: No module named 'pygments'`.

## Failure

The runner created a private virtual environment while inheriting LUNARC's global `PYTHONPATH`. Pip resolved requirements against packages visible through that global path, but the test phase replaced `PYTHONPATH` with `source/src`. The installed environment therefore lacked packages that pip had incorrectly regarded as already satisfied.

## Failure class

`EXECUTION_ENVIRONMENT_IDENTITY_MISMATCH`

## Correct response

Keep `3539804` immutable and failed. Any successor must have a new job identity, freeze the runner SHA-256 into its protocol, clear `PYTHONPATH` during installation and environment self-checks, and refuse execution if the live runner bytes differ from the frozen identity.

## General lesson candidate

A virtual environment is not dependency-isolated when its installer inherits an external module search path. Resolver inputs and runtime inputs must be made identical and recorded before execution.

## Authority boundary

The failure occurred before any scientific experiment. It is engineering evidence only and changes no manuscript, novelty, or top-tier authority.
