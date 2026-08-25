# Five-paper data, code and resource availability contract R2

## Current repository state

The manuscripts, theorem verifiers, exact finite result objects, protocols and focused tests are versioned in ORION. No external DOI or immutable release is invented here.

## Proposed manuscript statements

### Code availability

> Source code for the exact finite checks, theorem-corollary verifiers, manuscript claim audits and focused regression tests is available in the ORION repository at the submission commit identified in the final version. The all-size theorems are proved analytically in the manuscript; finite programs corroborate stated local obligations and production bindings rather than replacing those proofs.

### Data availability

> This work uses generated finite combinatorial instances and machine-readable result records rather than observational or personal data. The exact instance generators, registered counterexamples, result JSON files and figure source data will be deposited with the versioned submission archive. No confidential, personal or access-restricted data are used.

### Non-quantum authority note

> The support-at-least-23 object is supplied as bounded computational evidence whose current metadata requires external replay and withholds theorem authority. Exact `D_4(C_5^3)` and `C_0(31)` are not presented as established data products.

## Archive inventory required before submission

1. immutable source archive and commit identifier;
2. environment lock or documented minimal dependencies;
3. one-command execution for each R2 verifier;
4. expected result hashes;
5. generated counterexample instances and source data for figures;
6. machine-readable claim ledger and evidence map;
7. license statement for code and generated artifacts;
8. README separating analytic proof authority from finite corroboration;
9. external replay instructions that do not rely on a protected developer worktree.

## FAIR audit

- **Findable:** pending DOI/release metadata.
- **Accessible:** public GitHub source exists; final immutable archive pending.
- **Interoperable:** JSON/Markdown/Python are portable; schemas need final version identifiers.
- **Reusable:** exact commands and licenses must accompany the submission archive.

No statement should say “all data are in the paper” while machine-readable result objects remain repository-only.
