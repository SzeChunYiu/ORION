# Latest academic-paper-skills targeted release audit

`skills-applied: academic-paper-pipeline@1.20.0, academic-writing@1.18.0, nature-polishing@7.5.0, nature-reviewer@3.5.0, publication-release-integrity, manuscript-element-justification`

**Verified skill authority:** `SzeChunYiu/academic-paper-skills@be335c630240cd5e73535e8f813594b227d736a8`  
**Release scope:** ORION-01--25 dual-route publication adapters, with immediate manuscript/PDF priority for ORION-04--14, ORION-19, ORION-21, ORION-23 and ORION-24.  
**Scientific authority delta:** `NONE`

## Manuscript-element justification

The final pass reviewed the release elements that were actively changed or
revalidated. It did not claim a new sentence-by-sentence rewrite of already
closed manuscripts.

| Element | Reader/scientific function | Deletion or misrepresentation consequence | Decision |
|---|---|---|---|
| Canonical paper identity | Keeps one scientific object per ORION number and prevents legacy aliases from becoming extra submissions. | A legacy component could be filed as a second paper or carry a conflicting claim ceiling. | Keep one canonical package. |
| Author block | Attributes every public/single-blind route to Sze Chun Yiu, Stockholm University, `sze-chun.yiu@fysik.su.se`; preserves anonymity only where the verified journal route is double blind. | Public metadata would contradict the author's instruction, or a double-blind review copy could leak identity. | Correct and verify every route. |
| arXiv/journal manuscript pair | Preserves one scientific surface while allowing anonymity or mandatory venue formatting. | A stale arXiv source can silently report different sample size, results, or limitations from the journal manuscript. | Require cross-route scientific-surface similarity. |
| Abstract and claim boundary | Makes the bounded answer and its non-implications visible before the detailed evidence. | Editors/readers could infer a withdrawn superiority, external-transfer, novelty, or authority claim. | Retain calibrated prose. |
| Limitations/interpretation prose | Explains how null, adverse, refuted, excluded and `CANNOT_CHECK` results change interpretation. | A mechanical inventory would interrupt reasoning, while omission would widen the claim. | Keep cohesive prose, not bullet-point limitations. |
| Availability and release binding | Distinguishes inspectable source/package integrity from external replication or a real submission. | Repository checks could be mistaken for scientific or portal authority. | Keep explicit and content-bound. |

## Hostile findings and minimum-sufficient repairs

1. **Author-identity contradiction.** The inherited builder encoded
   `Independent Researcher` and expressly excluded Stockholm University despite
   the author's later explicit instruction. The canonical identity policy,
   attributed PDFs/sources, title pages, cover materials, metadata and checksums
   are regenerated with `Stockholm University`. Anonymous reviewer files remain
   anonymous where required.
2. **ORION-07 route drift.** The arXiv adapter used the older one-question V0
   manuscript while the TMLR route used the current three-question bounded
   manuscript. Both routes now derive from the same current TMLR scientific
   source; only attribution and mandatory route formatting differ.
3. **ORION-04 orphaned front-matter line.** Prefix-only removal of a wrapped
   internal routing note left `boundaries, and the absence of novelty or
   editorial authority` above the Abstract. The complete routing block is now
   removed, and the attributed global adapter no longer duplicates affiliation
   and correspondence lines.
4. **Route-parity blind spot.** The former verifier proved that each route built
   but not that both routes represented the same science. The verifier now
   rejects large arXiv/journal scientific-surface drift while allowing mandatory
   anonymity and venue-specific abstract formatting.

No finding requires a new experiment. Every controlling negative, null,
withdrawn, excluded, timeout, open and `CANNOT_CHECK` terminal remains retained.
