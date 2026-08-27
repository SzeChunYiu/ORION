# ORION-01 R11 implementation amendment 01

Date: 2026-08-27

The first post-freeze invocation terminated before source audit completion and
before any circuit word was constructed or any scientific outcome was
accessed. `protocol_freeze_binding()` ran Git from the experiment directory
while passing repository-relative paths, causing the recorded
`ORION01_R11_EXECUTION_FAILURE_01.json` failure.

Amendment 01 changes only the Git-command working directory to the repository
root and records the final runner change commit separately. It does not change
the pinned PyZX commit, registry, input domain, objective, exact-search rule,
hostile controls, allowed terminals, or authority boundary.

The failure receipt is permanent custody. A second execution is permitted only
after this amendment is committed and pushed without rewriting freeze commit
`449b254a8b0265747e8dc70dd771d432dd296b83`.
