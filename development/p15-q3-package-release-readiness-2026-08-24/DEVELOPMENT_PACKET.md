# P15+Q3 package release-readiness increment

## Atomic question

Can the existing shared `orion-research-harness` package declare an explicit
OSI-approved license expression with machine-readable package metadata and a
reproducible, version-bound release procedure, and expose P15+Q3 through one
content-bound API/CLI without changing or promoting any scientific result?

## Recovered state and negative history

- The shared package, CLI, install instructions, Q3 publication contract, P15
  threat model and P15 failure ledger already exist on `main`.
- Issue #1086 still correctly leaves the public workload/runtime campaign and
  feature-complete release box open.
- P15 records a full-key-compromise negative and a blocked acquisition. Neither
  may be removed or converted into a positive result.

## Bounded saturation and challenge

For this metadata atom, the relevant surfaces are package metadata, license
text, notice, changelog, clean install/build, tag identity and explicit authority
boundaries. Search could be falsely flat if an embedded dependency or benchmark
payload were silently redistributed; therefore the notice explicitly excludes
upstream corpora/repositories and package metadata declares the exact canonical
`orion-research-os==0.1.0` dependency rather than pretending the harness is
standalone.

## Frozen implementation hypothesis

Adding an Apache-2.0 metadata declaration and text, declaring the exact canonical
`orion-research-os==0.1.0` runtime dependency, a 0.1.0 changelog, and an exact
clean-release procedure makes the existing package release-ready at the
software-identity layer. The shared API replays the frozen P15 SEI disposition
and binds it to two typed Q3 decisions plus optional deferred scores while always
denying self-granted scientific/independent authority. The execution binding
includes the full canonical execution-record digest, and caller booleans emit
only `DECLARED_*` science labels. It does **not** satisfy the
>=30 workloads / >=20 upstream failures / three runtime images gate, an external
replay, or scientific superiority.

## Verification and reopen triggers

- build sdist/wheel from a clean package checkout;
- install both wheels into an isolated target using an existing dependency-seeded
  Python runtime (the sandbox cannot reach a package index, so a true clean-host
  dependency installation remains `CANNOT_CHECK`);
- run focused shared-instrument, Q3 contract/frontier and P15 study tests;
- inspect wheel/sdist license inclusion and version identity;
- reopen if metadata and artifact contents disagree, any package test fails, or
  a dependency/benchmark redistribution requires a separate license audit.

The first package build failed because PEP 639 forbids combining a license
expression with the deprecated license classifier. That attempt is retained in
the work log; the classifier was removed and the rebuild succeeded. The complete
harness suite on this base reported `427 passed, 1 skipped, 16 failed`. Those
failures are outside this bounded change: campaign shadow/revision/result
contracts, strictness/error typing, conflicting timeout expectations, live
ORION-RG campaign fixtures and the programme-wide operational terminal. They are
retained as adverse suite evidence and are not treated as success for this
increment. The focused P15+Q3/package tests pass.

A wheel-only `--no-deps` target import also failed on the canonical runtime's
undeclared transitive `defusedxml` import. Importing the same two newly built
wheels in the dependency-seeded verification environment passed. This does not
convert a true clean-host dependency installation into evidence; that remains
`CANNOT_CHECK` while the sandbox cannot resolve the dependency graph from an
index.

Scientific-authority delta: **NONE**. Independent replication, protected custody,
adoption and site independence remain `CANNOT_CHECK`. The Apache expression is a
mechanically valid package declaration; rights-holder authorization to relicense
the pre-existing package is not established here and remains `CANNOT_CHECK`.
