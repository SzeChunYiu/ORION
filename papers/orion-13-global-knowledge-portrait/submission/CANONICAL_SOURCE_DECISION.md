# Canonical manuscript decision — ORION-13

**Decision.** The canonical manuscript is the LaTeX tree
`papers/orion-13-global-knowledge-portrait/manuscript/`.

**Why it is not in doubt.** This paper's manuscript is already the subject of a
dedicated repository CI job, `p3-manuscript-audit`, which compiles it, checks
its references, and audits its abstract, introduction, dataset, evaluation,
conclusion and limitations sections against a list of claims that must not
reappear. Nothing else in the paper directory is a candidate.

**Binding.** `journal_package/SHA256SUMS` binds this manuscript. The edits in
this pass required reconciliation, performed once and last, after
`scripts/write_render_closure_state.py` regenerated the derived render state.
Content-binding state is back at its baseline `BOUND_PARTIAL / PASS`.

**Digests moved, not deleted.** Six raw digests sat in the Results narrative,
documenting the source-provenance chain behind the BERTMap repair line. That
chain is load-bearing: it is what makes the claim of a *minimal* patch checkable
rather than asserted. The digests were therefore moved into a source-provenance
list in the availability section, with every value preserved byte-for-byte, and
the Results prose now points at it. No checker binds those digests, which was
verified before moving them.
