# P4 exact-edge V11 handoff

- V10 predecessor: `76/80`; residual indices `36, 91, 133, 185`.
- V11: `0/4` closures; cumulative bridge remains `76/80`.
- Index 36: Zenodo and DataCite version remain null; preserved archive HEAD is tag 0.0.12, not publication 0.0.3.
- Index 91: embedded HEAD/tree and GitHub revision authenticate exactly, but the archive has 106 untracked compiled `.class` files and two executable-bit drifts versus codeload; exact payload equality fails.
- Indices 133/185: exact PyPI PEP 691 file hashes match, but `provenance` is null.
- No P4 manuscript or claim-ledger change is authorized because no edge closed.
- V10/V10B chronology is preserved; no pytest or repository CI was run.
