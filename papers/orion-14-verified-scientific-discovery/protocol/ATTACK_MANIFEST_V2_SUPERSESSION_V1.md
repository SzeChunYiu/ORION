# ATTACK_MANIFEST_V2 — verdict-leak repair

**V1 is not modified.** It stays frozen exactly as scored. V2 is a successor
battery with three cases repaired.

## What was wrong

`check_verdict_leak_v1.py` reports `FAIL — 3/39 cases state the verdict`. All
three are in `INSUFFICIENT_EVIDENCE`, and each ends its `evidence_text` with a
sentence naming its own terminal:

| case | trailing sentence |
|---|---|
| `ORION-14-INSUFFICIENT_EVIDENCE-001` | "The evidence is genuinely insufficient to support the comparative claim." |
| `ORION-14-INSUFFICIENT_EVIDENCE-002` | "The evidence is insufficient to support the sweeping claim." |
| `ORION-14-INSUFFICIENT_EVIDENCE-003` | "The evidence is insufficient to support the universal superiority claim." |

No case in the other twelve families does this. A grep for "insufficient"
scores all three correctly with no judgment at all.

## The repair

Only the trailing sentence is deleted. Nothing else changes — no claim, no
source, no evidence object, no expected terminal.

That is possible because each case **already** describes its deficiency
structurally, and the verdict sentence added nothing:

- **001** — "a single unreplicated study with high variance (n=5). No
  confidence intervals reported. The study does not control for model size,
  training data, or evaluation methodology."
- **002** — "compares GPT-4 on 3 tasks to BERT on 3 different tasks. Tasks are
  not the same. Evaluation metrics differ. The study is a preprint with no
  peer review."
- **003** — "correlations on 2 datasets using 1 LLM (GPT-4) as evaluator,
  compared to 3 baselines. No confidence intervals, no statistical
  significance tests, no analysis of evaluator bias."

Each now ends where the description ends, which is the style
`POOLED_SUPPORT_WRONG_OWNER` already uses: state the evidence, let the
terminal follow.

`artifact_hash` is recomputed for the three repaired rows under the scheme
`evaluate_campaign.py` verifies — `sha256` over the canonical JSON of the row
minus its own hash. That derivation was confirmed against **all 39** V1 rows
before anything was edited.

## Verification

| check | V1 | V2 |
|---|---|---|
| `check_verdict_leak_v1.py` | **exit 1**, 3 leaks | **exit 0**, clean (39 cases) |
| artifact-hash mismatches | 0 | 0 |
| `attack_label_visible_to_candidate` leaks | 0 | 0 |
| expected-terminal drift | 0 | 0 |

V1 still fails the leak check. That is the polarity control: the checker
distinguishes the two batteries rather than passing everything handed to it.

## What this does NOT do

**V2 has not been scored.** No panel has run against it, so it produces no
metric and no comparison. Re-scoring requires the eleven-system panel.

**V1's `INSUFFICIENT_EVIDENCE` numbers are not corrected by this file.** They
remain what they were: partly a reading score. ORION-14's H3 reports
`correct_cannot_check_rate = 1.0` across all eleven panel systems with no
observed variance anywhere in the study, and a leak of this shape is the
simplest available explanation for a whole-panel ceiling. That reading is not
established here, only left standing as the checker's own stated concern.

Until V2 is scored, any per-family accuracy on `INSUFFICIENT_EVIDENCE` should
be read as measured on a contaminated battery.

## Related

This is the third recorded instance of the same failure class:

- **ORION-14 H3** — a saturated metric where `len(evidence) == 0` reproduced the
  label at 420/420;
- **ORION-15 hidden-cause suite** — `root_cause_nonce` is the case ordinal in hex,
  recorded as `LABEL_RECOVERABLE_FROM_CONSTRUCTION_CUE`;
- **this** — the label stated in the case's own prose.

The pattern is a benchmark whose label is recoverable without the capability
it claims to measure.
