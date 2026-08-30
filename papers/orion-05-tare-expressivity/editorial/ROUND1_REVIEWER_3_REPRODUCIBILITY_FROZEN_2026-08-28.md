# Frozen Reviewer 3 report: reproducibility, reporting, clarity, boundaries, and readership

## Review identity and independence

- Review date: 2026-08-28
- Target supplied in the packet: *Quantum*, original research article
- Frozen packet: `support_two_initial_blind_review_packet_2026-08-28.zip`
- Frozen packet SHA-256: `b55f80649d0e04ed7901b7ab1550586e2d5c4c6f61051fc1922da83ee0f58dbf`
- Manuscript PDF SHA-256 within the packet: `1039ffa55e7ee8858d53bb95cc6250d0aa95fd9982dbf7b4f2622e5ce919e788`
- Review lens: reproducibility, reporting completeness, clarity, scientific boundaries, and reader accessibility
- Independence: this report used only the frozen packet. It did not use an author claim ledger, Reviewer 1 or Reviewer 2 report, editor synthesis, response, revision delta, later manuscript, or repository source.
- Decision boundary: this is a simulated blind review, not external peer review and not a journal decision.

## Recommendation

**Major revision.** The central normal-form argument is compact, the adverse runtime outcome is retained, and I found no obvious mathematical contradiction in the two analytic lemmas or the support-reduction argument. However, the current reviewer packet is not verification-complete. The exact grammar and normalized objective are not specified unambiguously in the manuscript; most of the bounded implementation and all runtime claims are supplied only as aggregate JSON assertions; and the reviewer archive exposes private audit/development language and digest material. These are repairable reporting and artifact problems. This report does not ask the authors to hide the adverse result or manufacture new performance evidence.

## Strengths

1. The paper consistently separates an all-size structural theorem from finite conformance and implementation performance.
2. The support-one obstruction is explicit rather than hidden. An independent enumeration written for this review, without importing the supplied solver, confirmed 12 ordered support-one anticommuting pairs per block and minimum normalized cost 6 for the displayed instance.
3. The two runnable checks succeeded. `proof_sanity.py` returned `PASS`; `verify_sharpness.py` returned support-two cost 5 and support-one cost 6.
4. All 19 files covered by the supplied checksum manifest matched. The manuscript source duplicated inside the review archive is byte-identical to the source beside the PDF.
5. All seven PDF pages were rendered and inspected. I found no clipping, overlap, broken reference, unreadable table, or final-page spill.
6. The manuscript prominently retains the 12 timeouts and states that no runtime, memory, hardware, fault-tolerant, or physical-resource benefit was established.

## Major concerns

### R3-OR5-001 - The admitted grammar and normalized objective are not self-contained

**Challenged claims.** The exact support-two theorem, the displayed costs 5 and 6, and the induced exact algorithm.

**Concern.** The Methods say that the shared Pauli realizes “the same two nonzero symplectic labels,” but the supplied implementation permits only the ordered label pairs `(0,1)` and `(1,0)`. One of those two labels is zero. The manuscript also describes only the marginal refund from deleting a frame coordinate. It never writes the normalized frame term used by the artifact, namely a multiplier applied to `support minus one` for each frame; the supplied code calls this the production raw cost minus 18. Thus a reader cannot derive the reported frame cost 2, total cost 5, or unrestricted/support-one comparison from the manuscript’s stated objective alone. “Admitted instance,” the exact branch/central semantics, and “full-subject” are also not formally defined.

**Why it matters.** The theorem is grammar-specific. Ambiguity in the grammar or objective changes the theorem’s denotation and prevents an independent reader from reproducing the sharpness calculation without reverse-engineering code.

**Resolution test.** Add one self-contained formal specification that defines: the Pauli encoding and global symplectic form; all instance variables and admissibility conditions; target pairing and relative orders; ordered frame constraints; the exact shared-label equations; central choices; the full normalized objective as a displayed equation, including all constants or offsets; and the unrestricted and support-bounded feasible sets. A reader using only that specification must be able to recompute the displayed support-two witness cost as `2 + 2 + 1 = 5`, enumerate the support-one feasible family, and obtain the same objective as the public solver. Replace “two nonzero labels” with the mathematically correct ordered-label statement.

### R3-OR5-002 - The claimed exact-conformance programme is not regenerable from the archive

**Challenged claims.** Complete one-qubit comparison, separate exact-referee agreement, two-qubit stress checks, phase reconstruction, and the statement that every completed witness verified.

**Concern.** The archive contains a direct solver and two small runnable checks, but it does not contain the claimed separate exact referee, a driver that regenerates `exact_comparison_summary.json`, per-case outputs for the 4,096 one-qubit target tuples/65,536 configuration slices, or a neutral checker that consumes those records. The summary reports that separate checks passed, but a static summary is not an independently reproducible comparison.

**Why it matters.** These claims are used to corroborate implementation conformance and the sharpness witness. They are not the logical proof of the theorem, but the manuscript and availability statement present them as independently checkable evidence.

**Resolution test.** Supply the separate referee or an implementation-independent verifier, the exact case generator, and a deterministic command that reconstructs every published count and stress-case result from raw records. In a clean extraction, the command must reproduce the summary exactly and must fail after a deliberate one-record perturbation. If those materials cannot be released, narrow the manuscript to the two checks actually shipped and describe the remaining comparison as unavailable internal evidence rather than independently reproducible evidence.

### R3-OR5-003 - The runtime claim lacks the pre-specified design and row-level evidence needed to audit it

**Challenged claims.** The pre-specified 120-attempt study; 108 completions and 12 timeouts; all six unrestricted full-subject completions; all six support-two full-subject timeouts; equality and witness validity on every jointly completed cell; and no measured runtime or memory improvement.

**Concern.** `runtime_summary.json` contains only aggregate counts. The packet does not identify the 120 rows, define the six “full-subject” cells, include the alleged pre-measurement specification, preserve row-level timeout/correctness/witness observations, identify hardware/OS/Python/solver versions, or provide a benchmark driver. The Data and code availability section says the runtime specification and timeout rows are available, but neither is present as an auditable object.

**Why it matters.** A timeout is part of the scientific result here. Without the design and rows, a reviewer cannot distinguish a faithful adverse panel from an aggregate assembled after measurement or determine whether the same limit and success rule were applied consistently.

**Resolution test.** Add the immutable pre-measurement protocol, a complete 120-row table with subject/cell identity, solver, repetition, limit, status, timing/memory fields, correctness/witness fields, environment, and source binding, plus a script that regenerates every aggregate. A clean run of the aggregator must yield 120 total, 108 completed, 12 timed out, six unrestricted full-subject completions, six direct full-subject timeouts, zero errors, and the stated joint-cell checks. If raw rows cannot be released, remove “pre-specified,” the exact row claims, and reproducibility language; retain only a clearly labeled descriptive adverse observation.

### R3-OR5-004 - The reviewer archive fails the reader-surface boundary

**Challenged claim.** The archive is a clean anonymous scientific review artifact that excludes development history.

**Concern.** The manuscript PDF itself contains no project code, path, branch, commit, issue, or digest. The supporting archive does. It includes a public `SHA256SUMS` digest list and code/JSON language such as “frozen 512-state production XOR DP,” “donor-owned,” “production convention,” “production raw cost minus 18,” `production_internal_checks`, and `project_quantum_imports`. Those strings describe private implementation lineage and governance, not the scientific method. The manuscript also uses audit-style phrases such as “authorized conclusion” and “release decisions,” which are less severe but should be translated into ordinary scientific language.

**Why it matters.** The review archive is submission-facing. Internal lineage can deanonymize, confuse readers, and makes the scientific object appear to depend on an undisclosed production system.

**Resolution test.** Rebuild the anonymous review archive from a neutral public-source tree. Remove private digests from the reviewer artifact and retain them only in a private binding record. Rename internal fields/comments/docstrings in scientific terms and remove references to donors, production systems, frozen release history, project imports, and internal checks. Recursively scan PDF text, manuscript source, archive entry names, and every text/code payload; require zero hits for project/paper/run identifiers, local/repository paths, hashes/digests, commits/branches/CI/issues/PRs/workflows, machine terminal/release strings, or private provenance language. Re-run both public checks after sanitization.

### R3-OR5-005 - A reader cannot yet reconstruct the scientific object efficiently

**Challenged criterion.** Clarity for the intended *Quantum* reader.

**Concern.** The paper moves directly from a high-level Tag-and-Restore description to frame pairs, two branches, central choices, shared labels, and factored corrections. The terms “central,” “shared-label syndrome,” “relative target order,” “exact referee,” and “full-subject cell” are either undefined or only inferable from code. The sharpness witness appears before a worked explanation of how all feasibility constraints and objective components are evaluated.

**Why it matters.** The result is intentionally narrow. Its value depends on readers being able to understand exactly what was reduced and what was not without already knowing the donor construction or reading software.

**Resolution test.** Add a compact worked grammar instance or schematic that identifies the six targets, three blocks, both branches, central selections, frame anticommutation, ordered shared-label equations, corrections, factor sharing, and objective components. Apply the formal definition from R3-OR5-001 to the displayed sharpness witness line by line. Define “exact referee” as an algorithm and replace “full-subject cell” with a scientific panel definition.

### R3-OR5-006 - The bounded literature search is not reported as a reproducible boundary

**Challenged claims.** The list of inspected research areas, the statement that no exact equivalent theorem was located, and the residual contribution boundary.

**Concern.** The manuscript appropriately avoids an absolute priority claim, but it supplies no search date, databases, query families, inclusion/exclusion rule, or nearest-neighbor comparison table. The packet contains bibliography entries, not source-entailment records. I therefore cannot audit whether the cited works support the exact distinctions claimed or whether the bounded search is current and adequate.

**Why it matters.** The target contract supplied in the packet includes significance beyond the state of the art. A bounded negative search can support cautious wording only when the boundary itself is inspectable.

**Resolution test.** Add a dated search-method paragraph and a concise nearest-work table containing object, assumptions, transformation, preserved quantity, exact/approximate status, and difference from the present theorem. Bind every literature proposition to a source locator. An independent checker must be able to reproduce the search boundary and confirm that the manuscript says only “not located within this search,” never absence or priority.

## Minor concerns

### R3-OR5-007 - PDF metadata and accessibility

The seven-page PDF has no embedded title or author metadata and is untagged. An anonymous author field can remain anonymous, but the exact title should be embedded and target accessibility expectations should be checked.

**Resolution test.** `pdfinfo` reports the correct title, an anonymity-safe author value, no scripts or suspicious objects, and the target-required accessibility state; every page still renders cleanly.

### R3-OR5-008 - Submission and build statements need final human/technical closure

The title page says “Anonymous authors,” while the contribution statement uses singular “The author.” Conflict, funding, affiliation, and final author approval are outside this blind packet. The source archive also gives no manuscript build command or pinned TeX engine; the available environment lacked a TeX engine, so I could not verify source-to-PDF reproduction.

**Resolution test.** Reconcile singular/plural authorship, obtain human approval for contribution and AI-assistance statements, include any target-required declarations, and provide a clean build recipe that produces a text- and page-equivalent seven-page PDF from the exact public source.

## Verification performed

| Check | Result |
|---|---|
| Frozen outer packet hash | Matched the supplied binding |
| Inner archive checksum verification | 19/19 files matched |
| `proof_sanity.py` | PASS; 192 local cases; maximum delta 2; no failure for support 3-8 |
| `verify_sharpness.py` | PASS; support-two cost 5; support-one cost 6 |
| Independent support-one enumeration | 12 ordered pairs per block; minimum 6; 64 minimizing configurations under the independently implemented model |
| Citation-key closure | 12 cited keys; 12 bibliography entries; no missing, uncited, or duplicate keys |
| Source duplication | Outer manuscript source and source inside review archive are identical |
| PDF visual QA | 7/7 pages inspected; no clipping, overlap, broken references, or final-page defect |
| PDF metadata/security | 7 pages, letter size, no JavaScript, no forms, no suspects; title metadata absent; untagged |
| Manuscript-facing leakage | No project identifiers, paths, hashes, or workflow history found in PDF/source |
| Review-archive leakage | Failed: digests and private production/frozen/donor/internal terminology present |

## Boundary of this report

The analytic theorem was not refuted by this review. The report does not validate target significance, novelty, author declarations, or real journal acceptance. The cheapest valid repair is formalization plus artifact reconstruction and claim-accurate reporting; no new favorable experiment is requested, and the adverse runtime outcome must remain visible.
