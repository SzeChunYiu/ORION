# ORION publication disposition matrix V1

**Purpose:** the gating artifact for issue #1701 section E, which closes only when every
ORION-01…25 section carries **one checked final disposition**.

- **Date:** 2026-08-29
- **Assessed tree:** `origin/main` only. No `chatgpt/*`, `codex/*`, `claude/*` or `shadow/*`
  branch content was adopted or credited. Where a result is known to exist only on a branch,
  the row says so and does **not** count it.
- **`scientific_authority_delta`:** `NONE`. This matrix grades readiness and terminal state.
  It does not create, upgrade, or ratify any scientific claim.
- **Same-researcher AI replays are not external investigators** and are never counted as
  external verification anywhere below.

## How each disposition was assigned

`BOUNDED_PAPER_READY_TO_FILE` is asserted only when the paper has (i) a named canonical
manuscript on `main`, and (ii) **no open scientific evidence gate** — that is, what remains
is production work (venue selection, PDF build, submission-date literature refresh,
byte manifest). Missing PDFs are production, and are always named in the blocker column,
because #1701's global gate demands "all exact PDFs visually audited" and that gate is
**currently unmet** for every row whose blocker names a PDF.

`TOP_TIER_SUCCESSOR_NOT_SUPPORTED__BOUNDED_RETAINED` requires a successor that was actually
**executed and graded adverse or null**. It is never used for a successor that was merely
never attempted.

**One string, two meanings — read the row before reading the terminal.** Of the five
papers carrying it, only **ORION-02** had a successor come out against it: two counted
revival attempts, R23 and R24, both graded adverse on contested comparisons against a
no-geometry lexical control. The other four — **21, 22, 23, 25** — *declined promotion
on their own favourable terminals*, under stop rules frozen before the outcome was seen.
ORION-25 states it outright: "That rule applies, and it applies on the favourable
outcome." For those four the terminal means **scope deliberately not broadened**, not
**experiment came out adverse**, and their controls are stronger than ORION-02's rather
than weaker — ORION-23's control V2 caught a tautology in its own ground truth before it
could ship (`papers/POSITIVE_DEMONSTRATION_CONTROL_V1.md`). Treating the five as one
class reads a discipline as a defeat.

`NEW_SUCCESSOR_QUESTION_REQUIRED__NO_RESCUE` is used where #1701's own paper section states
that any successor must carry a new frozen identity and cannot rescue the old claim.

Two rows carry the non-enum marker **`NO_BOX_EARNED_ON_MAIN`**. That is deliberate. For
those papers no section-E box is truthfully checkable from `main` today, and inventing one
would defeat the purpose of the gate. Each such row names exactly what would earn a box.

## Global findings that settle whole columns

1. **`BOUNDED_PAPER_FILED` is unavailable to all 25 rows.** A repo-wide search for filing
   receipts (`SUBMISSION_RECEIPT|BOUNDED_PAPER_FILED|FILED_ON|submitted_on`) over `papers/`
   returns **0 files**; the control pattern (`READY_TO_FILE|READINESS`) returns 134 files on
   the same search, so the search is working and the absence is real. No ORION paper has been
   submitted anywhere.
2. **`TOP_TIER_SUCCESSOR_EARNED` is earned by zero papers.** Every executed successor on
   `main` graded adverse, null, or ungradable. The programme's one genuine candidate
   (ORION-17's prospective density result) is **not on `main`**.
3. **Two papers have no PDF anywhere under `papers/`**: ORION-02 and ORION-04.
   This finding previously read *nine* — ORION-02, 04, 05, 06, 07, 08, 09, 10, 19 — and
   was correct when written on 2026-08-29 at 07:33. It is superseded twice over.
   #1719 gave ORION-07 and ORION-09 submission-package and frozen-packet PDFs 39 minutes
   later, and #1731 then imported a canonical `manuscript/main.pdf` for all seven papers
   that had a `manuscript/main.tex` entry point but no committed render.
   **Every paper with a manuscript entry point now has a byte-pinned PDF**: 21 `main.tex`
   against 22 `manuscript/main.pdf`, the extra being ORION-03's, which is built by pandoc
   rather than latexmk. Confirmed by `manuscript-clipping-audit` passing on `main` at
   `87e2bcb33`, which rebuilds every manuscript under the pinned toolchain and requires
   byte equality — so the renders are verified, not merely present.
   The two remaining papers are not a build failure. Neither carries a
   `manuscript/main.tex`; both are Markdown manuscripts (`MANUSCRIPT_V3.md` and
   equivalent), so the latexmk rebuild never sees them and the byte-identity gate does not
   cover them. ORION-03 shows the path — a pandoc/tectonic build, committed and audited
   for clipping — but that route is outside the epoch-pinned regime the other 21 sit in,
   which is an asymmetry a referee could notice and is worth closing deliberately rather
   than by accident.
   Build recipe: `papers/PDF_CANONICAL_BUILD_RECIPE.md`. The canonical bytes come from the
   audit's own `Archive rebuilt PDFs and logs` artifact, so the builder that produces a
   render and the gate that asserts its bytes are the same builder.

4. **Defect — two submission bundles declare a manuscript PDF they do not ship.**
   ORION-12's `journal_package/current_revision/` and ORION-13's
   `journal_package/wave1_current/` are journal submission bundles — cover letter, anonymous
   review archive, source zips, `SUBMISSION_MANIFEST.json`. Both manifests declare
   `manuscript.pdf` as an artifact (ORION-13's declares it twice) and **neither ships it**.
   Their `SHA256SUMS` pin a digest for it that does **not** match the parent package's
   `manuscript.pdf`, so it names an earlier render present nowhere on `main`.
   This is a filing blocker, not bookkeeping: the bundle a journal would receive is missing
   the manuscript it declares. It cannot be closed by copying the parent PDF in — that would
   substitute different bytes for the ones the manifest names — so it needs the bundle
   rebuilt by its owner. Recorded in `CONTENT_BINDING_DRIFT_BASELINE_V1.json` as
   `kind: SUBMISSION_BUNDLE_INCOMPLETE`; zero bytes have drifted in either paper.
   **ORION-05 has the same defect by a different route.** Its `journal_package/SHA256SUMS`
   declares `.github/workflows/orion05-wave1-closeout.yml`,
   `journal_package/manuscript.pdf` and
   `tests/unit/publication/test_orion05_wave1_manuscript_surface.py` — all three exist only on
   branches that never merged, and no commit on `main` ever removed them, so the package
   declares artifacts the repository has never contained. It also writes repo-root-relative
   paths where every other package writes paper-root-relative ones, which is why the currency
   survey reports 40 of 40 missing rather than the true 25 matching / 12 drifted / 3 absent.
   Recorded as `kind: PACKAGE_DECLARES_ABSENT_ARTIFACTS`.

4. **Defect — stale paper IDs inside four readiness records.**
   `papers/orion-05-*/JOURNAL_READINESS.md` is headed "ORION-01 journal-readiness record";
   orion-06's is headed "ORION-02"; orion-07's "ORION-03"; orion-08's "ORION-04". The
   *content* matches the containing directory (TARE support-two, recursive recovery, dual
   instrument, typed state); only the printed ID is wrong — a partial Q1–Q4 → ORION-05–08
   rename. The drift is **not confined to those four files**: ORION-07's whole lane uses
   "ORION-03" as its internal ID, including the frozen
   `Q3_REPLACEMENT_PROSPECTIVE_PROTOCOL_V2.md` and
   `CLAIM_LEDGER_PROSPECTIVE_CASE_SERIES_2026-08-23.md`, whose instrument slots are named
   `ORION-03-R1` and `ORION-03-R2`. These IDs collide with the real ORION-01…04 papers and
   will mislead any reviewer or checker keying on the printed ID. The fix is a rename, not
   science — but it reaches frozen protocol files, so it must be recorded as an aliasing
   note rather than by editing frozen bytes.
5. **ORION-16/17/18's structural gate PASSES — corrected.** An earlier version of this
   matrix claimed their terminal was "not computable from `main`" because
   `PEER_REVIEW_READY_PACKAGE.md` is referenced at paths that do not exist. **That was
   wrong**, and the error was generalizing from a broken human-readable link to a broken
   computation without checking the consumer. The authoritative consumer is
   `papers/candidates/submission/check_peer_review_ready.py`, which resolves
   `ROOT = parents[3]` → `papers/candidates/PEER_REVIEW_READY_PACKAGE.md` — a path that
   **exists**. Run on current `main` it prints
   `P6-P8 peer-review-ready structural gate: PASS` and exits 0. The terminal is computable,
   and one of its two conjuncts is already observed green.

   What remains stale is only the **human-readable relative links** in six documents:
   `JOURNAL_READINESS.md` uses `../PEER_REVIEW_READY_PACKAGE.md` and
   `JOURNAL_READINESS_V2_1.md` uses `../../PEER_REVIEW_READY_PACKAGE.md`, where both should
   be `../candidates/PEER_REVIEW_READY_PACKAGE.md`. These mislead a human reader and feed
   nothing. **Low priority, and deliberately not fixed**: all six are digest-bound in both
   `CONTENT_MANIFEST_V2.json` and `SHA256SUMS` for ORION-16/17/18 — the three papers
   currently `BOUND_CURRENT` and the ones the binding ratchet depends on. Editing them
   forces a manifest re-pin on exactly those papers, which is real risk to a passing guard
   for a cosmetic gain.

6. **No journal package on `main` is render-current.** Only six papers have a
   `journal_package*` directory at all: ORION-01 (as `_A`/`_B`), 11, 12, 13, 14, 15. The
   owning generator `scripts/write_render_closure_state.py` globs
   `papers/*/journal_package`, so it covers five of them, and **every committed state file
   it has produced reads `SUPERSEDED`**:

   | Package | State | Drift |
   |---|---|---|
   | ORION-11 | `SUPERSEDED` | 20 of 31 pinned inputs drifted (`main.tex`, `bibliography.bib`, section sources) |
   | ORION-12 | `SUPERSEDED` | 18 of 31 pinned inputs drifted (`bibliography.bib`, figure sources, manifest) |
   | ORION-13 | `SUPERSEDED` | packaged PDF 20pp vs built manuscript **45pp** |
   | ORION-15 | `SUPERSEDED` | 37pp vs 37pp — equal length, so the drift is in **content, not extent** |

   The state file's own wording for the page-count cases is that the packaged PDF "is a
   render of an earlier manuscript; it must be re-rendered, **and its claim-to-PDF audit
   re-run**, before the package is submitted." A re-render alone is not sufficient.

   **ORION-14 has a `journal_package/` but no committed `RENDER_CLOSURE_STATE.json` on
   `main`.** Running the generator produced `SUPERSEDED` at packaged 19pp vs built 28pp
   (reported by the team lead from a tree carrying adopted Codex wave1 artifacts; the same
   run reported an ORION-05 package as `CURRENT` at 8pp vs 8pp, and ORION-05 has no
   `journal_package` on `main` either). I could **not** verify either line against `main`,
   because neither file is there. Both are recorded here as pending landing.

   **ORION-01's packages are outside the generator's glob.** `journal_package_A` and
   `journal_package_B` do not match `papers/*/journal_package`, so their render closure has
   never been computed. That is `CANNOT_CHECK`, not current.

   **This changes no disposition.** Render drift is production work, not an open scientific
   evidence gate, so it does not move any paper between section-E boxes. It changes the
   blockers and the filing order, and it makes the picture materially worse.

---

## The matrix

| # | Paper | Disposition | Evidence path(s) on `main` | What blocks filing | Top-tier gap — is it supported? |
|---|---|---|---|---|---|
| **01** | certificate-realization | `NEW_SUCCESSOR_QUESTION_REQUIRED__NO_RESCUE` | `papers/orion-01-certificate-realization/theory-A-CLAIM_LEDGER_R2.md`, `theory-B-CLAIM_LEDGER_R2.md`, `journal_package_A/main.pdf`, `journal_package_B/main.pdf`, `experiments/contextual-move-completeness-v1/CLAIM_DISPOSITION.md`, `papers/publication_closure/wave2/WAVE2_DISPOSITION_V1.json` | WAVE2 lists four open items: `INDEPENDENT_PROOF_REVIEW`, `PRIMARY_SOURCE_NOVELTY_AUDIT`, `HOUSE_STYLE_DECOUPLING_OF_SIBLING_REFERENCES`, `FINAL_JOURNAL_PACKAGES`. PDFs exist for both split packages, but `journal_package_A`/`_B` fall **outside** the render-closure generator's `papers/*/journal_package` glob, so neither PDF's currency has ever been computed — `CANNOT_CHECK`, not current. | The completeness successor **ran** and reached `T1_QUOTIENT_REPAIRS_COMPLETENESS_ONLY` — quotient repairs completeness only; source-completeness is not proved. #1701 requires a *new frozen successor identity* and admits the old Round-3 outcomes as derivation/adverse evidence only. Bounded split (A: alphabet-Davenport normal form; B: certificate-complexity vs intrinsic-support separation) is the ceiling. |
| **02** | fiberguard-finite-fibre | `TOP_TIER_SUCCESSOR_NOT_SUPPORTED__BOUNDED_RETAINED` | `papers/orion-02-fiberguard-finite-fibre/CLAIM_LEDGER_V3.md` (V3-C10, V3-C11), `rounds/r23-density-backoff-revival/FIBERGUARD_..._R23_TERMINAL.txt` = `C_R23_PMLB_BACKOFF_COVERAGE_IMPROVED_BELOW_GATE`, `rounds/r24-arm-conditional-fibres-revival/`, `experiments/refinement-to-certifiability-v1/CLAIM_DISPOSITION.md` | **No PDF.** WAVE2 remaining: `ADOPT_R24_CONTROLLING_EVIDENCE`, `REWRITE_CANONICAL_MANUSCRIPT`, `INDEPENDENT_ALGEBRAIC_STATISTICS_REVIEW`. | Two executed revival rounds both adverse: R23 coverage 32/44 below the 0.95 gate against a 39/44 lexical control; R24 reached 44/44 coverage but `CERTIFICATE_INVALID` with 20/44 strict held-out violations, and the lexical control also reached 44/44. The negative control matched or beat the registered geometry in **both** rounds. V3-C11 records that the registered α=.10 full-coverage goal is arithmetically infeasible on that data. The theory (V3-C1…C7 all PROVEN) is the ceiling; the E2/OpenML-CC18 prospective successor is unrun and would need a new identity. |
| **03** | typed-merge-falsification | `BOUNDED_PAPER_READY_TO_FILE` | `papers/orion-03-typed-merge-falsification/CLAIM_LEDGER_R2.md` (D2-C1…C7 PROVEN, C8 DONOR-OWNED, C9 OPEN, C10 FORBIDDEN), `manuscript/main.pdf`, WAVE2 ORION-03 entry | Venue/article type unselected; submission-date literature closure; #1701 asks to re-verify the 1,962 external trust-store merge tasks / 46 hybrid obstructions binding — **not verified in this pass**. | Successor (E15: cosign / python-tuf / in-toto cross-trust-system transfer) **never attempted**, so no negative exists. WAVE2 holds `broad_methods_significance: WITHHELD_UNTIL_REUSABLE_EVALUATOR_AND_EXTERNAL_DOMAIN`. Bounded algebra + falsification calculus is fileable; top-tier needs ≥2 independent ecosystems with native-verifier gold. |
| **04** | rooted-completion-certificates | `CANNOT_CHECK_EXTERNAL_AUTHORITY__BOUNDED_RETAINED` | `papers/orion-04-rooted-completion-certificates/evidence/crb-full-replay/successor-v1/engine_b/SUBMISSION_BLOCKER.json`, `evidence/crb-full-replay/post-execution/job-3544056/TERMINAL.txt`, `successor-v1/DONOR_DISPOSITION_V1.json` | **Authorization, not compute.** `live_authorization: ABSENT`, `AWAITING_NEW_ONE_SHOT_AUTHORIZATION`. No PDF. | `SUBMISSION_BLOCKER.json` records `d2: CANNOT_CHECK`, `d3: CANNOT_CHECK`, `d4: OPEN` with `d4_rounds_consumed: 0`, `external_authority: false`, `journal_authority: false`, `machine_established_externality: false`, and `operator_attestation: USER_SUPPLIED_UNVERIFIED_BY_MACHINE`. The prior CRB replay terminal is `..._FAILED_CENSUS_RECEIPT_SERIALIZATION__D2_D3_AUTHORITY_CANNOT_CHECK`. The exact `D_4(C_5^3)=30` handoff cannot be graded without an authorization the machine cannot establish. |
| **05** | tare-expressivity | `CANNOT_CHECK_EXTERNAL_AUTHORITY__BOUNDED_RETAINED` **(box fit imperfect — see note)** | `papers/orion-05-tare-expressivity/experiments/global-obstruction-basis-v1/result/census-3551911/CAMPAIGN_TERMINAL_V1.md` = `CANNOT_CHECK__CHECKER_DISAGREEMENT`; `papers/ORION05_CANONICAL_MANUSCRIPT_DECISION_V1.md`; `orion-05-tare-expressivity/JOURNAL_READINESS.md` (`INTERNAL_REVIEW_PASS__BOUNDED_CLAIM / SUBMISSION_GATES_OPEN`) | **No PDF.** Venue unselected. Readiness file is mis-headed "ORION-01" (finding 4). Canonical manuscript is `MANUSCRIPT_V3_REFINED.md`. | Two lanes, decided separately. **Bounded:** complete local obstruction classification `kappa_R6M = 2`, review-passed — retained, and it is the ceiling. **Successor (global obstruction basis):** the 5,005-instance census is *complete* (all rows present, not a truncated run) but the control gate failed — the frozen independent checker recovers planted positives the runner misses, so the basis claim **cannot be graded at all**. Note: this is checker disagreement, not an absent external institution. If #1701 intends the `CANNOT_CHECK_EXTERNAL_AUTHORITY` box strictly for the latter, section E needs a `CANNOT_CHECK__CHECKER_DISAGREEMENT` box; ORION-05 and ORION-11 both need it. |
| **06** | recursive-recovery | `BOUNDED_PAPER_READY_TO_FILE` | `papers/orion-06-recursive-recovery/JOURNAL_READINESS.md` (`INTERNAL_REVIEW_PASS__METHOD_CLAIM / SUBMISSION_GATES_OPEN`), `CLAIM_LEDGER_V3.md` | **No PDF.** Venue unselected; hostile literature/donor refresh at submission; regenerate `RECEIPT_INDEX.md` against the final claim set; independent replay of headline receipts on the submission commit. Readiness file mis-headed "ORION-02". | Successor (≥3-domain objective-verifier recovery benchmark over E12 Lean/mathlib + E3 Defects4J) is **explicitly optional** in #1701 and was never run. The bounded object is a methods/provenance paper on executable negative-recovery; its own readiness record states no remaining gate licenses a stronger methodology-effectiveness claim. Bounded is the ceiling unless the 3-domain study is executed. |
| **07** | dual-instrument | `TEMPORAL_PROSPECTIVE_STUDY_FROZEN` | `papers/orion-07-dual-instrument/JOURNAL_READINESS.md` (`MANUSCRIPT_REVIEW_PASS / EVIDENCE_GATE_BLOCKED`), `theory/agreement-nonidentifiability-v1/CLAIM_DISPOSITION.md` = `THEORY_PROVED__INDEPENDENTLY_CHECKED`, `Q3_D2_D3_DISPOSITION_V2.md` | **Awaiting outcomes, not production.** `instances/` is **empty** — the two frozen replacement instances (QG-19 outside-cone sharpness, QG-20 SixLCU objective-rescale) have produced no scientific outcome yet, so only Benchmark V0 exists. No PDF. Lane is mis-headed "ORION-03" throughout (finding 4). The freeze is **real and verified**, which is why this box is earned rather than aspirational: `Q3_REPLACEMENT_PROSPECTIVE_PROTOCOL_V2.md` is frozen at 2026-08-22 against scientific base `main@c5ba39fef`, with a global contract that ORION-07's instruments may read only the base and the protocol, that QG19/QG20 analyzers must not import lane outputs, that `AGREE`/`PARTIAL`/`DISAGREE`/`CANNOT_CHECK` are all valid pre-outcome relations, and that no denominator reduction is allowed. Note the scale: what is frozen is a **2-instance case series** (`n_valid = 3` counting V0, explicitly not authorizing a reliability estimate, kappa, calibration claim or generalization) — **not** the >=20-item prospective registry #1701 describes for the successor. Both are awaiting outcomes. #1701 names this disposition itself: "successor status may `TEMPORAL_PROSPECTIVE_STUDY_FROZEN` until outcomes mature". The agreement-nonidentifiability theorem is proved and independently checked, with `scientific_authority_delta: NONE` for manuscript claims — it *bounds* what agreement can show and forbids a reliability claim. Both the bounded evidence gate and the successor require outcomes that do not exist yet; nothing here can be scored retrospectively without destroying prospectivity. |
| **08** | typed-state | `BOUNDED_PAPER_READY_TO_FILE` | `papers/orion-08-typed-state/JOURNAL_READINESS.md` (`INTERNAL_REVIEW_PASS__EXACT_SYNTHETIC_MECHANISM_CLAIM / SUBMISSION_GATES_OPEN`), `theory/binding-sufficiency-lattice-v1/CLAIM_DISPOSITION.md` = `THEORY_PROVED__INSTANTIATED_ON_FROZEN_RECEIPTS`, no new blocker raised | **No PDF.** Fresh literature closure for the typed/scoped-state composition claim; independent replay of cited receipts; figures after venue selection. Readiness file mis-headed "ORION-04". | Successor (E3 Defects4J + E2 OpenML-CC18 real decision families with frozen actions/utilities, requiring ≥1 predicted no-value stratum *and* ≥1 value stratum) is unrun. External validity is **intentionally not claimed** by the bounded paper, which is the honest position: it is a mechanism-isolation benchmark on exact synthetic designs. Bounded is fileable; top-tier needs the two-family transfer. |
| **09** | compilation-regime-geometry | `NEW_SUCCESSOR_QUESTION_REQUIRED__NO_RESCUE` | `papers/orion-09-compilation-regime-geometry/theory/regime-separator-complexity-v1/CLAIM_DISPOSITION.md` = `THEORY_PROVED__COMPUTED_ON_FROZEN_DOMAIN` with new blocker `MANUSCRIPT_INCOMPLETENESS__SUBMISSION_BLOCKED` (§6); `JOURNAL_READINESS.md` | **`MANUSCRIPT_INCOMPLETENESS__SUBMISSION_BLOCKED`** — the stale abstract does not carry the prospectively frozen enlarged-vocabulary result. No PDF. This is a correctness/package action, not new science. | `k* = 4` on frozen `n ≤ 3`, confirmed by an independent checker on LUNARC — and the law **fails to transfer to the unseen `n = 4`**, which is a mechanism-attribution adverse result, not noise. #1701 is explicit that any successor "must new identity, not rescue": derive the canonical interaction hypergraph from `n ≤ 4` derivation data only, and freeze a deterministic `n = 5` challenge before any cost measurement. No rescue of the four-feature separator is admissible. |
| **10** | certified-static-forecasting | `BOUNDED_PAPER_READY_TO_FILE` | `papers/orion-10-certified-static-forecasting/theory/certificate-explanation-gap-v1/CLAIM_DISPOSITION.md` = `THEORY_PROVED__COUNTS_REPRODUCED`, no new blocker; `JOURNAL_READINESS.md` (`INTERNAL_REVIEW_PASS__LAYERED_CERTIFICATE_CLAIM / SUBMISSION_GATES_OPEN`) | **No PDF.** Fresh literature closure for certified/static resource forecasting; independent replay of QG-3/5/5b/7/7b/7c on the submission commit; runtime presentation measured on the submission environment. | The paper's own structure is the honest one: the **exact cost theorem survives while the explanation vocabulary fails** (QG-7 finds 64 exact hybrid configurations outside the enlarged borrow `B'`). Successor requires either a permanent `Ψ`-vocabulary lower bound (find an equal-`Ψ`, unequal-cost witness) or a genuinely new primitive specified mechanism-first and frozen before fresh labels. Neither has been run. Bounded Quantum-level paper is the ceiling today. |
| **11** | recursive-epistemic-reconstruction | `NEW_SUCCESSOR_QUESTION_REQUIRED__NO_RESCUE` | `papers/orion-11-recursive-epistemic-reconstruction/JOURNAL_READINESS.md` (bounded claim `SUPPORTED`; submission readiness `CANNOT_CHECK`; `journal_package/MANIFEST.json` status `SUPERSEDED`), `experiments/costed-ordering-v1/CLAIM_DISPOSITION.md` = `CANNOT_CHECK__CHECKER_DISAGREEMENT`, `experiments/r4-faithful-comparator-v1/AUTHORITY_DISPOSITION_V1.json` | **Package, not science.** `journal_package/MANIFEST.json` is `SUPERSEDED`, and `journal_package/RENDER_CLOSURE_STATE.json` independently confirms it: **20 of 31 pinned inputs drifted**, including `main.tex`, `bibliography.bib` and the section sources. Both `manuscript/main.pdf` and `journal_package/manuscript.pdf` exist but are stale. | #1701 states plainly: "**True top-tier successor: NONE pre-authorized.**" The R4 faithful comparator **falsified the comparative reading** — ordered Active-VOI matches ORION on the frozen joint criterion — and the costed-ordering result shows the licensed-transition policy earns no economy superiority; that lane is itself `CANNOT_CHECK__CHECKER_DISAGREEMENT` (runner and checker agree on 34/36 fields). Model-general, naturalistic and open-ended superiority are not claimed. Bounded mechanical claim is the ceiling. |
| **12** | open-world-scientific-discovery | `BOUNDED_PAPER_READY_TO_FILE` | `papers/orion-12-open-world-scientific-discovery/JOURNAL_READINESS.md` (`ORION-12 = PEER_REVIEW_READY` on the bounded methods/system-design claim), `JOURNAL_READINESS_V2.md`, `protocol/P2_NARROWED_PUBLICATION_TERMINAL_2026-08-17.md`, `evidence/external_results/P2_V2_ACQUISITION_TERMINAL_2026-08-18.json`, `manuscript/` PDF present | `journal_package/RENDER_CLOSURE_STATE.json` reads `SUPERSEDED`: **18 of 31 pinned inputs have drifted**, including `bibliography.bib`, the P2-1 pipeline figure source and the P2-2 manifest, so the packaged PDF "is a faithful record of an earlier manuscript, not of the current one". Re-render before anything else, then finish the IP&M package: citations, figures, final byte manifest. Superiority is excluded from the ready claim and must stay excluded. | The four-arm TREC-COVID comparison **was run and failed its gate**: recall@100 is 0.0177 below the strongest comparator with bootstrap CI `[-0.0273, -0.0091]` — the interval's lower bound breaches the −0.02 non-inferiority margin — and cost fails outright at 2.8× the reads where the gate demands ≥25% fewer. nDCG@10 is +0.1488 `[+0.1010, +0.1995]` on 42/50 topics, but a criterion outside the gate cannot rescue it. Superiority stays `CANNOT_CHECK`. The BEIR successor (SciFact/NFCorpus/ArguAna, TREC-COVID excluded from fresh confirmation) requires a new identity and is unrun. |
| **13** | global-knowledge-portrait | `BOUNDED_PAPER_READY_TO_FILE` | `papers/orion-13-global-knowledge-portrait/JOURNAL_READINESS.md` (`PEER_REVIEW_READY` for the scoped ORION-13.C5/C9 structured-mapping claim), `evidence/JOURNAL_READINESS_CHECKBOX_AUDIT_2026-08-17.md`, `evidence/NEAREST_WORK_DISPOSITIONS_V1.md`, `evidence/P3_CLOSURE_BLOCKER_ATTRIBUTION_V1.json`, PDF present | Two blockers. (a) `journal_package/RENDER_CLOSURE_STATE.json` reads `SUPERSEDED` at packaged **20pp vs built 45pp** — the packaged PDF renders less than half the current manuscript, so it must be re-rendered **and its claim-to-PDF audit re-run**. (b) The terminal is **conditional**: `PEER_REVIEW_READY` holds "only on a commit whose repository CI and `p3-manuscript-audit` both succeed". That check is `NEEDS_COMPUTE` — it cannot run on this Mac. | Explicitly not claimed: raw-text end-to-end extraction superiority, universal coordinate necessity, expert-atlas adequacy, downstream answer-quality gain. The unique reduct `{polarity}` diagnosis means the **current corpus does not test** the necessity of the other coordinates — a scope limit, not a failure. Successor needs an anti-confounded external semantic corpus (E10 GO / Uberon / EFO) with matched-polarity opposite-verdict pairs so polarity alone cannot solve the task. Unrun. |
| **14** | verified-scientific-discovery | `BOUNDED_PAPER_READY_TO_FILE` | `papers/orion-14-verified-scientific-discovery/JOURNAL_READINESS.md` = `ORION-14 = PEER_REVIEW_READY`, campaign `ORION-14.protected-authority.v2`, publication-authorizing subject `f6e51b5c8f905382b8e2f5568d9035fc14241aa1`, protected run `31976589735`; PDF present | **More than the byte manifest.** `journal_package/` carries no committed `RENDER_CLOSURE_STATE.json` on `main`; running `scripts/write_render_closure_state.py` returns `SUPERSEDED` at packaged **19pp vs built 28pp** (team-lead run, tree with adopted wave1 artifacts — not verifiable on `main`, where the state file is absent). Nine pages of divergence means the packaged `manuscript.pdf` must be **re-rendered and its claim-to-PDF audit re-run**, not assumed to carry over. Then the TMLR submission-byte manifest. Retained `CANNOT_CHECK_ARTIFACT_ABSENT` on the 400-row reduct table — #1701 says explicitly **do not block filing on it**, and no synthetic reconstruction is permitted. | Strongest bounded evidence in the portfolio: H1 false scientific-authority promotion PASS (ORION 0/360 vs frozen comparator 180/360, effect −0.50, CI `[-0.553,-0.447]`); H2 clean coverage PASS (60/60 both, effect 0); custody telemetry PASS with zero protected-identifier hits and zero external-IP connections; eight registered ablations all increase false promotion. **H3 is `NOT_SUPPORTED` and is retained as a null, not converted.** Optional successor (E3 + E12 + E7, three objective-verifier domains) is unrun and separately named. |
| **15** | self-orion | `CANNOT_CHECK_EXTERNAL_AUTHORITY__BOUNDED_RETAINED` | `papers/orion-15-self-orion/JOURNAL_READINESS.md` = `NO_TERMINAL_UNDER_FROZEN_RULES`; `evidence/glm-5.3-attribution-v2/AUTHORITY_DISPOSITION_V1.json`; `top_tier/P5_RESIDUAL_ERROR_REVIVAL_DISPOSITION_2026-08-24.json` | `journal_package/manuscript.pdf` exists but there is **no `manuscript/main.pdf`**, and the package reads `SUPERSEDED` — at 37pp packaged vs 37pp built, so the drift is in **content at equal length**, which is the easiest kind to miss by eye and the reason the claim-to-PDF audit has to be re-run rather than assumed. General governed self-improvement is `CANNOT_CHECK` and **not** peer-review ready. | Read this row carefully: "bounded retained" here retains a **null**, not a positive. The frozen 96-case revision-level panel places FULL_T7 at **12/96 with no registered terminal**. Every baseline and ablation arm is `CANNOT_CHECK` — no-edit control, direct self-edit and the strongest runnable self-improvement baseline are unexecuted; ADAS, DGM and ADIAS are **unavailable comparators**, correctly not replaced by weak proxies. Historical diagnostic attribution is 21/24 with all three residual errors named, two of them HIGH-confidence misattributions. The E16 external model-family transfer is unrun and, per #1701, would **not** count as external-investigator replication even if run. |
| **16** | formal-epistemic-structures-and-mechanics | `BOUNDED_PAPER_READY_TO_FILE` | `papers/orion-16-*/JOURNAL_READINESS_V2_1.md`, `CLAIM_LEDGER_V4.md`, `P6_ACTIVE_CLAIM_AUTHORITY_V1.json`, `TOP_TIER_PROMOTION_V1.md`, `SHA256SUMS`; PDF present No open **evidence** gate: the V4 ledger carries a positive terminal, an exhaustive bounded support row and an explicit scope ceiling, with no `CANNOT_CHECK`/`OPEN`/`BLOCKED` claim row. What remains is packaging and CI. Its terminal is `PEER_REVIEW_READY := p6-p8-candidate-ci == success AND ci == success on one immutable head`. The **structural gate already passes** on current `main` (`check_peer_review_ready.py` → `PASS`, exit 0), so the single remaining item is **observing one green CI head** — `NEEDS_COMPUTE`, and CI must not run on this Mac. That is an observation, not work. ORION-16 also has **no journal package**, so it has no packaged PDF that can go stale; its PDFs sit at `manuscript/main.pdf` and `manuscript/FINAL_V5.pdf`, and `FINAL_V5.pdf` matches the ledger's named canonical `manuscript/FINAL_V5.md`. Bounded object is complete and is the ceiling for now: terminal `P6_CERTIFICATE_LIFTING_SEMANTICS_SUPPORTED__BOUNDED_FORMAL_DONOR_STACK__IDEAL_PRODUCT_EQUIVALENT`, canonical science manuscript `manuscript/FINAL_V5.md`, three PDFs, `SHA256SUMS`, and exhaustive bounded support at 320 states / 25 minimal separations / 155 sufficiency witnesses / 1,055 strict-subset necessity countermodels / zero donor-conservativity violations, plus a kernel mechanization of the exact Theorem 7 statement at 450 rule applications with a z3 cross-check. The clean-room replay is correctly labelled a **second implementation inside the programme, not external custodianship**. #1701 section A allows a bounded paper to be filed while a named successor stays optional, so active lane #1695 does not block this box. The two theorem packets #1701 names (dependency-closed revalidation; graph quality) are **not present under `papers/orion-16-*`** — that directory holds ledgers, manifests, readiness records and one manuscript dir, with no `theory/` or `experiments/` subtree. #1701 locates them on `claude/orion16-*` branches, which this pass did not assess. #1701 forbids creating a competing protocol while #1695 (real authoritative graph campaign over E4 RTPTorrent / E5 Bazel / E6 Cargo) is active, so the successor is *pending*, not failed — `TOP_TIER_SUCCESSOR_NOT_SUPPORTED` would be a false negative and `EARNED` a false positive. **To earn a box:** repair the dangling package reference, record one immutable green head, then re-grade. |
| **17** | epistemic-navigation-open-worlds | `NO_BOX_EARNED_ON_MAIN` | `papers/orion-17-*/JOURNAL_READINESS_V2_1.md` (three executed non-synthetic change classes: RO-Crate 1.2→1.3 at 14 frozen cases, UCI Wine at 712 protected rows, WDBC 5 folds × 2 states — each at witness-aware `1.0` against value-only and always-reopen baselines); PDF present | The prospective density result is **not on `main`**: a repo-wide search for `*density*` under `papers/` returns only ORION-02's `r23-density-backoff-revival` lane and two mathlib corpus files — zero ORION-17 packet. Draft PR #1716 (P7 content binding) is unmerged, and no standalone AIJ/TMLR manuscript exists. (Its structural gate passes — see corrected finding 5 — so that is *not* among its blockers.) | This is the programme's **only** genuine top-tier candidate: 5/5 held-out prospective predictions across requests/psf, networkx, django, tornado, sympy, threshold 1.5 fixed before outcomes, chronology density→predictions→outcome, independent checker green with negative controls. It still cannot be `TOP_TIER_SUCCESSOR_EARNED`, because the packet is not on `main`, the #1649 one-shot governance conflict is unadjudicated, and there is no standalone manuscript. **Do not harden this into `NO_RESCUE`** — the evidence exists; the binding does not. To earn the box: land the packet path-by-path, adjudicate governance, write the standalone manuscript. |
| **18** | epistemic-authority-autonomous-science | `CANNOT_CHECK_EXTERNAL_AUTHORITY__BOUNDED_RETAINED` | `papers/orion-18-*/JOURNAL_READINESS_V2_1.md` (17 frozen authority contracts executable: five clean native-domain cases, paired blockers, five laundering attacks, `CANNOT_CHECK`, positive registered coercion); PDF present | Structural gate passes on `main` (`check_peer_review_ready.py` → `PASS`); the CI-computed terminal is `NEEDS_COMPUTE`. Neither is the real blocker — see the top-tier column. | #1701 assigns this outcome directly: where the scientific terminal requires expert judgment beyond native rules, mark `REQUIRES_EXTERNAL_HUMAN_OR_INSTITUTION` and **do not fake closure**; the broader empirical top-tier claim "remains blocked unless independent external authority exists". A same-team second implementation strengthens reproducibility only. The bounded authorization/evidence-discharge theory is retained; broader scientific adjudication is structurally, not operationally, unavailable. |
| **19** | structured-epistemic-learning | `NO_BOX_EARNED_ON_MAIN` | `papers/orion-19-structured-epistemic-learning/JOURNAL_READINESS.md` = `P9_BOUNDED_STRUCTURAL_LEARNING_PEER_REVIEW_READY_PR` (target TMLR), `FINAL_RESULT_DISPOSITION_MAP_V1.md`, `P9_FINAL_NOVELTY_DISPOSITION_V1.md`, `experiments/ut3-checkpoint-custody-v1/AUTHORITY_DISPOSITION_V1.json` | **The manuscript body is not on `main`.** `papers/orion-19-structured-epistemic-learning/manuscript/` is an **empty directory**, so the paper fails criterion (i) of this matrix's own `READY_TO_FILE` rule. The terminal is explicitly a **review-branch** state that "does not mean the branch has merged to `main`". `PDF_VISUAL_AUDIT_2026-08-20.md` does pass visual review — but on review-branch head `9d12f3a36051f54d4a8a01e2ba61a473d9c32d50`, as GitHub Actions artifact `9396990591` from workflow `p9-tmlr-pdf` run `32340331816`, which was never committed: 0 PDFs exist under `papers/orion-19-*`. **To earn a box: merge the review branch so the manuscript and its PDF exist on `main`.** | Successor is coverage/transfer, not representation-only repair. The UT3 custody receipt records 4/6 checkpoints available and **zero grid cells executed**, so no grid evidence exists; #1701 forbids executing UT3 until a grid-cell executor with frozen renderers and gold verification exists. The V3 causal-diagnostic transport positive (LCB95 rule, diagnosis accuracy 1.0, all 5 cells agreeing, stable abstention on D-A) sits on `claude/r5-revival-orion19-18-20260828`, not `main`; the V2 D-A `CANNOT_CHECK` and the Qwen scaling negative both stand. |
| **20** | structured-problem-solving | `NEW_SUCCESSOR_QUESTION_REQUIRED__NO_RESCUE` | `papers/orion-20-structured-problem-solving/top_tier/primitive-minimality-v1/CLAIM_DISPOSITION.md` = `T3_PROMOTION_FAILS__NO_UNIQUE_MINIMUM`, `PROMOTION_STOPPED__RETURN_TO_BOUNDED_LANE`; PDF present | Finish the bounded formal manuscript/package. #1701 forbids reordering primitives or running another minimality rescue under the same claim. | Protocol frozen at `051f578a0` before any outcome was read. AND (code 8) and OR (code 14) are **both** minimal singleton bases, so there are **no indispensable primitives**: `G_UNIQUE` holds but `G_INDISPENSABLE` fails, and `G_DONOR` fails by its own frozen operationalisation, which required both. A successor must first write a genuinely new scientific question defining "outside-closure discovery" operationally, freeze a donor set and resource-matched baselines, and use ≥3 external domains with objective native verifiers. No compute may be spent on the old minimality claim. |
| **21** | state-as-computation | `TOP_TIER_SUCCESSOR_NOT_SUPPORTED__BOUNDED_RETAINED` | `papers/orion-21-state-as-computation/experiments/tie-robust-phase-v1/CLAIM_DISPOSITION.md` (controlling terminal of the V1 lane = `CANNOT_CHECK_INSTRUMENT_DRIFT`, unchanged), `experiments/nr07-width-law-falsification-v1/POST_OUTCOME_PROTOCOL_DEVIATION_DISPOSITION_V1.json`, `PEER_REVIEW_READINESS.md`; PDF present | Fold the ten-responsibility negative into the live ledger/manuscript and retire the older positive-assuming CI interpretation. Readiness is scoped to the width-conditioned result only. | The frozen tie-robust successor **was executed** (LUNARC job 3552796, independent checker `PASS`) and returned `T3_TIE_AMBIGUOUS_VERDICT_CHANGING` — it **confirms** the phase-boundary withdrawal rather than rescuing it. A faithful replay of the V1 ladder is impossible: custody terminal `NR07_LUNARC_EXECUTABLE_BYTES_ABSENT`, and only the post-outcome-modified variant survives, in quarantine. The ten-responsibility family result stays negative (LINEAR 3/10, RBF 5/10, KNN 5/10 against a frozen ≥8/10 gate) and was not retuned. |
| **22** | adaptive-state-reasoning | `TOP_TIER_SUCCESSOR_NOT_SUPPORTED__BOUNDED_RETAINED` | `papers/orion-22-adaptive-state-reasoning/experiments/observation-regret-law-v1/CLAIM_DISPOSITION.md` = `T1_REGRET_LAW_HOLDS` / `SCOPED_QUANTITATIVE_LAW__PROMOTION_NOT_EARNED`, `experiments/observation-aliasing-v1/CLAIM_DISPOSITION.md` = `T2_SOME_PRICE_BLIND_CLASSES_EMPTY__PRICE_REFINEMENT_RESOLVES_ALL`, `PEER_REVIEW_READINESS.md` (`CONTROLLED_LIFECYCLE_RESULT_BOUND__PUBLIC_TRANSFER_OPEN`); PDF present | P12A superiority remains **withheld** under `P12A_COMPARISON_VALIDITY_ADJUDICATION_V1.json`. Submission hardening on the P12B controlled result only. | The law is real but scoped: 36 observation classes, 23 with a positive regret floor, max forced regret 700, total 5092, and price refinement closes the floor in 36/36 — all four predictions hold, frozen at `52b4176c9` before outcomes. Promotion is still **not earned**, and the robustness boundary records `price_axis: BROKEN` and `distribution_shift_axis: BROKEN` with `retuned: false`. The second-family transfer (E3 Defects4J *or* E2 OpenML, one chosen before protocol freeze, requiring both zero-regret and positive-regret classes) is unrun. |
| **23** | responsibility-carrying-state | `TOP_TIER_SUCCESSOR_NOT_SUPPORTED__BOUNDED_RETAINED` | `papers/orion-23-responsibility-carrying-state/transport-law-v1/CLAIM_DISPOSITION.md` = `T1_TRANSPORT_LAW_HOLDS`, promotion status literally `TRANSPORT_LAW_ESTABLISHED__PROMOTION_NOT_EARNED__BOUNDED_PAPER_RETAINED`; `PEER_REVIEW_READINESS.md`; PDF present | Authority is **split by sub-claim**: P13B is `READY_FOR_CONTROLLED_P13B_CLAIM__EXTERNAL_VALIDATION_OPEN`, but P13A is `NOT_READY__P13A_SELF_SCORED_SAFETY_ENDPOINT` with `P13A_EMPIRICAL_SAFETY_COST_AUTHORITY_WITHHELD`. A self-scored safety endpoint cannot be filed as an empirical result. | The transport law is exact on 750 cases: the three-valued rule gives 0 unsound and 0 over-revocations with 296 abstentions, pessimistic collapse over-revokes 84 times, optimistic collapse is **unsound 212 times**. `UNKNOWN` is a third outcome, not a bias to pick. The artifact names its own disposition. #1691 live-Git acquisition is active and must not be duplicated; the `REUSABLE`-class successor needs organization-disjoint repositories outside the old 31-repo/14-org corpus, and if non-head reuse turns out non-discriminating the honest terminal is `CANNOT_CHECK_DESIGN_POWER`. |
| **24** | orion-rse | `CANNOT_CHECK_EXTERNAL_AUTHORITY__BOUNDED_RETAINED` | `papers/orion-24-orion-rse/PEER_REVIEW_READINESS.md` — `READY_FOR_EXTERNAL_REVIEW_AS_CONTROLLED_GOVERNANCE-CONFORMANCE_RESULT`, authority `P14_ACTIVE_CLAIM_AUTHORITY_V1.json`, terminal `P14C_SPECIFICATION_SEPARATED_GOVERNANCE_CONFORMANCE_SUPPORTED`, **`external_validity: OPEN`**; PDF present | Scoped to the frozen 28-case seven-implementation register. P14A is "a measurement that could not be taken", not a comparative negative; P14B stays diagnostic because it reuses its own adjudication function. | The control plane is verified but the empirical campaign was **not run** — `CONTROL_PLANE_VERIFIED__EMPIRICAL_CAMPAIGN_NOT_RUN`, and the wiring pilot is explicitly `NOT_AUTHORITY`. Top-tier requires R1 frontier-agent executions, R2 blinded expert adjudication, and R3 longitudinal negative-history ablation. A retrospective replay **cannot** be labelled prospective longitudinal evidence, and same-researcher agents cannot supply the blinded-expert arm. The gap is structural. |
| **25** | orion-research-harness | `TOP_TIER_SUCCESSOR_NOT_SUPPORTED__BOUNDED_RETAINED` | `papers/orion-25-orion-research-harness/experiments/trust-domain-law-v1/CLAIM_DISPOSITION.md` = `T1_LAW_HOLDS_EXACTLY`, promotion `LAW_ESTABLISHED_UNDER_CRYPTOGRAPHIC_INDEPENDENCE__PROMOTION_NOT_EARNED`; `experiments/execution-integrity-v1/CLAIM_DISPOSITION.md` (`ORION25.TRUST_DOMAIN_FRONTIER.v1`, state `PREREGISTERED_NOT_EXECUTED`, `promotion_allowed: false`); PDF present | Bind chained Ed25519 attestation V2 with false-rejection endpoints; Wave-2 closeout. | The bounded law is exact — 1000 cells swept, 1000 matching Theorem T, 0 sufficiency failures, 0 necessity failures, frozen at `da94bf412` before outcomes — and forgeability is exactly `supp(α) ⊆ C`, giving the security parameter `d_eff = |supp(α)|`. But the frontier successor is **preregistered and not executed**, and #1701 requires ≥2 real systems with structurally different trust models where organizational independence rests on genuinely separate governance. Cryptographic independence in one harness is not organizational independence. |

---

## Which #1701 section-E checkboxes each disposition satisfies

Section E closes only when **every** ORION-01…25 section has one checked disposition.
On `main` today, 23 of 25 rows are checkable and 2 are not.

| Section-E checkbox | Count | Papers |
|---|---|---|
| `BOUNDED_PAPER_READY_TO_FILE` | **8** | 03, 06, 08, 10, 12, 13, 14, 16 |
| `BOUNDED_PAPER_FILED` | **0** | none — no filing receipt exists anywhere in `papers/` |
| `TOP_TIER_SUCCESSOR_EARNED` | **0** | none — every executed successor graded adverse, null, or ungradable |
| `TOP_TIER_SUCCESSOR_NOT_SUPPORTED__BOUNDED_RETAINED` | **5** | 02 (successor graded adverse); 21, 22, 23, 25 (scope not broadened, on favourable terminals under pre-frozen stop rules) |
| `CANNOT_CHECK_EXTERNAL_AUTHORITY__BOUNDED_RETAINED` | **5** | 04, 05, 15, 18, 24 |
| `TEMPORAL_PROSPECTIVE_STUDY_FROZEN` | **1** | 07 |
| `NEW_SUCCESSOR_QUESTION_REQUIRED__NO_RESCUE` | **4** | 01, 09, 11, 20 |
| *(no box earned on `main`)* | **2** | 17, 19 |

Total: 8 + 0 + 0 + 5 + 5 + 1 + 4 + 2 = **25**.

### Section-E global gates

| Global gate | State | Why |
|---|---|---|
| all unique evidence on unmerged branches adopted, superseded with reason, or preserved | **NOT MET** | ORION-17's density packet, ORION-19's V3 causal-diagnostic positive, and ORION-16's two theory packets are known to exist only on branches and are not on `main`. |
| no stale branch wholesale merged | **CANNOT_CHECK** | Not checked. This pass adopted nothing, but that is a property of *this pass*, not of the repository's merge history, which needs a `main` merge-commit audit. |
| all manuscripts reflect strongest **admissible** evidence including negatives | **NOT MET** | ORION-09 carries `MANUSCRIPT_INCOMPLETENESS__SUBMISSION_BLOCKED`; ORION-21 must fold the ten-responsibility negative into the live ledger; ORION-11's package is `SUPERSEDED`. |
| all top-tier claims carry donor/literature subtraction | **PARTIAL** | Ledgers do carry explicit `DONOR-OWNED` / `FORBIDDEN` rows (01, 02, 03). Submission-date literature closure is open on essentially every row. |
| all exact PDFs visually audited | **NOT MET, and worse than a page count suggests** | Two papers have no PDF at all (02 and 04, both Markdown manuscripts with no `main.tex` entry point); the other 23 do, and the 21 with a `main.tex` are byte-pinned against the audit's own rebuild. Of the six that have a journal package, **not one is render-current**: ORION-11, 12, 13 and 15 are committed `SUPERSEDED`, ORION-14 has no committed state and returns `SUPERSEDED` when the generator is run, and ORION-01's two packages are outside the generator's glob entirely. Every `SUPERSEDED` package needs a re-render **and** a re-run claim-to-PDF audit. |
| same-researcher clean-room replays labelled precisely | **CANNOT_CHECK** | Held in every artifact inspected — ORION-16's V4.7 explicitly forbids the upgrade "externally reproduced by an outside party", and ORION-18 and ORION-24 are equally explicit — but that is a ~30-file sample, not a repo-wide property. No row in this matrix credits an AI replay as external verification. |

### The two rows that block issue closure

Issue #1701 **cannot close today**, on two rows and one global gate:

- **ORION-17** — the strongest successor evidence in the programme is real but unbound: the
  packet is not on `main`, governance vs #1649 is unadjudicated, and no standalone manuscript
  exists. Landing that packet path-by-path is the highest-value single action on this board.
- **ORION-19** — the manuscript directory is empty on `main`; the paper exists only on its
  review branch. Merging that branch converts this row to `BOUNDED_PAPER_READY_TO_FILE`
  immediately, because its evidence gates are already closed.
- Plus the PDF gate. The *render* half is now met for every paper with a manuscript entry point; what remains unmet is the *visual audit* half, and the six journal packages, none of which is render-current.

Both blocking rows are fixable by **binding work, not new science**. Everything else has a
defensible box today.


---

## Filing order, re-ranked after render closure

The earlier ranking in this programme's reporting put ORION-14, 13 and 12 at the front. All
three carry `SUPERSEDED` packages, so that order was wrong. Ranking by **total remaining
work to a submittable artifact**, not by scientific maturity:

| Rank | Paper | Why here |
|---|---|---|
| 1 | **ORION-16** | Moved up from 3 once its supposed blocker dissolved. Positive V4 terminal, canonical `manuscript/FINAL_V5.md` with a matching `FINAL_V5.pdf`, `SHA256SUMS`, kernel-mechanized Theorem 7 — and **no journal package**, so nothing can be render-stale. The structural gate **already passes** on `main`; the only outstanding item is observing one green CI head. That is an observation, not work. |
| 2 | **ORION-03** | Also very clean: `manuscript/main.pdf` directly under the paper, **no journal package to be stale**, R2 ledger closed (C1–C7 PROVEN, C8 DONOR-OWNED, C9 OPEN, C10 FORBIDDEN). Behind ORION-16 only because it carries a genuine outstanding verification — re-checking the 1,962-task / 46-obstruction binding — plus venue and submission-date literature closure. |
| 3 | **ORION-14** | Still the strongest *evidence* in the portfolio, and its PDF is at `manuscript/main.pdf`. But its package needs a re-render across a nine-page gap plus a re-run claim-to-PDF audit before the byte manifest. Strong science, non-trivial production. |
| 4 | **ORION-13** | Science is ready; the package renders 20pp of a 45pp manuscript. Re-render, re-run the claim-to-PDF audit, then satisfy the conditional CI terminal. |
| 5 | **ORION-12** | Science is ready and the failed TREC-COVID gate is correctly excluded; 18 of 31 pinned inputs have drifted. Re-render, then citations and manifest. |
| — | 06, 08, 10 | Science-closed. Canonical `manuscript/main.pdf` built and byte-pinned by #1731; production only, and no package to be stale. |

Ranks 1 and 2 are close, and neither can be finished from this Mac. The tiebreak is that
ORION-16's remaining item is *observing* a gate whose other conjunct already passes, while
ORION-03's is *performing* a verification. If the board judges the 1,962/46 binding check
cheaper than scheduling a CI head, swap them — nothing else in this table moves.

**ORION-01 is deliberately unranked.** It holds `NEW_SUCCESSOR_QUESTION_REQUIRED__NO_RESCUE`
and its two PDFs have never had their currency computed, so it cannot be placed honestly.

The pattern across ranks 2–5 is one problem, not four: **committed PDFs have drifted from
their manuscripts programme-wide**. Re-rendering is mechanical; the re-run claim-to-PDF
audits are not, and ORION-15 shows why — equal page counts with drifted content is exactly
the case a page-count check passes and an eyeball misses.
