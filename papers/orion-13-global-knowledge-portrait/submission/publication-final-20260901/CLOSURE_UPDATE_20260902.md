# Closure update 2026-09-02

**Scope.** Disclosure and synchronization additions only. No threshold,
comparator, corpus, gate, number or result was changed. The scientific
claim is unchanged and remains the bounded fixed-panel observation stated
in the abstract and discussion.

## What changed (mapped to the closure request's four items)

1. **Four mandatory disclosures** added to
   `manuscript/brief-report-final/common.tex` as a new Discussion
   subsection "Disclosures and limits of the comparison", plus a
   provenance sentence in Data and software availability naming the
   battery record:
   - minimal-rule equivalence: a predicate/modality/polarity three-field
     rule reproduces the full mechanism on these panels; the remaining
     coordinates are untested on this panel, not demonstrated-necessary;
   - degenerate comparator: the registered flat rule merges every case
     (predicate-equal fraction 1.0), so its false-merge rate is the
     non-merge base rate;
   - exact tests: McNemar p-values reported beside the bootstrap
     diagnostics, with the pooled test explicitly not computed;
   - same-programme/single-author limitation stated in one plain
     sentence.
2. **Claim ledger synchronized down** to the shipped Brief Report claim:
   `papers/orion-13-global-knowledge-portrait/CLAIM_LEDGER_V1.md` marks
   the previous full-paper headline SUPERSEDED (2026-09-02, historical row
   retained) and records the shipped bounded fixed-panel headline as
   governing.
3. **Bibliography anchors** added to
   `manuscript/brief-report-final/bibliography.bib`, both verified against
   publisher and proceedings records before inclusion: Li et al., "A
   Survey on Truth Discovery" (ACM SIGKDD Explorations Newsletter
   17(2):1-16, 2016, DOI 10.1145/2897350.2897352) and Abd Nikooie Pour et
   al., "Results of the Ontology Alignment Evaluation Initiative 2023"
   (OM 2023, CEUR-WS Vol-3591, pp. 97-139, 35 authors). One supporting
   clause each in the Introduction; no new claims.
4. **DOI blocker prepared, not executed**:
   `zenodo-deposition-metadata.json` in this directory holds the fields
   the operator needs (title, creators, publication/article upload type,
   CC-BY-4.0 licence matching the package's declared manuscript licence,
   related identifier to the pinned ORION repository snapshot).
   Minting remains HUMAN_FILING_ONLY; no DOI is asserted or fabricated
   anywhere in the package.

## Number provenance

Every disclosure number is transcribed from
`papers/orion-13-global-knowledge-portrait/evidence/null-and-baseline-battery-v1/BATTERY_V1.json`
(schema ORION.P3.NullAndBaselineBattery.v1, reproduction_check status
REPRODUCED): accuracy 1.0 / false_merge_rate 0.0 / false_split_rate 0.0
for the minimal predicate/modality/polarity rule on both 32-case panels;
`minimal_rule_matches_full_mechanism: true` on both; ten of the eleven
cascade-census coordinate categories listed in
`coordinates_that_never_differ` (only polarity differs);
`flat_is_constant_always_merge: true`, `predicate_equal_fraction: 1.0`,
non-merge base rate 0.1875 (confirmatory) and 0.125 (initial);
`exact_mcnemar_two_sided_p` 0.03125 (confirmatory, six flat-only
discordant pairs) and 0.125 (initial, four), `discordant_pairs_total` 10
with all ten favouring the coordinate-governed rule, and
`pooled_significance_test` recorded as NOT_COMPUTED_BY_PROTOCOL. The
same-programme/single-author limitation matches the Methods statement
already present in the manuscript.

## Rebuild

Rebuilt on the dedicated Linux build host (laptop-old) on 2026-09-02 in a
scratch copy `~/orion13-build-20260902/`:

    rsync -a papers/orion-13-global-knowledge-portrait/ <buildhost>:orion13-build-20260902/
    PATH=$HOME/.local/bin:$PATH python3 scripts/build_submission_package.py

Toolchain: tectonic 0.15.0 and pandoc 3.11 installed user-locally
(`~/.local/bin`) on the build host on 2026-09-02; no system-level
changes. The script compiles each route twice, once from the sources and
once from the unpacked source.zip, and verified both PDFs reproduce
byte-exactly (`source_archive_rebuild_exact: true`); it also regenerated
the DOCX, both route metadata files, the package manifest and the
checksums.

New filing objects:

- `journal/manuscript.pdf` sha256
  `7e7a75ca12d29e1faef8680366896ccf1750ae07bd3061314f1b8ced684890bc`,
  8 pages (previously 7; the disclosures subsection added one page).
- `arxiv/manuscript.pdf` sha256
  `c69c8426eed51e3379bf49788184a0a0d644de1af5d9830e67f156b0504cd858`,
  8 pages.
- `journal/manuscript.docx` regenerated from the same sources, sha256
  `e126d374effc4efa733cd0ee13d84252c4d7f68fcb5c9ab734cf6bd0d8b1a61b`.

`manuscript/brief-report-final/main.pdf` and `arxiv.pdf` were refreshed
to the same bytes as the package PDFs (the previous convention: the two
locations were identical).

## Post-build package edits

`zenodo-deposition-metadata.json` and this receipt were added after the
script build; `PACKAGE_MANIFEST.json` (payload entries for both files,
and its date field updated to 2026-09-02) and `SHA256SUMS` were then
regenerated so every package file is bound. Re-running
`scripts/build_submission_package.py` recreates the package from the
manuscript sources alone and will not include these two files; re-add
them after any such rebuild.

## Remaining human step (unchanged)

The journal route still requires the public archive DOI before filing:
the operator performs the Zenodo deposit using
`zenodo-deposition-metadata.json`, inserts the minted DOI into the Data
and software availability section, and rebuilds (HUMAN_INPUTS_REQUIRED.md
item 1).


## Rebuild addendum 2026-09-03

The 2026-09-02 rebuild described above never reached the repository: only
this receipt and `zenodo-deposition-metadata.json` were committed, while the
rebuilt PDF/DOCX/ZIP bytes stayed on the build host, so the package in git
still bound the pre-disclosure 2026-09-01 build. In addition, the manuscript
sources were revised after that rebuild (disclosures woven into Results and
Discussion instead of a separate subsection, and the truth-discovery/OAEI
lineage citations added), superseding the built revision.

The package has therefore been rebuilt again on the same build host from the
current committed sources (`common.tex` sha256
`da5cbcfb3c50957ab253df81b2d0e7e7da5748f520571ccb312801906dc3e769`,
`bibliography.bib` sha256
`e57d185140ae52197f3bc524aea436a3ba8efa967c2070aa8bbe343cb6874460`)
with the same toolchain and procedure. The digests in the "Rebuild" section
above are superseded by:

- `journal/manuscript.pdf` sha256 `75ffae29176e634b8477ffafed93e00f62dd8433d88a6a78f8197b844606036c`, 7 pages;
- `arxiv/manuscript.pdf` sha256 `e6ab1226eba191afbb24a8c15962290413e5934c5ed6003385a217ef5f4c89cd`, 7 pages;
- `journal/manuscript.docx` sha256 `d89d367802d232ad9139dc8df3fa2561997a54ca61d7d2efbf569486eacada09`.

Both route archives again reproduce their PDFs byte-exactly
(`source_archive_rebuild_exact: true`). The four mandatory disclosures and
the paired-test reporting are present in the rendered text of both PDFs.
`PACKAGE_MANIFEST.json` and `SHA256SUMS` bind every file of this package,
including this receipt and the Zenodo metadata.
