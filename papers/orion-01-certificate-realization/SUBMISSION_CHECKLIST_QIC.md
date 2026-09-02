# ORION-01 QIC-class submission checklist (2026-09-02)

> **Route (2026-09-02, issue #78 decision (b)):** arXiv `quant-ph` preprint first, then a
> quantum-information-and-computation class journal submission. Supersedes for routing only
> the 2026-09-01 *Quantum* resolution (`submission/tier-b-closure-20260901/VENUE_RESOLUTION.md`),
> which remains on disk as history. Venue-specific requirements (article types, length,
> declarations, AI-policy wording) must be read from the chosen journal's live instructions
> on the filing day — never from this checklist or from memory.

## Source and package

- [ ] **Re-render the PDF from the canonical V4 source** (`MANUSCRIPT_V4.md`).
      The `submission/tier-b-final-20260901/` PDFs predate the 2026-09-02 abstract
      narrowing (finding B-F4 closure) and the added single-author limitation sentence, and
      are therefore stale against the source. Render is the parent lane's build step (no
      builds from this lane).
- [ ] Verify the rendered abstract carries the one-rule scope sentence: "Because the
      calculus contains exactly one rule, the exactness of its budget holds by construction
      within that one-rule system rather than as a bound over alternative certificate
      rules."
- [ ] Confirm no V4 surface reintroduces the V2-era phrase "arbitrarily loose as a
      description of the compiler it certifies" (grep the rendered text; the phrase is
      allowed to remain only inside frozen historical provenance files).
- [ ] **Freeze-ledger sync check:** confirm `CLAIM_LEDGER_V4.md` statuses still match the
      manuscript text (spot-check O1-V4-C6, C9, C13, C15-C17) and that
      `PUBLICATION_FREEZE_ADDENDUM_V2.md` (2026-09-02) is the current addendum of record.
- [ ] **Single-author limitation sentence:** present in `MANUSCRIPT_V4.md` §13 as of
      2026-09-02 ("This work belongs to a single-author research programme using AI
      assistance, so the verification described here is author-side throughout and lacks the
      independent perspective of multi-author or externally replicated work."). Confirm it
      survives the render.

## Filing steps (HUMAN_FILING_ONLY)

- [ ] Post the arXiv `quant-ph` preprint (account, licence choice, plain-ASCII abstract
      within the live arXiv limit, single top-level `main` file in the source archive).
      Record the arXiv identifier as `[PLACEHOLDER]` until assigned.
- [ ] Submit to the chosen QIC-class journal **after** the preprint is live, per the
      journal's current author instructions (editor name, submission ID, declarations,
      funding, competing interests, AI-use disclosure wording — all portal facts).
- [ ] Cover letter: use `COVER_LETTER_QIC_V1.md`; fill every `[PLACEHOLDER]`; re-check that
      no claim in the letter exceeds `CLAIM_LEDGER_V4.md`.
- [ ] **Literature refresh on submission day:** repeat a bounded nearest-work search
      (TARE / Tag-and-Restore, Pauli-frame compilation, subset-Davenport variants,
      proof-system relativity) and record it; the 2026-08-28 novelty audit's external
      verification items (donor-PDF retrieval, bibliographic accuracy, subset-Davenport
      naming) remain open gates and must be discharged or explicitly bounded at filing.

## Companion paper (ORION-05)

ORION-05 ("A Sharp Support-Two Normal Form for Shared-Tag TARE Quantum Compilation") files
**separately** on the same route (arXiv `quant-ph` first), with its own authority surfaces:
`papers/orion-05-tare-expressivity/CLAIM_LEDGER_V4.md` (O5-P1..O5-P10) and its canonical
manuscript. The two papers share the certificate-realization lineage: ORION-01's matched
family \(F_M\) carries the support-two theorem and sharpness witness that ORION-05 states in
its own grammar-fixed form; each cites the other as sibling work rather than merging. The
coverage relationship is audited in
`papers/orion-05-tare-expressivity/MERGE_COVERAGE_AUDIT_20260902.md`; claims routed to the
ORION-09/10 object there must not migrate into either filing. ORION-05's single-author
limitation sentence is **not yet present** in its LaTeX limitations section and must be
added by the lane that owns `manuscript/sections/06-limitations.tex` before its filing.

*skills-applied: nature-publication-closure, nature-polishing*
