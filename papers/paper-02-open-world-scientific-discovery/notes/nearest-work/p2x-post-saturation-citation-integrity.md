# P2-X post-saturation citation-integrity repair

Date: 2026-08-19.

This note records bibliography/evidence drift introduced when the P2-X nearest-work paragraph was promoted into the manuscript. It changes no P2-X scientific result or nearest-work disposition.

## `knowplan2026` — recorded mismatch, metadata repaired

The pre-existing bibliography entry paired arXiv:2608.06530 with the wrong title and authors. The primary arXiv record is **KNOWPLAN: Knowledge-Driven AI Agents for Smart Degree Pathway Planning**, by Shuheng Cao, Weijia Zhang, Jiaqi Wu, Xiyun Hu, Yat Yang, Juqy Chen and Zhaoxiang Feng. The paper itself still supports the mechanism for which P2 cites it: it uses a finite set of atomic catalog obligations and terminates acquisition on an explicit closure certificate. The citation key and mechanism mapping therefore remain usable, but the old metadata was a live defect.

The bibliography is repaired in place. `evidence/literature/knowplan2026.json` deliberately retains `MISMATCH` so the defect does not disappear from the audit history.

## Four additional author/identifier repairs

The promoted P2-X paragraph also added `donotstopearly2026`, `confidencebasedstop2026`, `icore2026` and `scienceintent2026` without resolver fields or stored evidence records, and their author metadata did not match the primary arXiv records. Their titles/IDs support the mechanism-level citations; the bibliography now uses the primary author metadata and explicit arXiv identifiers, and one stored evidence record exists for every key.

These are citation-integrity repairs only. They do not promote generic evidence-based completion, confidence stopping, obligation graphs, intent/closure-gap terminology, or any other donor-owned mechanism into an ORION novelty claim.
