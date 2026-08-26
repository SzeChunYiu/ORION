# ORION V3 execution takeover failure ledger

## F-001 — dedicated V3 CI cannot collect its hostile suite

**Observed:** PR #1326 workflow run `32848793725`, job `97804605414`, exits 2 while collecting `tests/unit/discovery/test_frontier_dominance.py`.

**Failure:** `ModuleNotFoundError: No module named 'cryptography'`.

**Root cause:** `.github/workflows/orion-discovery-v3.yml` installs only `pytest`. Importing the nominally focused module loads the root `orion` package, whose experience authority module imports the declared project dependency `cryptography>=45`. The workflow's environment contract is therefore smaller than the import contract of the tested object.

**Reproduction distinction:** The same focused test passes locally in a private environment with the project dependencies installed: 14 passed. This isolates the failure to workflow provisioning rather than the V3 frontier implementation.

**Correct response:** Add a regression test for the workflow dependency contract, then install the project in the V3 workflow before running the hostile suite. Do not report the local pass as remote CI authority until a fresh workflow run succeeds.

**General lesson candidate:** A focused harness is not isolated merely because its test path is narrow. Its transitive import graph defines the minimum environment.

## F-002 — V3 execution queue has incompatible identities

**Observed:** The branch backlog has 11 `DISC-V3-*` jobs. Issue #1325 has an imperfectly aligned 11-job prose list. The newer issue #1329 has 13 renamed and reordered jobs, including precondition-liveness, cross-domain, paper-sync, and historical-triangulation identities that are absent or differently represented in the branch.

**Failure:** There is no single machine-readable execution order whose IDs, questions, dependencies, required outputs, and resource contracts match all current authorities.

**Failure class:** `EXECUTION_IDENTITY_BOUNDARY_MIXUP` risk.

**Correct response:** Reconcile sources into a manifest that retains predecessor IDs and fails closed on scientifically ambiguous aliases. Do not submit a scientific SLURM job from prose similarity.

**General lesson candidate:** Scheduler speed cannot repair protocol ambiguity; fast execution of the wrong frozen object is still failure.

## F-003 — full PR checks contain inherited multi-failure sets

**Observed:** The PR's repository-wide checks report at least 45 P2 failures with 621 passes and 2 skips, 16 engineering-conformance failures with 431 passes, plus heavy-shard and matched-dual-lane failures.

**Current status:** Root causes are not yet reduced to independent minimal reproductions. The logs contain claim-ledger drift, model/interface drift, incomplete frozen manifests, timeout-contract drift, and harness artifact mismatches. These must not be bundled into a speculative mass fix.

**Correct response:** Preserve the exact logs, group failures by earliest shared boundary, reproduce one group at a time, and add a regression test before each correction.

## F-004 — LUNARC private environment was resolved against global `PYTHONPATH`

**Observed:** Engineering reference job `3539804` (`V3-ENGINEERING-REFERENCE-01`) failed on `cx04` after 19 seconds with exit `1:0`. Frozen-protocol validation, the V3 structural checker, and the 13-job takeover-manifest checker completed before hostile-test collection failed with `ModuleNotFoundError: No module named 'pygments'`.

**Root cause:** LUNARC exported a global Jupyter/Python package path while the runner installed its private environment. Pip saw packages on that inherited `PYTHONPATH` and treated some dependencies as satisfied outside the private environment. A post-failure private-only probe contains `pytest==9.1.1` and `cryptography==50.0.0` but cannot import `pygments` or `defusedxml`. The runtime then intentionally set `PYTHONPATH=source/src`, making the resolver/runtime environment mismatch terminal.

**Correct response:** Preserve job `3539804` as failed. Create a separately named and content-addressed successor whose runner hash is bound into the protocol, clears `PYTHONPATH` for every private-environment installation and dependency probe, and self-checks its runner bytes before executing any repository check.

**Authority boundary:** No scientific job or outcome ran. This is engineering evidence only; external novelty remains `CANNOT_CHECK`, and paper authority changes by `NONE`.

**Successor terminal:** `V3-ENGINEERING-REFERENCE-02` passed only as a local dry run and was not submitted because its runner did not compare the source archive directly to the frozen protocol. The separately frozen `V3-ENGINEERING-REFERENCE-03` closed that boundary and completed on LUNARC as scheduler job `3539808` in 15 seconds with exit `0:0`. This resolves the engineering-environment retry only; all 13 scientific jobs remain independently specification-blocked.
