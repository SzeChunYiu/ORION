# Third-party notices

This file records the redistribution terms of third-party code this
repository depends on. Every entry below was read from the installed
package's own metadata rather than from documentation or memory, so it
reflects what is actually resolved at the pinned version.

## Direct runtime dependencies

| Package | Version verified | License | OSI-approved |
|---|---|---|---|
| `cryptography` | 50.0.0 | `Apache-2.0 OR BSD-3-Clause` (SPDX expression; dual, licensee chooses) | Yes, both options |
| `defusedxml` | 0.7.1 | Python Software Foundation License (PSFL) | Yes |

Both are permissive and both are compatible with this repository's own
Apache-2.0 terms. Neither imposes copyleft obligations on downstream users
of ORION.

### How these were verified

Read from `importlib.metadata` on the resolved environment:

- `cryptography` publishes a `License-Expression` field of
  `Apache-2.0 OR BSD-3-Clause`. Its legacy `License` field is empty, which is
  expected for packages that have migrated to PEP 639 SPDX expressions.
  Reading only the legacy field would have reported no license at all.
- `defusedxml` publishes `License: PSFL` and the trove classifier
  `License :: OSI Approved :: Python Software Foundation License`.

## Scope and limits of this notice

This covers **direct runtime dependencies declared in `pyproject.toml`**. It
is not a full transitive audit, and it does not cover development-only or
test-only tooling, which is not redistributed.

Stating that plainly matters more than a longer table would: a notice that
silently omits its own scope invites the reader to assume a completeness it
does not have. If a transitive audit is required for a specific
redistribution, it should be run against the resolved lockfile at that
moment, because transitive sets change with resolution.

## Documents, figures and data

Manuscripts, figures, tables and derived data are **not** covered by the
Apache-2.0 terms above. They are licensed CC BY 4.0
(`LICENSE-PAPERS-CC-BY-4.0.txt`). This matches the requirement of the
journals these papers target: TMLR publishes under CC BY, so the repository
license does not have to be renegotiated at submission time.

Any third-party figure, dataset or excerpt reproduced inside a manuscript
retains its own upstream terms and must carry its attribution in place. This
repository does not relicense material it does not own.
