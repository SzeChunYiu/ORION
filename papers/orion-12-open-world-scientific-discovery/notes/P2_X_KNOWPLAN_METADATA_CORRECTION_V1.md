# P2-X KNOWPLAN metadata correction V1

Date: 2026-08-19

Status: `CORRECTED_PRIMARY_SOURCE_BINDING`

During the P2-X promotion-integrity repair, live primary-source verification found that the bibliography entry `knowplan2026` paired arXiv `2608.06530` with an incorrect title and author list.

The incorrect promoted record was:

- title: `KNOWPLAN: An Information-Efficient Neuro-Symbolic Architecture for Zero-Retraining Data Engineering`;
- authors: de Salis et al.;
- arXiv id: `2608.06530`.

Primary-source verification of arXiv `2608.06530` shows the actual paper is:

- title: **`KNOWPLAN: Knowledge-Driven AI Agents for Smart Degree Pathway Planning`**;
- authors: **Shuheng Cao, Weijia Zhang, Jiaqi Wu, Xiyun Hu, Yat Yang, Juqy Chen, Zhaoxiang Feng**.

The false title could not be located in primary-source arXiv searches and is rejected rather than reassigned to a guessed identifier.

The corrected source is still structurally relevant to the P2 nearest-work sentence: its abstract explicitly describes a finite set of atomic catalog obligations and termination on a closure certificate over index, schema, provenance, and reference completeness. Therefore the citation is retained with corrected metadata; no P2 scientific claim is broadened by the correction.

The literature evidence record for `knowplan2026` must be regenerated against the corrected title and arXiv id before the repair can pass. Any future mismatch remains fail-closed.
