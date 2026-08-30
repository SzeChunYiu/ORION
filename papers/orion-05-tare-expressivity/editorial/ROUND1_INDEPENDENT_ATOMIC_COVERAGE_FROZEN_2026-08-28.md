# Frozen independent atomic-coverage pass

## Scope and independence

- Date: 2026-08-28
- Immutable input: `support_two_initial_blind_review_packet_2026-08-28.zip`
- Input SHA-256: `b55f80649d0e04ed7901b7ab1550586e2d5c4c6f61051fc1922da83ee0f58dbf`
- Audited surfaces: title, abstract, all manuscript sections, theorem/proof text, table, references, PDF, manuscript source, and the complete accompanying review archive.
- Excluded by design: author ledger, other reviewer reports, editor synthesis, responses, revision deltas, later source, repository evidence, and live external-source verification.
- Method: the inventory below was recreated from the frozen manuscript rather than checked against an author-provided row structure. Formal claims were normalized; proof dependencies and boundary cases were challenged; supplied checks were rerun; the support-one lower bound was independently enumerated without importing the supplied solver; all seven PDF pages and all review-archive text/code payloads were inspected.

Status vocabulary follows the pipeline contract: `VERIFIED`, `BOUNDED_INFERENCE`, `COHERENT_DEFINITION`, `NOT_APPLICABLE`, `SUPPORTED_INTERNAL`, `UNRESOLVED`, `CONTRADICTED`, `BLOCKED`, and `NOT_ASSESSABLE`.

## Independent atomic inventory

### Definitions, scope, and method

| ID | Atomic proposition | Status | Independent check, boundary, or release action |
|---|---|---|---|
| AC-D01 | An admitted instance contains six nonidentity Pauli targets on a common positive qubit count. | UNRESOLVED | The prose says nonidentity, while the “complete one-qubit domain” summary counts all `4^6=4096` Pauli tuples, including identity. Define whether identity targets are admitted or are only out-of-scope stress cases. |
| AC-D02 | The six targets are supplied as three ordered pairs. | COHERENT_DEFINITION | Consistent with the solver and sharpness instance. |
| AC-D03 | Six unpaired targets can be covered by a constant outer search over 15 perfect matchings. | VERIFIED | The number of perfect matchings of six labeled objects is 15. |
| AC-D04 | Global Pauli phases can be ignored for support counting. | VERIFIED | Correct for the declared phase-ignored support objective; phase reconstruction is a separate conformance claim. |
| AC-D05 | The binary symplectic product determines Pauli commutation. | VERIFIED | Standard finite-Pauli relation; the supplied code implements it consistently. |
| AC-D06 | Each block uses an ordered anticommuting frame pair. | COHERENT_DEFINITION | The constraint is used consistently in the proof and executable sharpness check. |
| AC-D07 | Each block assigns two targets to two branches and marks one branch central. | UNRESOLVED | Branch assignment is described, but the full target-order and central-choice semantics are not written as a formal feasible-set definition. |
| AC-D08 | A shared Pauli has “the same two nonzero symplectic labels” against every ordered pair. | CONTRADICTED | The public implementation and witness use `(0,1)` or `(1,0)`, so one label is zero. Replace with exact ordered equations. |
| AC-D09 | A local correction letter is the phase-ignored Pauli product of target and assigned frame letters. | COHERENT_DEFINITION | Consistent across prose and code. |
| AC-D10 | The local three-way factor cost is `w(a)+w(b)+w(c)-2*1[a=b=c!=I]`. | VERIFIED | Equivalent to the supplied `f3` implementation and independently checked on all 64 triples. |
| AC-D11 | Deleting one supported coordinate from a central frame refunds 2 and from a noncentral frame refunds 4. | VERIFIED | Matches the marginal frame-cost implementation. |
| AC-D12 | The absolute normalized frame cost used in reported totals is completely defined in the manuscript. | CONTRADICTED | The manuscript omits the `support minus one` baseline/offset needed to obtain frame cost 2 and total cost 5. |
| AC-D13 | The shared operator contributes 2 per supported qubit. | VERIFIED | Matches witness cost and public solver. |
| AC-D14 | The remaining objective is the coordinate sum of the two branch factor costs. | VERIFIED | Matches the displayed `F` and public solver. |
| AC-D15 | The unrestricted family and support-k family retain identical non-support choices. | COHERENT_DEFINITION | Sufficient for family containment, but the complete feasible family should be formalized under AC-D07/08/12. |
| AC-D16 | “Admitted instance,” “exact referee,” and “full-subject cell” denote fully specified reader-facing objects. | UNRESOLVED | None receives a complete local definition. |

### Formal claims and proof dependencies

| ID | Atomic proposition | Status | Independent check, boundary, or release action |
|---|---|---|---|
| AC-F01 | Replacing one correction letter `pf` by `p` increases `F` by at most 2. | VERIFIED | Analytic case split is correct; supplied independent checker exhausts 192 `(p,f,u,v)` cases. |
| AC-F02 | If the old triple has no sharing discount, the ordinary weight rises by at most 1 and a new discount cannot worsen it. | VERIFIED | Direct consequence of changing one letter. |
| AC-F03 | If the old triple has the sharing discount, destroying it adds 2 but the ordinary weight does not increase. | VERIFIED | For `pf=u=v!=I`, either `p=I` lowers ordinary weight or `p` is another nonidentity and preserves it. |
| AC-F04 | For one frame, each supported coordinate has class `(<Aq,A'q>,<Sq,Aq>)` in `F2^2`. | COHERENT_DEFINITION | Denotation is clear after interpreting the missing exact label equations. |
| AC-F05 | Global anticommutation makes the first class components sum to 1. | VERIFIED | Terms outside `supp(A)` vanish. |
| AC-F06 | A zero class gives a zero-sum singleton. | VERIFIED | Immediate. |
| AC-F07 | A repeated nonzero class gives a zero-sum pair. | VERIFIED | Equal vectors cancel in characteristic two. |
| AC-F08 | If classes are distinct and nonzero at support at least 3, the support-three case contains all three nonzero vectors and has first-component sum 0. | VERIFIED | There are only three nonzero vectors in `F2^2`; support above 3 already forces repetition. |
| AC-F09 | Every frame of support at least 3 has a nonempty proper zero-sum subset of size at most 2. | VERIFIED | The analytic proof covers all sizes; finite enumeration through support 8 corroborates it. |
| AC-F10 | Removing the selected frame letters preserves anticommutation with the partner. | VERIFIED | The first class components over the removed subset sum to zero. |
| AC-F11 | The same removal preserves the frame’s shared-label equation. | VERIFIED | The second class components over the removed subset sum to zero. |
| AC-F12 | The modified frame remains nonidentity. | VERIFIED | The removed subset is proper. |
| AC-F13 | At each removed coordinate, the frame refund offsets the correction increase. | VERIFIED | Refund is at least 2 and AC-F01 bounds the increase by 2. |
| AC-F14 | The shared-operator and all untouched terms remain unchanged during one exchange. | VERIFIED | Follows from the construction. |
| AC-F15 | Repeated exchanges terminate because total frame support strictly decreases. | VERIFIED | Nonnegative integer measure. |
| AC-F16 | Starting from an optimum, a non-increasing feasible exchange remains at the optimum value. | VERIFIED | A lower value would contradict optimality of the starting point. |
| AC-F17 | Family containment gives unrestricted optimum no larger than support-two optimum. | VERIFIED | Standard minimization containment direction. |
| AC-F18 | Every admitted optimum therefore has a support-two representative of equal cost. | VERIFIED | Follows from AC-F09 through AC-F17, conditional on the exact admitted grammar being formalized. |
| AC-F19 | The displayed support-two witness satisfies all three anticommutation constraints and common orientation `(1,0)`. | VERIFIED | Manually recomputed and confirmed by the executable sharpness verifier. |
| AC-F20 | The displayed witness has normalized frame, shared-operator, and correction costs 2, 2, and 1. | VERIFIED | Independently recomputed using the objective implemented in the packet; the missing manuscript baseline must still be repaired. |
| AC-F21 | There are 12 ordered anticommuting support-one pairs on two qubits. | VERIFIED | Independently enumerated from six weight-one Paulis. |
| AC-F22 | The complete support-one family for the displayed instance has minimum 6. | VERIFIED | Independent enumeration, importing no supplied code, returned minimum 6 and 64 minimizers. |
| AC-F23 | A separate exact referee independently returns support-two cost 5. | SUPPORTED_INTERNAL | Asserted in static JSON; the separate referee and generator are absent. |
| AC-F24 | Support one is not uniformly sufficient and the uniform threshold is exactly two. | VERIFIED | AC-F18 plus the independently verified 5-versus-6 witness establishes the sharp threshold. |
| AC-F25 | The number of nonidentity Paulis of support one or two is `3n+9*C(n,2)`. | VERIFIED | Direct combinatorial count. |
| AC-F26 | A weight-one first frame has `6n-4` anticommuting support-at-most-two partners. | VERIFIED | Two same-coordinate choices plus `2*3*(n-1)` one-overlap weight-two choices. |
| AC-F27 | A weight-two first frame has `12n-16` such partners. | VERIFIED | Four weight-one, four same-support weight-two, and `12(n-2)` one-overlap choices. |
| AC-F28 | The ordered-pair count is `54n^3-108n^2+60n`. | VERIFIED | Algebraic substitution of AC-F25 through AC-F27; public generator agrees for `n=1..6`. |
| AC-F29 | Three frame pairs use at most nine coordinates. | VERIFIED | Each pair’s active union has at most three coordinates. |
| AC-F30 | A minimum shared operator has no support outside that active union. | VERIFIED | Outside letters affect no symplectic constraint and strictly add cost when nonidentity. |
| AC-F31 | Six binary symplectic equations can be solved by a 64-syndrome dynamic program over at most nine coordinates. | VERIFIED | The public standard-library implementation realizes this finite DP. |
| AC-F32 | After one linear target scan, each candidate correction update touches at most nine active coordinates. | VERIFIED | Baseline-plus-active-union decomposition is correct. |
| AC-F33 | Enumerating three ordered pair choices gives `O(n^9)` word-RAM time. | VERIFIED | Pair family is `Theta(n^3)` and candidate work is constant after preprocessing. |
| AC-F34 | Working memory is `O(n^3)`. | VERIFIED | Target baseline is `O(n)` and stored pair universe is `O(n^3)`; no triple cube is stored. |
| AC-F35 | Bit-complexity accounting adds only polylogarithmic factors. | BOUNDED_INFERENCE | Plausible for indices and accumulated costs, but word size and arithmetic conventions should be stated explicitly. |

### Finite checks, exact-comparison claims, and runtime claims

| ID | Atomic proposition | Status | Independent check, boundary, or release action |
|---|---|---|---|
| AC-E01 | The standalone checker evaluates 192 local correction cases. | VERIFIED | Rerun output and source agree. |
| AC-E02 | The maximum observed local factor-cost increase is 2. | VERIFIED | Rerun returned six maximizers and maximum 2. |
| AC-E03 | Odd-first-parity class tuples through support 8 have no zero-subset failure above support 2. | VERIFIED | Rerun returned zero failures for support 3-8. |
| AC-E04 | Exactly four ordered support-two obstruction patterns occur. | VERIFIED | Rerun returned `(1,2),(1,3),(2,1),(3,1)`. |
| AC-E05 | The constructive pair generator matches the formula for `n=1..6`. | VERIFIED | Static records are consistent with the independently derived formula; the generator source is inspectable. |
| AC-E06 | The comparison covers all 4,096 one-qubit six-target tuples and 65,536 central/orientation slices. | SUPPORTED_INTERNAL | Counts appear only in a static summary; no driver or raw record is supplied. |
| AC-E07 | Every one-qubit direct optimum agrees with a separate exact referee. | SUPPORTED_INTERNAL | Separate referee absent. |
| AC-E08 | All compared one-qubit witnesses and phase certificates independently validate. | SUPPORTED_INTERNAL | Aggregate booleans only; no per-case records or independent checker input. |
| AC-E09 | The two named non-sharp stress cases have exact costs 6 and 8 under both solvers. | SUPPORTED_INTERNAL | Static rows only. |
| AC-E10 | The sharpness case has support-one cost 6 and support-two cost 5. | VERIFIED | Independently enumerated and executable verifier rerun. |
| AC-E11 | Every feasible shared operator can be confined to the active union in the checked preprocessing panel. | SUPPORTED_INTERNAL | Summary reports 412 feasible cases, but no generator/raw cases are supplied. The analytic confinement claim AC-F30 is independently verified. |
| AC-E12 | The runtime study contained exactly 120 pre-specified attempts. | SUPPORTED_INTERNAL | Aggregate assertion only; protocol and rows absent. |
| AC-E13 | Exactly 108 attempts completed and 12 timed out with zero other errors. | SUPPORTED_INTERNAL | Aggregate assertion only. |
| AC-E14 | Both solvers agreed on every jointly completed cell. | SUPPORTED_INTERNAL | No row-level outputs. |
| AC-E15 | Every completed witness verified. | SUPPORTED_INTERNAL | No row-level witness records. |
| AC-E16 | The unrestricted solver completed all six full-subject cells. | SUPPORTED_INTERNAL | “Full-subject” is undefined and rows are absent. |
| AC-E17 | The direct support-two solver timed out on all six corresponding cells at 120 seconds. | SUPPORTED_INTERNAL | Time-limit aggregate present; subjects, environment, and rows absent. |
| AC-E18 | The runtime panel establishes no measured runtime or memory improvement. | BOUNDED_INFERENCE | This is the appropriately adverse interpretation of the supplied aggregate, but the underlying panel remains internally supported rather than independently verified. |

### Interpretation, boundary, and cross-section restatements

| ID | Atomic proposition | Status | Independent check, boundary, or release action |
|---|---|---|---|
| AC-I01 | The theorem concerns representation, not practical implementation speed. | VERIFIED | Exact scope follows from the objective and proof. |
| AC-I02 | The complexity result is an upper bound, not a lower bound or exponent-optimality claim. | VERIFIED | Consistent in abstract, Results, Limitations, and Conclusion. |
| AC-I03 | No hardware, fault-tolerant, physical-resource, energy, or universal-compiler advantage is established. | BOUNDED_INFERENCE | Correctly bounded by the supplied evidence. |
| AC-I04 | The support-one obstruction occurs at the parity/shared-label boundary. | BOUNDED_INFERENCE | Plausible interpretation of the verified upper proof and lower witness; no broader mechanism is claimed. |
| AC-I05 | Practical significance would require a better algorithm, broader theorem, or physical-resource result. | BOUNDED_INFERENCE | Clearly presented as a future condition, not a current result. |
| AC-C01 | The title states only a support-two normal form for the shared-tag grammar. | VERIFIED | No universal or performance claim in the title. |
| AC-C02 | The abstract’s support-two theorem matches the Results theorem. | VERIFIED | Scope is consistent except for the unresolved exact grammar specification. |
| AC-C03 | The abstract’s 5-versus-6 sharpness statement matches the Results witness. | VERIFIED | Independently confirmed. |
| AC-C04 | The abstract’s `O(n^9)` time and `O(n^3)` memory match the Results derivation. | VERIFIED | Cross-section numbers agree. |
| AC-C05 | The abstract’s finite-conformance statements do not claim all-size proof authority. | VERIFIED | Evidence boundary is explicit. |
| AC-C06 | The abstract, Discussion, Limitations, and Conclusion all retain the adverse six-cell timeout result. | VERIFIED | No positive performance restatement was found. |

### Literature, novelty, and references

| ID | Atomic proposition | Status | Independent check, boundary, or release action |
|---|---|---|---|
| AC-L01 | The studied grammar derives from the cited Tag-and-Restore construction. | NOT_ASSESSABLE | Full cited source and entailment locator are outside the frozen packet. |
| AC-L02 | Anticommuting partitioning, Pauli-cluster compilation, and named Pauli compiler representations are established as described. | NOT_ASSESSABLE | Bibliographic entries exist; source entailment was not available under the blind-packet restriction. |
| AC-L03 | Support reduction is not new as a general idea. | NOT_ASSESSABLE | Plausible and cautiously worded, but requires source-level verification. |
| AC-L04 | Phase-gadget and parity-network works address different objects from this exact frame exchange. | NOT_ASSESSABLE | Requires comparison against located source passages. |
| AC-L05 | Two-qubit universality and stabilizer normal forms do not anticipate the grammar-specific theorem. | NOT_ASSESSABLE | The generic facts and the non-anticipation inference both require source-level checking. |
| AC-L06 | Hamiltonian weight reduction/perturbative gadgets change the encoded object rather than prove this cost-monotone exchange. | NOT_ASSESSABLE | Requires source entailment. |
| AC-L07 | Current bounded searches inspected the listed compiler/synthesis/resource categories. | SUPPORTED_INTERNAL | No dated search protocol, queries, databases, or screening record in the packet. |
| AC-L08 | No exact equivalent of the complete grammar-specific theorem was located. | SUPPORTED_INTERNAL | Properly bounded in prose, but the search cannot be reproduced from the packet. |
| AC-L09 | Novelty beyond the narrow descriptive formulation remains subject to independent review. | BOUNDED_INFERENCE | Appropriate boundary; it is not a novelty verification. |
| AC-L10 | Every citation key resolves to exactly one bibliography entry. | VERIFIED | 12 unique cited keys, 12 entries, no missing, uncited, or duplicate keys. |
| AC-L11 | Bibliographic metadata and proposition-level source entailment are correct. | NOT_ASSESSABLE | Live or full-text verification was excluded from this frozen pass. |

### Table, availability, compliance, and surface claims

| ID | Atomic proposition | Status | Independent check, boundary, or release action |
|---|---|---|---|
| AC-T01 | Table 1 maps the analytic exchange proof to the exact normal form. | VERIFIED | Matches AC-F18. |
| AC-T02 | Table 1 maps the cost 5-versus-6 witness to support-one insufficiency. | VERIFIED | Matches AC-F20/22. |
| AC-T03 | Table 1 maps the constructive count to the direct `O(n^9)` upper bound. | VERIFIED | Matches AC-F28/33. |
| AC-T04 | Table 1 maps finite implementation checks to conformance on checked domains. | SUPPORTED_INTERNAL | Correctly bounded, but most comparison records are aggregates only. |
| AC-T05 | Table 1 maps the runtime panel to no measured production value and retained timeouts. | BOUNDED_INFERENCE | Direction is cautious; “authorized conclusion” and “production value” should be translated into ordinary scientific wording. |
| AC-A01 | An anonymous review archive accompanies the manuscript. | VERIFIED | Archive exists and contains neutral top-level scientific filenames except for the digest manifest. |
| AC-A02 | The archive contains proof notes. | UNRESOLVED | No separate proof-notes object is present unless the manuscript source itself is intended; state that explicitly or correct the list. |
| AC-A03 | The archive contains a standalone checker, direct solver, exact-comparison summary, sharpness verifier, and runtime summary. | VERIFIED | All named artifact classes are present. |
| AC-A04 | The archive provides all material needed to regenerate the exact-comparison summary. | CONTRADICTED | Separate referee, drivers, and raw records are absent. |
| AC-A05 | The archive provides the pre-specified runtime protocol and complete timeout rows. | CONTRADICTED | Only an aggregate runtime JSON is present. |
| AC-A06 | The three-layer reproduction instructions are executable as written. | CONTRADICTED | Local lemma and sharpness layers run; exact-comparison and runtime layers can only inspect static summaries. |
| AC-A07 | All twelve timeout rows are included and can be retained rather than discarded. | CONTRADICTED | Counts are present, rows are absent. |
| AC-A08 | Protected data are unnecessary for every paper claim. | NOT_ASSESSABLE | No protected data appear in the packet, but completeness of evidence is an author/repository fact. |
| AC-A09 | The work uses no human, animal, clinical, or personal data. | NOT_ASSESSABLE | Consistent with the mathematical object, but requires author attestation. |
| AC-A10 | The author contribution and LLM-assistance disclosure are final and approved. | BLOCKED | Text is present, but singular/plural authorship and human approval are outside the packet. |
| AC-A11 | All mathematical statements, citations, calculations, and release decisions were checked by the author. | BLOCKED | Author attestation; “release decisions” is internal-governance wording unsuitable for the scientific surface. |
| AC-A12 | Runtime checks used ordinary CPU resources and support no lifecycle comparison. | NOT_ASSESSABLE | No environment/resource record is present. |
| AC-S01 | The exact PDF has seven visually clean pages. | VERIFIED | Every page rendered and inspected; no clipping, overlap, broken references, or final-page spill. |
| AC-S02 | The PDF/source manuscript surfaces contain no project IDs, local paths, hashes, branches, commits, CI/issues/PRs, or machine terminal labels. | VERIFIED | Conservative text scan and page inspection found no such tokens. |
| AC-S03 | The reviewer archive contains no private development/provenance language. | CONTRADICTED | Code/JSON include `frozen 512-state production XOR DP`, donor/production/internal/project terms, and production raw-offset history. |
| AC-S04 | The reviewer archive contains no reader-facing hashes/digests. | CONTRADICTED | `SHA256SUMS` exposes 19 digests; these belong in private binding evidence under the governing surface gate. |
| AC-S05 | The PDF embeds correct title metadata. | UNRESOLVED | `pdfinfo` shows no Title or Author fields. |
| AC-S06 | The exact public source is bound reproducibly to the supplied PDF. | NOT_ASSESSABLE | Sources match across the two packet locations, but no build receipt/command is supplied and no TeX engine was available for an independent rebuild. |
| AC-S07 | The source inside the review archive is identical to the source beside the PDF. | VERIFIED | Recursive byte comparison found no difference. |
| AC-S08 | Anonymous plural authorship is consistent with the contribution statement. | UNRESOLVED | Title page uses plural “authors”; disclosure uses singular “The author.” |
| AC-S09 | The supplied target contract is current and exact as of 2026-08-28. | NOT_ASSESSABLE | Only the frozen excerpt was permitted; live official guidance was not rechecked. |

## Independent coverage findings and stable resolution tests

### ACG-OR5-001 - Exact grammar/objective definition gap

**Open rows:** AC-D01, AC-D07, AC-D08, AC-D12, AC-D16.

**Resolution test.** Publish one complete formal specification and a normalized objective equation. The exact label orientations must be `(0,1)` and `(1,0)` or another explicitly proved set; no phrase may call both labels nonzero. An independent reader must recompute the 5-cost witness and the public solver must implement the same equation without a hidden offset.

### ACG-OR5-002 - Aggregate-only exact and runtime evidence

**Open rows:** AC-F23, AC-E06-E09, AC-E11-E17, AC-T04, AC-A04-A07.

**Resolution test.** Add raw case/row records, the separate referee or a genuinely implementation-independent checker, exact generators, environment/specification, and deterministic aggregators. Clean extraction must reconstruct every public number and fail under deliberate corruption. Otherwise remove or narrow every claim not reproducible from the released material.

### ACG-OR5-003 - Availability statement overclaims archive contents

**Open rows:** AC-A02, AC-A04-A07, AC-S06.

**Resolution test.** Reconcile the availability paragraph line by line against the final archive. Each named object must exist under a reader-facing name and each reproduction instruction must execute in a clean documented environment. Do not call static summary inspection reproduction.

### ACG-OR5-004 - Literature entailment and search coverage not independently assessable

**Open rows:** AC-L01-L09 and AC-L11.

**Resolution test.** Provide a dated search boundary and proposition-level source-entailment table with locators for each comparison. Re-run an independent source audit before editor closure; preserve the bounded “not located” wording.

### ACG-OR5-005 - Reviewer-surface leakage and metadata

**Open rows:** AC-T05, AC-A11, AC-S03-S05, AC-S08.

**Resolution test.** Regenerate the anonymous archive with neutral scientific terminology and no public digest list or private development lineage. Translate “authorized conclusion,” “production raw cost,” and “release decisions” into scientific statements. Recursively scan PDF, source, archive entry names, and payloads for internal identifiers/history and require zero hits. Embed correct anonymity-safe PDF metadata and reconcile author number.

### ACG-OR5-006 - Exact source/PDF build binding not independently demonstrated

**Open row:** AC-S06.

**Resolution test.** Supply the engine/version, build command, required bibliography pass, and deterministic or semantic binding receipt. A clean environment must build a seven-page PDF with identical extracted text, equations, table, references, and page-level visual result; bind the final bytes privately.

## Coverage conclusion

The independent pass did **not** find a counterexample to the support-two theorem. The correction lemma, zero-sum lemma, support-reduction proof, pair count, complexity upper bound, displayed support-two witness, and support-one minimum 6 all survived independent checking within the stated mathematical model.

The frozen manuscript nevertheless cannot receive a verification-complete release status from this pass. Non-closing items remain in the grammar definition, separate-referee and runtime evidence, availability claims, literature entailment/search coverage, reviewer-surface hygiene, human declarations, PDF metadata, and source-to-PDF build binding. The cheapest valid path is exact formalization, public-artifact reconstruction, and claim-accurate narrowing where evidence cannot be released. No new favorable performance experiment is required, and the adverse timeout result must remain visible.
