# Canonical manuscript decision — ORION-12

**Decision.** The canonical manuscript is the LaTeX tree
`papers/orion-12-open-world-scientific-discovery/manuscript/` (`main.tex` plus
eight section files, figures, generated suite facts, and `bibliography.bib`).

**Why it is unambiguous here.** Unlike its siblings this paper has no competing
Markdown drafts. The ambiguity was elsewhere: one section file contained the
same five paragraphs twice, an older copy carrying cross-references to a sibling
paper and a de-identified rewrite appended below it. Both were being typeset.
The duplicate copy has been removed and the rewrite retained.

**Sections in the submitted manuscript.** All nine `\input` targets are
retained, including `p2x_unresolved_route_successor.tex`. Its filename says
"successor", but its content is the exact-contract battery that the abstract and
conclusion both cite as the paper's positive result. Dropping it on a filename
match would have removed the paper's headline evidence. The genuinely
successor-shaped section, the structure-conditioned acquisition interface, is
retained in its de-identified form because it is a scoped extension of the
paper's own argument rather than a separate programme's result.

**Binding status.** `journal_package/SHA256SUMS` binds this manuscript. The edits
in this pass required reconciliation, which was performed once, last, with
`check_journal_package.py --write-hashes` after all content edits and after
`scripts/write_render_closure_state.py` regenerated the derived render state.
Content-binding state is back at its baseline `BOUND_PARTIAL / PASS`.

**Claim-ledger reconciliation.** `protocol/CLAIM_LEDGER_V1.json` pins the exact
sentences it binds. Four locator sentences moved under house-style rewording and
were re-verified and updated; each claim's strength, numeric bindings, and
support artifacts are unchanged. One claim, the record-set digest binding,
retains its two SHA-256 digests inline in Results as a stated exception, because
for that claim the digest binding is the claim and the ledger's declared support
artifacts require the digests to appear in the sentence they bind.
