# ORION-03 publication-freeze addendum V2 (successor)

**Freeze date (this successor):** 2026-09-02
**Status:** `CURRENT_FROZEN_SURFACE_V3__NARROWING_ONLY`
**Supersedes:** `PUBLICATION_FREEZE_ADDENDUM_V1.md` (2026-08-27), which names the
superseded `MANUSCRIPT_V2.md` + `CLAIM_LEDGER_R2.md` surface. V1 remains preserved
unchanged apart from its superseded-pointer header.

This addendum is the dated additive successor required because V1's frozen content
surface no longer names the canonical documents.

## Frozen content surface (V3)

The frozen paper-content packet is `MANUSCRIPT_V3.md` (canonical scientific source) and
`CLAIM_LEDGER_V3.md` (canonical claim ledger), together with the convergence/evidence
authority under `evidence/`. The canonical designation record is
`CANONICAL_SUBMISSION_V3.md`. The packet also carries the checksum-closed submission package `submission/tier-b-final-20260901/` shared by the arXiv and Journal of Automated Reasoning routes; the build-surface note below governs its rebuild state. All ledger statuses stand as frozen there: D3-C1–C6
PROVEN, D3-C7 VERIFIED, D3-C8 MEASURED, D3-C9–C15 forbidden / null / adverse / refuted /
cannot-check. No status in this document modifies the ledger.

## Narrowing-only rule

Relative to V1 and to the frozen V3 ledger, nothing is widened. The 2026-09-02
clarification pass only (a) states the expressiveness gate against annotated-logic,
provenance-semiring, and assumption-based truth-maintenance neighbours as OPEN in
Limitations — a deliberate boundary, recorded in
`SCIENCE_ITEM_DISPOSITION_20260902.md` and `FORMAL_SEPARATION_ATTEMPT_20260902.md`
(rung 1 of the disposition ladder did not land: the attempted impossibility proposition
is not airtight, and internal constructions indicate it is false as naturally matched);
(b) sharpens the stated deltas to TMS/ATMS, annotated logic, provenance semirings, and
authorization logics in Related Work, adding the verified `dekleer1986` citation; and
(c) restates the filed claim as a formal license-propagation system plus one measured
hybrid-authorization phenomenon (46 hybrid authorizations among 1,962 third-party merge
tasks; `evidence/round2-x509-truststore/ROUND2_RESULTS_V2.json`); and (d) adds the
tier-wide disclosure sentence to Limitations stating that all gold labels, audits,
adjudications, and the in-repository reproducer are same-programme, single-author work
using AI assistance, with no out-of-programme reviewer — required by the issue-#78
cross-cutting box and stated plainly where an independent check is impossible before
filing.

## Frozen boundary (unchanged from V1 in substance)

The paper does not claim arbitrary negation, probability, inconsistency handling, broad
human-science usability, independent policy-corpus superiority, external-domain
validation beyond the recorded instantiation, novelty authority over donor mathematics,
journal authority, or submission authority. A future mechanically scored public
policy/configuration corpus is successor work and must not retroactively promote the
current bounded calculus.

## Build-surface note (for the filer) — RESOLVED 2026-09-02

The frozen reader PDF named in `CANONICAL_SUBMISSION_V3.md`
(SHA-256 `4a1b74604880deccaebfac7697794ee0864b8f0a33271db6d293af51e46f0dc9`) predates the 2026-09-02 clarification edits to `MANUSCRIPT_V3.md`
and `publication_closure_20260831/references.bib`. **The rebuild has since been
executed on a build-capable host** (billy-old, 2026-09-02): the candidate package
under `publication_closure_20260831/candidate_package/` was rebuilt from the edited
sources and passed the round-3 independent release review at full candidate+package
scope (`review_rounds_20260902/ROUND3_PASS_INDEPENDENT_RELEASE_REVIEW_20260902.json`;
rounds 1–2 FAILed and their records are retained alongside). The canonical reader
PDF hash in `CANONICAL_SUBMISSION_V3.md` and the
`submission/tier-b-final-20260901/` packet digests are rebound to the rebuilt render
(SHA-256 `ed34801f5c2009259f84d61a9c15bae25f91c3d9c0c5e51519453b102a331da1`). The `submission/publication-ready-20260831/` package predates the
edits and remains checksum-closed history under its own hashes.
