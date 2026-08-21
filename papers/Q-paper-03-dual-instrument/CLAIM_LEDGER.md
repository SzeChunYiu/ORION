# Paper Q3 claim ledger V1

**Manuscript:** `papers/Q-paper-03-dual-instrument/MANUSCRIPT_V1.md`
**Branch:** `claude/orion-harness-verification-b17qdj`
**Date:** 2026-08-21

Format follows the repository's paper claim-ledger convention (cf.
`papers/paper-04-verified-scientific-discovery/CLAIM_LEDGER_V3.md`): each row states the
maximum permitted claim, its authority (the committed receipt/code that grounds it), and
the upgrade the manuscript must never make. Nothing in this ledger grants scientific,
novelty, promotion, or R6 authority.

| ID | Permitted claim | Authority | Forbidden upgrade |
|---|---|---|---|
| Q3.1 | Host capability requests have deterministic content-derived identity (`hostreq:` + sha256 of canonical `{session_id, capability, payload}`), and results are digest-bound to the exact request, with self-validation on load. | CODE: `packages/orion-research-harness/src/orion_research_harness/protocol.py` (L40–52, L131–149, L244–272) | Any cryptographic-security or signature claim; digests are integrity bindings, not signatures. |
| Q3.2 | Receipts are persisted create-only (fsync + `os.link`); re-ingesting identical content is idempotent and differing content for the same request is rejected; both behaviors observed live. | CODE: `workspace.py` L30–48, L279–294; RECEIPTED E2E steps 24b/24c in `development/orion-research-harness/E2E_HOST_DRIVE_VERIFICATION_2026-08-21.md` | Tamper-proof storage against an adversary with filesystem access. |
| Q3.3 | A completed solve replays deterministically from the receipt store with zero new host requests, as observed live. | RECEIPTED: E2E step 22, `development/orion-research-harness/e2e-2026-08-21-receipts/` | Determinism of host re-execution; only replay of recorded receipts is claimed. |
| Q3.4 | Missing/failed capabilities are structured orchestration conditions (exit 2/3), never scientific evidence; broker validation is strict per capability kind and `VERIFY_EVIDENCE` fails closed, requiring a certificate id to pass. | CODE: `broker.py` L29–53, L90–231; `cli.py` L304–311; RECEIPTED E2E steps 3, 25 | Claim that the harness prevents a dishonest host from fabricating receipt content (it cannot; see HOST_PROTOCOL obligations). |
| Q3.5 | `retry-failed` archives only failed receipts, bytes unchanged, freeing the deterministic identity while preserving the failure as auditable history; it healed a live poisoned campaign workspace. | CODE: `workspace.py` L330–358; TESTS: `tests/test_retry_failed.py`; RECEIPTED: `development/orion-q-max-r0/HARNESS_R6_DRIVE_VERIFICATION_2026-08-21.md` §3 | General crash/corruption recovery; the mechanism covers exactly the failed-receipt lane (see Q3.14). |
| Q3.6 | Local capabilities are confined to the project root, process tools are opt-in, output-bounded, timeout-killed by process group, and nonzero exits persist as failed receipts. | CODE: `local_tools.py` L26–34, L157–269; RECEIPTED E2E steps 23–24a | Any OS-sandbox or security-boundary claim; the README and the live receipt (`sandboxed: false`) disclaim it. |
| Q3.7 | Campaign manifests are frozen (digest-checked at decision time), and campaign state/decision/transition receipts form a digest-chained history. | CODE: `campaign_control.py` L395–399; `campaign_protocol.py`; `campaign_runner.py` L485–514; `workspace.py` L457–475 | Claim that chaining alone proves scientific correctness of the chained content. |
| Q3.8 | Campaign decisions are made natively by production ORION control modules over typed observations, with no LLM call and no free text in the decision path. | CODE: `campaign_control.py` L5–26, L395–486; RECEIPTED: `DUAL_HARNESS_LANE_B_RECEIPT.json` `provenance.decided_by` | Claim that manifest *construction* is LLM-free (it is not; see Q3.16). |
| Q3.9 | A malformed `success=true` campaign result is `CAPABILITY_CONTRACT_FAILED` under strict, non-coercing contracts (exact-type equality; string `"false"` is not boolean `False`) and cannot change observations or advance the campaign. | CODE: `campaign_runner.py` L59–184, L312–332, L432–443; `campaign_protocol.py` `ProtectedReference` | Claim that this makes malformed-successful receipts recoverable (they are not; Q3.14/D3). |
| Q3.10 | Unreleased protected references are guarded by a payload/read-path/script-text substring scan that fails closed, and release requires an explicit validated declaration; the reserved stretched-N2 DUCC2 subject was never opened in any cited receipt (`released: false` throughout). | CODE: `campaign_runner.py` L187–263; RECEIPTED: `DUAL_HARNESS_LANE_B_RECEIPT.json`, `harness-r6-drive-2026-08-21/CAMPAIGN_RUN_RECEIPT.json` | General information-flow security; the scan is a custody check on declared surfaces, not taint tracking. |
| Q3.11 | Every campaign state, decision, and transition carries all six `grants_*` authority fields false by construction; deserialization rejects any true value; capability payloads are recursively scanned and authority-true keys rejected as escalation. | CODE: `campaign_protocol.py` L13–24, L76–79; `campaign_runner.py` L18–56 | Claim that authority non-escalation extends to systems outside these schemas. |
| Q3.12 | The campaign layer drove the real MAX-R6 chain four cycles to `R6_PROSPECTIVE_VERDICT_RECORDED__NOT_SELF_AUTHORIZING` with `R6_EARNED = NO` and the protected subject never opened — a frozen scientific negative recorded, not softened. | RECEIPTED: `development/orion-q-max-r0/harness-r6-drive-2026-08-21/` + `HARNESS_R6_DRIVE_VERIFICATION_2026-08-21.md` §4 | Any scientific/novelty claim about R6 content; the negative is the programme's result, cited here only as instrument evidence. |
| Q3.13 | The full harness contract was live-verified end to end: 12/12 CLI commands, 8/8 implemented capability kinds, replay, both failure lanes, tamper rejection, path containment; suite 30/30 (base) and 98/0 (after §3 repairs). | RECEIPTED: `E2E_HOST_DRIVE_VERIFICATION_2026-08-21.md`; `HARNESS_R6_DRIVE_VERIFICATION_2026-08-21.md` §2–3 | "Fully verified" beyond the enumerated surface; `GITHUB` is documentation-only with no implementation. |
| Q3.14 | Two open instrument defects exist and are documented with code paths: (D2) a `success=true` `LLM_COMPLETE` receipt with well-formed envelope but non-JSON `content` crashes the recursive solve with an unstructured traceback instead of a structured failure; (D3) such successful-malformed receipts cannot be archived or corrected, permanently pinning the workspace's deterministic identity. The failed-receipt pinning defect (D1) was repaired same-day with `retry-failed`. | CODE: `src/orion/providers/reasoner/llm.py` L33–48; `recursive_runner.py` L423, L819–857; `cli.py` L282–311; `workspace.py` L293, L342; RECEIPTED (D1): `HARNESS_R6_DRIVE_VERIFICATION_2026-08-21.md` §2–3 | Claiming the instrument is defect-free, or that D2/D3 can corrupt scientific state (they halt or fail the contract; no evidence is admitted). |
| Q3.15 | Benchmark V0 was frozen before either lane's outcome existed; its outcome space makes divergence data (AGREE/PARTIAL/DISAGREE all valid, recorded verbatim with raw receipts). | RECEIPTED: `DUAL_HARNESS_AGREEMENT_BENCHMARK_V0_PROTOCOL.md` (status line, outcome-space section) | Claiming the protocol constrains what verdict was reachable; all outcomes were recordable. |
| Q3.16 | The Lane B manifest represents four materially different responsible layers, each observation-discriminable with a genuine survival region, each mapped to a recording capability so any native outcome could complete the cycle; observations are transcribed with per-field receipt provenance. | CODE+DOC: `domains/orion_q/post_r6o_diagnosis.py` (docstring + `_D0_HYPOTHESES`); RECEIPTED: protocol's manifest-independence requirement | Claiming manifest construction is instrument-independent; it is human/LLM-authored and is listed as a limitation. |
| Q3.17 | First measurement verdict: AGREE on coordinates 1 and 2 — Lane A diagnosed `REPRESENTATION_REGIME_CHARACTERIZATION` / move `REGIME_PREDICATE_CHARACTERIZATION_PRIMARY__WEIGHT2_CLOSURE_COMPLEMENTARY`; Lane B identified `RESP:REPRESENTATION_REGIME_UNCHARACTERIZED` / selected `COMPUTE:REGIME_CHARACTERIZATION`, defeating the other three hypotheses. Coordinate 3 is overlapping-by-construction. | RECEIPTED: `DUAL_HARNESS_AGREEMENT_BENCHMARK_V0_RESULTS.json`; both lane receipts | Any agreement-rate, reliability, or generalization claim from one instance. |
| Q3.18 | Lane B's revision gate independently withheld the unlicensed move: `REV:SPLIT_REPRESENTATION_REGIME` was `UNRESOLVED` (`NO_ADMISSIBLE_WITH_UNRESOLVED_CANDIDATES`) on the unresolved predicate obligation, and control selected the computation (`REVISION_NOT_YET_SELECTABLE_OPTIONAL_COMPUTE_AVAILABLE`). | RECEIPTED: `DUAL_HARNESS_LANE_B_RECEIPT.json` `decision.revision` / `decision.control`; mechanism in `post_r6o_diagnosis.py` | Claiming the gate discovers obligations; the obligation and its state were declared in the frozen manifest. |
| Q3.19 | Deferred coordinate 4 is scored ALIGNED: both instruments' primary move was rewarded by R6Q's exact regime-membership predicate and Lane A's complementary move by R6P's support-two closure restoration; neither instrument selected the moves the outcomes did not reward. | RECEIPTED: `DUAL_HARNESS_AGREEMENT_BENCHMARK_V0_RESULTS.json` coordinate 4; `research/extensions/orion-q/MAX_R6P_*.json`, `MAX_R6Q_REGIME_PREDICATE_RESULTS.json` | Predictive-validity or forecasting-skill claims; ALIGNED is one deferred observation against the programme's own frozen gates, not ground truth. |
| Q3.20 | Cost profile as recorded: Lane A consumed 13 host capability receipts (~10 min wall including host reasoning); Lane B one native cycle with a sub-second decision after manifest construction. | RECEIPTED: `DUAL_HARNESS_AGREEMENT_BENCHMARK_V0_RESULTS.json` coordinate 5 | Efficiency-superiority claims; manifest construction cost is excluded from Lane B's figure and said so. |
| Q3.21 | The benchmark class measures inter-instrument epistemic agreement on live frontier questions with deferred receipt-bound scoring, a different quantity from task-success-vs-ground-truth agent benchmarks and from same-substrate consensus (self-consistency, LLM-as-judge, debate). | DEFINITIONAL: `DUAL_HARNESS_AGREEMENT_BENCHMARK_V0_PROTOCOL.md`; positioning per `PUBLICATION_PLAN.md` Paper Q3 | Novelty assertion at submission without the plan-mandated fresh hostile novelty search, which has not yet been run for Q3. |
| Q3.22 | V0 is presented as a benchmark definition with a first measurement; submission is gated on 2–3 further question instances (and coordinate 4 is now scored, satisfying that gate). | PLAN: `papers/Q-paper-02-recursive-recovery/PUBLICATION_PLAN.md` Paper Q3 submission gates | Presenting V0 as an evaluation study or the agreement series as existing. |

## Allowed headline

> A receipt-replay research harness and a typed non-LLM campaign controller — both
> live-verified, both non-self-authorizing by construction — were posed the same frozen
> frontier question; they independently agreed on the responsible epistemic layer and the
> next move, the typed controller's revision gate withheld the not-yet-licensed revision,
> and the later frontier outcomes aligned with the agreed move. One instance; a benchmark
> definition with a first measurement.

## Prohibited headlines

- "The dual-harness benchmark shows LLM research agents are (un)reliable."
- "The typed controller predicts research outcomes." / "Agreement validates the diagnosis."
- "The harness makes research loops secure / tamper-proof / sandboxed."
- "The controller reached the diagnosis with no human/LLM involvement." (Manifest
  construction and Lane A hosting are LLM/human-authored.)
- "Instrument agreement confers scientific, novelty, or R6 authority on any result."
- Any claim about the quantum-mechanical content of the R6 chain (owned by Papers Q1/Q2
  per `papers/Q-paper-02-recursive-recovery/PUBLICATION_PLAN.md`).

## Open obligations before submission

1. Run 2–3 further benchmark question instances to seed the agreement series
   (`PUBLICATION_PLAN.md` Paper Q3 gate; coordinate-4 scoring gate already satisfied).
2. Fresh hostile novelty search dated at submission (shared obligation, same plan).
3. Independent replay of every receipt cited in `MANUSCRIPT_V1.md`.
4. Decide the disposition of open defects D2/D3 (repair under the development protocol and
   replay the unchanged gates, or document as accepted limitations with rationale).
