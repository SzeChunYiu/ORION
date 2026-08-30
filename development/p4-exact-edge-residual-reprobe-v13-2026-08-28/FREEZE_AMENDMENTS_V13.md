# V13 post-freeze amendments (documented, in order)

`FREEZE_RECEIPT_V13.json` records two pre-run amendments to `compile_probe_91_v13.py` (Adoptium `/v3/assets/version/` response parsing: `binaries[]` array shape; vestigial `binary["checksum"]` read removed). This file documents the post-freeze amendments.

3. **`compile_probe_91_v13.py` final-cleanup `shutil` import restored** (sha before `14e9a7227d9b657023f11d500c804d2f193bf67c6445167b97676d0026d2fbba`, after `9551b0...`). The successful run had already written `COMPILE_PROJECTION_V13.json` when cleanup crashed on a `NameError: shutil`; only the temp-dir cleanup line was affected. No computation, comparison or output changed.

4. **Rekor estimator validation added post-freeze** (`rekor_estimator_validation_v13.py`, `REKOR_ESTIMATOR_VALIDATION_V13.json`). Trigger: the validate-the-checker discipline. The frozen probe's digest-shaped Rekor retrieval returned `[]` for edges 133/185, which would have been cited as positive absence evidence; a positive control (a provenance-bearing PyPI file) also returns `[]` under that shape, invalidating it. The validation script proves by direct logIndex lookup that the control's transparency entry exists in the log while digest retrieval cannot see it — structural blindness. The frozen probe's Rekor rows are quarantined from adjudication; the frozen query set is unchanged.

5. **Two bounded adjudication-support captures added post-freeze on the already-frozen provider surfaces** (`PYPI_JSON_ATTESTATIONS_V13.json`, `PYPI_PROJECT_PROVENANCE_CENSUS_V13.json`): the PyPI JSON API per-file `attestations` key for the two frozen files (absent), and a whole-project provenance census for both publishers (0/7, 0/14). These complete the mechanistic publisher-state proof for edges 133/185. Same endpoints (`pypi.org`), same projects, no new providers, no outcome-bearing surface.

None of these amendments alters a frozen query, target identity, digest, command or comparison; all are additive captures or estimator validation on the same public metadata surfaces.
