# Canonical manuscript decision — ORION-06

**Decision.** The canonical named manuscript remains the LaTeX tree `papers/orion-06-recursive-recovery/manuscript/`.

**Claim authority.** `CLAIM_LEDGER_V4.md` is publication-canonical and corrects the stale ORION-number/source metadata in V3 without deleting V3 evidence history.

**TMLR review object.** `submission_tmlr/` is the upload-facing double-blind package. Its `main.tex` is a thin venue wrapper over the canonical sections and bibliography, with self-identifying paths removed from review prose. The TMLR style files are copied byte-for-byte from the already validated in-repository TMLR package used by ORION-07.

**Superseded for submission purposes.** Historical Markdown drafts and the generic `submission/manuscript.pdf` remain evidence/history, not the current TMLR upload object.

**Binding status.** Existing historical content bindings remain unchanged. The final TMLR PDF/source/supplement receive their own SHA-256 manifest.