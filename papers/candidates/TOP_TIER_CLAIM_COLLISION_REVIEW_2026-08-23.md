# Top-tier claim collision review — P6–P15

**Programme:** #977 (workstream W3)  
**Branch:** `claude/top-tier-claim-collision-20260823`  
**Date:** 2026-08-23  
**Scope:** the ten top-tier promotion objects P6–P15, at the claim scope of each `TOP_TIER_PROMOTION_V1.md` post-outcome status (2026-08-23). P1–P5 cross-boundaries are reviewed in §4 because three queued collisions reach into the existing portfolio.  
**Method:** every pair of one-sentence maximum claims was adjudicated into exactly one of `NONE` / `BORROWS-UPWARD` / `COLLIDES`. For every `COLLIDES` pair this review records the exact sentence-level collision and the fix as a boundary sharpening or a hierarchy statement (who owns which abstraction level). No fix narrows a claim: the lower paper is always cited as donor, never absorbed silently.

## 1. Vocabulary keys used per paper

- **P6** — transition admissibility: `(computational support, evidence meaning, obligation, authority/commit)` preservation/reopen; composition under epoch/scope transport; erasure non-full-abstraction.
- **P7** — regime transport: support/closure/obligation transport across representation/ontology/objective/world change; witness composition; open/censored boundary.
- **P8** — scientific authorization: action-authorization ≠ scientific-commitment authorization; full-type coercion; support-family revocation.
- **P9** — failure attribution: `Q = f(I, A, C, M)`; one-coordinate causal diagnostic (information/accessibility/computation); crossover surfaces.
- **P10** — OCME: obstruction-certified method-language expansion; outside-closure edit; held-out transfer.
- **P11** — computational placement: compile/cache/retain-raw/materialize trade-off; optionality law; no-answer-laundering.
- **P12** — resource-location metareasoning: online marginal allocation across state/reasoning/verifier/recovery loci.
- **P13** — responsibility-scoped sufficiency: reuse certificates, transport/revocation under responsibility/semantic change.
- **P14** — governance as research-decision machine: false-novelty/widening reduction under matched capability.
- **P15** — SEI: execution-provenance ladder `ATTRIBUTABLE != REPLAYABLE != AGREEMENT != VALID != AUTHORIZED`.

## 2. Pairwise matrix (upper triangle, 45 pairs)

Legend: `N` = NONE, `B` = BORROWS-UPWARD (lower paper must be cited as donor), `C` = COLLIDES (sentence-level collision; fix required).

|      | P7 | P8 | P9 | P10 | P11 | P12 | P13 | P14 | P15 |
|------|----|----|----|-----|-----|-----|-----|-----|-----|
| P6   | C1 | C2 | N  | N†  | N   | N   | B✓  | N†  | C3  |
| P7   |    | N† | N  | N   | N   | B   | C4  | N†  | N   |
| P8   |    |    | N  | N   | C5  | N   | C6  | C7  | C8  |
| P9   |    |    |    | B✓  | C9  | C10 | N   | N   | N   |
| P10  |    |    |    |     | N†  | N†  | N   | N   | B   |
| P11  |    |    |    |     |     | C11 | C12 | N   | N   |
| P12  |    |    |    |     |     |     | B   | N   | N   |
| P13  |    |    |    |     |     |     |     | N   | B   |
| P14  |    |    |    |     |     |     |     |     | C13 |

`B✓` = borrowing relation already declared in the lower/upper paper's own promotion doc. `N†` = no collision at current claim scope, but a boundary sentence is mandatory (§5). Bare `B` = borrowing required by claim structure but not yet declared (§3 fixes it).

## 3. COLLIDES pairs — sentence-level collision and fix

### C1. P6 ↔ P7 — transport composition

- **Collision.** P6: *"a transition must additionally preserve or explicitly reopen typed evidence meaning… these requirements **compose under explicit transport conditions**"* (T6.2: composition succeeds under matching epoch/scope and fails on mismatch). P7: *"P7 characterizes the witnesses required to preserve, revoke or reopen evidence/obligations across regime changes and **composes those witnesses across sequential changes**"* (T7.2 sequential transport).
  Both papers claim ownership of composing preservation semantics across sequential changes; a referee can read P7's sequential witness composition as P6's T6.2 re-instantiated on regime changes.
- **Fix (hierarchy).** P6 owns **transition-level transport**: composing admissibility certificates across adjacent transitions `A→B→C` within one fixed semantic regime, where epoch/scope tokens match or mismatch. P7 owns **regime-level transport**: whether support survives when the representation/ontology/world model itself changes, i.e. when the token vocabulary in which P6's epoch/scope conditions are written is replaced. P7's witnesses therefore take P6 certificates as typed inputs that may become uninterpretable; P7 must cite P6 as donor for the certificate layer and state that P6's matching conditions are intra-regime. Neither paper narrows; the abstraction levels are made explicit.

### C2. P6 ↔ P8 — authority/commit factor

- **Collision.** P6 factors a transition as `(computational support, evidence meaning, scientific obligation, authority/commit)` and requires authority preservation or explicit reopen. P8: *"scientific authorization is a distinct decision layer from action authorization"* with typed evidence-to-obligation discharge. The authority coordinate of P6's T6.1 and P8's entire object are the same abstraction level as written — P6's fourth factor silently re-owns P8's decision layer.
- **Fix (hierarchy).** P8 owns **the authorization semantics** (what discharges an obligation into an authorized commitment; coercion/revocation typing). P6 owns **transition admissibility given an authorization state**: P6's fourth factor must be re-worded as "authority/commit status as defined by the P8 layer (frozen upstream donor), preserved or explicitly reopened by the transition". P6's promotion doc already lists P1/P4/P8 as frozen upstream donors for its baseline; the manuscript must extend that declaration to the factor definition itself.

### C3. P6 ↔ P15 — the authorized-claim rung

- **Collision.** P15's separation ladder terminates in `SCIENTIFICALLY_VALID_RESULT != AUTHORIZED_SCIENTIFIC_CLAIM` and P15's checker adjudicates "false authorized science" counts. P6's transition object ends in commit authority. Both papers adjudicate when an authorized scientific state exists; P15's hostile corpus contains authorization-laundering cases (3 in P6's corpus too — same vocabulary, different corpora).
- **Fix (hierarchy + vocabulary).** P15 owns **execution-integrity evidence** up to the boundary it itself proves: provenance/replay/agreement never establish validity or authorization. P6/P8 (per C2) own the semantics of the two top rungs. P15's checker must treat `AUTHORIZED_SCIENTIFIC_CLAIM` as an externally supplied frozen disposition type (donor-owned by P6/P8), not as a semantics P15 defines; its gold dispositions then test only whether execution evidence is *conflated with* authorization. One citation sentence in P15's ladder section closes this.

### C4. P7 ↔ P13 — coarsening/responsibility invalidation

- **Collision.** P7 (wine domain): *"fine labels {0,1,2} are coarsened to class0_vs_other; reversing coarse class 0 is non-injective"* — support does not transport under ontology refinement. P13 (digits domain): *"a compact state… learned for parity responsibility is then confronted with the stronger exact-digit responsibility"* — the certificate is revoked under responsibility upgrade. Both claims are "the old state was adequate, the derived question changed, and value-only reuse is unsafe", instantiated on UCI tabular/handwritten coarsening-style changes. A referee can read P13's responsibility upgrade as P7's regime change with new vocabulary.
- **Fix (boundary sharpening).** P7 owns **mapping-level transport**: the representation/ontology map changed (fine→coarse), so retained *evidence* loses invertibility; the object is the transport witness across the changed map. P13 owns **query-level sufficiency**: the representation is unchanged, the *demanded responsibility* over it is strengthened, so retained *state* loses sufficiency; the object is the reuse certificate and its revocation. P13's T13.2 already declares composition with P6/P7/P8 through frozen interfaces; the manuscript must additionally state that P7's wine coarsening and P13's digits upgrade are dual (map-changes-under-fixed-question vs question-changes-under-fixed-map) and cite P7 as the donor of the transport-witness machinery.

### C5. P8 ↔ P11 — "laundering"

- **Collision.** Vocabulary-level. P11 T11.2: *"no-answer-laundering"* — compiled state must be informative without trivially encoding the protected answer. P8: authority laundering — a valid judgment in one layer misused as authorization in another. Both papers sell a "laundering" separator; a referee reading both abstracts sees one mechanism claimed twice.
- **Fix (boundary sharpening).** P8 owns *authority laundering* (decision-layer confusion). P11's object is *answer-content leakage* (information hiding in compilation). Rename P11's condition to "no answer-content leakage (no-laundering of the protected target into compiled state)" with one clause citing P8's distinct decision-layer notion. No claim changes on either side.

### C6. P8 ↔ P13 — revocation preserving independent support

- **Collision.** P8 T8.3: *"revoking source A preserves an independent derivation d2, while revoking A+B removes all surviving registered support."* P13: transport/revocation of reuse certificates under responsibility/epoch change, with reopen semantics. Both own "targeted revocation must not destroy independently derived support".
- **Fix (hierarchy).** P8 owns **support-family revocation inside a fixed regime** (source-level, authorization semantics). P13 owns **certificate revocation under responsibility/semantic change** (what the state is now sufficient for). P13's CNF clause/epoch change is exactly the P8-fixed-regime boundary being crossed; P13's manuscript must cite P8 for the within-regime revocation semantics it extends and keep its residual the responsibility-indexed part (its T13.2 declaration already points this way — make the citation explicit).

### C7. P8 ↔ P14 — who authorizes research claims

- **Collision.** P14: governance *"reduces false novelty and unsupported claim widening"* — a decision process over claim promotion. P8: typed discharge determines when a scientific commitment is authorized. Both are "the layer that stops unsupported scientific claims"; P14's disposition vocabulary (promote/subsume/reopen/CANNOT_CHECK) overlaps P8's terminal states.
- **Fix (hierarchy).** P8 owns **the typing/discharge semantics** (what evidence type authorizes what commitment). P14 owns **the workflow/process claim** (that a fail-closed recursive governance process using such typing reduces false novelty/widening at matched capability without suppressing useful discovery). P14's protocol must list P6/P7/P8 disposition semantics as frozen upstream donors in its packet/adjudication design, and its headline must remain process-superiority, not authorization-semantics novelty.

### C8. P8 ↔ P15 — see C3 (shared fix)

P15's top two rungs are P8-owned semantics consumed as frozen disposition types; P8's empirical gate (three real scientific-decision domains) may reuse P15's execution-integrity substrate as evidence plumbing but must not count P15 corpus outcomes as its own protected evidence (paper-disjointness, §6).

### C9. P9 ↔ P11 — accessibility vs placement

- **Collision.** P9: *"accessibility can change under an information-preserving representation intervention for a fixed access mechanism"* — coordinate `A` of `f(I,A,C,M)`. P11: *"a representation is a computational placement decision"* — paying structural work at construction vs downstream access. Both explain "same semantic information, different downstream cost by representation choice"; P11's compiled-vs-universal comparison on wine/digits and P9's native-vs-cubic comparison on breast-cancer/wine/digits are structurally the same experimental shape.
- **Fix (hierarchy).** P9 owns **the causal-diagnostic coordinate system and failure attribution** (which coordinate's intervention repairs failure, with protected causal gold). P11 owns **the placement/optionality resource law** (when compile/cache/retain/materialize is resource-optimal over a future-query process). P11 must phrase its near-universal-performance comparisons as movements of P9's `A` coordinate under matched `I` and cite P9 as donor for the coordinate; P9 must not claim placement-optimality language (its gate already forbids universal representation-superiority language — extend that to placement).

### C10. P9 ↔ P12 — offline diagnosis vs online allocation

- **Collision.** P9 causal diagnostic: *"predicts the lowest-cost intervention that reaches a frozen quality target"* (probe-time, one-coordinate). P12: *"an adaptive policy should decide whether the next unit of resource is best spent on state construction…, downstream reasoning/search, verification/tool use, or recovery."* Both are "choose the cheapest effective intervention"; a referee can call P12's allocator P9's diagnostic made sequential.
- **Fix (boundary sharpening).** P9 owns **ex-post causal attribution** (intervention-response diagnosis against protected gold, including its retained `CANNOT_CHECK` instability). P12 owns **pre-outcome online marginal allocation under one envelope** (sequential, budget-charged, regret-bounded to an oracle allocator). P12's generalized action set and P9's intervention set share the state-vs-reasoning axis by construction: P12 must cite P9's diagnostic as the offline upper-information comparator (what an allocator could do with causal gold it must not have), and P9's manuscript must state its diagnostic is not an online policy.

### C11. P11 ↔ P12 — placement law vs location policy

- **Collision.** P11 phase-diagram target: *"freeze query horizon, overlap/diversity, drift and memory/compute grids; predict the best state policy before protected evaluation."* P12: the resource-location decision rule with the same state-vs-reasoning locus axis, also predicting allocation from a pre-outcome signal (P12's path-study allocator selects REASON_ONLY vs STATE_FIRST from query count — which is P11's query-horizon parameter).
- **Fix (hierarchy).** P11 owns **the design-time crossover law** (over a future-query process distribution: horizon/diversity/drift → best state policy). P12 owns **the runtime marginal rule** (allocate the next unit online, charged in the programme resource vector, with oracle-regret semantics). P12's query-count signal is P11's horizon parameter observed online; P12 must cite P11's optionality law as the offline analysis layer it partially observes, and P11's phase-diagram claims must not be stated as runtime policies. The two papers' receipts currently use disjoint corpora (SAT/path vs wine/digits compilers) — keep that disjointness when either adds a domain.

### C12. P11 ↔ P13 — optionality vs reuse safety

- **Collision.** P11 optionality law: when to *"retain reversible raw+summary state"* because future-query diversity makes raw retention optimal. P13: reuse of compact state is safe only under responsibility certificates, with reopen conditions and recovery cost. Both decide "keep raw state or not" and both price recovery/reconstruction; P11's `R` vector and P13's resource-saved-vs-always-raw endpoint overlap directly.
- **Fix (hierarchy).** P11 owns **the resource/optionality trade-off** (expected future utility of retained optionality vs carrying cost, responsibility-agnostic). P13 owns **the sufficiency/safety contract** (which responsibilities certify reuse; unsafe-reuse rate is the non-compensatory endpoint). P13's unnecessary-reopen rate is exactly P11's optionality coordinate evaluated at the certificate level: P13 must cite P11 for the recovery/optionality costing and keep its residual the responsibility-scoped contract; P11 must not imply its optionality law certifies *safety* of reuse (only its cost-optimality).

### C13. P14 ↔ P15 — governance vs integrity evidence

- **Collision.** P14 adjudicates final allowed claims (scientific admission decisions). P15's ladder terminates in validity/authorization rungs that its receipts label (e.g. its real-receipt set includes an "authoritative negative" and a `CANNOT_CHECK` scientific claim). Both papers surface "what counts as admitted science" to the reader; P15's disposition columns (false authorized science) read like P14's outcome metrics.
- **Fix (hierarchy).** P15 owns **execution-integrity evidence and its non-implication ladder**; it records dispositions, it does not *decide* them. P14 owns **the decision-process claim** that governance changes those decisions for the better. P15's manuscript must state that every scientific disposition in its receipts is an imported frozen judgment (donor-owned by the P14/P8 layer or by deterministic contracts), never an output of the provenance layer; P14's benchmark must consume P15-class receipts as evidence packets without re-owning execution semantics. This makes the P14/P15 pair the top of the §6 ladder: decide (P14) on evidence that is bound-but-distinct (P15), with typing from P8.

## 4. P1–P5 cross-boundary collisions (outside the 10×10 matrix)

Three queued collisions reach the existing portfolio. The `P1_P5_OWNERSHIP_MATRIX_V1` dispositions remain binding; this review restates them as manuscript obligations at top-tier scope.

- **P6 ↔ P1 — selective reopening.** P6's "explicitly reopen typed evidence meaning and outstanding obligations" is P1's dependency-directed reopening after material reframe when instantiated on ORION's own reconstruction lane. Fix (already dispositioned `MERGE_EXISTING` for the native case): P6's manuscript must present P1 as the frozen upstream donor that embeds conservatively, and claim only the donor-faithful cross-mechanic transition algebra (its T6.1–T6.3 closure over heterogeneous, non-P1 transition families). P6's three executed families are already non-P1 — keep that disjointness explicit.
- **P7 ↔ P2 — stopping.** P7's "retaining honest open/censored stopping" and T7.3's 0.5 observed-only boundary sit directly on P2's route-vs-task stopping and fail-closed coverage. Fix: P7 uses P2's stopping semantics as a frozen invariant across chart changes and owns only the transport claim; P2 is cited as donor in T7.3.
- **P8 ↔ P4 — evidence and promotion.** P8's evidence-to-obligation discharge overlaps P4's content-bound evidence, protected-evaluator identity and non-escalating promotion (ownership matrix: all five within-domain gates `MERGE_EXISTING`). Fix: P8's residual is the cross-domain typed coercion calculus and authority-laundering composition only; P4 remains the owner of within-scientific-assertion authority, cited as donor.
- **P13/P15 ↔ P3/P5 (no collision, declaration only).** P13's provenance-only comparator and P15's provenance interop draw on P3's provenance-preserving projections; P15's no-self-certification and P14's authority separation draw on P5's evaluator-custody rules. One citation sentence each; no boundary dispute exists.

## 5. BORROWS-UPWARD registry (declared ✓ / must-declare ✗)

| Upper | Lower (donor) | Status | Required edit |
|---|---|---|---|
| P6 | P1, P4, P8 | ✓ declared (baseline donors) | extend declaration from baseline to the T6.1 factor definitions (C2) |
| P7 | P2 (stopping), P6 (certificates) | ✗ / ✗ | add donor citations in T7.2–T7.3 (C1, §4) |
| P8 | P4 (within-domain authority) | ✗ | manuscript states the five P1–P5 gates as frozen upstream (§4) |
| P9 | — | ✓ | none (P9 is a coordinate donor to others, not a borrower) |
| P10 | P9 (representation repair as refused donor) | ✓ declared in comparator stack | keep at manuscript scope; add the ladder sentence (§7) |
| P11 | P9 (accessibility coordinate) | ✗ | C9 fix |
| P12 | P9 (offline diagnostic ceiling), P11 (optionality law), P13 (reopen action), P7 (regime-change action) | ✗ all four | C10/C11 fixes + declare the reopen-after-unsupported-responsibility and regime-change actions as P13/P7-owned semantics consumed through frozen interfaces |
| P13 | P6/P7/P8 (frozen interfaces) | ✓ declared in T13.2 | make the P7/P8 citations explicit in the manuscript (C4/C6) |
| P14 | P6/P7/P8 (disposition semantics), P5 (authority separation) | ✗ | C7 fix |
| P15 | P8 (authorization typing), P14 (admission decisions), P3 (provenance projections) | ✗ | C3/C13 fixes |

## 6. Undeclared load-bearing evidence flags

These are places where one paper's earned evidence is implicitly load-bearing for another paper's claim without being declared a frozen upstream input. Each is a defect against the programme's no-silent-leakage rule, not a claim collision.

1. **P15's `AUTHORIZED_SCIENTIFIC_CLAIM`/`SCIENTIFICALLY_VALID` gold dispositions** are P8/P14-class judgments. Currently they exist only as frozen gold inside P15's own protocol. They are load-bearing for P8's future external gate and P14's adjudication design. Fix: P15's protocol already binds them; P8/P14 promotion docs must add "P15 SEI receipts admissible as execution-evidence substrate, dispositions imported as frozen inputs" so the dependency direction is visible from both ends.
2. **P12's reopen/recovery actions** (its generalized action set) execute P13's reopen semantics and P7's regime-change semantics without citation. If P12's final headline keeps those actions, P13/P7 become upstream donors; if the headline drops them, remove the actions rather than leave them uncited.
3. **P9's Qwen arm name `R2_TYPED_STATE`** implies typed-state semantics from the P11/P13 family. P9's negative result is about a structured-state representation, not about typed/responsibility-carrying state. Rename to `R2_STRUCTURED_STATE` in any manuscript use (analysis artifacts stay frozen under their original names).
4. **Shared datasets across protected cells.** Wine is a protected domain in P7 (712 transport rows), P9 (null accessibility cell) and P11 (compiler positive cell); digits in P9 (cubic + `D-A` diagnostic), P11 (64→32 compiler) and P13 (parity→exact-digit, 17,970 episodes). The frozen outcomes are different objects, so paper-disjointness technically holds (programme §4 allows shared infrastructure), but each paper must state the disjointness explicitly — which frozen quantity is whose — or a referee will read one dataset as generating three papers' evidence. P13's parity responsibility and P11's T11.2 parity witnesses use the same protected target family (parity on the same feature space); declare that the P13 episodes and the P11 checker witnesses are separately frozen corpora with no shared protected outcomes.
5. **P10's two-checker formal result appears inside P15's real-receipt set.** If that receipt is a P10 artifact, P15's interop study consumes P10's earned evidence as a real-world input. This is exactly the pattern §4 permits, but the P15 protocol must name the source paper of each real receipt so the dependency is auditable.

## 7. Portfolio unification (programme §6, sharpened)

The ten papers decompose one object — auditable adaptive scientific intelligence — into ten non-overlapping decision boundaries. Read as a ladder:

- **What may change:** P6 decides transition admissibility; P7 decides transport across regime change; P10 decides when the method language itself must expand.
- **What may be claimed:** P8 owns authorization typing; P14 owns the governance process that turns typing into research decisions; P15 owns the execution evidence those decisions consume and its non-implication ladder.
- **Where resource goes:** P9 attributes failure to information/accessibility/computation; P11 sets the design-time placement/optionality law; P12 allocates the next unit online.
- **What may be reused:** P13 owns responsibility-scoped sufficiency between construction and reuse.

Each level cites the level below as donor; no level re-owns a lower mechanism. The unification sentence admissible today: *state changes, regime changes, authorization, diagnosis, placement, allocation, reuse, governance and execution integrity are separable decision layers with demonstrated bounded separators, and the portfolio supplies one owner per layer.* Nothing stronger is currently earned portfolio-wide (P14's external result and the native P10 bridge remain open).

## 8. Sibling-leakage referee register (programme §3.G)

Pre-armed responses for the leakage attack each paper must carry:

- *"P7 is P6's composition theorem on regime instances"* → C1: intra-regime certificate composition vs vocabulary replacement; P7 cites P6.
- *"P13's revocation is P8's T8.3 with new words"* → C6: fixed-regime support revocation vs responsibility-indexed certificate revocation; P13 cites P8.
- *"P11's accessibility is P9's A-coordinate"* → C9: coordinate system vs placement law; mutual citations.
- *"P12's allocator is P9's diagnostic made sequential"* → C10: ex-post causal gold vs pre-outcome regret-bounded allocation.
- *"P12's allocator is P11's phase diagram online"* → C11: design-time crossover law vs runtime marginal rule.
- *"P9's intervention ladder is P10's expansion rung"* → ladder statement: P9 repairs access to a fixed method space; P10 certifies that the method space itself is insufficient (P10 already refuses P9-repair as a donor in its Stage-1 list).
- *"P11's compiled state is P10's outside-closure edit"* → both must state: compilation stays within the registered method basis (`KNOWN_COMPOSITION` in P10's terms); expansion changes the basis.
- *"P14's governance is P8's authorization"* → C7: typing vs process superiority under matched capability.
- *"P15's ladder decides admissions"* → C13: records dispositions, never decides them.
- *"P6/P7/P8 re-own P1/P2/P4"* → §4: conservative-embedding declarations, residuals only.
- *"three papers drink from one wine/digits well"* → §6.4: per-paper frozen-quantity declarations.

## 9. Required manuscript edits (per paper, minimal set)

- **P6:** re-word T6.1's fourth factor as P8-owned status consumed as frozen input (C2); extend the P1/P4/P8 donor declaration from the baseline to the factor definitions; keep C1's intra-regime scoping sentence in T6.2.
- **P7:** add P6 certificate-donor citation (C1), P2 stopping citation (§4), and the dual-to-P13 boundary sentence (C4).
- **P8:** add the five-gate `MERGE_EXISTING` statement with P4 cited (§4); declare P15 receipts as admissible evidence substrate (§6.1).
- **P9:** rename `R2_TYPED_STATE` in prose (§6.3); add "not an online policy, not a placement law" scoping (C9/C10).
- **P10:** add the P9-rung ladder sentence (§7) and the P11-compilation `KNOWN_COMPOSITION` note (§8).
- **P11:** phrase near-universal-performance comparisons through P9's `A` coordinate with citation (C9); rename the laundering condition to answer-content leakage with P8 citation (C5); add "optionality prices cost, not safety" scoping (C12).
- **P12:** declare P9/P11/P13/P7 donor relations for its action set and allocator framing (C10/C11, §6.2).
- **P13:** make P7 duality and P8 revocation citations explicit (C4/C6); cite P11 for recovery/optionality costing (C12); add the parity-corpus disjointness declaration (§6.4).
- **P14:** list P6/P7/P8/P5 frozen upstream donors in the adjudication design (C7); keep headline as process superiority.
- **P15:** import dispositions as frozen external types with P8/P14 named (C3/C13); name the source paper of each real receipt (§6.5).

## 10. Terminal disposition

`COLLISION_REVIEW_V1_COMPLETE`: 45 pairs adjudicated — 13 `COLLIDES` (all with sentence-level fixes above), 6 `BORROWS-UPWARD` (2 already declared, 4 to declare), 26 `NONE` (of which 6 carry mandatory boundary sentences). No pair requires claim narrowing; every fix is a hierarchy statement or boundary sharpening with explicit donor citation. Three undeclared load-bearing evidence dependencies (P15 gold dispositions, P12 reopen actions, shared dataset framing) and one arm-name defect (`R2_TYPED_STATE`) are queued as manuscript edits in §9. This review does not promote or demote any paper; it is an input to each paper's final cross-paper ownership gate (`P6/P7/P8` gates list it explicitly; `P9–P15` gates should add the same line at manuscript scope).
