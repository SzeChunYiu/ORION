# ORION research harness gap study — 2026-08-22

Status: `ENGINEERING_GAPS_CLOSED__SCIENTIFIC_VALIDATION_BOUNDARIES_RETAINED`
Scope: shared `packages/orion-research-harness` and its paper-programme interfaces
Authority: engineering review only. This record grants no scientific, novelty, adoption, promotion, merge, or global-task-stop authority.

## Review team / lenses

This study used four deliberately different reviewer roles.

1. **Paper-contract reviewer — formal methods / scientific-method representation.** Traced each P1-P15 mechanic from written contract to executable owner and looked for prose-only or fixture-only surfaces.
2. **Runtime systems reviewer — research workflow / orchestration.** Followed ordinary `solve`, campaign, host-capability and receipt paths to determine whether a working mechanic was actually reachable by a research host.
3. **Hostile epistemic reviewer — falsification / authority boundaries.** Looked for false greens: labels counted as route independence, verified answer counted as task stop, timeouts counted as obstruction, confidence counted as authority, or one proposer defining a paper structure.
4. **Research-agent usability reviewer — autonomous research operations.** Asked whether the harness tells the host what to do next, whether failures are causally routed, and whether raw scientific sources can enter the system without hand-authored intermediate structure.

Findings were accepted only when the four lenses agreed on the failure mode and the proposed repair preserved the stricter authority boundary.

## Findings and dispositions

### G1 — paper mechanic discoverability was being confused with execution

**Finding:** the original mechanics bridge could prove IDs/aliases/cells were discoverable while a paper mechanic remained non-operational.

**Disposition:** `CLOSED`.

Repairs:

- dedicated semantic paper-contract gate;
- executable P1-P15 programme matrix;
- positive and fail-closed probe required for every paper row;
- ordinary structural discoverability remains a separate weaker check.

Terminals:

- `ORION_HARNESS_PAPER_CONTRACT_P0_OPERATIONAL`;
- `ORION_HARNESS_P1_P15_OPERATIONAL`.

### G2 — raw-paper “extraction” started from authored method fixtures

**Finding:** P1/P3 structures were representable/validatable, but the successful pilot did not establish a raw-source execution path.

**Disposition:** `CLOSED_ENGINEERING / EXTERNAL_ACCURACY_OPEN`.

Repairs:

- exact source bytes/text are content-bound;
- PDFs use a digest-bound `DOCUMENT_TEXT_EXTRACT` host request;
- every populated coordinate requires an exact verbatim source span;
- unsupported coordinates remain typed `UNKNOWN`;
- canonical P1/P3 builders own the structured objects;
- independent `VERIFY_EVIDENCE` support certificate remains mandatory.

V3 adds a two-lane proposer path and independent coverage review so one proposer can no longer silently define the noticed structure.

The remaining question “how accurate is extraction over arbitrary scientific papers?” is an empirical evaluation question, not an engineering permission to claim completeness. It remains explicitly open until a suitably independent real-paper corpus is executed.

### G3 — `navigate` was mechanic lookup rather than Paper-VII navigation

**Finding:** catalog token matching was useful discovery UX but not epistemic-space navigation.

**Disposition:** `CLOSED`.

Repair: executable charts, route contracts, obligations, orientation, censored routes, local route stops, reframes, support transport/reopening and fail-closed task stopping.

### G4 — route labels could impersonate research-space coverage

**Finding:** a query labelled `PARENT_DISCIPLINE` could count as visiting that route family without proving structural independence or a coverage contract.

**Disposition:** `CLOSED_FOR_BOUNDED_SATURATION`.

Repairs:

- structural `RouteContract` carries critical assumptions and coverage scope;
- independence derives from structure rather than label/API/output overlap;
- mixed multi-route rounds cannot mint extra independent-flat credit;
- unobserved axes, residuals and resource bounds block bounded saturation;
- absolute completeness remains false.

### G5 — richer Self-ORION saturation existed separately from the live harness

**Finding:** the nine-axis development-saturation object was not the ordinary harness stopping surface.

**Disposition:** `CLOSED`.

Repair: evidence-derived round identities feed the canonical nine-axis evaluator; callers cannot submit novelty counts or an `independent_route=True` bit.

### G6 — P6 mechanics and P8 authority were formal/checker surfaces rather than host-callable research controls

**Finding:** paper equations/checkers existed without a complete shared-harness execution surface.

**Disposition:** `CLOSED`.

Repairs include:

- P6 declared footprints, hard-obligation persistence/discharge, root-inclusive repair, preservation certificates, non-escalating authority, append-only history and decreasing audit rank;
- P8 exact full-type discharge/coercion, blockers, grants, freshness, alternative support families/revocation and non-compensatory authority.

Hostile review additionally found and closed implicit scope widening in P8.

### G7 — P10 described OCME while general obstruction/outside-closure execution remained prospective

**Finding:** a method failure could not yet be driven through the paper's O0-O6 distinction between search/access/implementation failure and genuine language inadequacy.

**Disposition:** `CLOSED_AS_BOUNDED_RUNTIME`.

Repair: executable OCME assessment. Timeout-only failure, aliases/macros, self-certification, hidden access widening, donor recovery or missing reproduction cannot become method-space expansion.

### G8 — the ordinary recursive solve path did not tell the host which paper mechanic to invoke next

**Finding:** all paper mechanics could be real yet remain side surfaces requiring the host to know the framework manually.

**Disposition:** `CLOSED_V3`.

Repair: deterministic paper-aware research director derived from immutable recursive run state.

Key rule: a verified answer with no material residuals routes to `ASSESS_SATURATION`, **not** task stop. Method responsibility routes to `ASSESS_OCME`, **not** automatic invention. Execution/evidence/evaluator responsibilities have non-compensatory precedence.

Terminal: `ORION_HARNESS_RESEARCH_DIRECTOR_CONSENSUS_EXTRACTION_V3_OPERATIONAL`.

### G9 — a single proposer could miss or disagree about source-supported method structure

**Finding:** exact span checking prevents fabrication but not omission or one-model interpretation variance.

**Disposition:** `CLOSED_V3`.

Repair:

- two replay-distinct proposer lanes;
- identical claims retain both lane identities;
- scalar disagreement -> `CANNOT_CHECK_PROPOSER_DISAGREEMENT`;
- independent coverage review checks for missed supported coordinates;
- valid miss -> `CANNOT_CHECK_COVERAGE_GAP`, not silent reviewer injection;
- final semantic support verification remains independent and certificate-bound.

### G10 — normal query telemetry cannot prove Paper-VII route independence by itself

**Finding:** canonical `SearchQuery` contains `route_id` and `route_kind`, but not critical failure/coverage assumption identities. Therefore a fully automatic conversion from query traces to structurally independent route contracts would be unsound.

**Disposition:** `BOUNDARY_RETAINED`, not an engineering false green.

The harness deliberately requires explicit structural `RouteContract`s for navigation/saturation. A future route-contract registry could improve convenience, but it must not infer structural independence from route labels. Until such protected structure exists, missing route-contract identity is correctly `CANNOT_CHECK`.

### G11 — receipt completeness does not imply scientific evidence quality

**Finding:** P15 already records this distinction, and repository history contains a fully receipted but scientifically unusable digest-representation failure.

**Disposition:** `BOUNDARY_RETAINED`.

Repairs throughout this work preserve separate evidence verification and scientific authority. Harness success/CI success cannot promote a scientific claim.

### G12 — stale integration assertions can become false red infrastructure

**Finding:** the live ORION-Q smoke test still grepped an old intermediate P10 token after the campaign legitimately advanced to the protected pre-access R6 verdict.

**Disposition:** `CLOSED`.

Repair: parse the live campaign receipt and require the stronger invariant—terminal progression plus `R6_EARNED=NO`, protected-subject access `NO`, exact protected blob identity unreleased and authority ceiling below R6. The scientific prospective R6 job remains separate and unchanged.

## Improvements considered but deliberately not added

### Inferring route independence from `SearchRouteKind`

Rejected. It would recreate the original saturation false green.

### Automatically executing a method-language jump whenever responsibility is `METHOD`

Rejected. P10 requires lower-level first-right-of-refusal and an independent obstruction/outside-closure chain.

### Automatically treating `SOLVED_VERIFIED` as task completion

Rejected. P2/P7 require route/task stopping separation and V3 routes through bounded saturation.

### Letting coverage reviewer claims enter the canonical paper structure directly

Rejected. Reviewer-discovered misses reopen extraction; they do not silently become scientific structure.

### Requiring two different model vendors for consensus extraction

Not made a semantic requirement. Distinct replay lanes plus independent coverage/support review are enforceable with the available host contract; vendor/model diversity can be an evaluation configuration but is not equivalent to epistemic independence.

## Current engineering completion criterion

The shared harness is engineering-complete for this tranche when the same exact PR head satisfies all of:

1. P0 semantic gate green;
2. every P1-P15 row positive + fail-closed + operational;
3. V3 research-director/consensus gate green;
4. full shared-harness hostile/regression suite green;
5. execution-coverage gate green;
6. recursive-budget hardening green;
7. ordinary shared-harness live campaign smoke green with protected custody preserved;
8. ORION-Q matched dual lane green;
9. repository-wide CI green;
10. no unresolved hostile review thread;
11. branch based on current `main` with no unreviewed protected-subject changes.

No further feature is allowed to postpone closure merely because it would be convenient. New scientific capability questions after these criteria pass become new frozen research tranches rather than moving this merge target indefinitely.

## Residual scientific/evaluation questions after engineering closure

These remain legitimate future research, not hidden implementation gaps:

- arbitrary-paper extraction accuracy on a large independently annotated multi-domain corpus;
- whether real scientific search spaces admit sufficiently faithful operational atlases;
- empirical calibration of route-contract coverage and independence judgments;
- matched comparison of ORION research execution against external research-agent/harness baselines;
- whether a shared receipt semantics can unify the ordinary harness and ORION-Q dual-lane receipts without losing their different guarantees.

The correct disposition for those questions is future protected research, not an engineering claim that this harness already proves them.
