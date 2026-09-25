# ORION-13 canonical closure repair + mirror sync — prepared 2026-09-03 (NOT pushed)

## Root cause (P0-class canonical defect)
The #2124 closure rebuild (four mandatory F1000 disclosures woven into the
manuscript) ran 2026-09-02 on the build host (ssh `billy-old`,
`~/orion13-build-20260902/`) but was **never pushed**: only the receipt
(`CLOSURE_UPDATE_20260902.md`), `zenodo-deposition-metadata.json`, and their
manifest/sums entries reached `SzeChunYiu/ORION` main. Result: canonical main
binds **pre-disclosure 7-page binaries** while its own receipt describes
8-page digests (`7e7a75ca…`, `c69c8426…`, `e126d374…`) that exist nowhere in
the repo. Additionally 52e371d72 landed a LATER editorial tex revision
(disclosures in Results/Discussion; truth-discovery/OAEI citations:
yin2008truthfinder, dong2009dependence, li2016truthsurvey, euzenat2011oaei),
so current sources had never been built at all. The mirror's 2026-09-02
package is also pre-disclosure (all four PDF variants probe 7pp, 0 disclosure
markers).

## Repair executed (prepare-only)
Rebuilt on billy-old from the current committed sources (tex verified
byte-identical to main: common `1e283e63…`, bib `d8581ac6…`, main
`cb0cbeb2…`, arxiv `d35b1e23…` blob shas) using the receipt's exact
toolchain + `scripts/build_submission_package.py` (SOURCE_DATE_EPOCH pinned);
`source_archive_rebuild_exact: true` both routes. Disclosures confirmed in
rendered text (McNemar=1, minimal rule=1, always-merge=2, base rate=2, truth
discovery=2, OAEI=1, "pooled" NOT_COMPUTED retained); 7 pages both routes.
Post-build per receipt procedure: restored 2 closure files, amended receipt
with "## Rebuild addendum 2026-09-03", regenerated manifest (date 2026-09-03,
20 payload) + sums (21 lines).

## Payloads (local, verified, AWAITING parent push — nothing was pushed)
- **Canonical repair** `/tmp/o13/canonfix/` (22 files; diff vs main = 10
  files: CLOSURE_UPDATE, PACKAGE_MANIFEST, SHA256SUMS, arxiv/{manuscript.pdf,
  metadata.json, source.zip}, journal/{manuscript.docx, manuscript.pdf,
  metadata.json, source.zip}) →
  `papers/orion-13-global-knowledge-portrait/submission/publication-final-20260901/`.
  New digests: journal pdf `75ffae29176e634b8477ffafed93e00f62dd8433d88a6a78f8197b844606036c`,
  arxiv pdf `e6ab1226eba191afbb24a8c15962290413e5934c5ed6003385a217ef5f4c89cd`,
  docx `d89d367802d232ad9139dc8df3fa2561997a54ca61d7d2efbf569486eacada09`,
  arxiv zip `84045640290e14cbff244453fe9151722d10599d28695ceff716f83eae279f55`,
  journal zip `b66869232e908b569e16a566351eea801f069585db305bbf4b7135b14edc0538`,
  receipt (amended) `412a0c8ba2218b91e28cb75887bd2f53341cf1e2483ed376e06e8be429af0613`.
  Convention refresh: `/tmp/o13/canonfix_paper/manuscript/brief-report-final/{main.pdf→journal pdf, arxiv.pdf→arxiv pdf}` (previous convention: those two files matched the package PDFs byte-for-byte; main currently still binds the stale pre-disclosure pair).
- **Mirror sync** `/tmp/o13/merged/` (22 files; vs live mirror = 12 changed +
  2 added: +CLOSURE_UPDATE_20260902.md, +zenodo-deposition-metadata.json) →
  `v1-papers/orion-13-global-knowledge-portrait/SUBMIT_THIS/` on
  `SzeChunYiu/ORION-paper`. Mirror's newer scholarly register kept (skills rev
  `d5b61b5…`, pipeline 1.23.0, writing 1.20.0, reviewer 3.7.0, polishing
  7.5.0; "predeclared flat rule" wording — merged SCIENTIFIC_SCOPE.md +
  COVER_LETTER.md came out byte-identical to mirror). SKILLS_APPLIED ←
  mirror + sync note; REVIEWER_AUDIT ← repair + mirror's "Updated-skill
  re-closure" + sync note; README + sync note; mirror-format manifest
  (insertion order, no sort_keys; date 2026-09-03; payload 20) + sums (21,
  original order + 2 new alphabetically).

## Verification (all green, this session)
Round-trip: payload 20/20, sums 21/21, route digests == payload == files,
`canonical_science_source_sha256` `da5cbcfb…` == tex_common.tex,
authority `19376cf9…` == live SCOPED_PUBLICATION_TRACK_V1.md, binaries ==
canonfix, addendum present, register swaps present. Re-fetched main tree
fresh at finish: package 22 blobs byte-identical to build inputs (git
hash-object match) — nothing landed underneath us. Push mechanics reminder
(from memory): git data API base_tree = repo ROOT tree; PATCH
`git/refs/heads/main`; verify via recursive-tree count + untouched sibling.

Build host state: orphaned 8-page #2124 build preserved at
`billy-old:~/orion13-prevbuild-backup-20260903/`; workspace
`~/orion13-build-20260902/` holds the current-source build (docx/pdf/zips
match canonfix digests).
