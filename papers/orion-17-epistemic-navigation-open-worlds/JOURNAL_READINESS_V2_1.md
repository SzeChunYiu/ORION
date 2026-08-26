# P7 journal readiness V2.1

**Theory manuscript:** `manuscript/FINAL.md`  
**Submission manuscript:** `submission/AIJ_MANUSCRIPT.tex`  
**Formal core:** `manuscript/FORMAL_CORE_V2.md`  
**Theory:** `FINISHED_V2`  
**Primary venue:** Artificial Intelligence (AIJ)  
**Peer-review terminal:** computed by `../../PEER_REVIEW_READY_PACKAGE.md` from exact-head GitHub checks.

## Scientific closure

- [x] Extension-ambiguity stopping theorem and richness boundary.
- [x] Fixed-information representation refinement + harmful coarsening.
- [x] Evidence-preservation/closure-preservation separation.
- [x] Complete positive transport and ambiguity-conditioned negative transport.
- [x] Distinct route/task/continue/cannot-check terminals.
- [x] Route identity, structural equivalence/refinement and genuine-new-route boundary.
- [x] Defer/revisit, witness-backed backtracking, loop/dead-end and forced-reframe semantics.
- [x] Donor-complete embeddings for graph/POMDP/planning abstraction/schema/goal/world-model structures.
- [x] 8 frozen prospective contracts absorbed and executable.
- [x] Harmful/unnecessary-reframe control.
- [x] Non-retrieval experimental-design transfer case.
- [x] Final theory manuscript, claim ledger, reproduction path and CI wiring.

## Real-regime transport evidence (three landed classes)

This record was theory-only and did not mention the non-synthetic evidence at
all. A readiness record silent on a paper's empirical result is stale in the
way that matters: a reader checking readiness sees the theory closed and no
indication that three real change classes have landed.

All three are witness-aware `1.0` against the same two donor-complete
baselines, with the denominators that make that checkable:

| Change class | Denominator | Witness-aware | Value-only | Always-reopen |
| --- | --- | --- | --- | --- |
| representation (RO-Crate `1.2 -> 1.3`) | 14 frozen cases | `1.0`, 4 correct `CANNOT_CHECK` | `0.428571...`, 8 false closures | `0.285714...`, 6 unnecessary reopens |
| responsibility/ontology (UCI Wine) | 712 protected rows | `1.0`, 238 correct `CANNOT_CHECK` | `0.665730...`, 238 false closures | `0.0`, 474 unnecessary reopens |
| objective/obligation (WDBC) | 5 folds x 2 states = 10 cells | `1.0`, 5 correct `CANNOT_CHECK` | `0.3`, 5 false closures | `0.1`, 4 unnecessary reopens |

Bound receipts: `top_tier/P7_REAL_REGIME_TRANSPORT_RESULT_RECEIPT_V1.md` for
classes 1 and 2, `top_tier/P7_OBJECTIVE_CHANGE_TRANSPORT_RESULT_RECEIPT_V1.md`
for class 3.

The `1.0` is exact conformance to a finite frozen contract on the cases above,
not universal regime transport; the README states that boundary in full and it
is not weakened here.

## Peer-review submission closure

- [x] Two-round pre-submission literature delta dated 2026-08-18.
- [x] Categorical scientific-regime transport, sheaf transport/obstruction and current closure-gap work explicitly donor-owned.
- [x] Submission-specific headline claim-authority ledger.
- [x] AIJ-facing editable LaTeX source with normal in-text citations and reference list.
- [x] AIJ highlights (3–5, each <=85 characters) and cover letter.
- [x] Transparent generative-AI assistance declaration.
- [x] Corresponding-author institutional metadata.
- [x] Deterministic submission structural/citation linter wired into the fast candidate workflow.
- [x] Exact-head archive rule defined: successful PR head + GitHub check runs.

## Computed final gate

P7 is `PEER_REVIEW_READY` exactly when both `p6-p8-candidate-ci` and repository `ci` are successful on the same PR head. Any manuscript/source change reopens this terminal until the changed head is retested.

P7 does not claim representation/regime transport, planning abstraction, P1 reframing or P2 route/task stopping. Its submission residual is scientific evidence/closure/obligation transport under representation/objective change, coupled to honest open/censored stopping.

A later live-agent benchmark can strengthen the paper but is not required to establish the formal submission claims. Private funding, competing-interest and optional ORCID attestations are not inferred; see #377. External peer review is a later event; see #378.
