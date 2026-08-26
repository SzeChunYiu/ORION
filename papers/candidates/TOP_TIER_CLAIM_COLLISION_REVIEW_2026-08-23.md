# Top-tier claim collision review — ORION-16–ORION-25

**Programme:** #977 (workstream W3)  
**Branch:** `claude/top-tier-claim-collision-20260823`  
**Date:** 2026-08-23  
**Scope:** the ten top-tier promotion objects ORION-16–ORION-25, at the claim scope of each `TOP_TIER_PROMOTION_V1.md` post-outcome status (2026-08-23). ORION-11–ORION-15 cross-boundaries are reviewed in §4 because three queued collisions reach into the existing portfolio.  
**Method:** every pair of one-sentence maximum claims was adjudicated into exactly one of `NONE` / `BORROWS-UPWARD` / `COLLIDES`. For every `COLLIDES` pair this review records the exact sentence-level collision and the fix as a boundary sharpening or a hierarchy statement (who owns which abstraction level). No fix narrows a claim: the lower paper is always cited as donor, never absorbed silently.

## 1. Vocabulary keys used per paper

- **ORION-16** — transition admissibility: `(computational support, evidence meaning, obligation, authority/commit)` preservation/reopen; composition under epoch/scope transport; erasure non-full-abstraction.
- **ORION-17** — regime transport: support/closure/obligation transport across representation/ontology/objective/world change; witness composition; open/censored boundary.
- **ORION-18** — scientific authorization: action-authorization ≠ scientific-commitment authorization; full-type coercion; support-family revocation.
- **ORION-19** — failure attribution: `Q = f(I, A, C, M)`; one-coordinate causal diagnostic (information/accessibility/computation); crossover surfaces.
- **ORION-20** — OCME: obstruction-certified method-language expansion; outside-closure edit; held-out transfer.
- **ORION-21** — computational placement: compile/cache/retain-raw/materialize trade-off; optionality law; no-answer-laundering.
- **ORION-22** — resource-location metareasoning: online marginal allocation across state/reasoning/verifier/recovery loci.
- **ORION-23** — responsibility-scoped sufficiency: reuse certificates, transport/revocation under responsibility/semantic change.
- **ORION-24** — governance as research-decision machine: false-novelty/widening reduction under matched capability.
- **ORION-25** — SEI: execution-provenance ladder `ATTRIBUTABLE != REPLAYABLE != AGREEMENT != VALID != AUTHORIZED`.

## 2. Pairwise matrix (upper triangle, 45 pairs)

Legend: `N` = NONE, `B` = BORROWS-UPWARD (lower paper must be cited as donor), `C` = COLLIDES (sentence-level collision; fix required).

|      | ORION-17 | ORION-18 | ORION-19 | ORION-20 | ORION-21 | ORION-22 | ORION-23 | ORION-24 | ORION-25 |
|------|----|----|----|-----|-----|-----|-----|-----|-----|
| ORION-16   | C1 | C2 | N  | N†  | N   | N   | B✓  | N†  | C3  |
| ORION-17   |    | N† | N  | N   | N   | B   | C4  | N†  | N   |
| ORION-18   |    |    | N  | N   | C5  | N   | C6  | C7  | C8  |
| ORION-19   |    |    |    | B✓  | C9  | C10 | N   | N   | N   |
| ORION-20  |    |    |    |     | N†  | N†  | N   | N   | B   |
| ORION-21  |    |    |    |     |     | C11 | C12 | N   | N   |
| ORION-22  |    |    |    |     |     |     | B   | N   | N   |
| ORION-23  |    |    |    |     |     |     |     | N   | B   |
| ORION-24  |    |    |    |     |     |     |     |     | C13 |

`B✓` = borrowing relation already declared in the lower/upper paper's own promotion doc. `N†` = no collision at current claim scope, but a boundary sentence is mandatory (§5). Bare `B` = borrowing required by claim structure but not yet declared (§3 fixes it).

## 3. COLLIDES pairs — sentence-level collision and fix

### C1. ORION-16 ↔ ORION-17 — transport composition

- **Collision.** ORION-16: *"a transition must additionally preserve or explicitly reopen typed evidence meaning… these requirements **compose under explicit transport conditions**"* (T6.2: composition succeeds under matching epoch/scope and fails on mismatch). ORION-17: *"ORION-17 characterizes the witnesses required to preserve, revoke or reopen evidence/obligations across regime changes and **composes those witnesses across sequential changes**"* (T7.2 sequential transport).
  Both papers claim ownership of composing preservation semantics across sequential changes; a referee can read ORION-17's sequential witness composition as ORION-16's T6.2 re-instantiated on regime changes.
- **Fix (hierarchy).** ORION-16 owns **transition-level transport**: composing admissibility certificates across adjacent transitions `A→B→C` within one fixed semantic regime, where epoch/scope tokens match or mismatch. ORION-17 owns **regime-level transport**: whether support survives when the representation/ontology/world model itself changes, i.e. when the token vocabulary in which ORION-16's epoch/scope conditions are written is replaced. ORION-17's witnesses therefore take ORION-16 certificates as typed inputs that may become uninterpretable; ORION-17 must cite ORION-16 as donor for the certificate layer and state that ORION-16's matching conditions are intra-regime. Neither paper narrows; the abstraction levels are made explicit.

### C2. ORION-16 ↔ ORION-18 — authority/commit factor

- **Collision.** ORION-16 factors a transition as `(computational support, evidence meaning, scientific obligation, authority/commit)` and requires authority preservation or explicit reopen. ORION-18: *"scientific authorization is a distinct decision layer from action authorization"* with typed evidence-to-obligation discharge. The authority coordinate of ORION-16's T6.1 and ORION-18's entire object are the same abstraction level as written — ORION-16's fourth factor silently re-owns ORION-18's decision layer.
- **Fix (hierarchy).** ORION-18 owns **the authorization semantics** (what discharges an obligation into an authorized commitment; coercion/revocation typing). ORION-16 owns **transition admissibility given an authorization state**: ORION-16's fourth factor must be re-worded as "authority/commit status as defined by the ORION-18 layer (frozen upstream donor), preserved or explicitly reopened by the transition". ORION-16's promotion doc already lists ORION-11/ORION-14/ORION-18 as frozen upstream donors for its baseline; the manuscript must extend that declaration to the factor definition itself.

### C3. ORION-16 ↔ ORION-25 — the authorized-claim rung

- **Collision.** ORION-25's separation ladder terminates in `SCIENTIFICALLY_VALID_RESULT != AUTHORIZED_SCIENTIFIC_CLAIM` and ORION-25's checker adjudicates "false authorized science" counts. ORION-16's transition object ends in commit authority. Both papers adjudicate when an authorized scientific state exists; ORION-25's hostile corpus contains authorization-laundering cases (3 in ORION-16's corpus too — same vocabulary, different corpora).
- **Fix (hierarchy + vocabulary).** ORION-25 owns **execution-integrity evidence** up to the boundary it itself proves: provenance/replay/agreement never establish validity or authorization. ORION-16/ORION-18 (per C2) own the semantics of the two top rungs. ORION-25's checker must treat `AUTHORIZED_SCIENTIFIC_CLAIM` as an externally supplied frozen disposition type (donor-owned by ORION-16/ORION-18), not as a semantics ORION-25 defines; its gold dispositions then test only whether execution evidence is *conflated with* authorization. One citation sentence in ORION-25's ladder section closes this.

### C4. ORION-17 ↔ ORION-23 — coarsening/responsibility invalidation

- **Collision.** ORION-17 (wine domain): *"fine labels {0,1,2} are coarsened to class0_vs_other; reversing coarse class 0 is non-injective"* — support does not transport under ontology refinement. ORION-23 (digits domain): *"a compact state… learned for parity responsibility is then confronted with the stronger exact-digit responsibility"* — the certificate is revoked under responsibility upgrade. Both claims are "the old state was adequate, the derived question changed, and value-only reuse is unsafe", instantiated on UCI tabular/handwritten coarsening-style changes. A referee can read ORION-23's responsibility upgrade as ORION-17's regime change with new vocabulary.
- **Fix (boundary sharpening).** ORION-17 owns **mapping-level transport**: the representation/ontology map changed (fine→coarse), so retained *evidence* loses invertibility; the object is the transport witness across the changed map. ORION-23 owns **query-level sufficiency**: the representation is unchanged, the *demanded responsibility* over it is strengthened, so retained *state* loses sufficiency; the object is the reuse certificate and its revocation. ORION-23's T13.2 already declares composition with ORION-16/ORION-17/ORION-18 through frozen interfaces; the manuscript must additionally state that ORION-17's wine coarsening and ORION-23's digits upgrade are dual (map-changes-under-fixed-question vs question-changes-under-fixed-map) and cite ORION-17 as the donor of the transport-witness machinery.

### C5. ORION-18 ↔ ORION-21 — "laundering"

- **Collision.** Vocabulary-level. ORION-21 T11.2: *"no-answer-laundering"* — compiled state must be informative without trivially encoding the protected answer. ORION-18: authority laundering — a valid judgment in one layer misused as authorization in another. Both papers sell a "laundering" separator; a referee reading both abstracts sees one mechanism claimed twice.
- **Fix (boundary sharpening).** ORION-18 owns *authority laundering* (decision-layer confusion). ORION-21's object is *answer-content leakage* (information hiding in compilation). Rename ORION-21's condition to "no answer-content leakage (no-laundering of the protected target into compiled state)" with one clause citing ORION-18's distinct decision-layer notion. No claim changes on either side.

### C6. ORION-18 ↔ ORION-23 — revocation preserving independent support

- **Collision.** ORION-18 T8.3: *"revoking source A preserves an independent derivation d2, while revoking A+B removes all surviving registered support."* ORION-23: transport/revocation of reuse certificates under responsibility/epoch change, with reopen semantics. Both own "targeted revocation must not destroy independently derived support".
- **Fix (hierarchy).** ORION-18 owns **support-family revocation inside a fixed regime** (source-level, authorization semantics). ORION-23 owns **certificate revocation under responsibility/semantic change** (what the state is now sufficient for). ORION-23's CNF clause/epoch change is exactly the ORION-18-fixed-regime boundary being crossed; ORION-23's manuscript must cite ORION-18 for the within-regime revocation semantics it extends and keep its residual the responsibility-indexed part (its T13.2 declaration already points this way — make the citation explicit).

### C7. ORION-18 ↔ ORION-24 — who authorizes research claims

- **Collision.** ORION-24: governance *"reduces false novelty and unsupported claim widening"* — a decision process over claim promotion. ORION-18: typed discharge determines when a scientific commitment is authorized. Both are "the layer that stops unsupported scientific claims"; ORION-24's disposition vocabulary (promote/subsume/reopen/CANNOT_CHECK) overlaps ORION-18's terminal states.
- **Fix (hierarchy).** ORION-18 owns **the typing/discharge semantics** (what evidence type authorizes what commitment). ORION-24 owns **the workflow/process claim** (that a fail-closed recursive governance process using such typing reduces false novelty/widening at matched capability without suppressing useful discovery). ORION-24's protocol must list ORION-16/ORION-17/ORION-18 disposition semantics as frozen upstream donors in its packet/adjudication design, and its headline must remain process-superiority, not authorization-semantics novelty.

### C8. ORION-18 ↔ ORION-25 — see C3 (shared fix)

ORION-25's top two rungs are ORION-18-owned semantics consumed as frozen disposition types; ORION-18's empirical gate (three real scientific-decision domains) may reuse ORION-25's execution-integrity substrate as evidence plumbing but must not count ORION-25 corpus outcomes as its own protected evidence (paper-disjointness, §6).

### C9. ORION-19 ↔ ORION-21 — accessibility vs placement

- **Collision.** ORION-19: *"accessibility can change under an information-preserving representation intervention for a fixed access mechanism"* — coordinate `A` of `f(I,A,C,M)`. ORION-21: *"a representation is a computational placement decision"* — paying structural work at construction vs downstream access. Both explain "same semantic information, different downstream cost by representation choice"; ORION-21's compiled-vs-universal comparison on wine/digits and ORION-19's native-vs-cubic comparison on breast-cancer/wine/digits are structurally the same experimental shape.
- **Fix (hierarchy).** ORION-19 owns **the causal-diagnostic coordinate system and failure attribution** (which coordinate's intervention repairs failure, with protected causal gold). ORION-21 owns **the placement/optionality resource law** (when compile/cache/retain/materialize is resource-optimal over a future-query process). ORION-21 must phrase its near-universal-performance comparisons as movements of ORION-19's `A` coordinate under matched `I` and cite ORION-19 as donor for the coordinate; ORION-19 must not claim placement-optimality language (its gate already forbids universal representation-superiority language — extend that to placement).

### C10. ORION-19 ↔ ORION-22 — offline diagnosis vs online allocation

- **Collision.** ORION-19 causal diagnostic: *"predicts the lowest-cost intervention that reaches a frozen quality target"* (probe-time, one-coordinate). ORION-22: *"an adaptive policy should decide whether the next unit of resource is best spent on state construction…, downstream reasoning/search, verification/tool use, or recovery."* Both are "choose the cheapest effective intervention"; a referee can call ORION-22's allocator ORION-19's diagnostic made sequential.
- **Fix (boundary sharpening).** ORION-19 owns **ex-post causal attribution** (intervention-response diagnosis against protected gold, including its retained `CANNOT_CHECK` instability). ORION-22 owns **pre-outcome online marginal allocation under one envelope** (sequential, budget-charged, regret-bounded to an oracle allocator). ORION-22's generalized action set and ORION-19's intervention set share the state-vs-reasoning axis by construction: ORION-22 must cite ORION-19's diagnostic as the offline upper-information comparator (what an allocator could do with causal gold it must not have), and ORION-19's manuscript must state its diagnostic is not an online policy.

### C11. ORION-21 ↔ ORION-22 — placement law vs location policy

- **Collision.** ORION-21 phase-diagram target: *"freeze query horizon, overlap/diversity, drift and memory/compute grids; predict the best state policy before protected evaluation."* ORION-22: the resource-location decision rule with the same state-vs-reasoning locus axis, also predicting allocation from a pre-outcome signal (ORION-22's path-study allocator selects REASON_ONLY vs STATE_FIRST from query count — which is ORION-21's query-horizon parameter).
- **Fix (hierarchy).** ORION-21 owns **the design-time crossover law** (over a future-query process distribution: horizon/diversity/drift → best state policy). ORION-22 owns **the runtime marginal rule** (allocate the next unit online, charged in the programme resource vector, with oracle-regret semantics). ORION-22's query-count signal is ORION-21's horizon parameter observed online; ORION-22 must cite ORION-21's optionality law as the offline analysis layer it partially observes, and ORION-21's phase-diagram claims must not be stated as runtime policies. The two papers' receipts currently use disjoint corpora (SAT/path vs wine/digits compilers) — keep that disjointness when either adds a domain.

### C12. ORION-21 ↔ ORION-23 — optionality vs reuse safety

- **Collision.** ORION-21 optionality law: when to *"retain reversible raw+summary state"* because future-query diversity makes raw retention optimal. ORION-23: reuse of compact state is safe only under responsibility certificates, with reopen conditions and recovery cost. Both decide "keep raw state or not" and both price recovery/reconstruction; ORION-21's `R` vector and ORION-23's resource-saved-vs-always-raw endpoint overlap directly.
- **Fix (hierarchy).** ORION-21 owns **the resource/optionality trade-off** (expected future utility of retained optionality vs carrying cost, responsibility-agnostic). ORION-23 owns **the sufficiency/safety contract** (which responsibilities certify reuse; unsafe-reuse rate is the non-compensatory endpoint). ORION-23's unnecessary-reopen rate is exactly ORION-21's optionality coordinate evaluated at the certificate level: ORION-23 must cite ORION-21 for the recovery/optionality costing and keep its residual the responsibility-scoped contract; ORION-21 must not imply its optionality law certifies *safety* of reuse (only its cost-optimality).

### C13. ORION-24 ↔ ORION-25 — governance vs integrity evidence

- **Collision.** ORION-24 adjudicates final allowed claims (scientific admission decisions). ORION-25's ladder terminates in validity/authorization rungs that its receipts label (e.g. its real-receipt set includes an "authoritative negative" and a `CANNOT_CHECK` scientific claim). Both papers surface "what counts as admitted science" to the reader; ORION-25's disposition columns (false authorized science) read like ORION-24's outcome metrics.
- **Fix (hierarchy).** ORION-25 owns **execution-integrity evidence and its non-implication ladder**; it records dispositions, it does not *decide* them. ORION-24 owns **the decision-process claim** that governance changes those decisions for the better. ORION-25's manuscript must state that every scientific disposition in its receipts is an imported frozen judgment (donor-owned by the ORION-24/ORION-18 layer or by deterministic contracts), never an output of the provenance layer; ORION-24's benchmark must consume ORION-25-class receipts as evidence packets without re-owning execution semantics. This makes the ORION-24/ORION-25 pair the top of the §6 ladder: decide (ORION-24) on evidence that is bound-but-distinct (ORION-25), with typing from ORION-18.

## 4. ORION-11–ORION-15 cross-boundary collisions (outside the 10×10 matrix)

Three queued collisions reach the existing portfolio. The `P1_P5_OWNERSHIP_MATRIX_V1` dispositions remain binding; this review restates them as manuscript obligations at top-tier scope.

- **ORION-16 ↔ ORION-11 — selective reopening.** ORION-16's "explicitly reopen typed evidence meaning and outstanding obligations" is ORION-11's dependency-directed reopening after material reframe when instantiated on ORION's own reconstruction lane. Fix (already dispositioned `MERGE_EXISTING` for the native case): ORION-16's manuscript must present ORION-11 as the frozen upstream donor that embeds conservatively, and claim only the donor-faithful cross-mechanic transition algebra (its T6.1–T6.3 closure over heterogeneous, non-ORION-11 transition families). ORION-16's three executed families are already non-ORION-11 — keep that disjointness explicit.
- **ORION-17 ↔ ORION-12 — stopping.** ORION-17's "retaining honest open/censored stopping" and T7.3's 0.5 observed-only boundary sit directly on ORION-12's route-vs-task stopping and fail-closed coverage. Fix: ORION-17 uses ORION-12's stopping semantics as a frozen invariant across chart changes and owns only the transport claim; ORION-12 is cited as donor in T7.3.
- **ORION-18 ↔ ORION-14 — evidence and promotion.** ORION-18's evidence-to-obligation discharge overlaps ORION-14's content-bound evidence, protected-evaluator identity and non-escalating promotion (ownership matrix: all five within-domain gates `MERGE_EXISTING`). Fix: ORION-18's residual is the cross-domain typed coercion calculus and authority-laundering composition only; ORION-14 remains the owner of within-scientific-assertion authority, cited as donor.
- **ORION-23/ORION-25 ↔ ORION-13/ORION-15 (no collision, declaration only).** ORION-23's provenance-only comparator and ORION-25's provenance interop draw on ORION-13's provenance-preserving projections; ORION-25's no-self-certification and ORION-24's authority separation draw on ORION-15's evaluator-custody rules. One citation sentence each; no boundary dispute exists.

## 5. BORROWS-UPWARD registry (declared ✓ / must-declare ✗)

| Upper | Lower (donor) | Status | Required edit |
|---|---|---|---|
| ORION-16 | ORION-11, ORION-14, ORION-18 | ✓ declared (baseline donors) | extend declaration from baseline to the T6.1 factor definitions (C2) |
| ORION-17 | ORION-12 (stopping), ORION-16 (certificates) | ✗ / ✗ | add donor citations in T7.2–T7.3 (C1, §4) |
| ORION-18 | ORION-14 (within-domain authority) | ✗ | manuscript states the five ORION-11–ORION-15 gates as frozen upstream (§4) |
| ORION-19 | — | ✓ | none (ORION-19 is a coordinate donor to others, not a borrower) |
| ORION-20 | ORION-19 (representation repair as refused donor) | ✓ declared in comparator stack | keep at manuscript scope; add the ladder sentence (§7) |
| ORION-21 | ORION-19 (accessibility coordinate) | ✗ | C9 fix |
| ORION-22 | ORION-19 (offline diagnostic ceiling), ORION-21 (optionality law), ORION-23 (reopen action), ORION-17 (regime-change action) | ✗ all four | C10/C11 fixes + declare the reopen-after-unsupported-responsibility and regime-change actions as ORION-23/ORION-17-owned semantics consumed through frozen interfaces |
| ORION-23 | ORION-16/ORION-17/ORION-18 (frozen interfaces) | ✓ declared in T13.2 | make the ORION-17/ORION-18 citations explicit in the manuscript (C4/C6) |
| ORION-24 | ORION-16/ORION-17/ORION-18 (disposition semantics), ORION-15 (authority separation) | ✗ | C7 fix |
| ORION-25 | ORION-18 (authorization typing), ORION-24 (admission decisions), ORION-13 (provenance projections) | ✗ | C3/C13 fixes |

## 6. Undeclared load-bearing evidence flags

These are places where one paper's earned evidence is implicitly load-bearing for another paper's claim without being declared a frozen upstream input. Each is a defect against the programme's no-silent-leakage rule, not a claim collision.

1. **ORION-25's `AUTHORIZED_SCIENTIFIC_CLAIM`/`SCIENTIFICALLY_VALID` gold dispositions** are ORION-18/ORION-24-class judgments. Currently they exist only as frozen gold inside ORION-25's own protocol. They are load-bearing for ORION-18's future external gate and ORION-24's adjudication design. Fix: ORION-25's protocol already binds them; ORION-18/ORION-24 promotion docs must add "ORION-25 SEI receipts admissible as execution-evidence substrate, dispositions imported as frozen inputs" so the dependency direction is visible from both ends.
2. **ORION-22's reopen/recovery actions** (its generalized action set) execute ORION-23's reopen semantics and ORION-17's regime-change semantics without citation. If ORION-22's final headline keeps those actions, ORION-23/ORION-17 become upstream donors; if the headline drops them, remove the actions rather than leave them uncited.
3. **ORION-19's Qwen arm name `R2_TYPED_STATE`** implies typed-state semantics from the ORION-21/ORION-23 family. ORION-19's negative result is about a structured-state representation, not about typed/responsibility-carrying state. Rename to `R2_STRUCTURED_STATE` in any manuscript use (analysis artifacts stay frozen under their original names).
4. **Shared datasets across protected cells.** Wine is a protected domain in ORION-17 (712 transport rows), ORION-19 (null accessibility cell) and ORION-21 (compiler positive cell); digits in ORION-19 (cubic + `D-A` diagnostic), ORION-21 (64→32 compiler) and ORION-23 (parity→exact-digit, 17,970 episodes). The frozen outcomes are different objects, so paper-disjointness technically holds (programme §4 allows shared infrastructure), but each paper must state the disjointness explicitly — which frozen quantity is whose — or a referee will read one dataset as generating three papers' evidence. ORION-23's parity responsibility and ORION-21's T11.2 parity witnesses use the same protected target family (parity on the same feature space); declare that the ORION-23 episodes and the ORION-21 checker witnesses are separately frozen corpora with no shared protected outcomes.
5. **ORION-20's two-checker formal result appears inside ORION-25's real-receipt set.** If that receipt is a ORION-20 artifact, ORION-25's interop study consumes ORION-20's earned evidence as a real-world input. This is exactly the pattern §4 permits, but the ORION-25 protocol must name the source paper of each real receipt so the dependency is auditable.

## 7. Portfolio unification (programme §6, sharpened)

The ten papers decompose one object — auditable adaptive scientific intelligence — into ten non-overlapping decision boundaries. Read as a ladder:

- **What may change:** ORION-16 decides transition admissibility; ORION-17 decides transport across regime change; ORION-20 decides when the method language itself must expand.
- **What may be claimed:** ORION-18 owns authorization typing; ORION-24 owns the governance process that turns typing into research decisions; ORION-25 owns the execution evidence those decisions consume and its non-implication ladder.
- **Where resource goes:** ORION-19 attributes failure to information/accessibility/computation; ORION-21 sets the design-time placement/optionality law; ORION-22 allocates the next unit online.
- **What may be reused:** ORION-23 owns responsibility-scoped sufficiency between construction and reuse.

Each level cites the level below as donor; no level re-owns a lower mechanism. The unification sentence admissible today: *state changes, regime changes, authorization, diagnosis, placement, allocation, reuse, governance and execution integrity are separable decision layers with demonstrated bounded separators, and the portfolio supplies one owner per layer.* Nothing stronger is currently earned portfolio-wide (ORION-24's external result and the native ORION-20 bridge remain open).

## 8. Sibling-leakage referee register (programme §3.G)

Pre-armed responses for the leakage attack each paper must carry:

- *"ORION-17 is ORION-16's composition theorem on regime instances"* → C1: intra-regime certificate composition vs vocabulary replacement; ORION-17 cites ORION-16.
- *"ORION-23's revocation is ORION-18's T8.3 with new words"* → C6: fixed-regime support revocation vs responsibility-indexed certificate revocation; ORION-23 cites ORION-18.
- *"ORION-21's accessibility is ORION-19's A-coordinate"* → C9: coordinate system vs placement law; mutual citations.
- *"ORION-22's allocator is ORION-19's diagnostic made sequential"* → C10: ex-post causal gold vs pre-outcome regret-bounded allocation.
- *"ORION-22's allocator is ORION-21's phase diagram online"* → C11: design-time crossover law vs runtime marginal rule.
- *"ORION-19's intervention ladder is ORION-20's expansion rung"* → ladder statement: ORION-19 repairs access to a fixed method space; ORION-20 certifies that the method space itself is insufficient (ORION-20 already refuses ORION-19-repair as a donor in its Stage-1 list).
- *"ORION-21's compiled state is ORION-20's outside-closure edit"* → both must state: compilation stays within the registered method basis (`KNOWN_COMPOSITION` in ORION-20's terms); expansion changes the basis.
- *"ORION-24's governance is ORION-18's authorization"* → C7: typing vs process superiority under matched capability.
- *"ORION-25's ladder decides admissions"* → C13: records dispositions, never decides them.
- *"ORION-16/ORION-17/ORION-18 re-own ORION-11/ORION-12/ORION-14"* → §4: conservative-embedding declarations, residuals only.
- *"three papers drink from one wine/digits well"* → §6.4: per-paper frozen-quantity declarations.

## 9. Required manuscript edits (per paper, minimal set)

- **ORION-16:** re-word T6.1's fourth factor as ORION-18-owned status consumed as frozen input (C2); extend the ORION-11/ORION-14/ORION-18 donor declaration from the baseline to the factor definitions; keep C1's intra-regime scoping sentence in T6.2.
- **ORION-17:** add ORION-16 certificate-donor citation (C1), ORION-12 stopping citation (§4), and the dual-to-ORION-23 boundary sentence (C4).
- **ORION-18:** add the five-gate `MERGE_EXISTING` statement with ORION-14 cited (§4); declare ORION-25 receipts as admissible evidence substrate (§6.1).
- **ORION-19:** rename `R2_TYPED_STATE` in prose (§6.3); add "not an online policy, not a placement law" scoping (C9/C10).
- **ORION-20:** add the ORION-19-rung ladder sentence (§7) and the ORION-21-compilation `KNOWN_COMPOSITION` note (§8).
- **ORION-21:** phrase near-universal-performance comparisons through ORION-19's `A` coordinate with citation (C9); rename the laundering condition to answer-content leakage with ORION-18 citation (C5); add "optionality prices cost, not safety" scoping (C12).
- **ORION-22:** declare ORION-19/ORION-21/ORION-23/ORION-17 donor relations for its action set and allocator framing (C10/C11, §6.2).
- **ORION-23:** make ORION-17 duality and ORION-18 revocation citations explicit (C4/C6); cite ORION-21 for recovery/optionality costing (C12); add the parity-corpus disjointness declaration (§6.4).
- **ORION-24:** list ORION-16/ORION-17/ORION-18/ORION-15 frozen upstream donors in the adjudication design (C7); keep headline as process superiority.
- **ORION-25:** import dispositions as frozen external types with ORION-18/ORION-24 named (C3/C13); name the source paper of each real receipt (§6.5).

## 10. Terminal disposition

`COLLISION_REVIEW_V1_COMPLETE`: 45 pairs adjudicated — 13 `COLLIDES` (all with sentence-level fixes above), 6 `BORROWS-UPWARD` (2 already declared, 4 to declare), 26 `NONE` (of which 6 carry mandatory boundary sentences). No pair requires claim narrowing; every fix is a hierarchy statement or boundary sharpening with explicit donor citation. Three undeclared load-bearing evidence dependencies (ORION-25 gold dispositions, ORION-22 reopen actions, shared dataset framing) and one arm-name defect (`R2_TYPED_STATE`) are queued as manuscript edits in §9. This review does not promote or demote any paper; it is an input to each paper's final cross-paper ownership gate (`ORION-16/ORION-17/ORION-18` gates list it explicitly; `ORION-19–ORION-25` gates should add the same line at manuscript scope).
