# ORION papers — science-first publication dashboard

This README is the **portfolio control plane** for ORION papers. It answers four questions for every canonical paper:

1. what scientific object is currently earned;
2. where we intend to publish it;
3. what still blocks that venue route; and
4. which closure wave owns the next action.

It is a routing and status index, **not scientific authority**. A README edit cannot promote a claim. The authoritative theorem/result/negative-history/replay/receipt files remain inside each paper and its bound research/evidence lanes.

Canonical identities across the whole tree follow the single flat `ORION-NN`
registry in `PAPER_ALIASES.md`. “Flagship” below is a programme role, not a
separate numbering system. In particular, the former AB/C/D/NQ/Q1 studies are
now **ORION-01–05** (Certificate Realization, FiberGuard Finite Fibre,
Typed-Merge Falsification, Rooted Completion Certificates, and TARE
Expressivity). Their current evidence hierarchy and science-first closure gates
are controlled by `../research/orion-01-05-convergence-v1/README.md` and
`../research/orion-01-05-convergence-v1/SCIENCE_STATUS_V1.json`.

## Publication status checklist

**Last updated:** 2026-08-29 21:43 CEST (Europe/Stockholm)  
**Update rule:** change this timestamp whenever any row changes.  
**Checkbox rule:** replace `☐` with `☑` only when the corresponding event has actually happened and is supported by repository evidence (merge commit, arXiv identifier/URL, or journal submission receipt/ID).  
**Git rule:** the Git box is ticked only when the **latest publication state** for that paper is on `main`; a paper directory merely existing on `main` is not enough.  
**Venue rule:** the primary venue follows the strongest earned paper archetype. If the broad claim does not fit, use the narrower/specialist fallback rather than widening the science. “Fallback” is a scope/fit decision, not a quality judgment.

### Readiness legend

- `B0` — bounded paper **science is complete**. No new scientific evidence is required to submit that bounded paper; only mechanical/administrative publication work may remain.
- `B1` — no new outcome is intrinsically required for a bounded paper, but existing evidence/theory still needs substantive integration or audit before submission.
- `B2` — the intended current submission claim still requires new evidence or external authority.
- `B3` — the old question/promotion route is spent; a new frozen question is required.
- `T0` — a top-tier review attempt is scientifically defensible **now for the bounded claim**. A `B0 / T0` row therefore has **no scientific gap to its current bounded top-tier attempt**.
- `T1` — one substantial internal proof/reanalysis/integration closure remains for the stronger/top-tier version.
- `T2` — the stronger/top-tier interpretation needs prospective data, external gold, or genuinely independent authority.
- `T3` — the old top-tier promotion route is closed/adverse; publish/retarget the bounded negative or formal result rather than rescuing the old claim.

**Important:** `Submit-now blocker` and `Stronger/top-tier successor gap` are deliberately separate. For `B0 / T0`, the submit-now blocker may contain only merge, render, package, metadata, or portal mechanics. The successor-gap column is **not a blocker** to the current paper unless it explicitly says so.

| No. | Paper title | Status on Git | Primary target | Fallback / specialist target | Bounded | Top-tier | Submit-now blocker | Stronger/top-tier successor gap | arXiv | Journal |
|---:|---|---|---|---|---|---|---|---|---|---|
| 01 | [ORION-01 — Certificate Realization](orion-01-certificate-realization/) | ☑ `main` | Quantum | Theoretical Computer Science | `B1` | `T1` | Integrate move census, hidden-operation/confluence results and current proof/novelty closure into one submission surface. | Source-complete semantics/proof for the broader realization claim. | ☐ | ☐ |
| 02 | [ORION-02 — FiberGuard Finite Fibre](orion-02-fiberguard-finite-fibre/) | ☑ `main` | TMLR | Machine Learning / theory specialist | `B1` | `T2` | Recenter manuscript on the audited finite-fibre theorem plus adverse transfer boundary. | Prospective heterogeneous OpenML transfer with valid per-task bounds. | ☐ | ☐ |
| 03 | [ORION-03 — Typed-Merge Falsification](orion-03-typed-merge-falsification/) | ☑ `main` | Formal/security journal | Theoretical Computer Science | `B1` | `T2` | Rebind native trust-store/verifier evidence and finish the theorem-first reframe. | Independently governed native trust/provenance ecosystems for broad transfer. | ☐ | ☐ |
| 04 | [ORION-04 — Rooted Completion Certificates](orion-04-rooted-completion-certificates/) | ☑ `main` | Journal of Automated Reasoning-style | Theoretical Computer Science | `B2` | `T2` | Authorized independent proof/census authority is still required for the intended claim. | Same external authority gate; internal agents cannot manufacture it. | ☐ | ☐ |
| 05 | [ORION-05 — TARE Expressivity](orion-05-tare-expressivity/) | ☑ `main` | Quantum | Theoretical Computer Science | `B1` | `T1` | Finish governed compute/global-obstruction accounting and current package authority closure. | External compiler-facing cases for broader practical transfer. | ☐ | ☐ |
| 06 | [ORION-06 — Recursive Recovery](orion-06-recursive-recovery/) | ☐ PR #1798 — release package **GREEN** | Artificial Intelligence (AIJ) | TMLR | `B0` | `T0` | **No scientific blocker.** Merge PR #1798 / final release record, then file arXiv and AIJ. | **None for the bounded AIJ/TMLR attempt.** Cross-domain effectiveness is optional successor research. | ☐ | ☐ |
| 07 | [ORION-07 — Dual Instrument](orion-07-dual-instrument/) | ☐ PR #1798 — release package **GREEN** | TMLR | AIJ Research Note | `B0` | `T0` | **No scientific blocker.** Merge/package is green; file the bounded three-case paper. | **None for the bounded TMLR attempt.** Population reliability/generalization would require a prospective multi-domain registry. | ☐ | ☐ |
| 08 | [ORION-08 — Typed State](orion-08-typed-state/) | ☐ PR #1798 — release package **GREEN** | TMLR | AIJ | `B0` | `T0` | **No scientific blocker.** Merge current routed master/package, then file. | **None for the bounded TMLR attempt.** Real-system transfer is optional successor evidence. | ☐ | ☐ |
| 09 | [ORION-09 — Compilation Regime Geometry](orion-09-compilation-regime-geometry/) | ☑ `main` | Quantum | Theoretical Computer Science | `B1` | `T3` | Rewrite/package the exact geometry plus negative transfer result as the paper. | Old invariant-promotion route is closed; broader work requires a genuinely new frozen question. | ☐ | ☐ |
| 10 | [ORION-10 — Certified Static Forecasting](orion-10-certified-static-forecasting/) | ☐ PR #1798 — release package **GREEN** | Quantum | Theoretical Computer Science | `B0` | `T0` | **No scientific blocker.** Merge and file current `quant-ph` / CC BY 4.0 package. | **None for the bounded Quantum attempt.** Scoped B′ remains `CANNOT_CHECK` and belongs to successor work if pursued. | ☐ | ☐ |
| 11 | [ORION-11 — Recursive Epistemic Reconstruction](orion-11-recursive-epistemic-reconstruction/) | ☑ `main` | TMLR | AIJ Research Note / specialist AI methods | `B1` | `T3` old superiority route | Rebuild around corrected mechanism/leakage diagnosis and preserved comparative retraction. | Any renewed superiority claim requires a new frozen identity and new external evidence. | ☐ | ☐ |
| 12 | [ORION-12 — Open-World Scientific Knowledge Discovery](orion-12-open-world-scientific-discovery/) | ☐ PR #1798 — release package check **RED (mechanical)** | Information Processing & Management | JASIST-style information-science venue | `B0` | `T1` | **No new science required.** Fix remaining TeX references/citation/package mechanics, then file the bounded methods paper. | One internal framing/baseline-interface closure for a stronger methods presentation; a superiority claim is a separate `T2` successor requiring fresh matched BEIR evidence. | ☐ | ☐ |
| 13 | [ORION-13 — Global Knowledge Portrait](orion-13-global-knowledge-portrait/) | ☑ `main` | Journal of Web Semantics | Data & Knowledge Engineering | `B1` | `T1` | Rebuild the current manuscript around the polarity-sensitive scoped result, constant comparator and anti-confounding boundary. | Anti-confounded external semantic corpus for broader coordinate/semantic utility. | ☐ | ☐ |
| 14 | [ORION-14 — Verified Scientific Discovery](orion-14-verified-scientific-discovery/) | ☐ PR #1798 — release package check **RED (mechanical)** | TMLR | AIJ | `B0` | `T0` | **No scientific blocker.** Fix named-arXiv/package CI mechanics, then merge and file. | **None for the bounded TMLR attempt.** External naturalistic multi-domain authority is optional successor evidence. | ☐ | ☐ |
| 15 | [ORION-15 — Self-ORION](orion-15-self-orion/) | ☑ `main` | TMLR | AIJ / formal-methods specialist | `B1` | `T1` | Center the anytime-safe governance theorem, retain fail-closed non-computation and rebuild the bounded package. | Protected longitudinal empirical self-improvement campaign with external custody/evaluation. | ☐ | ☐ |
| 16 | [ORION-16 — Formal Epistemic Structures and Mechanics](orion-16-formal-epistemic-structures-and-mechanics/) | ☐ PR #1798 — release package **GREEN** | Artificial Intelligence (AIJ) | Theoretical Computer Science | `B0` | `T0` | **No scientific blocker.** Merge green release state and file. | **None for the bounded AIJ attempt.** Production consequence on authoritative build/test graphs is optional successor evidence. | ☐ | ☐ |
| 17 | [ORION-17 — Epistemic Navigation in Open Worlds](orion-17-epistemic-navigation-open-worlds/) | ☑ `main` | AIJ | Software-evolution empirical venue | `B1` | `T3` density route | Rewrite around `NO_DISCRIMINATION`, src-layout degeneracy and the still-valid bounded pairwise result. | Old density route is closed; any broad navigation law requires a new mechanism-identifiable, organization-disjoint successor. | ☐ | ☐ |
| 18 | [ORION-18 — Epistemic Authority in Autonomous Science](orion-18-epistemic-authority-autonomous-science/) | ☑ `main` | AIJ | Journal of Automated Reasoning / TCS | `B2` broad; theorem contraction possible | `T2` | Choose and package a theorem-first contraction, or obtain the external authority required by the broad empirical claim. | Independent human/institutional adjudication and conflict rules. | ☐ | ☐ |
| 19 | [ORION-19 — Structured Epistemic Learning](orion-19-structured-epistemic-learning/) | ☑ `main` | TMLR | AIJ Research Note | `B1` | `T1` bounded | Regrade inference at five-task-family level and integrate custody/current PDF plus small-`n` uncertainty. | Externally sourced blinded failure episodes for broad transfer. | ☐ | ☐ |
| 20 | [ORION-20 — Structured Problem Solving](orion-20-structured-problem-solving/) | ☑ `main` | Theoretical Computer Science | Journal of Automated Reasoning-style | `B1` | `T3` | Turn the multiple-singleton-minima result into the main impossibility/negative theorem and finish the bounded package. | Old primitive-indispensability route is closed; outside-closure discovery requires a new operational question. | ☐ | ☐ |
| 21 | [ORION-21 — State as Computation](orion-21-state-as-computation/) | ☑ `main` | Theoretical Computer Science | AIJ | `B1` | `T1` | Integrate general tie-equivalence impossibility, tie ambiguity and checker hardening into one theorem/falsification story. | Untouched external systems/families for magnitude and moderate-capability behavior. | ☐ | ☐ |
| 22 | [ORION-22 — Adaptive State Reasoning](orion-22-adaptive-state-reasoning/) | ☑ `main` | TMLR | AIJ | `B1` | `T2` | Package the exact nine-case law and broken robustness axes without broadening the claim. | Robustness plus one untouched transfer family selected before outcomes. | ☐ | ☐ |
| 23 | [ORION-23 — Responsibility-Carrying State](orion-23-responsibility-carrying-state/) | ☑ `main` | TMLR | AIJ / semantic-governance specialist | `B1` | `T2` | Separate P13A/P13B authority visibly, preserve `UNKNOWN`, and package the exact bounded transport result. | Organization-disjoint objective-gold lifecycle evidence for broader safety/reuse claims. | ☐ | ☐ |
| 24 | [ORION-24 — ORION-RSE](orion-24-orion-rse/) | ☑ `main` | Empirical software-engineering journal | TMLR only if final object is truly an evaluation method | `B1` | `T2` | Integrate principled nulls/group robustness and remove residual “beats SYSTEMA” framing. | Blinded independent adjudication plus prospective longitudinal negative-history evidence. | ☐ | ☐ |
| 25 | [ORION-25 — ORION Research Harness](orion-25-orion-research-harness/) | ☑ `main` | Security/formal-systems journal | Theoretical Computer Science | `B1` | `T2` | Center integrity-vs-authority separation and package the exact bounded trust-domain law. | At least two real systems with structurally different, genuinely independent governance/trust domains. | ☐ | ☐ |

For an external submission, keep the checkbox and append the durable identifier in the same cell, for example `☑ arXiv:2608.xxxxx` or `☑ TMLR / OpenReview submission <id>`. Do not tick a submission box for a generated package, an intended venue, or a locally completed manuscript.

## Publication identity rule

ORION has **exactly five flagship papers**, assigned ORION-11–15 in the flat
registry. A paper identity is determined by its canonical topic and directory
below, not by a historical number that may appear in an old RAKL artifact.

## Non-negotiable publication policy

**Science first. Packaging never repairs science.**

A paper may move toward submission only when its current headline claim is supported by the required theorem/protocol/result/negative-history and independent verification for the scope actually claimed. Venue templates, prose polishing, PDFs, cover letters and submission portals do not convert `CANNOT_CHECK`, a failed gate, a null result or an unexecuted experiment into scientific support.

The programme uses the following status vocabulary:

| Status | Meaning |
|---|---|
| `SCIENCE_RED` | A decisive registered gate failed, a contradiction is known, or the intended standalone scientific object has not been earned. The claim must shrink or new science must be run. |
| `SCIENCE_OPEN` | Useful bounded evidence exists, but a required theorem, transfer, robustness, baseline, adjudication or external-authority gap remains open. |
| `SCIENCE_VERIFIED_BOUNDED` | The current bounded claim has explicit evidence and independent verification/replay. This does **not** imply broad/general/top-tier authority. |
| `PACKAGE_OPEN` | The scientific object may be usable, but current manuscript/PDF/access/licence/archive/venue-binding requirements are incomplete. |
| `READY_SPECIALIST` | Bounded science plus current manuscript/PDF, independent replay, nearest-work boundary, target fit and exact submission-byte binding are all closed for the named specialist/second-tier route. |
| `TOP_TIER_PROMOTION_PENDING` | A bounded result is preserved, but the stronger discriminator needed for the higher venue is still open. |
| `TOP_TIER_READY` | Reserved for a future content-addressed receipt closing the common and paper-specific promotion gates. |
| `FILING_ONLY` | Repository-side submission object is complete; only human/portal attestations remain. |
| `CANNOT_CHECK` | Required authority is unavailable or unexecuted. Never treat this as PASS. |
| `ROUTING_REQUIRED` | No current venue decision has enough authority. Venue selection itself is a blocker and must be audited against official current guidance. |

### Refinement rule

The next broad prose/figure/title refinement pass happens **after most draft science is closed or explicitly bounded**. Refinement may improve clarity, structure and venue fit; it may not broaden the scientific claim beyond the bound receipts.

## Canonical paper identities

There is one flat canonical series: `ORION-01` through `ORION-25`, each mapped to exactly one `papers/orion-NN-<slug>/` directory. Historical `theory-*`, `NQ`, `Q*`, `QG*` and `P*` identifiers are aliases only. See `PAPER_ALIASES.md`.

Do **not** infer a venue, claim, result or readiness state from a historical alias. In particular, old Q/QG documents that call Q1–Q4 “ORION-01–04” are historical naming artifacts; canonical Q1–Q4 are ORION-05–08.

## Portfolio dashboard

Venue routes below are **current routing decisions or explicit proposed routes**, not acceptance predictions. `ROUTING_REQUIRED` is intentionally visible rather than guessed. Official author instructions, article types, anonymity, fees, data/code rules and submission mechanics must be revalidated immediately before filing.

| Paper | Scientific object / current bounded state | Primary route | Fallback / stronger route | Main gap before honest submission or promotion | Next owner |
|---|---|---|---|---|---|
| **ORION-01 — Certificate Realization** | `SCIENCE_OPEN`; certificate-realization line retained | SIAM Journal on Computing | Theoretical Computer Science | Production registry completeness/value and final current reproduction/claim binding | Wave C1 |
| **ORION-02 — FiberGuard Finite Fibre** | `SCIENCE_OPEN`; Round-1 null retained | JMLR | TMLR | Untouched-subject direct-relative/joint-route value; preserve null rather than force promotion | Wave C1 |
| **ORION-03 — Typed-Merge Falsification** | bounded theorem result present; `SCIENCE_OPEN` for stronger empirical route | IEEE TSE **only if** independent real-domain discriminator closes | Theoretical Computer Science | External real-domain value / independent transfer; otherwise keep the theorem-scoped route | Wave C1 |
| **ORION-04 — Rooted Completion Certificates** | `SCIENCE_OPEN / CANNOT_CHECK` on unresolved replay lane | Journal of Combinatorial Theory, Series A | European Journal of Combinatorics | D2/D3 replay remains `CANNOT_CHECK`; exact D4 closure and clean reproduction required | Wave C1 |
| **ORION-05 — TARE Expressivity** | `SCIENCE_VERIFIED_BOUNDED`: support-two normal form, exact counterexamples, result-bound sparse-direct R11 algorithm; no generic production/physical-resource claim | **IEEE Transactions on Quantum Engineering** — active specialist package | PRX Quantum / npj Quantum Information only after stronger public compiler/crossover discriminator; QST is a narrower fallback route | Wave-A final package receipt; stronger route additionally needs independent public compiler family and measured crossover/resource evidence | **Wave A** |
| **ORION-06 — Recursive Recovery** | bounded Q2 graph/result programme retained; broad superiority not inferred | Artificial Intelligence | JAIR / routing refresh | Revalidate current AIJ fit, fresh nearest-work subtraction and exact current package/replay binding | Wave C2 |
| **ORION-07 — Dual Instrument** | bounded completed prospective series with retained negative/counterexample; no reliability generalization | TMLR | routing refresh | Fresh target audit + final package/byte binding; keep contamination and adverse result visible | Wave C2 |
| **ORION-08 — Typed State** | bounded Q4 state/governance result retained | TMLR | routing refresh | Current target/nearest-work refresh and exact package/replay binding | Wave C2 |
| **ORION-09 — Compilation Regime Geometry** | `SCIENCE_VERIFIED_BOUNDED` for family-specific geometry / falsified finite feature laws | **IEEE Transactions on Quantum Engineering** — active specialist package | PRX Quantum only after general theorem or independent public compiler-family discriminator | Wave-A final package receipt; top-tier discriminator still open | **Wave A** |
| **ORION-10 — Certified Static Forecasting** | `SCIENCE_VERIFIED_BOUNDED` layered exact cost/explanation/verification certificate claim; classifier refutation retained | **IEEE Transactions on Quantum Engineering** — active specialist package | stronger quantum venue only after second-family downstream decision-value evidence | Wave-A final package receipt; second-family + decision-value science for promotion | **Wave A** |
| **ORION-11 — Recursive Epistemic Reconstruction** | bounded mechanical result `SUPPORTED` and independently recomputed; submission readiness currently `CANNOT_CHECK` | `ROUTING_REQUIRED` after package authority restored | — | Fresh current PDF + visual audit, immutable archive/DOI, redistribution rights, admissible source-native handoff bytes/checksum; then venue audit | Wave C3 |
| **ORION-12 — Open-World Scientific Discovery** | `SCIENCE_VERIFIED_BOUNDED / PEER_REVIEW_READY` for narrowed methods/critical-system-design claim; external superiority remains `CANNOT_CHECK` | Information Processing & Management | JASIST after larger information-science/use reframe | Filing-time freshness/official venue revalidation; do not reopen external superiority unless a new prospective campaign is frozen | Wave C3 |
| **ORION-13 — Global Knowledge Portrait** | `SCIENCE_VERIFIED_BOUNDED / PEER_REVIEW_READY` for scoped structured-mapping claim when exact-head CI + manuscript audit are green | Semantic Web Journal | Journal of Web Semantics | Exact-head CI/package freshness, filing-time literature refresh and final submission-byte binding | Wave C3 |
| **ORION-14 — Verified Scientific Discovery** | bounded verification-axis theory + protected-battery evidence, H3 null retained | **TMLR** | no stronger route required for honest specialist closure | Wave-A final package/filing receipt; do not reopen science absent a defect | **Wave A** |
| **ORION-15 — Self-ORION** | `SCIENCE_RED / NO_TERMINAL_UNDER_FROZEN_RULES`; 96-case panel does not establish governed self-improvement benefit | `ROUTING_REQUIRED AFTER SCIENCE` | — | Execute protected V1/V2 + matched baselines/ablations, bind evaluator/splits/budgets/custody, quantify harmful/fresh transfer, independent external attestation | **Wave B1** |
| **ORION-16 — Formal Epistemic Structures and Mechanics** | controlled bounded ETS result preserved; `TOP_TIER_PROMOTION_PENDING` | Artificial Intelligence | JAIR | Donor-complete real-system replication; final non-overlap/literature refresh; current submission-byte binding | Wave B2 |
| **ORION-17 — Epistemic Navigation in Open Worlds** | three executed non-synthetic change classes; `TOP_TIER_PROMOTION_PENDING`; current binding must revalidate | **Artificial Intelligence** — active Wave-A route | JAIR | Current exact binding, target-ambiguity repair, stronger external donor/lens comparator; public target identification for promotion | **Wave A**, then B2 if promoted |
| **ORION-18 — Epistemic Authority for Autonomous Science** | bounded authorization theory + 20-case/4-domain discharge preserved; `TOP_TIER_PROMOTION_PENDING` | JAAMAS | Artificial Intelligence | Sound mapping from 13-donor composition to general calculus; real integrated donor + independent adjudication | **Wave B2** |
| **ORION-19 — Structured Epistemic Learning** | strong mixed bounded result, including adverse/null evidence; `TOP_TIER_PROMOTION_PENDING` | **TMLR** — active Wave-A route | broader route only after public multi-model/procedural breadth | Hostile representation/length/format-prior attacks + Wave-A final package; public multi-model breadth only if headline broadens | **Wave A**, then B2 if promoted |
| **ORION-20 — Structured Problem Solving** | `SCIENCE_RED / SCIENTIFIC_OBJECT_NOT_YET_EARNED` for intended standalone object; bounded/historical negatives preserved | `ROUTING_REQUIRED AFTER SCIENCE OBJECT` | — | Donor-complete native theorem/search/repair/retrieval/synthesis/evolution first-refusal, native obstruction certificate, protected post-expansion transfer, manifest coverage | **Wave B1** |
| **ORION-21 — State as Computation** | `SCIENCE_OPEN`; authoritative responsibility result is negative/insufficient and must replace older positive-assuming narrative | `ROUTING_REQUIRED` after claim shrink/rebuild | — | Integrate negative terminal into live ledger/manuscript, retire stale positive-assuming CI, end-to-end accounting, real procedural validation | **Wave B1** |
| **ORION-22 — Adaptive State Reasoning** | verifier-backed SAT/path/allocator transfer with 9/9 zero-regret bounded panel; `TOP_TIER_PROMOTION_PENDING` | **TMLR** — active Wave-A route | stronger route after public stop/go transfer | Named robustness suite across price shift/task shift/hidden parameter + Wave-A final package | **Wave A**, then B2 if promoted |
| **ORION-23 — Responsibility-Carrying State** | strong bounded responsibility-relative certified-reuse result; 60/60 with adverse donor behavior retained; `TOP_TIER_PROMOTION_PENDING` | **JAAMAS** — active Wave-A route | stronger route only with externally determined responsibilities in real workflow | Wave-A final package; public real research/agent workflow responsibility ground truth for promotion | **Wave A**, then B2 if promoted |
| **ORION-24 — ORION RSE** | controlled governance/conformance result preserved; independent top-tier promotion still `CANNOT_CHECK` | `ROUTING_REQUIRED` | — | Execute R1 frontier-agent, R2 blinded-expert and R3 longitudinal negative-history ablation with recall/resource costs; then venue audit | **Wave B2** |
| **ORION-25 — ORION Research Harness** | `SCIENCE_RED / SCIENTIFIC_OBJECT_NOT_YET_EARNED` for standalone paper; harness engineering evidence only | `ROUTING_REQUIRED AFTER SCIENCE OBJECT` | — | Chained Ed25519 attestation with false-rejection measurement, production fault injection, overhead, protected paper-level result + independent verification | **Wave B1** |

## Active closure waves

### Wave A — eight nearest honest specialist packages

Canonical set: **ORION-05, ORION-09, ORION-10, ORION-14, ORION-17, ORION-19, ORION-22, ORION-23**.

Normative files:

- `WAVE_A_PUBLICATION_CLOSURE_MANIFEST_V1.json`
- `PUBLICATION_CLOSURE_WAVE_A_V1.md`
- `publication_closure/WAVE_A_SPECIALIST_TARGETS_V1.json`
- `publication_closure/wave_a/`
- final receipt: `publication_closure/receipts/WAVE_A_SPECIALIST_CLOSURE_V1.json`

Policy: `GOOD_SPECIALIST_FIRST__TOP_TIER_OPTIONAL`. A top-tier experiment may remain open without blocking an honest bounded specialist object; a failed or missing specialist requirement does block it.

**Current control-plane state:** `CLOSURE_IN_PROGRESS`. The latest completed materialization attempt at head `231aaa15b7bb2104d5893e0ff62b0ad38ca93a76` failed **before package generation** because the Q/QG publication hygiene checker was invoked on a push without PR base/head scope and therefore compared against its much older `ORIGINAL_CUT`. That classified inherited Q/QG science history as publication-branch mutation. This is a publication-control baseline defect, not evidence that those scientific results failed. The repair must change the scope context / ancestry measurement; it must **not** revert or delete valid science. No Wave-A paper is upgraded to `READY_SPECIALIST` until a newer final receipt is generated and passes.

### Wave B1 — science-object / contradiction closure

Priority: **ORION-15, ORION-20, ORION-21, ORION-25**.

These papers are not primarily formatting problems. The next work is theorem/experiment/protocol/result work:

- ORION-15: protected self-improvement campaign + strong matched baselines/ablations + harmful-transfer accounting;
- ORION-20: donor-complete native first-refusal and protected transfer/obstruction science;
- ORION-21: make the authoritative negative result load-bearing and run real procedural validation;
- ORION-25: attestation/fault-injection/overhead result strong enough to constitute a standalone scientific object.

A negative result may close a paper by **shrinking/reframing** the claim. We do not rerun until a desired sign appears.

### Wave B2 — external/top-tier promotion

Priority: **ORION-16, ORION-18, ORION-24**, followed by Wave-A papers only when their specialist object is already safe and the stronger discriminator is worth running.

The promotion programme never invalidates a correct bounded specialist result. `TOP_TIER_READY` requires the full promotion receipt: exact commit, current donor/literature state, frozen protocol/evaluator/task identities, raw/derived digests, independent verification/adjudication, hostile-review disposition, clean reproduction, manuscript/claim-ledger bindings and venue-facing package.

### Wave C1/C2/C3 — portfolio reconciliation and second-tier closure

- **C1:** ORION-01–04 — reconcile the newest 01–05 convergence authority, close the explicitly open scientific gates, then build target-specific packages.
- **C2:** ORION-06–08 — refresh venue/nearest-work authority, replay final bounded Q2/Q3/Q4 results and bind current submission bytes.
- **C3:** ORION-11–13 — restore ORION-11 package authority; retain ORION-12/13 bounded ready scopes; revalidate current official venue rules and exact final bytes.

## Wave-A science checklist

| Paper | Science that is already load-bearing | Science still open for stronger route |
|---|---|---|
| ORION-05 | support-two theorem/counterexamples + result-bound R11 sparse-direct execution and independent checks | independent public compiler family + measured production crossover/resource discriminator |
| ORION-09 | exact family-specific geometry + falsified finite feature laws | broader-family/general theorem or independent public compiler family |
| ORION-10 | layered exact certificate claim + retained classifier refutation | second compiler family + downstream decision value |
| ORION-14 | verification-axis theory + bounded protected battery; H3 null retained | none required for the current TMLR object |
| ORION-17 | T7.1–T7.3 / three executed non-synthetic change classes | target ambiguity + stronger public donor/lens transfer |
| ORION-19 | real-data positive/null/negative cases + causal diagnostic + corrected resource ledger | hostile format/representation attacks + public multi-model/procedural breadth |
| ORION-22 | verifier-backed three-family 9/9 zero-regret panel | price/task/hidden-parameter robustness + public stop/go transfer |
| ORION-23 | responsibility-shift + CNF/donor/certificate transport with independent verification | externally determined responsibilities in a real workflow |

## Common scientific gates for every paper

Before any paper is called ready, check the following atomically:

1. **Identity:** canonical paper id, title and manuscript object are unambiguous.
2. **Claim boundary:** every headline statement maps to a theorem/result/evidence artifact; all exclusions are visible.
3. **Nearest work:** primary-source refresh is current enough for filing, donor mechanisms are subtracted, and novelty is residual rather than rhetorical.
4. **Protocol custody:** decisive experiments were frozen before outcomes; evaluator/task/split/budget/custody identities are bound where required.
5. **Negative history:** null, adverse, contaminated, failed and `CANNOT_CHECK` outcomes remain first-class.
6. **Independent verification:** a second implementation/replay/adjudication verifies the scientific result rather than merely re-running the same wrapper.
7. **Hostile tests:** representation changes, denominator drift, leakage, retries, invalid inputs and other paper-specific failure modes cannot silently promote a claim.
8. **Reproduction:** clean-environment reproduction regenerates the load-bearing result from accessible bytes or explicitly records inaccessible authority.
9. **Manuscript binding:** abstract/results/limitations/conclusion agree with the current claim ledger and evidence.
10. **Submission bytes:** the exact target-specific source/PDF/supplement are content-addressed and visually audited.

If any required item is unavailable, the correct state is `CANNOT_CHECK` or a narrower claim — never inferred PASS.

## Venue routing rules

- A venue is chosen for the **earned scientific object**, not the aspirational broad programme.
- A specialist/second-tier submission may proceed when its bounded object is genuinely complete even if a top-tier discriminator remains open.
- A stronger venue may be attempted only after the paper-specific discriminator closes; prose cannot substitute for it.
- `ROUTING_REQUIRED` rows are active work, not missing documentation to be guessed away.
- Official venue requirements are volatile. Re-check scope, article type, anonymity, data/code policy, AI-use declarations, page/word limits, fees and submission system immediately before filing.
- Human-only fields — authors, affiliations, funding, conflicts, CRediT/acknowledgements where required, AI-use declarations and portal attestations — are never fabricated by automation.

## Status-update discipline

A scientific or publication wave that changes a paper's real state must update this README in the same branch/PR **and** point to the new authoritative result/receipt. The README records the state; it does not create it.

When a new result arrives:

1. verify raw/protocol/result identity and independent check;
2. update the paper claim ledger / readiness authority;
3. update venue implications only if the scientific object changed;
4. update this dashboard;
5. rebuild and bind submission bytes only after the science is stable.

This order is intentional: **fix and verify the science first, then refine the paper.**

A paper may describe only mechanics present in the canonical ORION registry or explicitly label a mechanic as proposed/research-only. Framework-changing commits must update the paper snapshot when they alter a published mechanic, state coordinate, authority rule, saturation rule, or nearest-work/novelty boundary.

Nearest work is part of the scientific object, not a citation appendix. Each flagship claim must have a nearest-work case recording mechanisms to `ADOPT`, `ADAPT`, `COMPOSE`, `DEFER`, or `REJECT`; an open nearest-work route blocks a novelty conclusion.

Passing repository tests or obtaining a `CANDIDATE_DELTA` cannot authorize an external novelty or empirical-superiority claim. The flagship programme separates **local falsifier gates** from **external promotion gates**. A paper is not publication-ready while its external gate is `CANNOT_CHECK`.

The full framework/paper/Q-series rules are in `SYNC_CONTRACT.md`.

## Current flagship status

1. **Paper I — Recursive Epistemic Reconstruction.** Scoped manuscript: explicit `K/W/M` state, typed responsibility-targeted reframing, dependency-directed reopening, the canonical mechanic-cell representation, recursive mechanic self-audit, and hidden formulation/search-universe falsification.
2. **Paper II — Open-World Scientific Knowledge Discovery.** Discovery/search paper: earned route independence, question-framed memory, route/task stopping, and recall-first evaluation.
3. **Paper III — Global Knowledge Portrait.** Absorption/synthesis paper: source projections, scientific meaning, identity/context/measurement mapping, GLUE/obstructions, typed ignorance, and recoverable portraits.
4. **Paper IV — Verified Scientific Discovery.** Scientific-authority paper: content-bound evidence, independent checks, protected evaluation, typed non-escalation, and `CANNOT_CHECK`.
5. **Paper V — Self-ORION.** Scoped manuscript: persistent failure/issue knowledge, causal discrimination, challenger/invention governance, isolated change control, replay/fresh transfer, protected assurance, negative-history retention, and no self-promotion.

## Flagship falsifier V1

The deterministic local five-paper suite passed at branch commit `8a8a7feed588363f8e2cd820d3399a33b7af3074`, CI run `31933432314`. It caused framework changes rather than merely producing scores: an over-broad Paper-I reframe gate was repaired, Paper III gained `ScientificMeaningProjection.v1`, and Paper V absorbed issue-centric persistence as `DevelopmentIssue.v1`.

The stronger external gates for **all five papers remain `CANNOT_CHECK`** until matched nearest-work baselines, fresh tasks/gold data, and protected evaluations are actually executed.

See `research/paper-programme-v1/FLAGSHIP_FALSIFIER_RESULTS_V1.md` and each paper's `evidence/FALSIFIER_V1.md`.

## Verified RSE successor synchronization — 2026-08-20

The paper programme now also consumes the bounded recursive-scientific-evolution falsifier as **successor research only**. The exact suite verifies task/standing separability, finite successor-state non-identifiability, delayed later-generation scientific errors from lost lineage, and a CEGAR refinement demonstration. Its strongest registered state-schema result is deliberately subtractive: a fixed generic justification condition language closes DPAIR-1..4 and therefore strikes bespoke projection-schema superiority on that scope.

No flagship headline claim is widened by this result. `JReach_B(F,x,C|kappa)`, mutable-framework/protected-constitution separation and reconstructive-lineage + task-relative-working-projection remain framework definitions/design principles, not newly proved universal theorems.

Canonical synchronization files:

- `RSE_VERIFIED_SUCCESSOR_HANDOFF_V1.md` — paper-tree boundary;
- `research/paper-programme-v1/RSE_P1_P10_HANDOFF_2026-08-20.md` — ORION-11–ORION-20 ownership map;
- `research/extensions/meta-orion-recursive-scientific-evolution/FORMAL_VERIFICATION_CLOSURE_V1.md` — executable theorem/definition disposition after final CI binding.

## ORION-Q publication wave — final internal spec 2026-08-22

The historical ORION-Q programme has a separate four-paper publication wave.
These packages are outside the five-paper **flagship** programme, but their
canonical identities are ORION-05–08 in the same flat `ORION-NN` registry.
“Closed” in the older wave record refers only to that bounded internal spec; it
does not override the current ORION-05 science and authority gates linked
above.

The machine-readable publication contract is `Q_SERIES_FINAL_SPEC_V1.json`; the human readiness record is `Q_SERIES_FINAL_READINESS_2026-08-22.md`. Canonical publication bytes are protected by `Q_SERIES_CONTENT_BINDING_V1.json`, and the framework/harness checks are defined in `src/orion/programme/q_series_sync.py` and `packages/orion-research-harness/src/orion_research_harness/publication_contract.py`.

| Q paper | Role | Canonical manuscript | Current bounded internal status |
|---|---|---|---|
| `orion-05-tare-expressivity/` | quantum-compilation mathematics | `MANUSCRIPT_SUBMISSION_DRAFT.md` | bounded `kappa_R6M=2` core/package complete; current science closure, runtime candidate, external-authority, and submission gates remain open under convergence V1 |
| `orion-06-recursive-recovery/` | negative-result recovery methodology | `MANUSCRIPT_V2.md` | complete single-programme case study; cross-domain protocol is optional successor research |
| `orion-07-dual-instrument/` | scientific decision instruments / deferred scoring | `MANUSCRIPT_V2.md` | complete systems/benchmark-definition paper with one V0 measurement; calibration study deferred |
| `orion-08-typed-state/` | typed/scoped epistemic state under partial knowledge | `MANUSCRIPT_V2.md` | complete exact-synthetic mechanism/benchmark paper; real-domain study deferred |

Each Q directory now carries a `REPRODUCE.md` and `SUBMISSION_PACKAGE.md` in addition to its canonical manuscript/ledger materials.

The owner elected to skip a separate external quantum-expert pre-review for ORION-05. The final spec records `SKIPPED_BY_OWNER`; this is not encoded as a scientific PASS and does not create external novelty/quantum authority.

### ORION-05 theorem status

For the frozen R6M shared-Tag TARE-M2 grammar/support-count objective:

- an analytic all-`n` exchange proof gives support <=2 sufficiency;
- the complete support-one family has an exact `n=2` counterexample (`5 < 6`);
- therefore the intrinsic uniform frame-support number is exactly `kappa_R6M = 2`;
- the proof's only weight-two parity obstruction is realized by the exact frame-for-Tag coupling witness;
- the original large finite enumerations remain independent verification, not the logical basis of the publication proof;
- a final exact-statement literature refresh records `NOT_LOCATED_IN_BOUNDED_SEARCH__NOT_NOVELTY_CERTIFICATE` rather than claiming absolute novelty.

Canonical proof/novelty artifacts include `HUMAN_PROOF_R6S_2026-08-22.md`, `CLAIM_LEDGER_V2.md`, `NOVELTY_RESEARCH_2026-08-22.md`, `NOVELTY_REFRESH_FINAL_2026-08-22.md`, and `FIGURES_PLAN_V2.md`.

### Q/QG claim boundary

ORION-QG remains a separate successor publication wave. Q papers may cite QG to disclose later limitations/follow-up, but must not back-port QG novelty into Q claims. In particular, later R6I support-one, objective cones, SixLCU/StabPrep results and refined support-two TARE subregimes belong to QG papers.

RAKL papers remain immutable provenance and are selectively remapped in `legacy-rakl-map.md`.
