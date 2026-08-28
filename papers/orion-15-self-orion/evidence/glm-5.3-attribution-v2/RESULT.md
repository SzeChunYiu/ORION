# RESULT — GLM-5.3 attribution harvest (frozen v2 protocol, blind subagent judging)

Campaign `p5-glm-5.3-attribution-v2-harvest` (lane NR-01), run 2026-08-28. This is the
pending revival item "24 GLM-5.3 harvest" for orion-15-self-orion: re-execute the frozen
`glm-5.2-attribution-v2` protocol end-to-end with judge = **GLM-5.3 (claude-cn harness,
glm-5.3)**, under *enforced* blindness (blind subagent per packet), scoring with the
frozen scorer imported verbatim from `scripts/run_p5_glm_attribution_v2.py`.

Protocol (read end-to-end before execution): `papers/orion-15-self-orion/protocol/
P5_ATTRIBUTION_INSTRUMENT_V2_PROTOCOL.json` (sha256 `5d4d0fa3…268b`, unchanged), driven by
`scripts/run_p5_glm_attribution_v2.py` and the V1 prompt imported from
`scripts/run_p5_glm_attribution.py`. Suite `PROTECTED_SUITE_V1.json` untouched
(sha256 `1c3650a6…e2747`).

## What was judged

48 packets = the 24 frozen cases × 2 arms, rebuilt from current main (`origin/main`
@ `ff0df7f2`) per the v2 packet-construction rules:

- **control** — verbatim V1 `ATTRIBUTION_PROMPT` (free-form attribution JSON).
- **treatment** — Stage A `EXTRACTION_PROMPT` (quote-backed licensed-evidence extraction)
  + deterministic Stage B rules R1–R6 (imported verbatim; not reimplemented).

Sanitization (guard hits: **0**): file paths, commit metadata, authorship, timestamps and
provenance headers stripped; case ids neutralized `P5-HC-NNN` → `PKT-{C,T}-NN` so the
judge-visible text carries no paper identity. Packet sha256s + source map live in
`PREPARATION_RECEIPT.json` (kept out of judge-visible material).

## Blindness mechanics

One fresh general-purpose subagent per packet (no inherited conversation context, model
inherit = glm-5.3), input = confinement wrapper + packet text only. No repo access, no
file paths, no source map. Verifiable from the harness transcripts: **0 tool calls across
all 48 judge transcripts**; every response parses with the frozen `parse_json_block`.
Confinement is by instruction rather than a technical sandbox (recorded deviation);
the zero-tool-call transcript evidence is the a-posteriori check.

## Headline metrics (frozen scorer, chance baseline 0.125)

| Run | Judge | Accuracy | Macro-F1 | Errors |
|---|---|---|---|---|
| 5.2 v1 | glm-5.2 (adapter) | 21/24 = 0.875 | 0.875 | {002, 012, 018} |
| 5.2 v2 control | served glm-5.3 (alias) | 21/24 = 0.875 | 0.8726 | {002, 012, 018} |
| 5.2 v2 treatment | served glm-5.3 (alias) | 24/24 = 1.000 | 1.000 | {} |
| **5.3 harvest control** | glm-5.3 (blind harness) | **22/24 = 0.9167** | **0.9143** | {012, 014} |
| **5.3 harvest treatment** | glm-5.3 (blind harness) | **23/24 = 0.9583** | **0.9571** | {020} |

Control extras (v1-script definitions): confidence HIGH 16 / MEDIUM 8 (5.2 v1 was 15/9);
`false_method_change_rate` 0.0909 = 2/22 (5.2 v1 was 0.1429 = 3/21). Per-family recall:
1.0 everywhere except ENVIRONMENT_DEPENDENCY_TOOL_FAILURE 0.667 (case 012) and
EVALUATOR_METRIC_BUG 0.667 (case 014). Treatment fired rules: R3×11, R5×9, R2×3, R4×1;
zero `CANNOT_DISTINGUISH`, zero extraction-flag hits, zero parse errors in either arm.

## Error analysis

- **Control error churn, net improvement.** `P5-HC-012` (gold ENVIRONMENT_DEPENDENCY,
  attributed IMPLEMENTATION_BUG) is the one error that reproduces across every generation
  and arm-generation pair — the instrument's one stable hard case. The 5.2-era errors 002
  (RETRIEVAL→REPRESENTATION) and 018 (REPRESENTATION→METHOD_BASIS) did not reproduce. New
  error `P5-HC-014` (gold EVALUATOR_METRIC_BUG → MEASUREMENT_SPECIFICATION_GAP) is an
  adjacent-family confusion inside the measurement cluster; the judge's own
  `competing_causes` listed EVALUATOR_METRIC_BUG.
- **Treatment: one Stage-A extraction drift, not a Stage-B failure.** `P5-HC-020` (gold
  MEASUREMENT_SPECIFICATION_GAP): the 5.3 extractor licensed the *same* causal quote the
  5.2-era run licensed ("because required ground truth data doesn't exist") and the same
  correct failing_subject locus (PROTOCOL_SPECIFICATION_MEASUREMENT_DESIGN), but classified
  the cause clause's locus as EXTERNAL_DEPENDENCY_ENVIRONMENT_TOOL; deterministic R3 then
  mapped it to ENVIRONMENT_DEPENDENCY_TOOL_FAILURE. Stage B behaved exactly as specified —
  the drift is in locus classification of a data-availability cause inside an
  infeasible-protocol statement.

## Meaning for the self-attribution claim

1. **Direction SUPPORTED at the new judge generation.** Treatment (0.9583 / macro-F1
   0.9571) still beats control (0.9167 / 0.9143) under enforced blindness, and both arms
   sit far above chance (0.125). The staged licensed-evidence instrument remains the
   better attributor when the judge cannot lean on anything but the packet.
2. **The perfect treatment score is NOT generation-invariant** (24/24 → 23/24). The claim
   should be stated as "treatment ≥ control with a stable margin", not "treatment is
   ceiling-perfect": one extraction-level locus drift is enough to drop a case. The
   5.2-era 24/24 is best read as a ceiling observation, not a reproducible constant.
3. **Blindness hardened, not weakened, the result.** This harvest ran under strictly
   stronger blinding than the frozen runs (neutralized case ids, no adapter identity,
   packet-only confinement), so the treatment-over-control margin surviving here is the
   conservative estimate.
4. **Caveat on "new generation".** The frozen v2 run already *served* glm-5.3 under the
   glm-5.2 alias, so the model delta between the 5.2-era v2 numbers and this harvest is
   nominal; the real deltas are enforced blindness + harness serving. Any 5.2-vs-5.3
   statement should be scoped accordingly.

**Verdict: SUPPORTED** — the v2 staged instrument's treatment-over-control attribution
advantage holds when re-harvested with GLM-5.3 as a strictly blinded judge; the
previously-observed perfect 24/24 is IMPROVED→not-reproduced (23/24) and should not be
cited as a stable ceiling.

## Protocol deviations / CANNOT_CHECK (recorded, none hidden)

- Judge substitution GLM-5.2-requested → GLM-5.3-executed is the point of the harvest.
- Case-id neutralization `P5-HC-NNN` → `PKT-NNN` (blinding hardening; the frozen prompts
  embed real case ids).
- Temperature 0.0 / max_tokens 4096 of the frozen protocol are **not settable** per call in
  the subagent harness (harness defaults; effort=high observed in transcripts). CANNOT_CHECK:
  no temperature-controlled replication of the frozen serving parameters.
- Confinement is by instruction, not a technical sandbox; verified a-posteriori by
  0 tool calls in all 48 transcripts.
- Paste normalization: packet text passed through JSONL escaping (unicode literal vs
  escaped forms, e.g. `O(n³)`); semantically identical, byte-level identity not guaranteed.
- Per-call API token counts / latency are not reported in the frozen row shape (harness
  accounting differs); token/latency columns are therefore absent rather than zero.

## Authority binding

`CLAIM_LEDGER_V1.json` has **no slot** for a newer judge generation, so no claim/coverage
file was modified by this harvest. Binding this evidence into the orion-15 claim ledger is
the lead's call.

## Artifacts

- `report.json` — frozen v2 schema, judge fields updated, both arms + control extras.
- `JUDGE_TRANSCRIPT.jsonl` — 48 records: packet id, arm, verbatim raw response, timestamp,
  transcript source file, paste-normalization/confinement/serving notes.
- `results_control_v1replay.jsonl`, `results_treatment_v2.jsonl` — per-case rows in the
  frozen runner's shape (incl. Stage-A extractions, fired rules, flags).
- `PREPARATION_RECEIPT.json`, `packets/*.txt`, `prepare_packets.py` — written pre-judging.
